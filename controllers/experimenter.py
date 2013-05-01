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
from controller import Controller
from models.settings import Settings
from models import ngram
from models import experimenting



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



   # List of the experiments we have
   # TODO: do this with introspection so we don't have to update things
   # in multiple places when these change.
   experiments_we_have = ['IntervalsList', 'ChordsList']



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
      self.status.emit('Waiting on DisplayHandler')

      # Make and emit the tuple for the DisplayHandler
      self.experiment_finished.emit((self._exper_result, experiment_result.toPyObject()))



   @QtCore.pyqtSlot() # for Experimenter.run_experiment
   def _run_experiment(self):
      '''
      Runs the currently-configured experiment(s).
      '''
      # Check there is an 'experiment' setting that refers to one we have
      
      namespace = [getattr(experimenting, s) for s in dir(experimenting)]
      classes = [c for c in namespace if isinstance(c, type)]
      experiments = [e.__name__ for e in classes if experimenting.Experiment in e.__bases__]
      exper = self._experiment_settings.experiment
      if exper in experiments:
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



class Experiment(QtCore.QRunnable):
   # NOTE: in subclasses, change "QtCore.QRunnable" to "Experiment"
   '''
   Base class for all Experiments.
   '''



   # List of strings that are the names of the Display objects suitable for this Experiment
   _good_for = ['None']



   def __init__(self, controller, records, settings):
      '''
      Create a new Experiment.

      There are three mandatory arguments:
      - controller : the Experimenter object to which this Experiment belongs
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object
      '''
      # NOTE: In subclasses, you should implement a check system to ensure the
      #       ExperimentSettings object has the right settings in it. If you do
      #       not have the settings you need, send an error through the
      #       Experimenter controller, then return without proper instantiation:
      # self._controller.error.emit(error_message_here)
      # return
      # NOTE: In subclasses, the following line should be like this:
      #       super(SubclassName, self).__init__(records, settings)
      super(Experiment, self).__init__()
      self._controller = controller
      self._records = records
      self._settings = settings



   def good_for(self):
      '''
      Returns a list of string objects that are the names of the Display objects suitable for
      this Experiment
      '''
      # NOTE: You do not need to reimplement this method in subclasses.
      return self._good_for



   def run(self):
      '''
      Just starts the perform() method.
      '''
      # NOTE: You do not need to reimplement this method in subclasses.
      # Collect the results of perform(), then emit the signal that sends them to the Experimenter
      signal_me = self.perform()
      self._controller._experiment_results.emit(QtCore.QVariant(signal_me))



   def perform(self):
      '''
      Perform the Experiment. This method is not called "run" to avoid possible
      confusion with the multiprocessing nature of Experiment subclasses.

      This method emits an Experimenter.experimented signal when it finishes.
      '''
      # NOTE: You must reimplement this method in subclasses.
      pass
# End class Experiment -----------------------------------------------------------------------------



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



   def __init__(self, controller, records, settings):
      '''
      Create a new IntervalsLists.

      There are three mandatory arguments:
      - controller : the Experimenter object to which this Experiment belongs
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object

      The IntervalsSpreadsheet uses these settings:
      - 'quality' : boolean, whether to print or suppress quality
      - 'simple or compound' : whether to print intervals in their single-octave
         ('simple') or actual ('compound') form.

      If one of these settings is not present, the constructor raises a KeyError.

      IntervalsLists can use this setting, but will not provide a default:
      - output format : choose the Display subclass for this experiment's results
      '''
      # Call the superclass constructor
      super(IntervalsLists, self).__init__(controller, records, settings)

      # Check the ExperimentSettings object has the right settings
      if not settings.has('quality') or not settings.has('simple or compound'):
         msg = 'IntervalsLists requires "quality" and "simple or compound" settings'
         raise KeyError(msg)

      # Process the optional "output format" setting
      if self._settings.has('output format'):
         self._good_for = [self._settings.get('output format')]
   # End __init__()



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
            if 1 == interv.direction:
               post += '+'

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



   def __init__(self, controller, records, settings):
      '''
      Create a new ChordsLists.

      There are three mandatory arguments:
      - controller : the Experimenter object to which this Experiment belongs
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object

      ChordsLists can use this setting, but will not provide a default:
      - output format : choose the Display subclass for this experiment's results
      '''
      # Call the superclass constructor
      super(ChordsLists, self).__init__(controller, records, settings)

      # Process the optional "output format" setting
      if self._settings.has('output format'):
         self._good_for = [self._settings.get('output format')]



   def perform(self):
      '''
      Perform the ChordsListsExperiment.

      This method emits an Experimenter.experimented signal when it finishes.
      '''

      # this is what we'll return
      post = [('chord', 'transformation', 'offset')]

      def remove_rests(event):
         '''
         Removes 'Rest' strings from a list of strings.
         '''
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

            the_chord = chord.Chord(first_chord)
            the_chord_name = the_chord.root().name + ' ' + the_chord.commonName
            horizontal = ngram.ChordNGram.find_transformation(chord.Chord(first_chord),
                                                              chord.Chord(second_chord))
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
# End class ChordsLists ----------------------------------------------------------------------------



class IntervalsStatistics(Experiment):
   '''
   Experiment that gathers statistics about the number of occurrences of vertical intervals.

   Produce a list of tuples, like this:
   [('m3', 10), ('M3', 4), ...]

   The list is sorted as per the ExperimentSettings. Each 0th element in the tuple is a
   string-format representation of an interval, and each 1st element is the number of occurrences.

   Intervals that do not occur in any of the AnalysisRecord objects are not included in the output.
   '''



   # List of strings that are the names of the Display objects suitable for this Experiment
   _good_for = ['StatisticsListDisplay', 'StatisticsChartDisplay']



   def __init__(self, controller, records, settings):
      '''
      Create a new IntervalsStatistics experiment.

      There are three mandatory arguments:
      - controller : the Experimenter object to which this Experiment belongs
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object

      IntervalsStatistics requires these settings:
      - quality : whether or not to display interval quality
      - simple or compound : whether to use simple or compound intervals

      IntervalsStatistics uses these settings, but provides defaults:
      - topX : display on the "top X" number of results (default: none)
      - threshold : stop displaying things after this point (default: none)
      - sort order : whether to sort things 'ascending' or 'descending' (default: 'descending')
      - sort by : whether to sort things by 'frequency' or 'name' (default: 'frequency')

      IntervalsStatistics can use this setting, but will not provide a default:
      - output format : choose the Display subclass for this experiment's results
      '''
      super(IntervalsStatistics, self).__init__(controller, records, settings)

      # Check the ExperimentSettings object has the right settings
      if not settings.has('quality') or not settings.has('simple or compound'):
         msg = 'IntervalsStatistics requires "quality" and "simple or compound" settings'
         raise KeyError(msg)

      # Check for the other settings we use, and provide default values if required
      if not self._settings.has('topX'):
         self._settings.set('topX', None)
      if not self._settings.has('threshold'):
         self._settings.set('threshold', None)
      if not self._settings.has('sort order'):
         self._settings.set('sort order', 'descending')
      if not self._settings.has('sort by'):
         self._settings.set('sort by', 'frequency')

      # Make a dictionary to store the intervals
      self._intervals = None

      # Make a list to store the sorted and filtered intervals
      self._keys = None

      # Process the optional "output format" setting
      if self._settings.has('output format'):
         self._good_for = [self._settings.get('output format')]
   # End __init__()



   def _add_interval(self, interv):
      '''
      Add an interval, represented as a string, to the occurrences dictionary in this experiment.
      '''
      if interv in self._intervals:
         self._intervals[interv] += 1
      else:
         self._intervals[interv] = 1



   @staticmethod
   def interval_sorter(left, right):
      '''
      Returns -1 if the first argument is a smaller interval.
      Returns 1 if the second argument is a smaller interval.
      Returns 0 if both arguments are the same.

      Input should be a str of the following form:
      - d, m, M, or A
      - an int

      Examples:
      >>> from vis import interval_sorter
      >>> interval_sorter( 'm3', 'm3' )
      0
      >>> interval_sorter( 'm3', 'M3' )
      1
      >>> interval_sorter( 'A4', 'd4' )
      -1
      '''

      string_digits = '0123456789'
      list_of_directions = ['+', '-']

      # I want to sort based on generic size, so the direction is irrelevant. If
      # we have directions, they'll be removed with this. If we don't have
      # directions, this will have no effect.
      for direct in list_of_directions:
         left = left.replace( direct, '' )
         right = right.replace( direct, '' )

      # If we have numbers with no qualities, we'll just add a 'P' to both, to
      # pretend they have the same quality (which, as far as we know, they do).
      if left[0] in string_digits and right[0] in string_digits:
         left = 'P' + left
         right = 'P' + right

      # Comparisons!
      if left == right:
         post = 0
      elif int(left[1:]) < int(right[1:]): # if x is generically smaller
         post = -1
      elif int(left[1:]) > int(right[1:]): # if y is generically smaller
         post = 1
      else: # otherwise, we're down to the species/quality
         left_qual = left[0]
         right_qual = right[0]
         if left_qual == 'd':
            post = -1
         elif right_qual == 'd':
            post = 1
         elif left_qual == 'A':
            post = 1
         elif right_qual == 'A':
            post = -1
         elif left_qual == 'm':
            post = -1
         elif right_qual == 'm':
            post = 1
         else:
            post = 0

      return post
   # End IntervalsStatistics.interval_sorter() ---------------------------------



   def perform(self):
      '''
      Perform the Experiment. This method is not called "run" to avoid possible
      confusion with the multiprocessing nature of Experiment subclasses.

      This method emits an Experimenter.experimented signal when it finishes.
      '''
      # (0) Instantiate/clear things
      self._intervals = {}
      self._keys = []

      # (1) Loop through each of the AnalysisRecord objects, adding the intervals we find.
      # We'll use these over and over again
      quality = self._settings.get('quality')
      interval_size = self._settings.get('simple or compound')

      for each_record in self._records:
         for each_event in each_record:
            # make sure we don't try to make an Interval from a rest
            if 'Rest' != each_event[1][0] and 'Rest' != each_event[1][1]:
               interv = Interval(Note(each_event[1][0]), Note(each_event[1][1]))
            else:
               continue

            if quality:
               if interval_size == 'simple':
                  self._add_interval(interv.semiSimpleName)
               else:
                  self._add_interval(interv.name)
            else:
               if interval_size == 'simple':
                  self._add_interval(str(interv.generic.semiSimpleDirected))
               else:
                  self._add_interval(str(interv.generic.directed))

      # (2.1) If there is a topX or threshold filter, sort by frequency now.
      if self._settings.get('topX') is not None or \
      self._settings.get('threshold') is not None:
         # returns a list of keys, sorted by descending frequency
         self._keys = sorted(self._intervals, key=lambda x:self._intervals[x], reverse=True)

         # (3) If we're doing a "topX" filter, do it now.
         if self._settings.get('topX') is not None:
            # cut the list at the "topX-th element"
            self._keys = self._keys[:int(self._settings.get('topX'))]

         # (4) If we're doing a "threshold" filter, do it now.
         if self._settings.get('threshold') is not None:
            thresh = int(self._settings.get('threshold'))
            # if the last key on the list is already greater than the threshold, we won't sort
            if self._intervals[self._keys[-1]] < thresh:
               # hold the keys of intervals above the threshold
               new_keys = []
               # check each key we already have, and add it to new_keys only if its occurrences are
               # above the threshold value
               for each_key in self._keys:
                  if self._intervals[each_key] >= thresh:
                     new_keys.append(each_key)
               # assign
               self._keys = new_keys
      # (2.2) Otherwise, just get all the keys
      else:
         self._keys = self._intervals.keys()

      # (4) Now do a final sorting.
      # Should we 'reverse' the list sorting? Yes, unless we sorted 'ascending'
      should_reverse = False if 'ascending' == self._settings.get('sort order') else True

      if 'frequency' == self._settings.get('sort by'):
         self._keys = sorted(self._keys,
                             key=lambda x:self._intervals[x],
                             reverse=should_reverse)
      else:
         self._keys = sorted(self._keys,
                             cmp=IntervalsStatistics.interval_sorter,
                             reverse=should_reverse)

      # (5) Construct the dictionary to return
      post = []
      for each_key in self._keys:
         post.append((each_key, self._intervals[each_key]))

      # (6) Conclude
      return post
# End class IntervalsStatistics --------------------------------------------------------------------



class IntervalNGramStatistics(Experiment):
   '''
   Experiment that gathers statistics about the number of occurrences of n-grams composed of
   vertical intervals and the horizontal connections between the lower voice.

   Produce a list of tuples, like this:
   [('m3 -P4 M6', 10), ('M3 -P4 m6', 4), ...]

   The list is sorted as per the ExperimentSettings. Each 0th element in the tuple is a
   string-format representation of an interval, and each 1st element is the number of occurrences.

   Intervals that do not occur in any of the AnalysisRecord objects are not included in the output.
   '''



   # List of strings that are the names of the Display objects suitable for this Experiment
   _good_for = ['StatisticsListDisplay', 'StatisticsChartDisplay', 'GraphDisplay']



   def __init__(self, controller, records, settings):
      '''
      Create a new IntervalNGramStatistics experiment.

      There are three mandatory arguments:
      - controller : the Experimenter object to which this Experiment belongs
      - records : a list of AnalysisRecord objects
      - settings : an ExperimentSettings object

      IntervalNGramStatistics requires these settings:
      - quality : whether or not to display interval quality
      - simple or compound : whether to use simple or compound intervals
      - values of n : a list of ints that is the values of 'n' to display

      IntervalNGramStatistics uses these settings, but provides defaults:
      - topX : display on the "top X" number of results (default: none)
      - threshold : stop displaying things after this point (default: none)
      - sort order : whether to sort things 'ascending' or 'descending' (default: 'descending')
      - sort by : whether to sort things by 'frequency' or 'name' (default: 'frequency')

      IntervalNGramStatistics can use this setting, but will not provide a default:
      - output format : choose the Display subclass for this experiment's results
      '''
      super(IntervalNGramStatistics, self).__init__(controller, records, settings)

      # Check the ExperimentSettings object has the right settings
      if not settings.has('quality') or not settings.has('simple or compound') or \
      not settings.has('values of n'):
         msg = 'IntervalNGramStatistics requires "quality," '
         msg += '"simple or compound," and "values of n" settings'
         raise KeyError(msg)

      # Check for the other settings we use, and provide default values if required
      if not self._settings.has('topX'):
         self._settings.set('topX', None)
      if not self._settings.has('threshold'):
         self._settings.set('threshold', None)
      if not self._settings.has('sort order'):
         self._settings.set('sort order', 'descending')
      if not self._settings.has('sort by'):
         self._settings.set('sort by', 'frequency')

      # Make a dictionary to store the intervals
      self._ngrams = None

      # Make a list to store the sorted and filtered intervals
      self._keys = None

      # Process the optional "output format" setting
      if self._settings.has('output format'):
         self._good_for = [self._settings.get('output format')]
   # End __init__()



   def _add_ngram(self, interv):
      '''
      Add an n-gram, represented as a string, to the occurrences dictionary in this experiment.
      '''
      if interv in self._ngrams:
         self._ngrams[interv] += 1
      else:
         self._ngrams[interv] = 1



   # TODO: implement vis7 tests for this
   @staticmethod
   def ngram_sorter(left, right):
      '''
      Returns -1 if the first argument is a smaller n-gram.
      Returns 1 if the second argument is a smaller n-gram.
      Returns 0 if both arguments are the same.

      If one n-gram is a subset of the other, starting at index 0, we consider the
      shorter n-gram to be the "smaller."

      Input should be like this, at minimum with three non-white-space characters
      separated by at most one space character.
      3 +4 7
      m3 +P4 m7
      -3 +4 1
      m-3 +P4 P1

      Examples:
      >>> from vis import ngram_sorter
      >>> ngram_sorter( '3 +4 7', '5 +2 4' )
      -1
      >>> ngram_sorter( '3 +5 6', '3 +4 6' )
      1
      >>> ngram_sorter( 'M3 1 m2', 'M3 1 M2' )
      -1
      >>> ngram_sorter( '9 -2 -3', '9 -2 -3' )
      0
      >>> ngram_sorter( '3 -2 3 -2 3', '6 +2 6' )
      -1
      >>> ngram_sorter( '3 -2 3 -2 3', '3 -2 3' )
      1
      '''

      # We need the string version for this
      left = str(left)
      right = str(right)

      # Just in case there are some extra spaces
      left = left.strip()
      right = right.strip()

      # See if we have only one interval left. When there is only one interval,
      # the result of this will be -1
      left_find = left.find(' ')
      right_find = right.find(' ')

      if -1 == left_find:
         if -1 == right_find:
            # Both x and y have only one interval left, so the best we can do is
            # the output from intervalSorter()
            return IntervalsStatistics.interval_sorter(left, right)
         else:
            # x has one interval left, but y has more than one, so x is shorter.
            return -1
      elif -1 == right_find:
         # y has one interval left, but x has more than one, so y is shorter.
         return 1

      # See if the first interval will differentiate
      possible_result = IntervalsStatistics.interval_sorter(left[:left_find], right[:right_find])

      if 0 != possible_result:
         return possible_result

      # If not, we'll rely on ourselves to solve the next mystery!
      return IntervalNGramStatistics.ngram_sorter(left[left_find + 1:], right[right_find + 1:])
   # End IntervalNGramStatistics.ngram_sorter() --------------------------------



   def perform(self):
      '''
      Perform the Experiment. This method is not called "run" to avoid possible
      confusion with the multiprocessing nature of Experiment subclasses.

      This method emits an Experimenter.experimented signal when it finishes.
      '''
      # (0) Instantiate/clear things
      self._ngrams = {}
      self._keys = []

      # (1) Loop through each of the AnalysisRecord objects, adding the n-grams we find.
      # We'll use these over and over again
      quality = self._settings.get('quality')
      interval_size = self._settings.get('simple or compound')
      values_of_n = sorted(self._settings.get('values of n')) # sorted lowest-to-highest

      for each_record in self._records:
         for i in xrange(len(each_record)):
            # store the last index in this record, so we know if we're about to cause an IndexError
            last_index = len(each_record) - 1

            # make sure our first vertical interval doesn't have a rest
            if 'Rest' == each_record[i][1][0] or 'Rest' == each_record[i][1][1]:
               continue

            # for the next loop, we'll use this to indicate that the current and all higher
            # values of 'n' do not have enough vertical intervals without rests
            kill_switch = False

            # for each of the values of 'n' we have to find:
            for each_n in values_of_n:
               # start of the intervals to build the n-gram with this 'n' value
               intervals_this_n = [Interval(Note(each_record[i][1][0]), Note(each_record[i][1][1]))]

               # reset the kill_switch
               kill_switch = False

               # - first check if there are enough vertical intervals without rests
               #   (if not, we'll skip this and all higher 'n' values with "kill_switch")
               for j in xrange(1, each_n):
                  # this first check will ensure we don't cause an IndexError going past the end
                  # of the list
                  if i+j > last_index:
                     kill_switch = True
                     break
                  # now check for rests
                  elif 'Rest' == each_record[i+j][1][0] or 'Rest' == each_record[i+j][1][1]:
                     kill_switch = True
                     break
                  # now assume we can make an n-gram
                  else:
                     this_interv = Interval(Note(each_record[i+j][1][0]),
                                            Note(each_record[i+j][1][1]))
                     intervals_this_n.append(this_interv)
               if kill_switch:
                  break

               # - build the n-gram
               this_ngram = ngram.IntervalNGram(intervals_this_n)

               # - find the n-gram's string-wise representation
               # - add the representation to the occurrences dictionary
               self._add_ngram(this_ngram.get_string_version(quality, interval_size))
      # (End of step 1)


      # (2.1) If there is a topX or threshold filter, sort by frequency now.
      if self._settings.get('topX') is not None or \
      self._settings.get('threshold') is not None:
         # returns a list of keys, sorted by descending frequency
         self._keys = sorted(self._ngrams, key=lambda x:self._ngrams[x], reverse=True)

         # (3) If we're doing a "topX" filter, do it now.
         if self._settings.get('topX') is not None:
            # cut the list at the "topX-th element"
            self._keys = self._keys[:int(self._settings.get('topX'))]

         # (4) If we're doing a "threshold" filter, do it now.
         if self._settings.get('threshold') is not None:
            thresh = int(self._settings.get('threshold'))
            # if the last key on the list is already greater than the threshold, we won't sort
            if self._ngrams[self._keys[-1]] < thresh:
               # hold the keys of intervals above the threshold
               new_keys = []
               # check each key we already have, and add it to new_keys only if its occurrences are
               # above the threshold value
               for each_key in self._keys:
                  if self._ngrams[each_key] >= thresh:
                     new_keys.append(each_key)
               # assign
               self._keys = new_keys
      # (2.2) Otherwise, just get all the keys
      else:
         self._keys = self._ngrams.keys()

      # (4) Now do a final sorting.
      # Should we 'reverse' the list sorting? Yes, unless we sorted 'ascending'
      should_reverse = False if 'ascending' == self._settings.get('sort order') else True

      if 'frequency' == self._settings.get('sort by'):
         self._keys = sorted(self._keys,
                             key=lambda x:self._ngrams[x],
                             reverse=should_reverse)
      else:
         self._keys = sorted(self._keys,
                             cmp=IntervalsStatistics.interval_sorter,
                             reverse=should_reverse)

      # (5) Construct the dictionary to return
      post = []
      for each_key in self._keys:
         post.append((each_key, self._ngrams[each_key]))

      # (6) Conclude
      return post
# End class IntervalNGramStatistics ----------------------------------------------------------------
