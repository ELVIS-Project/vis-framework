#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/repeat.py
# Purpose:                Filter consecutive identical events.
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
Indexer to filter consecutive identical events, leaving only the event at the first offset.
"""

import numpy
import pandas
from vis.analyzers import indexer


class FilterByRepeatIndexer(indexer.Indexer):
    """
    Filter consecutive identical events, leaving only the event at the first offset.
    """

    required_indices = []  # empty list accepts results of any Indexer
    required_score_type = pandas.Series
    requires_score = False  # adjust according to previous
    possible_settings = []  # list of strings
    default_settings = {}  # keys are strings, values are anything

    def __init__(self, score, settings=None):
        """
        Create a new FilterByRepeatIndexer.

        Parameters
        ==========
        :param score: Depending on how this Indexer works, this is a list of either Part or Series
            objects to use in creating a new index.
        :type: list of pandas.Series

        :param settings: A dict of all the settings required by this Indexer. All required settings
            should be listed in subclasses. Default is {}.
        :type: None

        Raises
        ======
        :raises: RuntimeError, if
            - the "score" argument is the wrong type.
            - the "score" argument is not a list of the same types.
        """
        super(FilterByRepeatIndexer, self).__init__(score, None)

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = []

        # This Indexer uses pandas magic, not an _indexer_func().
        self._indexer_func = None

    def run(self):
        """
        Make a new index of the piece, removing any event that is identical to the preceding.

        Returns
        =======
        :returns: A list of the new indices. The index of each Series corresponds to the index of
            the Part used to generate it, in the order specified to the constructor. Each element
            in the Series is a basestring.
        :rtype: list of pandas.Series
        """
        # NOTE: I'm relying on pandas efficiency. In the future, maybe we should use an MPC?
        post = []
        for part in self._score:
            if len(part.index) < 2:
                post.append(part)
                continue
            axe_me = []
            prev_off = None
            for offset in list(part.index):
                if prev_off is None:
                    pass  # prevent the other tests from being tried
                elif part[offset] == part[prev_off]:
                    axe_me.append(offset)
                prev_off = offset
            for axed in axe_me:
                part[axed] = numpy.nan
            post.append(part.dropna())
        return post
