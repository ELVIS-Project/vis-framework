#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_workflow.py
# Purpose:                Tests for the WorkflowManager
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
Tests for the WorkflowManager
"""

from unittest import TestCase, TestLoader
import mock
from mock import MagicMock
import pandas
from vis.workflow import WorkflowManager
from vis.models.indexed_piece import IndexedPiece
from vis.models.aggregated_pieces import AggregatedPieces
from vis.analyzers.indexers import noterest, interval


# pylint: disable=R0904
# pylint: disable=C0111
class WorkflowTests(TestCase):
    def test_init_1(self):
        # with a list of basestrings
        with mock.patch(u'vis.models.indexed_piece.IndexedPiece') as mock_ip:
            in_val = [u'help.txt', 'path.xml', u'why_you_do_this.rtf']
            test_wc = WorkflowManager(in_val)
            self.assertEqual(3, mock_ip.call_count)
            for val in in_val:
                mock_ip.assert_any_call(val)
            self.assertEqual(3, len(test_wc._data))
            for each in test_wc._data:
                self.assertTrue(isinstance(each, mock.MagicMock))
            self.assertEqual(3, len(test_wc._settings))
            for piece_sett in test_wc._settings:
                self.assertEqual(5, len(piece_sett))
                for sett in [u'offset interval', u'voice combinations']:
                    self.assertEqual(None, piece_sett[sett])
                for sett in [u'filter repeats', u'interval quality', u'simple intervals']:
                    self.assertEqual(False, piece_sett[sett])

    def test_init_2(self):
        # with a list of IndexedPieces
        in_val = [IndexedPiece(u'help.txt'), IndexedPiece('path.xml'),
                  IndexedPiece(u'why_you_do_this.rtf')]
        test_wc = WorkflowManager(in_val)
        self.assertEqual(3, len(test_wc._data))
        for each in test_wc._data:
            self.assertTrue(each in in_val)
        for piece_sett in test_wc._settings:
            self.assertEqual(5, len(piece_sett))
            for sett in [u'offset interval', u'voice combinations']:
                self.assertEqual(None, piece_sett[sett])
            for sett in [u'filter repeats', u'interval quality', u'simple intervals']:
                self.assertEqual(False, piece_sett[sett])

    def test_init_3(self):
        # with a mixed list of valid things
        in_val = [IndexedPiece(u'help.txt'), 'path.xml', u'why_you_do_this.rtf']
        test_wc = WorkflowManager(in_val)
        self.assertEqual(3, len(test_wc._data))
        self.assertEqual(in_val[0], test_wc._data[0])
        for each in test_wc._data[1:]:
            self.assertTrue(isinstance(each, IndexedPiece))
        for piece_sett in test_wc._settings:
            self.assertEqual(5, len(piece_sett))
            for sett in [u'offset interval', u'voice combinations']:
                self.assertEqual(None, piece_sett[sett])
            for sett in [u'filter repeats', u'interval quality', u'simple intervals']:
                self.assertEqual(False, piece_sett[sett])

    def test_init_4(self):
        # with mostly basestrings but a few ints
        in_val = [u'help.txt', 'path.xml', 4, u'why_you_do_this.rtf']
        test_wc = WorkflowManager(in_val)
        self.assertEqual(3, len(test_wc._data))
        for each in test_wc._data:
            self.assertTrue(isinstance(each, IndexedPiece))
        for piece_sett in test_wc._settings:
            self.assertEqual(5, len(piece_sett))
            for sett in [u'offset interval', u'voice combinations']:
                self.assertEqual(None, piece_sett[sett])
            for sett in [u'filter repeats', u'interval quality', u'simple intervals']:
                self.assertEqual(False, piece_sett[sett])

    def test_load_1(self):
        # that "get_data" is called correctly on each thing
        test_wc = WorkflowManager([])
        test_wc._data = [mock.MagicMock(spec=IndexedPiece) for _ in xrange(5)]
        test_wc.load(u'pieces')
        for mock_piece in test_wc._data:
            mock_piece.get_data.assert_called_once_with([noterest.NoteRestIndexer])

    def test_load_2(self):
        # that the not-yet-implemented instructions raise NotImplementedError
        test_wc = WorkflowManager([])
        self.assertRaises(NotImplementedError, test_wc.load, u'hdf5')
        self.assertRaises(NotImplementedError, test_wc.load, u'stata')
        self.assertRaises(NotImplementedError, test_wc.load, u'pickle')

    def test_run_1(self):
        mock_path = u'vis.workflow.WorkflowManager._intervs'
        with mock.patch(mock_path) as mock_meth:
            mock_meth.return_value = u'the final countdown'
            test_wc = WorkflowManager([])
            test_wc.run(u'all-combinations intervals', 42)
            mock_meth.assert_called_once_with(42)
            self.assertEqual(mock_meth.return_value, test_wc._result)

    def test_run_2(self):
        mock_path = u'vis.workflow.WorkflowManager._two_part_modules'
        with mock.patch(mock_path) as mock_meth:
            mock_meth.return_value = u'the final countdown'
            test_wc = WorkflowManager([])
            test_wc.run(u'all 2-part interval n-grams', 42)
            mock_meth.assert_called_once_with(42)
            self.assertEqual(mock_meth.return_value, test_wc._result)

    def test_run_3(self):
        mock_path = u'vis.workflow.WorkflowManager._all_part_modules'
        with mock.patch(mock_path) as mock_meth:
            mock_meth.return_value = u'the final countdown'
            test_wc = WorkflowManager([])
            test_wc.run(u'all-voice interval n-grams', 42)
            mock_meth.assert_called_once_with(42)
            self.assertEqual(mock_meth.return_value, test_wc._result)

    def test_run_4(self):
        mock_path_a = u'vis.workflow.WorkflowManager._two_part_modules'
        mock_path_b = u'vis.workflow.WorkflowManager._for_sc'
        with mock.patch(mock_path_a) as mock_meth_a:
            with mock.patch(mock_path_b) as mock_meth_b:
                mock_meth_a.return_value = 1200
                mock_meth_b.return_value = u'the final countdown'
                test_wc = WorkflowManager([])
                test_wc.run(u'all 2-part interval n-grams for SuperCollider', 42)
                mock_meth_a.assert_called_once_with(42)
                mock_meth_b.assert_called_once_with(mock_meth_a.return_value)
                self.assertEqual(mock_meth_b.return_value, test_wc._result)

    def test_run_6(self):
        test_wc = WorkflowManager([])
        self.assertRaises(RuntimeError, test_wc.run, u'too short')
        self.assertRaises(RuntimeError, test_wc.run, u'this just is not an instruction you know')

    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.workflow.AggregatedPieces')
    def test_intervs_1(self, mock_ap, mock_agg, mock_freq, mock_int, mock_nri):
        # mock NoteRestIndexer, IntervalIndexer, FrequencyExperimenter, ColumnAggregator,
        #      IndexedPiece, AggregatedPieces
        # test whether _intervs() calls all those things in the right order, with the right args
        # 1.) prepare the test and mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        ap_getdata_ret = MagicMock()
        ap_inst.get_data.return_value = ap_getdata_ret
        test_settings = {u'a setting': u'its value', u'other setting': u'so crazy!'}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        returns = [MagicMock(dict, name=u'piece1 1st get_data()'), u'piece1 2nd get_data()',
                   MagicMock(dict, name=u'piece2 1st get_data()'), u'piece2 2nd get_data()',
                   MagicMock(dict, name=u'piece3 1st get_data()'), u'piece3 2nd get_data()']
        ap_ret = [u'piece1 2nd get_data()', u'piece2 2nd get_data()', u'piece3 2nd get_data()']
        for i in [0, 2, 4]:
            returns[i].itervalues.return_value = [4]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        actual = test_wc._intervs(test_settings)
        # 3.) confirm everything was called in the right order
        for piece in test_pieces:
            self.assertEqual(2, piece.get_data.call_count)
            expected = [mock.call([mock_nri, mock_int], test_settings),
                        mock.call([mock_freq, mock_agg], {}, [4])]
            self.assertEqual(piece.get_data.mock_calls, expected)
        mock_ap.assert_called_once_with(test_pieces)
        ap_inst.get_data.assert_called_once_with([mock_agg], None, {}, ap_ret)
        self.assertEqual(ap_getdata_ret, actual)
        ap_getdata_ret.sort.assert_called_once_with(ascending=False)

    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.workflow.AggregatedPieces')
    def test_all_part_modules_1(self, mock_ap, mock_agg, mock_freq, mock_int, mock_nri, mock_ng, \
                                mock_horiz):
        # test without the "mark singles" and "continuer" settings
        # 1.) prepare the test and mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        ap_getdata_ret = MagicMock()
        ap_inst.get_data.return_value = ap_getdata_ret
        test_settings = {u'a setting': u'its value', u'n': 2}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        intind_ret = [{x: MagicMock(name=u'piece1 part ' + x) for x in [u'0,3', u'1,3', u'2,3']},
                      {x: MagicMock(name=u'piece2 part ' + x) for x in [u'0,3', u'1,3', u'2,3']},
                      {x: MagicMock(name=u'piece3 part ' + x) for x in [u'0,3', u'1,3', u'2,3']}]
        horiz_ret = [[None, None, None, MagicMock(name=u'piece1 horiz')],
                     [None, None, None, MagicMock(name=u'piece2 horiz')],
                     [None, None, None, MagicMock(name=u'piece3 horiz')]]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret[0], horiz_ret[0], u'piece1 3rd get_data()',
                   intind_ret[1], horiz_ret[1], u'piece2 3rd get_data()',
                   intind_ret[2], horiz_ret[2], u'piece3 3rd get_data()']
        ap_ret = [returns[2], returns[5], returns[8]]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        actual = test_wc._all_part_modules(test_settings)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_ngram_settings = {u'horizontal': [3], u'vertical': [0, 1, 2], u'n': 2}
        for i, piece in enumerate(test_pieces):
            self.assertEqual(3, piece.get_data.call_count)
            expected = [mock.call([mock_nri, mock_int], test_settings),
                        mock.call([mock_nri, mock_horiz], test_settings),
                        mock.call([mock_ng, mock_freq], mock.ANY, mock.ANY)]
            self.assertEqual(piece.get_data.mock_calls, expected)
            # - that each IndP.get_data() has the right settings for its call with NGramIndexer
            expected_call = mock.call([mock_ng, mock_freq],
                                      expected_ngram_settings,
                                      [intind_ret[i][u'0,3'],
                                       intind_ret[i][u'1,3'],
                                       intind_ret[i][u'2,3'],
                                       horiz_ret[i][3]])
            self.assertEqual(expected_call, piece.get_data.mock_calls[2])
        # - an AggP is created with the right IndPs, then called with ColumnAggregator, then sorted
        mock_ap.assert_called_once_with(test_pieces)
        ap_inst.get_data.assert_called_once_with([mock_agg], None, {}, ap_ret)
        self.assertEqual(ap_getdata_ret, actual)
        ap_getdata_ret.sort.assert_called_once_with(ascending=False)

    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.workflow.AggregatedPieces')
    def test_all_part_modules_2(self, mock_ap, mock_agg, mock_freq, mock_int, mock_nri, mock_ng, \
                                mock_horiz):
        # test with the "mark singles" and "continuer" settings
        # 1.) prepare the test and mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        ap_getdata_ret = MagicMock()
        ap_inst.get_data.return_value = ap_getdata_ret
        test_settings = {u'a setting': u'its value', u'n': 2, u'mark singles': False,
                         u'continuer': u':('}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        intind_ret = [{x: MagicMock(name=u'piece1 part ' + x) for x in [u'0,3', u'1,3', u'2,3']},
                      {x: MagicMock(name=u'piece2 part ' + x) for x in [u'0,3', u'1,3', u'2,3']},
                      {x: MagicMock(name=u'piece3 part ' + x) for x in [u'0,3', u'1,3', u'2,3']}]
        horiz_ret = [[None, None, None, MagicMock(name=u'piece1 horiz')],
                     [None, None, None, MagicMock(name=u'piece2 horiz')],
                     [None, None, None, MagicMock(name=u'piece3 horiz')]]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret[0], horiz_ret[0], u'piece1 3rd get_data()',
                   intind_ret[1], horiz_ret[1], u'piece2 3rd get_data()',
                   intind_ret[2], horiz_ret[2], u'piece3 3rd get_data()']
        ap_ret = [returns[2], returns[5], returns[8]]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        actual = test_wc._all_part_modules(test_settings)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_ngram_settings = {u'horizontal': [3], u'vertical': [0, 1, 2], u'n': 2,
                                   u'mark singles': False, u'continuer': u':('}
        for i, piece in enumerate(test_pieces):
            self.assertEqual(3, piece.get_data.call_count)
            expected = [mock.call([mock_nri, mock_int], test_settings),
                        mock.call([mock_nri, mock_horiz], test_settings),
                        mock.call([mock_ng, mock_freq], mock.ANY, mock.ANY)]
            self.assertEqual(piece.get_data.mock_calls, expected)
            # - that each IndP.get_data() has the right settings for its call with NGramIndexer
            expected_call = mock.call([mock_ng, mock_freq],
                                      expected_ngram_settings,
                                      [intind_ret[i][u'0,3'],
                                       intind_ret[i][u'1,3'],
                                       intind_ret[i][u'2,3'],
                                       horiz_ret[i][3]])
            self.assertEqual(expected_call, piece.get_data.mock_calls[2])
        # - an AggP is created with the right IndPs, then called with ColumnAggregator, then sorted
        mock_ap.assert_called_once_with(test_pieces)
        ap_inst.get_data.assert_called_once_with([mock_agg], None, {}, ap_ret)
        self.assertEqual(ap_getdata_ret, actual)
        ap_getdata_ret.sort.assert_called_once_with(ascending=False)

    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.workflow.AggregatedPieces')
    def test_two_part_modules_1(self, mock_ap, mock_agg, mock_freq, mock_int, mock_nri, mock_ng, \
                                mock_horiz):
        # test without the "mark singles" and "continuer" settings
        # 1.) prepare the test and mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        ap_getdata_ret = MagicMock()
        ap_inst.get_data.return_value = ap_getdata_ret
        test_settings = {u'a setting': u'its value', u'n': 2}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        intind_ret = [{x: MagicMock(name=u'piece1 part ' + x) for x in part_combos},
                      {x: MagicMock(name=u'piece2 part ' + x) for x in part_combos},
                      {x: MagicMock(name=u'piece3 part ' + x) for x in part_combos}]
        horiz_ret = [[MagicMock(name=u'piece1 horiz ' + str(x)) for x in xrange(4)],
                     [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)],
                     [MagicMock(name=u'piece3 horiz ' + str(x)) for x in xrange(4)]]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret[0], horiz_ret[0], u'piece1 3rd get_data()', u'piece1 4th get_data()',
                   u'piece1 5th get_data()', u'piece1 6th get_data()', u'piece1 7th get_data()',
                   u'piece1 8thd get_data()',
                   intind_ret[1], horiz_ret[1], u'piece2 3rd get_data()', u'piece2 4th get_data()',
                   u'piece2 5th get_data()', u'piece2 6th get_data()', u'piece2 7th get_data()',
                   u'piece2 8thd get_data()',
                   intind_ret[2], horiz_ret[2], u'piece3 3rd get_data()', u'piece3 4th get_data()',
                   u'piece3 5th get_data()', u'piece3 6th get_data()', u'piece3 7th get_data()',
                   u'piece3 8thd get_data()']
        ap_ret = []
        for i in xrange(len(returns)):
            if isinstance(returns[i], unicode):
                ap_ret.append(returns[i])
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        actual = test_wc._two_part_modules(test_settings)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_ngram_settings = {u'horizontal': [1], u'vertical': [0], u'n': 2}
        for i, piece in enumerate(test_pieces):
            self.assertEqual(8, piece.get_data.call_count)
            expected = [mock.call([mock_nri, mock_int], test_settings),
                        mock.call([mock_nri, mock_horiz], test_settings)]
            self.assertEqual(piece.get_data.mock_calls[0], expected[0])
            self.assertEqual(piece.get_data.mock_calls[1], expected[1])
            # - that each IndP.get_data() called NGramIndexer with the right settings at some point
            for combo in intind_ret[i].iterkeys():
                piece.get_data.assert_any_call([mock_ng, mock_freq],
                                               expected_ngram_settings,
                                               [intind_ret[i][combo],
                                               horiz_ret[i][interval.key_to_tuple(combo)[1]]])
        # - an AggP is created with the right IndPs, then called with ColumnAggregator, then sorted
        mock_ap.assert_called_once_with(test_pieces)
        ap_inst.get_data.assert_called_once_with([mock_agg], None, {}, ap_ret)
        self.assertEqual(ap_getdata_ret, actual)
        ap_getdata_ret.sort.assert_called_once_with(ascending=False)

    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.workflow.AggregatedPieces')
    def test_two_part_modules_2(self, mock_ap, mock_agg, mock_freq, mock_int, mock_nri, mock_ng, \
                                mock_horiz):
        # test with the "mark singles" and "continuer" settings
        # 1.) prepare the test and mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        ap_getdata_ret = MagicMock()
        ap_inst.get_data.return_value = ap_getdata_ret
        test_settings = {u'a setting': u'its value', u'n': 2, u'mark singles': False,
                         u'continuer': u':('}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        intind_ret = [{x: MagicMock(name=u'piece1 part ' + x) for x in part_combos},
                      {x: MagicMock(name=u'piece2 part ' + x) for x in part_combos},
                      {x: MagicMock(name=u'piece3 part ' + x) for x in part_combos}]
        horiz_ret = [[MagicMock(name=u'piece1 horiz ' + str(x)) for x in xrange(4)],
                     [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)],
                     [MagicMock(name=u'piece3 horiz ' + str(x)) for x in xrange(4)]]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret[0], horiz_ret[0], u'piece1 3rd get_data()', u'piece1 4th get_data()',
                   u'piece1 5th get_data()', u'piece1 6th get_data()', u'piece1 7th get_data()',
                   u'piece1 8thd get_data()',
                   intind_ret[1], horiz_ret[1], u'piece2 3rd get_data()', u'piece2 4th get_data()',
                   u'piece2 5th get_data()', u'piece2 6th get_data()', u'piece2 7th get_data()',
                   u'piece2 8thd get_data()',
                   intind_ret[2], horiz_ret[2], u'piece3 3rd get_data()', u'piece3 4th get_data()',
                   u'piece3 5th get_data()', u'piece3 6th get_data()', u'piece3 7th get_data()',
                   u'piece3 8thd get_data()']
        ap_ret = []
        for i in xrange(len(returns)):
            if isinstance(returns[i], unicode):
                ap_ret.append(returns[i])
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        actual = test_wc._two_part_modules(test_settings)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_ngram_settings = {u'horizontal': [1], u'vertical': [0], u'n': 2}
        expected_ngram_settings[u'continuer'] = test_settings[u'continuer']
        expected_ngram_settings[u'mark singles'] = test_settings[u'mark singles']
        for i, piece in enumerate(test_pieces):
            self.assertEqual(8, piece.get_data.call_count)
            expected = [mock.call([mock_nri, mock_int], test_settings),
                        mock.call([mock_nri, mock_horiz], test_settings)]
            self.assertEqual(piece.get_data.mock_calls[0], expected[0])
            self.assertEqual(piece.get_data.mock_calls[1], expected[1])
            # - that each IndP.get_data() called NGramIndexer with the right settings at some point
            for combo in intind_ret[i].iterkeys():
                piece.get_data.assert_any_call([mock_ng, mock_freq],
                                               expected_ngram_settings,
                                               [intind_ret[i][combo],
                                               horiz_ret[i][interval.key_to_tuple(combo)[1]]])
        # - an AggP is created with the right IndPs, then called with ColumnAggregator, then sorted
        mock_ap.assert_called_once_with(test_pieces)
        ap_inst.get_data.assert_called_once_with([mock_agg], None, {}, ap_ret)
        self.assertEqual(ap_getdata_ret, actual)
        ap_getdata_ret.sort.assert_called_once_with(ascending=False)

    def test_output_1(self):
        test_wc = WorkflowManager([])
        self.assertRaises(NotImplementedError, test_wc.output, u'LilyPond')

    def test_output_2(self):
        test_wc = WorkflowManager([])
        self.assertRaises(RuntimeError, test_wc.output, u'LJKDSFLAESFLKJ')

    def test_output_3(self):
        # with self._result as None
        test_wc = WorkflowManager([])
        self.assertRaises(RuntimeError, test_wc.output, u'R histogram')

    @mock.patch(u'pandas.DataFrame')
    @mock.patch(u'subprocess.call')
    def test_output_4(self, mock_call, mock_df):
        # with specified pathname
        test_wc = WorkflowManager([])
        test_wc._result = pandas.Series([x for x in xrange(10)])
        path = u'pathname!'
        actual = test_wc.output(u'R histogram', path)
        mock_df.assert_called_once_with({u'freq': test_wc._result})
        expected_args = [u'R', u'--vanilla', u'-f', u'R_script.r', u'--args', path + u'.dta',
                         path + u'.png']
        mock_call.assert_called_once_with(expected_args)
        self.assertEqual(path + u'.png', actual)

    @mock.patch(u'pandas.DataFrame')
    @mock.patch(u'subprocess.call')
    def test_output_5(self, mock_call, mock_df):
        # with unspecified pathname
        test_wc = WorkflowManager([])
        test_wc._result = pandas.Series([x for x in xrange(10)])
        path = u'test_output/output_result'
        actual = test_wc.output(u'R histogram')
        mock_df.assert_called_once_with({u'freq': test_wc._result})
        expected_args = [u'R', u'--vanilla', u'-f', u'R_script.r', u'--args', path + u'.dta',
                         path + u'.png']
        mock_call.assert_called_once_with(expected_args)
        self.assertEqual(path + u'.png', actual)

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_1(self, mock_ip):
        # - if index is None and value are None, raise ValueError
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        self.assertRaises(ValueError, test_wm.settings, None, u'interval quality', None)
        self.assertRaises(ValueError, test_wm.settings, None, u'interval quality')

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_2(self, mock_ip):
        # - if index is None, field and value are valid, it'll set for all IPs
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        test_wm.settings(None, u'interval quality', True)
        for i in xrange(3):
            self.assertEqual(True, test_wm._settings[i][u'interval quality'])

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_3(self, mock_ip):
        # - if index is less than 0 or greater-than-valid, raise IndexError
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        self.assertRaises(IndexError, test_wm.settings, -1, u'interval quality')
        self.assertRaises(IndexError, test_wm.settings, 20, u'interval quality')

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_4(self, mock_ip):
        # - if index is 0, return proper setting
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        test_wm._settings[0][u'interval quality'] = u'cheese'
        self.assertEqual(u'cheese', test_wm.settings(0, u'interval quality'))

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_5(self, mock_ip):
        # - if index is greater than 0 but valid, set proper setting
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        test_wm.settings(1, u'interval quality', u'leeks')
        self.assertEqual(u'leeks', test_wm._settings[1][u'interval quality'])

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_6(self, mock_ip):
        # - if index is valid but the setting isn't, raise AttributeError (with or without a value)
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        self.assertRaises(AttributeError, test_wm.settings, 1, u'drink wine')
        self.assertRaises(AttributeError, test_wm.settings, 1, u'drink wine', True)

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
WORKFLOW_TESTS = TestLoader().loadTestsFromTestCase(WorkflowTests)
