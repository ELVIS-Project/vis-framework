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
import imp
try:
    imp.find_module(u'vis')
except ImportError:
    import sys
    sys.path.insert(0, u'..')

VERBOSITY = 1

# Imports
import unittest
from vis.analyzers_tests.test_interval_indexer import INTERVAL_INDEXER_SHORT_SUITE, \
    INTERVAL_INDEXER_LONG_SUITE, INT_IND_INDEXER_SUITE, HORIZ_INT_IND_LONG_SUITE
from vis.analyzers_tests import test_frequency_experimenter
from vis.models_tests.test_indexed_piece import INDEXED_PIECE_SUITE
from vis.analyzers_tests.test_offset import OFFSET_INDEXER_SINGLE_SUITE, OFFSET_INDEXER_MULTI_SUITE
from vis.analyzers_tests import test_indexer, test_note_rest_indexer, test_ngram, test_repeat, \
    test_aggregator
#from vis.controllers_tests import test_mpinterface

# Indexer and Subclasses
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.INDEXER_HARDCORE_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.INDEXER_1_PART_SUITE)
# TODO: make this suite pass, and be quite different from INDEXER_1_PART_SUITE
#unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.INDEXER_3_PARTS_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.UNIQUE_OFFSETS_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.VERT_ALIGNER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_note_rest_indexer.NOTE_REST_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(INTERVAL_INDEXER_SHORT_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(INTERVAL_INDEXER_LONG_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(INT_IND_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(HORIZ_INT_IND_LONG_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(OFFSET_INDEXER_SINGLE_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(OFFSET_INDEXER_MULTI_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_repeat.REPEAT_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_ngram.NGRAM_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_aggregator.COLUMN_AGGREGATOR_SUITE)
# Experimenter and Subclasses
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_frequency_experimenter.FREQUENCY_FUNC_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_frequency_experimenter.FREQUENCY_RUN_SUITE)
# IndexedPiece and AggregatedPieces
unittest.TextTestRunner(verbosity=VERBOSITY).run(INDEXED_PIECE_SUITE)
# MPInterface
#unittest.TextTestRunner(verbosity=VERBOSITY).run(test_mpinterface.MPINTERFACE_SUITE)
