#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_workflow.py
# Purpose:                Tests for the WorkflowManager
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
from vis.workflow import WorkflowManager
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import interval


# pylint: disable=R0904
# pylint: disable=C0111
class Intervals(TestCase):
    @mock.patch(u'vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch(u'vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    def test_intervs_1(self, mock_int, mock_nri, mock_rfa, mock_ror):
        # --> test whether _intervs() calls all those things in the right order, with the right
        #     args, using all the default settings
        # 1.) prepare the test and mocks
        test_settings = {u'simple or compound': u'compound', u'quality': False}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        returns = [MagicMock(dict, name=u'get_data() piece' + str(i), return_value=[4]) \
                   for i in xrange(3)]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        mock_ror.return_value = [pandas.Series(['Rest', 'P5', 'm3']) for _ in xrange(len(test_pieces))]
        expected = [pandas.Series(['P5', 'm3'], index=[1, 2]) for _ in xrange(len(test_pieces))]
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        actual = test_wc._intervs()
        # 3.) confirm everything was called in the right order
        for piece in test_pieces:
            self.assertEqual(1, piece.get_data.call_count)
            piece.get_data.assert_called_once_with([mock_nri, mock_int], test_settings)
        self.assertEqual(len(test_pieces), mock_ror.call_count)
        mock_rfa.assert_called_once_with()
        self.assertEqual(len(test_pieces), len(expected), len(actual))
        for i in xrange(len(actual)):
            # NB: in real use, _run_freq_agg() would aggregate a piece's voice pairs, so we
            #     wouldn't need to ask for the [0] index here... but also, this experiment shouldn't
            #     call _run_freq_agg() anyway
            self.assertSequenceEqual(list(expected[i]), list(actual[i][0]))
            self.assertSequenceEqual(list(expected[i].index), list(actual[i][0].index))

    @mock.patch(u'vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch(u'vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch(u'vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    def test_intervs_2(self, mock_int, mock_nri, mock_rep, mock_rfa, mock_ror):
        # --> test whether _intervs() calls all those things in the right order, with specifying
        #     certain voice-pairs, keeping 'Rest' tokens, and not calling _run_freq_agg()
        # 1.) prepare the test and mocks
        test_settings = {u'simple or compound': u'compound', u'quality': False}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        the_dicts = [MagicMock(dict, name=u'get_data() piece' + str(i), return_value=[4]) \
                     for i in xrange(3)]
        returns = the_dicts
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        mock_ror.return_value = [pandas.Series(['Rest', 'P5', 'm3']) for _ in xrange(len(test_pieces))]
        expected = [pandas.Series(['Rest', 'P5', 'm3']) for _ in xrange(len(test_pieces))]
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        # (have to set the voice-pair settings)
        expected_pairs = [[0, 1], [0, 2]]
        for i in xrange(len(test_pieces)):
            test_wc._settings[i][u'voice combinations'] = unicode(expected_pairs)
        test_wc.settings(None, 'include rests', True)
        test_wc.settings(None, 'count frequency', False)
        actual = test_wc._intervs()
        # 3.) confirm everything was called in the right order
        self.assertEqual(len(test_pieces), mock_rep.call_count)
        for i in xrange(len(the_dicts)):
            mock_rep.assert_any_call(the_dicts[i], expected_pairs)
        for piece in test_pieces:
            piece.get_data.assert_called_once_with([mock_nri, mock_int], test_settings)
        self.assertEqual(len(test_pieces), mock_ror.call_count)
        self.assertEqual(0, mock_rfa.call_count)
        self.assertEqual(len(test_pieces), len(expected), len(actual))
        for i in xrange(len(actual)):
            # NB: in real use, _run_freq_agg() would aggregate a piece's voice pairs, so we
            #     wouldn't need to ask for the [0] index here... but also, this experiment shouldn't
            #     call _run_freq_agg() anyway
            self.assertSequenceEqual(list(expected[i]), list(actual[i][0]))
            self.assertSequenceEqual(list(expected[i].index), list(actual[i][0].index))

    @mock.patch(u'vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch(u'vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch(u'vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    def test_intervs_3(self, mock_int, mock_nri, mock_rep, mock_rfa, mock_ror):
        # --> test whether _intervs() when we specify an impossible voice pair ('[[0, 1, 2]]')
        # 1.) prepare the test and mocks
        test_settings = {u'simple or compound': u'compound', u'quality': False}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        the_dicts = [MagicMock(dict, name=u'get_data() piece' + str(i), return_value=[4]) \
                     for i in xrange(3)]
        returns = the_dicts
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        mock_ror.return_value = [pandas.Series(['Rest', 'P5', 'm3']) for _ in xrange(len(test_pieces))]
        expected = [pandas.Series(['Rest', 'P5', 'm3']) for _ in xrange(len(test_pieces))]
        expected_pairs = [[0, 1, 2]]
        expected_error_message = WorkflowManager._REQUIRE_PAIRS_ERROR % len(expected_pairs[0])
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        # (have to set the voice-pair settings)
        for i in xrange(len(test_pieces)):
            test_wc._settings[i][u'voice combinations'] = unicode(expected_pairs)
        # 3.) verify
        self.assertRaises(RuntimeError, test_wc._intervs)
        try:
            test_wc._intervs()
        except RuntimeError as runerr:
            self.assertEqual(expected_error_message, runerr.message)


class IntervalNGrams(TestCase):
    @mock.patch(u'vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch(u'vis.workflow.WorkflowManager._variable_part_modules')
    @mock.patch(u'vis.workflow.WorkflowManager._all_part_modules')
    @mock.patch(u'vis.workflow.WorkflowManager._two_part_modules')
    def test_interval_ngrams_1(self, mock_two, mock_all, mock_var, mock_rfa):
        # --> test with three pieces, each of which requires a different helper
        # 1.) prepare mocks
        ind_pieces = [MagicMock(spec=IndexedPiece) for _ in xrange(3)]
        mock_rfa.return_value = u'mock_rfa() return value'
        mock_two.return_value = [u'mock_two() return value']
        mock_all.return_value = [u'mock_all() return value']
        mock_var.return_value = [u'mock_var() return value']
        expected = [mock_all.return_value, mock_two.return_value, mock_var.return_value]
        # 2.) run the test
        test_wm = WorkflowManager(ind_pieces)
        test_wm.settings(0, u'voice combinations', u'all')
        test_wm.settings(1, u'voice combinations', u'all pairs')
        test_wm.settings(2, u'voice combinations', u'[[0, 1]]')
        actual = test_wm._interval_ngrams()
        # 3.) verify the mocks
        # NB: in actual use, _run_freq_agg() would have the final say on the value of
        #     test_wm._result... but it's mocked out, which means we can test whether
        #     _interval_ngrams() puts the right stuff there
        mock_two.assert_called_once_with(1)
        mock_all.assert_called_once_with(0)
        mock_var.assert_called_once_with(2)
        mock_rfa.assert_called_once_with()
        self.assertSequenceEqual(expected, actual)
        self.assertSequenceEqual(expected, test_wm._result)

    @mock.patch(u'vis.workflow.WorkflowManager._run_freq_agg')
    @mock.patch(u'vis.workflow.WorkflowManager._variable_part_modules')
    @mock.patch(u'vis.workflow.WorkflowManager._all_part_modules')
    @mock.patch(u'vis.workflow.WorkflowManager._two_part_modules')
    def test_interval_ngrams_2(self, mock_two, mock_all, mock_var, mock_rfa):
        # --> same as test_interval_ngrams_1(), but with "count frequency" set to False
        # 1.) prepare mocks
        ind_pieces = [MagicMock(spec=IndexedPiece) for _ in xrange(3)]
        mock_rfa.return_value = u'mock_rfa() return value'
        mock_two.return_value = [u'mock_two() return value']
        mock_all.return_value = [u'mock_all() return value']
        mock_var.return_value = [u'mock_var() return value']
        expected = [mock_all.return_value, mock_two.return_value, mock_var.return_value]
        # 2.) run the test
        test_wm = WorkflowManager(ind_pieces)
        test_wm.settings(0, u'voice combinations', u'all')
        test_wm.settings(1, u'voice combinations', u'all pairs')
        test_wm.settings(2, u'voice combinations', u'[[0, 1]]')
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

    @mock.patch(u'vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    def test_var_part_modules_1(self, mock_int, mock_nri, mock_ng, mock_horiz, mock_ror):
        # - we'll only use self._data[1]; excluding "Rest"
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up the mock_ror return values (i.e., what came out of the IntervalIndexer)
        all_part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        selected_part_combos = [[0, 3], [2, 3]]
        ror_vert_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in all_part_combos}
        ror_horiz_ret = [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)]
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
        returns = [vert_ret, horiz_ret, [u'piece2 3rd get_data()'], [u'piece2 4th get_data()']]
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
        test_wc.settings(test_index, u'interval quality', True)
        test_wc.settings(test_index, u'simple intervals', True)
        test_wc.settings(test_index, u'filter repeats', False)
        test_wc.settings(test_index, u'offset interval', None)
        test_wc.settings(test_index, u'voice combinations', unicode(selected_part_combos))
        actual = test_wc._variable_part_modules(test_index)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': True, u'simple or compound': u'simple'}
        expected_ngram_settings = {u'horizontal': [1], u'vertical': [0], u'n': 2,
                                   u'continuer': 'dynamic quality', u'mark singles': False,
                                   u'terminator': u'Rest'}
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
            zombo = str(combo[0]) + u',' + str(combo[1])
            test_pieces[1].get_data.assert_any_call([mock_ng],
                                                    expected_ngram_settings,
                                                    [ror_vert_ret[zombo],
                                                    ror_horiz_ret[combo[1]]])
        self.assertEqual(expected, actual)

    @mock.patch(u'vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    def test_var_part_modules_2(self, mock_int, mock_nri, mock_ng, mock_horiz, mock_ror):
        # - we'll only use self._data[1]; including "Rest"
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        all_part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        selected_part_combos = [[0, 1, 2], [1, 2, 3]]
        ror_vert_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in all_part_combos}
        ror_horiz_ret = [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)]
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
        returns = [vert_ret, horiz_ret, [u'piece2 3rd get_data()'], [u'piece2 4th get_data()']]
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
        test_wc.settings(test_index, u'interval quality', True)
        test_wc.settings(test_index, u'simple intervals', True)
        test_wc.settings(test_index, u'filter repeats', False)
        test_wc.settings(test_index, u'offset interval', None)
        test_wc.settings(test_index, u'voice combinations', unicode(selected_part_combos))
        test_wc.settings(None, u'include rests', True)
        actual = test_wc._variable_part_modules(test_index)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': True, u'simple or compound': u'simple'}
        expected_ngram_settings = {u'horizontal': [2], u'vertical': [0, 1], u'n': 2, \
                                   u'continuer': 'dynamic quality', u'mark singles': False}
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
            parts = [ror_vert_ret[str(i) + u',' + str(combo[-1])] for i in combo[:-1]]
            parts.append(ror_horiz_ret[combo[-1]])
            test_pieces[1].get_data.assert_any_call([mock_ng],
                                                    expected_ngram_settings,
                                                    parts)
        self.assertEqual(expected, actual)

    @mock.patch(u'vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    def test_all_part_modules_1(self, mock_int, mock_nri, mock_ng, mock_horiz, mock_ror):
        # - we'll only use self._data[1]; excluding "Rest"
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up pseudo-IntervalIndexer results for mock_ror
        ror_vert_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in [u'0,3', u'1,3', u'2,3']}
        ror_horiz_ret = [None, None, None, MagicMock(name=u'piece1 horiz')]
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
        test_wc.settings(test_index, u'interval quality', True)
        test_wc.settings(test_index, u'simple intervals', True)
        test_wc.settings(test_index, u'filter repeats', False)
        test_wc.settings(test_index, u'offset interval', None)
        actual = test_wc._all_part_modules(test_index)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': True, u'simple or compound': u'simple'}
        expected_ngram_settings = {u'horizontal': [3], u'vertical': [0, 1, 2], u'n': 2,
                                   u'continuer': 'dynamic quality', u'mark singles': False,
                                   u'terminator': u'Rest'}
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
                              [ror_vert_ret[u'0,3'],
                               ror_vert_ret[u'1,3'],
                               ror_vert_ret[u'2,3'],
                               ror_horiz_ret[3]])]
        for i in xrange(len(exp_calls)):
            self.assertEqual(test_pieces[test_index].get_data.mock_calls[i], exp_calls[i])
        self.assertEqual(expected, actual)

    @mock.patch(u'vis.workflow.WorkflowManager._run_off_rep')
    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    def test_two_part_modules_1(self, mock_int, mock_nri, mock_ng, mock_horiz, mock_ror):
        # - we'll only use self._data[1]; excluding "Rest"
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up pseudo-IntervalIndexer results for mock_ror
        part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        ror_vert_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in part_combos}
        ror_horiz_ret = [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)]
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
        returns = [vert_ret, horiz_ret, [u'piece2 3rd get_data()'], [u'piece2 4th get_data()'],
                   [u'piece2 5th get_data()'], [u'piece2 6th get_data()'], [u'piece2 7th get_data()'],
                   [u'piece2 8th get_data()']]
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
        test_wc.settings(test_index, u'interval quality', True)
        test_wc.settings(test_index, u'simple intervals', True)
        test_wc.settings(test_index, u'filter repeats', False)
        test_wc.settings(test_index, u'offset interval', None)
        actual = test_wc._two_part_modules(test_index)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': True, u'simple or compound': u'simple'}
        expected_ngram_settings = {u'horizontal': [1], u'vertical': [0], u'n': 2,
                                   u'continuer': 'dynamic quality', u'mark singles': False,
                                   u'terminator': u'Rest'}
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
                                                    ror_horiz_ret[interval.key_to_tuple(combo)[1]]])
        self.assertSequenceEqual(expected, actual)


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INTERVAL_NGRAMS = TestLoader().loadTestsFromTestCase(IntervalNGrams)
INTERVALS = TestLoader().loadTestsFromTestCase(Intervals)
