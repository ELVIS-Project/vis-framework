#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_workflow_integration.py
# Purpose:                Integration tests for the WorkflowManager
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
"""
Integration tests for the WorkflowManager
"""

import os
from unittest import TestCase, TestLoader
import pandas
from vis.workflow import WorkflowManager
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import noterest, interval

# find pathname of the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]

# pylint: disable=R0904
# pylint: disable=C0111
class IntervalsTests(TestCase):
    """Integration tests for the 'intervals' experiment."""

    # EXPECTED_1 is the result of the "intervals" experiment on bwv77 with "[[0, 1]]" as the voice
    # pairs; note that I didn't verify by counting... this just ensures a valid value comes out
    EXPECTED_1 = pandas.Series({'3': 32, '4': 22, '5': 18, '6': 16, '7': 4, '2': 3, '8': 2})
    # EXPECTED_2 is the result of the "intervals" experiment on bwv77 with "all pairs" as the voice
    # pairs; note that I didn't verify by counting
    EXPECTED_2 = pandas.Series({'3': 91, '6': 90, '5': 86, '10': 81, '4': 62, '8': 53,
                                '12': 37, '7': 26, '11': 17, '13': 16, '15': 12, '9': 8,
                                '1': 8, '2': 8, '14': 7, '17': 5, '-2': 3, '-3': 2, '16': 1})
    # EXPECTED_3 is the result of "intervals" experiment on madrigal51 with "all pairs" as the
    # voice pairs and not including rests; note that I didn't verify this by counting
    EXPECTED_3 = pandas.Series({'3': 219, '8': 208, '10': 193, '5': 192, '6': 155, '1': 154,
                                '4': 125, '7': 124, '9': 122, '11': 96, '12': 96, '2': 66,
                                '-3': 58, '15': 47, '13': 46, '14': 40, '-2': 37, '-4': 31,
                                '-5': 29, '16': 23, '-6': 22, '17': 14, '-8': 10, '19': 9, '-7': 8,
                                '18': 4, '-9': 3, '20': 3, '-12': 3, '22': 1, '-10': 1})
    # EXPECTED_4 is the result of "intervals" experiment on madrigal51 with "all pairs" as the
    # voice pairs and including rests; note that I didn't verify this by counting
    # NB: only difference between this and EXPECTED_3 should be the 'Rest' entry
    EXPECTED_4 = pandas.Series({'Rest': 1228, '3': 219, '8': 208, '10': 193, '5': 192, '6': 155,
                                '1': 154, '4': 125, '7': 124, '9': 122, '11': 96, '12': 96,
                                '2': 66, '-3': 58, '15': 47, '13': 46, '14': 40, '-2': 37,
                                '-4': 31, '-5': 29, '16': 23, '-6': 22, '17': 14, '-8': 10,
                                '19': 9, '-7': 8, '18': 4, '-9': 3, '20': 3, '-12': 3, '22': 1,
                                '-10': 1})

    def assertDataFramesEqual(self, exp, act):  # pylint: disable=invalid-name
        """Ensure that two DataFrame objects, ``exp`` and ``act``, are equal."""
        self.assertSequenceEqual(list(exp.columns), list(act.columns))
        for col_name in exp.columns:
            for loc_val in exp[col_name].index:
                self.assertTrue(loc_val in act.index)
                if exp[col_name].loc[loc_val] != act[col_name].loc[loc_val]:
                    msg = '"{}" is "{}" but we expected "{}"'
                    raise AssertionError(msg.format(loc_val,
                                                    act[col_name].loc[loc_val],
                                                    exp[col_name].loc[loc_val]))

    def test_intervals_1(self):
        """test the two highest voices of bwv77"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0, 1]]')
        actual = test_wm.run('intervals')
        self.assertEqual(1, len(actual.columns))
        actual = actual['aggregator.ColumnAggregator']
        exp_ind = list(IntervalsTests.EXPECTED_1.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(IntervalsTests.EXPECTED_1[ind_item], actual[ind_item])

    def test_intervals_2(self):
        """test all combinations of bwv77"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        actual = test_wm.run('intervals')
        self.assertEqual(1, len(actual.columns))
        actual = actual['aggregator.ColumnAggregator']
        exp_ind = list(IntervalsTests.EXPECTED_2.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(IntervalsTests.EXPECTED_2[ind_item], actual[ind_item])

    def test_intervals_3(self):
        """test all combinations of madrigal51 without rests"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'madrigal51.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        test_wm.settings(None, 'include rests', False)
        actual = test_wm.run('intervals')
        self.assertEqual(1, len(actual.columns))
        actual = actual['aggregator.ColumnAggregator']
        exp_ind = list(IntervalsTests.EXPECTED_3.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(IntervalsTests.EXPECTED_3[ind_item], actual[ind_item])

    def test_intervals_4(self):
        """test all combinations of madrigal51 with rests"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'madrigal51.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        test_wm.settings(None, 'include rests', True)
        actual = test_wm.run('intervals')
        self.assertEqual(1, len(actual.columns))
        actual = actual['aggregator.ColumnAggregator']
        exp_ind = list(IntervalsTests.EXPECTED_4.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(IntervalsTests.EXPECTED_4[ind_item], actual[ind_item])

    def test_intervals_5(self):
        """test all combinations of vis_Test_Piece"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'vis_Test_Piece.xml')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        test_wm.settings(None, 'include rests', True)
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'corpus', 'test_intervals_5.csv'),
                                   index_col=0)
        actual = test_wm.run('intervals')
        self.assertEqual(1, len(actual.columns))
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))
        for col_name in expected.columns:
            self.assertEqual(len(expected[col_name]), len(actual[col_name]))
            for each_interval in expected[col_name].index:
                # NOTE: for whatever reason, the "expected" file always imports with an Int64Index,
                #       so .loc() won't find things properly unless we give the int64 index to the
                #       expected and the str index to the actual
                self.assertEqual(expected[col_name].loc[each_interval],
                                 actual[col_name].loc[str(each_interval)])

    def test_intervals_6(self):  # TODO: add a frequency-counted test
        """test Soprano and Alto of bwv77; with quality; not counting frequency"""
        # NB: the "expected" was hand-counted
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'SA_intervals.csv'),
                                   comment='#', index_col=0, header=[0, 1], quotechar="'")

        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0, 1]]')
        test_wm.settings(None, 'count frequency', False)
        test_wm.settings(None, 'interval quality', True)
        actual = test_wm.run('intervals')

        self.assertEqual(1, len(actual))
        actual = actual[0].dropna()
        self.assertDataFramesEqual(expected, actual)

    def test_intervals_7(self):  # TODO: add a frequency-counted test
        """same as test_6 *but* no quality"""
        # NB: the "expected" was hand-counted
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'SA_intervals_nq.csv'),
                                   comment='#', index_col=0, header=[0, 1], quotechar="'", dtype='object')

        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0, 1]]')
        test_wm.settings(None, 'count frequency', False)
        test_wm.settings(None, 'interval quality', False)
        actual = test_wm.run('intervals')

        self.assertEqual(1, len(actual))
        actual = actual[0].dropna()
        self.assertDataFramesEqual(expected, actual)

    def test_intervals_8(self):
        """test horizontal of Alto of bwv77; with quality; not counting frequency"""
        # NB: the "expected" was hand-counted
        # TODO: change this into a WorkflowManager-using test when the "horizontal intervals" experiment is ready
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'A_horiz_ints.csv'),
                                   comment='#', index_col=0, header=[0, 1], quotechar="'")
        setts = {'quality': True, 'simple or compound': 'compound', 'horiz_attach_later': True}

        test_ip = IndexedPiece(os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl'))
        actual = test_ip.get_data([noterest.NoteRestIndexer, interval.HorizontalIntervalIndexer],
                                  setts)

        actual = actual['interval.HorizontalIntervalIndexer']
        self.assertEqual(4, len(actual.columns))
        actual = pandas.DataFrame({('interval.HorizontalIntervalIndexer', '1'): actual['1'].dropna()})
        self.assertDataFramesEqual(expected, actual)

    def test_intervals_9(self):
        """same as test_8 *but* no quality"""
        # NB: the "expected" was hand-counted
        # TODO: change this into a WorkflowManager-using test when the "horizontal intervals" experiment is ready
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'A_horiz_ints_nq.csv'),
                                   comment='#', index_col=0, header=[0, 1], quotechar="'", dtype='object')
        setts = {'quality': False, 'simple or compound': 'compound', 'horiz_attach_later': True}

        test_ip = IndexedPiece(os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl'))
        actual = test_ip.get_data([noterest.NoteRestIndexer, interval.HorizontalIntervalIndexer],
                                  setts)

        actual = actual['interval.HorizontalIntervalIndexer']
        self.assertEqual(4, len(actual.columns))
        actual = pandas.DataFrame({('interval.HorizontalIntervalIndexer', '1'): actual['1'].dropna()})
        self.assertDataFramesEqual(expected, actual)


class NGramsTests(TestCase):
    """Integration tests or the 'interval n-grams' experiment."""

    # EXPECTED_1 is the result of the "interval n-grams" experiment with "[[0, 1]]" as the voice
    # pairs; note that I didn't verify by counting... this just ensures a valid value comes out

    # EXPECTED_2 is the result of the "interval n-grams" experiment with "all pairs" as the voice
    # pairs; note that I didn't verify by counting... this just ensures a valid value comes out

    # EXPECTED_3 is the result of the "interval n-grams" experiment with "all" as the voice
    # pairs; note that I didn't verify by counting... this just ensures a valid value comes out

    # EXPECTED_4 is the result of "interval n-grams" on BWV2 with "all" as the voice pairs, and
    # compound intervals portrayed as their single-octave equivalents; note that I didn't verify
    # by counting... this just ensures a valid value comes out

    # EXPECTED_5 is the result of "interval n-grams" on madrigal51 with "all" as the voice pairs,
    # and no rests; note that I didn't verify by counting

    # EXPECTED_6 is the result of "interval n-grams" on madrigal51 with "all" as the voice pairs,
    # including rests; note that I didn't verify by counting

    # EXPECTED_7a is the result of "interval n-grams" on vis_Test_Piece.xml with all two-part
    # combinations of 2-grams. I counted it by hand!
    EXPECTED_7a = pandas.Series({'4 1 5': 1, '5 1 4': 1, '6 2 6': 1, '6 -2 6': 1, '8 -2 10': 1,
                                '10 2 8': 1, '3 2 2': 1, '2 -2 3': 1, '5 -2 6': 1, '6 2 5': 1,
                                '3 -2 5': 1, '5 2 3': 1})
    EXPECTED_7a = pandas.DataFrame({'aggregator.ColumnAggregator': EXPECTED_7a})

    # EXPECTED_7b is simply the "expected" for 7a, but doubled
    EXPECTED_7b = pandas.Series({'4 1 5': 2, '5 1 4': 2, '6 2 6': 2, '6 -2 6': 2, '8 -2 10': 2,
                                '10 2 8': 2, '3 2 2': 2, '2 -2 3': 2, '5 -2 6': 2, '6 2 5': 2,
                                '3 -2 5': 2, '5 2 3': 2})
    EXPECTED_7b = pandas.DataFrame({'aggregator.ColumnAggregator': EXPECTED_7b})

    # The expected values for tests 9a-c consist of 2-gram analyses of the soprano and alto in
    # bwv77 with the settings as described in each test. These results are stored in csv files in
    # ~/vis/tests/corpus/

    def assertDataFramesEqual(self, exp, act):  # pylint: disable=invalid-name
        """Ensure that two DataFrame objects, ``exp`` and ``act``, are equal."""
        self.assertSequenceEqual(list(exp.columns), list(act.columns))
        for col_name in exp.columns:
            for loc_val in exp[col_name].index:
                self.assertTrue(loc_val in act.index)
                if exp[col_name].loc[loc_val] != act[col_name].loc[loc_val]:
                    msg = '"{}" is {} but we expected {}'
                    raise AssertionError(msg.format(loc_val,
                                                    act[col_name].loc[loc_val],
                                                    exp[col_name].loc[loc_val]))

    # NB: test_ngrams_1() was replaced by the hand-counted suite of "bwv77.mxl" tests

    def test_ngrams_2(self):
        """test all two-part combinations of bwv77; 5-grams"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        test_wm.settings(0, 'n', 5)
        test_wm.settings(0, 'continuer', '_')
        expected = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'test_ngrams_2.pickle'))
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_3(self):
        """test all voices of bwv77; 1-grams"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(0, 'n', 1)
        expected = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'test_ngrams_3.pickle'))
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_4(self):
        """test all voices of bwv2; 3-grams; simple intervals"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv2.xml')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(0, 'n', 3)
        test_wm.settings(None, 'simple intervals', True)
        test_wm.settings(0, 'continuer', '_')
        expected = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'test_ngrams_4.pickle'))
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_5(self):
        """test madrigal51 with all-voice 2-grams and no rests (the default setting)"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'madrigal51.mxl')])
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(None, 'include rests', False)
        test_wm.load('pieces')
        test_wm.settings(0, 'continuer', '_')
        expected = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'test_ngrams_5.pickle'))
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_6(self):
        """test madrigal51 with all-voice 2-grams and rests"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'madrigal51.mxl')])
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(None, 'include rests', True)
        test_wm.load('pieces')
        test_wm.settings(0, 'continuer', '_')
        expected = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'test_ngrams_6.pickle'))
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_7a(self):
        """test all two-part combinations of the test piece; 2-grams"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'vis_Test_Piece.xml')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        test_wm.settings(0, 'n', 2)
        expected = NGramsTests.EXPECTED_7a
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_7b(self):
        """
        test_ngrams_7a() but with two pieces (both 'vis_Test_Piece.xml')

        This is a regression test for issue #335
        """
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'vis_Test_Piece.xml'),
                                   os.path.join(VIS_PATH, 'tests', 'corpus', 'vis_Test_Piece.xml')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        test_wm.settings(0, 'n', 2)
        test_wm.settings(1, 'voice combinations', 'all pairs')
        test_wm.settings(1, 'n', 2)
        expected = NGramsTests.EXPECTED_7b
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_8(self):
        """test_ngrams_7a *but* with part combinations specified rather than 'all pairs'"""
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'vis_Test_Piece.xml')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]')
        test_wm.settings(0, 'n', 2)
        expected = NGramsTests.EXPECTED_7a
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_9a(self):
        """
        2-grams between S&A in bwv77. Not counting frequency. Quality.

        Regression test for: https://github.com/ELVIS-Project/vis/issues/305 which means we *must*
        use an offset interval.
        """
        # NB: these results were counted by hand
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'SA_2grams_offset.csv'),
                                   comment='#', index_col=0, header=[0, 1], quotechar="'")
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0,1]]')
        test_wm.settings(0, 'n', 2)
        test_wm.settings(None, 'count frequency', False)
        test_wm.settings(None, 'interval quality', True)
        test_wm.settings(None, 'offset interval', 1.0)
        actual = test_wm.run('interval n-grams')
        self.assertEqual(1, len(actual))
        self.assertDataFramesEqual(expected, actual[0])

    def test_ngrams_9b(self):
        """
        test_ngrams_9a() but counting frequency.

        Regression test for: https://github.com/ELVIS-Project/vis/issues/305 which means we *must*
        use an offset interval.
        """
        # NB: these results were counted by hand
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'SA_2grams_offset_freq.csv'),
                                   comment='#', index_col=0, quotechar="'")
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0,1]]')
        test_wm.settings(0, 'n', 2)
        test_wm.settings(None, 'count frequency', True)
        test_wm.settings(None, 'interval quality', True)
        test_wm.settings(None, 'offset interval', 1.0)
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_9c(self):
        """
        2-grams between S&A in bwv77. Not counting frequency. Quality. No offset interval.
        """
        # NB: these results were counted by hand
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'SA_2grams.csv'),
                                   comment='#', index_col=0, header=[0, 1], quotechar="'")
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0,1]]')
        test_wm.settings(0, 'n', 2)
        test_wm.settings(None, 'count frequency', False)
        test_wm.settings(None, 'interval quality', True)
        actual = test_wm.run('interval n-grams')
        self.assertEqual(1, len(actual))
        self.assertDataFramesEqual(expected, actual[0])

    def test_ngrams_9d(self):
        """
        test_ngrams_9c() but counting frequency.
        """
        # NB: these results were counted by hand
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'SA_2grams_freq.csv'),
                                   comment='#', index_col=0, quotechar="'")
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0,1]]')
        test_wm.settings(0, 'n', 2)
        test_wm.settings(None, 'count frequency', True)
        test_wm.settings(None, 'interval quality', True)
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_9e(self):
        """
        2-grams between S&A in bwv77. Not counting frequency. No quality. No offset interval.
        """
        # NB: these results were counted by hand
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'SA_2grams_nq.csv'),
                                   comment='#', index_col=0, header=[0, 1], quotechar="'")
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0,1]]')
        test_wm.settings(0, 'n', 2)
        test_wm.settings(None, 'count frequency', False)
        test_wm.settings(None, 'interval quality', False)
        actual = test_wm.run('interval n-grams')
        self.assertEqual(1, len(actual))
        self.assertDataFramesEqual(expected, actual[0])

    def test_ngrams_9f(self):
        """
        test_ngrams_9e() but counting frequency.
        """
        # NB: these results were counted by hand
        expected = pandas.read_csv(os.path.join(VIS_PATH, 'tests', 'expecteds', 'bwv77', 'SA_2grams_nq_freq.csv'),
                                   comment='#', index_col=0, quotechar="'")
        test_wm = WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0,1]]')
        test_wm.settings(0, 'n', 2)
        test_wm.settings(None, 'count frequency', True)
        test_wm.settings(None, 'interval quality', False)
        actual = test_wm.run('interval n-grams')
        self.assertDataFramesEqual(expected, actual)

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INTERVALS_TESTS = TestLoader().loadTestsFromTestCase(IntervalsTests)
NGRAMS_TESTS = TestLoader().loadTestsFromTestCase(NGramsTests)
