#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_note_rest_indexer.py
# Purpose:                Tests for the NoteRestIndexer
#
# Copyright (C) 2015 Alexander Morgan
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
"""
.. codeauthor:: Alexander Morgan

Tests for the measure indexer. NB: Based on noterest indexer tests.
"""
# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904

import os
import unittest
import pandas
from music21 import converter, stream, note
from vis.analyzers.indexers import meter

# find the pathname of the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]

class TestMeasureIndexer(unittest.TestCase):
    bwv77_measure_index = [0.0, 1.0, 5.0, 9.0, 13.0, 17.0, 21.0, 25.0, 29.0, 33.0, 
                           37.0, 41.0, 45.0, 49.0, 53.0, 57.0, 61.0, 65.0, 69.0]

    def test_measure_indexer_1(self):
        # When the parts are empty
        expected = {'0': pandas.Series(), '1': pandas.Series()}
        test_part = [stream.Part(), stream.Part()]
        measure_indexer = meter.MeasureIndexer(test_part)
        actual = measure_indexer.run()['meter.MeasureIndexer']
        for key in expected:
            self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
            self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    def test_note_rest_indexer_2(self):
        # When the part has no Measure objects in it but a bunch of notes.
        expected = {'0': pandas.Series()}
        test_part = stream.Part()
        # add stuff to the test_part
        for i in range(0, 1000, 2):
            add_me = note.Note('C#5', quarterLength=2.0)
            add_me.offset = i
            test_part.append(add_me)
        test_part = [test_part]
        # finished adding stuff to the test_part
        measure_indexer = meter.MeasureIndexer(test_part)
        actual = measure_indexer.run()['meter.MeasureIndexer']
        self.assertEqual(len(expected), len(actual.columns))
        for key in expected:
            self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
            self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    def test_note_rest_indexer_3(self):
        # When there are a bunch of measures with a note in each one.
        expected = {'0': pandas.Series(range(1, 11), index=[float(x) for x in range(10)])}
        test_part = stream.Part()
        # add stuff to the test_part
        for i in range(1, 11):
            add_me = stream.Measure()
            add_me.number = i
            add_me.insert(note.Note('C#5', quarterLength=1.0))
            add_me.offset = i
            test_part.append(add_me)
        test_part = [test_part]
        # finished adding stuff to the test_part
        measure_indexer = meter.MeasureIndexer(test_part)
        actual = measure_indexer.run()['meter.MeasureIndexer']
        self.assertEqual(len(expected), len(actual.columns))
        for key in expected:
            self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
            self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    def test_note_rest_indexer_4(self):
        # bwv77.mxl, which is a piece with a pick-up measure. All 4 parts have the same data.
        measure_data = pandas.Series(range(19), index=TestMeasureIndexer.bwv77_measure_index)
        expected = {'0': measure_data, '1': measure_data, '2': measure_data, '3': measure_data}
        test_parts = converter.parse(os.path.join(VIS_PATH, 'tests', 'corpus/bwv77.mxl')).parts
        measure_indexer = meter.MeasureIndexer(test_parts)
        actual = measure_indexer.run()['meter.MeasureIndexer']
        self.assertEqual(len(expected), len(actual.columns))
        for key in expected:
            self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
            self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    def test_note_rest_indexer_5(self):
        # A two-part test piece with no pick-up measure originally written to test fermata indexer.
        measure_data = pandas.Series([1, 2], index=[0.0, 4.0])
        expected = {'0': measure_data, '1': measure_data}
        test_piece = converter.parse(os.path.join(VIS_PATH, 'tests', 'corpus/test_fermata_rest.xml'))
        test_parts = test_piece.parts
        measure_indexer = meter.MeasureIndexer(test_parts)
        actual = measure_indexer.run()['meter.MeasureIndexer']
        self.assertEqual(2, len(actual.columns))
        for key in expected:
            self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
            self.assertSequenceEqual(list(expected[key]), list(actual[key]))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
MEASURE_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMeasureIndexer)
