#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/figured_bass.py
# Purpose:                Figured bass indexer
#
# Copyright (C) 2016 Marina Borsodi-Benson
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
.. codeauthor:: Marina Borsodi-Benson

    #. Adjust :attr:`required_score_type`.
    #. Add settings to :attr:`possible_settings` and :attr:`default_settings`, as required.
    #. Rewrite the documentation for :meth:`__init__`.
    #. Rewrite the documentation for :meth:`~TemplateIndexer.run`.
    #. Rewrite the documentation for :func:`indexer_func`.
    #. Write all relevant tests for :meth:`__init__`, :meth:`~TemplateIndexer.run`, and \
        :func:`indexer_func`.
    #. Follow the instructions in :meth:`__init__` to write that method.
    #. Follow the instructions in :meth:`~TemplateIndexer.run` to write that method.
    #. Write a new :func:`indexer_func`.
    #. Ensure your tests pass, adding additional ones as required.
    #. Finally, run ``pylint`` with the VIS style rules.
"""

import six
from music21 import stream
from vis.analyzers import indexer
from vis.analyzers.indexers import ngram
import pandas


def indexer_func(obj):
    """
    The function that indexes.

    :param obj: The simultaneous event(s) to use when creating this index. (For indexers using a
        :class:`Score`).
    :type obj: list of objects of the types stored in :attr:`TemplateIndexer._types`

    **or**

    :param obj: The simultaneous event(s) to use when creating this index. (For indexers using a
        :class:`Series`).
    :type obj: :class:`pandas.Series` of strings

    :returns: The value to store for this index at this offset.
    :rtype: str
    """
    return None


class FiguredBassIndexer(indexer.Indexer):

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['horizontal']

    def __init__(self, score, settings=None):

        self.horiz_score = score['interval.HorizontalIntervalIndexer']
        self.vert_score = score['interval.IntervalIndexer']

        if settings is None:
            self._settings = {}
            self.horizontal_voice = len(self.horiz_score.columns) - 1
            self._settings['horizontal'] = len(self.horiz_score.columns) - 1
            
        super(FiguredBassIndexer, self).__init__(score, None)

        # self._types = []

        # self._indexer_func = indexer_func

    def run(self):

        # suffix = ',' + str(self.horizontal_voice)
        # index_pairs = '['
        pairs = []
        results = self.horiz_score[str(self.horizontal_voice)]

        for pair in list(self.vert_score.columns.values):
            if str(self.horizontal_voice) in pair:
                pairs.append(pair)
            
        return pandas.concat([self.vert_score[pairs], results], axis=1)
            #     index_pairs += ' ' + pair
            # index_pairs += '] (' + str(self.horizontal_voice) + ')'


        # print results

        # all_intervals = pandas.concat([self.horiz_score, self.vert_score], axis=1)
        # self._settings['n'] = 1
        # ngrams = ngram.NGramIndexer(all_intervals, self._settings).run()
        # pieces = {'Figured bass': ngrams['ngram.NGramIndexer'].T.loc[[index_pairs]].T,
        #           'Basso seguente': horizontal_intervals['interval.HorizontalIntervalIndexer'][str(horizontal_voice)]}
        # result = pandas.concat(pieces, axis = 1)



































