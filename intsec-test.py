#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         intsec-test.py
# Purpose:      Unit tests for intsec.py
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
from intsec import *
from music21 import interval
from music21 import note

## Import required libraries (this list is from the module)


#-------------------------------------------------------------------------------
class TestSettings( unittest.TestCase ):
   def setUp( self ):
      self.s = IntSecSettings()
   
   def test_default_init( self ):
      # Ensure all the settings are initialized to the proper default value.
      self.assertEqual( self.s._secretSettingsHash['produceLabeledScore'], False )
      self.assertEqual( self.s._secretSettingsHash['heedQuality'], False )
      self.assertEqual( self.s._secretSettingsHash['lookForTheseNs'], [2] )
   
   def test_set_some_things( self ):
      # Setting something to a new, valid value is done properly.
      self.s.parsePropertySet( 'set produceLabelledScore True' )
      self.assertEqual( self.s._secretSettingsHash['produceLabeledScore'], 'True' )
      self.s.parsePropertySet( 'produceLabelledScore False' )
      self.assertEqual( self.s._secretSettingsHash['produceLabeledScore'], 'False' )
   
   def test_get_some_things( self ):
      self.assertEqual( self.s.parsePropertyGet( 'produceLabeledScore' ), False )
      self.s._secretSettingsHash['produceLabeledScore'] = 'True'
      self.assertEqual( self.s.parsePropertyGet( 'produceLabeledScore' ), True )
      self.assertEqual( self.s.parsePropertyGet( 'produceLabelledScore' ), True )
   
   def test_get_invalid_setting( self ):
      self.assertRaises( NonsensicalInputError, self.s.parsePropertyGet, 'four score and five score' )
      self.assertRaises( NonsensicalInputError, self.s.parsePropertyGet, 'four' )
      self.assertRaises( NonsensicalInputError, self.s.parsePropertyGet, '' )
   
   def test_set_invalid_setting( self ):
      self.assertRaises( NonsensicalInputError, self.s.parsePropertySet, 'four score and five score' )
      self.assertRaises( NonsensicalInputError, self.s.parsePropertySet, 'fourscoreandfivescore' )
      self.assertRaises( NonsensicalInputError, self.s.parsePropertySet, '' )
   
   def test_set_to_invalid_value( self ):
      self.assertRaises( NonsensicalInputError, self.s.parsePropertySet, 'set produceLabeledScore five score' )
      self.assertRaises( NonsensicalInputError, self.s.parsePropertySet, 'produceLabeledScore five score' )

#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class TestIntervalSorter( unittest.TestCase ):
   def test_simple_cases( self ):
      self.assertEqual( intervalSorter( 'M3', 'P5' ), -1 )
      self.assertEqual( intervalSorter( 'm7', 'd4' ), 1 )
   
   def test_depends_on_quality( self ):
      self.assertEqual( intervalSorter( 'm3', 'M3' ), -1 )
      self.assertEqual( intervalSorter( 'M3', 'm3' ), 1 )
      self.assertEqual( intervalSorter( 'd3', 'm3' ), -1 )
      self.assertEqual( intervalSorter( 'M3', 'd3' ), 1 )
      self.assertEqual( intervalSorter( 'A3', 'M3' ), 1 )
      self.assertEqual( intervalSorter( 'd3', 'A3' ), -1 )
      self.assertEqual( intervalSorter( 'P4', 'A4' ), -1 )
      self.assertEqual( intervalSorter( 'A4', 'P4' ), 1 )
   
   def test_all_quality_equalities( self ):
      self.assertEqual( intervalSorter( 'M3', 'M3' ), 0 )
      self.assertEqual( intervalSorter( 'm3', 'm3' ), 0 )
      self.assertEqual( intervalSorter( 'd3', 'd3' ), 0 )
      self.assertEqual( intervalSorter( 'A3', 'A3' ), 0 )
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class TestNGram( unittest.TestCase ):
   def setUp( self ):
      # m3 u m3
      self.a = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C5'))]
      self.aDistance = [interval.Interval(note.Note('A4'),note.Note('A4'))]
      # m3 u M3
      self.b = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C#5'))]
      self.bDistance = [interval.Interval(note.Note('A4'),note.Note('A4'))]
      # m3 +P4 m3
      self.c = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('F5'))]
      self.cDistance = [interval.Interval(note.Note('A4'),note.Note('D5'))]
      # m-3 +P4 M3
      self.d = [interval.Interval(note.Note('C5'),note.Note('A4')), \
                interval.Interval(note.Note('D5'),note.Note('F#5'))]
      self.dDistance = [interval.Interval(note.Note('A4'),note.Note('D5'))]
      # m3 -P4 m3
      self.e = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('E4'),note.Note('G4'))]
      self.eDistance = [interval.Interval(note.Note('A4'),note.Note('E4'))]
      # m3 -P4 M-3
      self.f = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('G#4'),note.Note('E4'))]
      self.fDistance = [interval.Interval(note.Note('A4'),note.Note('E4'))]
      # m3 +P4 M2 -m6 P5 -m2 M-10
      self.g = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('E5')), \
                interval.Interval(note.Note('F#4'),note.Note('C#5')), \
                interval.Interval(note.Note('G##5'),note.Note('E#4'))]
      self.gDistance = [interval.Interval(note.Note('A4'),note.Note('D5')), \
                        interval.Interval(note.Note('D5'),note.Note('F#4')), \
                        interval.Interval(note.Note('F#4'),note.Note('E#4'))]
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
      self.assertEqual( x._listOfIntervals, self.a )
      #self.assertEqual( x.getIntervals(), self.a )
      y = NGram( self.g )
      self.assertEqual( y._listOfIntervals, self.g )
      #self.assertEqual( y.getIntervals(), self.g )
   
   def test_distance_calculations( self ):
      self.assertEqual( NGram( self.a )._listOfMovements, self.aDistance )
      self.assertEqual( NGram( self.b )._listOfMovements, self.bDistance )
      self.assertEqual( NGram( self.c )._listOfMovements, self.cDistance )
      self.assertEqual( NGram( self.d )._listOfMovements, self.dDistance )
      self.assertEqual( NGram( self.e )._listOfMovements, self.eDistance )
      self.assertEqual( NGram( self.f )._listOfMovements, self.fDistance )
      self.assertEqual( NGram( self.g )._listOfMovements, self.gDistance )
   
   def test_distance_calc_exception( self ):
      self.a = [interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval('m3')]
      self.assertRaises( NonsensicalInputError, NGram, self.a )
      try:
         self.g[2].noteEnd = None
      except AttributeError as e:
         pass
      self.assertRaises( NonsensicalInputError, NGram, self.g )
   
   def test_equality( self ):
      # if they have different heedQuality settings, they're not the same
      self.assertFalse( NGram( self.a ) == NGram( self.a, True ) )
      # if they aren't of the same "n," they're not the same
      self.assertFalse( NGram( self.a, False ) == NGram( self.g, False ) )
      self.assertFalse( NGram( self.a, True ) == NGram( self.g, True ) )
      # they're all equal to themselves if heedQuality
      self.assertTrue( NGram( self.a, True ) == NGram( self.a, True ) )
      self.assertTrue( NGram( self.b, True ) == NGram( self.b, True ) )
      self.assertTrue( NGram( self.c, True ) == NGram( self.c, True ) )
      self.assertTrue( NGram( self.d, True ) == NGram( self.d, True ) )
      self.assertTrue( NGram( self.e, True ) == NGram( self.e, True ) )
      self.assertTrue( NGram( self.f, True ) == NGram( self.f, True ) )
      self.assertTrue( NGram( self.g, True ) == NGram( self.g, True ) )
      # they're all not equal to the next ones if heedQuality
      self.assertFalse( NGram( self.a, True ) == NGram( self.b, True ) )
      self.assertFalse( NGram( self.b, True ) == NGram( self.c, True ) )
      self.assertFalse( NGram( self.c, True ) == NGram( self.d, True ) )
      self.assertFalse( NGram( self.d, True ) == NGram( self.e, True ) )
      self.assertFalse( NGram( self.e, True ) == NGram( self.f, True ) )
      self.assertFalse( NGram( self.f, True ) == NGram( self.g, True ) )
      self.assertFalse( NGram( self.g, True ) == NGram( self.a, True ) )
      # they're all equal to themselves if NOT heedQuality
      self.assertTrue( NGram( self.a, False ) == NGram( self.a, False ) )
      self.assertTrue( NGram( self.b, False ) == NGram( self.b, False ) )
      self.assertTrue( NGram( self.c, False ) == NGram( self.c, False ) )
      self.assertTrue( NGram( self.d, False ) == NGram( self.d, False ) )
      self.assertTrue( NGram( self.e, False ) == NGram( self.e, False ) )
      self.assertTrue( NGram( self.f, False ) == NGram( self.f, False ) )
      self.assertTrue( NGram( self.g, False ) == NGram( self.g, False ) )
      # these are additionally equal if NOT heedQuality
      self.assertTrue( NGram( self.a, False ) == NGram( self.b, False ) )
      self.assertTrue( NGram( self.c, False ) == NGram( self.d, False ) )
      self.assertTrue( NGram( self.e, False ) == NGram( self.f, False ) )
   
   def test_inequality( self ):
      # if they have different heedQuality settings, they're not the same
      self.assertTrue( NGram( self.a, False ) != NGram( self.a, True ) )
      # if they aren't of the same "n," they're not the same
      self.assertTrue( NGram( self.a, False ) != NGram( self.g, False ) )
      self.assertTrue( NGram( self.a, True ) != NGram( self.g, True ) )
      # they're all equal to themselves if heedQuality
      self.assertFalse( NGram( self.a, True ) != NGram( self.a, True ) )
      self.assertFalse( NGram( self.b, True ) != NGram( self.b, True ) )
      self.assertFalse( NGram( self.c, True ) != NGram( self.c, True ) )
      self.assertFalse( NGram( self.d, True ) != NGram( self.d, True ) )
      self.assertFalse( NGram( self.e, True ) != NGram( self.e, True ) )
      self.assertFalse( NGram( self.f, True ) != NGram( self.f, True ) )
      self.assertFalse( NGram( self.g, True ) != NGram( self.g, True ) )
      # they're all equal to themselves if NOT heedQuality
      self.assertFalse( NGram( self.a, False ) != NGram( self.a, False ) )
      self.assertFalse( NGram( self.b, False ) != NGram( self.b, False ) )
      self.assertFalse( NGram( self.c, False ) != NGram( self.c, False ) )
      self.assertFalse( NGram( self.d, False ) != NGram( self.d, False ) )
      self.assertFalse( NGram( self.e, False ) != NGram( self.e, False ) )
      self.assertFalse( NGram( self.f, False ) != NGram( self.f, False ) )
      self.assertFalse( NGram( self.g, False ) != NGram( self.g, False ) )
      # these are additionally equal if NOT heedQuality
      self.assertFalse( NGram( self.a, False ) != NGram( self.b, False ) )
      self.assertFalse( NGram( self.c, False ) != NGram( self.d, False ) )
      self.assertFalse( NGram( self.e, False ) != NGram( self.f, False ) )
   
   def test_str( self ):
      self.assertEqual( str(NGram(self.a,True)), 'm3 P1 m3' )
      self.assertEqual( str(NGram(self.b,True)), 'm3 P1 M3' )
      self.assertEqual( str(NGram(self.c,True)), 'm3 +P4 m3' )
      self.assertEqual( str(NGram(self.d,True)), 'm3 +P4 M3' )
      self.assertEqual( str(NGram(self.e,True)), 'm3 -P4 m3' )
      self.assertEqual( str(NGram(self.f,True)), 'm3 -P4 M3' )
      self.assertEqual( str(NGram(self.g,True)), 'm3 +P4 M2 -m6 P5 -m2 M10' )
      #
      self.assertEqual( str(NGram(self.a,False)), '3 1 3' )
      self.assertEqual( str(NGram(self.b,False)), '3 1 3' )
      self.assertEqual( str(NGram(self.c,False)), '3 +4 3' )
      self.assertEqual( str(NGram(self.d,False)), '3 +4 3' )
      self.assertEqual( str(NGram(self.e,False)), '3 -4 3' )
      self.assertEqual( str(NGram(self.f,False)), '3 -4 3' )
      self.assertEqual( str(NGram(self.g,False)), '3 +4 2 -6 5 -2 10' )
   
   def test_stringVersion( self ):
      self.assertEqual( NGram(self.a,True).stringVersion(heedQuality=True), 'm3 P1 m3' )
      self.assertEqual( NGram(self.b,True).stringVersion(heedQuality=True), 'm3 P1 M3' )
      self.assertEqual( NGram(self.c,True).stringVersion(heedQuality=True), 'm3 +P4 m3' )
      self.assertEqual( NGram(self.d,True).stringVersion(heedQuality=True), 'm3 +P4 M3' )
      self.assertEqual( NGram(self.e,True).stringVersion(heedQuality=True), 'm3 -P4 m3' )
      self.assertEqual( NGram(self.f,True).stringVersion(heedQuality=True), 'm3 -P4 M3' )
      self.assertEqual( NGram(self.g,True).stringVersion(heedQuality=True), 'm3 +P4 M2 -m6 P5 -m2 M10' )
      #
      self.assertEqual( NGram(self.a,False).stringVersion(heedQuality=True), 'm3 P1 m3' )
      self.assertEqual( NGram(self.b,False).stringVersion(heedQuality=True), 'm3 P1 M3' )
      self.assertEqual( NGram(self.c,False).stringVersion(heedQuality=True), 'm3 +P4 m3' )
      self.assertEqual( NGram(self.d,False).stringVersion(heedQuality=True), 'm3 +P4 M3' )
      self.assertEqual( NGram(self.e,False).stringVersion(heedQuality=True), 'm3 -P4 m3' )
      self.assertEqual( NGram(self.f,False).stringVersion(heedQuality=True), 'm3 -P4 M3' )
      self.assertEqual( NGram(self.g,False).stringVersion(heedQuality=True), 'm3 +P4 M2 -m6 P5 -m2 M10' )
      #
      self.assertEqual( NGram(self.a,True).stringVersion(heedQuality=False), '3 1 3' )
      self.assertEqual( NGram(self.b,True).stringVersion(heedQuality=False), '3 1 3' )
      self.assertEqual( NGram(self.c,True).stringVersion(heedQuality=False), '3 +4 3' )
      self.assertEqual( NGram(self.d,True).stringVersion(heedQuality=False), '3 +4 3' )
      self.assertEqual( NGram(self.e,True).stringVersion(heedQuality=False), '3 -4 3' )
      self.assertEqual( NGram(self.f,True).stringVersion(heedQuality=False), '3 -4 3' )
      self.assertEqual( NGram(self.g,True).stringVersion(heedQuality=False), '3 +4 2 -6 5 -2 10' )
      #
      self.assertEqual( NGram(self.a,False).stringVersion(heedQuality=False), '3 1 3' )
      self.assertEqual( NGram(self.b,False).stringVersion(heedQuality=False), '3 1 3' )
      self.assertEqual( NGram(self.c,False).stringVersion(heedQuality=False), '3 +4 3' )
      self.assertEqual( NGram(self.d,False).stringVersion(heedQuality=False), '3 +4 3' )
      self.assertEqual( NGram(self.e,False).stringVersion(heedQuality=False), '3 -4 3' )
      self.assertEqual( NGram(self.f,False).stringVersion(heedQuality=False), '3 -4 3' )
      self.assertEqual( NGram(self.g,False).stringVersion(heedQuality=False), '3 +4 2 -6 5 -2 10' )
      ####
      self.assertEqual( NGram(self.f,True).stringVersion(heedQuality=True,simpleOrCompound='simple'), 'm3 -P4 M3' )
      self.assertEqual( NGram(self.g,True).stringVersion(heedQuality=True,simpleOrCompound='simple'), 'm3 +P4 M2 -m6 P5 -m2 M3' )
      #
      self.assertEqual( NGram(self.f,False).stringVersion(heedQuality=True,simpleOrCompound='simple'), 'm3 -P4 M3' )
      self.assertEqual( NGram(self.g,False).stringVersion(heedQuality=True,simpleOrCompound='simple'), 'm3 +P4 M2 -m6 P5 -m2 M3' )
      #
      self.assertEqual( NGram(self.f,True).stringVersion(heedQuality=False,simpleOrCompound='simple'), '3 -4 3' )
      self.assertEqual( NGram(self.g,True).stringVersion(heedQuality=False,simpleOrCompound='simple'), '3 +4 2 -6 5 -2 3' )
      #
      self.assertEqual( NGram(self.f,False).stringVersion(heedQuality=False,simpleOrCompound='simple'), '3 -4 3' )
      self.assertEqual( NGram(self.g,False).stringVersion(heedQuality=False,simpleOrCompound='simple'), '3 +4 2 -6 5 -2 3' )
   
   def test_repr( self ):
      self.assertEqual( NGram(self.a,True).__repr__(), '<intsec.NGram m3 P1 m3>' )
      self.assertEqual( NGram(self.b,True).__repr__(), '<intsec.NGram m3 P1 M3>' )
      self.assertEqual( NGram(self.c,True).__repr__(), '<intsec.NGram m3 +P4 m3>' )
      self.assertEqual( NGram(self.d,True).__repr__(), '<intsec.NGram m3 +P4 M3>' )
      self.assertEqual( NGram(self.e,True).__repr__(), '<intsec.NGram m3 -P4 m3>' )
      self.assertEqual( NGram(self.f,True).__repr__(), '<intsec.NGram m3 -P4 M3>' )
      self.assertEqual( NGram(self.g,True).__repr__(), '<intsec.NGram m3 +P4 M2 -m6 P5 -m2 M10>' )
      #
      self.assertEqual( NGram(self.a,False).__repr__(), '<intsec.NGram 3 1 3>' )
      self.assertEqual( NGram(self.b,False).__repr__(), '<intsec.NGram 3 1 3>' )
      self.assertEqual( NGram(self.c,False).__repr__(), '<intsec.NGram 3 +4 3>' )
      self.assertEqual( NGram(self.d,False).__repr__(), '<intsec.NGram 3 +4 3>' )
      self.assertEqual( NGram(self.e,False).__repr__(), '<intsec.NGram 3 -4 3>' )
      self.assertEqual( NGram(self.f,False).__repr__(), '<intsec.NGram 3 -4 3>' )
      self.assertEqual( NGram(self.g,False).__repr__(), '<intsec.NGram 3 +4 2 -6 5 -2 10>' )
#------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class TestVerticalIntervalStatistics( unittest.TestCase ):
   def setUp( self ):
      self.vis = VerticalIntervalStatistics()
      self.m3 = interval.Interval( 'm3' )
      self.M3 = interval.Interval( 'M3' )
      self.m10 = interval.Interval( 'm10' )
      self.M10 = interval.Interval( 'M10' )
      # m3 u m3
      self.nga = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C5'))])
      # m3 u M3
      self.ngb = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('A4'),note.Note('C#5'))])
      # m3 +P4 m3
      self.ngc = NGram([interval.Interval(note.Note('A4'),note.Note('C5')), \
                interval.Interval(note.Note('D5'),note.Note('F5'))])
      # m-3 +P4 M3
      self.ngd = NGram([interval.Interval(note.Note('C5'),note.Note('A4')), \
                interval.Interval(note.Note('D5'),note.Note('F#5'))])
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
   
   def test_addInterval( self ):
      self.vis.addInterval( self.m3 )
      self.assertEqual( self.vis._simpleIntervalDict['m3'], 1 )
      self.assertEqual( self.vis._compoundIntervalDict['m3'], 1 )
      self.vis.addInterval( self.m10 )
      self.assertEqual( self.vis._simpleIntervalDict['m3'], 2 )
      self.assertEqual( self.vis._compoundIntervalDict['m3'], 1 )
      self.assertEqual( self.vis._compoundIntervalDict['m10'], 1 )
      self.vis.addInterval( self.M3 )
      self.assertEqual( self.vis._simpleIntervalDict['M3'], 1 )
      self.assertEqual( self.vis._compoundIntervalDict['M3'], 1 )
   
   def test_getIntervalOccurrences_heedQuality( self ):
      self.vis.addInterval( self.m3 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm3', 'simple' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M3', 'simple' ), 0 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm3', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M3', 'compound' ), 0 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm10', 'compound' ), 0 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M10', 'compound' ), 0 )
      self.vis.addInterval( self.m10 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm3', 'simple' ), 2 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M3', 'simple' ), 0 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm3', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M3', 'compound' ), 0 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm10', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M10', 'compound' ), 0 )
      self.vis.addInterval( self.M3 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm3', 'simple' ), 2 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M3', 'simple' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm3', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M3', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm10', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M10', 'compound' ), 0 )
      self.vis.addInterval( self.M10 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm3', 'simple' ), 2 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M3', 'simple' ), 2 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm3', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M3', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'm10', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'M10', 'compound' ), 1 )
   
   def test_getIntervalOccurrences_noHeedQuality( self ):
      self.vis.addInterval( self.m3 )
      self.assertEqual( self.vis.getIntervalOccurrences( '3', 'simple' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( '3', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( '10', 'compound' ), 0 )
      self.vis.addInterval( self.m10 )
      self.assertEqual( self.vis.getIntervalOccurrences( '3', 'simple' ), 2 )
      self.assertEqual( self.vis.getIntervalOccurrences( '3', 'compound' ), 1 )
      self.assertEqual( self.vis.getIntervalOccurrences( '10', 'compound' ), 1 )
      self.vis.addInterval( self.M3 )
      self.assertEqual( self.vis.getIntervalOccurrences( '3', 'simple' ), 3 )
      self.assertEqual( self.vis.getIntervalOccurrences( '3', 'compound' ), 2 )
      self.assertEqual( self.vis.getIntervalOccurrences( '10', 'compound' ), 1 )
      self.vis.addInterval( self.M10 )
      self.assertEqual( self.vis.getIntervalOccurrences( '3', 'simple' ), 4 )
      self.assertEqual( self.vis.getIntervalOccurrences( '3', 'compound' ), 2 )
      self.assertEqual( self.vis.getIntervalOccurrences( '10', 'compound' ), 2 )
   
   def test_getIntervalOccurrences_errors_and_zero( self ):
      self.assertEqual( self.vis.getIntervalOccurrences( 'P4', 'simple' ), 0 )
      self.assertEqual( self.vis.getIntervalOccurrences( 'P4', 'compound' ), 0 )
      self.assertEqual( self.vis.getIntervalOccurrences( '6', 'simple' ), 0 )
      self.assertEqual( self.vis.getIntervalOccurrences( '6', 'compound' ), 0 )
      self.assertRaises( NonsensicalInputError, self.vis.getIntervalOccurrences, 'P4', 'wrong3343' )
      self.assertRaises( NonsensicalInputError, self.vis.getIntervalOccurrences, 'P4', '' )
      self.assertRaises( NonsensicalInputError, self.vis.getIntervalOccurrences, 'P4', 5 )
      self.assertRaises( NonsensicalInputError, self.vis.getIntervalOccurrences, 'P4', False )
      self.assertRaises( NonsensicalInputError, self.vis.getIntervalOccurrences, 'P4', self.m3 )
   
   def test_addNGram( self ):
      # basic 2-gram
      self.vis.addNGram( self.ngc ) # m3 +P4 m3
      self.assertEqual( self.vis._compoundQualityNGramsDict[2], {'m3 +P4 m3': 1} )
      self.assertEqual( self.vis._compoundNoQualityNGramsDict[2], {'3 +4 3': 1} )
      # two of a basic 2-gram
      self.vis.addNGram( self.ngc ) # m3 +P4 m3
      self.assertEqual( self.vis._compoundQualityNGramsDict[2], {'m3 +P4 m3': 2} )
      self.assertEqual( self.vis._compoundNoQualityNGramsDict[2], {'3 +4 3': 2} )
      # add one of a similar 2-gram
      self.vis.addNGram( self.ngd ) # m-3 +P4 M3
      self.assertEqual( self.vis._compoundQualityNGramsDict[2], {'m3 +P4 m3': 2, 'm3 +P4 M3': 1} )
      self.assertEqual( self.vis._compoundNoQualityNGramsDict[2], {'3 +4 3': 3} )
      # add a 4-gram, 16 times
      for i in xrange(16):
         self.vis.addNGram( self.ngg ) # m3 +P4 M2 -m6 P5 -m2 M-10
      self.assertEqual( self.vis._compoundQualityNGramsDict[2], {'m3 +P4 m3': 2, 'm3 +P4 M3': 1} )
      self.assertEqual( self.vis._compoundQualityNGramsDict[4], {'m3 +P4 M2 -m6 P5 -m2 M10': 16} )
      self.assertEqual( self.vis._compoundNoQualityNGramsDict[2], {'3 +4 3': 3} )
      self.assertEqual( self.vis._compoundNoQualityNGramsDict[4], {'3 +4 2 -6 5 -2 10': 16} )
   
   def test_getNGramOccurrences( self ):
      # getNGramOccurrences( self, whichNGram, n )
      # test that non-existant n values are dealt with properly
      self.assertEqual( self.vis.getNGramOccurrences( '3 +4 3', n=2 ), 0 )
      self.assertEqual( self.vis.getNGramOccurrences( '3 +4 3', n=64 ), 0 )
      self.assertEqual( self.vis.getNGramOccurrences( '', n=2 ), 0 )
      self.assertEqual( self.vis.getNGramOccurrences( '', n=128 ), 0 )
      
      # test 2 n-grams
      # self.ngd:  m-3 +P4 M3
      # self.nge:  m3 -P4 m3
      self.vis = VerticalIntervalStatistics()
      for i in xrange(12):
         self.vis.addNGram( self.ngd )
      for i in xrange(8):
         self.vis.addNGram( self.nge )
      self.assertEqual( self.vis.getNGramOccurrences( 'm3 +P4 M3', n=2 ), 12 )
      self.assertEqual( self.vis.getNGramOccurrences( '3 +4 3', n=2 ), 12 )
      self.assertEqual( self.vis.getNGramOccurrences( 'm3 -P4 m3', n=2 ), 8 )
      self.assertEqual( self.vis.getNGramOccurrences( '3 -4 3', n=2 ), 8 )
      
      # test distinct 4-grams with identical simple-interval representations
      # self.ngg  m3 +P4 M2 -m6 P5 -m2 M10
      self.vis = VerticalIntervalStatistics()
      for i in xrange(10):
         self.vis.addNGram( self.ngg )
      self.assertEqual( self.vis.getNGramOccurrences( 'm3 +P4 M2 -m6 P5 -m2 M10', n=4 ), 10 )
      self.assertEqual( self.vis.getNGramOccurrences( '3 +4 2 -6 5 -2 10', n=4 ), 10 )
      self.assertEqual( self.vis.getNGramOccurrences( 'm3 +P4 M2 -m6 P5 -m2 M3', n=4 ), 0 )
      self.assertEqual( self.vis.getNGramOccurrences( '3 +4 2 -6 5 -2 3', n=4 ), 0 )
      # self.ngh  m3 +P4 M2 -m6 P5 -m2 M3
      for i in xrange(7):
         self.vis.addNGram( self.ngh )
      self.assertEqual( self.vis.getNGramOccurrences( 'm3 +P4 M2 -m6 P5 -m2 M10', n=4 ), 10 )
      self.assertEqual( self.vis.getNGramOccurrences( '3 +4 2 -6 5 -2 10', n=4 ), 10 )
      self.assertEqual( self.vis.getNGramOccurrences( 'm3 +P4 M2 -m6 P5 -m2 M3', n=4 ), 7 )
      self.assertEqual( self.vis.getNGramOccurrences( '3 +4 2 -6 5 -2 3', n=4 ), 7 )
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
# "Main" Function
#-------------------------------------------------------------------------------
if __name__ == '__main__':
   print( "###############################################################################" )
   print( "## IntSec Test Suite                                                         ##" )
   print( "###############################################################################" )
   print( "" )
   # define test suites
   settingsSuite = unittest.TestLoader().loadTestsFromTestCase( TestSettings )
   intervalSorterSuite = unittest.TestLoader().loadTestsFromTestCase( TestIntervalSorter )
   nGramSuite = unittest.TestLoader().loadTestsFromTestCase( TestNGram )
   verticalIntervalStatisticsSuite = unittest.TestLoader().loadTestsFromTestCase( TestVerticalIntervalStatistics )
   
   # run test suites
   #unittest.TextTestRunner( verbosity = 2 ).run( settingsSuite )
      # TODO: some sort of testing for the 'lookForTheseNs' settting
   #unittest.TextTestRunner( verbosity = 2 ).run( intervalSorterSuite )
   #unittest.TextTestRunner( verbosity = 2 ).run( nGramSuite )
   unittest.TextTestRunner( verbosity = 2 ).run( verticalIntervalStatisticsSuite )
   
   #unittest.main()


















