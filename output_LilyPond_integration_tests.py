#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         output_LilyPond-test.py
# Purpose:      Unit tests for output_LilyPond.py
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

# Confirmed Requirements:
import unittest
from output_LilyPond import *
from music21 import note, pitch, duration, converter, tie, key



#-------------------------------------------------------------------------------
class Test_Process_Measure( unittest.TestCase ):
   def test_bwv77_bass_part( self ):
      bass_part = converter.parse( 'test_corpus/bwv77.mxl' ).parts[3]
      measure_1 = u'\t\partial 4\n\t\clef bass\n\t\key b \minor\n\t\\time 4/4\n\te4 |\n'
      measure_3 = u'\tb4 a4 g4 fis4 |\n'
      measure_final = u'\tg8 e8 fis4 b,4\n\t\\bar "|." |\n'
      self.assertEqual( process_measure( bass_part[1] ), measure_1 )
      self.assertEqual( process_measure( bass_part[4] ), measure_3 )

   def test_ave_maris_stella( self ):
      # "ams" is "ave maris stella"... what were you thinking?
      ams = converter.parse( 'test_corpus/Jos2308.krn' )
      # First four measures, second highest part
      first_test = """\t\clef treble
\t\key f \major
\t\\time 2/1
\tr1 g'1 |
\td''1 r1 |
\tg'1 d''1~ |
\td''2 c''2 bes'2 a'2 |
"""
      result = process_measure( ams[1][7] ) + process_measure( ams[1][8] ) + \
         process_measure( ams[1][9] ) + process_measure( ams[1][10] )
      self.assertEqual( result, first_test )
      # Measures 125-7, lowest part
      second_test = """\tg\\breve~ |
\tg\\breve \\bar "||" |
\tR\\breve |
"""
      result = process_measure( ams[3][131] ) + process_measure( ams[3][132] ) + \
         process_measure( ams[3][133] )
      self.assertEqual( result, second_test )
      # Measure 107, second-lowest part (tuplets)
      third_test = "\t\\times 2/3 { e'1 c'1 d'1 } |\n"
      #print( str(ams[2][113].duration.quarterLength) + ' andza ' + str(ams[2][113].barDuration.quarterLength) )
      result = process_measure( ams[2][113] )
      self.assertEqual( result, third_test )

   def test_modeless_key_signature( self ):
      meas = stream.Measure()
      meas.append( key.KeySignature( -3 ) )
      self.assertEqual( process_measure( meas ), '\t\key ees \major\n\t|\n' )

   def test_some_tuplets_1( self ):
      # Complete measure starts with tuplets, filled with rests
      test_in1 = stream.Measure()
      test_in1.timeSignature = meter.TimeSignature( '4/4' )
      test_in1.append( note.Note('C4',quarterLength=0.16666))
      test_in1.append( note.Note('D4',quarterLength=0.16666))
      test_in1.append( note.Note('E4',quarterLength=0.16666))
      test_in1.append( note.Rest( quarterLength=0.5 ) )
      test_in1.append( note.Rest( quarterLength=1.0 ) )
      test_in1.append( note.Rest( quarterLength=2.0 ) )
      expect1 = "\t\\time 4/4\n\t\\times 2/3 { c'16 d'16 e'16 } r8 r4 r2 |\n"
      self.assertEqual( process_measure( test_in1 ), expect1 )

   #def test_some_tuplets_2( self ):
      ## Incomplete measure starts with tuplets
      ## TODO: currently this fails because the duration of the three triplets is
      ## 0.49999 and that's not equal to the 0.5 qL it should have. This is a
      ## problem in duration_to_lily()
      #test_in1 = stream.Measure()
      #test_in1.timeSignature = meter.TimeSignature( '4/4' )
      #test_in1.append( note.Note('C4',quarterLength=0.16666))
      #test_in1.append( note.Note('D4',quarterLength=0.16666))
      #test_in1.append( note.Note('E4',quarterLength=0.16666))
      #expect1 = """\t\partial 8
#\t\\time 4/4
#\t\\times 2/3 { c'16 d'16 e'16 } |
#"""
      #self.assertEqual( process_measure( test_in1 ), expect1 )



#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class Test_Process_Stream_Part( unittest.TestCase ):
   # NOTE: We have to pull a bit of trickery here, because there is some
   # randomness involved in part names.
   def test_first_measures_of_bach( self ):
      # first two measures of soprano part
      the_settings = LilyPond_Settings()
      the_score = converter.parse( 'test_corpus/bwv77.mxl' )
      actual = process_stream( the_score[1][:3], the_settings )
      actual = actual[8:] # remove the randomized part name
      expected = """ =
{
\t%% Soprano
\t\set Staff.instrumentName = \markup{ "Soprano" }
\t\set Staff.shortInstrumentName = \markup{ "Sop." }
\t\partial 4
\t\clef treble
\t\key b \minor
\t\\time 4/4
\te'8 fis'8 |
\tg'4 a'4 b'4 a'4 |
}
"""
      self.assertEqual( actual, expected )
   # ------------------------------------------------------

   def test_first_measures_of_Josquin( self ):
      # first three measures of highest part
      the_settings = LilyPond_Settings()
      the_score = converter.parse( 'test_corpus/Jos2308.krn' )
      actual = process_stream( the_score[0][:10], the_settings )
      actual = actual[8:] # remove the randomized part name
      expected = """ =
{
\t\clef treble
\t\key f \major
\t\\time 2/1
\tg'1 d''1 |
\tr1 g'1 |
\td''1 r1 |
}
"""
      self.assertEqual( actual, expected )
   # ------------------------------------------------------




#-------------------------------------------------------------------------------



# Define test suites
process_measure_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Process_Measure )
process_stream_part_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Process_Stream_Part )
