#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: Importer.py
# Purpose: Holds the Importer controller.
#
# Copyright (C) 2012 Jamie Klassen, Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
Holds the Importer controller.
"""

# Imports from...
# python
import os
from multiprocessing import Pool
# PyQt4
from PyQt4.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
# music21
from music21 import converter
from music21.stream import Score
# vis
from controllers.controller import Controller
from models import importing, analyzing


# multiprocessing requires your processes to be declared at module scope, sorry!
def import_piece(file_path):
    """
    Given a path to a music21 symbolic music notation file, return a tuple
    containing a frozen music21.Score and all the pertinent import information
    for the score, or else a string containing any errors that occurred in
    importing.

    NB: the reason we freeze the music21 Score is because normally music21
    Streams are complex webs of weak references, which cannot be pickled and
    therefore cannot be passed between different child processes in a
    multiprocessing context.

    NB2: if the imported file is a MIDI file, it won't be pickled, because then it would explode
    """
    try:
        piece = converter.parseFile(file_path)
        title = Importer._find_piece_title(piece)
        part_names = Importer._find_part_names(piece)
        _, extension = os.path.splitext(file_path)
        if '.midi' == extension or '.mid' == extension:
            return_score = piece
        else:
            return_score = converter.freezeStr(piece, fmt='pickle')
        return (file_path, return_score, title, part_names)
    except Exception as excep:
        return (file_path, str(excep))


class ImporterThread(QThread):
    """
    In a separate QThread, coordinate the multiprocessing-enabled analysis of pieces.
    """

    def __init__(self, importer):
        """
        Creates a new ImporterThread instance, keeping track of the
        Importer object which instantiated it.
        """
        self._pool = None
        self._importer = importer
        # this will hold the fraction of pieces which have been analyzed
        # at a given time
        self.progress = 0
        # flag for whether to use multiprocessing in importing
        self._multiprocess = True
        self.results = []
        super(QThread, self).__init__()

    def prepare(self, pieces):
        """
        Sets the analyzing.ListOfPieces object to store the imported
        pieces in, and sets some shorthands for the other methods.
        """
        self._pieces_list = pieces
        self._files = self._importer._list_of_files
        self.num_files = self._files.rowCount()

    def set_multiprocess(self, state):
        """
        Set the meaningless self._multiprocess instance variable to something.
        """
        self._multiprocess = bool(state)

    def callback(self, result):
        """
        Each time an import process is completed, either report any
        errors which occurred, or update the progress status and append
        the imported piece to the list of results.
        """
        self.progress += 1
        if len(result) == 2:
            msg = "Could not import {0}: {1}".format(*result)
            self._importer.error.emit(msg)
        else:
            file_path = result[0]
            self._importer.status.emit(str(int(float(self.progress) / self.num_files * 100)))
            self._importer.status.emit(file_path + ' completed.')
            self.results.append(result)

    def run(self):
        """
        Import all the pieces contained in the parent Importer's _list_of_files.
        """
        self._importer.import_is_running = True
        self._importer.status.emit('0')
        self._importer.status.emit('Importing...')

        # Sort the files according to whether their extension indicates they'll work with
        # multiprocessing or not
        sequential_extensions = ['.mid', '.midi']
        multiprocess_files = []  # for everything that works in multiprocessing
        sequential_files = []  # for everything that doesn't work (i.e., MIDI)
        for sort_file in self._files:
            _, extension = os.path.splitext(sort_file)
            if extension in sequential_extensions:
                sequential_files.append(sort_file)
            else:
                multiprocess_files.append(sort_file)

        # Start up the multiprocessing
        self._pool = Pool()
        for file_path in multiprocess_files:
            self._pool.apply_async(import_piece,
                                   (file_path,),
                                   callback=self.callback)
        self._pool.close()
        self._pool.join()
        self._importer.import_is_running = False
        self._pool = None

        # Start up the sequential importing
        for file_path in sequential_files:
            self.callback(import_piece(file_path))

        # self.progress != self.num_files if a user cancelled the runing job before it finished
        if self.progress != self.num_files:
            return None

        self._importer.status.emit('Assembling results...')
        # at this point, self._pieces_list should be an analyzing.ListOfPieces
        # which belongs to the relevant Analyzer we'll be passing the data to.
        post = self._pieces_list
        for file_path, piece, title, parts in self.results:
            post.insertRows(post.rowCount(), 1)
            new_row = post.rowCount() - 1
            post.setData((new_row, analyzing.ListOfPieces.filename),
                        file_path,
                        Qt.EditRole)
            post.setData((new_row, analyzing.ListOfPieces.score),
                        (piece, title),
                        Qt.EditRole)
            post.setData((new_row, analyzing.ListOfPieces.parts_list),
                        parts,
                        Qt.EditRole)
        self._importer.status.emit('Done!')
        self._importer.import_finished.emit()


class Importer(Controller):
    """
    This class knows how to keep a list of filenames with pieces to be analyzed,
    and how to import the files with music21.

    The ListOfFiles model is always stored in the list_of_files property.
    """

    # PyQt4 Signals
    # -------------
    # a list of str filenames to add to the list of files to analyze
    add_pieces_signal = pyqtSignal(list)
    # a list of str filenames to remove from the list of files to analyze
    remove_pieces_signal = pyqtSignal(list)
    # whether the add/remove operation was successful
    add_remove_success = pyqtSignal(bool)
    # create a ListOfPieces from the ListOfFiles
    run_import = pyqtSignal(analyzing.ListOfPieces)
    # the result of importer_import
    import_finished = pyqtSignal()
    # description of an error in the Importer
    error = pyqtSignal(str)
    # signal for each individual import
    piece_gotten = pyqtSignal(Score, str)
    # informs the GUI of the status for a currently-running import (if two or
    # three characters followed by a '%' then it should try to update a
    # progress bar, if available)
    status = pyqtSignal(str)
    # cancels the currently-running import, if there is one
    cancel_import = pyqtSignal()
    #-------------
    # Other Things
    #-------------
    # List of filename extensions for music21-supported files
    valid_extensions = ['.nwc.', '.mid', '.midi', '.mxl', '.krn', '.xml', '.md']
    # Whether there's an import running
    import_is_running = False

    def __init__(self, *args):
        """
        Create a new Importer instance.
        """
        # signals
        super(Importer, self).__init__()  # required for signals
        self.run_import.connect(self.import_pieces)
        self.add_pieces_signal.connect(self.add_pieces)
        self.remove_pieces_signal.connect(self.remove_pieces)
        self.cancel_import.connect(self._cancel_import)
        # other things
        self._list_of_files = importing.ListOfFiles()
        self.thread = ImporterThread(self)

    @pyqtSlot()
    def _cancel_import(self):
        """
        Determine whether there is an import operation running, then cancel it.
        """
        if self.thread._pool is not None:
            self.thread._pool.terminate()
            msg = 'Now you should close and re-open vis.'
            self.status.emit(msg)
            self.error.emit(msg)

    @pyqtSlot(list)
    def add_pieces(self, pieces):
        """
        Add the filenames to the list of filenames that should be imported. The
        argument is a list of strings. If a filename is a directory, all the files
        in that directory (and its subdirectories) are added to the list.

        This method emits the Importer.error signal, with a description, in the
        following situations:
        - a pathname does not exist
        - a pathname is already in the list

        Emits the Importer.add_remove_success signal with True if there were no
        errors, or with False if there was at least one error.
        """
        # Track whether there was an error
        we_are_error_free = True

        # Filter out paths that do not exist
        paths_that_exist = []
        for pathname in pieces:
            if os.path.exists(pathname):
                paths_that_exist.append(pathname)
            else:
                self.error.emit('Path does not exist: ' + str(pathname))
                we_are_error_free = False

        # If there's a directory, expand to the files therein
        directories_expanded = []
        for pathname in paths_that_exist:
            if os.path.isdir(pathname):
                for path, _, files in os.walk(pathname):
                    for filename in files:
                        directories_expanded.append(os.path.join(path, filename))
            else:
                directories_expanded.append(pathname)

        # Ensure there will be no duplicates
        no_duplicates_list = []
        for pathname in directories_expanded:
            if not self._list_of_files.isPresent(pathname):
                no_duplicates_list.append(pathname)
            else:
                self.error.emit('Filename already on the list: ' + str(pathname))
                we_are_error_free = False

        # Ensure all the filenames have valid extensions
        valid_extensions_list = []
        for pathname in no_duplicates_list:
            _, extension = os.path.splitext(pathname)
            if extension in Importer.valid_extensions:
                valid_extensions_list.append(pathname)
            else:
                we_are_error_free = False

        # If there are no remaining files in the list, just return now
        if 0 == len(valid_extensions_list):
            msg = 'All selected pathnames/filenames are invalid.'
            self.error.emit(msg)
            we_are_error_free = False
            return we_are_error_free

        # Add the number of rows we need
        first_index = self._list_of_files.rowCount()
        last_index = first_index + len(valid_extensions_list)
        self._list_of_files.insertRows(first_index, len(valid_extensions_list))

        # Add the files to the list
        for list_index in xrange(first_index, last_index):
            index = self._list_of_files.createIndex(list_index, 0)
            self._list_of_files.setData(index,
                                        valid_extensions_list[list_index - first_index],
                                        Qt.EditRole)

        if not we_are_error_free:
            msg = 'Some of the selected pathnames/filenames are invalid.'
            self.error.emit(msg)
        return we_are_error_free

    @pyqtSlot(list)
    def remove_pieces(self, pieces):
        """
        Remove the filenames from the list of filenames or list of QModelIndex objects that should
        be imported. The argument is a list of strings. If a filename is a directory, all the
        files in that directory (and its subdirectories) are removed from the list.

        If the argument is a string, it is treated like a single filename.

        If a filename is not in the list, it is ignored.

        Emits the Importer.add_remove_success signal with True or False, depending on whether the
        operation succeeded. Returns that same value.
        """
        # Is the argument a string? If so, make it a one-element list.
        if isinstance(pieces, str):
            pieces = [pieces]

        for piece_to_remove in pieces:
            # isPresent() either returns False or a QModelIndex referring to the
            # file we want to remove
            piece_index = self._list_of_files.isPresent(piece_to_remove)
            if piece_index is not False:
                # if the piece is actually in the list, remove it
                self._list_of_files.removeRows(piece_index.row(), 1)

        # I don't yet know of a situation that warrants a failure, so...
        self.add_remove_success.emit(True)
        return True

    @pyqtSlot(analyzing.ListOfPieces)
    def import_pieces(self, the_pieces):
        """
        Transforms the current ListOfFiles into a ListOfPieces by importing the
        files specified, then extracting data as needed.

        The argument is the ListOfPieces into which to load the data.

        Emits Importer.error if a file cannot be imported, but continues to
        import the rest of the files.

        Emits Importer.import_finished with the ListOfPieces when the import
        operation is completed, and returns the ListOfPieces.
        """
        # NB: I must initialize the offset_intervals field to [0.5]
        # NB: I must initialize the parts_combinations field to []
        # NB: Any time you use this method, you must follow it with .thread.wait()
        # or you may get disastrous results.
        self.thread.prepare(the_pieces)
        self.thread.start()

    def has_files(self):
        """
        Returns True if there is at least one file in the list of files to be imported.
        """
        if 0 < self._list_of_files.rowCount():
            return True
        else:
            return False

    @staticmethod
    def _find_part_names(the_score):
        """
        Returns a list with the names of the parts in the given Score.
        """
        # hold the list of part names
        post = []

        # First try to find Instrument objects. If that doesn't work, use the "id"
        for each_part in the_score.parts:
            instr = each_part.getInstrument()
            if instr is not None and instr.partName != '':
                post.append(instr.partName)
            else:
                post.append(each_part.id)

        # Make sure none of the part names are just numbers; if they are, use
        # a part name like "Part 1" instead.
        for part_index in xrange(len(post)):
            try:
                int(post[part_index])
                # if that worked, the part name is just an integer...
                post[part_index] = 'Part ' + str(part_index + 1)
            except ValueError:
                pass

        return post

    @staticmethod
    def _find_piece_title(the_score):
        """
        Returns the title of this Score or an empty string.
        """
        # hold the piece title
        post = ''

        # First try to get the title from a Metadata object, but if it doesn't
        # exist, use the filename without directory.
        if the_score.metadata is not None:
            post = the_score.metadata.title
        else:
            post = os.path.basename(the_score.filePath)

        # Now check that there is no file extension. This could happen either if
        # we used the filename or if music21 did a less-than-great job at the
        # Metadata object.
        post = os.path.splitext(post)[0]

        return post
