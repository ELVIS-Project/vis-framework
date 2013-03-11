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
from controllers import analyzer



class TestRunAnalysis(unittest.TestCase):
   # Test run_analysis()
   pass
# End TestRunAnalysis ----------------------------------------------------------



class TestEventFinderShort(unittest.TestCase):
   # Test _event_finder() with short excerpts
   # NB: all of these have two parts



   def setUp(self):
      self.a = analyzer.Analyzer()
      self.setts = analyzing.AnalysisSettings()
      self.setts.set('types', [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')])
      self.setts.set('salami', False)
      self.setts.set('offset', 0.5)



   def test_event_finder_short_1(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_1
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_2(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_2
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_3(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_3
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_4(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_4
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_5(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'F4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_5
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_6(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_6
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_7(self):
      expected = [(0.0, ('B3', 'A4')), (0.5, ('G3', 'G4')),
                  (1.0, ('A3', 'G4')), (1.5, ('B3', 'F4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_7
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_8(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_8
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_9(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4')),
                  (1.0, ('B3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_9
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_10(self):
      # NOTE: the thing reported at 0.25 is for the 0.5 offset
      expected = [(0.0, ('G3', 'G4')), (0.25, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_10
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_11(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_11
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_12(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_12
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_13(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_13
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_14(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_14
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_15(self):
      expected = [(0.0, ('G3', 'G4')), (1.0, ('Rest', 'G4')), (1.5, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_15
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_16(self):
      # NOTE: the thing at 0.75 is for the 1.0 offset
      expected = [(0.0, ('G3', 'G4')), (0.5, ('Rest', 'A4')),
                  (0.75, ('F3', 'A4')), (1.5, ('E3', 'B4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_16
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_17(self):
      # NOTE: the thing at 0.75 is for the 1.0 offset
      # NOTE: the thing at 1.375 is for the 1.5 offset
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'A4')),
                  (0.75, ('F3', 'A4')), (1.375, ('G3', 'F4')),
                  (2.0, ('G3', 'E4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_17
      actual = self.a._event_finder([this_piece[0], this_piece[1]], self.setts, actual)
      self.assertEqual(expected, actual._record)
# End TestEventFinderShort -----------------------------------------------------



class TestEventFinderMonteverdi(unittest.TestCase):
   # Test _event_finder() with long excerpts

   def test_madrigal_1(self):
      # tests madrigal51.mxl (cruda amarilli) offset = 0.5, we're salami slicing
      the_analyzer = analyzer.Analyzer()
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.set('types', [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')])
      setts.set('salami', True)
      setts.set('offset', 0.5)
      actual_result = the_analyzer._event_finder(parts=[madrigal.parts[0],  madrigal.parts[1]],
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
                        (4.0, (u'B4', u'D5')),
                        (4.0, (u'B4', u'D5')),
                        (4.0, (u'B4', u'D5')),
                        (4.0, (u'B4', u'D5')),
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
                        (20.0, (u'E5', u'G5')),
                        (20.0, (u'E5', u'G5')),
                        (20.0, (u'E5', u'G5')),
                        (20.0, (u'E5', u'G5')),
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
                        (33.5, (u'G4', u'C5')),
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
      the_analyzer = analyzer.Analyzer()
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.set('types', [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')])
      setts.set('salami', True)
      setts.set('offset', 1.0)
      actual_result = the_analyzer._event_finder(parts=[madrigal.parts[0],  madrigal.parts[1]],
                                                 settings=setts,
                                                 record=actual_result)
      expected_result = [(0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        # m. 2
                        (4.0, ('B4', 'D5')),
                        (4.0, ('B4', 'D5')),
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
                        (20.0, ('E5', 'G5')),
                        (20.0, ('E5', 'G5')),
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
      the_analyzer = analyzer.Analyzer()
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.set('types', [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')])
      setts.set('salami', True)
      setts.set('offset', 2.0)
      actual_result = the_analyzer._event_finder(parts=[madrigal.parts[0],  madrigal.parts[1]],
                                                 settings=setts,
                                                 record=actual_result)
      expected_result = [(0.0, ('B4', 'D5')),
                        (0.0, ('B4', 'D5')),
                        # m. 2
                        (4.0, ('B4', 'D5')),
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
                        (20.0, ('E5', 'G5')),
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
      the_analyzer = analyzer.Analyzer()
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.set('types', [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')])
      setts.set('salami', False)
      setts.set('offset', 0.5)
      actual_result = the_analyzer._event_finder(parts=[madrigal.parts[0],  madrigal.parts[1]],
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
      the_analyzer = analyzer.Analyzer()
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.set('types', [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')])
      setts.set('salami', False)
      setts.set('offset', 1.0)
      actual_result = the_analyzer._event_finder(parts=[madrigal.parts[0],  madrigal.parts[1]],
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
      the_analyzer = analyzer.Analyzer()
      madrigal = converter.parse('test_corpus/madrigal51.mxl')
      actual_result = analyzing.AnalysisRecord()
      setts = analyzing.AnalysisSettings()
      setts.set('types', [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')])
      setts.set('salami', False)
      setts.set('offset', 2.0)
      actual_result = the_analyzer._event_finder(parts=[madrigal.parts[0],  madrigal.parts[1]],
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
      self.the_analyzer = analyzer.Analyzer()
      self.actual_result = analyzing.AnalysisRecord()
      self.piece = converter.parse('test_corpus/Jos2308.krn')
      self.parts_list = [self.piece.parts[0][67:74],
                         self.piece.parts[1][67:74],
                         self.piece.parts[2][67:74],
                         self.piece.parts[3][67:74]]
      self.setts = analyzing.AnalysisSettings()
      self.setts.set('types', [(note.Note, lambda x: x.nameWithOctave), (note.Rest, lambda x: 'Rest')])



   def test_josquin_1(self):
      # tests Jos2308.krn ("Ave maris stella") offset = 0.5, we're salami slicing
      self.setts.set('salami', True)
      self.setts.set('offset', 0.5)
      self.actual_result = self.the_analyzer._event_finder(parts=self.parts_list,
                                                           settings=self.setts,
                                                           record=self.actual_result)
      expected_result = [(464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+0.0, ('A3', 'A3', 'C5', 'Rest')),
                         (464+2.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+2.5, ('F3', 'A3', 'A4', 'Rest')),
                         (464+3.0, ('F3', 'A3', 'A4', 'Rest')),
                         (464+3.5, ('F3', 'A3', 'A4', 'Rest')),
                         (464+4.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+4.5, ('E3', 'C4', 'G4', 'Rest')),
                         (464+5.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+5.5, ('E3', 'C4', 'G4', 'Rest')),
                         (464+6.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+6.5, ('E3', 'C4', 'G4', 'Rest')),
                         (464+7.0, ('E3', 'C4', 'G4', 'Rest')),
                         (464+7.5, ('E3', 'C4', 'G4', 'Rest')),
                         # m. 60
                         (464+8.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+8.5, ('D3', 'D4', 'F4', 'Rest')),
                         (464+9.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+9.5, ('D3', 'D4', 'F4', 'Rest')),
                         (464+10.0, ('D3', 'D4', 'F4', 'Rest')),
                         (464+10.5, ('D3', 'D4', 'F4', 'Rest')),
                         (464+11.0, ('D3', 'D4', 'G4', 'Rest')),
                         (464+11.5, ('D3', 'D4', 'G4', 'Rest')),
                         (464+12.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+12.5, ('D3', 'D4', 'A4', 'Rest')),
                         (464+13.0, ('D3', 'D4', 'A4', 'Rest')),
                         (464+13.5, ('D3', 'D4', 'A4', 'Rest')),
                         (464+14.0, ('D3', 'D4', 'B-4', 'Rest')),
                         (464+14.5, ('D3', 'D4', 'B-4', 'Rest')),
                         (464+15.0, ('D3', 'D4', 'B-4', 'Rest')),
                         (464+15.5, ('D3', 'D4', 'B-4', 'Rest')),
                         # m. 61
                         (464+16.0, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+16.5, ('Rest', 'G3', 'B-4', 'Rest')),
                         (464+17.0, ('Rest', 'G3', 'A4', 'Rest')),
                         (464+17.5, ('Rest', 'G3', 'A4', 'Rest')),
                         (464+18.0, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+18.5, ('Rest', 'G3', 'G4', 'Rest')),
                         (464+19.0, ('Rest', 'A3', 'F4', 'Rest')),
                         (464+19.5, ('Rest', 'A3', 'F4', 'Rest')),
                         (464+20.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+20.5, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+21.0, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+21.5, ('Rest', 'B-3', 'G4', 'Rest')),
                         (464+22.0, ('Rest', 'C4', 'A4', 'Rest')),
                         (464+22.5, ('Rest', 'C4', 'A4', 'Rest')),
                         (464+23.0, ('Rest', 'C4', 'A4', 'Rest')),
                         (464+23.5, ('Rest', 'C4', 'A4', 'Rest')),
                         # m. 62
                         (464+24.0, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+24.5, ('Rest', 'A3', 'A4', 'Rest')),
                         (464+25.0, ('Rest', 'A3', 'G4', 'Rest')),
                         (464+25.5, ('Rest', 'A3', 'G4', 'Rest')),
                         (464+26.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+26.5, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+27.0, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+27.5, ('Rest', 'B-3', 'F4', 'Rest')),
                         (464+28.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+28.5, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+29.0, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+29.5, ('Rest', 'G3', 'F4', 'Rest')),
                         (464+30.0, ('Rest', 'G3', 'E4', 'Rest')),
                         (464+30.5, ('Rest', 'G3', 'E4', 'Rest')),
                         (464+31.0, ('Rest', 'G3', 'E4', 'Rest')),
                         (464+31.5, ('Rest', 'G3', 'E4', 'Rest')),
                         # m. 63
                         (464+32.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+32.5, ('Rest', 'F3', 'F4', 'A4')),
                         (464+33.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+33.5, ('Rest', 'F3', 'F4', 'A4')),
                         (464+34.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+34.5, ('Rest', 'F3', 'F4', 'A4')),
                         (464+35.0, ('Rest', 'F3', 'F4', 'A4')),
                         (464+35.5, ('Rest', 'F3', 'F4', 'A4')),
                         (464+36.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+36.5, ('A3', 'F3', 'Rest', 'C5')),
                         (464+37.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+37.5, ('A3', 'F3', 'Rest', 'C5')),
                         (464+38.0, ('A3', 'F3', 'Rest', 'C5')),
                         (464+38.5, ('A3', 'F3', 'Rest', 'C5')),
                         (464+39.0, ('A3', 'F3', 'Rest', 'B-4')),
                         (464+39.5, ('A3', 'F3', 'Rest', 'B-4')),
                         # m. 64
                         (464+40.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+40.5, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+41.0, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+41.5, ('C4', 'Rest', 'Rest', 'A4')),
                         (464+42.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+42.5, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+43.0, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+43.5, ('C4', 'Rest', 'Rest', 'G4')),
                         (464+44.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+44.5, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+45.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+45.5, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+46.0, ('A3', 'Rest', 'Rest', 'E4')),
                         (464+46.5, ('A3', 'Rest', 'Rest', 'E4')),
                         (464+47.0, ('A3', 'Rest', 'Rest', 'E4')),
                         (464+47.5, ('A3', 'Rest', 'Rest', 'E4')),
                         # m. 65
                         (464+48.0, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+48.5, ('B-3', 'Rest', 'Rest', 'E4')),
                         (464+49.0, ('B-3', 'Rest', 'Rest', 'D4')),
                         (464+49.5, ('B-3', 'Rest', 'Rest', 'D4')),
                         (464+50.0, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+50.5, ('B-3', 'Rest', 'Rest', 'G4')),
                         (464+51.0, ('G3', 'Rest', 'Rest', 'G4')),
                         (464+51.5, ('G3', 'Rest', 'Rest', 'G4')),
                         (464+52.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+52.5, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+53.0, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+53.5, ('A3', 'Rest', 'Rest', 'G4')),
                         (464+54.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+54.5, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+55.0, ('A3', 'Rest', 'Rest', 'F4')),
                         (464+55.5, ('A3', 'Rest', 'Rest', 'F4')),
                        ]
      self.assertEqual(expected_result,  self.actual_result._record)



   #def test_josquin_2(self):
      ## tests Jos2308.krn ("Ave maris stella") offset = 1.0, we're salami slicing
      #self.setts.set('salami', True)
      #self.setts.set('offset', 1.0)
      #self.actual_result = self.the_analyzer._event_finder(parts=self.parts_list,
                                                           #settings=self.setts,
                                                           #record=self.actual_result)
      #expected_result = []
      #self.assertEqual(expected_result,  self.actual_result._record)



   #def test_madrigal_3(self):
      ## tests Jos2308.krn ("Ave maris stella") offset = 2.0, we're salami slicing
      #self.setts.set('salami', True)
      #self.setts.set('offset', 2.0)
      #self.actual_result = self.the_analyzer._event_finder(parts=self.parts_list,
                                                           #settings=self.setts,
                                                           #record=self.actual_result)
      #expected_result = []
      #self.assertEqual(expected_result,  self.actual_result._record)



   #def test_josquin_4(self):
      ## tests Jos2308.krn ("Ave maris stella") offset = 0.5, we're NOT salami slicing
      #self.setts.set('salami', False)
      #self.setts.set('offset', 0.5)
      #self.actual_result = self.the_analyzer._event_finder(parts=self.parts_list,
                                                           #settings=self.setts,
                                                           #record=self.actual_result)
      #expected_result = []
      #self.assertEqual(expected_result,  self.actual_result._record)



   #def test_josquin_5(self):
      ## tests Jos2308.krn ("Ave maris stella") offset = 1.0, we're NOT salami slicing
      #self.setts.set('salami', False)
      #self.setts.set('offset', 1.0)
      #self.actual_result = self.the_analyzer._event_finder(parts=self.parts_list,
                                                           #settings=self.setts,
                                                           #record=self.actual_result)
      #expected_result = []
      #self.assertEqual(expected_result,  self.actual_result._record)



   def test_josquin_6(self):
      # tests Jos2308.krn ("Ave maris stella") offset = 2.0, we're NOT salami slicing
      self.setts.set('salami', False)
      self.setts.set('offset', 2.0)
      self.actual_result = self.the_analyzer._event_finder(parts=self.parts_list,
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



#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
#run_analysis_suite = unittest.TestLoader().loadTestsFromTestCase(TestRunAnalysis)
analyzer_event_finder_short_suite = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderShort)
analyzer_event_finder_long_monteverdi = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderMonteverdi)
analyzer_event_finder_long_josquin = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderJosquin)
