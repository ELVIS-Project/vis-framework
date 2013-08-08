#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: run_tests.py
# Purpose: Run the autmated tests for the models in vis.
#
# Copyright (C) 2012, 2013 Jamie Klassen, Christopher Antila
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
"""
Run the tests for the models
"""

# Ensure we can import "vis"
try:
    import vis
except ImportError:
    import sys
    sys.path.insert(0, '..')

VERBOSITY = 1

# Imports
import unittest
from vis.analyzers_tests.test_interval_indexer import INTERVAL_INDEXER_SHORT_SUITE, \
    INTERVAL_INDEXER_LONG_SUITE, INT_IND_INDEXER_SUITE, HORIZ_INT_IND_LONG_SUITE
from vis.analyzers_tests.test_frequency_experimenter import FREQUENCY_FUNC_SUITE, \
    FREQUENCY_RUN_SUITE
# from vis.models_tests.test_indexed_piece import *
from vis.analyzers_tests.test_frequency_experimenter import *
from vis.analyzers_tests.test_offset import OFFSET_INDEXER_SUITE
from vis.models_tests.test_indexed_piece import *
from vis.controllers_tests.test_mpcontroller import MPC_TESTER_SUITE, MPCONTROLLER_SUITE, \
    MPCONTROLLER_RUNS_SUITE
from vis.analyzers_tests import test_indexer
from vis.analyzers_tests import test_note_rest_indexer
from vis.controllers_tests import test_mpcontroller

# New ---------------------------------------------------------------------------------------------
# Indexer and Subclasses
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.INDEXER_HARDCORE_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.INDEXER_1_PART_SUITE)
## TODO: this is lower priority, since it doesn't test meaningfully differently from
# INDEXER_1_PART_SUITE
##unittest.TextTestRunner(verbosity=verb).run(INDEXER_3_PARTS_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.UNIQUE_OFFSETS_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.VERT_ALIGNER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_note_rest_indexer.NOTE_REST_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(INTERVAL_INDEXER_SHORT_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(INTERVAL_INDEXER_LONG_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(INT_IND_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(HORIZ_INT_IND_LONG_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(OFFSET_INDEXER_SUITE)

# Experimenter and Subclasses
unittest.TextTestRunner(verbosity=VERBOSITY).run(FREQUENCY_FUNC_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(FREQUENCY_RUN_SUITE)

# IndexedPiece
#unittest.TextTestRunner(verbosity=verb).run(INDEXED_PIECE_SUITE)  # TODO: fails
# MPController
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_mpcontroller.MPC_TESTER_SUITE)
#unittest.TextTestRunner(verbosity=verb).run(MPCONTROLLER_SUITE)  # TODO: fails epically
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_mpcontroller.MPCONTROLLER_RUNS_SUITE)
