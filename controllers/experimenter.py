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
from models import ngram
# music21
from music21.interval import Interval
from music21.note import Note
from music21 import chord
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
      if self._experiment_settings.get('experiment') == 'IntervalsList':
         exper = IntervalsLists(self._list_of_analyses, self._experiment_settings)
      elif self._experiment_settings.get('experiment') == 'ChordsList':
         exper = ChordsLists(self._list_of_analyses, self._experiment_settings)
      post = exper.perform()

      # TODO: figure out the valid types of display, and put them in a list in
      # the first element of this tuple
      post = (exper.good_for(), post)

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



   # List of strings that are the names of the Display objects suitable for this Experiment
   _good_for = ['None']



   def __init__(self, records, settings):
      '''
      Create a new Experiment.

      There are three mandatory arguments:
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object
      '''
      # NOTE: In subclasses, you should implement a check system to ensure the
      #       ExperimentSettings object has the right settings in it.
      super(Experiment, self).__init__()
      self._records = records
      self._settings = settings



   def good_for(self):
      '''
      Returns a list of string objects that are the names of the Display objects suitable for
      this Experiment
      '''
      # NOTE: You do not need to reimplement this method in subclasses.
      return self._good_for



   def perform(self):
      '''
      Perform the Experiment. This method is not called "run" to avoid possible
      confusion with the multiprocessing nature of Experiment subclasses.

      This method emits an Experimenter.experimented signal when it finishes.
      '''
      # NOTE: You must reimplement this method in subclasses.
      pass
# End class Experiment ---------------------------------------------------------



class IntervalsLists(Experiment):
   '''
   Prepare a list of 3-tuples:
   [(vertical_interval, horizontal_interval, offset),
    (vertical_interval, horizontal_interval, offset)]

   BUT: the first element in the ouputted list is a tuple of strings that represent descriptions
   of the data in each tuple index that are suitable for use in a spreadsheet.

   Each horizontal interval specifies the movement of the lower part in going to the following
   chord.

   This Experiment can be outputted by these Display classes:
   - SpreadsheetFile
   - LilyPondAnnotated

   Although the Experiment itself does not use NGram objects or deal with
   n-grams (only intervals), both output formats are useful for visual
   inspections that allow human to find n-grams.
   '''



   # List of strings that are the names of the Display objects suitable for this Experiment
   _good_for = ['SpreadsheetFile', 'LilyPondAnnotated']



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
      # Call the superclass constructor
      super(Experiment, self).__init__()
      # Check the ExperimentSettings object has the right settings
      if settings.has('quality') and settings.has('simple or compound'):
         self._records = records
         self._settings = settings
      else:
         msg = 'IntervalsLists requires "quality" and "simple or compound" settings'
         raise KeyError(msg)



   def perform(self):
      '''
      Perform the IntervalsLists Experiment.

      This method emits an Experimenter.experimented signal when it finishes.
      '''

      # pre-fetch the settings we'll be using repeatedly
      quality = self._settings.get('quality')
      interval_size = self._settings.get('simple or compound')

      def the_formatter(interv, direction=False):
         '''
         Formats an Interval object according to the preferences of "quality" and "interval_size."

         You can also specify a boolean for "direction," which indicates whether to show the
         direction of the interval (being a '+' for ascending or '-' for descending). The default
         is False.
         '''
         post = ''

         if direction:
            if 1 == interv.direction: post += '+'
            #elif -1 == interv.direction: post += '-'

         if quality:
            if interval_size == 'simple':
               post += interv.semiSimpleName
            else:
               post += interv.name
         else:
            if interval_size == 'simple':
               post += str(interv.generic.semiSimpleDirected)
            else:
               post += str(interv.generic.directed)

         return post
      # End sub-method the_formatter()

      # this is the header for CSV-format output
      data = [('vertical', 'horizontal', 'offset')]

      # loop through every AnalysisRecord
      for record in self._records:
         # loop through all the events... this use of zip() works like this:
         #    a_list = (1, 2, 3, 4)
         #    zip(a_list, list(a_list)[1:])
         #    ((1, 2), (2, 3), (3, 4))
         for first, second in zip(record, list(record)[1:]):
            offset = first[0]
            # lower note of the fist interval
            first_lower = first[1][0]
            # upper note of the first interval
            first_upper = first[1][1]
            # lower note of the second interval
            second_lower = second[1][0]

            # these will hold the intervals
            vertical, horizontal = None, None

            # If one of the notes is actually a 'Rest' then we can't use it, so skip it
            if 'Rest' == first_lower:
               vertical = 'Rest & ' + first_upper
               horizontal = 'N/A'
            elif 'Rest' == first_upper:
               vertical = first_lower + ' & Rest'
            else:
               # make the vertical interval, which connects first_lower and first_upper
               vertical = the_formatter(Interval(Note(first_lower), Note(first_upper)))

            if 'Rest' == second_lower:
               horizontal = 'N/A'
            elif horizontal is None:
               # make the horizontal interval, which connects first_lower and second_lower
               horizontal = the_formatter(Interval(Note(first_lower), Note(second_lower)), True)

            # make the 3-tuplet to append to the list
            put_me = (vertical, horizontal, offset)

            data.append(put_me)

         # finally, add the last row, which has no horizontal connection
         last = record[-1]
         last_vertical = the_formatter(Interval(Note(last[1][0]), Note(last[1][1])))
         data.append((last_vertical, None, last[0]))

      return data
# End class IntervalsLists -------------------------------------------------------------------------



class ChordsLists(Experiment):
   '''
   Prepare a list of 3-tuples:
   [(chord_name, neoriemannian_transformation, offset),
    (chord_name, neoriemannian_transformation, offset)]

   BUT: the first element in the ouputted list is a tuple of strings that represent descriptions
   of the data in each tuple index that are suitable for use in a spreadsheet.

   Each transformation specifies how to get to the following chord.

   This Experiment can be outputted by these Display classes:
   - SpreadsheetFile
   - LilyPondAnnotated

   The experiment uses ChordNGram objects to find the transformation.
   '''



   # List of strings that are the names of the Display objects suitable for this Experiment
   _good_for = ['SpreadsheetFile', 'LilyPondAnnotated']



   def __init__(self, records, settings):
      '''
      Create a new ChordsLists.

      There are two argument, both of which are mandatory:
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object
      '''
      # Call the superclass constructor
      super(Experiment, self).__init__()
      # Save things
      self._records = records
      self._settings = settings



   def perform(self):
      '''
      Perform the ChordsListsExperiment.

      This method emits an Experimenter.experimented signal when it finishes.
      '''

      # this is what we'll return
      post = [('chord', 'transformation', 'offset')]

      def remove_rests(event):
         post = ''

         for chord_member in event:
            if isinstance(chord_member, list):
               for inner_chord_member in chord_member:
                  post += inner_chord_member + ' '
            elif 'Rest' != chord_member:
               post += chord_member + ' '

         return post

      for record in self._records:
         for first, second in zip(record, list(record)[1:]):
            # find the offset
            offset = first[0]

            # hold the string-wise representation of the notes in the chords
            first_chord, second_chord = '', ''

            # prepare the string-wise representation of notes in the chords
            # NOTE: we have the inner isinstance() call because, if a Chord object is put here,
            #       it'll be as a tuple, rather than, like Note objects, as simply right there
            first_chord = remove_rests(first[1])
            second_chord = remove_rests(second[1])

            # ensure neither of the chords is just a REST... if it is, we'll skip this loop
            if '' == first_chord or '' == second_chord:
               continue

            transformer = ngram.ChordNGram([chord.Chord(first_chord), chord.Chord(second_chord)])

            the_chord = chord.Chord(first_chord)
            the_chord_name = the_chord.root().name + ' ' + the_chord.commonName
            # TODO: this next line without violating the object
            horizontal = transformer._list_of_connections[0]
            put_me = (the_chord_name, horizontal, offset)

            # add this chord-and-transformation to the list of all of them
            post.append(put_me)

         # finally, add the last chord, which doesn't have a transformation
         last = record[-1]
         last_chord = ''

         # prepare the string-wise representation of notes in the chords
         last_chord = remove_rests(last[1])

         # format and add the chord, but only if the previous step didn't turn everyting to rests
         if '' != last_chord:
            last_chord = chord.Chord(last_chord)
            last_chord_name = last_chord.root().name + ' ' + last_chord.commonName
            post.append((last_chord_name, None, last[0]))

      return post
# End class Experiment ---------------------------------------------------------
