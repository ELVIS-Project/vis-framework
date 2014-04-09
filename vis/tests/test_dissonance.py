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
from numpy import nan, isnan
import pandas
from vis.analyzers.indexers import dissonance


class TestDissonanceIndexer(unittest.TestCase):
    @staticmethod
    def make_dataframe(name, labels, from_these):
        """
        Make a DataFrame in the style that comes from an Indexer.run()

        :param basestring name: The name of the indexer you're pretending to be.
        :param labels: The labels for each elements of ``from_these``.
        :type labels: list of basestring
        :param from_these: The Series to put as the new DataFrame's columns.
        :type from_these: list of :class:`pandas.Series`

        :returns: A DataFrame in the style of an Indexer.run()
        :rtype: :class:`pandas.DataFrame`
        """
        tuples = [(name, labels[i]) for i in xrange(len(labels))]
        multiindex = pandas.MultiIndex.from_tuples(tuples, names=['Indexer', 'Parts'])
        return pandas.DataFrame(from_these, index=multiindex).T

    def test_nancons_1(self):
        # that it picks up simple major/minor things as dissonant
        in_vals = [u'm2', u'M2', u'P4', u'm7', u'M7']
        expected = pandas.Series(in_vals)
        actual = dissonance.DissonanceIndexer.nan_consonance(expected)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_nancons_2(self):
        # that it picks up diminished/augmented dissonances
        in_vals = ['A4', 'd5', 'A1', 'd8']
        expected = pandas.Series(in_vals)
        actual = dissonance.DissonanceIndexer.nan_consonance(expected)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_nancons_3(self):
        # that consonances are properly noted as consonant
        in_vals = [u'm3', u'M3', u'P5', u'm6', u'M6']
        actual = dissonance.DissonanceIndexer.nan_consonance(pandas.Series(in_vals))
        self.assertEqual(len(in_vals), len(actual))
        self.assertTrue(all([isnan(x) for x in actual]))

    def test_nancons_4(self):
        # a quasi-realistic, single-part test
        in_ser = pandas.Series(['m3', 'M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7'])
        expected = pandas.Series([nan, 'M2', 'm2', 'P4', 'd5', nan, nan, 'm7'])
        actual = dissonance.DissonanceIndexer.nan_consonance(in_ser)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_special_fourths_1(self):
        """
        +------------------+----------+
        | Part Combination | Interval |
        +==================+==========+
        | 0,1              | M3       |
        +------------------+----------+
        | 0,2              | P4       |  retained
        +------------------+----------+
        | 0,3              | M3       |
        +------------------+----------+
        | 1,2              | M3       |
        +------------------+----------+
        | 1,3              | M3       |
        +------------------+----------+
        | 2,3              | P8       |
        +------------------+----------+
        """
        in_series = pandas.Series(['M3', 'P4', 'M3', 'M3', 'M3', 'P8'],
                                  index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        expected = pandas.Series(['M3', 'P4', 'M3', 'M3', 'M3', 'P8'],
                                 index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        actual = dissonance.DissonanceIndexer.special_fourths(in_series)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_special_fourths_2(self):
        """
        +------------------+----------+
        | Part Combination | Interval |
        +==================+==========+
        | 0,1              | P4       |  removed
        +------------------+----------+
        | 0,2              | P4       |  retained
        +------------------+----------+
        | 0,3              | M3       |
        +------------------+----------+
        | 1,2              | P8       |
        +------------------+----------+
        | 1,3              | M3       |
        +------------------+----------+
        | 2,3              | P8       |
        +------------------+----------+
        """
        in_series = pandas.Series(['P4', 'P4', 'M3', 'P8', 'M3', 'P8'],
                                  index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        expected = pandas.Series([nan, 'P4', 'M3', 'P8', 'M3', 'P8'],
                                 index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        actual = dissonance.DissonanceIndexer.special_fourths(in_series)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for i in xrange(len(expected)):
            # NB: if you get a TypeError here, that means failure
            self.assertTrue((expected.iloc[i] == actual.iloc[i]) or
                            (isnan(expected.iloc[i]) and isnan(actual.iloc[i])))

    def test_special_fourths_3(self):
        """
        +------------------+----------+
        | Part Combination | Interval |  all retained
        +==================+==========+
        | 0,1              | M3       |
        +------------------+----------+
        | 0,2              | P5       |
        +------------------+----------+
        | 0,3              | M3       |
        +------------------+----------+
        | 1,2              | M3       |
        +------------------+----------+
        | 1,3              | M3       |
        +------------------+----------+
        | 2,3              | P8       |
        +------------------+----------+
        """
        in_series = pandas.Series(['M3', 'P5', 'M3', 'M3', 'M3', 'P8'],
                                  index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        expected = pandas.Series(['M3', 'P5', 'M3', 'M3', 'M3', 'P8'],
                                 index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        actual = dissonance.DissonanceIndexer.special_fourths(in_series)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))


    def test_ind_1(self):
        # A quasi-realistic, multi-part test---special_P4 is False
        in_val = [pandas.Series(['m3', 'M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7']),
                  pandas.Series(['M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7', 'm3']),
                  pandas.Series(['m2', 'P4', 'd5', 'P5', 'M6', 'm7', 'm3', 'M2'])]
        in_val = TestDissonanceIndexer.make_dataframe(u'interval.IntervalIndexer',
                                                      ['0,1', '0,2', '1,2'],
                                                      in_val)
        expected = {'0,1': pandas.Series([nan, 'M2', 'm2', 'P4', 'd5', nan, nan, 'm7']),
                    '0,2': pandas.Series(['M2', 'm2', 'P4', 'd5', nan, nan, 'm7', nan]),
                    '1,2': pandas.Series(['m2', 'P4', 'd5', nan, nan, 'm7', nan, 'M2'])}
        actual = dissonance.DissonanceIndexer(in_val, {u'special_P4': False})
        actual = actual.run()['dissonance.DissonanceIndexer']
        self.assertEqual(len(expected), len(actual.columns))
        for key in expected.iterkeys():
            self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
            for i in xrange(len(expected[key])):
                # NB: if you get a TypeError here, that means failure
                self.assertTrue((expected[key].iloc[i] == actual[key].iloc[i]) or
                                (isnan(expected[key].iloc[i]) and isnan(actual[key].iloc[i])))

    def test_ind_2(self):
        # A totally realistic multi-part test---special_P4 is True
        # 1: rather complicated setup
        parts_index = ['0,1', '0,2', '0,3', '1,2', '1,3', '2,3']
        offset_index = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 8.0, 9.0, 9.5]
        i_event_lists = [['P4', 'M6', 'P8', 'M3', 'P5', 'm3'],
                         ['P5', 'M6', 'M2', 'M2', nan, 'P4'],
                         ['m3', 'm6', 'm3', 'P4', 'P8', 'P5'],
                         ['m3', 'P5', 'P5', 'M3', 'M3', 'P8'],
                         ['M3', 'M6', 'M3', 'P4', 'P8', 'P5'],
                         ['m3', 'P5', 'P5', 'M3', 'M3', 'P8'],
                         [nan, 'P4', 'm6', 'M2', 'P4', 'm3'],
                         ['m3', 'm6', 'm3', 'P4', 'P1', 'P5'],
                         [nan, 'P8', 'P5', 'M6', 'M3', 'P5'],
                         ['M2', 'A4', 'M6', 'M3', 'P5', 'm3'],
                         ['m3', 'P5', 'P5', 'M3', 'M3', 'P8'],
                         ['P4', 'M6', 'P8', 'M3', 'P5', 'm3'],
                         ['m3', 'm6', 'm3', 'P4', 'P8', 'P5'],
                         ['m6', 'm3', 'm3', 'P5', 'P5', 'P1'],
                         ['P5', nan, nan, 'm6', 'm6', nan]]
        i_event_lists = [pandas.Series(x, index=parts_index) for x in i_event_lists]
        input_df = pandas.DataFrame(i_event_lists, index=offset_index)
        i_event_lists = [input_df[x] for x in parts_index]
        input_df = TestDissonanceIndexer.make_dataframe(u'interval.IntervalIndexer',
                                                        parts_index,
                                                        i_event_lists)
        e_event_lists = [[nan, nan, nan, nan, nan, nan],
                         [nan, nan, 'M2', 'M2', nan, 'P4'],
                         [nan, nan, nan, 'P4', nan, nan],
                         [nan, nan, nan, nan, nan, nan],
                         [nan, nan, nan, 'P4', nan, nan],
                         [nan, nan, nan, nan, nan, nan],
                         [nan, nan, nan, 'M2', 'P4', nan],
                         [nan, nan, nan, 'P4', nan, nan],
                         [nan, nan, nan, nan, nan, nan],
                         ['M2', 'A4', nan, nan, nan, nan],
                         [nan, nan, nan, nan, nan, nan],
                         [nan, nan, nan, nan, nan, nan],
                         [nan, nan, nan, 'P4', nan, nan],
                         [nan, nan, nan, nan, nan, nan],
                         [nan, nan, nan, nan, nan, nan]]
        e_event_lists = [pandas.Series(x, index=parts_index) for x in e_event_lists]
        expected = pandas.DataFrame(e_event_lists, index=offset_index)
        # 2: run the test
        actual = dissonance.DissonanceIndexer(input_df, {u'special_P4': True})
        actual = actual.run()['dissonance.DissonanceIndexer']
        # 3: check everything out
        self.assertEqual(len(expected.columns), len(actual.columns))
        for key in parts_index:
            self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
            for i in xrange(len(expected[key])):
                # NB: if you get a TypeError here, that means failure
                self.assertTrue((expected[key].iloc[i] == actual[key].iloc[i]) or
                                (isnan(expected[key].iloc[i]) and isnan(actual[key].iloc[i])))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
DISSONANCE_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestDissonanceIndexer)
