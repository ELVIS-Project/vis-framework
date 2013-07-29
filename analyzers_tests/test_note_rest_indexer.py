#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import mock
import pandas
from music21 import converter, stream, clef, bar, note
from vis.analyzers import indexer
from vis.analyzers.indexers import noterest
from vis.controllers import mpcontroller


class TestNoteRestIndexer(unittest.TestCase):
    bwv77_soprano = [
        (0.0, "E4"),
        (0.5, "F#4"),
        (1.0, "G4"),
        (2.0, "A4"),
        (3.0, "B4"),
        (4.0, "A4"),
        (5.0, "D5"),
        (6.0, "C#5"),
        (7.0, "B4"),
        (8.0, "A4"),
        (9.0, "D5"),
        (10.0, "C#5"),
        (11.0, "B4"),
        (12.0, "A4"),
        (13.0, "G4"),
        (14.0, "F#4"),
        (15.0, "E4"),
        (16.0, "E4"),
        (16.5, "F#4"),
        (17.0, "G4"),
        (18.0, "A4"),
        (19.0, "B4"),
        (20.0, "A4"),
        (21.0, "D5"),
        (22.0, "C#5"),
        (23.0, "B4"),
        (24.0, "A4"),
        (25.0, "D5"),
        (26.0, "C#5"),
        (27.0, "B4"),
        (28.0, "A4"),
        (29.0, "G4"),
        (30.0, "F#4"),
        (31.0, "E4"),
        (32.0, "E4"),
        (33.0, "A4"),
        (34.0, "A4"),
        (34.5, "G4"),
        (35.0, "F#4"),
        (36.0, "B4"),
        (37.0, "B4"),
        (38.0, "A#4"),
        (39.0, "B4"),
        (40.0, "B4"),
        (41.0, "E5"),
        (42.0, "E5"),
        (43.0, "F#5"),
        (43.5, "E5"),
        (44.0, "D5"),
        (45.0, "E5"),
        (45.5, "D5"),
        (46.0, "C#5"),
        (47.0, "B4"),
        (48.0, "C#5"),
        (49.0, "D5"),
        (50.0, "C#5"),
        (51.0, "B4"),
        (52.0, "A4"),
        (53.0, "B4"),
        (53.5, "A4"),
        (54.0, "G4"),
        (55.0, "F#4"),
        (56.0, "E4"),
        (56.5, "F#4"),
        (57.0, "G4"),
        (58.0, "A4"),
        (59.0, "B4"),
        (60.0, "A4"),
        (60.5, "G4"),
        (61.0, "A4"),
        (61.5, "G4"),
        (62.0, "F#4"),
        (63.0, "E4"),
        (64.0, "E5"),
        (65.0, "E5"),
        (66.0, "E5"),
        (67.0, "F#5"),
        (68.0, "E5"),
        (69.0, "D5"),
        (70.0, "C#5"),
        (71.0, "B4")]
    bwv77_bass = [
        (0.0, "E3"),
        (1.0, "E3"),
        (2.0, "D3"),
        (3.0, "G3"),
        (4.0, "D3"),
        (4.5, "C#3"),
        (5.0, "B2"),
        (5.5, "G3"),
        (6.0, "E3"),
        (6.5, "F#3"),
        (7.0, "B3"),
        (8.0, "F#3"),
        (9.0, "B3"),
        (10.0, "A3"),
        (11.0, "G3"),
        (12.0, "F#3"),
        (13.0, "E3"),
        (14.0, "B2"),
        (15.0, "E3"),
        (16.0, "E3"),
        (17.0, "E3"),
        (18.0, "D3"),
        (19.0, "G3"),
        (20.0, "D3"),
        (20.5, "C#3"),
        (21.0, "B2"),
        (21.5, "G3"),
        (22.0, "E3"),
        (22.5, "F#3"),
        (23.0, "B3"),
        (24.0, "F#3"),
        (25.0, "B3"),
        (26.0, "A3"),
        (27.0, "G3"),
        (28.0, "F#3"),
        (29.0, "E3"),
        (30.0, "B2"),
        (31.0, "E3"),
        (32.0, "E3"),
        (32.5, "D3"),
        (33.0, "C#3"),
        (33.5, "B2"),
        (34.0, "C#3"),
        (34.5, "A2"),
        (35.0, "D3"),
        (36.0, "G3"),
        (36.5, "F#3"),
        (37.0, "E3"),
        (38.0, "F#3"),
        (39.0, "B2"),
        (40.0, "E3"),
        (40.5, "F#3"),
        (41.0, "G3"),
        (42.0, "A3"),
        (43.0, "D3"),
        (44.0, "G3"),
        (44.5, "F#3"),
        (45.0, "E3"),
        (46.0, "F#3"),
        (47.0, "B2"),
        (48.0, "F#3"),
        (49.0, "B3"),
        (50.0, "E3"),
        (50.5, "F#3"),
        (51.0, "G3"),
        (52.0, "F#3"),
        (52.5, "E3"),
        (53.0, "D#3"),
        (54.0, "E3"),
        (55.0, "B2"),
        (56.0, "E3"),
        (56.5, "D3"),
        (57.0, "C3"),
        (57.5, "B2"),
        (58.0, "A2"),
        (59.0, "G2"),
        (60.0, "A2"),
        (60.5, "B2"),
        (61.0, "C3"),
        (61.5, "A2"),
        (62.0, "B2"),
        (63.0, "E3"),
        (64.0, "E3"),
        (65.0, "A3"),
        (65.5, "G3"),
        (66.0, "F#3"),
        (66.5, "E3"),
        (67.0, "D3"),
        (68.0, "E3"),
        (68.5, "F#3"),
        (69.0, "G3"),
        (69.5, "E3"),
        (70.0, "F#3"),
        (71.0, "B2")]

    def test_note_rest_indexer_1(self):
        # The construcor must receive a Score
        test_part = [pandas.Series(['a', 'b', 'c']), pandas.Series([1, 2, 3])]
        self.assertRaises(RuntimeError, noterest.NoteRestIndexer, test_part)

    def test_note_rest_indexer_2(self):
        # The construcor must receive a Score
        test_part = [pandas.Series(['a', 'b', 'c']), pandas.Series([1, 2, 3])]
        self.assertRaises(RuntimeError, noterest.NoteRestIndexer, test_part)

    def test_note_rest_indexer_3(self):
        # Must be only one type in the list
        test_part = [stream.Part(), pandas.Series([1, 2, 3])]
        self.assertRaises(RuntimeError, noterest.NoteRestIndexer, test_part)

    def test_note_rest_indexer_4(self):
        # Must be only one type in the list
        test_part = [stream.Part(), pandas.Series([1, 2, 3]), stream.Part()]
        self.assertRaises(RuntimeError, noterest.NoteRestIndexer, test_part)

    def test_note_rest_indexer_5(self):
        # Should be fine
        expected = [[], []]
        test_part = [stream.Part(), stream.Part()]
        nr_indexer = noterest.NoteRestIndexer(test_part)
        actual = nr_indexer.run()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))
        self.assertEqual(len(expected[1]), len(actual[1]))

    def test_note_rest_indexer_10(self):
        # When the Part has nothing in it
        expected = [[]]
        test_part = [stream.Part()]
        nr_indexer = noterest.NoteRestIndexer(test_part)
        actual = nr_indexer.run()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))

    def test_note_rest_indexer_11(self):
        # When the part has no Note or Rest objects in it
        expected = [[]]
        test_part = stream.Part()
        # add stuff to the test_part
        for i in xrange(1000):
            add_me = clef.BassClef()
            add_me.offset = i
            test_part.append(add_me)
            add_me = bar.Barline()
            add_me.offset = i
            test_part.append(add_me)
        test_part = [test_part]
        # finished adding stuff to the test_part
        nr_indexer = noterest.NoteRestIndexer(test_part)
        actual = nr_indexer.run()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))

    def test_note_rest_indexer_12(self):
        # When there are a bunch of notes
        expected = [[(0.0, u'C4'), (1.0, u'C4'), (2.0, u'C4'), (3.0, u'C4'), (4.0, u'C4'),
                     (5.0, u'C4'), (6.0, u'C4'), (7.0, u'C4'), (8.0, u'C4'), (9.0, u'C4')]]
        test_part = stream.Part()
        # add stuff to the test_part
        for i in xrange(10):
            add_me = note.Note(u'C4', quarterLength=1.0)
            add_me.offset = i
            test_part.append(add_me)
        test_part = [test_part]
        # finished adding stuff to the test_part
        nr_indexer = noterest.NoteRestIndexer(test_part)
        actual = nr_indexer.run()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))
        for i in xrange(len(expected[0])):
            self.assertEqual(expected[0][i][0], actual[0][i].offset)
            self.assertEqual(expected[0][i][1], actual[0][i].obj)

    def test_note_rest_indexer_12_mpc(self):
        # When there are a bunch of notes
        # ... but with a real MPController
        expected = [[(0.0, u'C4'), (1.0, u'C4'), (2.0, u'C4'), (3.0, u'C4'), (4.0, u'C4'),
                     (5.0, u'C4'), (6.0, u'C4'), (7.0, u'C4'), (8.0, u'C4'), (9.0, u'C4')]]
        test_part = stream.Part()
        # add stuff to the test_part
        for i in xrange(10):
            add_me = note.Note(u'C4', quarterLength=1.0)
            add_me.offset = i
            test_part.append(add_me)
        test_part = [test_part]
        # finished adding stuff to the test_part
        mpc = mpcontroller.MPController()
        mpc.start()
        nr_indexer = noterest.NoteRestIndexer(test_part, {}, mpc)
        actual = nr_indexer.run()
        del nr_indexer
        mpc.shutdown()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))
        for i in xrange(len(expected[0])):
            self.assertEqual(expected[0][i][0], actual[0][i].offset)
            self.assertEqual(expected[0][i][1], actual[0][i].obj)

    def test_note_rest_indexer_200(self):
        # Soprano part of bwv77.mxl
        expected = [self.bwv77_soprano]
        test_part = [converter.parse('test_corpus/bwv77.mxl').parts[0]]
        nr_indexer = noterest.NoteRestIndexer(test_part)
        actual = nr_indexer.run()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))
        for i in xrange(len(expected[0])):
            self.assertEqual(expected[0][i][0], actual[0][i].offset)
            self.assertEqual(expected[0][i][1], actual[0][i].obj)

    def test_note_rest_indexer_201(self):
        # Bass part of bwv77.mxl
        expected = [self.bwv77_bass]
        test_part = [converter.parse('test_corpus/bwv77.mxl').parts[3]]
        nr_indexer = noterest.NoteRestIndexer(test_part)
        actual = nr_indexer.run()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))
        for i in xrange(len(expected[0])):
            self.assertEqual(expected[0][i][0], actual[0][i].offset)
            self.assertEqual(expected[0][i][1], actual[0][i].obj)

    def test_note_rest_indexer_202(self):
        # Soprano and Bass parts of bwv77.mxl
        expected = [self.bwv77_soprano, self.bwv77_bass]
        bwv77 = converter.parse('test_corpus/bwv77.mxl')
        test_part = [bwv77.parts[0], bwv77.parts[3]]
        nr_indexer = noterest.NoteRestIndexer(test_part)
        actual = nr_indexer.run()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))
        self.assertEqual(len(expected[1]), len(actual[1]))
        for i in xrange(len(expected[0])):
            self.assertEqual(expected[0][i][0], actual[0][i].offset)
            self.assertEqual(expected[0][i][1], actual[0][i].obj)
        for i in xrange(len(expected[1])):
            self.assertEqual(expected[1][i][0], actual[1][i].offset)
            self.assertEqual(expected[1][i][1], actual[1][i].obj)

    def test_note_rest_indexer_201_mpc(self):
        # Bass part of bwv77.mxl
        # with MPController
        expected = [self.bwv77_bass]
        test_part = [converter.parse('test_corpus/bwv77.mxl').parts[3]]
        mpc = mpcontroller.MPController()
        mpc.start()
        nr_indexer = noterest.NoteRestIndexer(test_part, {}, mpc)
        actual = nr_indexer.run()
        del nr_indexer
        mpc.shutdown()
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(len(expected[0]), len(actual[0]))
        for i in xrange(len(expected[0])):
            self.assertEqual(expected[0][i][0], actual[0][i].offset)
            self.assertEqual(expected[0][i][1], actual[0][i].obj)

    def test_note_rest_indexer_200_mock_mpc(self):
        # Soprano part of bwv77.mxl
        # ** with mock MPController
        bwv77 = converter.parse('test_corpus/bwv77.mxl')
        test_part = [bwv77.parts[0]]
        # prepare mocks
        mpc = mock.MagicMock(spec=mpcontroller.MPController)
        mock_conn = mock.MagicMock()
        mpc.get_pipe.return_value = mock_conn
        mock_conn.recv.return_value = u'returned by mock pipe'
        # run
        nr_indexer = noterest.NoteRestIndexer(test_part, {}, mpc)
        nr_indexer.run()
        # test mocks were used correctly
        mpc.get_pipe.assert_called_once_with()
        ccallz = mock_conn.mock_calls[0][1][0]  # take the arguments given to "send"
        self.assertEqual(ccallz[0], indexer.mp_indexer)
        self.assertTrue(isinstance(ccallz[1][0][0], basestring))
        self.assertEqual(ccallz[1][1], noterest.indexer_func)
        self.assertEqual(ccallz[1][2], [note.Note, note.Rest])
        mock_conn.recv.assert_called_once_with()

    def test_note_rest_indexer_202_mock_mpc(self):
        # Soprano and Bass parts of bwv77.mxl
        # ** with mock MPController
        bwv77 = converter.parse('test_corpus/bwv77.mxl')
        test_part = [bwv77.parts[0], bwv77.parts[3]]
        # prepare mocks
        mpc = mock.MagicMock(spec=mpcontroller.MPController)
        mock_conn = mock.MagicMock()
        mpc.get_pipe.return_value = mock_conn
        mock_conn.recv.return_value = u'returned by mock pipe'
        # run
        nr_indexer = noterest.NoteRestIndexer(test_part, {}, mpc)
        nr_indexer.run()
        # test mocks were used correctly
        mpc.get_pipe.assert_called_once_with()
        ccallz = mock_conn.mock_calls
        self.assertEqual(4, len(ccallz))
        send_call = ((indexer.mp_indexer,
                      [[test_part[0]], noterest.indexer_func, [note.Note, note.Rest]]),)
        self.assertEqual(ccallz[0][0], u'send')
        send_1 = mock_conn.mock_calls[0][1][0]  # take the arguments given to "send" (first call)
        self.assertEqual(send_1[0], indexer.mp_indexer)
        self.assertTrue(isinstance(send_1[1][0][0], basestring))
        self.assertEqual(send_1[1][1], noterest.indexer_func)
        self.assertEqual(send_1[1][2], [note.Note, note.Rest])
        self.assertEqual(ccallz[1][0], u'send')
        send_2 = mock_conn.mock_calls[0][1][0]  # take the arguments given to "send" (second call)
        self.assertEqual(send_2[0], indexer.mp_indexer)
        self.assertTrue(isinstance(send_2[1][0][0], basestring))
        self.assertEqual(send_2[1][1], noterest.indexer_func)
        self.assertEqual(send_2[1][2], [note.Note, note.Rest])
        # two recv() calls
        self.assertEqual(ccallz[2][0], u'recv')
        self.assertEqual(ccallz[3][0], u'recv')


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
note_rest_indexer_suite = unittest.TestLoader().loadTestsFromTestCase(TestNoteRestIndexer)
