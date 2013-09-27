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
import pandas
from vis.controllers.workflow import WorkflowController
from vis.models.indexed_piece import IndexedPiece
from vis.models.aggregated_pieces import AggregatedPieces
from vis.analyzers.indexers import noterest, interval, ngram
#from vis.analyzers.experimenters import frequency


# pylint: disable=R0904
# pylint: disable=C0111
class WorkflowTests(TestCase):
    def test_init_1(self):
        # with a list of basestrings
        with mock.patch(u'vis.models.indexed_piece.IndexedPiece') as mock_ip:
            in_val = [u'help.txt', 'path.xml', u'why_you_do_this.rtf']
            a = WorkflowController(in_val)
            self.assertEqual(3, mock_ip.call_count)
            for val in in_val:
                mock_ip.assert_any_call(val)
            self.assertEqual(3, len(a._data))
            for each in a._data:
                self.assertTrue(isinstance(each, mock.MagicMock))

    def test_init_2(self):
        # with a list of IndexedPieces
        in_val = [IndexedPiece(u'help.txt'), IndexedPiece('path.xml'),
                  IndexedPiece(u'why_you_do_this.rtf')]
        a = WorkflowController(in_val)
        self.assertEqual(3, len(a._data))
        for each in a._data:
            self.assertTrue(each in in_val)

    def test_init_3(self):
        # with a mixed list of valid things
        in_val = [IndexedPiece(u'help.txt'), 'path.xml', u'why_you_do_this.rtf']
        a = WorkflowController(in_val)
        self.assertEqual(3, len(a._data))
        self.assertEqual(in_val[0], a._data[0])
        for each in a._data[1:]:
            self.assertTrue(isinstance(each, IndexedPiece))

    def test_init_4(self):
        # with mostly basestrings but a few ints
        in_val = [u'help.txt', 'path.xml', 4, u'why_you_do_this.rtf']
        a = WorkflowController(in_val)
        self.assertEqual(3, len(a._data))
        for each in a._data:
            self.assertTrue(isinstance(each, IndexedPiece))

    def test_load_1(self):
        # that "get_data" is called correctly on each thing
        a = WorkflowController([])
        a._data = [mock.MagicMock(spec=IndexedPiece) for _ in xrange(5)]
        a.load(u'pieces')
        for mock_piece in a._data:
            mock_piece.get_data.assert_called_once_with([noterest.NoteRestIndexer])

    def test_run_1(self):
        mock_path = u'vis.controllers.workflow.WorkflowController._intervs'
        with mock.patch(mock_path) as mock_meth:
            a = WorkflowController([])
            a.run(u'all-combinations intervals', 42)
            mock_meth.assert_called_once_with(42)

    def test_run_2(self):
        mock_path = u'vis.controllers.workflow.WorkflowController._two_part_modules'
        with mock.patch(mock_path) as mock_meth:
            a = WorkflowController([])
            a.run(u'all 2-part interval n-grams', 42)
            mock_meth.assert_called_once_with(42)

    def test_run_3(self):
        mock_path = u'vis.controllers.workflow.WorkflowController._all_part_modules'
        with mock.patch(mock_path) as mock_meth:
            a = WorkflowController([])
            a.run(u'all-voice interval n-grams', 42)
            mock_meth.assert_called_once_with(42)

    def test_run_4(self):
        mock_path_a = u'vis.controllers.workflow.WorkflowController._two_part_modules'
        mock_path_b = u'vis.controllers.workflow.WorkflowController._for_sc'
        with mock.patch(mock_path_a) as mock_meth_a:
            with mock.patch(mock_path_b) as mock_meth_b:
                mock_meth_a.return_value = 1200
                a = WorkflowController([])
                a.run(u'all 2-part interval n-grams for SuperCollider', 42)
                mock_meth_a.assert_called_once_with(42)
                mock_meth_b.assert_called_once_with(mock_meth_a.return_value)

    def test_run_6(self):
        a = WorkflowController([])
        self.assertRaises(RuntimeError, a.run, u'too short')
        self.assertRaises(RuntimeError, a.run, u'this just is not an instruction you know')

    @mock.patch(u'vis.controllers.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.controllers.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.controllers.workflow.AggregatedPieces')
    def test_intervs_1(self, mock_ap, mock_agg, mock_freq, mock_int, mock_nri):
    #def test_intervs_1(self, mock_nri, mock_int, mock_freq, mock_agg, mock_ap):
        # mock NoteRestIndexer, IntervalIndexer, FrequencyExperimenter, ColumnAggregator,
        #      IndexedPiece, AggregatedPieces
        # test whether _intervs() calls all those things in the right order, with the right args
        # 1.) prepare the test and mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        test_settings = {u'a setting': u'its value', u'other setting': u'so crazy!'}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        returns = [MagicMock(dict, name=u'piece1 2nd get_data()'), u'piece1 2nd get_data()',
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
        test_wc._intervs(test_settings)
        # 3.) confirm everything was called in the right order
        for piece in test_pieces:
            self.assertEqual(2, piece.get_data.call_count)
            piece.get_data.assert_any_call([mock_nri, mock_int], test_settings)
            piece.get_data.assert_any_call([mock_freq, mock_agg], {}, [4])
        mock_ap.assert_called_once_with(test_pieces)
        ap_inst.get_data.assert_called_once_with([mock_agg], None, {}, ap_ret)


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
WORKFLOW_TESTS = TestLoader().loadTestsFromTestCase(WorkflowTests)
