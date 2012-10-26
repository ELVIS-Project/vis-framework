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
from problems import NonsensicalInputWarning
from music21 import converter
from analytic_engine import vis_these_parts



#-------------------------------------------------------------------------------
class Test_Analysis_Engine_Integration_Short( unittest.TestCase ):
   # vis_these_parts( theseParts, theSettings, theStatistics )
   #
   # This test suite is just excerpts of pieces selected from the works
   # available to the ELVIS project. I'm only testing small portions of works
   # so that it's possible to manually count the statistics, ensuring they
   # match my expectations of how the software should work. I'm using a
   # variety of pieces to ensure the assumptions hold true over a relatively
   # complex set of pieces.

   def setUp( self ):
      self.stats = Vertical_Interval_Statistics()
      self.settings = VIS_Settings()

   def test_intervals_not_counted_multiple_times( self ):
      # BWV 7.7 (a chorale)
      # MusicXML
      # Soprano and Bass
      # Measures 1 through 4

      # Process the excerpt
      filename = 'test_corpus/bwv77.mxl'
      the_piece = converter.parse( filename )
      self.settings.set_property( 'lookForTheseNs 2,3,4' )
      # offset 13.0 is the fourth measure
      higher_part = the_piece.parts[0].getElementsByOffset( 0.0, 12.9 )
      lower_part = the_piece.parts[3].getElementsByOffset( 0.0, 12.9 )
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      # Prepare the findings
      # NB: these are the same as test_theFirst()
      expected_compound_intervals = { 'P8':2, 'M9':1, 'M10':3, 'P12':4, \
            'm13':1, 'm17':1, 'M13':1, 'm10':4 }

      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )


   def test_theFirst( self ):
      # BWV 7.7 (a chorale)
      # MusicXML
      # Soprano and Bass
      # Measures 1 through 4

      # Process the excerpt
      filename = 'test_corpus/bwv77.mxl'
      the_piece = converter.parse( filename )
      # offset 13.0 is the fourth measure
      higher_part = the_piece.parts[0].getElementsByOffset( 0.0, 12.9 )
      lower_part = the_piece.parts[3].getElementsByOffset( 0.0, 12.9 )
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      # Prepare the findings
      expected_compound_intervals = { 'P8':2, 'M9':1, 'M10':3, 'P12':4, \
            'm13':1, 'm17':1, 'M13':1, 'm10':4 }
      expected_no_quality2grams = {2: { '8 1 9':1, '10 -2 12':1, '10 -4 12':1, \
            '13 -2 17':1, '17 +6 12':1, '9 1 10':1, '12 +4 10':1, '12 -2 13':1, \
            '12 -3 13':1, '13 +2 12':1, '12 +4 8':1, '8 -4 10':1, \
            '10 +4 10':1, '10 -2 10':3 }}

      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(self.settings)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(self.settings), expected_no_quality2grams )

   def test_theSecond( self ):
      # Kyrie from "Missa Pro Defunctis" by Palestrina
      # **kern
      # Spines 4 and 3 (the highest two of five staves)
      # Measures 1 through 5

      # Process the excerpt
      filename = 'test_corpus/Kyrie.krn'
      the_piece = converter.parse( filename )
      # offset 40.0 is the sixth measure
      higher_part = the_piece.parts[0].getElementsByOffset( 0.0, 39.9 )
      lower_part = the_piece.parts[1].getElementsByOffset( 0.0, 39.9 )
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      # Prepare the findings
      expected_compound_intervals = { 'm3':3, 'M3':2, 'P4':1, 'd5':2, 'm6':2, \
            'M6':2, 'M2':1, 'P5':1 }
      expected_no_quality2grams = {2: { '3 +2 3':2, '3 1 4':1, '4 -2 5':1, '5 -2 6':2, \
            '6 -2 6':2, '6 +4 3':1, '3 1 2':1, '2 -2 3':1, '3 -2 5':1, '6 1 5':1 }}

      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(self.settings)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(self.settings), expected_no_quality2grams )

   def test_theThird( self ):
      # Monteverdi's "Cruda amarilli" (a madrigal)
      # MusicXML
      # Alto and Quinto
      # Measures 6 through end of 11
      ## NB: Kind of a regular test, just that it doesn't start at the
      ## beginning. Plus, it ends on a unison and before that is a rest.

      # Process the excerpt
      filename = 'test_corpus/madrigal51.mxl'
      the_piece = converter.parse( filename )
      # offset 20.0 is the 6th measure
      # offset 44.0 is the 12th measure
      higher_part = the_piece.parts[1].getElementsByOffset( 20.0, 43.9 )
      lower_part = the_piece.parts[3].getElementsByOffset( 20.0, 43.9 )
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats.get_compound_interval_summary_dict() )
      #pprint.pprint( self.stats.get_formatted_ngram_dict('compound', 2) )

      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'M6':2, 'P4':3, 'M3':2, 'm3':2 }
      expected_no_quality2grams = {2: { '8 +2 6':1, '4 1 3':1, '4 -3 3':1, \
            '6 +2 4':1, '3 1 4':2, '4 +3 3':1, '3 +2 3':1, '3 -5 6':1}}#, \
            #'1 +2 2':1, '4 -2 3':1, '2 -2 1':1, '2 +2 1':1, '5 +3 3':1, \
            #'2 +2 3':1, '3 -2 2':1, '1 -2 2':1, '1 -2 5':1 }

      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(self.settings)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(self.settings), expected_no_quality2grams )

   def test_theSixthA( self ):
      # Two targeted testing excerpts.
      # A music21 Original
      # Just 2 arbitrary parts
      ## NB: This is designed to test an error that used to happen when one
      ## part has alternating notes and rests in a time when the other part has
      ## a note followed by a bunch of rests.

      from test_corpus.test_theSixth import the_first_piece
      filename = "filename"
      higher_part = the_first_piece.parts[0]
      lower_part = the_first_piece.parts[1]
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats.get_compound_interval_summary_dict() )
      #pprint.pprint( self.stats.get_formatted_ngram_dict('compound', 2) )

      ## Prepare the findings
      expected_compound_intervals = { 'P11':1, 'm14':1 }
      #expected_no_quality2grams = {}

      ## Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertRaises(NonsensicalInputWarning, self.stats.get_formatted_ngram_dict, self.settings)

   def test_theSixthB( self ):
      # Two targeted testing excerpts.
      # A music21 Original
      # Just 2 arbitrary parts
      ## NB: This is designed to test an error that used to happen when one
      ## part has alternating notes and rests in a time when the other part has
      ## a note followed by a bunch of rests. Unlike "SixthA," this test has a
      ## quantization quirk from the MIDI file that inspired this test, which
      ## is what caused the failure in the first place.
      ##
      ## The problem is this: even though one part has a rest, the rest doesn't
      ## start on one of the offsets we're checking, so the program thinks the
      ## part still has a note sounding.

      from test_corpus.test_theSixth import the_second_piece
      filename = "filename"
      higher_part = the_second_piece.parts[0]
      lower_part = the_second_piece.parts[1]
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats.get_compound_interval_summary_dict() )
      #pprint.pprint( self.stats.get_formatted_ngram_dict('compound', 2) )

      ## Prepare the findings
      expected_compound_intervals = { 'P11':1, 'm14':1 }
      expected_no_quality2grams = {}

      ## Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertRaises(NonsensicalInputWarning,self.stats.get_formatted_ngram_dict, self.settings)

   def test_theSixthC( self ):
      # Two targeted testing excerpts.
      # A music21 Original
      # Just 2 arbitrary parts
      ## NB: This test reverses theSixthB, so the bottom voice woudl cause the
      ## problem caused by the top voice in the previous test.

      from test_corpus.test_theSixth import the_third_piece
      filename = "filename"
      higher_part = the_third_piece.parts[0]
      lower_part = the_third_piece.parts[1]
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats.get_compound_interval_summary_dict() )
      #pprint.pprint( self.stats.get_formatted_ngram_dict('compound', 2) )

      ## Prepare the findings
      expected_compound_intervals = { 'P12':1, 'M9':1 }
      expected_no_quality2grams = {}

      ## Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertRaises(NonsensicalInputWarning,self.stats.get_formatted_ngram_dict, self.settings)

   def test_theSeventh( self ):
      # Joseph Haydn's String Quartet, Op.76/4, Movement 1
      # MIDI
      # Violin I and 'Cello
      # Measures 113 through 120
      ## NB:

      ## Process the excerpt
      filename = 'test_corpus/sqOp76-4-i.midi'
      the_piece = converter.parse( filename )
      # measure 113 is offset 448.0
      # measure 120 is offset 480.0
      higher_part = the_piece.parts[0].getElementsByOffset( 448.0, 479.9 )
      lower_part = the_piece.parts[3].getElementsByOffset( 448.0, 479.9 )
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats.get_compound_interval_summary_dict() )
      ##pprint.pprint( self.stats.get_formatted_ngram_dict('compound', 2) )

      ## Prepare the findings
      expected_compound_intervals = { 'P15':7, 'A11':1, 'M13':2, \
            'd14':5, 'A18':1, 'd18':2, 'A12':1, 'd19':1, 'A16':4, 'm13':1, \
            'm21':1, 'P22':4, 'm24':3, 'P26':5, 'm28':1, 'M24':1, 'M17':1, }
      expected_no_quality2grams = {2: { '16 +2 15':3, '16 -4 18':1, '15 +1 14':3, \
            '15 -2 16':2, '15 +2 12':1, '15 -3 18':1, '14 +3 11':1, \
            '14 -1 15':2, '14 -1 13':2, '11 -3 14':1, '18 +1 18':1, \
            '18 +3 15':1, '18 -3 19':1, '12 -2 15':1, '19 +2 16':1, \
            '13 +1 14':1, '13 +2 13':1, '21 -1 22':1, '22 -2 24':2, \
            '22 +4 17':1, '24 -2 26':3, '24 1 22':1, '26 -2 28':1, \
            '26 1 24':1, '28 1 26':1, '13 -9 21':1 }}

      ## Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(self.settings)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(self.settings), expected_no_quality2grams )

   def test_theFourth( self ):
      # Monteverdi's "Cruda amarilli" (a madrigal)
      # MusicXML
      # Alto and Quinto
      # Measures 6 through 16
      ## NB: Starts out the same as the previous test, but this excerpt is a
      ## little longer and ends with some voice crossing.

      # Process the excerpt
      filename = 'test_corpus/madrigal51.mxl'
      the_piece = converter.parse( filename )
      # offset 20.0 is the 6th measure
      # offset 64.0 is the 15th measure
      higher_part = the_piece.parts[1].getElementsByOffset( 20.0, 63.9 )
      lower_part = the_piece.parts[3].getElementsByOffset( 20.0, 63.9 )
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats.get_compound_interval_summary_dict() )
      #pprint.pprint( self.stats.get_formatted_ngram_dict('compound', 2) )

      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'M6':2, 'P4':3, 'M3':2, 'm3':3, \
            'P1':2, 'M-2':1, 'm-3':2, 'P-4':1, 'P5':1 }
      expected_no_quality2grams = {2: { '8 +2 6':1, '6 +2 4':1, '4 1 3':1, '3 1 4':2, \
            '4 -3 3':1, '4 +3 3':1, '3 +2 3':1, '3 -5 6':1, '1 +2 -2':1, \
            '-2 +2 -3':1, '-4 -2 -3':1, '-3 -3 1':1, '1 -2 5':1, '5 +3 3':1, \
            '-3 1 -4':1 }}
      #expected_quality2Grams = { 'P8 +m2 M6':1, 'M6 +M2 P4':1, 'P4 P1 M3':1, \
            #'M3 P1 P4':1, 'P4 -m3 m3':1, 'm3 P1 P4':1, 'P4 +m3 M3':1, \
            #'M3 +M2 m3':1, 'm3 -P5 M6':1, 'P1 +M2 M-2':1, 'M-2 +m2 m-3':1, \
            #'P-4 -M2 m-3':1, 'm-3 -m3 P1':1, 'P1 -M2 P5':1, 'P5 +M3 m3':1, \
            #'m-3 P1 P-4':1 }

      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(self.settings)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(self.settings), expected_no_quality2grams )
      # TODO: these tests would currently require a second analysis; I'll
      # re-enable them later when that isn't true.
      #self.assertEqual( len(self.stats._compound_quality_ngrams_dict[2]), len(expected_quality2Grams) )
      #self.assertEqual( self.stats._compound_quality_ngrams_dict[2], expected_quality2Grams )

   def test_theFifth( self ):
      # Monteverdi's "Cruda amarilli" (a madrigal)
      # MusicXML
      # Alto and Tenor
      # Measures 1 through 16
      ## NB: These parts cross many times.

      # Process the excerpt
      filename = 'test_corpus/madrigal51.mxl'
      the_piece = converter.parse( filename )
      # offset 0.0 is the 6th measure
      # offset 64.0 is the 15th measure
      higher_part = the_piece.parts[1].getElementsByOffset( 0.0, 63.9 )
      lower_part = the_piece.parts[2].getElementsByOffset( 0.0, 63.9 )
      vis_these_parts( [higher_part,lower_part], self.settings, self.stats, filename )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      # Prepare the findings
      expected_compound_intervals = { 'M6':5, 'M10':2, 'M9':2, 'P8':4, 'm6':1, \
            'P5':2, 'P4':2, 'M3':1, 'm-3':1, 'm-2':1, 'M2':2, 'm3':2 }
      #expected_quality2Grams = { 'M6 -P5 M10':2, 'M10 P1 M9':2, 'M9 P1 P8':2, \
            #'P8 +M2 M6':2, 'M6 -M2 P8':2, 'M6 +M2 m6':1, 'm6 -M3 P5':1, \
            #'P5 +M2 P4':1, 'P4 +M2 P4':1, 'P4 -M2 M6':1, 'P8 +P5 M3':1, \
            #'m-3 -M2 m-2':1, 'm-2 -m3 M2':1, 'M2 -m3 m3':1, 'm3 +m2 M2':1, \
            #'M2 -m2 m3':1, 'm3 +m2 P5':1 }
      expected_no_quality2grams = {2: { '6 -5 10':2, '10 1 9':2, '9 1 8':2, '8 +2 6':2, \
            '6 -2 8':2, '6 +2 6':1, '6 -3 5':1, '5 +2 4':1, '4 +2 4':1, \
            '4 -2 6':1, '8 +5 3':1, '-3 -2 -2':1, '-2 -3 2':1, '2 -3 3':1, \
            '3 +2 2':1, '2 -2 3':1, '3 +2 5':1 }}

      # Verify the findings
      self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      self.assertEqual( len(self.stats.get_formatted_ngram_dict(self.settings)), len(expected_no_quality2grams) )
      self.assertEqual( self.stats.get_formatted_ngram_dict(self.settings), expected_no_quality2grams )
      # TODO: these tests would currently require a second analysis; I'll
      # re-enable them later when that isn't true.
      #self.assertEqual( len(self.stats._compound_quality_ngrams_dict[2]), len(expected_quality2Grams) )
      #self.assertEqual( self.stats._compound_quality_ngrams_dict[2], expected_quality2Grams )

   #def test_triplet_bugA( self ):
      ## A targeted testing excerpt.
      ## A music21 Original
      ## Just an arbitrary parts
      ### NB: This tests a possible bug in the Jos2308 longer excerpt, below. But
      ### this test is crafted specifically to have only the suspected problem
      ### area.

      #from test_corpus.test_triplet_bug import triplet_test_piece
      #higher_part = triplet_test_piece.parts[0]
      #lower_part = triplet_test_piece.parts[1]
      #analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      ##print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      ##pprint.pprint( self.stats.get_compound_interval_summary_dict() )
      ##pprint.pprint( self.stats.get_formatted_ngram_dict('compound', 2) )

      ### Prepare the findings
      #expected_compound_intervals = { 'P8':3, 'm10':1, 'm9':1, 'M7':1, 'P5':1, \
         #'P4':2, 'P-15':1, 'm3':2, 'M2':1, 'A4':1, 'M3':1 }
      #expected_no_quality2grams = {}

      ### Verify the findings
      ##self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      #self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      ##self.assertEqual( len(self.stats.get_formatted_ngram_dict('compound', 2)), len(expected_no_quality2grams) )
      #self.assertEqual( self.stats.get_formatted_ngram_dict('compound', 2), expected_no_quality2grams )

   #def test_triplet_bugB( self ):
      ## A targeted testing excerpt.
      ## A music21 Original
      ## Just an arbitrary parts
      ### NB: This test tries to replicate the previous test, but without the
      ### triplet. Instead, notes are "hidden" in non-triplet (ie. "simple sub-
      ### division") offsets that are, like the triplet offsets, not being
      ### counted directly.
      ###
      ### I started this test as a way to help determine whether using the
      ### Decimal class might solve my problem.

      #from test_corpus.test_triplet_bug import simple_test_piece
      #higher_part = simple_test_piece.parts[0]
      #lower_part = simple_test_piece.parts[1]
      #analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      ##print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      ##pprint.pprint( self.stats.get_compound_interval_summary_dict() )
      ##pprint.pprint( self.stats.get_formatted_ngram_dict('compound', 2) )

      ### Prepare the findings
      #expected_compound_intervals = { 'P8':3, 'm10':1, 'm9':1, 'M7':1, 'P5':1, \
         #'P4':1, 'P-15':1, 'm3':1, 'M2':1, 'M3':2, 'A4':1 }
      #expected_no_quality2grams = {}

      ### Verify the findings
      ##self.assertEqual( len(self.stats.get_compound_interval_summary_dict()), len(expected_compound_intervals) )
      #self.assertEqual( self.stats.get_compound_interval_summary_dict(), expected_compound_intervals )
      ##self.assertEqual( len(self.stats.get_formatted_ngram_dict('compound', 2)), len(expected_no_quality2grams) )
      #self.assertEqual( self.stats.get_formatted_ngram_dict('compound', 2), expected_no_quality2grams )

# NOTE: compare NoQuality 2-gram dictionaries
#for thing in self.stats.get_formatted_ngram_dict('compound', 2).iterkeys():
   #if thing in expected_no_quality2grams:
      #if self.stats.get_formatted_ngram_dict('compound', 2)[thing] != expected_no_quality2grams[thing]:
         #print( 'for ' + thing + ', actual ' + str(self.stats.get_formatted_ngram_dict('compound', 2)[thing]) + ' != expected ' + str(expected_no_quality2grams[thing]) )
   #else:
      #print( 'actual ' + thing + ' isn\'t expected (there are ' + str(self.stats.get_formatted_ngram_dict('compound', 2)[thing]) + ')' )

#for thing in expected_no_quality2grams.iterkeys():
   #if thing in self.stats.get_formatted_ngram_dict('compound', 2):
      #if self.stats.get_formatted_ngram_dict('compound', 2)[thing] != expected_no_quality2grams[thing]:
         #print( 'for ' + thing + ', actual ' + str(self.stats.get_formatted_ngram_dict('compound', 2)[thing]) + ' != expected ' + str(expected_no_quality2grams[thing]) )
   #else:
      #print( 'expected ' + thing + ' isn\'t present' )

# NOTE: compare interval dictionaries
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

# NOTE: compare 2-gram Quality dictionaries
#for thing in self.stats._compound_quality_ngrams_dict[2].iterkeys():
   #if thing in expected_quality2Grams:
      #if self.stats._compound_quality_ngrams_dict[2][thing] != expected_quality2Grams[thing]:
         #print( 'for ' + thing + ', actual ' + str(self.stats._compound_quality_ngrams_dict[2][thing]) + ' != expected ' + str(expected_quality2Grams[thing]) )
   #else:
      #print( 'actual ' + thing + ' isn\'t expected (there are ' + str(self.stats._compound_quality_ngrams_dict[2][thing]) + ')' )

#for thing in expected_quality2Grams.iterkeys():
   #if thing in self.stats._compound_quality_ngrams_dict[2]:
      #if self.stats._compound_quality_ngrams_dict[2][thing] != expected_quality2Grams[thing]:
         #print( 'for ' + thing + ', actual ' + str(self.stats._compound_quality_ngrams_dict[2][thing]) + ' != expected ' + str(expected_quality2Grams[thing]) )
   #else:
      #print( 'expected ' + thing + ' isn\'t present' )

# End TestVisTheseParts -------------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( Test_Analysis_Engine_Integration_Short )
