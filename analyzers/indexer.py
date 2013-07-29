#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
#
# Copyright (C) 2013 Christopher Antila, Jamie Klassen
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
from music21 import stream, base, duration, converter


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

    # Convert "frozen" Streams, if needed
    if isinstance(parts[0], basestring):
        parts = [converter.thaw(each) for each in parts]

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
    if post != []:
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
    required_indices = []
    required_score_type = None
    possible_settings = {}
    default_settings = {}
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
        RuntimeError:
            - If the "score" argument is not a list of the right type.
            - If required settings are not present in the "settings" argument.
        """
        # Check the "score" argument is either uniformly Part or Series objects.
        for elem in score:
            if not isinstance(elem, self.required_score_type):
                msg = unicode(self.__class__) + u' requires ' + unicode(self.required_score_type) \
                      +  u' objects, not ' + str(type(elem))
                raise RuntimeError(msg)
        # Call our superclass constructor, then set instance variables
        super(Indexer, self).__init__()
        self._score = score
        self._mpc = mpc
        self._indexer_func = None
        self._types = None
        if hasattr(self, u'_settings'):
            if self._settings is None:
                self._settings = {}
        else:
            self._settings = {}

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
        voices = None

        if self._mpc is None:
            # use serial processing
            for each_combo in combos:
                voices = [self._score[x] for x in each_combo]
                post.append(mp_indexer(0, voices, self._indexer_func, self._types)[1])
        else:
            # use the MPController for multiprocessing
            pipe_end = self._mpc.get_pipe()
            jobs_submitted = 0
            for each_combo in combos:
                jobs_submitted += 1
                if isinstance(self._score[0], stream.Stream):
                    voices = [converter.freeze(self._score[x], u'pickle') for x in each_combo]
                else:
                    voices = [self._score[x] for x in each_combo]
                pipe_end.send((mp_indexer, [voices, self._indexer_func, self._types]))
            for each in xrange(jobs_submitted):
                post.append(pipe_end.recv())

        return post
