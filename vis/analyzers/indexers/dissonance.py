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

Indexers related to dissonance.
"""

# disable "string statement has no effect" warning---they do have an effect with Sphinx!
# pylint: disable=W0105

import pandas
from vis.analyzers import indexer


class DissonanceIndexer(indexer.Indexer):
    """
    Remove consonant intervals. All remaining intervals are a "dissonance."

    The following intervals are curently considered "consonant": P1, m3, M3, P5, m6, M6, and P8.
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
        :param score: The output from :class:`~vis.analyzers.indexers.interval.IntervalIndexer`.
            You must include interval quality and *not* use compound intervals.
        :type score: `list`` of :class:`pandas.Series`

        :param settings: There are no settings.
        :type settings: ``None``

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(DissonanceIndexer, self).__init__(score, None)

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
        results = [p.loc[~p.str.contains(r'P1|m3|M3|P5|m6|M6|P8')] for p in self._score]
        return results
