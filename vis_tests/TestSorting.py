#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         TestSorting.py
# Purpose:      Unit tests for interval_sorter() and ngram_sorter() in the
#               VerticalIntervalStatistics package.
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
from VerticalIntervalStatistics import interval_sorter, ngram_sorter



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
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( TestSorting )
