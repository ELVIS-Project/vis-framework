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
simple_conversions_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Simple_Conversions )
detect_lilypond_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Detect_LilyPond )
