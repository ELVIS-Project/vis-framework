#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_barchart.py
# Purpose:                Tests for the "barchart" experimenter module.
#
# Copyright (C) 2015 Alexander Morgan
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
.. codeauthor:: Alexander Morgan

Tests for the "dendrogram" experimenters.
"""

import unittest
import pandas
from vis.analyzers.experimenters import dendrogram

list_of_3_series_a = [pandas.Series([1, 1, 1], index=['A', 'B', 'C']),
                    pandas.Series([1, 2, 3], index=['A', 'B', 'C']),
                    pandas.Series([3, 2, 1], index=['A', 'B', 'C'])]

list_of_3_series_b = [pandas.Series([1, 1, 1], index=['4', '2', '1']),
                    pandas.Series([1, 2, 3], index=['2', '1', '.5']),
                    pandas.Series([3, 2, 1], index=['3', '1.5', '2'])]

class TestHierarchicalClusterer(unittest.TestCase):
    """Tests for the dendrogram.HierarchicalClusterer experimenter."""

    def test_init_1(self):
        """That __init__() initializes properly."""
        setts = {'sers': [[]], 'weights': (1.0,), 'graph_settings': None, 'dendrogram_settings': None}
        actual = dendrogram.HierarchicalClusterer(**setts)
        self.assertEqual(setts['sers'], actual._sers)
        self.assertEqual(setts['weights'], actual._weights)
        self.assertEqual(dendrogram.HierarchicalClusterer.default_graph_settings, actual._graph_settings)
        self.assertEqual(dendrogram.HierarchicalClusterer.default_dendrogram_settings, actual._dendrogram_settings)

    def test_init_2a(self):
        """That __init__() raises RuntimeWarning when the sum of weights argument doesn't equal 1.0."""
        setts = {'sers': [[]], 'weights': (.45,)}
        self.assertRaises(RuntimeWarning, dendrogram.HierarchicalClusterer, setts)
        try:
            dendrogram.HierarchicalClusterer(**setts)
        except RuntimeWarning as runwarn:
            self.assertEqual(dendrogram.HierarchicalClusterer._INVALID_WEIGHTS, runwarn.args[0])

    def test_init_2b(self):
        """That __init__() raises RuntimeWarning when an element in weights is greater than 1.0. 
        Like test_init_2a but tests a different part of the logic statement."""
        setts = {'sers': [[], []], 'weights': (1.1, -0.1)}
        self.assertRaises(RuntimeWarning, dendrogram.HierarchicalClusterer, setts)
        try:
            dendrogram.HierarchicalClusterer(**setts)
        except RuntimeWarning as runwarn:
            self.assertEqual(dendrogram.HierarchicalClusterer._INVALID_WEIGHTS, runwarn.args[0])

    def test_init_2c(self):
        """That __init__() raises RuntimeWarning when an element in weights is less than 0. Like 
        test_init_2a but tests a different part of the logic statement."""
        setts = {'sers': [[], [], []], 'weights': (.5, .6, -0.1)}
        self.assertRaises(RuntimeWarning, dendrogram.HierarchicalClusterer, setts)
        try:
            dendrogram.HierarchicalClusterer(**setts)
        except RuntimeWarning as runwarn:
            self.assertEqual(dendrogram.HierarchicalClusterer._INVALID_WEIGHTS, runwarn.args[0])

    def test_init_3(self):
        """That __init__() raises RuntimeWarning when sers and weights are of different lengths."""
        setts = {'sers': [[], [], []], 'weights': (.8, .2)}
        self.assertRaises(RuntimeWarning, dendrogram.HierarchicalClusterer, setts)
        try:
            dendrogram.HierarchicalClusterer(**setts)
        except RuntimeWarning as runwarn:
            # I'm not sure why runwarn[0] adds a return line, so just looking at the first 20 characters will have to do.
            self.assertEqual(dendrogram.HierarchicalClusterer._UNEQUAL_SERS_WEIGHTS[:20], runwarn.args[0][:20])

    def test_init_4(self):
        """That __init__() raises RuntimeWarning when an erroneous setting is passed in graph_settings."""
        setts = {'sers': [[]], 'graph_settings': {'invalid_setting': True}}
        self.assertRaises(RuntimeWarning, dendrogram.HierarchicalClusterer, setts)
        try:
            dendrogram.HierarchicalClusterer(**setts)
        except RuntimeWarning as runwarn:
            self.assertEqual('invalid_setting' + dendrogram.HierarchicalClusterer._INVALID_GRAPH_SETTING, runwarn.args[0])

    def test_init_5(self):
        """That __init__() raises RuntimeWarning when an erroneous setting is passed in dendrogram_settings."""
        setts = {'sers': [[]], 'dendrogram_settings': {'invalid_setting': True}}
        self.assertRaises(RuntimeWarning, dendrogram.HierarchicalClusterer, setts)
        try:
            dendrogram.HierarchicalClusterer(**setts)
        except RuntimeWarning as runwarn:
            self.assertEqual('invalid_setting' + dendrogram.HierarchicalClusterer._INVALID_DENDRO_SETTING, runwarn.args[0])

    def test_init_6(self):
        """That __init__() raises RuntimeWarning when the internal lists of sers are of differing lengths."""
        setts = {'sers': [[1, 2, 3], [1, 2]], 'weights': (.55, .45)}
        self.assertRaises(RuntimeWarning, dendrogram.HierarchicalClusterer, setts)
        try:
            dendrogram.HierarchicalClusterer(**setts)
        except RuntimeWarning as runwarn:
            self.assertEqual(dendrogram.HierarchicalClusterer._UNEQUAL_ANALYSES, runwarn.args[0])

    def test_init_7a(self):
        """That self._dendrogram_settings['no_plot'] overrides to True if user sets it to False but
        no visual output format is requested."""
        setts = {'sers': [[]],
                 'dendrogram_settings': {'no_plot': False},
                 'graph_settings':{'interactive_dendrogram': False, 'filename_and_type': None}
                 }
        exp = dendrogram.HierarchicalClusterer(**setts)
        self.assertEqual(True, exp._dendrogram_settings['no_plot'])

    def test_init_7b(self):
        """That self._dendrogram_settings['no_plot'] overrides to False if user sets it to True but
        also requests an interactive matplotlib plot. Similar to test_init_6a but the opposite case."""
        setts = {'sers': [[]],
                 'dendrogram_settings': {'no_plot': True},
                 'graph_settings':{'interactive_dendrogram': True, 'filename_and_type': None}
                 }
        exp = dendrogram.HierarchicalClusterer(**setts)
        self.assertEqual(False, exp._dendrogram_settings['no_plot'])

    def test_init_7c(self):
        """That self._dendrogram_settings['no_plot'] overrides to False if user sets it to True but
        also requests an interactive matplotlib plot. Same as test_init_6b but with a
        filename_and_type argument instead of requesting an interactive dendrogram."""
        setts = {'sers': [[]],
                 'dendrogram_settings': {'no_plot': True},
                 'graph_settings':{'interactive_dendrogram': False, 'filename_and_type': 'Zamboni.png'}
                 }
        actual = dendrogram.HierarchicalClusterer(**setts)
        self.assertEqual(False, actual._dendrogram_settings['no_plot'])

    def test_pair_compare_1(self):
        """ That pair_compare() produces the expected matrix with one analysis metric. This is the
        same matrix that will get passed to the run() method in test_run_1."""
        setts = {'sers': [list_of_3_series_a]}
        actual = dendrogram.HierarchicalClusterer(**setts).pair_compare()
        expected = [16.666666666666675, 16.666666666666675, 33.333333333333336]
        self.assertEqual(expected, actual)

    def test_pair_compare_2(self):
        """ That pair_compare() works properly with just one metric again but with some values that 
        are not present in some of the analyses. The sers argument passed here is similar to what a 
        duration count would look like."""
        setts = {'sers': [list_of_3_series_b]}
        actual = dendrogram.HierarchicalClusterer(**setts).pair_compare()
        expected = [50.0, 83.333333333333343, 83.333333333333343]
        self.assertEqual(expected, actual)

    def test_pair_compare_3(self):
        """ That pair_compare() works properly with two analysis metrics. These results 
        combine the dissimilarities shown in the two previous tests according to the weights 
        argument."""
        setts = {'sers': [list_of_3_series_a, list_of_3_series_b], 'weights': (.8, .2) }
        actual = dendrogram.HierarchicalClusterer(**setts).pair_compare()
        expected = [23.333333333333339, 30.000000000000007, 43.333333333333343]
        self.assertEqual(expected, actual)

    def test_run_1(self):
        """ That run() works properly. The sers argument passed here is similar to what a note 
        count would look like. If test_pair_compare_1 passed, but this test fails, it is likely a
        problem with the run() method."""
        setts = {'sers': [list_of_3_series_a],
                 'graph_settings': {'return_data': True, 'interactive_dendrogram': False} }
        actual = dendrogram.HierarchicalClusterer(**setts).run()
        expected = {'ivl': ['3', '1', '2'],
                    'dcoord': [[0.0, 16.666666666666675, 16.666666666666675, 0.0],
                               [0.0, 25.000000000000007, 25.000000000000007, 16.666666666666675]],
                    'leaves': [2, 0, 1], 'color_list': ['g', 'g'],
                    'icoord': [[15.0, 15.0, 25.0, 25.0], [5.0, 5.0, 20.0, 20.0]]}
        self.assertEqual(expected, actual)

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
DENDROGRAM_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestHierarchicalClusterer)
