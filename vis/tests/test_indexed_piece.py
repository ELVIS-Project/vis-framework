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
from vis.models.indexed_piece import IndexedPiece, _find_piece_title, _find_part_names, OpusWarning, _find_piece_range, _find_part_ranges, login_edb, auth_get
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
        self.assertRaises(TypeError, self.ind_piece.get_data, non_analyzer)

    @patch('vis.models.indexed_piece.IndexedPiece._import_score')
    def test_get_data_1a(self, mock_is):
        """get data for an Indexer requiring a [Part]"""
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.required_score_type = 'stream.Part'
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = 'ahhh!'
        expected = 'ahhh!'
        mock_is.return_value = MagicMock(spec_set=music21.stream.Score)
        mock_is.return_value.parts = [MagicMock(spec_set=music21.stream.Part)]

        actual = self.ind_piece.get_data([mock_indexer_cls])

        self.assertEquals(expected, actual)
        mock_is.assert_called_once_with(known_opus=False)
        mock_indexer_cls.run.assert_called_once_with()

    @patch('vis.models.indexed_piece.IndexedPiece._import_score')
    def test_get_data_1a(self, mock_is):
        """get data for an Indexer requiring a [Part]"""
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.required_score_type = 'stream.Score'
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = 'ahhh!'
        expected = 'ahhh!'
        mock_is.return_value = MagicMock(spec_set=music21.stream.Score)

        actual = self.ind_piece.get_data([mock_indexer_cls])

        self.assertEquals(expected, actual)
        mock_is.assert_called_once_with(known_opus=False)
        mock_indexer_cls.run.assert_called_once_with()

    def test_get_data_2(self):
        """get data for an Indexer requiring other data"""
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_init = MagicMock()
        mock_init.return_value = None
        mock_indexer_cls.__init__ = mock_init
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = 'ahhh!'
        mock_indexer_cls.required_score_type = int
        self.assertEqual('ahhh!', self.ind_piece.get_data([mock_indexer_cls], data=[14]))
        mock_indexer_cls.run.assert_called_once_with()
        mock_init.assert_called_once_with([14], None)

    @mock.patch('vis.models.indexed_piece.converter')
    def test_get_data_3(self, mock_conv):
        """get data from a chained Indexer"""
        # set up the mock converter
        mock_con_class = mock.MagicMock(spec_set=converter.Converter())
        mock_con_class.parseFile = mock.MagicMock(return_value=None)
        mock_conv.Converter.return_value = mock_con_class
        # the rest
        first_indexer_cls = type('MockIndexer', (Indexer,), {})
        first_init = MagicMock(spec_set=Indexer)
        first_init.return_value = None
        first_indexer_cls.__init__ = first_init
        first_indexer_cls.run = MagicMock()
        first_indexer_cls.run.return_value = [14]
        first_indexer_cls.required_score_type = 'stream.Part'
        second_indexer_cls = type('MockIndexer', (Indexer,), {})
        second_init = MagicMock(spec_set=Indexer)
        second_init.return_value = None
        second_indexer_cls.__init__ = second_init
        second_indexer_cls.run = MagicMock()
        second_indexer_cls.run.return_value = 'ahhh!'
        second_indexer_cls.required_score_type = int
        self.assertEqual('ahhh!', self.ind_piece.get_data([first_indexer_cls, second_indexer_cls]))
        first_init.assert_called_once_with([], None)
        second_init.assert_called_once_with(first_indexer_cls.run.return_value, None)
        first_indexer_cls.run.assert_called_once_with()
        second_indexer_cls.run.assert_called_once_with()

    @mock.patch('vis.models.indexed_piece.converter')
    def test_get_data_4(self, mock_conv):
        """chained Indexer plus settings"""
        # set up the mock converter
        mock_con_class = mock.MagicMock(spec_set=converter.Converter())
        mock_con_class.parseFile = mock.MagicMock(return_value=None)
        mock_conv.Converter.return_value = mock_con_class
        # the rest
        first_indexer_cls = type('MockIndexer', (Indexer,), {})
        first_init = MagicMock()
        first_init.return_value = None
        first_indexer_cls.__init__ = first_init
        first_indexer_cls.run = MagicMock()
        first_indexer_cls.run.return_value = [14]
        first_indexer_cls.required_score_type = 'stream.Part'
        second_indexer_cls = type('MockIndexer', (Indexer,), {})
        second_init = MagicMock()
        second_init.return_value = None
        second_indexer_cls.__init__ = second_init
        second_indexer_cls.run = MagicMock()
        second_indexer_cls.run.return_value = 'ahhh!'
        second_indexer_cls.required_score_type = int
        settings_dict = {'fake setting': 'so good!'}
        self.assertEqual('ahhh!', self.ind_piece.get_data([first_indexer_cls, second_indexer_cls],
                                                           settings_dict))
        first_init.assert_called_once_with([], settings_dict)
        second_init.assert_called_once_with(first_indexer_cls.run.return_value, settings_dict)
        first_indexer_cls.run.assert_called_once_with()
        second_indexer_cls.run.assert_called_once_with()

    @mock.patch('vis.models.indexed_piece.converter')
    def test_get_data_5(self, mock_conv):
        """
        get data from an Experimenter that requires an Indexer
        (same as test 3, but second_indexer_cls is an Experimenter subclass)
        """
        # set up the mock converter
        mock_con_class = mock.MagicMock(spec_set=converter.Converter())
        mock_con_class.parseFile = mock.MagicMock(return_value=None)
        mock_conv.Converter.return_value = mock_con_class
        # the rest
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_init = MagicMock()
        mock_init.return_value = None
        mock_indexer_cls.__init__ = mock_init
        mock_indexer_cls.run = MagicMock()
        mock_indexer_cls.run.return_value = [14]
        mock_indexer_cls.required_score_type = 'stream.Part'
        mock_experimenter_cls = type('MockIndexer', (Experimenter,), {})
        exp_init = MagicMock()
        exp_init.return_value = None
        mock_experimenter_cls.__init__ = exp_init
        mock_experimenter_cls.run = MagicMock()
        mock_experimenter_cls.run.return_value = 'ahhh!'
        self.assertEqual('ahhh!', self.ind_piece.get_data([mock_indexer_cls,
                                                            mock_experimenter_cls]))
        mock_init.assert_called_once_with([], None)
        exp_init.assert_called_once_with(mock_indexer_cls.run.return_value, None)
        mock_indexer_cls.run.assert_called_once_with()
        mock_experimenter_cls.run.assert_called_once_with()

    def test_get_data_6(self):
        """
        That get_data() complains when an Indexer expects the results of another Indexer but
        doesn't get them.
        """
        mock_indexer_cls = type('MockIndexer', (Indexer,), {})
        mock_indexer_cls.required_score_type = pandas.Series
        self.assertRaises(RuntimeError, self.ind_piece.get_data, [mock_indexer_cls])

    def test_get_data_7(self):
        """
        That get_data() complains when you call it with something that isn't either an Indexer
        or Experimenter.
        """
        self.assertRaises(TypeError, self.ind_piece.get_data, [TestIndexedPieceB])

    def test_get_data_8(self):
        """That get_data() calls _get_note_rest_index() if asked for NoteRestIndexer."""
        with patch.object(IndexedPiece, '_get_note_rest_index') as mock_gnri:
            self.ind_piece.get_data([noterest.NoteRestIndexer])
            mock_gnri.assert_called_once_with(known_opus=False)

    def test_get_data_9(self):
        """
        That get_data() calls _get_note_rest_index() if asked for NoteRestIndexer, and another
        test Indexer is also called. This is a regression test to monitor a bug found after
        implementing caching of NoteRestIndexer results. Also ensure that NoteRestIndexer is only
        instantiated once.
        """
        with patch.object(IndexedPiece, '_get_note_rest_index') as mock_gnri:
            mock_gnri.return_value = 42
            with patch.object(IndexedPiece, '_type_verifier') as mock_tv:
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
        """
        # That get_data() calls _get_note_rest_index() if asked for NoteRestIndexer. This is a
        # regression test to monitor a bug found after implementing caching of NoteRestIndexer
        # results. Also ensure that NoteRestIndexer is only instantiated once
        """
        with patch.object(IndexedPiece, '_get_note_rest_index') as mock_gnri:
            mock_gnri.return_value = 42
            with patch.object(IndexedPiece, '_type_verifier') as mock_tv:
                # we'll mock _type_verifier() to avoid getting a TypeError when mock_nri_cls isn't
                # a proper subclass of Indexer
                actual = self.ind_piece.get_data([noterest.NoteRestIndexer])
                mock_tv.assert_called_once_with([noterest.NoteRestIndexer])
                mock_gnri.assert_called_once_with(known_opus=False)
                self.assertEqual(mock_gnri.return_value, actual)

    def test_get_data_11(self):
        """
        # That get_data() correctly passes its "known_opus" parameter to _get_note_rest_indexer()
        # and _import_score()
        """
        with patch.object(IndexedPiece, '_get_note_rest_index') as mock_gnri:
            self.ind_piece.get_data([noterest.NoteRestIndexer], known_opus='battery')
            mock_gnri.assert_called_once_with(known_opus='battery')
        with patch.object(IndexedPiece, '_import_score') as mock_is:
            with patch.object(IndexedPiece, '_type_verifier') as mock_tv:
                mock_ind = MagicMock()
                mock_ind.required_score_type = 'stream.Part'
                self.ind_piece.get_data([mock_ind], known_opus='horse')
                mock_is.assert_called_once_with(known_opus='horse')

    def test_get_data_12(self):
        """get data for an Experimenter requiring other data; this is test 2, slightly modified"""
        mock_experimenter_cls = type('MockExperimenter', (Experimenter,), {})
        mock_experimenter_cls.__init__ = MagicMock(return_value=None)
        mock_experimenter_cls.run = MagicMock(return_value='ahhh!')
        prev_data = 'data from the previous analyzers'
        self.assertEqual('ahhh!', self.ind_piece.get_data([mock_experimenter_cls], {}, prev_data))
        mock_experimenter_cls.run.assert_called_once_with()
        mock_experimenter_cls.__init__.assert_called_once_with(prev_data, {})

    def test_type_verifier_1(self):
        """with an Indexer"""
        # pylint: disable=W0212
        self.assertEqual(None, IndexedPiece._type_verifier([noterest.NoteRestIndexer]))

    def test_type_verifier_2(self):
        """with an Experimenter"""
        # pylint: disable=W0212
        cls = type('TestExperimenter', (Experimenter,), {})
        self.assertEqual(None, IndexedPiece._type_verifier([cls]))

    def test_type_verifier_3(self):
        """with another class"""
        # pylint: disable=W0212
        cls = type('TestGarbage', (object,), {})
        self.assertRaises(TypeError, IndexedPiece._type_verifier, [cls])

    def test_type_verifier_4(self):
        """with a bunch of valid classes"""
        # pylint: disable=W0212
        cls_1 = type('TestExperimenter1', (Experimenter,), {})
        cls_2 = type('TestExperimenter2', (Experimenter,), {})
        cls_3 = type('TestIndexer', (Indexer,), {})
        self.assertEqual(None, IndexedPiece._type_verifier([cls_1, cls_2, cls_3]))

    def test_type_verifier_5(self):
        """with a bunch of valid, but one invalid, class"""
        # pylint: disable=W0212
        cls_1 = type('TestExperimenter1', (Experimenter,), {})
        cls_2 = type('TestIndexer', (Indexer,), {})
        cls_3 = type('TestGarbage', (object,), {})
        self.assertRaises(TypeError, IndexedPiece._type_verifier, [cls_1, cls_2, cls_3])

    def test_get_nrindex_1(self):
        """That _get_note_rest_index() returns self._noterest_results if it's not None."""
        # pylint: disable=W0212
        self.ind_piece._noterest_results = 42
        self.assertEqual(42, self.ind_piece._get_note_rest_index())

    @mock.patch('vis.models.indexed_piece.converter')
    def test_get_nrindex_2(self, mock_conv):
        """That we run the NoteRestIndexer and store results in self._note_rest_results if is None."""
        # pylint: disable=W0212
        # set up the mock converter
        mock_con_class = mock.MagicMock(spec_set=converter.Converter())
        mock_con_class.parseFile = mock.MagicMock(return_value=None)
        mock_conv.Converter.return_value = mock_con_class
        # the rest
        with patch('vis.models.indexed_piece.noterest.NoteRestIndexer') as mock_nri_cls:
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
        """That _get_note_rest_index() just flat-out calls _import_score() when "known_opus" is True"""
        with patch.object(IndexedPiece, '_import_score') as mock_is:
            with patch.object(noterest.NoteRestIndexer, 'run') as mock_nri:
                self.ind_piece._get_note_rest_index(known_opus=True)
                mock_is.assert_called_once_with(known_opus=True)
                self.assertEqual(0, mock_nri.call_count)

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


class TestIndexedPieceB(TestCase):
    """The 'B' part of tests for IndexedPiece."""

    def setUp(self):
        """Set up some stuff."""
        self._pathname = 'test_path'
        self.ind_piece = IndexedPiece(self._pathname)

    @mock.patch('vis.models.indexed_piece.converter')
    def test_import_score_1(self, mock_conv):
        """
        That _import_score() raises an OpusWarning when it imports an Opus but "expect_opus" is
        False
        """
        mock_con_class = mock.MagicMock(spec_set=converter.Converter())
        mock_con_class.parseFile = mock.MagicMock(return_value=None)
        mock_con_class.stream = music21.stream.Opus()
        mock_conv.Converter.return_value = mock_con_class

        self.assertRaises(OpusWarning, self.ind_piece._import_score, known_opus=False)

    @mock.patch('vis.models.indexed_piece.converter')
    def test_import_score_2(self, mock_conv):
        """
        That _import_score() returns multiple IndexedPiece objects when it imports an Opus and
        "expect_opus" is True
        """
        mock_con_class = mock.MagicMock(spec_set=converter.Converter())
        mock_con_class.parseFile = mock.MagicMock(return_value=None)
        mock_con_class.stream = music21.stream.Opus()
        for _ in range(5):
            mock_con_class.stream.insert(music21.stream.Score())
        mock_conv.Converter.return_value = mock_con_class

        actual = self.ind_piece._import_score(known_opus=True)

        self.assertEqual(5, len(actual))
        for i, piece in enumerate(actual):
            self.assertTrue(isinstance(piece, IndexedPiece))
            self.assertEqual(i, piece._opus_id)

    @mock.patch('vis.models.indexed_piece.converter')
    def test_import_score_3(self, mock_conv):
        """
        That _import_score() raises an OpusWarning when "expect_opus" is True, but it doesn't
        import an Opus.
        """
        mock_con_class = mock.MagicMock(spec_set=converter.Converter())
        mock_con_class.parseFile = mock.MagicMock(return_value=None)
        mock_con_class.stream = music21.stream.Score()
        mock_conv.Converter.return_value = mock_con_class

        self.assertRaises(OpusWarning, self.ind_piece._import_score, known_opus=True)

    @mock.patch('vis.models.indexed_piece.converter')
    def test_import_score_4(self, mock_conv):
        """That _import_score() returns the right Score object when it imports an Opus."""
        mock_con_class = mock.MagicMock(spec_set=converter.Converter())
        mock_con_class.parseFile = mock.MagicMock(return_value=None)
        mock_con_class.stream = music21.stream.Opus()
        for i in range(5):
            mock_con_class.stream.insert(music21.stream.Score())
            # vis_import_order is an attribute just created for this test. vis_import_order is meant
            # represent the order in which pieces inside of an opus are stored.
            mock_con_class.stream[i].vis_import_order = 42 + i
        mock_conv.Converter.return_value = mock_con_class

        actual = self.ind_piece._import_score(known_opus=True)

        self.assertEqual(5, len(actual))
        for i, piece in enumerate(actual):
            self.assertEqual(42 + i, piece._import_score().vis_import_order)

    # TODO: write more tests here, bro


class TestPartsAndTitles(TestCase):
   # NB: These tests take a while because they involve actual imports, then run the
   # _find_part_names() and _find_piece_title() methods.
   # NOTE: not testing "Sanctus.krn" because it's an Opus, and we can't deal with them yet.
    def test_bwv77(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv77.mxl')
        expected_title = 'bwv77'
        expected_parts = ['Soprano', 'Alto', 'Tenor', 'Bass']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_jos2308_krn(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'Jos2308.krn')
        expected_title = 'Jos2308'
        expected_parts = ['spine_3', 'spine_2', 'spine_1', 'spine_0']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_kyrie(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'Kyrie.krn')
        expected_title = 'Kyrie'
        expected_parts = ['spine_4', 'spine_3', 'spine_2', 'spine_1', 'spine_0']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_madrigal51(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'madrigal51.mxl')
        expected_title = 'madrigal51'
        expected_parts = ['Canto', 'Alto', 'Tenor', 'Quinto', 'Basso', 'Continuo']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_sinfony(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'sinfony.md')
        expected_title = 'Messiah'
        expected_parts = ['Violino I', 'Violino II', 'Viola', 'Bassi']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_opus76(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'sqOp76-4-i.midi')
        expected_title = 'sqOp76-4-i'
        expected_parts = ['Part 1', 'Part 2', 'Part 3', 'Part 4']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_bwv2(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv2.xml')
        expected_title = 'bwv2'
        expected_parts = ['Soprano', 'Alto', 'Tenor', 'Bass']
        the_score = music21.converter.parse(path)
        actual_title = _find_piece_title(the_score)
        actual_parts = _find_part_names(the_score)
        self.assertEqual(expected_title, actual_title)
        self.assertSequenceEqual(expected_parts, actual_parts)

    def test_piece_range(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv2.xml')
        score = music21.converter.parse(path)
        expected_range = ('A2', 'E5')
        actual_range = _find_piece_range(score)
        self.assertEqual(expected_range, actual_range)

    def test_part_ranges(self):
        path = os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv2.xml')
        score = music21.converter.parse(path)
        expected_range = [('E4', 'E5'), ('E3', 'B4'), ('F#3', 'A4'), ('A2', 'C4')]
        actual_range = _find_part_ranges(score)
        self.assertEqual(expected_range, actual_range)

class TestIndexedPieceC(TestCase):

    def test_meta(self):
        meta = os.path.join(VIS_PATH, 'tests', 'corpus', 'meta')
        piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
        ind = IndexedPiece(piece, metafile=meta)
        self.assertEqual('Sacred', ind.metadata('religiosity'))

    def test_run(self):
        piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
        ind = IndexedPiece(piece).run()
        self.assertTrue(isinstance(ind, IndexedPiece))

    def test_json(self):
        meta = 'http://database.elvisproject.ca/piece/1971/?format=json'
        username = 'mborsodi'
        password = 'lalalalala'
        piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
        ind = IndexedPiece(piece, metafile=meta, username=username, password=password)
        self.assertEqual('Missa Fortuna desperata', ind.metadata('title'))

    def test_json2(self):
        meta = 'http://database.elvisproject.ca/piece/1971/'
        username = 'mborsodi'
        password = 'lalalalala'
        piece = os.path.join(VIS_PATH, 'tests', 'corpus', 'Missa-Fortuna-desperata_Kyrie_Josquin-Des-Prez_file6.xml')
        ind = IndexedPiece(piece, metafile=meta, username=username, password=password)
        self.assertEqual('Missa Fortuna desperata', ind.metadata('title'))

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
INDEXED_PIECE_SUITE_B = TestLoader().loadTestsFromTestCase(TestIndexedPieceB)
INDEXED_PIECE_PARTS_TITLES = TestLoader().loadTestsFromTestCase(TestPartsAndTitles)
INDEXED_PIECE_SUITE_C = TestLoader().loadTestsFromTestCase(TestIndexedPieceC)
