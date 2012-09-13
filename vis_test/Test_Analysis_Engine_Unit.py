#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         Test_Output_Formatting.py
# Purpose:      Unit tests for the get_formatted_ngrams() and
#               get_formatted_intervals() in the Vertical_Interval_Statistics
#               module.
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
from test_corpus import vis_these_parts_unit_tests



#------------------------------------------------------------------------------
class Test_Analysis_Engine_Unit( unittest.TestCase ):
   '''
   Contains unit tests for vis_these_parts(). These tests are small fragments
   to help ensure vis_these_parts() functions correctly, before integration
   testing on larger segments of real pieces. These tests are designed to put
   vis_these_parts() through all the tough situations I can predict.
   '''
   def setUp( self ):
      self.stats = Vertical_Interval_Statistics()
      self.settings = VIS_Settings()
   
   def test_one( self ):
      # Test 1
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_1[0]
      lower_part = vis_these_parts_unit_tests.test_1[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_two( self ):
      # Test 2
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_2[0]
      lower_part = vis_these_parts_unit_tests.test_2[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_three( self ):
      # Test 3
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_3[0]
      lower_part = vis_these_parts_unit_tests.test_3[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_four( self ):
      # Test 4
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_4[0]
      lower_part = vis_these_parts_unit_tests.test_4[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_five( self ):
      # Test 5
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_5[0]
      lower_part = vis_these_parts_unit_tests.test_5[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'm6':1 }
      
      expected_no_quality2grams = { '8 +2 6':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_six( self ):
      # Test 6
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_6[0]
      lower_part = vis_these_parts_unit_tests.test_6[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'm7':1 }
      
      expected_no_quality2grams = { '8 +2 7':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_sixB( self ):
      # Test 6B
      # Same as 6, plus an extra qL=0.5 at beginning and end of both streams.
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_6B[0]
      lower_part = vis_these_parts_unit_tests.test_6B[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'm7':2, 'd5':1 }
      
      expected_no_quality2grams = { '7 -3 8':1, '8 +2 7':1, '7 +2 5':1 }
      
      # Verify the findings
      #self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_seven( self ):
      # Test 7
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_7[0]
      lower_part = vis_these_parts_unit_tests.test_7[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'm7':1 }
      
      expected_no_quality2grams = { '8 +2 7':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_sevenB( self ):
      # Test 7B
      # Same as 7, plus an extra qL=0.5 at the end in both streams.
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_7B[0]
      lower_part = vis_these_parts_unit_tests.test_7B[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'm7':1, 'm6':1 }
      
      expected_no_quality2grams = { '8 +2 7':1, '7 +2 6':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_eight( self ):
      # Test 8
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_8[0]
      lower_part = vis_these_parts_unit_tests.test_8[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'm7':1 }
      
      expected_no_quality2grams = { '8 +2 7':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_nine( self ):
      # Test 9
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_9[0]
      lower_part = vis_these_parts_unit_tests.test_9[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_ten( self ):
      # Test 10
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_10[0]
      lower_part = vis_these_parts_unit_tests.test_10[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_eleven( self ):
      # Test 11
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_11[0]
      lower_part = vis_these_parts_unit_tests.test_1[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_twelve( self ):
      # Test 12
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_12[0]
      lower_part = vis_these_parts_unit_tests.test_12[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_thirteen( self ):
      # Test 13
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_13[0]
      lower_part = vis_these_parts_unit_tests.test_13[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':2 }
      
      expected_no_quality2grams = {}
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_fourteen( self ):
      # Test 14
      
      # Process the excerpt
      #the_piece = vis_these_parts_unit_tests.test_1
      higher_part = vis_these_parts_unit_tests.test_14[0]
      lower_part = vis_these_parts_unit_tests.test_14[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'M10':1, 'P12':1 }
      
      expected_no_quality2grams = { '10 -2 12':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
   
   def test_fifteen( self ):
      # Test 15
      
      # Process the excerpt
      higher_part = vis_these_parts_unit_tests.test_15[0]
      lower_part = vis_these_parts_unit_tests.test_15[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':2, 'M10':1, 'm7':1, 'M6':1 }
      
      expected_no_quality2grams = { '8 +2 8':1, '8 -3 10':1, '10 +2 7':1, \
         '7 1 6':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(2)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(2), expected_no_quality2grams )
# End Test_Vis_These_Parts_Unit -----------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( Test_Analysis_Engine_Unit )
