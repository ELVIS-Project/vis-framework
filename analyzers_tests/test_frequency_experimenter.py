#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import mock
from pandas import Series, DataFrame
from vis.analyzers.experimenters.frequency import FrequencyExperimenter, experimenter_func


class TestExperimenterFunc(unittest.TestCase):
    def test_func_1(self):
        in_series = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        expected = Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1})
        actual = experimenter_func(in_series)
        self.assertEqual(len(expected), len(actual))
        for each_i in expected.index:
            self.assertEqual(expected[each_i], actual[each_i])

    def test_func_2(self):
        in_series = Series([12])
        expected = Series({12: 1})
        actual = experimenter_func(in_series)
        self.assertEqual(len(expected), len(actual))
        for each_i in expected.index:
            self.assertEqual(expected[each_i], actual[each_i])

    def test_func_3(self):
        in_series = Series([])
        expected = Series({})
        actual = experimenter_func(in_series)
        self.assertEqual(len(expected), len(actual))
        for each_i in expected.index:
            self.assertEqual(expected[each_i], actual[each_i])


# pylint: disable=W0212
class TestRun(unittest.TestCase):
    def test_run_1(self):
        # should have the same output as test_run_2, but _do_multiprocessing() is a MagicMock
        in_a = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_b = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_c = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_series = [in_a, in_b, in_c]
        expected = DataFrame({0: Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              1: Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              2: Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              u'all': Series({1: 15, 2: 6, 3: 6, 4: 3, 5: 3})})
        exp = FrequencyExperimenter(in_series)
        exp._do_multiprocessing = mock.MagicMock()
        exp._do_multiprocessing.return_value = [Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                                                Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                                                Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1})]
        actual = exp.run()
        exp._do_multiprocessing.assert_called_once_with(experimenter_func, [[in_a], [in_b], [in_c]])
        self.assertTrue(expected.sort(axis=1) == actual.sort(axis=1))

    def test_run_2(self):
        in_a = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_b = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_c = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_series = [in_a, in_b, in_c]
        expected = DataFrame({0: Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              1: Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              2: Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              u'all': Series({1: 15, 2: 6, 3: 6, 4: 3, 5: 3})})
        exp = FrequencyExperimenter(in_series)
        actual = exp.run()
        self.assertTrue(expected.sort(axis=1) == actual.sort(axis=1))

    def test_run_3(self):
        in_a = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_b = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1, 4, 4, 3, 5, 1, 1, 1])
        in_c = Series([1, 2, 1, 1, 3, 1, 3, 2, 1])
        in_series = [in_a, in_b, in_c]
        expected = DataFrame({0: Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              1: Series({1: 8, 2: 2, 3: 3, 4: 3, 5: 2}),
                              2: Series({1: 5, 2: 2, 3: 2}),
                              u'all': Series({1: 18, 2: 6, 3: 7, 4: 7, 5: 3})})
        exp = FrequencyExperimenter(in_series)
        actual = exp.run()
        self.assertTrue(expected.sort(axis=1) == actual.sort(axis=1))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
FREQUENCY_FUNC_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestExperimenterFunc)
FREQUENCY_RUN_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestRun)
