#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/over_bass.py
# Purpose:                Over Bass indexer
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
.. codeauthor:: Marina Borsodi-Benson <marinaborsodibenson@gmail.com>
"""

import six
from music21 import stream
from vis.analyzers import indexer
from vis.analyzers.indexers import ngram
import pandas


class OverBassIndexer(indexer.Indexer):
    """
    Using horizontal events and vertical intervals, this finds the intervals over the bass motion.
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['horizontal', 'type']
    """
    :keyword 'horizontal': The horizontal voice you wish to use as a bass. If not indicated, this is automatically assigned to the lowest voice.
    :type 'horizontal': int

    :keyword 'type': The type of horizontal event you wish to index. 
        The default is 'intervals', which should be used if you are passing in the results of the HorizontalIntervalIndexer. 
        If you are passing in the results of the NoteRestIndexer or FilterByOffsetIndexer those should be indentified as "notes" or "offsets"
    :type 'type': str
    """


    def __init__(self, score, settings=None):
        """
        :param score: The intervals and horizontal events to be used to find the intervals over the bass.
        :type score: :class:`pandas.DataFrame`
        :param settings: There are 2 settings but no required settings
        :type settings: dict or NoneType

        :raises: :exc:`RuntimeError` if the optional setting ``type`` does not match the ``score`` input.
        :raises: :exc:`RuntimeError` if the optional setting ``horizontal`` indicates a voice that does not exist
        """

        if settings is None:
            self._settings = {}
            self._settings['type'] = 'intervals'
        else:
            self._settings = settings

        types = {'intervals': 'interval.HorizontalIntervalIndexer', 
                'notes': 'noterest.NoteRestIndexer', 
                'offsets': 'offset.FilterByOffsetIndexer'}

        if types[self._settings['type']] in score:
            self.horiz_score = score[types[self._settings['type']]]
        else:
            raise RuntimeError('Type given is not found')

        self.vert_score = score['interval.IntervalIndexer']

        if 'horizontal' not in self._settings:
            self._settings['horizontal'] = len(self.horiz_score.columns) - 1
        elif self._settings['horizontal'] > len(self.horiz_score.columns) - 1:
            raise RuntimeError('horizontal setting must be a voice present in the piece.')

        self.horizontal_voice = self._settings['horizontal']
            
        super(OverBassIndexer, self).__init__(score, None)


    def run(self):
        """
        Make a new index of the intervals over the bass motion.

        :returns: A :class:`DataFrame` of the intervals over the bass.
        :rtype: :class:`pandas.DataFrame`
        """

        pairs = []
        intervals = []
        results = self.horiz_score[str(self.horizontal_voice)]
        intervals.append(results.tolist())

        for pair in list(self.vert_score.columns.values):
            if str(self.horizontal_voice) in pair:
                pairs.append(pair)

        for pair in pairs:
            intervals.append(self.vert_score[pair].tolist())

        intervals = zip(*intervals)
        pairs = str(self.horizontal_voice) + ' ' + ' '.join(pairs)

        result = pandas.DataFrame({pairs: pandas.Series([str(intvl) for intvl in intervals], index=self.horiz_score.index)})

        return self.make_return(result.columns.values, [result[name] for name in result.columns])