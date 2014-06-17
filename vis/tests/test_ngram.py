#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_ngram.py
# Purpose:                Test the NGram Indexer
#
# Copyright (C) 2013, 2014 Christopher Antila, Alexander Morgan
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
import pandas
from vis.analyzers.indexers import ngram

VERTICAL_TUPLES = [(0.0, u'P4'),
                   (4.0, u'M3'),
                   (8.0, u'M6'),
                   (12.0, u'P8'),
                   (14.0, u'm6'),
                   (16.0, u'm7'),
                   (18.0, u'M6'),
                   (20.0, u'M6'),
                   (22.0, u'P5'),
                   (26.0, u'P8'),
                   (28.0, u'P4'),
                   (30.0, u'M3'),
                   (31.0, u'A4'),
                   (32.0, u'P4'),
                   (34.0, u'm3'),
                   (36.0, u'Rest'),
                   (38.0, u'Rest')]

HORIZONTAL_TUPLES = [(4.0, u'P4'),
                     (8.0, u'-m3'),
                     (12.0, u'-M2'),
                     (14.0, u'M3'),
                     (16.0, u'-M2'),
                     (20.0, u'-M2'),
                     (28.0, u'P5'),
                     (31.0, u'-M2'),
                     (32.0, u'-m2'),
                     (36.0, u'Rest')]

EXPECTED = [(0.0, u'[P4] (P4) [M3] (-m3) [M6] (-M2) [P8]'),
            (4.0, u'[M3] (-m3) [M6] (-M2) [P8] (M3) [m6]'),
            (8.0, u'[M6] (-M2) [P8] (M3) [m6] (-M2) [m7]'),
            (12.0, u'[P8] (M3) [m6] (-M2) [m7] (P1) [M6]'),
            (14.0, u'[m6] (-M2) [m7] (P1) [M6] (-M2) [M6]'),
            (16.0, u'[m7] (P1) [M6] (-M2) [M6] (P1) [P5]'),
            (18.0, u'[M6] (-M2) [M6] (P1) [P5] (P1) [P8]'),
            (20.0, u'[M6] (P1) [P5] (P1) [P8] (P5) [P4]'),
            (22.0, u'[P5] (P1) [P8] (P5) [P4] (P1) [M3]'),
            (26.0, u'[P8] (P5) [P4] (P1) [M3] (-M2) [A4]'),
            (28.0, u'[P4] (P1) [M3] (-M2) [A4] (-m2) [P4]'),
            (30.0, u'[M3] (-M2) [A4] (-m2) [P4] (P1) [m3]')]

def series_maker(lotuples):
    "Turn a List Of TUPLES (offset, 'value') into a Series"
    return pandas.Series([x[1] for x in lotuples], index=[x[0] for x in lotuples])


class TestNGramIndexer(unittest.TestCase):
    def test_ngram_0(self):
        # most basic test
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A a B', u'B b C', u'C c D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_0a(self):
        # like test _0 but with an extra element in "scores" and no "horizontal" assignment
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A B', u'B C', u'C D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_0b(self):
        # like test _0 but with u'mark singles' instead of u'mark_singles'
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark singles': False}
        expected = [pandas.Series([u'A a B', u'B b C', u'C c D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_1(self):
        # adds the brackets and parentheses
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark_singles': True}
        expected = [pandas.Series([u'[A] (a) [B]', u'[B] (b) [C]', u'[C] (c) [D]'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_2(self):
        # test _0 but n=3
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 3, u'horizontal': [1], u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A a B b C', u'B b C c D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_3(self):
        # test _0 but with two verticals
        vertical_a = pandas.Series(['A', 'B', 'C', 'D'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W'])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [2], u'vertical': [0, 1], u'mark_singles': False}
        expected = [pandas.Series([u'[A Z] a [B X]', u'[B X] b [C Y]', u'[C Y] c [D W]'])]
        ng_ind = ngram.NGramIndexer([vertical_a, vertical_b, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_4(self):
        # test _0 but with two horizontals, and the order of u'horizontal' setting is important
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal_b = pandas.Series(['z', 'x', 'y'], index=[1, 2, 3])
        horizontal_a = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A (a z) B', u'B (b x) C', u'C (c y) D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal_b, horizontal_a], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_5(self):
        # combination of tests _3 and _4
        vertical_a = pandas.Series(['A', 'B', 'C', 'D'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W'])
        horizontal_b = pandas.Series(['z', 'x', 'y'], index=[1, 2, 3])
        horizontal_a = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [3, 0], u'mark_singles': False}
        expected = [pandas.Series([u'[A Z] (a z) [B X]',
                                   u'[B X] (b x) [C Y]', u'[C Y] (c y) [D W]'])]
        ng_ind = ngram.NGramIndexer([vertical_b, horizontal_b, horizontal_a, vertical_a], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_6(self):
        # test constructor fails when it should
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        setts = {u'n':0, u'vertical': [0]}  # n is too short
        self.assertRaises(RuntimeError, ngram.NGramIndexer, [vertical], setts)
        setts = {u'n':14, u'horizontal': [0]}  # no "vertical" parts
        self.assertRaises(RuntimeError, ngram.NGramIndexer, [vertical], setts)

    def test_ngram_7(self):
        # test _0 with a terminator; nothing should be picked up after terminator
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'terminator': [u'C']}
        expected = [pandas.Series([u'[A] (a) [B]'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_8(self):
        # test _5 with a terminator; nothing should be picked up before terminator
        vertical_a = pandas.Series(['A', 'B', 'C', 'D'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W'])
        horizontal_b = pandas.Series(['z', 'x', 'y'], index=[1, 2, 3])
        horizontal_a = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [3, 0], u'terminator': [u'X']}
        expected = [pandas.Series([u'[C Y] (c y) [D W]'], index=[2])]
        ng_ind = ngram.NGramIndexer([vertical_b, horizontal_b, horizontal_a, vertical_a], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_9(self):
        # test _9 but longer; things happen before and after terminator
        vertical_a = pandas.Series(['A', 'B', 'C', 'D', 'E'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W', 'V'])
        horizontal_b = pandas.Series(['z', 'x', 'y', 'w'], index=[1, 2, 3, 4])
        horizontal_a = pandas.Series(['a', 'b', 'c', 'd'], index=[1, 2, 3, 4])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [3, 0], u'terminator': [u'C']}
        expected = [pandas.Series([u'[A Z] (a z) [B X]', u'[D W] (d w) [E V]'], index=[0, 3])]
        ng_ind = ngram.NGramIndexer([vertical_b, horizontal_b, horizontal_a, vertical_a], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_10(self):
        # test _0 with too few "horizontal" things (should use "continuer" character in settings)
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'b'], index=[1, 2])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A a B', u'B b C', u'C _ D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_11(self):
        # test _10 with one "horizontal" thing at the end
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['z'], index=[3])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A _ B', u'B _ C', u'C z D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_12(self):
        # test _11 with one missing "horizontal" thing in the middle
        vertical = pandas.Series(['A', 'B', 'C', 'D'])
        horizontal = pandas.Series(['a', 'z'], index=[1, 3])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A a B', u'B _ C', u'C z D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_13(self):
        # test _0 with too few "vertical" things (last should be repeated)
        vertical = pandas.Series(['A', 'B', 'C'])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A a B', u'B b C', u'C c C'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_14(self):
        # test _13 with one missing "vertical" thing in the middle
        vertical = pandas.Series(['A', 'C', 'D'], index=[0, 2, 3])
        horizontal = pandas.Series(['a', 'b', 'c'], index=[1, 2, 3])
        setts = {u'n': 2, u'horizontal': [1], u'vertical': [0], u'mark_singles': False}
        expected = [pandas.Series([u'A a A', u'A b C', u'C c D'])]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_15(self):
        # longer test, inspired by the first five measures of "Kyrie.krn" parts 1 and 3
        vertical = series_maker(VERTICAL_TUPLES)
        horizontal = series_maker(HORIZONTAL_TUPLES)
        setts = {u'n': 4, u'horizontal': [1], u'vertical': [0], u'continuer': u'P1',
                 u'terminator': u'Rest', u'mark_singles': True}
        expected = [series_maker(EXPECTED)]
        ng_ind = ngram.NGramIndexer([vertical, horizontal], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_16a(self):
        # test _9 but with three "vertical" parts and no terminator
        vertical_a = pandas.Series(['A', 'B', 'C', 'D', 'E'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W', 'V'])
        vertical_c = pandas.Series(['Q', 'R', 'S', 'T', 'U'])
        horizontal_b = pandas.Series(['z', 'x', 'y', 'w'], index=[1, 2, 3, 4])
        horizontal_a = pandas.Series(['a', 'b', 'c', 'd'], index=[1, 2, 3, 4])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [3, 0, 4]}
        expected = [pandas.Series([u'[A Z Q] (a z) [B X R]', u'[B X R] (b x) [C Y S]',
                                   u'[C Y S] (c y) [D W T]', u'[D W T] (d w) [E V U]'],
                                   index=[0, 1, 2, 3])]
        ng_ind = ngram.NGramIndexer([vertical_b, horizontal_b, horizontal_a,
                                     vertical_a, vertical_c], setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_16b(self):
        # test _16a but with a MagicMock for the formatter
        vertical_a = pandas.Series(['A', 'B', 'C', 'D', 'E'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W', 'V'])
        vertical_c = pandas.Series(['Q', 'R', 'S', 'T', 'U'])
        horizontal_b = pandas.Series(['z', 'x', 'y', 'w'], index=[1, 2, 3, 4])
        horizontal_a = pandas.Series(['a', 'b', 'c', 'd'], index=[1, 2, 3, 4])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [3, 0, 4]}
        ng_ind = ngram.NGramIndexer([vertical_b, horizontal_b, horizontal_a,
                                     vertical_a, vertical_c], setts)
        with mock.patch(u'vis.analyzers.indexers.ngram.NGramIndexer._format_thing') as mock_f:
            mock_f.return_value = u''
            ng_ind.run()
            calls = mock_f.call_args_list
            # 13 calls because there's one at the end when we run off the end of the list
            self.assertEqual(13, len(calls))
            expected_calls = [['A', 'Z', 'Q'],
                              ['a', 'z'],
                              ['B', 'X', 'R'],
                              ['B', 'X', 'R'],
                              ['b', 'x'],
                              ['C', 'Y', 'S'],
                              ['C', 'Y', 'S'],
                              ['c', 'y'],
                              ['D', 'W', 'T'],
                              ['D', 'W', 'T'],
                              ['d', 'w'],
                              ['E', 'V', 'U'],
                              ['E', 'V', 'U']]
            actual_calls = [x[0][0] for x in calls]  # just the "things" argument
            self.assertSequenceEqual(expected_calls, actual_calls)

    def test_ngram_17(self):
        # test _16a but with four "vertical" parts
        vertical_a = pandas.Series(['A', 'B', 'C', 'D', 'E'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W', 'V'])
        vertical_c = pandas.Series(['Q', 'R', 'S', 'T', 'U'])
        vertical_d = pandas.Series(['J', 'K', 'L', 'M', 'N'])
        horizontal_b = pandas.Series(['z', 'x', 'y', 'w'], index=[1, 2, 3, 4])
        horizontal_a = pandas.Series(['a', 'b', 'c', 'd'], index=[1, 2, 3, 4])
        setts = {u'n': 2, u'horizontal': [2, 1], u'vertical': [3, 0, 4, 5]}
        expected = [pandas.Series([u'[A Z Q J] (a z) [B X R K]', u'[B X R K] (b x) [C Y S L]',
                                   u'[C Y S L] (c y) [D W T M]', u'[D W T M] (d w) [E V U N]'],
                                   index=[0, 1, 2, 3])]
        ng_ind = ngram.NGramIndexer([vertical_b, horizontal_b, horizontal_a,
                                     vertical_a, vertical_c, vertical_d],
                                     setts)
        actual = ng_ind.run()
        self.assertEqual(len(expected), len(actual))
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i].values), list(actual[i].values))

    def test_ngram_18(self):
        # n=1
        vertical_a = pandas.Series(['A', 'B', 'C', 'D', 'E'])
        vertical_b = pandas.Series(['Z', 'X', 'Y', 'W', 'V'])
        vertical_c = pandas.Series(['Q', 'R', 'S', 'T', 'U'])
        vertical_d = pandas.Series(['J', 'K', 'L', 'M', 'N'])
        setts_many = {u'n': 1, u'vertical': [0, 1, 2, 3]}
        setts_one = {u'n': 1, u'vertical': [0], u'mark_singles': False}
        expected_many = [pandas.Series([u'[A Z Q J]', u'[B X R K]', u'[C Y S L]', u'[D W T M]',
                                   u'[E V U N]'],
                                  index=[0, 1, 2, 3, 4])]
        expected_one = [pandas.Series([u'A', u'B', u'C', u'D', u'E'], index=[0, 1, 2, 3, 4])]
        ng_many = ngram.NGramIndexer([vertical_a, vertical_b, vertical_c, vertical_d], setts_many)
        ng_one = ngram.NGramIndexer([vertical_a, vertical_b, vertical_c, vertical_d], setts_one)
        actual_many = ng_many.run()
        actual_one = ng_one.run()
        self.assertEqual(len(expected_one), len(actual_one))
        for i in xrange(len(expected_one)):
            self.assertSequenceEqual(list(expected_one[i].index), list(actual_one[i].index))
            self.assertSequenceEqual(list(expected_one[i].values), list(actual_one[i].values))
        self.assertEqual(len(expected_many), len(actual_many))
        for i in xrange(len(expected_many)):
            self.assertSequenceEqual(list(expected_many[i].index), list(actual_many[i].index))
            self.assertSequenceEqual(list(expected_many[i].values), list(actual_many[i].values))

    def test_ngram_format_1(self):
        # one thing, it's a terminator (don't mark singles)
        # pylint: disable=W0212
        things = [u'A']
        m_singles = False
        self.assertRaises(RuntimeWarning, ngram.NGramIndexer._format_thing, things, m_singles, None,
                          terminator=[u'A'])

    def test_ngram_format_2(self):
        # one thing, don't mark singles
        # pylint: disable=W0212
        things = [u'A']
        m_singles = False
        expected = u'A'
        actual = ngram.NGramIndexer._format_thing(things, m_singles)
        self.assertTrue(isinstance(actual, unicode))
        self.assertEqual(expected, actual)

    def test_ngram_format_3(self):
        # one thing, mark singles
        # pylint: disable=W0212
        things = [u'A']
        m_singles = True
        expected = u'[A]'
        actual = ngram.NGramIndexer._format_thing(things, m_singles)
        self.assertTrue(isinstance(actual, unicode))
        self.assertEqual(expected, actual)

    def test_ngram_format_4(self):
        # many things, terminator first
        # pylint: disable=W0212
        things = [u'A', u'B', u'C']
        m_singles = False
        self.assertRaises(RuntimeWarning, ngram.NGramIndexer._format_thing, things, m_singles,
                          (u'[', u']'), terminator=[u'A'])

    def test_ngram_format_5(self):
        # many things, terminator middle
        # pylint: disable=W0212
        things = [u'A', u'B', u'C']
        m_singles = False
        self.assertRaises(RuntimeWarning, ngram.NGramIndexer._format_thing, things, m_singles,
                          (u'[', u']'), terminator=[u'B'])

    def test_ngram_format_6(self):
        # many things, terminator last
        # pylint: disable=W0212
        things = [u'A', u'B', u'C']
        m_singles = False
        self.assertRaises(RuntimeWarning, ngram.NGramIndexer._format_thing, things, m_singles,
                          (u'[', u']'), terminator=[u'C'])

    def test_ngram_format_7(self):
        # many things, don't mark singles
        # pylint: disable=W0212
        things = [u'A', u'B', u'C']
        m_singles = False
        expected = u'[A B C]'
        actual = ngram.NGramIndexer._format_thing(things, m_singles)
        self.assertTrue(isinstance(actual, unicode))
        self.assertEqual(expected, actual)

    def test_ngram_format_8(self):
        # many things, mark singles
        # pylint: disable=W0212
        things = [u'A', u'B', u'C']
        m_singles = True
        expected = u'[A B C]'
        actual = ngram.NGramIndexer._format_thing(things, m_singles)
        self.assertTrue(isinstance(actual, unicode))
        self.assertEqual(expected, actual)

    def test_ngram_format_9(self):
        # many things, change the markers
        # pylint: disable=W0212
        things = [u'A', u'B', u'C']
        m_singles = False
        expected = u'$A B C&'
        actual = ngram.NGramIndexer._format_thing(things, m_singles, (u'$', u'&'))
        self.assertTrue(isinstance(actual, unicode))
        self.assertEqual(expected, actual)

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
NGRAM_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestNGramIndexer)
