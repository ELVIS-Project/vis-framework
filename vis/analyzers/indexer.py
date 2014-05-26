#!/usr/bin/env python
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
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>
.. codeauthor:: Jamie Klassen <michigan.j.frog@gmail.com>

The controllers that deal with indexing data from music21 Score objects.
"""

import pandas
from music21 import stream, converter


def mpi_unique_offsets(streams):
    """
    For a set of streams, find the offsets at which events begin. Used by mp_indexer.

    :param streams: A list of Streams in which to find the offsets at which events begin.
    :type streams: list of music21.stream.Stream

    :returns: A list of floating-point numbers representing offsets at which a new event begins in
        any of the streams. Offsets are sorted from lowest to highest (start to end).
    :rtype: list of float
    """
    offsets = ({e.offset for e in part.elements} for part in streams)
    return sorted(set.union(*offsets))  # pylint: disable=W0142


def mpi_vert_aligner(events):
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


def stream_indexer(pipe_index, parts, indexer_func, types=None):
    """
    Perform the indexation of a part or part combination. This is a module-level function designed
    to ease implementation of multiprocessing.

    If your Indexer has settings, use the indexer_func() to adjust for them.

    If an offset has multiple events of the correct type, only the "first" discovered results will
    be included in the output. This may produce misleading results when, for example, a double-stop
    was imported as two Note objects in the same Part, rather than as a Chord.

    :param pipe_index: An identifier value for use by the caller.
    :type pipe_index: any
    :param parts: A list of at least one Stream object. Every new event, or change of simlutaneity,
        will appear in the outputted index. Therefore, the new index will contain at least as many
        events as the inputted Part or Series with the most events.
    :type parts: list of music21.stream.Stream
    :param indexer_func: This function transforms found events into a unicode object.
    :type indexer_func: function
    :param types: Only objects of a type in this list will be passed to the indexer_func for
        inclusion in the resulting index.
    :type types: list of types

    :returns: The "pipe_index" argument and the new index. The new index is a pandas.Series where
        every element is a unicode object. The Series' index corresponds to the quarterLength
        offset of the event in the input Stream.
    :rtype: 2-tuple of any and pandas.Series
    """
    # NB: It's hard to tell, but this function is based on music21.stream.Stream.chordify()
    # NB2: This must not be a single-line if/else statement, or the getter() call will fail.
    if types is None:
        getter = lambda thing: thing
    else:
        getter = lambda thing: thing.getElementsByClass(types)

    # Convert "frozen" Streams, if needed; flatten the streams and filter classes
    if isinstance(parts[0], basestring):
        all_parts = [getter(converter.thaw(each).flat) for each in parts]
    else:
        all_parts = [getter(part.flat) for part in parts]

    # collect all unique offsets
    unique_offsets = mpi_unique_offsets(all_parts)

    # in cases where there will be more than one event at an offset, we need this
    offsets_for_series = []

    # Convert to requested index format
    new_series_data = []
    for off in unique_offsets:
        # inspired by vis.controllers.analyzer._event_finder() in vis9c
        current_events = []
        for part in all_parts:  # find the events happening at this offset in all parts
            current_events.append(list(part.getElementsByOffset(off, mustBeginInSpan=False)))

        # Arrange groups of things to index
        current_events = [[event[0] for event in current_events]]

        # Index previously-arranged groups
        for each_simul in current_events:
            new_series_data.append(indexer_func(each_simul))
            offsets_for_series.append(off)

    return pipe_index, pandas.Series(new_series_data, index=offsets_for_series)


def series_indexer(pipe_index, parts, indexer_func):
    """
    Perform the indexation of a part or part combination. This is a module-level function designed
    to ease implementation of multiprocessing with the MPController module.

    If your Indexer has settings, use the indexer_func() to adjust for them.

    :param pipe_index: An identifier value for use by the caller.
    :type pipe_index: any
    :param parts: A list of at least one Series object. Every new event, or change of simlutaneity,
        will appear in the outputted index. Therefore, the new index will contain at least as many
        events as the inputted Part or Series with the most events. This is not a DataFrame, since
        each part will likely have different offsets.
    :type parts: list of pandas.Series
    :param indexer_func: This function transforms found events into a unicode object.
    :type indexer_func: function

    :returns: The new index where each element is a unicode object and the "index" of the pandas
        object corresponds to the offset at which each event begins. Index 0 is the argument
        "pipe_index" unchanged.
    :rtype: 2-tuple with "pipe_index" and pandas.Series or pandas.DataFrame

    :raises: ValueError, if there are multiple events at an offset in any of the inputted Series.
    """

    # find the offsets at which things happen
    all_offsets = pandas.Index([])
    for i in xrange(0, len(parts)):
        all_offsets = all_offsets.union(parts[i].index)

    # Copy each Series with index=offset values that match all_offsets, filling in non-existant
    # offsets with the value that was at the most recent offset with a value. We put these in a
    # dict so DataFrame.__init__() puts parts in columns.
    in_dict = {i: part.reindex(index=all_offsets, method='ffill') for i, part in enumerate(parts)}
    dframe = pandas.DataFrame(in_dict)

    # do the indexing
    new_series_data = dframe.apply(indexer_func, axis=1)

    # make the new index
    return pipe_index, new_series_data


class Indexer(object):
    """
    Create an index of a music21 stream.

    Use the :attr:`requires_score` attribute to know whether :meth:`__init__` requires a list of
    :class:`~music21.stream.Part` objects. If ``False``, read the documentation to know which
    indexers' results it requires.

    The name of the indexer, as stored in an :class:`IndexedPiece`, is the unicode-format version
    of the class name.
    """

    # just the standard instance variables
    required_score_type = None
    possible_settings = {}
    default_settings = {}
    # self._score
    # self._indexer_func
    # self._types

    # Ignore that we don't use the "settings" argument in this method. Subclasses handle it.
    # pylint: disable=W0613
    def __init__(self, score, settings=None):
        """
        Create a new Indexer.

        :param score: Depending on how this Indexer works, this is a list of either :class:`Part`
            or :class:`Series` objects to use in creating a new index.
        :type score: list of :class:`pandas.Series` or :class:`music21.stream.Part`
        :param settings: A dict of all the settings required by this :class:`Indexer`. All required
            settings should be listed in subclasses. Default is ``None``.
        :type settings: dict or None

        :raises: :exc:`TypeError` if the ``score`` argument is not a list of the right types.
        :raises: :exc:`RuntimeError` if the required settings are not present in the ``settings``
            argument.
        """
        # Check the "score" argument is either uniformly Part or Series objects.
        for elem in score:
            if not isinstance(elem, self.required_score_type):
                msg = u'{} requires {} objects, not {}'.format(self.__class__,
                                                               self.required_score_type,
                                                               type(elem))
                raise TypeError(msg)
        # Call our superclass constructor, then set instance variables
        super(Indexer, self).__init__()
        self._score = score
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

        :returns: A list of the new indices. The index of each :class:`Series` corresponds to the
            index of the :class:`Part` or :class:`Series` used to generate it, as given to the
            constructor. Each element in each :class:`Series` is a basestring (unless specified
            otherwise in a subclass).
        :rtype: list of :class:`pandas.Series`
        """
        pass

    def _do_multiprocessing(self, combos):
        """
        Index each part combination and await the jobs' completion. In the future, this method
        may use multiprocessing.

        :param combos: A list of all voice combinations to be analyzed. For example:
            - ``[[0], [1], [2], [3]]``
                Analyze each of four parts independently.
            - ``[[0, 1], [0, 2], [0, 3]]``
                Analyze the highest part compared with all others.
            - ``[[0, 1, 2, 3]]``
                Analyze all parts at once.
            The function stored in :func:`self._indexer_func` must know how to deal with the number
            of simultaneous events it will receive.
        :type combos: list of list of integers

        :returns: Analysis results.
        :rtype: list of :class:`pandas.Series`

        ** Side Effects **

        Blocks until all voice combinations have completed.
        """
        post = []
        # use serial processing
        for each_combo in combos:
            voices = [self._score[x] for x in each_combo]
            if isinstance(self._score[0], stream.Stream):
                post.append(stream_indexer(0, voices, self._indexer_func, self._types)[1])
            else:
                post.append(series_indexer(0, voices, self._indexer_func)[1])
        return post
