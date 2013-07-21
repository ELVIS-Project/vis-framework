#! /usr/bin/python
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

# Verbosity
verb = 1

# Imports
import unittest
# new
from analyzers_tests.test_note_rest_indexer import *
from analyzers_tests.test_interval_indexer import *
from models_tests.test_indexed_piece import *
# old
from controllers_tests.test_importer import *
from controllers_tests.test_analyzer import *
from controllers_tests.test_experimenter import *
from models_tests.test_importing import *
from models_tests.test_analyzing import *
from models_tests.test_ngram import *

# Analyzers ---------------------------------------------------------------------------------------
#unittest.TextTestRunner(verbosity=verb).run(note_rest_indexer_suite)
unittest.TextTestRunner(verbosity=verb).run(interval_indexer_suite)
#unittest.TextTestRunner(verbosity=verb).run(indexed_piece_suite)
#unittest.TextTestRunner(verbosity=verb).run(indexed_piece_errors_suite)

# Controllers ------------------------------------------------------------------
# Importer
#unittest.TextTestRunner(verbosity=verb).run(importer_piece_getter_suite)
#unittest.TextTestRunner(verbosity=verb).run(importer_part_and_titles_suite)
#unittest.TextTestRunner(verbosity=verb).run(importer_add_pieces_suite)
#unittest.TextTestRunner(verbosity=verb).run(importer_remove_pieces_suite)
#unittest.TextTestRunner(verbosity=verb).run(importer_import_pieces_suite)

# Analyzer
#unittest.TextTestRunner(verbosity=verb).run(analyzer_event_finder_short_suite)
#unittest.TextTestRunner(verbosity=verb).run(analyzer_event_finder_long_monteverdi)
#unittest.TextTestRunner(verbosity=verb).run(analyzer_event_finder_long_josquin)
#unittest.TextTestRunner(verbosity=verb).run(analyzer_event_finder_long_bach)

# Experimenter
#unittest.TextTestRunner(verbosity=verb).run(experimenter_interv_stats_suite)
#unittest.TextTestRunner(verbosity=verb).run(experimenter_interv_lists_suite)

# Models -----------------------------------------------------------------------
# Importing -- all tests pass
#unittest.TextTestRunner(verbosity=verb).run(importing_basics_suite)
#unittest.TextTestRunner(verbosity=verb).run(importing_data_suite)
#unittest.TextTestRunner(verbosity=verb).run(importing_set_data_suite)
#unittest.TextTestRunner(verbosity=verb).run(importing_insert_rows_suite)
#unittest.TextTestRunner(verbosity=verb).run(importing_is_present_suite)
#unittest.TextTestRunner(verbosity=verb).run(importing_iterator_suite)
#unittest.TextTestRunner(verbosity=verb).run(importing_remove_rows_suite)

# Analyzing: ListOfPieces
#unittest.TextTestRunner(verbosity=verb).run(lop_basics_suite)
#unittest.TextTestRunner(verbosity=verb).run(lop_insert_and_remove_suite)
#unittest.TextTestRunner(verbosity=verb).run(lop_iterate_rows_suite)
#unittest.TextTestRunner(verbosity=verb).run(lop_set_data_suite)
#unittest.TextTestRunner(verbosity=verb).run(lop_header_data_suite)
#unittest.TextTestRunner(verbosity=verb).run(lop_data_suite)
## Analyzing.AnalysisRecord
#unittest.TextTestRunner(verbosity=verb).run(ar_init_suite)
#unittest.TextTestRunner(verbosity=verb).run(ar_iter_suite)
#unittest.TextTestRunner(verbosity=verb).run(ar_getters_suite)
#unittest.TextTestRunner(verbosity=verb).run(ar_append_event_suite)
## Analyzing.NGram
#unittest.TextTestRunner(verbosity=verb).run(test_interval_ngram_suite)
#unittest.TextTestRunner(verbosity=verb).run(test_chord_ngram_suite)
