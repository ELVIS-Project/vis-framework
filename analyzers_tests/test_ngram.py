#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_ngram.py
# Purpose:                Test the NGram Indexer
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
import pandas
from vis.analyzers.indexers import ngram


class TestNGramIndexer(unittest.TestCase):
    def test_ngram_0(self):
        # most basic test
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c', 'd'])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark singles': False}
        expected = [pandas.Series([u'A a B', u'B b C', u'C c D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            for j in xrange(len(expected[i])):
                self.assertEqual(expected[i][j], actual[i][j])

    def test_ngram_1(self):
        # adds the brackets and parentheses
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c', 'd'])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark singles': True}
        expected = [pandas.Series([u'[A] (a) [B]', u'[B] (b) [C]', u'[C] (c) [D]'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            for j in xrange(len(expected[i])):
                self.assertEqual(expected[i][j], actual[i][j])

    def test_ngram_2(self):
        # test _0 but n=3
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c', 'd'])
        setts = {u'n': 3, u'horizontal': [1], u'vertical': [0], u'mark singles': False}
        expected = [pandas.Series([u'A a B b C', u'B b C c D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            for j in xrange(len(expected[i])):
                self.assertEqual(expected[i][j], actual[i][j])

    def test_ngram_3(self):
        # test _0 but with two verticals
        vertical_a = pandas.Series(['A', 'B', 'C', 'D'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W'])
        horizontal = pandas.Series(['a', 'b', 'c', 'd'])
        setts = {u'n': 2, u'horizontal': [2], u'vertical': [0, 1], u'mark singles': False}
        expected = [pandas.Series([u'[A Z] a [B X]', u'[B X] b [C Y]', u'[C Y] c [D W]'])]
        ng_ind = ngram.NGramIndexer([vertical_a, vertical_b, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            for j in xrange(len(expected[i])):
                self.assertEqual(expected[i][j], actual[i][j])

    def test_ngram_4(self):
        # test _0 but with two horizontals, and the order of u'horizontal' setting is important
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal_b = pandas.Series(['z', 'x', 'y', 'w'])
        horizontal_a = pandas.Series(['a', 'b', 'c', 'd'])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [0], u'mark singles': False}
        expected = [pandas.Series([u'A (a z) B', u'B (b x) C', u'C (c y) D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal_b, horizontal_a], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            for j in xrange(len(expected[i])):
                self.assertEqual(expected[i][j], actual[i][j])

    def test_ngram_5(self):
        # combination of tests _3 and _4
        vertical_a = pandas.Series(['A', 'B', 'C', 'D'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W'])
        horizontal_b = pandas.Series(['z', 'x', 'y', 'w'])
        horizontal_a = pandas.Series(['a', 'b', 'c', 'd'])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [3, 0], u'mark singles': False}
        expected = [pandas.Series([u'[A Z] (a z) [B X]',
                                   u'[B X] (b x) [C Y]', u'[C Y] (c y) [D W]'])]
        ng_ind = ngram.NGramIndexer([vertical_b, horizontal_b, horizontal_a, vertical_a], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            for j in xrange(len(expected[i])):
                self.assertEqual(expected[i][j], actual[i][j])

    def test_ngram_6(self):
        # test constructor fails when it should
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        setts = {u'n':1, u'vertical': [0]}  # n is too short
        self.assertRaises(RuntimeError, ngram.NGramIndexer, [vertical], setts)
        setts = {u'n':1, u'horizontal': [0]}  # no "vertical" parts
        self.assertRaises(RuntimeError, ngram.NGramIndexer, [vertical], setts)

    # TODO: test these
    # - terminator
    # - not enough "horizontal" things (should assume last one continues)
    # - everything with floats for index in the Series

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
NGRAM_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestNGramIndexer)
