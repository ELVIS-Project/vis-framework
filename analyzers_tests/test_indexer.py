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
import pandas
from music21 import base, stream, duration, note
from analyzers import indexer
from test_corpus import int_indexer_short


class TestIndexerSinglePart(unittest.TestCase):
    def setUp(self):
        # prepare a valid list of ElementWrappers (with proper offset and duration)
        self.in_list = [base.ElementWrapper(x) for x in xrange(100)]
        for i, elem in enumerate(self.in_list):
            elem.offset = i * 0.25
            elem.duration = duration.Duration(0.25)
        # lambda for mp_indexer() that returns the object unmodified
        self.verbatim = lambda x: x[0].obj
        # prepare a valid list of Rests and ElementWrappers, happening simultaneously, to see that
        # we can properly filter by type
        self.mixed_list = []
        for i in xrange(100):
            app_me = note.Rest(quarterLength=0.25)
            app_me.offset = i * 0.5
            self.mixed_list.append(app_me)
            app_me = base.ElementWrapper(i)
            app_me.offset = i * 0.5 + 0.25
            app_me.duration = duration.Duration(0.25)
            self.mixed_list.append(app_me)
        # same list as previous, but with a Rest and ElementerWrapper sharing each offset
        self.shared_mixed_list = []
        for i in xrange(100):
            app_me = note.Rest(quarterLength=0.25)
            app_me.offset = i * 0.25
            self.shared_mixed_list.append(app_me)
            app_me = base.ElementWrapper(i)
            app_me.offset = i * 0.25
            app_me.duration = duration.Duration(0.25)
            self.shared_mixed_list.append(app_me)
        # lambda that deals with Rest objects
        self.verbatim_rests = lambda x: u'Rest' if isinstance(x[0], note.Rest) else x[0].obj

    def test_mp_indexer_1(self):
        # that we get a Series back when a Series is given
        input_series = pandas.Series(self.in_list)
        result = indexer.mp_indexer([input_series], self.verbatim)
        self.assertTrue(isinstance(result, pandas.Series))

    def test_mp_indexer_2(self):
        # that we get a Series back when a Stream is given
        input_stream = stream.Stream(self.in_list)
        result = indexer.mp_indexer([input_stream], self.verbatim, [base.ElementWrapper])
        self.assertTrue(isinstance(result, pandas.Series))

    def test_mp_indexer_3(self):
        # that ommitting the "types" argument when giving a list of Streams raises RuntimeError
        input_stream = stream.Stream(self.in_list)
        self.assertRaises(RuntimeError, indexer.mp_indexer, [input_stream], self.verbatim)

    def test_mp_indexer_4(self):
        # that the resulting Series is the same length (given a Series)
        input_series = pandas.Series(self.in_list)
        result = indexer.mp_indexer([input_series], self.verbatim)
        self.assertEqual(len(self.in_list), len(result))

    def test_mp_indexer_5(self):
        # that the resulting Series is the same length (given a Stream)
        input_stream = stream.Stream(self.in_list)
        result = indexer.mp_indexer([input_stream], self.verbatim, [base.ElementWrapper])
        self.assertEqual(len(self.in_list), len(result))

    def test_mp_indexer_6(self):
        # that the resulting Series has the same objects (given a Series)
        input_series = pandas.Series(self.in_list)
        result = indexer.mp_indexer([input_series], self.verbatim)
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_7(self):
        # that the resulting Series has the same objects (given a Stream)
        input_stream = stream.Stream(self.in_list)
        result = indexer.mp_indexer([input_stream], self.verbatim, [base.ElementWrapper])
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_8(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> one event at each offset
        input_stream = stream.Stream(self.mixed_list)
        result = indexer.mp_indexer([input_stream], self.verbatim, [base.ElementWrapper])
        self.assertEqual(len(self.in_list), len(result))

    def test_mp_indexer_9(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test lengths
        # --> one event at each offset
        input_series = pandas.Series(self.mixed_list)
        result = indexer.mp_indexer([input_series], self.verbatim_rests, [base.ElementWrapper])
        self.assertEqual(len(self.mixed_list), len(result))

    def test_mp_indexer_10(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> one event at each offset
        input_stream = stream.Stream(self.mixed_list)
        result = indexer.mp_indexer([input_stream], self.verbatim, [base.ElementWrapper])
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_11(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test values
        # --> one event at each offset
        input_series = pandas.Series(self.mixed_list)
        result = indexer.mp_indexer([input_series], self.verbatim_rests, [base.ElementWrapper])
        for i in xrange(len(self.in_list)):
            if isinstance(self.mixed_list[i], note.Rest):
                self.assertEqual(result[i].obj, u'Rest')
            else:
                self.assertEqual(self.mixed_list[i].obj, result[i].obj)

    def test_mp_indexer_12(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        input_stream = stream.Stream(self.shared_mixed_list)
        result = indexer.mp_indexer([input_stream], self.verbatim, [base.ElementWrapper])
        self.assertEqual(len(self.in_list), len(result))

    def test_mp_indexer_12a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        input_stream = stream.Stream(self.shared_mixed_list)
        result = indexer.mp_indexer([input_stream],
                                    self.verbatim_rests,
                                    [base.ElementWrapper, note.Rest])
        self.assertEqual(len(self.shared_mixed_list), len(result))

    def test_mp_indexer_13(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test lengths
        # --> two events at each offset
        input_series = pandas.Series(self.shared_mixed_list)
        result = indexer.mp_indexer([input_series], self.verbatim_rests, [base.ElementWrapper])
        self.assertEqual(len(self.shared_mixed_list), len(result))

    def test_mp_indexer_14(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        input_stream = stream.Stream(self.shared_mixed_list)
        result = indexer.mp_indexer([input_stream], self.verbatim, [base.ElementWrapper])
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_14a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        input_stream = stream.Stream(self.shared_mixed_list)
        result = indexer.mp_indexer([input_stream],
                                    self.verbatim_rests,
                                    [base.ElementWrapper, note.Rest])
        for i in xrange(len(self.shared_mixed_list)):
            if isinstance(self.shared_mixed_list[i], note.Rest):
                self.assertEqual(result[i].obj, u'Rest')
            else:
                self.assertEqual(self.shared_mixed_list[i].obj, result[i].obj)

    def test_mp_indexer_15(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test values
        # --> two events at each offset
        input_series = pandas.Series(self.shared_mixed_list)
        result = indexer.mp_indexer([input_series], self.verbatim_rests, [base.ElementWrapper])
        for i in xrange(len(self.in_list)):
            if isinstance(self.mixed_list[i], note.Rest):
                self.assertEqual(result[i].obj, u'Rest')
            else:
                self.assertEqual(self.mixed_list[i].obj, result[i].obj)

class TestMpiUniqueOffsets(unittest.TestCase):
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
indexer_1_part_suite = unittest.TestLoader().loadTestsFromTestCase(TestIndexerSinglePart)
unique_offsets_suite = unittest.TestLoader().loadTestsFromTestCase(TestMpiUniqueOffsets)
