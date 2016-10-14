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
from vis.models.indexed_piece import Importer, IndexedPiece
import vis
VIS_PATH = vis.__path__[0]


class TestAggregatedPieces(TestCase):
    """Tests for AggregatedPieces"""
    # pylint: disable=too-many-public-methods

    def setUp(self):
        """Set up stuff"""
        self.pathnames = ['test_path_1', 'test_path_2', 'test_path_3']
        self.ind_pieces = [MagicMock(spec=IndexedPiece) for _ in range(len(self.pathnames))]
        for i, ind_p in enumerate(self.ind_pieces):
            ind_p.metadata.return_value = self.pathnames[i]
        self.agg_p = AggregatedPieces(pieces=self.ind_pieces)
        self.agg_p2 = AggregatedPieces(pieces=[IndexedPiece(path) for path in self.pathnames])

    def test_metadata_1(self):
        """access the field automatically set"""
        self.assertSequenceEqual(self.pathnames, self.agg_p2.metadata('pathnames'))

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
        self.assertRaises(TypeError, self.agg_p.get_data, None, '')
        try:
            self.agg_p.get_data(None, '')
        except TypeError as t_err:
            # pylint: disable=protected-access
            self.assertEqual(AggregatedPieces._NOT_EXPERIMENTER.format('', sorted([k[0] for k in self.agg_p._mkd.keys()])),
                             t_err.args[0])

    def test_get_data_2(self):
        """try get_data() on an AggregatedPieces object with no pieces"""
        aps = AggregatedPieces()
        self.assertRaises(RuntimeWarning, aps.get_data, None, None)
        try:
            aps.get_data()
        except RuntimeWarning as r_warn:
            # pylint: disable=protected-access
            self.assertEqual(AggregatedPieces._NO_PIECES, r_warn.args[0])

    def test_get_data_3(self):
        """integration test with a nested called to get_data, an ind_analyzer and a 
        combined_experimenter"""
        expected = pandas.Series([4.0,2.0,2.0,2.0,2.0,2.0,2.0,4.0],
                                 index=['C3','C4','D4','E4','F4','G2','G4','Rest'])
        pieces = [Importer(os.path.join(VIS_PATH, 'tests', 'corpus', 'test_fermata_rest.xml'))]*2
        aps = AggregatedPieces(pieces=pieces)
        actual = aps.get_data(combined_experimenter='aggregator',
                              data=aps.get_data(ind_analyzer='noterest', combined_experimenter='frequency'))
        self.assertTrue(actual.iloc[:,0].equals(expected))

    def test_date(self):
        date = ['----/--/-- to ----/--/--']
        agg = AggregatedPieces()._make_date_range(date)
        self.assertEqual(agg, None)

class TestImporter(TestCase):
    """Tests for Importer"""

    def test_Importer1(self):
        directory = 'vis/tests/corpus/elvisdownload'
        agg = Importer(directory)
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_Importer2(self):
        directory = 'vis/tests/corpus/elvisdownload2'
        agg = Importer(directory)
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_Importer3(self):
        path = 'vis/tests/corpus/elvisdownload/'
        folder = os.listdir(path)
        if '.DS_Store' in folder:
            folder.remove('.DS_Store')
        folder.remove('meta')
        new_f = []
        for f in folder:
            new_f.append(path + f)
        agg = Importer(new_f)
        self.assertTrue(isinstance(agg, AggregatedPieces))

    def test_Importer4(self):
        path = 'vis/tests/corpus/elvisdownload/'
        folder = os.listdir(path)
        if '.DS_Store' in folder:
            folder.remove('.DS_Store')
        folder.remove('meta')
        new_f = []
        for f in folder:
            new_f.append(path + f)
        new_f.append(path + 'meta')
        agg = Importer(path)
        self.assertTrue(isinstance(agg, AggregatedPieces))

    # Commented out because we can't be sure which metafile corresponds to whic piece if there is 
    # more than one metafile.
    # def test_Importer5(self):
    #     """When there are as many metafiles as there are pieces."""
    #     path = 'vis/tests/corpus/elvisdownload/'
    #     folder = os.listdir(path)
    #     if '.DS_Store' in folder:
    #         folder.remove('.DS_Store')
    #     folder.remove('meta')
    #     new_f = []
    #     for f in folder:
    #         new_f.append(path + f)
    #     meta = path + 'meta'
    #     agg = Importer(new_f, metafiles=[meta]*3)
    #     self.assertTrue(isinstance(agg, AggregatedPieces))


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
AGGREGATED_PIECES_SUITE = TestLoader().loadTestsFromTestCase(TestAggregatedPieces)
IMPORTER_SUITE = TestLoader().loadTestsFromTestCase(TestImporter)
