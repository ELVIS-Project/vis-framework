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
                self.assertEqual(3, len(piece_sett))
                for sett in [u'offset interval', u'voice combinations']:
                    self.assertEqual(None, piece_sett[sett])
                for sett in [u'filter repeats']:
                    self.assertEqual(False, piece_sett[sett])
            exp_sh_setts = {u'n': 2, u'continuer': u'_', u'mark singles': False,
                            u'interval quality': False, u'simple intervals': False}
            self.assertEqual(exp_sh_setts, test_wc._shared_settings)

    def test_init_2(self):
        # with a list of IndexedPieces
        in_val = [IndexedPiece(u'help.txt'), IndexedPiece('path.xml'),
                  IndexedPiece(u'why_you_do_this.rtf')]
        test_wc = WorkflowManager(in_val)
        self.assertEqual(3, len(test_wc._data))
        for each in test_wc._data:
            self.assertTrue(each in in_val)
        for piece_sett in test_wc._settings:
            self.assertEqual(3, len(piece_sett))
            for sett in [u'offset interval', u'voice combinations']:
                self.assertEqual(None, piece_sett[sett])
            for sett in [u'filter repeats']:
                self.assertEqual(False, piece_sett[sett])
        exp_sh_setts = {u'n': 2, u'continuer': u'_', u'mark singles': False,
                        u'interval quality': False, u'simple intervals': False}
        self.assertEqual(exp_sh_setts, test_wc._shared_settings)

    def test_init_3(self):
        # with a mixed list of valid things
        in_val = [IndexedPiece(u'help.txt'), 'path.xml', u'why_you_do_this.rtf']
        test_wc = WorkflowManager(in_val)
        self.assertEqual(3, len(test_wc._data))
        self.assertEqual(in_val[0], test_wc._data[0])
        for each in test_wc._data[1:]:
            self.assertTrue(isinstance(each, IndexedPiece))
        for piece_sett in test_wc._settings:
            self.assertEqual(3, len(piece_sett))
            for sett in [u'offset interval', u'voice combinations']:
                self.assertEqual(None, piece_sett[sett])
            for sett in [u'filter repeats']:
                self.assertEqual(False, piece_sett[sett])
        exp_sh_setts = {u'n': 2, u'continuer': u'_', u'mark singles': False,
                        u'interval quality': False, u'simple intervals': False}
        self.assertEqual(exp_sh_setts, test_wc._shared_settings)

    def test_init_4(self):
        # with mostly basestrings but a few ints
        in_val = [u'help.txt', 'path.xml', 4, u'why_you_do_this.rtf']
        test_wc = WorkflowManager(in_val)
        self.assertEqual(3, len(test_wc._data))
        for each in test_wc._data:
            self.assertTrue(isinstance(each, IndexedPiece))
        for piece_sett in test_wc._settings:
            self.assertEqual(3, len(piece_sett))
            for sett in [u'offset interval', u'voice combinations']:
                self.assertEqual(None, piece_sett[sett])
            for sett in [u'filter repeats']:
                self.assertEqual(False, piece_sett[sett])
        exp_sh_setts = {u'n': 2, u'continuer': u'_', u'mark singles': False,
                        u'interval quality': False, u'simple intervals': False}
        self.assertEqual(exp_sh_setts, test_wc._shared_settings)

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
            test_wc.run(u'intervals')
            mock_meth.assert_called_once_with()
            self.assertEqual(mock_meth.return_value, test_wc._result)
            self.assertEqual(u'intervals', test_wc._previous_exp)

    def test_run_2(self):
        mock_path = u'vis.workflow.WorkflowManager._interval_ngrams'
        with mock.patch(mock_path) as mock_meth:
            mock_meth.return_value = u'the final countdown'
            test_wc = WorkflowManager([])
            test_wc.run(u'interval n-grams')
            mock_meth.assert_called_once_with()
            self.assertEqual(mock_meth.return_value, test_wc._result)
            self.assertEqual(u'n-grams', test_wc._previous_exp)

    def test_run_5(self):
        test_wc = WorkflowManager([])
        self.assertRaises(RuntimeError, test_wc.run, u'too short')
        self.assertRaises(RuntimeError, test_wc.run, u'this just is not an instruction you know')

    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.workflow.AggregatedPieces')
    def test_intervs_1(self, mock_ap, mock_agg, mock_freq, mock_int, mock_nri):
        # --> test whether _intervs() calls all those things in the right order, with the right
        #     args, using all the default settings
        # 1.) prepare the test and mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        ap_getdata_ret = MagicMock()
        ap_inst.get_data.return_value = ap_getdata_ret
        test_settings = {u'simple or compound': u'compound', u'quality': False}
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
        actual = test_wc._intervs()
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

    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.workflow.AggregatedPieces')
    @mock.patch(u'vis.workflow.offset.FilterByOffsetIndexer')
    @mock.patch(u'vis.workflow.repeat.FilterByRepeatIndexer')
    def test_intervs_2(self, mock_rep, mock_off, mock_ap, mock_agg, mock_freq, mock_int, mock_nri):
        # --> test whether _intervs() calls all those things in the right order, with running the
        #     offset and repeat indexers
        # 1.) prepare the test and mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        ap_getdata_ret = MagicMock()
        ap_inst.get_data.return_value = ap_getdata_ret
        test_settings = {u'simple or compound': u'compound', u'quality': False}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        returns = [MagicMock(dict, name=u'piece1 1st get_data()'), u'piece1 2nd get_data()',
                       u'piece1 3rd get_data()', u'piece1 4th get_data()',
                   MagicMock(dict, name=u'piece2 1st get_data()'), u'piece2 2nd get_data()',
                       u'piece2 3rd get_data()', u'piece2 4th get_data()',
                   MagicMock(dict, name=u'piece3 1st get_data()'), u'piece3 2nd get_data()',
                       u'piece3 3rd get_data()', u'piece3 4th get_data()']
        ap_ret = [u'piece1 4th get_data()', u'piece2 4th get_data()', u'piece3 4th get_data()']
        for i in [0, 4, 8]:
            returns[i].itervalues.return_value = [4]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) run the test
        test_wc = WorkflowManager(test_pieces)
        # (have to set the offset and repeat settings)
        for i in xrange(3):
            test_wc._settings[i][u'offset interval'] = 0.5
            test_wc._settings[i][u'filter repeats'] = True
        actual = test_wc._intervs()
        # 3.) confirm everything was called in the right order
        for i, piece in enumerate(test_pieces):
            self.assertEqual(4, piece.get_data.call_count)
            expected = [mock.call([mock_nri, mock_int], test_settings),
                        mock.call([mock_off], {u'quarterLength': 0.5}, [4]),
                        mock.call([mock_rep], {}, u'piece' + str(i + 1) + u' 2nd get_data()'),
                        mock.call([mock_freq, mock_agg], {},
                                   u'piece' + str(i + 1) + u' 3rd get_data()')]
            self.assertEqual(piece.get_data.mock_calls, expected)
        mock_ap.assert_called_once_with(test_pieces)
        ap_inst.get_data.assert_called_once_with([mock_agg], None, {}, ap_ret)
        self.assertEqual(ap_getdata_ret, actual)
        ap_getdata_ret.sort.assert_called_once_with(ascending=False)

    @mock.patch(u'vis.workflow.WorkflowManager._remove_extra_pairs')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    @mock.patch(u'vis.analyzers.experimenters.aggregator.ColumnAggregator')
    @mock.patch(u'vis.workflow.AggregatedPieces')
    def test_intervs_3(self, mock_ap, mock_agg, mock_freq, mock_int, mock_nri, mock_rep):
        # NB: most of the things up there are only mocked to prevent the real versions
        #     from being called
        # --> test whether _intervs() calls all those things in the right order, with specifying
        #     certain voice-pairs
        # 1.) prepare the test and mocks
        test_settings = {u'simple or compound': u'compound', u'quality': False}
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        the_dicts = [MagicMock(dict, name=u'piece1 1st get_data()'),
                     MagicMock(dict, name=u'piece2 1st get_data()'),
                     MagicMock(dict, name=u'piece3 1st get_data()')]
        returns = [the_dicts[0], u'piece1 2nd get_data()',
                   the_dicts[1], u'piece2 2nd get_data()',
                   the_dicts[2], u'piece3 2nd get_data()']
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
        # (have to set the voice-pair settings)
        expected_pairs = [[0, 1], [0, 2]]
        for i in xrange(3):
            test_wc._settings[i][u'voice combinations'] = expected_pairs
        test_wc._intervs()
        # 3.) for this test, we'll actually only confirm that mock_rep (_remove_extra_pairs) was
        #     called with the right arguments.
        self.assertEqual(3, mock_rep.call_count)
        for i in xrange(3):
            mock_rep.assert_any_call(the_dicts[i], expected_pairs)

    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    def test_all_part_modules_1(self, mock_freq, mock_int, mock_nri, mock_ng, mock_horiz):
        # - test without the "filter repeats" or "offset interval" settings
        # - we'll only use self._data[1]
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        intind_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in [u'0,3', u'1,3', u'2,3']}
        horiz_ret = [None, None, None, MagicMock(name=u'piece1 horiz')]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret, horiz_ret, 3]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(1, u'interval quality', True)
        test_wc.settings(1, u'simple intervals', True)
        test_wc.settings(1, u'filter repeats', False)
        test_wc.settings(1, u'offset interval', None)
        actual = test_wc._all_part_modules(1)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': True, u'simple or compound': u'simple'}
        expected_ngram_settings = {u'horizontal': [3], u'vertical': [0, 1, 2], u'n': 2, \
                                   u'continuer': u'_', u'mark singles': False}
        # all parts at once for NGramIndexer, plus 2 calls to interval indexers
        self.assertEqual(3, test_pieces[1].get_data.call_count)
        # confirm the calls to interval indexers an NGramIndexer all together
        expected = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts),
                    mock.call([mock_ng, mock_freq],
                              expected_ngram_settings,
                              [intind_ret[u'0,3'],
                               intind_ret[u'1,3'],
                               intind_ret[u'2,3'],
                               horiz_ret[3]])]
        for i in xrange(len(expected)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], expected[i])
        self.assertEqual(3, actual)

    @mock.patch(u'vis.workflow.repeat.FilterByRepeatIndexer')
    @mock.patch(u'vis.workflow.offset.FilterByOffsetIndexer')
    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    def test_all_part_modules_2(self, mock_freq, mock_int, mock_nri, mock_ng, mock_horiz, \
                                mock_off, mock_rep):
        # - test with the "filter repeats" or "offset interval" settings
        # - we'll only use self._data[1]
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        intind_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in [u'0,3', u'1,3', u'2,3']}
        horiz_ret = [None, None, None, MagicMock(name=u'piece1 horiz')]
        # set up return values for IndexedPiece.get_data()
        returns = [1, 2, 3, 4, intind_ret, horiz_ret, 7]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(1, u'interval quality', False)
        test_wc.settings(1, u'simple intervals', False)
        test_wc.settings(1, u'filter repeats', True)
        test_wc.settings(1, u'offset interval', 0.5)
        actual = test_wc._all_part_modules(1)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': False, u'simple or compound': u'compound'}
        expected_ngram_settings = {u'horizontal': [3], u'vertical': [0, 1, 2], u'n': 2, \
                                   u'continuer': u'_', u'mark singles': False}
        expected_off_setts = {u'quarterLength': 0.5}
        # all parts at once for NGramIndexer, plus 2 calls to interval indexers, plus two calls
        # each to the repeat and offset indexers
        self.assertEqual(7, test_pieces[1].get_data.call_count)
        # confirm the calls to interval indexers an NGramIndexer all together
        expected = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts),
                    mock.call([mock_off], expected_off_setts, 1),
                    mock.call([mock_off], expected_off_setts, 2),
                    mock.call([mock_rep], {}, 3),
                    mock.call([mock_rep], {}, 4),
                    mock.call([mock_ng, mock_freq],
                              expected_ngram_settings,
                              [intind_ret[u'0,3'],
                               intind_ret[u'1,3'],
                               intind_ret[u'2,3'],
                               horiz_ret[3]])]
        for i in xrange(len(expected)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], expected[i])
        self.assertEqual(7, actual)

    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    def test_two_part_modules_1(self, mock_freq, mock_int, mock_nri, mock_ng, \
                                mock_horiz):
        # - test without the "filter repeats" or "offset interval" settings
        # - we'll only use self._data[1]
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        intind_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in part_combos}
        horiz_ret = [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret, horiz_ret, u'piece2 3rd get_data()', u'piece2 4th get_data()',
                   u'piece2 5th get_data()', u'piece2 6th get_data()', u'piece2 7th get_data()',
                   u'piece2 8thd get_data()']
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(1, u'interval quality', True)
        test_wc.settings(1, u'simple intervals', True)
        test_wc.settings(1, u'filter repeats', False)
        test_wc.settings(1, u'offset interval', None)
        actual = test_wc._two_part_modules(1)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': True, u'simple or compound': u'simple'}
        expected_ngram_settings = {u'horizontal': [1], u'vertical': [0], u'n': 2, \
                                   u'continuer': u'_', u'mark singles': False}
        # four-part piece means 6 combinations for NGramIndexer, plus 2 calls to interval indexers
        self.assertEqual(8, test_pieces[1].get_data.call_count)
        expected = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts)]
        for i in xrange(len(expected)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], expected[i])
        # - that each IndP.get_data() called NGramIndexer with the right settings at some point
        for combo in intind_ret.iterkeys():
            test_pieces[1].get_data.assert_any_call([mock_ng, mock_freq],
                                                    expected_ngram_settings,
                                                    [intind_ret[combo],
                                                    horiz_ret[interval.key_to_tuple(combo)[1]]])
        self.assertEqual(u'piece2 8thd get_data()', actual)

    @mock.patch(u'vis.workflow.repeat.FilterByRepeatIndexer')
    @mock.patch(u'vis.workflow.offset.FilterByOffsetIndexer')
    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    def test_two_part_modules_2(self, mock_freq, mock_int, mock_nri, mock_ng, \
                                mock_horiz, mock_off, mock_rep):
        # - test with the "filter repeats" or "offset interval" settings
        # - we'll only use self._data[1]
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        intind_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in part_combos}
        horiz_ret = [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)]
        # set up return values for IndexedPiece.get_data()
        returns = [1, 2, 3, 4, intind_ret, horiz_ret, 7, 8, 9, 10, 11, 12]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(1, u'interval quality', False)
        test_wc.settings(1, u'simple intervals', False)
        test_wc.settings(1, u'filter repeats', True)
        test_wc.settings(1, u'offset interval', 0.5)
        actual = test_wc._two_part_modules(1)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': False, u'simple or compound': u'compound'}
        expected_ngram_settings = {u'horizontal': [1], u'vertical': [0], u'n': 2, \
                                   u'continuer': u'_', u'mark singles': False}
        expected_off_setts = {u'quarterLength': 0.5}
        # four-part piece means 6 combinations for NGramIndexer, plus 2 calls to interval indexers,
        # plus two calls each to the repeat and offset indexers
        self.assertEqual(12, test_pieces[1].get_data.call_count)
        expected = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts),
                    mock.call([mock_off], expected_off_setts, 1),
                    mock.call([mock_off], expected_off_setts, 2),
                    mock.call([mock_rep], {}, 3),
                    mock.call([mock_rep], {}, 4)]
        for i in xrange(len(expected)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], expected[i])
        # - that each IndP.get_data() called NGramIndexer with the right settings at some point
        for combo in intind_ret.iterkeys():
            test_pieces[1].get_data.assert_any_call([mock_ng, mock_freq],
                                                    expected_ngram_settings,
                                                    [intind_ret[combo],
                                                    horiz_ret[interval.key_to_tuple(combo)[1]]])
        self.assertEqual(12, actual)

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

    @mock.patch(u'vis.workflow.WorkflowManager._get_dataframe')
    @mock.patch(u'subprocess.call')
    def test_output_4(self, mock_call, mock_gdf):
        # with specified pathname; last experiment was intervals with 20 pieces; self._result is DF
        test_wc = WorkflowManager([])
        test_wc._previous_exp = u'intervals'
        test_wc._data = [1 for _ in xrange(20)]
        test_wc._result = MagicMock(spec=pandas.DataFrame)
        path = u'pathname!'
        actual = test_wc.output(u'R histogram', path)
        self.assertEqual(0, mock_gdf.call_count)
        expected_args = [u'R', u'--vanilla', u'-f', WorkflowManager._R_bar_chart_path, u'--args',
                         path + u'.dta', path + u'.png', u'int', u'20']
        mock_call.assert_called_once_with(expected_args)
        self.assertEqual(path + u'.png', actual)

    @mock.patch(u'vis.workflow.WorkflowManager._get_dataframe')
    @mock.patch(u'subprocess.call')
    def test_output_5(self, mock_call, mock_gdf):
        # with unspecified pathname; last experiment was 14-grams with 1 piece; self._result is S
        test_wc = WorkflowManager([])
        test_wc._previous_exp = u'n-grams'
        test_wc._data = [1]
        test_wc._shared_settings[u'n'] = 14
        test_wc._result = MagicMock(spec=pandas.Series)
        path = u'test_output/output_result'
        actual = test_wc.output(u'R histogram')
        mock_gdf.assert_called_once_with(u'freq', None, None)
        expected_args = [u'R', u'--vanilla', u'-f', WorkflowManager._R_bar_chart_path, u'--args',
                         path + u'.dta', path + u'.png', u'14', u'1']
        mock_call.assert_called_once_with(expected_args)
        self.assertEqual(path + u'.png', actual)

    @mock.patch(u'vis.workflow.WorkflowManager._get_dataframe')
    @mock.patch(u'subprocess.call')
    def test_output_6(self, mock_call, mock_gdf):
        # test_ouput_6, plus top_x and threshold
        test_wc = WorkflowManager([])
        test_wc._previous_exp = u'n-grams'
        test_wc._data = [1]
        test_wc._shared_settings[u'n'] = 14
        test_wc._result = MagicMock(spec=pandas.Series)
        path = u'test_output/output_result'
        actual = test_wc.output(u'R histogram', top_x=420, threshold=1987)
        mock_gdf.assert_called_once_with(u'freq', 420, 1987)
        expected_args = [u'R', u'--vanilla', u'-f', WorkflowManager._R_bar_chart_path, u'--args',
                         path + u'.dta', path + u'.png', u'14', u'1']
        mock_call.assert_called_once_with(expected_args)
        self.assertEqual(path + u'.png', actual)

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_1(self, mock_ip):
        # - if index is None and value are None, raise ValueError
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        self.assertRaises(ValueError, test_wm.settings, None, u'filter repeats', None)
        self.assertRaises(ValueError, test_wm.settings, None, u'filter repeats')

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_2(self, mock_ip):
        # - if index is None, field and value are valid, it'll set for all IPs
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        test_wm.settings(None, u'filter repeats', True)
        for i in xrange(3):
            self.assertEqual(True, test_wm._settings[i][u'filter repeats'])

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_3(self, mock_ip):
        # - if index is less than 0 or greater-than-valid, raise IndexError
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        self.assertRaises(IndexError, test_wm.settings, -1, u'filter repeats')
        self.assertRaises(IndexError, test_wm.settings, 20, u'filter repeats')

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_4(self, mock_ip):
        # - if index is 0, return proper setting
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        test_wm._settings[0][u'filter repeats'] = u'cheese'
        self.assertEqual(u'cheese', test_wm.settings(0, u'filter repeats'))

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_5(self, mock_ip):
        # - if index is greater than 0 but valid, set proper setting
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        test_wm.settings(1, u'filter repeats', u'leeks')
        self.assertEqual(u'leeks', test_wm._settings[1][u'filter repeats'])

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_6(self, mock_ip):
        # - if index is valid but the setting isn't, raise AttributeError (with or without a value)
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        self.assertRaises(AttributeError, test_wm.settings, 1, u'drink wine')
        self.assertRaises(AttributeError, test_wm.settings, 1, u'drink wine', True)

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_7(self, mock_ip):
        # - we can properly fetch a "shared setting"
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        test_wm._shared_settings[u'n'] = 4000
        self.assertEqual(4000, test_wm.settings(None, u'n'))

    @mock.patch(u'vis.models.indexed_piece.IndexedPiece')
    def test_settings_8(self, mock_ip):
        # - we can properly set a "shared setting"
        test_wm = WorkflowManager([u'a', u'b', u'c'])
        self.assertEqual(3, mock_ip.call_count)  # to make sure we're using the mock, not real IP
        test_wm.settings(None, u'n', 4000)
        self.assertEqual(4000, test_wm._shared_settings[u'n'])

    def test_extra_pairs_1(self):
        # testing WorkflowManager._remove_extra_pairs()
        # --> when only desired pairs are present
        vert_ints = {'0,1': 1, '0,2': 2, '1,2': 3}
        combos = [[0, 1], [0, 2], [1, 2]]
        expected = {'0,1': 1, '0,2': 2, '1,2': 3}
        actual = WorkflowManager._remove_extra_pairs(vert_ints, combos)
        self.assertSequenceEqual(expected, actual)

    def test_extra_pairs_2(self):
        # testing WorkflowManager._remove_extra_pairs()
        # --> when no pairs are desired
        vert_ints = {'0,1': 1, '0,2': 2, '1,2': 3}
        combos = []
        expected = {}
        actual = WorkflowManager._remove_extra_pairs(vert_ints, combos)
        self.assertSequenceEqual(expected, actual)

    def test_extra_pairs_3(self):
        # testing WorkflowManager._remove_extra_pairs()
        # --> when there are desired pairs, but they are not present
        vert_ints = {'0,1': 1, '0,2': 2, '1,2': 3}
        combos = [[4, 20], [11, 12]]
        expected = {}
        actual = WorkflowManager._remove_extra_pairs(vert_ints, combos)
        self.assertSequenceEqual(expected, actual)

    def test_extra_pairs_4(self):
        # testing WorkflowManager._remove_extra_pairs()
        # --> when there are lots of pairs, only some of which are desired
        vert_ints = {'4,20': 0, '0,1': 1, '11,12': 4, '0,2': 2, '1,2': 3, '256,128': 12}
        combos = [[0, 1], [0, 2], [1, 2]]
        expected = {'0,1': 1, '0,2': 2, '1,2': 3}
        actual = WorkflowManager._remove_extra_pairs(vert_ints, combos)
        self.assertSequenceEqual(expected, actual)

    def test_extra_pairs_5(self):
        # --> when there are lots of pairs, only some of which are desired, and there are invalid
        vert_ints = {'4,20': 0, '0,1': 1, '11,12': 4, '0,2': 2, '1,2': 3, '256,128': 12}
        combos = [[0, 1], [1, 2, 3, 4, 5], [0, 2], [1, 2], [9, 11, 43], [4]]
        expected = {'0,1': 1, '0,2': 2, '1,2': 3}
        actual = WorkflowManager._remove_extra_pairs(vert_ints, combos)
        self.assertSequenceEqual(expected, actual)

    def test_export_1(self):
        # --> raise RuntimeError with unrecognized output format
        test_wm = WorkflowManager([])
        test_wm._result = pandas.Series(xrange(100))
        self.assertRaises(RuntimeError, test_wm.export, u'PowerPoint')

    def test_export_2(self):
        # --> raise RuntimeError if run() hasn't been called (i.e., self._result is None)
        test_wm = WorkflowManager([])
        self.assertRaises(RuntimeError, test_wm.export, u'Excel', u'C:\autoexec.bat')

    @mock.patch(u'vis.workflow.WorkflowManager._get_dataframe')
    def test_export_3(self, mock_gdf):
        # --> the method works as expected for CSV, Excel, and Stata when _result is a DataFrame
        test_wm = WorkflowManager([])
        test_wm._result = mock.MagicMock(spec=pandas.DataFrame)
        test_wm.export(u'CSV', u'test_path')
        test_wm.export(u'Excel', u'test_path')
        test_wm.export(u'Stata', u'test_path')
        test_wm.export(u'HTML', u'test_path')
        test_wm._result.to_csv.assert_called_once_with(u'test_path.csv')
        test_wm._result.to_stata.assert_called_once_with(u'test_path.dta')
        test_wm._result.to_excel.assert_called_once_with(u'test_path.xlsx')
        test_wm._result.to_html.assert_called_once_with(u'test_path.html')
        self.assertEqual(0, mock_gdf.call_count)

    @mock.patch(u'vis.workflow.WorkflowManager._get_dataframe')
    def test_export_4(self, mock_gdf):
        # --> test_export_3() with a valid extension already on
        test_wm = WorkflowManager([])
        test_wm._result = mock.MagicMock(spec=pandas.DataFrame)
        test_wm.export(u'CSV', u'test_path.csv')
        test_wm.export(u'Excel', u'test_path.xlsx')
        test_wm.export(u'Stata', u'test_path.dta')
        test_wm.export(u'HTML', u'test_path.html')
        test_wm._result.to_csv.assert_called_once_with(u'test_path.csv')
        test_wm._result.to_stata.assert_called_once_with(u'test_path.dta')
        test_wm._result.to_excel.assert_called_once_with(u'test_path.xlsx')
        test_wm._result.to_html.assert_called_once_with(u'test_path.html')
        self.assertEqual(0, mock_gdf.call_count)

    @mock.patch(u'vis.workflow.WorkflowManager._get_dataframe')
    def test_export_5(self, mock_gdf):
        # --> test_export_3() with a Series that requires calling _get_dataframe()
        test_wm = WorkflowManager([])
        test_wm._result = mock.MagicMock(spec=pandas.Series)
        # CSV
        mock_gdf.return_value = MagicMock(spec=pandas.DataFrame)
        test_wm.export(u'CSV', u'test_path')
        mock_gdf.assert_called_once_with(u'data', None, None)
        mock_gdf.return_value.to_csv.assert_called_once_with(u'test_path.csv')
        mock_gdf.reset_mock()
        # Excel
        test_wm.export(u'Excel', u'test_path', 5)
        mock_gdf.assert_called_once_with(u'data', 5, None)
        mock_gdf.return_value.to_excel.assert_called_once_with(u'test_path.xlsx')
        mock_gdf.reset_mock()
        # Stata
        test_wm.export(u'Stata', u'test_path', 5, 10)
        mock_gdf.assert_called_once_with(u'data', 5, 10)
        mock_gdf.return_value.to_stata.assert_called_once_with(u'test_path.dta')
        mock_gdf.reset_mock()
        # HTML
        test_wm.export(u'HTML', u'test_path', threshold=10)
        mock_gdf.assert_called_once_with(u'data', None, 10)
        mock_gdf.return_value.to_html.assert_called_once_with(u'test_path.html')

    def test_export_6(self):
        # --> the method always outputs a DataFrame, even if self._result isn't a DF yet
        # TODO: I don't know how to test this. I want to mock DataFrame, but it also needs to pass
        #       the isinstance() test, so it can't be a MagicMock unless it's a MagicMock instance
        #       of DataFrame, which is impossible(?) because I have to patch it at
        #       vis.workflow.pandas.DataFrame
        pass

    @mock.patch(u'vis.workflow.AggregatedPieces')
    @mock.patch(u'vis.workflow.WorkflowManager._variable_part_modules')
    @mock.patch(u'vis.workflow.WorkflowManager._all_part_modules')
    @mock.patch(u'vis.workflow.WorkflowManager._two_part_modules')
    def test_interval_ngrams_1(self, mock_two, mock_all, mock_var, mock_ap):
        # --> test with three pieces, each of which requires a different helper
        # 1.) prepare mocks
        ap_inst = MagicMock(AggregatedPieces)
        mock_ap.return_value = ap_inst
        ap_getdata_ret = MagicMock(spec=pandas.DataFrame)
        ap_inst.get_data.return_value = ap_getdata_ret
        ind_pieces = [MagicMock(spec=IndexedPiece) for _ in xrange(3)]
        test_wm = WorkflowManager(ind_pieces)
        test_wm.settings(0, u'voice combinations', u'[all]')
        test_wm.settings(1, u'voice combinations', u'[all pairs]')
        test_wm.settings(2, u'voice combinations', u'other')
        actual = test_wm._interval_ngrams()
        # 3.) verify the mocks
        mock_two.assert_called_once_with(1)
        mock_all.assert_called_once_with(0)
        mock_var.assert_called_once_with(2)
        self.assertEqual(ap_getdata_ret, actual)
        self.assertEqual(ap_getdata_ret, test_wm._result)

    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    def test_var_part_modules_1(self, mock_freq, mock_int, mock_nri, mock_ng, mock_horiz):
        # - test without the "filter repeats" or "offset interval" settings
        # - we'll only use self._data[1]
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        all_part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        selected_part_combos = [[0, 3], [2, 3]]
        intind_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in all_part_combos}
        horiz_ret = [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret, horiz_ret, u'piece2 3rd get_data()', u'piece2 4th get_data()']
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(1, u'interval quality', True)
        test_wc.settings(1, u'simple intervals', True)
        test_wc.settings(1, u'filter repeats', False)
        test_wc.settings(1, u'offset interval', None)
        test_wc.settings(1, u'voice combinations', unicode(selected_part_combos))
        actual = test_wc._variable_part_modules(1)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': True, u'simple or compound': u'simple'}
        expected_ngram_settings = {u'horizontal': [1], u'vertical': [0], u'n': 2, \
                                   u'continuer': u'_', u'mark singles': False}
        # 2 combinations for NGramIndexer, plus 2 calls to interval indexers
        self.assertEqual(4, test_pieces[1].get_data.call_count)
        expected = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts)]
        for i in xrange(len(expected)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], expected[i])
        # - that each IndP.get_data() called NGramIndexer with the right settings at some point
        for combo in selected_part_combos:
            zombo = str(combo[0]) + u',' + str(combo[1])
            test_pieces[1].get_data.assert_any_call([mock_ng, mock_freq],
                                                    expected_ngram_settings,
                                                    [intind_ret[zombo],
                                                    horiz_ret[combo[1]]])
        self.assertEqual(u'piece2 4th get_data()', actual)

    @mock.patch(u'vis.workflow.repeat.FilterByRepeatIndexer')
    @mock.patch(u'vis.workflow.offset.FilterByOffsetIndexer')
    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    def test_var_part_modules_2(self, mock_freq, mock_int, mock_nri, mock_ng, mock_horiz, \
                                mock_off, mock_rep):
        # - test with the "filter repeats" or "offset interval" settings
        # - we'll only use self._data[1]
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        all_part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        selected_part_combos = [[0, 3], [2, 3]]
        intind_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in all_part_combos}
        horiz_ret = [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)]
        # set up return values for IndexedPiece.get_data()
        returns = [1, 2, 3, 4, intind_ret, horiz_ret, 7, 8]
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(1, u'interval quality', False)
        test_wc.settings(1, u'simple intervals', False)
        test_wc.settings(1, u'filter repeats', True)
        test_wc.settings(1, u'offset interval', 0.5)
        test_wc.settings(1, u'voice combinations', unicode(selected_part_combos))
        actual = test_wc._variable_part_modules(1)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': False, u'simple or compound': u'compound'}
        expected_ngram_settings = {u'horizontal': [1], u'vertical': [0], u'n': 2, \
                                   u'continuer': u'_', u'mark singles': False}
        expected_off_setts = {u'quarterLength': 0.5}
        # 2 combinations for NGramIndexer, plus 2 calls to interval indexers, plus 2 calls each to
        # the repeat and offset indexers
        self.assertEqual(8, test_pieces[1].get_data.call_count)
        expected = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts),
                    mock.call([mock_off], expected_off_setts, 1),
                    mock.call([mock_off], expected_off_setts, 2),
                    mock.call([mock_rep], {}, 3),
                    mock.call([mock_rep], {}, 4)]
        for i in xrange(len(expected)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], expected[i])
        # - that each IndP.get_data() called NGramIndexer with the right settings at some point
        for combo in selected_part_combos:
            zombo = str(combo[0]) + u',' + str(combo[1])
            test_pieces[1].get_data.assert_any_call([mock_ng, mock_freq],
                                                    expected_ngram_settings,
                                                    [intind_ret[zombo],
                                                    horiz_ret[combo[1]]])
        self.assertEqual(8, actual)

    @mock.patch(u'vis.workflow.interval.HorizontalIntervalIndexer')
    @mock.patch(u'vis.workflow.ngram.NGramIndexer')
    @mock.patch(u'vis.workflow.noterest.NoteRestIndexer')
    @mock.patch(u'vis.workflow.interval.IntervalIndexer')
    @mock.patch(u'vis.analyzers.experimenters.frequency.FrequencyExperimenter')
    def test_var_part_modules_3(self, mock_freq, mock_int, mock_nri, mock_ng, mock_horiz):
        # - test without the "filter repeats" or "offset interval" settings
        # - we'll only use self._data[1]
        # 1.) prepare the test and mocks
        test_pieces = [MagicMock(IndexedPiece, name=x) for x in [u'test1', u'test2', u'test3']]
        # set up fake part names
        for piece in test_pieces:
            piece.metadata.return_value = [u'S', u'A', u'T', u'B']
        # set up fake return values for IntervalIndexer
        all_part_combos = [u'0,3', u'1,3', u'2,3', u'0,1', u'0,2', u'1,2']
        selected_part_combos = [[0, 1, 2], [1, 2, 3]]
        intind_ret = {x: MagicMock(name=u'piece2 part ' + x) for x in all_part_combos}
        horiz_ret = [MagicMock(name=u'piece2 horiz ' + str(x)) for x in xrange(4)]
        # set up return values for IndexedPiece.get_data()
        returns = [intind_ret, horiz_ret, u'piece2 3rd get_data()', u'piece2 4th get_data()']
        def side_effect(*args):
            # NB: we need to accept "args" as a mock framework formality
            # pylint: disable=W0613
            return returns.pop(0)
        for piece in test_pieces:
            piece.get_data.side_effect = side_effect
        # 2.) prepare WorkflowManager and run the test
        test_wc = WorkflowManager(test_pieces)
        test_wc.settings(1, u'interval quality', True)
        test_wc.settings(1, u'simple intervals', True)
        test_wc.settings(1, u'filter repeats', False)
        test_wc.settings(1, u'offset interval', None)
        test_wc.settings(1, u'voice combinations', unicode(selected_part_combos))
        actual = test_wc._variable_part_modules(1)
        # 3.) confirm everything was called in the right order
        # - that every IP is asked for its vertical and horizontal interval indexes
        #   (that "mark singles" and "continuer" weren't put in the settings)
        expected_interv_setts = {u'quality': True, u'simple or compound': u'simple'}
        expected_ngram_settings = {u'horizontal': [2], u'vertical': [0, 1], u'n': 2, \
                                   u'continuer': u'_', u'mark singles': False}
        # 2 combinations for NGramIndexer, plus 2 calls to interval indexers
        self.assertEqual(4, test_pieces[1].get_data.call_count)
        expected = [mock.call([mock_nri, mock_int], expected_interv_setts),
                    mock.call([mock_nri, mock_horiz], expected_interv_setts)]
        for i in xrange(len(expected)):
            self.assertEqual(test_pieces[1].get_data.mock_calls[i], expected[i])
        # - that each IndP.get_data() called NGramIndexer with the right settings at some point
        selected_part_combos = [[0, 1, 2], [1, 2, 3]]
        for combo in selected_part_combos:
            parts = [intind_ret[str(i) + u',' + str(combo[-1])] for i in combo[:-1]]
            parts.append(horiz_ret[combo[-1]])
            test_pieces[1].get_data.assert_any_call([mock_ng, mock_freq],
                                                    expected_ngram_settings,
                                                    parts)
        self.assertEqual(u'piece2 4th get_data()', actual)

    def test_get_dataframe_1(self):
        # test with name=auto, top_x=auto, threshold=auto
        test_wc = WorkflowManager([])
        test_wc._result = pandas.Series([i for i in xrange(10, 0, -1)])
        expected = pandas.DataFrame({'data': pandas.Series([i for i in xrange(10, 0, -1)])})
        actual = test_wc._get_dataframe()
        self.assertEqual(expected, actual)
        for i in xrange(len(expected['data'])):
            self.assertEqual(expected['data'][i], actual['data'][i])

    def test_get_dataframe_2(self):
        # test with name='asdf', top_x=3, threshold=auto
        test_wc = WorkflowManager([])
        test_wc._result = pandas.Series([i for i in xrange(10, 0, -1)])
        expected = pandas.DataFrame({'asdf': pandas.Series([10, 9, 8])})
        actual = test_wc._get_dataframe('asdf', 3)
        self.assertEqual(expected, actual)
        for i in xrange(len(expected['asdf'])):
            self.assertEqual(expected['asdf'][i], actual['asdf'][i])

    def test_get_dataframe_3(self):
        # test with name=auto, top_x=3, threshold=5 (so the top_x still removes after threshold)
        test_wc = WorkflowManager([])
        test_wc._result = pandas.Series([i for i in xrange(10, 0, -1)])
        expected = pandas.DataFrame({'data': pandas.Series([10, 9, 8])})
        actual = test_wc._get_dataframe(top_x=3, threshold=5)
        self.assertEqual(expected, actual)
        for i in xrange(len(expected['data'])):
            self.assertEqual(expected['data'][i], actual['data'][i])

    def test_get_dataframe_4(self):
        # test with name=auto, top_x=5, threshold=7 (so threshold leaves fewer than 3 results)
        test_wc = WorkflowManager([])
        test_wc._result = pandas.Series([i for i in xrange(10, 0, -1)])
        expected = pandas.DataFrame({'data': pandas.Series([10, 9, 8])})
        actual = test_wc._get_dataframe(top_x=5, threshold=7)
        self.assertEqual(expected, actual)
        for i in xrange(len(expected['data'])):
            self.assertEqual(expected['data'][i], actual['data'][i])

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
WORKFLOW_TESTS = TestLoader().loadTestsFromTestCase(WorkflowTests)
