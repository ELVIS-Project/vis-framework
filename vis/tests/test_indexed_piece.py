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

from unittest import TestCase, TestLoader
from mock import call, patch, MagicMock, Mock
import pandas
import music21
from vis.analyzers.indexer import Indexer
from vis.analyzers.indexers import noterest
from vis.analyzers.experimenter import Experimenter
from vis.models.indexed_piece import IndexedPiece, _find_piece_title, _find_part_names, OpusWarning


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
        self.assertRaises(AttributeError, self.ind_piece.metadata, 'invalid_field')
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
        mock_indexer_cls.required_score_type = music21.stream.Part
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = u'ahhh!'
        self.assertEquals(u'ahhh!', self.ind_piece.get_data([mock_indexer_cls]))
        mock_indexer_cls.run.assert_called_once_with()

    def test_get_data_2(self):
        # get data for an Indexer requiring other data
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_init = MagicMock()
        mock_init.return_value = None
        mock_indexer_cls.__init__ = mock_init
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = u'ahhh!'
        mock_indexer_cls.required_score_type = int
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([mock_indexer_cls], data=[14]))
        mock_indexer_cls.run.assert_called_once_with()
        mock_init.assert_called_once_with([14], None)

    def test_get_data_3(self):
        # get data from a chained Indexer
        first_indexer_cls = type('MockIndexer', (Indexer,), {})
        first_init = MagicMock()
        first_init.return_value = None
        first_indexer_cls.__init__ = first_init
        first_indexer_cls.run = MagicMock()
        first_indexer_cls.run.return_value = [14]
        first_indexer_cls.required_score_type = music21.stream.Part
        second_indexer_cls = type('MockIndexer', (Indexer,), {})
        second_init = MagicMock()
        second_init.return_value = None
        second_indexer_cls.__init__ = second_init
        second_indexer_cls.run = MagicMock()
        second_indexer_cls.run.return_value = u'ahhh!'
        second_indexer_cls.required_score_type = int
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([first_indexer_cls, second_indexer_cls]))
        first_init.assert_called_once_with([], None)
        second_init.assert_called_once_with(first_indexer_cls.run.return_value, None)
        first_indexer_cls.run.assert_called_once_with()
        second_indexer_cls.run.assert_called_once_with()

    def test_get_data_4(self):
        # chained Indexer plus settings
        first_indexer_cls = type('MockIndexer', (Indexer,), {})
        first_init = MagicMock()
        first_init.return_value = None
        first_indexer_cls.__init__ = first_init
        first_indexer_cls.run = MagicMock()
        first_indexer_cls.run.return_value = [14]
        first_indexer_cls.required_score_type = music21.stream.Part
        second_indexer_cls = type('MockIndexer', (Indexer,), {})
        second_init = MagicMock()
        second_init.return_value = None
        second_indexer_cls.__init__ = second_init
        second_indexer_cls.run = MagicMock()
        second_indexer_cls.run.return_value = u'ahhh!'
        second_indexer_cls.required_score_type = int
        settings_dict = {u'fake setting': u'so good!'}
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([first_indexer_cls, second_indexer_cls],
                                                           settings_dict))
        first_init.assert_called_once_with([], settings_dict)
        second_init.assert_called_once_with(first_indexer_cls.run.return_value, settings_dict)
        first_indexer_cls.run.assert_called_once_with()
        second_indexer_cls.run.assert_called_once_with()

    def test_get_data_5(self):
        # get data from an Experimenter that requires an Indexer
        # (same as test 3, but second_indexer_cls is an Experimenter subclass)
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_init = MagicMock()
        mock_init.return_value = None
        mock_indexer_cls.__init__ = mock_init
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = [14]
        mock_indexer_cls.required_score_type = music21.stream.Part
        mock_experimenter_cls = type('MockIndexer', (Experimenter,), {})
        exp_init = MagicMock()
        exp_init.return_value = None
        mock_experimenter_cls.__init__ = exp_init
        mock_experimenter_cls.run = MagicMock()
        mock_experimenter_cls.run.return_value = u'ahhh!'
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([mock_indexer_cls,
                                                            mock_experimenter_cls]))
        mock_init.assert_called_once_with([], None)
        exp_init.assert_called_once_with(mock_indexer_cls.run.return_value, None)
        mock_indexer_cls.run.assert_called_once_with()
        mock_experimenter_cls.run.assert_called_once_with()

    def test_get_data_6(self):
        # That get_data() complains when an Indexer expects the results of another Indexer but
        # doesn't get them.
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
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
            mock_gnri.assert_called_once_with(known_opus=False)

    def test_get_data_9(self):
        # That get_data() calls _get_note_rest_index() if asked for NoteRestIndexer, and another
        # test Indexer is also called. This is a regression test to monitor a bug found after
        # implementing caching of NoteRestIndexer results. Also ensure that NoteRestIndexer is only
        # instantiated once
        with patch.object(IndexedPiece, u'_get_note_rest_index') as mock_gnri:
            mock_gnri.return_value = 42
            with patch.object(IndexedPiece, u'_type_verifier') as mock_tv:
                # we'll mock _type_verifier() to avoid getting a TypeError when mock_nri_cls isn't
                # a proper subclass of Indexer
                expected = [400]
                mock_indexer_cls = type('MockIndexer', (Indexer,), {})
                mock_indexer_cls.__init__ = MagicMock()
                mock_indexer_cls.__init__.return_value = None
                mock_indexer_cls.run = MagicMock()
                mock_indexer_cls.run.return_value = expected
                actual = self.ind_piece.get_data([noterest.NoteRestIndexer, mock_indexer_cls])
                self.assertEqual(2, mock_tv.call_count)
                mock_tv.assert_has_calls([call([noterest.NoteRestIndexer, mock_indexer_cls]),
                                            call([mock_indexer_cls])])
                mock_gnri.assert_called_once_with(known_opus=False)
                mock_indexer_cls.__init__.assert_called_once_with(mock_gnri.return_value, None)
                mock_indexer_cls.run.assert_called_once_with()
                self.assertEqual(expected, actual)

    def test_get_data_10(self):
        # That get_data() calls _get_note_rest_index() if asked for NoteRestIndexer. This is a
        # regression test to monitor a bug found after implementing caching of NoteRestIndexer
        # results. Also ensure that NoteRestIndexer is only instantiated once
        with patch.object(IndexedPiece, u'_get_note_rest_index') as mock_gnri:
            mock_gnri.return_value = 42
            with patch.object(IndexedPiece, u'_type_verifier') as mock_tv:
                # we'll mock _type_verifier() to avoid getting a TypeError when mock_nri_cls isn't
                # a proper subclass of Indexer
                actual = self.ind_piece.get_data([noterest.NoteRestIndexer])
                mock_tv.assert_called_once_with([noterest.NoteRestIndexer])
                mock_gnri.assert_called_once_with(known_opus=False)
                self.assertEqual(mock_gnri.return_value, actual)

    def test_get_data_11(self):
        # That get_data() correctly passes its "known_opus" parameter to _get_note_rest_indexer()
        # and _import_score()
        with patch.object(IndexedPiece, u'_get_note_rest_index') as mock_gnri:
            self.ind_piece.get_data([noterest.NoteRestIndexer], known_opus='battery')
            mock_gnri.assert_called_once_with(known_opus='battery')
        with patch.object(IndexedPiece, u'_import_score') as mock_is:
            with patch.object(IndexedPiece, u'_type_verifier') as mock_tv:
                mock_ind = MagicMock()
                mock_ind.required_score_type = music21.stream.Part
                self.ind_piece.get_data([mock_ind], known_opus='horse')
                mock_is.assert_called_once_with(known_opus='horse')

    def test_get_data_12(self):
        # get data for an Experimenter requiring other data; this is test 2, slightly modified
        mock_experimenter_cls = type('MockExperimenter', (Experimenter,), {})
        mock_experimenter_cls.__init__ = MagicMock(return_value=None)
        mock_experimenter_cls.run = MagicMock(return_value=u'ahhh!')
        prev_data= u'data from the previous analyzers'
        self.assertEqual(u'ahhh!', self.ind_piece.get_data([mock_experimenter_cls], {}, prev_data))
        mock_experimenter_cls.run.assert_called_once_with()
        mock_experimenter_cls.__init__.assert_called_once_with(prev_data, {})

    def test_type_verifier_1(self):
        # with an Indexer
        # pylint: disable=W0212
        self.assertEqual(None, IndexedPiece._type_verifier([noterest.NoteRestIndexer]))

    def test_type_verifier_2(self):
        # with an Experimenter
        # pylint: disable=W0212
        cls = type('TestExperimenter', (Experimenter,), {})
        self.assertEqual(None, IndexedPiece._type_verifier([cls]))

    def test_type_verifier_3(self):
        # with another class
        # pylint: disable=W0212
        cls = type('TestGarbage', (object,), {})
        self.assertRaises(TypeError, IndexedPiece._type_verifier, [cls])

    def test_type_verifier_4(self):
        # with a bunch of valid classes
        # pylint: disable=W0212
        cls_1 = type('TestExperimenter1', (Experimenter,), {})
        cls_2 = type('TestExperimenter2', (Experimenter,), {})
        cls_3 = type('TestIndexer', (Indexer,), {})
        self.assertEqual(None, IndexedPiece._type_verifier([cls_1, cls_2, cls_3]))

    def test_type_verifier_5(self):
        # with a bunch of valid, but one invalid, class
        # pylint: disable=W0212
        cls_1 = type('TestExperimenter1', (Experimenter,), {})
        cls_2 = type('TestIndexer', (Indexer,), {})
        cls_3 = type('TestGarbage', (object,), {})
        self.assertRaises(TypeError, IndexedPiece._type_verifier, [cls_1, cls_2, cls_3])

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
            mock_nri_cls.return_value = mock_nri
            expected = [14]
            actual = self.ind_piece._get_note_rest_index()
            mock_nri.run.assert_called_once_with()
            self.assertEqual(expected, actual)
            self.assertEqual(expected, self.ind_piece._noterest_results)

    def test_get_nrindex_3(self):
        # That _get_note_rest_index() just flat-out calls _import_score() when "known_opus" is True
        with patch.object(IndexedPiece, u'_import_score') as mock_is:
            with patch.object(noterest.NoteRestIndexer, u'run') as mock_nri:
                self.ind_piece._get_note_rest_index(known_opus=True)
                mock_is.assert_called_once_with(known_opus=True)
                self.assertEqual(0, mock_nri.call_count)

    def test_unicode_1(self):
        # __unicode__() without having imported yet
        # NB: adjusting _imported is the whole point of the test
        # pylint: disable=W0212
        self.ind_piece._imported = False
        with patch(u'vis.models.indexed_piece.IndexedPiece.metadata') as mock_meta:
            mock_meta.return_value = u'42'
            expected = u'<IndexedPiece (42)>'
            actual = self.ind_piece.__unicode__()
            self.assertEqual(expected, actual)
            mock_meta.assert_called_once_with(u'pathname')

    def test_unicode_2(self):
        # __unicode__() with proper title and composer
        # NB: adjusting _imported is the whole point of the test
        # pylint: disable=W0212
        self.ind_piece._imported = True
        with patch(u'vis.models.indexed_piece.IndexedPiece.metadata') as mock_meta:
            returns = [u'some ridiculous piece', u'a no-name composer']
            def side_effect(*args):
                # NB: we need to accept "args" as a mock framework formality
                # pylint: disable=W0613
                return returns.pop(0)
            mock_meta.side_effect = side_effect
            expected = u'<IndexedPiece (some ridiculous piece by a no-name composer)>'
            actual = self.ind_piece.__unicode__()
            self.assertEqual(expected, actual)
            expected_calls = [call(u'title'), call(u'composer')]
            self.assertSequenceEqual(expected_calls, mock_meta.call_args_list)


class TestIndexedPieceB(TestCase):
    def setUp(self):
        self._pathname = u'test_path'
        self.ind_piece = IndexedPiece(self._pathname)

    def test_import_score_1(self):
        # That _import_score() raises an OpusWarning when it imports an Opus but "expect_opus" is
        # False
        with patch(u'vis.models.indexed_piece.converter.parse') as mock_parse:
            mock_parse.return_value = music21.stream.Opus()
            self.assertRaises(OpusWarning, self.ind_piece._import_score, known_opus=False)

    def test_import_score_2(self):
        # That _import_score() returns multiple IndexedPiece objects when it imports an Opus and
        # "expect_opus" is True
        with patch(u'vis.models.indexed_piece.converter.parse') as mock_parse:
            mock_parse.return_value = music21.stream.Opus()
            for _ in xrange(5):
                mock_parse.return_value.insert(music21.stream.Score())
            actual = self.ind_piece._import_score(known_opus=True)
            self.assertEqual(5, len(actual))
            for i, piece in enumerate(actual):
                self.assertTrue(isinstance(piece, IndexedPiece))
                self.assertEqual(i, piece._opus_id)

    def test_import_score_3(self):
        # That _import_score() raises an OpusWarning when "expect_opus" is True, but it doesn't
        # import an Opus
        with patch(u'vis.models.indexed_piece.converter.parse') as mock_parse:
            mock_parse.return_value = music21.stream.Score()
            self.assertRaises(OpusWarning, self.ind_piece._import_score, known_opus=True)

    def test_import_score_4(self):
        # That _import_score() returns the right Score object when it imports an Opus
        with patch(u'vis.models.indexed_piece.converter.parse') as mock_parse:
            mock_parse.return_value = music21.stream.Opus()
            for i in xrange(5):
                mock_parse.return_value.insert(music21.stream.Score())
                mock_parse.return_value[i].priority = 42 + i
            actual = self.ind_piece._import_score(known_opus=True)
            self.assertEqual(5, len(actual))
            for i, piece in enumerate(actual):
                self.assertEqual(42 + i, piece._import_score().priority)

    # TODO: write more tests here, bro


class TestPartsAndTitles(TestCase):
   # NB: These tests take a while because they involve actual imports, then run the
   # _find_part_names() and _find_piece_title() methods.
   # NOTE: not testing "Sanctus.krn" because it's an Opus, and we can't deal with them yet.
    def test_bwv77(self):
        path = u'vis/tests/corpus/bwv77.mxl'
        expected_title = u'bwv77'
        expected_parts = [u'Soprano', u'Alto', u'Tenor', u'Bass']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_jos2308_krn(self):
        path = u'vis/tests/corpus/Jos2308.krn'
        expected_title = u'Jos2308'
        expected_parts = [u'spine_3', u'spine_2', u'spine_1', u'spine_0']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_kyrie(self):
        path = u'vis/tests/corpus/Kyrie.krn'
        expected_title = u'Kyrie'
        expected_parts = [u'spine_4', u'spine_3', u'spine_2', u'spine_1', u'spine_0']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_madrigal51(self):
        path = u'vis/tests/corpus/madrigal51.mxl'
        expected_title = u'madrigal51'
        expected_parts = [u'Canto', u'Alto', u'Tenor', u'Quinto', u'Basso', u'Continuo']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_sinfony(self):
        path = u'vis/tests/corpus/sinfony.md'
        expected_title = u'Messiah'
        expected_parts = [u'Violino I', u'Violino II', u'Viola', u'Bassi']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_opus76(self):
        path = u'vis/tests/corpus/sqOp76-4-i.midi'
        expected_title = u'sqOp76-4-i'
        expected_parts = [u'Part 1', u'Part 2', u'Part 3', u'Part 4']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_bwv2(self):
        path = u'vis/tests/corpus/bwv2.xml'
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
