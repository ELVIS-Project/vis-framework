#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               other_tests/test_workflow_integration.py
# Purpose:                Integration tests for the WorkflowManager
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
"""
Integration tests for the WorkflowManager
"""

from unittest import TestCase, TestLoader
import pandas
from vis.workflow import WorkflowManager


# pylint: disable=R0904
# pylint: disable=C0111
class IntervalsTests(TestCase):
    # EXPECTED_1 is the result of the "intervals" experiment with "[[0, 1]]" as the voice pairs;
    # note that I didn't verify by counting... this just ensures a valid value comes out
    EXPECTED_1 = pandas.Series({u'3': 32, u'4': 22, u'5': 18, u'6': 16, u'7': 4, u'2': 3, u'8': 2})
    # EXPECTED_2 is the result of the "intervals" experiment with "all pairs" as the voice pairs;
    # note that I didn't verify by counting... this just ensures a valid value comes out
    EXPECTED_2 = pandas.Series({u'3': 91, u'6': 90, u'5': 86, u'10': 81, u'4': 62, u'8': 53,
                                u'12': 37, u'7': 26, u'11': 17, u'13': 16, u'15': 12, u'9': 8,
                                u'1': 8, u'2': 8, u'14': 7, u'17': 5, u'-2': 3, u'-3': 2, u'16': 1})

    def test_intervals_1(self):
        # test the two highest voices of bwv77
        test_wm = WorkflowManager(['test_corpus/bwv77.mxl'])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0, 1]]')
        actual = test_wm.run('intervals')
        exp_ind = list(IntervalsTests.EXPECTED_1.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(IntervalsTests.EXPECTED_1[ind_item], actual[ind_item])

    def test_intervals_2(self):
        # test all combinations of bwv77
        test_wm = WorkflowManager(['test_corpus/bwv77.mxl'])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        actual = test_wm.run('intervals')
        exp_ind = list(IntervalsTests.EXPECTED_2.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(IntervalsTests.EXPECTED_2[ind_item], actual[ind_item])


class NGramsTests(TestCase):
    # EXPECTED_1 is the result of the "interval n-grams" experiment with "[[0, 1]]" as the voice
    # pairs; note that I didn't verify by counting... this just ensures a valid value comes out
    EXPECTED_1 = pandas.Series({'3 -2 3': 9, '3 -3 4': 7, '4 -2 5': 7, '5 1 4': 6, '6 -2 6': 6,
                                '3 2 3': 5, '6 2 5': 5, '5 2 3': 4, '4 _ 5': 3, '3 1 6': 3,
                                '3 _ 2': 3, '5 4 3': 3, '4 1 3': 2, '4 1 4': 2, '4 _ 3': 2,
                                '3 1 4': 2, '3 4 3': 2, '2 -2 3': 2, '6 -2 7': 2, '7 4 3': 2,
                                '5 1 6': 2, '6 -2 8': 1, '2 -2 4': 1, '3 -2 4': 1, '7 2 6': 1,
                                '7 1 6': 1, '6 3 5': 1, '6 2 6': 1, '5 1 5': 1, '8 2 7': 1,
                                '5 2 4': 1, '4 -2 6': 1, '4 -3 5': 1, '5 1 8': 1, '4 2 3': 1,
                                '4 4 4': 1, '4 6 6': 1, '8 _ 7': 1})
    # EXPECTED_2 is the result of the "interval n-grams" experiment with "all pairs" as the voice
    # pairs; note that I didn't verify by counting... this just ensures a valid value comes out
    # NB: just the first ten, because seriously.
    EXPECTED_2 = pandas.Series({'5 _ 6 -2 8 -2 5 -4 8': 2, '3 -4 5 4 1 -2 3 -2 5': 2,
                                '5 4 1 -2 3 -2 5 _ 6': 2, '3 -2 5 _ 6 -2 8 -2 5': 2,
                                '5 -4 8 _ 7 4 3 1 3': 2, '5 -4 8 -2 10 -2 12 6 5': 2,
                                '5 -3 10 2 8 4 3 -4 5': 2, '5 -2 8 4 5 -4 8 -2 10': 2,
                                '12 6 5 -3 10 2 8 4 3': 2, '6 -2 8 -2 5 -4 8 _ 7': 2,})
    # EXPECTED_3 is the result of the "interval n-grams" experiment with "all" as the voice
    # pairs; note that I didn't verify by counting... this just ensures a valid value comes out
    # NB: just the first ten, because seriously.
    EXPECTED_3 = pandas.Series({'[12 10 8]': 11, '[10 8 5]': 10, '[8 5 3]': 9, '[10 5 1]': 5,
                                '[15 10 5]': 5, '[12 7 3]': 3, '[17 15 12]': 3, '[12 10 7]': 3,
                                '[12 8 3]': 3, '[13 10 6]': 3})
    # EXPECTED_4 is the result of "interval n-grams" on BWV2 with "all" as the voice pairs, and
    # compound intervals portrayed as their single-octave equivalents; note that I didn't verify
    # by counting... this just ensures a valid value comes out
    # NB: just the first ten, because seriously.
    EXPECTED_4 = pandas.Series({'[8 6 3] 2 [6 6 3]': 1, '[3 5 3] _ [3 6 4]': 1,
                                '[4 2 6] -2 [6 3 8]': 1, '[3 8 5] _ [3 7 5]': 1,
                                '[3 8 5] 5 [5 3 1]': 1, '[3 8 5] 2 [8 6 3]': 1,
                                '[3 8 5] -2 [4 4 6]': 1, '[3 7 5] 2 [3 5 3]': 1,
                                '[3 7 5] 2 [1 5 3]': 1, '[3 6 5] 2 [1 6 3]': 1})
    # EXPECTED_5 is the result of "interval n-grams" on madrigal51 with "all" as the voice pairs,
    # and no rests; note that I didn't verify by counting
    # NB: just the first ten
    EXPECTED_5 = pandas.Series({'[15 13 6 10 1] 3 [12 10 5 8 1]': 2,
                                '[9 8 5 1 -4] _ [9 7 5 1 -4]': 1,
                                '[13 10 3 8 1] 1 [12 10 3 8 1]': 1,
                                '[15 15 10 12 1] 8 [8 5 1 3 1]': 1,
                                '[15 11 5 1 4] _ [15 11 5 1 4]': 1,
                                '[15 11 5 1 4] _ [14 10 5 1 4]': 1,
                                '[15 10 5 1 4] _ [15 11 5 1 4]': 1,
                                '[14 5 7 6 1] -2 [15 6 8 7 1]': 1,
                                '[14 5 4 5 1] _ [14 5 3 5 1]': 1,
                                '[14 5 3 5 1] -5 [17 12 8 8 1]': 1})
    # EXPECTED_6 is the result of "interval n-grams" on madrigal51 with "all" as the voice pairs,
    # including rests; note that I didn't verify by counting
    # NB: just the first ten
    EXPECTED_6 = pandas.Series({'[Rest Rest Rest Rest Rest] _ [Rest Rest Rest Rest Rest]': 4,
                                '[Rest Rest 1 3 Rest] 1 [Rest Rest 1 3 Rest]': 3,
                                '[Rest Rest 1 8 Rest] 4 [Rest Rest 1 5 Rest]': 2,
                                '[Rest Rest 1 5 Rest] -3 [Rest Rest 1 6 Rest]': 2,
                                '[Rest Rest 1 5 Rest] 1 [Rest Rest 1 5 Rest]': 2,
                                '[15 13 6 10 1] 3 [12 10 5 8 1]': 2,
                                '[10 10 5 Rest Rest] _ [10 11 8 2 Rest]': 1,
                                '[15 11 5 1 4] _ [15 11 5 1 4]': 1,
                                '[15 11 5 8 Rest] _ [14 11 5 8 Rest]': 1,
                                '[15 11 Rest 4 Rest] _ [14 10 5 4 Rest]': 1})

    def test_ngrams_1(self):
        # test the two highest voices of bwv77; 2-grams
        test_wm = WorkflowManager(['test_corpus/bwv77.mxl'])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0, 1]]')
        test_wm.settings(0, 'n', 2)
        actual = test_wm.run('interval n-grams')
        exp_ind = list(NGramsTests.EXPECTED_1.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(NGramsTests.EXPECTED_1[ind_item], actual[ind_item])

    def test_ngrams_2(self):
        # test all combinations of bwv77; 5-grams
        test_wm = WorkflowManager(['test_corpus/bwv77.mxl'])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all pairs')
        test_wm.settings(0, 'n', 5)
        actual = test_wm.run('interval n-grams')[:10]
        exp_ind = list(NGramsTests.EXPECTED_2.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(NGramsTests.EXPECTED_2[ind_item], actual[ind_item])

    def test_ngrams_3(self):
        # test all voices of bwv77; 1-grams
        test_wm = WorkflowManager(['test_corpus/bwv77.mxl'])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(0, 'n', 1)
        actual = test_wm.run('interval n-grams')
        exp_ind = list(NGramsTests.EXPECTED_3.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(NGramsTests.EXPECTED_3[ind_item], actual[ind_item])

    def test_ngrams_4(self):
        # test all voices of bwv2; 3-grams; simple intervals
        test_wm = WorkflowManager(['test_corpus/bwv2.xml'])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(0, 'n', 2)
        test_wm.settings(None, 'simple intervals', True)
        actual = test_wm.run('interval n-grams')[:10]
        exp_ind = list(NGramsTests.EXPECTED_4.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(NGramsTests.EXPECTED_4[ind_item], actual[ind_item])

    def test_ngrams_5(self):
        # test madrigal51 with all-voice 2-grams and no rests (the default setting)
        test_wm = WorkflowManager(['test_corpus/madrigal51.mxl'])
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(None, 'include rests', False)
        test_wm.load('pieces')
        actual = test_wm.run('interval n-grams')
        exp_ind = list(NGramsTests.EXPECTED_5.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(NGramsTests.EXPECTED_5[ind_item], actual[ind_item])

    def test_ngrams_6(self):
        # test madrigal51 with all-voice 2-grams and rests
        test_wm = WorkflowManager(['test_corpus/madrigal51.mxl'])
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(None, 'include rests', True)
        test_wm.load('pieces')
        actual = test_wm.run('interval n-grams')
        exp_ind = list(NGramsTests.EXPECTED_6.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(NGramsTests.EXPECTED_6[ind_item], actual[ind_item])


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INTERVALS_TESTS = TestLoader().loadTestsFromTestCase(IntervalsTests)
NGRAMS_TESTS = TestLoader().loadTestsFromTestCase(NGramsTests)
