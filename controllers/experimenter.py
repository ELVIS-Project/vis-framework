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
from models.experimenting import ExperimentSettings
# music21
from music21.interval import Interval
from music21.note import Note
# PyQt4
from PyQt4 import QtCore



class Experimenter(Controller, QtCore.QObject):
   '''
   This class handles input for a user's choice of Experiment and choice
   of associated Settings, then performs the experiment, returning the
   relevant Results object(s).
   '''



   # PyQt4 Signals
   # -------------
   # a 2-tuple: a string for a setting name and the value for the setting
   set = QtCore.pyqtSignal(tuple)
   # tell the Experimenter controller to perform an experiment
   run_experiment = QtCore.pyqtSignal()
   # the result of experimenter_experiment; the result is a tuple, where the
   # first element is the type of Display object to use, and the second is
   # whatever the Display object needs
   experiment_finished = QtCore.pyqtSignal(tuple)
   # description of an error in the Experimenter
   error = QtCore.pyqtSignal(str)
   # informs the GUI of the status for a currently-running experiment (if two
   # or three characters followed by a '%' then it should try to update a
   # progress bar, if available)
   status = QtCore.pyqtSignal(str)



   # List of the experiments we have
   experiments_we_have = ['IntervalsList']



   def __init__(self):
      '''
      Create a new Experimenter controller.
      '''
      super(Experimenter, self).__init__() # required for signals
      self._list_of_analyses = None
      self._experiment_settings = ExperimentSettings()
      # Signals
      self.set.connect(self._change_setting)
      self.run_experiment.connect(self._run_experiment)



   @QtCore.pyqtSlot(list)
   def catch_analyses(self, analyses_list):
      '''
      Slot for the Analyzer.analysis_finished signal. This method is called
      when the Analyzer controller has finished analysis.

      The argument is a list of AnalysisRecord objects.
      '''
      self._list_of_analyses = analyses_list



   @QtCore.pyqtSlot() # for Experimenter.run_experiment
   def _run_experiment(self):
      '''
      Runs the currently-configured experiment(s).
      '''
      # Check there is an 'experiment' setting that refers to one we have
      # TODO: plug it in
      # Trigger that experiment
      # TODO: run the right experiment
      il = IntervalsLists(self._list_of_analyses, self._experiment_settings)
      post = il.perform()

      # TODO: figure out the valid types of display, and put them in a list in
      # the first element of this tuple
      post = (['SpreadsheetDisplay'], post)

      self.experiment_finished.emit(post)



   #def get_setting(self, sett):
      #'''
      #Returns the value of the setting whose `name` field is equal to `sett`.
      #'''
      #matches = [s for s in self._settings if s.name == sett]
      #if matches:
         #return matches[0].value



   @QtCore.pyqtSlot(tuple) # for Experimenter.set
   def _change_setting(self, sett):
      '''
      Given a 2-tuple, where the first element is a string (setting name) and
      the second element is any type (setting value), make that setting refer
      to that value.
      '''
      self._experiment_settings.set(sett[0], sett[1])
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
      # NOTE: In subclasses, you should implement a check system to ensure the
      #       ExperimentSettings object has the right settings in it.
      super(Experiment, self).__init__()
      self._records = records
      self._settings = settings



   def perform(self):
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
      Create a new IntervalsLists.

      There are two argument, both of which are mandatory:
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object

      The IntervalsSpreadsheet uses these settings:
      - 'quality' : boolean, whether to print or suppress quality
      - 'simple or compound' : whether to print intervals in their single-octave
         ('simple') or actual ('compound') form.
      '''
      # Check the ExperimentSettings object has the right settings
      if settings.has('quality') and settings.has('simple or compound'):
         self._records = records
         self._settings = settings
      else:
         msg = 'IntervalsLists requires "quality" and "simple or compound" settings'
         raise KeyError(msg)



   def perform(self):
      # TODO: write documentation and comments
      data = 'vertical, horizontal, offset\n'
      print('number of records: ' + str(len(self._records))) # DEBUGGING
      for record in self._records:
         for first, second in zip(record,list(record)[1:]):
            offset = first[0]
            first_lower = first[1][0]
            first_upper = first[1][1]
            second_lower = second[1][0]

            vertical = Interval(Note(first_lower), Note(first_upper))
            horizontal = Interval(Note(first_lower), Note(second_lower))
            put_me = ''
            if self._settings.get('quality'):
               if self._settings.get('simple or compound') == 'simple':
                  put_me = vertical.semiSimpleName + ', ' + \
                           horizontal.semiSimpleName + ', ' + \
                           str(offset) + '\n'
               else:
                  put_me = vertical.name + ', ' + \
                           horizontal.name + ', ' + \
                           str(offset) + '\n'
            else:
               if self._settings.get('simple or compound') == 'simple':
                  put_me = str(vertical.generic.semiSimpleDirected) + ', ' + \
                           str(horizontal.generic.semiSimpleDirected) + ', ' + \
                           str(offset) + '\n'
               else:
                  put_me = str(vertical.generic.directed) + ', ' + \
                           str(horizontal.generic.directed) + ', ' + \
                           str(offset) + '\n'

            data += put_me
         # TODO: Then add the last row
      return data
# End class Experiment ---------------------------------------------------------
