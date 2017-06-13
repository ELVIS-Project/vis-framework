#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_contour.py
# Purpose:                Test the Contour Indexer
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
"""Tests for the contour indexer and its helper functions."""

# pylint: disable=too-many-public-methods

from unittest import TestCase, TestLoader
import pandas
from vis.analyzers.indexers import contour


def make_dataframe(labels, indices, name):
    ret = pandas.concat(indices, levels=labels, axis=1)
    iterables = (name, labels)
    multi_index = pandas.MultiIndex.from_product(iterables, names=('Indexer', 'Parts'))
    ret.columns = multi_index
    return ret

index = [1.0, 1.5, 2.0, 2.5]

horizontal = [['D5', 'E5', 'E5', 'D5'],
              ['G4', 'G4', 'G4', 'F#4'],
              ['B3', 'C4', 'B3', 'A3'],
              ['G3', 'C3', 'C3', 'Rest']]

horiz_name = 'interval.HorizontalIntervalIndexer'
result = pandas.DataFrame({str(x): pandas.Series(horizontal[x], index=index) for x in range(len(horizontal))})
NOTES = make_dataframe(result.columns.values, [result[name] for name in result.columns], horiz_name)

index = [1.0, 1.5]
cont_name = 'contour.ContourIndexer'

one = pandas.Series(data=['[0, 1, 1]', '[1, 1, 0]'], index=index)
two = pandas.Series(data=['[0, 0, 0]', '[1, 1, 0]'], index=index)
three = pandas.Series(data=['[0, 1, 0]', '[2, 1, 0]'], index=index)
four = pandas.Series(data=['[1, 0, 0]'], index=[1.0])

result = pandas.DataFrame({'0': one, '1': two, '2': three, '3': four})
EXPECTED = make_dataframe(result.columns.values, [result[name] for name in result.columns], cont_name)

test1 = '[4, 0, 1, 3, 2]'
test2 = '[4, 1, 2, 3, 0]'

matrix1 = [['0', '-', '-', '-', '-'],
          ['+', '0', '+', '+', '+'],
          ['+', '-', '0', '+', '+'],
          ['+', '-', '-', '0', '-'],
          ['+', '-', '-', '+', '0']]

matrix2 = [['0', '-', '-', '-', '-'],
           ['+', '0', '+', '+', '-'],
           ['+', '-', '0', '+', '-'],
           ['+', '-', '-', '0', '-'],
           ['+', '+', '+', '+', '0']]


class TestContourIndexer(TestCase):

    def test_init1(self):
        """tests that __init__() works with the necessary settings"""
        settings = {'length': 3}
        actual = contour.ContourIndexer(NOTES, settings)
        self.assertEqual(settings, actual.settings)

    def test_init2(self):
        """tests that __init__() fails when no settings are given"""
        self.assertRaises(RuntimeError, contour.ContourIndexer, NOTES, {})
        try:
            contour.ContourIndexer(NOTES)
        except RuntimeError as run_err:
            self.assertEqual(contour.ContourIndexer._MISSING_LENGTH, run_err.args[0])

    def test_init3(self):
        """tests that __init__() fails when the length is too low"""
        settings = {'length': 0.3}
        self.assertRaises(RuntimeError, contour.ContourIndexer, NOTES, settings)
        try:
            contour.ContourIndexer(NOTES, settings)
        except RuntimeError as run_err:
            self.assertEqual(contour.ContourIndexer._LOW_LENGTH, run_err.args[0])

    def test_contour(self):
        """tests that running the contour indexer returns the expected results"""
        settings = {'length': 3}
        actual = contour.ContourIndexer(NOTES, settings).run()
        self.assertTrue(actual.equals(EXPECTED))

    def test_matrix(self):
        matrix = contour.COM_matrix(test1)
        self.assertEqual(matrix, matrix1)

    def test_compare(self):
        comparison = contour.compare(matrix1, matrix2)
        self.assertEqual(0.8, comparison)


CONTOUR_INDEXER_SUITE = TestLoader().loadTestsFromTestCase(TestContourIndexer)
