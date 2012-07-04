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
   The error that I'm using for vis. This should potentially be
   replaced with more useful errors.
   '''
   def __init__( self, val ):
      self.value = val
   def __str__( self ):
      return repr( self.value )
#-------------------------------------------------------------------------------
