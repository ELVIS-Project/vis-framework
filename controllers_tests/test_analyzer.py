#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         TestSorting.py
# Purpose:      Unit tests for the NGram class.
#
# Copyright (C) 2012 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------



# Imports from...
# python
import unittest
# music21
from music21 import note, converter
# vis
from test_corpus import event_finder_short
from models import analyzing
from controllers.analyzer import _event_finder



class TestRunAnalysis(unittest.TestCase):
   # Test run_analysis()
   pass
# End TestRunAnalysis ----------------------------------------------------------



class TestEventFinderShort(unittest.TestCase):
   # Test _event_finder() with short excerpts
   # NB: all of these have two parts



   def setUp(self):
      self.setts = analyzing.AnalysisSettings()
      self.setts.types =  [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]
      self.setts.salami =  False
      self.setts.offset =  0.5



   def test_event_finder_short_1(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_1
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_2(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_2
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_3(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_3
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_4(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_4
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_5(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'F4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_5
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_6(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_6
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_7(self):
      expected = [(0.0, ('B3', 'A4')), (0.5, ('G3', 'G4')),
                  (1.0, ('A3', 'G4')), (1.5, ('B3', 'F4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_7
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_8(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_8
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_9(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4')),
                  (1.0, ('B3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_9
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_10(self):
      # NOTE: the thing reported at 0.25 is for the 0.5 offset
      expected = [(0.0, ('G3', 'G4')), (0.25, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_10
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_11(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_11
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_12(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_12
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_13(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_13
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_14(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_14
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_15(self):
      expected = [(0.0, ('G3', 'G4')), (1.0, ('Rest', 'G4')), (1.5, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_15
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_16(self):
      # NOTE: the thing at 0.75 is for the 1.0 offset
      expected = [(0.0, ('G3', 'G4')), (0.5, ('Rest', 'A4')),
                  (0.75, ('F3', 'A4')), (1.5, ('E3', 'B4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_16
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_17(self):
      # NOTE: the thing at 0.75 is for the 1.0 offset
      # NOTE: the thing at 1.375 is for the 1.5 offset
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'A4')),
                  (0.75, ('F3', 'A4')), (1.375, ('G3', 'F4')),
                  (2.0, ('G3', 'E4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_17
      actual = _event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)
# End TestEventFinderShort -----------------------------------------------------



class TestEventFinderMonteverdi(unittest.TestCase):
   # Test _event_finder() with long excerpts

   def test_madrigal_1(self):
      # tests madrigal51.mxl (cruda amarilli) offset = 0.5, we're salami slicing
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.types =  [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]
      setts.salami =  True
      setts.offset =  0.5
      actual_result = _event_finder(parts=[madrigal.parts[0],
                                           madrigal.parts[1]],
                                    settings=setts,
                                    record=actual_result)
      expected_result = [(0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        # m. 2
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (0.0, (u'B4', u'D5')),
                        (6.0, (u'A4', u'C5')),
                        (6.0, (u'A4', u'C5')),
                        (7.0, (u'G4', u'B4')),
                        (7.0, (u'G4', u'B4')),
                        # m. 3
                        (8.0, (u'F#4', u'A4')),
                        (8.0, (u'F#4', u'A4')),
                        (8.0, (u'F#4', u'A4')),
                        (8.0, (u'F#4', u'A4')),
                        (8.0, (u'F#4', u'A4')),
                        (8.0, (u'F#4', u'A4')),
                        (8.0, (u'F#4', u'A4')),
                        (8.0, (u'F#4', u'A4')),
                        # m. 4
                        (12.0, (u'G4', u'B4')),
                        (12.0, (u'G4', u'B4')),
                        (12.0, (u'G4', u'B4')),
                        (12.0, (u'G4', u'B4')),
                        (14.0, (u'G4', u'G5')),
                        (14.0, (u'G4', u'G5')),
                        (14.0, (u'G4', u'G5')),
                        (14.0, (u'G4', u'G5')),
                        # m. 5
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        # m. 6
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (16.0, (u'E5', u'G5')),
                        (22.0, (u'D5', u'F5')),
                        (22.0, (u'D5', u'F5')),
                        (23.0, (u'C5', u'E5')),
                        (23.0, (u'C5', u'E5')),
                        # m. 7
                        (24.0, (u'B4', u'D5')),
                        (24.0, (u'B4', u'D5')),
                        (24.0, (u'B4', u'D5')),
                        (24.0, (u'B4', u'D5')),
                        (24.0, (u'B4', u'D5')),
                        (24.0, (u'B4', u'D5')),
                        (24.0, (u'B4', u'D5')),
                        (24.0, (u'B4', u'D5')),
                        # m. 8
                        (28.0, (u'C5', u'C5')),
                        (28.0, (u'C5', u'C5')),
                        (28.0, (u'C5', u'C5')),
                        (28.0, (u'C5', u'C5')),
                        (28.0, (u'C5', u'C5')),
                        (28.0, (u'C5', u'C5')),
                        (28.0, (u'C5', u'C5')),
                        (28.0, (u'C5', u'C5')),
                        # m. 9
                        (32.0, (u'G4', u'C5')),
                        (32.0, (u'G4', u'C5')),
                        (32.0, (u'G4', u'C5')),
                        (32.0, (u'G4', u'C5')),
                        (34.0, (u'A4', u'C5')),
                        (34.0, (u'A4', u'C5')),
                        (35.0, (u'B4', u'D5')),
                        (35.0, (u'B4', u'D5')),
                        # m. 10
                        (36.0, (u'C5', u'F5')),
                        (36.0, (u'C5', u'F5')),
                        (36.0, (u'C5', u'F5')),
                        (36.0, (u'C5', u'F5')),
                        (38.0, (u'C5', u'E5')),
                        (38.0, (u'C5', u'E5')),
                        (39.0, (u'C5', u'F#5')),
                        (39.0, (u'C5', u'F#5'))]
      self.assertEqual(expected_result,  actual_result._record[:80])



   def test_madrigal_2(self):
      # tests madrigal51.mxl (cruda amarilli) offset = 1.0, we're salami slicing
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.types =  [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]
      setts.salami =  True
      setts.offset =  1.0
      actual_result = _event_finder(parts=[madrigal.parts[0],
                                           madrigal.parts[1]],
                                    settings=setts,
                                    record=actual_result)
      expected_result = [(0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        # m. 2
                        (0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        (6.0, ('A4', 'C5')),
                        (7.0, ('G4', 'B4')),
                        # m. 3
                        (8.0, ('F#4', 'A4')),
                        (8.0, ('F#4', 'A4')),
                        (8.0, ('F#4', 'A4')),
                        (8.0, ('F#4', 'A4')),
                        # m. 4
                        (12.0, ('G4', 'B4')),
                        (12.0, ('G4', 'B4')),
                        (14.0, ('G4', 'G5')),
                        (14.0, ('G4', 'G5')),
                        # m. 5
                        (16.0, ('E5', 'G5')),
                        (16.0, ('E5', 'G5')),
                        (16.0, ('E5', 'G5')),
                        (16.0, ('E5', 'G5')),
                        # m. 6
                        (16.0, ('E5', 'G5')),
                        (16.0, ('E5', 'G5')),
                        (22.0, ('D5', 'F5')),
                        (23.0, ('C5', 'E5')),
                        # m. 7
                        (24.0, ('B4', 'D5')),
                        (24.0, ('B4', 'D5')),
                        (24.0, ('B4', 'D5')),
                        (24.0, ('B4', 'D5')),
                        # m. 8
                        (28.0, ('C5', 'C5')),
                        (28.0, ('C5', 'C5')),
                        (28.0, ('C5', 'C5')),
                        (28.0, ('C5', 'C5')),
                        # m. 9
                        (32.0, ('G4', 'C5')),
                        (32.0, ('G4', 'C5')),
                        (34.0, ('A4', 'C5')),
                        (35.0, ('B4', 'D5')),
                        # m. 10
                        (36.0, ('C5', 'F5')),
                        (36.0, ('C5', 'F5')),
                        (38.0, ('C5', 'E5')),
                        (39.0, ('C5', 'F#5'))]
      self.assertEqual(expected_result,  actual_result._record[:40])



   def test_madrigal_3(self):
      # tests madrigal51.mxl (cruda amarilli) offset = 2.0, we're salami slicing
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.types =  [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]
      setts.salami =  True
      setts.offset =  2.0
      actual_result = _event_finder(parts=[madrigal.parts[0],
                                           madrigal.parts[1]],
                                    settings=setts,
                                    record=actual_result)
      expected_result = [(0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        # m. 2
                        (0.0, ('B4', 'D5')),
                        (6.0, ('A4', 'C5')),
                        # m. 3
                        (8.0, ('F#4', 'A4')),
                        (8.0, ('F#4', 'A4')),
                        # m. 4
                        (12.0, ('G4', 'B4')),
                        (14.0, ('G4', 'G5')),
                        # m. 5
                        (16.0, ('E5', 'G5')),
                        (16.0, ('E5', 'G5')),
                        # m. 6
                        (16.0, ('E5', 'G5')),
                        (22.0, ('D5', 'F5')),
                        # m. 7
                        (24.0, ('B4', 'D5')),
                        (24.0, ('B4', 'D5')),
                        # m. 8
                        (28.0, ('C5', 'C5')),
                        (28.0, ('C5', 'C5')),
                        # m. 9
                        (32.0, ('G4', 'C5')),
                        (34.0, ('A4', 'C5')),
                        # m. 10
                        (36.0, ('C5', 'F5')),
                        (38.0, ('C5', 'E5'))]
      self.assertEqual(expected_result,  actual_result._record[:20])



   def test_madrigal_4(self):
      # tests madrigal51.mxl (cruda amarilli) offset = 0.5, we're NOT salami slicing
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.types =  [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]
      setts.salami =  False
      setts.offset =  0.5
      actual_result = _event_finder(parts=[madrigal.parts[0],
                                           madrigal.parts[1]],
                                    settings=setts,
                                    record=actual_result)
      expected_result = [(0.0, ('B4', 'D5')),
                                 # m. 2
                                 (6.0, ('A4', 'C5')),
                                 (7.0, ('G4', 'B4')),
                                 # m. 3
                                 (8.0, ('F#4', 'A4')),
                                 # m. 4
                                 (12.0, ('G4', 'B4')),
                                 (14.0, ('G4', 'G5')),
                                 # m. 5
                                 (16.0, ('E5', 'G5')),
                                 # m. 6
                                 (22.0, ('D5', 'F5')),
                                 (23.0, ('C5', 'E5')),
                                 # m. 7
                                 (24.0, ('B4', 'D5')),
                                 # m. 8
                                 (28.0, ('C5', 'C5')),
                                 # m. 9
                                 (32.0, ('G4', 'C5')),
                                 (34.0, ('A4', 'C5')),
                                 (35.0, ('B4', 'D5')),
                                 # m. 10
                                 (36.0, ('C5', 'F5')),
                                 (38.0, ('C5', 'E5')),
                                 (39.0, ('C5', 'F#5'))]
      self.assertEqual(expected_result,  actual_result._record[:17])



   def test_madrigal_5(self):
      # tests madrigal51.mxl (cruda amarilli) offset = 1.0, we're NOT salami slicing
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.types =  [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]
      setts.salami =  False
      setts.offset =  1.0
      actual_result = _event_finder(parts=[madrigal.parts[0],
                                           madrigal.parts[1]],
                                    settings=setts,
                                    record=actual_result)
      expected_result = [(0.0, ('B4', 'D5')),
                        # m. 2
                        (6.0, ('A4', 'C5')),
                        (7.0, ('G4', 'B4')),
                        # m. 3
                        (8.0, ('F#4', 'A4')),
                        # m. 4
                        (12.0, ('G4', 'B4')),
                        (14.0, ('G4', 'G5')),
                        # m. 5
                        (16.0, ('E5', 'G5')),
                        # m. 6
                        (22.0, ('D5', 'F5')),
                        (23.0, ('C5', 'E5')),
                        # m. 7
                        (24.0, ('B4', 'D5')),
                        # m. 8
                        (28.0, ('C5', 'C5')),
                        # m. 9
                        (32.0, ('G4', 'C5')),
                        (34.0, ('A4', 'C5')),
                        (35.0, ('B4', 'D5')),
                        # m. 10
                        (36.0, ('C5', 'F5')),
                        (38.0, ('C5', 'E5')),
                        (39.0, ('C5', 'F#5'))]
      self.assertEqual(expected_result,  actual_result._record[:17])



   def test_madrigal_6(self):
      # tests madrigal51.mxl (cruda amarilli) offset = 2.0, we're NOT salami slicing
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.types =  [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]
      setts.salami =  False
      setts.offset =  2.0
      actual_result = _event_finder(parts=[madrigal.parts[0],
                                           madrigal.parts[1]],
                                    settings=setts,
                                    record=actual_result)
      expected_result = [(0.0, ('B4', 'D5')),
                                 # m. 2
                                 (6.0, ('A4', 'C5')),
                                 # m. 3
                                 (8.0, ('F#4', 'A4')),
                                 # m. 4
                                 (12.0, ('G4', 'B4')),
                                 (14.0, ('G4', 'G5')),
                                 # m. 5
                                 (16.0, ('E5', 'G5')),
                                 # m. 6
                                 (22.0, ('D5', 'F5')),
                                 # m. 7
                                 (24.0, ('B4', 'D5')),
                                 # m. 8
                                 (28.0, ('C5', 'C5')),
                                 # m. 9
                                 (32.0, ('G4', 'C5')),
                                 (34.0, ('A4', 'C5')),
                                 # m. 10
                                 (36.0, ('C5', 'F5')),
                                 (38.0, ('C5', 'E5'))]
      self.assertEqual(expected_result,  actual_result._record[:13])
# End TestEventFinderMonteverdi --------------------------------------------------------------------



class TestEventFinderJosquin(unittest.TestCase):
   # Test _event_finder() with long excerpts:
   # Josquin's "Ave maris stella," all parts in measures 59 through 65

   def setUp(self):
      # set-up for tests of Jos2308.krn
      self.actual_result = analyzing.AnalysisRecord()
      self.piece = converter.parse('test_corpus/Jos2308.krn')
      self.parts_list = [self.piece.parts[0][67:74],
                         self.piece.parts[1][67:74],
                         self.piece.parts[2][67:74],
                         self.piece.parts[3][67:74]]
      self.setts = analyzing.AnalysisSettings()
      self.setts.types =  [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')]



   def test_josquin_1(self):
      # tests Jos2308.krn ("Ave maris stella") offset = 0.5, we're salami slicing
      self.setts.salami =  True
      self.setts.offset =  0.5
      self.actual_result = _event_finder(parts=self.parts_list,
                                         settings=self.setts,
                                         record=self.actual_result)
      expected_result = [(464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         # m. 60
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+11.0, ('D3', 'D4', 'G4', 'Rest')),
                         (464+11.0, ('D3', 'D4', 'G4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         # m. 61
                         (464+16.0, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+16.0, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+17.0, ('Rest', 'G3', 'A4', 'Rest')),
                         (464+17.0, ('Rest', 'G3', 'A4', 'Rest')),
                         (464+18.0, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+18.0, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+19.0, ('Rest', 'A3', 'F4', 'Rest')),
                         (464+19.0, ('Rest', 'A3', 'F4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         # m. 62
                         (464+24.0, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+24.0, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+25.0, ('Rest', 'A3', 'G4', 'Rest')),
                         (464+25.0, ('Rest', 'A3', 'G4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         # m. 63
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+39.0, ('A3', 'F3', 'Rest', 'B-4')),
                         (464+39.0, ('A3', 'F3', 'Rest', 'B-4')),
                         # m. 64
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         # m. 65
                         (464+48.0, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+48.0, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+49.0, ('B-3', 'Rest', 'Rest', 'D4')),
                         (464+49.0, ('B-3', 'Rest', 'Rest', 'D4')),
                         (464+50.0, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+50.0, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+51.0, ('G3', 'Rest', 'Rest', 'G4')),
                         (464+51.0, ('G3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_josquin_2(self):
      # tests Jos2308.krn ("Ave maris stella") offset = 1.0, we're salami slicing
      self.setts.salami =  True
      self.setts.offset =  1.0
      self.actual_result = _event_finder(parts=self.parts_list,
                                                           settings=self.setts,
                                                           record=self.actual_result)
      expected_result = [(464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         # m. 60
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+11.0, ('D3', 'D4', 'G4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         # m. 61
                         (464+16.0, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+17.0, ('Rest', 'G3', 'A4', 'Rest')),
                         (464+18.0, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+19.0, ('Rest', 'A3', 'F4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         # m. 62
                         (464+24.0, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+25.0, ('Rest', 'A3', 'G4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         # m. 63
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+39.0, ('A3', 'F3', 'Rest', 'B-4')),
                         # m. 64
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         # m. 65
                         (464+48.0, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+49.0, ('B-3', 'Rest', 'Rest', 'D4')),
                         (464+50.0, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+51.0, ('G3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_madrigal_3(self):
      # tests Jos2308.krn ("Ave maris stella") offset = 2.0, we're salami slicing
      self.setts.salami =  True
      self.setts.offset =  2.0
      self.actual_result = _event_finder(parts=self.parts_list,
                                                           settings=self.setts,
                                                           record=self.actual_result)
      expected_result = [(464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         # m. 60
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         # m. 61
                         (464+16.0, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+18.0, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         # m. 62
                         (464+24.0, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         # m. 63
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         # m. 64
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         # m. 65
                         (464+48.0, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+50.0, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_josquin_4(self):
      # tests Jos2308.krn ("Ave maris stella") offset = 0.5, we're NOT salami slicing
      self.setts.salami =  False
      self.setts.offset =  0.5
      self.actual_result = _event_finder(parts=self.parts_list,
                                                           settings=self.setts,
                                                           record=self.actual_result)
      expected_result = [(464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         # m. 60
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+11.0, ('D3', 'D4', 'G4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         # m. 61
                         (464+16.0, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+17.0, ('Rest', 'G3', 'A4', 'Rest')),
                         (464+18.0, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+19.0, ('Rest', 'A3', 'F4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         # m. 62
                         (464+24.0, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+25.0, ('Rest', 'A3', 'G4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         # m. 63
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+39.0, ('A3', 'F3', 'Rest', 'B-4')),
                         # m. 64
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         # m. 65
                         (464+48.0, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+49.0, ('B-3', 'Rest', 'Rest', 'D4')),
                         (464+50.0, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+51.0, ('G3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_josquin_5(self):
      # tests Jos2308.krn ("Ave maris stella") offset = 1.0, we're NOT salami slicing
      self.setts.salami =  False
      self.setts.offset =  1.0
      self.actual_result = _event_finder(parts=self.parts_list,
                                                           settings=self.setts,
                                                           record=self.actual_result)
      expected_result = [(464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         # m. 60
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+11.0, ('D3', 'D4', 'G4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         # m. 61
                         (464+16.0, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+17.0, ('Rest', 'G3', 'A4', 'Rest')),
                         (464+18.0, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+19.0, ('Rest', 'A3', 'F4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         # m. 62
                         (464+24.0, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+25.0, ('Rest', 'A3', 'G4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         # m. 63
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+39.0, ('A3', 'F3', 'Rest', 'B-4')),
                         # m. 64
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         # m. 65
                         (464+48.0, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+49.0, ('B-3', 'Rest', 'Rest', 'D4')),
                         (464+50.0, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+51.0, ('G3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_josquin_6(self):
      # tests Jos2308.krn ("Ave maris stella") offset = 2.0, we're NOT salami slicing
      self.setts.salami =  False
      self.setts.offset =  2.0
      self.actual_result = _event_finder(parts=self.parts_list,
                                         settings=self.setts,
                                         record=self.actual_result)
      expected_result = [(464.0, ('A3', 'A3', 'C5', 'Rest')),
                         (466.0, ('F3', 'A3', 'A4', 'Rest')),
                         (468.0, ('E3', 'C4', 'G4', 'Rest')),
                         # m. 60
                         (472.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         # m. 61
                         (464+16.0, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+18.0, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         # m. 62
                         (464+24.0, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         # m. 63
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         # m. 64
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         # m. 65
                         (464+48.0, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+50.0, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)
# End TestEventFinderJosquin -----------------------------------------------------------------------



class TestEventFinderBach(unittest.TestCase):
   # Test _event_finder() with long excerpts:
   # BWV 7.7, all parts in measures 1 through 7

   def setUp(self):
      # set-up for tests of bwv77.mxl
      self.actual_result = analyzing.AnalysisRecord()
      self.piece = converter.parse('test_corpus/bwv77.mxl')
      self.parts_list = [self.piece.parts[0][1:9],
                         self.piece.parts[1][1:9],
                         self.piece.parts[2][1:9],
                         self.piece.parts[3][1:9]]
      self.setts = analyzing.AnalysisSettings()
      self.setts.types = [(note.Note, lambda x: x.nameWithOctave),
                          (note.Rest, lambda x: 'Rest')]



   def test_bach_1(self):
      # tests bwv77.mxl offset = 0.5, we're salami slicing
      self.setts.salami =  True
      self.setts.offset =  0.5
      self.actual_result = _event_finder(
                              parts=self.parts_list,
                              settings=self.setts,
                              record=self.actual_result
                           )
      expected_result = [
                           # offset interval: 0.5
                           # repeat identical events
                           # pickup
                           (0.0, ('E3', 'G3', 'B3', 'E4')),
                           (0.5, ('E3', 'A3', 'B3', 'F#4')),
                           # m.1
                           (1.0, ('E3', 'B3', 'E4', 'G4')),
                           (1.0, ('E3', 'B3', 'E4', 'G4')),
                           (2.0, ('D3', 'D4', 'F#4', 'A4')),
                           (2.0, ('D3', 'D4', 'F#4', 'A4')),
                           (3.0, ('G3', 'D4', 'G4', 'B4')),
                           (3.0, ('G3', 'D4', 'G4', 'B4')),
                           (4.0, ('D3', 'D4', 'F#4', 'A4')),
                           (4.5, ('C#3', 'E4', 'F#4', 'A4')),
                           # m.2
                           (5.0, ('B2', 'F#4', 'B4', 'D5')),
                           (5.5, ('G3', 'D4', 'B4', 'D5')),
                           (6.0, ('E3', 'G4', 'B4', 'C#5')),
                           (6.5, ('F#3', 'F#4', 'A#4', 'C#5')),
                           (7.0, ('B3', 'D4', 'F#4', 'B4')),
                           (7.0, ('B3', 'D4', 'F#4', 'B4')),
                           (8.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           (8.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.3
                           (9.0, ('B3', 'B3', 'F#4', 'D5')),
                           (9.5, ('B3', 'B3', 'G4', 'D5')),
                           (10.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (10.5, ('A3', 'C#4', 'F#4', 'C#5')),
                           (11.0, ('G3', 'D#4', 'F#4', 'B4')),
                           (11.5, ('G3', 'E4', 'E4', 'B4')),
                           (12.0, ('F#3', 'F#4', 'E4', 'A4')),
                           (12.5, ('F#3', 'F#4', 'D#4', 'A4')),
                           # m.4
                           (13.0, ('E3', 'B3', 'E4', 'G4')),
                           (13.0, ('E3', 'B3', 'E4', 'G4')),
                           (14.0, ('B2', 'B3', 'D#4', 'F#4')),
                           (14.5, ('B2', 'A3', 'D#4', 'F#4')),
                           (15.0, ('E3', 'G3', 'B3', 'E4')),
                           (15.0, ('E3', 'G3', 'B3', 'E4')),
                           (15.0, ('E3', 'G3', 'B3', 'E4')),
                           (16.5, ('E3', 'A3', 'B3', 'F#4')),
                           # m.5
                           (17.0, ('E3', 'B3', 'E4', 'G4')),
                           (17.0, ('E3', 'B3', 'E4', 'G4')),
                           (18.0, ('D3', 'D4', 'F#4', 'A4')),
                           (18.0, ('D3', 'D4', 'F#4', 'A4')),
                           (19.0, ('G3', 'D4', 'G4', 'B4')),
                           (19.0, ('G3', 'D4', 'G4', 'B4')),
                           (20.0, ('D3', 'D4', 'F#4', 'A4')),
                           (20.5, ('C#3', 'E4', 'F#4', 'A4')),
                           # m.6
                           (21.0, ('B2', 'F#4', 'B4', 'D5')),
                           (21.5, ('G3', 'D4', 'B4', 'D5')),
                           (22.0, ('E3', 'G4', 'B4', 'C#5')),
                           (22.5, ('F#3', 'F#4', 'A#4', 'C#5')),
                           (23.0, ('B3', 'D4', 'F#4', 'B4')),
                           (23.0, ('B3', 'D4', 'F#4', 'B4')),
                           (24.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           (24.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.7
                           (25.0, ('B3', 'B3', 'F#4', 'D5')),
                           (25.5, ('B3', 'B3', 'G4', 'D5')),
                           (26.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (26.5, ('A3', 'C#4', 'F#4', 'C#5')),
                           (27.0, ('G3', 'D#4', 'F#4', 'B4')),
                           (27.5, ('G3', 'E4', 'E4', 'B4')),
                           (28.0, ('F#3', 'F#4', 'E4', 'A4')),
                           (28.5, ('F#3', 'F#4', 'D#4', 'A4'))
                        ]
      #print self.actual_result._record
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_bach_2(self):
      # tests bwv77.mxl offset = 0.5, we're NOT salami slicing
      self.setts.salami =  False
      self.setts.offset =  0.5
      self.actual_result = _event_finder(
                              parts=self.parts_list,
                              settings=self.setts,
                              record=self.actual_result
                           )
      expected_result = [
                           # offset interval: 0.5
                           # do not repeat identical events
                           # pickup
                           (0.0, ('E3', 'G3', 'B3', 'E4')),
                           (0.5, ('E3', 'A3', 'B3', 'F#4')),
                           # m.1
                           (1.0, ('E3', 'B3', 'E4', 'G4')),
                           (2.0, ('D3', 'D4', 'F#4', 'A4')),
                           (3.0, ('G3', 'D4', 'G4', 'B4')),
                           (4.0, ('D3', 'D4', 'F#4', 'A4')),
                           (4.5, ('C#3', 'E4', 'F#4', 'A4')),
                           # m.2
                           (5.0, ('B2', 'F#4', 'B4', 'D5')),
                           (5.5, ('G3', 'D4', 'B4', 'D5')),
                           (6.0, ('E3', 'G4', 'B4', 'C#5')),
                           (6.5, ('F#3', 'F#4', 'A#4', 'C#5')),
                           (7.0, ('B3', 'D4', 'F#4', 'B4')),
                           (8.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.3
                           (9.0, ('B3', 'B3', 'F#4', 'D5')),
                           (9.5, ('B3', 'B3', 'G4', 'D5')),
                           (10.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (10.5, ('A3', 'C#4', 'F#4', 'C#5')),
                           (11.0, ('G3', 'D#4', 'F#4', 'B4')),
                           (11.5, ('G3', 'E4', 'E4', 'B4')),
                           (12.0, ('F#3', 'F#4', 'E4', 'A4')),
                           (12.5, ('F#3', 'F#4', 'D#4', 'A4')),
                           # m.4
                           (13.0, ('E3', 'B3', 'E4', 'G4')),
                           (14.0, ('B2', 'B3', 'D#4', 'F#4')),
                           (14.5, ('B2', 'A3', 'D#4', 'F#4')),
                           (15.0, ('E3', 'G3', 'B3', 'E4')),
                           (16.5, ('E3', 'A3', 'B3', 'F#4')),
                           # m.5
                           (17.0, ('E3', 'B3', 'E4', 'G4')),
                           (18.0, ('D3', 'D4', 'F#4', 'A4')),
                           (19.0, ('G3', 'D4', 'G4', 'B4')),
                           (20.0, ('D3', 'D4', 'F#4', 'A4')),
                           (20.5, ('C#3', 'E4', 'F#4', 'A4')),
                           # m.6
                           (21.0, ('B2', 'F#4', 'B4', 'D5')),
                           (21.5, ('G3', 'D4', 'B4', 'D5')),
                           (22.0, ('E3', 'G4', 'B4', 'C#5')),
                           (22.5, ('F#3', 'F#4', 'A#4', 'C#5')),
                           (23.0, ('B3', 'D4', 'F#4', 'B4')),
                           (24.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.7
                           (25.0, ('B3', 'B3', 'F#4', 'D5')),
                           (25.5, ('B3', 'B3', 'G4', 'D5')),
                           (26.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (26.5, ('A3', 'C#4', 'F#4', 'C#5')),
                           (27.0, ('G3', 'D#4', 'F#4', 'B4')),
                           (27.5, ('G3', 'E4', 'E4', 'B4')),
                           (28.0, ('F#3', 'F#4', 'E4', 'A4')),
                           (28.5, ('F#3', 'F#4', 'D#4', 'A4'))
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_bach_3(self):
      # tests bwv77.mxl offset = 1.0, we're salami slicing
      self.setts.salami =  True
      self.setts.offset =  1.0
      self.actual_result = _event_finder(
                              parts=self.parts_list,
                              settings=self.setts,
                              record=self.actual_result
                           )
      expected_result = [
                           # offset interval: 1.0
                           # repeat identical events
                           # pickup
                           (0.0, ('E3', 'G3', 'B3', 'E4')),
                           # m.1
                           (1.0, ('E3', 'B3', 'E4', 'G4')),
                           (2.0, ('D3', 'D4', 'F#4', 'A4')),
                           (3.0, ('G3', 'D4', 'G4', 'B4')),
                           (4.0, ('D3', 'D4', 'F#4', 'A4')),
                           # m.2
                           (5.0, ('B2', 'F#4', 'B4', 'D5')),
                           (6.0, ('E3', 'G4', 'B4', 'C#5')),
                           (7.0, ('B3', 'D4', 'F#4', 'B4')),
                           (8.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.3
                           (9.0, ('B3', 'B3', 'F#4', 'D5')),
                           (10.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (11.0, ('G3', 'D#4', 'F#4', 'B4')),
                           (12.0, ('F#3', 'F#4', 'E4', 'A4')),
                           # m.4
                           (13.0, ('E3', 'B3', 'E4', 'G4')),
                           (14.0, ('B2', 'B3', 'D#4', 'F#4')),
                           (15.0, ('E3', 'G3', 'B3', 'E4')),
                           (15.0, ('E3', 'G3', 'B3', 'E4')),
                           # m.5
                           (17.0, ('E3', 'B3', 'E4', 'G4')),
                           (18.0, ('D3', 'D4', 'F#4', 'A4')),
                           (19.0, ('G3', 'D4', 'G4', 'B4')),
                           (20.0, ('D3', 'D4', 'F#4', 'A4')),
                           # m.6
                           (21.0, ('B2', 'F#4', 'B4', 'D5')),
                           (22.0, ('E3', 'G4', 'B4', 'C#5')),
                           (23.0, ('B3', 'D4', 'F#4', 'B4')),
                           (24.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.7
                           (25.0, ('B3', 'B3', 'F#4', 'D5')),
                           (26.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (27.0, ('G3', 'D#4', 'F#4', 'B4')),
                           (28.0, ('F#3', 'F#4', 'E4', 'A4'))
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_bach_4(self):
      # tests bwv77.mxl offset = 1.0, we're NOT salami slicing
      self.setts.salami =  False
      self.setts.offset =  1.0
      self.actual_result = _event_finder(
                              parts=self.parts_list,
                              settings=self.setts,
                              record=self.actual_result
                           )
      expected_result = [
                           # offset interval: 1.0
                           # do not repeat identical events
                           # pickup
                           (0.0, ('E3', 'G3', 'B3', 'E4')),
                           # m.1
                           (1.0, ('E3', 'B3', 'E4', 'G4')),
                           (2.0, ('D3', 'D4', 'F#4', 'A4')),
                           (3.0, ('G3', 'D4', 'G4', 'B4')),
                           (4.0, ('D3', 'D4', 'F#4', 'A4')),
                           # m.2
                           (5.0, ('B2', 'F#4', 'B4', 'D5')),
                           (6.0, ('E3', 'G4', 'B4', 'C#5')),
                           (7.0, ('B3', 'D4', 'F#4', 'B4')),
                           (8.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.3
                           (9.0, ('B3', 'B3', 'F#4', 'D5')),
                           (10.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (11.0, ('G3', 'D#4', 'F#4', 'B4')),
                           (12.0, ('F#3', 'F#4', 'E4', 'A4')),
                           # m.4
                           (13.0, ('E3', 'B3', 'E4', 'G4')),
                           (14.0, ('B2', 'B3', 'D#4', 'F#4')),
                           (15.0, ('E3', 'G3', 'B3', 'E4')),
                           # m.5
                           (17.0, ('E3', 'B3', 'E4', 'G4')),
                           (18.0, ('D3', 'D4', 'F#4', 'A4')),
                           (19.0, ('G3', 'D4', 'G4', 'B4')),
                           (20.0, ('D3', 'D4', 'F#4', 'A4')),
                           # m.6
                           (21.0, ('B2', 'F#4', 'B4', 'D5')),
                           (22.0, ('E3', 'G4', 'B4', 'C#5')),
                           (23.0, ('B3', 'D4', 'F#4', 'B4')),
                           (24.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.7
                           (25.0, ('B3', 'B3', 'F#4', 'D5')),
                           (26.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (27.0, ('G3', 'D#4', 'F#4', 'B4')),
                           (28.0, ('F#3', 'F#4', 'E4', 'A4'))
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_bach_5(self):
      # tests bwv77.mxl offset = 2.0, we're salami slicing
      self.setts.salami =  True
      self.setts.offset =  2.0
      self.actual_result = _event_finder(
                              parts=self.parts_list,
                              settings=self.setts,
                              record=self.actual_result
                           )
      expected_result = [
                           # offset interval: 2.0
                           # repeat identical events
                           # pickup
                           (0.0, ('E3', 'G3', 'B3', 'E4')),
                           # m.1
                           (2.0, ('D3', 'D4', 'F#4', 'A4')),
                           (2.0, ('D3', 'D4', 'F#4', 'A4')),
                           # m.2
                           (6.0, ('E3', 'G4', 'B4', 'C#5')),
                           (8.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.3
                           (10.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (12.0, ('F#3', 'F#4', 'E4', 'A4')),
                           # m.4
                           (14.0, ('B2', 'B3', 'D#4', 'F#4')),
                           (16.0, ('E3', 'G3', 'B3', 'E4')),
                           # m.5
                           (18.0, ('D3', 'D4', 'F#4', 'A4')),
                           (18.0, ('D3', 'D4', 'F#4', 'A4')),
                           # m.6
                           (22.0, ('E3', 'G4', 'B4', 'C#5')),
                           (24.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.7
                           (26.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (28.0, ('F#3', 'F#4', 'E4', 'A4'))
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   def test_bach_6(self):
      # tests bwv77.mxl offset = 2.0, we're NOT salami slicing
      self.setts.salami =  False
      self.setts.offset =  2.0
      self.actual_result = _event_finder(
                              parts=self.parts_list,
                              settings=self.setts,
                              record=self.actual_result
                           )
      expected_result = [
                           # offset interval: 2.0
                           # do not repeat identical events
                           # pickup
                           (0.0, ('E3', 'G3', 'B3', 'E4')),
                           # m.1
                           (2.0, ('D3', 'D4', 'F#4', 'A4')),
                           # m.2
                           (6.0, ('E3', 'G4', 'B4', 'C#5')),
                           (8.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.3
                           (10.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (12.0, ('F#3', 'F#4', 'E4', 'A4')),
                           # m.4
                           (14.0, ('B2', 'B3', 'D#4', 'F#4')),
                           (16.0, ('E3', 'G3', 'B3', 'E4')),
                           # m.5
                           (18.0, ('D3', 'D4', 'F#4', 'A4')),
                           # m.6
                           (22.0, ('E3', 'G4', 'B4', 'C#5')),
                           (24.0, ('F#3', 'C#4', 'F#4', 'A4')),
                           # m.7
                           (26.0, ('A3', 'C#4', 'G4', 'C#5')),
                           (28.0, ('F#3', 'F#4', 'E4', 'A4'))
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)
# End TestEventFinderBach -----------------------------------------------------------------------



#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
#run_analysis_suite = unittest.TestLoader().loadTestsFromTestCase(TestRunAnalysis)
analyzer_event_finder_short_suite = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderShort)
analyzer_event_finder_long_monteverdi = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderMonteverdi)
analyzer_event_finder_long_josquin = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderJosquin)
analyzer_event_finder_long_bach = (
unittest.TestLoader().loadTestsFromTestCase(TestEventFinderBach))
