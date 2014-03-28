#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_repeat.py
# Purpose:                Tests for repeat-based indexers.
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
from vis.analyzers.indexers.repeat import FilterByRepeatIndexer


class TestRepeatIndexer(unittest.TestCase):
    def test_offset_1part_0(self):
        # 0 parts
        in_val = []
        expected = []
        ind = FilterByRepeatIndexer(in_val)
        actual = ind.run()
        self.assertEqual(len(expected), len(actual))  # same number of parts?

    def test_offset_1part_1(self):
        # 0 length
        # NOTE: this requires much more extensive testing in the multi-part suite
        in_val = [pandas.Series()]
        expected = [pandas.Series()]
        ind = FilterByRepeatIndexer(in_val)
        actual = ind.run()
        self.assertEqual(len(expected), len(actual))  # same number of parts?
        for part_i in xrange(len(expected)):
            # same number of rows?
            self.assertEqual(len(expected[part_i].index), len(actual[part_i].index))

    def test_offset_1part_2(self):
        # input is expected output
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        expected = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        ind = FilterByRepeatIndexer(in_val)
        actual = ind.run()
        self.assertEqual(len(expected), len(actual))  # same number of parts?
        for i in xrange(len(expected)):  # compare each Series
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_offset_1part_3(self):
        # remove a bunch at the end
        in_val = [pandas.Series(['a', 'b', 'c', 'd', 'd', 'd', 'd'],
                                index=[0.0, 0.5, 1.0, 1.5, 1.6, 1.7, 1.8])]
        expected = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        ind = FilterByRepeatIndexer(in_val)
        actual = ind.run()
        self.assertEqual(len(expected), len(actual))  # same number of parts?
        for i in xrange(len(expected)):  # compare each Series
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_offset_1part_4(self):
        # remove a bunch at the beginning
        in_val = [pandas.Series(['a', 'a', 'a', 'b', 'c', 'd'],
                                index=[0.0, 0.1, 0.2, 0.5, 1.0, 1.5])]
        expected = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        ind = FilterByRepeatIndexer(in_val)
        actual = ind.run()
        self.assertEqual(len(expected), len(actual))  # same number of parts?
        for i in xrange(len(expected)):  # compare each Series
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_offset_1part_5(self):
        # remove every other thing
        in_val = [pandas.Series(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'd'],
                                index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75])]
        expected = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        ind = FilterByRepeatIndexer(in_val)
        actual = ind.run()
        self.assertEqual(len(expected), len(actual))  # same number of parts?
        for i in xrange(len(expected)):  # compare each Series
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_offset_1part_6(self):
        # pseudo-random
        in_val = [pandas.Series(['d', 'd', 'a', 's', 's', 'd', 'f', 'a', 'f', 'f', 's', 'd',
                                 'f', 's', 'f', 'd', 's', 's', 'a', 's'],
                                index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                                       17, 18, 19, 20])]
        expected = [pandas.Series(['d', 'a', 's', 'd', 'f', 'a', 'f', 's', 'd', 'f', 's', 'f',
                                   'd', 's', 'a', 's'],
                                  index=[1, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20])]
        ind = FilterByRepeatIndexer(in_val)
        actual = ind.run()
        self.assertEqual(len(expected), len(actual))  # same number of parts?
        for i in xrange(len(expected)):  # compare each Series
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_offset_2parts_1(self):
        # pseudo-random, many parts
        in_val = [pandas.Series(['d', 'd', 'a', 's', 's', 'd', 'f', 'a', 'f', 'f', 's', 'd', 'f',
                                 's', 'f', 'd', 's', 's', 'a', 's'],
                                index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                                       18, 19, 20]),
                  pandas.Series(['d', 'd', 'a', 's', 's', 'd', 'f', 'a', 'f', 'f', 's', 'd', 'f',
                                 's', 'f', 'd', 's', 's', 'a', 's'],
                                index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                                       18, 19, 20])]
        expected = [pandas.Series(['d', 'a', 's', 'd', 'f', 'a', 'f', 's', 'd', 'f', 's', 'f', 'd',
                                   's', 'a', 's'],
                                  index=[1, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20]),
                    pandas.Series(['d', 'a', 's', 'd', 'f', 'a', 'f', 's', 'd', 'f', 's', 'f', 'd',
                                   's', 'a', 's'],
                                  index=[1, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20])]
        ind = FilterByRepeatIndexer(in_val)
        actual = ind.run()
        self.assertEqual(len(expected), len(actual))  # same number of parts?
        for i in xrange(len(expected)):  # compare each Series
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
REPEAT_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestRepeatIndexer)
