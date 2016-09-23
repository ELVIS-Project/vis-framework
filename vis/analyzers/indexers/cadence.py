#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/cadence.py
# Purpose:                Cadence Indexer
#
# Copyright (C) 2016 Marina Borsodi-Benson, Alexander Morgan
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

from vis.analyzers import indexer
import pandas


class CadenceIndexer(indexer.Indexer):
    """
    Using OverBassIndexer and FermataIndexer results, finds cadences as lists
    of occurences before a fermata.

    :keyword 'length': The length of the cadence, or how many events happen
        before a fermata.
    :type 'length': int

    :keyword 'voice': The voice in which you want to look for fermatas.
        The default value for this is 'all'.
    :type 'voice': str or int
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['length', 'voice']

    _MISSING_LENGTH = 'CadenceIndexer requires "length" setting.'
    _LOW_LENGTH = 'Setting "length" must have a value of at least 1.'
    _BAD_VOICE = 'voice setting must be a voice present in the piece'

    def __init__(self, score, settings=None):
        """
        :param score: The OverBassIndexer results and FermataIndexer results
            to be used to find cadences.
        :type score: :class:`pandas.DataFrame`
        :param settings: The setting 'length' is required.
        :type settings: dict

        :raises: :exc:`RuntimeError` if the required setting 'length' is not
            given.
        :raises: :exc:`RuntimeError` if the value of 'length' is below 1
        :raises: :exc:`RuntimeError` if the given voice is not a voice found
            in the piece.
        """

        self.fig = score['over_bass.OverBassIndexer']
        self.ferm = score['fermata.FermataIndexer']

        if settings is None or 'length' not in settings:
            raise RuntimeError(self._MISSING_LENGTH)
        elif settings['length'] < 1:
            raise RuntimeError(self._LOW_LENGTH)
        elif 'voice' not in settings:
            self._settings = settings
            self._settings['voice'] = 'all'
        elif type(settings['voice']) is int and settings['voice'] > len(self.ferm.columns):
            raise RuntimeError(self._BAD_VOICE)
        else:
            self._settings = settings

        super(CadenceIndexer, self).__init__(score, None)

    def run(self):
        """
        Makes a new index of the cadences in the piece.

        :returns: A :class:`DataFrame` of the cadences.
        :rtype: :class:`pandas.DataFrame`

        ***Examples***

        import music21
        import pandas
        import vis.analyzers.indexers import noterest, interval, over_bass, fermata, cadence

        score = music21.converter.parse('example.xml')
        notes = noterest.NoteRestIndexer(score).run()
        intervals = interval.IntervalIndexer(notes).run()

        fermatas = fermata.FermataIndexer(score).run()

        df = pandas.concat([notes, intervals])
        overbass = over_bass.OverBassIndexer(df).run()

        settings = {'length': 3}
        df = pandas.concat([overbass, fermatas])

        cadences = cadence.CadenceIndexer(df, settings).run()
        print(cadences)
        """

        endings = []
        if self._settings['voice'] is 'all':
            for part in self.ferm.columns:
                endings.extend(self.ferm[self.ferm[part].notnull()].index.tolist())
        else:
            endings.extend(self.ferm[self.ferm[str(self._settings['voice'])].notnull()].index.tolist())

        endings = list(set(endings))
        beginnings = []
        indices = self.ferm.index.tolist()

        for ind in endings:
            beginnings.append(indices[indices.index(ind)-self._settings['length']+1])

        beginnings.sort()
        endings.sort()
        locations = list(zip(beginnings, endings))

        cadences = []

        for x in range(len(beginnings)):
            my_cadence = []
            for place in self.fig.loc[locations[x][0]:locations[x][1]].index.tolist():
                my_cadence.extend(self.fig.loc[place].tolist())
            cadences.append(my_cadence)

        result = pandas.DataFrame({'Cadences': pandas.Series(cadences, index=beginnings)})

        return self.make_return(result.columns.values, [result[name] for name in result.columns])
