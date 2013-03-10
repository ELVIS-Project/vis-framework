#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Filename: coreproblems.py
# Purpose: Core exceptions and errors for vis
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
'''
This module contains errors and warnings for the "vis" program.
'''



class NonsensicalInputError( Exception ):
   '''
   VIS uses this error for situations where a user-provided value does not
   make sense, and the only recourse is to stop execution.

   For example: if we are setting accepting a user's preferred value for whether
   or not to pay attention to interval quality, and they tell us 'cheese'.
   '''

   pass



class NonsensicalInputWarning( Warning ):
   '''
   VIS uses this error for situations where an argument does not make sense,
   but we can somehow continue execution.

   For example: setting a property to an invalid value. It'll just be ignored.
   '''

   pass



class MissingInformationError( Exception ):
   '''
   VIS uses this error when there is insufficient information to continue
   processing, and execution must be stopped.

   For example: if we are to find the interval between the lower notes of two
   Interval objects, but the Interval objects do not have Note objects
   associated, and therefore could be any distance apart.
   '''

   pass



class BadFileError( Exception ):
   '''
   VIS uses this error when there is a problem loading or handling a file, not
   related to a more specific musical element.
   '''

   pass



class IncompatibleSetupError( Exception ):
   '''
   VIS uses this error when there is a problem with either the setup of VIS
   itself, or of the system on which it's operating.

   For example: VIS will not create a colour for the 2.15.x series of LilyPond
   because there was an incompatible change at some point. Therefore a system
   with LilyPond 2.15.x is an incompatible setup.
   '''

   pass
