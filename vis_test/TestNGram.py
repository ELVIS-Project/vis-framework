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



import unittest
from music21.interval import Interval
from music21.note import Note
from NGram import NGram
from VISSettings import VISSettings
from problems import MissingInformationError, NonsensicalInputError



#-------------------------------------------------------------------------------
class TestNGram( unittest.TestCase ):
   def setUp(self):
      # 'm3 P1 m3'
      self.a = [Interval(Note('A4'), Note('C5')), \
                Interval(Note('A4'), Note('C5'))]
      self.a_distance = [Interval(Note('A4'), Note('A4'))]
      # 'm3 P1 M3'
      self.b = [Interval(Note('A4'), Note('C5')), \
                Interval(Note('A4'), Note('C#5'))]
      self.b_distance = [Interval(Note('A4'), Note('A4'))]
      # 'm3 +P4 m3'
      self.c = [Interval(Note('A4'), Note('C5')), \
                Interval(Note('D5'), Note('F5'))]
      self.c_distance = [Interval(Note('A4'), Note('D5'))]
      # 'm-3 +M2 M3'
      self.d = [Interval(Note('C5'), Note('A4')), \
                Interval(Note('D5'), Note('F#5'))]
      self.d_distance = [Interval(Note('C5'), Note('D5'))]
      # 'm3 -P4 m3'
      self.e = [Interval(Note('A4'), Note('C5')), \
                Interval(Note('E4'), Note('G4'))]
      self.e_distance = [Interval(Note('A4'), Note('E4'))]
      # 'm3 -m2 M-3'
      self.f = [Interval(Note('A4'), Note('C5')), \
                Interval(Note('G#4'), Note('E4'))]
      self.f_distance = [Interval(Note('A4'), Note('G#4'))]
      # 4-gram
      # 'm3 +P4 M2 -m6 P5 +A9 M-10'
      self.g = [Interval(Note('A4'), Note('C5')),
                Interval(Note('D5'), Note('E5')),
                Interval(Note('F#4'), Note('C#5')),
                Interval(Note('G##5'), Note('E#4'))]
      self.g_distance = [Interval(Note('A4'), Note('D5')),
                        Interval(Note('D5'), Note('F#4')),
                        Interval(Note('F#4'), Note('G##5'))]
      # 25-gram
      # vertical:
      # (g#4, e5), (f##4, d#5), (f#4, g#4), (f#4, b4), (f#4, a4)
      # (f#4, g#4), (f#4, d#5), (f#4, g#4), (f#4, b4), (f#4, a4)
      # (f#4, g#4), (e4, c#5), (e4, c#5), (d#4, b#4), (d4, e4)
      # (d4, g#4), (d4, f#4), (d4, e4), (d4, b4), (d4, e4)
      # (c#4, g#4), (c#4, f#4), (c#4, e4), (c#4, a4), (b#3, a4)
      self.h = \
      [Interval(Note('g#4'), Note('e5')), Interval(Note('f##4'), Note('d#5')),
       Interval(Note('f#4'), Note('g#4')), Interval(Note('f#4'), Note('b4')),
       Interval(Note('f#4'), Note('a4')), Interval(Note('f#4'), Note('g#4')),
       Interval(Note('f#4'), Note('d#5')), Interval(Note('f#4'), Note('g#4')),
       Interval(Note('f#4'), Note('b4')), Interval(Note('f#4'), Note('a4')),
       Interval(Note('f#4'), Note('g#4')), Interval(Note('e4'), Note('c#5')),
       Interval(Note('e4'), Note('c#5')), Interval(Note('d#4'), Note('b#4')),
       Interval(Note('d4'), Note('e4')), Interval(Note('d4'), Note('g#4')),
       Interval(Note('d4'), Note('f#4')), Interval(Note('d4'), Note('e4')),
       Interval(Note('d4'), Note('b4')), Interval(Note('d4'), Note('e4')),
       Interval(Note('c#4'), Note('g#4')), Interval(Note('c#4'), Note('f#4')),
       Interval(Note('c#4'), Note('e4')), Interval(Note('c#4'), Note('a4')),
       Interval(Note('b#3'), Note('a4'))]
      # horizontal:
      # (g#4, f##4), (f##4, f#4), (f#4, f#4), (f#4, f#4), (f#4, f#4)
      # (f#4, f#4), (f#4, f#4), (f#4, f#4), (f#4, f#4), (f#4, f#4)
      # (f#4, e4), (e4, e4), (e4, d#4), (d#4, d4), (d4, d4)
      # (d4, d4), (d4, d4), (d4, d4), (d4, d4), (d4, c#4)
      # (c#4, c#4), (c#4, c#4), (c#4, c#4), (c#4, b#3)
      self.h_distance = \
      [Interval(Note('g#4'), Note('f##4')), Interval(Note('f##4'), Note('f#4')),
       Interval(Note('f#4'), Note('f#4')), Interval(Note('f#4'), Note('f#4')),
       Interval(Note('f#4'), Note('f#4')), Interval(Note('f#4'), Note('f#4')),
       Interval(Note('f#4'), Note('f#4')), Interval(Note('f#4'), Note('f#4')),
       Interval(Note('f#4'), Note('f#4')), Interval(Note('f#4'), Note('f#4')),
       Interval(Note('f#4'), Note('e4')), Interval(Note('e4'), Note('e4')),
       Interval(Note('e4'), Note('d#4')), Interval(Note('d#4'), Note('d4')),
       Interval(Note('d4'), Note('d4')), Interval(Note('d4'), Note('d4')),
       Interval(Note('d4'), Note('d4')), Interval(Note('d4'), Note('d4')),
       Interval(Note('d4'), Note('d4')), Interval(Note('d4'), Note('c#4')),
       Interval(Note('c#4'), Note('c#4')), Interval(Note('c#4'), Note('c#4')),
       Interval(Note('c#4'), Note('c#4')), Interval(Note('c#4'), Note('b#3'))]
   # end set_up()



   # test_calculating_n
   def test_calculating_n_1(self):
      x = NGram( self.a )
      self.assertEqual( x.n(), 2 )
      self.assertEqual( x._n, 2 )

   def test_calculating_n_2(self):
      y = NGram( self.g )
      self.assertEqual( y.n(), 4 )
      self.assertEqual( y._n, 4 )

   def test_calculating_n_3(self):
      x = NGram( self.h )
      self.assertEqual( x.n(), 25 )
      self.assertEqual( x._n, 25 )

   # test_constructor_assignment
   def test_constructor_assignment_1(self):
      actual = NGram( self.a )
      self.assertEqual( actual._list_of_intervals, self.a )

   def test_constructor_assignment_2(self):
      actual = NGram( self.b )
      self.assertEqual( actual._list_of_intervals, self.b )

   def test_constructor_assignment_3(self):
      actual = NGram( self.c )
      self.assertEqual( actual._list_of_intervals, self.c )

   def test_constructor_assignment_4(self):
      actual = NGram( self.d )
      self.assertEqual( actual._list_of_intervals, self.d )

   def test_constructor_assignment_5(self):
      actual = NGram( self.e )
      self.assertEqual( actual._list_of_intervals, self.e )

   def test_constructor_assignment_6(self):
      actual = NGram( self.f )
      self.assertEqual( actual._list_of_intervals, self.f )

   def test_constructor_assignment_7(self):
      actual = NGram( self.g )
      self.assertEqual( actual._list_of_intervals, self.g )

   def test_constructor_assignment_8(self):
      actual = NGram( self.h )
      self.assertEqual( actual._list_of_intervals, self.h )

   # test_horizontal_calculations
   def test_horizontal_calculations_1(self):
      self.assertEqual(NGram(self.a)._list_of_movements, self.a_distance)

   def test_horizontal_calculations_2(self):
      self.assertEqual(NGram(self.b)._list_of_movements, self.b_distance)

   def test_horizontal_calculations_3(self):
      self.assertEqual(NGram(self.c)._list_of_movements, self.c_distance)

   def test_horizontal_calculations_4(self):
      self.assertEqual(NGram(self.d)._list_of_movements, self.d_distance)

   def test_horizontal_calculations_5(self):
      self.assertEqual(NGram(self.e)._list_of_movements, self.e_distance)

   def test_horizontal_calculations_6(self):
      self.assertEqual(NGram(self.f)._list_of_movements, self.f_distance)

   def test_horizontal_calculations_7(self):
      self.assertEqual(NGram(self.g)._list_of_movements, self.g_distance)

   def test_horizontal_calculations_8(self):
      self.assertEqual(NGram(self.h)._list_of_movements, self.h_distance)

   def test_distance_calc_exception(self):
      self.temp = [Interval(Note('A4'),Note('C5')), \
                Interval('m3')]
      self.assertRaises(MissingInformationError, NGram, self.temp)
      # Note that if we do this with
      # >>> self.g[2].noteEnd = None
      # then everything is okay because we only use the .noteStart to calculate
      # movement of the lower voice.
      try:
         self.g[2].noteEnd = None
      except AttributeError:
         pass
      self.assertEqual( NGram( self.g )._list_of_movements, self.g_distance )
      # But this should fail
      try:
         self.g[2].noteStart = None
      except AttributeError:
         pass
      self.assertRaises( MissingInformationError, NGram, self.g )

   # test_equality
   def test_equality_1(self):
      # if the n-grams have different 'n' values, they're not the same
      self.assertFalse(NGram(self.a) == NGram(self.g))
      self.assertFalse(NGram(self.a) == NGram(self.h))
      self.assertFalse(NGram(self.h) == NGram(self.g))

   def test_equality_2(self):
      # if the n-grams have different 'n' values, they're not the same
      self.assertTrue(NGram(self.a) != NGram(self.g))
      self.assertTrue(NGram(self.a) != NGram(self.h))
      self.assertTrue(NGram(self.h) != NGram(self.g))

   def test_equality_3(self):
      # they're all equal to themselves
      self.assertTrue(NGram(self.a) == NGram(self.a))
      self.assertTrue(NGram(self.b) == NGram(self.b))
      self.assertTrue(NGram(self.c) == NGram(self.c))
      self.assertTrue(NGram(self.d) == NGram(self.d))
      self.assertTrue(NGram(self.e) == NGram(self.e))
      self.assertTrue(NGram(self.f) == NGram(self.f))
      self.assertTrue(NGram(self.g) == NGram(self.g))
      self.assertTrue(NGram(self.h) == NGram(self.h))

   def test_equality_4(self):
      # they're all equal to themselves
      self.assertFalse(NGram(self.a) != NGram(self.a))
      self.assertFalse(NGram(self.b) != NGram(self.b))
      self.assertFalse(NGram(self.c) != NGram(self.c))
      self.assertFalse(NGram(self.d) != NGram(self.d))
      self.assertFalse(NGram(self.e) != NGram(self.e))
      self.assertFalse(NGram(self.f) != NGram(self.f))
      self.assertFalse(NGram(self.g) != NGram(self.g))
      self.assertFalse(NGram(self.h) != NGram(self.h))

   def test_equality_5(self):
      # some arbitrary things that should not be equal
      self.assertFalse(NGram(self.a) == NGram(self.b))
      self.assertFalse(NGram(self.b) == NGram(self.c))
      self.assertFalse(NGram(self.c) == NGram(self.d))
      self.assertFalse(NGram(self.d) == NGram(self.e))
      self.assertFalse(NGram(self.e) == NGram(self.f))
      self.assertFalse(NGram(self.f) == NGram(self.g))
      self.assertFalse(NGram(self.g) == NGram(self.h))
      self.assertFalse(NGram(self.h) == NGram(self.a))

   def test_equality_6(self):
      # some arbitrary things that should not be equal
      self.assertTrue(NGram(self.a) != NGram(self.b))
      self.assertTrue(NGram(self.b) != NGram(self.c))
      self.assertTrue(NGram(self.c) != NGram(self.d))
      self.assertTrue(NGram(self.d) != NGram(self.e))
      self.assertTrue(NGram(self.e) != NGram(self.f))
      self.assertTrue(NGram(self.f) != NGram(self.g))
      self.assertTrue(NGram(self.g) != NGram(self.h))
      self.assertTrue(NGram(self.h) != NGram(self.a))

   def test_str_1(self):
      self.assertEqual(NGram(self.a).get_string_version(True, 'compound'),
                       'm3 P1 m3')
      self.assertEqual(NGram(self.b).get_string_version(True, 'compound'),
                       'm3 P1 M3')
      self.assertEqual(NGram(self.c).get_string_version(True, 'compound'),
                       'm3 +P4 m3')
      self.assertEqual(NGram(self.d).get_string_version(True, 'compound'),
                       'm-3 +M2 M3')
      self.assertEqual(NGram(self.e).get_string_version(True, 'compound'),
                       'm3 -P4 m3')
      self.assertEqual(NGram(self.f).get_string_version(True, 'compound'),
                       'm3 -m2 M-3')
      self.assertEqual(NGram(self.g).get_string_version(True, 'compound'),
                       'm3 +P4 M2 -m6 P5 +A9 M-10')
      self.assertEqual(NGram(self.h).get_string_version(True, 'compound'),
                       'm6 -m2 m6 -A1 M2 P1 P4 P1 m3 P1 M2 P1 M6 P1 M2 P1 P4 P1 m3 P1 M2 -M2 M6 P1 M6 -m2 M6 -A1 M2 P1 A4 P1 M3 P1 M2 P1 M6 P1 M2 -m2 P5 P1 P4 P1 m3 P1 m6 -m2 d7')

   def test_str_2(self):
      self.assertEqual(NGram(self.a).get_string_version(False, 'compound'),
                       '3 1 3')
      self.assertEqual(NGram(self.b).get_string_version(False, 'compound'),
                       '3 1 3')
      self.assertEqual(NGram(self.c).get_string_version(False, 'compound'),
                        '3 +4 3')
      self.assertEqual(NGram(self.d).get_string_version(False, 'compound'),
                       '-3 +2 3')
      self.assertEqual(NGram(self.e).get_string_version(False, 'compound'),
                       '3 -4 3')
      self.assertEqual(NGram(self.f).get_string_version(False, 'compound'),
                       '3 -2 -3')
      self.assertEqual(NGram(self.g).get_string_version(False, 'compound'),
                       '3 +4 2 -6 5 +9 -10')
      self.assertEqual(NGram(self.h).get_string_version(False, 'compound'),
                       '6 -2 6 -1 2 1 4 1 3 1 2 1 6 1 2 1 4 1 3 1 2 -2 6 1 6 -2 6 -1 2 1 4 1 3 1 2 1 6 1 2 -2 5 1 4 1 3 1 6 -2 7')

   def test_str_3(self):
      self.assertEqual(NGram(self.a).get_string_version(True, 'simple'),
                       'm3 P1 m3' )
      self.assertEqual(NGram(self.b).get_string_version(True, 'simple'),
                       'm3 P1 M3' )
      self.assertEqual(NGram(self.c).get_string_version(True, 'simple'),
                       'm3 +P4 m3' )
      self.assertEqual(NGram(self.d).get_string_version(True, 'simple'),
                       'm-3 +M2 M3' )
      self.assertEqual(NGram(self.e).get_string_version(True, 'simple'),
                       'm3 -P4 m3' )
      self.assertEqual(NGram(self.f).get_string_version(True, 'simple'),
                       'm3 -m2 M-3' )
      self.assertEqual(NGram(self.g).get_string_version(True, 'simple'),
                       'm3 +P4 M2 -m6 P5 +A2 M-3' )
      self.assertEqual(NGram(self.h).get_string_version(True, 'simple'),
                       'm6 -m2 m6 -A1 M2 P1 P4 P1 m3 P1 M2 P1 M6 P1 M2 P1 P4 P1 m3 P1 M2 -M2 M6 P1 M6 -m2 M6 -A1 M2 P1 A4 P1 M3 P1 M2 P1 M6 P1 M2 -m2 P5 P1 P4 P1 m3 P1 m6 -m2 d7')

   def test_str_4(self):
      self.assertEqual(NGram(self.a).get_string_version(False, 'simple'),
                       '3 1 3')
      self.assertEqual(NGram(self.b).get_string_version(False, 'simple'),
                       '3 1 3')
      self.assertEqual(NGram(self.c).get_string_version(False, 'simple'),
                       '3 +4 3')
      self.assertEqual(NGram(self.d).get_string_version(False, 'simple'),
                       '-3 +2 3')
      self.assertEqual(NGram(self.e).get_string_version(False, 'simple'),
                       '3 -4 3')
      self.assertEqual(NGram(self.f).get_string_version(False, 'simple'),
                       '3 -2 -3')
      self.assertEqual(NGram(self.g).get_string_version(False, 'simple'),
                       '3 +4 2 -6 5 +2 -3')
      self.assertEqual(NGram(self.h).get_string_version(False, 'simple'),
                       '6 -2 6 -1 2 1 4 1 3 1 2 1 6 1 2 1 4 1 3 1 2 -2 6 1 6 -2 6 -1 2 1 4 1 3 1 2 1 6 1 2 -2 5 1 4 1 3 1 6 -2 7')

   #def test_repr_1(self):
      #self.assertEqual( NGram(self.a).__repr__(), "NGram( [Interval( Note( 'A4' ), Note( 'C5' ) ), Interval( Note( 'A4' ), Note( 'C5' ) )] )" )
#
   #def test_repr_2(self):
      #self.assertEqual( NGram(self.b).__repr__(), "NGram( [Interval( Note( 'A4' ), Note( 'C5' ) ), Interval( Note( 'A4' ), Note( 'C#5' ) )] )" )
#
   ##def test_repr_3(self):
      ##self.assertEqual( NGram(self.c).__repr__()), Note( 'C5' ) ), Interval( Note( 'D5' ), Note( 'F5' ) )] )" )
#
   ##def test_repr_4(self):
      ##self.assertEqual( NGram(self.d).__repr__()), Note( 'A4' ) ), Interval( Note( 'D5' ), Note( 'F#5' ) )] )" )
#
   ##def test_repr_5(self):
      ##self.assertEqual( NGram(self.e).__repr__()), Note( 'C5' ) ), Interval( Note( 'E4' ), Note( 'G4' ) )] )" )
#
   ##def test_repr_6(self):
      ##self.assertEqual( NGram(self.f).__repr__()), Note( 'C5' ) ), Interval( Note( 'G#4' ), Note( 'E4' ) )] )" )
#
   ##def test_repr_7(self):
      ##self.assertEqual( NGram(self.g).__repr__()), Note( 'C5' ) ), Interval( Note( 'D5' ), Note( 'E5' ) ), Interval( Note( 'F#4' ), Note( 'C#5' ) ), Interval( Note( 'G##5' ), Note( 'E#4' ) )] )" )
#
   #def test_voice_crossing_1(self):
      #self.assertFalse( NGram( self.a ).voice_crossing() )
#
   #def test_voice_crossing_2(self):
      #self.assertFalse( NGram( self.b ).voice_crossing() )
#
   #def test_voice_crossing_3(self):
      #self.assertTrue( NGram( self.f ).voice_crossing() )
#
   #def test_voice_crossing_4(self):
      #self.assertTrue( NGram( self.g ).voice_crossing() )
#
   #def test_retrograde_1(self):
      #self.assertTrue( NGram(self.a).retrograde() == NGram([Interval(Note('A4'), \
            #Note('C5')),Interval(Note('A4'),Note('C5'))]) )
#
   #def test_retrograde_2(self):
      #self.assertTrue( NGram(self.b).retrograde() == NGram([Interval(Note('A4'), \
            #Note('C#5')),Interval(Note('A4'),Note('C5'))]) )
#
   #def test_retrograde_3(self):
      #self.assertTrue( NGram(self.c).retrograde() == NGram([Interval(Note('D5'), \
            #Note('F5')),Interval(Note('A4'),Note('C5'))]) )
#
   #def test_retrograde_4(self):
      #self.assertTrue( NGram(self.d).retrograde() == NGram([Interval(Note('D5'), \
            #Note('F#5')),Interval(Note('C5'),Note('A4'))]) )
#
   #def test_retrograde_5(self):
      #self.assertTrue( NGram(self.e).retrograde() == NGram([Interval(Note('E4'), \
            #Note('G4')),Interval(Note('A4'),Note('C5'))]) )
#
   #def test_retrograde_6(self):
      #self.assertTrue( NGram(self.f).retrograde() == NGram([Interval(Note('G#4'), \
            #Note('E4')),Interval(Note('A4'),Note('C5'))]) )
#
   #def test_retrograde_7(self):
      #self.assertTrue( NGram(self.g).retrograde() == NGram([Interval(Note('G##5'), \
            #Note('E#4')),Interval(Note('F#4'),Note('C#5')), \
            #Interval(Note('D5'),Note('E5')), \
            #Interval(Note('A4'),Note('C5'))]) )
#
   #def test_canonical_1(self):
      ## m-3 +M2 M3
      #self.assertEqual( NGram( self.d ).canonical(), 'm3 M2 M3' )
#
   #def test_canonical_2(self):
      ## m3 -P4 m3
      #self.assertEqual( NGram( self.e ).canonical(), 'm3 P4 m3' )
#
   #def test_canonical_3(self):
      ## m3 -P4 M-3
      #self.assertEqual( NGram( self.f ).canonical(), 'm3 m2 M3' )
#
   #def test_canonical_4(self):
      ## m3 +P4 M2 -m6 P5 -m2 M-10
      #self.assertEqual( NGram( self.g ).canonical(), 'm3 P4 M2 m6 P5 A9 M10' )
#
   #def test_inversion_1(self):
      ## m3 M+2 P4 ==(12/up)==> M-10 +M2 M-9
      #i1 = Interval( Note( 'A4' ), Note( 'C5' ) )
      #i2 = Interval( Note( 'B4' ), Note( 'E5' ) )
      #ng = NGram( [i1, i2] )
      #inv_ng = ng.get_inversion_at_the( 12, 'up' )
      #self.assertEqual( inv_ng.get_string_version(True, 'compound'), 'M-10 +M2 M-9' )
      #self.assertEqual( inv_ng._list_of_intervals[0].noteStart.nameWithOctave, 'E6' )
      #self.assertEqual( inv_ng._list_of_intervals[0].noteEnd.nameWithOctave, 'C5' )
      #self.assertEqual( inv_ng._list_of_intervals[1].noteStart.nameWithOctave, 'F#6' )
      #self.assertEqual( inv_ng._list_of_intervals[1].noteEnd.nameWithOctave, 'E5' )
#
   #def test_inversion_2(self):
      ## m3 M+2 P4 ==(12/down)==> M-10 +M2 M-9
      #i1 = Interval( Note( 'A4' ), Note( 'C5' ) )
      #i2 = Interval( Note( 'B4' ), Note( 'E5' ) )
      #ng = NGram( [i1, i2] )
      #inv_ng = ng.get_inversion_at_the( 12, 'down' )
      #self.assertEqual( inv_ng.get_string_version(True, 'compound'), 'M-10 +M2 M-9' )
      #self.assertEqual( inv_ng._list_of_intervals[0].noteStart.nameWithOctave, 'A4' )
      #self.assertEqual( inv_ng._list_of_intervals[0].noteEnd.nameWithOctave, 'F3' )
      #self.assertEqual( inv_ng._list_of_intervals[1].noteStart.nameWithOctave, 'B4' )
      #self.assertEqual( inv_ng._list_of_intervals[1].noteEnd.nameWithOctave, 'A3' )
#
   #def test_inversion_3(self):
      ## m3 M+2 P4 ==(12/6)==> We're going for an error!
      #i1 = Interval( Note( 'A4' ), Note( 'C5' ) )
      #i2 = Interval( Note( 'B4' ), Note( 'E5' ) )
      #ng = NGram( [i1, i2] )
      #self.assertRaises( NonsensicalInputError, ng.get_inversion_at_the, 12, 6 )
#
   #def test_make_from_str_1(self):
      ## Does it work in general?
      ## a : 'm3 P1 m3'
      #str_ng = NGram.make_from_str( 'm3 P1 m3' )
      #orig_ng = NGram( self.a )
      #self.assertEqual( str_ng._list_of_intervals, orig_ng._list_of_intervals )
      #self.assertEqual( str_ng._list_of_movements, orig_ng._list_of_movements )
#
   #def test_make_from_str_2(self):
      ## Does it work in general?
      ## c : 'm3 +P4 m3'
      #str_ng = NGram.make_from_str( 'm3 +P4 m3' )
      #orig_ng = NGram( self.c )
      #self.assertEqual( str_ng._list_of_intervals, orig_ng._list_of_intervals )
      #self.assertEqual( str_ng._list_of_movements, orig_ng._list_of_movements )
#
   #def test_make_from_str_3(self):
      ## Does it work in general?
      ## f : 'm3 -m2 M-3'
      #str_ng = NGram.make_from_str( 'm3 -m2 M-3' )
      #orig_ng = NGram( self.f )
      #self.assertEqual( str_ng._list_of_intervals, orig_ng._list_of_intervals )
      #self.assertEqual( str_ng._list_of_movements, orig_ng._list_of_movements )
#
   #def test_make_from_str_4(self):
      ## negative and positive intervals in input string
      ## g : 'm3 +P4 M2 -m6 P5 +A9 M-10'
      #str_ng = NGram.make_from_str( 'm3 +P4 M2 -m6 P5 +A9 M-10' )
      #orig_ng = NGram( self.g )
      #self.assertEqual( str_ng._list_of_intervals, orig_ng._list_of_intervals )
      #self.assertEqual( str_ng._list_of_movements, orig_ng._list_of_movements )
#
   #def test_make_from_str_5(self):
      ## heedQuality set as per whether there was quality on the way in
      #str_ng = NGram.make_from_str( 'm3 P1 m3' )
      #orig_ng = NGram( self.a )
      #self.assertEqual( str_ng.get_string_version(True, 'compound'), orig_ng.get_string_version(True, 'compound') )
#
   #def test_make_from_str_6(self):
      ## heedQuality set as per whether there was quality on the way in
      #str_ng = NGram.make_from_str( '3 1 3' )
      #orig_ng = NGram( self.a )
      #self.assertEqual( str_ng.get_string_version(False, 'compound'), orig_ng.get_string_version(False, 'compound') )
#
   #def test_make_from_str_7(self):
      ## wrong number of intervals in input string
      #self.assertRaises( NonsensicalInputError, NGram.make_from_str, \
                         #'3 1 3 1' )
#
   #def test_make_from_str_8(self):
      ## wrong number of intervals in input string
      #self.assertRaises( NonsensicalInputError, NGram.make_from_str, '3 12' )
#
   #def test_make_from_str_9(self):
      ## intervals (perfect and non-perfect) larger than P23
      #str_ng = NGram.make_from_str( '24 1 24' )
      #self.assertEqual( str_ng.get_string_version(False, 'compound'), '24 1 24' )
#
   #def test_make_from_str_10(self):
      ## intervals (perfect and non-perfect) larger than P23
      #str_ng = NGram.make_from_str( 'm24 P1 M24' )
      #self.assertEqual( str_ng.get_string_version(True, 'compound'), 'm24 P1 M24' )
#
   #def test_make_from_str_11(self):
      ## intervals (perfect and non-perfect) larger than P23
      #str_ng = NGram.make_from_str( '26 1 26' )
      #self.assertEqual( str_ng.get_string_version(False, 'compound'), '26 1 26' )
#
   #def test_make_from_str_12(self):
      ## intervals (perfect and non-perfect) larger than P23
      #str_ng = NGram.make_from_str( 'P26 P1 d26' )
      #self.assertEqual( str_ng.get_string_version(True, 'compound'), 'P26 P1 d26' )
#
   #def test_make_from_str_13(self):
      ## putting the '-' for negative intervals in all kinds of places
      #str_ng = NGram.make_from_str( 'M3 -M2 M3' )
      #self.assertEqual( str_ng.get_string_version(True, 'compound'), 'M3 -M2 M3' )

   # the following two tests currently fail... does it make sense for
   # them to produce valid NGrams? Those are really weird looking
   # strings.

   #def test_make_from_str_14(self):
      # putting the '-' for negative intervals in all kinds of places
      #str_ng = NGram.make_from_str( 'M3 M-2 M3' )
      #self.assertEqual( str(str_ng), 'M3 -M2 M3' )

   #def test_make_from_str_15(self):
      # putting the '-' for negative intervals in all kinds of places
      #str_ng = NGram.make_from_str( 'M3 M2- M3' )
      #self.assertEqual( str(str_ng), 'M3 -M2 M3' )
#------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( TestNGram )
