#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_frequency.py
# Purpose:                Tests for the frequency experimenters.
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
"""Tests for the 'frequency' module."""

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes


import unittest
import six
import numpy
import pandas
from vis.analyzers.experimenters.frequency import FrequencyExperimenter


class TestFrequency(unittest.TestCase):
    """Tests for the FrequencyExperimenter."""
    def setUp(self):
        """prepare base Series used in every test"""
        self.in_a = pandas.Series([4, 3, 1, 5, 5, 4, 2, 0, 0, 4, 2, 4, 5, 6, 2, 2, 1, 5, 0, 5])
        self.in_b = pandas.Series([5, 4, 4, 2, 4, 0, 2, 4, 3, 1, 2, 6, 4, 5, 3, 5, 3, 3, 0, 3])
        self.in_c = pandas.Series([5, 3, 4, 2, 5, 1, 0, 4, 5, 0, 6, 5, 1, 0, 3, 1, 1, 4, 3, 2])
        self.in_d = pandas.Series([0, 2, 1, 1, 5, 1, 1, 2, 5, 1, 0, 2, 2, 5, 5, 3, 1, 5, 1, 2])
        self.freq_a = pandas.Series({5: 5, 4: 4, 2: 4, 0: 3, 1: 2, 6: 1, 3: 1})
        self.freq_b = pandas.Series({4: 5, 3: 5, 5: 3, 2: 3, 0: 2, 6: 1, 1: 1})
        self.freq_c = pandas.Series({5: 4, 1: 4, 4: 3, 3: 3, 0: 3, 2: 2, 6: 1})
        self.freq_d = pandas.Series({1: 7, 5: 5, 2: 5, 0: 2, 3: 1, 4: numpy.NaN, 6: numpy.NaN})  # pylint: disable=no-member

    def test_run_1(self):
        """single DataFrame, no 'column' setting"""
        in_df = pandas.DataFrame({'a': self.in_a, 'b': self.in_b})
        actual = FrequencyExperimenter(in_df).run()
        self.assertEqual(1, len(actual))
        actual = actual[0]['frequency.FrequencyExperimenter']
        self.assertEqual(2, len(actual.columns))
        self.assertSequenceEqual(list(self.freq_a.index), list(actual['a'].index))
        self.assertSequenceEqual(list(self.freq_a.values), list(actual['a'].values))
        self.assertSequenceEqual(list(self.freq_b.index), list(actual['b'].index))
        self.assertSequenceEqual(list(self.freq_b.values), list(actual['b'].values))

    def test_run_2(self):
        """two DataFrame, only count some of the results in each"""
        in_df = [pandas.DataFrame({'a': self.in_a, 'b': self.in_b}),
                 pandas.DataFrame({'a': self.in_a, 'b': self.in_b})]
        actual = FrequencyExperimenter(in_df, {'column': 'a'}).run()
        self.assertEqual(2, len(actual))
        for each_df in actual:
            each_df = each_df['frequency.FrequencyExperimenter']
            self.assertEqual(1, len(each_df.columns))
            if six.PY2:
                self.assertItemsEqual(list(self.freq_a.index), list(each_df['a'].index))
            else:
                self.assertCountEqual(list(self.freq_a.index), list(each_df['a'].index))
            for each in self.freq_a.index:
                self.assertEqual(self.freq_a[each], each_df['a'][each])

    def test_run_3(self):
        """two DataFrame, 'column' breaks a MultiIndex"""
        in_df = [pandas.DataFrame([self.in_a, self.in_b, self.in_c, self.in_d],
                                  index=[['one', 'one', 'two', 'two'], ['a', 'b', 'c', 'd']]).T,
                 pandas.DataFrame([self.in_a, self.in_b, self.in_c, self.in_d],
                                  index=[['two', 'two', 'one', 'one'], ['a', 'b', 'c', 'd']]).T]
        actual = FrequencyExperimenter(in_df, {'column': 'one'}).run()
        self.assertEqual(2, len(actual))
        left_df = actual[0]['frequency.FrequencyExperimenter']
        right_df = actual[1]['frequency.FrequencyExperimenter']
        self.assertEqual(2, len(left_df.columns))
        self.assertEqual(2, len(right_df.columns))
        # left, column 'a'
        if six.PY2:
            self.assertItemsEqual(list(self.freq_a.index), list(left_df['a'].index))
        else:
            self.assertCountEqual(list(self.freq_a.index), list(left_df['a'].index))
        for each in self.freq_a.index:
            self.assertEqual(self.freq_a[each], left_df['a'][each])
        # left, column 'b'
        if six.PY2:
            self.assertItemsEqual(list(self.freq_b.index), list(left_df['b'].index))
        else:
            self.assertCountEqual(list(self.freq_a.index), list(left_df['b'].index))
        for each in self.freq_a.index:
            self.assertEqual(self.freq_b[each], left_df['b'][each])
        # rightt, column 'c'
        if six.PY2:
            self.assertItemsEqual(list(self.freq_c.index), list(right_df['c'].index))
        else:
            self.assertCountEqual(list(self.freq_a.index), list(right_df['c'].index))
        for each in self.freq_a.index:
            self.assertEqual(self.freq_c[each], right_df['c'][each])
        # right, column 'd'  (the only column with NaN)
        if six.PY2:
            self.assertItemsEqual(list(self.freq_d.index), list(right_df['d'].index))
        else:
            self.assertCountEqual(list(self.freq_a.index), list(right_df['d'].index))
        for each in self.freq_a.index:
            if numpy.isnan(self.freq_d[each]):  # pylint: disable=no-member
                self.assertTrue(numpy.isnan(right_df['d'][each]))  # pylint: disable=no-member
            else:
                self.assertEqual(self.freq_d[each], right_df['d'][each])

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
FREQUENCY_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestFrequency)
