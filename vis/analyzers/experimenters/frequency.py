#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/experimenters/frequency.py
# Purpose:                Frequency experimenter
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

Experimenters that deal with the frequencies (number of occurrences) of events.
"""

import pandas
from vis.analyzers import experimenter


def experimenter_func(obj):
    """
    Used by the :class:`FrequencyExperimenter` to calculate the frequencies of things in an index.

    :param obj: An identifier plus the results of an indexer.
    :type obj: :obj:`tuple` of (anything, :class:`pandas.Series`)

    :returns: An identifier plus the result of this indexation. In the series, the index is the \
        names of objects found in the inputted series, and the value is the number of occurrences. \
        The first element is the first element given here, used for identification purposes.
    :rtype: :obj:`tuple` of (anything, :class:`pandas.Series`)
    """
    thing_dict = {}
    for each in obj[1]:
        if each not in thing_dict:
            thing_dict[each] = sum(obj[1] == each)
    return obj[0], pandas.Series(thing_dict)


class FrequencyExperimenter(experimenter.Experimenter):
    """
    Calculate the number of occurrences of things found in an index.
    """

    possible_settings = []
    default_settings = {}

    def __init__(self, index, settings=None):
        """
        .. note:: It is the caller's responsibility to provide indices with the proper settings.

        :param index: A list of :class:`Series`, where each one is the result of an indexer for \
            one of the parts in this score.
        :type index: :obj:`list` or :obj:`dict` of :class:`pandas.Series`
        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: :obj:`dict` or :obj:`None`
        """
        super(FrequencyExperimenter, self).__init__(index, None)

    def run(self):
        """
        Run the :class:`FrequencyExperimenter`.

        :returns: The result of the experiment. Data is stored such that column labels correspond \
            to the part (combinations) totalled in the column, and row labels correspond to a type \
            of the kind of objects found in the given index. Note that all columns are totalled in \
            the "all" column, and that not every part combination will have every interval; in \
            case an interval does not appear in a part combination, the value is :obj:`numpy.NaN`.
        :rtype: :class:`pandas.DataFrame`
        """
        # assemble results per-part
        results = None
        if isinstance(self._index, dict):
            results = [[(x, self._index[x])] for x in self._index.iterkeys()]
        else:
            results = [[(i, x)] for i, x in enumerate(self._index)]
        results = self._do_multiprocessing(experimenter_func, results)
        post = {}
        for result in results:
            post[result[0]] = result[1]
        # assemble all-part results
        tokens = []
        for part_i in post.iterkeys():
            tokens.extend(list(post[part_i].index))
        tokens = set(tokens)
        for i in post.iterkeys():
            post[i].reindex(index=tokens)
        post = pandas.DataFrame(post)
        post[u'all'] = post.sum(axis=1, skipna=True)
        return post
