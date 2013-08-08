#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models_tests/test_indexed_piece.py
# Purpose:                Tests for models/indexed_piece.py.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Tests for :py:class:`~vis.models.indexed_piece.IndexedPiece`.
"""

from unittest import TestCase, TestLoader
from mock import patch, MagicMock, Mock
import music21
from vis.analyzers.experimenter import Experimenter
from vis.analyzers.indexer import Indexer
from vis.models.indexed_piece import IndexedPiece


# pylint: disable=R0904
@patch('music21.converter.parse', lambda path: MagicMock(spec=music21.stream.Score))
class TestIndexedPiece(TestCase):
    """
    Tests for :py:class:`~vis.models.indexed_piece.IndexedPiece`.
    """

    def setUp(self):
        """
        Initialize a sample :py:class:`IndexedPiece` instance for use in each test.
        :returns: None
        """
        self.ind_piece = IndexedPiece('')

    def test_metadata(self):
        """
        Tests for the method :py:meth:`~IndexedPiece.metadata`.
        :returns: None
        """
        # access fields which are set by default
        pathname = self.ind_piece.metadata('pathname')
        self.assertEquals('', pathname, "pathname variable doesn't match initialization value")
        # assign a value
        self.ind_piece.metadata('field', 2)
        value = self.ind_piece.metadata('field')
        self.assertEquals(2, value, "extracted metadata field doesn't match assigned value")
        # access an invalid value
        value = self.ind_piece.metadata('invalid_field')
        self.assertEquals(None, value)
        # try accessing keys with invalid types
        self.assertRaises(TypeError, self.ind_piece.metadata, 2)
        self.assertRaises(TypeError, self.ind_piece.metadata, [])
        self.assertRaises(TypeError, self.ind_piece.metadata, {})

    def test_get_data(self):
        """
        Tests for the method :py:meth:`~IndexedPiece.get_data`.
        :returns: None
        """
        # get data for a basic Indexer
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.run = lambda self: None
        self.assertEquals(None, self.ind_piece.get_data(mock_indexer_cls))
        # get data for an Indexer which requires another Indexer
        required_indexer_cls = type('RequiredIndexer', (mock_indexer_cls,), {})
        another_indexer_cls = type('AnotherIndexer', (mock_indexer_cls,),
                                   {'required_indices': [required_indexer_cls]})
        self.assertEquals(None, self.ind_piece.get_data(another_indexer_cls))
        # get data for a basic Experimenter
        mock_experimenter_cls = type('MockExperimenter', (Experimenter,), {})
        mock_experimenter_cls.run = lambda self: None
        self.assertEquals(None, self.ind_piece.get_data(mock_experimenter_cls))
        # try getting data for a non-Indexer, non-Experimenter class
        non_analyzer = Mock()
        self.assertRaises(TypeError, self.ind_piece.get_data, non_analyzer)


#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
INDEXED_PIECE_SUITE = TestLoader().loadTestsFromTestCase(TestIndexedPiece)
