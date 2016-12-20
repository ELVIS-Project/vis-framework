#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: run_tests.py
# Purpose: Run automated tests for the VIS Framework.
#
# Copyright (C) 2012, 2013, 2014 Jamie Klassen, Christopher Antila, Ryan Bannon, Alexander Morgan
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
Run automated tests for the VIS Framework.
"""

VERBOSITY = 0

from unittest import TextTestRunner

from vis.tests import test_indexer
from vis.tests import test_duration_indexer
from vis.tests import test_note_beat_strength_indexer
from vis.tests import test_measure_indexer
from vis.tests import test_note_rest_indexer
from vis.tests import test_ngram
from vis.tests import test_dissonance_indexer
from vis.tests import test_repeat
from vis.tests import test_interval_indexer
from vis.tests import test_frequency_experimenter
from vis.tests import test_aggregator
from vis.tests import test_barchart
# from vis.tests import test_dendrogram
from vis.tests import test_offset
from vis.tests import test_indexed_piece
from vis.tests import test_aggregated_pieces
from vis.tests import bwv2_integration_tests as bwv2
from vis.tests import bwv603_integration_tests as bwv603
# NB: The WorkflowManager is deprecated, though most of its tests still pass.
# from vis.tests import test_workflow
# from vis.tests import test_workflow_integration
# from vis.tests import test_workflow_experiments
from vis.tests import test_fermata_indexer
from vis.tests import test_over_bass
from vis.tests import test_approach
from vis.tests import test_contour
from vis.tests import test_active_voices
from vis.tests import test_windexer


THE_TESTS = (  # Indexer and Subclasses
             test_indexer.INDEXER_INIT_SUITE,
             test_indexer.INDEXER_1_PART_SUITE,
             test_indexer.INDEXER_MULTI_EVENT_SUITE,  # no tests run
             test_fermata_indexer.FERMATA_INDEXER_SUITE,
             test_note_rest_indexer.NOTE_REST_INDEXER_SUITE,
             test_note_rest_indexer.MULTI_STOP_INDEXER_SUITE,
             test_duration_indexer.DURATION_INDEXER_SUITE,
             test_note_beat_strength_indexer.NOTE_BEAT_STRENGTH_INDEXER_SUITE,
             test_measure_indexer.MEASURE_INDEXER_SUITE,
             test_interval_indexer.INTERVAL_INDEXER_SHORT_SUITE,
             test_interval_indexer.INTERVAL_INDEXER_LONG_SUITE,
             test_interval_indexer.INT_IND_INDEXER_SUITE,
             test_interval_indexer.HORIZ_INT_IND_LONG_SUITE,
             test_repeat.REPEAT_INDEXER_SUITE,
             test_ngram.NGRAM_INDEXER_SUITE,
             test_dissonance_indexer.DISSONANCE_INDEXER_SUITE,
             test_offset.OFFSET_INDEXER_SINGLE_SUITE,
             test_offset.OFFSET_INDEXER_MULTI_SUITE,
             test_over_bass.OVER_BASS_INDEXER_SUITE,
             test_approach.APPROACH_INDEXER_SUITE,
             test_contour.CONTOUR_INDEXER_SUITE,
             test_active_voices.ACTIVE_VOICES_INDEXER_SUITE,
             test_windexer.WINDEXER_SUITE,
             # Experimenter and Subclasses
             test_frequency_experimenter.FREQUENCY_SUITE,
             test_aggregator.COLUMN_AGGREGATOR_SUITE,
             test_barchart.R_BAR_CHART_SUITE,
             # test_dendrogram.DENDROGRAM_SUITE, # This test suite is commented out so that we can remove our SciPy dependency.
             # Importer, IndexedPiece, and AggregatedPieces
             test_aggregated_pieces.IMPORTER_SUITE,
             test_indexed_piece.INDEXED_PIECE_SUITE_A,
             test_indexed_piece.INDEXED_PIECE_PARTS_TITLES,
             test_indexed_piece.INDEXED_PIECE_SUITE_C,
             test_aggregated_pieces.AGGREGATED_PIECES_SUITE,
             # NB: Most of these WorkflowManager tests pass but they are commented out because the WorkflowManager is deprecated.
             # # WorkflowManager 
             # test_workflow.WORKFLOW_TESTS,  # FutureWarning: sort(columns) is depracated, use sort_values(by=...)
             # test_workflow.FILTER_DATA_FRAME,
             # test_workflow.MAKE_TABLE,
             # test_workflow.EXTRA_PAIRS,
             # test_workflow.SETTINGS,
             # test_workflow.OUTPUT,
             # test_workflow.MAKE_HISTOGRAM,
             # test_workflow.MAKE_LILYPOND,
             # test_workflow.AUX_METHODS,
             # test_workflow_experiments.INTERVALS,
             # Integration Tests
             bwv2.ALL_VOICE_INTERVAL_NGRAMS,
             bwv603.ALL_VOICE_INTERVAL_NGRAMS,
             # NB: The integration tests below are commented out because the WorkflowManager is deprecated.
             # test_workflow_integration.INTERVALS_TESTS,
        )


if __name__ == '__main__':
    for each_test in THE_TESTS:
        result = TextTestRunner(verbosity=VERBOSITY, descriptions=False).run(each_test)
        if not result.wasSuccessful():
            raise RuntimeError('Test failure')
