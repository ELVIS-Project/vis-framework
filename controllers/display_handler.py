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
# PyQt4
from PyQt4.QtCore import pyqtSignal, QObject
# vis
from controller import Controller
from vis_controller import VisSignals



class DisplayHandler(Controller):
   '''
   This class handles input for a user's choice of Settings and takes the
   results of an Experiment, formats them according to the user's choices
   and displays them in the appropriate view.
   '''
   def __init__(self, stylesheet, results):
      '''
      Creates a new DisplayHandler instance

      INPUTS:
      results - a Results object containing data for the results of an
      Experiment
      '''
      super(DisplayHandler, self).__init__()
      self._stylesheet = stylesheet
      self._results = results

   def setup_signals(self):
      VisSignals.display_results.connect(self.display_results)
