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
# music21
from music21 import note
# vis
from test_corpus import event_finder_short
from models import analyzing



class TestRunAnalysis(unittest.TestCase):
   # Test run_analysis()
   pass
# End TestRunAnalysis ----------------------------------------------------------



class TestEventFinderShort(unittest.TestCase):
   # Test _event_finder() with short excerpts
   # NB: all of these have two parts
   def test_event_finder_short_1(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_1
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_2(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_2
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_3(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_3
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_4(self):
      expected = [(0.0, ('G3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_4
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_5(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'F4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_5
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_6(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_6
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_7(self):
      expected = [(0.0, ('B3', 'A4')), (0.5, ('G3', 'G4')),
                  (1.0, ('A3', 'G4')), (1.5, ('B3', 'F4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_7
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_8(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_8
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_9(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4')),
                  (1.0, ('B3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_9
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_10(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_10
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_11(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_11
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_12(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_12
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_13(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_13
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_14(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_14
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_15(self):
      expected = [(0.0, ('G3', 'G4'))] # different if salami=True
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_15
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_16(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('Rest', 'A4')),
                  (1.0, ('F3', 'A4')), (1.5, ('E3', 'B4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_16
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
                             salami=False,
                             record=actual)
      self.assertEqual(expected, actual._record)



   def test_event_finder_short_17(self):
      expected = [(0.0, ('G3', 'G4')), (0.5, ('A3', 'G4')),
                  (1.0, ('F3', 'A4')), (1.5, ('G3', 'F4')),
                  (2.0, ('G3', 'E4'))]
      actual = analyzing.AnalysisRecord()
      this_piece = event_finder_short.test_17
      Analyzer._event_finder(parts=[this_piece[0], this_piece[1]],
                             types=[note.Note, note.Rest],
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
run_analysis_suite = unittest.TestLoader().loadTestsFromTestCase(TestRunAnalysis)
event_finder_short_suite = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderShort)
event_finder_long_suite = unittest.TestLoader().loadTestsFromTestCase(TestEventFinderLong)
