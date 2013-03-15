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
# vis
from controllers import experimenter



class TestIntervalsStatistics(unittest.TestCase):
   def test_experimenter_interval_sorter_1(self):
      # simple cases
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('M3', 'P5'), -1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('m7', 'd4'), 1)

   def test_experimenter_interval_sorter_2(self):
      # depends on quality
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('m3', 'M3'), -1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('M3', 'm3'), 1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('d3', 'm3'), -1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('M3', 'd3'), 1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('A3', 'M3'), 1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('d3', 'A3'), -1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('P4', 'A4'), -1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('A4', 'P4'), 1)

   def test_experimenter_interval_sorter_3(self):
      # all the qualities, testing for equality
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('M3', 'M3'), 0)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('m3', 'm3'), 0)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('d3', 'd3'), 0)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('A3', 'A3'), 0)

   def test_experimenter_interval_sorter_4(self):
      # no qualities
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('3', '3'), 0)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('3', '4'), -1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('3', '2'), 1)

   def test_experimenter_interval_sorter_5(self):
      # with directions
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('+3', '-3'), 0)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('+3', '-4'), -1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('+3', '-2'), 1)

   def test_experimenter_interval_sorter_6(self):
      # with directions and quality
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('M+3', 'M-3'), 0)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('m+3', 'P-4'), -1)
      self.assertEqual(experimenter.IntervalsStatistics.interval_sorter('m+3', 'M-2'), 1)
# End TestIntervalsStatistics ----------------------------------------------------------------------



#---------------------------------------------------------------------------------------------------
# Definitions
#---------------------------------------------------------------------------------------------------
experimenter_interv_stats_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalsStatistics)
