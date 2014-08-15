#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_interval_indexer.py
# Purpose:                Tests for analyzers/indexers/interval.py
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
from music21 import interval, note
from vis.analyzers.indexers.interval import IntervalIndexer, HorizontalIntervalIndexer, \
    real_indexer, key_to_tuple
from vis.tests.test_note_rest_indexer import TestNoteRestIndexer


class TestIntervalIndexerShort(unittest.TestCase):
    """
    These 'short' tests were brought over from the vis9 tests for _event_finder().
    """

    @staticmethod
    def pandas_maker(wrap_this):
        """
        Transform tuple-formatted tests into appropriate pandas.Series.

        Input:
        ======
        --> [[tuples_for_part_1], [tuples_for_part_2], ...]
        --> [[(offset, obj), ...], ...]

        Output:
        =======
        lists of Series, ready for IntervalIndexer.__init__()
        """
        post = []
        for part in wrap_this:
            offsets = []
            objs = []
            for obj in part:
                offsets.append(obj[0])
                objs.append(obj[1])
            post.append(pandas.Series(objs, index=offsets))
        return post

    def test_int_indexer_short_1(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4')], [(0.0, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_2(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4'), (0.25, u'Rest')],
                         [(0.0, u'G3'), (0.25, u'Rest')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_3(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4')], [(0.0, u'G3'), (0.25, u'Rest')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_4(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4'), (0.25, u'Rest')], [(0.0, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_5(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('F4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4'), (0.5, u'F4')],
                         [(0.0, u'G3'), (0.5, u'A3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_6(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3'), (0.5, u'A3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_7(self):
        expected = [(0.0, interval.Interval(note.Note('B3'), note.Note('A4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (1.0, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (1.5, interval.Interval(note.Note('B3'), note.Note('F4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'A4'), (0.5, u'G4', 1.0), (1.5, u'F4')],
                         [(0.0, u'B3'), (0.5, u'G3'),
                          (1.0, u'A3'), (1.5, u'B3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_8(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4', 1.0)],
                         [(0.0, u'G3'), (0.25, u'Rest'), (0.5, u'A3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_9(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (1.0, interval.Interval(note.Note('B3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4', 1.0), (1.0, u'G4')],
                         [(0.0, u'G3'), (0.25, u'Rest'), (0.5, u'A3'), (1.0, u'B3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_10(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3'), (0.25, u'A3', 0.75)]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_11(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3'), (0.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_12(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4', 1.0)],
                         [(0.0, u'G3'), (0.25, u'Rest'), (0.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_13(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.125, u'Rest'),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (0.375, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4', 1.0)],
                         [(0.0, u'G3', 0.125), (0.125, u'Rest', 0.125),
                          (0.25, u'A3', 0.125), (0.375, u'Rest', 0.125), (0.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_14(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.0625, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.125, u'Rest'),
                    (0.1875, u'Rest'),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (0.3125, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (0.375, u'Rest'),
                    (0.4375, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4', 0.0625), (0.0625, u'G4', 0.0625),
                          (0.125, u'G4', 0.0625), (0.1875, u'G4', 0.0625),
                          (0.25, u'G4', 0.0625), (0.3125, u'G4', 0.0625),
                          (0.375, u'G4', 0.0625), (0.4375, u'G4', 0.0625),
                          (0.5, u'G4')],
                         [(0.0, u'G3', 0.125), (0.125, u'Rest', 0.125), (0.25, u'A3', 0.125),
                          (0.375, u'Rest', 0.0625), (0.4375, u'Rest', 0.0625), (0.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_15(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.75, u'Rest'),
                    (1.0, u'Rest'),
                    (1.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4'), (0.5, u'G4'), (0.75, u'Rest'),
                          (1.0, u'G4'), (1.5, u'G4')],
                         [(0.0, u'G3'), (0.5, u'G3'), (0.75, u'Rest'),
                          (1.0, u'Rest'), (1.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_16(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, u'Rest'),
                    (0.75, interval.Interval(note.Note('F3'), note.Note('A4')).name),
                    (1.25, interval.Interval(note.Note('F3'), note.Note('G4')).name),
                    (1.5, interval.Interval(note.Note('E3'), note.Note('B4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4'), (0.5, u'A4', 0.75),
                          (1.25, u'G4'), (1.5, u'B4')],
                         [(0.0, u'G3'), (0.5, u'Rest'),
                          (0.75, u'F3', 0.75), (1.5, u'E3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_int_indexer_short_17(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('A4')).name),
                    (0.75, interval.Interval(note.Note('F3'), note.Note('A4')).name),
                    (1.125, u'Rest'),
                    (1.25, u'Rest'),
                    (1.375, interval.Interval(note.Note('G3'), note.Note('F4')).name),
                    (2.0, interval.Interval(note.Note('G3'), note.Note('E4')).name)]
        expected = TestIntervalIndexerShort.pandas_maker([expected])[0]
        not_processed = [[(0.0, u'G4'), (0.5, u'A4', 0.75), (1.25, u'F4', 0.75),
                          (2.0, u'E4')],
                         [(0.0, u'G3'), (0.5, u'A3'), (0.75, u'F3', 0.375),
                          (1.125, u'Rest'), (1.375, u'G3', 0.625), (2.0, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'0,1']
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_key_to_tuple_1(self):
        in_val = u'5,6'
        expected = (5, 6)
        actual = key_to_tuple(in_val)
        self.assertSequenceEqual(expected, actual)

    def test_key_to_tuple_2(self):
        in_val = u'234522,98100'
        expected = (234522, 98100)
        actual = key_to_tuple(in_val)
        self.assertSequenceEqual(expected, actual)


class TestIntervalIndexerLong(unittest.TestCase):
    bwv77_S_B_basis = [
        (0.0, "P8"),
        (0.5, "M9"),
        (1.0, "m10"),
        (2.0, "P12"),
        (3.0, "M10"),
        (4.0, "P12"),
        (4.5, "m13"),
        (5.0, "m17"),
        (5.5, "P12"),
        (6.0, "M13"),
        (6.5, "P12"),
        (7.0, "P8"),
        (8.0, "m10"),
        (9.0, "m10"),
        (10.0, "M10"),
        (11.0, "M10"),
        (12.0, "m10"),
        (13.0, "m10"),
        (14.0, "P12"),
        (15.0, "P8"),
        (16.0, "P8"),
        (16.5, "M9"),
        (17.0, "m10"),
        (18.0, "P12"),
        (19.0, "M10"),
        (20.0, "P12"),
        (20.5, "m13"),
        (21.0, "m17"),
        (21.5, "P12"),
        (22.0, "M13"),
        (22.5, "P12"),
        (23.0, "P8"),
        (24.0, "m10"),
        (25.0, "m10"),
        (26.0, "M10"),
        (27.0, "M10"),
        (28.0, "m10"),
        (29.0, "m10"),
        (30.0, "P12"),
        (31.0, "P8"),
        (32.0, "P8"),
        (32.5, "M9"),
        (33.0, "m13"),
        (33.5, "m14"),
        (34.0, "m13"),
        (34.5, "m14"),
        (35.0, "M10"),
        (36.0, "M10"),
        (36.5, "P11"),
        (37.0, "P12"),
        (38.0, "M10"),
        (39.0, "P15"),
        (40.0, "P12"),
        (40.5, "P11"),
        (41.0, "M13"),
        (42.0, "P12"),
        (43.0, "M17"),
        (43.5, "M16"),
        (44.0, "P12"),
        (44.5, "m13"),
        (45.0, "P15"),
        (45.5, "m14"),
        (46.0, "P12"),
        (47.0, "P15"),
        (48.0, "P12"),
        (49.0, "m10"),
        (50.0, "M13"),
        (50.5, "P12"),
        (51.0, "M10"),
        (52.0, "m10"),
        (52.5, "P11"),
        (53.0, "m13"),
        (53.5, "d12"),
        (54.0, "m10"),
        (55.0, "P12"),
        (56.0, "P8"),
        (56.5, "M10"),
        (57.0, "P12"),
        (57.5, "m13"),
        (58.0, "P15"),
        (59.0, "M17"),
        (60.0, "P15"),
        (60.5, "m13"),
        (61.0, "M13"),
        (61.5, "m14"),
        (62.0, "P12"),
        (63.0, "P8"),
        (64.0, "P15"),
        (65.0, "P12"),
        (65.5, "M13"),
        (66.0, "m14"),
        (66.5, "P15"),
        (67.0, "M17"),
        (68.0, "P15"),
        (68.5, "m14"),
        (69.0, "P12"),
        (69.5, "m14"),
        (70.0, "P12"),
        (71.0, "P15")]

    bwv77_S_B_small_compound_noqual = [
        (0.0, "8"),
        (0.5, "9"),
        (1.0, "10"),
        (2.0, "12"),
        (3.0, "10"),
        (4.0, "12"),
        (4.5, "13"),
        (5.0, "17"),
        (5.5, "12"),
        (6.0, "13"),
        (6.5, "12"),
        (7.0, "8")]

    bwv77_S_B_small_simple_qual = [
        (0.0, "P8"),
        (0.5, "M2"),
        (1.0, "m3"),
        (2.0, "P5"),
        (3.0, "M3"),
        (4.0, "P5"),
        (4.5, "m6"),
        (5.0, "m3"),
        (5.5, "P5"),
        (6.0, "M6"),
        (6.5, "P5"),
        (7.0, "P8")]

    bwv77_S_B_small_simple_noqual = [
        (0.0, "8"),
        (0.5, "2"),
        (1.0, "3"),
        (2.0, "5"),
        (3.0, "3"),
        (4.0, "5"),
        (4.5, "6"),
        (5.0, "3"),
        (5.5, "5"),
        (6.0, "6"),
        (6.5, "5"),
        (7.0, "8")]

    bwv77_soprano_small = [
        (0.0, "E4"),
        (0.5, "F#4"),
        (1.0, "G4"),
        (2.0, "A4"),
        (3.0, "B4"),
        (4.0, "A4"),
        (5.0, "D5"),
        (6.0, "C#5"),
        (7.0, "B4")]

    bwv77_bass_small = [
        (0.0, "E3"),
        (1.0, "E3"),
        (2.0, "D3"),
        (3.0, "G3"),
        (4.0, "D3"),
        (4.5, "C#3"),
        (5.0, "B2"),
        (5.5, "G3"),
        (6.0, "E3"),
        (6.5, "F#3"),
        (7.0, "B3")]

    def setUp(self):
        self.bwv77_soprano = TestIntervalIndexerLong.do_wrapping(TestNoteRestIndexer.bwv77_soprano)
        self.bwv77_bass = TestIntervalIndexerLong.do_wrapping(TestNoteRestIndexer.bwv77_bass)
        self.bwv77_s_small = TestIntervalIndexerLong.do_wrapping(self.bwv77_soprano_small)
        self.bwv77_b_small = TestIntervalIndexerLong.do_wrapping(self.bwv77_bass_small)

    @staticmethod
    def do_wrapping(of_this):
        "Convert a list of tuples (offset, obj) into the expected Series version."
        post_data = []
        post_offsets = []
        for each_obj in of_this:
            post_data.append(unicode(each_obj[1]))
            post_offsets.append(each_obj[0])
        return pandas.Series(post_data, index=post_offsets)

    def test_interval_indexer_1(self):
        # BWV7.7: full soprano and bass parts
        test_parts = [self.bwv77_soprano, self.bwv77_bass]
        expected = TestIntervalIndexerLong.bwv77_S_B_basis
        setts = {u'simple or compound': u'compound', u'quality': True}
        int_indexer = IntervalIndexer(test_parts, setts)
        actual = int_indexer.run()[u'0,1']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_interval_indexer_2(self):
        # BWV7.7: small soprano and bass parts; "simple" in settings
        test_parts = [self.bwv77_s_small, self.bwv77_b_small]
        expected = TestIntervalIndexerLong.bwv77_S_B_small_simple_qual
        setts = {u'simple or compound': u'simple', u'quality': True}
        int_indexer = IntervalIndexer(test_parts, setts)
        actual = int_indexer.run()[u'0,1']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_interval_indexer_3(self):
        # BWV7.7: small soprano and bass parts; "simple" and "quality" not in settings, and the
        # settings are in fact not specified
        test_parts = [self.bwv77_s_small, self.bwv77_b_small]
        expected = TestIntervalIndexerLong.bwv77_S_B_small_compound_noqual
        #setts = {}
        int_indexer = IntervalIndexer(test_parts)
        actual = int_indexer.run()[u'0,1']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_interval_indexer_4(self):
        # BWV7.7: small soprano and bass parts; "simple" in settings, "quality" not
        test_parts = [self.bwv77_s_small, self.bwv77_b_small]
        expected = TestIntervalIndexerLong.bwv77_S_B_small_simple_noqual
        setts = {u'simple or compound': u'simple'}
        int_indexer = IntervalIndexer(test_parts, setts)
        actual = int_indexer.run()[u'0,1']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])


class TestIntervalIndexerIndexer(unittest.TestCase):
    def test_int_ind_indexer_1(self):
        # ascending simple: quality, simple
        notes = [u'E4', u'C4']
        expected = u'M3'
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_2(self):
        # ascending simple: quality, compound
        notes = [u'E4', u'C4']
        expected = u'M3'
        actual = real_indexer(notes, quality=True, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_3(self):
        # ascending simple: noQuality, simple
        notes = [u'E4', u'C4']
        expected = u'3'
        actual = real_indexer(notes, quality=False, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_4(self):
        # ascending simple: noQuality, compound
        notes = [u'E4', u'C4']
        expected = u'3'
        actual = real_indexer(notes, quality=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_5(self):
        # ascending compound: quality, simple
        notes = [u'E5', u'C4']
        expected = u'M3'
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_6(self):
        # ascending compound: quality, compound
        notes = [u'E5', u'C4']
        expected = u'M10'
        actual = real_indexer(notes, quality=True, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_7(self):
        # ascending compound: noQuality, simple
        notes = [u'E5', u'C4']
        expected = u'3'
        actual = real_indexer(notes, quality=False, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_8(self):
        # ascending compound: noQuality, compound
        notes = [u'E5', u'C4']
        expected = u'10'
        actual = real_indexer(notes, quality=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_9(self):
        # descending simple: quality, simple
        notes = [u'C4', u'E4']
        expected = u'-M3'
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_10(self):
        # descending simple: quality, compound
        notes = [u'C4', u'E4']
        expected = u'-M3'
        actual = real_indexer(notes, quality=True, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_11(self):
        # descending simple: noQuality, simple
        notes = [u'C4', u'E4']
        expected = u'-3'
        actual = real_indexer(notes, quality=False, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_12(self):
        # descending simple: noQuality, compound
        notes = [u'C4', u'E4']
        expected = u'-3'
        actual = real_indexer(notes, quality=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_13(self):
        # descending compound: quality, simple
        notes = [u'C4', u'E5']
        expected = u'-M3'
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_14(self):
        # descending compound: quality, compound
        notes = [u'C4', u'E5']
        expected = u'-M10'
        actual = real_indexer(notes, quality=True, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_15(self):
        # descending compound: noQuality, simple
        notes = [u'C4', u'E5']
        expected = u'-3'
        actual = real_indexer(notes, quality=False, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_16(self):
        # descending compound: noQuality, compound
        notes = [u'C4', u'E5']
        expected = u'-10'
        actual = real_indexer(notes, quality=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_17(self):
        # rest in upper part
        notes = [u'C4', u'Rest']
        expected = u'Rest'
        actual = real_indexer(notes, quality=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_18(self):
        # rest in lower part
        notes = [u'Rest', u'C4']
        expected = u'Rest'
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_19(self):
        # triple augmented ascending
        notes = [u'G###4', u'C4']
        expected = u'AAA5'
        actual = real_indexer(notes, quality=True, simple=False)
        self.assertEqual(expected, actual)
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_20(self):
        # triple diminished descending
        notes = [u'C###4', u'G4']
        expected = u'-ddd5'
        actual = real_indexer(notes, quality=True, simple=False)
        self.assertEqual(expected, actual)
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_21(self):
        # too few inputs
        notes = [u'C4']
        expected = None
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_22(self):
        # too many inputs
        notes = [u'C4', u'D4', u'E4']
        expected = None
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_regression_1(self):
        "indexer_qual_simple(): P15 --> P8"
        notes = [u'C6', u'C4']
        expected = u'P8'
        actual = real_indexer(notes, quality=True, simple=True)
        self.assertEqual(expected, actual)

    def test_regression_2(self):
        "indexer_nq_simple(): 15 --> 8"
        notes = [u'C6', u'C4']
        expected = u'8'
        actual = real_indexer(notes, quality=False, simple=True)
        self.assertEqual(expected, actual)


class TestHorizIntervalIndexerLong(unittest.TestCase):
    bwv77_S_B_short = [(0.5, "M2"),
                       (1.0, "m2"),
                       (2.0, "M2"),
                       (3.0, "M2"),
                       (4.0, "-M2"),
                       (5.0, "P4"),
                       (6.0, "-m2"),
                       (7.0, "-M2"),
                       (8.0, "-M2"),
                       (9.0, "P4"),
                       (10.0, "-m2"),
                       (11.0, "-M2"),
                       (12.0, "-M2"),
                       (13.0, "-M2"),
                       (14.0, "-m2"),
                       (15.0, "-M2"),
                       (16.0, "P1"),
                       (16.5, "M2"),
                       (17.0, "m2"),
                       (18.0, "M2"),
                       (19.0, "M2"),
                       (20.0, "-M2"),
                       (21.0, "P4"),
                       (22.0, "-m2"),
                       (23.0, "-M2"),
                       (24.0, "-M2")]

    bwv77_S_B_short_noqual = [(0.5, "2"),
                             (1.0, "2"),
                             (2.0, "2"),
                             (3.0, "2"),
                             (4.0, "-2"),
                             (5.0, "4"),
                             (6.0, "-2"),
                             (7.0, "-2"),
                             (8.0, "-2"),
                             (9.0, "4"),
                             (10.0, "-2"),
                             (11.0, "-2"),
                             (12.0, "-2"),
                             (13.0, "-2"),
                             (14.0, "-2"),
                             (15.0, "-2"),
                             (16.0, "1"),
                             (16.5, "2"),
                             (17.0, "2"),
                             (18.0, "2"),
                             (19.0, "2"),
                             (20.0, "-2"),
                             (21.0, "4"),
                             (22.0, "-2"),
                             (23.0, "-2"),
                             (24.0, "-2")]

    bwv77_S_B_basis = [(0.5, "M2"),
                       (1.0, "m2"),
                       (2.0, "M2"),
                       (3.0, "M2"),
                       (4.0, "-M2"),
                       (5.0, "P4"),
                       (6.0, "-m2"),
                       (7.0, "-M2"),
                       (8.0, "-M2"),
                       (9.0, "P4"),
                       (10.0, "-m2"),
                       (11.0, "-M2"),
                       (12.0, "-M2"),
                       (13.0, "-M2"),
                       (14.0, "-m2"),
                       (15.0, "-M2"),
                       (16.0, "P1"),
                       (16.5, "M2"),
                       (17.0, "m2"),
                       (18.0, "M2"),
                       (19.0, "M2"),
                       (20.0, "-M2"),
                       (21.0, "P4"),
                       (22.0, "-m2"),
                       (23.0, "-M2"),
                       (24.0, "-M2"),
                       (25.0, "P4"),
                       (26.0, "-m2"),
                       (27.0, "-M2"),
                       (28.0, "-M2"),
                       (29.0, "-M2"),
                       (30.0, "-m2"),
                       (31.0, "-M2"),
                       (32.0, "P1"),
                       (33.0, "P4"),
                       (34.0, "P1"),
                       (34.5, "-M2"),
                       (35.0, "-m2"),
                       (36.0, "P4"),
                       (37.0, "P1"),
                       (38.0, "-m2"),
                       (39.0, "m2"),
                       (40.0, "P1"),
                       (41.0, "P4"),
                       (42.0, "P1"),
                       (43.0, "M2"),
                       (43.5, "-M2"),
                       (44.0, "-M2"),
                       (45.0, "M2"),
                       (45.5, "-M2"),
                       (46.0, "-m2"),
                       (47.0, "-M2"),
                       (48.0, "M2"),
                       (49.0, "m2"),
                       (50.0, "-m2"),
                       (51.0, "-M2"),
                       (52.0, "-M2"),
                       (53.0, "M2"),
                       (53.5, "-M2"),
                       (54.0, "-M2"),
                       (55.0, "-m2"),
                       (56.0, "-M2"),
                       (56.5, "M2"),
                       (57.0, "m2"),
                       (58.0, "M2"),
                       (59.0, "M2"),
                       (60.0, "-M2"),
                       (60.5, "-M2"),
                       (61.0, "M2"),
                       (61.5, "-M2"),
                       (62.0, "-m2"),
                       (63.0, "-M2"),
                       (64.0, "P8"),
                       (65.0, "P1"),
                       (66.0, "P1"),
                       (67.0, "M2"),
                       (68.0, "-M2"),
                       (69.0, "-M2"),
                       (70.0, "-m2"),
                       (71.0, "-M2")]

    def setUp(self):
        self.bwv77_soprano = TestIntervalIndexerLong.do_wrapping(TestNoteRestIndexer.bwv77_soprano)
        self.bwv77_bass = TestIntervalIndexerLong.do_wrapping(TestNoteRestIndexer.bwv77_bass)

    @staticmethod
    def do_wrapping(of_this):
        "Convert a list of tuples (offset, obj) into the expected Series version."
        post_data = []
        post_offsets = []
        for each_obj in of_this:
            post_data.append(unicode(each_obj[1]))
            post_offsets.append(each_obj[0])
        return pandas.Series(post_data, index=post_offsets)

    def test_interval_indexer_1a(self):
        # BWV7.7: first 26 things in soprano part
        test_parts = [self.bwv77_soprano]
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_short
        setts = {u'simple or compound': u'compound', u'quality': True}
        int_indexer = HorizontalIntervalIndexer(test_parts, setts)
        res = int_indexer.run()
        actual = res[0].iloc[:26]
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_interval_indexer_1b(self):
        # BWV7.7: first 26 things in soprano part (no settings specified)
        test_parts = [self.bwv77_soprano]
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_short_noqual
        #setts = {u'simple or compound': u'compound', u'quality': True}
        int_indexer = HorizontalIntervalIndexer(test_parts)
        res = int_indexer.run()
        actual = res[0].iloc[:26]
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_interval_indexer_1c(self):
        # BWV7.7: first 26 things in soprano part (simple; quality)
        test_parts = [self.bwv77_soprano]
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_short
        setts = {u'simple or compound': u'simple', u'quality': True}
        int_indexer = HorizontalIntervalIndexer(test_parts, setts)
        res = int_indexer.run()
        actual = res[0].iloc[:26]
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_interval_indexer_1d(self):
        # BWV7.7: first 26 things in soprano part (simple; no quality)
        test_parts = [self.bwv77_soprano]
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_short_noqual
        setts = {u'simple or compound': u'simple', u'quality': False}
        int_indexer = HorizontalIntervalIndexer(test_parts, setts)
        res = int_indexer.run()
        actual = res[0].iloc[:26]
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_interval_indexer_2(self):
        # BWV7.7: whole soprano part
        test_parts = [self.bwv77_soprano]
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_basis
        setts = {u'simple or compound': u'compound', u'quality': True}
        int_indexer = HorizontalIntervalIndexer(test_parts, setts)
        res = int_indexer.run()
        actual = res[0]
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#-------------------------------------------------------------------------------------------------#
INTERVAL_INDEXER_SHORT_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerShort)
INTERVAL_INDEXER_LONG_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerLong)
INT_IND_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerIndexer)
HORIZ_INT_IND_LONG_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestHorizIntervalIndexerLong)
