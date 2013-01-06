#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: run_tests.py
# Purpose: Run the autmated tests for the models in vis.
#
# Copyright (C) 2012 Jamie Klassen, Christopher Antila
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
Run the tests for the models
'''


# Imports
import unittest
from models_tests.test_importing import *
from models_tests.test_analyzing import *



# Models -----------------------------------------------------------------------
# Importing
unittest.TextTestRunner(verbosity=2).run(importing_basics_suite)
unittest.TextTestRunner(verbosity=2).run(importing_data_suite)
unittest.TextTestRunner(verbosity=2).run(importing_set_data_suite)
unittest.TextTestRunner(verbosity=2).run(importing_insert_rows_suite)
unittest.TextTestRunner(verbosity=2).run(importing_is_present_suite)
unittest.TextTestRunner(verbosity=2).run(importing_iterator_suite)
unittest.TextTestRunner(verbosity=2).run(importing_remove_rows_suite)



# Analyzing
unittest.TextTestRunner(verbosity=2).run(lop_basics_suite)
unittest.TextTestRunner(verbosity=2).run(lop_insert_and_remove_suite)
unittest.TextTestRunner(verbosity=2).run(lop_iterate_rows_suite)
unittest.TextTestRunner(verbosity=2).run(lop_set_data_suite)
unittest.TextTestRunner(verbosity=2).run(lop_header_data_suite)
unittest.TextTestRunner(verbosity=2).run(lop_data_suite)
