#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/experimenters/aggregator.py
# Purpose:                Aggregating experimenters.
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

Aggregating experimenters.
"""

import pandas
from vis.analyzers import experimenter


class ColumnAggregator(experimenter.Experimenter):
    """
    Experiment that aggregates data from all columns of a :class:`DataFrame`, a list of \
    :class:`DataFrame` objects, or a list of :class:`Series`, into a single :class:`Series`. \
    Aggregation is done through addition. If a :class:`DataFrame` has a column with the name \
    :obj:`u'all'`, it will *not* be included in the aggregation.
    """

    def __init__(self, index, settings=None):
        """
        :param index: The data to aggregate. You should ensure the row index of each pandas object \
            can be sensibly combined. The data should be numbers.
        :type index: :class:`pandas.DataFrame` or :obj:`list` of :class:`pandas.DataFrame` or of \
            :class:`pandas.Series`

        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: :obj:`dict` or :obj:`None`
        """
        super(ColumnAggregator, self).__init__(index, None)

    def run(self):
        """
        Run the :class:`ColumnAggregator` experiment.

        :returns: A :class:`Series` with an index that is the combination of all indices of the \
            provided pandas objects, and the value is the sum of all values in the pandas objects.
        :rtype: :class:`pandas.Series`
        """
        # make sure we have a single DataFrame
        if isinstance(self._index, list):
            if isinstance(self._index[0], pandas.DataFrame):
                self._index = [ColumnAggregator(x).run() for x in self._index]
            # combine the list-of-Series into a DataFrame
            self._index = pandas.DataFrame(dict([(i, x) for i, x in enumerate(self._index)]))
        # make the sum aggregation
        return self._index.select(lambda x: x != u'all', axis=1).sum(axis=1, skipna=True)
