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
from multiprocessing import Process
# music21
from music21 import note
# PyQt4
from PyQt4 import QtCore
# vis
from controller import Controller
from models.analyzing import ListOfPieces, AnalysisRecord



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
      super(Controller, self).__init__() # required for signals
      # other things
      self._list_of_pieces = ListOfPieces()
      self._list_of_analyses = []



   def setup_signals(self):
      self.event_finder_finished.connect(self._part_combo_finished)


   @QtCore.pyqtSlot(AnalysisRecord)
   def _part_combo_finished(self, this_record):
      '''
      For internal use.

      Called when the _event_finder() has finished with a parts combination.
      This method adds the resulting AnalysisRecord to the internal list of
      analyses, then emits Analyzer.status and, if appropriate,
      Analyzer.analysis_finished.
      '''
      self.post.append(this_record)



   @QtCore.pyqtSlot(ListOfPieces)
   def catch_import(self, pieces_list):
      # TODO: I think this method is unnecessary and should be removed
      '''
      Slot for the Importer.import_finished signal. This method is called
      when the Importer controller has finished importing the list of pieces.

      The argument is a ListOfPieces object.
      '''
      self._list_of_pieces = pieces_list



   def set_data(self, index, change_to):
      '''
      Changes the data in a cell of the ListOfPieces model.

      The arguments here should be the same as sent to ListOfPieces.setData().
      '''
      self._list_of_pieces.setData(index, change_to, QtCore.Qt.EditRole)



   def run_analysis(self):
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
      self.post = []

      # TODO: uncomment multiprocessing stuff, make it work

      #jobs = []
      # Run the analyses
      for each_piece in self._list_of_pieces.iterateRows():
         for combo in each_piece[4]:
            parts = [each_piece[1][0].parts[i] for i in combo]
            args = (parts,
                    [note.Note, note.Rest],
                    2.0,
                    False,
                    AnalysisRecord(part_names=[p.id for p in parts]))
            self.post.append(self._event_finder(args))
            #p = Process(target=self._event_finder, args=args)
            #jobs.append(p)
            #p.start()
      #for job in jobs:
      #   job.join()
      # Return
      self.analysis_finished.emit(self.post)
      return self.post



   @staticmethod
   def _stream_type_filter(parts, types):
      '''
      Given a list of flat music21.stream.Part objects and a list of python
      types, return the list of Part objects with only the objects that are of
      the given types.
      '''
      # TODO: test this method
      for each_part in parts:
         # list of objects to remove from this part
         things_to_remove = []
         for each_thing in each_part:
            # whether to keep each_thing; if each_thing is one of the approved
            # types, we'll change this to True
            keep_thing = False
            for each_type in types:
               if isinstance(each_thing, each_type):
                  keep_thing = True
            if not keep_thing:
               things_to_remove.append(each_thing)
         each_part.remove(things_to_remove, shiftOffsets=False)

      return parts



   @staticmethod
   def _we_should_continue(current_index, last_index):
      '''
      Accepts two lists of ints. If any of the ints in the first list is equal
      to or less than the int with the same index in the second list,
      returns True.
      '''
      #print('*** checking continue with ' + str(current_index))# DEBUGGING
      # TODO: test this method
      for index in xrange(len(current_index)):
         if current_index[index] <= last_index[index]:
            return True

      return False



   @staticmethod
   def _object_stringer(string_me):
      '''
      Converts music21 objects to strings for use in AnalysisRecord objects.

      Currently converts:
      - Note objects (as 'F4')
      - Rest objects (as 'Rest')

      All other types are simply sent to str().
      '''
      # TODO: test this method
      if isinstance(string_me, note.Note):
         return string_me.nameWithOctave
      elif isinstance(string_me, note.Rest):
         return 'Rest'
      else:
         return str(string_me)



   def _event_finder(self, parts, types, offset, salami, record):
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

      Emits the Analyzer.event_finder_finished signal with the AnalysisRecord,
      and returns the AnalysisRecord, when finished.
      '''

      def round_to(n, precision):
         '''
         Rounds a float down to the nearest "precision."

         Thanks to...
         http://stackoverflow.com/questions/4265546/python-round-to-nearest-05

         >>> round_to(12.6, 0.5)
         12.5
         >>> round_to(12.3, 0.25)
         12.25
         >>> round_to(12.4, 0.25)
         12.25
         '''
         correction = 0.5 if n >= 0 else -0.5
         new_n = int( n / precision + correction ) * precision
         new_n -= precision if new_n > n else 0.0
         return new_n

      # 1.) Filter each Stream for only the types specified in "types"
      for index in xrange(len(parts)):
         parts[index] = parts[index].flat
      parts = Analyzer._stream_type_filter(parts, types)

      # 2.) Store...
      # the index of the current objects, independently for each Stream
      current_index = [0 for i in xrange(len(parts))]
      # the last index in each Part
      last_index = [len(each_part)-1 for each_part in parts]
      # the offset of the most recently recorded event
      most_recent_event = None
      # indices from the most recent loop (see (3.2))
      indices_from_last_time = [-1 for i in xrange(len(parts))]

      # 3.) Iterate
      while Analyzer._we_should_continue(current_index, last_index):
         #print('++++ beginning the loop') # DEBUGGING
         # 3.1) Safety check: ensure "current index" isn't past the end of the
         # part. If so, we'll just use the last index in the part.
         for index in xrange(len(current_index)):
            if current_index[index] > last_index[index]:
               #print('++ + decrementing index ' + str(index)) # DEBUGGING
               current_index[index] = last_index[index]

         # 3.2) If we're using the same indicess we started with last time,
         # that's a bad sign.
         #print('!!!! last_time: ' + str(indices_from_last_time) + ' and current: ' + str(current_index)) # DEBUGGING
         if indices_from_last_time == current_index:
            msg = 'Error in controllers.Analyzer._event_finder, section 3.2'
            raise RuntimeError(msg)
         else:
            indices_from_last_time = [index for index in current_index]
            #print('!!!! assigning... last_time is now ' + str(indices_from_last_time))

         # 3.3) If the events in all the parts don't have the same offset, we
         # need to use the previous event in every part except the one that
         # already has that offset.
         # TODO: rename "asdf"
         asdf = [parts[index][current_index[index]].offset for index in xrange(len(parts))]
         #if [asdf[index] != asdf[index+1] for index in xrange(len(asdf)-1)]:
         if asdf[0] != asdf[1]:
            # TODO: remove this limitation to two parts

            # If the objects are the last in their streams...
            if current_index[0] == last_index[0] and current_index[1] == last_index[1]:
               pass
            # If the 0 object is last in its stream...
            elif current_index[0] == last_index[0]:
               # We can only decrement the 0 stream, if it's what occurs later.
               if parts[0][current_index[0]].offset > parts[1][current_index[1]].offset:
                  current_index[0] -= 1
            # If the 1 object is last in its stream...
            elif current_index[1] == last_index[1]:
               # We can only decrement the 1 stream, if it's what occurs later.
               if parts[1][current_index[1]].offset > parts[0][current_index[0]].offset:
                  current_index[1] -= 1
            # Neither object is last in its stream...
            else:
               # Which object has the greater offset?
               if parts[0][current_index[0]].offset > parts[1][current_index[1]].offset:
                  # Must be the 0 part with a greater offset
                  current_index[0] -= 1
               else:
                  # Must be the 1 part with a greater offset
                  current_index[1] -= 1

         # 3.4) Decide whether to use this simultaneity:
         use_this_simultaneity = False
         # The offset of the current simultaneity will be the highest
         # offset of all the objects involved.
         # NB: We need this for later steps.
         potential_offset = max([parts[index][current_index[index]].offset for index in xrange(len(parts))])
         # What is the next "yes-counting" offset after the most_recent_event?
         next_offset_to_count = round_to(most_recent_event, offset) if most_recent_event is not None else 0.0
         next_offset_to_count += offset

         # 3.4.1) Does the event happen at an offset we're counting?
         if potential_offset % offset == 0.0:
            use_this_simultaneity = True
            #print('**** True in 3.4.1') # DEBUGGING
            #print('potential_offset % offset is ' + str(potential_offset) + ' % ' + str(offset)) # DEBUGGING
         # 3.4.2) If the object is after the next offset we're counting, we
         # have to re-count the most recent event. We only need to re-count
         # the same event if the "salami" flag is set; otherwise, we need to
         # see whether this event continues past any particular offset that
         # we're supposed to count (in sect 3.4.3).
         elif potential_offset > next_offset_to_count and salami:
            # Assuming "yes"...
            # 3.4.2.1) Decrement indices of the current objects
            current_index = [index-1 for index in current_index]
            # 3.4.2.2) Update the potential offset
            potential_offset = next_offset_to_count
            # 3.4.2.3) Set to use this simultaneity
            use_this_simultaneity = True
            #print('**** True in 3.4.2.3') # DEBUGGING
         # 3.4.3) Does this event continue past an offset that we're counting?
         else:
            # Find the next offset to be counted that's after the
            # potential_offset of this event
            next_offset_to_count = round_to(potential_offset, offset)
            next_offset_to_count += offset

            # 3.4.3.1) Find the offset of the next event, which is actually
            # finding where this event ends.
            offset_of_next_event = None
            # Here, "index" means the index of the part being considered.
            for index in xrange(len(parts)):
               # Store the end of this event
               potential_event_end = None
               # If this is the last object in the stream, we need to use the
               # quarterLength to figure out when this event ends.
               if current_index[index] >= last_index[index]:
                  potential_event_end = parts[index][current_index[index]].offset + \
                                        parts[index][current_index[index]].quarterLength
               # Otherwise use the start of the next event as the end of this
               else:
                  potential_event_end = parts[index][current_index[index]+1].offset

               # Is this less than the current offset_of_next_event, or is the
               # current offset_of_next event still set to None?
               if offset_of_next_event > potential_event_end or offset_of_next_event is None:
                  offset_of_next_event = potential_event_end

            # 3.4.3.2) If offset_of_next_event is strictly greater than the
            # next_offset_to_count, then we must count this event.
            if offset_of_next_event > next_offset_to_count:
               #print('**** True in (3.4.3.2)') # DEBUGGING
               use_this_simultaneity = True

         # 3.5) Make this event
         if use_this_simultaneity:
            # For each of the things in the parts at this moment, run them
            # through _object_stringer() and add them to this list.
            current_event = [Analyzer._object_stringer(parts[index][current_index[index]]) for index in xrange(len(parts))]
            # Reverse the list, so it's lowest-voice-to-highest-voice, and
            # turn it into a tuple.
            current_event = tuple(reversed(current_event))

         # 3.6) If we're not "salami"-ing, and this event is the same as the
         # most recently recorded one, then we actually won't count this.
         if use_this_simultaneity and not salami and \
         record.most_recent_event()[1] == current_event:
            use_this_simultaneity = False

         # 3.7) Add this event to the AnalysisRecord, if relevant
         if use_this_simultaneity:
            record.append(potential_offset, current_event)
            # Update the offset of the most recent event from step (2)
            most_recent_event = potential_offset

         # 3.8) Increment the current_index from step (2).
         current_index = [index+1 for index in current_index]
      # End the "while" loop
      self.event_finder_finished.emit(record)
      return record
   # End method _event_finder() ----------------------------
# End class Analyzer -----------------------------------------------------------
