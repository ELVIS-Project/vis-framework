#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         file_output.py
# Purpose:      Outputs files for vis and output_LilyPond
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

# Import:
# python standard library
from os.path import exists
from os import access, W_OK
import fileinput
# vis
from problems import BadFileError



#------------------------------------------------------------------------------
def file_outputter( contents, filename, extension='' ):
   '''
   Outputs the first argument, which should be a str, into a file whose name is
   specified as the second argument.
   
   Return value is a two-element list. Index 0 is the filename we either did or
   attempted to output, and index 1 is a descriptive str error message or None
   if relevant.
   
   Use the method like this:
   >>> from file_output import file_outputter
   >>> output_this = 'Lots of stuff in this file!\n'
   >>> output_result = file_outputter( output_this, 'file', 'txt' )
   >>> if output_result[0] is not None:
   >>>    print( 'We had an error! ' + output_result[0] )
   >>> else:
   >>>    print( 'File successfully outputted to ' + output_result[0]
   '''
   
   # Sanity checks
   # Filename must be a str
   if not isinstance( filename, str ):
      filename = str(filename)
   # Unless we got the OVERWRITE signal, the file mustn't already exist.
   if 'OVERWRITE' != extension:
      while exists( filename + extension ):
         filename += '-0'
   else:
      # We need to do this, or else we'll inadvertently *not* overwrite the
      # pre-existing file.
      extension = ''
   # Output must be a str.
   if not isinstance( contents, str ):
      contents = str(contents)
   
   # Store a description of a possible error
   return_error = None
   
   # Open the file for writing
   try:
      output_file = open( filename+extension, 'w' )
   except IOError as ioe:
      return_error = 'Unable to open file for writing (' + filename + extension + ') because of exception: '+str(ioe)
      return [filename, return_error]
   
   # Write the file.
   try:
      output_file.write( contents )
   except IOError as ioe:
      return_error = 'Unable to write contents into the file.'
   
   # Close the file.
   try:
      output_file.close()
   except IOError as ioe:
      return_error = 'Unble to close the file (' + filename + extension + ')'
   
   # Return the filename we actually used.
   return [filename, return_error]
#-------------------------------------------------------------------------------



#------------------------------------------------------------------------------
def file_inputter( filename ):
   '''
   Reads the file with the path specified as a str, and returns its contents.
   '''
   
   # Sanity checks
   # Filename must be a str
   if not isinstance( filename, str ):
      filename = str(filename)
   # File must exist
   if not exists( filename ):
      raise BadFileError( 'File does not seem to exist.' )
   
   the_file = ''
   
   for line in fileinput.input( filename ):
      the_file += line
   
   return the_file
#------------------------------------------------------------------------------
