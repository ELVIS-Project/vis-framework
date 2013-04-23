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
from multiprocessing import Pool
import pickle
import traceback
# music21
from music21 import note, chord, converter, stream
# PyQt4
from PyQt4 import QtCore
# vis
from models.analyzing import Piece, ListOfPieces, AnalysisRecord
from models import settings as models_settings


def _analyze_piece(each_piece):
    """
    Conduct the analysis for a Piece

    Parameters
    ----------

    each_piece : :py:class:`models.analyzing.Piece`
        The Piece to analyze, including all specifications for part combinations, events to pick
        up, etc., and the the music21 Score object itself.

    Returns
    -------

    2-tuple : (piece_name, records)
        piece_name : string
            The name of the piece for which analyses are contained in 'records'.

        records : list of :py:class:`models.analyzing.AnalysisRecord` or string
            The analyses, or a string-format description of an error that occurred during analysis.
    """
    records = []
    piece_name = str(each_piece[ListOfPieces.score][1]) # TODO: this won't work in milestone 11 and up
    # (1) Decode the part-combination specification
    this_combos = str(each_piece[ListOfPieces.parts_combinations])
    the_score = converter.thawStr(each_piece[ListOfPieces.score][0])
    if '[all]' == this_combos:
        # We have to examine all combinations of parts...
        # How many parts are in this piece?
        number_of_parts = len(the_score.parts)
        # Get a list of all the part-combinations to examine
        this_combos = Analyzer.calculate_all_combos(number_of_parts-1)
    else:
        # Turn the str specification of parts into a list of int (or str)
        if '(no selection)' == this_combos:
            # This is what happens when no voice pairs were selected
            # (1) Notify the user what happened
            msg = 'No voices selected for analysis in "'+each_piece[ListOfPieces.score][1]+'"'
            msg += '\nSome analyses may have been completed, but you should re-start vis.'
            return (piece_name, msg)
            # (3) Return to the panel where the user can select some voice pairs
            # TODO: this part
        else:
            # TODO: we should do this in a safer way, because, as it stands
            #       any code put in here will be blindly executed
            this_combos = eval(this_combos)
    # calculate the number of voice combinations for this piece
    nr_of_voice_combos = len(this_combos) # TODO: use this
    # prepare the list of offset values to check
    this_offset = float(str(each_piece[ListOfPieces.offset_intervals])[1:-1])
    # (2) Loop through every part combination
    for combo in this_combos:
        # select the two parts to analyze
        # NOTE: the step used to look like this... but QVariants...
        this_parts = [the_score.parts[i] for i in combo]
        # prepare the metadata
        this_metadata = the_score.metadata
        this_part_names = [each_piece[ListOfPieces.parts_list][i] for i in combo]
        this_salami = each_piece[ListOfPieces.repeat_identical]
        # TODO: figure this dynamically (issue #146)
        # TODO: formalize the lambda things somehow
        # NOTE: 'c' is for 'Chord' and 'm' is for 'chord Member'
        chords_lambda = lambda c: [m.nameWithOctave for m in c]
        this_types = [(note.Note, lambda x: x.nameWithOctave),
                      (note.Rest, lambda x: 'Rest'),
                      (chord.Chord, chords_lambda)]
        # prepare the AnalysisRecord object
        this_record = AnalysisRecord(metadata=this_metadata,
                                     part_names=this_part_names,
                                     offset=this_offset,
                                     salami=this_salami)
        # prepare the AnalysisSettings object
        this_settings = AnalysisSettings()
        this_settings.types = this_types
        this_settings.offset = this_offset
        this_settings.salami = this_salami
        # run the analysis and append results to our results-collector
        try:
            records.append(_event_finder(parts=this_parts,
                                         settings=this_settings,
                                         record=this_record))
        except RuntimeError as e:
            return (piece_name, str(e))
    return (piece_name, records)


def _event_finder(parts, settings, record):
    """
    Find events in parts.

    Parameters
    ----------

    parts : list of :py:class:`music21.stream.Part`
        A list of one or more Part objects to analyze.

    settings :

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
    """

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
    list_of_types = [type for type, name in settings.types]

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
        # 4.1) Make sure we're not using the same offset as last time through the loop.
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
        # 4.3) Make sure we only have the first event at this offset.
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
        # 4.5) Turn the objects into their string forms
        current_events = Analyzer._object_stringer(current_events, settings.types)
        # 4.6) Reverse the list, so it's lowest-to-highest voices
        current_events = tuple(reversed(current_events))
        # 4.7) Add the event to the AnalysisRecord, if relevant
        if settings.salami:
            # If salami, we always add the event.
            # But also, if this event is the same as the previous event, we have to use the
            # previous event's offset.
            if record.most_recent_event()[1] == current_events:
                current_event_offset_start = record.most_recent_event()[0]
            record.append(current_event_offset_start, current_events)
        elif record.most_recent_event()[1] != current_events:
            # If not salami, we only add the event if it's different from the previous
            record.append(current_event_offset_start, current_events)
        # 4.8) Increment the offset
        current_offset += settings.offset
    # End step 4 ... return
    return record
# End _event_finder() ------------------------------------------------------------------------------


class AnalyzerThread(QtCore.QThread):
   def __init__(self, analyzer):
      super(AnalyzerThread, self).__init__()
      self.analyzer = analyzer

   def callback(self, result):
      '''
      For internal use.

      Called when the _event_finder() has finished with a parts combination.
      This method adds the resulting AnalysisRecord to the internal list of
      analyses.
      '''
      piece_name, result = result
      if isinstance(result, basestring):
         self.error.emit(result)
      else:
         self.progress += 1.0/self.num_pieces
         self.analyzer.status.emit(str(int(self.progress * 100)))
         self.analyzer.status.emit("Analyzing... {0} Analyzed.".format(piece_name))
         for record in result:
            self.analysis_records.append(record)

   def run(self):
      self.analyzer.status.emit('0')
      self.analyzer.status.emit('Analyzing...')
      self.num_pieces = self.list_of_pieces.rowCount()

      if self.settings.multiprocess:
         pool = Pool()
         for each_raw_piece in self.list_of_pieces:
            # (1) Ensure all the things in "each_piece" are *not* a QVariant
            each_piece = []
            for each_column in each_raw_piece:
               if isinstance(each_column, QtCore.QVariant):
                  each_piece.append(each_column.toPyObject())
               else:
                  each_piece.append(each_column)
            pool.apply_async(_analyze_piece, (each_piece,), callback=self.callback)

         pool.close()
         pool.join()
      else:
         for each_raw_piece in self.list_of_pieces:
            each_piece = []
            for each_column in each_raw_piece:
               if isinstance(each_column, QtCore.QVariant):
                  each_piece.append(each_column.toPyObject())
               else:
                  each_piece.append(each_column)

            self.callback(_analyze_piece(each_piece))

      self.analyzer.status.emit('100')
      self.analyzer.status.emit('Done!')


class Analyzer(QtCore.QObject):
   '''
   This class performs analysis for series of vertical intervals, and manages
   the settings with which to analyze. Makes a list of AnalysisRecord objects
   that each holds a half-analyzed voice-pair that Experimenter will use to
   perform fuller analysis.

   The ListOfPieces model is always stored in the list_of_pieces property.
   '''
   # description of an error in the Analyzer
   error = QtCore.pyqtSignal(str)
   # status of the analysis
   status = QtCore.pyqtSignal(str)
   finished = QtCore.pyqtSignal()
   start = QtCore.pyqtSignal()

   def __init__(self):
      '''
      Create a new Analyzer instance.
      '''
      super(Analyzer, self).__init__()
      self.thread = AnalyzerThread(self)
      self.current_piece = Piece('', stream.Score(), '', [])
      self.thread.list_of_pieces = ListOfPieces()
      self.thread.list_of_analyses = []
      self.thread.progress = 0.0
      self.thread.settings = models_settings.Settings({
         'multiprocess': models_settings.BooleanSetting(
            False,
            display_name="Use multiprocessing (import in parallel)"
         )
      })

   @property
   def current_piece(self):
      '''
      Method docstring
      '''
      return self._current_piece

   @current_piece.setter
   def current_piece(self, value):
      '''
      Method docstring
      '''
      if not hasattr(self, "_current_piece"):
         self._current_piece = Piece('', stream.Score(), '', [])
      self._current_piece.update(value)

   def analyze(self):
      '''
      Method docstring
      '''
      self.thread.start()

   def load_statistics(self, statistics):
      '''
      This method may not even be required, but if it is, it will import
      the "precalculated statistics" -- some kind of serialized AnalysisRecord.
      '''
      pass

   def set_data(self, index, change_to):
      '''
      Changes the data in a cell of the ListOfPieces model.

      The arguments here should be the same as sent to ListOfPieces.setData().
      '''
      self.thread.list_of_pieces.setData(index, change_to, QtCore.Qt.EditRole)

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
# End class Analyzer -------------------------------------------------------------------------------
