#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Filename: problems.py
# Purpose: Exceptions and Errors for vis
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



#-------------------------------------------------------------------------------
class NonsensicalInputError( Exception ):
   '''
   VIS uses this error for situations where a user-provided value does not
   make sense, and the only recourse is to stop execution.
   
   For example: if we are setting accepting a user's preferred value for whether
   or not to pay attention to interval quality, and they tell us 'cheese'.
   '''
   
   # NB: This class has a name in camel case so it fits in with the built-in
   # Python exceptions and errors.
   
   def __init__( self, val ):
      self.value = val
   def __str__( self ):
      return repr( self.value )
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class NonsensicalInputWarning( Exception ):
   '''
   VIS uses this error for situations where an argument does not make sense,
   but we can somehow continue execution.
   
   For example: TODO
   '''
   
   # NB: This class has a name in camel case so it fits in with the built-in
   # Python exceptions and errors.
   
   def __init__( self, val ):
      self.value = val
   def __str__( self ):
      return repr( self.value )
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class MissingInformationError( Exception ):
   '''
   VIS uses this error when there is insufficient information to continue
   processing, and execution must be stopped.
   
   For example: if we are to find the interval between the lower notes of two
   Interval objects, but the Interval objects do not have Note objects
   associated, and therefore could be any distance apart.
   '''
   
   # NB: This class has a name in camel case so it fits in with the built-in
   # Python exceptions and errors.
   
   def __init__( self, val ):
      self.value = val
   def __str__( self ):
      return repr( self.value )
#-------------------------------------------------------------------------------
