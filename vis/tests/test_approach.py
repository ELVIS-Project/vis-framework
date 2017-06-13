#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_approach.py
# Purpose:                Test indexing of approach indexer.
#
# Copyright (C) 2016 Marina Cottrell
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

from unittest import TestCase, TestLoader
import pandas
from vis.analyzers.indexers import approach


def make_dataframe(labels, indices, name):
    ret = pandas.concat(indices, levels=labels, axis=1)
    iterables = (name, labels)
    multi_index = pandas.MultiIndex.from_product(iterables, names=('Indexer', 'Parts'))
    ret.columns = multi_index
    return ret


index = [2.5, 5.0, 9.5]
ferms = ['Fermata', 'Fermata', 'Fermata']
label = '0'
ferm_name = 'fermata.FermataIndexer'

result = pandas.DataFrame({label: pandas.Series(ferms, index=index)})
FERMS = make_dataframe(result.columns.values, [result[name] for name in result.columns], ferm_name)


index = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 8.0, 9.0, 9.5, 10.0]

overs = [['-P5', 'P1', 'M2', 'P1', 'M2', 'P1', 'M2', 'm2', 'M2', 'P1', '-P5', 'P1', 'P4', '-m2', 'm2', '-m2', '-M2'],
         ['P5', 'M3', 'M3', 'P8', 'm7', 'P5', 'm6', 'm6', 'P5', 'm3', 'M2', 'm7', 'm7', 'M3', 'm3', 'M3', 'P4'],
         ['P8', 'P5', 'P5', 'M3', 'M3', 'm3', 'm3', 'P8', 'M7', 'P5', 'm7', 'P4', 'M3', 'P8', 'm3', 'P8', 'm2'],
         ['M3', 'P8', 'M7', 'P5', 'P5', 'P8', 'P8', 'm3', 'M3', 'm3', 'P5', 'P8', 'P8', 'P5', 'm6', 'P5', 'm6']]


label = '3 0,3 1,3 2,3'
over_name = 'over_bass.OverBassIndexer'

result = pandas.DataFrame({label: pandas.Series([str(intvl) for intvl in list(zip(*overs))], index=index)})
EXPECTED = make_dataframe(result.columns.values, [result[name] for name in result.columns], over_name)

lyst = [EXPECTED, FERMS]

index = [2.0, 4.5, 9.0]
apprs = [["('M2', 'M3', 'P5', 'M7')", "('P1', 'P8', 'M3', 'P5')"], 
        ["('m2', 'm6', 'P8', 'm3')", "('M2', 'P5', 'M7', 'M3')"], 
        ["('m2', 'm3', 'm3', 'm6')", "('-m2', 'M3', 'P8', 'P5')"]]

label = 'Approaches'
appr_name = 'approach.ApproachIndexer'

result = pandas.DataFrame({label: pandas.Series(apprs, index=index)})
APPROACH = make_dataframe(result.columns.values, [result[name] for name in result.columns], appr_name)

class TestApproachIndexer(TestCase):

    def test_init1(self):
        """tests that __init__() works with only the basic settings given"""
        actual = approach.ApproachIndexer(lyst, {'length': 4})
        self.assertEqual(actual._settings, {'length': 4, 'voice': 'all'})

    def test_init2(self):
        """tests that __init__() works with all possible settings given"""
        settings = {'length': 3, 'voice': 0}
        actual = approach.ApproachIndexer(lyst, settings)
        self.assertEqual(actual._settings, settings)

    def test_init3(self):
        """tests that __init__() fails when length is not given"""
        settings = {}
        self.assertRaises(RuntimeError, approach.ApproachIndexer, lyst, settings)
        try:
            approach.ApproachIndexer(lyst, settings)
        except RuntimeError as run_err:
            self.assertEqual(approach.ApproachIndexer._MISSING_LENGTH, run_err.args[0])

    def test_init4(self):
        """tests that __init__() fails when the given length is too low"""
        settings = {'length': 0.3}
        self.assertRaises(RuntimeError, approach.ApproachIndexer, lyst, settings)
        try:
            approach.ApproachIndexer(lyst, settings)
        except RuntimeError as run_err:
            self.assertEqual(approach.ApproachIndexer._LOW_LENGTH, run_err.args[0])

    def test_init5(self):
        """tests that __init__() fails when the given voice doesn't exist"""
        settings = {'length': 2, 'voice': 15}
        self.assertRaises(RuntimeError, approach.ApproachIndexer, lyst, settings)
        try: 
            approach.ApproachIndexer(lyst, settings)
        except RuntimeError as run_err:
            self.assertEqual(approach.ApproachIndexer._BAD_VOICE, run_err.args[0])

    def test_approach(self):
        """tests that running the approach indexer returns the expected results"""
        settings = {'length': 2}
        actual = approach.ApproachIndexer(lyst, settings).run()
        self.assertTrue(actual.equals(APPROACH))

    def test_approach2(self):
        settings = {'length': 2, 'voice': 0}
        actual = approach.ApproachIndexer(lyst, settings).run()
        self.assertTrue(actual.equals(APPROACH))

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
APPROACH_INDEXER_SUITE = TestLoader().loadTestsFromTestCase(TestApproachIndexer)
