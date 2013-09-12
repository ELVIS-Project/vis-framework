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
import pandas
import music21
from vis.analyzers.indexer import Indexer
from vis.analyzers.indexers import noterest
from vis.analyzers.experimenter import Experimenter
from vis.models.indexed_piece import IndexedPiece


# pylint: disable=R0904
@patch('music21.converter.parse', new=lambda path: MagicMock(name=u'ScoreMock: ' + path,
                                                             spec=music21.stream.Score))
class TestIndexedPieceA(TestCase):
    """
    Tests for :py:class:`~vis.models.indexed_piece.IndexedPiece`.
    """
    def setUp(self):
        """
        Initialize a sample :py:class:`IndexedPiece` instance for use in each test.
        :returns: None
        """
        self._pathname = u'test_path'
        self.ind_piece = IndexedPiece(self._pathname)

    def test_metadata(self):
        """
        Tests for the method :py:meth:`~IndexedPiece.metadata`.
        :returns: None
        """
        # access fields which are set by default
        pathname = self.ind_piece.metadata('pathname')
        self.assertEquals(self._pathname, pathname, "pathname has changed!")
        # assign a value to a valid field
        self.ind_piece.metadata('date', 2)
        value = self.ind_piece.metadata('date')
        self.assertEquals(2, value, "extracted metadata field doesn't match assigned value")
        # assign a value to an invalid field
        self.assertRaises(AttributeError, self.ind_piece.metadata, 'field', 2)
        # access an invalid value
        value = self.ind_piece.metadata('invalid_field')
        self.assertEquals(None, value)
        # try accessing keys with invalid types
        self.assertRaises(TypeError, self.ind_piece.metadata, 2)
        self.assertRaises(TypeError, self.ind_piece.metadata, [])
        self.assertRaises(TypeError, self.ind_piece.metadata, {})

    def test_get_data_0(self):
        """
        Test for the method :py:meth:`~IndexedPiece.get_data`.
        :returns: None
        """
        # try getting data for a non-Indexer, non-Experimenter class
        non_analyzer = Mock()
        self.assertRaises(TypeError, self.ind_piece.get_data, non_analyzer)

    def test_get_data_1(self):
        """
        Test for the method :py:meth:`~IndexedPiece.get_data`.
        :returns: None
        """
        # get data for an Indexer requiring a Score
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.requires_score = True
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = u'ahhh!'
        self.assertEquals(u'ahhh!', self.ind_piece.get_data([mock_indexer_cls]))
        mock_indexer_cls.run.assert_called_once_with()

    def test_get_data_2(self):
        """
        Test for the method :py:meth:`~IndexedPiece.get_data`.
        :returns: None
        """
        # get data for an Indexer requiring other data
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = u'ahhh!'
        mock_indexer_cls.requires_score = False
        mock_indexer_cls.required_score_type = int
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([mock_indexer_cls], data=[14]))
        mock_indexer_cls.run.assert_called_once_with()
        # TODO: does it give mock_indexer_cls.__init__() the list?

    def test_get_data_3(self):
        """
        Test for the method :py:meth:`~IndexedPiece.get_data`.
        :returns: None
        """
        # get data from a chained Indexer
        first_indexer_cls = type('MockIndexer', (Indexer,), {})
        first_indexer_cls.run = MagicMock()
        first_indexer_cls.run.return_value = [14]
        first_indexer_cls.requires_score = True
        second_indexer_cls = type('MockIndexer', (Indexer,), {})
        second_indexer_cls.run = MagicMock()
        second_indexer_cls.run.return_value = u'ahhh!'
        second_indexer_cls.requires_score = False
        second_indexer_cls.required_score_type = int
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([first_indexer_cls, second_indexer_cls]))
        first_indexer_cls.run.assert_called_once_with()
        second_indexer_cls.run.assert_called_once_with()
        # TODO: does the result of first_indexer_cls get passed to second_indexer_cls.__init__()?

    def test_get_data_4(self):
        """
        Tests for the method :py:meth:`~IndexedPiece.get_data`.
        :returns: None
        """
        # chained Indexer plus settings
        # TODO: write the settings
        first_indexer_cls = type('MockIndexer', (Indexer,), {})
        first_indexer_cls.run = MagicMock()
        first_indexer_cls.run.return_value = [14]
        first_indexer_cls.requires_score = True
        second_indexer_cls = type('MockIndexer', (Indexer,), {})
        second_indexer_cls.run = MagicMock()
        second_indexer_cls.run.return_value = u'ahhh!'
        second_indexer_cls.requires_score = False
        second_indexer_cls.required_score_type = int
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([first_indexer_cls, second_indexer_cls],
                                                           {u'fake setting': u'so good!'}))
        first_indexer_cls.run.assert_called_once_with()
        second_indexer_cls.run.assert_called_once_with()
        # TODO: does the result of first_indexer_cls get passed to second_indexer_cls.__init__()?
        # TODO: are the settings shared between all analyzers?

    def test_get_data_5(self):
        """
        Test for the method :py:meth:`~IndexedPiece.get_data`.
        :returns: None
        """
        # get data from an Experimenter that requires an Indexer
        # (same as test 3, but second_indexer_cls is an Experimenter subclass)
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = [14]
        mock_indexer_cls.requires_score = True
        mock_experimenter_cls = type('MockIndexer', (Experimenter,), {})
        mock_experimenter_cls.run = MagicMock()
        mock_experimenter_cls.run.return_value = u'ahhh!'
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([mock_indexer_cls, mock_experimenter_cls]))
        mock_indexer_cls.run.assert_called_once_with()
        mock_experimenter_cls.run.assert_called_once_with()
        # TODO: does the result of first_indexer_cls get passed to second_indexer_cls.__init__()?

    def test_get_data_6(self):
        # That get_data() complains when an Indexer expects the results of another Indexer but
        # doesn't get them.
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.requires_score = False
        mock_indexer_cls.required_score_type = pandas.Series
        self.assertRaises(RuntimeError, self.ind_piece.get_data, [mock_indexer_cls])

    def test_get_data_7(self):
        # That get_data() complains when you call it with something that isn't either an Indexer
        # or Experimenter.
        self.assertRaises(TypeError, self.ind_piece.get_data, [TestIndexedPieceB])

class TestIndexedPieceB(TestCase):
    def test_import_score_1(self):
        # That get_data() fails with a file that imports as a music21.stream.Opus. Fixing this
        # properly is issue #234 on GitHub.
        test_piece = IndexedPiece(u'test_corpus/Sanctus.krn')
        self.assertRaises(NotImplementedError, test_piece._import_score)

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                       #
#--------------------------------------------------------------------------------------------------#
INDEXED_PIECE_SUITE_A = TestLoader().loadTestsFromTestCase(TestIndexedPieceA)
INDEXED_PIECE_SUITE_B = TestLoader().loadTestsFromTestCase(TestIndexedPieceB)

# TODO: test at least these things:
# 331
# - _find_piece_title() (tests can be ported from vis9c)
# - _find_part_names() (tests can be ported from vis9c)
# - __repr__(), __str__(), and __unicode__()
# - that _import_score() properly calls _find_piece_title()
# - that all the other metadata properties are properly converted to our Metadata attributes
