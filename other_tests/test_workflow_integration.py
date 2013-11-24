#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               other_tests/test_workflow_integration.py
# Purpose:                Integration tests for the WorkflowManager
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
"""
Integration tests for the WorkflowManager
"""

from unittest import TestCase, TestLoader
import pandas
from vis.workflow import WorkflowManager


# pylint: disable=R0904
# pylint: disable=C0111
class IntervalsTests(TestCase):
    # EXPECTED_A is the result of the "intervals" experiment with "[[0, 1]]" as the voice pairs;
    # note that I didn't verify by counting... this just ensures a valid value comes out
    EXPECTED_A = pandas.Series({u'3': 32, u'4': 22, u'5': 18, u'6': 16, u'7': 4, u'2': 3, u'8': 2})

    def test_intervals_1(self):
        # test the two highest voices of bwv77
        test_wm = WorkflowManager(['test_corpus/bwv77.mxl'])
        test_wm.load('pieces')
        test_wm.settings(0, 'voice combinations', '[[0, 1]]')
        actual = test_wm.run('intervals')
        exp_ind = list(IntervalsTests.EXPECTED_A.index)
        act_ind = list(actual.index)
        for ind_item in exp_ind:
            self.assertTrue(ind_item in act_ind)
        for ind_item in exp_ind:
            self.assertEqual(IntervalsTests.EXPECTED_A[ind_item], actual[ind_item])


#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
INTERVALS_TESTS = TestLoader().loadTestsFromTestCase(IntervalsTests)
