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
# vis
from controller import Controller



class Experimenter(Controller):
   '''
   This class handles input for a user's choice of Experiment and choice
   of associated Settings, then performs the experiment, returning the
   relevant Results object(s).
   '''


   def __init__(self):
      '''
      ???
      '''
      self._list_of_analyses = None
      self._analysis_settings = None
      # Obiously, this method isn't finished



   def catch_analyses(self, analyses_list):
      '''
      Slot for the VisSignals.analyzer_analyzed signal. This method is called
      when the Analyzer controller has finished analysis.

      The argument is a list of AnalysisRecord objects.
      '''
      self.list_of_analyses = analyses_list



   def run_experiment(self):
      '''
      Runs the currently-configured experiment(s).
      '''
      pass



   def change_setting(self, sett):
      '''
      Given a 2-tuple, where the first element is a string (setting name) and
      the second element is any type (setting value), make that setting refer
      to that value.
      '''
      pass
# End class Experimenter -------------------------------------------------------



class Experiment(object):
   '''
   Base class for all Experiments.
   '''



   def __init__(self, records, settings):
      '''
      Create a new Experiment.

      There are two argument, both of which are mandatory:
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object
      '''
      # NOTE: You do not need to reimplement this method for subclasses.
      super(Experiment, self).__init__()
      self._records = records
      self._settings = settings



   def perform():
      '''
      Perform the Experiment. This method is not called "run" to avoid possible
      confusion with the multiprocessing nature of Experiment subclasses.

      This method emits an Experimenter.experimented signal when it
      finishes.
      '''
      # NOTE: You must reimplement this method in subclasses.
      pass
# End class Experiment ---------------------------------------------------------



class IntervalsLists(Experiment):
   '''
   Prepares two lists of intervals: one of harmonic intervals, and the other of
   the melodic intervals that connect the lower voice of the harmonic intervals.

   This Experiment is useful for these Display classes:
   - spreadsheet
   - LilyPond annotated score

   Although the Experiment itself does not use NGram objects or deal with
   n-grams (only intervals), both output formats are useful for visual
   inspections that allow human to find n-grams.
   '''



   def __init__(self, records, settings):
      '''
      Create a new IntervalsLists

      There are two argument, both of which are mandatory:
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object

      The IntervalsSpreadsheet uses these settings:
      - 'quality' : boolean, whether to print or suppress quality
      - 'simple or compound' : whether to print intervals in their single-octave
         ('simple') or actual ('compound') form.
      -
      '''
      # NOTE: You do not need to reimplement this method for subclasses.
      super(Experiment, self).__init__()
      self._records = records
      self._settings = settings



   def perform():
      '''
      Perform the Experiment. This method is not called "run" to avoid possible
      confusion with the multiprocessing nature of Experiment subclasses.

      This method emits an Experimenter.experimented signal when it
      finishes.
      '''
      # NOTE: You must reimplement this method in subclasses.
      pass
# End class Experiment ---------------------------------------------------------
