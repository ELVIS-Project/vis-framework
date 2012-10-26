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
from Vertical_Interval_Statistics import Vertical_Interval_Statistics
from VIS_Settings import VIS_Settings
from music21 import converter
from analytic_engine import vis_these_parts



#-------------------------------------------------------------------------------
class Test_Analysis_Engine_Integration_Long( unittest.TestCase ):
   # vis_these_parts( theseParts, theSettings, theStatistics )
   #
   # This test suite expands on the TestVisTheseParts() by using longer
   # excerpts, which increases the chances for errors and also allows me to see
   # how long longer excerpts take.

   def setUp( self ):
      self.stats = Vertical_Interval_Statistics()
      self.settings = VIS_Settings()

   def test_Messiah( self ):
      # Title: "Sinfony" from "Messiah" by Handel
      # Format: MuseData
      # Voices: Violino I and Violino II
      # Measures: 14 through 50

      # Process the excerpt
      filename = 'test_corpus/sinfony.md'
      the_piece = converter.parse( filename )
      # offset 52.0 is m.14
      # offset 200.0 is m.51
      higher_part = the_piece.parts[0].getElementsByOffset( 52.0, 199.9 )
      lower_part = the_piece.parts[1].getElementsByOffset( 52.0, 199.9 )
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      # Prepare the findings
      expected_compound_intervals = { 'P1':12, 'M6':14, 'm7':4, 'P8':7, 'm10':7, \
            'm9':1, 'd4':5, 'm3':12, 'm6':24, 'M2':8, 'P5':13, 'P4':17, \
            'A4':1, 'M3':10, 'M-3':2, 'P-5':2, 'd5':3, 'd-5':1, 'm-6':1, \
            'M10':2, 'M9':4, 'P11':3, 'M-2':1, 'm-3':1, 'P-12':1 }

      # If voice crossing means negative intervals.
      expected_no_quality2grams = {2: { '1 -2 6':1, '1 1 2':2, '1 -3 6':1, \
            '1 +2 -3':1, '1 1 5':1, '1 -2 2':1, '1 1 4':2, '1 1 -2':1, \
            '1 -2 3':1, '2 1 3':2, '2 +2 1':1, '2 1 1':3, '2 -2 6':1, \
            '2 1 5':1, '3 +2 3':1, '3 1 2':2, '3 1 1':1, '3 -3 6':1, \
            '-3 -6 5':1, '3 +2 1':1, '-3 +2 -5':1, '3 1 4':6, '3 -3 5':1, \
            '3 1 6':2, '3 +5 -5':1, '3 -6 6':1, '3 -7 8':1, '-3 -3 3':1, \
            '3 -2 4':1, '3 +10 -12':1, '3 -4 6':1, '4 -3 5':1, '4 -2 5':1, \
            '4 1 3':3, '4 -2 4':3, '4 1 -5':1, '4 +2 3':2, '4 -3 3':1, \
            '4 1 5':1, '4 -2 3':1, '4 1 1':1, '4 1 2':1, '4 +2 1':2, \
            '4 -8 10':1, '4 +2 4':2, '4 -5 6':1, '5 -3 7':1, '-5 1 -6':1, '5 1 6':7, \
            '5 -2 5':1, '-5 -2 5':1, '5 -3 6':2, '5 -2 6':1, '5 1 3':1, '5 -8 10':1, \
            '5 +2 3':1, '6 -2 7':2, '6 +2 4':1, '6 +4 3':1, '6 +2 5':2, \
            '6 1 -3':1, '6 +4 4':3, '6 1 5':4, '6 -2 6':8, '6 +3 4':1, \
            '-6 -2 3':1, '6 +2 3':2, '6 +4 2':1, '6 +3 3':2, '6 1 9':1, \
            '6 +2 6':4, '6 -6 8':1, '6 -3 6':1, '6 -5 8':1, '7 -2 8':2, \
            '7 -5 10':1, '7 +4 4':1, '8 +2 7':1, '8 -2 10':1, '8 -2 9':1, \
            '8 +6 6':2, '8 +4 6':1, '9 +5 6':1, '9 1 8':2, '9 -2 10':1, \
            '9 -3 10':1, '10 1 9':2, '10 1 6':1, '10 1 11':3, '11 +7 3':1 }}

      # Verify the findings
      ngram_dict, keys = self.stats.get_ngram_dict(self.settings, False)
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(ngram_dict), len(expected_no_quality2grams) )
      self.assertEqual( ngram_dict, expected_no_quality2grams )

   #def test_La_Plus_des_Plus( self ):
      ## Title: "La Plus des Plus" by Josquin
      ## Format ABC
      ## Voices: ??
      ## Measures ??
      # NOTE: I can't finish this test until vis supports ABC files.

      ## Process the excerpt
      #filename = 'test_corpus/laPlusDesPlus.abc'
      #the_piece = converter.parse( filename )
      ## offset ??? is ???
      #higher_part = the_piece.parts[0].getElementsByOffset( 0.0, 12.9 )
      #lower_part = the_piece.parts[3].getElementsByOffset( 0.0, 12.9 )
      #analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      ## Prepare the findings
      #expected_compound_intervals = {}
      #expected_no_quality2grams = {}

      ## Verify the findings
      #self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      #self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      #self.assertEqual( len(self.stats.get_ngram_dict('compound', 2)), len(expected_no_quality2grams) )
      #self.assertEqual( self.stats.get_ngram_dict('compound', 2), expected_no_quality2grams )

   #def test_Ave_Maris_Stella( self ):
      # NOTE: This test is postponed to Milestone 2, because it unearted a
      # rather large problem. See Issue #15 for more information.
      ## Title: "Ave maris stella" by Josquin
      ## Format: **kern and MEI
      ## Voices: middle (indices 1 and 2)
      ## Measures: 104 to 126, incl.
      ##
      ## NB: This one should be good to test that the same results arise of the
      ## **kern and MEI formats.
      ##
      ## NB: This analyzes 3-grams and not 2-grams.

      ## Set to analyze 3-grams
      #self.settings.set_property( 'lookForTheseNs 2, 3' )
      ## NB: We should still look for 2-grams, just to ensure that doesn't affect
      ## how vis counts 3-grams. I guess we should try it both ways.

      ## Process the excerpt
      #filenameA = 'test_corpus/Jos2308.krn'
      #filenameB = 'test_corpus/Jos2308.mei'

      #the_pieceA = converter.parse( filenameA )
      ## offset 824.0 is m.104
      ## offset 1000.0 is m.126
      #higher_partA = the_pieceA.parts[1].getElementsByOffset( 824.0, 1000.0 )
      #lower_partA = the_pieceA.parts[2].getElementsByOffset( 824.0, 1000.0 )
      #analysis_time = vis_these_parts( [higher_partA,lower_partA], self.settings, self.stats )

      ##the_pieceB = converter.parse( filenameB )
      ### offset ??? is ???
      ##higher_partB = the_pieceA.parts[0].getElementsByOffset( 0.0, 12.9 )
      ##lower_partB = the_pieceA.parts[3].getElementsByOffset( 0.0, 12.9 )
      ##analysis_time += vis_these_parts( [higher_partB,lower_partB], self.settings, self.stats )

      #print( '--> analysis took ' + str(analysis_time[0]) + ' seconds' )

      ## Prepare the findings
      #expected_compound_intervals = { 'P1':2, 'M2':4, 'm3':5, 'P4':9, 'P5':11, \
         #'m6':6, 'P8':7, 'M7':2, 'm7':7, 'm10':2, 'm9':1, 'A4':1, 'M3':9, \
         #'M6':8 }
      #expected_no_quality3grams = {}

      #for thing in self.stats.get_compound_interval_summary_dict().iterkeys():
         #if thing in expected_compound_intervals:
            #if self.stats.get_compound_interval_summary_dict()[thing] != expected_compound_intervals[thing]:
               #print( 'for ' + thing + ', actual ' + str(self.stats.get_compound_interval_summary_dict()[thing]) + ' != expected ' + str(expected_compound_intervals[thing]) )
         #else:
            #print( 'actual ' + thing + ' isn\'t expected (there are ' + str(expected_compound_intervals[thing]) + ')' )

      #for thing in expected_compound_intervals.iterkeys():
         #if thing in self.stats.get_compound_interval_summary_dict():
            #if self.stats.get_compound_interval_summary_dict()[thing] != expected_compound_intervals[thing]:
               #print( 'for ' + thing + ', actual ' + str(self.stats.get_compound_interval_summary_dict()[thing]) + ' != expected ' + str(expected_compound_intervals[thing]) )
         #else:
            #print( 'expected ' + thing + ' isn\'t present' )

      ## Verify the findings
      #self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      #self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      ##self.assertEqual( len(self.stats._ngrams_dict[3]), len(expected_no_quality2grams) )
      ##self.assertEqual( self.stats._ngrams_dict[3], expected_no_quality2grams )
# End TestVisThesePartsLong ---------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( Test_Analysis_Engine_Integration_Long )
