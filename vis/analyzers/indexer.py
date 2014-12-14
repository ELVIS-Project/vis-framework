#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
#
# Copyright (C) 2013, 2014 Christopher Antila and Jamie Klassen
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
.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. codeauthor:: Jamie Klassen <michigan.j.frog@gmail.com>

The controllers that deal with indexing data from music21 Score objects.
"""

import six
from six.moves import range, xrange
import pandas
from music21 import stream, converter


def mpi_unique_offsets(streams):
    """
    For a set of :class:`Stream` objects, find the offsets at which events begin. Used by
    :meth:`stream_indexer`.

    :param streams: A list of :class:`Stream` objects in which to find the offsets where events begin.
    :type streams: list of :class:`music21.stream.Stream`

    :returns: A list of floating-point numbers representing offsets at which a new event begins in
        any of the :class:`Stream` objects. Offsets are sorted from lowest to highest (start to end).
    :rtype: list of float
    """
    offsets = ({e.offset for e in part.elements} for part in streams)
    return sorted(set.union(*offsets))  # pylint: disable=W0142


def stream_indexer(pipe_index, parts, indexer_func, types=None):
    """
    Perform the indexation of a :class:`Part` or :class:`Part` combination. This is a module-level
    function designed to ease implementation of multiprocessing.

    If your :class:`Indexer` subclass has settings, use the :func:`indexer_func` to adjust for them.

    If an offset has multiple events of the correct type, only the "first" discovered results will
    be included in the output. This may produce misleading results when, for example, a double-stop
    was imported as two :class:`Note` objects in the same :class:`Part`, rather than as a
    :class:`Chord`.

    :param object pipe_index: An identifier value for use by the caller. This is returned unchanged,
        so a caller may use the ``pipe_index`` as a tag with which to keep track of jobs.
    :param parts: A list of at least one :class:`Stream` object. Every new event or change of
        simlutaneity will appear in the outputted index. Therefore, the new index will contain at
        least as many events as the inputted :class:`Part` with the most events.
    :type parts: list of :class:`music21.stream.Stream`
    :param function indexer_func: This function transforms found events into some other string.
    :param types: Only objects of a type in this list will be passed to the
        :func:`~vis.analyzers.indexers.template.indexer_func` for inclusion in the resulting index.
    :type types: list of type

    :returns: The ``pipe_index`` argument and the new index. The new index is a :class:`pandas.Series`
        where every element is a string. The :class:`~pandas.core.index.Index` of the
        :class:`Series` corresponds to the ``quarterLength`` offset of the event in the inputted
        :class:`Stream`.
    :rtype: 2-tuple of object and :class:`pandas.Series`
    """
    # NB: It's hard to tell, but this function is based on music21.stream.Stream.chordify()
    # NB2: This must not be a single-line if/else statement, or the getter() call will fail.
    if types is None:
        getter = lambda thing: thing
    else:
        getter = lambda thing: thing.getElementsByClass(types)

    # Convert "frozen" Streams, if needed; flatten the streams and filter classes
    if isinstance(parts[0], six.string_types):
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
    to ease implementation of multiprocessing.

    If your :class:`Indexer` has settings, use the :func:`indexer_func` to adjust for them.

    :param pipe_index: An identifier value for use by the caller. This is returned unchanged, so a
        caller may use the ``pipe_index`` as a tag with which to keep track of jobs.
    :type pipe_index: object
    :param parts: A list of at least one :class:`Series` object. Every new event, or change of
        simlutaneity, will appear in the outputted index. Therefore, the new index will contain at
        least as many events as the inputted :class:`Series` with the most events. This is not a
        :class:`DataFrame`, since each part will likely have different offsets.
    :type parts: list of :class:`pandas.Series`
    :param function indexer_func: This function transforms found events into some other string.

    :returns: The ``pipe_index`` argument and the new index. The new index is a :class:`pandas.Series`
        where every element is a string. The :class:`~pandas.core.index.Index` of the
        :class:`Series` corresponds to the ``quarterLength`` offset of the event in the inputted
        :class:`Stream`.
    :rtype: 2-tuple of object and :class:`pandas.Series`

    :raises: :exc:`ValueError` if there are multiple events at an offset in any of the inputted
        :class:`Series`.
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
    An object that manages creating an index of a piece, or part of a piece, based on one feature.

    Use the :attr:`required_score_type` attribute to know what type of object is required in
    :meth:`__init__`.

    The name of the indexer, as stored in the :class:`DataFrame` it returns, is the module name and
    class name. For example, the name of the :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
    is ``'interval.IntervalIndexer'``.

    .. caution::
        This module underwent significant changes for  release 2.0.0. In particular, the
        constructor's ``score`` argument and the :meth:`run` method's return type have changed.
    """

    # just the standard instance variables
    required_score_type = None
    "Described in the :class:`~vis.analyzers.indexers.template.TemplateIndexer`."
    possible_settings = {}
    "Described in the :class:`~vis.analyzers.indexers.template.TemplateIndexer`."
    default_settings = {}
    "Described in the :class:`~vis.analyzers.indexers.template.TemplateIndexer`."
    # self._score  # this will hold the input data
    # self._indexer_func  # this function will do the indexing
    # self._types  # if the input is a Score, this is a list of types we'll use for the index

    # In subclasses, we might get these values for required_score_type. The superclass here will
    # "convert" them into the actual type.
    _TYPE_CONVERTER = {'stream.Part': stream.Part,
                       'stream.Score': stream.Score,
                       'pandas.Series': pandas.Series,
                       'pandas.DataFrame': pandas.DataFrame}

    # Error messages
    _MAKE_RETURN_INDEX_ERR = 'Indexer.make_return(): arguments must have the same legnth.'
    _INIT_KEY_ERR = '{} has an incorrectly-set "required_score_type"'
    _INIT_INDEX_ERR = 'Indexer: got a DataFrame but expected a Series; problem with the MultiIndex'
    _INIT_TYPE_ERR = '{} requires "{}" objects'

    # Ignore that we don't use the "settings" argument in this method. Subclasses handle it.
    # pylint: disable=W0613
    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. Each indexer will specify its
            required input type, of which there will be one. Also refer to the note below.
        :type score: :class:`pandas.DataFrame`, :class:`music21.stream.Score`, or list of \
            :class:`pandas.Series` or of :class:`music21.stream.Part`
        :param settings: A dict of all the settings required by this :class:`Indexer`. All required
            settings should be listed in subclasses. Default is ``None``.
        :type settings: dict or None

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the required settings are not present in the ``settings``
            argument.
        :raises: :exc:`IndexError` if ``required_score_type`` is ``'pandas.Series'`` and the
            ``score`` argument is an improperly-formatted :class:`DataFrame` (e.g., it contains the
            results of more than one indexer, or the columns do not have a :class:`MultiIndex`).

        .. note:: **About the "score" Parameter:**

            A two-dimensional type, :class:`DataFrame` or :class:`Score`, can be provided to an
            indexer that otherwise requires a list of the corresponding single-dimensional type
            (being :class:`Series` or :class:`Part`, respectively).

            When a :class:`Part`-requiring indexer is given a :class:`Score`, the call to the
            :class:`Indexer` superclass constructor (i.e., this method) will use the
            :attr:`~music21.stream.Score.parts` attribute to get a list of :class:`Part` objects.

            When a :class:`Series`-requiring indexer is given a :class:`DataFrame`, the call to the
            :class:`Indexer` superclass constructor (i.e., this method) exepcts a :class:`DataFrame`
            in the style outputted by :meth:`run`. In other words, the columns must have a
            :class:`pandas.MultiIndex` where the first level is the name of the indexer class that
            produced the results and the second level is the name of the part or part combination
            that produced those results. In this case, the :class:`DataFrame` *must* contain the
            results of only one indexer.

            Also in the last case, any ``NaN`` values are "dropped" with :meth:`~pandas.Series.dropna`.
            The ``NaN`` values would have been introduced as the part (or part combination) was
            re-indexed when being added to the :class:`DataFrame`, and they're only relevant when
            considering all the parts at once.
        """
        # check the required_score_type is valid
        try:
            req_s_type = Indexer._TYPE_CONVERTER[self.required_score_type]
        except KeyError:
            raise TypeError(Indexer._INIT_KEY_ERR.format(self.__class__))
        # if "score" is a list, check it's of the right type
        if isinstance(score, list) and (req_s_type is pandas.Series or req_s_type is stream.Part):
            if not all([isinstance(e, req_s_type) for e in score]):
                raise TypeError(Indexer._INIT_TYPE_ERR.format(self.__class__,
                                                             self.required_score_type))
        elif isinstance(score, pandas.DataFrame) and req_s_type is pandas.Series:
            if (not isinstance(score.columns, pandas.MultiIndex)) or 1 != len(score.columns.levels[0]):
                raise IndexError(Indexer._INIT_INDEX_ERR)
            else:
                ind_name = score.columns.levels[0][0]
                num_parts = len(score[ind_name].columns)
                score = [score[ind_name][str(i)].dropna() for i in xrange(num_parts)]
        elif isinstance(score, stream.Score) and req_s_type is stream.Part:
            score = [score.parts[i] for i in xrange(len(score.parts))]

        # Call our superclass constructor, then set instance variables
        super(Indexer, self).__init__()
        self._score = score
        self._indexer_func = None
        self._types = None
        if hasattr(self, '_settings'):
            if self._settings is None:
                self._settings = {}
        else:
            self._settings = {}

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices. Refer to the section below.
        :rtype: :class:`pandas.DataFrame`

        **About Return Values:**

        Every indexer must return a :class:`DataFrame` with a special kind of :class:`MultiIndex`
        that helps organize data across multiple indexers. Programmers making a new indexer should
        follow the instructions in the :class:`TemplateIndexer`
        :meth:`~vis.analyzers.indexers.template.TemplateIndexer.run` method to ensure this happens
        properly.

        Indexers return a :class:`DataFrame` where the columns are indexed on two levels: the first
        level is a string with the name of the indexer, and the second level is a string with the
        index of the part, the indices of the parts in a combination, or some other value as
        specified by the indexer.

        This allows, for example:

        >>> the_score = music21.converter.parse('sibelius_5-i.mei')
        >>> the_score.parts[5]
        (the first clarinet Part)
        >>> the_notes = NoteRestIndexer(the_score).run()
        >>> the_notes['noterest.NoteRestIndexer']['5']
        (the first clarinet Series)
        >>> the_intervals = IntervalIndexer(the_notes).run()
        >>> the_intervals['interval.IntervalIndexer']['5,6']
        (Series with vertical intervals between first and second clarinet)

        This is more useful when you have a larger :class:`DataFrame` with the results of multiple
        indexers. Refer to :func:`Indexer.combine_results` to see how that works.

        >>> some_results = Indexer.combine_results([the_notes, the_intervals])
        >>> some_results['noterest.NoteRestIndexer']['5']
        (the first clarinet Series)
        >>> some_results['interval.IntervalIndexer']['5,6']
        (Series with vertical intervals between first and second clarinet)
        >>> some_results.to_hdf('brahms3.h5', 'table')

        After the call to :meth:`~pandas.DataFrame.to_hdf`, your results are stored in the
        'brahms3.h5' file. When you load them (very quickly!) with the :func:`~pandas.read_hdf`
        method, the :class:`DataFrame` returns exactly as it was.

        .. note:: In release 1.0.0, it was sometimes acceptable to use undocumented return values;
            from release 1.1.0, this is no longer necessary, and you should avoid it. In a future
            release, the :class:`IndexedPiece` class will depend on indexers following these rules.
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

    def make_return(self, labels, indices):
        """
        Prepare a properly-formatted :class:`DataFrame` as should be returned by any :class:`Indexer`
        subclass. We intend for this to be called by :class:`Indexer` subclasses only.

        The index of a label in ``labels`` should be the same as the index of the :class:`Series`
        to which it corresponds in ``indices``. For example, if ``indices[12]`` is the tuba part,
        then ``labels[12]`` might say ``'Tuba'``.

        :param labels: Indices of the parts or the part combinations, or another descriptive label
            as described in the indexer subclass documentation.
        :type labels: list of six.string_types
        :param indices: The results of the indexer.
        :type indices: list of :class:`pandas.Series`.

        :returns: A :class:`DataFrame` with the appropriate :class:`~pandas.MultiIndex` required
            by the :meth:`Indexer.run` method signature.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`IndexError` if the number of labels and indices does not match.
        """
        if len(labels) != len(indices):
            raise IndexError(Indexer._MAKE_RETURN_INDEX_ERR)
        # make the indexer's name using filename and classname (but not full class name)
        my_mod = six.u(str(self.__module__))[six.u(str(self.__module__)).rfind('.') + 1:]
        my_class = six.u(str(self.__class__))[six.u(str(self.__class__)).rfind('.'):-2]
        my_name = my_mod + my_class
        # make the MultiIndex and its labels
        tuples = [(my_name, labels[i]) for i in xrange(len(labels))]
        multiindex = pandas.MultiIndex.from_tuples(tuples, names=['Indexer', 'Parts'])
        # foist our MultiIndex onto the new results
        return pandas.DataFrame(indices, index=multiindex).T
