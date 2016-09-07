#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/experimenters/frequency.py
# Purpose:                Frequency experimenter
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

Experimenters that deal with the frequencies (number of occurrences) of events.
"""

# pylint: disable=pointless-string-statement

import six
import pandas
from vis.analyzers import experimenter


class FrequencyExperimenter(experimenter.Experimenter):
    """
    Calculate the number of occurrences of objects in an index.

    Use the ``'column'`` setting to choose only the results of one previous analyzer. For example,
    if you wanted to calculate the frequency of vertical intervals, you would specify
    ``'interval.IntervalIndexer'``. This would avoid counting, for example, the horizontal intervals
    if they were also present.
    """

    possible_settings = ['column']
    """
    :keyword str 'column': The column name to use for counting frequency. The default is ``None``,
        which counts all columns. Use this to count only the frequency of one previous analyzer.
    """

    default_settings = {'column': None}

    def __init__(self, index, settings=None):
        """
        :param index: The data in which to count frequencies.
        :type index: :class:`pandas.DataFrame` or list of :class:`pandas.DataFrame`
        :param settings: Optional dictionary with the settings described above in
            :const:`possible_settings`.
        :type settings: dict or NoneType
        """

        if settings is None or 'column' not in settings:
            self._settings = {'column': FrequencyExperimenter.default_settings['column']}
        else:
            self._settings = {'column': settings['column']}

        super(FrequencyExperimenter, self).__init__(index, None)

    def run(self):
        """
        Run the :class:`FrequencyExperimenter`.

        :returns: The result of the experiment. Data is stored such that column labels correspond \
            to the part (combinations) totalled in the column, and row labels correspond to a type \
            of the kind of objects found in the given index. Note that all columns are totalled in \
            the "all" column, and that not every part combination will have every interval; in \
            case an interval does not appear in a part combination, the value is :obj:`numpy.NaN`.
        :rtype: list of :class:`pandas.DataFrame`

        ***Example:***

        import music21
        from vis.analyzers.indexers import noterest
        from vis.analyzers.experimenters import frequency

        score = music21.converter.parse('example.xml')
        notes = noterest.NoteRestIndexer(score).run()

        freqs = frequency.FrequencyExperimenter(notes).run()
        print(freqs)
        """

        # ensure we have a list of DatFrame
        if isinstance(self._index, pandas.DataFrame):
            uncounted = [self._index]
        else:
            uncounted = self._index

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

            uncounted = [df.select(select_func, axis=1) for df in uncounted]

        # get the value_counts() on every Series
        counted = []
        for each_df in uncounted:
            each_df_results = {}
            for col_name in each_df:
                each_df_results[col_name] = each_df[col_name].value_counts()
            each_df = pandas.DataFrame(each_df_results)
            # make the MultiIndex and its labels
            if isinstance(each_df.columns[0], tuple):
                tuples = [('frequency.FrequencyExperimenter', label[1]) for label in each_df.columns]
            else:
                tuples = [('frequency.FrequencyExperimenter', label) for label in each_df.columns]
            multiindex = pandas.MultiIndex.from_tuples(tuples, names=['Experimenter', 'Parts'])
            # foist our MultiIndex onto the new results
            each_df.columns = multiindex
            counted.append(each_df)

        return counted
