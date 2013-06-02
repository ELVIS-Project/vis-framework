#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         TestSorting.py
# Purpose:      Unit tests for the NGram class.
#
# Copyright (C) 2012 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

# Imports from...
# python
import unittest
# music21
from music21 import interval
# vis
from controllers.experimenter import IntervalsStatistics, IntervalsLists


class TestIntervalsStatistics(unittest.TestCase):
    def test_experimenter_interval_sorter_1(self):
        # simple cases
        self.assertEqual(IntervalsStatistics.interval_sorter('M3', 'P5'), -1)
        self.assertEqual(IntervalsStatistics.interval_sorter('m7', 'd4'), 1)

    def test_experimenter_interval_sorter_2(self):
        # depends on quality
        self.assertEqual(IntervalsStatistics.interval_sorter('m3', 'M3'), -1)
        self.assertEqual(IntervalsStatistics.interval_sorter('M3', 'm3'), 1)
        self.assertEqual(IntervalsStatistics.interval_sorter('d3', 'm3'), -1)
        self.assertEqual(IntervalsStatistics.interval_sorter('M3', 'd3'), 1)
        self.assertEqual(IntervalsStatistics.interval_sorter('A3', 'M3'), 1)
        self.assertEqual(IntervalsStatistics.interval_sorter('d3', 'A3'), -1)
        self.assertEqual(IntervalsStatistics.interval_sorter('P4', 'A4'), -1)
        self.assertEqual(IntervalsStatistics.interval_sorter('A4', 'P4'), 1)

    def test_experimenter_interval_sorter_3(self):
        # all the qualities, testing for equality
        self.assertEqual(IntervalsStatistics.interval_sorter('M3', 'M3'), 0)
        self.assertEqual(IntervalsStatistics.interval_sorter('m3', 'm3'), 0)
        self.assertEqual(IntervalsStatistics.interval_sorter('d3', 'd3'), 0)
        self.assertEqual(IntervalsStatistics.interval_sorter('A3', 'A3'), 0)

    def test_experimenter_interval_sorter_4(self):
        # no qualities
        self.assertEqual(IntervalsStatistics.interval_sorter('3', '3'), 0)
        self.assertEqual(IntervalsStatistics.interval_sorter('3', '4'), -1)
        self.assertEqual(IntervalsStatistics.interval_sorter('3', '2'), 1)

    def test_experimenter_interval_sorter_5(self):
        # with directions
        self.assertEqual(IntervalsStatistics.interval_sorter('+3', '-3'), 0)
        self.assertEqual(IntervalsStatistics.interval_sorter('+3', '-4'), -1)
        self.assertEqual(IntervalsStatistics.interval_sorter('+3', '-2'), 1)

    def test_experimenter_interval_sorter_6(self):
        # with directions and quality
        self.assertEqual(IntervalsStatistics.interval_sorter('M+3', 'M-3'), 0)
        self.assertEqual(IntervalsStatistics.interval_sorter('m+3', 'P-4'), -1)
        self.assertEqual(IntervalsStatistics.interval_sorter('m+3', 'M-2'), 1)


class TestIntervalsLists(unittest.TestCase):
    def test_interval_formatter_1(self):
        interv = interval.Interval('m3')
        expect = u'm3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='compound',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_2(self):
        interv = interval.Interval('m3')
        expect = u'm3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='simple',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_3(self):
        interv = interval.Interval('m3')
        expect = u'm3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='compund',
                                                   direction='sometimes')
        self.assertEqual(expect, actual)

    def test_interval_formatter_4(self):
        interv = interval.Interval('m3')
        expect = u'+m3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='compound',
                                                   direction=True)
        self.assertEqual(expect, actual)

    def test_interval_formatter_5(self):
        interv = interval.Interval('m3')
        expect = u'3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=False,
                                                   size='compound',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_6(self):
        interv = interval.Interval('m3')
        expect = u'+3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=False,
                                                   size='compound',
                                                   direction=True)
        self.assertEqual(expect, actual)

    def test_interval_formatter_7(self):
        interv = interval.Interval('P8')
        expect = u'8'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=False,
                                                   size='compound',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_8(self):
        interv = interval.Interval('P8')
        expect = u'8'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=False,
                                                   size='simple',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_9(self):
        interv = interval.Interval('AA10')
        expect = u'AA10'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='compound',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_10(self):
        interv = interval.Interval('AA10')
        expect = u'10'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=False,
                                                   size='compound',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_11(self):
        interv = interval.Interval('AA10')
        expect = u'AA3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='simple',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_12(self):
        interv = interval.Interval('-m3')
        expect = u'-m3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='compound',
                                                   direction=True)
        self.assertEqual(expect, actual)

    def test_interval_formatter_13(self):
        interv = interval.Interval('-m3')
        expect = u'm3'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='compound',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_14(self):
        interv = interval.Interval('P1')
        expect = u'P1'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='compound',
                                                   direction=True)
        self.assertEqual(expect, actual)

    def test_interval_formatter_15(self):
        interv = interval.Interval('P1')
        expect = u'P1'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=True,
                                                   size='compound',
                                                   direction=False)
        self.assertEqual(expect, actual)

    def test_interval_formatter_16(self):
        interv = interval.Interval('A1')
        expect = u'+1'
        actual = IntervalsLists.interval_formatter(interv,
                                                   quality=False,
                                                   size='compound',
                                                   direction=True)
        self.assertEqual(expect, actual)

#---------------------------------------------------------------------------------------------------
# Definitions
#---------------------------------------------------------------------------------------------------
experimenter_interv_stats_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalsStatistics)
experimenter_interv_lists_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalsLists)
