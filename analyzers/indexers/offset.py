#!/usr/bin/env python
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
Indexers that modify the "offset" values (floats stored as the "index" of a :class:`pandas.Series`),
and potentially the number of events, without modifying the events themselves.
"""

import pandas
from vis.analyzers import indexer


class FilterByOffsetIndexer(indexer.Indexer):
    """
    Indexer that regularizes the "offset" values of observations from other indexers.
    """

    required_score_type = pandas.Series
    "The :class:`FilterByOffsetIndexer` uses :class:`pandas.Series` objects."

    possible_settings = [u'quarterLength']
    """
    A :obj:`list` of possible settings for the :class:`FilterByOffsetIndexer`.

    :keyword u'quarterLength': The quarterLength duration between observations desired in the
        output. This value must not have more than three digits to the right of the decimal
        (i.e. 0.001 is the smallest possible value).
    :type u'quarterLength': :obj:`float`
    """

    def __init__(self, score, settings=None):
        """
        Create a new :class:`FilterByOffsetIndexer`.

        The Indexer regularizes observations from offsets spaced any, possibly irregular,
        quarterLength durations apart, so they are instead observed at regular intervals. This has
        two effects:
        * events that do not begin at an observed offset will only be included in the output if no
          other event occurs before the next observed offset
        * events that last for many observed offsets will be repeated for those offsets

        Since elements' durations are not recorded, the last observation in a Series will always be
        included in the results. If it does not start on an observed offset, it will be included as
        the next observed offset---again, whether or not this is true in the actual music. However,
        the last observation will only ever be counted once, even if a part ends before others in
        a piece with many parts. See the doctests for examples.

        Examples
        ========
        TODO: totally gotta write these!

        Parameters
        ==========
        :param score: A list of Series you wish to filter by offset values, stored in the Index.
        :type score: :obj:`list` of :obj:`pandas.Series`

        :param settings: There is one required setting. See :const:`possible_settings`.
        :type settings: :obj:`dict`

        Raises
        ======
        :raises: :exc:`RuntimeError` if :obj:`score` is the wrong type.
        :raises: :exc:`RuntimeError` if :obj:`score` is not a list of the same types.
        :raises: :exc:`RuntimeError` if the required setting is not present in :obj:`settings`.
        :raises: :exc:`RuntimeError` if the :obj:`u'quarterLength'` setting has a value less
            than 0.001.
        """
        super(FilterByOffsetIndexer, self).__init__(score, None)

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
        :returns: A DataFrame with the indices for all the inputted parts, where the "index" value
            for each part is the same as in the list in which they were submitted to the
            constructor. The "index" for each member Series is the same, starting at 0.0 then at
            every "quarterLength" after, until either the last observation in the piece, or the
            nearest multiple before.
        :rtype: :class:`pandas.DataFrame`
        """
        if 0 == len(self._score):
            return pandas.DataFrame()
        start_offset = None
        try:
            start_offset = int(min([part.index[0] for part in self._score]) * 1000)
        except IndexError:
            # if one of the parts has 0 length
            start_offset = []
            for part in self._score:
                if 0 < len(part.index):
                    start_offset.append(part.index[0])
            if start_offset == []:
                # all the parts have no length, so return a DataFrame with as many empty parts
                return pandas.DataFrame({i: pandas.Series() for i in xrange(len(self._score))})
            start_offset = int(min(start_offset))
        step = int(self._settings[u'quarterLength'] * 1000)
        post = {}
        for i in xrange(len(self._score)):
            if len(self._score[i].index) < 1:
                post[i] = self._score[i]
                continue
            end_offset = int(self._score[i].index[-1] * 1000)
            off_list = list(pandas.Series(range(start_offset, end_offset + step, step)).div(1000.0))
            post[i] = self._score[i].reindex(index=off_list, method='ffill')
        return pandas.DataFrame(post)
