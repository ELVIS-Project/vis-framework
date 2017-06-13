#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/approach.py
# Purpose:                Approach Indexer
#
# Copyright (C) 2016 M. Ryan Bannon, Marina Cottrell, Alexander 
# Morgan
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
# You should have received a copy of the GNU Affero General Public 
# License along with this program.  If not, see 
# <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------- #
"""
.. codeauthor:: Marina Cottrell <marinaborsodibenson@gmail.com>

"""

from vis.analyzers import indexer
import pandas


class ApproachIndexer(indexer.Indexer):
    """
    Using ``OverBassIndexer`` and ``FermataIndexer`` results, finds 
    cadences as lists of events in the approach to a fermata.

    Call this indexer via the ``get_data()`` method of either an 
    ``indexed_piece`` object or an ``aggregated_pieces`` object (see 
    example below).

    :keyword 'length':  The length of the cadence, or how many events 
                        happen before a fermata.
    
    :type 'length':     int

    :keyword 'voice':   The voice in which you want to look for 
                        fermatas. The default value for this is 'all'.
    
    :type 'voice': str or int

    **Example:**

    Prepare an indexed piece and import pandas:

    >>> from vis.models.indexed_piece import Importer
    >>> import pandas
    >>> ip = Importer('path_to_piece.xml')

    Prepare ``OverBassIndexer`` and ``FermataIndexer`` results. For more 
    specific advice on how to do this, please see the documentation of 
    those two indexers. These two DataFrames should be passed as a list. 
    For simplicity, including the ``FermataIndexer`` results is 
    optional, and this example shows how to use the ``ApproachIndexer`` 
    without explicitly providing the ``FermataIndexer`` results, so the 
    'data' argument is a singleton list.

    >>> overbass_input_dfs = [ip.get_data('noterest'), 
            ip.get_data('vertical_interval')]
    >>> ob_setts = {
            'type': 'notes'
        }
    >>> overbass = ip.get_data('over_bass', data=overbass_input_dfs, 
            settings=ob_setts)
    
    Get the ``ApproachIndexer`` results with specified settings:
    
    >>> approach_setts = {'length': 3}
    >>> ip.get_data('approach', data=[overbass], settings=approach_setts)
    
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['length', 'voice']

    _MISSING_LENGTH = 'ApproachIndexer requires "length" setting.'
    _LOW_LENGTH = 'Setting "length" must have a value of at least 1.'
    _BAD_VOICE = 'voice setting must be a voice present in the piece'

    def __init__(self, score, settings=None):
        """
        :param score:   The OverBassIndexer results and FermataIndexer 
            results to be used to find cadences.
        
        :type score: :class:`pandas.DataFrame`
        
        :param settings: The setting 'length' is required.
        
        :type settings: dict

        :raises: :exc:`RuntimeError` if the required setting 'length' is 
            notgiven.
        
        :raises: :exc:`RuntimeError` if the value of 'length' is below 1
        
        :raises: :exc:`RuntimeError` if the given voice is not a voice 
            found in the piece.

        """
        self._score = pandas.concat(score, axis=1)
        self.fig = self._score['over_bass.OverBassIndexer']
        self.ferm = self._score['fermata.FermataIndexer']

        if settings is None or 'length' not in settings:
            raise RuntimeError(self._MISSING_LENGTH)
        elif settings['length'] < 1:
            raise RuntimeError(self._LOW_LENGTH)
        elif 'voice' not in settings:
            self._settings = settings
            self._settings['voice'] = 'all'
        elif(type(settings['voice']) is int 
            and settings['voice'] >= len(self.ferm.columns)):
            raise RuntimeError(self._BAD_VOICE)
        else:
            self._settings = settings

        super(ApproachIndexer, self).__init__(score, None)

    def run(self):
        """
        Makes a new index of the approaches to fermatas in the piece.

        :returns: A :class:`DataFrame` of the approaches.
        :rtype: :class:`pandas.DataFrame`
        """

        endings = []
        if self._settings['voice'] is 'all':
            for part in self.ferm.columns:
                endings.extend(self.ferm[
                    self.ferm[part].notnull()].index.tolist())
        else:
            endings.extend(self.ferm[self.ferm[
                str(self._settings['voice'])].notnull()].index.tolist())

        endings = list(set(endings))
        beginnings = []
        indices = self.ferm.index.tolist()

        for ind in endings:
            beginnings.append(indices[
                indices.index(ind)-self._settings['length']+1])

        beginnings.sort()
        endings.sort()
        locations = list(zip(beginnings, endings))

        approaches = []

        for x in range(len(beginnings)):
            my_approach = []
            for place in self.fig.loc[locations[x][0]:locations[x][1]].index.tolist():
                my_approach.extend(self.fig.loc[place].tolist())
            approaches.append(my_approach)

        result = pandas.DataFrame(
            {'Approaches': pandas.Series(approaches, index=beginnings)})

        return self.make_return(result.columns.values, 
            [result[name] for name in result.columns])
