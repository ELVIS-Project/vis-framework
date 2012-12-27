#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: Experimenter.py
# Purpose: Holds the Experimenter controller.
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
Holds the Experimenter controller.
'''



# Imports from...
# PyQt4
from PyQt4.QtCore import pyqtSignal, QObject
# vis
from controller import Controller
from vis_controller import VisSignals



class Experimenter(Controller):
   '''
   This class handles input for a user's choice of Experiment and choice
   of associated Settings, then performs the experiment, returning the
   relevant Results object(s).
   '''


   def __init__(self):
      self.list_of_analyses = None



   def setup_signals(self):
      '''
      Set the methods of Experimenter as slots for the relevant methods emitted
      by the VisController.
      '''
      VisSignals.analyzer_analyzed.connect(self.catch_analyses)



   @pyqtSlot(list)
   def catch_analyses(self, analyses_list):
      '''
      Slot for the VisSignals.analyzer_analyzed signal. This method is called
      when the Analyzer controller has finished analysis.

      The argument is a list of AnalysisRecord objects.
      '''
      self.list_of_analyses = analyses_list

   # TODO: etc.
# End class Experimenter -------------------------------------------------------
