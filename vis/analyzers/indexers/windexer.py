#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Aids in computational music analysis tasks.
#
# Filename:               analyzers/indexers/windexer.py
# Purpose:                Windexer
#
# Copyright (C) 2016 Marina Cottrell
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
# License along with this program. If not, see 
# <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------- #
"""
.. codeauthor:: Marina Cottrell <marinaborsodibenson@gmail.com>

"""

from vis.analyzers import indexer
import pandas

class Windexer(indexer.Indexer):
    """
    Indexer that creates new a new windowed version of other indexer 
    results.

    :keyword 'window_size': The size of the window of the DataFrame that 
        you would like to look at. The default setting is 4.

    :type 'window_size': integer

    **Example:**

    Prepare an indexed piece:
    
    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('path_to_piece.xml')

    This example prepares "windows" of notes and rests, but any 
    dataframe could be used:
    
    >>> notes = ip.get_data('noterest')
    >>> setts = {'window_size': 4}
    >>> ip.get_data('windexer', data=notes, settings=setts)
    
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['window_size']

    default_settings = {'window_size': 4}

    _BIG_WINDOW = 'Window size is too large'

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        
        :type score: :class:`pandas.DataFrame`
        
        :param settings: The only possible setting is 'window_size'
        
        :type settings: dict or None
        
        :raises: :exc:`TypeError` if the ``score`` argument is the wrong 
            type.
        
        :raises: :exc:`RuntimeError` if the given window size is too big
        
        """

        self._score = score

        if settings is None:
            self._settings = Windexer.default_settings
        elif settings['window_size'] > len(score):
            raise RuntimeError(self._BIG_WINDOW)
        else:
            self._settings = settings

        super(Windexer, self).__init__(score, None)

    def run(self):
        """
        Make a new windowed index of the indexer results.
        
        :returns: The new windowed DataFrame.
        
        :rtype: :class:`pandas.DataFrame`
        
        """

        x = 0
        l = self._settings['window_size'] - 1

        indices = self._score.index.tolist()
        windowed = pandas.DataFrame(self._score[indices[x]:indices[l]])

        x += 1
        l += 1
        
        while l < len(indices):

            temp = pandas.DataFrame(self._score[indices[x]:indices[l]])
            windowed = pandas.concat([windowed, temp])
            x += 1
            l += 1

        return windowed
