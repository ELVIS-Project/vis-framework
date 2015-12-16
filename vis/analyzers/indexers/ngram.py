#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/ngram.py
# Purpose:                k-part anything n-gram Indexer
#
# Copyright (C) 2013, 2014 Christopher Antila, Alexander Morgan
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
.. codeauthor:: Alexander Morgan

Indexer to find k-part any-object n-grams.
"""

# pylint: disable=pointless-string-statement

import six
import pandas
from vis.analyzers import indexer
import pdb
import time
import numpy as np


class NGramIndexer(indexer.Indexer):
    """
    Indexer that finds k-part n-grams from other indices.

    The indexer requires at least one "vertical" index, and supports "horizontal" indices that seem
    to "connect" instances in the vertical indices. Although we use "vertical" and "horizontal" to
    describe these index types, because the class is an abstraction of two-part interval n-grams,
    you can supply any information as either type of index. If you want one-part melodic n-grams
    for example, you should supply the relevant interval information as the "vertical" component.

    There is no relationship between the number of index types, though there must be at least one
    "vertical" index.

    The ``'horizontal'`` and ``'vertical'`` settings determine which columns of the ``score``
    :class:`DataFrame` are included in the n-gram output. They are added to the n-gram in the order
    specified, so if the ``'vertical'`` setting is
    ``[('noterest.NoteRestIndexer', '1'), ('noterest.NoteRestIndexer', '0')]``, this will put the
    lower part (with index ``'1'``) before the higher part (with index ``'0'``). Note that both the
    indexer's name and the part-combination name must be included.

    This is an example minimum ``settings`` dictionary for making interval 3-grams:::

        {'vertical': [('interval.IntervalIndexer', '0,1')],
         'horizontal': [('interval.HorizontalIntervalIndexer', '1')],
         'n': 3}

    IMPORTANT: the data associated with the ``'horizontal'`` settings should have been generated
    with ``'horiz_attach_later'`` set to ``True``. If not, the resulting n-grams will have their
    "horizontal" intervals incorrectly offset.

    In the output, groups of "vertical" events are normally enclosed in brackets, while groups of
    "horizontal" events are enclosed in parentheses. For cases where there is only one index in a
    particular direction, you can avoid printing the brackets or parentheses by setting the
    ``'mark singles'`` setting to ``False`` (the default is ``True``).

    If you want n-grams to terminate when finding one or several particular values, you can specify
    this with the ``'terminator'`` setting.

    To show that a horizontal event continues, we use ``'_'`` by default, but you can set this
    separately, for example to ``'P1'`` ``'0'``, as seems appropriate. Note that the default
    :class:`WorkflowManager` overrides this setting by dynamically adjusting for interval quality,
    and also offers a ``'continuer'`` setting of its own, which is passed to this indexer.

    You can also use the :class:`NGramIndexer` to collect "stacks" of single vertical events. If
    you provide indices of intervals above a lowest part, for example, these "stacks" become the
    figured bass signature of a single moment. Set ``'n'`` to ``1`` for this feature. Horizontal
    events are obviously ignored in this case.
    """

    required_score_type = 'pandas.DataFrame'

    possible_settings = ['horizontal', 'vertical', 'n', 'hanging', 'mark_singles', 'terminator', 'continuer', 'mp']
    """
    A list of possible settings for the :class:`NGramIndexer`.

    :keyword 'horizontal': Selectors for the parts to consider as "horizontal."
    :type 'horizontal': list of (str, str) tuples
    :keyword 'vertical': Selectors for the parts to consider as "vertical."
    :type 'vertical': list of (str, str) tuples
    :keyword 'n': The number of "vertical" events per n-gram.
    :type 'n': int
    :keyword 'hanging': End ngrams with a vertical event if False (default), or end ngrams with 
        their last horizontal event if True.
    :type 'hanigng': boolean
    :keyword 'mark_singles': Whether to use delimiters around a direction's events when
        there is only one event in that direction (e.g., the "horizontal" maps only the activity
        of a single voice). (You may also use ``'mark singles'``).
    :type 'mark_singles': bool
    :keyword 'terminator': Do not find an n-gram with a vertical item that contains any of these
        values.
    :type 'terminator': list of str
    :keyword 'continuer': When there is no "horizontal" event that corresponds to a vertical
        event, this is printed instead, to show that the previous "horizontal" event continues.
    :type 'continuer': str
    :keyword 'mp': Multiprocesses when True (default) or processes serially when False.
    :type 'mp': boolean
    """

    default_settings = {'mark_singles': True, 'horizontal': 'lowest', 'hanging': False, 'terminator': [], 
                        'vertical': 'all pairs', 'continuer': '_', 'mp': True}

    _MISSING_SETTINGS = 'NGramIndexer requires "vertical" and "n" settings'
    _N_VALUE_TOO_LOW = 'NGramIndexer requires an "n" value of at least 1'

    def __init__(self, score, settings=None):
        """
        :param score: The :class:`DataFrame` to use for preparing n-grams. You must ensure the
            :class:`DataFrame` has the columns indicated in the ``settings``, or the :meth:`run`
            method will fail.
        :type score: :class:`pandas.DataFrame`
        :param dict settings: Required and optional settings. See descriptions in
            :const:`possible_settings`.

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        :raises: :exc:`RuntimeError` if required settings are not present in ``settings``.
        :raises: :exc:`RuntimeError` if ``'n'`` is less than ``1``.
        """
        # Check all required settings are present in the "settings" argument.
        if settings is None or 'vertical' not in settings or 'n' not in settings:
            raise RuntimeError(NGramIndexer._MISSING_SETTINGS)
        elif settings['n'] < 1:
            raise RuntimeError(NGramIndexer._N_VALUE_TOO_LOW)
        else:
            self._settings = NGramIndexer.default_settings.copy()
            self._settings.update(settings)
     
        super(NGramIndexer, self).__init__(score, None)

        if self._settings['vertical'] == 'all pairs':
            self._settings['vertical'] = [(x,) for x in self._score[0]['interval.IntervalIndexer'].columns]

        if self._settings['horizontal'] == 'lowest':
            temp = [list(map(int, x[0].split(','))) for x in self._settings['vertical']]
            self._settings['horizontal'] = [(str(max(y)),) for y in temp]
        elif self._settings['horizontal'] == 'highest':
            temp = [list(map(int, x[0].split(','))) for x in self._settings['vertical']]
            self._settings['horizontal'] = [(str(min(y)),) for y in temp]


    def run(self):
        """
        Make an index of k-part n-grams of anything.

        :returns: A single-column :class:`~pandas.DataFrame` with the new index.
        """
        n = self._settings['n']        
        post = []
        cols = []
        for j, verts in enumerate(self._settings['vertical']):
            events = {}
            events[('v', 'v0')] = '['
            col_label = []
            for i, name in enumerate(verts):
                if i == 0:
                    events[('v', 'v1')] = self._score[0].loc[:, ('interval.IntervalIndexer', name)].dropna()
                    col_label.append(name)
                else:
                    events[('v', 'v' + str(i + 1))] = ' ' + self._score[0].loc[:, ('interval.IntervalIndexer', name)].dropna()
                    col_label.extend((' ', name))
            events[('v', 'v' + str(len(verts) + 1))] = '] '

            if self._settings['horizontal']: # NB: the bool value of an empty list is False.
                horizs = self._settings['horizontal'][j]
                events[('h', 'h0')] = '('
                for i, name in enumerate(horizs):
                    if i == 0:
                        events[('h', 'h' + str(i + 1))] = self._score[1].loc[:, ('interval.HorizontalIntervalIndexer', name)].dropna()
                        col_label.extend((':', name))
                    else:
                        events[('h', 'h' + str(i + 1))] = ' ' + self._score[1].loc[:, ('interval.HorizontalIntervalIndexer', name)].dropna()
                        col_label.extend((' ', name))
                events[('h', 'h' + str(len(horizs) + 1))] = ') '
            
            cols.append(' '.join(col_label))
            events = pandas.DataFrame.from_dict(events)
            
            v_filled = events.loc[:, 'v'].fillna(method='ffill')
            # Fill in all "horizontal" NaN values with the continuer
            if 'h' in events: # XXXX Can't we ffill all of the columns at the same time?
                h_filled = events.loc[:, 'h'].fillna(value=self._settings['continuer'])
                events = pandas.concat((v_filled, h_filled), axis=1)
                chunks = [events.shift(-x) for x in range(n - 1)]
            else:
                chunks = [v_filled.shift(-x) for x in range(n - 1)]
            if not self._settings['hanging']:
                chunks.append(v_filled.shift(-n + 1))
            ngram_df = pandas.concat(chunks, axis=1)
            
            # Get rid of the rows that contain any of the terminators
            if self._settings['terminator']:
                ngram_df = ngram_df.loc[~(ngram_df.isin(self._settings['terminator'])).apply(np.any, axis=1)]
            
            # Concatenate strings of each row to turn df into a series and also remove the last n-1
            # observations since they can't contain valid n-grams.
            res = ngram_df.iloc[:(-n+1), 0].str.cat([ngram_df.iloc[:(-n+1), x] for x in range(1, len(ngram_df.columns))])
            
            # Get rid of the trailing space in each ngram and add this combo to post
            post.append(res.str.rstrip())

        return self.make_return(cols, post)
