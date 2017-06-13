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
import pandas as pd
from vis.analyzers.indexers import dissonance, noterest, meter, interval
from vis.models.indexed_piece import Importer, IndexedPiece
from pandas.util.testing import assert_frame_equal

# find the pathname of the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]


def make_df(series_list, mI):
    """
    Takes a list of series and a multiIndex.
    Returns a dataframe that concatenates on column axis and adds the passed multiIndex
    """
    df = pd.concat(series_list, axis=1)
    df.columns = mI
    return df

# strings with which to make multiIndecies
b_ind = u'meter.NoteBeatStrengthIndexer'
diss_ind = u'dissonance.DissonanceIndexer' # equivalent to diss_types in dissonance indexer, not diss_ind
dur_ind = u'meter.DurationIndexer'
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
    Limited unit tests and two integration tests for the dissonance indexer.
    """
    def test_diss_indexer_is_passing_1a(self):
        """
        Check that (False,) is returned whenprevious_event is None.
        """
        in_dfs = [qh_b_df, qh_dur_df, qh_h_df, asc_q_v_df]
        expected = (False,)
        init = dissonance.DissonanceIndexer(in_dfs)
        actual = init._is_passing_or_neigh('dummy', 'dummy', 'dummy', None)
        self.assertSequenceEqual(expected, actual)

    def test_diss_indexer_is_passing_1b(self):
        """
        Check that (False,) is returned when previous_event is not in dissonance._consonances.
        """
        in_dfs = [qh_b_df, qh_dur_df, qh_h_df, asc_q_v_df]
        expected = (False,)
        init = dissonance.DissonanceIndexer(in_dfs)
        actual = init._is_passing_or_neigh(1, '0,1', 'M2', 'm2')
        self.assertSequenceEqual(expected, actual)

    def test_diss_indexer_is_passing_2a(self):
        """
        Detection of rising passing tone in quarter notes.
        """
        in_dfs = [qh_b_df, qh_dur_df, qh_h_df, asc_q_v_df]
        expected = (True, '0', dissonance._pass_rp_label, '1', dissonance._no_diss_label)
        init = dissonance.DissonanceIndexer(in_dfs)
        actual = init._is_passing_or_neigh(1, '0,1', 'M2', 'P1')
        self.assertSequenceEqual(expected, actual)

    def test_diss_indexer_is_passing_2b(self):
        """
        Detection of rising passing tone in quarter notes.
        """
        in_dfs = [hq_b_df, hq_dur_df, hdescq_h_df, asc_q_v_df]
        expected = (True, '0', dissonance._no_diss_label, '1', dissonance._pass_dp_label)
        init = dissonance.DissonanceIndexer(in_dfs)
        actual = init._is_passing_or_neigh(1, '0,1', 'M2', 'P1')
        self.assertSequenceEqual(expected, actual)

    def test_diss_indexer_run_1a(self):
        """
        Detection of two rising passing tones in a mini-piece.
        """
        in_dfs = [qh_b_df, qh_dur_df, qh_h_df, asc_q_v_df]
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
        expected = empty_df.copy()
        expected.iat[1, 1] = 'D'
        expected.iat[3, 1] = 'D'
        actual = dissonance.DissonanceIndexer(in_dfs).run()
        assert_frame_equal(expected, actual)

    def test_diss_indexer_run_2(self):
        """
        Test the dissonance indexer on an entire real piece that has most of the dissonance types 
        and covers almost all of the logic, namely the "Kyrie" in the test corpus. NB: perhaps 
        this test should get moved to the integration tests file.
        """
        expected = pd.read_pickle(os.path.join(VIS_PATH, 'tests', 'expecteds', 'test_dissonance_thorough.pickle'))
        # Detection of Z's and O's was removed and so this old ground-truth is updated in this test with the two 
        # following lines. If the dissonance indexer gets re-written, it would be good to go back to this old 
        # ground truth without needing these two replace() calls.
        expected.replace('Z', '-', inplace=True)
        expected.replace('O', '-', inplace=True)
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus', 'Kyrie.krn'))
        actual = ip.get_data('dissonance')
        expected.columns = actual.columns # the pickle file has old-style column names.
        assert_frame_equal(actual, expected)


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
DISSONANCE_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestDissonanceIndexer)
