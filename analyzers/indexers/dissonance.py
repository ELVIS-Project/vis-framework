#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/dissonance.py
# Purpose:                Indexers related to dissonance.
#
# Copyright (C) 2013, 2014 Christopher Antila
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

What will it do?!
"""

import pandas
from vis.analyzers import indexer


def diss_ind_func(obj):
    """
    If this is a dissonant interval, return the interval.

    :param obj: The intervals to evaluate for dissonance.
    :type obj: :class:`pandas.Series` of ``unicode``

    :returns: The interval, if it is dissonant, or else none.
    :rtype: ``unicode`` or ``None``
    """
    dissonance_list = [u'2', u'4', u'7']
    # TODO: u'd5'
    if obj.iloc[0][-1:] in dissonance_list:
        return obj.iloc[0]
    else:
        return None


class DissonanceIndexer(indexer.Indexer):
    """
    Locate and name "dissonant" intervals in a simultaneity.

    The following are currently considered "dissonant" intervals:
    - 2nd
    - 4th
    - diminished 5th
    - 7th
    """

    required_score_type = pandas.Series
    """
    Provide a list of :class:`pandas.Series`.
    """

    possible_settings = []
    """
    There are no settings?
    """

    default_settings = {}
    """
    There are no settings?
    """

    def __init__(self, score, settings=None):
        """
        Parameters
        ==========
        :param score: The output from :class:`~vis.analyzers.indexers.interval.IntervalIndexer`.
            You must include interval quality and *not* use compound intervals.
        :type score: `list`` of :class:`pandas.Series`

        :param settings: There are no settings?
        :type settings: ``None``

        Raises
        ======
        :raises: :exc:`RuntimeError` if :obj:`score` is the wrong type.
        :raises: :exc:`RuntimeError` if :obj:`score` is not a list of the same types.
        :raises: :exc:`RuntimeError` if required settings are not present in :obj:`settings`.
        """

        # Check all required settings are present in the "settings" argument. You must ignore
        # extra settings.
        # If there are no settings, you may safely remove this.
        #if settings is None:
            #self._settings = {}

        super(DissonanceIndexer, self).__init__(score, None)
        self._indexer_func = diss_ind_func

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        :returns: A list of the new indices. The index of each Series corresponds to the index of
            the Part used to generate it, in the order specified to the constructor. Each element
            in the Series is a basestring.
        :rtype: ``list`` of :class:`pandas.Series`
        """

        # each part separately
        combinations = [[x] for x in xrange(len(self._score))]
        results = self._do_multiprocessing(combinations)
        return results
