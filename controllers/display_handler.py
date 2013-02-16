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
from PyQt4 import QtCore, QtGui
# vis
from controller import Controller
import file_output



class DisplayHandler(Controller):
   '''
   This class takes an ExperimentResults object, if relevant determines which
   Display format to use and its DisplaySettings, then actually displays the
   results for the user.

   Really, the DisplayHandler waits for an Experimenter.experimented
   signal, then processes it.
   '''



   # PyQt4 Signals
   # -------------
   # when the user should be able to see the results of an experiment on the
   # screen in a particular format
   display_shown = QtCore.pyqtSignal()



   def __init__(self):
      '''
      Create a new DisplayHandler instance.
      '''
      super(DisplayHandler, self).__init__() # required for signals



   #@QtCore.pyqtSlot
   def show_result(self, signal_result):
      '''
      Slot for the Experimenter.experiment_finished signal. This method is
      called when the Experimenter controller has finished analysis.

      The argument is a 2-tuple, where the first element is a list of the
      possible Display objects to use for the results, and the second is the
      data needed by that Display object.

      If there is more than one possible display type, the DisplayHandler will
      somehow choose.
      '''

      # (1) Make a new ___Display
      # (2) Call its "show" method

      # (1) Choose which display type to use
      # TODO: write this section properly... note that signal_result is a
      # 2-tuple, where index 0 has a list of possible Display objects
      display_type = FileOutputDisplay

      # (2) Instantiate and show the display
      this_display = display_type(self, signal_result[1])
      this_display.show()

      # (3) Send the signal of success
      self.display_shown.emit()
# End class DisplayHandler -------------------------------------------------------



class Display(object):
   '''
   Base class for all Displays.
   '''



   def __init__(self, controller, data, settings=None):
      '''
      Create a new Display.

      There are three arguments, the first two of which are mandatory:
      - controller : the DisplayHandler controller to which this Display belongs
      - data : argument of any type, as required by the Display subclass
      - settings : the optional ExperimentSettings object
      '''
      # NOTE: You must re-implement this, and change "object" to "Display"
      super(object, self).__init__()
      self._controller = controller
      self._data = data
      self._settings = settings



   def show(self):
      '''
      Show the data in the display.

      This method emits a VisSignals.display_shown signal when it finishes.
      '''
      # NOTE: You must reimplement this method in subclasses.
      self._controller.display_shown.emit()
# End class Display ------------------------------------------------------------



class FileOutputDisplay(Display):
   '''
   Saves text-based results into a file.
   '''



   def __init__(self, controller, data, settings=None):
      '''
      Create a new FileOutputDisplay.

      There are three arguments, the first two of which are mandatory:
      - controller : the DisplayHandler controller to which this Display belongs
      - data : a string that should be the contents of the text file
      - settings : the optional ExperimentSettings object

      The filename is determined dynamically by the show() method.
      '''
      # NOTE: You do not need to reimplement this method for subclasses.
      super(Display, self).__init__()
      self._controller = controller
      self._data = data
      self._settings = settings



   def show(self):
      '''
      Saves the data in a file on the filesystem.

      This method emits a VisSignals.display_shown signal when it finishes.
      '''
      # (1) Ask for the filename
      the_filename = QtGui.QFileDialog.getSaveFileName(\
         None,
         'vis: Enter filename for file output',
         '',
         '',
         None,
         QtGui.QFileDialog.Options())#QtGui.QFileDialog.DontConfirmOverwrite)) # TODO: remove this if possible

      # (2) Write out the file
      output_result = file_output.file_outputter(self._data, the_filename, 'OVERWRITE')

      # (3) Send the signal of success
      if output_result[0] is None:
         self._controller.display_shown.emit()
      else:
         # TODO: raise some exception!
         pass
# End class Display ------------------------------------------------------------
