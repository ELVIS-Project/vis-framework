#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_new_ngram.py
# Purpose:                Test the NGram Indexer
#
# Copyright (C) 2013, 2014 Christopher Antila, Alexander Morgan
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
"""Tests for the NGramIndexer and its helper functions."""

# pylint: disable=too-many-public-methods

import os
import unittest
import pandas
from vis.analyzers.indexers import new_ngram
import pdb
# find pathname of the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]

VERTICAL_TUPLES = [(0.0, 'P4'), (4.0, 'M3'), (8.0, 'M6'), (12.0, 'P8'), (14.0, 'm6'), (16.0, 'm7'),
                   (18.0, 'M6'), (20.0, 'M6'), (22.0, 'P5'), (28.0, 'P4'), (31.0, 'A4'), (32.0, 'P4'),
                   (34.0, 'm3'), (36.0, 'Rest'), (38.0, 'Rest')]
VERT_DF = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'new_ngram_1.pickle'))

HORIZONTAL_TUPLES = [(0.0, 'P4'), (4.0, '-m3'), (8.0, '-M2'), (12.0, 'M3'), (14.0, '-M2'),
                     (16.0, '-M2'), (20.0, 'P5'), (28.0, '-M2'), (31.0, '-m2'), (32.0, 'Rest')]
HORIZ_DF = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'new_ngram_2.pickle'))

EXPECTED = [(0.0, '[P4] (P4) [M3] (-m3) [M6] (-M2) [P8]'),
            (4.0, '[M3] (-m3) [M6] (-M2) [P8] (M3) [m6]'),
            (8.0, '[M6] (-M2) [P8] (M3) [m6] (-M2) [m7]'),
            (12.0, '[P8] (M3) [m6] (-M2) [m7] (-M2) [M6]'),
            (14.0, '[m6] (-M2) [m7] (-M2) [M6] (P1) [M6]'),
            (16.0, '[m7] (-M2) [M6] (P1) [M6] (P5) [P5]'),
            (18.0, '[M6] (P1) [M6] (P5) [P5] (P1) [P4]'),
            (20.0, '[M6] (P5) [P5] (P1) [P4] (-M2) [A4]'),
            (22.0, '[P5] (P1) [P4] (-M2) [A4] (-m2) [P4]')]

# EXPECTED_DF = pandas.concat([series_maker(EXPECTED)], axis=1)

EXPECTED_DF = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'new_ngram_3.pickle'))

V_IND = 'interval.IntervalIndexer'
H_IND = 'interval.HorizontalIntervalIndexer'

# iterables = [['interval.HorizontalIntervalIndexer'], ('1',)]
# hmi = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
# HORIZ_DF.columns = hmi

iterables = [['new_ngram.NewNGramIndexer'], ('0,1 : 1',)]
emi = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
EXPECTED_DF.columns = emi


# pdb.set_trace()


# VERT_DATA.to_pickle('/home/amor/Code/vis-framework/vis/tests/expecteds/new_ngram_1.pickle')
# HORIZ_DF.to_pickle('/home/amor/Code/vis-framework/vis/tests/expecteds/new_ngram_2.pickle')
EXPECTED_DF.to_pickle('/home/amor/Code/vis-framework/vis/tests/expecteds/new_ngram_3.pickle')

# pdb.set_trace()

def series_maker(lotuples):
    """Turn a List Of TUPLES (offset, 'value') into a Series."""
    return pandas.Series([x[1] for x in lotuples], index=[x[0] for x in lotuples])

def mi_maker(iterable1, iterable2):
    """Makes a pandas MultiIndex that conforms to vis standards. Iterable1 should be the
    name of the indexer and iterable2 should be a list of the part combinations. Returns
    the same df with the columns renamed according to the iterables passed."""
    iterables = (iterable1, iterable2)
    return pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])

def df_maker(series, cols):
    """Makes a pandas DataFrame that conforms to vis standards. Iterable1 should be the
    name of the indexer and iterable2 should be a list of the part combinations. Returns
    the same df with the columns renamed according to the iterables passed."""
    df = pandas.concat(series, axis=1)
    df.columns = cols
    return df

class TestNewNGramIndexer(unittest.TestCase):
    """Tests for the NewNGramIndexer and its helper functions."""

    def test_init_1(self):
        """that __init__() works properly (only required settings given)"""
        # pylint: disable=protected-access
        setts = {'n': 1, 'vertical': ['0,1']}
        actual = new_ngram.NewNGramIndexer((VERT_DF,), setts)
        for setting in ('n', 'vertical'):
            self.assertEqual(setts[setting], actual._settings[setting])
        for setting in ('horizontal', 'brackets', 'terminator', 'continuer'):
            self.assertEqual(new_ngram.NewNGramIndexer.default_settings[setting], actual._settings[setting])

    def test_init_2(self):
        """that __init__() works properly (all settings given)"""
        # pylint: disable=protected-access
        setts = {'n': 2, 'vertical': ['0,1'], 'horizontal': 'banana', 'brackets': True,
                 'terminator': 'RoboCop', 'continuer': 'Alex Murphy', 'hanging': True}
        actual = new_ngram.NewNGramIndexer((VERT_DF, HORIZ_DF), setts)
        for setting in ('n', 'vertical', 'horizontal', 'brackets', 'terminator', 'continuer', 'hanging'):
            self.assertEqual(setts[setting], actual._settings[setting])

    def test_init_3(self):
        """that __init__() fails when 'n' is too short"""
        # pylint: disable=protected-access
        setts = {'n': 0, 'vertical': ['0,1']}  # n is too short
        self.assertRaises(RuntimeError, new_ngram.NewNGramIndexer, (VERT_DF,), setts)
        try:
            new_ngram.NewNGramIndexer((VERT_DF,), setts)
        except RuntimeError as run_err:
            self.assertEqual(new_ngram.NewNGramIndexer._N_VALUE_TOO_LOW, run_err.args[0])

    def test_init_4(self):
        """that __init__() fails when there are no 'vertical' events"""
        # pylint: disable=protected-access
        setts = {'n': 14, 'horizontal': [0]}  # no "vertical" parts
        self.assertRaises(RuntimeError, new_ngram.NewNGramIndexer, 'a DataFrame', setts)
        try:
            new_ngram.NewNGramIndexer('a DataFrame', setts)
        except RuntimeError as run_err:
            self.assertEqual(new_ngram.NewNGramIndexer._MISSING_SETTINGS, run_err.args[0])

    def test_init_5(self):
        """that __init__() fails when horizontal observations are provided and 'n' equals 1."""
        # pylint: disable=protected-access
        setts = {'n': 1, 'vertical': ['0,1'], 'horizontal': 'banana', 'brackets': True,
                 'terminator': 'RoboCop', 'continuer': 'Alex Murphy', 'hanging': True}
        self.assertRaises(RuntimeError, new_ngram.NewNGramIndexer, (VERT_DF,), setts)
        try:
            new_ngram.NewNGramIndexer((VERT_DF, HORIZ_DF), setts)
        except RuntimeError as run_err:
            self.assertEqual(new_ngram.NewNGramIndexer._SUPERFLUOUS_HORIZONTAL_DATA, run_err.args[0])

    def test_init_6a(self):
        """that __init__() manages the horizontal setting set to 'highest' correctly."""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        mi = mi_maker((H_IND,), ('1', '0'))
        horizontal = df_maker([pandas.Series(['z', 'x', 'y']),
                               pandas.Series(['a', 'b', 'c'])], mi)
        setts = {'n': 2, 'horizontal': 'highest', 'vertical': [('0,1',)], 'brackets': False}

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts)

        self.assertEqual([('0',)], actual._settings['horizontal'])

    def test_init_6b(self):
        """that __init__() manages the horizontal setting set to 'lowest' correctly."""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        mi = mi_maker((H_IND,), ('1', '0'))
        horizontal = df_maker([pandas.Series(['z', 'x', 'y']),
                               pandas.Series(['a', 'b', 'c'])], mi)
        setts = {'n': 2, 'horizontal': 'lowest', 'vertical': [('0,1',)], 'brackets': False}

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts)

        self.assertEqual([('1',)], actual._settings['horizontal'])

    def test_ngram_1a(self):
        """most basic test"""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1',)], 'brackets': False}
        expected = pandas.DataFrame([pandas.Series(['A a B', 'B b C', 'C c D'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_1b(self): # Perhaps we just don't need this test.
        """like test _1a but with an extra element in "scores" and no "horizontal" assignment"""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
        setts = {'n': 2, 'vertical': [('0,1',)], 'brackets': False}
        expected = pandas.DataFrame([pandas.Series(['A B', 'B C', 'C D'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_1c(self):
        """like test _1a but with self._settings['hanging'] set to True."""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1',)], 'brackets': False,
                 'hanging': True}
        expected = pandas.DataFrame([pandas.Series(['A a', 'B b', 'C c'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))
    def test_ngram_2(self):
        """adds the grouping characters"""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1',)],
                 'brackets': True}
        expected = pandas.DataFrame([pandas.Series(['[A] (a) [B]', '[B] (b) [C]', '[C] (c) [D]'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_3(self):
        """test _1 but n=3"""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
        setts = {'n': 3, 'horizontal': [('1',)], 'vertical': [('0,1',)], 'brackets': False}
        expected = pandas.DataFrame([pandas.Series(['A a B b C', 'B b C c D'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_4a(self):
        """test _1 but with two verticals"""
        mi = mi_maker((V_IND,), ('0,1', '0,2'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D']),
                             pandas.Series(['Z', 'X', 'Y', 'W'])], mi) 
        horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1', '0,2')], 'brackets': False}
        expected = pandas.DataFrame([pandas.Series(['A Z a B X', 'B X b C Y', 'C Y c D W'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 : 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_4b(self):
        """test _4a but with 'brackets' set to True"""
        mi = mi_maker((V_IND,), ('0,1', '0,2'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D']),
                             pandas.Series(['Z', 'X', 'Y', 'W'])], mi) 
        horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1', '0,2')], 'brackets': True}
        expected = pandas.DataFrame([pandas.Series(['[A Z] (a) [B X]', '[B X] (b) [C Y]', '[C Y] (c) [D W]'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 : 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_5a(self):
        """test _1 but with two horizontals, and the order of 'horizontal' setting is important"""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        mi = mi_maker((H_IND,), ('1', '0'))
        horizontal = df_maker([pandas.Series(['z', 'x', 'y']),
                               pandas.Series(['a', 'b', 'c'])], mi)
        setts = {'n': 2, 'horizontal': [('0', '1')], 'vertical': [('0,1',)], 'brackets': False}
        expected = pandas.DataFrame([pandas.Series(['A a z B', 'B b x C', 'C c y D'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 0 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_5b(self):
        """test _5a but with 'brackets' set to True"""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        mi = mi_maker((H_IND,), ('1', '0'))
        horizontal = df_maker([pandas.Series(['z', 'x', 'y']),
                               pandas.Series(['a', 'b', 'c'])], mi)
        setts = {'n': 2, 'horizontal': [('0', '1')], 'vertical': [('0,1',)], 'brackets': True}
        expected = pandas.DataFrame([pandas.Series(['[A] (a z) [B]', '[B] (b x) [C]', '[C] (c y) [D]'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 0 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    # def test_ngram_5c(self):
    #     """test _1 but with two horizontals, and the order of 'horizontal' setting is important"""
    #     vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
    #     mi = mi_maker((H_IND,), ('1', '0'))
    #     horizontal = df_maker([pandas.Series(['z', 'x', 'y']),
    #                            pandas.Series(['a', 'b', 'c'])], mi)
    #     setts = {'n': 2, 'horizontal': [('0', '1')], 'vertical': [('0,1',)], 'brackets': False}
    #     expected = pandas.DataFrame([pandas.Series(['A a z B', 'B b x C', 'C c y D'])],
    #                                 index=[['new_ngram.NewNGramIndexer'], ['0,1 : 0 1']]).T

    #     actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

    #     self.assertTrue(actual.equals(expected))

    def test_ngram_6(self):
        """combination of tests _4a and _5a"""
        mi = mi_maker((V_IND,), ('0,1', '0,2'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D']),
                             pandas.Series(['Z', 'X', 'Y', 'W'])], mi) 
        mi = mi_maker((H_IND,), ('1', '2'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c']),
                               pandas.Series(['z', 'x', 'y'])], mi)
        setts = {'n': 2, 'horizontal': [('1', '2')], 'vertical': [('0,1', '0,2')], 'brackets': True}
        expected = pandas.DataFrame([pandas.Series(['[A Z] (a z) [B X]',
                                                    '[B X] (b x) [C Y]',
                                                    '[C Y] (c y) [D W]'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 : 1 2']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_7(self):
        """test _1 with a terminator; nothing should be picked up after terminator"""
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'])], VERT_DF.columns) 
        horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1',)], 'brackets': True,
                 'terminator': ['C']}
        expected = pandas.DataFrame([pandas.Series(['[A] (a) [B]'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_8(self):
        """test _6 with a terminator; nothing should be picked up before terminator"""
        mi = mi_maker((V_IND,), ('0,1', '0,2'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D']),
                             pandas.Series(['Z', 'X', 'Y', 'W'])], mi) 
        mi = mi_maker((H_IND,), ('1', '2'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c']),
                               pandas.Series(['z', 'x', 'y'])], mi)
        setts = {'n': 2, 'horizontal': [('1', '2')], 'vertical': [('0,1', '0,2')], 'brackets': True,
                 'terminator': ['X']}
        expected = pandas.DataFrame([pandas.Series(['[C Y] (c y) [D W]'], index=[2])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 : 1 2']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_9(self):
        """test _8 but longer; things happen before and after terminator"""
        mi = mi_maker((V_IND,), ('0,1', '0,2'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D', 'E']),
                             pandas.Series(['Z', 'X', 'Y', 'W', 'V'])], mi) 
        mi = mi_maker((H_IND,), ('1', '2'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c', 'd']),
                               pandas.Series(['z', 'x', 'y', 'w'])], mi)
        setts = {'n': 2, 'horizontal': [('1', '2')], 'vertical': [('0,1', '0,2')], 'brackets': True,
                 'terminator': ['C']}
        expected = pandas.DataFrame([pandas.Series(['[A Z] (a z) [B X]', '[D W] (d w) [E V]'],
                                                   index=[0, 3])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 : 1 2']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_10(self):
        """test _1 with too few "horizontal" things (should use "continuer" character)"""
        vertical = pandas.concat([pandas.Series(['A', 'B', 'C', 'D'])], axis=1)
        vertical.columns = VERT_DF.columns
        horizontal = pandas.concat([pandas.Series(['a', 'b'])], axis=1)
        horizontal.columns = HORIZ_DF.columns
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1',)],
                 'brackets': False}
        expected = pandas.DataFrame([pandas.Series(['A a B', 'B b C', 'C _ D'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T
        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_11(self):
        """test _10 with one "horizontal" thing at the end"""
        vertical = pandas.concat([pandas.Series(['A', 'B', 'C', 'D'])], axis=1)
        vertical.columns = VERT_DF.columns
        horizontal = pandas.concat([pandas.Series(['z'], index=[2])], axis=1)
        horizontal.columns = HORIZ_DF.columns
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1',)],
                 'brackets': False}
        expected = pandas.DataFrame([pandas.Series(['A _ B', 'B _ C', 'C z D'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T
        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_12(self):
        """test _11 with one missing "horizontal" thing in the middle"""
        vertical = pandas.concat([pandas.Series(['A', 'B', 'C', 'D'])], axis=1)
        vertical.columns = VERT_DF.columns
        horizontal = pandas.concat([pandas.Series(['a', 'z'], index=[0, 2])], axis=1)
        horizontal.columns = HORIZ_DF.columns
        setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1',)],
                 'brackets': False}
        expected = pandas.DataFrame([pandas.Series(['A a B', 'B _ C', 'C z D'])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T
        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    # def test_ngram_13(self): # XXXX This is an impossible scenario because the horizontal observations
    #     # must stop one before the vertical ones. This would only be feasible if the "horizontal"
    #     # component being tracked is in a voice that doesn't participate in the "vertical" component.
    #     # For now this test is going to get commented out.
    #     """test _1 with too few "vertical" things (last should be repeated)"""
    #     vertical = df_maker([pandas.Series(['A', 'B', 'C'])], VERT_DF.columns) 
    #     horizontal = df_maker([pandas.Series(['a', 'b', 'c'])], HORIZ_DF.columns) 
    #     setts = {'n': 2, 'horizontal': [('1',)], 'vertical': [('0,1',)], 'brackets': False}
    #     expected = pandas.DataFrame([pandas.Series(['A a B', 'B b C', 'C c C'])],
    #                                 index=[['new_ngram.NewNGramIndexer'], ['0,1 : 1']]).T

    #     actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

    #     self.assertSequenceEqual(list(expected.columns), list(actual.columns))
    #     self.assertEqual(len(expected), len(actual))
    #     for col_name in expected.columns:
    #         self.assertSequenceEqual(list(expected[col_name].index), list(actual[col_name].index))
    #         self.assertSequenceEqual(list(expected[col_name].values), list(actual[col_name].values))

    # def test_ngram_14(self):
    #     """test _13 with one missing "vertical" thing in the middle"""
    #     vertical = pandas.Series(['A', 'C', 'D'], index=[0, 2, 3])
    #     horizontal = pandas.Series(['a', 'b', 'c'])
    #     in_val = pandas.DataFrame([vertical, horizontal], index=[['vert', 'horiz'], ['0,1', '1']]).T
    #     setts = {'n': 2, 'horizontal': [('horiz', '1')], 'vertical': [('vert', '0,1')],
    #              'brackets': False}
    #     expected = pandas.DataFrame([pandas.Series(['A a A', 'A b C', 'C c D'])],
    #                                 index=[['new_ngram.NewNGramIndexer'], ['0,1 1']]).T

    #     actual = new_ngram.NewNGramIndexer(in_val, setts).run()

    #     self.assertSequenceEqual(list(expected.columns), list(actual.columns))
    #     self.assertEqual(len(expected), len(actual))
    #     for col_name in expected.columns:
    #         self.assertSequenceEqual(list(expected[col_name].index), list(actual[col_name].index))
    #         self.assertSequenceEqual(list(expected[col_name].values), list(actual[col_name].values))

    def test_ngram_15(self):
        """longer test, inspired by the first five measures of "Kyrie.krn" parts 1 and 3"""
        setts = {'n': 4, 'horizontal': [('1',)], 'vertical': [('0,1',)],
                 'continuer': 'P1', 'terminator': 'Rest', 'brackets': True}
        actual = new_ngram.NewNGramIndexer([VERT_DF, HORIZ_DF], setts).run()

        self.assertTrue(actual.equals(EXPECTED_DF))

    def test_ngram_16a(self):
        """test _9 but with three "vertical" parts and no terminator"""
        mi = mi_maker((V_IND,), ('0,1', '0,2', '0,3'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D', 'E']),
                             pandas.Series(['Z', 'X', 'Y', 'W', 'V']),
                             pandas.Series(['Q', 'R', 'S', 'T', 'U'])], mi) 
        mi = mi_maker((H_IND,), ('2', '3'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c', 'd']),
                               pandas.Series(['z', 'x', 'y', 'w'])], mi)
        setts = {'n': 2, 'horizontal': [('2', '3')], 'vertical': [('0,1', '0,2', '0,3')], 'brackets': True,}
        expected = pandas.DataFrame([pandas.Series(['[A Z Q] (a z) [B X R]', '[B X R] (b x) [C Y S]',
                                                    '[C Y S] (c y) [D W T]', '[D W T] (d w) [E V U]'],
                                                   index=[0, 1, 2, 3])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 0,3 : 2 3']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_17(self):
        """test _16 but with four "vertical" parts"""
        mi = mi_maker((V_IND,), ('0,1', '0,2', '0,3', '0,4'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D', 'E']),
                             pandas.Series(['Z', 'X', 'Y', 'W', 'V']),
                             pandas.Series(['Q', 'R', 'S', 'T', 'U']),
                             pandas.Series(['J', 'K', 'L', 'M', 'N'])], mi) 
        mi = mi_maker((H_IND,), ('3', '4'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c', 'd']),
                               pandas.Series(['z', 'x', 'y', 'w'])], mi)
        setts = {'n': 2, 'horizontal': [('3', '4')], 'vertical': [('0,1', '0,2', '0,3', '0,4')], 'brackets': True,}
        expected = pandas.DataFrame([pandas.Series(['[A Z Q J] (a z) [B X R K]',
                                                    '[B X R K] (b x) [C Y S L]',
                                                    '[C Y S L] (c y) [D W T M]',
                                                    '[D W T M] (d w) [E V U N]'],
                                                   index=[0, 1, 2, 3])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 0,3 0,4 : 3 4']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_18(self):
        """test _17 but with n=1"""
        mi = mi_maker((V_IND,), ('0,1', '0,2', '0,3', '0,4'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D', 'E']),
                             pandas.Series(['Z', 'X', 'Y', 'W', 'V']),
                             pandas.Series(['Q', 'R', 'S', 'T', 'U']),
                             pandas.Series(['J', 'K', 'L', 'M', 'N'])], mi) 
        setts = {'n': 1, 'vertical': [('0,1', '0,2', '0,3', '0,4')], 'brackets': True,}
        expected = pandas.DataFrame([pandas.Series(['[A Z Q J]', '[B X R K]', '[C Y S L]',
                                                    '[D W T M]', '[E V U N]'],
                                                   index=[0, 1, 2, 3, 4])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 0,3 0,4']]).T

        actual = new_ngram.NewNGramIndexer([vertical], setts).run()

        self.assertTrue(actual.equals(expected))

    # def test_ngram_19(self): # Commented out for the same reasons as test_ngram_13.
    #     # test _0 with a "missing" vertical and horizontal thing
    #     # Input:
    #     #    0  1  2  3  4
    #     # v: A  B  C     D
    #     # h:    a     b  c
    #     #
    #     # Expected:
    #     # 0: 'A a B'
    #     # 1: 'B _ C'
    #     # 2: 'C b C'
    #     # 3: 'C c D'
    #     # NB: this started as a regression test for issue 261, where missing values weren't filled
    #     vertical = pandas.Series(['A', 'B', 'C', 'D'], index=[0, 1, 2, 4])
    #     horizontal = pandas.Series(['a', 'b', 'c'], index=[0, 2, 3])
    #     in_val = pandas.DataFrame([vertical, horizontal],
    #                               index=[['vert', 'horiz'], ['0,1', '1']]).T
    #     setts = {'n': 2, 'mark singles': False, 'horizontal': [('horiz', '1')],
    #              'vertical': [('vert', '0,1')]}
    #     expected = pandas.DataFrame([pandas.Series(['A a B', 'B _ C', 'C b C', 'C c D'])],
    #                                 index=[['new_ngram.NewNGramIndexer'], ['0,1 1']]).T

    #     actual = new_ngram.NewNGramIndexer(in_val, setts).run()

    #     self.assertSequenceEqual(list(expected.columns), list(actual.columns))
    #     self.assertEqual(len(expected), len(actual))
    #     for col_name in expected.columns:
    #         self.assertSequenceEqual(list(expected[col_name].index), list(actual[col_name].index))
    #         self.assertSequenceEqual(list(expected[col_name].values), list(actual[col_name].values))

    def test_ngram_20(self):
        """
        Ensure that events in other voices don't erroneously cause events in the voices-under-study.

        Regression test for GH#334.
        """
        # NB: it looks like this:
        #
        #    0 | .5 | 1 | .5 | 2 | .5 | 3  <-- offset/index
        # A: A |    | B |    | C |    | D  <-- included voice
        # B: Q | W  |   |    | E | R  |    <-- included voice
        # C:   | Z  |   | X  | V | N  |    <-- not included
        #
        # NOTE: for this to be a sufficient test, there must be an offset like 0.5, where one part
        #       has an event but the other has NaN, *and* an offset like 1.5, where both included
        #       parts do not have events, but the not-included part does.
        mi = mi_maker((V_IND,), ('0,1', '0,2', '0,3'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D'], index=[0.0, 1.0, 2.0, 3.0]),
                             pandas.Series(['Q', 'W', 'E', 'R'], index=[0.0, 0.5, 2.0, 2.5]),
                             pandas.Series(['Z', 'X', 'V', 'N'], index=[0.5, 1.5, 2.0, 2.5])], mi)
        setts = {'n': 2, 'vertical': [('0,1', '0,2',)]}
        expected = ['[A Q] [A W]', '[A W] [B W]', '[B W] [C E]', '[C E] [C R]', '[C R] [D R]']
        expected = pandas.DataFrame([pandas.Series(expected, index=[0.0, 0.5, 1.0, 2.0, 2.5])],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2']]).T

        actual = new_ngram.NewNGramIndexer([vertical], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_21a(self):
        """tests that horizontal setting is set correctly when 'highest' is passed and there
        are multiple vertical voice pairs lumped in the same group. NB this is like tracking
        the highest voice of 'soprano-continuo' sonorities."""
        mi = mi_maker((V_IND,), ('0,1', '0,2', '0,3'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D', 'E']),
                             pandas.Series(['Z', 'X', 'Y', 'W', 'V']),
                             pandas.Series(['Q', 'R', 'S', 'T', 'U'])], mi) 
        mi = mi_maker((H_IND,), ('0', '1', '2', '3'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c', 'd']),
                               pandas.Series(['a2', 'b2', 'c2', 'd2']),
                               pandas.Series(['z', 'x', 'y', 'w']),
                               pandas.Series(['z2', 'x2', 'y2', 'w2'])], mi)
        setts = {'n': 2, 'horizontal': 'highest', 'vertical': [('0,1', '0,2', '0,3')], 'brackets': True,}
        expected = pandas.DataFrame([pandas.Series(['[A Z Q] (a) [B X R]', '[B X R] (b) [C Y S]',
                                                    '[C Y S] (c) [D W T]', '[D W T] (d) [E V U]'], )],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,1 0,2 0,3 : 0']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_21b(self):
        """tests that horizontal setting is set correctly when 'lowest' is passed and there
        are multiple vertical voice pairs lumped in the same group. NB this is like tracking
        the lowest voice of figured-bass sonorities."""
        mi = mi_maker((V_IND,), ('0,3', '1,3', '2,3'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D', 'E']),
                             pandas.Series(['Z', 'X', 'Y', 'W', 'V']),
                             pandas.Series(['Q', 'R', 'S', 'T', 'U'])], mi) 
        mi = mi_maker((H_IND,), ('0', '1', '2', '3'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c', 'd']),
                               pandas.Series(['a2', 'b2', 'c2', 'd2']),
                               pandas.Series(['z', 'x', 'y', 'w']),
                               pandas.Series(['z2', 'x2', 'y2', 'w2'])], mi)
        setts = {'n': 2, 'horizontal': 'lowest', 'vertical': [('0,3', '1,3', '2,3')], 'brackets': True,}
        expected = pandas.DataFrame([pandas.Series(['[A Z Q] (z2) [B X R]', '[B X R] (x2) [C Y S]',
                                                    '[C Y S] (y2) [D W T]', '[D W T] (w2) [E V U]']) ],
                                    index=[['new_ngram.NewNGramIndexer'], ['0,3 1,3 2,3 : 3']]).T

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_21c(self):
        """tests that horizontal setting is set correctly when 'lowest' is passed and there
        are multiple vertical voice pairs. Also outputs results into multiple columns."""
        mi = mi_maker((V_IND,), ('0,1', '0,2', '1,2'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D', 'E']),
                             pandas.Series(['Z', 'X', 'Y', 'W', 'V']),
                             pandas.Series(['Q', 'R', 'S', 'T', 'U'])], mi) 
        mi = mi_maker((H_IND,), ('0', '1', '2'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c', 'd']),
                               pandas.Series(['a2', 'b2', 'c2', 'd2']),
                               pandas.Series(['z', 'x', 'y', 'w'])], mi)
        setts = {'n': 2, 'horizontal': 'lowest', 'vertical': [('0,1',), ('0,2',), ('1,2',)], 'brackets': False,}
        mi = mi_maker(['new_ngram.NewNGramIndexer'], ['0,1 : 1', '0,2 : 2', '1,2 : 2'])
        expected = df_maker([pandas.Series(['A a2 B', 'B b2 C', 'C c2 D', 'D d2 E']),
                             pandas.Series(['Z z X', 'X x Y', 'Y y W', 'W w V']),
                             pandas.Series(['Q z R', 'R x S', 'S y T', 'T w U']) ], mi)

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

    def test_ngram_21d(self):
        """tests that horizontal setting is set correctly when 'highest' is passed and there
        are multiple vertical voice pairs. Also outputs results into multiple columns."""
        mi = mi_maker((V_IND,), ('0,1', '0,2', '1,2'))
        vertical = df_maker([pandas.Series(['A', 'B', 'C', 'D', 'E']),
                             pandas.Series(['Z', 'X', 'Y', 'W', 'V']),
                             pandas.Series(['Q', 'R', 'S', 'T', 'U'])], mi) 
        mi = mi_maker((H_IND,), ('0', '1', '2'))
        horizontal = df_maker([pandas.Series(['a', 'b', 'c', 'd']),
                               pandas.Series(['a2', 'b2', 'c2', 'd2']),
                               pandas.Series(['z', 'x', 'y', 'w']) ], mi)
        setts = {'n': 2, 'horizontal': 'highest', 'vertical': [('0,1',), ('0,2',), ('1,2',)], 'brackets': True,}
        mi = mi_maker(['new_ngram.NewNGramIndexer'], ['0,1 : 0', '0,2 : 0', '1,2 : 1'])
        expected = df_maker([pandas.Series(['[A] (a) [B]', '[B] (b) [C]', '[C] (c) [D]', '[D] (d) [E]']),
                             pandas.Series(['[Z] (a) [X]', '[X] (b) [Y]', '[Y] (c) [W]', '[W] (d) [V]']),
                             pandas.Series(['[Q] (a2) [R]', '[R] (b2) [S]', '[S] (c2) [T]', '[T] (d2) [U]']) ], mi)

        actual = new_ngram.NewNGramIndexer([vertical, horizontal], setts).run()

        self.assertTrue(actual.equals(expected))

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
NEW_NGRAM_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestNewNGramIndexer)
