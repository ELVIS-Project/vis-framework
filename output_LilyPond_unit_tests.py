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
class Test_Octave_Num_to_Lily( unittest.TestCase ):
   def test_octave_num_to_lily_1( self ):
      self.assertRaises( UnidentifiedObjectError, octave_num_to_lily, -10 )

   def test_octave_num_to_lily_2( self ):
      self.assertRaises( UnidentifiedObjectError, octave_num_to_lily, -1 )

   def test_octave_num_to_lily_3( self ):
      self.assertEqual( octave_num_to_lily( 0 ), ',,,' )

   def test_octave_num_to_lily_4( self ):
      self.assertEqual( octave_num_to_lily( 1 ), ',,' )

   def test_octave_num_to_lily_5( self ):
      self.assertEqual( octave_num_to_lily( 2 ), ',' )

   def test_octave_num_to_lily_6( self ):
      self.assertEqual( octave_num_to_lily( 3 ), '' )

   def test_octave_num_to_lily_7( self ):
      self.assertEqual( octave_num_to_lily( 4 ), "'" )

   def test_octave_num_to_lily_8( self ):
      self.assertEqual( octave_num_to_lily( 5 ), "''" )

   def test_octave_num_to_lily_9( self ):
      self.assertEqual( octave_num_to_lily( 6 ), "'''" )

   def test_octave_num_to_lily_10( self ):
      self.assertEqual( octave_num_to_lily( 7 ), "''''" )

   def test_octave_num_to_lily_11( self ):
      self.assertEqual( octave_num_to_lily( 8 ), "'''''" )

   def test_octave_num_to_lily_12( self ):
      self.assertEqual( octave_num_to_lily( 9 ), "''''''" )

   def test_octave_num_to_lily_13( self ):
      self.assertEqual( octave_num_to_lily( 10 ), "'''''''" )

   def test_octave_num_to_lily_14( self ):
      self.assertEqual( octave_num_to_lily( 11 ), "''''''''" )

   def test_octave_num_to_lily_15( self ):
      self.assertEqual( octave_num_to_lily( 12 ), "'''''''''" )

   def test_octave_num_to_lily_16( self ):
      self.assertRaises( UnidentifiedObjectError, octave_num_to_lily, 13 )

   def test_octave_num_to_lily_17( self ):
      self.assertRaises( UnidentifiedObjectError, octave_num_to_lily, 128 )



#-------------------------------------------------------------------------------
class Test_Pitch_to_Lily( unittest.TestCase ):
   def test_pitch_to_lily_1( self ):
      # Pitch with octave
      self.assertEqual( pitch_to_lily( pitch.Pitch( 'C4' ) ), "c'" )

   def test_pitch_to_lily_2( self ):
      # Pitch with octave
      self.assertEqual( pitch_to_lily( pitch.Pitch( 'E#0' ) ), "eis,,," )

   def test_pitch_to_lily_3( self ):
      # Note with octave
      self.assertEqual( pitch_to_lily( note.Note( 'F##3' ) ), "fisis" )

   def test_pitch_to_lily_4( self ):
      # Note without octave
      self.assertEqual( pitch_to_lily( pitch.Pitch( 'B-6' ), False ), "bes" )

   def test_pitch_to_lily_5( self ):
      # Pitch without octave
      self.assertEqual( pitch_to_lily( pitch.Pitch( 'F--11' ), False ), "feses" )



#-------------------------------------------------------------------------------
class Test_Duration_to_Lily( unittest.TestCase ):
   def test_duration_to_lily_1( self ):
      # Simple things
      self.assertEqual( duration_to_lily( duration.Duration( 1.0 ) ), '4' )

   def test_duration_to_lily_2( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 16.0 ) ), '\longa' )

   def test_duration_to_lily_3( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 0.0625 ) ), '64' )

   def test_duration_to_lily_4( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 3.0 ) ), '2.' )

   def test_duration_to_lily_5( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 0.1875 ) ), '32.' )

   def test_duration_to_lily_6( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 3.5 ) ), '2..' )

   def test_duration_to_lily_7( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 3.75 ) ), '2...' )

   def test_duration_to_lily_8( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 0.12109375 ) ), '64....' )

   def test_duration_to_lily_9( self ):
      # Same as above, but with known_tuplet==True... all results should be the same.
      self.assertEqual( duration_to_lily( duration.Duration( 1.0 ) ), '4', True )

   def test_duration_to_lily_10( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 16.0 ) ), '\longa', True )

   def test_duration_to_lily_11( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 0.0625 ) ), '64', True )

   def test_duration_to_lily_12( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 3.0 ) ), '2.', True )

   def test_duration_to_lily_13( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 0.1875 ) ), '32.', True )

   def test_duration_to_lily_14( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 3.5 ) ), '2..', True )

   def test_duration_to_lily_15( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 3.75 ) ), '2...', True )

   def test_duration_to_lily_16( self ):
      self.assertEqual( duration_to_lily( duration.Duration( 0.12109375 ) ), '64....', True )

   def test_duration_to_lily_17( self ):
      # This should be rounded to qL==8.0 ... but I don't know how to make a
      # single-component duration with this qL, so I can't run this test as it
      # gets rounded, only as it produces an error.
      #self.assertEqual( duration_to_lily( duration.Duration( 7.99609375 ) ), '\\breve' )
      self.assertRaises( ImpossibleToProcessError, duration_to_lily, duration.Duration( 7.99609375 ) )

   def test_duration_to_lily_18( self ):
      # These take multiple Note objects, and as such cannot be portrayed by
      # the output from a single call to duration_to_lily()
      self.assertRaises( ImpossibleToProcessError, duration_to_lily, duration.Duration( 16.1 ) )

   def test_duration_to_lily_19( self ):
      self.assertRaises( ImpossibleToProcessError, duration_to_lily, duration.Duration( 25.0 ) )

   def test_duration_to_lily_20( self ):
      self.assertRaises( ImpossibleToProcessError, duration_to_lily, duration.Duration( 0.01268128 ) )

   def test_duration_to_lily_21( self ):
      # tuplet component--shouldn't work
      self.assertRaises( ImpossibleToProcessError, duration_to_lily, duration.Duration( 0.16666666 ) )

   def test_duration_to_lily_22( self ):
      # tuplet component--should work
      self.assertEqual( duration_to_lily( duration.Duration( 0.16666666 ), True ), '16' )
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class Test_Note_to_Lily( unittest.TestCase ):
   def test_note_to_lily_1( self ):
      self.assertEqual( note_to_lily( note.Note( 'C4', quarterLength=1.0 ) ), "c'4" )

   def test_note_to_lily_2( self ):
      self.assertEqual( note_to_lily( note.Note( 'E#0', quarterLength=16.0 ) ), "eis,,,\longa" )

   def test_note_to_lily_3( self ):
      self.assertEqual( note_to_lily( note.Note( 'F##3', quarterLength=0.0625 ) ), "fisis64" )

   def test_note_to_lily_4( self ):
      self.assertEqual( note_to_lily( note.Note( 'F--11', quarterLength=3.75 ) ), "feses''''''''2..." )

   def test_note_to_lily_5( self ):
      #self.assertRaises( UnidentifiedObjectError, note_to_lily, note.Note( 'C4', quarterLength=25.0 ) )
      self.assertRaises( UnidentifiedObjectError, note_to_lily, note.Note( 'C17', quarterLength=1.0 ) )

   def test_note_to_lily_6( self ):
      self.assertEqual( note_to_lily( note.Rest( quarterLength=16.0 ) ), "r\longa" )

   def test_note_to_lily_7( self ):
      self.assertEqual( note_to_lily( note.Rest( quarterLength=0.0625 ) ), "r64" )

   def test_note_to_lily_8( self ):
      test_Note_1 = note.Note( 'C4', quarterLength=1.0 )
      test_Note_1.tie = tie.Tie( 'start' )
      self.assertEqual( note_to_lily( test_Note_1 ), "c'4~" )

   def test_note_to_lily_9( self ):
      test_Note_1 = note.Note( 'C4', quarterLength=1.0 )
      test_Note_1.tie = tie.Tie( 'start' )
      test_Note_1.lily_markup = '_\markup{ "example!" }'
      self.assertEqual( note_to_lily( test_Note_1 ), "c'4~_\markup{ \"example!\" }" )

   def test_note_to_lily_11( self ):
      self.assertEqual( note_to_lily( note.Note( 'C4', quarterLength=7.99609375 ) ), "c'1~ c'2~ c'4~ c'8~ c'16~ c'32~ c'64...." )



#-------------------------------------------------------------------------------
class Test_Barline_to_Lily( unittest.TestCase ):
   def test_barline_to_lily_1( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'regular' ) ), '\\bar "|"' )

   def test_barline_to_lily_2( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'dotted' ) ), '\\bar ":"' )

   def test_barline_to_lily_3( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'dashed' ) ), '\\bar "dashed"' )

   def test_barline_to_lily_4( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'heavy' ) ), '\\bar "|.|"' )

   def test_barline_to_lily_5( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'double' ) ), '\\bar "||"' )

   def test_barline_to_lily_6( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'final' ) ), '\\bar "|."' )

   def test_barline_to_lily_7( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'heavy-light' ) ), '\\bar ".|"' )

   def test_barline_to_lily_8( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'heavy-heavy' ) ), '\\bar ".|."' )

   def test_barline_to_lily_9( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'tick' ) ), '\\bar "\'"' )

   def test_barline_to_lily_10( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'short' ) ), '\\bar "\'"' )

   def test_barline_to_lily_11( self ):
      self.assertEqual( barline_to_lily( bar.Barline( 'none' ) ), '\\bar ""' )

#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class Test_Detect_LilyPond( unittest.TestCase ):
   # detect_lilypond() -------------------------------------
   def test_for_path( self ):
      # NB: You have to write in your path and version!
      my_path = '/usr/bin/lilypond'
      my_version = '2.16.0'
      res = detect_lilypond()
      self.assertEqual( res[0], my_path )
      self.assertEqual( res[1], my_version )

   # make_lily_version_numbers() ---------------------------
   def test_make_lily_version_numbers_1( self ):
      self.assertEqual( make_lily_version_numbers( '2.14.0' ), (2,14,0) )

   def test_make_lily_version_numbers_2( self ):
      self.assertEqual( make_lily_version_numbers( '2.14.2' ), (2,14,2) )

   def test_make_lily_version_numbers_3( self ):
      self.assertEqual( make_lily_version_numbers( '2.16.0' ), (2,16,0) )

   def test_make_lily_version_numbers_4( self ):
      self.assertEqual( make_lily_version_numbers( '2.15.31' ), (2,15,31) )

   def test_make_lily_version_numbers_5( self ):
      self.assertEqual( make_lily_version_numbers( '218901289304.1123412344.12897795' ), (218901289304,1123412344,12897795) )

   def test_make_lily_version_numbers_6( self ):
      self.assertRaises( ValueError, make_lily_version_numbers, '..' )


#-------------------------------------------------------------------------------



# Define test suites
detect_lilypond_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Detect_LilyPond )
t_o_n_t_l = unittest.TestLoader().loadTestsFromTestCase( Test_Octave_Num_to_Lily )
t_p_t_l = unittest.TestLoader().loadTestsFromTestCase( Test_Pitch_to_Lily )
t_d_t_l = unittest.TestLoader().loadTestsFromTestCase( Test_Duration_to_Lily )
t_n_t_l = unittest.TestLoader().loadTestsFromTestCase( Test_Note_to_Lily )
t_b_t_l = unittest.TestLoader().loadTestsFromTestCase( Test_Barline_to_Lily )
