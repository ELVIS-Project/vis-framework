#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_interval_indexer.py
# Purpose:                Tests for analyzers/indexers/interval.py
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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import os
import unittest
import six
import pandas as pd
import music21
from vis.analyzers.indexers import dissonance
import pdb
from pandas.util.testing import assert_frame_equal

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
    return pd.Series(vals, index=new_index)

def pandas_maker(lolists):
    """
    Use make_series() to convert a list of appropriate tuples into a list of appropriate Series.

    Input: list of the input desired by make_series()

    Output: list of pd.Series
    """
    return [make_series(x) for x in lolists]

def make_df(series_list, mI):
    """
    Takes a list of series and a multiIndex.
    Returns a dataframe that concatenates on column axis and adds the passed multiIndex
    """
    df = pd.concat(series_list, axis=1)
    df.columns = mI
    return df

# strings with which to make multiIndecies
b_ind = u'metre.NoteBeatStrengthIndexer'
diss_ind = u'dissonance.DissonanceIndexer' # equivalent to diss_types in dissonance indexer, not diss_ind
dur_ind = u'metre.DurationIndexer'
h_ind = u'interval.HorizontalIntervalIndexer'
v_ind = u'interval.IntervalIndexer'
names = ('Indexer', 'Parts')

# sample note beat strength values (assumes 4/2 time signature)
q_b_ser = pd.Series([1, .125, .25, .125, .5, .125]) # a six-window series of beat strengths of quarter notes in 4/2
h_b_ser = pd.Series([1, .25, .5], index=q_b_ser.index[:3]*2) # a 3-window series of beat strengths of half notes in 4/2
b_mI = pd.MultiIndex.from_product((b_ind, ('0', '1')), names=names)
qh_b_df = make_df((q_b_ser, h_b_ser), b_mI)
qq_b_df = make_df((q_b_ser, q_b_ser), b_mI)
hh_b_df = make_df((h_b_ser, h_b_ser), b_mI)
hq_b_df = make_df((h_b_ser, q_b_ser), b_mI)

# sample duration values
q_dur_ser = pd.Series([1]*6) # a six-window series of quarter note durations
h_dur_ser = pd.Series([2]*3, index=q_dur_ser.index[:3]*2) # a three-window series of half note durations
dur_mI = pd.MultiIndex.from_product((dur_ind, ('0', '1')), names=names)
qh_dur_df = make_df((q_dur_ser, h_dur_ser), dur_mI)
qq_dur_df = make_df((q_dur_ser, q_dur_ser), dur_mI)
hh_dur_df = make_df((h_dur_ser, h_dur_ser), dur_mI)
hq_dur_df = make_df((h_dur_ser, q_dur_ser), dur_mI)

# sample horizontal interval values
q_h_ser = pd.Series(['2']*6) # a six-window series of stepwise horizontal ascent in quarter notes
desc_q_h_ser = pd.Series(['-2']*6)
h_h_ser = pd.Series(['1']*3, index=q_h_ser.index[:3]*2) # a 3-window series of horizontal ints in half notes (reiterated unisons)
h2_h_ser = pd.Series(['1']*3, index=q_h_ser.index[:3]*2)
h_mI = pd.MultiIndex.from_product((h_ind, ('0', '1')), names=names)
qh_h_df = make_df((q_h_ser, h_h_ser), h_mI) # ascending quarter notes over stationary half notes
qq_h_df = make_df((q_h_ser, q_h_ser), h_mI) # two lines of quarter notes ascending together by step
hh_h_df = make_df((h_h_ser, h_h_ser), h_mI) # two lines of stationary half notes
hdescq_h_df = make_df((h_h_ser, desc_q_h_ser), h_mI) # stationary half notes over quarter notes descending by step

# sample vertical interval values
asc_maj_ints = ['P1', 'M2', 'M3', 'P4', 'P5', 'M6']
desc_maj_ints = [ntrvl for ntrvl in reversed(asc_maj_ints)]
asc_q_v_ser = pd.Series(asc_maj_ints) # a six-window series vertical intervals ascending stepwise up a major scale in quarter notes
desc_q_v_ser = pd.Series(desc_maj_ints) # a six-window series vertical intervals ascending stepwise up a major scale in quarter notes
v_mI = pd.MultiIndex.from_product((v_ind, ('0,1',)), names=names)
asc_q_v_df = make_df((asc_q_v_ser,), v_mI)
desc_q_v_df = make_df((desc_q_v_ser,), v_mI)

# dissonance results df constructor materials
empty = pd.Series(['-']*6)
diss_mI = pd.MultiIndex.from_product((diss_ind, ('0', '1')), names=names)
empty_df = make_df([empty, empty], diss_mI)



class TestDissonanceIndexer(unittest.TestCase):
    """
    TODO:
    - Use actual indexers instead of basic_indexer in test_dissonance_indexer.py
    - Consider omitting the concatenation step for the indexer results that are passed to the 
        dissonance indexer call (duration, horiz_int, note_beat_strength, vert_int)
        NB: be sure to put them in alphabetical order as above.
    - Separate out check4s_5s() into its own series indexer
    - Separate out passing tone and neighbor tone detection
    - Revisit run method
    - Reconsider assigning variables just once and sending the results to each dissonance type checker. 
        Ask Ryan about this.
    - Revisit classify() method
    - Actually write a bunch of tests. Loosely base them on the interval indexer tests below.
    """
    def test_diss_indexer_is_passing_1a(self):
        """
        Check that (False,) is returned whenprevious_event is None.
        """
        in_dfs = [qh_b_df, qh_dur_df, qh_h_df, asc_q_v_df]
        in_dfs = pd.concat(in_dfs, axis=1)
        expected = (False,)
        init = dissonance.DissonanceIndexer(in_dfs)
        actual = init._is_passing_or_neigh('dummy', 'dummy', 'dummy', None)
        self.assertSequenceEqual(expected, actual)

    def test_diss_indexer_is_passing_1b(self):
        """
        Check that (False,) is returned when previous_event is not in dissonance._consonances.
        """
        in_dfs = [qh_b_df, qh_dur_df, qh_h_df, asc_q_v_df]
        in_dfs = pd.concat(in_dfs, axis=1)
        expected = (False,)
        init = dissonance.DissonanceIndexer(in_dfs)
        actual = init._is_passing_or_neigh(1, '0,1', 'M2', 'm2')
        self.assertSequenceEqual(expected, actual)

    def test_diss_indexer_is_passing_2a(self):
        """
        Detection of rising passing tone in quarter notes.
        """
        in_dfs = [qh_b_df, qh_dur_df, qh_h_df, asc_q_v_df]
        in_dfs = pd.concat(in_dfs, axis=1)
        expected = (True, '0', dissonance._pass_rp_label, '1', dissonance._no_diss_label)
        init = dissonance.DissonanceIndexer(in_dfs)
        actual = init._is_passing_or_neigh(1, '0,1', 'M2', 'P1')
        self.assertSequenceEqual(expected, actual)

    def test_diss_indexer_is_passing_2b(self):
        """
        Detection of rising passing tone in quarter notes.
        """
        in_dfs = [hq_b_df, hq_dur_df, hdescq_h_df, asc_q_v_df]
        in_dfs = pd.concat(in_dfs, axis=1)
        expected = (True, '0', dissonance._no_diss_label, '1', dissonance._pass_dp_label)
        init = dissonance.DissonanceIndexer(in_dfs)
        actual = init._is_passing_or_neigh(1, '0,1', 'M2', 'P1')
        self.assertSequenceEqual(expected, actual)

    def test_diss_indexer_run_1a(self):
        """
        Detection of two rising passing tones in a mini-piece.
        """
        in_dfs = [qh_b_df, qh_dur_df, qh_h_df, asc_q_v_df]
        in_dfs = pd.concat(in_dfs, axis=1)
        expected = empty_df.copy()
        expected.iat[1, 0] = 'R'
        expected.iat[3, 0] = 'R'
        actual = dissonance.DissonanceIndexer(in_dfs).run()
        assert_frame_equal(expected, actual)

    def test_diss_indexer_run_1b(self):
        """
        Detection of two descending passing tones in a mini-piece. NB: the int size increases even 
        though the passing tones are descending because the passing tones are in the lower voice
        """
        in_dfs = [hq_b_df, hq_dur_df, hdescq_h_df, asc_q_v_df]
        in_dfs = pd.concat(in_dfs, axis=1)
        expected = empty_df.copy()
        expected.iat[1, 1] = 'D'
        expected.iat[3, 1] = 'D'
        actual = dissonance.DissonanceIndexer(in_dfs).run()
        assert_frame_equal(expected, actual)


    # def test_int_indexer_short_2(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.25, 'Rest')]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4'), (0.25, 'Rest')],
    #                      [(0.0, 'G3'), (0.25, 'Rest')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_3(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.25, 'Rest')]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4')], [(0.0, 'G3'), (0.25, 'Rest')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_4(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.25, 'Rest')]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4'), (0.25, 'Rest')], [(0.0, 'G3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_5(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.5, interval.Interval(note.Note('A3'), note.Note('F4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4'), (0.5, 'F4')],
    #                      [(0.0, 'G3'), (0.5, 'A3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_6(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4', 1.0)], [(0.0, 'G3'), (0.5, 'A3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_7(self):
    #     expected = [[(0.0, interval.Interval(note.Note('B3'), note.Note('A4')).name),
    #                  (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (1.0, interval.Interval(note.Note('A3'), note.Note('G4')).name),
    #                  (1.5, interval.Interval(note.Note('B3'), note.Note('F4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'A4'), (0.5, 'G4', 1.0), (1.5, 'F4')],
    #                      [(0.0, 'B3'), (0.5, 'G3'),
    #                       (1.0, 'A3'), (1.5, 'B3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_8(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.25, 'Rest'),
    #                  (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4', 1.0)],
    #                      [(0.0, 'G3'), (0.25, 'Rest'), (0.5, 'A3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_9(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.25, 'Rest'),
    #                  (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name),
    #                  (1.0, interval.Interval(note.Note('B3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4', 1.0), (1.0, 'G4')],
    #                      [(0.0, 'G3'), (0.25, 'Rest'), (0.5, 'A3'), (1.0, 'B3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_10(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4', 1.0)], [(0.0, 'G3'), (0.25, 'A3', 0.75)]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_11(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4', 1.0)], [(0.0, 'G3'), (0.5, 'G3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_12(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.25, 'Rest'),
    #                  (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4', 1.0)],
    #                      [(0.0, 'G3'), (0.25, 'Rest'), (0.5, 'G3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_13(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.125, 'Rest'),
    #                  (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name),
    #                  (0.375, 'Rest'),
    #                  (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4', 1.0)],
    #                      [(0.0, 'G3', 0.125), (0.125, 'Rest', 0.125),
    #                       (0.25, 'A3', 0.125), (0.375, 'Rest', 0.125), (0.5, 'G3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_14(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.0625, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.125, 'Rest'),
    #                  (0.1875, 'Rest'),
    #                  (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name),
    #                  (0.3125, interval.Interval(note.Note('A3'), note.Note('G4')).name),
    #                  (0.375, 'Rest'),
    #                  (0.4375, 'Rest'),
    #                  (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4', 0.0625), (0.0625, 'G4', 0.0625),
    #                       (0.125, 'G4', 0.0625), (0.1875, 'G4', 0.0625),
    #                       (0.25, 'G4', 0.0625), (0.3125, 'G4', 0.0625),
    #                       (0.375, 'G4', 0.0625), (0.4375, 'G4', 0.0625),
    #                       (0.5, 'G4')],
    #                      [(0.0, 'G3', 0.125), (0.125, 'Rest', 0.125), (0.25, 'A3', 0.125),
    #                       (0.375, 'Rest', 0.0625), (0.4375, 'Rest', 0.0625), (0.5, 'G3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_15(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.75, 'Rest'),
    #                  (1.0, 'Rest'),
    #                  (1.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4'), (0.5, 'G4'), (0.75, 'Rest'),
    #                       (1.0, 'G4'), (1.5, 'G4')],
    #                      [(0.0, 'G3'), (0.5, 'G3'), (0.75, 'Rest'),
    #                       (1.0, 'Rest'), (1.5, 'G3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_16(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.5, 'Rest'),
    #                  (0.75, interval.Interval(note.Note('F3'), note.Note('A4')).name),
    #                  (1.25, interval.Interval(note.Note('F3'), note.Note('G4')).name),
    #                  (1.5, interval.Interval(note.Note('E3'), note.Note('B4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4'), (0.5, 'A4', 0.75),
    #                       (1.25, 'G4'), (1.5, 'B4')],
    #                      [(0.0, 'G3'), (0.5, 'Rest'),
    #                       (0.75, 'F3', 0.75), (1.5, 'E3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))

    # def test_int_indexer_short_17(self):
    #     expected = [[(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
    #                  (0.5, interval.Interval(note.Note('A3'), note.Note('A4')).name),
    #                  (0.75, interval.Interval(note.Note('F3'), note.Note('A4')).name),
    #                  (1.125, 'Rest'),
    #                  (1.25, 'Rest'),
    #                  (1.375, interval.Interval(note.Note('G3'), note.Note('F4')).name),
    #                  (2.0, interval.Interval(note.Note('G3'), note.Note('E4')).name)]]
    #     expected = {'0,1': pandas_maker(expected)[0]}
    #     not_processed = [[(0.0, 'G4'), (0.5, 'A4', 0.75), (1.25, 'F4', 0.75),
    #                       (2.0, 'E4')],
    #                      [(0.0, 'G3'), (0.5, 'A3'), (0.75, 'F3', 0.375),
    #                       (1.125, 'Rest'), (1.375, 'G3', 0.625), (2.0, 'G3')]]
    #     test_in = pandas_maker(not_processed)
    #     int_indexer = IntervalIndexer(test_in,
    #                                   {'quality': True, 'simple or compound': 'compound', 'direction': True})
    #     actual = int_indexer.run()['interval.IntervalIndexer']
    #     self.assertEqual(len(expected), len(actual.columns))
    #     for key in six.iterkeys(expected):
    #         self.assertTrue(key in actual)
    #         self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
    #         self.assertSequenceEqual(list(expected[key]), list(actual[key]))




#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
DISSONANCE_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestDissonanceIndexer)
