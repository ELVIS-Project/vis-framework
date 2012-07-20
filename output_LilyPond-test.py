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

# Requirements from output_LilyPond.py
# music21
#from music21 import clef
#from music21 import meter
#from music21 import key
#from music21 import stream
#from music21 import instrument
#from music21 import metadata
#from music21 import layout
#from music21 import bar



#-------------------------------------------------------------------------------
class Test_Simple_Conversions( unittest.TestCase ):
   def test_octave_num_to_lily( self ):
      self.assertRaises( UnidentifiedObjectError, octave_num_to_lily, -10 )
      self.assertRaises( UnidentifiedObjectError, octave_num_to_lily, -1 )
      self.assertEqual( octave_num_to_lily( 0 ), ',,,' )
      self.assertEqual( octave_num_to_lily( 1 ), ',,' )
      self.assertEqual( octave_num_to_lily( 2 ), ',' )
      self.assertEqual( octave_num_to_lily( 3 ), '' )
      self.assertEqual( octave_num_to_lily( 4 ), "'" )
      self.assertEqual( octave_num_to_lily( 5 ), "''" )
      self.assertEqual( octave_num_to_lily( 6 ), "'''" )
      self.assertEqual( octave_num_to_lily( 7 ), "''''" )
      self.assertEqual( octave_num_to_lily( 8 ), "'''''" )
      self.assertEqual( octave_num_to_lily( 9 ), "''''''" )
      self.assertEqual( octave_num_to_lily( 10 ), "'''''''" )
      self.assertEqual( octave_num_to_lily( 11 ), "''''''''" )
      self.assertEqual( octave_num_to_lily( 12 ), "'''''''''" )
      self.assertRaises( UnidentifiedObjectError, octave_num_to_lily, 13 )
      self.assertRaises( UnidentifiedObjectError, octave_num_to_lily, 128 )
   
   def test_pitch_to_lily( self ):
      # Pitch with octave
      self.assertEqual( pitch_to_lily( pitch.Pitch( 'C4' ) ), "c'" )
      self.assertEqual( pitch_to_lily( pitch.Pitch( 'E#0' ) ), "eis,,," )
      # Note with octave
      self.assertEqual( pitch_to_lily( note.Note( 'F##3' ) ), "fisis" )
      # Note without octave
      self.assertEqual( pitch_to_lily( pitch.Pitch( 'B-6' ), False ), "bes" )
      # Pitch without octave
      self.assertEqual( pitch_to_lily( pitch.Pitch( 'F--11' ), False ), "feses" )
   
   def test_duration_to_lily( self ):
      # TODO: make sure you're testing all possible durations (hint: you're not)
      self.assertEqual( duration_to_lily( duration.Duration( 1.0 ) ), '4' )
      self.assertEqual( duration_to_lily( duration.Duration( 16.0 ) ), '\longa' )
      self.assertEqual( duration_to_lily( duration.Duration( 0.0625 ) ), '64' )
      self.assertEqual( duration_to_lily( duration.Duration( 3.0 ) ), '2.' )
      self.assertEqual( duration_to_lily( duration.Duration( 0.1875 ) ), '32.' )
      self.assertEqual( duration_to_lily( duration.Duration( 3.5 ) ), '2..' )
      self.assertEqual( duration_to_lily( duration.Duration( 3.75 ) ), '2...' )
      self.assertEqual( duration_to_lily( duration.Duration( 0.12109375 ) ), '64....' )
      # Same as above, but with known_tuplet==True... all results should be the same.
      self.assertEqual( duration_to_lily( duration.Duration( 1.0 ) ), '4', True )
      self.assertEqual( duration_to_lily( duration.Duration( 16.0 ) ), '\longa', True )
      self.assertEqual( duration_to_lily( duration.Duration( 0.0625 ) ), '64', True )
      self.assertEqual( duration_to_lily( duration.Duration( 3.0 ) ), '2.', True )
      self.assertEqual( duration_to_lily( duration.Duration( 0.1875 ) ), '32.', True )
      self.assertEqual( duration_to_lily( duration.Duration( 3.5 ) ), '2..', True )
      self.assertEqual( duration_to_lily( duration.Duration( 3.75 ) ), '2...', True )
      self.assertEqual( duration_to_lily( duration.Duration( 0.12109375 ) ), '64....', True )
      # This should be rounded to qL==8.0 ... but I don't know how to make a
      # single-component duration with this qL, so I can't run this test as it
      # gets rounded, only as it produces an error.
      #self.assertEqual( duration_to_lily( duration.Duration( 7.99609375 ) ), '\\breve' )
      self.assertRaises( UnidentifiedObjectError, duration_to_lily, duration.Duration( 7.99609375 ) )
      # These take multiple Note objects, and as such cannot be portrayed by
      # the output from a single call to duration_to_lily()
      self.assertRaises( UnidentifiedObjectError, duration_to_lily, duration.Duration( 16.1 ) )
      self.assertRaises( UnidentifiedObjectError, duration_to_lily, duration.Duration( 25.0 ) )
      self.assertRaises( UnidentifiedObjectError, duration_to_lily, duration.Duration( 0.01268128 ) )
      # This is a tuplet, so it should only work when I say I know I have one
      self.assertRaises( UnidentifiedObjectError, duration_to_lily, duration.Duration( 0.16666666 ) )
      self.assertEqual( duration_to_lily( duration.Duration( 0.16666666 ), True ), '16' )
   
   def test_note_to_lily( self ):
      self.assertEqual( note_to_lily( note.Note( 'C4', quarterLength=1.0 ) ), "c'4" )
      self.assertEqual( note_to_lily( note.Note( 'E#0', quarterLength=16.0 ) ), "eis,,,\longa" )
      self.assertEqual( note_to_lily( note.Note( 'F##3', quarterLength=0.0625 ) ), "fisis64" )
      self.assertEqual( note_to_lily( note.Note( 'F--11', quarterLength=3.75 ) ), "feses''''''''2..." )
      #self.assertRaises( UnidentifiedObjectError, note_to_lily, note.Note( 'C4', quarterLength=25.0 ) )
      self.assertRaises( UnidentifiedObjectError, note_to_lily, note.Note( 'C17', quarterLength=1.0 ) )
      self.assertEqual( note_to_lily( note.Rest( quarterLength=16.0 ) ), "r\longa" )
      self.assertEqual( note_to_lily( note.Rest( quarterLength=0.0625 ) ), "r64" )
      test_Note_1 = note.Note( 'C4', quarterLength=1.0 )
      test_Note_1.tie = tie.Tie( 'start' )
      self.assertEqual( note_to_lily( test_Note_1 ), "c'4~" )
      test_Note_1.lily_markup = '_\markup{ "example!" }'
      self.assertEqual( note_to_lily( test_Note_1 ), "c'4~_\markup{ \"example!\" }" )
      self.assertEqual( note_to_lily( note.Note( 'C4', quarterLength=7.99609375 ) ), "c'1~ c'2~ c'4~ c'8~ c'16~ c'32~ c'64...." )
   
   def test_barline_to_lily( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'regular' ) ), '\\bar "|"' )
      self.assertEqual( barline_to_lily( bar.Barline( 'dotted' ) ), '\\bar ":"' )
      self.assertEqual( barline_to_lily( bar.Barline( 'dashed' ) ), '\\bar "dashed"' )
      self.assertEqual( barline_to_lily( bar.Barline( 'heavy' ) ), '\\bar "|.|"' )
      self.assertEqual( barline_to_lily( bar.Barline( 'double' ) ), '\\bar "||"' )
      self.assertEqual( barline_to_lily( bar.Barline( 'final' ) ), '\\bar "|."' )
      self.assertEqual( barline_to_lily( bar.Barline( 'heavy-light' ) ), '\\bar ".|"' )
      self.assertEqual( barline_to_lily( bar.Barline( 'heavy-heavy' ) ), '\\bar ".|."' )
      self.assertEqual( barline_to_lily( bar.Barline( 'tick' ) ), '\\bar "\'"' )
      self.assertEqual( barline_to_lily( bar.Barline( 'short' ) ), '\\bar "\'"' )
      self.assertEqual( barline_to_lily( bar.Barline( 'none' ) ), '\\bar ""' )
   
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class Test_Process_Measure( unittest.TestCase ):
   def test_bwv77_bass_part( self ):
      bass_part = converter.parse( 'test_corpus/bwv77.mxl' ).parts[3]
      measure_1 = u'   \partial 4\n   \clef bass\n   \key b \minor\n   \\time 4/4\n   e4 |\n'
      measure_3 = u'   b4 a4 g4 fis4 |\n'
      measure_final = u'   g8 e8 fis4 b,4\n   \\bar "|." |\n'
      self.assertEqual( process_measure( bass_part[1] ), measure_1 )
      self.assertEqual( process_measure( bass_part[4] ), measure_3 )
   
   def test_ave_maris_stella( self ):
      # "ams" is "ave maris stella"... what were you thinking?
      ams = converter.parse( 'test_corpus/Jos2308.krn' )
      # First four measures, second highest part
      first_test = """   \clef treble
   \key f \major
   \\time 2/1
   r1 g'1 |
   d''1 r1 |
   g'1 d''1~ |
   d''2 c''2 bes'2 a'2 |
"""
      result = process_measure( ams[1][7] ) + process_measure( ams[1][8] ) + \
         process_measure( ams[1][9] ) + process_measure( ams[1][10] )
      self.assertEqual( result, first_test )
      # Measures 125-7, lowest part
      second_test = """   g\\breve~ |
   g\\breve \\bar "||" |
   R\\breve |
"""
      result = process_measure( ams[3][131] ) + process_measure( ams[3][132] ) + \
         process_measure( ams[3][133] )
      self.assertEqual( result, second_test )
      # Measure 107, second-lowest part (tuplets)
      third_test = "   \\times 2/3 { e'1 c'1 d'1 } |\n"
      #print( str(ams[2][113].duration.quarterLength) + ' andza ' + str(ams[2][113].barDuration.quarterLength) )
      result = process_measure( ams[2][113] )
      self.assertEqual( result, third_test )
   
   def test_modeless_key_signature( self ):
      meas = stream.Measure()
      meas.append( key.KeySignature( -3 ) )
      self.assertEqual( process_measure( meas ), '   \key ees \major\n   |\n' )
   
   def test_some_tuplets( self ):
      test_in1 = stream.Measure()
      test_in1.timeSignature = meter.TimeSignature( '4/4' )
      test_in1.append( note.Note('C4',quarterLength=0.16666))
      test_in1.append( note.Note('D4',quarterLength=0.16666))
      test_in1.append( note.Note('E4',quarterLength=0.16666))
      expect1 = """   \partial 8
   \\time 4/4
   \\times 2/3 { c'16 d'16 e'16 } |
"""
      self.assertEqual( process_measure( test_in1 ), expect1 )

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
   %% Soprano
   \set Staff.instrumentName = \markup{ "Soprano" }
   \set Staff.shortInstrumentName = \markup{ "Sop." }
   \partial 4
   \clef treble
   \key b \minor
   \\time 4/4
   e'8 fis'8 |
   g'4 a'4 b'4 a'4 |
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
   \clef treble
   \key f \major
   \\time 2/1
   g'1 d''1 |
   r1 g'1 |
   d''1 r1 |
}
"""
      self.assertEqual( actual, expected )
   # ------------------------------------------------------




#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
# "Main" Function
#-------------------------------------------------------------------------------
if __name__ == '__main__':
   print( "###############################################################################" )
   print( "## output_LilyPond Test Suite                                                ##" )
   print( "###############################################################################" )
   print( "" )
   # define test suites
   simple_conversions_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Simple_Conversions )
   process_measure_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Process_Measure )
   process_stream_part_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Process_Stream_Part )

   # Run test suites
   unittest.TextTestRunner( verbosity = 2 ).run( simple_conversions_suite )
   unittest.TextTestRunner( verbosity = 2 ).run( process_measure_suite )
   unittest.TextTestRunner( verbosity = 2 ).run( process_stream_part_suite )








