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
from unittest import TestCase, TestLoader
from mock import patch, MagicMock, Mock
import music21
from vis.analyzers.experimenter import Experimenter
from vis.analyzers.indexer import Indexer
from vis.models.indexed_piece import IndexedPiece


@patch('music21.converter.parse', lambda path: MagicMock(spec=music21.stream.Score))
class TestIndexedPiece(TestCase):
    def setUp(self):
        """
        Initialize a sample :py:class:`IndexedPiece` instance for use in each test.
        :returns: None
        """
        self.ip = IndexedPiece('')

    def test_metadata(self):
        """
        Tests for the method :py:meth:`~IndexedPiece.metadata`.
        :returns: None
        """
        # access fields which are set by default
        pathname = self.ip.metadata('pathname')
        self.assertEquals('', pathname, "pathname variable doesn't match initialization value")
        # assign a value
        self.ip.metadata('field', 2)
        value = self.ip.metadata('field')
        self.assertEquals(2, value, "extracted metadata field doesn't match assigned value")
        # access an invalid value
        value = self.ip.metadata('invalid_field')
        self.assertEquals(None, value)
        # try accessing keys with invalid types
        self.assertRaises(TypeError, self.ip.metadata, 2)
        self.assertRaises(TypeError, self.ip.metadata, [])
        self.assertRaises(TypeError, self.ip.metadata, {})

    def test_get_data(self):
        """
        Tests for the method :py:meth:`~IndexedPiece.get_data`.
        :returns: None
        """
        # get data for a basic Indexer
        MockIndexer = type('TestIndexer', (Indexer,), {})
        MockIndexer.run = lambda self: None
        self.assertEquals(None, self.ip.get_data(MockIndexer))
        # get data for an Indexer which requires another Indexer
        RequiredIndexer = type('RequiredIndexer', (MockIndexer,), {})
        AnotherIndexer = type('AnotherIndexer', (MockIndexer,),
                              {'required_indices': [RequiredIndexer]})
        self.assertEquals(None, self.ip.get_data(AnotherIndexer))
        # get data for a basic Experimenter
        TestExperimenter = type('TestExperimenter', (Experimenter,), {})
        TestExperimenter.run = lambda self: None
        self.assertEquals(None, self.ip.get_data(TestExperimenter))
        # try getting data for a non-Indexer, non-Experimenter class
        NonIndexer = Mock()
        self.assertRaises(TypeError, self.ip.get_data, NonIndexer)


#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
INDEXED_PIECE_SUITE = TestLoader().loadTestsFromTestCase(TestIndexedPiece)