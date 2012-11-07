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
   unittest.TextTestRunner( verbosity = 2 ).run( TestSettings.suite )
   unittest.TextTestRunner( verbosity = 2 ).run( TestSorting.suite )
   unittest.TextTestRunner( verbosity = 2 ).run( TestNGram.suite )
   unittest.TextTestRunner( verbosity = 2 ).run( TestVerticalIntervalStatistics.suite )
   # NB: this one's broken, but all the other test suites should work
   #unittest.TextTestRunner( verbosity = 2 ).run( TestOutputFormatting.suite )

   # Suites for the Analysis Engine
   unittest.TextTestRunner( verbosity = 2 ).run( TestAnalysisEngineUnit.suite )
   unittest.TextTestRunner( verbosity = 2 ).run( TestAnalysisEngineIntegrationShort.suite )
   unittest.TextTestRunner( verbosity = 2 ).run( TestAnalysisEngineIntegrationLong.suite )
   unittest.TextTestRunner( verbosity = 2 ).run( TestOtherAnalysisEngine.suite )
