#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
# 
# Filename: VIS_Settings.py
# Purpose: Provide a settings object for vis
#
# Attribution:  Based on the 'harrisonHarmony.py' module available at...
#               https://github.com/crantila/harrisonHarmony/
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



# Import
import re
from problems import NonsensicalInputError



# Class: VIS_Settings ----------------------------------------------
class VIS_Settings:
   # An internal class that holds settings for stuff.
   #
   # produceLabeledScore : whether to produce a score showing interval
   #     sequences, through LilyPond.
   # heedQuality : whether to pay attention to the quality of an interval
   #
   # NOTE: When you add a property, remember to test its default setting in
   # the unit test file.
   # 
   # NOTE: I'm going to keep the setting names in camel case because this is
   # the music21 convention, and it's probably a good idea for our users to
   # think consistently.
   def __init__( self ):
      self._secret_settings_hash = {}
      self._secret_settings_hash['produceLabeledScore'] = False
      self._secret_settings_hash['heedQuality'] = False
      self._secret_settings_hash['lookForTheseNs'] = [2]
      self._secret_settings_hash['offsetBetweenInterval'] = 0.5
      self._secret_settings_hash['outputResultsToFile'] = ''
      self._secret_settings_hash['simpleOrCompound'] = 'compound'
      #self._secret_settings_hash['n'] = [2] 
   
   # Helper method to test whether a str contains a boolean value.
   @staticmethod
   def _is_t_or_f( s ):
      s = s.lower()
      if 'true' == s or 'yes' == s or 'false' == s or 'no' == s:
         return True
      else:
         return False
   #-----
   
   # Helper method to turn the str boolean into a real boolean
   @staticmethod
   def _str_to_bool( s ):
      s = s.lower()
      if 'true' == s or 'yes' == s:
         return True
      elif 'false' == s or 'no' == s:
         return False
      else:
         return '' # panic?
   #-----
   
   # Helper method to parse a str-based list of 'n' into an actual
   # list of python int
   @staticmethod
   def _parse_list_of_n( ns ):
      '''
      Accepts a str and returns a sort()-ed list with all of the integers
      as separated by any non-integer characters, with duplicates removed.
      '''
      
      # This method courtesy of Greg Burlet.
      return sorted(set([int(n) for n in re.findall('(\d+)', ns)]))
   #-----
   
   def set_property( self, property_str ):
      # Parses 'property_str' and sets the specified property to the specified
      # value. Might later raise an exception if the property doesn't exist or
      # if the value is invalid.
      #
      # Examples:
      # a.set_property( 'chordLabelVerbosity concise' )
      # a.set_property( 'set chordLabelVerbosity concise' )
      
      # If the str starts with "set " then remove that
      if 'set ' == property_str[:4]:
         property_str = property_str[4:]
      
      # Check to make sure we still have a setting and a value
      setting = property_str[:property_str.find(' ')]
      value = property_str[property_str.find(' ')+1:]
      
      if 0 == len(setting):
         raise NonsensicalInputError( 'Unable to find setting name in "' + property_str + '"' )
      if 0 == len(value):
         raise NonsensicalInputError( 'Unable to find value in "' + property_str + '"' )
      
      # If the property requires a boolean value, make sure we have one
      if 'heedQuality' == setting or 'produceLabeledScore' == setting or \
            'produceLabelledScore' == setting:
         if not VIS_Settings._is_t_or_f( value ):
            raise NonsensicalInputError( \
                  'Value must be either True or False, but we got "' + \
                  str(value) + '"' )
         else:
            value = VIS_Settings._str_to_bool( value )
      
      # If the property is 'n' we need to parse the list of values into
      # a real list of int.
      if 'lookForTheseNs' == setting:
         value = VIS_Settings._parse_list_of_n( value )
      
      # now match the property
      if setting in self._secret_settings_hash:
         self._secret_settings_hash[setting] = value
      elif 'produceLabelledScore' == setting:
         self._secret_settings_hash['produceLabeledScore'] = value
      # We don't have that setting
      else:
         raise NonsensicalInputError( "Unrecognized setting name: " + setting)
   # end set_propety() ------------------------------------
   
   def get_property( self, property_str ):
      # Parses 'property_str' and returns the value of the specified property.
      # Might later raise an exception if the property doesn't exist.
      #
      # Examples:
      # a.get_property( 'chordLabelVerbosity' )
      # a.get_property( 'get chordLabelVerbosity' )
      
      # if the str starts with "get " then remove that
      if 'get ' == property_str[:4]:
         property_str = property_str[4:]

      # now match the property
      post = None
      if property_str in self._secret_settings_hash:
         post = self._secret_settings_hash[property_str]
      elif 'produceLabelledScore' == property_str:
         post = self._secret_settings_hash['produceLabeledScore']
      # unrecognized property
      else:
         raise NonsensicalInputError( "Unrecognized property: " + property_str )

      return post
# End Class: VIS_Settings ------------------------------------------
