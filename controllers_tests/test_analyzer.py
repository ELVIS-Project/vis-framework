#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         TestSorting.py
# Purpose:      Unit tests for the NGram class.
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



# Imports from...



class TestRunAnalysis(unittest.TestCase):
   # Test run_analysis()
   pass
# End TestRunAnalysis ----------------------------------------------------------



class TestEventFinder(unittest.TestCase):
   # Test _event_finder()
   pass
# End TestEventFinder ----------------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
run_analysis_suite = unittest.TestLoader().loadTestsFromTestCase(TestRunAnalysis)
event_finder_suite = unittest.TestLoader().loadTestsFromTestCase(TestEventFinder)
