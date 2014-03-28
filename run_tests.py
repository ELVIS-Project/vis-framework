#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: run_tests.py
# Purpose: Run the autmated tests for the models in vis.
#
# Copyright (C) 2012, 2013, 2014 Jamie Klassen, Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Run the tests for the models
"""

VERBOSITY = 1

# Imports
import unittest
from vis.tests import test_indexer, test_note_rest_indexer, test_ngram, test_repeat, \
    test_aggregator, test_interval_indexer, test_frequency_experimenter, test_offset, \
    test_lilypond
from vis.tests import test_indexed_piece, test_aggregated_pieces
from vis.tests import bwv2_integration_tests as bwv2
from vis.tests import test_workflow, test_workflow_integration, test_workflow_experiments

# Indexer and Subclasses
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.INDEXER_HARDCORE_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.INDEXER_1_PART_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.INDEXER_MULTI_EVENT_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.UNIQUE_OFFSETS_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexer.VERT_ALIGNER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_note_rest_indexer.NOTE_REST_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_interval_indexer.INTERVAL_INDEXER_SHORT_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_interval_indexer.INTERVAL_INDEXER_LONG_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_interval_indexer.INT_IND_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_interval_indexer.HORIZ_INT_IND_LONG_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_repeat.REPEAT_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_ngram.NGRAM_INDEXER_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_offset.OFFSET_INDEXER_SINGLE_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_offset.OFFSET_INDEXER_MULTI_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_lilypond.ANNOTATION_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_lilypond.ANNOTATE_NOTE_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_lilypond.PART_NOTES_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_lilypond.LILYPOND_SUITE)
# Experimenter and Subclasses
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_frequency_experimenter.FREQUENCY_FUNC_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_frequency_experimenter.FREQUENCY_RUN_SUITE)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_aggregator.COLUMN_AGGREGATOR_SUITE)
# IndexedPiece and AggregatedPieces
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexed_piece.INDEXED_PIECE_SUITE_A)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexed_piece.INDEXED_PIECE_SUITE_B)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_indexed_piece.INDEXED_PIECE_PARTS_TITLES)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_aggregated_pieces.AGGREGATED_PIECES_SUITE)
# WorkflowManager
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.WORKFLOW_TESTS)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.GET_DATA_FRAME)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.EXPORT)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.EXTRA_PAIRS)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.SETTINGS)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.OUTPUT)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.MAKE_HISTOGRAM)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.MAKE_LILYPOND)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow.AUX_METHODS)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow_experiments.INTERVAL_NGRAMS)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow_experiments.INTERVALS)
# Integration Tests
unittest.TextTestRunner(verbosity=VERBOSITY).run(bwv2.ALL_VOICE_INTERVAL_NGRAMS)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow_integration.INTERVALS_TESTS)
unittest.TextTestRunner(verbosity=VERBOSITY).run(test_workflow_integration.NGRAMS_TESTS)
