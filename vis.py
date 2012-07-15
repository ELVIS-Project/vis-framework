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
from os.path import exists as path_exists
# music21
from music21.instrument import Instrument
from music21 import converter
from music21.converter import ConverterException
from music21.converter import ConverterFileException
# vis
from output_LilyPond import process_score
# ngram_sorter only needed for the unit tests?
from Vertical_Interval_Statistics import Vertical_Interval_Statistics, interval_sorter, ngram_sorter
from analytic_engine import vis_these_parts
from NGram import NGram
from problems import *
from file_output import file_outputter
from VIS_Settings import VIS_Settings



#-------------------------------------------------------------------------------
def analyze_this( pathname, the_settings = None ):#, verbosity = 'concise' ):
   '''
   Given the path to a music21-supported score, imports the score, performs a
   harmonic-functional analysis, annotates the score, and displays it with show().

   The second argument is optional, and takes the form of a str that is either
   'concise' or 'verbose', which will be passed to `labelThisChord()`, to
   display either verbose or concise labels.
   '''
   
   #-------------------------------------------------------
   def calculate_all_combis( upto ):
      # Calculate all combinations of integers, up to a given integer.
      # 
      # Includes a 0th item... the argument should be len(whatevs) - 1.
      post = []
      for left in xrange(upto):
         for right in xrange(left+1,upto+1):
            post.append( [left,right] )
      return post
   #-------------------------------------------------------
   
   if the_settings is None:
      the_settings = VIS_Settings()
   
   the_stats = Vertical_Interval_Statistics()
   the_score = None
   
   # See what input we have
   if isinstance( pathname, str ):
      ## get the score
      print( "Importing score to music21.\n" )
      try:
         the_score = converter.parse( pathname )
      except Converter_Exception:
         # This would happen when the filename doesn't exist.
         raise BadFileError( 'music21 reports this file does not exist: ' \
                              + pathname )
      except Converter_File_Exception:
         # This would happen for an unsupported file type.
         raise BadFileError( 'music21 reports this file type is unsupported: ' \
                              + pathname )
   elif isinstance( pathname, stream.Score ):
      the_score = pathname
   else:
      raise BadFileError( "analyze_this(): input must be str or stream.Score; received " + str(type(pathname)) )
   
   # find out which 2 parts to investigate
   number_of_parts = len(the_score.parts)
   look_at_parts = [number_of_parts+5,number_of_parts+5]
   while look_at_parts[0] == look_at_parts[1] or look_at_parts[0] >= number_of_parts or look_at_parts[1] >= number_of_parts:
      print( "Please input the part numbers to investigate." )
      print( "From highest to lowest, these are the possibilities:" )
      # print something like "1 for Soprano"
      for i in xrange(number_of_parts):
         # Try to get a part name... there may not be an Instrument object. If
         # we don't find something, this will be what appears.
         part_name = '(no part name)'
         for j in xrange(10):
            if isinstance( the_score.parts[i][0], Instrument ):
               part_name = the_score.parts[i][0].bestName()
         #
         print( str(i) + " for " + part_name )
      their_specification = raw_input( "Specify with higher part first.\n--> " )
      if 'help' == their_specification:
         print( "Input the two numbers with a space between them, or type 'all'" )
      elif 'all' == their_specification:
         print( 'Comparing all voices!' )
         look_at_parts = 'all'
         break
      try:
         look_at_parts[0] = int(their_specification[0])
         look_at_parts[1] = int(their_specification[-1])
      except ValueError as val_err:
         # If something didn't work out with int() we can just ask for the
         # part specification again.
         print( 'Does not compute: ' + str(val_err) )
         look_at_parts = [number_of_parts+5,number_of_parts+5]
   #-----
   
   # find out what or which 'n' to look for
   n_list = raw_input( "Please input the desired values of n (as in n-gram). Default is n=2.\n--> ").split()
   if n_list is not '':
      the_settings.set_property( 'n', n_list )

   print( "Processing...\n" )
   it_took = 0.0
   if 'all' == look_at_parts:
      partsToExamine = calculate_all_combis( number_of_parts - 1 )
      for setOfParts in partsToExamine:
         higher, lower = the_score.parts[setOfParts[0]], the_score.parts[setOfParts[1]]
         it_took += vis_these_parts( [higher,lower], the_settings, the_stats )
   else:
      higher, lower = the_score.parts[look_at_parts[0]], the_score.parts[look_at_parts[1]]
      it_took = vis_these_parts( [higher,lower], the_settings, the_stats )
   #
   print( ' --> the analysis took ' + str(it_took) + ' seconds' )
   
   #-------------------------------------------------------
   # Prepare and Output Our Results
   #-------------------------------------------------------
   
   # Parse what we'll output
   parsed_output = the_stats.get_formatted_intervals( the_settings ) + \
                  the_stats.get_formatted_ngrams( the_settings )
   # If this has anything, we'll assume it's a filename to use for output.
   possible_file = the_settings.get_property( 'outputResultsToFile' )
   if len(possible_file) > 0:
      print( '----------------------' )
      print( 'Outputting results to ' + possible_file )
      output_feedback = file_outputter( parsed_output, possible_file )
      if output_feedback[1] is not None:
         print( 'Encountered an error while attempting to write results to a file.\n' + \
               output_feedback[1] )
   else:
      print( '---------------------' )
      print( 'Here are the results!' )
      print( parsed_output )
   
   if the_settings.get_property( 'produceLabeledScore' ):
      print( "-----------------------------" )
      print( "Processing score for display." )
      # Use the built-in output_LilyPond.py module
      process_score( the_score )
   else:
      print( "----------------------------" )
      print( "Not producing labeled score." )
   
   #
   print( '' )
# End function analyze_this() ---------------------------------------------------



# "main" function --------------------------------------------------------------
if __name__ == '__main__':
   print( "vis (Prerelease)\n" )
   print( "Copyright (C) 2012 Christopher Antila" )
   print( "This program comes with ABSOLUTELY NO WARRANTY; for details type 'show w'." )
   print( "This is free software; type 'show c' for details.\n" )
   print( "For a list of commands, type \'help\'." )

   my_settings = VIS_Settings()
   exit_program = False

   # See which command they wanted
   while False == exit_program:
      try:
         user_says = raw_input( "vis @: " )
      except EOFError as eof:
         # Fine, we'll just quit
         user_says = 'quit'
      except KeyboardInterrupt as kbi:
         # Fine, we'll just exit
         user_says = 'exit'
      # help
      if 'help' == user_says:
         print( """\nList of Commands:
-------------------
- 'exit' or 'quit' to exit or quit the program
- 'set' to set an option (see 'set help' for more information)
- 'get' to get the setting of an option (see 'get help')
- 'help settings' for a list of available settings
- a filename to analyze
- 'help filename' for help with file names

** Note: You can type 'help' at any user prompt for more information.
""" )
      elif 'exit' == user_says or 'quit' == user_says:
         print( "" )
         exit_program = True
      # multi-word commands
      elif 0 < user_says.find(' '):
         if 'set' == user_says[:user_says.find(' ')]:
            if 'set help' == user_says:
               print( """
You can change any of the settings described in the \'help settings\' command.

Just write 'set' followed by a space, the name of the property, and
the value you wish to set. If you mis-type a property or value name,
vis will tell you, rather than failing with no feedback.

For example:
set produceLabeledScore true

... but...
set orderPizza true
""" )
               try:
                  my_settings.set_property( 'orderPizza true' )
               except NonsensicalInputError as err:
                  print( 'Unable to set property: ' + str(err) + "\n" )
            else:
               try:
                  my_settings.set_property( user_says )
               except NonsensicalInputError as e:
                  print( "Unable to set property: " + str(e) )
         elif 'get' == user_says[:user_says.find(' ')]:
            if 'get help' == user_says:
               print( "You can view any of the settings described in the \'help settings\' command.\n" )
               print( "Just write 'get' followed by a space and the name of the property. If" )
               print( "you mis-type a property name, vis may either guess at which property" )
               print( "meant, or tell you that it couldn't find a corresponding propety.\n" )
               print( "For example:\nget produceLabeledScore" )
               print( my_settings.get_property( 'produceLabeledScore' ) )
            else:
               try:
                  val = my_settings.get_property( user_says )
                  print( val )
               except NonsensicalInputError as e:
                  print( "Unable to get property: " + str(e) )
         elif 'help' == user_says[:user_says.find(' ')]:
            if 'help settings' == user_says:
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
               print( "- outputResultsToFile: the filename to output to, or nothing to disable output to a file." )
            elif 'help settings offsetBetweenInterval' == user_says:
               print( "This should be the value of music21's 'quarterLength' corresponding to the" )
               print( "   \"every ____ note\" you want to look for. For example, to check on \"every" )
               print( "   eighth note,\" you use 0.5, because that is the quarterLength value that" )
               print( "   means eighth note in music21.\n" )
               print( "   1.0 quarterLength means \"one quarter note,\" which explains why an eighth" )
               print( "   note has a quarterLength of 0.5." )
            elif 'help settings lookForTheseNs' == user_says:
               print( "Surprise--this setting doesn't actually work yet. When it does, you'll know." )
            elif 'help filename' == user_says:
               print( "Just type the filename. TODO: Say something useful about this." )
            else:
               print( "I don't have any help about " + user_says[user_says.find(' ')+1:] + " yet." )
         elif 'show w' == user_says:
            print( "\nvis is distributed in the hope that it will be useful," )
            print( "but WITHOUT ANY WARRANTY; without even the implied warranty of" )
            print( "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the" )
            print( "GNU General Public License for more details.\n" )
            print( "A copy of the licence is included in the vis directory in the" )
            print( "file called 'GPL.txt'\n" )
         elif 'show c' == user_says:
            print( "\nvis is free software: you can redistribute it and/or modify" )
            print( "it under the terms of the GNU General Public License as published by" )
            print( "the Free Software Foundation, either version 3 of the License, or" )
            print( "(at your option) any later version.\n" )
            print( "A copy of the licence is included in the vis directory in the" )
            print( "file called 'GPL.txt'\n" )
         else:
            print( "Unrecognized command or file name (" + user_says + ")" )
      else:
         if path_exists( user_says ):
            print( "Loading " + user_says + " for analysis." )
            try:
               analyze_this( user_says, my_settings )
            except BadFileError as bfe:
               print( 'Encountered a BadFileError while processing ' + user_says + '...' )
               print( str(bfe) )
         else:
            print( "Unrecognized command or file name (" + user_says + ")" )
# End "main" function ----------------------------------------------------------
