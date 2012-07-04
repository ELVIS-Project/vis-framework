#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
# 
# Filename: vis.py
# Purpose: Provide the interface for vis.
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

## For Debugging:
import pprint

## Import:
# python standard library
from os.path import exists as pathExists
# music21
from music21.instrument import Instrument
from music21 import converter
from music21.converter import ConverterException
from music21.converter import ConverterFileException
# vis
from outputLilyPond import processScore
from VerticalIntervalStatistics import VerticalIntervalStatistics, intervalSorter
from analyticEngine import visTheseParts
from NGram import NGram
from problems import NonsensicalInputError



#-------------------------------------------------------------------------------
def analyzeThis( pathname, theSettings = None ):#, verbosity = 'concise' ):
   '''
   Given the path to a music21-supported score, imports the score, performs a
   harmonic-functional analysis, annotates the score, and displays it with show().

   The second argument is optional, and takes the form of a str that is either
   'concise' or 'verbose', which will be passed to `labelThisChord()`, to
   display either verbose or concise labels.
   '''

   if None == theSettings:
      theSettings = visSettings()

   theStats = VerticalIntervalStatistics()
   theScore = None

   # See what input we have
   if isinstance( pathname, str ):
      ## get the score
      print( "Importing score to music21.\n" )
      try:
         theScore = converter.parse( pathname )
      except ConverterException:
         raise
      except ConverterFileException:
         raise
   elif isinstance( pathname, stream.Score ):
      theScore = pathname
   else:
      raise NonsensicalInputError( "analyzeThis(): input must be str or stream.Score; received " + str(type(pathname)) )

   # find out which 2 parts to investigate
   numberOfParts = len(theScore.parts)
   lookAtParts = [numberOfParts+5,numberOfParts+5]
   while lookAtParts[0] == lookAtParts[1] or lookAtParts[0] >= numberOfParts or lookAtParts[1] >= numberOfParts:
      print( "Please input the part numbers to investigate." )
      print( "From highest to lowest, these are the possibilities:" )
      # print something like "1 for Soprano"
      for i in xrange(numberOfParts):
         # Try to get a part name... there may not be an Instrument object. If
         # we don't find something, this will be what appears.
         partName = '(no part name)'
         for j in xrange(10):
            if isinstance( theScore.parts[i][0], Instrument ):
               partName = theScore.parts[i][0].bestName()
         #
         print( str(i) + " for " + partName )
      theirSpecification = raw_input( "Specify with higher part first.\n--> " )
      if 'help' == theirSpecification:
         print( "Just put in the two numbers with a space between them! // TODO: write more useful help here" )
      try:
         lookAtParts[0] = int(theirSpecification[0])
         lookAtParts[1] = int(theirSpecification[-1])
      except ValueError as valErr:
         # if something didn't work out with int()
         lookAtParts = [numberOfParts+5,numberOfParts+5]

   # must have taken the numbers!
   higher, lower = theScore.parts[lookAtParts[0]], theScore.parts[lookAtParts[1]]
   # This sometimes doesn't work, and it's a little silly anyway in a real program.
   #print( "We'll use " + higher[0].bestName() + ' and ' + lower[0].bestName() + ', okay!\n' )

   # find out what or which 'n' to look for
   print( "In the future, we'll ask which 'n' values to look for... for now it's just 2-grams.\n" )
   n = 2

   print( "Processing...\n" )
   itTook = visTheseParts( [higher,lower], theSettings, theStats )
   print( ' --> the analysis took ' + str(itTook) + ' seconds' )

   print( '-----------------------' )
   print( "Here are the intervals!" )
   #print( "Compound Intervals:" )
   pprint.pprint( theStats._compoundIntervalDict )
   pprint.pprint( sorted( theStats._compoundIntervalDict.items(), cmp=intervalSorter ) )
   #print( '-----------------------' )
   #print( "Those as Simple Intervals:" )
   #pprint.pprint( theStats._simpleIntervalDict )
   #pprint.pprint( sorted( theStats._simpleIntervalDict.items(), cmp=intervalSorter ) )

   print( "---------------------" )
   print( "Here are the n-grams!" )
   pprint.pprint( theStats._compoundQualityNGramsDict )
   pprint.pprint( theStats._compoundNoQualityNGramsDict )

   if theSettings.propertyGet( 'produceLabeledScore' ):
      print( "-----------------------------" )
      print( "Processing score for display." )
      # Use the built-in outputLilyPond.py module
      processScore( theScore )
   else:
      print( "----------------------------" )
      print( "Not producing labeled score." )
# End function analyzeThis() ---------------------------------------------------



# Class: visSettings ----------------------------------------------
class visSettings:
   # An internal class that holds settings for stuff.
   #
   # produceLabeledScore : whether to produce a score showing interval
   #     sequences, through LilyPond.
   # heedQuality : whether to pay attention to the quality of an interval
   #
   # NOTE: When you add a property, remember to test its default setting in
   # the unit test file.
   def __init__( self ):
      self._secretSettingsHash = {}
      self._secretSettingsHash['produceLabeledScore'] = False
      self._secretSettingsHash['heedQuality'] = False
      self._secretSettingsHash['lookForTheseNs'] = [2]
      self._secretSettingsHash['offsetBetweenInterval'] = 0.5
   
   def propertySet( self, propertyStr ):
      # TODO: rename this method "propertySet()"
      # Parses 'propertyStr' and sets the specified property to the specified
      # value. Might later raise an exception if the property doesn't exist or
      # if the value is invalid.
      #
      # Examples:
      # a.propertySet( 'chordLabelVerbosity concise' )
      # a.propertySet( 'set chordLabelVerbosity concise' )

      # just tests whether a str is 'true' or 'True' or 'false' or 'False
      def isTorF( s ):
         if 'true' == s or 'True' == s or 'false' == s or 'False' == s:
            return True
         else:
            return False
      ####

      # if the str starts with "set " then remove that
      if len(propertyStr) < 4:
         pass # panic
      elif 'set ' == propertyStr[:4]:
         propertyStr = propertyStr[4:]

      # check to make sure there's a property and a value
      spaceIndex = propertyStr.find(' ')
      if -1 == spaceIndex:
         pass #panic

      # make sure we have a proper 'true' or 'false' str if we need one
      if 'heedQuality' == propertyStr[:spaceIndex] or \
         'produceLabeledScore' == propertyStr[:spaceIndex] or \
         'produceLabelledScore' == propertyStr[:spaceIndex]:
            if not isTorF( propertyStr[spaceIndex+1:] ):
               raise NonsensicalInputError( "Value must be either True or False, but we got " + str(propertyStr[spaceIndex+1:]) )

      # TODO: some sort of parsing to allow us to set 'lookForTheseNs'

      # now match the property
      if propertyStr[:spaceIndex] in self._secretSettingsHash:
         self._secretSettingsHash[propertyStr[:spaceIndex]] = propertyStr[spaceIndex+1:]
      elif 'produceLabelledScore' == propertyStr[:spaceIndex]:
         self._secretSettingsHash['produceLabeledScore'] = propertyStr[spaceIndex+1:]
      # unrecognized property
      else:
         raise NonsensicalInputError( "Unrecognized property: " + propertyStr[:spaceIndex])

   def propertyGet( self, propertyStr ):
      # TODO: rename this method "propertyGet()"
      # Parses 'propertyStr' and returns the value of the specified property.
      # Might later raise an exception if the property doesn't exist.
      #
      # Examples:
      # a.propertyGet( 'chordLabelVerbosity' )
      # a.propertyGet( 'get chordLabelVerbosity' )

      # if the str starts with "get " then remove that
      if len(propertyStr) < 4:
         pass # panic
      elif 'get ' == propertyStr[:4]:
         propertyStr = propertyStr[4:]

      # now match the property
      post = None
      if propertyStr in self._secretSettingsHash:
         post = self._secretSettingsHash[propertyStr]
      elif 'produceLabelledScore' == propertyStr:
         post = self._secretSettingsHash['produceLabeledScore']
      # unrecognized property
      else:
         raise NonsensicalInputError( "Unrecognized property: " + propertyStr )

      if 'True' == post or 'true' == post:
         return True
      elif 'False' == post or 'false' == post:
         return False
      else:
         return post
# End Class: visSettings ------------------------------------------



# "main" function --------------------------------------------------------------
if __name__ == '__main__':
   print( "vis (Prerelease)\n" )
   print( "Copyright (C) 2012 Christopher Antila" )
   print( "This program comes with ABSOLUTELY NO WARRANTY; for details type 'show w'." )
   print( "This is free software; type 'show c' for details.\n" )
   print( "For a list of commands, type \'help\'." )

   mySettings = visSettings()
   exitProgram = False

   # See which command they wanted
   while False == exitProgram:
      userSays = raw_input( "vis @: " )
      # help
      if 'help' == userSays:
         print( "\nList of Commands:" )
         print( "-------------------" )
         print( "- 'exit' or 'quit' to exit or quit the program" )
         print( "- 'set' to set an option (see 'set help' for more information)" )
         print( "- 'get' to get the setting of an option (see 'get help')" )
         print( "- 'help settings' for a list of available settings" )
         print( "- a filename to analyze" )
         print( "- 'help filename' for help with file names" )
         print( "\n** Note: You can type 'help' at any user prompt for more information." )
         print( "" )
      elif 'exit' == userSays or 'quit' == userSays:
         print( "" )
         exitProgram = True
      # multi-word commands
      elif 0 < userSays.find(' '):
         if 'set' == userSays[:userSays.find(' ')]:
            if 'set help' == userSays:
               print( "You can change any of the settings described in the \'help settings\' command.\n" )
               print( "Just write 'set' followed by a space, the name of the property, and" )
               print( "the value you wish to set. If you mis-type a property or value name," )
               print( "vis will tell you, rather than failing with no feedback.\n" )
               print( "For example:\nset produceLabeledScore true" )
               print( "... but...\nset orderPizza true" )
               try:
                  mySettings.propertySet( 'orderPizza true' )
               except NonsensicalInputError as err:
                  print( 'Error: ' + str(err) )
               #print( "Unrecognized property: parduceLabeledScore" )
            else:
               try:
                  mySettings.propertySet( userSays )
               except NonsensicalInputError as e:
                  print( "Error: " + str(e) )
         elif 'get' == userSays[:userSays.find(' ')]:
            if 'get help' == userSays:
               print( "You can view any of the settings described in the \'help settings\' command.\n" )
               print( "Just write 'get' followed by a space and the name of the property. If" )
               print( "you mis-type a property name, vis may either guess at which property" )
               print( "meant, or tell you that it couldn't find a corresponding propety.\n" )
               print( "For example:\nget produceLabeledScore" )
               print( mySettings.propertyGet( 'produceLabeledScore' ) )
            else:
               try:
                  val = mySettings.propertyGet( userSays )
                  print( val )
               except NonsensiclaInputError as e:
                  print( "Error: " + str(e) )
         elif 'help' == userSays[:userSays.find(' ')]:
            if 'help settings' == userSays:
               print( "List of Settings:" )
               print( "=================" )
               print( "- produceLabeledScore: whether to produce a LilyPond score with n-gram diagrams." )
               print( "- heedQuality: whether to pay attention to the quality of an interval (major, minor)," )
               print( "        or just the size (5th, 6th)." )
               print( "- lookForTheseNs: a list of integers that are the values of 'n' (as in n-gram) that" )
               print( "        you want to look for. Type 'help settings lookForTheseNs' to see how to " )
               print( "        write the list of integers." )
               print( "- offsetBetweenInterval: a decimal number representing the 'granularity' with which" )
               print( "        to search for n-grams. Type 'help settings offsetBetweenInterval' for more." )
            elif 'help settings offsetBetweenInterval' == userSays:
               print( "This should be the value of music21's 'quarterLength' corresponding to the" )
               print( "   \"every ____ note\" you want to look for. For example, to check on \"every" )
               print( "   eighth note,\" you use 0.5, because that is the quarterLength value that" )
               print( "   means eighth note in music21.\n" )
               print( "   1.0 quarterLength means \"one quarter note,\" which explains why an eighth" )
               print( "   note has a quarterLength of 0.5." )
            elif 'help settings lookForTheseNs' == userSays:
               print( "Surprise--this setting doesn't actually work yet. When it does, you'll know." )
            elif 'help filename' == userSays:
               print( "Just type the filename. TODO: Say something useful about this." )
            else:
               print( "I don't have any help about " + userSays[userSays.find(' ')+1:] + " yet." )
         elif 'show w' == userSays:
            print( "\nvis is distributed in the hope that it will be useful," )
            print( "but WITHOUT ANY WARRANTY; without even the implied warranty of" )
            print( "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the" )
            print( "GNU General Public License for more details.\n" )
            print( "A copy of the licence is included in the vis directory in the" )
            print( "file called 'GPL.txt'\n" )
         elif 'show c' == userSays:
            print( "\nvis is free software: you can redistribute it and/or modify" )
            print( "it under the terms of the GNU General Public License as published by" )
            print( "the Free Software Foundation, either version 3 of the License, or" )
            print( "(at your option) any later version.\n" )
            print( "A copy of the licence is included in the vis directory in the" )
            print( "file called 'GPL.txt'\n" )
         else:
            print( "Unrecognized command or file name (" + userSays + ")" )
      else:
         if pathExists( userSays ):
            print( "Loading " + userSays + " for analysis." )
            try:
               analyzeThis( userSays, mySettings )
            except ConverterException as e:
               print( "--> music21 Error: " + str(e) )
            except ConverterFileException as e:
               print( "--> music21 Error: " + str(e) )
            except NonsensicalInputError as e:
               print( "--> Error from analyzeThis(): " + str(e) )
         else:
            print( "Unrecognized command or file name (" + userSays + ")" )
# End "main" function ----------------------------------------------------------