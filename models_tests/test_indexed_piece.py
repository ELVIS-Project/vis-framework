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

import unittest
from music21 import converter, stream, clef, bar
from models.indexed_piece import IndexedPiece


class TestIndexedPieceNormal(unittest.TestCase):
    def setUp(self):
        self.bwv77_soprano = [
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
            (71.0, "B4")
            ]
        self.bwv77_bass = [
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
            (71.0, "B2")
            ]

    def test_indexed_piece_200(self):
        # Soprano and Bass parts of bwv77.mxl
        expected_0 = self.bwv77_soprano
        expected_3 = self.bwv77_bass
        ip = IndexedPiece('test_corpus/bwv77.mxl')
        ip.add_index([u'NoteRestIndexer'])
        actual_0 = ip._data[u'NoteRestIndexer']['{}'][0]
        actual_3 = ip._data[u'NoteRestIndexer']['{}'][3]
        self.assertEqual(len(expected_0), len(actual_0))
        self.assertEqual(len(expected_3), len(actual_3))


class TestIndexedPieceErrors(unittest.TestCase):
    pass


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
indexed_piece_suite = unittest.TestLoader().loadTestsFromTestCase(TestIndexedPieceNormal)
indexed_piece_errors_suite = unittest.TestLoader().loadTestsFromTestCase(TestIndexedPieceErrors)
