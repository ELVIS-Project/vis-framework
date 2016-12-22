#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models_tests/test_indexed_piece.py
# Purpose:                Tests for models/indexed_piece.py.
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
Tests for :py:class:`~vis.models.indexed_piece.IndexedPiece`.
"""

import os
from unittest import TestCase, TestLoader
import six
if six.PY3:
    from unittest import mock
    from unittest.mock import call, patch, MagicMock, Mock
else:
    import mock
    from mock import call, patch, MagicMock, Mock
import pandas
import music21
from music21 import converter
from vis.analyzers.indexer import Indexer
from vis.analyzers.indexers import noterest
from vis.analyzers.experimenter import Experimenter
from vis.models.indexed_piece import Importer, IndexedPiece, _find_piece_title, _find_part_names, _find_piece_range, _find_part_ranges, login_edb, auth_get
# find pathname to the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]

# pylint: disable=R0904
# pylint: disable=C0111
#@patch('music21.converter.Converter', new=lambda: MagicMock(spec_set=music21.converter.Converter,
                                                            #parseFile=MagicMock(return_value=lambda *x: MagicMock(name='MockScore {}'.format(x[0]), spec_set=music21.stream.Score))))
class TestIndexedPieceA(TestCase):
    """The 'A' part of tests for IndexedPiece."""

    def setUp(self):
        """Set up some stuff."""
        self._pathname = 'test_path'
        self.ind_piece = IndexedPiece(self._pathname)

    def test_metadata(self):
        """access fields that are set by default"""
        pathname = self.ind_piece.metadata('pathname')
        self.assertEquals(self._pathname, pathname, "pathname has changed!")
        # assign a value to a valid field
        self.ind_piece.metadata('date', 2)
        value = self.ind_piece.metadata('date')
        self.assertEquals(2, value, "extracted metadata field doesn't match assigned value")
        # assign a value to an invalid field
        self.assertRaises(AttributeError, self.ind_piece.metadata, 'field', 2)
        # access an invalid value
        self.assertRaises(AttributeError, self.ind_piece.metadata, 'invalid_field')
        # try accessing keys with invalid types
        self.assertRaises(TypeError, self.ind_piece.metadata, 2)
        self.assertRaises(TypeError, self.ind_piece.metadata, [])
        self.assertRaises(TypeError, self.ind_piece.metadata, {})

    def test_get_data_0(self):
        """try getting data for a non-Indexer, non-Experimenter class"""
        non_analyzer = Mock()
        self.assertRaises(KeyError, self.ind_piece.get_data, non_analyzer)

    def test_get_data_1(self):
        """
        That get_data() complains when an Indexer expects the results of another Indexer but
        doesn't get them.
        """
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.required_score_type = pandas.DataFrame
        self.assertRaises(RuntimeWarning, self.ind_piece.get_data, vis.analyzers.indexers.ngram.NGramIndexer)

    def test_get_data_2(self):
        """
        That get_data() complains when you call it with something that isn't either an Indexer
        or Experimenter.
        """
        self.assertRaises(KeyError, self.ind_piece.get_data, TestIndexedPieceA)

    def test_get_nrindex_1(self):
        """That _get_noterest() returns self._analyses['noterest'] if it's not None."""
        # pylint: disable=W0212
        self.ind_piece._analyses['noterest'] = 42
        self.assertEqual(42, self.ind_piece._get_noterest())

    def test_str_1(self):
        """__str__() without having imported yet"""
        # NB: adjusting _imported is the whole point of the test
        # pylint: disable=W0212
        self.ind_piece._imported = False
        with patch('vis.models.indexed_piece.IndexedPiece.metadata') as mock_meta:
            mock_meta.return_value = '42'
            expected = '<IndexedPiece (42)>'
            actual = self.ind_piece.__str__()
            self.assertEqual(expected, actual)
            mock_meta.assert_called_once_with('pathname')

    def test_str_2(self):
        """__str__() with proper title and composer"""
        # NB: adjusting _imported is the whole point of the test
        # pylint: disable=W0212
        self.ind_piece._imported = True
        with patch('vis.models.indexed_piece.IndexedPiece.metadata') as mock_meta:
            returns = ['some ridiculous piece', 'a no-name composer']
            def side_effect(*args):
                # NB: we need to accept "args" as a mock framework formality
                # pylint: disable=W0613
                return returns.pop(0)
            mock_meta.side_effect = side_effect
            expected = '<IndexedPiece (some ridiculous piece by a no-name composer)>'
            actual = self.ind_piece.__str__()
            self.assertEqual(expected, actual)
            expected_calls = [call('title'), call('composer')]
            self.assertSequenceEqual(expected_calls, mock_meta.call_args_list)


class TestPartsAndTitles(TestCase):
   # NB: These tests take a while because they involve actual imports, then run the
   # _find_part_names() and _find_piece_title() methods. The different files are actually 
   # different filetypes.
   # NOTE: not testing "Sanctus.krn" because it's an Opus, and we can't deal with them yet.
    def test_bwv77(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')
        expected_title = 'bwv77'
        expected_parts = ['Soprano', 'Alto', 'Tenor', 'Bass']
        the_score = Importer(path)._score
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score.parts)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_jos2308_krn(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'Jos2308.krn')
        expected_title = 'Jos2308'
        expected_parts = ['spine_3', 'spine_2', 'spine_1', 'spine_0']
        the_score = Importer(path)._score
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_sinfony(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'sinfony.md')
        expected_title = 'Messiah'
        expected_parts = ['Violino I', 'Violino II', 'Viola', 'Bassi']
        the_score = Importer(path)._score
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score.parts)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_opus76(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'sqOp76-4-i.midi')
        expected_title = 'sqOp76-4-i'
        expected_parts = ['Part 1', 'Part 2', 'Part 3', 'Part 4']
        the_score = Importer(path)._score
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score.parts)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_bwv2(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv2.xml')
        expected_title = 'bwv2'
        expected_parts = ['Soprano', 'Alto', 'Tenor', 'Bass']
        the_score = Importer(path)._score
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score.parts)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_piece_range(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv2.xml')
        score = Importer(path)._score
        expected_range = ('A2', 'E5')
        actual_range = _find_piece_range(score)
        self.assertEqual(expected_range, actual_range)

    def test_part_ranges(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv2.xml')
        score = Importer(path)._score
        expected_range = [('E4', 'E5'), ('E3', 'B4'), ('F#3', 'A4'), ('A2', 'C4')]
        actual_range = _find_part_ranges(score)
        self.assertEqual(expected_range, actual_range)

class TestIndexedPieceC(TestCase):

    def test_meta(self):
        meta = os.path.join(VIS_PATH, 'tests', 'corpus', 'meta')
        piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
        ind = IndexedPiece(piece, metafile=meta)
        self.assertEqual('Sacred', ind.metadata('religiosity'))

    # These two tests are turned off until we can test without having to link to the ELVIS Database.
    # def test_json(self):
    #     meta = 'http://database.elvisproject.ca/piece/1971/?format=json'
    #     username = 'mborsodi'
    #     password = 'lalalalala'
    #     piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
    #     ind = IndexedPiece(piece, metafile=meta, username=username, password=password)
    #     self.assertEqual('Missa Fortuna desperata', ind.metadata('title'))

    # def test_json2(self):
    #     meta = 'http://database.elvisproject.ca/piece/1971/'
    #     username = 'mborsodi'
    #     password = 'lalalalala'
    #     piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
    #     ind = IndexedPiece(piece, metafile=meta, username=username, password=password)
    #     self.assertEqual('Missa Fortuna desperata', ind.metadata('title'))

    def test_missing_usrn(self):
        meta = 'http://database.elvisproject.ca/piece/1971/'
        piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
        try:
            IndexedPiece(piece, metafile=meta)
        except RuntimeError as run_err:
            self.assertEqual(IndexedPiece._MISSING_USERNAME, run_err.args[0])

    def test_missing_pswrd(self):
        meta = 'http://database.elvisproject.ca/piece/1971/'
        piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
        try:
            IndexedPiece(piece, metafile=meta, username='mborsodi')
        except RuntimeError as run_err:
            self.assertEqual(IndexedPiece._MISSING_PASSWORD, run_err.args[0])


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INDEXED_PIECE_SUITE_A = TestLoader().loadTestsFromTestCase(TestIndexedPieceA)
INDEXED_PIECE_PARTS_TITLES = TestLoader().loadTestsFromTestCase(TestPartsAndTitles)
INDEXED_PIECE_SUITE_C = TestLoader().loadTestsFromTestCase(TestIndexedPieceC)
