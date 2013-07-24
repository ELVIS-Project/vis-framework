#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
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

import unittest
from analyzers import indexer
from test_corpus import int_indexer_short


class TestIndexer(unittest.TestCase):
    # _mpi_unique_offsets -----------------------------------------------------
    def test_mpi_unique_offsets_1(self):
        streams = int_indexer_short.test_1
        expected = [0.0]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_2(self):
        streams = int_indexer_short.test_2
        expected = [0.0, 0.25]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_3(self):
        streams = int_indexer_short.test_3
        expected = [0.0, 0.25]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_4(self):
        streams = int_indexer_short.test_4
        expected = [0.0, 0.25]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_5(self):
        streams = int_indexer_short.test_5
        expected = [0.0, 0.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_6(self):
        streams = int_indexer_short.test_6
        expected = [0.0, 0.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_7(self):
        streams = int_indexer_short.test_7
        expected = [0.0, 0.5, 1.0, 1.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_8(self):
        streams = int_indexer_short.test_8
        expected = [0.0, 0.25, 0.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_9(self):
        streams = int_indexer_short.test_9
        expected = [0.0, 0.25, 0.5, 1.0]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_10(self):
        streams = int_indexer_short.test_10
        expected = [0.0, 0.25]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_12(self):
        streams = int_indexer_short.test_12
        expected = [0.0, 0.25, 0.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_13(self):
        streams = int_indexer_short.test_13
        expected = [0.0, 0.125, 0.25, 0.375, 0.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_14(self):
        streams = int_indexer_short.test_14
        expected = [0.0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_15(self):
        streams = int_indexer_short.test_15
        expected = [0.0, 0.5, 0.75, 1.0, 1.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_16(self):
        streams = int_indexer_short.test_16
        expected = [0.0, 0.5, 0.75, 1.25, 1.5]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_17(self):
        streams = int_indexer_short.test_17
        expected = [0.0, 0.5, 0.75, 1.125, 1.25, 1.375, 2.0]
        actual = indexer._mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
indexer_suite = unittest.TestLoader().loadTestsFromTestCase(TestIndexer)
