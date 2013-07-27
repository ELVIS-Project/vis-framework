#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
The controllers that deal with indexing data from music21 Score objects.
"""

import pandas
from music21 import stream, note, base, interval, duration


def _mpi_unique_offsets(streams):
    """
    For a set of streams, find the offsets at which events begin. Used by mp_indexer.

    Parameters
    ==========
    streams : [music21.stream.Stream]
        A list of Streams in which to find the offsets at which events begin.

    Returns
    =======
    list :
        A list of floating-point numbers representing offsets at which a new event begins in any of
        the streams. Offsets are sorted from lowest to highest (start to end).
    """
    # inspired by music21.stream.Stream._uniqueOffsetsAndEndTimes()
    post = []
    for each_part in streams:
        for each_offset in [e.offset for e in each_part.elements]:
            if each_offset not in post:
                post.append(each_offset)
    return sorted(post)


def _mpi_vert_aligner(events):
    """
    When there is more than one event at an offset, call this method to ensure parsing
    simultaneities.

    Example:
    Transforms this...
    [[1, 2, 3], [1, 2, 3], [1, 2]]
    ... into this...
    [[1, 1, 1], [2, 2, 2], [3, 3]]
    """
    post = []
    for i in xrange(max([len(x) for x in events])):
        # for every 'i' from 0 to the highest index of any object at this offset
        this_e = []
        for j in xrange(len(events)):
            # for every part
            try:
                this_e.append(events[j][i])
            except IndexError:
                # when some parts have fewer objects at this offset
                pass
        post.append(this_e)
    return post


def mp_indexer(pipe_index, parts, indexer_func, types=None):
    """
    Perform the indexation of a part, or part combination. This is a module-level function designed
    to ease implementation of multiprocessing with the MPController module.

    If your Indexer has settings, use the indexer_func() to adjust for them.

    If an offset has multiple events of the correct type, all will be included in the new index. If
    this is the case, events are grouped and processed as simultaneities across parts, according to
    their order of appearance in the "parts" argument. In these examples, each [x] is an event in
    the part at the offset indicated above, and the integer indicates the order of processing.

    offset:  0.0  |  0.5  |  1.0  |  1.5  |  2.0
    part 1:  [1]  |  [1]  |  [1]  |  [1]  |  [1]
    part 2:  [1]  |  [1]  |  [1]  |  [1]  |  [1]

    offset:  0.0  |  0.5     |  1.0     |  1.5     |  2.0
    part 1:  [1]  |  [1][2]  |  [1]     |  [1][2]  |  [1][2]
    part 2:  [1]  |  [1][2]  |  [1][2]  |  [1]     |  [1][2]

    offset:  0.0  |  0.5     |  1.0        |  1.5     |  2.0
    part 1:  [1]  |  [1][2]  |  [1][2][3]  |  [1][2]  |  [1][2][3]
    part 2:  [1]  |  [1][2]  |  [1][2]     |  [1]     |  [1]
    part 3:  [1]  |  [1][2]  |  [1][2]     |  [1][2]  |  [1][2]

    This situation is probably rare, since there are not usually simultaneous events that properly
    belong in the same index (i.e., one part will not have both a note and rest at the same time,
    or even two notes at the same time---the first situation is probably two parts on the same
    staff, and the second situation is more profitably treated as a chord).

    Parameters:
    ===========
    :param parts : [music21.stream.Stream] or [pandas.Series]
        A list of at least one Stream (should be Part) or Series object. Every new event, or change
        of simlutaneity, will appear in the outputted index. Therefore, the new index will contain
        at least as many events as the inputted Part or Series with the most events.

    :param indexer_func : function
        This function transforms found events into another suitable format. The output of this
        function is put into an ElementWrapper object.

    :param types : list of type objects
        Required only if "parts" contains Part objects (otherwise ignored). Only objects of a type
        in this list will be passed to the indexer_func for inclusion in the resulting index.

    Returns:
    ========
    pandas.Series :
        The new index. Each element is an instance of music21.base.ElementWrapper. The output of
        the indexer_func is stored in the "obj" attribute. Each ElementWrapper has an appropriate
        offset according to its place in the score.

    Raises:
    =======
    RuntimeError :
        If "parts" is a list of Stream objects but "types" is None (the default value).
    """
    # NB: It's hard to tell, but this function is based on music21.stream.Stream.chordify()

    # flatten the streams or change Series to Parts, as required
    if isinstance(parts[0], stream.Stream):
        if types is None:
            raise RuntimeError(u'mp_indexer requires a list of types when given Stream objects')
        all_parts = [x.flat.getElementsByClass(types) for x in parts]
    else:
        all_parts = [stream.Part(x) for x in parts]

    # collect all unique offsets
    unique_offsets = _mpi_unique_offsets(all_parts)

    # Convert to requested index format
    post = []
    for off in unique_offsets:
        # inspired by vis.controllers.analyzer._event_finder() in vis9c
        current_events = []
        for part in all_parts:  # find the events happening at this offset in all parts
            current_events.append([x for x in part.getElementsByOffset(off, mustBeginInSpan=False)])

        # Arrange groups of things to index
        if 1 == max([len(x) for x in current_events]):
            # each offset has only one event
            current_events = [[current_events[i][0] for i in xrange(len(current_events))]]
        else:
            current_events = _mpi_vert_aligner(current_events)

        # Index previously-arranged groups
        for each_simul in current_events:
            new_obj = indexer_func(each_simul)
            if new_obj is not None:
                new_obj = base.ElementWrapper(new_obj)
                new_obj.offset = off  # copy offset to new Stream
                try:  # set duration for previous event
                    post[-1].duration = duration.Duration(off - post[-1].offset)
                except IndexError:
                    # Happens when this is the first element in "post"; faster than using an "if"
                    pass
                post.append(new_obj)

    # Ensure the last items have the correct duration
    if post:
        end_offset = all_parts[0][-1].offset + all_parts[0][-1].duration.quarterLength
        post[-1].duration = duration.Duration(end_offset - post[-1].offset)

    return pipe_index, pandas.Series(post)


class Indexer(object):
    """
    Create an index of a music21 stream.

    Use the "requires_score" attribute to know whether the __init__() method should be given a
    list of music21.stream.Part objects. If False, use the "required_indices" attribute to get a
    list of the names of Indexers that should be provided instead.

    The name of the indexer, as stored in an IndexedPiece, is the unicode-format version of the
    class name.
    """

    # just the standard instance variables
    required_indices = None
    required_score_type = None
    possible_settings = None
    default_settings = None
    requires_score = False
    # self._score
    # self._mpc
    # self._indexer_func
    # self._types

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new Indexer.

        Parameters
        ==========
        :param score: [pandas.Series] or [music21.stream.Part]
            Depending on how this Indexer works, this is a list of either Part or Series obejcts
            to use in creating a new index.

        :param settings: dict
            A dict of all the settings required by this Indexer. All required settings should be
            listed in subclasses. Default is {}.

        :param mpc: MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        RuntimeError :
            - If the "score" argument is the wrong type.
            - If the "score" argument is not a list of the same types.
            - If required settings are not present in the "settings" argument.
        """
        if settings is None:
            settings = {}
        # Check the "score" argument is either uniformly Part or Series objects.
        for i in xrange(len(score) - 1):
            if type(score[i]) != type(score[i + 1]):
                raise RuntimeError(u'All elements of "score" must be the same type.')
        if not isinstance(score[0], self.required_score_type):
            raise RuntimeError(u'All elements of "score" must be a ' +
                               unicode(self.required_score_type) + '.')
        # Call our superclass constructor, then set instance variables
        super(Indexer, self).__init__()
        self._score = score
        self._mpc = mpc
        self._indexer_func = None
        self._types = None
        self._settings = settings

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        [pandas.Series] :
            A list of the new indices. The index of each Series corresponds to the index of the Part
            used to generate it, in the order specified to the constructor. Each element in the
            Series is an instance of music21.base.ElementWrapper.
        """
        pass

    def _do_multiprocessing(self, combos):
        """
        Dispatch jobs to the MPController for multiprocessing, then await the jobs' completion.

        Parameters
        ==========
        combos : list of list of integers
            A list of all voice combinations to be analyzed. For example:
            - [[0], [1], [2], [3]]
                Analyze each of four parts independently.
            - [[0, 1], [0, 2], [0, 3]]
                Analyze the highest part compared with all others.
            - [[0, 1, 2, 3]]
                Analyze all parts at once.
            The function stored in "self._indexer_func" must know how to deal with the number of
            simultaneous events it will receive.

        Returns
        =======
        [pandas.Series]
            A list of Series.

        Side Effects
        ============
        1.) Blocks until all voice combinations have completed.
        """

        post = []

        if self._mpc is None:
            # use serial processing
            for each_combo in combos:
                voices = [self._score[x] for x in each_combo]
                post.append(mp_indexer(0, voices, self._indexer_func, self._types)[1])
        else:
            # use the MPController for multiprocessing
            self._mpc.run()
            pipe_end = self._mpc.get_pipe()
            jobs_submitted = 0
            for each_combo in combos:
                jobs_submitted += 1
                voices = [self._score[x] for x in each_combo]
                pipe_end.send((mp_indexer, [voices, self._indexer_func, self._types]))
            for each in xrange(jobs_submitted):
                post.append(pipe_end.recv())

        return post


class NoteRestIndexer(Indexer):
    """
    Index music21.note.Note and Rest objects found in a music21.stream.Part.

    Rest objects are indexed as u'Rest', and Note objects as the unicode-format version of their
    "pitchWithOctave" attribute.
    """

    required_indices = []
    required_score_type = stream.Part
    requires_score = True

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new Indexer.

        Parameters
        ==========
        :param score : [music21.stream.Part]
            A list of all the Parts to index.

        :param mpc : MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        RuntimeError :
            If the "score" argument is the wrong type.
        """
        super(NoteRestIndexer, self).__init__(score, None, mpc)

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = [note.Rest, note.Note]

        # Change to the function you want to use
        self._indexer_func = lambda x: u'Rest' if isinstance(x[0], note.Rest) \
                                       else unicode(x[0].nameWithOctave)

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        [pandas.Series] :
            A list of the new indices. The index of each Series corresponds to the index of the Part
            used to generate it, in the order specified to the constructor. Each element in the
            Series is an instance of music21.base.ElementWrapper.
        """

        combinations = [[x] for x in xrange(len(self._score))]  # calculate each voice separately
        return self._do_multiprocessing(combinations)


class IntervalIndexer(Indexer):
    """
    Create an index of music21.interval.Interval objects found in the result of a NoteRestIndexer.

    This indexer does not require a score.
    """

    required_indices = [u'NoteRestIndexer']
    required_score_type = pandas.Series
    possible_settings = [u'simple or compound', u'quality']
    default_settings = {u'simple or compound': u'compound', u'quality': False}

    @staticmethod
    def indexer_func(ecks, simple, qual):
        """
        Turn a notes-and-rests simultaneity into the name of the interval it represents. Note that,
        because of the u'Rest' strings, you can compare the duration of the piece in which the two
        parts do or do not have notes sounding together.

        Parameters
        ==========
        :param ecks : [music21.base.ElementWrapper]
            A two-item iterable of ElementWrapper objects, for which the "obj" attribute should be
            strings like 'Rest' or 'G4'; the upper voice should have index 0.

        :param simple : boolean
            True if intervals should be reduced to their single-octave version.

        :param qual : boolean
            True if the interval's quality should be prepended.

        Returns
        =======
        string :
            Like 'M3' or similar.
        u'Rest' :
            If one of the elements of "ecks" == u'Rest'.
        None :
            If there "ecks" has greater or fewer than two elements.
        """
        if 2 != len(ecks):
            return None
        if u'Rest' == ecks[0].obj or u'Rest' == ecks[1].obj:
            return u'Rest'
        else:
            interv = interval.Interval(note.Note(ecks[1].obj), note.Note(ecks[0].obj))
            post = u'-' if interv.direction < 0 else u''
            if qual:
                # We must get all of the quality, and none of the size (important for AA, dd, etc.)
                q_str = u''
                for each in interv.name:
                    if each in [u'A', u'M', u'P', u'm', u'd']:
                        q_str += each
                post += q_str
            if simple:
                post += u'8' if 8 == interv.generic.undirected \
                        else unicode(interv.generic.simpleUndirected)
            else:
                post += unicode(interv.generic.undirected)
            return post

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new IntervalIndexer. For the output format, see the docs for
        IntervalIndexer.indexer_func().

        Parameters
        ==========
        :param score : vis.models.IndexedPiece
            The piece with parts to index.

        :param settings : dict
            A dict of relevant settings, both optional. These are:
            - 'simple or compound' : 'simple' or 'compound'
                Whether intervals should be represented in their single-octave form. Defaults to
                'compound'.
            - 'quality' : boolean
                Whether to consider the quality of intervals. Optional. Defaults to False.

        :param mpc : MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        Nothing. There are no required settings.
        """

        if settings is None:
            settings = {}

        # Check all required settings are present in the "settings" argument
        self._settings = {}
        if 'simple or compound' in settings:
            self._settings['simple or compound'] = settings['simple or compound']
        else:
            self._settings['simple or compound'] = \
                IntervalIndexer.default_settings['simple or compound']
        if 'quality' in settings:
            self._settings['quality'] = settings['quality']
        else:
            self._settings['quality'] = IntervalIndexer.default_settings['quality']

        super(IntervalIndexer, self).__init__(score, None, mpc)
        self._indexer_func = lambda x: IntervalIndexer.indexer_func(x, False, True)

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        {pandas.Series} :
            A dict of the new indices. The index of each Series corresponds to the indices of the
            Part combinations used to generate it, in the order specified to the constructor. Each
            element in the Series is an instance of music21.base.ElementWrapper.
            Example, if you stored output of run() in the "result" variable:
                result['[0, 1]'] : the highest and second highest parts
        """

        combinations = []

        # To calculate all 2-part combinations:
        for left in xrange(len(self._score)):
            # noinspection PyArgumentList
            for right in xrange(left + 1, len(self._score)):
                combinations.append([left, right])

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing, like adding a label for voice combinations.
        post = {}
        for i, combo in enumerate(combinations):
            post[str(combo)] = results[i]

        # Return the results.
        return post


class TemplateIndexer(Indexer):
    """
    Template for a class to make an index of a music21 stream.

    Use this class when you want to write a new Indexer subclass.
    """

    required_indices = []  # empty list means the Indexer uses Part objects
    required_score_type = stream.Part  # or pandas.Series
    requires_score = True  # adjust according to previous
    possible_settings = []  # list of strings
    default_settings = {}  # keys are strings, values are anything

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new Indexer.

        Parameters
        ==========
        :param score: [pandas.Series] or [music21.stream.Part]
            Depending on how this Indexer works, this is a list of either Part or Series obejcts
            to use in creating a new index.

        :param settings: dict
            A dict of all the settings required by this Indexer. All required settings should be
            listed in subclasses. Default is {}.

        :param mpc : MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        RuntimeError :
            - If the "score" argument is the wrong type.
            - If the "score" argument is not a list of the same types.
            - If required settings are not present in the "settings" argument.
        """

        # Check all required settings are present in the "settings" argument. You must ignore
        # extra settings.
        if settings is None:
            self._settings = {}

        # Change "TemplateIndexer" to the current class name. The superclass will handle the
        # "score" and "mpc" arguments, but you should have processed "settings" above, so it should
        # not be sent to the superclass constructor.
        super(TemplateIndexer, self).__init__(score, None, mpc)

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = []

        # Change to the function you want to use
        # NB: The lambda function receives events in a list of all voices in the current voice
        #     combination; if this Indexer processes one voice at a time, it's a one-element list.
        #     The function receives the unmodified object, the type of which is either in
        #     self._types object or music21.base.ElementWrapper.
        self._indexer_func = lambda x: None

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        [pandas.Series] :
            A list of the new indices. The index of each Series corresponds to the index of the Part
            used to generate it, in the order specified to the constructor. Each element in the
            Series is an instance of music21.base.ElementWrapper.
        """

        # NOTE: We recommend indexing all possible voice combinations, whenever feasible.

        # To calculate each part separately:
        combinations = [[x] for x in xrange(len(self._score))]

        # To calculate all 2-part combinations:
        #for left in xrange(len(self._score)):
        #    for right in xrange(left + 1, len(self._score)):
        #        combinations.append([left, right])

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing, like adding a label for voice combinations.

        # Return the results.
        return results
