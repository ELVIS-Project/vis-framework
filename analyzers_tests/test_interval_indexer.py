#! /usr/bin/python
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

import unittest
import pandas
from music21 import interval, note, duration, base
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers.interval import IntervalIndexer
from vis.analyzers.indexers.noterest import NoteRestIndexer
from vis.test_corpus import int_indexer_short
from vis.analyzers_tests.test_note_rest_indexer import TestNoteRestIndexer


class TestIntervalIndexerShort(unittest.TestCase):
    "These 'short' tests were brought over from the vis9 tests for _event_finder()."
    @staticmethod
    def elem_wrapper(wrap_this):
        """
        Transform tuple-formatted tests into appropriate ElementWrapper things.

        Input:
        ======
        --> [[tuples_for_part_1], [tuples_for_part_2], ...]
        --> [[(offset, obj, quarterLength), ...], ...]

        Output:
        =======
        lists of Series, ready for IntervalIndexer.__init__()
        """
        post = []
        for part in wrap_this:
            past = []
            for obj in part:
                past.append(base.ElementWrapper(obj[1]))
                past[-1].offset = obj[0]
                past[-1].duration = duration.Duration(obj[2])
            post.append(pandas.Series(past))
        return post

    def setUp(self):
        # NB: each of these is one of the _event_finder() tests
        # NB: [[tuples_for_part_1], [tuples_for_part_2]]
        # NB: [[(offset, obj, quarterLength)]]
        pass

    def test_int_indexer_short_1(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 0.5)], [(0.0, u'G3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_2(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        not_processed = [[(0.0, u'G4', 0.25), (0.25, u'Rest', 0.25)],
                         [(0.0, u'G3', 0.25), (0.25, u'Rest', 0.25)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_3(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        not_processed = [[(0.5, u'G4', 0.5)], [(0.0, u'G3', 0.25), (0.25, u'Rest', 0.25)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_4(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        not_processed = [[(0.0, u'G4', 0.25), (0.25, u'Rest', 0.25)], [(0.0, u'G3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_5(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('F4')).name)]
        not_processed = [[(0.0, u'G4', 0.5), (0.5, u'F4', 0.5)],
                         [(0.0, u'G3', 0.5), (0.5, u'A3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_6(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3', 0.5), (0.5, u'A3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_7(self):
        expected = [(0.0, interval.Interval(note.Note('B3'), note.Note('A4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (1.0, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (1.5, interval.Interval(note.Note('B3'), note.Note('F4')).name)]
        not_processed = [[(0.0, u'A4', 0.5), (0.5, u'G4', 1.0), (1.5, u'F4', 0.5)],
                         [(0.0, u'B3', 0.5), (0.5, u'G3', 0.5),
                          (1.0, u'A3', 0.5), (1.5, u'B3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_8(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        not_processed =  [[(0.0, u'G4', 1.0)],
                  [(0.0, u'G3', 0.25), (0.25, u'Rest', 0.25), (0.5, u'A3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_9(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (1.0, interval.Interval(note.Note('B3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0), (1.0, u'G4', 0.5)],
                [(0.0, u'G3', 0.25), (0.25, u'Rest', 0.25), (0.5, u'A3', 0.5), (1.0, u'B3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_10(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3', 0.25), (0.25, u'A3', 0.75)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_11(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3', 0.5), (0.5, u'G3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_12(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)],
                   [(0.0, u'G3', 0.25), (0.25, u'Rest', 0.25), (0.5, u'G3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_13(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.125, u'Rest'),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (0.375, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)],
                   [(0.0, u'G3', 0.125), (0.125, u'Rest', 0.125),
                    (0.25, u'A3', 0,125), (0.375, u'Rest', 0.125), (0.5, u'G3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

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
        not_processed = [[(0.0, u'G4', 0.0625), (0.0625, u'G4', 0.0625),
                    (0.125, u'G4', 0.0625), (0.1875, u'G4', 0.0625),
                    (0.25, u'G4', 0.0625), (0.3125, u'G4', 0.0625),
                    (0.375, u'G4', 0.0625), (0.4375, u'G4', 0.0625),
                    (0.5, u'G4', 0.5)],
                   [(0.0, u'G3', 0.125), (0.125, u'Rest', 0.125), (0.25, u'A3', 0.125),
                    (0.375, u'Rest', 0.0625), (0.4375, u'Rest', 0.0625), (0.5, u'G3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_15(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.75, u'Rest'),
                    (1.0, u'Rest'),
                    (1.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 0.5), (0.5, u'G4', 0.25), (0.75, u'Rest', 0.25),
                    (1.0, u'G4', 0.5), (1.5, u'G4', 0.5)],
                   [(0.0, u'G3', 0.5), (0.5, u'G3', 0.25), (0.75, u'Rest', 0.25),
                    (1.0, u'Rest', 0.5), (1.5, u'G3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_16(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, u'Rest'),
                    (0.75, interval.Interval(note.Note('F3'), note.Note('A4')).name),
                    (1.25, interval.Interval(note.Note('F3'), note.Note('G4')).name),
                    (1.5, interval.Interval(note.Note('E3'), note.Note('B4')).name)]
        not_processed = [[(0.0, u'G4', 0.5), (0.5, u'A4', 0.75),
                          (1.25, u'G4', 0.25), (1.5, u'B4', 0.5)],
                         [(0.0, u'G3', 0.5), (0.5, u'Rest', 0.25),
                          (0.75, u'F3', 0.75), (1.5, u'E3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_17(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('A4')).name),
                    (0.75, interval.Interval(note.Note('F3'), note.Note('A4')).name),
                    (1.125, u'Rest'),
                    (1.25, u'Rest'),
                    (1.375, interval.Interval(note.Note('G3'), note.Note('F4')).name),
                    (2.0, interval.Interval(note.Note('G3'), note.Note('E4')).name)]
        not_processed = [[(0.0, u'G4', 0.5), (0.5, u'A4', 0.75), (1.25, u'F4', 0.75),
                          (2.0, u'E4', 0.5)],
                         [(0.0, u'G3', 0.5), (0.5, u'A3', 0.25), (0.75, u'F3', 0.375),
                          (1.125, u'Rest', 0.25), (1.375, u'G3', 0.625), (2.0, u'G3', 0.5)]]
        test_in = TestIntervalIndexerShort.elem_wrapper(not_processed)
        int_indexer = IntervalIndexer(test_in)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)


class TestIntervalIndexerLong(unittest.TestCase):
    bwv77_S_B = [
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

    def setUp(self):
        self.bwv77_soprano = pandas.Series(
            TestIntervalIndexerLong.do_wrapping(TestNoteRestIndexer.bwv77_soprano))
        self.bwv77_bass = pandas.Series(
            TestIntervalIndexerLong.do_wrapping(TestNoteRestIndexer.bwv77_bass))

    @staticmethod
    def do_wrapping(of_this):
        "Convert a list of tuples (offset, obj) into the expected ElementWrapper version."
        post = []
        for each_obj in of_this:
            post.append(base.ElementWrapper(each_obj[1]))
            post[-1].offset = each_obj[0]
            try:  # set duration for previous event
                post[-2].duration = duration.Duration(each_obj[0] - post[-2].offset)
            except IndexError:
                pass  # when this is the first element in "post"; faster than using an "if"
        if post != []:  # Ensure the last items have the correct duration
            post[-1].duration = duration.Duration(0.5)  # doesn't matter what, in this case
        return post

    def test_interval_indexer_1(self):
        # assemble the "parts"
        test_parts = [self.bwv77_soprano, self.bwv77_bass]
        expected = self.bwv77_S_B
        int_indexer = IntervalIndexer(test_parts)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertEqual(expected[i][0], actual[i].offset)
            self.assertEqual(expected[i][1], actual[i].obj)


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
interval_indexer_short_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerShort)
interval_indexer_long_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerLong)
