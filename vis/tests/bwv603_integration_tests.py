#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/bwv603_integration_tests.py
# Purpose:                Integration tests with the "bwv603.xml" file.
#
# Copyright (C) 2013, 2014 Christopher Antila, Ryan Bannon
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
Integration tests with the "bwv603.xml" file.
"""

import os
from unittest import TestCase, TestLoader
import pandas
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import noterest, interval, ngram, new_ngram
from vis.analyzers.experimenters import frequency
from vis import workflow

# get the path to the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]


# pylint: disable=R0904
# pylint: disable=C0111
class AllVoiceIntervalNGrams(TestCase):
    twograms = [(0, '[15 12 10] 8 [8 5 3]'),
                (1, '[8 5 3] -2 [9 6 4]'),
                (2, '[9 6 4] -2 [10 10 6]'),
                (3, '[10 10 6] 2 [10 8 5]'),
                (4, '[10 8 5] -4 [13 11 8]'),
                (5, '[13 11 8] 3 [11 9 6]'),
                (6, '[11 9 6] -2 [13 10 6]'),
                (7, '[13 10 6] -3 [14 12 10]'),
                (8, '[14 12 10] 4 [10 8 5]'),
                (9, '[10 8 5] -4 [12 10 8]'),
                (10, '[12 10 8] 1 [15 12 10]'),
                (13, '[15 12 10] 8 [8 5 3]'),
                (14, '[8 5 3] -2 [10 6 4]'),
                (15, '[10 6 4] -2 [10 8 5]'),
                (16, '[10 8 5] -3 [12 10 6]'),
                (17, '[12 10 6] 2 [10 8 5]'),
                (18, '[10 8 5] -5 [15 12 10]'),
                (19, '[15 12 10] 8 [8 5 3]'),
                (21, '[8 5 3] -3 [10 8 5]'),
                (22, '[10 8 5] -3 [12 10 6]'),
                (23, '[12 10 6] -3 [14 10 8]'),
                (24, '[14 10 8] 4 [10 8 5]'),
                (25, '[10 8 5] -3 [12 10 8]'),
                (26, '[12 10 8] -3 [13 12 10]'),
                (27, '[13 12 10] 2 [12 11 8]'),
                (28, '[12 11 8] 1 [13 10 6]'),
                (29, '[13 10 6] 2 [10 8 5]'),
                (30, '[10 8 5] -5 [15 12 10]'),
                (31, '[15 12 10] 6 [10 6 3]'),
                (33, '[10 6 3] 1 [9 6 4]'),
                (34, '[9 6 4] -2 [10 8 6]'),
                (35, '[10 8 6] 2 [10 6 3]'),
                (36, '[10 6 3] 2 [10 5 1]'),
                (37, '[10 5 1] -2 [11 6 4]'),
                (38, '[11 6 4] 2 [10 7 5]'),
                (39, '[10 7 5] 2 [10 5 3]'),
                (40, '[10 5 3] -5 [14 10 8]'),
                (41, '[14 10 8] 2 [12 10 7]'),
                (42, '[12 10 7] 2 [10 9 5]'),
                (43, '[10 9 5] -3 [12 10 7]'),
                (44, '[12 10 7] 2 [10 8 5]'),
                (45, '[10 8 5] -5 [15 12 10]')]

    new_two_grams = [(0, '[15 12 10] (8) [8 5 3]'),
                    (1, '[8 5 3] (-2) [9 6 4]'),
                    (2, '[9 6 4] (-2) [10 10 6]'),
                    (3, '[10 10 6] (2) [10 8 5]'),
                    (4, '[10 8 5] (-4) [13 11 8]'),
                    (5, '[13 11 8] (3) [11 9 6]'),
                    (6, '[11 9 6] (-2) [13 10 6]'),
                    (7, '[13 10 6] (-3) [14 12 10]'),
                    (8, '[14 12 10] (4) [10 8 5]'),
                    (9, '[10 8 5] (-4) [12 10 8]'),
                    (10, '[12 10 8] (1) [15 12 10]'),
                    (13, '[15 12 10] (8) [8 5 3]'),
                    (14, '[8 5 3] (-2) [10 6 4]'),
                    (15, '[10 6 4] (-2) [10 8 5]'),
                    (16, '[10 8 5] (-3) [12 10 6]'),
                    (17, '[12 10 6] (2) [10 8 5]'),
                    (18, '[10 8 5] (-5) [15 12 10]'),
                    (19, '[15 12 10] (8) [8 5 3]'),
                    (21, '[8 5 3] (-3) [10 8 5]'),
                    (22, '[10 8 5] (-3) [12 10 6]'),
                    (23, '[12 10 6] (-3) [14 10 8]'),
                    (24, '[14 10 8] (4) [10 8 5]'),
                    (25, '[10 8 5] (-3) [12 10 8]'),
                    (26, '[12 10 8] (-3) [13 12 10]'),
                    (27, '[13 12 10] (2) [12 11 8]'),
                    (28, '[12 11 8] (1) [13 10 6]'),
                    (29, '[13 10 6] (2) [10 8 5]'),
                    (30, '[10 8 5] (-5) [15 12 10]'),
                    (31, '[15 12 10] (6) [10 6 3]'),
                    (33, '[10 6 3] (1) [9 6 4]'),
                    (34, '[9 6 4] (-2) [10 8 6]'),
                    (35, '[10 8 6] (2) [10 6 3]'),
                    (36, '[10 6 3] (2) [10 5 1]'),
                    (37, '[10 5 1] (-2) [11 6 4]'),
                    (38, '[11 6 4] (2) [10 7 5]'),
                    (39, '[10 7 5] (2) [10 5 3]'),
                    (40, '[10 5 3] (-5) [14 10 8]'),
                    (41, '[14 10 8] (2) [12 10 7]'),
                    (42, '[12 10 7] (2) [10 9 5]'),
                    (43, '[10 9 5] (-3) [12 10 7]'),
                    (44, '[12 10 7] (2) [10 8 5]'),
                    (45, '[10 8 5] (-5) [15 12 10]')]

    @staticmethod
    def series_maker(make_series):
        """
        Convert an iterable of 2-tuples into a pandas.Series. Each 2-tuple should have the "index"
        value at index 0 and the "value" itself at index 1.
        """
        post_ind = []
        post_vals = []
        for each in make_series:
            post_ind.append(each[0])
            post_vals.append(each[1])
        return pandas.Series(post_vals, index=post_ind)

    def assertDataFramesEqual(self, exp, act):
        """Ensure that two DataFrame objects, ``exp`` and ``act``, are equal."""
        self.assertSequenceEqual(list(exp.columns), list(act.columns))
        for col_name in exp.columns:
            for loc_val in exp[col_name].index:
                self.assertTrue(loc_val in act.index)
                if exp[col_name].loc[loc_val] != act[col_name].loc[loc_val]:
                    msg = '"{}" is {} but we expected {}'
                    raise AssertionError(msg.format(loc_val,
                                                    exp[col_name].loc[loc_val],
                                                    act[col_name].loc[loc_val]))

    def test_ngrams_1(self):
        """all-voice interval 2-grams; no WorkflowManager"""
        expected = AllVoiceIntervalNGrams.series_maker(AllVoiceIntervalNGrams.twograms)
        expected = pandas.DataFrame({('ngram.NGramIndexer', '[0,3 1,3 2,3] 3'): expected})
        ind_piece = IndexedPiece(os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv603.xml'))
        setts = {'quality': False, 'simple': False, 'horiz_attach_later': True}
        horiz_ints = ind_piece.get_data([noterest.NoteRestIndexer,
                                         interval.HorizontalIntervalIndexer],
                                        setts)
        vert_ints = ind_piece.get_data([noterest.NoteRestIndexer,
                                        interval.IntervalIndexer],
                                        setts)
        all_ints = pandas.concat([horiz_ints, vert_ints], axis=1)
        setts = {'mark singles': False, 'continuer': '1', 'n': 2}
        setts['horizontal'] = [('interval.HorizontalIntervalIndexer', '3')]
        setts['vertical'] = [('interval.IntervalIndexer', '0,3'),
                             ('interval.IntervalIndexer', '1,3'),
                             ('interval.IntervalIndexer', '2,3')]
        actual = ind_piece.get_data([ngram.NGramIndexer], setts, all_ints)
        self.assertDataFramesEqual(expected, actual)

    def test_ngrams_2(self):
        """same as test_ngrams_1() *but* with WorkflowManager"""
        expected = AllVoiceIntervalNGrams.series_maker(AllVoiceIntervalNGrams.twograms)
        expected = pandas.DataFrame({('ngram.NGramIndexer', '[0,3 1,3 2,3] 3'): expected})
        workm = workflow.WorkflowManager([os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv603.xml')])
        workm.load()
        workm.settings(None, 'interval quality', False)
        workm.settings(None, 'n', 2)
        workm.settings(None, 'count frequency', False)
        workm.settings(0, 'voice combinations', 'all')
        actual = workm.run('interval n-grams')[0]
        self.assertDataFramesEqual(expected, actual)

    def test_new_ngrams_3(self):
        """same as test_ngrams_2() but with new_ngram_indexer instead of WorkFlowManager."""
        expected = AllVoiceIntervalNGrams.series_maker(AllVoiceIntervalNGrams.new_two_grams)
        expected = pandas.DataFrame({('new_ngram.NewNGramIndexer', '0,3 1,3 2,3 : 3'): expected})
        v_setts = {'quality': False, 'simple or compound': 'compound', 'directed': True}
        h_setts = {'quality': False, 'horiz_attach_later': True, 'simple or compound': False, 'directed': True}
        n_setts = {'n': 2, 'horizontal': [('3',)], 'vertical': [('0,3', '1,3', '2,3')], 'brackets': True, 'continuer': '1'}
        ind_piece = IndexedPiece(os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv603.xml'))
        parts = ind_piece._import_score().parts
        nr = noterest.NoteRestIndexer(parts).run()
        vt = interval.IntervalIndexer(nr, v_setts).run()
        hz = interval.HorizontalIntervalIndexer(nr, h_setts).run()
        actual = new_ngram.NewNGramIndexer((vt, hz), n_setts).run()
        self.assertTrue(actual.equals(expected))

    # TODO: those two tests, again, counting frequency

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
ALL_VOICE_INTERVAL_NGRAMS = TestLoader().loadTestsFromTestCase(AllVoiceIntervalNGrams)
