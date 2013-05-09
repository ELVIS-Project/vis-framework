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
"""
Holds the Analyzer controller.
"""

# Imports from...
# Python
import os
from multiprocessing import Pool
# music21
from music21 import note, chord, converter, stream
# PyQt4
from PyQt4 import QtCore
# vis
from controller import Controller
from models.analyzing import ListOfPieces, AnalysisRecord, AnalysisSettings


def analyze_piece(each_piece):
    """
    This method basically only prepares things for _event_finder().
    """
    records = []
    try:
        piece_name = str(each_piece[ListOfPieces.score][1])
    except Exception as exc:
        return str(exc)
    # (1) Decode the part-combination specification
    this_combos = str(each_piece[ListOfPieces.parts_combinations])
    the_score = each_piece[ListOfPieces.score][0]
    if not isinstance(the_score, stream.Score):
        the_score = converter.thawStr(the_score)
    if '[all]' == this_combos:
        # We have to examine all combinations of parts...
        # How many parts are in this piece?
        number_of_parts = len(the_score.parts)
        # Get a list of all the part-combinations to examine
        this_combos = Analyzer.calculate_all_combos(number_of_parts - 1)
    else:
        # Turn the str specification of parts into a list of int (or str)
        this_combos = eval(this_combos)
    # calculate the number of voice combinations for this piece
    #nr_of_voice_combos = len(this_combos)  # TODO: use this
    # prepare the offset value to check... kind of clunky, but it works for now
    this_offset = str(each_piece[ListOfPieces.offset_intervals])
    if this_offset[0] == '[':
        this_offset = this_offset[1:]
    if this_offset[-1] == ']':
        this_offset = this_offset[:-1]
    this_offset = float(this_offset)

    # (2) Loop through every part combination
    for combo in this_combos:
        # select the two parts to analyze
        # NOTE: the step used to look like this... but QVariants...
        this_parts = [the_score.parts[i] for i in combo]
        # prepare the metadata
        this_metadata = the_score.metadata
        this_part_names = [each_piece[ListOfPieces.parts_list][i] for i in combo]
        this_salami = each_piece[ListOfPieces.repeat_identical]
        # TODO: figure this dynamically
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
        """
        Given an object with an "offset" property and optionally a "quarterLength" proper, returns
        either the value of offset+quarterLength or, if there is no quarterLength property, just
        the value of offset.
        """
        if hasattr(this_obj, 'quarterLength'):
            return this_obj.offset + this_obj.quarterLength
        else:
            return this_obj.offset

    # Make an iterable out of the list of types we'll need, so it's easier to pass as an argument
    list_of_types = [each_type for each_type, name in settings.types]

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
    # End step 4

    # Return
    return record


class AnalyzerThread(QtCore.QThread):
    """
    In a separate QThread, coordinate the multiprocessing-enabled analysis of pieces.
    """

    def __init__(self, analyzer):
        """
        Create a new AnalyzerThread instance, keeping track of the Analyzer object
        that instantiated it.
        """
        self._analyzer = analyzer
        self.progress = 0
        self._multiprocess = True
        self._pool = None
        super(QtCore.QThread, self).__init__()

    def set_multiprocess(self, state):
        """
        Set the meaningless self._multiprocess instance variable to something.
        """
        self._multiprocess = bool(state)

    def callback(self, result):
        """
        For internal use.

        Called when the _event_finder() has finished with a parts combination.
        This method adds the resulting AnalysisRecord to the internal list of
        analyses.
        """
        self.progress += 1
        piece_name, result = result
        if isinstance(result, basestring):
            self._analyzer.error.emit(result)
        else:
            self._analyzer.status.emit(str(int(float(self.progress) / self.num_pieces * 100)))
            self._analyzer.status.emit(unicode(piece_name) + " completed.")
            for record in result:
                self._analyzer._list_of_analyses.append(record)

    def run(self):
        """
        Analyze all the pieces held in the Analyzers ListOfPieces instance.
        """
        self._analyzer.analysis_is_running = True
        self._analyzer.status.emit('0')
        self._analyzer.status.emit('Analyzing...')
        self.num_pieces = self._analyzer._list_of_pieces.rowCount()
        self.progress = 0

        # Convert everything in "each_piece" to *not* a QVariant
        the_pieces = []
        for each_raw_piece in self._analyzer._list_of_pieces:
            collecting = []
            for each_column in each_raw_piece:
                if isinstance(each_column, QtCore.QVariant):
                    collecting.append(each_column.toPyObject())
                else:
                    collecting.append(each_column)
            the_pieces.append(collecting)

        # Sort the files according to whether their extension indicates they'll work with
        # multiprocessing or not
        sequential_extensions = ['.mid', '.midi']
        multiprocess_pieces = []  # for everything that works in multiprocessing
        sequential_pieces = []  # for everything that doesn't work (i.e., MIDI)
        for sort_piece in the_pieces:
            _, extension = os.path.splitext(sort_piece[ListOfPieces.filename])
            if extension in sequential_extensions:
                sequential_pieces.append(sort_piece)
            else:
                multiprocess_pieces.append(sort_piece)

        # Start up the multiprocessing
        self._pool = Pool()
        for each_piece in multiprocess_pieces:
            # Load up the stuff in the Pool!
            self._pool.apply_async(analyze_piece,
                                   (each_piece,),
                                   callback=self.callback)
        # Wait for the multiprocessing to finish
        self._pool.close()
        self._pool.join()
        self._pool = None

        # Start up the sequential analysis
        for each_piece in sequential_pieces:
            self.callback(analyze_piece(each_piece))

        # self.progress != self.num_pieces if a user cancelled before the analyses were completed
        if self.progress != self.num_pieces:
            return None

        self._analyzer.status.emit('100')
        self._analyzer.status.emit('Done!')
        self._analyzer.analysis_finished.emit(self._analyzer._list_of_analyses)
        # last thing: must clear these analyses, so they don't get re-used!
        self._analyzer._list_of_analyses = []
        self._analyzer.analysis_is_running = False


class Analyzer(Controller):
    """
    This class performs analysis for series of vertical intervals, and manages
    the settings with which to analyze. Makes a list of AnalysisRecord objects
    that each holds a half-analyzed voice-pair that Experimenter will use to
    perform fuller analysis.

    The ListOfPieces model is always stored in the list_of_pieces property.
    """

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
    # cancels the currently-runing analysis, if there is one
    cancel_analysis = QtCore.pyqtSignal()

    # Whether there's a running analysis
    analysis_is_running = False

    def __init__(self):
        """
        Create a new Analyzer instance.
        """
        super(Analyzer, self).__init__()  # required for signals
        # other things
        self._list_of_pieces = ListOfPieces()
        self._list_of_analyses = []
        self.thread = AnalyzerThread(self)

    def setup_signals(self):
        """
        Connect Analyzer-relevant signals
        """
        self.cancel_analysis.connect(self._cancel_analysis)
        self.run_analysis.connect(self.analyze_pieces)
        self.change_settings.connect(self.set_data)

    @QtCore.pyqtSlot()
    def _cancel_analysis(self):
        """
        Determine whether there is an analysis operation running, then cancel it.
        """
        if self.thread._pool is not None:
            self.thread._pool.terminate()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QVariant)
    def set_data(self, index, change_to):
        """
        Changes the data in a cell of the ListOfPieces model.

        The arguments here should be the same as sent to ListOfPieces.setData().
        """
        self._list_of_pieces.setData(index, change_to, QtCore.Qt.EditRole)

    @staticmethod
    def calculate_all_combos(upto):
        """
        Calculate all combinations of integers between 0 and the argument.

        Includes a 0th item... the argument should be len(whatevs) - 1.
        """
        post = []

        for left in xrange(upto):
            for right in xrange(left + 1, upto + 1):
                post.append([left, right])

        return post

    @QtCore.pyqtSlot()
    def analyze_pieces(self):
        """
        Runs the analysis specified in the ListOfPieces. Produces an
        AnalysisRecord object for each voice pair analyzed.

        Emits the Analyzer.error signal if there is a problem, and continues to
        process further pieces.

        Emits the Analyzer.analysis_finished signal upon completion, with a list
        of the AnalysisRecord objects generated.
        """
        self.thread.start()

    @staticmethod
    def _object_stringer(string_me, specs):
        # TODO: test this method
        """
        Converts music21 objects to strings for use in AnalysisRecord objects.

        string_me : is a list of music21 objects
        specs : a list of 2-tuples, where element 0 is a python type and element 1 is a method to
                convert objects of that type into a string.

        >>> a = [Note('C4', quarterLength=1.0), Rest(quarterLength=1.0)]
        >>> b = [(Note, lambda x: x.nameWithOctave), (Rest, lambda x: 'Rest')]
        >>> Analyzer._object_stringer(a, b)
        ['C4', 'Rest']
        """
        post = []

        for obj in string_me:
            for i in xrange(len(specs)):
                if isinstance(obj, specs[i][0]):
                    post.append(specs[i][1](obj))

        return post
