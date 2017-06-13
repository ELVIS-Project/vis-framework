#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_dur_indexer.py
# Purpose:                Tests for the DurationIndexer
#
# Copyright (C) 2015 Alexander Morgan, Christopher Antila
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

import os
import unittest
import six
import pandas
from music21 import converter, stream, clef, bar, note
from vis.analyzers.indexers import meter
from numpy import isnan
from vis.models.indexed_piece import Importer, IndexedPiece

# find the pathname of the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]

class TestDurationIndexer(unittest.TestCase):

    bwv77_soprano = [(0.0, 0.5), (0.5, 0.5), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0), (4.0, 1.0),
                     (5.0, 1.0), (6.0, 1.0), (7.0, 1.0), (8.0, 1.0), (9.0, 1.0), (10.0, 1.0),
                     (11.0, 1.0), (12.0, 1.0), (13.0, 1.0), (14.0, 1.0), (15.0, 1.0), (16.0, 0.5),
                     (16.5, 0.5), (17.0, 1.0), (18.0, 1.0), (19.0, 1.0), (20.0, 1.0), (21.0, 1.0),
                     (22.0, 1.0), (23.0, 1.0), (24.0, 1.0), (25.0, 1.0), (26.0, 1.0), (27.0, 1.0),
                     (28.0, 1.0), (29.0, 1.0), (30.0, 1.0), (31.0, 1.0), (32.0, 1.0), (33.0, 1.0),
                     (34.0, 0.5), (34.5, 0.5), (35.0, 1.0), (36.0, 1.0), (37.0, 1.0), (38.0, 1.0),
                     (39.0, 1.0), (40.0, 1.0), (41.0, 1.0), (42.0, 1.0), (43.0, 0.5), (43.5, 0.5),
                     (44.0, 1.0), (45.0, 0.5), (45.5, 0.5), (46.0, 1.0), (47.0, 1.0), (48.0, 1.0),
                     (49.0, 1.0), (50.0, 1.0), (51.0, 1.0), (52.0, 1.0), (53.0, 0.5), (53.5, 0.5),
                     (54.0, 1.0), (55.0, 1.0), (56.0, 0.5), (56.5, 0.5), (57.0, 1.0), (58.0, 1.0),
                     (59.0, 1.0), (60.0, 0.5), (60.5, 0.5), (61.0, 0.5), (61.5, 0.5), (62.0, 1.0),
                     (63.0, 1.0), (64.0, 1.0), (65.0, 1.0), (66.0, 1.0), (67.0, 1.0), (68.0, 1.0),
                     (69.0, 1.0), (70.0, 1.0), (71.0, 1.0)]

    bwv603_alto = [(0.0, 1.0), (1.0, 2.0), (3.0, 1.0), (4.0, 2.0), (6.0, 1.0), (7.0, 2.0),
                   (9.0, 1.0), (10.0, 3.0), (13.0, 2.0), (15.0, 1.0), (16.0, 2.0), (18.0, 1.0),
                   (19.0, 2.0), (21.0, 1.0), (22.0, 2.0), (24.0, 1.0), (25.0, 2.0), (27.0, 2.0),
                   (29.0, 1.0), (30.0, 1.0), (31.0, 2.0), (33.0, 1.0), (34.0, 1.0), (35.0, 1.0),
                   (36.0, 1.0), (37.0, 2.0), (39.0, 1.0), (40.0, 1.0), (41.0, 1.0), (42.0, 2.0),
                   (44.0, 1.0), (45.0, 1.0), (46.0, 2.0)]

    bwv603_soprano = [(0.0, 1.0), (1.0, 2.0), (2.0, float('nan')), (3.0, 1.0), (4.0, 2.0),
                     (5.0, float('nan')), (6.0, 1.0), (7.0, 1.0), (8.0, 1.0), (9.0, 1.0),
                     (10.0, 3.0), (13.0, 2.0), (14.0, float('nan')), (15.0, 1.0), (16.0, 2.0),
                     (17.0, float('nan')), (18.0, 1.0), (19.0, 2.0), (21.0, 1.0), (22.0, 2.0),
                     (23.0, float('nan')), (24.0, 1.0), (25.0, 2.0), (26.0, float('nan')),
                     (27.0, 1.0), (28.0, 1.0), (29.0, 1.0), (30.0, 1.0), (31.0, 2.0), (33.0, 1.0),
                     (34.0, 2.0), (35.0, float('nan')), (36.0, 1.0), (37.0, 2.0),
                     (38.0, float('nan')), (39.0, 1.0), (40.0, 2.0), (41.0, float('nan')),
                     (42.0, 1.0), (43.0, 2.0), (44.0, float('nan')), (45.0, 1.0), (46.0, 2.0)]

    bwv603_bass = [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0), (4.0, 1.0), (5.0, 1.0),
                   (6.0, 1.0), (7.0, 1.0), (8.0, 1.0), (9.0, 1.0), (10.0, 3.0), (13.0, 1.0),
                   (14.0, 1.0), (15.0, 1.0), (16.0, 1.0), (17.0, 1.0), (18.0, 1.0), (19.0, 2.0),
                   (21.0, 1.0), (22.0, 1.0), (23.0, 1.0), (24.0, 1.0), (25.0, 1.0), (26.0, 1.0),
                   (27.0, 1.0), (28.0, 1.0), (29.0, 1.0), (30.0, 1.0), (31.0, 2.0), (33.0, 2.0),
                   (34.0, float('nan')), (35.0, 1.0), (36.0, 1.0), (37.0, 1.0), (38.0, 1.0),
                   (39.0, 1.0), (40.0, 1.0), (41.0, 1.0), (42.0, 1.0), (43.0, 1.0), (44.0, 1.0),
                   (45.0, 1.0), (46.0, 2.0)]


    @staticmethod
    def make_series(lotuples):
        """
        From a list of two-tuples, make a Series. The list should be like this:

        [(desired_index, value), (desired_index, value), (desired_index, value)]
        """
        new_index = [x[0] for x in lotuples]
        vals = [x[1] for x in lotuples]
        return pandas.Series(vals, index=new_index)

    def test_duration_indexer_1(self):
        # When the parts are empty
        expected = pandas.DataFrame({'0': pandas.Series(), '1': pandas.Series()})
        expected.columns = pandas.MultiIndex.from_product([('meter.DurationIndexer',), ['0','1']])
        test_parts = [stream.Part(), stream.Part()]
        dur_indexer = meter.DurationIndexer(expected, test_parts)
        actual = dur_indexer.run()
        self.assertTrue(actual.equals(expected))

    def test_duration_indexer_2(self):
        # When the part has no Note or Rest objects in it
        expected = pandas.DataFrame({'0': pandas.Series()})
        expected.columns = pandas.MultiIndex.from_product([('meter.DurationIndexer',), ('0',)])
        test_part = stream.Part()
        # add stuff to the test_part
        for i in range(10):
            add_me = clef.BassClef()
            add_me.offset = i
            test_part.append(add_me)
            add_me = bar.Barline()
            add_me.offset = i
            test_part.append(add_me)
        test_part = [test_part] # finished adding stuff to the test_part
        dur_indexer = meter.DurationIndexer(expected, test_part)
        actual = dur_indexer.run()
        self.assertTrue(actual.equals(expected))

    def test_duration_indexer_3(self):
        # When there are a bunch of notes
        expected = TestDurationIndexer.make_series([(float(x), 1.0) for x in range(10)])
        expected.name = 'Part_1'
        test_part = stream.Part()
        # add stuff to the test_part
        for i in range(10):
            add_me = note.Note('C4', quarterLength=1.0)
            add_me.offset = i
            test_part.append(add_me)
        ip = IndexedPiece()
        test_part = [test_part]
        ip._analyses['part_streams'] = test_part
        ip.metadata('parts', [expected.name])
        actual = ip.get_data('duration').iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_duration_indexer_4(self):
        # Soprano part of bwv77.mxl which is a part with no ties
        expected = TestDurationIndexer.make_series(TestDurationIndexer.bwv77_soprano)
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus/bwv77.mxl'))
        ip._analyses['part_streams'] = ip._get_part_streams()
        actual = ip.get_data('duration').iloc[:, 0].dropna()
        self.assertTrue(actual.equals(expected))

    def test_duration_indexer_5(self):
        # Alto part of bwv603.mxl which is a part with ties. Also test that data argument is passed 
        # correctly. Since the data argument is passed, these results should not be cached.
        expected = TestDurationIndexer.make_series(TestDurationIndexer.bwv603_alto)
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus/bwv603.xml'))
        actual = ip.get_data('duration', data=(ip.get_data('noterest'), ip._analyses['part_streams'])).iloc[:, 1].dropna()
        self.assertTrue(actual.equals(expected))
        self.assertTrue('duration' not in ip._analyses.keys())

    def test_duration_indexer_6(self):
        # Soprano and bass parts of bwv603.xml
        # We won't verify all the parts, but we'll submit them all for analysis.
        expected = pandas.concat([TestDurationIndexer.make_series(TestDurationIndexer.bwv603_soprano),
                                  TestDurationIndexer.make_series(TestDurationIndexer.bwv603_bass)], axis=1)
        expected.columns = pandas.MultiIndex.from_product([('meter.DurationIndexer',), ('Soprano', 'Bass')])
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus/bwv603.xml'))
        actual = ip.get_data('duration').iloc[:, [0, 3]].dropna(how='all')
        self.assertTrue(actual.equals(expected))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
DURATION_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestDurationIndexer)
