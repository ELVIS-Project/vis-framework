#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_note_rest_indexer.py
# Purpose:                Tests for the NoteRestIndexer
#
# Copyright (C) 2013, 2014, 2016 Christopher Antila, Alexander Morgan
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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904

import os
import unittest
import pandas
from music21 import note, chord, stream, clef, bar
from vis.analyzers.indexers import noterest
from vis.models.indexed_piece import Importer, IndexedPiece, _find_part_names

# find the pathname of the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]

class TestNoteRestIndexer(unittest.TestCase):
    bwv77_soprano = [(0.0, "E4"), (0.5, "F#4"), (1.0, "G4"), (2.0, "A4"), (3.0, "B4"), (4.0, "A4"),
                     (5.0, "D5"), (6.0, "C#5"), (7.0, "B4"), (8.0, "A4"), (9.0, "D5"), (10.0, "C#5"),
                     (11.0, "B4"), (12.0, "A4"), (13.0, "G4"), (14.0, "F#4"), (15.0, "E4"),
                     (16.0, "E4"), (16.5, "F#4"), (17.0, "G4"), (18.0, "A4"), (19.0, "B4"),
                     (20.0, "A4"), (21.0, "D5"), (22.0, "C#5"), (23.0, "B4"), (24.0, "A4"),
                     (25.0, "D5"), (26.0, "C#5"), (27.0, "B4"), (28.0, "A4"), (29.0, "G4"),
                     (30.0, "F#4"), (31.0, "E4"), (32.0, "E4"), (33.0, "A4"), (34.0, "A4"),
                     (34.5, "G4"), (35.0, "F#4"), (36.0, "B4"), (37.0, "B4"), (38.0, "A#4"),
                     (39.0, "B4"), (40.0, "B4"), (41.0, "E5"), (42.0, "E5"), (43.0, "F#5"),
                     (43.5, "E5"), (44.0, "D5"), (45.0, "E5"), (45.5, "D5"), (46.0, "C#5"),
                     (47.0, "B4"), (48.0, "C#5"), (49.0, "D5"), (50.0, "C#5"), (51.0, "B4"),
                     (52.0, "A4"), (53.0, "B4"), (53.5, "A4"), (54.0, "G4"), (55.0, "F#4"),
                     (56.0, "E4"), (56.5, "F#4"), (57.0, "G4"), (58.0, "A4"), (59.0, "B4"),
                     (60.0, "A4"), (60.5, "G4"), (61.0, "A4"), (61.5, "G4"), (62.0, "F#4"),
                     (63.0, "E4"), (64.0, "E5"), (65.0, "E5"), (66.0, "E5"), (67.0, "F#5"),
                     (68.0, "E5"), (69.0, "D5"), (70.0, "C#5"), (71.0, "B4")]
    bwv77_bass = [(0.0, "E3"), (1.0, "E3"), (2.0, "D3"), (3.0, "G3"), (4.0, "D3"), (4.5, "C#3"),
                  (5.0, "B2"), (5.5, "G3"), (6.0, "E3"), (6.5, "F#3"), (7.0, "B3"), (8.0, "F#3"),
                  (9.0, "B3"), (10.0, "A3"), (11.0, "G3"), (12.0, "F#3"), (13.0, "E3"),
                  (14.0, "B2"), (15.0, "E3"), (16.0, "E3"), (17.0, "E3"), (18.0, "D3"),
                  (19.0, "G3"), (20.0, "D3"), (20.5, "C#3"), (21.0, "B2"), (21.5, "G3"),
                  (22.0, "E3"), (22.5, "F#3"), (23.0, "B3"), (24.0, "F#3"), (25.0, "B3"),
                  (26.0, "A3"), (27.0, "G3"), (28.0, "F#3"), (29.0, "E3"), (30.0, "B2"),
                  (31.0, "E3"), (32.0, "E3"), (32.5, "D3"), (33.0, "C#3"), (33.5, "B2"),
                  (34.0, "C#3"), (34.5, "A2"), (35.0, "D3"), (36.0, "G3"), (36.5, "F#3"),
                  (37.0, "E3"), (38.0, "F#3"), (39.0, "B2"), (40.0, "E3"), (40.5, "F#3"),
                  (41.0, "G3"), (42.0, "A3"), (43.0, "D3"), (44.0, "G3"), (44.5, "F#3"),
                  (45.0, "E3"), (46.0, "F#3"), (47.0, "B2"), (48.0, "F#3"), (49.0, "B3"),
                  (50.0, "E3"), (50.5, "F#3"), (51.0, "G3"), (52.0, "F#3"), (52.5, "E3"),
                  (53.0, "D#3"), (54.0, "E3"), (55.0, "B2"), (56.0, "E3"), (56.5, "D3"),
                  (57.0, "C3"), (57.5, "B2"), (58.0, "A2"), (59.0, "G2"), (60.0, "A2"),
                  (60.5, "B2"), (61.0, "C3"), (61.5, "A2"), (62.0, "B2"), (63.0, "E3"),
                  (64.0, "E3"), (65.0, "A3"), (65.5, "G3"), (66.0, "F#3"), (66.5, "E3"),
                  (67.0, "D3"), (68.0, "E3"), (68.5, "F#3"), (69.0, "G3"), (69.5, "E3"),
                  (70.0, "F#3"), (71.0, "B2")]

    @staticmethod
    def make_series(lotuples):
        """
        From a list of two-tuples, make a Series. The list should be like this:

        [(desired_index, value), (desired_index, value), (desired_index, value)]
        """
        new_index = [x[0] for x in lotuples]
        vals = [x[1] for x in lotuples]
        return pandas.Series(vals, index=new_index)

    def test_noterest_ind_func_1(self):
        # Check the indexer_func on note, rest, and chord objects
        expected = pandas.Series(('A-4', 'Rest', 'F#5'))
        n1 = note.Note('A-4')
        n2 = note.Note('D#5')
        n3 = note.Note('F#5')
        r1 = note.Rest()
        c1 = chord.Chord([n3, n2, n1])
        temp = pandas.Series((n1, r1, c1))
        actual = temp.apply(noterest.noterest_ind_func)
        self.assertTrue(actual.equals(expected))

    def test_noterest_indexer_1(self):
        # When the parts are empty
        expected = pandas.DataFrame({'0': pandas.Series(), '1': pandas.Series()})
        nr_indexer = noterest.NoteRestIndexer(expected)
        actual = nr_indexer.run()['noterest.NoteRestIndexer']
        self.assertTrue(actual.equals(expected))

    def test_note_rest_indexer_2(self):
        # When the part has no Note or Rest objects in it. Really this is a test for the methods between
        # _get_part_streams() and _get_noterest().
        expected = pandas.DataFrame({'Part 1': pandas.Series()})
        test_part = stream.Part()
        # add stuff to the test_part
        for i in range(1000):
            add_me = clef.BassClef()
            add_me.offset = i
            test_part.append(add_me)
            add_me = bar.Barline()
            add_me.offset = i
            test_part.append(add_me)
        ip = IndexedPiece()
        ip._analyses['part_streams'] = [test_part]
        ip.metadata('parts', _find_part_names(ip._analyses['part_streams']))
        actual = ip.get_data('noterest')['noterest.NoteRestIndexer']
        self.assertTrue(actual.equals(expected))

    def test_noterest_indexer_3(self):
        # When there are a bunch of notes
        expected = pandas.DataFrame({'0': pandas.Series([u'C4' for _ in range(10)])})
        test_score = pandas.DataFrame({'0': pandas.Series([note.Note('C4') for i in range(10)])})
        nr_indexer = noterest.NoteRestIndexer(test_score)
        actual = nr_indexer.run()['noterest.NoteRestIndexer']
        self.assertTrue(actual.equals(expected))

    def test_noterest_indexer_4(self):
        # Combine three previous tests to avoid re-importing the same piece multiple times.
        # Soprano part of bwv77.mxl
        expected = TestNoteRestIndexer.make_series(TestNoteRestIndexer.bwv77_soprano)
        expected.name = 'Soprano'
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus/bwv77.mxl'))
        actual = ip._get_noterest()['noterest.NoteRestIndexer'].iloc[:, 0].dropna()
        self.assertTrue(actual.equals(expected))
        
        # Reset analysis dictionary and make the score just the bass part and do the same test.
        expected = TestNoteRestIndexer.make_series(TestNoteRestIndexer.bwv77_bass)
        expected.name = 'Bass'
        actual = ip._get_noterest()['noterest.NoteRestIndexer'].iloc[:, 3].dropna()
        self.assertTrue(actual.equals(expected))


class TestMultiStopIndexer(unittest.TestCase):

    def test_unpack_chords_1(self):
        # Make sure that unpack_chords expands chords the right way.
        expected = pandas.concat((pandas.Series(('A-4', 'Rest', 'A-4')),
                                 pandas.Series((None, None, 'D#5')),
                                 pandas.Series((None, None, 'F#5'))), axis=1)
        temp = pandas.concat((pandas.Series((('A-4',), ('Rest',), ['A-4', 'D#5', 'F#5'])),), axis=1)
        actual = noterest.unpack_chords(temp)
        self.assertTrue(actual.equals(expected))

    def test_multistop_ind_func_1(self):
        # Check the indexer_func on note, rest, and chord objects
        expected = pandas.Series((('A-4',), ('Rest',), ['F#5', 'D#5', 'A-4']))
        n1 = note.Note('A-4')
        n2 = note.Note('D#5')
        n3 = note.Note('F#5')
        r1 = note.Rest()
        c1 = chord.Chord([n3, n2, n1])
        temp = pandas.Series((n1, r1, c1))
        actual = temp.apply(noterest.multistop_ind_func)
        self.assertTrue(actual.equals(expected))

    def test_multistop_indexer_1(self):
        # When the parts are empty
        expected = pandas.DataFrame({'0': pandas.Series(), '1': pandas.Series()})
        mu_indexer = noterest.MultiStopIndexer(expected)
        actual = mu_indexer.run()['noterest.MultiStopIndexer']
        self.assertTrue(actual.equals(expected))

    def test_multistop_indexer_2(self):
        # Integration test of a whole piece, the string quarted in the test corpus.
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus', 'sqOp76-4-i.midi'))
        actual = ip._get_multistop()
        # Until we figure out why pickling isn't working:
        self.assertTrue(10 == len(actual.columns))
        self.assertTrue(3286 == len(actual.index))
        self.assertSequenceEqual([val for val in actual.count().values],
                                 [2098, 41, 4, 1818, 131, 1, 1621, 15, 1232, 2])
        # When we get pickling working again (just save to_pickle once):
        # actual.to_pickle(os.path.join(VIS_PATH, 'tests', 'corpus', 'expecteds', 'test_multistop.pickle'))
        # expected = pandas.read_pickle(os.path.join(VIS_PATH, 'tests', 'corpus', 'expecteds', 'test_multistop.pickle'))
        # self.assertTrue(actual.equals(expected))

    def test_multistop_indexer_3(self):
        # Integration test on a piece with multiple voices in each part
        ip = Importer(os.path.join(VIS_PATH, 'tests', 'corpus', 'prelude28-20.mid'))
        actual = ip.get_data('multistop')
        self.assertTrue(8 == len(actual.columns))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
NOTE_REST_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestNoteRestIndexer)
MULTI_STOP_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMultiStopIndexer)
