#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_aggregator.py
# Purpose:                Test the aggregating experimenters.
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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import pandas
from vis.analyzers.experimenters.aggregator import ColumnAggregator


class TestColumnAggregator(unittest.TestCase):
    def setUp(self):
        self.column_a = pandas.Series([18, 143, 121, 70, 77, 16, 34, 5],
                                      index=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
        self.column_b = pandas.Series([1, 22, 28, 62, 20], index=['A', 'B', 'C', 'D', 'H'])
        self.column_c = pandas.Series([1, 23, 18, 51, 23, 92, 20],
                                      index=['A', 'B', 'C', 'D', 'F', 'G', 'H'])
        self.column_d = pandas.Series([1, 1, 3, 4, 2, 13, 10],
                                      index=['B', 'C', 'D', 'E', 'F', 'G', 'H'])
        self.expected = pandas.Series([20, 189, 168, 186, 81, 41, 139, 55],
                                      index=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])

    def test_column_agg_1(self):
        # that a DataFrame will be aggregated
        deeframe = pandas.DataFrame({u'a': self.column_a, u'b': self.column_b,
                                     u'c': self.column_c, u'd': self.column_d})
        actual = ColumnAggregator(deeframe).run()
        self.assertSequenceEqual(list(self.expected.index), list(actual.index))
        self.assertEqual(len(self.expected), len(actual))
        self.assertSequenceEqual(list(self.expected), list(actual))

    def test_column_agg_2(self):
        # that a DataFrame's u'all' column won't be aggregated
        deeframe = pandas.DataFrame({u'a': self.column_a, u'b': self.column_b,
                                     u'c': self.column_c, u'd': self.column_d,
                                     u'all': pandas.Series([400, 400, 400],
                                                           index=['A', 'B', 'C'])})
        actual = ColumnAggregator(deeframe).run()
        self.assertSequenceEqual(list(self.expected.index), list(actual.index))
        self.assertEqual(len(self.expected), len(actual))
        self.assertSequenceEqual(list(self.expected), list(actual))

    def test_column_agg_3(self):
        # that a list of Series will be aggregated
        actual = ColumnAggregator([self.column_a, self.column_b, self.column_c, self.column_d]).run()
        self.assertSequenceEqual(list(self.expected.index), list(actual.index))
        self.assertEqual(len(self.expected), len(actual))
        self.assertSequenceEqual(list(self.expected), list(actual))

    def test_column_agg_4(self):
        # that a list of DataFrames is aggregated
        deeframe_1 = pandas.DataFrame({u'a': self.column_a, u'b': self.column_b})
        deeframe_2 = pandas.DataFrame({u'c': self.column_c, u'd': self.column_d})
        actual = ColumnAggregator([deeframe_1, deeframe_2]).run()
        self.assertSequenceEqual(list(self.expected.index), list(actual.index))
        self.assertEqual(len(self.expected), len(actual))
        self.assertSequenceEqual(list(self.expected), list(actual))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
COLUMN_AGGREGATOR_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestColumnAggregator)
