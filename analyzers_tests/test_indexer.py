#!/usr/bin/env python
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
import mock
import copy
import pandas
from music21 import base, stream, duration, note, converter
from vis.analyzers import indexer
from vis.test_corpus import int_indexer_short


def fake_indexer_func(ecks):
    return unicode(ecks)


class TestIndexerHardcore(unittest.TestCase):
    # accessing TestIndexer._indexer_func is part of the test
    # pylint: disable=W0212
    def test_indexer_hardcore_0(self):
        # That calling Indexer.__init__() with the wrong type results in the proper error message.
        class TestIndexer(indexer.Indexer):
            # Class with bare minimum changes, since we can't instantiate Indexer directly
            required_score_type = stream.Stream

        test_parts = [pandas.Series()]
        settings = {}
        self.assertRaises(RuntimeError, TestIndexer, test_parts, settings)
        error_msg = unicode("<class 'vis.analyzers_tests.test_indexer.TestIndexer'> requires "
                            "<class 'music21.stream.Stream'> objects, not <class 'pandas.core"
                            ".series.Series'>")
        try:
            TestIndexer(test_parts, settings)
        except RuntimeError as err:
            self.assertEqual(err.args[0], error_msg)

    def test_indexer_hardcore_1(self):
        # That _do_multiprocessing() passes the correct arguments to stream_indexer()
        class TestIndexer(indexer.Indexer):
            # Class with bare minimum changes, since we can't instantiate Indexer directly
            required_score_type = stream.Stream
            def run(self):
                self._do_multiprocessing([[0]])
        # the actual testing
        test_parts = [stream.Stream()]
        settings = {}
        # prepare mocks
        with mock.patch(u'vis.analyzers.indexer.stream_indexer') as mpi_mock:
            # run test
            t_ind = TestIndexer(test_parts, settings)
            t_ind._indexer_func = fake_indexer_func
            t_ind.run()
            # check results
            mpi_mock.assert_called_once_with(0, test_parts, fake_indexer_func, None)

    # TODO: add at least these tests:
    # - indexer.py:L132 ... want to test that objects of all types are returned when "types" is None



def verbatim(iterable):
    """
    Get the object contained in the first item of an iterable.
    :param iterable:
    :return iterable:
    """
    return iterable[0].obj


def verbatim_ser(iterable):
    """
    Get the first item in an iterable
    :param iterable:
    :return: the first item
    """
    return iterable[0]


def verbatim_rests(arg):
    return u'Rest' if isinstance(arg[0], note.Rest) else unicode(arg[0].obj)


def verbatim_variable(iterable):
    return str(tuple(item.obj for item in iterable))


# TODO: pylint says we have 8 instance attributes on this bad boy, which is just too many.
class IndexerTestBase(unittest.TestCase):
    def setUp(self):
        # prepare a valid list of ElementWrappers (with proper offset and duration)
        self.in_series = pandas.Series(range(100), index=[0.25 * x for x in xrange(100)])
        self.in_stream = stream.Stream(base.ElementWrapper(i) for i in xrange(100))
        for i, elem in enumerate(self.in_stream):
            elem.offset = i * 0.25
            elem.duration = duration.Duration(0.25)
        # prepare a valid list of Rests and ElementWrappers, happening simultaneously, to see that
        # we can properly filter by type
        self.mixed_list = []
        self.shared_mixed_list = []
        mixed_series_data = []
        mixed_series_offsets = []
        mixed_series_rests = []
        mixed_series_rests_offsets = []
        mixed_series_notes = []
        mixed_series_notes_offsets = []
        for i in xrange(100):
            app_me = note.Rest(quarterLength=0.25)
            app_me.offset = i * 0.5
            mixed_series_offsets.append(app_me.offset)
            mixed_series_rests_offsets.append(app_me.offset)
            mixed_series_rests.append(u'Rest')
            mixed_series_data.append(u'Rest')
            self.mixed_list.append(app_me)
            app_me = base.ElementWrapper(unicode(i))
            app_me.offset = i * 0.5 + 0.25
            app_me.duration = duration.Duration(0.25)
            mixed_series_offsets.append(app_me.offset)
            mixed_series_notes_offsets.append(app_me.offset)
            mixed_series_data.append(unicode(i))
            mixed_series_notes.append(unicode(i))
            self.mixed_list.append(app_me)
        self.mixed_series = pandas.Series(mixed_series_data, index=mixed_series_offsets)
        self.mixed_series_notes = pandas.Series(mixed_series_notes,
                                                index=mixed_series_notes_offsets)
        self.mixed_series_rests = pandas.Series(mixed_series_rests,
                                                index=mixed_series_rests_offsets)
        self.mixed_list = stream.Stream(self.mixed_list)
        # same list as previous, but with a Rest and ElementerWrapper sharing each offset
        s_m_series = []
        s_m_series_offsets = []
        for i in xrange(100):
            app_me = note.Rest(quarterLength=0.25)
            app_me.offset = i * 0.25
            s_m_series_offsets.append(app_me.offset)
            s_m_series.append(u'Rest')
            self.shared_mixed_list.append(app_me)
            app_me = base.ElementWrapper(i)
            app_me.offset = i * 0.25
            app_me.duration = duration.Duration(0.25)
            s_m_series_offsets.append(app_me.offset)
            s_m_series.append(unicode(i))
            self.shared_mixed_list.append(app_me)
        self.shared_mixed_list = stream.Stream(self.shared_mixed_list)
        self.shared_mixed_series = pandas.Series(s_m_series, index=s_m_series_offsets)


class TestIndexerSinglePart(IndexerTestBase):
    def test_series_indexer(self):
        result_uniform = indexer.series_indexer(0, [self.in_series], verbatim_ser)[1]
        # that we get a Series back when a Series is given
        self.assertIs(type(result_uniform), pandas.Series, msg='')
        # the verbatim_ser function is designed to produce exactly what is given
        self.assertSequenceEqual(list(result_uniform.index), list(self.in_series.index))
        self.assertSequenceEqual(list(result_uniform), list(self.in_series))
        result_mixed = indexer.series_indexer(0, [self.mixed_series], verbatim_ser)[1]
        # that a list with two types is not filtered when it's given as a Series
        self.assertEqual(len(self.mixed_series), len(result_mixed))
        expect_mixed = [u'Rest' if isinstance(elt, note.Rest) else elt.obj
                        for elt in self.mixed_list]
        self.assertSequenceEqual(list(expect_mixed), list(result_mixed))

    def test_stream_indexer(self):
        result = indexer.stream_indexer(0, [self.in_stream], verbatim, [base.ElementWrapper])[1]
        # that we get a Series back when a Stream is given
        self.assertIs(type(result), pandas.Series)
        # the verbatim function is designed to produce exactly what is given
        self.assertEqual(len(result), len(self.in_stream))
        self.assertSequenceEqual(list(result), [elt.obj for elt in self.in_stream])

    def test_mp_indexer_8(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> one event at each offset
        # input_stream = stream.Stream(self.mixed_list)
        result = indexer.stream_indexer(0, [self.in_stream],
                                        verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_series), len(result))

    def test_mp_indexer_10(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> one event at each offset
        result = \
            indexer.stream_indexer(0, [self.mixed_list], verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.mixed_series_notes)):
            self.assertEqual(self.mixed_series_notes[i], result[i])

    def test_mp_indexer_10_pickle(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # ** inputted Streams are pickled
        # --> test values
        # --> one event at each offset
        input_stream = converter.freeze(stream.Stream(self.mixed_list), u'pickle')
        result = indexer.stream_indexer(0, [input_stream], verbatim, [base.ElementWrapper])[1]
        for i in xrange(len(self.mixed_series_notes)):
            self.assertEqual(self.mixed_series_notes[i], result[i])

    def test_mp_indexer_12(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        result = indexer.stream_indexer(0, [self.in_stream],
                                        verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_series), len(result))

    def test_mp_indexer_12a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        # input_stream = stream.Stream(self.shared_mixed_list)
        result = indexer.stream_indexer(0, [self.shared_mixed_list],
                                        verbatim_rests,
                                        [base.ElementWrapper, note.Rest])[1]
        self.assertEqual(len(self.shared_mixed_list), len(result))

    # def test_mp_indexer_13(self):  # TODO: fails pending implementation of MultiIndex
    #     # that a list with two types is not filtered when it's given as a Series, even if there's
    #     # a value for the "types" parameter
    #     # --> test lengths
    #     # --> two events at each offset
    #     result = indexer.series_indexer(0, [self.shared_mixed_series], verbatim_rests)[1]
    #     self.assertEqual(len(self.shared_mixed_series), len(result))

    # def test_mp_indexer_14a(self):  # TODO: fails pending implementation of MultiIndex
    #     # that a list with two types is properly filtered when it's given as a Stream
    #     # --> test values
    #     # --> two events at each offset
    #     # --> if we want ElementWrappers and Rests
    #     result = indexer.stream_indexer(0, [self.shared_mixed_list],
    #                                      verbatim_rests,
    #                                      [base.ElementWrapper, note.Rest])[1]
    #     for i in self.shared_mixed_series.index:
    #         self.assertEqual(result[i], pandas.Series([u'Rest', unicode(i)], index=[i, i]))

    # def test_mp_indexer_15(self):  # TODO: fails pending implementation of MultiIndex
    #     # that a list with two types is not filtered when it's given as a Series,
    #     # even if there's a value for the "types" parameter
    #     # --> test values
    #     # --> two events at each offset
    #     result = indexer.series_indexer(0, [self.shared_mixed_series], verbatim_rests)[1]
    #     for i in self.shared_mixed_series.index:
    #         self.assertEqual(result[i], pandas.Series([u'Rest', unicode(i)], index=[i, i]))

    def test_mp_indexer_14(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        result = indexer.stream_indexer(0, [self.shared_mixed_list],
                                        verbatim,
                                        [base.ElementWrapper])[1]
        for i in xrange(len(self.in_stream)):
            self.assertEqual(self.in_series[i], result[i])


class TestIndexerThreeParts(IndexerTestBase):
    def setUp(self):
        super(TestIndexerThreeParts, self).setUp()
        self.test_series = [self.in_series,
                            copy.deepcopy(self.in_series),
                            copy.deepcopy(self.in_series)]
        self.test_streams = [self.in_stream,
                             copy.deepcopy(self.in_stream),
                             copy.deepcopy(self.in_stream)]

    def test_mpi_triple_1(self):
        # that we get a Series back when a Series is given
        result = indexer.series_indexer(0, self.test_series, verbatim, [base.ElementWrapper])[1]
        self.assertTrue(isinstance(result, pandas.Series))

    def test_mpi_triple_2(self):
        # that we get a Series back when a Stream is given
        result = indexer.stream_indexer(0, self.test_streams, verbatim, [base.ElementWrapper])[1]
        self.assertTrue(isinstance(result, pandas.Series))

    def test_mpi_triple_5(self):
        # that the resulting Series is the same length (given a Stream)
        result = indexer.stream_indexer(0, self.test_streams, verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_stream), len(result))

    def test_mpi_triple_6(self):
        # that the resulting Series is the same length (given a Series)
        result = indexer.stream_indexer(0, self.test_streams, verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_stream), len(result))

    def test_mpi_triple_7(self):
        # that the resulting Series has the same objects (given a Stream)
        result = indexer.stream_indexer(0, self.test_streams, verbatim, [base.ElementWrapper])[1]
        for self_item, result_item in zip(self.in_stream, result):
            res = str((self_item.obj, self_item.obj, self_item.obj))
            self.assertEqual(res, result_item.obj)

    def test_mpi_triple_8(self):
        # that the resulting Series has the same objects (given a Series)
        result = indexer.stream_indexer(0, self.test_series, verbatim)[1]
        for self_item, result_item in zip(self.in_series, result):
            res = str((self_item.obj, self_item.obj, self_item.obj))
            self.assertEqual(res, result_item.obj)

    def test_mpi_triple_9(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> one event at each offset
        result = indexer.stream_indexer(0, self.test_streams, verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_stream), len(result))

    def test_mpi_triple_10(self):
        # that a list with two types is not filtered when it's given as a Series
        # --> test lengths
        # --> one event at each offset
        result = indexer.stream_indexer(0, self.test_streams, verbatim_rests)[1]
        self.assertEqual(len(self.mixed_list), len(result))

    def test_mpi_triple_11(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> one event at each offset
        result = indexer.stream_indexer(0, self.test_streams, verbatim, [base.ElementWrapper])[1]
        for self_item, result_item in zip(self.in_stream, result):
            res = str((self_item.obj, self_item.obj, self_item.obj))
            self.assertEqual(res, result_item.obj)

    def test_mpi_triple_12(self):
        # that a list with two types is not filtered when it's given as a Series
        # --> test values
        # --> one event at each offset
        result = indexer.stream_indexer(0, self.test_streams, verbatim_rests)[1]
        for i in xrange(len(self.mixed_list)):
            if isinstance(self.mixed_list[i], note.Rest):
                res = str((u'Rest', u'Rest', u'Rest'))
            else:
                res = str((self.mixed_list[i].obj, self.mixed_list[i].obj, self.mixed_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_13(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        result = indexer.stream_indexer(0, self.test_streams, verbatim, [base.ElementWrapper])[1]
        self.assertEqual(len(self.in_stream), len(result))

    def test_mpi_triple_13a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        result = indexer.stream_indexer(0, self.test_streams,
                                        verbatim_rests,
                                        [base.ElementWrapper, note.Rest])[1]
        self.assertEqual(len(self.shared_mixed_list), len(result))

    def test_mpi_triple_14(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test lengths
        # --> two events at each offset
        input_series = [pandas.Series(self.shared_mixed_list),
                        pandas.Series(copy.deepcopy(self.shared_mixed_list)),
                        pandas.Series(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.series_indexer(0, input_series, verbatim_rests, [base.ElementWrapper])[1]
        self.assertEqual(len(self.shared_mixed_list), len(result))

    def test_mpi_triple_15(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        input_stream = [stream.Stream(self.shared_mixed_list),
                        stream.Stream(copy.deepcopy(self.shared_mixed_list)),
                        stream.Stream(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.stream_indexer(0, input_stream, verbatim, [base.ElementWrapper])[1]
        for self_item, result_item in zip(self.in_stream, result):
            res = str((self_item.obj, self_item.obj, self_item.obj))
            self.assertEqual(res, result_item.obj)

    def test_mpi_triple_15a(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        # --> if we want ElementWrappers and Rests
        input_stream = [stream.Stream(self.shared_mixed_list),
                        stream.Stream(copy.deepcopy(self.shared_mixed_list)),
                        stream.Stream(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.stream_indexer(0, input_stream, verbatim_rests,
                                        [base.ElementWrapper, note.Rest])[1]
        for i in xrange(len(self.mixed_list)):
            if isinstance(self.mixed_list[i], note.Rest):
                res = str((u'Rest', u'Rest', u'Rest'))
            else:
                res = str((self.mixed_list[i].obj, self.mixed_list[i].obj, self.mixed_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_16(self):
        # that a list with two types is not filtered when it's given as a Series, even if there's
        # a value for the "types" parameter
        # --> test values
        # --> two events at each offset
        input_series = [pandas.Series(self.shared_mixed_list),
                        pandas.Series(copy.deepcopy(self.shared_mixed_list)),
                        pandas.Series(copy.deepcopy(self.shared_mixed_list))]
        result = indexer.series_indexer(0, input_series, verbatim_rests, [base.ElementWrapper])[1]
        for i in xrange(len(self.mixed_list)):
            if isinstance(self.mixed_list[i], note.Rest):
                res = str((u'Rest', u'Rest', u'Rest'))
            else:
                res = str((self.mixed_list[i].obj, self.mixed_list[i].obj, self.mixed_list[i].obj))
            self.assertEqual(res, result[i].obj)

    def test_mpi_triple_17(self):
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
        result = indexer.series_indexer(0, [part_1, part_2], verbatim_variable)[1]
        for i in xrange(len(expected)):
            self.assertEqual(expected[i][0], result[i].offset)
            self.assertEqual(expected[i][1], result[i].obj)

    def test_mpi_triple_18(self):
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
        result = \
            indexer.series_indexer(0, [part_1, part_2], verbatim_variable, [base.ElementWrapper])[
                1]
        for i in xrange(len(expected)):
            self.assertEqual(expected[i][0], result[i].offset)
            self.assertEqual(expected[i][1], result[i].obj)

    def test_mpi_triple_19(self):
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
        result = indexer.stream_indexer(0, [part_1, part_2, part_3],
                                        verbatim_variable,
                                        [base.ElementWrapper])[1]
        for i in xrange(len(expected)):
            self.assertEqual(expected[i][0], result[i].offset)
            self.assertEqual(expected[i][1], result[i].obj)


class TestMpiUniqueOffsets(unittest.TestCase):
    def test_mpi_unique_offsets_1(self):
        streams = int_indexer_short.test_1()
        expected = [0.0]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_2(self):
        streams = int_indexer_short.test_2()
        expected = [0.0, 0.25]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_3(self):
        streams = int_indexer_short.test_3()
        expected = [0.0, 0.25]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_4(self):
        streams = int_indexer_short.test_4()
        expected = [0.0, 0.25]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_5(self):
        streams = int_indexer_short.test_5()
        expected = [0.0, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_6(self):
        streams = int_indexer_short.test_6()
        expected = [0.0, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_7(self):
        streams = int_indexer_short.test_7()
        expected = [0.0, 0.5, 1.0, 1.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_8(self):
        streams = int_indexer_short.test_8()
        expected = [0.0, 0.25, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_9(self):
        streams = int_indexer_short.test_9()
        expected = [0.0, 0.25, 0.5, 1.0]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_10(self):
        streams = int_indexer_short.test_10()
        expected = [0.0, 0.25]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_12(self):
        streams = int_indexer_short.test_12()
        expected = [0.0, 0.25, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_13(self):
        streams = int_indexer_short.test_13()
        expected = [0.0, 0.125, 0.25, 0.375, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_14(self):
        streams = int_indexer_short.test_14()
        expected = [0.0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_15(self):
        streams = int_indexer_short.test_15()
        expected = [0.0, 0.5, 0.75, 1.0, 1.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_16(self):
        streams = int_indexer_short.test_16()
        expected = [0.0, 0.5, 0.75, 1.25, 1.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_mpi_unique_offsets_17(self):
        streams = int_indexer_short.test_17()
        expected = [0.0, 0.5, 0.75, 1.125, 1.25, 1.375, 2.0]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)


class TestMpiVertAligner(unittest.TestCase):
    def test_mpi_vert_aligner_1(self):
        in_list = [[1]]
        expected = [[1]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_2(self):
        in_list = [[1, 2]]
        expected = [[1], [2]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_3(self):
        in_list = [[1], [2]]
        expected = [[1, 2]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_4(self):
        in_list = [[1, 2], [1, 2]]
        expected = [[1, 1], [2, 2]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_5(self):
        in_list = [[1, 2], [5]]
        expected = [[1, 5], [2]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_6(self):
        in_list = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
        expected = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_7(self):
        in_list = [[1, 2, 3], [1], [1, 2, 3]]
        expected = [[1, 1, 1], [2, 2], [3, 3]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_8(self):
        in_list = [[1, 2, 3], [1], [1, 2]]
        expected = [[1, 1, 1], [2, 2], [3]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

    def test_mpi_vert_aligner_9(self):
        in_list = [[1], [1], [1]]
        expected = [[1, 1, 1]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertEqual(expected, actual)

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
INDEXER_1_PART_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerSinglePart)
INDEXER_3_PARTS_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerThreeParts)
UNIQUE_OFFSETS_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMpiUniqueOffsets)
VERT_ALIGNER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMpiVertAligner)
INDEXER_HARDCORE_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerHardcore)
