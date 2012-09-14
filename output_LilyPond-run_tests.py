#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         output_LilyPond-run_tests.py
# Purpose:      Runs automated tests for output_LilyPond.py
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



# Confirmed Requirements:
import unittest
from output_LilyPond_unit_tests import *
from output_LilyPond_integration_tests import *



#-------------------------------------------------------------------------------
# "Main" Function
#-------------------------------------------------------------------------------
if __name__ == '__main__':
   print( "###############################################################################" )
   print( "## output_LilyPond Test Suite                                                ##" )
   print( "###############################################################################" )
   print( "" )

   # Unit Tests
   unittest.TextTestRunner( verbosity = 1 ).run( detect_lilypond_suite )
   unittest.TextTestRunner( verbosity = 1 ).run( t_o_n_t_l )
   unittest.TextTestRunner( verbosity = 1 ).run( t_p_t_l )
   unittest.TextTestRunner( verbosity = 1 ).run( t_d_t_l )
   unittest.TextTestRunner( verbosity = 1 ).run( t_n_t_l )
   unittest.TextTestRunner( verbosity = 1 ).run( t_b_t_l )

   # Run Integration Tests
   unittest.TextTestRunner( verbosity = 1 ).run( process_measure_suite )
   unittest.TextTestRunner( verbosity = 1 ).run( process_stream_part_suite )
