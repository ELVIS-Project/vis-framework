#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         Test_Settings.py
# Purpose:      Unit tests for VIS_Settings
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

#-------------------------------------------------------------------------------
class Test_Settings( unittest.TestCase ):
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
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( Test_Settings )
# TODO: some sort of testing for the 'lookForTheseNs' settting
