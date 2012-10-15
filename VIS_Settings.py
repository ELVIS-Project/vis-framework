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
from problems import NonsensicalInputWarning
import string
from file_output import file_outputter, file_inputter
from output_LilyPond import detect_lilypond, make_lily_version_numbers



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
      self._secret_settings_hash['recurse'] = False
      self._secret_settings_hash['lookForTheseNs'] = [2]
      self._secret_settings_hash['offsetBetweenInterval'] = 0.5
      self._secret_settings_hash['outputResultsToFile'] = ''
      self._secret_settings_hash['simpleOrCompound'] = 'compound'
      res = detect_lilypond()
      self._secret_settings_hash['lilypondPath'] = res[0]
      self._secret_settings_hash['lilypondVersion'] = res[1]
      self._secret_settings_hash['lilypondVersionNumbers'] = \
         make_lily_version_numbers( res[1] )
      self._secret_settings_hash['topX'] = None
      self._secret_settings_hash['threshold'] = None
      self._secret_settings_hash['sortBy'] = 'frequency'
      self._secret_settings_hash['sortOrder'] = 'descending'
      self._secret_settings_hash['showTheseNs'] = [2]
      self._secret_settings_hash['outputFormat'] = 'graph'
      self._secret_settings_hash['content'] = 'ngrams'

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
      # WARNING: generate_summary_score() in __main__.py uses this method!

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

      # Check to make sure we have a setting and a value
      setting = property_str[:property_str.find(' ')]
      value = property_str[property_str.find(' ')+1:]

      if 0 == len(setting):
         raise NonsensicalInputWarning( 'Unable to find setting name in "' + property_str + '"' )
      if 0 == len(value):
         raise NonsensicalInputWarning( 'Unable to find value in "' + property_str + '"' )

      # If the property requires a boolean value, make sure we have one
      if 'heedQuality' == setting or 'produceLabeledScore' == setting or \
            'produceLabelledScore' == setting or 'recurse' == setting:
         if not VIS_Settings._is_t_or_f( value ):
            raise NonsensicalInputWarning( \
                  'Value must be either True or False, but we got "' + \
                  str(value) + '"' )
         else:
            value = VIS_Settings._str_to_bool( value )

      # If the property is 'n' we need to parse the list of values into
      # a real list of int.
      if 'lookForTheseNs' == setting or 'showTheseNs' == setting:
         value = VIS_Settings._parse_list_of_n( value )

      if 'threshold' == setting or 'topX' == setting:
         try:
            value = int(value)
         except ValueError as vale:
            msg = 'Invalid value for '+setting+'; ignoring'
            raise NonsensicalInputWarning( msg )

      # If the property is 'offsetBetweenInterval' then make sure we have an
      # int for this, not a str
      if 'offsetBetweenInterval' == setting:
         try:
            value = float(value)
         except ValueError as vale:
            msg = 'Invalid value for offsetBetweenInterval; ignoring'
            raise NonsensicalInputWarning( msg )

      # If the property is 'outputResultsToFile' and the value is 'None' then
      # the value should actually be ''
      if 'outputResultsToFile' == setting and 'None' == value:
         value = ''

      # now match the property
      if setting in self._secret_settings_hash:
         self._secret_settings_hash[setting] = value
      elif 'produceLabelledScore' == setting:
         self._secret_settings_hash['produceLabeledScore'] = value
      # We don't have that setting
      else:
         raise NonsensicalInputWarning( "Unrecognized setting name: " + setting )
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
         raise NonsensicalInputWarning( "Unrecognized property: " + property_str )

      return post

   def import_settings( self, import_from ):
      '''
      Given a str with settings, modifies self to have the same settings.

      The str should be of the format outputted by export_settings()

      TODO: deal with test_import_settings_2()
      '''

      # Make a list of all the newline-separated fragments.
      list_of_settings = []
      while 0 < len(import_from):
         # Find the newline (nli = new line index)
         nli = import_from.find( '\n' )
         # If there isn't one, we're at the end of the file, so everything
         # goes in as the final setting.
         if 0 > nli:
            list_of_settings.append( import_from )
            import_from = ''
         # Otherwise, take everything up to the newline and add it as the next
         # setting, then remove the newline.
         else:
            this_setting = import_from[:nli]
            list_of_settings.append( this_setting )
            import_from = import_from[nli+1:]

      # Prepare each setting and send it to set_property()
      for setting in list_of_settings:
         # If there is no ':' then there is no setting, so ignore this.
         if 0 > setting.find( ':' ):
            continue
         else:
            # Otherwise, strip the setting.
            setting = string.strip( setting, ' \n' )
            # Remove the ':'
            setting = string.replace( setting, ':', '' )
            # If the setting is 'outputResultsToFile' but there is no filename,
            # add 'None' so set_property() can pick this up.
            if 'outputResultsToFile' == setting:
               setting += ' None'
            # Send it to set_property()
            self.set_property( setting )
   # ------------------------------------------------------

   def export_settings( self ):
      '''
      Exports the settings of self to a str. Each setting is written on one
      line, with a semicolon separating the setting name (on the left) from the
      setting value (on the right).
      '''

      # Hold the str that will have settings in it.
      post = ''

      # Go through every setting, and output it.
      for key in self._secret_settings_hash.iterkeys():
         post += str(key) + ': ' + str(self._secret_settings_hash[key]) + '\n'

      return post

   def save_settings( self, filename ):
      '''
      When called with a filename, this method puts the result of
      self.export_settings() into the specified file.
      '''
      file_outputter( self.export_settings(), filename )

   def load_settings( self, filename ):
      '''
      When called with a filename, this method puts the contents of that file
      through self.import_settings().
      '''
      self.import_settings( file_inputter( filename ) )

# End Class: VIS_Settings -----------------------------------------------------
