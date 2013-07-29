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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import copy
import pandas
from music21 import base, stream, duration, note, converter
from vis.analyzers import indexer
from vis.test_corpus import int_indexer_short


class TestIndexerSinglePart(unittest.TestCase):
    # TODO: test that _do_multiprocessing() with an MPController only tries to "freeze" Streams
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
        result = indexer.mp_indexer(0, [input_series], self.verbatim)[1]
        self.assertTrue(isinstance(result, pandas.Series))

    def test_mp_indexer_2(self):
        # that we get a Series back when a Stream is given
        input_stream = stream.Stream(self.in_list)
        result = indexer.mp_indexer(0, [input_stream], self.verbatim, [base.ElementWrapper])[1]
        self.assertTrue(isinstance(result, pandas.Series))

    def test_mp_indexer_3(self):
        # that ommitting the "types" argument when giving a list of Streams raises RuntimeError
        input_stream = stream.Stream(self.in_list)
        self.assertRaises(RuntimeError, indexer.mp_indexer, 0, [input_stream], self.verbatim)

    def test_mp_indexer_4(self):
        # that the resulting Series is the same length (given a Series)
        input_series = pandas.Series(self.in_list)
        result = indexer.mp_indexer(0, [input_series], self.verbatim)[1]
        self.assertEqual(len(self.in_list), len(result))

    def test_mp_indexer_5(self):
        # that the resulting Series is the same length (given a Stream)
        input_stream = stream.Stream(self.in_list)
        result = indexer.mp_indexer(0, [input_stream], self.verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_list), len(result))

    def test_mp_indexer_6(self):
        # that the resulting Series has the same objects (given a Series)
        input_series = pandas.Series(self.in_list)
        result = indexer.mp_indexer(0, [input_series], self.verbatim)[1]
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_7(self):
        # that the resulting Series has the same objects (given a Stream)
        input_stream = stream.Stream(self.in_list)
        result = indexer.mp_indexer(0, [input_stream], self.verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_8(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> one event at each offset
        input_stream = stream.Stream(self.mixed_list)
        result = indexer.mp_indexer(0, [input_stream], self.verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_list), len(result))

    def test_mp_indexer_9(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test lengths
        # --> one event at each offset
        input_series = pandas.Series(self.mixed_list)
        result = indexer.mp_indexer(0, [input_series], self.verbatim_rests, [base.ElementWrapper])[1]
        self.assertEqual(len(self.mixed_list), len(result))

    def test_mp_indexer_10(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> one event at each offset
        input_stream = stream.Stream(self.mixed_list)
        result = indexer.mp_indexer(0, [input_stream], self.verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_10_pickle(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # ** inputted Streams are pickled
        # --> test values
        # --> one event at each offset
        input_stream = converter.freeze(stream.Stream(self.mixed_list), u'pickle')
        result = indexer.mp_indexer(0, [input_stream], self.verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_11(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test values
        # --> one event at each offset
        input_series = pandas.Series(self.mixed_list)
        result = indexer.mp_indexer(0, [input_series], self.verbatim_rests, [base.ElementWrapper])[1]
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
        result = indexer.mp_indexer(0, [input_stream], self.verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_list), len(result))

    def test_mp_indexer_12a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        input_stream = stream.Stream(self.shared_mixed_list)
        result = indexer.mp_indexer(0, [input_stream],
                                    self.verbatim_rests,
                                    [base.ElementWrapper, note.Rest])[1]
        self.assertEqual(len(self.shared_mixed_list), len(result))

    def test_mp_indexer_13(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test lengths
        # --> two events at each offset
        input_series = pandas.Series(self.shared_mixed_list)
        result = indexer.mp_indexer(0, [input_series], self.verbatim_rests, [base.ElementWrapper])[1]
        self.assertEqual(len(self.shared_mixed_list), len(result))

    def test_mp_indexer_14(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        input_stream = stream.Stream(self.shared_mixed_list)
        result = indexer.mp_indexer(0, [input_stream], self.verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.in_list)):
            self.assertEqual(self.in_list[i].obj, result[i].obj)

    def test_mp_indexer_14a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        input_stream = stream.Stream(self.shared_mixed_list)
        result = indexer.mp_indexer(0, [input_stream],
                                    self.verbatim_rests,
                                    [base.ElementWrapper, note.Rest])[1]
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
        result = indexer.mp_indexer(0, [input_series], self.verbatim_rests, [base.ElementWrapper])[1]
        for i in xrange(len(self.in_list)):
            if isinstance(self.mixed_list[i], note.Rest):
                self.assertEqual(result[i].obj, u'Rest')
            else:
                self.assertEqual(self.mixed_list[i].obj, result[i].obj)

class TestIndexerThreeParts(unittest.TestCase):
    def setUp(self):
        # prepare a valid list of ElementWrappers (with proper offset and duration)
        self.in_list = [base.ElementWrapper(x) for x in xrange(100)]
        for i, elem in enumerate(self.in_list):
            elem.offset = i * 0.25
            elem.duration = duration.Duration(0.25)
        # lambda for mp_indexer() that returns the object unmodified
        self.verbatim = lambda x: str((x[0].obj, x[1].obj, x[2].obj))
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
        ## same list as previous, but with a Rest and ElementerWrapper sharing each offset
        self.shared_mixed_list = []
        for i in xrange(100):
            app_me = note.Rest(quarterLength=0.25)
            app_me.offset = i * 0.25
            self.shared_mixed_list.append(app_me)
            app_me = base.ElementWrapper(i)
            app_me.offset = i * 0.25
            app_me.duration = duration.Duration(0.25)
            self.shared_mixed_list.append(app_me)
        ## lambda that deals with Rest objects
        def verb_r(x):
            if isinstance(x[0], note.Rest):
                return str((u'Rest', u'Rest', u'Rest'))
            else:
                return str((x[0].obj, x[1].obj, x[2].obj))
        self.verbatim_rests = lambda x: verb_r(x)
        ## lambda that deals with an unknown number of objects
        self.verbatim_variable = lambda x: str(tuple([zed.obj for zed in x]))

    def test_mpi_triple_1(self):
        # that we get a Series back when a Series is given
        input_streams = [pandas.Series(self.in_list),
                         pandas.Series(copy.deepcopy(self.in_list)),
                         pandas.Series(copy.deepcopy(self.in_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim, [base.ElementWrapper])[1]
        self.assertTrue(isinstance(result, pandas.Series))

    def test_mpi_triple_2(self):
        # that we get a Series back when a Stream is given
        input_streams = [stream.Stream(self.in_list),
                         stream.Stream(copy.deepcopy(self.in_list)),
                         stream.Stream(copy.deepcopy(self.in_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim, [base.ElementWrapper])[1]
        self.assertTrue(isinstance(result, pandas.Series))

    def test_mpi_triple_5(self):
        # that the resulting Series is the same length (given a Stream)
        input_streams = [stream.Stream(self.in_list),
                         stream.Stream(copy.deepcopy(self.in_list)),
                         stream.Stream(copy.deepcopy(self.in_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_list), len(result))

    def test_mpi_triple_6(self):
        # that the resulting Series is the same length (given a Series)
        input_streams = [pandas.Series(self.in_list),
                         pandas.Series(copy.deepcopy(self.in_list)),
                         pandas.Series(copy.deepcopy(self.in_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_list), len(result))

    def test_mpi_triple_7(self):
        # that the resulting Series has the same objects (given a Stream)
        input_streams = [stream.Stream(self.in_list),
                         stream.Stream(copy.deepcopy(self.in_list)),
                         stream.Stream(copy.deepcopy(self.in_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.in_list)):
            res = str((self.in_list[i].obj, self.in_list[i].obj, self.in_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_8(self):
        # that the resulting Series has the same objects (given a Series)
        input_streams = [pandas.Series(self.in_list),
                         pandas.Series(copy.deepcopy(self.in_list)),
                         pandas.Series(copy.deepcopy(self.in_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim)[1]
        for i in xrange(len(self.in_list)):
            res = str((self.in_list[i].obj, self.in_list[i].obj, self.in_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_8(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> one event at each offset
        input_streams = [stream.Stream(self.mixed_list),
                         stream.Stream(copy.deepcopy(self.mixed_list)),
                         stream.Stream(copy.deepcopy(self.mixed_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_list), len(result))

    def test_mpi_triple_9(self):
        # that a list with two types is not filtered when it's given as a Series
        # --> test lengths
        # --> one event at each offset
        input_streams = [pandas.Series(self.mixed_list),
                         pandas.Series(copy.deepcopy(self.mixed_list)),
                         pandas.Series(copy.deepcopy(self.mixed_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim_rests)[1]
        self.assertEqual(len(self.mixed_list), len(result))

    def test_mpi_triple_10(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> one event at each offset
        input_streams = [stream.Stream(self.mixed_list),
                         stream.Stream(copy.deepcopy(self.mixed_list)),
                         stream.Stream(copy.deepcopy(self.mixed_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.in_list)):
            res = str((self.in_list[i].obj, self.in_list[i].obj, self.in_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_11(self):
        # that a list with two types is not filtered when it's given as a Series
        # --> test values
        # --> one event at each offset
        input_streams = [pandas.Series(self.mixed_list),
                         pandas.Series(copy.deepcopy(self.mixed_list)),
                         pandas.Series(copy.deepcopy(self.mixed_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim_rests)[1]
        for i in xrange(len(self.mixed_list)):
            res = None
            if isinstance(self.mixed_list[i], note.Rest):
                res = str((u'Rest', u'Rest', u'Rest'))
            else:
                res = str((self.mixed_list[i].obj, self.mixed_list[i].obj, self.mixed_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_12(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        input_streams = [stream.Stream(self.shared_mixed_list),
                         stream.Stream(copy.deepcopy(self.shared_mixed_list)),
                         stream.Stream(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.mp_indexer(0, input_streams, self.verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_list), len(result))

    def test_mpi_triple_12a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        input_streams = [stream.Stream(self.shared_mixed_list),
                         stream.Stream(copy.deepcopy(self.shared_mixed_list)),
                         stream.Stream(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.mp_indexer(0, input_streams,
                                    self.verbatim_rests,
                                    [base.ElementWrapper, note.Rest])[1]
        self.assertEqual(len(self.shared_mixed_list), len(result))

    def test_mpi_triple_13(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test lengths
        # --> two events at each offset
        input_series = [pandas.Series(self.shared_mixed_list),
                        pandas.Series(copy.deepcopy(self.shared_mixed_list)),
                        pandas.Series(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.mp_indexer(0, input_series, self.verbatim_rests, [base.ElementWrapper])[1]
        self.assertEqual(len(self.shared_mixed_list), len(result))

    def test_mpi_triple_14(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        input_stream = [stream.Stream(self.shared_mixed_list),
                        stream.Stream(copy.deepcopy(self.shared_mixed_list)),
                        stream.Stream(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.mp_indexer(0, input_stream, self.verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.in_list)):
            res = str((self.in_list[i].obj, self.in_list[i].obj, self.in_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_14a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        input_stream = [stream.Stream(self.shared_mixed_list),
                        stream.Stream(copy.deepcopy(self.shared_mixed_list)),
                        stream.Stream(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.mp_indexer(0, input_stream,
                                    self.verbatim_rests,
                                    [base.ElementWrapper, note.Rest])[1]
        for i in xrange(len(self.mixed_list)):
            res = None
            if isinstance(self.mixed_list[i], note.Rest):
                res = str((u'Rest', u'Rest', u'Rest'))
            else:
                res = str((self.mixed_list[i].obj, self.mixed_list[i].obj, self.mixed_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_15(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test values
        # --> two events at each offset
        input_series = [pandas.Series(self.shared_mixed_list),
                        pandas.Series(copy.deepcopy(self.shared_mixed_list)),
                        pandas.Series(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.mp_indexer(0, input_series, self.verbatim_rests, [base.ElementWrapper])[1]
        for i in xrange(len(self.mixed_list)):
            res = None
            if isinstance(self.mixed_list[i], note.Rest):
                res = str((u'Rest', u'Rest', u'Rest'))
            else:
                res = str((self.mixed_list[i].obj, self.mixed_list[i].obj, self.mixed_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_16(self):
        # Test this:
        # offset:  0.0  |  0.5  |  1.0  |  1.5  |  2.0
        # part 1:  [1]  |  [1]  |  [1]  |  [1]  |  [1]
        # part 2:  [1]  |  [1]  |  [1]  |  [1]  |  [1]
        part_1 = [base.ElementWrapper(x) for x in xrange(5)]
        for i, elem in enumerate(part_1):
            elem.offset = i * 0.5
            elem.duration = duration.Duration(0.5)
        part_2 = [base.ElementWrapper(x) for x in xrange(5)]
        for i, elem in enumerate(part_2):
            elem.offset = i * 0.5
            elem.duration = duration.Duration(0.5)
        part_1 = pandas.Series(part_1)
        part_2 = pandas.Series(part_2)
        # define expected
        expected = [(0.0, u'(0, 0)'),
                    (0.5, u'(1, 1)'),
                    (1.0, u'(2, 2)'),
                    (1.5, u'(3, 3)'),
                    (2.0, u'(4, 4)')]
        # do the test
        result = indexer.mp_indexer(0, [part_1, part_2], self.verbatim_variable)[1]
        for i in xrange(len(expected)):
            self.assertEqual(expected[i][0], result[i].offset)
            self.assertEqual(expected[i][1], result[i].obj)

    def test_mpi_triple_17(self):
        # Test this:
        # offset:  0.0  |  0.5     |  1.0     |  1.5     |  2.0
        # part 1:  [1]  |  [1][2]  |  [1]     |  [1][2]  |  [1][2]
        # part 2:  [1]  |  [1][2]  |  [1][2]  |  [1]     |  [1][2]
        part_1 = [base.ElementWrapper(x) for x in xrange(5)]
        for i, elem in enumerate(part_1):
            elem.offset = i * 0.5
            elem.duration = duration.Duration(0.5)
        part_2 = [base.ElementWrapper(x) for x in xrange(5)]
        for i, elem in enumerate(part_2):
            elem.offset = i * 0.5
            elem.duration = duration.Duration(0.5)
        part_1 = stream.Stream(part_1)
        part_2 = stream.Stream(part_2)
        # add_these = [(part, offset, number), (part, offset, number), ...]
        # ... for offsets that have more than one event
        add_these = [(part_1, 0.5, 100), (part_2, 0.5, 100),
                     (part_2, 1.0, 200),
                     (part_1, 1.5, 300),
                     (part_1, 2.0, 400), (part_2, 2.0, 400)]
        for part, offset, number in add_these:
            zed = base.ElementWrapper(number)
            zed.duration = duration.Duration(0.5)
            part.insert(offset, zed)
        # define expected
        expected = [(0.0, u'(0, 0)'),
                    (0.5, u'(1, 1)'),
                    (0.5, u'(100, 100)'),
                    (1.0, u'(2, 2)'),
                    (1.0, u'(200,)'),
                    (1.5, u'(3, 3)'),
                    (1.5, u'(300,)'),
                    (2.0, u'(4, 4)'),
                    (2.0, u'(400, 400)')]
        # do the test
        result = indexer.mp_indexer(0, [part_1, part_2], self.verbatim_variable, [base.ElementWrapper])[1]
        for i in xrange(len(expected)):
            self.assertEqual(expected[i][0], result[i].offset)
            self.assertEqual(expected[i][1], result[i].obj)

    def test_mpi_triple_18(self):
        ## offset:  0.0  |  0.5     |  1.0        |  1.5     |  2.0
        ## part 1:  [1]  |  [1][2]  |  [1][2][3]  |  [1][2]  |  [1][2][3]
        ## part 2:  [1]  |  [1][2]  |  [1][2]     |  [1]     |  [1]
        ## part 3:  [1]  |  [1][2]  |  [1][2]     |  [1][2]  |  [1][2]
        part_1 = [base.ElementWrapper(x) for x in xrange(5)]
        for i, elem in enumerate(part_1):
            elem.offset = i * 0.5
            elem.duration = duration.Duration(0.5)
        part_2 = [base.ElementWrapper(x) for x in xrange(5)]
        for i, elem in enumerate(part_2):
            elem.offset = i * 0.5
            elem.duration = duration.Duration(0.5)
        part_3 = [base.ElementWrapper(x) for x in xrange(5)]
        for i, elem in enumerate(part_3):
            elem.offset = i * 0.5
            elem.duration = duration.Duration(0.5)
        part_1 = stream.Stream(part_1)
        part_2 = stream.Stream(part_2)
        part_3 = stream.Stream(part_3)
        # add_these = [(part, offset, number), (part, offset, number), ...]
        # ... for offsets that have more than one event
        add_these = [(part_1, 0.5, 101), (part_2, 0.5, 102), (part_3, 0.5, 103),
                     (part_1, 1.0, 201), (part_2, 1.0, 202), (part_3, 1.0, 203), (part_1, 1.0, 251),
                     (part_1, 1.5, 301), (part_2, 1.5, 302),
                     (part_1, 2.0, 401), (part_2, 2.0, 402), (part_1, 2.0, 451)]
        for part, offset, number in add_these:
            zed = base.ElementWrapper(number)
            zed.duration = duration.Duration(0.5)
            part.insert(offset, zed)
        # define expected
        expected = [(0.0, u'(0, 0, 0)'),
                    (0.5, u'(1, 1, 1)'),
                    (0.5, u'(101, 102, 103)'),
                    (1.0, u'(2, 2, 2)'),
                    (1.0, u'(201, 202, 203)'),
                    (1.0, u'(251,)'),
                    (1.5, u'(3, 3, 3)'),
                    (1.5, u'(301, 302)'),
                    (2.0, u'(4, 4, 4)'),
                    (2.0, u'(401, 402)'),
                    (2.0, u'(451,)')]
        # do the test
        result = indexer.mp_indexer(0, [part_1, part_2, part_3],
                                    self.verbatim_variable,
                                    [base.ElementWrapper])[1]
        for i in xrange(len(expected)):
            self.assertEqual(expected[i][0], result[i].offset)
            self.assertEqual(expected[i][1], result[i].obj)

class TestMpiUniqueOffsets(unittest.TestCase):
    # the whole point is to test a "private" function
    # pylint: disable=W0212
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

class TestMpiVertAligner(unittest.TestCase):
    # the whole point is to test a "private" function
    # pylint: disable=W0212
    def test_mpi_vert_aligner_1(self):
        in_list = [[1]]
        expected = [[1]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_2(self):
        in_list = [[1, 2]]
        expected = [[1], [2]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_3(self):
        in_list = [[1], [2]]
        expected = [[1, 2]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_4(self):
        in_list = [[1, 2], [1, 2]]
        expected = [[1, 1], [2, 2]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_5(self):
        in_list = [[1, 2], [5]]
        expected = [[1, 5], [2]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_6(self):
        in_list = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
        expected = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_7(self):
        in_list = [[1, 2, 3], [1], [1, 2, 3]]
        expected = [[1, 1, 1], [2, 2], [3, 3]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_8(self):
        in_list = [[1, 2, 3], [1], [1, 2]]
        expected = [[1, 1, 1], [2, 2], [3]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_9(self):
        in_list = [[1], [1], [1]]
        expected = [[1, 1, 1]]
        actual = indexer._mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
indexer_1_part_suite = unittest.TestLoader().loadTestsFromTestCase(TestIndexerSinglePart)
indexer_3_parts_suite = unittest.TestLoader().loadTestsFromTestCase(TestIndexerThreeParts)
unique_offsets_suite = unittest.TestLoader().loadTestsFromTestCase(TestMpiUniqueOffsets)
vert_aligner_suite = unittest.TestLoader().loadTestsFromTestCase(TestMpiVertAligner)
