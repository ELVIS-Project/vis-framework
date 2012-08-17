#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         vis-test.py
# Purpose:      Unit test runner for vis
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



import unittest
from vis_test import *



#-------------------------------------------------------------------------------
# "Main" Function
#-------------------------------------------------------------------------------
if __name__ == '__main__':
   print( "###############################################################################" )
   print( "## vis Test Suite                                                            ##" )
   print( "###############################################################################" )
   print( "" )
   # Suite for the interface/background components
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_Settings.suite )
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_Sorting.suite )
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_NGram.suite )
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_Vertical_Interval_Statistics.suite )
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_Output_Formatting.suite )
   
   # Suites for the Analysis Engine
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_Analysis_Engine_Unit.suite )
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_Analysis_Engine_Integration_Short.suite )
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_Analysis_Engine_Integration_Long.suite )
   #unittest.TextTestRunner( verbosity = 2 ).run( Test_Fill_Space_Between_Offsets.suite )
