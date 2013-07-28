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
from music21 import interval, note
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers.interval import IntervalIndexer
from vis.analyzers.indexers.noterest import NoteRestIndexer
from vis.test_corpus import int_indexer_short


class TestIntervalIndexer(unittest.TestCase):
    def setUp(self):
        self.bwv77_soprano = [
            (0.0, "E4"),
            (0.5, "F#4"),
            (1.0, "G4"),
            (2.0, "A4"),
            (3.0, "B4"),
            (4.0, "A4"),
            (5.0, "D5"),
            (6.0, "C#5"),
            (7.0, "B4"),
            (8.0, "A4"),
            (9.0, "D5"),
            (10.0, "C#5"),
            (11.0, "B4"),
            (12.0, "A4"),
            (13.0, "G4"),
            (14.0, "F#4"),
            (15.0, "E4"),
            (16.0, "E4"),
            (16.5, "F#4"),
            (17.0, "G4"),
            (18.0, "A4"),
            (19.0, "B4"),
            (20.0, "A4"),
            (21.0, "D5"),
            (22.0, "C#5"),
            (23.0, "B4"),
            (24.0, "A4"),
            (25.0, "D5"),
            (26.0, "C#5"),
            (27.0, "B4"),
            (28.0, "A4"),
            (29.0, "G4"),
            (30.0, "F#4"),
            (31.0, "E4"),
            (32.0, "E4"),
            (33.0, "A4"),
            (34.0, "A4"),
            (34.5, "G4"),
            (35.0, "F#4"),
            (36.0, "B4"),
            (37.0, "B4"),
            (38.0, "A#4"),
            (39.0, "B4"),
            (40.0, "B4"),
            (41.0, "E5"),
            (42.0, "E5"),
            (43.0, "F#5"),
            (43.5, "E5"),
            (44.0, "D5"),
            (45.0, "E5"),
            (45.5, "D5"),
            (46.0, "C#5"),
            (47.0, "B4"),
            (48.0, "C#5"),
            (49.0, "D5"),
            (50.0, "C#5"),
            (51.0, "B4"),
            (52.0, "A4"),
            (53.0, "B4"),
            (53.5, "A4"),
            (54.0, "G4"),
            (55.0, "F#4"),
            (56.0, "E4"),
            (56.5, "F#4"),
            (57.0, "G4"),
            (58.0, "A4"),
            (59.0, "B4"),
            (60.0, "A4"),
            (60.5, "G4"),
            (61.0, "A4"),
            (61.5, "G4"),
            (62.0, "F#4"),
            (63.0, "E4"),
            (64.0, "E5"),
            (65.0, "E5"),
            (66.0, "E5"),
            (67.0, "F#5"),
            (68.0, "E5"),
            (69.0, "D5"),
            (70.0, "C#5"),
            (71.0, "B4")
            ]
        self.bwv77_bass = [
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
            (7.0, "B3"),
            (8.0, "F#3"),
            (9.0, "B3"),
            (10.0, "A3"),
            (11.0, "G3"),
            (12.0, "F#3"),
            (13.0, "E3"),
            (14.0, "B2"),
            (15.0, "E3"),
            (16.0, "E3"),
            (17.0, "E3"),
            (18.0, "D3"),
            (19.0, "G3"),
            (20.0, "D3"),
            (20.5, "C#3"),
            (21.0, "B2"),
            (21.5, "G3"),
            (22.0, "E3"),
            (22.5, "F#3"),
            (23.0, "B3"),
            (24.0, "F#3"),
            (25.0, "B3"),
            (26.0, "A3"),
            (27.0, "G3"),
            (28.0, "F#3"),
            (29.0, "E3"),
            (30.0, "B2"),
            (31.0, "E3"),
            (32.0, "E3"),
            (32.5, "D3"),
            (33.0, "C#3"),
            (33.5, "B2"),
            (34.0, "C#3"),
            (34.5, "A2"),
            (35.0, "D3"),
            (36.0, "G3"),
            (36.5, "F#3"),
            (37.0, "E3"),
            (38.0, "F#3"),
            (39.0, "B2"),
            (40.0, "E3"),
            (40.5, "F#3"),
            (41.0, "G3"),
            (42.0, "A3"),
            (43.0, "D3"),
            (44.0, "G3"),
            (44.5, "F#3"),
            (45.0, "E3"),
            (46.0, "F#3"),
            (47.0, "B2"),
            (48.0, "F#3"),
            (49.0, "B3"),
            (50.0, "E3"),
            (50.5, "F#3"),
            (51.0, "G3"),
            (52.0, "F#3"),
            (52.5, "E3"),
            (53.0, "D#3"),
            (54.0, "E3"),
            (55.0, "B2"),
            (56.0, "E3"),
            (56.5, "D3"),
            (57.0, "C3"),
            (57.5, "B2"),
            (58.0, "A2"),
            (59.0, "G2"),
            (60.0, "A2"),
            (60.5, "B2"),
            (61.0, "C3"),
            (61.5, "A2"),
            (62.0, "B2"),
            (63.0, "E3"),
            (64.0, "E3"),
            (65.0, "A3"),
            (65.5, "G3"),
            (66.0, "F#3"),
            (66.5, "E3"),
            (67.0, "D3"),
            (68.0, "E3"),
            (68.5, "F#3"),
            (69.0, "G3"),
            (69.5, "E3"),
            (70.0, "F#3"),
            (71.0, "B2")
            ]
        self.bwv77_S_B = [
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
            (71.0, "P15")
            ]

    #def test_interval_indexer_X(self):
        ## This is a pattern
        #expected = [[]]
        #test_part = None
        #test_ip = IndexedPiece('pathname')
        #int_indexer = IntervalIndexer(test_ip._data[u'NoteRestIndexer'][u'{}'])
        #actual = int_indexer.run()
        #??????

    # NB: these "short" tests were brought over from the vis9 tests for _event_finder()
    def test_int_indexer_short_1(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_1)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_2(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_2)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_3(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_3)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_4(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_4)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_5(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('F4')).name)]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_5)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_6(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_6)
        int_indexer = IntervalIndexer(nr_indexer.run())
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
        nr_indexer = NoteRestIndexer(int_indexer_short.test_7)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_8(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_8)
        int_indexer = IntervalIndexer(nr_indexer.run())
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
        nr_indexer = NoteRestIndexer(int_indexer_short.test_9)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_10(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_10)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_11(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_11)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_12(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_12)
        int_indexer = IntervalIndexer(nr_indexer.run())
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
        nr_indexer = NoteRestIndexer(int_indexer_short.test_13)
        int_indexer = IntervalIndexer(nr_indexer.run())
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
        nr_indexer = NoteRestIndexer(int_indexer_short.test_14)
        int_indexer = IntervalIndexer(nr_indexer.run())
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
        nr_indexer = NoteRestIndexer(int_indexer_short.test_15)
        int_indexer = IntervalIndexer(nr_indexer.run())
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
        nr_indexer = NoteRestIndexer(int_indexer_short.test_16)
        int_indexer = IntervalIndexer(nr_indexer.run())
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
        nr_indexer = NoteRestIndexer(int_indexer_short.test_17)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_18(self):
        # What happens when we look only for Rest objects, no Note ones?
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, u'Rest')]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_18)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_int_indexer_short_19(self):
        # What happens when we look only for Rest objects, no Note ones, and there are Rest objects
        # at the same offset as other Note objects?
        # NB: We need the extra , in "expected" or else python will simplify ('Rest') to 'Rest'
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, u'Rest')]
        nr_indexer = NoteRestIndexer(int_indexer_short.test_19)
        int_indexer = IntervalIndexer(nr_indexer.run())
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, event in enumerate(expected):
            self.assertEqual(event[0], actual[i].offset)
            self.assertEqual(event[1], actual[i].obj)

    def test_interval_indexer_1(self):
        # This is a pattern
        test_part = None
        test_ip = IndexedPiece('test_corpus/bwv77.mxl')
        test_ip.add_index(u'NoteRestIndexer')
        # verify NoteRestIndexer results
        expected = [self.bwv77_soprano, self.bwv77_bass]
        actual = [test_ip._data[u'NoteRestIndexer'][u'{}'][0],
                  test_ip._data[u'NoteRestIndexer'][u'{}'][3]]
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))
        self.assertEqual(len(expected[1]), len(actual[1]))
        for i in xrange(len(expected[0])):
            self.assertEqual(expected[0][i][0], actual[0][i].offset)
            self.assertEqual(expected[0][i][1], actual[0][i].obj)
        for i in xrange(len(expected[1])):
            self.assertEqual(expected[1][i][0], actual[1][i].offset)
            self.assertEqual(expected[1][i][1], actual[1][i].obj)
        # now the IntervalIndexer
        int_indexer = IntervalIndexer(test_ip._data[u'NoteRestIndexer'][u'{}'])
        expected = self.bwv77_S_B
        actual = int_indexer.run()[u'[0, 3]']
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertEqual(expected[i][0], actual[i].offset)
            self.assertEqual(expected[i][1], actual[i].obj)


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
interval_indexer_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexer)
