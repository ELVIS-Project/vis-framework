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
from music21 import note
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



   def test_event_finder_short_1(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_1
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                                    types=[note.Note, note.Rest],
                                    offset=0.5,
                                    salami=False,
                                    record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_2(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_2
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_3(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_3
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_4(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_4
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_5(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'F4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_5
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_6(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_6
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_7(self):
      expected = [(0.0, ('B3', 'A4')), (0.5, ('G3', 'G4')),
                  (1.0, ('A3', 'G4')), (1.5, ('B3', 'F4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_7
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_8(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_8
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_9(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4')),
                  (1.0, ('B3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_9
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_10(self):
      # NOTE: the thing reported at 0.25 is for the 0.5 offset
      expected = [(0.0, ('G3', 'G4')), (0.25, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_10
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_11(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_11
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_12(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_12
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_13(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_13
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_14(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_14
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_15(self):
      expected = [(0.0, ('G3', 'G4')), (1.0, ('Rest', 'G4')), (1.5, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_15
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_16(self):
      # NOTE: the thing at 0.75 is for the 1.0 offset
      expected = [(0.0, ('G3', 'G4')), (0.5, ('Rest', 'A4')),
                  (0.75, ('F3', 'A4')), (1.5, ('E3', 'B4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_16
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_17(self):
      # NOTE: the thing at 0.75 is for the 1.0 offset
      # NOTE: the thing at 1.375 is for the 1.5 offset
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'A4')),
                  (0.75, ('F3', 'A4')), (1.375, ('G3', 'F4')),
                  (2.0, ('G3', 'E4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_17
      actual = self.a._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             offset=0.5,
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)
# End TestEventFinderShort -----------------------------------------------------



class TestEventFinderLong(unittest.TestCase):
   # Test _event_finder() with long excerpts
   pass
# End TestEventFinderLong ------------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
#run_analysis_suite = unittest.TestLoader().loadTestsFromTestCase(TestRunAnalysis)
analyzer_event_finder_short_suite = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderShort)
#event_finder_long_suite = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderLong)
