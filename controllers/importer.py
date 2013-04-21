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
from PyQt4.QtCore import pyqtSignal, Qt, QThread, QObject, QString
# music21
from music21 import converter
from music21.stream import Score
# vis
from models import importing, analyzing, settings


def _import_piece(file_path):
   '''
   Given a path to a music21 symbolic music notation file, return a tuple
   containing a frozen music21.Score and all the pertinent import information 
   for the score, or else a string containing any errors that occurred in 
   importing.
   
   NB: the reason we freeze the music21 Score is because normally music21
   Streams are complex webs of weak references, which cannot be pickled and
   therefore cannot be passed between different child processes in a
   multiprocessing context.
   '''
   file_path = str(file_path)
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


class Importer(QObject):
   '''
   This class knows how to keep a list of filenames with pieces to be analyzed,
   and how to import the files with music21.
   
   The ListOfFiles model is always stored in the list_of_files property.
   '''
   
   status = pyqtSignal(QString)
   # TODO: reimplement this with exceptions which are caught
   # by higher-level controllers.
   error = pyqtSignal(QString)
   finished = pyqtSignal()
   start = pyqtSignal()
   
   def __init__(self, *args):
      '''
      Create a new Importer instance.
      '''
      super(Importer, self).__init__()
      self.progress = 0.0
      self.list_of_files = importing.ListOfFiles()
      self.list_of_pieces = analyzing.ListOfPieces()
      self.results = []
      self.multiprocess = settings.BooleanSetting(
         False,
         display_name="Use multiprocessing (import in parallel)"
      )
   
   def start_import(self):
      self.start.emit()
   
   def callback(self, result):
      '''
      Each time an import process is completed, either report any
      errors which occurred, or update the progress status and append
      the imported piece to the list of results.
      '''
      if isinstance(result, str):
         self.error.emit(unpickled)
      else: # it is a tuple
         file_path = result[0]
         self.progress += 1.0 / self.list_of_files.rowCount()
         self.status.emit(str(int(self.progress * 100)))
         self.status.emit('Importing... {0} imported.'.format(file_path))
         self.results.append(result)

   def run(self):
      '''
      Import all the pieces contained in list_of_files.
      '''
      # TODO: Check that the list_of_pieces has been set
      if 0 >= self.list_of_files.rowCount():
         s1 = "The list of pieces is empty."
         s2 = "You must choose pieces before we can import them."
         self.error.emit("{0} {1}".format(s1, s2))
      self.status.emit('0')
      self.status.emit('Importing...')
      if self.multiprocess.value:
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
      self.finished.emit()
   
   def add_folders(self, folders):
      '''
      Method docstring
      '''
      extensions = ['.nwc.', '.mid', '.midi', '.mxl', '.krn', '.xml', '.md']
      files_to_add = []
      for folder in folders:
         for path, _, files in os.walk(d):
            for fp in files:
               _, extension = os.path.splitext(fp)
               if extension in extensions:
                  files_to_add.append(os.path.join(path, fp))
      self.add_files(files_to_add)
   
   def add_files(self, files):
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
      for pathname in files:
         if os.path.exists(pathname):
            paths_that_exist.append(pathname)
         else:
            self.error.emit('Path does not exist: ' + str(pathname))
            we_are_error_free = False
      
      # If there's a directory, expand to the files therein
      directories_expanded = []
      for pathname in paths_that_exist:
         if os.path.isdir(pathname):
            pass # TODO: ??
         else:
            directories_expanded.append(pathname)
      
      # Ensure there will be no duplicates
      no_duplicates_list = []
      for pathname in directories_expanded:
         if not self.list_of_files.isPresent(pathname):
            no_duplicates_list.append(pathname)
         else:
            self.error.emit('Filename already on the list: ' + str(pathname))
            we_are_error_free = False
      
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
      
      return we_are_error_free
   
   def remove_files(self, files):
      '''
      Remove the filenames from the list of filenames or list of QModelIndex objects that should
      be imported. The argument is a list of strings. If a filename is a directory, all the
      files in that directory (and its subdirectories) are removed from the list.

      If the argument is a string, it is treated like a single filename.

      If a filename is not in the list, it is ignored.
      '''
      # Is the argument a string? If so, make it a one-element list.
      if isinstance(files, str):
         files = [files]
      
      for piece_to_remove in files:
         # isPresent() either returns False or a QModelIndex referring to the
         # file we want to remove
         piece_index = self.list_of_files.isPresent(piece_to_remove)
         if piece_index is not False:
            # if the piece is actually in the list, remove it
            self.list_of_files.removeRows(piece_index.row(), 1)
      
      return True
   
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
         post = the_score.metadata.title
      else:
         post = os.path.basename(the_score.filePath)
      
      # Now check that there is no file extension. This could happen either if
      # we used the filename or if music21 did a less-than-great job at the
      # Metadata object.
      post = os.path.splitext(post)[0]
      
      return post
# End class Importer -----------------------------------------------------------
