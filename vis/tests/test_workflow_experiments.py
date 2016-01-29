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
import six
if six.PY3:
    from unittest import mock
else:
    import mock
from mock import MagicMock
import pandas
from vis.workflow import WorkflowManager
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import interval, noterest, ngram


class Intervals(TestCase):
    """Tests for the WorkflowManager._intervs() experiment."""

    @mock.patch('vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch('vis.workflow.WorkflowManager._get_unique_combos')
    def test_intervs_1(self, mock_guc, mock_rfa, mock_rep):
        """Ensure _intervs() calls everything in the right order, with the right args & settings.
           This test uses all the default settings."""
        test_settings = {'simple or compound': 'compound', 'quality': False}
        test_pieces = [MagicMock(spec_set=IndexedPiece) for _ in range(3)]
        returns = ['get_data() {}'.format(i) for i in range(len(test_pieces))]
        for piece in test_pieces:
            piece.get_data.side_effect = lambda *x: returns.pop(0)
        expected = ['get_data() {}'.format(i) for i in range(len(test_pieces))]
        exp_analyzers = [noterest.NoteRestIndexer, interval.IntervalIndexer]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(None, 'include rests', True)
        actual = test_wc._intervs()  # pylint: disable=protected-access

        self.assertEqual(0, mock_guc.call_count)
        self.assertEqual(len(test_pieces), len(expected), len(actual))
        self.assertEqual(0, mock_rep.call_count)
        mock_rfa.assert_called_once_with('interval.IntervalIndexer')
        for piece in test_pieces:
            piece.get_data.assert_called_once_with(exp_analyzers, test_settings)
        for i in range(len(actual)):
            # NB: in real use, _run_freq_agg() would aggregate a piece's voice pairs and save it in
            #     self._result... but since that method's mocked out, we have to check here the
            #     return of each piece's get_data() call
            self.assertSequenceEqual(expected[i], actual[i])

    @mock.patch('vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch('vis.workflow.WorkflowManager._get_unique_combos')
    def test_intervs_2(self, mock_guc, mock_rfa, mock_rep):
        """Ensure _intervs() calls everything in the right order, with the right args & settings.
           Same as test_intervs_1() but:
              - calls _remove_extra_pairs(), and
              - doesn't call _run_freq_agg()."""
        mock_guc.return_value = [[0, 1]]
        voice_combos = str(mock_guc.return_value)
        exp_voice_combos = ['0,1']
        test_settings = {'simple or compound': 'compound', 'quality': False}
        test_pieces = [MagicMock(spec_set=IndexedPiece) for _ in range(3)]
        returns = ['get_data() {}'.format(i) for i in range(len(test_pieces))]
        for piece in test_pieces:
            piece.get_data.side_effect = lambda *x: returns.pop(0)
        exp_into_mock_rep = ['get_data() {}'.format(i) for i in range(len(test_pieces))]
        mock_rep_returns = ['IndP-{} no pairs'.format(i) for i in range(len(test_pieces))]
        mock_rep.side_effect = lambda *x: mock_rep_returns.pop(0)
        expected = ['IndP-{} no pairs'.format(i) for i in range(len(test_pieces))]
        exp_analyzers = [noterest.NoteRestIndexer, interval.IntervalIndexer]
        exp_mock_guc = [mock.call(i) for i in range(len(test_pieces))]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(None, 'include rests', True)
        test_wc.settings(None, 'count frequency', False)
        test_wc.settings(None, 'voice combinations', voice_combos)
        actual = test_wc._intervs()  # pylint: disable=protected-access

        self.assertSequenceEqual(exp_mock_guc, mock_guc.call_args_list)
        self.assertEqual(len(test_pieces), len(expected), len(actual))
        self.assertEqual(0, mock_rfa.call_count)
        self.assertEqual(len(test_pieces), mock_rep.call_count)
        for i in range(len(test_pieces)):
            mock_rep.assert_any_call(exp_into_mock_rep[i], exp_voice_combos)
        for piece in test_pieces:
            piece.get_data.assert_called_once_with(exp_analyzers, test_settings)
        for i in range(len(actual)):
            self.assertSequenceEqual(expected[i], actual[i])

    @mock.patch('vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch('vis.workflow.WorkflowManager._get_unique_combos')
    def test_intervs_3(self, mock_guc, mock_rfa, mock_rep):
        """Ensure _intervs() calls everything in the right order, with the right args & settings.
           This uses the default *except* requires removing rests, so it's more complex."""
        test_settings = {'simple or compound': 'compound', 'quality': False}
        test_pieces = [MagicMock(spec_set=IndexedPiece) for _ in range(3)]
        returns = [pandas.DataFrame([pandas.Series(['3', 'Rest', '5'])],
                                    index=[['interval.IntervalIndexer'], ['0,1']]).T
                   for i in range(len(test_pieces))]
        for piece in test_pieces:
            piece.get_data.side_effect = lambda *x: returns.pop(0)
        exp_series_ind = ('interval.IntervalIndexer', '0,1')
        expected_df = pandas.DataFrame({exp_series_ind: pandas.Series(['3', '5'], index=[0, 2])})
        exp_analyzers = [noterest.NoteRestIndexer, interval.IntervalIndexer]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(None, 'count frequency', False)
        actual = test_wc._intervs()  # pylint: disable=protected-access

        self.assertEqual(0, mock_guc.call_count)
        self.assertEqual(len(test_pieces), len(actual))
        self.assertEqual(0, mock_rfa.call_count)
        self.assertEqual(0, mock_rep.call_count)
        for piece in test_pieces:
            piece.get_data.assert_called_once_with(exp_analyzers, test_settings)
        for i in range(len(actual)):
            self.assertSequenceEqual(list(expected_df.columns), list(actual[i].columns))
            self.assertSequenceEqual(list(expected_df[exp_series_ind].index),
                                     list(actual[i][exp_series_ind].index))
            self.assertSequenceEqual(list(expected_df[exp_series_ind].values),
                                     list(actual[i][exp_series_ind].values))

    def test_intervs_4(self):
        """Ensure _intervs() fails when given an impossible 'voice pair'."""
        test_pieces = [MagicMock(spec_set=IndexedPiece) for _ in range(3)]
        returns = ['get_data() {}'.format(i) for i in range(len(test_pieces))]
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
            self.assertEqual(exp_err_msg, run_err.args[0])


class IntervalNGrams(TestCase):
    """Tests for helper functions related to the "interval n-grams" experiments."""

    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch('vis.workflow.WorkflowManager._variable_part_modules')
    @mock.patch('vis.workflow.WorkflowManager._all_part_modules')
    @mock.patch('vis.workflow.WorkflowManager._two_part_modules')
    def test_interval_ngrams_1(self, mock_two, mock_all, mock_var, mock_rfa):
        """test _interval_ngrams() with three pieces, each of which requires a different helper"""
        # 1.) prepare mocks
        ind_pieces = [MagicMock(spec_set=IndexedPiece) for _ in range(3)]
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
        actual = test_wm._interval_ngrams()  # pylint: disable=protected-access
        # 3.) verify the mocks
        # NB: in actual use, _run_freq_agg() would have the final say on the value of
        #     test_wm._result... but it's mocked out, which means we can test whether
        #     _interval_ngrams() puts the right stuff there
        mock_two.assert_called_once_with(1)
        mock_all.assert_called_once_with(0)
        mock_var.assert_called_once_with(2)
        mock_rfa.assert_called_once_with('ngram.NGramIndexer')
        self.assertSequenceEqual(expected, actual)
        self.assertSequenceEqual(expected, test_wm._result)  # pylint: disable=protected-access

    @mock.patch('vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch('vis.workflow.WorkflowManager._variable_part_modules')
    @mock.patch('vis.workflow.WorkflowManager._all_part_modules')
    @mock.patch('vis.workflow.WorkflowManager._two_part_modules')
    def test_interval_ngrams_2(self, mock_two, mock_all, mock_var, mock_rfa):
        """same as test_interval_ngrams_1(), but with "count frequency" set to False"""
        # 1.) prepare mocks
        ind_pieces = [MagicMock(spec_set=IndexedPiece) for _ in range(3)]
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
        actual = test_wm._interval_ngrams()  # pylint: disable=protected-access
        # 3.) verify the mocks
        # NB: in actual use, _run_freq_agg() would have the final say on the value of
        #     test_wm._result... but it's mocked out, which means we can test whether
        #     _interval_ngrams() puts the right stuff there
        self.assertEqual(3, len(test_wm._result))  # pylint: disable=protected-access
        for ret_val in expected:
            self.assertTrue(ret_val in test_wm._result)  # pylint: disable=protected-access
        mock_two.assert_called_once_with(1)
        mock_all.assert_called_once_with(0)
        mock_var.assert_called_once_with(2)
        self.assertEqual(0, mock_rfa.call_count)
        self.assertEqual(expected, actual)
        self.assertSequenceEqual(expected, test_wm._result)  # pylint: disable=protected-access

    @mock.patch('vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch('pandas.concat')
    @mock.patch('vis.workflow.WorkflowManager._get_unique_combos')
    def test_var_part_modules_1(self, mock_guc, mock_concat, mock_ror):
        """uses two two-part combinations"""
        # pylint: disable=line-too-long
        # inputs
        test_pieces = [MagicMock(spec_set=IndexedPiece)]
        test_pieces[0].get_data.side_effect = lambda *x: 'get_data({})'.format(x[0])
        selected_part_combos = [[0, 3], [2, 3]]
        mock_ror.return_value = 'mock_ror return'
        mock_concat.return_value = 'pandas.concat() return'
        test_index = 0
        mock_guc.return_value = selected_part_combos
        # expecteds
        expected = mock_concat.return_value
        # NB: this looks more complicated than it is; it's simply the calls we expect to get_data(),
        #     mock_ror, and mock_concat, in the order they should happen
        exp_calls = [mock.call([noterest.NoteRestIndexer]),
                     mock.call([interval.IntervalIndexer],
                               {'simple or compound': 'simple', 'quality': True,
                                'horiz_attach_later': True},
                               mock_ror.return_value),
                     mock.call([interval.HorizontalIntervalIndexer],
                               {'simple or compound': 'simple', 'quality': True,
                                'horiz_attach_later': True},
                               mock_ror.return_value),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '0,3')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '3')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               mock_concat.return_value),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '2,3')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '3')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               mock_concat.return_value)]
        exp_ror_calls = [mock.call(0, "get_data([<class 'vis.analyzers.indexers.noterest.NoteRestIndexer'>])")]
        exp_concat_calls = [mock.call(("get_data([<class 'vis.analyzers.indexers.interval.IntervalIndexer'>])",
                                       "get_data([<class 'vis.analyzers.indexers.interval.HorizontalIntervalIndexer'>])"), axis=1),
                            mock.call(["get_data([<class 'vis.analyzers.indexers.ngram.NGramIndexer'>])", "get_data([<class 'vis.analyzers.indexers.ngram.NGramIndexer'>])"], axis=1)]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(test_index, 'interval quality', True)
        test_wc.settings(test_index, 'simple intervals', True)
        test_wc.settings(test_index, 'filter repeats', False)
        test_wc.settings(test_index, 'offset interval', None)
        test_wc.settings(test_index, 'voice combinations', str(selected_part_combos))
        actual = test_wc._variable_part_modules(test_index)  # pylint: disable=protected-access

        mock_guc.assert_called_once_with(test_index)
        self.assertEqual(expected, actual)
        self.assertSequenceEqual(exp_calls, test_pieces[0].get_data.call_args_list)
        self.assertSequenceEqual(exp_ror_calls, mock_ror.call_args_list)
        self.assertSequenceEqual(exp_concat_calls, mock_concat.call_args_list)

    @mock.patch('vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch('pandas.concat')
    @mock.patch('vis.workflow.WorkflowManager._get_unique_combos')
    def test_var_part_modules_2(self, mock_guc, mock_concat, mock_ror):
        """uses two three-part combinations; do include rests"""
        # pylint: disable=line-too-long
        # inputs
        test_pieces = [MagicMock(spec_set=IndexedPiece)]
        test_pieces[0].get_data.side_effect = lambda *x: 'get_data({})'.format(x[0])
        selected_part_combos = [[0, 1, 2], [1, 2, 3]]  # different from test _1
        mock_ror.return_value = 'mock_ror return'
        mock_concat.return_value = 'pandas.concat() return'
        test_index = 0
        mock_guc.return_value = selected_part_combos
        # expecteds
        expected = mock_concat.return_value
        # NB: this looks more complicated than it is; it's simply the calls we expect to get_data(),
        #     mock_ror, and mock_concat, in the order they should happen
        exp_calls = [mock.call([noterest.NoteRestIndexer]),
                     mock.call([interval.IntervalIndexer],
                               {'simple or compound': 'simple', 'quality': True,
                                'horiz_attach_later': True},
                               mock_ror.return_value),
                     mock.call([interval.HorizontalIntervalIndexer],
                               {'simple or compound': 'simple', 'quality': True,
                                'horiz_attach_later': True},
                               mock_ror.return_value),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '0,2'),  # different from test _1
                                             ('interval.IntervalIndexer', '1,2')],  # different from test _1
                                'horizontal': [('interval.HorizontalIntervalIndexer', '2')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               mock_concat.return_value),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '1,3'),  # different from test _1
                                             ('interval.IntervalIndexer', '2,3')],  # different from test _1
                                'horizontal': [('interval.HorizontalIntervalIndexer', '3')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               mock_concat.return_value)]
        exp_ror_calls = [mock.call(0, "get_data([<class 'vis.analyzers.indexers.noterest.NoteRestIndexer'>])")]
        exp_concat_calls = [mock.call(("get_data([<class 'vis.analyzers.indexers.interval.IntervalIndexer'>])",
                                       "get_data([<class 'vis.analyzers.indexers.interval.HorizontalIntervalIndexer'>])"), axis=1),
                            mock.call(["get_data([<class 'vis.analyzers.indexers.ngram.NGramIndexer'>])", "get_data([<class 'vis.analyzers.indexers.ngram.NGramIndexer'>])"], axis=1)]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(test_index, 'interval quality', True)
        test_wc.settings(test_index, 'simple intervals', True)
        test_wc.settings(test_index, 'filter repeats', False)
        test_wc.settings(test_index, 'offset interval', None)
        test_wc.settings(test_index, 'voice combinations', str(selected_part_combos))
        actual = test_wc._variable_part_modules(test_index)  # pylint: disable=protected-access

        mock_guc.assert_called_once_with(test_index)
        self.assertEqual(expected, actual)
        self.assertSequenceEqual(exp_calls, test_pieces[0].get_data.call_args_list)
        self.assertSequenceEqual(exp_ror_calls, mock_ror.call_args_list)
        self.assertSequenceEqual(exp_concat_calls, mock_concat.call_args_list)

    @mock.patch('vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch('pandas.concat')
    def test_all_part_modules_1(self, mock_concat, mock_ror):
        """uses one all-part combination"""
        # pylint: disable=line-too-long
        # inputs
        test_pieces = [MagicMock(spec_set=IndexedPiece)]
        test_pieces[0].get_data.side_effect = lambda *x: 'get_data({})'.format(x[0])
        # this allows _all_part_modules() to know the part combinations we'll need
        test_pieces[0].metadata.return_value = ['Vl. I', 'Vl. II', 'Vla.', 'Vc.']
        mock_ror.return_value = 'mock_ror return'
        test_index = 0
        mock_concat.return_value = 'pandas.concat() return'
        # expecteds
        expected = "get_data([<class 'vis.analyzers.indexers.ngram.NGramIndexer'>])"
        # NB: this looks more complicated than it is; it's simply the calls we expect to get_data(),
        #     mock_ror, and mock_concat, in the order they should happen
        exp_calls = [mock.call([noterest.NoteRestIndexer]),
                     mock.call([interval.IntervalIndexer],
                               {'simple or compound': 'simple', 'quality': True,
                                'horiz_attach_later': True},
                               mock_ror.return_value),
                     mock.call([interval.HorizontalIntervalIndexer],
                               {'simple or compound': 'simple', 'quality': True,
                                'horiz_attach_later': True},
                               mock_ror.return_value),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '0,3'),
                                             ('interval.IntervalIndexer', '1,3'),
                                             ('interval.IntervalIndexer', '2,3')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '3')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               mock_concat.return_value)]
        exp_ror_calls = [mock.call(0, "get_data([<class 'vis.analyzers.indexers.noterest.NoteRestIndexer'>])")]
        exp_concat_calls = [mock.call(("get_data([<class 'vis.analyzers.indexers.interval.IntervalIndexer'>])",
                                       "get_data([<class 'vis.analyzers.indexers.interval.HorizontalIntervalIndexer'>])"), axis=1)]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(test_index, 'interval quality', True)
        test_wc.settings(test_index, 'simple intervals', True)
        test_wc.settings(test_index, 'filter repeats', False)
        test_wc.settings(test_index, 'offset interval', None)
        actual = test_wc._all_part_modules(test_index)  # pylint: disable=protected-access

        self.assertEqual(expected, actual)
        self.assertSequenceEqual(exp_calls, test_pieces[0].get_data.call_args_list)
        self.assertSequenceEqual(exp_ror_calls, mock_ror.call_args_list)
        self.assertSequenceEqual(exp_concat_calls, mock_concat.call_args_list)

    @mock.patch('vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch('pandas.concat')
    def test_two_part_modules_1(self, mock_concat, mock_ror):
        """uses all two-part combinations"""
        # pylint: disable=line-too-long
        # inputs
        test_pieces = [MagicMock(spec_set=IndexedPiece)]
        test_pieces[0].get_data.side_effect = lambda *x: 'get_data({})'.format(x[0])
        mock_ror.return_value = 'mock_ror return'
        test_index = 0
        # NB: this DataFrame replicates what would exist for a four-voice piece; we have to return
        #     a real DataFrame so that _two_part_modules() will loop appropriately
        piece_df = pandas.DataFrame([None for _ in range(6)],
                                    index=[['interval.IntervalIndexer' for _ in range(6)],
                                           ['0,1', '0,2', '0,3', '1,2', '1,3', '2,3']]).T
        mock_concat_returns = [piece_df, 'pandas.concat() return']
        mock_concat.side_effect = lambda df, axis: mock_concat_returns.pop(0)
        # expecteds
        expected = 'pandas.concat() return'
        # NB: this looks more complicated than it is; it's simply the calls we expect to get_data(),
        #     mock_ror, and mock_concat, in the order they should happen
        exp_calls = [mock.call([noterest.NoteRestIndexer]),
                     mock.call([interval.IntervalIndexer],
                               {'simple or compound': 'simple', 'quality': True,
                                'horiz_attach_later': True},
                               mock_ror.return_value),
                     mock.call([interval.HorizontalIntervalIndexer],
                               {'simple or compound': 'simple', 'quality': True,
                                'horiz_attach_later': True},
                               mock_ror.return_value),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '0,1')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '1')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               piece_df),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '0,2')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '2')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               piece_df),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '0,3')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '3')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               piece_df),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '1,2')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '2')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               piece_df),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '1,3')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '3')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               piece_df),
                     mock.call([ngram.NGramIndexer],
                               {'vertical': [('interval.IntervalIndexer', '2,3')],
                                'horizontal': [('interval.HorizontalIntervalIndexer', '3')],
                                'continuer': 'dynamic quality',
                                'n': 2,
                                'mark singles': False,
                                'terminator': 'Rest'},
                               piece_df)]
        exp_ror_calls = [mock.call(0, "get_data([<class 'vis.analyzers.indexers.noterest.NoteRestIndexer'>])")]
        exp_concat_calls = [mock.call(("get_data([<class 'vis.analyzers.indexers.interval.IntervalIndexer'>])",
                                       "get_data([<class 'vis.analyzers.indexers.interval.HorizontalIntervalIndexer'>])"), axis=1),
                            mock.call(["get_data([<class 'vis.analyzers.indexers.ngram.NGramIndexer'>])" for _ in range(6)], axis=1)]

        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(test_index, 'interval quality', True)
        test_wc.settings(test_index, 'simple intervals', True)
        test_wc.settings(test_index, 'filter repeats', False)
        test_wc.settings(test_index, 'offset interval', None)
        actual = test_wc._two_part_modules(test_index)  # pylint: disable=protected-access

        self.assertEqual(expected, actual)
        self.assertSequenceEqual(exp_calls, test_pieces[0].get_data.call_args_list)
        self.assertSequenceEqual(exp_ror_calls, mock_ror.call_args_list)
        self.assertSequenceEqual(exp_concat_calls, mock_concat.call_args_list)


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INTERVAL_NGRAMS = TestLoader().loadTestsFromTestCase(IntervalNGrams)
INTERVALS = TestLoader().loadTestsFromTestCase(Intervals)
