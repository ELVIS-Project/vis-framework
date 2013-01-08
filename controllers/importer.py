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
from os import path
# PyQt4
from PyQt4.QtCore import pyqtSignal, Qt
# music21
from music21 import converter
# vis
from controllers.controller import Controller
from models import importing, analyzing



class Importer(Controller):
   '''
   This class knows how to keep a list of filenames with pieces to be analyzed,
   and how to import the files with music21.

   The ListOfFiles model is always stored in the list_of_files property.
   '''



   # PyQt4 Signals
   add_remove_success = pyqtSignal()
   imported = pyqtSignal()
   error = pyqtSignal()
   status = pyqtSignal()



   def __init__(self, *args):
      '''
      Create a new Importer instance.
      '''
      self._list_of_files = importing.ListOfFiles()



   def add_piece(self, piece):
      '''
      Call add_pieces() with the given argument.
      '''
      return self.add_pieces(piece)



   def add_pieces(self, pieces):
      '''
      Add the filenames to the list of filenames that should be imported. The
      argument is a list of strings. If a filename is a directory, all the files
      in that directory (and its subdirectories) are added to the list.

      This method emits the Importer.error signal, with a description, in the
      following situations:
      - a pathname does not exist
      - a pathname is already in the list

      Emits the Importer.add_remove_success signal with True if there were no
      errors, or with False if there was at least one error.
      '''
      # Track whether there was an error
      we_are_error_free = True

      # Filter out paths that do not exist
      paths_that_exist = []
      for pathname in pieces:
         if path.exists(pathname):
            paths_that_exist.append(pathname)
         else:
            # TODO: emit
            #Importer.error.emit('Path does not exist: ' + str(pathname))
            #print('**** path does not exist: ' + str(pathname))
            we_are_error_free = False

      # If there's a directory, expand to the files therein
      directories_expanded = []
      for pathname in paths_that_exist:
         if path.isdir(pathname):
            pass # TODO: ??
         else:
            directories_expanded.append(pathname)

      # Ensure there will be no duplicates
      no_duplicates_list = []
      for pathname in directories_expanded:
         if not self._list_of_files.isPresent(pathname):
            no_duplicates_list.append(pathname)
         else:
            # TODO: emit
            #Importer.error.emit('Filename already on the list: ' + str(pathname))
            we_are_error_free = False
            #print('++++ filename already in list: ' + str(pathname))

      # If there are no remaining files in the list, just return now
      if 0 == len(no_duplicates_list):
         return we_are_error_free

      # Add the number of rows we need
      first_index = self._list_of_files.rowCount()
      last_index = first_index + len(no_duplicates_list)
      self._list_of_files.insertRows(first_index, len(no_duplicates_list))

      # Add the files to the list
      for list_index in xrange(first_index, last_index):
         index = self._list_of_files.createIndex(list_index, 0)
         self._list_of_files.setData(index,
                                     no_duplicates_list[list_index-first_index],
                                     Qt.EditRole)

      return we_are_error_free



   def remove_pieces(self, pieces):
      '''
      Remove the filenames from the list of filenames that should be imported.
      The argument is a list of strings. If a filename is a directory, all the
      files in that directory (and its subdirectories) are removed from the
      list.

      If the argument is a string, it is treated like a single filename.

      If a filename is not in the list, it is ignored.

      Emits the Importer.add_remove_success signal with True or
      False, depending on whether the operation succeeded. Returns that same
      value.
      '''
      # Is the argument a string? If so, make it a one-element list.
      if isinstance(pieces, str):
         pieces = [pieces]

      for piece_to_remove in pieces:
         # isPresent() either returns False or a QModelIndex referring to the
         # file we want to remove
         piece_index = self._list_of_files.isPresent(piece_to_remove)
         if piece_index is not False:
            # if the piece is actually in the list, remove it
            #print('**** removing row ' + str(piece_index.row())) # DEBUGGING
            self._list_of_files.removeRows(piece_index.row(), 1)

      # I don't yet know of a situation that warrants a failure, so...
      Importer.add_remove_success.emit(True)
      return True



   def import_pieces(self):
      '''
      Transforms the current ListOfFiles into a ListOfPieces by importing the
      files specified, then extracting data as needed.

      Emits VisSignals.importer_error if a file cannot be imported, but
      continues to import the rest of the files.

      Emits VisSignals.importer_imported with the ListOfPieces when the import
      operation is completed, and returns the ListOfPieces.
      '''
      # NB: I must initialize the offset_intervals field to [0.5]
      # NB: I must initialize the parts_combinations field to []

      # hold the ListOfPieces that we'll return
      post = analyzing.ListOfPieces()

      for each_path in self._list_of_files:
         # Try to import the piece
         this_piece = Importer._piece_getter(each_path)
         # Did it fail? Report the error
         if this_piece is None:
            Importer.error.emit('Unable to import this file: ' + str(each_path))
         # Otherwise keep working
         else:
            # prepare the ListOfPieces!
            post.insertRows(post.rowCount(), 1)
            new_row = post.rowCount() - 1
            post.setData((new_row, analyzing.ListOfPieces.filename),
                         each_path,
                         Qt.EditRole)
            post.setData((new_row, analyzing.ListOfPieces.score),
                         (this_piece, Importer._find_piece_title(this_piece)),
                         Qt.EditRole)
            post.setData((new_row, analyzing.ListOfPieces.parts_list),
                         Importer._find_part_names(this_piece),
                         Qt.EditRole)
            # Leave offset-interval and parts-combinations at defaults
      # return
      #Importer.imported.emit(post) # commented for DEBUGGING
      return post



   @staticmethod
   def _piece_getter(pathname):
      '''
      Load a file and import it to music21. Return the Score object.

      This method should only be called by the Importer.import_pieces() method,
      which coordinates multiprocessing.
      '''
      try:
         post = converter.parseFile(pathname)
      except ArchiveManagerException, PickleFilterException:
         # these are the exceptions I found in the music21 'converter.py' file
         post = None
         #Importer.error.emit('Unable to import this file: ' + str(pathname)) # commented for DEBUGGING
      except ConverterException, ConverterFileException:
         # these are the exceptions I found in the music21 'converter.py' file
         post = None
         #Importer.error.emit('Unable to import this file: ' + str(pathname)) # commented for DEBUGGING

      return post



   @staticmethod
   def _find_part_names(the_score):
      '''
      Returns a list with the names of the parts in the given Score.
      '''
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

      return post



   @staticmethod
   def _find_piece_title(the_score):
      '''
      Returns the title of this Score or an empty string.
      '''
      # hold the piece title
      post = ''

      # First try to get the title from a Metadata object, but if it doesn't
      # exist, use the filename without directory.
      if the_score.metadata is not None:
         #print('**** using metadata')
         post = the_score.metadata.title
      else:
         #print('++++ using pathname')
         post = path.basename(the_score.filePath)

      # Now check that there is no file extension. This could happen either if
      # we used the filename or if music21 did a less-than-great job at the
      # Metadata object.
      post = path.splitext(post)[0]

      return post
# End class Importer -----------------------------------------------------------
