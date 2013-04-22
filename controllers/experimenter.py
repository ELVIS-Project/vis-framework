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
from PyQt4 import QtCore
# vis
from models.settings import Settings
from models import ngram
from models import experimenting



class Experimenter(QtCore.QObject):
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
   # Emitted by the Experimenter when the experiment is finished. The argument is a tuple, where
   # the first element is the type of Display object to use, and the second is the data required
   # by the Display object.
   experiment_finished = QtCore.pyqtSignal(tuple)
   # description of an error in the Experimenter
   error = QtCore.pyqtSignal(str)
   # informs the GUI of the status for a currently-running experiment (if two
   # or three characters followed by a '%' then it should try to update a
   # progress bar, if available)
   status = QtCore.pyqtSignal(str)
   # Emitted by an Experiment when it's finished. The argument should be a QVariant that holds
   # whatever type is required by the relevant Display class.
   _experiment_results = QtCore.pyqtSignal(QtCore.QVariant)



   def __init__(self):
      '''
      Create a new Experimenter controller.
      '''
      super(Experimenter, self).__init__() # required for signals
      self._list_of_analyses = None
      self._experiment_settings = Settings()
      # Signals
      self.set.connect(self._change_setting)
      self.run_experiment.connect(self._run_experiment)
      self._experiment_results.connect(self._catch_experiments)
      # Hold the result emitted by an Experiment when it's finished
      self._exper_result = None
      # look into models.experimenting and find the names of Experiments
      namespace = [getattr(experimenting, s) for s in dir(experimenting)]
      classes = [c for c in namespace if isinstance(c, type)]
      experiments = [e for e in classes if experimenting.Experiment in e.__bases__]
      self.available_experiments = experiments

   def set_experiment(self):
      '''
      Method docstring
      '''
      pass



   @QtCore.pyqtSlot(list)
   def catch_analyses(self, analyses_list):
      '''
      Slot for the Analyzer.analysis_finished signal. This method is called
      when the Analyzer controller has finished analysis.

      The argument is a list of AnalysisRecord objects.
      '''
      self._list_of_analyses = analyses_list



   @QtCore.pyqtSlot(QtCore.QVariant)
   def _catch_experiments(self, experiment_result):
      '''
      Slot for the Experimenter._experiment_results signal. Catches the result, converts it to a
      python object, then assigns it to the Experimenter._exper_result instance variable.

      The argument is a QVariant object.
      '''
      # Update the status
      self.status.emit('100')
      self.status.emit('Waiting on Visualizer')

      # Make and emit the tuple for the Visualizer
      self.experiment_finished.emit((self._exper_result, experiment_result.toPyObject()))



   @QtCore.pyqtSlot() # for Experimenter.run_experiment
   def _run_experiment(self):
      '''
      Runs the currently-configured experiment(s).
      '''
      # Check there is an 'experiment' setting that refers to one we have
      exper = self._experiment_settings.experiment
      if exper in [e.__name__ for e in self.available_experiments]:
         exper = getattr(experimenting, exper)
      else:
         self.error.emit('Experimenter: could not determine which experiment to run.')
         return

      # Trigger the experiment
      try:
         exper = exper(self, self._list_of_analyses, self._experiment_settings)
      except KeyError as kerr:
         # If the experiment doesn't have the Settings it needs
         self.error.emit(kerr.message)
         return

      # Get the preferred (or possible) Display subclasses for this Experiment
      self._exper_result = exper.good_for()

      # add to the QThreadPool
      QtCore.QThreadPool.globalInstance().start(exper)
      self.status.emit('0')
      self.status.emit('Experiment running... the progress bar will not be updated.')
   # End _run_experiment() -----------------------------------------------------



   @QtCore.pyqtSlot(tuple) # for Experimenter.set
   def _change_setting(self, sett):
      '''
      Given a 2-tuple, where the first element is a string (setting name) and
      the second element is any type (setting value), make that setting refer
      to that value.
      '''
      name, value = sett
      setattr(self._experiment_settings, name, value)
# End class Experimenter ---------------------------------------------------------------------------
