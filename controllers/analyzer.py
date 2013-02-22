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
# Python
#from multiprocessing import Process # NB: commented because we aren't multiprocessing yet
# music21
from music21 import note
# PyQt4
from PyQt4 import QtCore
# vis
from controller import Controller
from models.analyzing import ListOfPieces, AnalysisRecord, AnalysisSettings



class Analyzer(Controller):
   '''
   This class performs analysis for series of vertical intervals, and manages
   the settings with which to analyze. Makes a list of AnalysisRecord objects
   that each holds a half-analyzed voice-pair that Experimenter will use to
   perform fuller analysis.

   The ListOfPieces model is always stored in the list_of_pieces property.
   '''



   # PyQt4 Signals
   # -------------
   # Change the data of a cell in the ListOfPieces; the GUI will know how to
   # create an index based on which rows are selected and which data is being
   # changed (cross-referenced with the ListOfPieces' declaration of
   # column indices)
   change_settings = QtCore.pyqtSignal(QtCore.QModelIndex, QtCore.QVariant)
   # description of an error in the Analyzer
   error = QtCore.pyqtSignal(str)
   # to tell the Analyzer controller to perform analysis
   run_analysis = QtCore.pyqtSignal()
   # the result of analyzer_analyze; the result is a list of AnalysisRecord objects
   analysis_finished = QtCore.pyqtSignal(list)
   # informs the GUI of the status for a currently-running analysis (if two
   # or three characters followed by a '%' then it should try to update a
   # progress bar, if available)
   status = QtCore.pyqtSignal(str)
   # For internal use...
   # When _event_finder() finished, it emits this signal
   event_finder_finished = QtCore.pyqtSignal(AnalysisRecord)



   def __init__(self):
      '''
      Create a new Analyzer instance.
      '''
      # signals
      super(Analyzer, self).__init__() # required for signals
      # other things
      self._list_of_pieces = ListOfPieces()
      self._list_of_analyses = []



   def setup_signals(self):
      self.event_finder_finished.connect(self._part_combo_finished)
      self.run_analysis.connect(self.analyze_pieces)
      self.change_settings.connect(self.set_data)



   @QtCore.pyqtSlot(AnalysisRecord)
   def _part_combo_finished(self, this_record):
      '''
      For internal use.

      Called when the _event_finder() has finished with a parts combination.
      This method adds the resulting AnalysisRecord to the internal list of
      analyses, then emits Analyzer.status and, if appropriate,
      Analyzer.analysis_finished.
      '''
      self._list_of_analyses.append(this_record)



   @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QVariant)
   def set_data(self, index, change_to):
      '''
      Changes the data in a cell of the ListOfPieces model.

      The arguments here should be the same as sent to ListOfPieces.setData().
      '''
      self._list_of_pieces.setData(index, change_to, QtCore.Qt.EditRole)



   @staticmethod
   def calculate_all_combos(upto):
      '''
      Calculate all combinations of integers between 0 and the argument.

      Includes a 0th item... the argument should be len(whatevs) - 1.
      '''
      post = []

      for left in xrange(upto):
         for right in xrange(left+1, upto+1):
            post.append([left, right])

      return post



   @QtCore.pyqtSlot()
   def analyze_pieces(self):
      '''
      Runs the analysis specified in the ListOfPieces. Produces an
      AnalysisRecord object for each voice pair analyzed.

      Emits the Analyzer.error signal if there is a problem, and continues to
      process further pieces.

      Emits the Analyzer.analysis_finished signal upon completion, with a list
      of the AnalysisRecord objects generated.
      '''
      # TODO: rewrite this method so it...
      # - uses multiprocessing, and
      # - doesn't return anything, but just starts the analyses and waits for
      #   the _part_combo_finished() to do its job

      # hold the list of AnalysisRecord objects to return
      self._list_of_analyses = []

      #jobs = []
      # Run the Analyses
      # loop through every piece
      for each_piece in self._list_of_pieces:
         # (1) Decode the part-combination specification
         this_combos = each_piece[ListOfPieces.parts_combinations].toPyObject()
         this_combos = str(this_combos)
         if '[all]' == this_combos:
            # We have to examine all combinations of parts

            # How many parts are in this piece?
            number_of_parts = len(each_piece[ListOfPieces.score][0].parts)

            # Get a list of all the part-combinations to examine
            this_combos = Analyzer.calculate_all_combos(number_of_parts-1)
         else:
            # Turn the str specification of parts into a list of int (or str)
            if '(no selection)' == this_combos:
               # This is what happens when no voice pairs were selected
               # TODO: raise an exception
               pass
            else:
               # TODO: we should do this in a safer way, because, as it stands
               #       any code put in here will be blindly executed
               this_combos = eval(this_combos)

         # calculate the number of voice combinations for this piece
         nr_of_voice_combos = len(this_combos) # TODO: use this

         # (2) Loop through every part combination
         for combo in this_combos:
            # select the two parts to analyze
            this_parts = [each_piece[ListOfPieces.score][0].parts[i] for i in combo]
            # prepare the metadata
            this_metadata = each_piece[ListOfPieces.score][0].metadata
            this_part_names = [each_piece[ListOfPieces.parts_list][i] for i in combo]
            this_offset = each_piece[ListOfPieces.offset_intervals][0]
            # TODO: figure this dynamically
            this_salami = False
             # TODO: figure this dynamically
            this_types = [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]
            # prepare the AnalysisRecord object
            this_record = AnalysisRecord(metadata=this_metadata,
                                         part_names=this_part_names,
                                         offset=this_offset,
                                         salami=this_salami)
            # prepare the AnalysisSettings object
            this_settings = AnalysisSettings()
            this_settings.set('types', this_types)
            this_settings.set('offset', this_offset)
            this_settings.set('salami', this_salami)
            # run the analysis and append results to our results-collector
            self._list_of_analyses.append(self._event_finder(parts=this_parts,
                                                             settings=this_settings,
                                                             record=this_record))

      # Conclude
      self.status.emit('100')
      self.status.emit('I finished!')
      self.analysis_finished.emit(self._list_of_analyses)
      return self._list_of_analyses



   @staticmethod
   def _object_stringer(string_me, specs):
      # TODO: test this method
      '''
      Converts music21 objects to strings for use in AnalysisRecord objects.

      string_me : is a list of music21 objects
      specs : a list of 2-tuples, where element 0 is a python type and element 1 is a method to
              convert objects of that type into a string.

      >>> a = [Note('C4', quarterLength=1.0), Rest(quarterLength=1.0)]
      >>> b = [(Note, lambda x: x.nameWithOctave), (Rest, lambda x: 'Rest')]
      >>> Analyzer._object_stringer(a, b)
      ['C4', 'Rest']
      '''
      post = []

      for obj in string_me:
         for i in xrange(len(specs)):
            if isinstance(obj, specs[i][0]):
               post.append(specs[i][1](obj))

      return post



   def _event_finder(self, parts, settings, record):
      '''
      Find events in parts.

      The 'parts' argument is a list of at least one music21 Part object

      The 'settings' argument must be an AnalysisSettings object with all the following settings:
      - types : a list of 2-tuples, where element 0 is a type you want to count as an "event,"
                and element 1 is a function that produces a string version suitable for an
                AnalysisRecord instance.
      - offset : the minimum quarterLength offset between consecutive events
      - salami : if True, all events will be the offset distance from each
         other, even if this produces a series of identical events

      The 'record' argument is an AnalysisRecord object to use for recording this analysis.

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

      This method should only be called from the Analyzer.analyze_pieces() method,
      which coordinates multiprocessing.

      Emits the Analyzer.event_finder_finished signal with the AnalysisRecord,
      and returns the AnalysisRecord, when finished.
      '''

      def end_finder(this_obj):
         '''
         Given an object with an "offset" property and optionally a "quarterLength" proper, returns
         either the value of offset+quarterLength or, if there is no quarterLength property, just
         the value of offset.
         '''
         if hasattr(this_obj, 'quarterLength'):
            return this_obj.offset + this_obj.quarterLength
         else:
            return this_obj.offset

      # Make an iterable out of the list of types we'll need, so it's easier to pass as an argument
      list_of_types = [l[0] for l in settings.get('types')]

      # 1.) Flatten the parts
      parts = [p.flat for p in parts]

      # 2.) Find the end of the last thing in the parts we have
      #    [p[-1] for p in parts] ... make a list of the last event in each Part
      #    [end_finder(l) for l in <<>>] ... calculate the offset of the end of the event
      end_of_score = max([end_finder(l) for l in [p[-1] for p in parts]])

      # 3.) Find the starting offset of this Score
      #    NB: We'll store it in "current_offset" because that's where the loop starts
      current_offset = min([l.offset for l in [p[0] for p in parts]])

      # Keep track of the offset from last time, to prevent accidentally moving backward somehow.
      offset_from_last_time = None

      # 4.) Iterate
      while current_offset < end_of_score:
         # 4.1) Make sure we're not using the same offset at last time through the loop.
         if offset_from_last_time == current_offset:
            msg = 'Error in controllers.Analyzer._event_finder, section 3.1'
            raise RuntimeError(msg)
         else:
            offset_from_last_time = current_offset

         # 4.2) Get the events at the current offset
         current_events = [p.getElementsByOffset(current_offset,
                                                 mustBeginInSpan=False,
                                                 classList=list_of_types)
                           for p in parts]

         #print(str(current_offset)) # DEBUGGING
         # 4.3) We only actually want the first elements in these lists (but we have to know there
         # current_events = [e[0] for e in current_events]
         # TODO: surely there is a cleaner way to do this
         underprocessed = current_events
         current_events = []
         skip_this_offset = False
         for event in underprocessed:
            if 0 == len(event):
               skip_this_offset = True
            else:
               current_events.append(event[0])
         if skip_this_offset:
            break

         # 4.4) Calculate the offset at which this event could be said to start
         current_event_offset_start = max([obj.offset for obj in current_events])

         # DEBUGGING
         #print('--> pre-stringer at ' + str(current_offset) + ' is ' + str(current_events))

         # 4.5) Turn the objects into their string forms
         current_events = Analyzer._object_stringer(current_events, settings.get('types'))

         # 4.6) Reverse the list, so it's lowest-to-highest voices
         current_events = tuple(reversed(current_events))

         # DEBUGGING
         #print('--> pre-commit at ' + str(current_offset) + ' is ' + str(current_events))

         # 4.7) Add the event to the AnalysisRecord, if relevant
         if settings.get('salami'):
            # If salami, we always add the event
            record.append(current_event_offset_start, current_events)
         elif record.most_recent_event()[1] != current_events:
            # If not salami, we only add the event if it's different from the previous
            record.append(current_event_offset_start, current_events)

         # 4.8) Increment the offset
         current_offset += settings.get('offset')
      # End step 4

      # Return
      self.event_finder_finished.emit(record)
      return record
   # End _event_finder() -------------------------------------------------------
# End class Analyzer -------------------------------------------------------------------------------
