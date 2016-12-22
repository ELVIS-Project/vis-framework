#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_note_beat_strength_indexer.py
# Purpose:                Tests for the BeatStrengthIndexer
#
# Copyright (C) 2015, Alexander Morgan, Christopher Antilla
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
# along with this programself.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904

import os
import unittest
import pandas
from music21 import stream, clef, bar, note
from music21 import meter as m21_meter
from vis.analyzers.indexers import meter
from vis.models.indexed_piece import Importer, IndexedPiece
from numpy import nan

# find the pathname of the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]


bwv77_soprano = [(0.0, 0.25), (0.5, 0.125), (1.0, 1.0), (2.0, 0.25), (3.0, 0.5), (4.0, 0.25),
                 (5.0, 1.0), (6.0, 0.25), (7.0, 0.5), (8.0, 0.25), (9.0, 1.0), (10.0, 0.25),
                 (11.0, 0.5), (12.0, 0.25), (13.0, 1.0), (14.0, 0.25), (15.0, 0.5), (16.0, 0.25),
                 (16.5, 0.125), (17.0, 1.0), (18.0, 0.25), (19.0, 0.5), (20.0, 0.25), (21.0, 1.0),
                 (22.0, 0.25), (23.0, 0.5), (24.0, 0.25), (25.0, 1.0), (26.0, 0.25), (27.0, 0.5),
                 (28.0, 0.25), (29.0, 1.0), (30.0, 0.25), (31.0, 0.5), (32.0, 0.25), (33.0, 1.0),
                 (34.0, 0.25), (34.5, 0.125), (35.0, 0.5), (36.0, 0.25), (37.0, 1.0), (38.0, 0.25),
                 (39.0, 0.5), (40.0, 0.25), (41.0, 1.0), (42.0, 0.25), (43.0, 0.5), (43.5, 0.125),
                 (44.0, 0.25), (45.0, 1.0), (45.5, 0.125), (46.0, 0.25), (47.0, 0.5), (48.0, 0.25),
                 (49.0, 1.0), (50.0, 0.25), (51.0, 0.5), (52.0, 0.25), (53.0, 1.0), (53.5, 0.125),
                 (54.0, 0.25), (55.0, 0.5), (56.0, 0.25), (56.5, 0.125), (57.0, 1.0), (58.0, 0.25),
                 (59.0, 0.5), (60.0, 0.25), (60.5, 0.125), (61.0, 1.0), (61.5, 0.125), (62.0, 0.25),
                 (63.0, 0.5), (64.0, 0.25), (65.0, 1.0), (66.0, 0.25), (67.0, 0.5), (68.0, 0.25),
                 (69.0, 1.0), (70.0, 0.25), (71.0, 0.5)]

bwv603_alto = [(0.0, 0.5), (1.0, 1.0), (3.0, 0.5), (4.0, 1.0), (6.0, 0.5), (7.0, 1.0), (9.0, 0.5),
               (10.0, 1.0), (13.0, 1.0), (15.0, 0.5), (16.0, 1.0), (18.0, 0.5), (19.0, 1.0),
               (21.0, 0.5), (22.0, 1.0), (24.0, 0.5), (25.0, 1.0), (27.0, 0.5), (29.0, 0.5),
               (30.0, 0.5), (31.0, 1.0), (33.0, 0.5), (34.0, 1.0), (35.0, 0.5), (36.0, 0.5),
               (37.0, 1.0), (39.0, 0.5), (40.0, 1.0), (41.0, 0.5), (42.0, 0.5), (44.0, 0.5),
               (45.0, 0.5), (46.0, 1.0)]

bwv603_soprano = [(0.0, 0.5), (1.0, 1.0), (2.0, nan), (3.0, 0.5), (4.0, 1.0), (5.0, nan),
                  (6.0, 0.5), (7.0, 1.0), (8.0, 0.5), (9.0, 0.5), (10.0, 1.0), (13.0, 1.0),
                  (14.0, nan), (15.0, 0.5), (16.0, 1.0), (17.0, nan), (18.0, 0.5), (19.0, 1.0),
                  (21.0, 0.5), (22.0, 1.0), (23.0, nan), (24.0, 0.5), (25.0, 1.0), (26.0, nan),
                  (27.0, 0.5), (28.0, 1.0), (29.0, 0.5), (30.0, 0.5), (31.0, 1.0), (33.0, 0.5),
                  (34.0, 1.0), (35.0, nan), (36.0, 0.5), (37.0, 1.0), (38.0, nan), (39.0, 0.5),
                  (40.0, 1.0), (41.0, nan), (42.0, 0.5), (43.0, 1.0), (44.0, nan), (45.0, 0.5),
                  (46.0, 1.0)]


bwv603_bass = [(0.0, 0.5), (1.0, 1.0), (2.0, 0.5), (3.0, 0.5), (4.0, 1.0), (5.0, 0.5), (6.0, 0.5),
               (7.0, 1.0), (8.0, 0.5), (9.0, 0.5), (10.0, 1.0), (13.0, 1.0), (14.0, 0.5),
               (15.0, 0.5), (16.0, 1.0), (17.0, 0.5), (18.0, 0.5), (19.0, 1.0), (21.0, 0.5),
               (22.0, 1.0), (23.0, 0.5), (24.0, 0.5), (25.0, 1.0), (26.0, 0.5), (27.0, 0.5),
               (28.0, 1.0), (29.0, 0.5), (30.0, 0.5), (31.0, 1.0), (33.0, 0.5), (34.0, nan),
               (35.0, 0.5), (36.0, 0.5), (37.0, 1.0), (38.0, 0.5), (39.0, 0.5), (40.0, 1.0),
               (41.0, 0.5), (42.0, 0.5), (43.0, 1.0), (44.0, 0.5), (45.0, 0.5), (46.0, 1.0)]

class TestNoteBeatStrengthIndexer(unittest.TestCase):


    @staticmethod
    def make_series(lotuples):
        """
        From a list of two-tuples, make a Series. The list should be like this:

        [(desired_index, value), (desired_index, value), (desired_index, value)]
        """
        new_index = [x[0] for x in lotuples]
        vals = [x[1] for x in lotuples]
        return pandas.Series(vals, index=new_index)

    def test_note_beat_strength_indexer_1(self):
        # When the parts are empty
        expected = pandas.DataFrame({'0': pandas.Series(), '1': pandas.Series()})
        test_parts = [stream.Part(), stream.Part()]
        ip = IndexedPiece()
        ip.metadata('parts', expected.columns)
        ip._analyses['part_streams'] = test_parts # supply part_streams.
        actual = ip._get_beat_strength()['meter.NoteBeatStrengthIndexer']
        self.assertTrue(actual.equals(expected))

    def test_note_beat_strength_indexer_2(self):
        # When the part has no Note or Rest objects in it
        expected = pandas.DataFrame({'0': pandas.Series()})
        test_part = stream.Part()
        # add stuff to the test_part
        for i in range(1000):
            add_me = clef.BassClef()
            add_me.offset = i
            test_part.append(add_me)
            add_me = bar.Barline()
            add_me.offset = i
            test_part.append(add_me) # finished adding stuff to the test_part
        ip = IndexedPiece()
        ip.metadata('parts', expected.columns)
        ip._analyses['part_streams'] = [test_part] # supply part_streams.
        actual = ip._get_beat_strength()['meter.NoteBeatStrengthIndexer']
        self.assertTrue(actual.equals(expected))

    def test_note_beat_strength_indexer_3(self):
        # When there are a few notes
        expected = pandas.DataFrame({'0': pandas.Series([1.0, 0.5, 0.5, 1.0, 0.5, 0.5])})
        test_part = stream.Part()
        # add stuff to the test_part
        measure = stream.Measure()
        # In music21 beginning time signatures are preferably inserted in the first measure and a
        # timeSignature is needed to be able to calculate beatStrength
        measure.insert(0, m21_meter.TimeSignature('3/4'))
        for i in range(6):
            add_me = note.Note(u'C4', quarterLength=1.0)
            add_me.offset = i
            measure.append(add_me)
        test_part.insert(0, measure) # finished adding stuff to the test_part
        ip = IndexedPiece()
        ip.metadata('parts', expected.columns)
        ip._analyses['part_streams'] = [test_part] # supply part_streams.
        actual = ip._get_beat_strength()['meter.NoteBeatStrengthIndexer']
        self.assertTrue(actual.equals(expected))

    def test_note_beat_strength_indexer_4(self):
        # Soprano part of bwv77.mxl which is a part with no ties
        expected = TestNoteBeatStrengthIndexer.make_series(bwv77_soprano)
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus/bwv77.mxl'))
        actual = ip._get_beat_strength().iloc[:, 0].dropna()
        self.assertTrue(actual.equals(expected))

    def test_note_beat_strength_indexer_5(self):
        # Alto part of bwv603.mxl which is a part with ties
        expected = TestNoteBeatStrengthIndexer.make_series(bwv603_alto)
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus/bwv603.xml'))
        actual = ip._get_beat_strength().iloc[:, 1].dropna()
        self.assertTrue(actual.equals(expected))

    def test_note_beat_strength_indexer_6(self):
        # Soprano and bass parts of bwv603.xml
        # We won't verify all the parts, but we'll submit them all for analysis.
        expected = pandas.concat([TestNoteBeatStrengthIndexer.make_series(bwv603_soprano),
                                 TestNoteBeatStrengthIndexer.make_series(bwv603_bass)], axis=1)
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus/bwv603.xml'))
        actual = ip._get_beat_strength()['meter.NoteBeatStrengthIndexer'].iloc[:, [0, 3]].dropna(how='all')
        expected.columns = actual.columns
        self.assertTrue(actual.equals(expected))

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
NOTE_BEAT_STRENGTH_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestNoteBeatStrengthIndexer)
