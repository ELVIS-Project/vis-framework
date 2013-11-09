#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/key.py
# Purpose:                Indexers for key-finding.
#
# Copyright (C) 2013 Christopher Antila
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
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>

Indexers for key-finding.
"""

import pandas
from music21 import stream, analysis
from vis.analyzers import indexer


class KeyIndexer(indexer.Indexer):
    """
    Find the key of a piece.

    .. note:: This indexer currently finds only one key for the entire piece, but in the future
        it may be revised to find the key in "windows," or other indexers may be written for that.
    """

    required_score_type = stream.Score
    possible_settings = []
    """
    In the future, you may be able to specify the algorithm to use. Not now.
    """

    default_settings = {}

    def __init__(self, score, settings=None):
        """
        Parameters
        ==========
        :param score: The score of which to find the key.
        :type score: singleton ``list`` of :class:`music21.stream.Score`

        :param settings: There are no required settings, so you may omit this.
        :type settings: ``dict`` or :const:`None`

        Raises
        ======
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(KeyIndexer, self).__init__(score, None)

    def run(self):
        """
        Make an index of the piece by key; as the indexer currently works, this means returning
        a single-element :class:`Series` that has the (supposed) key of the entire piece.

        Each element in the :class:`Series` is a 2-tuple with the tonic pitch class (the ``name``
        property of the :class:`Pitch` object) and the mode of the key (as a string that's
        probably either ``'major'`` or ``'minor'``).

        Returns
        =======
        :returns: A list with the new index.
        :rtype: singleton ``list`` of :class:`pandas.Series`
        """

        simple_w = analysis.discrete.SimpleWeights()
        the_key = simple_w.getSolution(self._score[0])  # returns music21.key.Key
        return pandas.Series([(the_key.getTonic().name, the_key.mode)], index=[0.0])
