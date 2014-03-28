#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_frequency.py
# Purpose:                Tests for the frequency experimenters.
#
# Copyright (C) 2013 Christopher Antila
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
        ident = 2343
        in_series = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        expected = (ident, Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}))
        actual = experimenter_func((ident, in_series))
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected[0], actual[0])
        self.assertEqual(len(expected[1]), len(actual[1]))
        for each_i in expected[1].index:
            self.assertEqual(expected[1][each_i], actual[1][each_i])

    def test_func_2(self):
        ident = 7743
        in_series = Series([12])
        expected = (ident, Series({12: 1}))
        actual = experimenter_func((ident, in_series))
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected[0], actual[0])
        self.assertEqual(len(expected[1]), len(actual[1]))
        for each_i in expected[1].index:
            self.assertEqual(expected[1][each_i], actual[1][each_i])

    def test_func_3(self):
        ident = u'swamp'
        in_series = Series([])
        expected = (ident, Series({}))
        actual = experimenter_func((ident, in_series))
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected[0], actual[0])
        self.assertEqual(len(expected[1]), len(actual[1]))
        for each_i in expected[1].index:
            self.assertEqual(expected[1][each_i], actual[1][each_i])


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
        exp._do_multiprocessing.return_value = [(0, Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1})),
                                                (1, Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1})),
                                                (2, Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}))]
        actual = exp.run()
        exp._do_multiprocessing.assert_called_once_with(experimenter_func, [[(0, in_a)],
            [(1, in_b)], [(2, in_c)]])
        self.assertEqual(len(expected.columns), len(actual.columns))
        for i in expected.columns:
            self.assertSequenceEqual(list(expected.loc[:,i].index), list(actual.loc[:,i].index))
            self.assertSequenceEqual(list(expected.loc[:,i].values), list(actual.loc[:,i].values))

    def test_run_2(self):
        # should have the same output as test_run_1, but without the MagicMock
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
        self.assertEqual(len(expected.columns), len(actual.columns))
        for i in expected.columns:
            self.assertSequenceEqual(list(expected.loc[:,i].index), list(actual.loc[:,i].index))
            self.assertSequenceEqual(list(expected.loc[:,i].values), list(actual.loc[:,i].values))

    def test_run_3(self):
        # more complicated arithmetic
        in_a = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_b = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1, 4, 4, 3, 5, 1, 1, 1])
        in_c = Series([1, 2, 1, 1, 3, 1, 3, 2, 1])
        in_series = [in_a, in_b, in_c]
        expected = DataFrame({0: Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              1: Series({1: 8, 2: 2, 3: 3, 4: 3, 5: 2}),
                              2: Series({1: 5, 2: 2, 3: 2}),
                              u'all': Series({1: 18, 2: 6, 3: 7, 4: 4, 5: 3})})
        exp = FrequencyExperimenter(in_series)
        actual = exp.run()
        # because numpy's NaN != NaN
        actual = actual.fillna(value=4000)
        expected = expected.fillna(value=4000)
        self.assertEqual(len(expected.columns), len(actual.columns))
        for i in expected.columns:
            self.assertSequenceEqual(list(expected.loc[:,i].index), list(actual.loc[:,i].index))
            self.assertSequenceEqual(list(expected.loc[:,i].values), list(actual.loc[:,i].values))

    def test_run_4(self):
        # same as test_run_3, but input is a dict
        in_a = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1])
        in_b = Series([1, 2, 1, 1, 3, 1, 4, 5, 3, 2, 1, 4, 4, 3, 5, 1, 1, 1])
        in_c = Series([1, 2, 1, 1, 3, 1, 3, 2, 1])
        in_series = {u'hello': in_a, u'zello': in_b, u'jello': in_c}
        expected = DataFrame({u'hello': Series({1: 5, 2: 2, 3: 2, 4: 1, 5: 1}),
                              u'zello': Series({1: 8, 2: 2, 3: 3, 4: 3, 5: 2}),
                              u'jello': Series({1: 5, 2: 2, 3: 2}),
                              u'all': Series({1: 18, 2: 6, 3: 7, 4: 4, 5: 3})})
        exp = FrequencyExperimenter(in_series)
        actual = exp.run()
        # because numpy's NaN != NaN
        actual = actual.fillna(value=4000)
        expected = expected.fillna(value=4000)
        self.assertEqual(len(expected.columns), len(actual.columns))
        for i in expected.columns:
            self.assertSequenceEqual(list(expected.loc[:,i].index), list(actual.loc[:,i].index))
            self.assertSequenceEqual(list(expected.loc[:,i].values), list(actual.loc[:,i].values))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
FREQUENCY_FUNC_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestExperimenterFunc)
FREQUENCY_RUN_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestRun)
