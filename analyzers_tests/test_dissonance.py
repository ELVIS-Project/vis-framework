#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/template_test.py
# Purpose:                Template for testing indexers.
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

# NB: These are for the "pylint" source file checker.
# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import mock
import pandas
from vis.analyzers.indexers import dissonance


class TestDissonanceIndexer(unittest.TestCase):
    # NOTE: every method that is a test must be named with the "test_" prefix
    def test_template_0(self):
        # Test the indexer function alone...
        # - with as few parts as valid
        # - with as many parts as valid (or many parts)
        # - with some parts, each with barely valid values
        # - with some parts, each with decent
        pass

    def test_template_1(self):
        # Example of how to replace the indexer function with a MagicMock.
        # NB: This may not make sense for every indexer; you may be better off mocking
        #     _do_multiprocessing() and ensuring that method gets the right arguments... or try
        #     mocking both! But not at the same time.
        #
        # 1.) Prepare settings.
        setts = {u'fake_setting': u'fake value'}
        # 2.) Prepare the input values.
        in_val = [pandas.Series([1, 2, 3]), pandas.Series([4, 5, 6])]
        # 3.) Make the test indexer instance.
        test_ind = template.TemplateIndexer(in_val, setts)
        # 4.) Setup the mock.
        with mock.patch(u'vis.analyzers.indexers.template.indexer_func') as mock_indfunc:
            # 5.) The indexer_func() will always return a zero-length unicode string.
            mock_indfunc.return_value = u''
            # 6.) Run the indexer.
            test_ind.run()
            # 7.) Test the indexer_func() was called the right number of times (probably 3 in this
            #     case, if we assume the two Series from "in_val" are treated as simultaneous parts
            #     of the same piece.
            self.assertEqual(3, len(mock_indfunc.call_args_list))
            # 8.) The simultaneities that should have been given to indexer_func().
            expected_calls = [[1, 4], [2, 5], [3, 6]]
            # 9.) Everything in the "call_args_list" is a iterable "call" object. What you really
            #     want is the first thing in that call, which is what the indexer_func() received.
            actual_calls = [each[0] for each in mock_indfunc.call_args_list]
            # 10.) Compare expected and actual. (NB: assertSequenceEqual() was new in Python 2.7)
            self.assertSequenceEqual(expected_calls, actual_calls)

    def test_template_2(self):
        # Example for using the whole indexer; let's pretend this one adds a ^ over characters that
        # support it, and removes those that don't.
        # 1.) Prepare the input values.
        in_val = [pandas.Series(['a', 'b', 'c', 'd'], index=[0.0, 0.5, 1.0, 1.5])]
        # 2.) Prepare our expected output.
        expected = [pandas.Series(['â', 'ĉ'], index=[0.0, 1.0])]
        # 3.) Make then run the test indexer.
        test_ind = template.TemplateIndexer(in_val)
        actual = test_ind.run()
        # 4.) Ensure we received the expected number of parts.
        self.assertEqual(len(expected), len(actual))
        # 5.) Compare each part...
        for i in xrange(len(expected)):
            # ... to know the index has the expected values, ...
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            # ... and that the values are the expected values.
            self.assertSequenceEqual(list(expected[i]), list(actual[i]))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
DISSONANCE_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestDissonanceIndexer)
