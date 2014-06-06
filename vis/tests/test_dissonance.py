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
import mock
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

    def test_nancons_1a(self):
        # that it picks up simple major/minor things as dissonant
        in_vals = [u'm2', u'M2', u'P4', u'm7', u'M7']
        expected = pandas.Series(in_vals)
        actual = dissonance.DissonanceIndexer.nan_consonance(expected)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_nancons_1b(self):
        # with descending intervals
        in_vals = [u'-m2', u'-M2', u'-P4', u'-m7', u'-M7']
        expected = pandas.Series(in_vals)
        actual = dissonance.DissonanceIndexer.nan_consonance(expected)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_nancons_2a(self):
        # that it picks up diminished/augmented dissonances
        in_vals = ['A4', 'd5', 'A1', 'd8']
        expected = pandas.Series(in_vals)
        actual = dissonance.DissonanceIndexer.nan_consonance(expected)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_nancons_2b(self):
        # with descending intervals
        in_vals = ['-A4', '-d5', '-A1', '-d8']
        expected = pandas.Series(in_vals)
        actual = dissonance.DissonanceIndexer.nan_consonance(expected)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_nancons_3a(self):
        # that consonances are properly noted as consonant
        in_vals = [u'm3', u'M3', u'P5', u'm6', u'M6']
        actual = dissonance.DissonanceIndexer.nan_consonance(pandas.Series(in_vals))
        self.assertEqual(len(in_vals), len(actual))
        self.assertTrue(all([isnan(x) for x in actual]))

    def test_nancons_3b(self):
        # with descending intervals
        in_vals = [u'-m3', u'-M3', u'-P5', u'-m6', u'-M6']
        actual = dissonance.DissonanceIndexer.nan_consonance(pandas.Series(in_vals))
        self.assertEqual(len(in_vals), len(actual))
        self.assertTrue(all([isnan(x) for x in actual]))

    def test_nancons_4a(self):
        # a quasi-realistic, single-part test
        in_ser = pandas.Series(['m3', 'M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7'])
        expected = pandas.Series([nan, 'M2', 'm2', 'P4', 'd5', nan, nan, 'm7'])
        actual = dissonance.DissonanceIndexer.nan_consonance(in_ser)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_nancons_4b(self):
        # with descending intervals
        in_ser = pandas.Series(['-m3', '-M2', '-m2', '-P4', '-d5', '-P5', '-M6', '-m7'])
        expected = pandas.Series([nan, '-M2', '-m2', '-P4', '-d5', nan, nan, '-m7'])
        actual = dissonance.DissonanceIndexer.nan_consonance(in_ser)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_nancons_5(self):
        # test_nancons_4, with some 'Rest' objects
        in_ser = pandas.Series(['m3', 'Rest', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7'])
        expected = pandas.Series([nan, nan, 'm2', 'P4', 'd5', nan, nan, 'm7'])
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

    def test_special_fifths_1(self):
        """
        +------------------+----------+
        | Part Combination | Interval |
        +==================+==========+
        | 0,1              | M3       |
        +------------------+----------+
        | 0,2              | d5       |  retained
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
        in_series = pandas.Series(['M3', 'd5', 'M3', 'M3', 'M3', 'P8'],
                                  index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        expected = pandas.Series(['M3', 'd5', 'M3', 'M3', 'M3', 'P8'],
                                 index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        actual = dissonance.DissonanceIndexer.special_fifths(in_series)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_special_fifths_2(self):
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
        | 1,2              | M6       |
        +------------------+----------+
        | 1,3              | M3       |
        +------------------+----------+
        | 2,3              | P8       |
        +------------------+----------+
        """
        in_series = pandas.Series(['d5', 'd5', 'M3', 'M6', 'M3', 'P8'],
                                  index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        expected = pandas.Series([nan, 'd5', 'M3', 'M6', 'M3', 'P8'],
                                 index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        actual = dissonance.DissonanceIndexer.special_fifths(in_series)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for i in xrange(len(expected)):
            # NB: if you get a TypeError here, that means failure
            self.assertTrue((expected.iloc[i] == actual.iloc[i]) or
                            (isnan(expected.iloc[i]) and isnan(actual.iloc[i])))

    def test_special_fifths_3(self):
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
        actual = dissonance.DissonanceIndexer.special_fifths(in_series)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_ind_1(self):
        # A quasi-realistic, multi-part test---special_P4 and special_d5 are False
        in_val = [pandas.Series(['m3', 'M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7']),
                  pandas.Series(['M2', 'm2', 'P4', 'd5', 'P5', 'M6', 'm7', 'm3']),
                  pandas.Series(['m2', 'P4', 'd5', 'P5', 'M6', 'm7', 'm3', 'M2'])]
        in_val = TestDissonanceIndexer.make_dataframe(u'interval.IntervalIndexer',
                                                      ['0,1', '0,2', '1,2'],
                                                      in_val)
        expected = {'0,1': pandas.Series([nan, 'M2', 'm2', 'P4', 'd5', nan, nan, 'm7']),
                    '0,2': pandas.Series(['M2', 'm2', 'P4', 'd5', nan, nan, 'm7', nan]),
                    '1,2': pandas.Series(['m2', 'P4', 'd5', nan, nan, 'm7', nan, 'M2'])}
        actual = dissonance.DissonanceIndexer(in_val, {'special_P4': False, 'special_d5': False})
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


@mock.patch('vis.analyzers.indexers.dissonance._SUSP_NODISS_LABEL',
            mock.MagicMock(name='no dissonance'))
@mock.patch('vis.analyzers.indexers.dissonance._SUSP_OTHER_LABEL',
            mock.MagicMock(name='other dissonance'))
@mock.patch('vis.analyzers.indexers.dissonance._SUSP_USUSP_LABEL',
            mock.MagicMock(name='upper-voice suspension'))
@mock.patch('vis.analyzers.indexers.dissonance._SUSP_LSUSP_LABEL',
            mock.MagicMock(name='lower-voice suspension'))
class TestSuspensionIndexer(unittest.TestCase):
    # NOTE: we patch the objects to ensure all four are different, and that we don't need isnan()
    def test_ind_func_1(self):
        # simple: it's a suspension
        # 1.) prepare inputs
        columns = (('interval.IntervalIndexer', '0,1'),
                   ('interval.HorizontalIntervalIndexer', '0'),
                   ('interval.HorizontalIntervalIndexer', '1'),
                   ('dissonance.DissonanceIndexer', '0,1'))
        columns = pandas.MultiIndex.from_tuples(columns)
        row_one = ['P8', 'P1', 'M2', nan]
        row_two = ['m7', '-M2', 'P1', 'm7']
        row_three = ['m6', '-M2', 'P1', nan]
        row_one = pandas.Series(row_one, index=columns)
        row_two = pandas.Series(row_two, index=columns)
        row_three = pandas.Series(row_three, index=columns)
        # 2.) prepare expected
        expected = pandas.Series([dissonance._SUSP_USUSP_LABEL], index=['0,1'])
        # 3.) run and check
        actual = dissonance.susp_ind_func((row_one, row_two, row_three))
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for key in expected.index:
            self.assertEqual(expected[key], actual[key])

    def test_ind_func_2(self):
        # simple: it's not a suspension (lower part into diss is P1)
        # 1.) prepare inputs
        columns = (('interval.IntervalIndexer', '0,1'),
                   ('interval.HorizontalIntervalIndexer', '0'),
                   ('interval.HorizontalIntervalIndexer', '1'),
                   ('dissonance.DissonanceIndexer', '0,1'))
        columns = pandas.MultiIndex.from_tuples(columns)
        row_one = ['M6', 'M2', 'P1', nan]
        row_two = ['M7', 'M2', 'M3', 'M7']
        row_three = ['m6', '-M2', 'P1', nan]
        row_one = pandas.Series(row_one, index=columns)
        row_two = pandas.Series(row_two, index=columns)
        row_three = pandas.Series(row_three, index=columns)
        # 2.) prepare expected
        expected = pandas.Series([dissonance._SUSP_OTHER_LABEL], index=['0,1'])
        # 3.) run and check
        actual = dissonance.susp_ind_func((row_one, row_two, row_three))
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for key in expected.index:
            self.assertEqual(expected[key], actual[key])

    def test_ind_func_3(self):
        # simple: it's not a suspension (lower part into diss is not P1)
        # 1.) prepare inputs
        columns = (('interval.IntervalIndexer', '0,1'),
                   ('interval.HorizontalIntervalIndexer', '0'),
                   ('interval.HorizontalIntervalIndexer', '1'),
                   ('dissonance.DissonanceIndexer', '0,1'))
        columns = pandas.MultiIndex.from_tuples(columns)
        row_one = ['M6', 'M2', '-M2', nan]
        row_two = ['M7', 'M2', 'M3', 'M7']
        row_three = ['m6', '-M2', 'P1', nan]
        row_one = pandas.Series(row_one, index=columns)
        row_two = pandas.Series(row_two, index=columns)
        row_three = pandas.Series(row_three, index=columns)
        # 2.) prepare expected
        expected = pandas.Series([dissonance._SUSP_OTHER_LABEL], index=['0,1'])
        # 3.) run and check
        actual = dissonance.susp_ind_func((row_one, row_two, row_three))
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for key in expected.index:
            self.assertEqual(expected[key], actual[key])

    def test_ind_func_4(self):
        # simple: it's not a dissonance
        # 1.) prepare inputs
        columns = (('interval.IntervalIndexer', '0,1'),
                   ('interval.HorizontalIntervalIndexer', '0'),
                   ('interval.HorizontalIntervalIndexer', '1'),
                   ('dissonance.DissonanceIndexer', '0,1'))
        columns = pandas.MultiIndex.from_tuples(columns)
        row_one = ['M3', 'M3', 'M3', nan]
        row_two = ['M3', '-M2', 'P1', nan]
        row_three = ['M2', '-M2', 'P1', 'M2']
        row_one = pandas.Series(row_one, index=columns)
        row_two = pandas.Series(row_two, index=columns)
        row_three = pandas.Series(row_three, index=columns)
        # 2.) prepare expected
        expected = pandas.Series([dissonance._SUSP_NODISS_LABEL], index=['0,1'])
        # 3.) run and check
        actual = dissonance.susp_ind_func((row_one, row_two, row_three))
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for key in expected.index:
            self.assertEqual(expected[key], actual[key])

    def test_ind_func_5(self):
        # simple: it would be a suspension, even though the lower voice drops out
        # 1.) prepare inputs
        columns = (('interval.IntervalIndexer', '0,1'),
                   ('interval.HorizontalIntervalIndexer', '0'),
                   ('interval.HorizontalIntervalIndexer', '1'),
                   ('dissonance.DissonanceIndexer', '0,1'))
        columns = pandas.MultiIndex.from_tuples(columns)
        row_one = ['P8', 'P1', 'M2', nan]
        row_two = ['m7', '-M2', nan, 'm7']
        row_three = [nan, '-M2', nan, nan]
        row_one = pandas.Series(row_one, index=columns)
        row_two = pandas.Series(row_two, index=columns)
        row_three = pandas.Series(row_three, index=columns)
        # 2.) prepare expected
        expected = pandas.Series([dissonance._SUSP_OTHER_LABEL], index=['0,1'])
        # 3.) run and check
        actual = dissonance.susp_ind_func((row_one, row_two, row_three))
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for key in expected.index:
            self.assertEqual(expected[key], actual[key])

    def test_ind_func_6(self):
        # multi-part: mixed "other" and "no" dissonances
        # NB: the input is taken from the first offset of bwv77.mxl
        # 1.) prepare inputs
        columns = (('interval.IntervalIndexer', '0,1'),
                   ('interval.IntervalIndexer', '0,2'),
                   ('interval.IntervalIndexer', '0,3'),
                   ('interval.IntervalIndexer', '1,2'),
                   ('interval.IntervalIndexer', '1,3'),
                   ('interval.IntervalIndexer', '2,3'),
                   ('interval.HorizontalIntervalIndexer', '0'),
                   ('interval.HorizontalIntervalIndexer', '1'),
                   ('interval.HorizontalIntervalIndexer', '2'),
                   ('interval.HorizontalIntervalIndexer', '3'),
                   ('dissonance.DissonanceIndexer', '0,1'),
                   ('dissonance.DissonanceIndexer', '0,2'),
                   ('dissonance.DissonanceIndexer', '0,3'),
                   ('dissonance.DissonanceIndexer', '1,2'),
                   ('dissonance.DissonanceIndexer', '1,3'),
                   ('dissonance.DissonanceIndexer', '2,3'))
        columns = pandas.MultiIndex.from_tuples(columns)
        #         int: 0,1  0,2  0,3  1,2  1,3  2,3
        #         horiz: 0, 1, 2, 3
        #         diss: 0,1  0,2  0,3  1,2  1,3  2,3
        row_one = ['P4', 'M6', 'P8', 'M3', 'P5', 'm3',
                   'M2', nan, 'M2', nan,
                   nan, nan, nan, nan, nan, nan]
        row_two = ['P5', 'M6', 'M2', 'M2', nan, 'P4',
                   'm2', 'P4', 'M2', 'P1',
                   nan, nan, 'M2', 'M2', nan, 'P4']  # they're all "other"
        row_three = ['m3', 'm6', 'm3', 'P4', 'P8', 'P5',
                     'M2', 'M2', 'm3', '-M2',
                     nan, nan, nan, 'P4', nan, nan]
        row_one = pandas.Series(row_one, index=columns)
        row_two = pandas.Series(row_two, index=columns)
        row_three = pandas.Series(row_three, index=columns)
        # 2.) prepare expected
        expected = pandas.Series([dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_OTHER_LABEL,
                                  dissonance._SUSP_OTHER_LABEL,
                                  dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_OTHER_LABEL],
                                 index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        # 3.) run and check
        actual = dissonance.susp_ind_func((row_one, row_two, row_three))
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for key in expected.index:
            self.assertEqual(expected[key], actual[key])

    def test_ind_func_7(self):  # TODO: verify the test!
        # multi-part: mixed "susp," "other," and "no" dissonances
        # NB: the input is taken from bwv77.mxl, offsets 10.5, 11.0, and 11.5
        # 1.) prepare inputs
        columns = (('interval.IntervalIndexer', '0,1'),
                   ('interval.IntervalIndexer', '0,2'),
                   ('interval.IntervalIndexer', '0,3'),
                   ('interval.IntervalIndexer', '1,2'),
                   ('interval.IntervalIndexer', '1,3'),
                   ('interval.IntervalIndexer', '2,3'),
                   ('interval.HorizontalIntervalIndexer', '0'),
                   ('interval.HorizontalIntervalIndexer', '1'),
                   ('interval.HorizontalIntervalIndexer', '2'),
                   ('interval.HorizontalIntervalIndexer', '3'),
                   ('dissonance.DissonanceIndexer', '0,1'),
                   ('dissonance.DissonanceIndexer', '0,2'),
                   ('dissonance.DissonanceIndexer', '0,3'),
                   ('dissonance.DissonanceIndexer', '1,2'),
                   ('dissonance.DissonanceIndexer', '1,3'),
                   ('dissonance.DissonanceIndexer', '2,3'))
        columns = pandas.MultiIndex.from_tuples(columns)
        #         int: 0,1  0,2  0,3  1,2  1,3  2,3
        #         horiz: 0, 1, 2, 3
        #         diss: 0,1  0,2  0,3  1,2  1,3  2,3
        row_one = ['P5', 'P8', 'M3', 'P4', 'M6', 'M3',  # IntervalIndexer
                   '-M2', 'P1', 'M2', '-M2',  # HorizontalIntervalIndexer
                   nan, nan, nan, nan, nan, nan]  # DissonanceIndexer
        row_two = ['P4', 'm6', 'M3', 'm3', 'M7', 'A5',
                   nan, '-M2', 'm2', nan,
                   nan, nan, nan, nan, 'M7', 'A5']  # M7 is susp, A5 is other (PT)
        row_three = ['P5', 'P5', 'M3', 'P1', 'M6', 'M6',
                     nan, nan, nan, nan,
                     nan, nan, nan, nan, nan, nan]
        row_one = pandas.Series(row_one, index=columns)
        row_two = pandas.Series(row_two, index=columns)
        row_three = pandas.Series(row_three, index=columns)
        # 2.) prepare expected
        expected = pandas.Series([dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_USUSP_LABEL,
                                  dissonance._SUSP_OTHER_LABEL],
                                 index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        # 3.) run and check
        actual = dissonance.susp_ind_func((row_one, row_two, row_three))
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for key in expected.index:
            self.assertEqual(expected[key], actual[key])

    def test_ind_func_8(self):
        # multi-part: mixed "susp," "other," and "no" dissonances
        # NB: this is a lower-voice suspension
        # NB: the input is taken from bwv77.mxl, offsets 5.5, 6.0, 6.5
        # 1.) prepare inputs
        columns = (('interval.IntervalIndexer', '0,1'),
                   ('interval.IntervalIndexer', '0,2'),
                   ('interval.IntervalIndexer', '0,3'),
                   ('interval.IntervalIndexer', '1,2'),
                   ('interval.IntervalIndexer', '1,3'),
                   ('interval.IntervalIndexer', '2,3'),
                   ('interval.HorizontalIntervalIndexer', '0'),
                   ('interval.HorizontalIntervalIndexer', '1'),
                   ('interval.HorizontalIntervalIndexer', '2'),
                   ('interval.HorizontalIntervalIndexer', '3'),
                   ('dissonance.DissonanceIndexer', '0,1'),
                   ('dissonance.DissonanceIndexer', '0,2'),
                   ('dissonance.DissonanceIndexer', '0,3'),
                   ('dissonance.DissonanceIndexer', '1,2'),
                   ('dissonance.DissonanceIndexer', '1,3'),
                   ('dissonance.DissonanceIndexer', '2,3'))
        columns = pandas.MultiIndex.from_tuples(columns)
        #         int: 0,1  0,2  0,3  1,2  1,3  2,3
        #         horiz: 0, 1, 2, 3
        #         diss: 0,1  0,2  0,3  1,2  1,3  2,3
        row_one = ['m3', 'P8', 'P12', 'M3', 'M10', 'P5',  # IntervalIndexer
                   '-m2', nan, 'P4', '-m3',  # HorizontalIntervalIndexer
                   nan, nan, nan, nan, nan, nan]  # DissonanceIndexer
        row_two = ['M2', 'A4', 'M13', 'M3', 'm10', '',
                   nan, '-m2', '-m2', 'M2',
                   'M2', 'A4', nan, nan, nan, nan]  # M2 is suspension; A4 is other
        row_three = ['m3', 'P5', 'P12', 'M3', 'M10', 'P8',
                     '-M2', '-M3', '-M3', 'P4',
                     nan, nan, nan, nan, nan, nan]
        row_one = pandas.Series(row_one, index=columns)
        row_two = pandas.Series(row_two, index=columns)
        row_three = pandas.Series(row_three, index=columns)
        # 2.) prepare expected
        expected = pandas.Series([dissonance._SUSP_LSUSP_LABEL,
                                  dissonance._SUSP_OTHER_LABEL,
                                  dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_NODISS_LABEL,
                                  dissonance._SUSP_NODISS_LABEL],
                                 index=['0,1', '0,2', '0,3', '1,2', '1,3', '2,3'])
        # 3.) run and check
        actual = dissonance.susp_ind_func((row_one, row_two, row_three))
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for key in expected.index:
            self.assertEqual(expected[key], actual[key])

    def test_run_1(self):
        # Given a DataFrame with a bunch of rows, ensure run() gives them to susp_ind_func(),
        # three at a time, in the right order.
        # 1.) prepare inputs
        in_frame = pandas.DataFrame({'col': pandas.Series([i for i in xrange(10)])})
        in_frame.columns = pandas.MultiIndex.from_tuples((('FakeIndexer', 'col'),))
        # Susp_Ind_Func mock's Side Effect (bare minimum for the method to not fail)
        sifse = lambda x: pandas.Series((None,), index=('None',))
        # 2.) prepare expected
        expected = []
        for i in xrange(8):  # because we won't want to start on .iloc[8] or 9
            # NB: this is a bit of a hack, since it doesn't technically make a MultiIndex, but
            #     when we run .index through list() it will look the same
            arg = [pandas.Series([j], index=[('FakeIndexer', 'col')], name=j)
                   for j in [i, i + 1, i + 2]]
            expected.append(arg)
        # 3.) run and check
        with mock.patch('vis.analyzers.indexers.dissonance.susp_ind_func') as sif:
            sif.side_effect = sifse
            dissonance.SuspensionIndexer(in_frame).run()
            calist = sif.call_args_list
        self.assertEqual(len(expected), len(calist))  # same number of calls
        for i in xrange(len(expected)):
            self.assertEqual(len(expected[i]), len(calist[i][0][0]))  # same nr of args per call
            for j in xrange(len(expected[i])):
                # check indices then values
                self.assertSequenceEqual(list(expected[i][j].index),
                                            list(calist[i][0][0][j].index))
                self.assertSequenceEqual(list(expected[i][j].values),
                                            list(calist[i][0][0][j].values))

    def test_run_2(self):
        # Given the same input as test_run_1(), with predetermined results from susp_ind_func(),
        # ensure run() reinserts the results properly
        # 1.) prepare inputs
        in_frame = pandas.DataFrame({'col': pandas.Series([i for i in xrange(10)])})
        in_frame.columns = pandas.MultiIndex.from_tuples((('FakeIndexer', 'col'),))
        in_frame.index = pandas.Index([i / 2.0 for i in xrange(10)])
        # Susp_Ind_Func mock's Side Effect
        sifse = lambda x: pandas.Series((x[0].iloc[0], x[1].iloc[0], x[2].iloc[0]),
                                        index=('left', 'middle', 'right'))
        # we have to change this so we don't have to use isnan() in step 3, which is complicated
        dissonance._SUSP_NODISS_LABEL = 'nan'
        # 2.) prepare expected
        mind = pandas.MultiIndex.from_tuples((('FakeIndexer', 'col'),
                                              ('dissonance.SuspensionIndexer', 'left'),
                                              ('dissonance.SuspensionIndexer', 'middle'),
                                              ('dissonance.SuspensionIndexer', 'right')))
        rows = ((0, dissonance._SUSP_NODISS_LABEL,
                 dissonance._SUSP_NODISS_LABEL, dissonance._SUSP_NODISS_LABEL),
                (1, 0, 1, 2),
                (2, 1, 2, 3),
                (3, 2, 3, 4),
                (4, 3, 4, 5),
                (5, 4, 5, 6),
                (6, 5, 6, 7),
                (7, 6, 7, 8),
                (8, 7, 8, 9),
                (9, dissonance._SUSP_NODISS_LABEL,
                 dissonance._SUSP_NODISS_LABEL, dissonance._SUSP_NODISS_LABEL))
        expected = pandas.DataFrame({(i / 2.0): pandas.Series(rows[i], index=mind)
                                     for i in xrange(10)}).T
        # 3.) run and check
        with mock.patch('vis.analyzers.indexers.dissonance.susp_ind_func') as sif:
            sif.side_effect = sifse
            actual = dissonance.SuspensionIndexer(in_frame).run()
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        for i in xrange(len(expected.index)):
            self.assertSequenceEqual(list(expected.iloc[i].index), list(actual.iloc[i].index))
            self.assertSequenceEqual(list(expected.iloc[i].values), list(actual.iloc[i].values))

    def test_run_3(self):
        # Combining the complexities of test_run_1() and test_run_2(), to know what happens with
        # scores that have only three offsets.
        # 1.) prepare inputs
        in_frame = pandas.DataFrame({'col': pandas.Series([i for i in xrange(3)])})
        in_frame.columns = pandas.MultiIndex.from_tuples((('FakeIndexer', 'col'),))
        in_frame.index = pandas.Index([i / 2.0 for i in xrange(3)])
        # Susp_Ind_Func mock's Side Effect
        sifse = lambda x: pandas.Series((x[0].iloc[0], x[1].iloc[0], x[2].iloc[0]),
                                        index=('left', 'middle', 'right'))
        # we have to change this so we don't have to use isnan() in step 3, which is complicated
        dissonance._SUSP_NODISS_LABEL = 'nan'
        # 2.1.) prepare exp_run for run()
        mind = pandas.MultiIndex.from_tuples((('FakeIndexer', 'col'),
                                              ('dissonance.SuspensionIndexer', 'left'),
                                              ('dissonance.SuspensionIndexer', 'middle'),
                                              ('dissonance.SuspensionIndexer', 'right')))
        rows = ((0, dissonance._SUSP_NODISS_LABEL,
                 dissonance._SUSP_NODISS_LABEL, dissonance._SUSP_NODISS_LABEL),
                (1, 0, 1, 2),
                (2, dissonance._SUSP_NODISS_LABEL,
                 dissonance._SUSP_NODISS_LABEL, dissonance._SUSP_NODISS_LABEL))
        exp_run = pandas.DataFrame({(i / 2.0): pandas.Series(rows[i], index=mind)
                                    for i in xrange(3)}).T
        # 2.2.) prepare exp_run for susp_ind_func()
        exp_sif = [[pandas.Series(i, index=(('FakeIndexer', 'col'),)) for i in xrange(3)]]
        # 3.) run
        with mock.patch('vis.analyzers.indexers.dissonance.susp_ind_func') as sif:
            sif.side_effect = sifse
            actual = dissonance.SuspensionIndexer(in_frame).run()
            calist = sif.call_args_list
        # 4.1) check for run()
        self.assertSequenceEqual(list(exp_run.index), list(actual.index))
        for i in xrange(len(exp_run.index)):
            self.assertSequenceEqual(list(exp_run.iloc[i].index), list(actual.iloc[i].index))
            self.assertSequenceEqual(list(exp_run.iloc[i].values), list(actual.iloc[i].values))
        # 4.2.) check for susp_ind_func()
        self.assertEqual(len(exp_sif), len(calist))  # same number of calls
        for i in xrange(len(exp_sif)):
            self.assertEqual(len(exp_sif[i]), len(calist[i][0][0]))  # same nr of args per call
            for j in xrange(len(exp_sif[i])):
                # check indices then values
                self.assertSequenceEqual(list(exp_sif[i][j].index),
                                            list(calist[i][0][0][j].index))
                self.assertSequenceEqual(list(exp_sif[i][j].values),
                                            list(calist[i][0][0][j].values))

    def test_init_1(self):
        # an exception is raised about a score that's too short (fewer than 3 offsets)
        in_frame = pandas.DataFrame({'col': pandas.Series([i for i in xrange(2)])})
        in_frame.columns = pandas.MultiIndex.from_tuples((('FakeIndexer', 'col'),))
        in_frame.index = pandas.Index([i / 2.0 for i in xrange(2)])
        self.assertRaises(RuntimeError, dissonance.SuspensionIndexer, in_frame)


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
DISSONANCE_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestDissonanceIndexer)
SUSPENSION_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestSuspensionIndexer)
