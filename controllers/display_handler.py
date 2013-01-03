#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: DisplayHandler.py
# Purpose: Holds the DisplayHandler controller.
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
Holds the DisplayHandler controller.
'''



# Imports from...
# PyQt
from PyQt4.QtCore import pyqtSlot
# vis
from controller import Controller



class DisplayHandler(Controller):
   '''
   This class takes an ExperimentResults object, if relevant determines which
   Display format to use and its DisplaySettings, then actually displays the
   results for the user.

   Really, the DisplayHandler waits for an Experimenter.experimented
   signal, then processes it.
   '''


   def __init__(self):
      '''
      ???
      '''
      pass



   def show_result(self, signal_result):
      '''
      Slot for the Experimenter.experimented signal. This method is
      called when the Experimenter controller has finished analysis.

      The argument is a 2-tuple, where the first element specifies which Display
      object to use for the results, and the second is the data needed by that
      Display object.
      '''

      # (1) Make a new ___Display
      # (2) Call its "show" method

      pass
# End class DisplayHandler -------------------------------------------------------



class Display(object):
   '''
   Base class for all Displays.
   '''



   def __init__(self, data, settings=None):
      '''
      Create a new Display.

      There are two arguments, the first of which is mandatory:
      - data : argument of any type, as required by the Display subclass
      - settings : the optional ExperimentSettings object
      '''
      # NOTE: You do not need to reimplement this method for subclasses.
      super(Experiment, self).__init__()
      self._data = data
      self._settings = settings



   def show():
      '''
      Show the data in the display.

      This method emits a VisSignals.display_shown signal when it finishes.
      '''
      # NOTE: You must reimplement this method in subclasses.
      pass
# End class Display ------------------------------------------------------------



class SpreadsheetDisplay(object):
   '''
   Saves results in a CSV file (comma-separated values) so that they can be
   imported by a spreadsheet program like LibreOffice Calc or Microsoft Excel.
   '''



   def __init__(self, data, settings=None):
      '''
      Create a new SpreadsheetDisplay.

      There are two arguments, the first of which is mandatory:
      - data : a string that should be the contents of the CSV file
      - settings : the optional ExperimentSettings object
      '''
      # NOTE: You do not need to reimplement this method for subclasses.
      super(Experiment, self).__init__()
      self._data = data
      self._settings = settings



   def show():
      '''
      Saves the data in a file on the filesystem.

      This method emits a VisSignals.display_shown signal when it finishes.
      '''
      # NOTE: You must reimplement this method in subclasses.
      pass
# End class Display ------------------------------------------------------------
