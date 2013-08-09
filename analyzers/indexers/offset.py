#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/offset.py
# Purpose:                Indexer to regularize the observed offsets.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Template indexer.
"""

import pandas
from vis.analyzers import indexer


class FilterByOffsetIndexer(indexer.Indexer):
    """
    Indexer to regularize the observed offsets.
    """

    required_indices = []  # empty list accepts results of any Indexer
    required_score_type = pandas.Series
    requires_score = False
    possible_settings = []  # none
    default_settings = {}  # none

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new FilterByOffsetIndexer.

        Parameters
        ==========
        :param score: [pandas.Series] or [music21.stream.Part]
            Depending on how this Indexer works, this is a list of either Part or Series objects
            to use in creating a new index.

        :param settings: dict
            There is one required setting:
            - u'quarterLength': float
                The quarterLength duration between observations desired in the output. This value
                must not have more than three digits to the right of the decimal (i.e. 0.001 is the
                smallest possible value).

        :param mpc : MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        RuntimeError :
            - If the "score" argument is the wrong type.
            - If the "score" argument is not a list of the same types.
            - If a "quarterLength" setting is not found in the "settings" argument.
            - If the "quarterLength" setting has a value less than 0.001.
        """
        super(FilterByOffsetIndexer, self).__init__(score, None, mpc)

        # check the settings instance has a u'quarterLength' property.
        if settings is None or u'quarterLength' not in settings:
            err_msg = u'FilterByOffsetIndexer requires a "quarterLength" setting.'
            raise RuntimeError(err_msg)
        elif settings[u'quarterLength'] < 0.001:
            err_msg = u'FilterByOffsetIndexer requires a "quarterLength" greater than 0.001'
            raise RuntimeError(err_msg)
        else:
            self._settings[u'quarterLength'] = settings[u'quarterLength']

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = []

        # This Indexer uses pandas magic, not an _indexer_func().
        self._indexer_func = None

    def run(self):
        """
        Regularize the observed offsets for the inputted Series.

        Returns
        =======
        :returns: pandas.DataFrame
            Including the indices for all the inputted parts, where the "index" value for each part
            is the same as in the list in which they were submitted to the constructor. The "index"
            for each member Series is the same, starting at 0.0 then at every "quarterLength" after,
            until either the last observation in the piece, or the nearest multiple before.
        """
        if 0 == len(self._score):
            return pandas.DataFrame()
        start_offset, end_offset = None, None
        try:
            start_offset = int(min([part.index[0] for part in self._score]) * 1000)
            end_offset = int(max([part.index[-1] for part in self._score]) * 1000)
        except IndexError:
            # if one of the parts has 0 length
            for part in self._score:
                if 0 < len(part.index):
                    start_offset.append(part.index[0])
            if start_offset is None:
                # all the parts have no length, so return a DataFrame with as many empty parts
                return pandas.DataFrame({i: pandas.Series() for i in xrange(len(self._score))})
            start_offset = int(min(start_offset))
            for part in self._score:
                if 0 < len(part.index):
                    end_offset.append(part.index[-1])
            end_offset = int(min(end_offset))
        step = int(self._settings[u'quarterLength'] * 1000)
        off_list = list(pandas.Series(range(start_offset, end_offset + step, step)).div(1000.0))
        post = {i: x.reindex(index=off_list, method='ffill') for i, x in enumerate(self._score)}
        return pandas.DataFrame(post)
