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
from models import analyzing, experimenting


class TestIntervalsStatistics(unittest.TestCase):
    def setUp(self):
        self.record_1 = [(0.0, ('B4', 'D6')),
                         (6.0, ('A4', 'C5')),
                         (8.0, ('F#4', 'A4')),
                         (12.0, ('G4', 'B4')),
                         (14.0, ('G4', 'G5')),
                         (16.0, ('E5', 'G5')),
                         (22.0, ('D5', 'F5')),
                         (24.0, ('B4', 'D5')),
                         (28.0, ('C5', 'C5')),
                         (32.0, ('G4', 'C5')),
                         (34.0, ('A4', 'C5')),
                         (36.0, ('C6', 'F6')),
                         (38.0, ('C6', 'E6'))]

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

    def test_intervals_stats_1(self):
        # test mostly simple, with "simple" setting, and quality
        # not testing topX, sort order, sort by, and threshold
        a_rec = analyzing.AnalysisRecord()
        setts = experimenting.ExperimentSettings()
        setts.set('quality', True)
        setts.set('simple or compound', 'simple')
        a_rec._record = self.record_1
        expect = {'+m3': 7, '+M3': 2, '+P8': 1, 'P1': 1, '+P4': 2}
        actual = IntervalsStatistics(None, [a_rec], setts)
        actual.perform()
        self.assertEqual(expect, actual._intervals)

    def test_intervals_stats_2(self):
        # test mostly simple, with "simple" setting, and no quality
        # not testing topX, sort order, sort by, and threshold
        a_rec = analyzing.AnalysisRecord()
        setts = experimenting.ExperimentSettings()
        setts.set('quality', False)
        setts.set('simple or compound', 'simple')
        a_rec._record = self.record_1
        expect = {'+3': 9, '+8': 1, '1': 1, '+4': 2}
        actual = IntervalsStatistics(None, [a_rec], setts)
        actual.perform()
        self.assertEqual(expect, actual._intervals)


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

    def test_intervals_lists_1(self):
        # test mostly simple, with "compound" setting, and no quality
        a_rec = analyzing.AnalysisRecord()
        setts = experimenting.ExperimentSettings()
        setts.set('quality', False)
        setts.set('simple or compound', 'compound')
        a_rec._record = [(0.0, ('B4', 'D5')),
                         (6.0, ('A4', 'C5')),
                         (8.0, ('F#4', 'A4')),
                         (12.0, ('G4', 'B4')),
                         (14.0, ('G4', 'G5')),
                         (16.0, ('E5', 'G5')),
                         (22.0, ('D5', 'F5')),
                         (24.0, ('B4', 'D5')),
                         (28.0, ('C5', 'C5')),
                         (32.0, ('G4', 'C5')),
                         (34.0, ('A4', 'C5')),
                         (36.0, ('C5', 'F5')),
                         (38.0, ('C5', 'E5'))]
        expect = [('vertical', 'horizontal', 'offset'),
                  ('3', '-2', 0.0),
                  ('3', '-3', 6.0),
                  ('3', '+2', 8.0),
                  ('3', '1', 12.0),
                  ('8', '+6', 14.0),
                  ('3', '-2', 16.0),
                  ('3', '-3', 22.0),
                  ('3', '+2', 24.0),
                  ('1', '-4', 28.0),
                  ('4', '+2', 32.0),
                  ('3', '+3', 34.0),
                  ('4', '1', 36.0),
                  ('3', None, 38.0)]
        actual = IntervalsLists(None, [a_rec], setts).perform()
        self.assertEqual(expect, actual)

    def test_intervals_lists_2(self):
        # test mostly simple, with "compound" setting, and quality
        a_rec = analyzing.AnalysisRecord()
        setts = experimenting.ExperimentSettings()
        setts.set('quality', True)
        setts.set('simple or compound', 'compound')
        a_rec._record = [(0.0, ('B4', 'D5')),
                         (6.0, ('A4', 'C5')),
                         (8.0, ('F#4', 'A4')),
                         (12.0, ('G4', 'B4')),
                         (14.0, ('G4', 'G5')),
                         (16.0, ('E5', 'G5')),
                         (22.0, ('D5', 'F5')),
                         (24.0, ('B4', 'D5')),
                         (28.0, ('C5', 'C5')),
                         (32.0, ('G4', 'C5')),
                         (34.0, ('A4', 'C5')),
                         (36.0, ('C5', 'F5')),
                         (38.0, ('C5', 'E5'))]
        expect = [('vertical', 'horizontal', 'offset'),
                  ('m3', '-M2', 0.0),
                  ('m3', '-m3', 6.0),
                  ('m3', '+m2', 8.0),
                  ('M3', 'P1', 12.0),
                  ('P8', '+M6', 14.0),
                  ('m3', '-M2', 16.0),
                  ('m3', '-m3', 22.0),
                  ('m3', '+m2', 24.0),
                  ('P1', '-P4', 28.0),
                  ('P4', '+M2', 32.0),
                  ('m3', '+m3', 34.0),
                  ('P4', 'P1', 36.0),
                  ('M3', None, 38.0)]
        actual = IntervalsLists(None, [a_rec], setts).perform()
        self.assertEqual(expect, actual)

    def test_intervals_lists_3(self):
        # test strategic compound, with "compound" setting, and quality
        a_rec = analyzing.AnalysisRecord()
        setts = experimenting.ExperimentSettings()
        setts.set('quality', True)
        setts.set('simple or compound', 'compound')
        a_rec._record = [(0.0, ('B4', 'D6')),
                         (6.0, ('A4', 'C5')),
                         (8.0, ('F#4', 'A4')),
                         (12.0, ('G4', 'B4')),
                         (14.0, ('G4', 'G5')),
                         (16.0, ('E5', 'G5')),
                         (22.0, ('D5', 'F5')),
                         (24.0, ('B4', 'D5')),
                         (28.0, ('C5', 'C5')),
                         (32.0, ('G4', 'C5')),
                         (34.0, ('A4', 'C5')),
                         (36.0, ('C6', 'F6')),
                         (38.0, ('C6', 'E6'))]
        expect = [('vertical', 'horizontal', 'offset'),
                  ('m10', '-M2', 0.0),
                  ('m3', '-m3', 6.0),
                  ('m3', '+m2', 8.0),
                  ('M3', 'P1', 12.0),
                  ('P8', '+M6', 14.0),
                  ('m3', '-M2', 16.0),
                  ('m3', '-m3', 22.0),
                  ('m3', '+m2', 24.0),
                  ('P1', '-P4', 28.0),
                  ('P4', '+M2', 32.0),
                  ('m3', '+m10', 34.0),
                  ('P4', 'P1', 36.0),
                  ('M3', None, 38.0)]
        actual = IntervalsLists(None, [a_rec], setts).perform()
        self.assertEqual(expect, actual)

    def test_intervals_lists_4(self):
        # test strategic compound, with "simple" setting, and quality
        a_rec = analyzing.AnalysisRecord()
        setts = experimenting.ExperimentSettings()
        setts.set('quality', True)
        setts.set('simple or compound', 'simple')
        a_rec._record = [(0.0, ('B4', 'D6')),
                         (6.0, ('A4', 'C5')),
                         (8.0, ('F#4', 'A4')),
                         (12.0, ('G4', 'B4')),
                         (14.0, ('G4', 'G5')),
                         (16.0, ('E5', 'G5')),
                         (22.0, ('D5', 'F5')),
                         (24.0, ('B4', 'D5')),
                         (28.0, ('C5', 'C5')),
                         (32.0, ('G4', 'C5')),
                         (34.0, ('A4', 'C5')),
                         (36.0, ('C6', 'F6')),
                         (38.0, ('C6', 'E6'))]
        expect = [('vertical', 'horizontal', 'offset'),
                  ('m3', '-M2', 0.0),
                  ('m3', '-m3', 6.0),
                  ('m3', '+m2', 8.0),
                  ('M3', 'P1', 12.0),
                  ('P8', '+M6', 14.0),
                  ('m3', '-M2', 16.0),
                  ('m3', '-m3', 22.0),
                  ('m3', '+m2', 24.0),
                  ('P1', '-P4', 28.0),
                  ('P4', '+M2', 32.0),
                  ('m3', '+m3', 34.0),
                  ('P4', 'P1', 36.0),
                  ('M3', None, 38.0)]
        actual = IntervalsLists(None, [a_rec], setts).perform()
        self.assertEqual(expect, actual)


#---------------------------------------------------------------------------------------------------
# Definitions
#---------------------------------------------------------------------------------------------------
experimenter_interv_stats_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalsStatistics)
experimenter_interv_lists_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalsLists)
