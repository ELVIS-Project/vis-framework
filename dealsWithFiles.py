#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         outputLilypond.py
# Purpose:      Outputs music21 Objects into LilyPond Format
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



#------------------------------------------------------------------------------
def fileOutputter( contents, filename ):
   '''
   Outputs the first argument, which should be a str, into a file whose name is
   specified as the second argument.
   '''
   
   # Sanity checks
   # Filename must be a str
   if not isinstance( filename, str ):
      filename = str(filename)
   # File mustn't already exist
   while exists( filename ):
      filename += '-0'
   # Output must must be a str.
   if not isinstance( contents, str ):
      contents = str(contents)
   
   # Open the file for writing
   try:
      outputFile = open( filename, 'w' )
   except Exception as exc:
      print( 'Error: ' + str(exc) )
   
   # Write the file.
   try:
      outputFile.write( contents )
   except Exception as exc:
      print( 'Error: ' + str(exc) )
   
   # Close the file.
   try:
      outputFile.close()
   except Exception as exc:
      print( 'Error: ' + str(exc) )
#------------------------------------------------------------------------------