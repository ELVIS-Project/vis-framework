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
# vis
from controller import Controller
from models.importing import ListOfFiles
from models.analyzing import ListOfPieces



class Importer(Controller):
   '''
   This class knows how to keep a list of filenames with pieces to be analyzed,
   and how to import the files with music21.

   The ListOfFiles model is always stored in the list_of_files property.
   '''



   def __init__(self, *args):
      '''
      Create a new Importer instance.
      '''
      self.list_of_files = ListOfFiles()



   def setup_signals(self):
      '''
      Set the methods of Importer as slots for the relevant methods emitted by
      the VisController.
      '''
      # importer_add_pieces
      # importer_remove_pieces
      # importer_import
      pass



   def add_pieces(self, pieces):
      '''
      Add the filenames to the list of filenames that should be imported. The
      argument is a list of strings. If a filename is a directory, all the files
      in that directory (and its subdirectories) are added to the list.

      If a filename does not exist, this method emits the
      VisSignals.importer_error signal, with a description of the error.

      Emits the VisSignals.importer_add_remove_success signal with True or
      False, depending on whether the operation succeeded.
      '''
      pass



   def remove_pieces(self, pieces):
      '''
      Remove the filenames from the list of filenames that should be imported.
      The argument is a list of strings. If a filename is a directory, all the
      files in that directory (and its subdirectories) are removed from the
      list.

      If a filename does not exist, it is ignored.

      Emits the VisSignals.importer_add_remove_success signal with True or
      False, depending on whether the operation succeeded.
      '''
      pass



   def import_pieces(self):
      '''
      Transforms the current ListOfFiles into a ListOfPieces by importing the
      files specified, then extracting data as needed.

      Emits VisSignals.importer_error if a file cannot be imported, but
      continues to import the rest of the files.

      Emits VisSignals.importer_imported with the ListOfPieces when the import
      operation is completed.
      '''
      pass



   @staticmethod
   def _piece_getter(pathname):
      '''
      Load a file and import it to music21. Return the Score object.

      This method should only be called by the Importer.import_pieces() method,
      which coordinates multiprocessing.
      '''
      pass
# End class Importer -----------------------------------------------------------
