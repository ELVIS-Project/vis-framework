#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: controllers.py
# Purpose: Holds the "controllers" for the MVC architecture in vis.
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
Holds the "controllers" for the MVC architecture in vis.
'''
from PyQt4.QtCore import pyqtSignal, QObject
from models.analyzing import ListOfPieces


class Controller(object):
   '''
   Base class for all vis controllers.
   '''



   def __init__(self):
      '''
      Creates a new instance, and assigns the appropriate widget.
      '''
      pass



   def setup_signals(self):
      '''
      Set methods of this controller as the slot for relevant signals emitted
      by the GUI.
      '''
      pass

class VisSignals(QObject):
   '''
   The VisSignals class holds signals used for communication between
   controllers and their views. We're using signals-and-slots because it helps
   us with the MVC separation: a controller need not know *which* GUI is being
   used, so long as it knows that it will receive particular signals.
   Furthermore, there need not be a one-to-one correspondence between GUI
   widgets and methods in the models.

   Currently depends on PyQt4.QtCore.QObject for the signals-and-slots
   implementation.
   '''
   # Create a signal like this:
   # signal_name = pyqtSignal(str)

   # Importer
   importer_add_pieces = pyqtSignal(list) # a list of str filenames
   importer_remove_pieces = pyqtSignal(list) # a list of str filenames
   importer_add_remove_success = pyqtSignal(bool) # whether the add/remove operation was successful
   importer_import = pyqtSignal(str) # create a ListOfPieces from the ListOfFiles; argument ignored
   importer_imported = pyqtSignal(ListOfPieces) # the result of importer_import
   importer_error = pyqtSignal(str) # description of an error in the Importer
   importer_status = pyqtSignal(str) # informs the GUI of the status for a currently-running import (if two or three characters followed by a '%' then it should try to update a progress bar, if available)

   # Analyzer
   # TODO: figure out what type "index" and "data" are
   #analyzer_change_settings = pyqtSignal(index, data) # change the data of a cell in the ListOfPieces; the GUI will know how to create an index based on which rows are selected and which data is being changed (cross-referenced with the ListOfPieces' declaration of column indices)
   analyzer_analyze = pyqtSignal(str) # to tell the Analyzer controller to perform analysis
   analyzer_analyzed = pyqtSignal(list) # the result of analyzer_analyze; the result is a list of AnalysisRecord objects
   analyzer_error = pyqtSignal(str) # description of an error in the Analyzer
   analyzer_status = pyqtSignal(str) # informs the GUI of the status for a currently-running analysis (if two or three characters followed by a '%' then it should try to update a progress bar, if available)

   # Experimenter
   experimenter_set = pyqtSignal(tuple) # a 2-tuple: a string for a setting name and the value for the setting
   experimenter_experiment = pyqtSignal(str) # tell the Experimenter controller to perform an experiment
   experimenter_experimented = pyqtSignal(tuple) # the result of experimenter_experiment; the result is a tuple, where the first element is the type of Display object to use, and the second is whatever the Display object needs
   experimenter_error = pyqtSignal(str) # description of an error in the Experimenter
   experimenter_status = pyqtSignal(str) # informs the GUI of the status for a currently-running experiment (if two or three characters followed by a '%' then it should try to update a progress bar, if available)

   # DisplayHandler
   display_shown = pyqtSignal(str) # when the user should be able to see the results of an experiment on the screen in a particular format
# End class VisSignals ---------------------------------------------------------