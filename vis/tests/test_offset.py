#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_offset.py
# Purpose:                Tests for offset-based indexers.
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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904

import unittest
import six
if six.PY3:
    from unittest import mock
else:
    import mock
import pandas
from vis.analyzers.indexers.offset import FilterByOffsetIndexer


class TestOffsetIndexerSinglePart(unittest.TestCase):
    def test_init_1(self):
        # ensure that __init__() properly sets the "method" setting
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        settings = {'quarterLength': 0.5, 'method': 'silly'}
        ind = FilterByOffsetIndexer(in_val, settings)
        self.assertEqual('silly', ind._settings['method'])

    def test_init_2(self):
        # when there is no quarterLength specified
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        setts = {u'void setting': u'just so void'}
        self.assertRaises(RuntimeError, FilterByOffsetIndexer, in_val, setts)
        try:
            FilterByOffsetIndexer(in_val, setts)
        except RuntimeError as run_err:
            self.assertEqual(FilterByOffsetIndexer._NO_QLENGTH_ERROR, run_err.args[0])

    def test_init_3(self):
        # when the specified quarterLength is less than 0.001
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        setts = {u'void setting': u'just so void', u'quarterLength': 0.0003}
        self.assertRaises(RuntimeError, FilterByOffsetIndexer, in_val, setts)
        try:
            FilterByOffsetIndexer(in_val, setts)
        except RuntimeError as run_err:
            self.assertEqual(FilterByOffsetIndexer._QLENGTH_TOO_SMALL_ERROR, run_err.args[0])

    def test_init_4(self):
        # when the inputted indices have no parts
        in_val = []
        setts = {u'quarterLength': 0.5}
        self.assertRaises(RuntimeError, FilterByOffsetIndexer, in_val, setts)
        try:
            FilterByOffsetIndexer(in_val, setts)
        except RuntimeError as run_err:
            self.assertEqual(FilterByOffsetIndexer._ZERO_PART_ERROR, run_err.args[0])
    
    def test_run_1_a(self):
        # try statement correctly finds minimum start_offset and whole index when no series is empty.
        in_val = [pandas.Series(['A', 'B']), pandas.Series(['B', 'C'], index=[1, 2])]
        settings = {'quarterLength': 1.0, 'method': 'ffill'}
        actual = FilterByOffsetIndexer(in_val, settings).run()
        self.assertListEqual(list(actual.index), [0.0, 1.0, 2.0])
        self.assertEqual(len(actual.columns), 2)

    def test_run_1_b(self):
        # same as test_run_1_a but with a non-zero starting point and non-overlapping indecies.
        in_val = [pandas.Series(['A', 'B'], index=[4, 5]), pandas.Series(['C', 'D'], index=[9, 10])]
        settings = {'quarterLength': 1.0, 'method': 'ffill'}
        actual = FilterByOffsetIndexer(in_val, settings).run()
        self.assertEqual(actual.index[0], 4.0)
        self.assertListEqual(list(actual.index), [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        self.assertEqual(len(actual.columns), 2)

    def test_run_2_a(self):
        # checks if the index and number of columns are correct if one of the passed series is empty.
        in_val = [pandas.Series(['A', 'B']), pandas.Series()]
        settings = {'quarterLength': 1.0, 'method': 'ffill'}
        actual = FilterByOffsetIndexer(in_val, settings).run()
        self.assertListEqual(list(actual.index), [0.0, 1.0])
        self.assertEqual(len(actual.columns), 2)
        
    def test_run_2_b(self):
        # checks if the index and number of columns are correct if all the passed series are empty.
        in_val = [pandas.Series(), pandas.Series()]
        settings = {'quarterLength': 1.0, 'method': 'ffill'}
        actual = FilterByOffsetIndexer(in_val, settings).run()
        self.assertListEqual(list(actual.index), [])
        self.assertEqual(len(actual.columns), 2)

    def test_offset_1part_1(self):
        # 0 length
        in_val = [pandas.Series()]
        expected = pandas.Series()
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(len(in_val), len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertEqual(len(expected), len(actual))  # same number of rows?
        self.assertEqual(list(expected.index), list(actual.index))  # same row names?

    def test_offset_1part_2(self):
        # input is expected output
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        expected = pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_3(self):
        # already regular offset interval to larger one
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        expected = pandas.Series(['a', 'c', 'd'], index=[0.0, 1.0, 2.0])
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_4a(self):
        # already regular offset interval to smaller one
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        expected = pandas.Series(['a', 'a', 'b', 'b', 'c', 'c', 'd'],
                                 index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
        offset_interval = 0.25
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_4b(self):
        # already regular offset interval to a very small one
        in_val = [pandas.Series(['a', 'b'], index=[0.0, 0.5])]
        expected = pandas.Series(['a', 'a', 'a', 'a', 'b'], index=[0.0, 0.125, 0.25, 0.375, 0.5])
        offset_interval = 0.125
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_5(self):
        # already regular offset interval (but some missing) to larger one
        in_val = [pandas.Series(['a', 'b', 'c'], index=[0.0, 0.5, 1.5])]
        expected = pandas.Series(['a', 'b', 'c'], index=[0.0, 1.0, 2.0])
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_6(self):
        # already regular offset interval (but some missing) to smaller one
        in_val = [pandas.Series(['a', 'b', 'c'], index=[0.0, 0.5, 1.5])]
        expected = pandas.Series(['a', 'a', 'b', 'b', 'b', 'b', 'c'],
                                 index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
        offset_interval = 0.25
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_7(self):
        # irregular offset interval to a large one
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        expected = pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 1.0, 2.0, 3.0])
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_8(self):
        # irregular offset interval to a small one
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        expected = pandas.Series(['a', 'a', 'b', 'b', 'b', 'c', 'c', 'c', 'c', 'd'],
                                 index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25])
        offset_interval = 0.25
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_9(self):
        #  targeted test for end-of-piece: when last thing lands on an observed offset
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.0])]
        expected = pandas.Series(['a', 'b', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5, 2.0])
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?

    def test_offset_1part_10(self):
        # targeted test for end-of-piece: when last thing doesn't land on an observed offset
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1])]
        expected = pandas.Series(['a', 'b', 'b', 'c', 'c', 'd'],
                                 index=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(1, len(actual.columns))  # same number of columns?
        actual = actual['0']
        self.assertSequenceEqual(list(expected.values), list(actual.values))  # same rows?
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # same index?


class TestOffsetIndexerManyParts(unittest.TestCase):
    def test_offset_xparts_0a(self):
        # 0 length, many parts
        in_val = [pandas.Series(), pandas.Series(), pandas.Series(), pandas.Series()]
        expected = pandas.DataFrame({str(i): pandas.Series() for i in range(4)})
        offset_interval = 12.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(len(expected.columns), len(actual.columns))
        expected = expected.fillna(value='None')  # avoid having to use isnan()
        actual = actual.fillna(value='None')
        for partname in expected.columns:
            self.assertSequenceEqual(list(expected[partname].values), list(actual[partname].values))
            self.assertSequenceEqual(list(expected[partname].index), list(actual[partname].index))

    def test_offset_xparts_0b(self):
        # 0 length, many parts, but one part has stuff
        in_val = [pandas.Series(), pandas.Series(['a', 'b', 'c'], index=[0.0, 0.5, 1.0]),
                  pandas.Series(), pandas.Series()]
        expected = {str(i): pandas.Series() for i in [0, 2, 3]}
        #print(str(expected))  # DEBUG
        expected['1'] = pandas.Series(['a', 'b', 'c'], index=[0.0, 0.5, 1.0])
        #print(str(expected))  # DEBUG
        expected = pandas.DataFrame(expected)
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(len(expected.columns), len(actual.columns))
        expected = expected.fillna(value='None')  # avoid having to use isnan()
        actual = actual.fillna(value='None')
        for partname in expected.columns:
            self.assertSequenceEqual(list(expected[partname].values), list(actual[partname].values))
            self.assertSequenceEqual(list(expected[partname].index), list(actual[partname].index))

    def test_offset_xparts_1(self):
        # input is expected output; 2 parts
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5]),
                  pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        expected = {'0': pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5]),
                    '1':pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])}
        expected = pandas.DataFrame(expected)
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(len(expected.columns), len(actual.columns))
        expected = expected.fillna(value='None')  # avoid having to use isnan()
        actual = actual.fillna(value='None')
        for partname in expected.columns:
            self.assertSequenceEqual(list(expected[partname].values), list(actual[partname].values))
            self.assertSequenceEqual(list(expected[partname].index), list(actual[partname].index))

    def test_offset_xparts_2(self):
        # input is expected output; 10 parts
        letters = ['a', 'b', 'c', 'd']
        offsets = [0.0, 0.5, 1.0, 1.5]
        in_val = [pandas.Series(letters, index=offsets) for _ in range(10)]
        expected = {str(i): pandas.Series(letters, index=offsets) for i in range(10)}
        expected = pandas.DataFrame(expected)
        offset_interval = 0.5
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(len(expected.columns), len(actual.columns))
        expected = expected.fillna(value='None')  # avoid having to use isnan()
        actual = actual.fillna(value='None')
        for partname in expected.columns:
            self.assertSequenceEqual(list(expected[partname].values), list(actual[partname].values))
            self.assertSequenceEqual(list(expected[partname].index), list(actual[partname].index))

    def test_offset_xparts_3(self):
        # irregular offset interval to 1.0; 3 parts, same offsets
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.1]),
                  pandas.Series(['q', 'w', 'e', 'r'], index=[0.0, 0.4, 1.1, 2.1]),
                  pandas.Series(['t', 'a', 'l', 'l'], index=[0.0, 0.4, 1.1, 2.1])]
        expected = {'0': pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 1.0, 2.0, 3.0]),
                    '1': pandas.Series(['q', 'w', 'e', 'r'], index=[0.0, 1.0, 2.0, 3.0]),
                    '2': pandas.Series(['t', 'a', 'l', 'l'], index=[0.0, 1.0, 2.0, 3.0])}
        expected = pandas.DataFrame(expected)
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(len(expected.columns), len(actual.columns))
        expected = expected.fillna(value='None')  # avoid having to use isnan()
        actual = actual.fillna(value='None')
        for partname in expected.columns:
            self.assertSequenceEqual(list(expected[partname].values), list(actual[partname].values))
            self.assertSequenceEqual(list(expected[partname].index), list(actual[partname].index))

    def test_offset_xparts_4(self):
        # irregular offset interval to 1.0; 3 parts, same offsets
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.9]),
                  pandas.Series(['q', 'w', 'e', 'r'], index=[0.0, 0.3, 1.4, 2.6]),
                  pandas.Series(['t', 'a', 'l', 'l'], index=[0.0, 0.2, 1.9, 2.555])]
        expected = {'0': pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 1.0, 2.0, 3.0]),
                    '1': pandas.Series(['q', 'w', 'e', 'r'], index=[0.0, 1.0, 2.0, 3.0]),
                    '2': pandas.Series(['t', 'a', 'l', 'l'], index=[0.0, 1.0, 2.0, 3.0])}
        expected = pandas.DataFrame(expected)
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(len(expected.columns), len(actual.columns))
        expected = expected.fillna(value='None')  # avoid having to use isnan()
        actual = actual.fillna(value='None')
        for partname in expected.columns:
            self.assertSequenceEqual(list(expected[partname].values), list(actual[partname].values))
            self.assertSequenceEqual(list(expected[partname].index), list(actual[partname].index))

    def test_offset_xparts_5(self):
        # irregular offset interval to 1.0; 3 parts, same offsets, one much longer
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.4, 1.1, 2.9]),
                  pandas.Series(['q', 'w', 'e', 'r'], index=[0.0, 0.3, 1.4, 2.6]),
                  pandas.Series(['t', 'a', 'l', 'l', 'o', 'r', 'd', 'e', 'r'],
                                index=[0.0, 0.2, 1.9, 2.5, 4.0, 5.0, 6.0, 7.0, 8.0])]
        expected = {'0': pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 1.0, 2.0, 3.0]),
                    '1': pandas.Series(['q', 'w', 'e', 'r'], index=[0.0, 1.0, 2.0, 3.0]),
                    '2': pandas.Series(['t', 'a', 'l', 'l', 'o', 'r', 'd', 'e', 'r'], index=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])}
        expected = pandas.DataFrame(expected)
        offset_interval = 1.0
        ind = FilterByOffsetIndexer(in_val, {u'quarterLength': offset_interval})
        actual = ind.run()['offset.FilterByOffsetIndexer']
        self.assertEqual(len(expected.columns), len(actual.columns))
        expected = expected.fillna(value='None')  # avoid having to use isnan()
        actual = actual.fillna(value='None')
        for partname in expected.columns:
            self.assertSequenceEqual(list(expected[partname].values), list(actual[partname].values))
            self.assertSequenceEqual(list(expected[partname].index), list(actual[partname].index))

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
OFFSET_INDEXER_SINGLE_SUITE = \
    unittest.TestLoader().loadTestsFromTestCase(TestOffsetIndexerSinglePart)
OFFSET_INDEXER_MULTI_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestOffsetIndexerManyParts)
