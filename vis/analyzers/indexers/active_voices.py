#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/active_voices.py
# Purpose:                Active voices indexer
#
# Copyright (C) 2016 Marina Cottrell, and Alexander Morgan
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
.. codeauthor:: Alexander Morgan

"""

from vis.analyzers import indexer
import pandas


def indexer1(x):

    """
    Used internally by the :class:`ActiveVoicesIndexer` to count 
    individualevents.
    """
    if x == 'Rest' or isinstance(x, float):
        return 0
    else:
        return 1


class ActiveVoicesIndexer(indexer.Indexer):
    """
    Indexer that counts the number of voices active at each offset. It 
    can either find all voices sounding, or only the voices that are 
    attacking, depending on the settings passed. 

    Call this indexer via the ``get_data()`` method of either an 
    ``indexed_piece`` object or an ``aggregated_pieces`` object (see 
    example below). If nothing is passed in the 'data' argument of the 
    call to ``get_data()``, then the default is to process the 
    ``NoteRestIndexer`` results of the ``indexed_piece`` in question. 
    You can pass some other DataFrame in the 'data' argument, but it is 
    discouraged.

    :keyword 'attacked':    When true, only counts the voices that are 
                            attacking at each offset. Defaults to false.
    
    :type 'attacked':       boolean
    
    :keyword 'show_all':    When true, shows the results at all offsets, 
                            even if there is not change. Defaults to 
                            false.
    
    :type 'show_all':       boolean

    **Examples:**

    Prepare an indexed piece:
    
    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('path_to_piece.xml')

    Get the ``ActiveVoicesIndexer`` results with the default settings:
    
    >>> ip.get_data('active_voices')

    Get the ``ActiveVoicesIndexer`` results with specified settings:
    
    >>> av_setts = {
            'attacked': True, 
            'show_all': True
        }
    >>> ip.get_data('active_voices', settings=av_setts)
    
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['attacked', 'show_all']

    default_settings = {'attacked': False, 'show_all': False}

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: :class:`pandas.DataFrame`
        :param settings: All the settings required by this indexer.
        :type settings: dict or None
        :raises: :exc:`TypeError` if the ``score`` argument is the wrong 
        type.
        """
        self._settings = self.default_settings.copy()
        if settings is not None:
            self._settings.update(settings)

        super(ActiveVoicesIndexer, self).__init__(score, None)

        if not self._settings['attacked']:
            self._score = score.fillna(method='ffill')

    def run(self):
        """
        :returns: new index of the active voices in the piece.
        :rtype: :class:`pandas.DataFrame`
        """

        post = self._score.applymap(indexer1)
        most = post.sum(axis=1)
        if not self._settings['show_all']:
            most = most[most != most.shift(1)]

        return self.make_return(('Active Voices',), (most,))
