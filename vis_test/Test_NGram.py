#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         Test_Sorting.py
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



import unittest
from vis import *
from music21 import interval, note



#-------------------------------------------------------------------------------
class Test_NGram( unittest.TestCase ):
   def setUp( self ):
      # 'm3 P1 m3'
      self.a = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C5'))]
      self.a_distance = [interval.Interval(note.Note('A4'),note.Note('A4'))]
      # 'm3 P1 M3'
      self.b = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C#5'))]
      self.b_distance = [interval.Interval(note.Note('A4'),note.Note('A4'))]
      # 'm3 +P4 m3'
      self.c = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('F5'))]
      self.c_distance = [interval.Interval(note.Note('A4'),note.Note('D5'))]
      # 'm-3 +M2 M3'
      self.d = [interval.Interval(note.Note('C5'),note.Note('A4')), \
                interval.Interval(note.Note('D5'),note.Note('F#5'))]
      self.d_distance = [interval.Interval(note.Note('C5'),note.Note('D5'))]
      # 'm3 -P4 m3'
      self.e = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('E4'),note.Note('G4'))]
      self.e_distance = [interval.Interval(note.Note('A4'),note.Note('E4'))]
      # 'm3 -m2 M-3'
      self.f = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('G#4'),note.Note('E4'))]
      self.f_distance = [interval.Interval(note.Note('A4'),note.Note('G#4'))]
      # 'm3 +P4 M2 -m6 P5 +A9 M-10'
      self.g = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('E5')), \
                interval.Interval(note.Note('F#4'),note.Note('C#5')), \
                interval.Interval(note.Note('G##5'),note.Note('E#4'))]
      self.g_distance = [interval.Interval(note.Note('A4'),note.Note('D5')), \
                        interval.Interval(note.Note('D5'),note.Note('F#4')), \
                        interval.Interval(note.Note('F#4'),note.Note('G##5'))]
   # end set_up()

   def test_calculating_n( self ):
      x = NGram( self.a )
      self.assertEqual( x.n(), 2 )
      self.assertEqual( x._n, 2 )
      y = NGram( self.g )
      self.assertEqual( y.n(), 4 )
      self.assertEqual( y._n, 4 )

   def test_constructor_assignment( self ):
      # We have to make sure the settings are properly set, and that it works
      # for n-grams of multiple sizes/lengths.
      s = VIS_Settings()
      s.set_property( 'heedQuality true' )
      s.set_property( 'simpleOrCompound simple' )
      #
      x = NGram( self.a )
      self.assertEqual( x._list_of_intervals, self.a )
      self.assertFalse( x._heed_quality )
      self.assertEqual( x._simple_or_compound, 'compound' )
      #
      x = NGram( self.a, s )
      self.assertEqual( x._list_of_intervals, self.a )
      self.assertTrue( x._heed_quality )
      self.assertEqual( x._simple_or_compound, 'simple' )
      #
      y = NGram( self.g )
      self.assertEqual( y._list_of_intervals, self.g )
      self.assertFalse( y._heed_quality )
      self.assertEqual( y._simple_or_compound, 'compound' )
      #
      y = NGram( self.g, s )
      self.assertEqual( y._list_of_intervals, self.g )
      self.assertTrue( y._heed_quality )
      self.assertEqual( y._simple_or_compound, 'simple' )

   def test_distance_calculations( self ):
      self.assertEqual( NGram( self.a )._list_of_movements, self.a_distance )
      self.assertEqual( NGram( self.b )._list_of_movements, self.b_distance )
      self.assertEqual( NGram( self.c )._list_of_movements, self.c_distance )
      self.assertEqual( NGram( self.d )._list_of_movements, self.d_distance )
      self.assertEqual( NGram( self.e )._list_of_movements, self.e_distance )
      self.assertEqual( NGram( self.f )._list_of_movements, self.f_distance )
      self.assertEqual( NGram( self.g )._list_of_movements, self.g_distance )

   def test_distance_calc_exception( self ):
      self.temp = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval('m3')]
      self.assertRaises( MissingInformationError, NGram, self.temp )
      # Note that if we do this with
      # >>> self.g[2].noteEnd = None
      # then everything is okay because we only use the .noteStart to calculate
      # movement of the lower voice.
      try:
         self.g[2].noteEnd = None
      except AttributeError as e:
         pass
      self.assertEqual( NGram( self.g )._list_of_movements, self.g_distance )
      # But this should fail
      try:
         self.g[2].noteStart = None
      except AttributeError as e:
         pass
      self.assertRaises( MissingInformationError, NGram, self.g )

   def test_equality( self ):
      # if they have different heed_quality settings, they're not the same
      self.assertFalse( NGram( self.a ) == NGram( self.a, True ) )
      # if they aren't of the same "n," they're not the same
      self.assertFalse( NGram( self.a, False ) == NGram( self.g, False ) )
      self.assertFalse( NGram( self.a, True ) == NGram( self.g, True ) )
      # they're all equal to themselves if heed_quality
      self.assertTrue( NGram( self.a, True ) == NGram( self.a, True ) )
      self.assertTrue( NGram( self.b, True ) == NGram( self.b, True ) )
      self.assertTrue( NGram( self.c, True ) == NGram( self.c, True ) )
      self.assertTrue( NGram( self.d, True ) == NGram( self.d, True ) )
      self.assertTrue( NGram( self.e, True ) == NGram( self.e, True ) )
      self.assertTrue( NGram( self.f, True ) == NGram( self.f, True ) )
      self.assertTrue( NGram( self.g, True ) == NGram( self.g, True ) )
      # they're all not equal to the next ones if heed_quality
      self.assertFalse( NGram( self.a, True ) == NGram( self.b, True ) )
      self.assertFalse( NGram( self.b, True ) == NGram( self.c, True ) )
      self.assertFalse( NGram( self.c, True ) == NGram( self.d, True ) )
      self.assertFalse( NGram( self.d, True ) == NGram( self.e, True ) )
      self.assertFalse( NGram( self.e, True ) == NGram( self.f, True ) )
      self.assertFalse( NGram( self.f, True ) == NGram( self.g, True ) )
      self.assertFalse( NGram( self.g, True ) == NGram( self.a, True ) )
      # they're all equal to themselves if NOT heed_quality
      self.assertTrue( NGram( self.a, False ) == NGram( self.a, False ) )
      self.assertTrue( NGram( self.b, False ) == NGram( self.b, False ) )
      self.assertTrue( NGram( self.c, False ) == NGram( self.c, False ) )
      self.assertTrue( NGram( self.d, False ) == NGram( self.d, False ) )
      self.assertTrue( NGram( self.e, False ) == NGram( self.e, False ) )
      self.assertTrue( NGram( self.f, False ) == NGram( self.f, False ) )
      self.assertTrue( NGram( self.g, False ) == NGram( self.g, False ) )
      # these are additionally equal if NOT heed_quality
      self.assertTrue( NGram( self.a, False ) == NGram( self.b, False ) )
      #self.assertTrue( NGram( self.c, False ) == NGram( self.d, False ) )
      #self.assertTrue( NGram( self.e, False ) == NGram( self.f, False ) )

   def test_inequality( self ):
      # if they have different heed_quality settings, they're not the same
      self.assertTrue( NGram( self.a, False ) != NGram( self.a, True ) )
      # if they aren't of the same "n," they're not the same
      self.assertTrue( NGram( self.a, False ) != NGram( self.g, False ) )
      self.assertTrue( NGram( self.a, True ) != NGram( self.g, True ) )
      # they're all equal to themselves if heed_quality
      self.assertFalse( NGram( self.a, True ) != NGram( self.a, True ) )
      self.assertFalse( NGram( self.b, True ) != NGram( self.b, True ) )
      self.assertFalse( NGram( self.c, True ) != NGram( self.c, True ) )
      self.assertFalse( NGram( self.d, True ) != NGram( self.d, True ) )
      self.assertFalse( NGram( self.e, True ) != NGram( self.e, True ) )
      self.assertFalse( NGram( self.f, True ) != NGram( self.f, True ) )
      self.assertFalse( NGram( self.g, True ) != NGram( self.g, True ) )
      # they're all equal to themselves if NOT heed_quality
      self.assertFalse( NGram( self.a, False ) != NGram( self.a, False ) )
      self.assertFalse( NGram( self.b, False ) != NGram( self.b, False ) )
      self.assertFalse( NGram( self.c, False ) != NGram( self.c, False ) )
      self.assertFalse( NGram( self.d, False ) != NGram( self.d, False ) )
      self.assertFalse( NGram( self.e, False ) != NGram( self.e, False ) )
      self.assertFalse( NGram( self.f, False ) != NGram( self.f, False ) )
      self.assertFalse( NGram( self.g, False ) != NGram( self.g, False ) )
      # these are additionally equal if NOT heed_quality
      self.assertFalse( NGram( self.a, False ) != NGram( self.b, False ) )
      #self.assertFalse( NGram( self.c, False ) != NGram( self.d, False ) )
      #self.assertFalse( NGram( self.e, False ) != NGram( self.f, False ) )

   def test_str( self ):
      self.assertEqual( str(NGram(self.a,True)), 'm3 P1 m3' )
      self.assertEqual( str(NGram(self.b,True)), 'm3 P1 M3' )
      self.assertEqual( str(NGram(self.c,True)), 'm3 +P4 m3' )
      self.assertEqual( str(NGram(self.d,True)), 'm-3 +M2 M3' )
      self.assertEqual( str(NGram(self.e,True)), 'm3 -P4 m3' )
      self.assertEqual( str(NGram(self.f,True)), 'm3 -m2 M-3' )
      self.assertEqual( str(NGram(self.g,True)), 'm3 +P4 M2 -m6 P5 +A9 M-10' )
      #
      self.assertEqual( str(NGram(self.a,False)), '3 1 3' )
      self.assertEqual( str(NGram(self.b,False)), '3 1 3' )
      self.assertEqual( str(NGram(self.c,False)), '3 +4 3' )
      self.assertEqual( str(NGram(self.d,False)), '-3 +2 3' )
      self.assertEqual( str(NGram(self.e,False)), '3 -4 3' )
      self.assertEqual( str(NGram(self.f,False)), '3 -2 -3' )
      self.assertEqual( str(NGram(self.g,False)), '3 +4 2 -6 5 +9 -10' )

   def test_stringVersion( self ):
      self.assertEqual( NGram(self.a,True).get_string_version(True,'compound'), 'm3 P1 m3' )
      self.assertEqual( NGram(self.b,True).get_string_version(True,'compound'), 'm3 P1 M3' )
      self.assertEqual( NGram(self.c,True).get_string_version(True,'compound'), 'm3 +P4 m3' )
      self.assertEqual( NGram(self.d,True).get_string_version(True,'compound'), 'm-3 +M2 M3' )
      self.assertEqual( NGram(self.e,True).get_string_version(True,'compound'), 'm3 -P4 m3' )
      self.assertEqual( NGram(self.f,True).get_string_version(True,'compound'), 'm3 -m2 M-3' )
      self.assertEqual( NGram(self.g,True).get_string_version(True,'compound'), 'm3 +P4 M2 -m6 P5 +A9 M-10' )
      #
      self.assertEqual( NGram(self.a,False).get_string_version(True,'compound'), 'm3 P1 m3' )
      self.assertEqual( NGram(self.b,False).get_string_version(True,'compound'), 'm3 P1 M3' )
      self.assertEqual( NGram(self.c,False).get_string_version(True,'compound'), 'm3 +P4 m3' )
      self.assertEqual( NGram(self.d,False).get_string_version(True,'compound'), 'm-3 +M2 M3' )
      self.assertEqual( NGram(self.e,False).get_string_version(True,'compound'), 'm3 -P4 m3' )
      self.assertEqual( NGram(self.f,False).get_string_version(True,'compound'), 'm3 -m2 M-3' )
      self.assertEqual( NGram(self.g,False).get_string_version(True,'compound'), 'm3 +P4 M2 -m6 P5 +A9 M-10' )
      #
      self.assertEqual( NGram(self.a,True).get_string_version(False,'compound'), '3 1 3' )
      self.assertEqual( NGram(self.b,True).get_string_version(False,'compound'), '3 1 3' )
      self.assertEqual( NGram(self.c,True).get_string_version(False,'compound'), '3 +4 3' )
      self.assertEqual( NGram(self.d,True).get_string_version(False,'compound'), '-3 +2 3' )
      self.assertEqual( NGram(self.e,True).get_string_version(False,'compound'), '3 -4 3' )
      self.assertEqual( NGram(self.f,True).get_string_version(False,'compound'), '3 -2 -3' )
      self.assertEqual( NGram(self.g,True).get_string_version(False,'compound'), '3 +4 2 -6 5 +9 -10' )
      #
      self.assertEqual( NGram(self.a,False).get_string_version(False,'compound'), '3 1 3' )
      self.assertEqual( NGram(self.b,False).get_string_version(False,'compound'), '3 1 3' )
      self.assertEqual( NGram(self.c,False).get_string_version(False,'compound'), '3 +4 3' )
      self.assertEqual( NGram(self.d,False).get_string_version(False,'compound'), '-3 +2 3' )
      self.assertEqual( NGram(self.e,False).get_string_version(False,'compound'), '3 -4 3' )
      self.assertEqual( NGram(self.f,False).get_string_version(False,'compound'), '3 -2 -3' )
      self.assertEqual( NGram(self.g,False).get_string_version(False,'compound'), '3 +4 2 -6 5 +9 -10' )
      ####
      self.assertEqual( NGram(self.f,True).get_string_version(True,'simple'), 'm3 -m2 M-3' )
      self.assertEqual( NGram(self.g,True).get_string_version(True,'simple'), 'm3 +P4 M2 -m6 P5 +A2 M-3' )
      #
      self.assertEqual( NGram(self.f,False).get_string_version(True,'simple'), 'm3 -m2 M-3' )
      self.assertEqual( NGram(self.g,False).get_string_version(True,'simple'), 'm3 +P4 M2 -m6 P5 +A2 M-3' )
      #
      self.assertEqual( NGram(self.f,True).get_string_version(False,'simple'), '3 -2 -3' )
      self.assertEqual( NGram(self.g,True).get_string_version(False,'simple'), '3 +4 2 -6 5 +2 -3' )
      #
      self.assertEqual( NGram(self.f,False).get_string_version(False,'simple'), '3 -2 -3' )
      self.assertEqual( NGram(self.g,False).get_string_version(False,'simple'), '3 +4 2 -6 5 +2 -3' )
      # Now test with a VIS_Settings object
      s = VIS_Settings()
      s.set_property( 'heedQuality true' )
      s.set_property( 'simpleOrCompound compound' )
      self.assertEqual( NGram(self.g).get_string_version( s ), 'm3 +P4 M2 -m6 P5 +A9 M-10' )
      s.set_property( 'heedQuality false' )
      self.assertEqual( NGram(self.g).get_string_version( s ), '3 +4 2 -6 5 +9 -10' )
      s.set_property( 'simpleOrCompound simple' )
      self.assertEqual( NGram(self.g).get_string_version( s ), '3 +4 2 -6 5 +2 -3' )
      s.set_property( 'heedQuality true' )
      self.assertEqual( NGram(self.g).get_string_version( s ), 'm3 +P4 M2 -m6 P5 +A2 M-3' )

   def test_repr( self ):
      self.assertEqual( NGram(self.a).__repr__(), "NGram( [Interval( Note( 'A4' ), Note( 'C5' ) ), Interval( Note( 'A4' ), Note( 'C5' ) )] )" )
      self.assertEqual( NGram(self.b).__repr__(), "NGram( [Interval( Note( 'A4' ), Note( 'C5' ) ), Interval( Note( 'A4' ), Note( 'C#5' ) )] )" )
      self.assertEqual( NGram(self.c).__repr__(), "NGram( [Interval( Note( 'A4' ), Note( 'C5' ) ), Interval( Note( 'D5' ), Note( 'F5' ) )] )" )
      self.assertEqual( NGram(self.d).__repr__(), "NGram( [Interval( Note( 'C5' ), Note( 'A4' ) ), Interval( Note( 'D5' ), Note( 'F#5' ) )] )" )
      self.assertEqual( NGram(self.e).__repr__(), "NGram( [Interval( Note( 'A4' ), Note( 'C5' ) ), Interval( Note( 'E4' ), Note( 'G4' ) )] )" )
      self.assertEqual( NGram(self.f).__repr__(), "NGram( [Interval( Note( 'A4' ), Note( 'C5' ) ), Interval( Note( 'G#4' ), Note( 'E4' ) )] )" )
      self.assertEqual( NGram(self.g).__repr__(), "NGram( [Interval( Note( 'A4' ), Note( 'C5' ) ), Interval( Note( 'D5' ), Note( 'E5' ) ), Interval( Note( 'F#4' ), Note( 'C#5' ) ), Interval( Note( 'G##5' ), Note( 'E#4' ) )] )" )
   
   def test_voice_crossing( self ):
      self.assertFalse( NGram( self.a ).voice_crossing() )
      self.assertFalse( NGram( self.b ).voice_crossing() )
      self.assertTrue( NGram( self.f ).voice_crossing() )
      self.assertTrue( NGram( self.g ).voice_crossing() )
   
   def test_retrograde( self ):
      self.assertTrue( NGram(self.a,True).retrograde() == NGram([interval.Interval(note.Note('A4'), \
            note.Note('C5')),interval.Interval(note.Note('A4'),note.Note('C5'))],True) )
      self.assertTrue( NGram(self.b,True).retrograde() == NGram([interval.Interval(note.Note('A4'), \
            note.Note('C#5')),interval.Interval(note.Note('A4'),note.Note('C5'))],True) )
      self.assertTrue( NGram(self.c,True).retrograde() == NGram([interval.Interval(note.Note('D5'), \
            note.Note('F5')),interval.Interval(note.Note('A4'),note.Note('C5'))],True) )
      self.assertTrue( NGram(self.d,True).retrograde() == NGram([interval.Interval(note.Note('D5'), \
            note.Note('F#5')),interval.Interval(note.Note('C5'),note.Note('A4'))],True) )
      self.assertTrue( NGram(self.e,True).retrograde() == NGram([interval.Interval(note.Note('E4'), \
            note.Note('G4')),interval.Interval(note.Note('A4'),note.Note('C5'))],True) )
      self.assertTrue( NGram(self.f,True).retrograde() == NGram([interval.Interval(note.Note('G#4'), \
            note.Note('E4')),interval.Interval(note.Note('A4'),note.Note('C5'))],True) )
      self.assertTrue( NGram(self.g,True).retrograde() == NGram([interval.Interval(note.Note('G##5'), \
            note.Note('E#4')),interval.Interval(note.Note('F#4'),note.Note('C#5')), \
            interval.Interval(note.Note('D5'),note.Note('E5')), \
            interval.Interval(note.Note('A4'),note.Note('C5'))],True) )
   
   def test_canonical( self ):
      # m-3 +M2 M3
      self.assertEqual( NGram( self.d, True ).canonical(), 'm3 M2 M3' )
      self.assertEqual( NGram( self.d, False ).canonical(), '3 2 3' )
      # m3 -P4 m3
      self.assertEqual( NGram( self.e, True ).canonical(), 'm3 P4 m3' )
      self.assertEqual( NGram( self.e, False ).canonical(), '3 4 3' )
      # m3 -P4 M-3
      self.assertEqual( NGram( self.f, True ).canonical(), 'm3 m2 M3' )
      self.assertEqual( NGram( self.f, False ).canonical(), '3 2 3' )
      # m3 +P4 M2 -m6 P5 -m2 M-10
      self.assertEqual( NGram( self.g, True ).canonical(), 'm3 P4 M2 m6 P5 A9 M10' )
      self.assertEqual( NGram( self.g, False ).canonical(), '3 4 2 6 5 9 10' )
   
   def test_inversion( self ):
      # NOTE: I'm not 100% sure whether I understand the task here, so I won't
      # finish the tests for now.
      s = VIS_Settings()
      s.set_property( 'heedQuality true' )
      # 'm3 P1 m3'
         # interval.Interval(note.Note('A4'),note.Note('C5'))
         # interval.Interval(note.Note('A4'),note.Note('C5'))
      self.assertEqual( str(NGram(self.a, s).get_inversion_at_the( 12 )), \
            'M-10 P1 M-10' )
      # 'm3 P1 M3' # FIXME
         # interval.Interval(note.Note('A4'),note.Note('C5'))
         # interval.Interval(note.Note('A4'),note.Note('C#5'))
      #self.assertEqual( str(NGram(self.b, s).get_inversion_at_the( 12 )), \
            #'M-10 +A1 m-10' )
      # 'm3 +P4 m3'
         # interval.Interval(note.Note('A4'),note.Note('C5'))
         # interval.Interval(note.Note('D5'),note.Note('F5'))
      self.assertEqual( str(NGram(self.c, s).get_inversion_at_the( 12 )), \
            'M-10 +P4 M-10' )
      # 'm-3 +M2 M3' # FIXME
         # interval.Interval(note.Note('C5'),note.Note('A4'))
         # interval.Interval(note.Note('D5'),note.Note('F#5'))
      #self.assertEqual( str(NGram(self.d, s).get_inversion_at_the( 12 )), \
            #'M10 +M6 m-10' )
      # 'm3 -P4 m3'
         # interval.Interval(note.Note('A4'),note.Note('C5'))
         # interval.Interval(note.Note('E4'),note.Note('G4'))
      self.assertEqual( str(NGram(self.e, s).get_inversion_at_the( 12 )), \
            'M-10 -P4 M-10' )
      # 'm3 -m2 M-3' # FIXME
         # interval.Interval(note.Note('A4'),note.Note('C5'))
         # interval.Interval(note.Note('G#4'),note.Note('E4'))
      #self.assertEqual( str(NGram(self.f, s).get_inversion_at_the( 12 )), \
            #'M-10 -m6 m10' )
      # 'm3 +P4 M2 -m6 P5 +A9 M-10' # FIXME
         # interval.Interval(note.Note('A4'),note.Note('C5'))
         # interval.Interval(note.Note('D5'),note.Note('E5'))
         # interval.Interval(note.Note('F#4'),note.Note('C#5'))
         # interval.Interval(note.Note('G##5'),note.Note('E#4'))
      #self.assertEqual( str(NGram(self.g, s).get_inversion_at_the( 12 )), \
            #'m3 +P4 M2 -m6 P5 +A9 M-10' )
#------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( Test_NGram )
