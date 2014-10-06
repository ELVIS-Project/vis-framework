#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_workflow_experiments.py
# Purpose:                Tests for the WorkflowManager's experiment-specific methods
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
Tests for the WorkflowManager
"""

from unittest import TestCase, TestLoader
import mock
from mock import MagicMock
import pandas
from vis.workflow import WorkflowManager, split_part_combo
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import interval, noterest


class Intervals(TestCase):
    """Tests for the WorkflowManager._intervs() experiment."""

    @mock.patch('vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    def test_intervs_1(self, mock_rfa, mock_rep):
        """Ensure _intervs() calls everything in the right order, with the right args & settings.
           This test uses all the default settings."""
        test_settings = {'simple or compound': 'compound', 'quality': False}
        test_pieces = [MagicMock(autospec=IndexedPiece) for _ in xrange(3)]
        returns = ['get_data() {}'.format(i) for i in xrange(len(test_pieces))]
        for piece in test_pieces:
            piece.get_data.side_effect = lambda *x: returns.pop(0)
        expected = ['get_data() {}'.format(i) for i in xrange(len(test_pieces))]
        exp_analyzers = [noterest.NoteRestIndexer, interval.IntervalIndexer]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(None, 'include rests', True)
        actual = test_wc._intervs()  # pylint: disable=protected-access

        self.assertEqual(len(test_pieces), len(expected), len(actual))
        self.assertEqual(0, mock_rep.call_count)
        mock_rfa.assert_called_once_with('interval.IntervalIndexer')
        for piece in test_pieces:
            piece.get_data.assert_called_once_with(exp_analyzers, test_settings)
        for i in xrange(len(actual)):
            # NB: in real use, _run_freq_agg() would aggregate a piece's voice pairs and save it in
            #     self._result... but since that method's mocked out, we have to check here the
            #     return of each piece's get_data() call
            self.assertSequenceEqual(expected[i], actual[i])

    @mock.patch('vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    def test_intervs_2(self, mock_rfa, mock_rep):
        """Ensure _intervs() calls everything in the right order, with the right args & settings.
           Same as test_intervs_1() but:
              - calls _remove_extra_pairs(), and
              - doesn't call _run_freq_agg()."""
        voice_combos = '[[0, 1]]'
        exp_voice_combos = ['0,1']
        test_settings = {'simple or compound': 'compound', 'quality': False}
        test_pieces = [MagicMock(autospec=IndexedPiece) for _ in xrange(3)]
        returns = ['get_data() {}'.format(i) for i in xrange(len(test_pieces))]
        for piece in test_pieces:
            piece.get_data.side_effect = lambda *x: returns.pop(0)
        exp_into_mock_rep = ['get_data() {}'.format(i) for i in xrange(len(test_pieces))]
        mock_rep_returns = ['IndP-{} no pairs'.format(i) for i in xrange(len(test_pieces))]
        mock_rep.side_effect = lambda *x: mock_rep_returns.pop(0)
        expected = ['IndP-{} no pairs'.format(i) for i in xrange(len(test_pieces))]
        exp_analyzers = [noterest.NoteRestIndexer, interval.IntervalIndexer]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(None, 'include rests', True)
        test_wc.settings(None, 'count frequency', False)
        test_wc.settings(None, 'voice combinations', voice_combos)
        actual = test_wc._intervs()  # pylint: disable=protected-access

        self.assertEqual(len(test_pieces), len(expected), len(actual))
        self.assertEqual(0, mock_rfa.call_count)
        self.assertEqual(len(test_pieces), mock_rep.call_count)
        for i in xrange(len(test_pieces)):
            mock_rep.assert_any_call(exp_into_mock_rep[i], exp_voice_combos)
        for piece in test_pieces:
            piece.get_data.assert_called_once_with(exp_analyzers, test_settings)
        for i in xrange(len(actual)):
            self.assertSequenceEqual(expected[i], actual[i])

    @mock.patch('vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    def test_intervs_3(self, mock_rfa, mock_rep):
        """Ensure _intervs() calls everything in the right order, with the right args & settings.
           This uses the default *except* requires removing rests, so it's more complex."""
        test_settings = {'simple or compound': 'compound', 'quality': False}
        test_pieces = [MagicMock(autospec=IndexedPiece) for _ in xrange(3)]
        returns = [pandas.DataFrame([pandas.Series(['3', 'Rest', '5'])],
                                    index=[['interval.IntervalIndexer'], ['0,1']]).T
                   for i in xrange(len(test_pieces))]
        for piece in test_pieces:
            piece.get_data.side_effect = lambda *x: returns.pop(0)
        exp_series_ind = ('interval.IntervalIndexer', '0,1')
        expected_df = pandas.DataFrame({exp_series_ind: pandas.Series(['3', '5'], index=[0, 2])})
        exp_analyzers = [noterest.NoteRestIndexer, interval.IntervalIndexer]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(None, 'count frequency', False)
        actual = test_wc._intervs()  # pylint: disable=protected-access

        self.assertEqual(len(test_pieces), len(actual))
        self.assertEqual(0, mock_rfa.call_count)
        self.assertEqual(0, mock_rep.call_count)
        for piece in test_pieces:
            piece.get_data.assert_called_once_with(exp_analyzers, test_settings)
        for i in xrange(len(actual)):
            self.assertSequenceEqual(list(expected_df.columns), list(actual[i].columns))
            self.assertSequenceEqual(list(expected_df[exp_series_ind].index),
                                     list(actual[i][exp_series_ind].index))
            self.assertSequenceEqual(list(expected_df[exp_series_ind].values),
                                     list(actual[i][exp_series_ind].values))

    def test_intervs_4(self):
        """Ensure _intervs() fails when given an impossible 'voice pair'."""
        test_pieces = [MagicMock(autospec=IndexedPiece) for _ in xrange(3)]
        returns = ['get_data() {}'.format(i) for i in xrange(len(test_pieces))]
        for piece in test_pieces:
            piece.get_data.side_effect = lambda *x: returns.pop(0)
        exp_err_msg = WorkflowManager._REQUIRE_PAIRS_ERROR.format(3)  # pylint: disable=protected-access

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(None, 'include rests', True)
        test_wc.settings(None, 'voice combinations', '[[0, 1, 2]]')  # that's not a pair!

        self.assertRaises(RuntimeError, test_wc._intervs)  # pylint: disable=protected-access
        try:
            test_wc._intervs()  # pylint: disable=protected-access
        except RuntimeError as run_err:
            self.assertEqual(exp_err_msg, run_err.message)


class IntervalNGrams(TestCase):

    """Tests for helper functions related to the "interval n-grams" experiments."""
    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch('vis.workflow.WorkflowManager._variable_part_modules')
    @mock.patch('vis.workflow.WorkflowManager._all_part_modules')
    @mock.patch('vis.workflow.WorkflowManager._two_part_modules')
    def test_interval_ngrams_1(self, mock_two, mock_all, mock_var, mock_rfa):
        """test _interval_ngrams() with three pieces, each of which requires a different helper"""
        # 1.) prepare mocks
        ind_pieces = [MagicMock(atuospec=IndexedPiece) for _ in xrange(3)]
        mock_rfa.return_value = 'mock_rfa() return value'
        mock_two.return_value = ['mock_two() return value']
        mock_all.return_value = ['mock_all() return value']
        mock_var.return_value = ['mock_var() return value']
        expected = [mock_all.return_value, mock_two.return_value, mock_var.return_value]
        # 2.) run the test
        test_wm = WorkflowManager(ind_pieces)
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(1, 'voice combinations', 'all pairs')
        test_wm.settings(2, 'voice combinations', '[[0, 1]]')
        actual = test_wm._interval_ngrams()
        # 3.) verify the mocks
        # NB: in actual use, _run_freq_agg() would have the final say on the value of
        #     test_wm._result... but it's mocked out, which means we can test whether
        #     _interval_ngrams() puts the right stuff there
        mock_two.assert_called_once_with(1)
        mock_all.assert_called_once_with(0)
        mock_var.assert_called_once_with(2)
        mock_rfa.assert_called_once_with('ngram.NGramIndexer')
        self.assertSequenceEqual(expected, actual)
        self.assertSequenceEqual(expected, test_wm._result)

    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch('vis.workflow.WorkflowManager._variable_part_modules')
    @mock.patch('vis.workflow.WorkflowManager._all_part_modules')
    @mock.patch('vis.workflow.WorkflowManager._two_part_modules')
    def test_interval_ngrams_2(self, mock_two, mock_all, mock_var, mock_rfa):
        """same as test_interval_ngrams_1(), but with "count frequency" set to False"""
        # 1.) prepare mocks
        ind_pieces = [MagicMock(autospec=IndexedPiece) for _ in xrange(3)]
        mock_rfa.return_value = 'mock_rfa() return value'
        mock_two.return_value = ['mock_two() return value']
        mock_all.return_value = ['mock_all() return value']
        mock_var.return_value = ['mock_var() return value']
        expected = [mock_all.return_value, mock_two.return_value, mock_var.return_value]
        # 2.) run the test
        test_wm = WorkflowManager(ind_pieces)
        test_wm.settings(0, 'voice combinations', 'all')
        test_wm.settings(1, 'voice combinations', 'all pairs')
        test_wm.settings(2, 'voice combinations', '[[0, 1]]')
        test_wm.settings(None, 'count frequency', False)
        actual = test_wm._interval_ngrams()
        # 3.) verify the mocks
        # NB: in actual use, _run_freq_agg() would have the final say on the value of
        #     test_wm._result... but it's mocked out, which means we can test whether
        #     _interval_ngrams() puts the right stuff there
        self.assertEqual(3, len(test_wm._result))
        for ret_val in expected:
            self.assertTrue(ret_val in test_wm._result)
        mock_two.assert_called_once_with(1)
        mock_all.assert_called_once_with(0)
        mock_var.assert_called_once_with(2)
        self.assertEqual(0, mock_rfa.call_count)
        self.assertEqual(expected, actual)
        self.assertSequenceEqual(expected, test_wm._result)

    @mock.patch('vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch('vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch('vis.workflow.ngram.NGramIndexer')
    @mock.patch('vis.workflow.noterest.NoteRestIndexer')
    @mock.patch('vis.workflow.interval.IntervalIndexer')
    def test_var_part_modules_1(self, mock_int, mock_nri, mock_ng, mock_horiz, mock_ror):
        # - we'll only use self._data[1]; excluding "Rest"
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in ['test1', 'test2', 'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = ['S', 'A', 'T', 'B']
        # set up the mock_ror return values (i.e., what came out of the IntervalIndexer)
        all_part_combos = ['0,3', '1,3', '2,3', '0,1', '0,2', '1,2']
        selected_part_combos = [[0, 3], [2, 3]]
        ror_vert_ret = {x: MagicMock(name='piece2 part ' + x) for x in all_part_combos}
        ror_horiz_ret = [MagicMock(name='piece2 horiz ' + str(x)) for x in xrange(4)]
        ror_returns = [ror_vert_ret, ror_horiz_ret]
        def ror_side_effect(*args, **kwargs):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return ror_returns.pop(0)
        mock_ror.side_effect = ror_side_effect
        # set up fake return values for IntervalIndexer
        vert_ret = u"IntervalIndexer's return"
        horiz_ret = u"HorizontalIntervalIndexer's return"
        # set up return values for IndexedPiece.get_data()
        returns = [vert_ret, horiz_ret, ['piece2 3rd get_data()'], ['piece2 4th get_data()']]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        expected = [x[0] for x in returns[2:]]
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_index = 1
        test_wc.settings(test_index, 'interval quality', True)
        test_wc.settings(test_index, 'simple intervals', True)
        test_wc.settings(test_index, 'filter repeats', False)
        test_wc.settings(test_index, 'offset interval', None)
        test_wc.settings(test_index, 'voice combinations', unicode(selected_part_combos))
        actual = test_wc._variable_part_modules(test_index)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {'quality': True, 'simple or compound': 'simple'}
        expected_ngram_settings = {'horizontal': [1], 'vertical': [0], 'n': 2,
                                   'continuer': 'dynamic quality', 'mark singles': False,
                                   'terminator': 'Rest'}
        # 2 combinations for NGramIndexer, plus 2 calls to interval indexers
        self.assertEqual(4, test_pieces[1].get_data.call_count)
        exp_calls = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts)]
        for i in xrange(len(exp_calls)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], exp_calls[i])
        # - that _run_off_rep() is called once for horizontal and vertical
        self.assertEqual(2, mock_ror.call_count)
        mock_ror.assert_any_call(test_index, vert_ret)
        mock_ror.assert_any_call(test_index, horiz_ret, is_horizontal=True)
        # - that each IndP.get_data() called NGramIndexer with the right settings at some point
        for combo in selected_part_combos:
            zombo = str(combo[0]) + ',' + str(combo[1])
            test_pieces[1].get_data.assert_any_call([mock_ng],
                                                    expected_ngram_settings,
                                                    [ror_vert_ret[zombo],
                                                    ror_horiz_ret[combo[1]]])
        self.assertEqual(expected, actual)

    @mock.patch('vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch('vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch('vis.workflow.ngram.NGramIndexer')
    @mock.patch('vis.workflow.noterest.NoteRestIndexer')
    @mock.patch('vis.workflow.interval.IntervalIndexer')
    def test_var_part_modules_2(self, mock_int, mock_nri, mock_ng, mock_horiz, mock_ror):
        # - we'll only use self._data[1]; including "Rest"
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in ['test1', 'test2', 'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = ['S', 'A', 'T', 'B']
        # set up fake return values for IntervalIndexer
        all_part_combos = ['0,3', '1,3', '2,3', '0,1', '0,2', '1,2']
        selected_part_combos = [[0, 1, 2], [1, 2, 3]]
        ror_vert_ret = {x: MagicMock(name='piece2 part ' + x) for x in all_part_combos}
        ror_horiz_ret = [MagicMock(name='piece2 horiz ' + str(x)) for x in xrange(4)]
        ror_returns = [ror_vert_ret, ror_horiz_ret]
        def ror_side_effect(*args, **kwargs):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return ror_returns.pop(0)
        mock_ror.side_effect = ror_side_effect
        # set up fake return values for IntervalIndexer
        vert_ret = u"IntervalIndexer's return"
        horiz_ret = u"HorizontalIntervalIndexer's return"
        # set up return values for IndexedPiece.get_data()
        returns = [vert_ret, horiz_ret, ['piece2 3rd get_data()'], ['piece2 4th get_data()']]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        expected = [x[0] for x in returns[2:]]
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_index = 1
        test_wc.settings(test_index, 'interval quality', True)
        test_wc.settings(test_index, 'simple intervals', True)
        test_wc.settings(test_index, 'filter repeats', False)
        test_wc.settings(test_index, 'offset interval', None)
        test_wc.settings(test_index, 'voice combinations', unicode(selected_part_combos))
        test_wc.settings(None, 'include rests', True)
        actual = test_wc._variable_part_modules(test_index)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {'quality': True, 'simple or compound': 'simple'}
        expected_ngram_settings = {'horizontal': [2], 'vertical': [0, 1], 'n': 2, \
                                   'continuer': 'dynamic quality', 'mark singles': False}
        # 2 combinations for NGramIndexer, plus 2 calls to interval indexers
        self.assertEqual(4, test_pieces[1].get_data.call_count)
        exp_calls = [mock.call([mock_nri, mock_int], expected_interv_setts),
                     mock.call([mock_nri, mock_horiz], expected_interv_setts)]
        for i in xrange(len(exp_calls)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], exp_calls[i])
        # - that _run_off_rep() is called once for horizontal and vertical
        self.assertEqual(2, mock_ror.call_count)
        mock_ror.assert_any_call(test_index, vert_ret)
        mock_ror.assert_any_call(test_index, horiz_ret, is_horizontal=True)
        # - that each IndP.get_data() called NGramIndexer with the right settings at some point
        selected_part_combos = [[0, 1, 2], [1, 2, 3]]
        for combo in selected_part_combos:
            parts = [ror_vert_ret[str(i) + ',' + str(combo[-1])] for i in combo[:-1]]
            parts.append(ror_horiz_ret[combo[-1]])
            test_pieces[1].get_data.assert_any_call([mock_ng],
                                                    expected_ngram_settings,
                                                    parts)
        self.assertEqual(expected, actual)

    @mock.patch('vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch('vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch('vis.workflow.ngram.NGramIndexer')
    @mock.patch('vis.workflow.noterest.NoteRestIndexer')
    @mock.patch('vis.workflow.interval.IntervalIndexer')
    def test_all_part_modules_1(self, mock_int, mock_nri, mock_ng, mock_horiz, mock_ror):
        # - we'll only use self._data[1]; excluding "Rest"
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in ['test1', 'test2', 'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = ['S', 'A', 'T', 'B']
        # set up pseudo-IntervalIndexer results for mock_ror
        ror_vert_ret = {x: MagicMock(name='piece2 part ' + x) for x in ['0,3', '1,3', '2,3']}
        ror_horiz_ret = [None, None, None, MagicMock(name='piece1 horiz')]
        ror_returns = [ror_vert_ret, ror_horiz_ret]
        def ror_side_effect(*args, **kwargs):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return ror_returns.pop(0)
        mock_ror.side_effect = ror_side_effect
        # set up fake return values for IntervalIndexer
        vert_ret = u"IntervalIndexer's return"
        horiz_ret = u"HorizontalIntervalIndexer's return"
        # set up return values for IndexedPiece.get_data()
        returns = [vert_ret, horiz_ret, [3]]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        expected = [x[0] for x in returns[2:]]
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_index = 1
        test_wc.settings(test_index, 'interval quality', True)
        test_wc.settings(test_index, 'simple intervals', True)
        test_wc.settings(test_index, 'filter repeats', False)
        test_wc.settings(test_index, 'offset interval', None)
        actual = test_wc._all_part_modules(test_index)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {'quality': True, 'simple or compound': 'simple'}
        expected_ngram_settings = {'horizontal': [3], 'vertical': [0, 1, 2], 'n': 2,
                                   'continuer': 'dynamic quality', 'mark singles': False,
                                   'terminator': 'Rest'}
        # all parts at once for NGramIndexer, plus 2 calls to interval indexers
        self.assertEqual(3, test_pieces[test_index].get_data.call_count)
        # - that _run_off_rep() is called once for horizontal and vertical
        self.assertEqual(2, mock_ror.call_count)
        mock_ror.assert_any_call(test_index, vert_ret)
        mock_ror.assert_any_call(test_index, horiz_ret, is_horizontal=True)
        # confirm the calls to interval indexers an NGramIndexer all together
        exp_calls = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts),
                    mock.call([mock_ng],
                              expected_ngram_settings,
                              [ror_vert_ret['0,3'],
                               ror_vert_ret['1,3'],
                               ror_vert_ret['2,3'],
                               ror_horiz_ret[3]])]
        for i in xrange(len(exp_calls)):
            self.assertEqual(test_pieces[test_index].get_data.mock_calls[i], exp_calls[i])
        self.assertEqual(expected, actual)

    @mock.patch('vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch('vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch('vis.workflow.ngram.NGramIndexer')
    @mock.patch('vis.workflow.noterest.NoteRestIndexer')
    @mock.patch('vis.workflow.interval.IntervalIndexer')
    def test_two_part_modules_1(self, mock_int, mock_nri, mock_ng, mock_horiz, mock_ror):
        # - we'll only use self._data[1]; excluding "Rest"
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in ['test1', 'test2', 'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = ['S', 'A', 'T', 'B']
        # set up pseudo-IntervalIndexer results for mock_ror
        part_combos = ['0,3', '1,3', '2,3', '0,1', '0,2', '1,2']
        ror_vert_ret = {x: MagicMock(name='piece2 part ' + x) for x in part_combos}
        ror_horiz_ret = [MagicMock(name='piece2 horiz ' + str(x)) for x in xrange(4)]
        ror_returns = [ror_vert_ret, ror_horiz_ret]
        def ror_side_effect(*args, **kwargs):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return ror_returns.pop(0)
        mock_ror.side_effect = ror_side_effect
        # set up fake return values for IntervalIndexer
        vert_ret = u"IntervalIndexer's return"
        horiz_ret = u"HorizontalIntervalIndexer's return"
        # set up return values for IndexedPiece.get_data()
        returns = [vert_ret, horiz_ret, ['piece2 3rd get_data()'], ['piece2 4th get_data()'],
                   ['piece2 5th get_data()'], ['piece2 6th get_data()'], ['piece2 7th get_data()'],
                   ['piece2 8th get_data()']]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        expected = [x[0] for x in returns[2:]]
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_index = 1
        test_wc.settings(test_index, 'interval quality', True)
        test_wc.settings(test_index, 'simple intervals', True)
        test_wc.settings(test_index, 'filter repeats', False)
        test_wc.settings(test_index, 'offset interval', None)
        actual = test_wc._two_part_modules(test_index)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {'quality': True, 'simple or compound': 'simple'}
        expected_ngram_settings = {'horizontal': [1], 'vertical': [0], 'n': 2,
                                   'continuer': 'dynamic quality', 'mark singles': False,
                                   'terminator': 'Rest'}
        # four-part piece means 6 combinations for NGramIndexer, plus 2 calls to interval indexers
        self.assertEqual(8, test_pieces[test_index].get_data.call_count)
        exp_calls = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts)]
        for i in xrange(len(exp_calls)):
            self.assertEqual(test_pieces[test_index].get_data.mock_calls[i], exp_calls[i])
        # - that _run_off_rep() is called once for horizontal and vertical
        self.assertEqual(2, mock_ror.call_count)
        mock_ror.assert_any_call(test_index, vert_ret)
        mock_ror.assert_any_call(test_index, horiz_ret, is_horizontal=True)
        # - that each IndP.get_data() called NGramIndexer with the right settings at some point
        for combo in ror_vert_ret.iterkeys():
            test_pieces[1].get_data.assert_any_call([mock_ng],
                                                    expected_ngram_settings,
                                                    [ror_vert_ret[combo],
                                                    ror_horiz_ret[split_part_combo(combo)[1]]])
        self.assertSequenceEqual(expected, actual)


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INTERVAL_NGRAMS = TestLoader().loadTestsFromTestCase(IntervalNGrams)
INTERVALS = TestLoader().loadTestsFromTestCase(Intervals)
