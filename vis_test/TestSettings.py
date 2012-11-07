#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         TestSettings.py
# Purpose:      Unit tests for VISSettings
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
from VISSettings import VISSettings
from problems import NonsensicalInputWarning

#-------------------------------------------------------------------------------
class TestSettings( unittest.TestCase ):
   def setUp( self ):
      self.s = VISSettings()

   def test_default_init( self ):
      # Ensure all the settings are initialized to the proper default value.
      self.assertEqual( self.s._secret_settings_hash['produceLabeledScore'], False )
      self.assertEqual( self.s._secret_settings_hash['heedQuality'], False )
      self.assertEqual( self.s._secret_settings_hash['lookForTheseNs'], [2] )
      self.assertEqual( self.s._secret_settings_hash['offsetBetweenInterval'], 0.5 )
      self.assertEqual( self.s._secret_settings_hash['outputResultsToFile'], '' )
      self.assertEqual( self.s._secret_settings_hash['simpleOrCompound'], 'compound' )

   def test_set_property_1( self ):
      # Setting something to a new, valid value is done properly.
      self.s.set_property( 'set produceLabelledScore True' )
      self.assertEqual( self.s._secret_settings_hash['produceLabeledScore'], True )
      self.s.set_property( 'produceLabelledScore False' )
      self.assertEqual( self.s._secret_settings_hash['produceLabeledScore'], False )

   def test_set_property_2( self ):
      # Invalid settings
      self.assertRaises( NonsensicalInputWarning, self.s.set_property, 'four score and five score' )
      self.assertRaises( NonsensicalInputWarning, self.s.set_property, 'fourscoreandfivescore' )
      self.assertRaises( NonsensicalInputWarning, self.s.set_property, '' )

   def test_set_property_3( self ):
      # Invalid value
      self.assertRaises( NonsensicalInputWarning, self.s.set_property, 'set produceLabeledScore five score' )
      self.assertRaises( NonsensicalInputWarning, self.s.set_property, 'produceLabeledScore five score' )

   def test_set_property_4( self ):
      # Ensure offsetBetweenInterval is done correctly.
      self.s.set_property( 'offsetBetweenInterval 0.6' )
      self.assertEqual( self.s._secret_settings_hash['offsetBetweenInterval'], 0.6 )
      self.assertRaises( NonsensicalInputWarning, self.s.set_property, 'offsetBetweenInterval pointfive' )

   def test_set_property_5A( self ):
      # Ensure outputResultsToFile is done correctly.
      self.s.set_property( 'outputResultsToFile /path/to/file' )
      self.assertEqual( self.s._secret_settings_hash['outputResultsToFile'], '/path/to/file' )

   def test_set_property_5B( self ):
      # Ensure outputResultsToFile is done correctly.
      self.s.set_property( 'outputResultsToFile None' )
      self.assertEqual( self.s._secret_settings_hash['outputResultsToFile'], '' )

   def test_get_property_1( self ):
      # Valid settings
      self.assertEqual( self.s.get_property( 'produceLabeledScore' ), False )
      self.s._secret_settings_hash['produceLabeledScore'] = True
      self.assertEqual( self.s.get_property( 'produceLabeledScore' ), True )
      self.assertEqual( self.s.get_property( 'produceLabelledScore' ), True )

   def test_get_property_2( self ):
      # Invalid settings
      self.assertRaises( NonsensicalInputWarning, self.s.get_property, 'four score and five score' )
      self.assertRaises( NonsensicalInputWarning, self.s.get_property, 'four' )
      self.assertRaises( NonsensicalInputWarning, self.s.get_property, '' )

   def test_n_parser( self ):
      # For the method _parse_list_of_n() which is called when users set the
      # "lookForTheseNs" property.
      self.assertEqual( VISSettings._parse_list_of_n( '1, 2, 3, 4, 5' ), \
                        [1, 2, 3, 4, 5] )
      self.assertEqual( VISSettings._parse_list_of_n( '[1,2,3,4,5]' ), \
                        [1, 2, 3, 4, 5] )
      self.assertEqual( VISSettings._parse_list_of_n( '[1, 2, 3, 4, 5]' ), \
                        [1, 2, 3, 4, 5] )
      self.assertEqual( VISSettings._parse_list_of_n( '[3, 2, 1, 4, 5]' ), \
                        [1, 2, 3, 4, 5] )
      self.assertEqual( VISSettings._parse_list_of_n( '[1, 3, 3, 2, 1]' ), \
                        [1, 2, 3] )
      self.assertEqual( VISSettings._parse_list_of_n( '8, 9, 10' ), \
                        [8, 9, 10] )
      self.assertEqual( VISSettings._parse_list_of_n( '8-:!9nanana10' ), \
                        [8, 9, 10] )
      self.assertEqual( VISSettings._parse_list_of_n( '42 6  12   ' ), \
                        [6, 12, 42] )
      self.assertEqual( VISSettings._parse_list_of_n( '6278 9180 1019 2, 1123' ), \
                        [2, 1019, 1123, 6278, 9180] )

   def test_export_settings( self ):
      actual = self.s.export_settings()
      # We can't guarantee the order in which the settings are printed, so we
      # have to use this less-good style of checking until I think of something.
      self.assertTrue( 'produceLabeledScore: False' in actual )
      self.assertTrue( 'heedQuality: False' in actual )
      self.assertTrue( 'lookForTheseNs: [2]' in actual )
      self.assertTrue( 'offsetBetweenInterval: 0.5' in actual )
      self.assertTrue( 'outputResultsToFile: ' in actual )

   def test_import_settings_1( self ):
      # For the first one, just set most things to their default values,
      # nothing difficult.
      set_str = 'produceLabeledScore: True\nheedQuality: True\nlookForTheseNs: [3]\noffsetBetweenInterval: 0.6\noutputResultsToFile: '
      self.s.import_settings( set_str )
      # Ensure all the settings are initialized to the proper default value.
      self.assertEqual( self.s._secret_settings_hash['produceLabeledScore'], True )
      self.assertEqual( self.s._secret_settings_hash['heedQuality'], True )
      self.assertEqual( self.s._secret_settings_hash['lookForTheseNs'], [3] )
      self.assertEqual( self.s._secret_settings_hash['offsetBetweenInterval'], 0.6 )
      self.assertEqual( self.s._secret_settings_hash['outputResultsToFile'], '' )

   #def test_import_settings_2( self ):
      ## More complicated stuff
      #set_str = ' produceLabeledScore:   True       \n   \n \n   heedQuality:    True\nlookForTheseNs: 2 and 4\n\noffsetBetweenInterval   :0.125   \n   outputResultsToFile: /home/christo/output.txt    \n \n   \n    '
      #self.s.import_settings( set_str )
      ## Ensure all the settings are initialized to the proper default value.
      #self.assertEqual( self.s._secret_settings_hash['produceLabeledScore'], True )
      #self.assertEqual( self.s._secret_settings_hash['heedQuality'], True )
      #self.assertEqual( self.s._secret_settings_hash['lookForTheseNs'], [2,4] )
      #self.assertEqual( self.s._secret_settings_hash['offsetBetweenInterval'], 0.125 )
      #self.assertEqual( self.s._secret_settings_hash['outputResultsToFile'], '/home/christo/output.txt' )

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( TestSettings )
