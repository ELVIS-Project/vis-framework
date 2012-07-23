#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         vis-test.py
# Purpose:      Unit tests for vis.py
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

## To help find reasons for errors.
#from pprint import pprint

# Confirmed Requirements:
import unittest
from vis import *
from analytic_engine import fill_space_between_offsets
from music21 import interval
from music21 import note
from music21 import converter



#-------------------------------------------------------------------------------
class TestSettings( unittest.TestCase ):
   def setUp( self ):
      self.s = VIS_Settings()

   def test_default_init( self ):
      # Ensure all the settings are initialized to the proper default value.
      self.assertEqual( self.s._secret_settings_hash['produceLabeledScore'], False )
      self.assertEqual( self.s._secret_settings_hash['heedQuality'], False )
      self.assertEqual( self.s._secret_settings_hash['lookForTheseNs'], [2] )
      self.assertEqual( self.s._secret_settings_hash['offsetBetweenInterval'], 0.5 )
      self.assertEqual( self.s._secret_settings_hash['outputResultsToFile'], '' )
   
   def test_set_some_things( self ):
      # Setting something to a new, valid value is done properly.
      self.s.set_property( 'set produceLabelledScore True' )
      self.assertEqual( self.s._secret_settings_hash['produceLabeledScore'], True )
      self.s.set_property( 'produceLabelledScore False' )
      self.assertEqual( self.s._secret_settings_hash['produceLabeledScore'], False )
   
   def test_get_some_things( self ):
      self.assertEqual( self.s.get_property( 'produceLabeledScore' ), False )
      self.s._secret_settings_hash['produceLabeledScore'] = True
      self.assertEqual( self.s.get_property( 'produceLabeledScore' ), True )
      self.assertEqual( self.s.get_property( 'produceLabelledScore' ), True )
   
   def test_get_invalid_setting( self ):
      self.assertRaises( NonsensicalInputError, self.s.get_property, 'four score and five score' )
      self.assertRaises( NonsensicalInputError, self.s.get_property, 'four' )
      self.assertRaises( NonsensicalInputError, self.s.get_property, '' )
   
   def test_set_invalid_setting( self ):
      self.assertRaises( NonsensicalInputError, self.s.set_property, 'four score and five score' )
      self.assertRaises( NonsensicalInputError, self.s.set_property, 'fourscoreandfivescore' )
      self.assertRaises( NonsensicalInputError, self.s.set_property, '' )
   
   def test_set_to_invalid_value( self ):
      self.assertRaises( NonsensicalInputError, self.s.set_property, 'set produceLabeledScore five score' )
      self.assertRaises( NonsensicalInputError, self.s.set_property, 'produceLabeledScore five score' )
   
   def test_n_parser( self ):
      # for the method _parse_list_of_n()
      #self.assertEqual( VIS_Settings._parse_list_of_n( '1,2,3,4,5' ), \
                        #[1, 2, 3, 4, 5] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '1, 2, 3, 4, 5' ), \
                        [1, 2, 3, 4, 5] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '[1,2,3,4,5]' ), \
                        [1, 2, 3, 4, 5] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '[1, 2, 3, 4, 5]' ), \
                        [1, 2, 3, 4, 5] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '[3, 2, 1, 4, 5]' ), \
                        [1, 2, 3, 4, 5] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '[1, 3, 3, 2, 1]' ), \
                        [1, 2, 3] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '8, 9, 10' ), \
                        [8, 9, 10] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '8-:!9nanana10' ), \
                        [8, 9, 10] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '42 6  12   ' ), \
                        [6, 12, 42] )
      self.assertEqual( VIS_Settings._parse_list_of_n( '6278 9180 1019 2, 1123' ), \
                        [2, 1019, 1123, 6278, 9180] )
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class TestSorting( unittest.TestCase ):
   def test_interval_simple_cases( self ):
      self.assertEqual( interval_sorter( 'M3', 'P5' ), -1 )
      self.assertEqual( interval_sorter( 'm7', 'd4' ), 1 )

   def test_interval_depends_on_quality( self ):
      self.assertEqual( interval_sorter( 'm3', 'M3' ), -1 )
      self.assertEqual( interval_sorter( 'M3', 'm3' ), 1 )
      self.assertEqual( interval_sorter( 'd3', 'm3' ), -1 )
      self.assertEqual( interval_sorter( 'M3', 'd3' ), 1 )
      self.assertEqual( interval_sorter( 'A3', 'M3' ), 1 )
      self.assertEqual( interval_sorter( 'd3', 'A3' ), -1 )
      self.assertEqual( interval_sorter( 'P4', 'A4' ), -1 )
      self.assertEqual( interval_sorter( 'A4', 'P4' ), 1 )

   def test_interval_all_quality_equalities( self ):
      self.assertEqual( interval_sorter( 'M3', 'M3' ), 0 )
      self.assertEqual( interval_sorter( 'm3', 'm3' ), 0 )
      self.assertEqual( interval_sorter( 'd3', 'd3' ), 0 )
      self.assertEqual( interval_sorter( 'A3', 'A3' ), 0 )
   
   def test_interval_no_qualities( self ):
      self.assertEqual( interval_sorter( '3', '3' ), 0 )
      self.assertEqual( interval_sorter( '3', '4' ), -1 )
      self.assertEqual( interval_sorter( '3', '2' ), 1 )
   
   def test_interval_with_directions( self ):
      self.assertEqual( interval_sorter( '+3', '-3' ), 0 )
      self.assertEqual( interval_sorter( '+3', '-4' ), -1 )
      self.assertEqual( interval_sorter( '+3', '-2' ), 1 )
   
   def test_interval_with_directions_and_quality( self ):
      self.assertEqual( interval_sorter( 'M+3', 'M-3' ), 0 )
      self.assertEqual( interval_sorter( 'm+3', 'P-4' ), -1 )
      self.assertEqual( interval_sorter( 'm+3', 'M-2' ), 1 )
   
   def test_ngram( self ):
      # same as the doctests
      self.assertEqual( ngram_sorter( '3 +4 7', '5 +2 4' ), -1 )
      self.assertEqual( ngram_sorter( '3 +5 6', '3 +4 6' ), 1 )
      self.assertEqual( ngram_sorter( 'M3 1 m2', 'M3 1 M2' ), -1 )
      self.assertEqual( ngram_sorter( '9 -2 -3', '9 -2 -3' ), 0 )
      self.assertEqual( ngram_sorter( '3 -2 3 -2 3', '6 +2 6' ), -1 )
      self.assertEqual( ngram_sorter( '3 -2 3 -2 3', '3 -2 3' ), 1 )
      # additional
      self.assertEqual( ngram_sorter( '3 +4 7', '-3 +4 -7' ), 0 )
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class TestNGram( unittest.TestCase ):
   def setUp( self ):
      # m3 u m3
      self.a = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C5'))]
      self.a_distance = [interval.Interval(note.Note('A4'),note.Note('A4'))]
      # m3 u M3
      self.b = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C#5'))]
      self.b_distance = [interval.Interval(note.Note('A4'),note.Note('A4'))]
      # m3 +P4 m3
      self.c = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('F5'))]
      self.c_distance = [interval.Interval(note.Note('A4'),note.Note('D5'))]
      # m-3 +P4 M3
      self.d = [interval.Interval(note.Note('C5'),note.Note('A4')), \
                interval.Interval(note.Note('D5'),note.Note('F#5'))]
      self.d_distance = [interval.Interval(note.Note('C5'),note.Note('D5'))]
      # m3 -P4 m3
      self.e = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('E4'),note.Note('G4'))]
      self.e_distance = [interval.Interval(note.Note('A4'),note.Note('E4'))]
      # m3 -P4 M-3
      self.f = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('G#4'),note.Note('E4'))]
      self.f_distance = [interval.Interval(note.Note('A4'),note.Note('G#4'))]
      # m3 +P4 M2 -m6 P5 -m2 M-10
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
      x = NGram( self.a )
      self.assertEqual( x._list_of_intervals, self.a )
      #self.assertEqual( x.getIntervals(), self.a )
      y = NGram( self.g )
      self.assertEqual( y._list_of_intervals, self.g )
      #self.assertEqual( y.getIntervals(), self.g )

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

   def test_repr( self ):
      self.assertEqual( NGram(self.a,True).__repr__(), '<NGram m3 P1 m3>' )
      self.assertEqual( NGram(self.b,True).__repr__(), '<NGram m3 P1 M3>' )
      self.assertEqual( NGram(self.c,True).__repr__(), '<NGram m3 +P4 m3>' )
      self.assertEqual( NGram(self.d,True).__repr__(), '<NGram m-3 +M2 M3>' )
      self.assertEqual( NGram(self.e,True).__repr__(), '<NGram m3 -P4 m3>' )
      self.assertEqual( NGram(self.f,True).__repr__(), '<NGram m3 -m2 M-3>' )
      self.assertEqual( NGram(self.g,True).__repr__(), '<NGram m3 +P4 M2 -m6 P5 +A9 M-10>' )
      #
      self.assertEqual( NGram(self.a,False).__repr__(), '<NGram 3 1 3>' )
      self.assertEqual( NGram(self.b,False).__repr__(), '<NGram 3 1 3>' )
      self.assertEqual( NGram(self.c,False).__repr__(), '<NGram 3 +4 3>' )
      self.assertEqual( NGram(self.d,False).__repr__(), '<NGram -3 +2 3>' )
      self.assertEqual( NGram(self.e,False).__repr__(), '<NGram 3 -4 3>' )
      self.assertEqual( NGram(self.f,False).__repr__(), '<NGram 3 -2 -3>' )
      self.assertEqual( NGram(self.g,False).__repr__(), '<NGram 3 +4 2 -6 5 +9 -10>' )
#------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class TestVertical_Interval_Statistics( unittest.TestCase ):
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
      # self.ngg  m3 +P4 M2 -m6 P5 -m2 M-10
      self.ngg = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('E5')), \
                interval.Interval(note.Note('F#4'),note.Note('C#5')), \
                interval.Interval(note.Note('G##5'),note.Note('E#4'))])
      # self.ngh  m3 +P4 M2 -m6 P5 -m2 M-3
      self.ngh = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('E5')), \
                interval.Interval(note.Note('F#4'),note.Note('C#5')), \
                interval.Interval(note.Note('G##4'),note.Note('E#4'))])

   def test_addUpInterval( self ):
      self.vis.add_interval( self.m3 )
      self.assertEqual( self.vis._simple_interval_dict['m3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m3'], 1 )
      self.vis.add_interval( self.m10 )
      self.assertEqual( self.vis._simple_interval_dict['m3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m10'], 1 )
      self.vis.add_interval( self.M3 )
      self.assertEqual( self.vis._simple_interval_dict['M3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['M3'], 1 )
      self.vis.add_interval( self.d_m3 )
      self.assertEqual( self.vis._simple_interval_dict['m3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m3'], 1 )
      self.vis.add_interval( self.d_m10 )
      self.assertEqual( self.vis._simple_interval_dict['m3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m10'], 1 )
   
   def test_addDownInterval( self ):
      self.vis.add_interval( self.d_m3 )
      self.assertEqual( self.vis._simple_interval_dict['m-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m-3'], 1 )
      self.vis.add_interval( self.d_m10 )
      self.assertEqual( self.vis._simple_interval_dict['m-3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m-10'], 1 )
      self.vis.add_interval( self.d_M3 )
      self.assertEqual( self.vis._simple_interval_dict['M-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['M-3'], 1 )
      self.vis.add_interval( self.m3 )
      self.assertEqual( self.vis._simple_interval_dict['m-3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m-3'], 1 )
      self.vis.add_interval( self.m10 )
      self.assertEqual( self.vis._simple_interval_dict['m-3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m-10'], 1 )
   
   def test_addUpDownIntervals( self ):
      self.vis.add_interval( self.m3 )
      self.vis.add_interval( self.d_m3 )
      self.assertEqual( self.vis._simple_interval_dict['m3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m3'], 1 )
      self.assertEqual( self.vis._simple_interval_dict['m-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m-3'], 1 )
      self.vis.add_interval( self.m10 )
      self.vis.add_interval( self.d_m10 )
      self.assertEqual( self.vis._simple_interval_dict['m3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m10'], 1 )
      self.assertEqual( self.vis._simple_interval_dict['m-3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m-10'], 1 )
      self.vis.add_interval( self.M3 )
      self.vis.add_interval( self.d_M3 )
      self.assertEqual( self.vis._simple_interval_dict['M3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['M3'], 1 )
      self.assertEqual( self.vis._simple_interval_dict['M-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['M-3'], 1 )
      self.vis.add_interval( self.M10 )
      self.vis.add_interval( self.d_M10 )
      self.assertEqual( self.vis._simple_interval_dict['m3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m10'], 1 )
      self.assertEqual( self.vis._simple_interval_dict['m-3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['m-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['m-10'], 1 )
      self.assertEqual( self.vis._simple_interval_dict['M3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['M3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['M10'], 1 )
      self.assertEqual( self.vis._simple_interval_dict['M-3'], 2 )
      self.assertEqual( self.vis._compound_interval_dict['M-3'], 1 )
      self.assertEqual( self.vis._compound_interval_dict['M-10'], 1 )

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
   
   def test_add_ngram( self ):
      # basic 2-gram
      self.vis.add_ngram( self.ngc ) # m3 +P4 m3
      self.assertEqual( self.vis._compound_quality_ngrams_dict[2], {'m3 +P4 m3': 1} )
      self.assertEqual( self.vis._compound_no_quality_ngrams_dict[2], {'3 +4 3': 1} )
      # two of a basic 2-gram
      self.vis.add_ngram( self.ngc ) # m3 +P4 m3
      self.assertEqual( self.vis._compound_quality_ngrams_dict[2], {'m3 +P4 m3': 2} )
      self.assertEqual( self.vis._compound_no_quality_ngrams_dict[2], {'3 +4 3': 2} )
      # add one of a similar 2-gram
      self.vis.add_ngram( self.ngd ) # m3 +d4 M3
      self.assertEqual( self.vis._compound_quality_ngrams_dict[2], {'m3 +P4 m3': 2, 'm3 +d4 M3': 1} )
      self.assertEqual( self.vis._compound_no_quality_ngrams_dict[2], {'3 +4 3': 3} )
      # add a 4-gram, 16 times
      for i in xrange(16):
         self.vis.add_ngram( self.ngg ) # m3 +P4 M2 -m6 P5 -m2 M-10
      self.assertEqual( self.vis._compound_quality_ngrams_dict[2], {'m3 +P4 m3': 2, 'm3 +d4 M3': 1} )
      self.assertEqual( self.vis._compound_quality_ngrams_dict[4], {'m3 +P4 M2 -m6 P5 +A9 M-10': 16} )
      self.assertEqual( self.vis._compound_no_quality_ngrams_dict[2], {'3 +4 3': 3} )
      self.assertEqual( self.vis._compound_no_quality_ngrams_dict[4], {'3 +4 2 -6 5 +9 -10': 16} )
   
   def test_get_ngram_occurrences( self ):
      # get_ngram_occurrences( self, whichNGram, n )
      # test that non-existant n values are dealt with properly
      self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 3', n=2 ), 0 )
      self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 3', n=64 ), 0 )
      self.assertEqual( self.vis.get_ngram_occurrences( '', n=2 ), 0 )
      self.assertEqual( self.vis.get_ngram_occurrences( '', n=128 ), 0 )
      
      # test 2 n-grams
      # self.ngd:  m-3 +P4 M3
      # self.nge:  m3 -P4 m3
      self.vis = Vertical_Interval_Statistics()
      for i in xrange(12):
         self.vis.add_ngram( self.ngd )
      for i in xrange(8):
         self.vis.add_ngram( self.nge )
      self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +d4 M3', n=2 ), 12 )
      self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 3', n=2 ), 12 )
      self.assertEqual( self.vis.get_ngram_occurrences( 'm3 -P4 m3', n=2 ), 8 )
      self.assertEqual( self.vis.get_ngram_occurrences( '3 -4 3', n=2 ), 8 )
      
      # test distinct 4-grams with identical simple-interval representations
      # self.ngg  m3 +P4 M2 -m6 P5 -m2 M10
      self.vis = Vertical_Interval_Statistics()
      for i in xrange(10):
         self.vis.add_ngram( self.ngg )
      self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +P4 M2 -m6 P5 +A9 M-10', n=4 ), 10 )
      self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 2 -6 5 +9 -10', n=4 ), 10 )
      self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +P4 M2 -m6 P5 +A2 M-3', n=4 ), 0 )
      self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 2 -6 5 +9 -3', n=4 ), 0 )
      # self.ngh  m3 +P4 M2 -m6 P5 -m2 M3
      for i in xrange(7):
         self.vis.add_ngram( self.ngh )
      self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +P4 M2 -m6 P5 +A9 M-10', n=4 ), 10 )
      self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 2 -6 5 +9 -10', n=4 ), 10 )
      self.assertEqual( self.vis.get_ngram_occurrences( 'm3 +P4 M2 -m6 P5 +A2 M-3', n=4 ), 7 )
      self.assertEqual( self.vis.get_ngram_occurrences( '3 +4 2 -6 5 +2 -3', n=4 ), 7 )
   
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
# End TestVertical_Interval_Statistics ----------------------------------------



#------------------------------------------------------------------------------
class Test_Output_Formatting( unittest.TestCase ):
   def setUp( self ):
      self.vis = Vertical_Interval_Statistics()
   
   def test_basic_formatted_intervals( self ):
      # TODO: test negative intervals
      # TODO: test with quality
      # TODO: test with simple
      expected_ascending_by_interval = '''All the Intervals:
------------------
8: 7
9: 3
10: 24
11: 3
12: 24
13: 14
14: 7
15: 9
16: 1
17: 5

'''
      expected_ascending_by_frequency = '''All the Intervals:
------------------
1: 16
3: 11, 9
5: 17
7: 14, 8
9: 15
14: 13
24: 10, 12

'''
      expected_descending_by_frequency = '''All the Intervals:
------------------
24: 10, 12
14: 13
9: 15
7: 14, 8
5: 17
3: 11, 9
1: 16

'''
      expected_descending_by_interval = '''All the Intervals:
------------------
17: 5
16: 1
15: 9
14: 7
13: 14
12: 24
11: 3
10: 24
9: 3
8: 7

'''
      score = converter.parse( 'test_corpus/bwv77.mxl' )
      sets = VIS_Settings()
      vis_these_parts( [score.parts[0], score.parts[3]], sets, self.vis )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'ascending by interval' ), \
                        expected_ascending_by_interval )
      self.assertEqual( self.vis.get_formatted_intervals( sets, ' ascending by frequency' ), \
                        expected_ascending_by_frequency )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'descending by interval' ), \
                        expected_descending_by_interval )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'descending by frequency' ), \
                        expected_descending_by_frequency )
   
   def test_basic_formatted_ngrams( self ):
      # TODO: test with voice crossing
      # TODO: test with and without heedQuality
      ascending_by_frequency = '''All the 2-grams:
-----------------------------
1: 8 -4 11 and 12 +2 13 and 8 -8 12 and 15 1 8 and 15 -4 18 and 15 -4 17 and 17 +4 15 and 16 1 15 and 17 +8 10 and 4 1 5 and 5 -2 6 and 8 1 10 and 15 -2 12 and 17 +5 12 and 11 +3 10 and 13 -3 17 and 7 1 8 and 10 -4 12 and 10 +4 7 and 10 +4 8 and 12 +4 10 and 17 1 16 and 17 1 15 and 10 -2 15 and 10 -3 12 and 12 1 8 and 11 -2 13 and 5 1 6 and 14 +2 13 and 11 -2 12 and 3 -2 5 and 7 1 6 and 8 -2 9 and 8 -3 10 and 15 +2 12 and 6 1 7 and 10 1 13 and 5 -3 8 and 15 +5 11 and 15 +5 12 and 8 +3 6 and 12 -3 15
2: 17 +3 15 and 11 +2 10 and 17 +2 16 and 10 +2 10 and 6 -2 8 and 15 -2 17 and 9 1 8 and 17 -2 18 and 12 -4 15 and 12 +3 10 and 13 -2 13 and 10 1 12 and 10 -2 12 and 17 +2 15 and 13 -2 17 and 16 +2 15 and 13 +5 10 and 15 +8 8 and 12 -5 15 and 12 1 10 and 15 +2 13 and 8 -2 10 and 14 +2 12 and 9 +2 8 and 10 +2 9 and 10 +2 8 and 9 1 10
3: 15 +4 12 and 12 +2 11 and 12 -5 17 and 15 1 17 and 10 -2 13 and 8 1 9 and 11 1 12 and 15 +2 14 and 18 1 17
4: 17 +4 12 and 10 1 9 and 10 1 11 and 12 -3 17 and 9 -2 10
5: 17 -2 17 and 10 -2 10 and 12 1 13
7: 12 +2 10 and 12 -2 13 and 13 1 12 and 10 -2 11 and 12 1 11
8: 13 +2 12
11: 10 -5 15
15: 11 1 10

'''
      descending_by_frequency = '''All the 2-grams:
-----------------------------
15: 11 1 10
11: 10 -5 15
8: 13 +2 12
7: 12 +2 10 and 12 -2 13 and 13 1 12 and 10 -2 11 and 12 1 11
5: 17 -2 17 and 10 -2 10 and 12 1 13
4: 17 +4 12 and 10 1 9 and 10 1 11 and 12 -3 17 and 9 -2 10
3: 15 +4 12 and 12 +2 11 and 12 -5 17 and 15 1 17 and 10 -2 13 and 8 1 9 and 11 1 12 and 15 +2 14 and 18 1 17
2: 17 +3 15 and 11 +2 10 and 17 +2 16 and 10 +2 10 and 6 -2 8 and 15 -2 17 and 9 1 8 and 17 -2 18 and 12 -4 15 and 12 +3 10 and 13 -2 13 and 10 1 12 and 10 -2 12 and 17 +2 15 and 13 -2 17 and 16 +2 15 and 13 +5 10 and 15 +8 8 and 12 -5 15 and 12 1 10 and 15 +2 13 and 8 -2 10 and 14 +2 12 and 9 +2 8 and 10 +2 9 and 10 +2 8 and 9 1 10
1: 8 -4 11 and 12 +2 13 and 8 -8 12 and 15 1 8 and 15 -4 18 and 15 -4 17 and 17 +4 15 and 16 1 15 and 17 +8 10 and 4 1 5 and 5 -2 6 and 8 1 10 and 15 -2 12 and 17 +5 12 and 11 +3 10 and 13 -3 17 and 7 1 8 and 10 -4 12 and 10 +4 7 and 10 +4 8 and 12 +4 10 and 17 1 16 and 17 1 15 and 10 -2 15 and 10 -3 12 and 12 1 8 and 11 -2 13 and 5 1 6 and 14 +2 13 and 11 -2 12 and 3 -2 5 and 7 1 6 and 8 -2 9 and 8 -3 10 and 15 +2 12 and 6 1 7 and 10 1 13 and 5 -3 8 and 15 +5 11 and 15 +5 12 and 8 +3 6 and 12 -3 15

'''
      ascending_by_ngram = '''All the 2-grams:
-----------------------------
3 -2 5: 1
4 1 5: 1
5 1 6: 1
5 -2 6: 1
5 -3 8: 1
6 1 7: 1
6 -2 8: 2
7 1 6: 1
7 1 8: 1
8 1 9: 3
8 1 10: 1
8 -2 9: 1
8 -2 10: 2
8 +3 6: 1
8 -3 10: 1
8 -4 11: 1
8 -8 12: 1
9 1 8: 2
9 1 10: 2
9 +2 8: 2
9 -2 10: 4
10 1 9: 4
10 1 11: 4
10 1 12: 2
10 1 13: 1
10 +2 8: 2
10 +2 9: 2
10 +2 10: 2
10 -2 10: 5
10 -2 11: 7
10 -2 12: 2
10 -2 13: 3
10 -2 15: 1
10 -3 12: 1
10 +4 7: 1
10 +4 8: 1
10 -4 12: 1
10 -5 15: 11
11 1 10: 15
11 1 12: 3
11 +2 10: 2
11 -2 12: 1
11 -2 13: 1
11 +3 10: 1
12 1 8: 1
12 1 10: 2
12 1 11: 7
12 1 13: 5
12 +2 10: 7
12 +2 11: 3
12 +2 13: 1
12 -2 13: 7
12 +3 10: 2
12 -3 15: 1
12 -3 17: 4
12 +4 10: 1
12 -4 15: 2
12 -5 15: 2
12 -5 17: 3
13 1 12: 7
13 +2 12: 8
13 -2 13: 2
13 -2 17: 2
13 -3 17: 1
13 +5 10: 2
14 +2 12: 2
14 +2 13: 1
15 1 8: 1
15 1 17: 3
15 -2 12: 1
15 +2 12: 1
15 +2 13: 2
15 +2 14: 3
15 -2 17: 2
15 +4 12: 3
15 -4 17: 1
15 -4 18: 1
15 +5 11: 1
15 +5 12: 1
15 +8 8: 2
16 1 15: 1
16 +2 15: 2
17 1 15: 1
17 1 16: 1
17 +2 15: 2
17 +2 16: 2
17 -2 17: 5
17 -2 18: 2
17 +3 15: 2
17 +4 12: 4
17 +4 15: 1
17 +5 12: 1
17 +8 10: 1
18 1 17: 3

'''
      descending_by_ngram = '''All the 2-grams:
-----------------------------
18 1 17: 3
17 +8 10: 1
17 +5 12: 1
17 +4 15: 1
17 +4 12: 4
17 +3 15: 2
17 -2 18: 2
17 -2 17: 5
17 +2 16: 2
17 +2 15: 2
17 1 16: 1
17 1 15: 1
16 +2 15: 2
16 1 15: 1
15 +8 8: 2
15 +5 12: 1
15 +5 11: 1
15 -4 18: 1
15 -4 17: 1
15 +4 12: 3
15 -2 17: 2
15 +2 14: 3
15 +2 13: 2
15 -2 12: 1
15 +2 12: 1
15 1 17: 3
15 1 8: 1
14 +2 13: 1
14 +2 12: 2
13 +5 10: 2
13 -3 17: 1
13 -2 17: 2
13 -2 13: 2
13 +2 12: 8
13 1 12: 7
12 -5 17: 3
12 -5 15: 2
12 -4 15: 2
12 +4 10: 1
12 -3 17: 4
12 -3 15: 1
12 +3 10: 2
12 +2 13: 1
12 -2 13: 7
12 +2 11: 3
12 +2 10: 7
12 1 13: 5
12 1 11: 7
12 1 10: 2
12 1 8: 1
11 +3 10: 1
11 -2 13: 1
11 -2 12: 1
11 +2 10: 2
11 1 12: 3
11 1 10: 15
10 -5 15: 11
10 -4 12: 1
10 +4 8: 1
10 +4 7: 1
10 -3 12: 1
10 -2 15: 1
10 -2 13: 3
10 -2 12: 2
10 -2 11: 7
10 +2 10: 2
10 -2 10: 5
10 +2 9: 2
10 +2 8: 2
10 1 13: 1
10 1 12: 2
10 1 11: 4
10 1 9: 4
9 -2 10: 4
9 +2 8: 2
9 1 10: 2
9 1 8: 2
8 -8 12: 1
8 -4 11: 1
8 -3 10: 1
8 +3 6: 1
8 -2 10: 2
8 -2 9: 1
8 1 10: 1
8 1 9: 3
7 1 8: 1
7 1 6: 1
6 -2 8: 2
6 1 7: 1
5 -3 8: 1
5 -2 6: 1
5 1 6: 1
4 1 5: 1
3 -2 5: 1

'''
      score = converter.parse( 'test_corpus/Kyrie.krn' )
      sets = VIS_Settings()
      vis_these_parts( [score.parts[0], score.parts[-1]], sets, self.vis )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by ngram' ), \
                        ascending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by ngram' ), \
                        descending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by frequency' ), \
                        ascending_by_frequency )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by frequency' ), \
                        descending_by_frequency )
   
   def test_with_negative_intervals( self ):
      ascending_by_interval = '''All the Intervals:
------------------
1: 31
-2: 7
2: 17
3: 72
-3: 13
-4: 2
4: 78
-5: 6
5: 56
-6: 5
6: 107
7: 13
8: 29
9: 9
10: 15
11: 8
-12: 1
12: 1
13: 3

'''
      descending_by_interval = '''All the Intervals:
------------------
13: 3
-12: 1
12: 1
11: 8
10: 15
9: 9
8: 29
7: 13
-6: 5
6: 107
-5: 6
5: 56
-4: 2
4: 78
3: 72
-3: 13
-2: 7
2: 17
1: 31

'''
      ascending_by_frequency = '''All the Intervals:
------------------
1: -12, 12
2: -4
3: 13
5: -6
6: -5
7: -2
8: 11
9: 9
13: 7, -3
15: 10
17: 2
29: 8
31: 1
56: 5
72: 3
78: 4
107: 6

'''
      descending_by_frequency = '''All the Intervals:
------------------
107: 6
78: 4
72: 3
56: 5
31: 1
29: 8
17: 2
15: 10
13: 7, -3
9: 9
8: 11
7: -2
6: -5
5: -6
3: 13
2: -4
1: -12, 12

'''
      score = converter.parse( 'test_corpus/sinfony.md' )
      sets = VIS_Settings()
      vis_these_parts( [score.parts[0], score.parts[1]], sets, self.vis )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'ascending by interval' ), \
                        ascending_by_interval )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'descending by interval' ), \
                        descending_by_interval )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'ascending by frequency' ), \
                        ascending_by_frequency )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'descending by frequency' ), \
                        descending_by_frequency )
   
   def test_with_negative_ngrams( self ):
      ascending_by_ngram = '''All the 2-grams:
-----------------------------
1 1 2: 3
1 1 -2: 2
1 1 3: 1
1 1 4: 6
1 1 5: 2
1 1 6: 1
1 1 8: 1
1 +2 -2: 3
1 -2 2: 2
1 +2 -3: 1
1 -2 3: 1
1 -2 6: 1
1 +3 3: 1
1 -3 6: 1
1 -3 10: 1
1 -5 4: 1
1 -5 5: 1
2 1 1: 5
2 1 3: 4
-2 1 -3: 1
2 1 5: 2
-2 -2 1: 2
2 +2 1: 2
-2 +2 -3: 1
2 -2 3: 1
2 -2 6: 2
2 -2 8: 1
-2 +3 -5: 1
-2 -5 4: 1
3 1 1: 2
3 1 2: 6
-3 1 3: 1
-3 1 4: 1
3 1 4: 20
3 1 5: 2
3 1 6: 5
3 1 -6: 1
3 1 8: 1
3 +2 1: 1
-3 -2 -2: 2
3 +2 3: 3
3 -2 3: 4
-3 +2 -4: 2
3 -2 4: 6
-3 +2 -5: 1
-3 -2 5: 1
-3 -3 -3: 2
-3 -3 3: 1
3 -3 3: 1
3 -3 4: 2
3 -3 5: 4
3 -3 6: 3
3 -4 5: 1
3 -4 6: 1
-3 +4 -6: 1
3 +5 -5: 1
3 -5 5: 1
3 -5 6: 1
-3 -6 5: 1
3 -6 5: 1
3 -6 6: 1
3 -7 4: 1
3 -7 8: 1
3 +10 -12: 1
4 1 1: 3
4 1 2: 2
4 1 3: 11
4 1 5: 5
4 1 -5: 1
4 1 6: 1
4 1 9: 1
4 +2 1: 2
4 +2 3: 7
4 -2 3: 6
4 +2 4: 2
4 -2 4: 5
-4 +2 -5: 1
4 -2 5: 5
4 +2 6: 1
4 -2 6: 3
4 -2 8: 1
-4 -3 -3: 1
4 -3 3: 1
4 -3 5: 2
4 -3 6: 3
4 +4 6: 1
4 -4 6: 1
4 -5 5: 1
4 -5 6: 4
4 -5 7: 1
4 +6 6: 1
4 +7 3: 1
4 -8 6: 1
4 -8 10: 1
4 -8 11: 1
5 1 1: 1
5 1 3: 2
5 1 4: 6
5 1 6: 18
-5 1 -6: 2
5 1 8: 4
5 +2 3: 1
5 +2 4: 2
5 -2 5: 3
-5 -2 5: 1
5 -2 6: 4
-5 +2 -6: 1
-5 -3 -3: 1
5 +3 3: 1
5 +3 4: 1
5 -3 6: 5
5 -3 7: 1
5 +4 1: 1
5 -4 6: 1
5 -4 7: 1
5 -5 5: 1
5 -8 10: 1
6 1 -3: 1
6 1 3: 2
6 1 4: 2
6 1 5: 11
6 1 7: 1
6 1 8: 2
6 1 9: 2
6 1 11: 1
6 +2 1: 4
-6 -2 3: 1
6 +2 3: 4
6 -2 4: 1
6 +2 4: 1
-6 -2 -5: 1
6 +2 5: 6
6 -2 6: 10
6 +2 6: 14
6 -2 7: 5
6 -2 8: 2
6 +3 1: 1
6 -3 1: 1
6 +3 3: 2
-6 -3 -3: 1
6 +3 4: 1
6 -3 6: 3
6 -3 8: 1
6 -3 10: 1
6 +4 2: 2
6 +4 3: 4
6 +4 4: 7
6 +5 6: 1
-6 -5 6: 1
6 -5 8: 1
6 -5 11: 1
6 +6 3: 2
6 +6 4: 2
6 -6 8: 1
6 -8 6: 1
7 1 6: 2
7 1 8: 4
7 +2 6: 1
7 -2 8: 4
7 +4 4: 1
7 -5 10: 1
8 1 4: 1
8 1 6: 2
8 1 7: 2
8 1 11: 1
8 +2 5: 1
8 +2 7: 2
8 -2 9: 2
8 -2 10: 2
8 +3 3: 1
8 +3 5: 1
8 -4 4: 1
8 +4 4: 1
8 +4 6: 1
8 +5 3: 2
8 +5 -3: 1
8 +5 4: 2
8 +6 3: 2
8 +6 6: 2
9 1 8: 3
9 -2 10: 2
9 -3 10: 1
9 +4 5: 2
9 +5 6: 1
10 1 6: 2
10 1 9: 3
10 1 11: 4
10 +3 6: 1
10 -3 13: 1
10 +5 6: 1
11 +2 10: 1
11 -2 12: 1
11 +4 8: 1
11 +7 3: 2
11 +8 3: 1
12 -2 13: 1
13 +2 8: 1
13 +3 13: 1

'''
      descending_by_ngram = '''All the 2-grams:
-----------------------------
13 +3 13: 1
13 +2 8: 1
12 -2 13: 1
11 +8 3: 1
11 +7 3: 2
11 +4 8: 1
11 -2 12: 1
11 +2 10: 1
10 +5 6: 1
10 -3 13: 1
10 +3 6: 1
10 1 11: 4
10 1 9: 3
10 1 6: 2
9 +5 6: 1
9 +4 5: 2
9 -3 10: 1
9 -2 10: 2
9 1 8: 3
8 +6 6: 2
8 +6 3: 2
8 +5 4: 2
8 +5 3: 2
8 +5 -3: 1
8 +4 6: 1
8 -4 4: 1
8 +4 4: 1
8 +3 5: 1
8 +3 3: 1
8 -2 10: 2
8 -2 9: 2
8 +2 7: 2
8 +2 5: 1
8 1 11: 1
8 1 7: 2
8 1 6: 2
8 1 4: 1
7 -5 10: 1
7 +4 4: 1
7 -2 8: 4
7 +2 6: 1
7 1 8: 4
7 1 6: 2
6 -8 6: 1
6 -6 8: 1
6 +6 4: 2
6 +6 3: 2
6 -5 11: 1
6 -5 8: 1
6 +5 6: 1
-6 -5 6: 1
6 +4 4: 7
6 +4 3: 4
6 +4 2: 2
6 -3 10: 1
6 -3 8: 1
6 -3 6: 3
6 +3 4: 1
6 +3 3: 2
-6 -3 -3: 1
6 +3 1: 1
6 -3 1: 1
6 -2 8: 2
6 -2 7: 5
6 -2 6: 10
6 +2 6: 14
-6 -2 -5: 1
6 +2 5: 6
6 -2 4: 1
6 +2 4: 1
-6 -2 3: 1
6 +2 3: 4
6 +2 1: 4
6 1 11: 1
6 1 9: 2
6 1 8: 2
6 1 7: 1
6 1 5: 11
6 1 4: 2
6 1 -3: 1
6 1 3: 2
5 -8 10: 1
5 -5 5: 1
5 -4 7: 1
5 -4 6: 1
5 +4 1: 1
5 -3 7: 1
5 -3 6: 5
5 +3 4: 1
-5 -3 -3: 1
5 +3 3: 1
5 -2 6: 4
-5 +2 -6: 1
5 -2 5: 3
-5 -2 5: 1
5 +2 4: 2
5 +2 3: 1
5 1 8: 4
5 1 6: 18
-5 1 -6: 2
5 1 4: 6
5 1 3: 2
5 1 1: 1
4 -8 11: 1
4 -8 10: 1
4 -8 6: 1
4 +7 3: 1
4 +6 6: 1
4 -5 7: 1
4 -5 6: 4
4 -5 5: 1
4 +4 6: 1
4 -4 6: 1
4 -3 6: 3
4 -3 5: 2
-4 -3 -3: 1
4 -3 3: 1
4 -2 8: 1
4 +2 6: 1
4 -2 6: 3
-4 +2 -5: 1
4 -2 5: 5
4 +2 4: 2
4 -2 4: 5
4 +2 3: 7
4 -2 3: 6
4 +2 1: 2
4 1 9: 1
4 1 6: 1
4 1 5: 5
4 1 -5: 1
4 1 3: 11
4 1 2: 2
4 1 1: 3
3 +10 -12: 1
3 -7 8: 1
3 -7 4: 1
3 -6 6: 1
-3 -6 5: 1
3 -6 5: 1
3 -5 6: 1
3 +5 -5: 1
3 -5 5: 1
3 -4 6: 1
-3 +4 -6: 1
3 -4 5: 1
3 -3 6: 3
3 -3 5: 4
3 -3 4: 2
-3 -3 -3: 2
-3 -3 3: 1
3 -3 3: 1
-3 +2 -5: 1
-3 -2 5: 1
-3 +2 -4: 2
3 -2 4: 6
3 +2 3: 3
3 -2 3: 4
-3 -2 -2: 2
3 +2 1: 1
3 1 8: 1
3 1 6: 5
3 1 -6: 1
3 1 5: 2
-3 1 4: 1
3 1 4: 20
-3 1 3: 1
3 1 2: 6
3 1 1: 2
-2 -5 4: 1
-2 +3 -5: 1
2 -2 8: 1
2 -2 6: 2
-2 +2 -3: 1
2 -2 3: 1
-2 -2 1: 2
2 +2 1: 2
2 1 5: 2
2 1 3: 4
-2 1 -3: 1
2 1 1: 5
1 -5 5: 1
1 -5 4: 1
1 -3 10: 1
1 -3 6: 1
1 +3 3: 1
1 -2 6: 1
1 +2 -3: 1
1 -2 3: 1
1 +2 -2: 3
1 -2 2: 2
1 1 8: 1
1 1 6: 1
1 1 5: 2
1 1 4: 6
1 1 3: 1
1 1 2: 3
1 1 -2: 2

'''
      ascending_by_frequency = '''All the 2-grams:
-----------------------------
1: -4 -3 -3 and 8 +2 5 and 3 +2 1 and 7 -5 10 and 8 1 4 and 12 -2 13 and 4 -3 3 and 4 +7 3 and 4 1 9 and -5 -3 -3 and 1 1 8 and 4 1 6 and 6 +3 1 and 3 -4 5 and 3 -4 6 and -3 -6 5 and 9 +5 6 and 8 1 11 and 1 +3 3 and 6 -2 4 and 10 +5 6 and 5 +3 4 and 5 +3 3 and 6 1 7 and -3 1 3 and -3 1 4 and -3 +2 -5 and -6 -3 -3 and 8 -4 4 and 4 -5 5 and 4 +6 6 and 4 +4 6 and 1 +2 -3 and 4 +2 6 and 6 -5 11 and 7 +4 4 and 11 +8 3 and 3 -6 5 and -2 +2 -3 and 6 -8 6 and 3 -7 8 and 6 -3 1 and 3 -5 6 and 6 -3 8 and 5 +2 3 and 4 -4 6 and -3 -3 3 and 11 +2 10 and 3 -3 3 and 6 -5 8 and 8 +4 6 and 8 +4 4 and -5 +2 -6 and 2 -2 3 and 6 -3 10 and 1 -3 10 and 4 -8 6 and 7 +2 6 and -2 +3 -5 and 1 -5 5 and 10 -3 13 and 1 -3 6 and 5 1 1 and 3 -7 4 and 5 -8 10 and 5 -5 5 and -6 -2 -5 and -5 -2 5 and 1 -2 3 and 1 -5 4 and 1 -2 6 and 6 1 11 and 11 -2 12 and 6 +5 6 and 6 1 -3 and 3 -6 6 and -2 -5 4 and -6 -5 6 and 1 1 6 and 10 +3 6 and 5 +4 1 and 3 1 8 and 4 -5 7 and 13 +3 13 and 11 +4 8 and 2 -2 8 and -6 -2 3 and -4 +2 -5 and 4 -2 8 and -3 -2 5 and 6 +3 4 and 5 -4 6 and 5 -4 7 and -3 +4 -6 and 3 +5 -5 and 3 +10 -12 and 3 1 -6 and 5 -3 7 and 3 -5 5 and 6 +2 4 and 13 +2 8 and -2 1 -3 and 8 +5 -3 and 1 1 3 and 8 +3 5 and 9 -3 10 and 8 +3 3 and 6 -6 8 and 4 1 -5 and 4 -8 11 and 4 -8 10
2: 8 +2 7 and 8 1 6 and 8 1 7 and -3 -3 -3 and 9 +4 5 and 4 -3 5 and 6 +3 3 and 1 1 5 and 4 1 2 and 6 -2 8 and 8 +6 3 and 6 1 4 and 8 +6 6 and -3 +2 -4 and -2 -2 1 and 6 1 8 and 4 +2 1 and 4 +2 4 and 6 +4 2 and 5 +2 4 and 2 +2 1 and 7 1 6 and 3 -3 4 and 11 +7 3 and 5 1 3 and 8 -2 9 and 1 -2 2 and 3 1 5 and 3 1 1 and 2 -2 6 and 8 +5 3 and 1 1 -2 and 8 +5 4 and 9 -2 10 and 6 1 9 and 6 1 3 and 8 -2 10 and -5 1 -6 and -3 -2 -2 and 2 1 5 and 6 +6 4 and 6 +6 3 and 10 1 6
3: 3 +2 3 and 4 -3 6 and 4 1 1 and 1 1 2 and 5 -2 5 and 9 1 8 and 10 1 9 and 1 +2 -2 and 6 -3 6 and 3 -3 6 and 4 -2 6
4: 5 -2 6 and 7 -2 8 and 6 +4 3 and 4 -5 6 and 10 1 11 and 3 -3 5 and 2 1 3 and 6 +2 1 and 5 1 8 and 7 1 8 and 3 -2 3 and 6 +2 3
5: 4 1 5 and 6 -2 7 and 2 1 1 and 3 1 6 and 4 -2 5 and 4 -2 4 and 5 -3 6
6: 1 1 4 and 5 1 4 and 3 -2 4 and 3 1 2 and 4 -2 3 and 6 +2 5
7: 4 +2 3 and 6 +4 4
10: 6 -2 6
11: 4 1 3 and 6 1 5
14: 6 +2 6
18: 5 1 6
20: 3 1 4

'''
      descending_by_frequency = '''All the 2-grams:
-----------------------------
20: 3 1 4
18: 5 1 6
14: 6 +2 6
11: 4 1 3 and 6 1 5
10: 6 -2 6
7: 4 +2 3 and 6 +4 4
6: 1 1 4 and 5 1 4 and 3 -2 4 and 3 1 2 and 4 -2 3 and 6 +2 5
5: 4 1 5 and 6 -2 7 and 2 1 1 and 3 1 6 and 4 -2 5 and 4 -2 4 and 5 -3 6
4: 5 -2 6 and 7 -2 8 and 6 +4 3 and 4 -5 6 and 10 1 11 and 3 -3 5 and 2 1 3 and 6 +2 1 and 5 1 8 and 7 1 8 and 3 -2 3 and 6 +2 3
3: 3 +2 3 and 4 -3 6 and 4 1 1 and 1 1 2 and 5 -2 5 and 9 1 8 and 10 1 9 and 1 +2 -2 and 6 -3 6 and 3 -3 6 and 4 -2 6
2: 8 +2 7 and 8 1 6 and 8 1 7 and -3 -3 -3 and 9 +4 5 and 4 -3 5 and 6 +3 3 and 1 1 5 and 4 1 2 and 6 -2 8 and 8 +6 3 and 6 1 4 and 8 +6 6 and -3 +2 -4 and -2 -2 1 and 6 1 8 and 4 +2 1 and 4 +2 4 and 6 +4 2 and 5 +2 4 and 2 +2 1 and 7 1 6 and 3 -3 4 and 11 +7 3 and 5 1 3 and 8 -2 9 and 1 -2 2 and 3 1 5 and 3 1 1 and 2 -2 6 and 8 +5 3 and 1 1 -2 and 8 +5 4 and 9 -2 10 and 6 1 9 and 6 1 3 and 8 -2 10 and -5 1 -6 and -3 -2 -2 and 2 1 5 and 6 +6 4 and 6 +6 3 and 10 1 6
1: -4 -3 -3 and 8 +2 5 and 3 +2 1 and 7 -5 10 and 8 1 4 and 12 -2 13 and 4 -3 3 and 4 +7 3 and 4 1 9 and -5 -3 -3 and 1 1 8 and 4 1 6 and 6 +3 1 and 3 -4 5 and 3 -4 6 and -3 -6 5 and 9 +5 6 and 8 1 11 and 1 +3 3 and 6 -2 4 and 10 +5 6 and 5 +3 4 and 5 +3 3 and 6 1 7 and -3 1 3 and -3 1 4 and -3 +2 -5 and -6 -3 -3 and 8 -4 4 and 4 -5 5 and 4 +6 6 and 4 +4 6 and 1 +2 -3 and 4 +2 6 and 6 -5 11 and 7 +4 4 and 11 +8 3 and 3 -6 5 and -2 +2 -3 and 6 -8 6 and 3 -7 8 and 6 -3 1 and 3 -5 6 and 6 -3 8 and 5 +2 3 and 4 -4 6 and -3 -3 3 and 11 +2 10 and 3 -3 3 and 6 -5 8 and 8 +4 6 and 8 +4 4 and -5 +2 -6 and 2 -2 3 and 6 -3 10 and 1 -3 10 and 4 -8 6 and 7 +2 6 and -2 +3 -5 and 1 -5 5 and 10 -3 13 and 1 -3 6 and 5 1 1 and 3 -7 4 and 5 -8 10 and 5 -5 5 and -6 -2 -5 and -5 -2 5 and 1 -2 3 and 1 -5 4 and 1 -2 6 and 6 1 11 and 11 -2 12 and 6 +5 6 and 6 1 -3 and 3 -6 6 and -2 -5 4 and -6 -5 6 and 1 1 6 and 10 +3 6 and 5 +4 1 and 3 1 8 and 4 -5 7 and 13 +3 13 and 11 +4 8 and 2 -2 8 and -6 -2 3 and -4 +2 -5 and 4 -2 8 and -3 -2 5 and 6 +3 4 and 5 -4 6 and 5 -4 7 and -3 +4 -6 and 3 +5 -5 and 3 +10 -12 and 3 1 -6 and 5 -3 7 and 3 -5 5 and 6 +2 4 and 13 +2 8 and -2 1 -3 and 8 +5 -3 and 1 1 3 and 8 +3 5 and 9 -3 10 and 8 +3 3 and 6 -6 8 and 4 1 -5 and 4 -8 11 and 4 -8 10

'''
      score = converter.parse( 'test_corpus/sinfony.md' )
      sets = VIS_Settings()
      vis_these_parts( [score.parts[0], score.parts[1]], sets, self.vis )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by ngram' ), \
                        ascending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by ngram' ), \
                        descending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by frequency' ), \
                        ascending_by_frequency )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by frequency' ), \
                        descending_by_frequency )
   
   def test_2_and_3_grams( self ):
      ascending_by_ngram = '''All the 2-grams:
-----------------------------
3 1 6: 1
4 1 3: 1
5 +2 4: 1
5 -3 6: 1
6 1 5: 2
6 -2 8: 1
6 -3 8: 1
7 1 6: 1
8 1 5: 1
8 1 10: 1
8 +2 7: 1
8 -2 9: 4
8 -2 10: 1
8 -3 10: 1
9 1 8: 1
9 +2 10: 1
9 -2 10: 3
9 +3 6: 1
10 1 8: 1
10 1 9: 2
10 1 12: 3
10 +2 8: 1
10 +2 9: 1
10 +2 10: 4
10 -2 10: 10
10 -2 11: 4
10 -2 15: 2
10 -3 10: 3
10 -3 11: 1
10 -3 12: 2
10 -4 12: 1
10 -5 15: 3
10 +8 10: 1
11 1 10: 5
11 +2 10: 1
11 -2 12: 1
11 -2 15: 1
12 1 8: 1
12 1 11: 2
12 +2 10: 2
12 -2 13: 3
12 +3 10: 2
12 +5 8: 1
12 +5 10: 1
13 1 12: 1
13 -2 14: 3
14 +2 12: 1
14 -2 15: 2
14 -2 17: 1
15 1 14: 1
15 +2 13: 1
15 +4 12: 1
15 +5 11: 1
15 +8 8: 2
16 1 15: 1
17 -2 17: 1

All the 3-grams:
-----------------------------
3 1 6 -3 8: 1
4 1 3 1 6: 1
5 +2 4 1 3: 1
5 -3 6 1 5: 1
6 1 5 +2 4: 1
6 1 5 -3 6: 1
6 -2 8 1 5: 1
6 -3 8 +2 7: 1
7 1 6 -2 8: 1
8 1 10 -2 10: 1
8 +2 7 1 6: 1
8 -2 9 -2 10: 3
8 -2 10 -5 15: 1
8 -3 10 -2 11: 1
9 1 8 -2 10: 1
9 -2 10 -2 11: 2
9 -2 10 -2 15: 1
9 +2 10 -3 11: 1
9 +3 6 1 5: 1
10 1 8 1 10: 1
10 1 9 1 8: 1
10 1 9 +3 6: 1
10 1 12 -2 13: 2
10 +2 8 -3 10: 1
10 +2 9 +2 10: 1
10 -2 10 -2 10: 5
10 +2 10 -2 10: 1
10 +2 10 -3 10: 1
10 -2 10 -3 10: 2
10 -2 10 -3 12: 1
10 +2 10 -4 12: 1
10 -2 10 +8 10: 1
10 -2 11 1 10: 2
10 -2 11 -2 12: 1
10 -2 11 -2 15: 1
10 -3 10 +2 10: 2
10 -3 10 -2 10: 1
10 -3 11 +2 10: 1
10 -3 12 +3 10: 1
10 -3 12 +5 10: 1
10 -5 15 +8 8: 2
10 +8 10 1 8: 1
11 1 10 +2 8: 1
11 1 10 +2 10: 1
11 1 10 -5 15: 1
11 +2 10 -2 11: 1
11 -2 12 1 8: 1
11 -2 15 +4 12: 1
12 1 8 -2 9: 1
12 1 11 1 10: 2
12 +2 10 1 12: 1
12 +2 10 +2 9: 1
12 -2 13 -2 14: 3
12 +3 10 1 9: 1
12 +3 10 -2 10: 1
12 +5 10 -5 15: 1
13 1 12 +2 10: 1
13 -2 14 -2 15: 2
13 -2 14 -2 17: 1
14 +2 12 +2 10: 1
14 -2 15 1 14: 1
14 -2 15 +2 13: 1
14 -2 17 -2 17: 1
15 1 14 +2 12: 1
15 +2 13 1 12: 1
15 +4 12 1 11: 1
15 +5 11 1 10: 1
15 +8 8 -2 9: 1
16 1 15 +5 11: 1

'''
      descending_by_frequency = '''All the 2-grams:
-----------------------------
10: 10 -2 10
5: 11 1 10
4: 8 -2 9 and 10 +2 10 and 10 -2 11
3: 10 -3 10 and 9 -2 10 and 13 -2 14 and 12 -2 13 and 10 -5 15 and 10 1 12
2: 6 1 5 and 12 1 11 and 12 +2 10 and 10 -3 12 and 10 1 9 and 15 +8 8 and 12 +3 10 and 14 -2 15 and 10 -2 15
1: 11 -2 15 and 15 +4 12 and 8 +2 7 and 12 +5 10 and 15 +2 13 and 17 -2 17 and 8 1 5 and 10 1 8 and 12 1 8 and 11 +2 10 and 9 +2 10 and 11 -2 12 and 13 1 12 and 12 +5 8 and 16 1 15 and 15 1 14 and 4 1 3 and 10 -4 12 and 8 -3 10 and 9 +3 6 and 10 -3 11 and 5 -3 6 and 9 1 8 and 15 +5 11 and 10 +8 10 and 6 -2 8 and 8 1 10 and 6 -3 8 and 14 -2 17 and 5 +2 4 and 8 -2 10 and 10 +2 9 and 10 +2 8 and 14 +2 12 and 3 1 6 and 7 1 6

All the 3-grams:
-----------------------------
5: 10 -2 10 -2 10
3: 8 -2 9 -2 10 and 12 -2 13 -2 14
2: 10 -2 11 1 10 and 10 -2 10 -3 10 and 10 -3 10 +2 10 and 13 -2 14 -2 15 and 12 1 11 1 10 and 9 -2 10 -2 11 and 10 1 12 -2 13 and 10 -5 15 +8 8
1: 14 -2 15 1 14 and 11 1 10 +2 8 and 15 1 14 +2 12 and 10 +2 10 -3 10 and 9 +3 6 1 5 and 9 +2 10 -3 11 and 6 1 5 -3 6 and 14 +2 12 +2 10 and 14 -2 17 -2 17 and 9 1 8 -2 10 and 12 +3 10 -2 10 and 8 +2 7 1 6 and 10 -2 10 -3 12 and 6 -2 8 1 5 and 5 -3 6 1 5 and 10 +2 10 -4 12 and 8 -3 10 -2 11 and 10 1 9 +3 6 and 9 -2 10 -2 15 and 4 1 3 1 6 and 15 +8 8 -2 9 and 10 +2 8 -3 10 and 11 1 10 -5 15 and 11 1 10 +2 10 and 15 +2 13 1 12 and 12 +3 10 1 9 and 10 -3 11 +2 10 and 13 1 12 +2 10 and 10 -3 10 -2 10 and 10 -2 10 +8 10 and 10 1 8 1 10 and 7 1 6 -2 8 and 12 +2 10 1 12 and 8 -2 10 -5 15 and 16 1 15 +5 11 and 3 1 6 -3 8 and 14 -2 15 +2 13 and 11 +2 10 -2 11 and 13 -2 14 -2 17 and 11 -2 15 +4 12 and 10 +2 10 -2 10 and 12 +5 10 -5 15 and 15 +4 12 1 11 and 5 +2 4 1 3 and 10 +8 10 1 8 and 6 1 5 +2 4 and 8 1 10 -2 10 and 10 -2 11 -2 15 and 12 +2 10 +2 9 and 10 -3 12 +5 10 and 12 1 8 -2 9 and 10 -3 12 +3 10 and 10 -2 11 -2 12 and 11 -2 12 1 8 and 10 1 9 1 8 and 6 -3 8 +2 7 and 10 +2 9 +2 10 and 15 +5 11 1 10

'''
      score = converter.parse( 'test_corpus/Jos2308.krn' )
      sets = VIS_Settings()
      sets.set_property( 'lookForTheseNs 2,3' )
      vis_these_parts( [score.parts[0][:100], score.parts[-1][:100]], sets, self.vis )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by ngram' ), \
                        ascending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by frequency' ), \
                        descending_by_frequency )
   
   def test_only_4_grams_with_negatives( self ):
      ascending_by_frequency = '''All the 4-grams:
-----------------------------
1: 5 -3 8 +2 7 +2 -3 and 3 -5 8 +3 -3 1 3 and 3 +3 1 1 -2 1 -3 and 5 1 6 +3 3 -2 4 and 4 +2 2 1 3 1 4 and 3 +2 3 +2 3 +2 3 and 3 -3 5 +2 4 1 3 and -2 1 -3 1 -4 1 -5 and 8 +3 6 1 5 1 6 and 8 +3 6 1 5 1 4 and 8 +3 6 1 5 1 3 and 4 1 3 +2 3 1 4 and 5 +2 3 1 2 -2 3 and 2 1 3 1 4 -2 5 and 6 +5 3 -5 8 +2 7 and -5 -2 -4 -2 3 -2 4 and 6 1 5 1 4 1 3 and 4 -2 3 +4 3 -2 3 and 5 1 4 1 3 1 5 and 6 1 5 +3 1 1 2 and 6 1 5 +3 1 1 3 and 4 -2 6 1 7 1 8 and 7 +2 6 1 5 +2 3 and -3 1 -2 -5 5 +2 4 and 3 -2 3 1 2 1 1 and 6 -2 7 -2 8 1 7 and 7 +2 6 +2 4 1 3 and 3 1 2 -2 3 +2 1 and 8 +3 6 -3 8 +2 6 and 3 +4 3 1 2 1 1 and 3 +3 1 1 3 +3 1 and -2 -2 1 1 2 1 3 and 6 +2 5 1 4 -3 6 and 5 +2 3 -2 3 1 1 and 5 -3 8 +2 7 1 6 and 2 -2 3 +2 6 +4 3 and 6 +3 3 -2 4 -2 5 and -3 +2 -3 1 -2 -5 5 and 2 -2 3 1 -3 -2 -2 and -3 1 -2 1 1 1 2 and 6 1 5 +2 4 1 3 and 6 -3 8 +2 6 -3 8 and 3 +3 1 1 2 1 3 and 7 +2 6 -3 8 +2 6 and 2 1 3 1 4 1 5 and 6 1 7 1 8 +2 7 and 6 -2 7 1 6 -2 8 and -5 -8 8 +3 6 -3 8 and 5 +2 3 +5 -3 -2 -2 and 3 -2 6 -2 8 +3 6 and 4 1 3 1 4 1 8 and 4 -2 5 -2 8 +3 6 and 3 1 1 -2 3 -2 3 and 2 -2 -3 -2 -2 -2 1 and 8 +2 5 1 6 -3 8 and 3 +2 3 -2 3 1 2 and 5 1 6 +5 3 -5 8 and 3 +4 3 -2 3 +4 3 and 6 -3 8 +2 5 1 6 and -2 -2 1 -2 2 -2 6 and 6 +2 3 +2 1 1 5 and 4 +2 1 1 2 -2 3 and 1 -5 5 1 6 +5 3 and 8 +3 -3 1 3 -2 4 and 8 +2 7 +2 6 -3 8 and -4 -2 -3 -2 -2 -2 1 and -5 -5 1 +3 3 1 -3 and 1 -3 3 -2 6 -2 8 and 4 -2 5 +2 3 -3 5 and 7 +2 6 +2 5 +2 3 and 1 1 2 1 3 1 4 and -3 1 3 -2 5 1 3 and 4 +2 3 +2 3 +2 3 and 1 1 8 -3 10 +3 6 and 3 +2 3 -2 4 +2 3 and 5 -2 6 -2 7 +2 6 and 8 +2 6 +2 4 +2 3 and -4 1 -3 -2 -2 -2 1 and 5 1 3 -2 5 -2 6 and 6 +2 5 1 4 1 3 and -2 -2 1 +3 -4 -2 -3 and 8 +3 5 1 4 1 3 and 3 1 2 1 1 1 -2 and 7 1 8 +2 7 1 6 and 6 -3 8 +2 7 1 6 and 1 1 3 +3 1 1 -2 and 6 1 5 1 3 1 4 and 5 +2 4 +2 1 1 2 and 4 1 5 -3 6 +2 5 and 6 -3 8 +2 6 -2 8 and 8 +2 7 1 6 -3 8 and 5 -3 3 -3 8 1 7 and 4 1 8 1 7 1 6 and -3 -2 -2 -2 5 -2 6 and 7 1 6 -2 8 +2 7 and 2 1 1 1 -2 1 -3 and 6 -2 8 +2 6 +2 4 and 8 +2 7 +2 5 +2 4 and 6 -5 10 1 9 +3 6 and 3 -2 3 -3 4 1 3 and 6 1 4 -2 5 +2 3 and -3 +2 -3 1 -6 -3 -3 and 2 +2 3 -5 8 +3 -3 and 5 1 1 -5 5 1 6 and 1 +3 3 1 -3 -2 -2 and 5 1 4 -3 6 -2 7 and 6 -2 7 +2 4 +2 3 and -4 -2 3 -3 5 +2 4 and 5 +5 1 -2 2 -2 -3 and 3 1 -3 -2 -2 -2 1 and 3 -2 3 +4 3 1 2 and 3 +2 3 1 4 -2 5 and 3 -2 3 1 1 -2 3 and 8 1 6 -2 8 +2 6 and 5 -3 7 1 6 -2 8 and -3 1 -6 -3 -3 +2 -3 and -3 1 -2 1 1 1 -3 and 6 1 7 1 8 1 6 and -3 -2 -2 -2 1 +3 -4 and 6 +3 3 -2 6 -2 8 and 7 1 8 +3 6 1 5 and 7 +2 5 -4 8 1 7 and 5 -2 6 -2 6 -2 6 and 2 -2 6 +2 5 1 4 and 6 -3 8 +3 5 1 4 and 6 -2 6 +2 6 -2 8 and 5 -2 6 -2 6 -2 8 and 4 1 3 -2 3 -3 5 and 5 +2 4 1 3 1 4 and -2 -2 5 -2 6 +2 1 and 6 1 5 +2 3 -2 3 and 3 -2 4 -2 6 1 4 and 3 1 5 -2 6 1 5 and 5 1 6 -3 8 +4 5 and 5 1 4 1 3 -2 3 and 6 +2 5 -3 7 1 6 and 5 1 4 1 3 -2 4 and 4 1 3 -3 6 -2 8 and 4 1 3 1 5 -2 6 and 5 -2 8 +2 7 +2 5 and 1 1 -2 1 -3 1 -4 and 10 +5 6 -5 10 1 9 and 2 1 3 -2 5 -2 6 and 7 +2 6 -2 7 +2 6 and 3 -3 5 +2 4 -2 3 and 5 +3 1 1 3 -2 4 and 6 +2 5 -3 3 -3 8 and -3 -2 -2 -2 1 1 2 and 6 1 8 +2 7 +2 6 and 4 1 6 +3 3 +2 2 and 8 +2 6 -3 8 +2 5 and 9 +3 6 -3 8 +3 5 and 3 +2 1 -3 3 -2 6 and 7 1 6 -3 8 +2 7 and 6 +3 3 +2 2 +2 3 and 3 1 2 +3 1 1 2 and 4 -2 5 1 3 -2 5 and 3 -3 4 1 3 +2 3 and 6 +2 5 +2 3 1 2 and 5 1 4 -2 3 1 4 and 4 -2 3 1 4 -2 5 and 8 +8 1 -2 2 -2 3 and 6 -3 8 +4 5 1 4 and 7 -2 8 1 7 +2 5 and 3 -2 4 -3 8 +2 7 and 5 +3 3 -2 4 -2 5 and 6 -2 8 +3 6 1 5 and -2 -5 5 +2 4 1 3 and 7 1 8 1 6 -2 8 and 3 1 4 -2 5 +2 3 and 2 1 1 1 2 -2 3 and 5 -2 8 +3 6 1 5 and 8 +2 7 +2 6 -2 7 and 6 -2 6 -2 6 +2 6 and 3 +5 -3 -2 -2 -2 1 and 3 +2 6 +4 3 -2 4 and 3 -2 4 +2 3 +2 3 and 3 1 4 1 5 -3 6 and 3 1 4 1 5 -3 7 and 4 -2 6 +8 -3 -2 -2 and 1 -2 2 -2 3 1 -3 and 5 -3 6 +2 5 1 4 and 5 1 6 1 7 1 8 and 4 -2 5 -2 6 -2 7 and 6 1 5 1 6 1 7 and 3 1 -3 -2 -2 -2 5 and 10 1 9 +3 6 -3 8 and 7 1 6 +2 5 -3 7 and 3 1 4 1 8 1 7 and 1 +3 -4 -2 -3 -2 -2 and 5 1 3 1 4 -2 6 and 7 +2 6 +2 5 -3 3 and -2 1 -3 +2 -3 1 -6 and 7 +2 5 +2 4 +2 1 and 4 +2 3 +2 3 -2 4 and 4 -3 8 +2 7 +2 6 and 4 -2 5 -2 8 +2 7 and 7 1 6 1 5 +2 4 and 6 +2 5 1 3 -2 6 and 4 -2 5 1 4 1 3 and 8 +2 7 +2 6 1 5 and 5 +2 4 -2 3 +4 3 and 5 +3 1 1 2 1 3 and 5 -3 7 1 6 +2 5 and 4 -2 6 1 4 -2 5 and -4 -2 3 -2 4 -2 5 and 5 -2 6 +2 1 1 2 and 5 -4 8 1 7 1 6 and -3 +2 -3 +2 -3 1 -2 and 2 +3 1 1 2 1 3 and 3 1 2 1 1 1 2 and -3 1 -4 1 -3 -2 -2 and 10 +3 6 1 8 +2 7 and -3 1 3 -2 4 -2 3 and 4 1 5 -3 7 1 6 and 3 -2 3 -3 5 +2 4 and 6 +2 1 1 2 1 3 and 6 1 5 1 4 1 8 and 7 +2 6 +2 5 1 3 and 4 -3 6 -2 7 1 6 and 8 +4 5 1 4 -2 3 and 3 +2 3 +2 3 -2 3 and 6 1 5 1 6 +3 3 and 5 -2 6 1 5 1 4 and 7 +2 -3 +2 -3 +2 -3 and 8 -3 10 +3 6 1 8 and -2 1 1 1 2 1 3 and 1 -2 2 -2 6 +2 5 and 6 -2 8 +2 7 +2 6 and 3 1 4 -2 6 +8 -3 and -6 -3 -3 +2 -3 1 -2 and 7 +2 4 +2 3 +2 3 and 3 +2 2 +2 3 -5 8 and 1 -2 2 -2 3 +2 6 and 6 +2 4 1 3 -3 6 and 3 -2 4 -2 5 1 3 and 3 -3 8 1 7 1 6 and 5 1 3 -2 6 -2 7 and 4 1 6 +3 3 -2 6 and 3 -5 8 +2 7 +2 6 and 6 1 7 1 8 +3 6 and 3 1 4 -2 5 1 4 and -3 +2 -3 1 -2 1 1 and 3 -2 6 -2 7 -2 8 and 3 1 4 -2 5 -2 6 and 1 -2 2 -2 -3 -2 -2 and 7 1 6 1 5 1 6 and 6 -2 7 +2 6 +2 4 and 6 -2 7 +2 6 +2 5 and 3 +2 3 1 1 -4 5 and 4 -2 5 +2 3 +5 -3 and 4 1 3 -2 4 -2 6 and 3 -2 4 +2 2 1 3 and 5 +2 4 1 3 +8 -5 and 8 1 7 +2 5 -4 8 and 6 +4 3 -2 4 +2 2 and 5 -2 6 -2 7 +2 4 and 1 -2 2 -2 3 1 4 and 8 +2 7 +2 -3 +2 -3 and -3 1 -4 1 -5 -2 -3 and 3 -3 3 1 4 -2 6 and -2 1 1 1 -3 -2 1
2: 5 -2 6 +2 3 +2 1 and 3 -2 4 -2 5 -2 6 and 4 -2 6 1 7 1 6 and 8 1 7 1 6 1 5 and 1 1 2 1 3 -2 3 and 3 -2 3 -2 3 -2 3 and -2 -2 1 -2 2 -2 3 and 3 -2 5 -3 8 +2 7 and 4 -3 6 1 5 +3 1 and 1 1 2 -2 3 +2 1 and 3 -2 5 -2 6 +2 3 and 8 +2 7 1 6 -2 8 and 6 1 7 1 6 1 5 and 1 1 3 -2 4 -3 6 and 4 -2 5 -2 6 -2 6 and 3 -2 4 -3 6 1 5 and 2 1 3 -2 3 -2 3 and 2 1 3 -2 5 -3 8 and 7 1 6 1 5 1 4
3: 8 +2 7 +2 6 +2 5 and 3 -2 4 -2 5 -2 8 and 1 1 2 1 3 -2 5 and 3 1 4 -2 6 1 7
4: -3 -2 -2 -2 1 -2 2

'''
      score = converter.parse( 'test_corpus/Jos2308.krn' )
      sets = VIS_Settings()
      sets.set_property( 'lookForTheseNs 4' )
      vis_these_parts( [score.parts[0], score.parts[1]], sets, self.vis )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by frequency' ), \
                        ascending_by_frequency )
# End Test_Output_Formatting() ------------------------------------------------



#-------------------------------------------------------------------------------
class TestVisTheseParts( unittest.TestCase ):
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
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )
      
      # Prepare the findings
      # NB: these are the same as test_theFirst()
      expected_compound_intervals = { 'P8':2, 'M9':1, 'M10':3, 'P12':4, \
            'm13':1, 'm17':1, 'M13':1, 'm10':4 }
      
      # Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
   
   
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
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':2, 'M9':1, 'M10':3, 'P12':4, \
            'm13':1, 'm17':1, 'M13':1, 'm10':4 }
      expected_no_quality2grams = { '8 1 9':1, '10 -2 12':1, '10 -4 12':1, \
            '13 -2 17':1, '17 +6 12':1, '9 1 10':1, '12 +4 10':1, '12 -2 13':1, \
            '12 -3 13':1, '13 +2 12':1, '12 +4 8':1, '8 -4 10':1, \
            '10 +4 10':1, '10 -2 10':3 }
      
      # Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
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
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      # Prepare the findings
      expected_compound_intervals = { 'm3':3, 'M3':2, 'P4':1, 'd5':2, 'm6':2, \
            'M6':2, 'M2':1, 'P5':1 }
      expected_no_quality2grams = { '3 +2 3':2, '3 1 4':1, '4 -2 5':1, '5 -2 6':2, \
            '6 -2 6':2, '6 +4 3':1, '3 1 2':1, '2 -2 3':1, '3 -2 5':1, '6 1 5':1 }

      # Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )

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
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats._compound_interval_dict )
      #pprint.pprint( self.stats._compound_no_quality_ngrams_dict[2] )

      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'M6':2, 'P4':3, 'M3':2, 'm3':2 }
      expected_no_quality2grams = { '8 +2 6':1, '4 1 3':1, '4 -3 3':1, \
            '6 +2 4':1, '3 1 4':2, '4 +3 3':1, '3 +2 3':1, '3 -5 6':1}#, \
            #'1 +2 2':1, '4 -2 3':1, '2 -2 1':1, '2 +2 1':1, '5 +3 3':1, \
            #'2 +2 3':1, '3 -2 2':1, '1 -2 2':1, '1 -2 5':1 }

      # Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
      
   def test_theSixthA( self ):
      # Two targeted testing excerpts.
      # A music21 Original
      # Just 2 arbitrary parts
      ## NB: This is designed to test an error that used to happen when one
      ## part has alternating notes and rests in a time when the other part has
      ## a note followed by a bunch of rests.
      
      from test_corpus.test_theSixth import the_first_piece
      higher_part = the_first_piece.parts[0]
      lower_part = the_first_piece.parts[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats._compound_interval_dict )
      #pprint.pprint( self.stats._compound_no_quality_ngrams_dict[2] )

      ## Prepare the findings
      expected_compound_intervals = { 'P11':1, 'm14':1 }
      expected_no_quality2grams = {}

      ## Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
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
      higher_part = the_second_piece.parts[0]
      lower_part = the_second_piece.parts[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats._compound_interval_dict )
      #pprint.pprint( self.stats._compound_no_quality_ngrams_dict[2] )

      ## Prepare the findings
      expected_compound_intervals = { 'P11':1, 'm14':1 }
      expected_no_quality2grams = {}

      ## Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
   def test_theSixthC( self ):
      # Two targeted testing excerpts.
      # A music21 Original
      # Just 2 arbitrary parts
      ## NB: This test reverses theSixthB, so the bottom voice woudl cause the
      ## problem caused by the top voice in the previous test.
      
      from test_corpus.test_theSixth import the_third_piece
      higher_part = the_third_piece.parts[0]
      lower_part = the_third_piece.parts[1]
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      #pprint.pprint( self.stats._compound_interval_dict )
      #pprint.pprint( self.stats._compound_no_quality_ngrams_dict[2] )

      ## Prepare the findings
      expected_compound_intervals = { 'P12':1, 'M9':1 }
      expected_no_quality2grams = {}

      ## Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
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
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )
      
      #pprint.pprint( self.stats._compound_interval_dict )
      ##pprint.pprint( self.stats._compound_no_quality_ngrams_dict[2] )
      
      ## Prepare the findings
      expected_compound_intervals = { 'P15':7, 'A11':1, 'M13':2, \
            'd14':5, 'A18':1, 'd18':2, 'A12':1, 'd19':1, 'A16':4, 'm13':1, \
            'm21':1, 'P22':4, 'm24':3, 'P26':5, 'm28':1, 'M24':1, 'M17':1, }
      expected_no_quality2grams = { '16 +2 15':3, '16 -4 18':1, '15 +1 14':3, \
            '15 -2 16':2, '15 +2 12':1, '15 -3 18':1, '14 +3 11':1, \
            '14 -1 15':2, '14 -1 13':2, '11 -3 14':1, '18 +1 18':1, \
            '18 +3 15':1, '18 -3 19':1, '12 -2 15':1, '19 +2 16':1, \
            '13 +1 14':1, '13 +2 13':1, '21 -1 22':1, '22 -2 24':2, \
            '22 +4 17':1, '24 -2 26':3, '24 1 22':1, '26 -2 28':1, \
            '26 1 24':1, '28 1 26':1, '13 -9 21':1 }
      
      ## Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
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
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )
      
      #pprint.pprint( self.stats._compound_interval_dict )
      #pprint.pprint( self.stats._compound_no_quality_ngrams_dict[2] )
      
      # Prepare the findings
      expected_compound_intervals = { 'P8':1, 'M6':2, 'P4':3, 'M3':2, 'm3':3, \
            'P1':2, 'M-2':1, 'm-3':2, 'P-4':1, 'P5':1 }
      expected_no_quality2grams = { '8 +2 6':1, '6 +2 4':1, '4 1 3':1, '3 1 4':2, \
            '4 -3 3':1, '4 +3 3':1, '3 +2 3':1, '3 -5 6':1, '1 +2 -2':1, \
            '-2 +2 -3':1, '-4 -2 -3':1, '-3 -3 1':1, '1 -2 5':1, '5 +3 3':1, \
            '-3 1 -4':1 }
      expected_quality2Grams = { 'P8 +m2 M6':1, 'M6 +M2 P4':1, 'P4 P1 M3':1, \
            'M3 P1 P4':1, 'P4 -m3 m3':1, 'm3 P1 P4':1, 'P4 +m3 M3':1, \
            'M3 +M2 m3':1, 'm3 -P5 M6':1, 'P1 +M2 M-2':1, 'M-2 +m2 m-3':1, \
            'P-4 -M2 m-3':1, 'm-3 -m3 P1':1, 'P1 -M2 P5':1, 'P5 +M3 m3':1, \
            'm-3 P1 P-4':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
      self.assertEqual( len(self.stats._compound_quality_ngrams_dict[2]), len(expected_quality2Grams) )
      self.assertEqual( self.stats._compound_quality_ngrams_dict[2], expected_quality2Grams )
   
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
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )

      # Prepare the findings
      expected_compound_intervals = { 'M6':5, 'M10':2, 'M9':2, 'P8':4, 'm6':1, \
            'P5':2, 'P4':2, 'M3':1, 'm-3':1, 'm-2':1, 'M2':2, 'm3':2 }
      expected_quality2Grams = { 'M6 -P5 M10':2, 'M10 P1 M9':2, 'M9 P1 P8':2, \
            'P8 +M2 M6':2, 'M6 -M2 P8':2, 'M6 +M2 m6':1, 'm6 -M3 P5':1, \
            'P5 +M2 P4':1, 'P4 +M2 P4':1, 'P4 -M2 M6':1, 'P8 +P5 M3':1, \
            'm-3 -M2 m-2':1, 'm-2 -m3 M2':1, 'M2 -m3 m3':1, 'm3 +m2 M2':1, \
            'M2 -m2 m3':1, 'm3 +m2 P5':1 }
      expected_no_quality2grams = { '6 -5 10':2, '10 1 9':2, '9 1 8':2, '8 +2 6':2, \
            '6 -2 8':2, '6 +2 6':1, '6 -3 5':1, '5 +2 4':1, '4 +2 4':1, \
            '4 -2 6':1, '8 +5 3':1, '-3 -2 -2':1, '-2 -3 2':1, '2 -3 3':1, \
            '3 +2 2':1, '2 -2 3':1, '3 +2 5':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
      self.assertEqual( len(self.stats._compound_quality_ngrams_dict[2]), len(expected_quality2Grams) )
      self.assertEqual( self.stats._compound_quality_ngrams_dict[2], expected_quality2Grams )
   
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

      ##pprint.pprint( self.stats._compound_interval_dict )
      ##pprint.pprint( self.stats._compound_no_quality_ngrams_dict[2] )

      ### Prepare the findings
      #expected_compound_intervals = { 'P8':3, 'm10':1, 'm9':1, 'M7':1, 'P5':1, \
         #'P4':2, 'P-15':1, 'm3':2, 'M2':1, 'A4':1, 'M3':1 }
      #expected_no_quality2grams = {}

      ### Verify the findings
      ##self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      #self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      ##self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      #self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
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

      ##pprint.pprint( self.stats._compound_interval_dict )
      ##pprint.pprint( self.stats._compound_no_quality_ngrams_dict[2] )

      ### Prepare the findings
      #expected_compound_intervals = { 'P8':3, 'm10':1, 'm9':1, 'M7':1, 'P5':1, \
         #'P4':1, 'P-15':1, 'm3':1, 'M2':1, 'M3':2, 'A4':1 }
      #expected_no_quality2grams = {}

      ### Verify the findings
      ##self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      #self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      ##self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      #self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
# NOTE: compare NoQuality 2-gram dictionaries
#for thing in self.stats._compound_no_quality_ngrams_dict[2].iterkeys():
   #if thing in expected_no_quality2grams:
      #if self.stats._compound_no_quality_ngrams_dict[2][thing] != expected_no_quality2grams[thing]:
         #print( 'for ' + thing + ', actual ' + str(self.stats._compound_no_quality_ngrams_dict[2][thing]) + ' != expected ' + str(expected_no_quality2grams[thing]) )
   #else:
      #print( 'actual ' + thing + ' isn\'t expected (there are ' + str(self.stats._compound_no_quality_ngrams_dict[2][thing]) + ')' )

#for thing in expected_no_quality2grams.iterkeys():
   #if thing in self.stats._compound_no_quality_ngrams_dict[2]:
      #if self.stats._compound_no_quality_ngrams_dict[2][thing] != expected_no_quality2grams[thing]:
         #print( 'for ' + thing + ', actual ' + str(self.stats._compound_no_quality_ngrams_dict[2][thing]) + ' != expected ' + str(expected_no_quality2grams[thing]) )
   #else:
      #print( 'expected ' + thing + ' isn\'t present' )

# NOTE: compare interval dictionaries
#for thing in self.stats._compound_interval_dict.iterkeys():
   #if thing in expected_compound_intervals:
      #if self.stats._compound_interval_dict[thing] != expected_compound_intervals[thing]:
         #print( 'for ' + thing + ', actual ' + str(self.stats._compound_interval_dict[thing]) + ' != expected ' + str(expected_compound_intervals[thing]) )
   #else:
      #print( 'actual ' + thing + ' isn\'t expected (there are ' + str(expected_compound_intervals[thing]) + ')' )

#for thing in expected_compound_intervals.iterkeys():
   #if thing in self.stats._compound_interval_dict:
      #if self.stats._compound_interval_dict[thing] != expected_compound_intervals[thing]:
         #print( 'for ' + thing + ', actual ' + str(self.stats._compound_interval_dict[thing]) + ' != expected ' + str(expected_compound_intervals[thing]) )
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
class TestVisThesePartsLong( unittest.TestCase ):
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
      analysis_time = vis_these_parts( [higher_part,lower_part], self.settings, self.stats )
      #print( '--> analysis took ' + str(analysis_time) + ' seconds' )
      
      # Prepare the findings
      expected_compound_intervals = { 'P1':12, 'M6':14, 'm7':4, 'P8':7, 'm10':7, \
            'm9':1, 'd4':5, 'm3':12, 'm6':24, 'M2':8, 'P5':13, 'P4':17, \
            'A4':1, 'M3':10, 'M-3':2, 'P-5':2, 'd5':3, 'd-5':1, 'm-6':1, \
            'M10':2, 'M9':4, 'P11':3, 'M-2':1, 'm-3':1, 'P-12':1 }
      
      # If voice crossing means negative intervals.
      expected_no_quality2grams = { '1 -2 6':1, '1 1 2':2, '1 -3 6':1, \
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
            '9 -3 10':1, '10 1 9':2, '10 1 6':1, '10 1 11':3, '11 +7 3':1 }
      
      # Verify the findings
      self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
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
      #self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      #self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      #self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[2]), len(expected_no_quality2grams) )
      #self.assertEqual( self.stats._compound_no_quality_ngrams_dict[2], expected_no_quality2grams )
   
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
      
      #for thing in self.stats._compound_interval_dict.iterkeys():
         #if thing in expected_compound_intervals:
            #if self.stats._compound_interval_dict[thing] != expected_compound_intervals[thing]:
               #print( 'for ' + thing + ', actual ' + str(self.stats._compound_interval_dict[thing]) + ' != expected ' + str(expected_compound_intervals[thing]) )
         #else:
            #print( 'actual ' + thing + ' isn\'t expected (there are ' + str(expected_compound_intervals[thing]) + ')' )

      #for thing in expected_compound_intervals.iterkeys():
         #if thing in self.stats._compound_interval_dict:
            #if self.stats._compound_interval_dict[thing] != expected_compound_intervals[thing]:
               #print( 'for ' + thing + ', actual ' + str(self.stats._compound_interval_dict[thing]) + ' != expected ' + str(expected_compound_intervals[thing]) )
         #else:
            #print( 'expected ' + thing + ' isn\'t present' )
      
      ## Verify the findings
      #self.assertEqual( len(self.stats._compound_interval_dict), len(expected_compound_intervals) )
      #self.assertEqual( self.stats._compound_interval_dict, expected_compound_intervals )
      ##self.assertEqual( len(self.stats._compound_no_quality_ngrams_dict[3]), len(expected_no_quality2grams) )
      ##self.assertEqual( self.stats._compound_no_quality_ngrams_dict[3], expected_no_quality2grams )
   
   
# End TestVisThesePartsLong ---------------------------------------------------



#------------------------------------------------------------------------------
class Test_Fill_Space_Between_Offsets( unittest.TestCase ):
   def test_the_basics( self ):
      self.assertEqual( fill_space_between_offsets( 0.0, 1.0 ), (1.0, []) )
      self.assertEqual( fill_space_between_offsets( 0.0, 4.0 ), (4.0, []) )
      self.assertEqual( fill_space_between_offsets( 0.0, 5.0 ), (4.0, [1.0]) )
      self.assertEqual( fill_space_between_offsets( 0.0, 8.0 ), (4.0, [4.0]) )
      self.assertEqual( fill_space_between_offsets( 0.0, 9.0 ), (4.0, [4.0, 1.0]) )
      self.assertEqual( fill_space_between_offsets( 4.5, 5.0 ), (0.5, []) )
      self.assertEqual( fill_space_between_offsets( 7693.5, 7703.0 ), (4.0, [4.0, 1.0, 0.5]) )
      self.assertEqual( fill_space_between_offsets( 0.0, 3.96875 ), (2.0, [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125] ) )
      self.assertEqual( fill_space_between_offsets( 3.96875, 7.9375 ), (2.0, [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125] ) )
      # This one is kind of ridiculous... thanks computers!
      rez = fill_space_between_offsets( 0.0, 3.03125000344 )
      exp = (2.0, [1.0, 0.03125, 0.00000000344])
      self.assertEqual( rez[0], exp[0] )
      self.assertEqual( rez[1][0], exp[1][0] )
      self.assertEqual( rez[1][1], exp[1][1] )
      self.assertAlmostEqual( rez[1][2], exp[1][2], 2 )
      #self.assertEqual( fill_space_between_offsets( ,  ), (, []) )
# End Test_Fill_Space_Between_Offsets -----------------------------------------



#-------------------------------------------------------------------------------
# "Main" Function
#-------------------------------------------------------------------------------
if __name__ == '__main__':
   print( "###############################################################################" )
   print( "## vis Test Suite                                                            ##" )
   print( "###############################################################################" )
   print( "" )
   # define test suites
   settingsSuite = unittest.TestLoader().loadTestsFromTestCase( TestSettings )
   sortingSuite = unittest.TestLoader().loadTestsFromTestCase( TestSorting )
   nGramSuite = unittest.TestLoader().loadTestsFromTestCase( TestNGram )
   verticalIntervalStatisticsSuite = unittest.TestLoader().loadTestsFromTestCase( TestVertical_Interval_Statistics )
   vis_these_partsSuite = unittest.TestLoader().loadTestsFromTestCase( TestVisTheseParts )
   vis_these_partsLongSuite = unittest.TestLoader().loadTestsFromTestCase( TestVisThesePartsLong )
   output_formatting_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Output_Formatting )
   fill_space_between_offsets_suite = unittest.TestLoader().loadTestsFromTestCase( Test_Fill_Space_Between_Offsets )

   # Run test suites for interface/background components
   unittest.TextTestRunner( verbosity = 2 ).run( settingsSuite )
      ##TODO: some sort of testing for the 'lookForTheseNs' settting
   unittest.TextTestRunner( verbosity = 2 ).run( sortingSuite )
   unittest.TextTestRunner( verbosity = 2 ).run( nGramSuite )
   unittest.TextTestRunner( verbosity = 2 ).run( verticalIntervalStatisticsSuite )
   unittest.TextTestRunner( verbosity = 2 ).run( output_formatting_suite )
   
   # Run test suites for analytic engine
   unittest.TextTestRunner( verbosity = 2 ).run( vis_these_partsSuite )
   unittest.TextTestRunner( verbosity = 2 ).run( vis_these_partsLongSuite )
   unittest.TextTestRunner( verbosity = 2 ).run( fill_space_between_offsets_suite )
   