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
    def test_ind_1(self):
        # that it picks up simple major/minor things as dissonant
        in_vals = [u'm2', u'M2', u'P4', u'm7', u'M7']
        for val in in_vals:
            expected = pandas.Series([val])
            actual = dissonance.DissonanceIndexer([expected]).run()[0]
            self.assertSequenceEqual(list(expected.index), list(actual.index))
            self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_ind_2(self):
        # that it picks up diminished/augmented dissonances
        in_vals = ['A4', 'd5', 'A1', 'd8']
        for val in in_vals:
            expected = pandas.Series([val])
            actual = dissonance.DissonanceIndexer([expected]).run()[0]
            self.assertSequenceEqual(list(expected.index), list(actual.index))
            self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_ind_3(self):
        # that consonances are properly noted as consonant
        in_vals = [u'm3', u'M3', u'P5', u'm6', u'M6']
        for val in in_vals:
            in_ser = pandas.Series([val])
            act = dissonance.DissonanceIndexer([in_ser]).run()[0]
            self.assertEqual(0, len(act))

    def test_ind_4(self):
        # a quasi-realistic, single-part test
        in_ser = pandas.Series(['m3', 'M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7'])
        expected = pandas.Series(['M2', 'm2', 'P4', 'd5', 'm7'], index=[1, 2, 3, 4, 7])
        actual = dissonance.DissonanceIndexer([in_ser]).run()[0]
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_ind_5(self):
        # a quasi-realistic, multi-part test
        in_sers = [pandas.Series(['m3', 'M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7']),
                   pandas.Series(['M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7', 'm3']),
                   pandas.Series(['m2', 'P4', 'd5', 'P5', 'M6', 'm7', 'm3', 'M2'])]
        expected = [pandas.Series(['M2', 'm2', 'P4', 'd5', 'm7'], index=[1, 2, 3, 4, 7]),
                    pandas.Series(['M2', 'm2', 'P4', 'd5', 'm7'], index=[0, 1, 2, 3, 6]),
                    pandas.Series(['m2', 'P4', 'd5', 'm7', 'M2'], index=[0, 1, 2, 5, 7])]
        actual = dissonance.DissonanceIndexer(in_sers).run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    # NOTE: I decided not to test the rest of this indexer because it uses a pattern very common
    #       through the rest of the Framework.


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
DISSONANCE_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestDissonanceIndexer)
