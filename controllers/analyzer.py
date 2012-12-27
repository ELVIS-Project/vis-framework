#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: Analyzer.py
# Purpose: Holds the Analyzer controller.
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
Holds the Analyzer controller.
'''



# Imports from...
# PyQt4
from PyQt4.QtCore import pyqtSignal, QObject
# vis
from controller import Controller
from models.analyzer import ListOfPieces



class Analyzer(Controller):
   '''
   This class performs analysis for series of vertical intervals, and manages
   the settings with which to analyze. Makes a list of AnalysisRecord objects
   that each holds a half-analyzed voice-pair that Experimenter will use to
   perform fuller analysis.

   The ListOfPieces model is always stored in the list_of_pieces property.
   '''



   def __init__(self, pieces, *args):
      '''
      Create a new Analyzer instance.

      The first arguent, "pieces", must be a ListOfPieces object, as created
      by the Importer controller.
      '''
      self.list_of_pieces = None



   def setup_signals(self):
      '''
      Set the methods of Analyzer as slots for the relevant methods emitted by
      the VisController.
      '''
      VisSignals.importer_imported.connect(self.catch_import)



   @pyqtSlot(ListOfPieces)
   def catch_import(self, pieces_list):
      '''
      Slot for the VisSignals.importer_imported signal. This method is called
      when the Importer controller has finished importing the list of pieces.

      The argument is a ListOfPieces object.
      '''
      self.list_of_pieces = pieces_list



   def set_data(self, index, change_to):
      '''
      Changes the data in a cell of the ListOfPieces model.

      The arguments here should be the same as sent to ListOfPieces.setData().
      '''
      pass



   def run_analysis(self):
      '''
      Runs the analysis specified in the ListOfPieces. Produces an
      AnalysisRecord object for each voice pair analyzed.

      Emits the VisSignal.analyzer_error signal if there is a problem, and
      continues to process.

      Emits the VisSignal.analyzer_analyzed signal upon completion, with a list
      of the AnalysisRecord objects generated.
      '''
      pass



   @staticmethod
   def _event_finder(parts, types, offset, salami, record):
      '''
      Find events in parts.

      These are the arguments:
      - parts : a list of at least one music21 Part object
      - types : a list of types that you want to count as an "event"
      - offset : the minimum quarterLength offset between consecutive events
      - salami : if True, all events will be the offset distance from each
         other, even if this produces a series of identical events
      - record : an AnalysisRecord object to use for recording this analysis

      This method is intended to analyze more than one part, finding
      simultaneous occurrences of "events," as determined by whether a thing
      in the part is an instance of one of the classes or types supplied.

      The method checks at every offset that is divisisble by "offset" without
      remainder. If "salami" is True, every such offset will have an event--if
      no new event has happened, the previous event is repeated. If "salami" is
      False, no events will be repeated, leading to unequal offset intervals
      between consecutive events in the AnalysisRecord.

      If given only one Part object, event_finder() acts essentially like an
      overly-complicated filter.

      This method should only be called from the Analyzer.run_analysis() method,
      which coordinates multiprocessing.
      '''
      pass
# End class Analyzer -----------------------------------------------------------
