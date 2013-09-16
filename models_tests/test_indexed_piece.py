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
from vis.models.indexed_piece import IndexedPiece, _find_piece_title, _find_part_names


# pylint: disable=R0904
# pylint: disable=C0111
@patch('music21.converter.parse', new=lambda path: MagicMock(name=u'ScoreMock: ' + path,
                                                             spec=music21.stream.Score))
class TestIndexedPieceA(TestCase):
    def setUp(self):
        self._pathname = u'test_path'
        self.ind_piece = IndexedPiece(self._pathname)

    def test_metadata(self):
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
        # try getting data for a non-Indexer, non-Experimenter class
        non_analyzer = Mock()
        self.assertRaises(TypeError, self.ind_piece.get_data, non_analyzer)

    def test_get_data_1(self):
        # get data for an Indexer requiring a Score
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.requires_score = True
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = u'ahhh!'
        self.assertEquals(u'ahhh!', self.ind_piece.get_data([mock_indexer_cls]))
        mock_indexer_cls.run.assert_called_once_with()

    def test_get_data_2(self):
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
        # get data from an Experimenter that requires an Indexer
        # (same as test 3, but second_indexer_cls is an Experimenter subclass)
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = [14]
        mock_indexer_cls.requires_score = True
        mock_experimenter_cls = type('MockIndexer', (Experimenter,), {})
        mock_experimenter_cls.run = MagicMock()
        mock_experimenter_cls.run.return_value = u'ahhh!'
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([mock_indexer_cls,
                                                            mock_experimenter_cls]))
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

    def test_get_data_8(self):
        # That get_data() calls _get_note_rest_index() if asked for NoteRestIndexer.
        with patch.object(IndexedPiece, u'_get_note_rest_index') as mock_gnri:
            self.ind_piece.get_data([noterest.NoteRestIndexer])
            mock_gnri.assert_called_once_with()

    def test_get_data_9(self):
        # That get_data() calls _get_note_rest_index() if asked for NoteRestIndexer, and another
        # test Indexer is also called. This is a regression test to monitor a bug found after
        # implementing caching of NoteRestIndexer results.
        with patch.object(IndexedPiece, u'_get_note_rest_index') as mock_gnri:
            expected = [400]
            mock_indexer_cls = type('MockIndexer', (Indexer,), {})
            mock_indexer_cls.run = MagicMock()
            mock_indexer_cls.run.return_value = [400]
            mock_indexer_cls.requires_score = False
            actual = self.ind_piece.get_data([noterest.NoteRestIndexer, mock_indexer_cls])
            mock_gnri.assert_called_once_with()
            mock_indexer_cls.run.assert_called_once_with()
            self.assertEqual(expected, actual)

    def test_get_nrindex_1(self):
        # pylint: disable=W0212
        # That _get_note_rest_index() returns self._noterest_results if it's not None.
        self.ind_piece._noterest_results = 42
        self.assertEqual(42, self.ind_piece._get_note_rest_index())

    def test_get_nrindex_2(self):
        # pylint: disable=W0212
        # That we run the NoteRestIndexer and store results in self._note_rest_results if is None.
        with patch(u'vis.models.indexed_piece.noterest.NoteRestIndexer') as mock_nri_cls:
            mock_nri = MagicMock(return_value=[14])
            mock_nri.run = MagicMock()
            mock_nri.run.return_value = [14]
            #mock_nri.requires_score = True
            mock_nri_cls.return_value = mock_nri
            expected = [14]
            actual = self.ind_piece._get_note_rest_index()
            mock_nri.run.assert_called_once_with()
            self.assertEqual(expected, actual)
            self.assertEqual(expected, self.ind_piece._noterest_results)


class TestIndexedPieceB(TestCase):
    # NB: These are longer tests.
    def test_import_score_1(self):
        # pylint: disable=W0212
        # That get_data() fails with a file that imports as a music21.stream.Opus. Fixing this
        # properly is issue #234 on GitHub.
        test_piece = IndexedPiece(u'test_corpus/Sanctus.krn')
        self.assertRaises(NotImplementedError, test_piece._import_score)


class TestPartsAndTitles(TestCase):
   # NB: These tests take a while because they involve actual imports, then run the
   # _find_part_names() and _find_piece_title() methods.
   # NOTE: not testing "Sanctus.krn" because it's an Opus, and we can't deal with them yet.
    def test_bwv77(self):
        path = u'test_corpus/bwv77.mxl'
        expected_title = u'bwv77'
        expected_parts = [u'Soprano', u'Alto', u'Tenor', u'Bass']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_jos2308_krn(self):
        path = u'test_corpus/Jos2308.krn'
        expected_title = u'Jos2308'
        expected_parts = [u'spine_3', u'spine_2', u'spine_1', u'spine_0']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_kyrie(self):
        path = u'test_corpus/Kyrie.krn'
        expected_title = u'Kyrie'
        expected_parts = [u'spine_4', u'spine_3', u'spine_2', u'spine_1', u'spine_0']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_madrigal51(self):
        path = u'test_corpus/madrigal51.mxl'
        expected_title = u'madrigal51'
        expected_parts = [u'Canto', u'Alto', u'Tenor', u'Quinto', u'Basso', u'Continuo']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_sinfony(self):
        path = u'test_corpus/sinfony.md'
        expected_title = u'Messiah'
        expected_parts = [u'Violino I', u'Violino II', u'Viola', u'Bassi']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_sqOp76(self):
        path = u'test_corpus/sqOp76-4-i.midi'
        expected_title = u'sqOp76-4-i'
        expected_parts = [u'Part 1', u'Part 2', u'Part 3', u'Part 4']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_bwv2(self):
        path = u'test_corpus/bwv2.xml'
        expected_title = u'bwv2'
        expected_parts = [u'Soprano', u'Alto', u'Tenor', u'Bass']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INDEXED_PIECE_SUITE_A = TestLoader().loadTestsFromTestCase(TestIndexedPieceA)
INDEXED_PIECE_SUITE_B = TestLoader().loadTestsFromTestCase(TestIndexedPieceB)
INDEXED_PIECE_PARTS_TITLES = TestLoader().loadTestsFromTestCase(TestPartsAndTitles)

# TODO: test at least these things:
# - __repr__(), __str__(), and __unicode__()
# - that _import_score() properly calls _find_piece_title()
# - that all the other metadata properties are properly converted to our Metadata attributes
