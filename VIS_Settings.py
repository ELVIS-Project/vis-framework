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
      self._secret_settings_hash['n'] = [2] 
   
   def set_property( self, property_str, prop_value = None ):
      # Parses 'property_str' and sets the specified property to the specified
      # value. Might later raise an exception if the property doesn't exist or
      # if the value is invalid.
      #
      # Examples:
      # a.set_property( 'chordLabelVerbosity concise' )
      # a.set_property( 'set chordLabelVerbosity concise' )
      
      # just tests whether a str is 'true' or 'True' or 'false' or 'False
      def is_t_or_f( s ):
         if 'true' == s or 'True' == s or 'false' == s or 'False' == s:
            return True
         else:
            return False
      ####
      if prop_value is None:
         # if the str starts with "set " then remove that
         if len(property_str) < 4:
            pass # panic
         elif 'set ' == property_str[:4]:
            property_str = property_str[4:]
               # check to make sure there's a property and a value
         spaceIndex = property_str.find(' ')
         if -1 == spaceIndex:
            pass #panic
     
         # make sure we have a proper 'true' or 'false' str if we need one
         if 'heedQuality' == property_str[:spaceIndex] or \
            'produceLabeledScore' == property_str[:spaceIndex] or \
            'produceLabelledScore' == property_str[:spaceIndex]:
               if not is_t_or_f( property_str[spaceIndex+1:] ):
                  raise NonsensicalInputError( "Value must be either True or False, but we got " + str(property_str[spaceIndex+1:]) )
      
         # now match the property
         if property_str[:spaceIndex] in self._secret_settings_hash:
            self._secret_settings_hash[property_str[:spaceIndex]] = property_str[spaceIndex+1:]
         elif 'produceLabelledScore' == property_str[:spaceIndex]:
            self._secret_settings_hash['produceLabeledScore'] = property_str[spaceIndex+1:]
         # unrecognized property
         else:
            raise NonsensicalInputError( "Unrecognized property: " + property_str[:spaceIndex])
      # So that we have a conventional setter as well, and we don't have to cast from string to list, etc
      else:
         if property_str in self._secret_settings_hash:
           self._secret_settings_hash[property_str] = prop_value
         else:
           raise NonsensicalInputError("Unrecognized property: " + property_str)
   
   def get_property( self, property_str ):
      # Parses 'property_str' and returns the value of the specified property.
      # Might later raise an exception if the property doesn't exist.
      #
      # Examples:
      # a.get_property( 'chordLabelVerbosity' )
      # a.get_property( 'get chordLabelVerbosity' )
      
      # if the str starts with "get " then remove that
      if len(property_str) < 4:
         pass # panic
      elif 'get ' == property_str[:4]:
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

      if 'True' == post or 'true' == post:
         return True
      elif 'False' == post or 'false' == post:
         return False
      else:
         return post
# End Class: VIS_Settings ------------------------------------------
