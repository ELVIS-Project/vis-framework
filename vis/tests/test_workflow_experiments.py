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
from vis.analyzers.indexers import interval, noterest


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


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INTERVALS = TestLoader().loadTestsFromTestCase(Intervals)
