#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
#
# Copyright (C) 2013, 2014, 2015 Christopher Antila, Jamie Klassen, and Alexander Morgan
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
.. codeauthor:: Alexander Morgan

The controllers that deal with indexing data from music21 Score objects.
"""

import six
import pandas
from music21 import stream, converter
import multiprocessing as mp
from functools import partial


def series_indexer(parts, indexer_func):
    """
    Perform the indexation of a part or part combination. This is a module-level function designed
    to ease implementation of multiprocessing.

    If your :class:`Indexer` has settings, use the :func:`indexer_func` to adjust for them.

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
    for i in range(0, len(parts)):
        all_offsets = all_offsets.union(parts[i].index)

    # Copy each Series with index=offset values that match all_offsets, filling in non-existant
    # offsets with the value that was at the most recent offset with a value. We put these in a
    # dict so DataFrame.__init__() puts parts in columns.
    in_dict = {i: part.reindex(index=all_offsets, method='ffill') for i, part in enumerate(parts)}
    dframe = pandas.DataFrame(in_dict)

    # do the indexing
    new_series_data = dframe.apply(indexer_func, axis=1)
    return new_series_data


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
        if isinstance(score, list) and (req_s_type in (pandas.DataFrame, pandas.Series, stream.Part)):
            if not all([isinstance(e, req_s_type) for e in score]):
                raise TypeError(Indexer._INIT_TYPE_ERR.format(self.__class__,
                                                             self.required_score_type))
        elif isinstance(score, pandas.DataFrame) and req_s_type is pandas.Series:
            if (not isinstance(score.columns, pandas.MultiIndex)) or 1 != len(score.columns.levels[0]):
                raise IndexError(Indexer._INIT_INDEX_ERR)
            else:
                ind_name = score.columns.levels[0][0]
                score = [score.iloc[:, x].dropna() for x in range(len(score.columns))]
        elif isinstance(score, stream.Score) and req_s_type is stream.Part:
            score = [score.parts[i] for i in range(len(score.parts))]

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
        # This if statement is necessary because of a pandas bug, see pandas issue #8222.
        if len(self._score.index) == 0: # If parts have no note, rest, or chord events in them
            result = self._score.copy()
        else: # This is the regular case.
            result = self._score.applymap(self._indexer_func)
        if type(self._score.columns) == pandas.Index:
            labels = self._score.columns
        else:
            labels = self._score.columns.get_level_values(-1)
        return self.make_return(labels, result)


    def _do_multiprocessing(self, combos, index_tied=False, on=True):
        """
        Parallelize the indexing of series. If the call to this function is for stream_indexer jobs,
        it will execute serially because music21 streams cannot be multiprocessed.

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
        :param on: On/off switch allowing multiprocessing to be turned off if necessary.
        :type on: Boolean, defaults to True meaning that multiprocessing will occur if possible.

        :returns: Analysis results.
        :rtype: list of one :class:`pandas.Series` per combo in combos.
        """
        post = []
        jobs = []
        for each_combo in combos:
            # voices holds the music21 Part objects indicated by each_combo
            voices = [self._score[x] for x in each_combo]
            jobs.append(voices)
            if not on and len(jobs) > 0:
                post.append(series_indexer(voices, self._indexer_func))
    
        if on and len(jobs) > 0:
            # Determine an appropriate number of cores to use.
            tasks = len(combos)
            if tasks < 16:
                cores = tasks
            else:
                cores = 16
                
            pool = mp.Pool(cores)
            post = pool.map(partial(series_indexer, indexer_func=self._indexer_func), jobs)
            pool.close()

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
        :type indices: list of :class:`pandas.Series` or a :class:`pandas.DataFrame`

        :returns: A :class:`DataFrame` with the appropriate :class:`~pandas.MultiIndex` required
            by the :meth:`Indexer.run` method signature.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`IndexError` if the number of labels and indices does not match.
        """
        if isinstance(indices, pandas.DataFrame):
            ret = indices
        else:
            if len(labels) != len(indices):
                raise IndexError(Indexer._MAKE_RETURN_INDEX_ERR)
            # the levels argument is necessary below even though it just gets written over by the 
            # multi_index because it ensures that even empty series will be included in the dataframe.
            ret = pandas.concat(indices, levels=labels, axis=1)

        # make the indexer's name using filename and classname (but not full class name)
        my_mod = six.u(str(self.__module__))[six.u(str(self.__module__)).rfind('.') + 1:]
        my_class = six.u(str(self.__class__))[six.u(str(self.__class__)).rfind('.'):-2]
        my_name = my_mod + my_class

        # Apply the multi_index as the column labels.
        iterables = (my_name, labels)
        multi_index = pandas.MultiIndex.from_product(iterables, names = ('Indexer', 'Parts'))
        ret.columns = multi_index

        return ret

