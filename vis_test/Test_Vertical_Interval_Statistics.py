#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         Test_Sorting.py
# Purpose:      Unit tests for the Vertical_Interval_Statistics class.
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



import unittest
from vis import *
from music21 import interval, note



#-------------------------------------------------------------------------------
class Test_Vertical_Interval_Statistics( unittest.TestCase ):
   def setUp( self ):
      self.vis = Vertical_Interval_Statistics()
      self.m3 = interval.Interval( 'm3' )
      self.M3 = interval.Interval( 'M3' )
      self.m10 = interval.Interval( 'm10' )
      self.M10 = interval.Interval( 'M10' )
      # Descending versions
      self.d_m3 = interval.Interval( 'm-3' )
      self.d_M3 = interval.Interval( 'M-3' )
      self.d_m10 = interval.Interval( 'm-10' )
      self.d_M10 = interval.Interval( 'M-10' )
      # m3 u m3
      self.nga = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C5'))])
      # m3 u M3
      self.ngb = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C#5'))])
      # m3 +P4 m3
      self.ngc = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('F5'))])
      # m3 +d4 M3
      self.ngd = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D-5'),note.Note('F5'))])
      # m3 -P4 m3
      self.nge = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('E4'),note.Note('G4'))])
      # m3 -P4 M-3
      self.ngf = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('G#4'),note.Note('E4'))])
      # self.ngg  m3 +P4 M2 -m6 P5 +m2 M-10
      self.ngg = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('E5')), \
                interval.Interval(note.Note('F#4'),note.Note('C#5')), \
                interval.Interval(note.Note('G##5'),note.Note('E#4'))])
      # self.ngh  m3 +P4 M2 -m6 P5 +m2 M-3
      self.ngh = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('E5')), \
                interval.Interval(note.Note('F#4'),note.Note('C#5')), \
                interval.Interval(note.Note('G##4'),note.Note('E#4'))])
   
   # get_formatted_ngram_dict() ---------------------------
   def test_get_formatted_ngram_dict_1( self ):
      self.vis.add_ngram( self.nga )
      self.vis.add_ngram( self.ngh )
      check = self.vis.get_formatted_ngram_dict()
      expected = [{}, {}, {'3 1 3':1}, {}, {'3 +4 2 -6 5 +2 -3':1}]
      self.assertEqual( check, expected )
   
   def test_get_formatted_ngram_dict_2( self ):
      self.vis.add_ngram( self.nga )
      self.vis.add_ngram( self.ngh )
      check = self.vis.get_formatted_ngram_dict( 2 )
      expected = {'3 1 3':1}
      self.assertEqual( check, expected )
   
   def test_get_formatted_ngram_dict_3( self ):
      self.vis.add_ngram( self.nga )
      self.vis.add_ngram( self.ngh )
      check = self.vis.get_formatted_ngram_dict( 4 )
      expected = {'3 +4 2 -6 5 +2 -3':1}
      self.assertEqual( check, expected )
   
   # add_interval() ---------------------------------------
   def test_addUpInterval( self ):
      self.vis.add_interval( self.m3 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m3'], 1 )
      self.vis.add_interval( self.m10 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m10'], 1 )
      self.vis.add_interval( self.M3 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['M3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['M3'], 1 )
      self.vis.add_interval( self.d_m3 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m3'], 1 )
      self.vis.add_interval( self.d_m10 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m10'], 1 )
   
   def test_addDownInterval( self ):
      self.vis.add_interval( self.d_m3 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-3'], 1 )
      self.vis.add_interval( self.d_m10 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m-3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-10'], 1 )
      self.vis.add_interval( self.d_M3 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['M-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['M-3'], 1 )
      self.vis.add_interval( self.m3 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m-3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-3'], 1 )
      self.vis.add_interval( self.m10 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m-3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-10'], 1 )
   
   def test_addUpDownIntervals( self ):
      self.vis.add_interval( self.m3 )
      self.vis.add_interval( self.d_m3 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m3'], 1 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-3'], 1 )
      self.vis.add_interval( self.m10 )
      self.vis.add_interval( self.d_m10 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m10'], 1 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m-3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-10'], 1 )
      self.vis.add_interval( self.M3 )
      self.vis.add_interval( self.d_M3 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['M3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['M3'], 1 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['M-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['M-3'], 1 )
      self.vis.add_interval( self.M10 )
      self.vis.add_interval( self.d_M10 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m10'], 1 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['m-3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['m-10'], 1 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['M3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['M3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['M10'], 1 )
      self.assertEqual( self.vis.get_simple_interval_summary_dict()['M-3'], 2 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['M-3'], 1 )
      self.assertEqual( self.vis.get_compound_interval_summary_dict()['M-10'], 1 )
   
   # get_interval_occurrences() ---------------------------
   def test_get_interval_occurrences_heed_quality_Up( self ):
      self.vis.add_interval( self.m3 )
      self.vis.add_interval( self.m10 )
      self.vis.add_interval( self.M3 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M3', 'simple' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M10', 'compound' ), 0 )
      self.vis.add_interval( self.M10 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M10', 'compound' ), 1 )
   
   def test_get_interval_occurrences_heed_quality_Down( self ):
      self.vis.add_interval( self.d_m3 )
      self.vis.add_interval( self.d_m10 )
      self.vis.add_interval( self.d_M3 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-3', 'simple' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-10', 'compound' ), 0 )
      self.vis.add_interval( self.d_M10 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-10', 'compound' ), 1 )
   
   def test_get_interval_occurrences_heed_quality_Both( self ):
      self.vis.add_interval( self.d_m3 )
      self.vis.add_interval( self.d_m10 )
      self.vis.add_interval( self.d_M3 )
      self.vis.add_interval( self.d_M10 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm3', 'simple' ), 0 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M3', 'simple' ), 0 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm3', 'compound' ), 0 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M3', 'compound' ), 0 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm10', 'compound' ), 0 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M10', 'compound' ), 0 )
      self.vis.add_interval( self.m3 )
      self.vis.add_interval( self.m10 )
      self.vis.add_interval( self.M3 )
      self.vis.add_interval( self.M10 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm-10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M-10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'm10', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( 'M10', 'compound' ), 1 )
   
   def test_get_interval_occurrences_noHeedQuality_Up( self ):
      self.vis.add_interval( self.m3 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'simple' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( '10', 'compound' ), 0 )
      self.vis.add_interval( self.m10 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( '10', 'compound' ), 1 )
      self.vis.add_interval( self.M3 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'simple' ), 3 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'compound' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '10', 'compound' ), 1 )
      self.vis.add_interval( self.M10 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'simple' ), 4 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'compound' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '10', 'compound' ), 2 )
   
   def test_get_interval_occurrences_noHeedQuality_Down( self ):
      self.vis.add_interval( self.d_m3 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'simple' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( '-10', 'compound' ), 0 )
      self.vis.add_interval( self.d_m10 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'simple' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'compound' ), 1 )
      self.assertEqual( self.vis.get_interval_occurrences( '-10', 'compound' ), 1 )
      self.vis.add_interval( self.d_M3 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'simple' ), 3 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'compound' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '-10', 'compound' ), 1 )
      self.vis.add_interval( self.d_M10 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'simple' ), 4 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'compound' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '-10', 'compound' ), 2 )
   
   def test_get_interval_occurrences_noHeedQuality_Both( self ):
      self.vis.add_interval( self.m3 )
      self.vis.add_interval( self.m10 )
      self.vis.add_interval( self.M3 )
      self.vis.add_interval( self.M10 )
      self.vis.add_interval( self.d_m3 )
      self.vis.add_interval( self.d_m10 )
      self.vis.add_interval( self.d_M3 )
      self.vis.add_interval( self.d_M10 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'simple' ), 4 )
      self.assertEqual( self.vis.get_interval_occurrences( '-3', 'compound' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '-10', 'compound' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'simple' ), 4 )
      self.assertEqual( self.vis.get_interval_occurrences( '3', 'compound' ), 2 )
      self.assertEqual( self.vis.get_interval_occurrences( '10', 'compound' ), 2 )
   
   def test_get_interval_occurrences_errors_and_zero( self ):
      self.assertEqual( self.vis.get_interval_occurrences( 'P4', 'simple' ), 0 )
      self.assertEqual( self.vis.get_interval_occurrences( 'P4', 'compound' ), 0 )
      self.assertEqual( self.vis.get_interval_occurrences( '6', 'simple' ), 0 )
      self.assertEqual( self.vis.get_interval_occurrences( '6', 'compound' ), 0 )
      self.assertRaises( NonsensicalInputError, self.vis.get_interval_occurrences, 'P4', 'wrong3343' )
      self.assertRaises( NonsensicalInputError, self.vis.get_interval_occurrences, 'P4', '' )
      self.assertRaises( NonsensicalInputError, self.vis.get_interval_occurrences, 'P4', 5 )
      self.assertRaises( NonsensicalInputError, self.vis.get_interval_occurrences, 'P4', False )
      self.assertRaises( NonsensicalInputError, self.vis.get_interval_occurrences, 'P4', self.m3 )
   
   # add_ngram() ------------------------------------------
   def test_add_ngram( self ):
      # basic 2-gram
      self.vis.add_ngram( self.ngc ) # m3 +P4 m3
      #self.assertEqual( self.vis.get_formatted_ngram_dict( 2 ), {'m3 +P4 m3': 1} )
      self.assertEqual( self.vis.get_formatted_ngram_dict( 2 ), {'3 +4 3': 1} )
      # two of a basic 2-gram
      self.vis.add_ngram( self.ngc ) # m3 +P4 m3
      #self.assertEqual( self.vis.get_formatted_ngram_dict( 2 ), {'m3 +P4 m3': 2} )
      self.assertEqual( self.vis.get_formatted_ngram_dict( 2 ), {'3 +4 3': 2} )
      # add one of a similar 2-gram
      self.vis.add_ngram( self.ngd ) # m3 +d4 M3
      #self.assertEqual( self.vis.get_formatted_ngram_dict( 2 ), {'m3 +P4 m3': 2, 'm3 +d4 M3': 1} )
      self.assertEqual( self.vis.get_formatted_ngram_dict( 2 ), {'3 +4 3': 3} )
      # add a 4-gram, 16 times
      for i in xrange(16):
         self.vis.add_ngram( self.ngg ) # m3 +P4 M2 -m6 P5 -m2 M-10
      #self.assertEqual( self.vis.get_formatted_ngram_dict( 2 ), {'m3 +P4 m3': 2, 'm3 +d4 M3': 1} )
      #self.assertEqual( self.vis.get_formatted_ngram_dict( 4 ), {'m3 +P4 M2 -m6 P5 +A9 M-10': 16} )
      self.assertEqual( self.vis.get_formatted_ngram_dict( 2 ), {'3 +4 3': 3} )
      self.assertEqual( self.vis.get_formatted_ngram_dict( 4 ), {'3 +4 2 -6 5 +9 -10': 16} )
   
   # get_ngram_occurrences() ------------------------------
   #def test_get_ngram_occurrences( self ):
      # NOTE: Test removed because the method is broken and also removed. If we
      # need this method again, we'll have to modify these tests.
      ## get_ngram_occurrences( self, whichNGram, n )
      ## test that non-existant n values are dealt with properly
      #self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 3', n=2 ), 0 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 3', n=64 ), 0 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '', n=2 ), 0 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '', n=128 ), 0 )
      
      ## test 2 n-grams
      ## self.ngd:  m-3 +P4 M3
      ## self.nge:  m3 -P4 m3
      #self.vis = Vertical_Interval_Statistics()
      #for i in xrange(12):
         #self.vis.add_ngram( self.ngd )
      #for i in xrange(8):
         #self.vis.add_ngram( self.nge )
      #self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +d4 M3', n=2 ), 12 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 3', n=2 ), 12 )
      #self.assertEqual( self.vis.get_ngram_occurrences( 'm3 -P4 m3', n=2 ), 8 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '3 -4 3', n=2 ), 8 )
      
      ## test distinct 4-grams with identical simple-interval representations
      ## self.ngg  m3 +P4 M2 -m6 P5 -m2 M10
      #self.vis = Vertical_Interval_Statistics()
      #for i in xrange(10):
         #self.vis.add_ngram( self.ngg )
      #self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +P4 M2 -m6 P5 +A9 M-10', n=4 ), 10 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 2 -6 5 +9 -10', n=4 ), 10 )
      #self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +P4 M2 -m6 P5 +A2 M-3', n=4 ), 0 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 2 -6 5 +9 -3', n=4 ), 0 )
      ## self.ngh  m3 +P4 M2 -m6 P5 -m2 M3
      #for i in xrange(7):
         #self.vis.add_ngram( self.ngh )
      #self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +P4 M2 -m6 P5 +A9 M-10', n=4 ), 10 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 2 -6 5 +9 -10', n=4 ), 10 )
      #self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +P4 M2 -m6 P5 +A2 M-3', n=4 ), 7 )
      #self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 2 -6 5 +2 -3', n=4 ), 7 )
   
   # _reduce_qualities() ----------------------------------
   def test__reduce_qualities( self ):
      # this stands for interval_dictionary
      i_d = {'m3':5, 'M3':4}
      self.assertEqual( Vertical_Interval_Statistics._reduce_qualities( i_d ), \
                        {'3':9} )
      i_d['d3'] = 12
      self.assertEqual( Vertical_Interval_Statistics._reduce_qualities( i_d ), \
                        {'3':21} )
      i_d['A3'] = 12
      i_d['P3'] = 12
      self.assertEqual( Vertical_Interval_Statistics._reduce_qualities( i_d ), \
                        {'3':45} )
      i_d['d1'] = 1
      i_d['P1'] = 4
      self.assertEqual( Vertical_Interval_Statistics._reduce_qualities( i_d ), \
                        {'1':5, '3':45} )

   def test_compare_noHeedQuality( self ):
      other_stats = Vertical_Interval_Statistics()
      settings = VIS_Settings()
      output = '''2-Gram  # settings1  # settings2
--------------------------------
3 +4 3  3            1
3 1 3   2            4

Total difference between 2-grams: 0.8
'''
      settings.set_property( 'heedQuality false')
      other_stats.add_ngram( self.ngc )
      for i in range(2):
         self.vis.add_ngram( self.nga )
      for i in range(3):
         self.vis.add_ngram( self.ngc )
      for i in range(4):
         other_stats.add_ngram( self.nga )
      self.assertEqual( self.vis.compare( settings, other_stats, "settings1", "settings2", ""), output )

   def test_compare_heedQuality( self ):
      other_stats = Vertical_Interval_Statistics()
      settings = VIS_Settings()
      output = '''2-Gram     # settings1  # settings2
-----------------------------------
m3 +P4 m3  3            1
m3 P1 m3   2            4

Total difference between 2-grams: 0.8
'''
      settings.set_property( 'heedQuality true')
      other_stats.add_ngram( self.ngc )
      for i in range(2):
         self.vis.add_ngram( self.nga )
      for i in range(3):
         self.vis.add_ngram( self.ngc )
      for i in range(4):
         other_stats.add_ngram( self.nga )
      self.assertEqual( self.vis.compare( settings, other_stats, "settings1", "settings2", ""), output )


# End TestVertical_Interval_Statistics ----------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( Test_Vertical_Interval_Statistics )
