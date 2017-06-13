#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_interval_indexer.py
# Purpose:                Tests for analyzers/indexers/interval.py
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


import os
import unittest
import six
import pandas
from music21 import interval, note
from vis.analyzers.indexers.interval import IntervalIndexer, HorizontalIntervalIndexer, real_indexer_func, indexer_funcs
from vis.tests.test_note_rest_indexer import TestNoteRestIndexer

# find the pathname of the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]


def make_series(lotuples):
    """
    From a list of two-tuples, make a Series. The list should be like this:

    [(desired_index, value), (desired_index, value), (desired_index, value)]
    """
    new_index = [x[0] for x in lotuples]
    vals = [x[1] for x in lotuples]
    return pandas.Series(vals, index=new_index)

def pandas_maker(lolists):
    """
    Use make_series() to convert a list of appropriate tuples into a DataFrame.

    Input: list of the input desired by make_series()

    Output: list of pandas.Series
    """
    return pandas.concat([make_series(x) for x in lolists], axis=1)


class TestIntervalIndexerShort(unittest.TestCase):
    """
    These 'short' tests were brought over from the vis9 tests for _event_finder().
    """
    def test_int_indexer_short_1(self):
        expected = pandas.Series('P8', name='0,1')
        test_in = pandas.concat([pandas.Series('G4'), pandas.Series('G3')], axis=1)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_2(self):
        expected = pandas.Series(['P8', 'Rest'], index=[0.0, 0.25], name='0,1')
        not_processed = [[(0.0, 'G4'), (0.25, 'Rest')],
                         [(0.0, 'G3'), (0.25, 'Rest')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_3(self):
        expected = pandas.Series(['P8', 'Rest'], index=[0.0, 0.25], name='0,1')
        not_processed = [[(0.0, 'G4')], [(0.0, 'G3'), (0.25, 'Rest')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_4(self):
        expected = pandas.Series(['P8', 'Rest'], index=[0.0, 0.25], name='0,1')
        not_processed = [[(0.0, 'G4'), (0.25, 'Rest')], [(0.0, 'G3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_5(self):
        expected = pandas.Series(['P8', 'm6'], index=[0.0, 0.5], name='0,1')
        not_processed = [[(0.0, 'G4'), (0.5, 'F4')],
                         [(0.0, 'G3'), (0.5, 'A3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_6(self):
        expected = pandas.Series(['P8', 'm7'], index=[0.0, 0.5], name='0,1')
        not_processed = [[(0.0, 'G4', 1.0)], [(0.0, 'G3'), (0.5, 'A3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_7(self):
        expected = pandas.Series(['m7', 'P8', 'm7', 'd5'], index=[0.0, 0.5, 1.0, 1.5], name='0,1')
        not_processed = [[(0.0, 'A4'), (0.5, 'G4', 1.0), (1.5, 'F4')],
                         [(0.0, 'B3'), (0.5, 'G3'),
                          (1.0, 'A3'), (1.5, 'B3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_8(self):
        expected = pandas.Series(['P8', 'Rest', 'm7'], index=[0.0, 0.25, 0.5], name='0,1')
        not_processed = [[(0.0, 'G4', 1.0)],
                         [(0.0, 'G3'), (0.25, 'Rest'), (0.5, 'A3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_9(self):
        expected = pandas.Series(['P8', 'Rest', 'm7', 'm6'], index=[0.0, 0.25, 0.5, 1.0], name='0,1')
        not_processed = [[(0.0, 'G4', 1.0), (1.0, 'G4')],
                         [(0.0, 'G3'), (0.25, 'Rest'), (0.5, 'A3'), (1.0, 'B3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_10(self):
        expected = pandas.Series(['P8', 'm7'], index=[0.0, 0.25], name='0,1')
        not_processed = [[(0.0, 'G4', 1.0)], [(0.0, 'G3'), (0.25, 'A3', 0.75)]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_11(self):
        expected = pandas.Series(['P8', 'P8'], index=[0.0, 0.5], name='0,1')
        not_processed = [[(0.0, 'G4', 1.0)], [(0.0, 'G3'), (0.5, 'G3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_12(self):
        expected = pandas.Series(['P8', 'Rest', 'P8'], index=[.0, .25, .5], name='0,1')
        not_processed = [[(0.0, 'G4', 1.0)], [(0.0, 'G3'), (0.25, 'Rest'), (0.5, 'G3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_13(self):
        expected = pandas.Series(['P8', 'Rest', 'm7', 'Rest', 'P8'],
                                 index=[.0, .125, .25, .375, .5], name='0,1')
        not_processed = [[(0.0, 'G4', 1.0)],
                         [(0.0, 'G3', 0.125), (0.125, 'Rest', 0.125),
                          (0.25, 'A3', 0.125), (0.375, 'Rest', 0.125), (0.5, 'G3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_14(self):
        expected = pandas.Series(['P8', 'P8', 'Rest', 'Rest', 'm7', 'm7', 'Rest', 'Rest', 'P8'],
                                 index=[.0, .0625, .125, .1875, .25, .3125, .375, .4375, .5], name='0,1')
        not_processed = [[(0.0, 'G4', 0.0625), (0.0625, 'G4', 0.0625),
                          (0.125, 'G4', 0.0625), (0.1875, 'G4', 0.0625),
                          (0.25, 'G4', 0.0625), (0.3125, 'G4', 0.0625),
                          (0.375, 'G4', 0.0625), (0.4375, 'G4', 0.0625),
                          (0.5, 'G4')],
                         [(0.0, 'G3', 0.125), (0.125, 'Rest', 0.125), (0.25, 'A3', 0.125),
                          (0.375, 'Rest', 0.0625), (0.4375, 'Rest', 0.0625), (0.5, 'G3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_15(self):
        expected = pandas.Series(['P8', 'P8', 'Rest', 'Rest', 'P8'],
                                 index=[.0, .5, .75, 1.0, 1.5], name='0,1')
        not_processed = [[(0.0, 'G4'), (0.5, 'G4'), (0.75, 'Rest'),
                          (1.0, 'G4'), (1.5, 'G4')],
                         [(0.0, 'G3'), (0.5, 'G3'), (0.75, 'Rest'),
                          (1.0, 'Rest'), (1.5, 'G3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_16(self):
        expected = pandas.Series(['P8', 'Rest', 'M10', 'M9', 'P12'],
                                 index=[.0, .5, .75, 1.25, 1.5], name='0,1')
        not_processed = [[(0.0, 'G4'), (0.5, 'A4', 0.75),
                          (1.25, 'G4'), (1.5, 'B4')],
                         [(0.0, 'G3'), (0.5, 'Rest'),
                          (0.75, 'F3', 0.75), (1.5, 'E3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_int_indexer_short_17(self):
        expected = pandas.Series(['P8', 'P8', 'M10', 'Rest', 'Rest', 'm7', 'M6'],
                                 index=[.0, .5, .75, 1.125, 1.25, 1.375, 2.0], name='0,1')
        not_processed = [[(0.0, 'G4'), (0.5, 'A4', 0.75), (1.25, 'F4', 0.75),
                          (2.0, 'E4')],
                         [(0.0, 'G3'), (0.5, 'A3'), (0.75, 'F3', 0.375),
                          (1.125, 'Rest'), (1.375, 'G3', 0.625), (2.0, 'G3')]]
        test_in = pandas_maker(not_processed)
        test_in.columns = pandas.MultiIndex.from_product([('notes',), ('0', '1')])
        setts = {'quality': True, 'simple or compound': 'compound', 'directed': True}
        actual = IntervalIndexer(test_in, settings=setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

class TestIntervalIndexerLong(unittest.TestCase):
    bwv77_S_B_basis = [(0.0, "P8"), (0.5, "M9"), (1.0, "m10"), (2.0, "P12"), (3.0, "M10"),
                       (4.0, "P12"), (4.5, "m13"), (5.0, "m17"), (5.5, "P12"), (6.0, "M13"),
                       (6.5, "P12"), (7.0, "P8"), (8.0, "m10"), (9.0, "m10"), (10.0, "M10"),
                       (11.0, "M10"), (12.0, "m10"), (13.0, "m10"), (14.0, "P12"), (15.0, "P8"),
                       (16.0, "P8"), (16.5, "M9"), (17.0, "m10"), (18.0, "P12"), (19.0, "M10"),
                       (20.0, "P12"), (20.5, "m13"), (21.0, "m17"), (21.5, "P12"), (22.0, "M13"),
                       (22.5, "P12"), (23.0, "P8"), (24.0, "m10"), (25.0, "m10"), (26.0, "M10"),
                       (27.0, "M10"), (28.0, "m10"), (29.0, "m10"), (30.0, "P12"), (31.0, "P8"),
                       (32.0, "P8"), (32.5, "M9"), (33.0, "m13"), (33.5, "m14"), (34.0, "m13"),
                       (34.5, "m14"), (35.0, "M10"), (36.0, "M10"), (36.5, "P11"), (37.0, "P12"),
                       (38.0, "M10"), (39.0, "P15"), (40.0, "P12"), (40.5, "P11"), (41.0, "M13"),
                       (42.0, "P12"), (43.0, "M17"), (43.5, "M16"), (44.0, "P12"), (44.5, "m13"),
                       (45.0, "P15"), (45.5, "m14"), (46.0, "P12"), (47.0, "P15"), (48.0, "P12"),
                       (49.0, "m10"), (50.0, "M13"), (50.5, "P12"), (51.0, "M10"), (52.0, "m10"),
                       (52.5, "P11"), (53.0, "m13"), (53.5, "d12"), (54.0, "m10"), (55.0, "P12"),
                       (56.0, "P8"), (56.5, "M10"), (57.0, "P12"), (57.5, "m13"), (58.0, "P15"),
                       (59.0, "M17"), (60.0, "P15"), (60.5, "m13"), (61.0, "M13"), (61.5, "m14"),
                       (62.0, "P12"), (63.0, "P8"), (64.0, "P15"), (65.0, "P12"), (65.5, "M13"),
                       (66.0, "m14"), (66.5, "P15"), (67.0, "M17"), (68.0, "P15"), (68.5, "m14"),
                       (69.0, "P12"), (69.5, "m14"), (70.0, "P12"), (71.0, "P15")]

    bwv77_S_B_small_compound_noqual = [(0.0, "8"), (0.5, "9"), (1.0, "10"), (2.0, "12"),
                                       (3.0, "10"), (4.0, "12"), (4.5, "13"), (5.0, "17"),
                                       (5.5, "12"), (6.0, "13"), (6.5, "12"), (7.0, "8")]

    bwv77_S_B_small_simple_qual = [(0.0, "P8"), (0.5, "M2"), (1.0, "m3"), (2.0, "P5"),
                                   (3.0, "M3"), (4.0, "P5"), (4.5, "m6"), (5.0, "m3"),
                                   (5.5, "P5"), (6.0, "M6"), (6.5, "P5"), (7.0, "P8")]

    bwv77_S_B_small_simple_noqual = [(0.0, "8"), (0.5, "2"), (1.0, "3"), (2.0, "5"), (3.0, "3"),
                                     (4.0, "5"), (4.5, "6"), (5.0, "3"), (5.5, "5"), (6.0, "6"),
                                     (6.5, "5"), (7.0, "8")]

    bwv77_soprano_small = [(0.0, "E4"), (0.5, "F#4"), (1.0, "G4"), (2.0, "A4"), (3.0, "B4"),
                           (4.0, "A4"), (5.0, "D5"), (6.0, "C#5"), (7.0, "B4")]

    bwv77_bass_small = [(0.0, "E3"), (1.0, "E3"), (2.0, "D3"), (3.0, "G3"), (4.0, "D3"), (4.5, "C#3"),
                        (5.0, "B2"), (5.5, "G3"), (6.0, "E3"), (6.5, "F#3"), (7.0, "B3")]

    def setUp(self):
        self.bwv77_soprano = make_series(TestNoteRestIndexer.bwv77_soprano)
        self.bwv77_bass = make_series(TestNoteRestIndexer.bwv77_bass)
        self.bwv77_s_small = make_series(self.bwv77_soprano_small)
        self.bwv77_b_small = make_series(self.bwv77_bass_small)

    def test_interval_indexer_1(self):
        # BWV7.7: full soprano and bass parts
        test_parts = pandas.concat([self.bwv77_soprano, self.bwv77_bass], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('a', 'b')])
        expected = make_series(TestIntervalIndexerLong.bwv77_S_B_basis)
        setts = {'simple or compound': 'compound', 'quality': True}
        actual = IntervalIndexer(test_parts, setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_interval_indexer_2(self):
        # BWV7.7: small soprano and bass parts; "simple" in settings
        test_parts = pandas.concat([self.bwv77_s_small, self.bwv77_b_small], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('a', 'b')])
        expected = make_series(TestIntervalIndexerLong.bwv77_S_B_small_simple_qual)
        setts = {'simple or compound': 'simple', 'quality': True}
        actual = IntervalIndexer(test_parts, setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_interval_indexer_3(self):
        # BWV7.7: small soprano and bass parts; "simple" and "quality" not in settings, and the
        # settings are in fact not specified
        test_parts = pandas.concat([self.bwv77_s_small, self.bwv77_b_small], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('a', 'b')])
        expected = make_series(TestIntervalIndexerLong.bwv77_S_B_small_compound_noqual)
        # setts = {}
        actual = IntervalIndexer(test_parts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_interval_indexer_4(self):
        # BWV7.7: small soprano and bass parts; "simple" in settings, "quality" not
        test_parts = pandas.concat([self.bwv77_s_small, self.bwv77_b_small], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('a', 'b')])
        expected = make_series(TestIntervalIndexerLong.bwv77_S_B_small_simple_noqual)
        setts = {'simple or compound': 'simple'}
        actual = IntervalIndexer(test_parts, setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))


class TestIntervalIndexerIndexer(unittest.TestCase):
    """
    These tests check that the indexer_func is correctly selected by the combination of settings.
    """
    def test_int_ind_indexer_init_0(self):
        int_indexer_1 = IntervalIndexer([], {'quality': False, 'simple or compound': 'simple', 'directed': True})
        int_indexer_2 = IntervalIndexer([], {'quality': 'diatonic no quality', 'simple or compound': 'simple', 'directed': True})
        self.assertEqual(int_indexer_1._indexer_func.__name__, 'indexer_dnq_dir_sim')
        self.assertEqual(int_indexer_2._indexer_func.__name__, 'indexer_dnq_dir_sim')

    def test_int_ind_indexer_init_1(self):
        int_indexer_1 = IntervalIndexer([], {'quality': True, 'simple or compound': 'simple', 'directed': True})
        int_indexer_2 = IntervalIndexer([], {'quality': 'diatonic with quality', 'simple or compound': 'simple', 'directed': True})
        self.assertEqual(int_indexer_1._indexer_func.__name__, 'indexer_dwq_dir_sim')
        self.assertEqual(int_indexer_2._indexer_func.__name__, 'indexer_dwq_dir_sim')

    def test_int_ind_indexer_init_2(self):
        int_indexer = IntervalIndexer([], {'quality': 'chromatic', 'simple or compound': 'simple', 'directed': True})
        self.assertEqual(int_indexer._indexer_func.__name__, 'indexer_chr_dir_sim')

    def test_int_ind_indexer_init_3(self):
        int_indexer = IntervalIndexer([], {'quality': 'interval class', 'simple or compound': 'simple', 'directed': True})
        self.assertEqual(int_indexer._indexer_func.__name__, 'indexer_icl_dir_sim')
    # ------
    def test_int_ind_indexer_init_4(self):
        int_indexer_1 = IntervalIndexer([], {'quality': False, 'simple or compound': 'simple', 'directed': False})
        int_indexer_2 = IntervalIndexer([], {'quality': 'diatonic no quality', 'simple or compound': 'simple', 'directed': False})
        self.assertEqual(int_indexer_1._indexer_func.__name__, 'indexer_dnq_und_sim')
        self.assertEqual(int_indexer_2._indexer_func.__name__, 'indexer_dnq_und_sim')

    def test_int_ind_indexer_init_5(self):
        int_indexer_1 = IntervalIndexer([], {'quality': True, 'simple or compound': 'simple', 'directed': False})
        int_indexer_2 = IntervalIndexer([], {'quality': 'diatonic with quality', 'simple or compound': 'simple', 'directed': False})
        self.assertEqual(int_indexer_1._indexer_func.__name__, 'indexer_dwq_und_sim')
        self.assertEqual(int_indexer_2._indexer_func.__name__, 'indexer_dwq_und_sim')

    def test_int_ind_indexer_init_6(self):
        int_indexer = IntervalIndexer([], {'quality': 'chromatic', 'simple or compound': 'simple', 'directed': False})
        self.assertEqual(int_indexer._indexer_func.__name__, 'indexer_chr_und_sim')

    def test_int_ind_indexer_init_7(self):
        int_indexer = IntervalIndexer([], {'quality': 'interval class', 'simple or compound': 'simple', 'directed': False})
        self.assertEqual(int_indexer._indexer_func.__name__, 'indexer_icl_und_sim')
    # ------
    def test_int_ind_indexer_init_8(self):
        int_indexer_1 = IntervalIndexer([], {'quality': False, 'simple or compound': 'compound', 'directed': True})
        int_indexer_2 = IntervalIndexer([], {'quality': 'diatonic no quality', 'simple or compound': 'compound', 'directed': True})
        self.assertEqual(int_indexer_1._indexer_func.__name__, 'indexer_dnq_dir_com')
        self.assertEqual(int_indexer_2._indexer_func.__name__, 'indexer_dnq_dir_com')

    def test_int_ind_indexer_init_9(self):
        int_indexer_1 = IntervalIndexer([], {'quality': True, 'simple or compound': 'compound', 'directed': True})
        int_indexer_2 = IntervalIndexer([], {'quality': 'diatonic with quality', 'simple or compound': 'compound', 'directed': True})
        self.assertEqual(int_indexer_1._indexer_func.__name__, 'indexer_dwq_dir_com')
        self.assertEqual(int_indexer_2._indexer_func.__name__, 'indexer_dwq_dir_com')

    def test_int_ind_indexer_init_10(self):
        int_indexer = IntervalIndexer([], {'quality': 'chromatic', 'simple or compound': 'compound', 'directed': True})
        self.assertEqual(int_indexer._indexer_func.__name__, 'indexer_chr_dir_com')

    def test_int_ind_indexer_init_11(self):
        setts = {'quality': 'interval class', 'simple or compound': 'compound', 'directed': True}
        self.assertRaises(RuntimeWarning, IntervalIndexer, [], setts)
    # ------
    def test_int_ind_indexer_init_12(self):
        int_indexer_1 = IntervalIndexer([], {'quality': False, 'simple or compound': 'compound', 'directed': False})
        int_indexer_2 = IntervalIndexer([], {'quality': 'diatonic no quality', 'simple or compound': 'compound', 'directed': False})
        self.assertEqual(int_indexer_1._indexer_func.__name__, 'indexer_dnq_und_com')
        self.assertEqual(int_indexer_2._indexer_func.__name__, 'indexer_dnq_und_com')

    def test_int_ind_indexer_init_13(self):
        int_indexer_1 = IntervalIndexer([], {'quality': True, 'simple or compound': 'compound', 'directed': False})
        int_indexer_2 = IntervalIndexer([], {'quality': 'diatonic with quality', 'simple or compound': 'compound', 'directed': False})
        self.assertEqual(int_indexer_1._indexer_func.__name__, 'indexer_dwq_und_com')
        self.assertEqual(int_indexer_2._indexer_func.__name__, 'indexer_dwq_und_com')

    def test_int_ind_indexer_init_14(self):
        int_indexer = IntervalIndexer([], {'quality': 'chromatic', 'simple or compound': 'compound', 'directed': False})
        self.assertEqual(int_indexer._indexer_func.__name__, 'indexer_chr_und_com')

    def test_int_ind_indexer_init_15(self):
        setts = {'quality': 'interval class', 'simple or compound': 'compound', 'directed': False}
        self.assertRaises(RuntimeWarning, IntervalIndexer, [], setts)

    def test_indexer_funcs_1(self):
        """ This test makes sure that the analysis types are working correctly for all sorts of intervals. """
        expecteds = (['1', 'P1', '0', '0', '1', 'P1', '0', '0', '1', 'P1', '0', '1', 'P1', '0'],
                     ['1', 'P1', '0', '0', '1', 'P1', '0', '0', '1', 'P1', '0', '1', 'P1', '0'],
                     ['1', 'P1', '0', '0', '1', 'P1', '0', '0', '1', 'P1', '0', '1', 'P1', '0'],
                     ['8', 'd8', '11', '1', '8', 'd8', '11', '1', '8', 'd8', '11', '8', 'd8', '11'],
                     ['-2', '-m2', '-1', '-1', '2', 'm2', '1', '1', '-2', '-m2', '-1', '2', 'm2', '1'],
                     ['2', 'm2', '1', '1', '2', 'm2', '1', '1', '2', 'm2', '1', '2', 'm2', '1'],
                     ['1', '-d1', '-1', '-1', '1', 'd1', '1', '1', '1', '-d1', '-1', '1', 'd1', '1'],
                     ['1', '-ddd1', '-3', '-3', '1', 'ddd1', '3', '3', '1', '-ddd1', '-3', '1', 'ddd1', '3'],
                     ['-6', '-M6', '-9', '-3', '6', 'M6', '9', '3', '-6', '-M6', '-9', '6', 'M6', '9'],
                     ['-3', '-m3', '-3', '-3', '3', 'm3', '3', '3', '-10', '-m10', '-15', '10', 'm10', '15'],
                     ['-2', '-m2', '-1', '-1', '2', 'm2', '1', '1', '-9', '-m9', '-13', '9', 'm9', '13'],
                     ['-8', '-P8', '0', '-0', '8', 'P8', '0', '0', '-8', '-P8', '-12', '8', 'P8', '12'],
                     ['-8', '-P8', '0', '-0', '8', 'P8', '0', '0', '-15', '-P15', '-24', '15', 'P15', '24'],
                     ['-5', '-A5', '-8', '-4', '5', 'A5', '8', '4', '-5', '-A5', '-8', '5', 'A5', '8'],
                     ['-5', '-AA5', '-9', '-3', '5', 'AA5', '9', '3', '-12', '-AA12', '-21', '12', 'AA12', '21'],
                     ['-2', 'dd2', '1', '1', '2', 'dd2', '1', '1', '-2', 'dd2', '1', '2', 'dd2', '1'],
                     ['2', '-dd2', '-1', '-1', '2', 'dd2', '1', '1', '2', '-dd2', '-1', '2', 'dd2', '1'],
                     ['-3', '-A3', '-5', '-5', '3', 'A3', '5', '5', '-3', '-A3', '-5', '3', 'A3', '5'],
                     ['-7', '-M7', '-11', '-1', '7', 'M7', '11', '1', '-49', '-M49', '-83', '49', 'M49', '83']
                     )
        funcs = indexer_funcs[:11] + indexer_funcs[12:-1] # copy the indexer_funcs list minus the None placeholders
        # NB: the first note in each 2-tuple is the "upper" note.
        pairs = (('C0', 'C0'), ('C17', 'C17'), ('C-27', 'C-27'), ('c-10', 'c9'), ('b5', 'c6'),
                 ('c6', 'b5'), ('c4', 'c#4'), ('c--', 'c#'), ('f3', 'd4'), ('d#2', 'f#3'),
                 ('e1', 'f2'), ('g3', 'g4'), ('g3', 'g5'), ('e-4', 'b4'), ('e-4', 'b#5'),
                 ('e#2', 'f-2'), ('f-2', 'e#2'), ('a-1', 'c#2'), ('a2', 'g#9') )
        for i, pair in enumerate(pairs):
            func_results = []
            for func in funcs:
                func_results.append(func(pair))
            self.assertSequenceEqual(expecteds[i], func_results)


class TestHorizIntervalIndexerLong(unittest.TestCase):
    # data_interval_indexer_1.csv
    bwv77_S_B_short = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'data_interval_indexer_1.csv'),
                                      index_col=0,
                                      names=['a'],
                                      dtype={'a': str})

    # data_interval_indexer_2.csv
    bwv77_S_B_short_noqual = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'data_interval_indexer_2.csv'),
                                             index_col=0,
                                             names=['a'],
                                             dtype={'a': str})

    # data_interval_indexer_3.csv
    bwv77_S_B_basis = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'data_interval_indexer_3.csv'),
                                      index_col=0,
                                      names=['a'],
                                      dtype={'a': str})

    def setUp(self):
        self.bwv77_soprano = make_series(TestNoteRestIndexer.bwv77_soprano)
        self.bwv77_bass = make_series(TestNoteRestIndexer.bwv77_bass)

    def test_interval_indexer_1a(self):
        # BWV7.7: first 26 things in soprano part
        test_parts = pandas.concat([self.bwv77_soprano], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('0',)])
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_short['a']
        setts = {'simple or compound': 'compound', 'quality': True}
        actual = HorizontalIntervalIndexer(test_parts, setts).run().iloc[:26, 0]
        self.assertTrue(actual.equals(expected))

    def test_interval_indexer_1b(self):
        # BWV7.7: first 26 things in soprano part (no settings specified)
        test_parts = pandas.concat([self.bwv77_soprano], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('0',)])
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_short_noqual['a']
        actual = HorizontalIntervalIndexer(test_parts).run().iloc[:26, 0]
        self.assertTrue(actual.equals(expected))

    def test_interval_indexer_1c(self):
        # BWV7.7: first 26 things in soprano part (simple; no quality)
        test_parts = pandas.concat([self.bwv77_soprano], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('0',)])
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_short_noqual['a']
        setts = {'simple or compound': 'simple', 'quality': False}
        actual = HorizontalIntervalIndexer(test_parts, setts).run().iloc[:26, 0]
        self.assertTrue(actual.equals(expected))

    def test_interval_indexer_2(self):
        # BWV7.7: whole soprano part
        # NB: this test is more rigourous than the others, since it actually uses the DataFrame
        test_parts = pandas.concat([self.bwv77_soprano], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('0',)])
        expected = TestHorizIntervalIndexerLong.bwv77_S_B_basis['a']
        setts = {'simple or compound': 'compound', 'quality': True}
        actual = HorizontalIntervalIndexer(test_parts, setts).run().iloc[:, 0]
        self.assertTrue(actual.equals(expected))

    def test_interval_indexer_3(self):
        """BWV7.7: whole bass part; 'horiz_attach_later' is True"""
        test_parts = pandas.concat([self.bwv77_bass], axis=1)
        test_parts.columns = pandas.MultiIndex.from_product([('A',), ('0',)])
        setts = {'simple or compound': 'compound', 'quality': True, 'horiz_attach_later': True}
        expected = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'corpus', 'data_horiz_int_ind_3.pickle'))
        actual = HorizontalIntervalIndexer(test_parts, setts).run()
        self.assertTrue(actual.equals(expected))


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INTERVAL_INDEXER_SHORT_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerShort)
INTERVAL_INDEXER_LONG_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerLong)
INT_IND_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerIndexer)
HORIZ_INT_IND_LONG_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestHorizIntervalIndexerLong)
