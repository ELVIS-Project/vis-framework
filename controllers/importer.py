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
'''
Holds the Importer controller.
'''


# Imports from...
# python
import os
from multiprocessing import Pool
import pickle
# PyQt4
from PyQt4.QtCore import pyqtSignal, Qt, QThread, QObject
# music21
from music21 import converter
from music21.stream import Score
# vis
from models import importing, analyzing, settings


def _import_piece(file_path):
    """
    Import a music21-supported symbolic music notation file and find the title and part names.

    Parameters
    ----------

    file_path : string
        The path to a symbolic notation file.

    Returns
    -------

    t : 4-tuple or string
        Either:
        * (path, score, title, names)
        * string with description of a :module:`music21.converter` exception.

    path : string
        The path to the symbolic notation file.

    score : :class:`music21.stream.Score`
        A "frozen" (pickled) Score object. The Score is pickled so it can be passed between
        processes; since :class:`music21.stream.Stream` objects are usually collections of weak
        references, they cannot otherwise be passed around for multiprocessing.

    title : string
        The title found in the Score

    names : list of string
        A list of the part names found in the Score, from top to bottom.
    """
    try:
        piece = converter.parseFile(file_path)
        title = Importer._find_piece_title(piece)
        part_names = Importer._find_part_names(piece)
        s = converter.freezeStr(piece, fmt='pickle')
        return (file_path, s, title, part_names)
    except (converter.ArchiveManagerException,
            converter.PickleFilterException,
            converter.ConverterException,
            converter.ConverterFileException) as e:
        return str(e)


class Importer(QThread):
    '''
    This class knows how to keep a list of filenames with pieces to be analyzed,
    and how to import the files with music21.

    The ListOfFiles model is always stored in the list_of_files property.
    '''

    status = pyqtSignal(str)
    # TODO: reimplement this with exceptions which are caught
    # by higher-level controllers.
    error = pyqtSignal(str)

    def __init__(self, *args):
        '''
        Create a new Importer instance.
        '''
        self.progress = 0.0
        self.list_of_files = importing.ListOfFiles()
        self.list_of_pieces = analyzing.ListOfPieces()
        self.results = []
        self.multiprocess = settings.BooleanSetting(
            False,
            display_name="Use multiprocessing (import in parallel)"
        )
        super(Importer, self).__init__()

    def start_import(self):
        '''
        Method docstring
        '''
        self.start()

    def add_folders(self, folders):
        """
        For a list of directories, make a list of the files in the directory (and all
        subdirectories), then call :py:method::`add_files` to import them.

        Parameters
        ----------

        folders : list of string
            Each string should be a pathname referring to a directory.

        Returns
        -------

        i : integer
            Returns 0 on method completion

        Side Effects
        ------------

        Calls :py:method::`add_files`, causing its side effects.
        """
        extensions = ['.nwc.', '.mid', '.midi', '.mxl', '.krn', '.xml', '.md']
        files_to_add = []
        for folder in folders:
            for path, _, files in os.walk(d):
                for fp in files:
                    _, extension = os.path.splitext(fp)
                    if extension in extensions:
                        files_to_add.append(os.path.join(path, fp))
        self.add_files(files_to_add)
        #
        return 0

    def add_files(self, files):
        """
        Add a list of pathnames to the data model representing symbolic notation files to import
        for this analysis activity.

        Parameters
        ----------

        files : list of string
            List of pathnames to import. If one of the pathnames is a directory, then all valid
            files in that directory (and its subdirectories) will be appended to the list.

        Returns
        -------

        we_are_error_free : integer
            0 if there are no errors; otherwise incremented by 1 for each error.

        Emits
        -----

        :py:const:`Importer.error` : If a pathname does not exist. This would not cause the entire
            import to fail.

        :py:const:`Importer.error` : If a pathname is already in the list of files to import. This
            would not cause the entire import to fail.

        Side Effects:
        -------------

        Between 0 and len(files) pathnames will be added to the
        :py:attribute:`self.list_of_files` :class:`models.importing.ListOfFiles` instance.
        """
        # Track whether there was an error
        we_are_error_free = 0
        # Filter out paths that do not exist
        paths_that_exist = []
        for pathname in files:
            if os.path.exists(pathname):
                paths_that_exist.append(pathname)
            else:
                self.error.emit('Path does not exist: ' + str(pathname))
                we_are_error_free += 1
        # If there's a directory, expand to the files therein
        directories_expanded = []
        for pathname in paths_that_exist:
            if os.path.isdir(pathname):
                self.add_folders(pathname)
            else:
                directories_expanded.append(pathname)
        # Ensure there will be no duplicates
        no_duplicates_list = []
        for pathname in directories_expanded:
            if not self.list_of_files.isPresent(pathname):
                no_duplicates_list.append(pathname)
            else:
                self.error.emit('Filename already on the list: ' + str(pathname))
                we_are_error_free += 1
        # If there are no remaining files in the list, just return now
        if 0 == len(no_duplicates_list):
            return we_are_error_free
        # Add the number of rows we need
        first_index = self.list_of_files.rowCount()
        last_index = first_index + len(no_duplicates_list)
        self.list_of_files.insertRows(first_index, len(no_duplicates_list))
        # Add the files to the list
        for list_index in xrange(first_index, last_index):
            index = self.list_of_files.createIndex(list_index, 0)
            self.list_of_files.setData(index,
                                       no_duplicates_list[list_index-first_index],
                                       Qt.EditRole)
        # Return an error, if we have one
        return we_are_error_free

    def remove_files(self, files):
        """
        Remove pathnames that are in the list of files to import.

        Parameters
        ----------

        files : string or list of string
            Either the pathname to remove or a list of pathnames to remove.

        Returns
        -------

        i : zero
            Returns 0 to indicate the method has finished.

        Side Effects
        ------------

        Between 0 and len(files) pathnames will be removed from the
        :py:attribute:`self.list_of_files` :class:`models.importing.ListOfFiles` instance.
        """
        # Is the argument a string? If so, make it a one-element list.
        if isinstance(files, str):
            files = [files]
        # Remove each file, as appropriate
        for piece_to_remove in files:
            # isPresent() either returns False or a QModelIndex referring to the
            # file we want to remove
            piece_index = self.list_of_files.isPresent(piece_to_remove)
            if piece_index is not False:
                # if the piece is actually in the list, remove it
                self.list_of_files.removeRows(piece_index.row(), 1)
        # The code for success!
        return 0

    def callback(self, result):
        """
        Deal with the result of :function:`_import_piece`, either handling an error appropriately
        or updating the progress and saving the results of the import.

        Parameters
        ----------

        result : 4-tuple or string
            Either:
                * (path, score, title, names)
                * string with description of a :module:`music21.converter` exception.

                path : string
                    The path to the symbolic notation file.

                score : :class:`music21.stream.Score`
                    A "frozen" (pickled) Score object.

                title : string
                    The title found in the Score

                names : list of string
                    A list of the part names found in the Score, from top to bottom.

        Returns
        -------

        i : zero
            Returns 0 to indicate the method has finished.

        Emits
        -----

        :py:const:`Importer.error` : If the import raised an exception, callback() emits this
            signal with the string version of that exception.

        :py:const:`Importer.progress` : If the import was successful, callback() emits this signal
            both with an int representing percentage completion of the entire import job, then with
            a string to describe the progress.

        Side Effects:
        -------------

        If the import was successful, :py:attribute:`self.results` has the imported Score file,
        along with certain metadata, appended.
        """
        if isinstance(result, str): # import was unsuccessful
            self.error.emit(result)
        else: # import was successful
            self.progress += 1.0/self.num_files
            self.status.emit(str(int(self.progress * 100)))
            self.status.emit('Ongoing import... ' + result[0] + ' completed.')
            self.results.append(result)
        return 0

    def run(self):
        '''
        Import all the pieces contained in the parent Importer's _list_of_files.
        '''
        # TODO: fix the documentation here
        # TODO: Check that the list_of_pieces has been set
        if 0 >= self.list_of_files.rowCount():
            s1 = "The list of pieces is empty."
            s2 = "You must choose pieces before we can import them."
            self.error.emit("{0} {1}".format(s1, s2))
            return
        self.status.emit('0')
        self.status.emit('Importing...')
        if self.multiprocess:
            pool = Pool()
            for file_path in self.list_of_files:
                pool.apply_async(_import_piece,
                                 (file_path,),
                                 callback=self.callback)
            pool.close()
            pool.join()
        else:
            for file_path in self.list_of_files:
                self.callback(_import_piece(file_path))
        self.status.emit('Assembling Results...')
        post = self.list_of_pieces
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
        self.status.emit('Done!')

    @staticmethod
    def _find_part_names(the_score):
        """
        Find the names of parts in a Score object, if any. If there are no intelligile part names,
        use names like "Part 1," "Part 2," and so on.

        Parameters
        ----------

        the_score : :class:`music21.stream.Score`

        Returns
        -------

        post : list of string
            The part names will be listed from top to bottom, as they appear in the score, like:
                ['Soprano', 'Alto', 'Tenor', 'Bass']
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
                post[part_index] = 'Part ' + str(part_index+1)
            except ValueError:
                pass
        #
        return post

    @staticmethod
    def _find_piece_title(the_score):
        """
        Find the title stored in a Score object, if any. Otherwise, return the pathname, without
        directories or the last file extension.

        Parameters
        ----------

        the_score : :class:`music21.stream.Score`

        Returns
        -------

        post : string
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
        #
        return post
