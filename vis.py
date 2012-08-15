#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
# 
# Filename: vis.py
# Purpose: Provide the text interface for vis.
#
# Attribution:  Based on the 'harrisonHarmony.py' module available at...
#               https://github.com/crantila/harrisonHarmony/
#
# Copyright (C) 2012 Christopher Antila, Jamie Klassen
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
from os.path import splitext
from os.path import exists as path_exists
from os.path import isdir, isfile
from os import walk as os_walk
import re
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
def analyze_this( pathname, the_settings = None, the_stats = None ):
   
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
   
   if the_stats is None:
      the_stats = Vertical_Interval_Statistics()
   
   list_of_filenames = []
   
   # See what input we have
   if isinstance( pathname, str ):
      # Is the pathname a directory?
      if isdir( pathname ):
         for a, b, filename in os_walk( pathname ):
            list_of_filenames.append( filename )
         list_of_filenames = list_of_filenames[0]
      # Is the pathname a file?
      elif isfile( pathname ):
         list_of_filenames.append( pathname )
      else:
         raise BadFileError( 'Given filename or directory name appears to be neither a file or directory.' )
   elif isinstance( pathname, stream.Score ):
      the_score = pathname
   else:
      raise BadFileError( "analyze_this(): input must be file name, directory name, or a stream.Score; received " + str(type(pathname)) )
   
   # Analysis: Multiple Pieces ----------------------------
   if len(list_of_filenames) > 1:
      # Find out which 2 parts they want us to investigate.
      print( "Please input the part numbers to investigate. 0 is the highest part; -1 is the lowest. Or 'all'" )
      print( "Remember the higher part goes first!" )
      parts_to_investigate = raw_input( '--> ' )
      # If the user isn't asking for all parts...
      if 'all' != parts_to_investigate:
         # Parse the input to pick out which parts they specified.
         parts_to_investigate = list(set([int(n) for n in re.findall('(-?\d+)', parts_to_investigate)]))
      
      cumulative_analysis_duration = 0.0
      
      # Holds a list of files that music21 was unable to analyze.
      files_not_analyzed = []
      
      ## Iterate through all the files, analyzing them.
      for filename in list_of_filenames:
         print( 'Trying ' + filename + '...' )
         try:
            the_score = converter.parse( pathname + '/' + filename )
         except ConverterException:
            print( '   failed during import' )
            files_not_analyzed.append( filename )
            continue
         except ConverterFileException:
            print( '   failed during import' )
            files_not_analyzed.append( filename )
            continue
         except Exception:
            print( '   failed during import' )
            files_not_analyzed.append( filename )
            continue
         print( '   successfully imported' )
         try:
            if 'all' == parts_to_investigate:
               # We have to examine all combinations of parts.
               # How many parts are in this piece?
               number_of_parts = len(the_score.parts)
               # Get a list of all the part-combinations to examine.
               parts_to_examine = calculate_all_combis( number_of_parts - 1 )
               # "Zero" it_took
               it_took = 0.0
               # Analyze every part combination.
               for set_of_parts in parts_to_examine:
                  higher = the_score.parts[set_of_parts[0]]
                  lower = the_score.parts[set_of_parts[1]]
                  it_took += vis_these_parts( [higher,lower], the_settings, the_stats )[0]
               # Add this duration to the cumulative duration.
               cumulative_analysis_duration += it_took
               # Print how long it took
               print( '   finished in ' + str(it_took) )
            else:
               # We should only examine the specified parts.
               # Get the two parts.
               higher = the_score.parts[parts_to_investigate[0]]
               lower = the_score.parts[parts_to_investigate[1]]
               # Run the analysis
               it_took = vis_these_parts( [higher,lower], the_settings, the_stats )[0]
               # Add this duration to the cumulative duration.
               cumulative_analysis_duration += it_took
               # Print this duration.
               print( '   finished in ' + str(it_took) )
         except Exception as exc:
            print( '   failed during analysis' )
            files_not_analyzed.append( filename )
            continue
      
      print( ' --> the analysis took ' + str(cumulative_analysis_duration) + ' seconds' )
      if len(files_not_analyzed) > 0:
         print( '*** Unable to analyze the following files:' )
         for filename in files_not_analyzed:
            print( filename )
   # Analysis: Single Piece -------------------------------
   else:
      # Import the score.
      print( "Importing score to music21.\n" )
      try:
         the_score = converter.parse( list_of_filenames[0] )
      except ConverterException:
         # This would happen when the filename doesn't exist.
         raise BadFileError( 'music21 reports this file does not exist: ' \
                              + list_of_filenames[0] )
      except ConverterFileException:
         # This would happen for an unsupported file type.
         raise BadFileError( 'music21 reports this file type is unsupported: ' \
                              + list_of_filenames[0] )
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
         print( '(or \'all\' to analyze all parts)' )
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
      
      # NB: I removed the "find out which 'n' to look for" part because users
      # should set this before they type the filename.
      
      print( "Processing...\n" )
      # TODO: update this section, and vis_these_parts(), to accept a list of
      # Part objects for LilyPond annotation, rather than a single Part object
      # that is the only possible annotation.
      it_took = 0.0
      ly = None
      if 'all' == look_at_parts:
         partsToExamine = calculate_all_combis( number_of_parts - 1 )
         for setOfParts in partsToExamine:
            higher, lower = the_score.parts[setOfParts[0]], the_score.parts[setOfParts[1]]
            it_took += vis_these_parts( [higher,lower], the_settings, the_stats )[0]
      else:
         higher, lower = the_score.parts[look_at_parts[0]], the_score.parts[look_at_parts[1]]
         it_took, ly = vis_these_parts( [higher,lower], the_settings, the_stats )
      
      print( ' --> the analysis took ' + str(it_took) + ' seconds' )
      
      if True == the_settings.get_property( 'produceLabelledScore' ):
         # Add the annotated part to the score
         the_score.append( ly )
         process_score( the_score )
         #process_score( the_score )
         # TODO: decide how to dynamically decide filename, then move this into
         # a sub-section of the "show" command in the "main" method.
   # End of "else" clause ---------------------------------
# End function analyze_this() ---------------------------------------------------



# "main" method --------------------------------------------------------------
if __name__ == '__main__':
   print( "vis (post-Milestone 1)\n" )
   print( "Copyright (C) 2012 Christopher Antila" )
   print( "This program comes with ABSOLUTELY NO WARRANTY; for details type 'warranty'." )
   print( "This is free software; type 'copyright' for details.\n" )
   print( "For a list of commands, type \'help\'." )

   my_settings = VIS_Settings()
   my_statistics = Vertical_Interval_Statistics()
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
      
      # Single-word Commands :
      
      # Help ----------------------------------------------
      if 'help' == user_says:
         print( """\nList of Commands:
-------------------
- 'exit' or 'quit' to exit or quit the program
- 'set' to set an option (see 'set help' for more information)
- 'get' to get the setting of an option (see 'get help')
- 'show' for guided display of results
- 'reset' to reset all settings and statistics
- 'help settings' for a list of available settings
- 'help filename' for help with file names
- a file name or directory/folder name to analyze

** Note: You can type 'help' at most user prompts for more information.
""" )
      elif 'exit' == user_says or 'quit' == user_says:
         print( "" )
         exit_program = True
      # Display of Results -----------------------------
      elif 'show' == user_says:
         which_results = raw_input( "Which results would you like to view? ('score' or 'ngrams' or 'intervals' or 'powerlaw' or 'retrogrades') " )
         if 'ngrams' == which_results:
            # NOTE: this is the same as for intervals, except for the call
            # to my_statistics.get_formatted_ngramss!!
            
            # Get the user's formatting options.
            format = 'help'
            while 'help' == format: 
               format = raw_input( "Please input formatting options, if any (or 'help'): " )
               if 'help' == format:
                  print( '''For n-grams, you can use the following options:
- 'by frequency' or 'by ngram' to decide by what to sort
- 'ascending'/'low to high' or 'descending'/'high to low' to decide the order
- 'n=3,4,5' for example, preceded and separated by a space or the start/end of the options,
  to control which 'n' values to show.
- 'graph' to see a bar graph of the results
- 'total' for the number of n-grams found (*not* the number of different kinds)
''' )
            #-----
            
            # Format the output.
            print( "Formatting output... " )
            try:
               formatted_output = my_statistics.get_formatted_ngrams( my_settings, format )
            except MissingInformationError as mie:
               # This error happens if all the user-specified 'n' values, or all
               # the possible 'n' values, have no n-grams associated.
               print( "Looks like the n-gram database is empty for the n values you specified." )
               continue
            
            # See whether they already set a file name.
            fn = my_settings.get_property( 'outputResultsToFile' )
            
            # If the filename is '' then they didn't set one.
            if len(fn) < 1:
               where = raw_input( "Output results to a file? ('yes' or 'no'): " )
               if 'yes' == where:
                  fn = raw_input( "Input a file name: " )
               elif 'no' == where:
                  if isinstance(formatted_output,basestring):
                     print( '\n' + formatted_output )
                  else:
                     for g in formatted_output:
                        g.show()
                  continue
               else:
                  print( "Please type 'yes' or 'no'" )
                  continue
            
            # If we're still going, we must be outputting to a file
            print( 'Writing results to ' + fn + ' ...' )
            if isinstance(formatted_output,basestring):
               file_output_result = file_outputter( formatted_output, fn )
               if file_output_result[1] is not None:
                  print( 'Encountered an error while attempting to write results to a file.\n' + \
                      file_output_result[1] )
               if file_output_result[0] is not fn:
                  print( 'Couldn\'t use <' + fn + '>, so results are in <' + \
                      file_output_result[0] + '>' )
            else: #must be an array of graphs
               for n in range(len(formatted_output)):
                  formatted_output[n].write(splitext(fn)[0]+'-'+str(n)+splitext(fn)[1])
       	 elif 'powerlaw' == which_results:
            try:
               power_law = my_statistics.power_law_analysis( my_settings )
            except MissingInformationError as mie:
               # This error happens if all the user-specified 'n' values, or all
               # the possible 'n' values, have no n-grams associated.
               print( "Looks like the n-gram database is empty for the n values you specified." )
               continue
            print power_law
         elif 'retrogrades' == which_results:
            format = 'help'
            while 'help' == format:
               format = raw_input("Please input formatting options, if any (or 'help'): ")
               if 'help' == format:
                  print('''You can use the following options:
-'by ratio' to sort the retrograde pairs by their ratio
- 'ascending'/'low to high' or 'descending'/'high to low' to decide the order
- 'quality' or 'noQuality' to distinguish between n-grams with different qualities
- 'graph' to see a bar graph of the results''')

            # Format the output.
            print( "Formatting output... " )
            formatted_output = my_statistics.retrogrades( my_settings, format )

            # See whether they already set a file name.
            fn = my_settings.get_property( 'outputResultsToFile' )

            # If the filename is '' then they didn't set one.
            if len(fn) < 1:
               where = raw_input( "Output results to a file? ('yes' or 'no'): " )
               if 'yes' == where:
                  fn = raw_input( "Input a file name: " )
               elif 'no' == where:
                  if isinstance(formatted_output,basestring):
                     print( '\n' + formatted_output )
                  else:
                     for g in formatted_output: 
                        g.show()
                  continue
               else:
                  print( "Please type 'yes' or 'no'" )
                  continue

            # If we're still going, we must be outputting to a file
            print( 'Writing results to ' + fn + ' ...' )
            if isinstance(formatted_output,basestring):
               file_output_result = file_outputter( formatted_output, fn )
               if file_output_result[1] is not None:
                  print( 'Encountered an error while attempting to write results to a file.\n' + \
                      file_output_result[1] )
               if file_output_result[0] is not fn:
                  print( 'Couldn\'t use <' + fn + '>, so results are in <' + \
                      file_output_result[0] + '>' )
            else: #must be an array of graphs
               for n in range(len(formatted_output)):
                  formatted_output[n].write(splitext(fn)[0]+'-'+str(n)+splitext(fn)[1])
         elif 'intervals' == which_results:
            # NOTE: this is the same as for ngrams, except for the call to 
            # my_statistics.get_formatted_intervals!!
            
            # Get the user's formatting options.
            format = 'help'
            while 'help' == format: 
               format = raw_input( "Please input formatting options, if any (or 'help'): " )
               if 'help' == format:
                  print( '''For intervals, you can use the following options:
- 'by frequency' or 'by interval' to decide by what to sort
- 'ascending'/'low to high' or 'descending'/'high to low' to decide the order
- 'simple' or 'compound' to determine which type of intervals to show; otherwise
  this is determined from your previous or the default settings
- 'graph' to see a bar graph of the results
- 'total' for the total number of intervals found (*not* the number of different kinds)
''' )
            #-----
            
            # Format the output.
            print( "Formatting output... " )
            formatted_output = my_statistics.get_formatted_intervals( my_settings, format )
            
            # See whether they already set a file name.
            fn = my_settings.get_property( 'outputResultsToFile' )
            
            # If the filename is '' then they didn't set one.
            if len(fn) < 1:
               where = raw_input( "Output results to a file? ('yes' or 'no'): " )
               if 'yes' == where:
                  fn = raw_input( "Input a file name: " )
               elif 'no' == where:
                  if isinstance(formatted_output,basestring):
                     print( '\n' + formatted_output )
                  else:
                     formatted_output.show()
                  continue
               else:
                  print( "Please type 'yes' or 'no'" )
                  continue
            
            # If we're still going, we must be outputting to a file
            print( 'Writing results to ' + fn + ' ...' )
            if isinstance(formatted_output,basestring):
               file_output_result = file_outputter( formatted_output, fn )
               if file_output_result[1] is not None:
                  print( 'Encountered an error while attempting to write results to a file.\n' + \
                      file_output_result[1] )
               if file_output_result[0] is not fn:
                  print( 'Couldn\'t use <' + fn + '>, so results are in <' + \
                      file_output_result[0] + '>' )
            else: #must be a graph
               formatted_output.write(fn)
         elif 'score' == which_results:
            print( 'At least for now, you still have to set the "produceLabelledScore" property.' )
         else:
            print( "Did you misspell something? And you call yourself \"university-educated\"..." )
      # Reset ------------------------------------------
      elif 'reset' == user_says:
         my_settings = VIS_Settings()
         my_statistics = Vertical_Interval_Statistics()
         print( "Settings and statistics reset." )
      # GPL Compliance ---------------------------------
      elif 'warranty' == user_says:
         print( "\nvis is distributed in the hope that it will be useful," )
         print( "but WITHOUT ANY WARRANTY; without even the implied warranty of" )
         print( "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the" )
         print( "GNU General Public License for more details.\n" )
         print( "A copy of the licence is included in the vis directory in the" )
         print( "file called 'GPL.txt'\n" )
      elif 'copyright' == user_says:
         print( "\nvis is free software: you can redistribute it and/or modify" )
         print( "it under the terms of the GNU General Public License as published by" )
         print( "the Free Software Foundation, either version 3 of the License, or" )
         print( "(at your option) any later version.\n" )
         print( "A copy of the licence is included in the vis directory in the" )
         print( "file called 'GPL.txt'\n" )
      # Temporary for Testing -----------------------------
      elif 'lytest' == user_says:
         print( "Running the LilyPond test." )
         my_settings.set_property( 'produceLabeledScore true' )
         analyze_this( 'test_corpus/bwv77.mxl', my_settings, my_statistics )
      
      # Multi-word Commands
      
      elif 0 < user_says.find(' '):
         # Set Setting ------------------------------------
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
         # Get Setting ------------------------------------
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
         # Help -------------------------------------------
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
         # Analyze a whole directory/folder ---------------
         #elif 'directory' == user_says[:user_says.find(' ')] or \
              #'folder' == user_says[:user_says.find(' ')] :
            #user_says = user_says[user_says.find(' ')+1:]
            #if path_exists( user_says ):
               #print( "Loading directory " + user_says + " for analysis." )
               #try:
                  #analyze_this( user_says, my_settings, my_statistics )
               #except BadFileError as bfe:
                  #print( 'Encountered a BadFileError while processing ' + user_says + '...' )
                  #print( str(bfe) )
            #else:
               #print( "Directory doesn't seem to exist: <" + user_says + ">" )
      else:
         if path_exists( user_says ):
            try:
               analyze_this( user_says, my_settings, my_statistics )
            except BadFileError as bfe:
               print( 'Encountered a BadFileError while processing ' + user_says + '...' )
               print( str(bfe) )
         else:
            print( "Unrecognized command or file name (" + user_says + ")" )
# End "main" function ----------------------------------------------------------
