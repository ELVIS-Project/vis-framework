#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/cadence.py
# Purpose:                Cadence Indexer
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


class CadenceIndexer(indexer.Indexer):

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['length', 'voice']

    def __init__(self, score, settings=None):


        self.fig = score['figured_bass.FiguredBassIndexer']
        self.ferm = score['fermata.FermataIndexer']

        if settings is None or 'length' not in settings:
            raise RuntimeError('CadenceIndexer requires "length" setting.')
        elif settings['length'] < 1:
            raise RuntimeError('Setting "length" must have a value of at least 1.')
        else:
            self._settings = settings

        super(CadenceIndexer, self).__init__(score, None)


    def run(self):
        
        endings = []
        for part in self.ferm.columns:
            endings.extend(self.ferm[self.ferm[part].notnull()].index.tolist())

        endings = list(set(endings))
        beginnings = []
        indices = self.ferm.index.tolist()

        for ind in endings:
            beginnings.append(indices[indices.index(ind)-self._settings['length']+1])

        beginnings.sort()
        endings.sort()
        locations = zip(beginnings, endings)

        cadences = []

        for x in range(len(beginnings)):
            my_cadence = []
            for place in self.fig.loc[locations[x][0]:locations[x][1]].index.tolist():
                my_cadence.extend(self.fig.loc[place].tolist())
            cadences.append(my_cadence)

        result = pandas.DataFrame({'Cadences': pandas.Series(cadences, index=beginnings)})

        return self.make_return(result.columns.values, [result[name] for name in result.columns])