#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/active_voices.py
# Purpose:                Active voices indexer
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

import music21
from vis.analyzers import indexer
import numpy
import pandas


class ActiveVoicesIndexer(indexer.Indexer):
    """
    Class that indexer the number of voices active at each offset.
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['attacked']
    """
    :keyword 'attacked': attacked decides if voiced counted as active need to be attacking at that offset or not.
    :type 'attacked': boolean
    """
    default_settings = {'attacked': False}


    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: :class:`pandas.DataFrame`
        :param settings: All the settings required by this indexer.
        :type settings: dict or None

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        """

        if settings is not None and 'attacked' in settings:
            self._settings = {'attacked': settings['attacked']}
        else:
            self._settings = self.default_settings

        self.score = score

        super(ActiveVoicesIndexer, self).__init__(score, None)


    def run(self):
        """
        :returns: Make a new index of the active voices in the piece.
        :rtype: :class:`pandas.DataFrame`
        """

        num_voices = []

        for x in range(len(self.score.index)):
            voices = []

            for name in self.score.columns.values:
                voices.append(self.score[name].tolist()[x])

            if self._settings['attacked']:
                voices = [voice for voice in voices if type(voice) is not float]

            voices = [voice for voice in voices if type(voice) is not str]
            num_voices.append(len(voices))

        result = pandas.DataFrame({'Active Voices': pandas.Series(num_voices, index=self.score.index)})
        return self.make_return(result.columns.values, [result[name] for name in result.columns])