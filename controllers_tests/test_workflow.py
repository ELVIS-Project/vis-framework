#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_workflow.py
# Purpose:                Tests for the WorkflowController
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
Tests for the WorkflowController
"""

from unittest import TestCase, TestLoader
import mock
from mock import MagicMock
from vis.controllers.workflow import WorkflowController
from vis.models.indexed_piece import IndexedPiece
from vis.models.aggregated_pieces import AggregatedPieces
from vis.analyzers.indexers import noterest


# pylint: disable=R0904
# pylint: disable=C0111
class WorkflowTests(TestCase):
    def test_init_1(self):
        # with a list of basestrings
        with mock.patch(u'vis.models.indexed_piece.IndexedPiece') as mock_ip:
            in_val = [u'help.txt', 'path.xml', u'why_you_do_this.rtf']
            test_wc = WorkflowController(in_val)
            self.assertEqual(3, mock_ip.call_count)
            for val in in_val:
                mock_ip.assert_any_call(val)
            self.assertEqual(3, len(test_wc._data))
            for each in test_wc._data:
                self.assertTrue(isinstance(each, mock.MagicMock))

    def test_init_2(self):
        # with a list of IndexedPieces
        in_val = [IndexedPiece(u'help.txt'), IndexedPiece('path.xml'),
                  IndexedPiece(u'why_you_do_this.rtf')]
        test_wc = WorkflowController(in_val)
        self.assertEqual(3, len(test_wc._data))
        for each in test_wc._data:
            self.assertTrue(each in in_val)

    def test_init_3(self):
        # with a mixed list of valid things
        in_val = [IndexedPiece(u'help.txt'), 'path.xml', u'why_you_do_this.rtf']
        test_wc = WorkflowController(in_val)
        self.assertEqual(3, len(test_wc._data))
        self.assertEqual(in_val[0], test_wc._data[0])
        for each in test_wc._data[1:]:
            self.assertTrue(isinstance(each, IndexedPiece))

    def test_init_4(self):
        # with mostly basestrings but a few ints
        in_val = [u'help.txt', 'path.xml', 4, u'why_you_do_this.rtf']
        test_wc = WorkflowController(in_val)
        self.assertEqual(3, len(test_wc._data))
        for each in test_wc._data:
            self.assertTrue(isinstance(each, IndexedPiece))

    def test_load_1(self):
        # that "get_data" is called correctly on each thing
        test_wc = WorkflowController([])
        test_wc._data = [mock.MagicMock(spec=IndexedPiece) for _ in xrange(5)]
        test_wc.load(u'pieces')
        for mock_piece in test_wc._data:
            mock_piece.get_data.assert_called_once_with([noterest.NoteRestIndexer])

    def test_load_2(self):
        # that the not-yet-implemented instructions raise NotImplementedError
        test_wc = WorkflowController([])
        self.assertRaises(NotImplementedError, test_wc.load, u'hdf5')
        self.assertRaises(NotImplementedError, test_wc.load, u'stata')
        self.assertRaises(NotImplementedError, test_wc.load, u'pickle')

    def test_run_1(self):
        mock_path = u'vis.controllers.workflow.WorkflowController._intervs'
        with mock.patch(mock_path) as mock_meth:
            test_wc = WorkflowController([])
            test_wc.run(u'all-combinations intervals', 42)
            mock_meth.assert_called_once_with(42)

    def test_run_2(self):
        mock_path = u'vis.controllers.workflow.WorkflowController._two_part_modules'
        with mock.patch(mock_path) as mock_meth:
            test_wc = WorkflowController([])
            test_wc.run(u'all 2-part interval n-grams', 42)
            mock_meth.assert_called_once_with(42)

    def test_run_3(self):
        mock_path = u'vis.controllers.workflow.WorkflowController._all_part_modules'
        with mock.patch(mock_path) as mock_meth:
            test_wc = WorkflowController([])
            test_wc.run(u'all-voice interval n-grams', 42)
            mock_meth.assert_called_once_with(42)

    def test_run_4(self):
        mock_path_a = u'vis.controllers.workflow.WorkflowController._two_part_modules'
        mock_path_b = u'vis.controllers.workflow.WorkflowController._for_sc'
        with mock.patch(mock_path_a) as mock_meth_a:
            with mock.patch(mock_path_b) as mock_meth_b:
                mock_meth_a.return_value = 1200
                test_wc = WorkflowController([])
                test_wc.run(u'all 2-part interval n-grams for SuperCollider', 42)
                mock_meth_a.assert_called_once_with(42)
                mock_meth_b.assert_called_once_with(mock_meth_a.return_value)

    def test_run_6(self):
        test_wc = WorkflowController([])
        self.assertRaises(RuntimeError, test_wc.run, u'too short')
        self.assertRaises(RuntimeError, test_wc.run, u'this just is not an instruction you know')

    @mock.patch(u'vis.controllers.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.controllers.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.controllers.workflow.AggregatedPieces')
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
        test_wc = WorkflowController(test_pieces)
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

    @mock.patch(u'vis.controllers.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.controllers.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.controllers.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.controllers.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.controllers.workflow.AggregatedPieces')
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
                     [None, None, None, MagicMock(name=u'piece1 horiz')],
                     [None, None, None, MagicMock(name=u'piece1 horiz')]]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret[0], horiz_ret[0], u'piece1 3rd get_data()',
                   intind_ret[1], horiz_ret[1], u'piece3 3rd get_data()',
                   intind_ret[2], horiz_ret[2], u'piece2 3rd get_data()']
        ap_ret = [returns[2], returns[5], returns[8]]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) run the test
        test_wc = WorkflowController(test_pieces)
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

    @mock.patch(u'vis.controllers.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.controllers.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.controllers.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.controllers.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.controllers.workflow.AggregatedPieces')
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
                     [None, None, None, MagicMock(name=u'piece1 horiz')],
                     [None, None, None, MagicMock(name=u'piece1 horiz')]]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret[0], horiz_ret[0], u'piece1 3rd get_data()',
                   intind_ret[1], horiz_ret[1], u'piece3 3rd get_data()',
                   intind_ret[2], horiz_ret[2], u'piece2 3rd get_data()']
        ap_ret = [returns[2], returns[5], returns[8]]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) run the test
        test_wc = WorkflowController(test_pieces)
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

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
WORKFLOW_TESTS = TestLoader().loadTestsFromTestCase(WorkflowTests)
