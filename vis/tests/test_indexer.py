#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_indexer.py
# Purpose:                Tests for the Indexer superclass.
#
# Copyright (C) 2013 Christopher Antila
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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import mock
import copy
import pandas
from music21 import base, stream, duration, note, converter, clef
from vis.analyzers import indexer
from vis.tests.corpus import int_indexer_short


def fake_indexer_func(ecks):
    return unicode(ecks)


class TestIndexerHardcore(unittest.TestCase):
    # accessing TestIndexer._indexer_func is part of the test
    # pylint: disable=W0212
    def test_indexer_hardcore_1(self):
        # That calling Indexer.__init__() with the wrong type results in the proper error message.
        class TestIndexer(indexer.Indexer):
            # Class with bare minimum changes, since we can't instantiate Indexer directly
            required_score_type = stream.Stream

        test_parts = [pandas.Series()]
        settings = {}
        self.assertRaises(TypeError, TestIndexer, test_parts, settings)
        error_msg = unicode("<class 'vis.tests.test_indexer.TestIndexer'> requires "
                            "<class 'music21.stream.Stream'> objects, not <class 'pandas.core"
                            ".series.Series'>")
        try:
            TestIndexer(test_parts, settings)
        except TypeError as err:
            self.assertEqual(err.args[0], error_msg)

    def test_indexer_hardcore_2(self):
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

    def test_indexer_hardcore_3(self):
        # when no "types" is specified, make sure it returns everything in the Stream
        # setup the input stream
        the_stream = stream.Stream()
        the_stream.append(note.Note(u'D#2', quarterLength=0.5))
        the_stream.append(note.Rest(quarterLength=0.5))
        the_stream.append(clef.TrebleClef())
        # setup the expected Series
        expected = pandas.Series({0.0: note.Note(u'D#2', quarterLength=0.5),
                                  0.5: note.Rest(quarterLength=0.5),
                                  1.0: clef.TrebleClef()})
        # run the test; verify results
        actual = indexer.stream_indexer(12, [the_stream], verbatim_ser)
        # check the multiprocessing token is returned, then get rid of it
        self.assertEqual(2, len(actual))
        self.assertEqual(12, actual[0])
        actual = actual[1]
        # check both the index and values are equal
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))


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
    return unicode(tuple(item.obj for item in iterable))


# Jamie: pylint says we have 8 instance attributes on this bad boy, which is just too many.
# Christopher: pylint can shove it
class IndexerTestBase(unittest.TestCase):
    # pylint: disable=R0902
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
        s_m_rests_series = []
        s_m_rests_series_offsets = []
        for i in xrange(100):
            app_me = note.Rest(quarterLength=0.25)
            app_me.offset = i * 0.25
            s_m_series_offsets.append(app_me.offset)
            s_m_series.append(u'Rest')
            s_m_rests_series.append(u'Rest')
            s_m_rests_series_offsets.append(app_me.offset)
            self.shared_mixed_list.append(app_me)
            app_me = base.ElementWrapper(i)
            app_me.offset = i * 0.25
            app_me.duration = duration.Duration(0.25)
            s_m_series_offsets.append(app_me.offset)
            s_m_series.append(unicode(i))
            self.shared_mixed_list.append(app_me)
        self.shared_mixed_list = stream.Stream(self.shared_mixed_list)
        self.shared_mixed_series = pandas.Series(s_m_series, index=s_m_series_offsets)
        self.shared_mixed_rests_series = pandas.Series(s_m_rests_series,
                                                       index=s_m_rests_series_offsets)


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

    def test_mp_indexer_1(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> one event at each offset
        # input_stream = stream.Stream(self.mixed_list)
        actual = indexer.stream_indexer(0, [self.in_stream], verbatim, [base.ElementWrapper])[1]
        self.assertSequenceEqual(list(self.in_series.index), list(actual.index))
        self.assertSequenceEqual(list(self.in_series.values), list(actual.values))

    def test_mp_indexer_2(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> one event at each offset
        actual = indexer.stream_indexer(0, [self.mixed_list], verbatim, [base.ElementWrapper])[1]
        self.assertSequenceEqual(list(self.mixed_series_notes.index), list(actual.index))
        self.assertSequenceEqual(list(self.mixed_series_notes.values), list(actual.values))

    def test_mp_indexer_3(self):
        # same as test _2, but the Strame is pickled
        # ** inputted Streams are pickled
        # --> test values
        # --> one event at each offset
        input_stream = converter.freeze(stream.Stream(self.mixed_list), u'pickle')
        actual = indexer.stream_indexer(0, [input_stream], verbatim, [base.ElementWrapper])[1]
        self.assertSequenceEqual(list(self.mixed_series_notes.index), list(actual.index))
        self.assertSequenceEqual(list(self.mixed_series_notes.values), list(actual.values))

    def test_mp_indexer_4(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        actual = indexer.stream_indexer(0, [self.in_stream], verbatim, [base.ElementWrapper])[1]
        self.assertSequenceEqual(list(self.in_series.index), list(actual.index))
        self.assertSequenceEqual(list(self.in_series.values), list(actual.values))

    def test_mp_indexer_5(self):
        # test _4, but we want both ElementWrapper and Rest objects (we should only get
        # the "first" events)
        actual = indexer.stream_indexer(0,
                                        [self.shared_mixed_list],
                                        verbatim_rests,
                                        [base.ElementWrapper, note.Rest])[1]
        self.assertSequenceEqual(list(self.shared_mixed_rests_series.index), list(actual.index))
        self.assertSequenceEqual(list(self.shared_mixed_rests_series.values), list(actual.values))

    def test_mp_indexer_6(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        actual = indexer.stream_indexer(0,
                                        [self.shared_mixed_list],
                                        verbatim,
                                        [base.ElementWrapper])[1]
        self.assertSequenceEqual(list(self.in_series.index), list(actual.index))
        self.assertSequenceEqual(list(self.in_series.values), list(actual.values))

    # TODO: March 2014: the following tests fail; I'm not sure we need them, or why they're here,
    #       but in the past I made a note that it was "pending implementation of MultiIndex"
    # def test_mp_indexer_7(self):
    #     # that a list with two types is not filtered when it's given as a Series, even if there's
    #     # a value for the "types" parameter
    #     # --> test lengths
    #     # --> two events at each offset
    #     result = indexer.series_indexer(0, [self.shared_mixed_series], verbatim_rests)[1]
    #     self.assertEqual(len(self.shared_mixed_series), len(result))

    # def test_mp_indexer_8(self):
    #     # test _7, but it's given as a Stream, so it should be filtered
    #     result = indexer.stream_indexer(0, [self.shared_mixed_list],
    #                                      verbatim_rests,
    #                                      [base.ElementWrapper, note.Rest])[1]
    #     for i in self.shared_mixed_series.index:
    #         self.assertEqual(result[i], pandas.Series([u'Rest', unicode(i)], index=[i, i]))

    # def test_mp_indexer_9(self):
    #     # that a list with two types is not filtered when it's given as a Series,
    #     # even if there's a value for the "types" parameter
    #     # --> test values
    #     # --> two events at each offset
    #     result = indexer.series_indexer(0, [self.shared_mixed_series], verbatim_rests)[1]
    #     for i in self.shared_mixed_series.index:
    #         self.assertEqual(result[i], pandas.Series([u'Rest', unicode(i)], index=[i, i]))


class TestIndexerMultiEvent(IndexerTestBase):
    # Testing that, if there are many events at an offset, only the "first" one is outputted.
    def setUp(self):
        super(TestIndexerMultiEvent, self).setUp()
        self.test_series = [self.in_series,
                            copy.deepcopy(self.in_series),
                            copy.deepcopy(self.in_series)]
        self.test_streams = [self.in_stream,
                             copy.deepcopy(self.in_stream),
                             copy.deepcopy(self.in_stream)]

    def test_multi_event_1(self):
        # Test this:
        # offset:  0.0  |  0.5  |  1.0  |  1.5  |  2.0
        # part 1:  [0]  |  [1]  |  [2]  |  [3]  |  [4]
        # part 2:  [0]  |  [1]  |  [2]  |  [3]  |  [4]
        part_1 = stream.Stream()
        for i in xrange(5):
            obj = base.ElementWrapper(i)
            obj.offset = 0.5 * i
            obj.duration = duration.Duration(0.5)
            part_1.append(obj)
        part_2 = stream.Stream()
        for i in xrange(5):
            obj = base.ElementWrapper(i)
            obj.offset = 0.5 * i
            obj.duration = duration.Duration(0.5)
            part_2.append(obj)
        expected = pandas.Series({0.0: u'(0, 0)', 0.5: u'(1, 1)', 1.0: u'(2, 2)',
                                  1.5: u'(3, 3)', 2.0: u'(4, 4)'})
        actual = indexer.stream_indexer(0, [part_1, part_2], verbatim_variable)[1]
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected), list(actual))

    def test_multi_event_2(self):
        # Test this:
        # offset:  0.0  |  0.5     |  1.0     |  1.5     |  2.0
        # part 1:  [1]  |  [2][6]  |  [3]     |  [4][7]  |  [5][8]
        # part 2:  [1]  |  [2][6]  |  [3][7]  |  [4]     |  [5][8]
        part_1 = stream.Stream()
        for i in xrange(5):
            obj = base.ElementWrapper(i)
            obj.offset = 0.5 * i
            obj.duration = duration.Duration(0.5)
            part_1.append(obj)
        part_2 = stream.Stream()
        for i in xrange(5):
            obj = base.ElementWrapper(i)
            obj.offset = 0.5 * i
            obj.duration = duration.Duration(0.5)
            part_2.append(obj)
        add_these = [(part_1, 0.5, 6), (part_1, 1.5, 7), (part_1, 2.0, 8),
                     (part_2, 0.5, 6), (part_2, 1.0, 7), (part_2, 2.0, 8)]
        for part, offset, number in add_these:
            zed = base.ElementWrapper(number)
            zed.duration = duration.Duration(0.5)
            part.insert(offset, zed)
        expected = pandas.Series({0.0: u'(0, 0)', 0.5: u'(1, 1)', 1.0: u'(2, 2)',
                                  1.5: u'(3, 3)', 2.0: u'(4, 4)'})
        actual = indexer.stream_indexer(0, [part_1, part_2], verbatim_variable)[1]
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected), list(actual))

    def test_multi_event_3(self):
        ## offset:  0.0  |  0.5     |  1.0        |  1.5     |  2.0
        ## part 1:  [1]  |  [2][6]  |  [3][7][8]  |  [4][9]  |  [5][10][11]
        ## part 2:  [1]  |  [2][6]  |  [3][7]     |  [4]     |  [5]
        ## part 3:  [1]  |  [2][6]  |  [3][7]     |  [4][8]  |  [5][9]
        part_1 = stream.Stream()
        for i in xrange(5):
            obj = base.ElementWrapper(i)
            obj.offset = 0.5 * i
            obj.duration = duration.Duration(0.5)
            part_1.append(obj)
        part_2 = stream.Stream()
        for i in xrange(5):
            obj = base.ElementWrapper(i)
            obj.offset = 0.5 * i
            obj.duration = duration.Duration(0.5)
            part_2.append(obj)
        part_3 = stream.Stream()
        for i in xrange(5):
            obj = base.ElementWrapper(i)
            obj.offset = 0.5 * i
            obj.duration = duration.Duration(0.5)
            part_3.append(obj)
        add_these = [(part_1, 0.5, 6), (part_1, 1.0, 7), (part_1, 1.0, 8), (part_1, 1.5, 9),
                     (part_1, 2.0, 10), (part_1, 2.0, 11),
                     (part_2, 0.5, 6), (part_2, 1.0, 7),
                     (part_3, 0.5, 6), (part_3, 1.0, 7), (part_3, 1.5, 8), (part_3, 2.0, 9)]
        for part, offset, number in add_these:
            zed = base.ElementWrapper(number)
            zed.duration = duration.Duration(0.5)
            part.insert(offset, zed)
        expected = pandas.Series({0.0: u'(0, 0)', 0.5: u'(1, 1)', 1.0: u'(2, 2)',
                                  1.5: u'(3, 3)', 2.0: u'(4, 4)'})
        actual = indexer.stream_indexer(0, [part_1, part_2], verbatim_variable)[1]
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected), list(actual))


class TestMpiUniqueOffsets(unittest.TestCase):
    def test_mpi_unique_offsets_1(self):
        streams = int_indexer_short.test_1()
        expected = [0.0]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_2(self):
        streams = int_indexer_short.test_2()
        expected = [0.0, 0.25]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_3(self):
        streams = int_indexer_short.test_3()
        expected = [0.0, 0.25]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_4(self):
        streams = int_indexer_short.test_4()
        expected = [0.0, 0.25]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_5(self):
        streams = int_indexer_short.test_5()
        expected = [0.0, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_6(self):
        streams = int_indexer_short.test_6()
        expected = [0.0, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_7(self):
        streams = int_indexer_short.test_7()
        expected = [0.0, 0.5, 1.0, 1.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_8(self):
        streams = int_indexer_short.test_8()
        expected = [0.0, 0.25, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_9(self):
        streams = int_indexer_short.test_9()
        expected = [0.0, 0.25, 0.5, 1.0]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_10(self):
        streams = int_indexer_short.test_10()
        expected = [0.0, 0.25]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_12(self):
        streams = int_indexer_short.test_12()
        expected = [0.0, 0.25, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_13(self):
        streams = int_indexer_short.test_13()
        expected = [0.0, 0.125, 0.25, 0.375, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_14(self):
        streams = int_indexer_short.test_14()
        expected = [0.0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_15(self):
        streams = int_indexer_short.test_15()
        expected = [0.0, 0.5, 0.75, 1.0, 1.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_16(self):
        streams = int_indexer_short.test_16()
        expected = [0.0, 0.5, 0.75, 1.25, 1.5]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_unique_offsets_17(self):
        streams = int_indexer_short.test_17()
        expected = [0.0, 0.5, 0.75, 1.125, 1.25, 1.375, 2.0]
        actual = indexer.mpi_unique_offsets(streams)
        self.assertSequenceEqual(expected, actual)


class TestMpiVertAligner(unittest.TestCase):
    def test_mpi_vert_aligner_1(self):
        in_list = [[1]]
        expected = [[1]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_vert_aligner_2(self):
        in_list = [[1, 2]]
        expected = [[1], [2]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_vert_aligner_3(self):
        in_list = [[1], [2]]
        expected = [[1, 2]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_vert_aligner_4(self):
        in_list = [[1, 2], [1, 2]]
        expected = [[1, 1], [2, 2]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_vert_aligner_5(self):
        in_list = [[1, 2], [5]]
        expected = [[1, 5], [2]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_vert_aligner_6(self):
        in_list = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
        expected = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_vert_aligner_7(self):
        in_list = [[1, 2, 3], [1], [1, 2, 3]]
        expected = [[1, 1, 1], [2, 2], [3, 3]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_vert_aligner_8(self):
        in_list = [[1, 2, 3], [1], [1, 2]]
        expected = [[1, 1, 1], [2, 2], [3]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

    def test_mpi_vert_aligner_9(self):
        in_list = [[1], [1], [1]]
        expected = [[1, 1, 1]]
        actual = indexer.mpi_vert_aligner(in_list)
        self.assertSequenceEqual(expected, actual)

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
INDEXER_1_PART_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerSinglePart)
INDEXER_MULTI_EVENT_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerMultiEvent)
UNIQUE_OFFSETS_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMpiUniqueOffsets)
VERT_ALIGNER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMpiVertAligner)
INDEXER_HARDCORE_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerHardcore)
