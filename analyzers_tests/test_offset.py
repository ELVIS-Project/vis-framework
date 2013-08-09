#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import pandas
from vis.analyzers.indexers.offset import FilterByOffsetIndexer


# TODO: add tests for more than one part
# TODO: add tests for the dealing-with-zero-length part of run()
class TestOffsetIndexerSinglePart(unittest.TestCase):
    def test_offset_1part_0(self):
        # 0 parts
        in_val = []
        expected = pandas.DataFrame()
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?

    def test_offset_1part_1(self):
        # 0 length
        # NOTE: this requires much more extensive testing in the multi-part suite
        in_val = [pandas.Series()]
        expected = pandas.DataFrame({0: pandas.Series()})
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?

    def test_offset_1part_2(self):
        # input is expected output
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'b', 'c', 'd'],
                                                      index=[0.0, 0.5, 1.0, 1.5])})
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_3(self):
        # already regular offset interval to larger one
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'c', 'd'], index=[0.0, 1.0, 2.0])})
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_4(self):
        # already regular offset interval to smaller one
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'a', 'b', 'b', 'c', 'c', 'd'],
                                                      index=[0.0, 0.25, 0.5, 0.75,
                                                             1.0, 1.25, 1.5])})
        offset_interval = 0.25
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_4b(self):
        # already regular offset interval to a very small one
        in_val = [pandas.Series(['a', 'b'], index=[0.0, 0.5])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'a', 'a', 'a', 'b'],
                                                      index=[0.0, 0.125, 0.25, 0.375, 0.5])})
        offset_interval = 0.125
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_5(self):
        # already regular offset interval (but some missing) to larger one
        in_val = [pandas.Series(['a', 'b', 'c'], index=[0.0, 0.5, 1.5])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'b', 'c'], index=[0.0, 1.0, 2.0])})
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_6(self):
        # already regular offset interval (but some missing) to smaller one
        in_val = [pandas.Series(['a', 'b', 'c'], index=[0.0, 0.5, 1.5])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'a', 'b', 'b', 'b', 'b', 'c'],
                                                      index=[0.0, 0.25, 0.5, 0.75,
                                                             1.0, 1.25, 1.5])})
        offset_interval = 0.25
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_7(self):
        # irregular offset interval to a large one
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'b', 'c', 'd'],
                                                      index=[0.0, 1.0, 2.0, 3.0])})
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_8(self):
        # irregular offset interval to a small one
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'a', 'b', 'b', 'b', 'c', 'c',
                                                       'c', 'c', 'd'],
                                                      index=[0.0, 0.25, 0.5, 0.75, 1.0,
                                                             1.25, 1.5, 1.75, 2.0, 2.25])})
        offset_interval = 0.25
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_9(self):
        #  targeted test for end-of-piece: when last thing lands on an observed offset
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.0])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'b', 'b', 'c', 'd'],
                                                      index=[0.0, 0.5, 1.0, 1.5, 2.0])})
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

    def test_offset_1part_10(self):
        # targeted test for end-of-piece: when last thing doesn't land on an observed offset
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        expected = pandas.DataFrame({0: pandas.Series(['a', 'b', 'b', 'c', 'c', 'd'],
                                                      index=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5])})
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()
        self.assertEqual(len(expected.columns), len(actual.columns))  # same number of columns?
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # same column index?
        self.assertEqual(len(expected.index), len(actual.index))  # same number of rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same row index?
        for i in xrange(len(expected.columns)):  # compare each Series
            for j in expected[0].index:  # compare each offset
                self.assertEqual(expected[i][j], actual[i][j])

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
OFFSET_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestOffsetIndexerSinglePart)
