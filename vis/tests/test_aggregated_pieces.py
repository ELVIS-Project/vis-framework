#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models_tests/test_aggregated_pieces.py
# Purpose:                Tests for models/aggregated_pieces.py.
#
# Copyright (C) 2013, 2014 Christopher Antila
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
Tests for :py:class:`~vis.models.aggregated_pieces.AggregatedPieces`.
"""

import os
from unittest import TestCase, TestLoader
import six
if six.PY3:
    from unittest.mock import MagicMock, Mock
else:
    from mock import MagicMock, Mock
import pandas
from vis.analyzers.indexer import Indexer
from vis.analyzers.experimenter import Experimenter
from vis.models.aggregated_pieces import AggregatedPieces
from vis.models.indexed_piece import IndexedPiece


class TestAggregatedPieces(TestCase):
    """Tests for AggregatedPieces"""
    # pylint: disable=too-many-public-methods

    def setUp(self):
        """Set up stuff"""
        self.pathnames = ['test_path_1', 'test_path_2', 'test_path_3']
        self.ind_pieces = [MagicMock(spec=IndexedPiece) for _ in range(len(self.pathnames))]
        for i, ind_p in enumerate(self.ind_pieces):
            ind_p.metadata.return_value = self.pathnames[i]
        self.agg_p = AggregatedPieces(self.ind_pieces).run()

    def test_metadata_1(self):
        """access the field automatically set"""
        self.assertSequenceEqual(self.pathnames, self.agg_p.metadata('pathnames'))

    def test_metadata_2(self):
        """raises TypeError if the field is not a string"""
        self.assertRaises(TypeError, self.agg_p.metadata, 12)
        try:
            self.agg_p.metadata(12)
        except TypeError as t_err:
            self.assertEqual(AggregatedPieces._FIELD_STRING, t_err.args[0])  # pylint: disable=protected-access

    def test_metadata_3(self):
        """returns None for non-existant field"""
        self.assertEqual(None, self.agg_p.metadata('pizza value'))

    def test_metadata_4(self):
        """calls _fetch_metadata() a not-yet-initialized field"""
        # pylint: disable=W0212
        self.agg_p._fetch_metadata = MagicMock(return_value=['Composer list!'])
        self.assertEqual(['Composer list!'], self.agg_p.metadata('composers'))
        self.agg_p._fetch_metadata.assert_called_once_with('composers')

    def test_fetch_metadata_1(self):
        """composers field"""
        self.ind_pieces[0].metadata = MagicMock(return_value='Bok')
        self.ind_pieces[1].metadata = MagicMock(return_value='Baytowvinn')
        self.ind_pieces[2].metadata = MagicMock(return_value='The Boys')
        expected = ['Bok', 'Baytowvinn', 'The Boys']
        self.assertEqual(expected, self.agg_p._fetch_metadata('composers'))  # pylint: disable=protected-access
        self.assertEqual(expected, self.agg_p._metadata['composers'])  # pylint: disable=protected-access
        for piece in self.ind_pieces:
            piece.metadata.assert_called_once_with('composer')

    def test_fetch_metadata_2a(self):
        """dates field"""
        # pylint: disable=W0212
        self.ind_pieces[0].metadata = MagicMock(return_value='1993')
        self.ind_pieces[1].metadata = MagicMock(return_value='1302')
        self.ind_pieces[2].metadata = MagicMock(return_value='1987')
        expected = ['1993', '1302', '1987']
        self.assertSequenceEqual(expected, self.agg_p._fetch_metadata('dates'))  # pylint: disable=protected-access
        self.assertSequenceEqual(expected, self.agg_p._metadata['dates'])  # pylint: disable=protected-access
        for piece in self.ind_pieces:
            piece.metadata.assert_called_once_with('date')

    def test_fetch_metadata_2b(self):
        """dates field with ranges"""
        # pylint: disable=W0212
        self.ind_pieces[0].metadata = MagicMock(return_value='1993 to 1993/08/08')
        self.ind_pieces[1].metadata = MagicMock(return_value='1302 to 1405')
        # he predicted his own death date in a unit test
        self.ind_pieces[2].metadata = MagicMock(return_value='1987/09/09 to 2045/05/12')
        expected = ['1993 to 1993/08/08', '1302 to 1405', '1987/09/09 to 2045/05/12']
        self.assertSequenceEqual(expected, self.agg_p._fetch_metadata('dates'))  # pylint: disable=protected-access
        self.assertSequenceEqual(expected, self.agg_p._metadata['dates'])  # pylint: disable=protected-access
        for piece in self.ind_pieces:
            piece.metadata.assert_called_once_with('date')

    def test_fetch_metadata_3(self):
        """date range field"""
        # pylint: disable=W0212
        self.ind_pieces[0].metadata = MagicMock(return_value='1993')
        self.ind_pieces[1].metadata = MagicMock(return_value='1302')
        self.ind_pieces[2].metadata = MagicMock(return_value='1987')
        expected = ('1302', '1993')
        self.assertSequenceEqual(expected, self.agg_p._fetch_metadata('date_range'))  # pylint: disable=protected-access
        self.assertSequenceEqual(expected, self.agg_p._metadata['date_range'])  # pylint: disable=protected-access
        for piece in self.ind_pieces:
            piece.metadata.assert_called_once_with('date')

    def test_fetch_metadata_4(self):
        """titles field"""
        # pylint: disable=W0212
        self.ind_pieces[0].metadata = MagicMock(return_value='Boris Godunov')
        self.ind_pieces[1].metadata = MagicMock(return_value='Peter Grimes')
        self.ind_pieces[2].metadata = MagicMock(return_value='Lights and Music')
        expected = ['Boris Godunov', 'Peter Grimes', 'Lights and Music']
        self.assertEqual(expected, self.agg_p._fetch_metadata('titles'))  # pylint: disable=protected-access
        self.assertEqual(expected, self.agg_p._metadata['titles'])  # pylint: disable=protected-access
        for piece in self.ind_pieces:
            piece.metadata.assert_called_once_with('title')

    def test_fetch_metadata_5(self):
        """locales field"""
        # pylint: disable=W0212
        self.ind_pieces[0].metadata = MagicMock(return_value='Cheronnow')
        self.ind_pieces[1].metadata = MagicMock(return_value='Munchreeawl')
        self.ind_pieces[2].metadata = MagicMock(return_value='Cowgree')
        expected = ['Cheronnow', 'Munchreeawl', 'Cowgree']
        self.assertEqual(expected, self.agg_p._fetch_metadata('locales'))  # pylint: disable=protected-access
        self.assertEqual(expected, self.agg_p._metadata['locales'])  # pylint: disable=protected-access
        for piece in self.ind_pieces:
            piece.metadata.assert_called_once_with('locale_of_composition')

    def test_get_data_1(self):
        """try getting data for a non-Indexer, non-Experimenter class"""
        non_analyzer = Mock
        self.assertRaises(TypeError, self.agg_p.get_data, [], [non_analyzer])
        try:
            self.agg_p.get_data([], [non_analyzer])
        except TypeError as t_err:
            # pylint: disable=protected-access
            self.assertEqual(AggregatedPieces._NOT_EXPERIMENTER.format(non_analyzer),
                             t_err.args[0])

    def test_get_data_2(self):
        """try get_data() on an AggregatedPieces with no pieces (no aggregated analyzers)"""
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        expected = [pandas.DataFrame()]
        aps = AggregatedPieces()
        actual = aps.get_data([mock_indexer_cls], [])
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(list(expected[0].index), list(actual[0].index))
        self.assertSequenceEqual(list(expected[0].columns), list(actual[0].columns))
        self.assertSequenceEqual(list(expected[0]), list(actual[0]))

    def test_get_data_3(self):
        """try get_data() on an AggregatedPieces with no pieces (with aggregated analyzers)"""
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_experimenter_cls = type('MockExperimenter', (Experimenter,), {})
        expected = pandas.DataFrame()
        aps = AggregatedPieces()
        actual = aps.get_data([mock_indexer_cls], [mock_experimenter_cls])
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))
        self.assertSequenceEqual(list(expected), list(actual))

    def test_get_data_4(self):
        """chained independent indexers, no aggregated results"""
        for piece in self.ind_pieces:
            piece.get_data.return_value = pandas.Series(['c4', 'd4', 'e4'], index=[0.0, 0.5, 1.0])
        an_indexer = type('AMockIndexer', (Indexer,), {})
        other_indexer = type('OtherMockIndexer', (Indexer,), {})
        expected = [pandas.Series(['c4', 'd4', 'e4'], index=[0.0, 0.5, 1.0]) for _ in range(3)]
        actual = self.agg_p.get_data([an_indexer, other_indexer], [])
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i]), list(actual[i]))
        for piece in self.ind_pieces:
            piece.get_data.assert_called_once_with([an_indexer, other_indexer], None)

    def test_get_data_5(self):
        """chained independent indexers, one aggregated experimenter"""
        for piece in self.ind_pieces:
            piece.get_data.return_value = pandas.Series(['c4', 'd4', 'e4'], index=[0.0, 0.5, 1.0])
        an_indexer = type('AMockIndexer', (Indexer,), {})
        other_indexer = type('OtherMockIndexer', (Indexer,), {})
        an_experimenter = type('AMockExperimenter', (Experimenter,), {})
        an_experimenter.run = MagicMock(return_value=pandas.DataFrame({0: [1, 2], 2: [4, 5]}))
        expected = pandas.DataFrame({0: [1, 2], 2: [4, 5]})
        actual = self.agg_p.get_data([an_indexer, other_indexer], [an_experimenter])
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))
        self.assertSequenceEqual(list(expected), list(actual))
        for piece in self.ind_pieces:
            piece.get_data.assert_called_once_with([an_indexer, other_indexer], None)
        an_experimenter.run.assert_called_once_with()

    def test_get_data_6(self):
        """chained independent indexers, chained aggregated experimenters"""
        for piece in self.ind_pieces:
            piece.get_data.return_value = pandas.Series(['c4', 'd4', 'e4'], index=[0.0, 0.5, 1.0])
        an_indexer = type('AMockIndexer', (Indexer,), {})
        other_indexer = type('OtherMockIndexer', (Indexer,), {})
        an_experimenter = type('AMockExperimenter', (Experimenter,), {})
        an_experimenter.run = MagicMock()
        other_experimenter = type('OtherMockExperimenter', (Experimenter,), {})
        other_experimenter.run = MagicMock(return_value=pandas.DataFrame({0: [1, 2], 2: [4, 5]}))
        expected = pandas.DataFrame({0: [1, 2], 2: [4, 5]})
        actual = self.agg_p.get_data([an_indexer, other_indexer],
                                     [an_experimenter, other_experimenter])
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))
        self.assertSequenceEqual(list(expected), list(actual))
        for piece in self.ind_pieces:
            piece.get_data.assert_called_once_with([an_indexer, other_indexer], None)
        an_experimenter.run.assert_called_once_with()
        other_experimenter.run.assert_called_once_with()

    def test_get_data_7(self):
        """one independent indexer, no aggregated results... checking settings get sent"""
        for piece in self.ind_pieces:
            piece.get_data.return_value = pandas.Series(['c4', 'd4', 'e4'], index=[0.0, 0.5, 1.0])
        an_indexer = type('AMockIndexer', (Indexer,), {})
        expected = [pandas.Series(['c4', 'd4', 'e4'], index=[0.0, 0.5, 1.0]) for _ in range(3)]
        actual = self.agg_p.get_data([an_indexer], [], {'awesome': True})
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i]), list(actual[i]))
        for piece in self.ind_pieces:
            piece.get_data.assert_called_once_with([an_indexer], {'awesome': True})

    def test_get_data_9(self):
        """no independent indexers (given as None), chained aggregated experimenters"""
        # NB: based on test 6
        for piece in self.ind_pieces:
            piece.get_data.return_value = pandas.Series(['c4', 'd4', 'e4'], index=[0.0, 0.5, 1.0])
        an_experimenter = type('AMockExperimenter', (Experimenter,), {})
        an_experimenter.__init__ = MagicMock(return_value=None)
        an_experimenter.run = MagicMock()
        an_experimenter.run.return_value = 41
        other_experimenter = type('OtherMockExperimenter', (Experimenter,), {})
        other_experimenter.__init__ = MagicMock(return_value=None)
        other_experimenter.run = MagicMock(return_value=pandas.DataFrame({0: [1, 2], 2: [4, 5]}))
        expected = pandas.DataFrame({0: [1, 2], 2: [4, 5]})
        actual = self.agg_p.get_data(None, [an_experimenter, other_experimenter], {}, 14)
        self.assertSequenceEqual(list(expected.index), list(actual.index))  # pylint: disable=maybe-no-member
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # pylint: disable=maybe-no-member
        self.assertSequenceEqual(list(expected), list(actual))
        for piece in self.ind_pieces:
            self.assertEqual(0, piece.get_data.call_count)
        an_experimenter.__init__.assert_called_once_with(14, {})
        an_experimenter.run.assert_called_once_with()
        other_experimenter.__init__.assert_called_once_with(an_experimenter.run.return_value, {})
        other_experimenter.run.assert_called_once_with()

    def test_get_data_10(self):
        """no independent indexers (given as []), chained aggregated experimenters"""
        # NB: based on test 9
        for piece in self.ind_pieces:
            piece.get_data.return_value = pandas.Series(['c4', 'd4', 'e4'], index=[0.0, 0.5, 1.0])
        an_experimenter = type('AMockExperimenter', (Experimenter,), {})
        an_experimenter.__init__ = MagicMock(return_value=None)
        an_experimenter.run = MagicMock()
        an_experimenter.run.return_value = 41
        other_experimenter = type('OtherMockExperimenter', (Experimenter,), {})
        other_experimenter.__init__ = MagicMock(return_value=None)
        other_experimenter.run = MagicMock(return_value=pandas.DataFrame({0: [1, 2], 2: [4, 5]}))
        expected = pandas.DataFrame({0: [1, 2], 2: [4, 5]})
        prev_data = ['data from', 'previous get_data()', 'call']
        actual = self.agg_p.get_data([], [an_experimenter, other_experimenter], {}, prev_data)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # pylint: disable=maybe-no-member
        self.assertSequenceEqual(list(expected), list(actual))
        for piece in self.ind_pieces:
            self.assertEqual(0, piece.get_data.call_count)
        an_experimenter.__init__.assert_called_once_with(prev_data, {})
        an_experimenter.run.assert_called_once_with()
        other_experimenter.__init__.assert_called_once_with(an_experimenter.run.return_value, {})
        other_experimenter.run.assert_called_once_with()

    def test_get_data_11(self):
        """(based on test 5): one independent experimenter, one aggregated experimenter; provides"""
        # data from a (false) previous call to get_data()
        ind_experimenter = type('AMockExperimenter', (Experimenter,), {})
        agg_experimenter = type('OtherMockExperimenter', (Experimenter,), {})
        agg_experimenter.run = MagicMock(return_value=pandas.DataFrame({0: [1, 2], 2: [4, 5]}))
        expected = pandas.DataFrame({0: [1, 2], 2: [4, 5]})
        prev_data = ['data from', 'previous get_data()', 'call']
        actual = self.agg_p.get_data([ind_experimenter], [agg_experimenter], {}, prev_data)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.columns), list(actual.columns))  # pylint: disable=maybe-no-member
        self.assertSequenceEqual(list(expected), list(actual))
        for i, piece in enumerate(self.ind_pieces):
            piece.get_data.assert_called_once_with([ind_experimenter], {}, prev_data[i])
        agg_experimenter.run.assert_called_once_with()

    def test_run(self):
        directory = 'vis/tests/corpus/elvisdownload'
        agg = AggregatedPieces(directory).run()
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_run2(self):
        directory = 'vis/tests/corpus/elvisdownload2'
        agg = AggregatedPieces(directory).run()
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_run3(self):
        path = 'vis/tests/corpus/elvisdownload/'
        folder = os.listdir(path)
        folder.remove('.DS_Store')
        folder.remove('meta')
        new_f = []
        for f in folder:
            new_f.append(path + f)
        agg = AggregatedPieces(new_f).run()
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_run4(self):
        path = 'vis/tests/corpus/elvisdownload/'
        folder = os.listdir(path)
        folder.remove('.DS_Store')
        folder.remove('meta')
        new_f = []
        for f in folder:
            new_f.append(path + f)
        meta = path + 'meta'
        agg = AggregatedPieces(new_f, metafiles=meta).run()
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_run5(self):
        path = 'vis/tests/corpus/elvisdownload'
        agg = AggregatedPieces(path).run()
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_run6(self):
        path = 'vis/tests/corpus/elvisdownload/'
        folder = os.listdir(path)
        folder.remove('.DS_Store')
        folder.remove('meta')
        new_f = []
        for f in folder:
            new_f.append(path + f)
        meta = path + 'meta'
        agg = AggregatedPieces(new_f, metafiles=[meta, meta, meta]).run()
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_date(self):
        date = ['----/--/-- to ----/--/--']
        agg = AggregatedPieces()._make_date_range(date)
        self.assertEqual(agg, None)


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
AGGREGATED_PIECES_SUITE = TestLoader().loadTestsFromTestCase(TestAggregatedPieces)
