#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/experimenters/aggregator.py
# Purpose:                Aggregating experimenters.
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

Aggregating experimenters.
"""

# pylint: disable=pointless-string-statement

import six
import pandas
from vis.analyzers import experimenter


class ColumnAggregator(experimenter.Experimenter):
    """
    (Arguments for the constructor are listed below).

    Experiment that aggregates data from columns of a :class:`DataFrame`, or a list of
    :class:`DataFrame` objects, by summing each row. Values from columns named ``'all'`` will not
    be included in the aggregated results. You may provide a ``'column'`` setting to guide the
    experimenter to include only certain results.

    **Example 1**

    Inputting single :class:`DataFrame` like this:

    +-------+---------+---------+
    | Index | piece_1 | piece_2 |
    +=======+=========+=========+
    | M3    | 12      | 24      |
    +-------+---------+---------+
    | m3    | NaN     | 36      |
    +-------+---------+---------+
    | P5    | 3       | 9       |
    +-------+---------+---------+

    Yields this :class:`DataFrame`:

    +-------+-------------------------------+
    | Index | 'aggregator.ColumnAggregator' |
    +=======+===============================+
    | M3    | 36                            |
    +-------+-------------------------------+
    | m3    | 36                            |
    +-------+-------------------------------+
    | P5    | 12                            |
    +-------+-------------------------------+

    **Example 2**

    Inputting two :class:`DataFrame` objects is similar.

    +-------+---------+
    | Index | piece_1 |
    +=======+=========+
    | M3    | 12      |
    +-------+---------+
    | P5    | 3       |
    +-------+---------+

    +-------+---------+
    | Index | piece_2 |
    +=======+=========+
    | M3    | 24      |
    +-------+---------+
    | m3    | 36      |
    +-------+---------+
    | P5    | 9       |
    +-------+---------+

    The result is the same :class:`DataFrame`:

    +-------+-------------------------------+
    | Index | 'aggregator.ColumnAggregator' |
    +=======+===============================+
    | M3    | 36                            |
    +-------+-------------------------------+
    | m3    | 36                            |
    +-------+-------------------------------+
    | P5    | 12                            |
    +-------+-------------------------------+

    **Example 3**

    You may also give a :class:`DataFrame` (or a list of :class:`DataFrame` objects) that have a
    :class:`pandas.MultiIndex` as produced by subclasses of :class:`~vis.analyzers.indexer.Indexer`.
    In this case, use the ``'column'`` setting to indicate which indexer's results you wish to
    aggregate.

    +-------+-----------------------------------+---------------------------------+
    |       | 'frequency.FrequencyExperimenter' | 'feelings.FeelingsExperimenter' |
    +       +---------+-------------------------+---------------+-----------------+
    | Index | '0,1'   | '1,2'                   | 'Christopher' | 'Alex'          |
    +=======+=========+=========================+===============+=================+
    | M3    | 12      | 24                      | 'delight'     | 'exuberance'    |
    +-------+---------+-------------------------+---------------+-----------------+
    | m3    | NaN     | 36                      | 'sheer joy'   | 'nonchalance'   |
    +-------+---------+-------------------------+---------------+-----------------+
    | P5    | 3       | 9                       | 'emptiness'   | 'serenity'      |
    +-------+---------+-------------------------+---------------+-----------------+

    If ``'column'`` is ``'frequency.FrequencyExperimenter'``, yet again you will have this
    :class:`DataFrame`:

    +-------+-------------------------------+
    | Index | 'aggregator.ColumnAggregator' |
    +=======+===============================+
    | M3    | 36                            |
    +-------+-------------------------------+
    | m3    | 36                            |
    +-------+-------------------------------+
    | P5    | 12                            |
    +-------+-------------------------------+
    """

    possible_settings = ['column']
    """
    :keyword str 'column': The column name to use for aggregation. The default is ``None``, which
        aggregates across all columns. If you set this to ``'all'``, it will override the default
        behaviour of not including columns called ``'all'``.
    """

    default_settings = {'column': None}

    def __init__(self, index, settings=None):
        """
        **For the __init__() Method**

        :param index: The data to aggregate. The values should be numbers.
        :type index: :class:`pandas.DataFrame` or list of :class:`pandas.DataFrame`

        :param settings: Optional dictionary with the settings described above in
            :const:`possible_settings`.
        :type settings: dict or NoneType
        """

        if settings is None or 'column' not in settings:
            self._settings = {'column': ColumnAggregator.default_settings['column']}
        else:
            self._settings = {'column': settings['column']}

        super(ColumnAggregator, self).__init__(index, None)

    def run(self):
        """
        Run the :class:`ColumnAggregator` experiment.

        :returns: A :class:`Series` with an index that is the combination of all indices of the \
            provided pandas objects, and the value is the sum of all values in the pandas objects.
        :rtype: :class:`pandas.Series`

        ***Example:***

        import music21
        from vis.analyzers.indexers import noterest
        from vis.analyzers.experimenters import aggregator, frequency

        score = music21.converter.parse('example.xml')
        notes = noterest.NoteRestIndexer(score).run()

        freqs = frequency.FrequencyExperimenter(notes).run()
        agg = aggregator.ColumnAggregator(freqs).run()
        print(agg)
        """

        # ensure we have a list of DatFrame
        if isinstance(self._index, pandas.DataFrame):
            aggregated = [self._index]
        else:
            aggregated = self._index

        # if there's a 'column', select it from every DataFrame
        if self._settings['column'] is not None:
            def select_func(column_label):
                """
                Used to select columns; automatically adjusts to select through the column label or
                the upper-most level of a MultiIndex, as required.
                """
                if isinstance(column_label, six.string_types):
                    return column_label == self._settings['column']
                else:
                    return column_label[0] == self._settings['column']

            aggregated = [df.select(select_func, axis=1) for df in aggregated]

        # unless the 'column' is 'all', de-select all the 'all' columns
        if self._settings['column'] != 'all':
            aggregated = [df.select(lambda x: x != 'all', axis=1) for df in aggregated]

        # concatenate the DataFrame together
        aggregated = pandas.concat(aggregated, axis=1)

        # calculate the sum
        aggregated = aggregated.sum(axis=1, skipna=True)

        return pandas.DataFrame({'aggregator.ColumnAggregator': aggregated})
