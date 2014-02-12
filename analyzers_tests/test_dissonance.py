#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_dissonance.py
# Purpose:                For testing indexers in the "dissonance" module.
#
# Copyright (C) 2013, 2014 Christopher Antila
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
import pandas
from vis.analyzers.indexers import dissonance


class TestDissonanceIndexer(unittest.TestCase):
    def test_ind_func_1(self):
        # test diss_ind_func() with 2nds
        in_vals = [u'd2', u'm2', u'M2', 'A2']
        for val in in_vals:
            self.assertEqual(val, dissonance.diss_ind_func(pandas.Series([val])))

    def test_ind_func_2(self):
        # test diss_ind_func() with 4ths
        in_vals = [u'd4', u'P4', 'A2']
        for val in in_vals:
            self.assertEqual(val, dissonance.diss_ind_func(pandas.Series([val])))

    def test_ind_func_3(self):
        # test diss_ind_func() with diminished 5th
        in_vals = [u'd5']
        for val in in_vals:
            self.assertEqual(val, dissonance.diss_ind_func(pandas.Series([val])))

    def test_ind_func_4(self):
        # test diss_ind_func() with 7ths
        in_vals = [u'd7', u'm7', u'M7', 'A7']
        for val in in_vals:
            self.assertEqual(val, dissonance.diss_ind_func(pandas.Series([val])))

    # NOTE: I decided not to test the rest of this indexer because it uses a pattern very common
    #       through the rest of the Framework.


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
DISSONANCE_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestDissonanceIndexer)
