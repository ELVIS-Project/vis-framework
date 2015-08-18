#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_indexer.py
# Purpose:                Tests for the Indexer superclass.
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

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import copy
import six
if six.PY3:
    from unittest import mock
else:
    import mock
from numpy import NaN
import pandas
from music21 import base, stream, duration, note, converter, clef
from vis.analyzers import indexer
from vis.tests.corpus import int_indexer_short


def fake_indexer_func(ecks):
    return six.u(str(ecks))


class TestIndexerInit(unittest.TestCase):
    # accessing TestIndexer._indexer_func is part of the test
    # pylint: disable=W0212
    def test_indexer_init_1(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 1: stream.Part, given a list of Part
        class TestIndexer(indexer.Indexer):
            # Minimum required changes!
            required_score_type = 'stream.Part'
        test_score = [stream.Part(), stream.Part()]
        test_ind = TestIndexer(test_score)
        self.assertTrue(isinstance(test_ind._score, list))
        self.assertSequenceEqual(test_score, test_ind._score)

    def test_indexer_init_2a(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 2a: stream.Part, given a Score (two parts in the Score)
        class TestIndexer(indexer.Indexer):
            required_score_type = 'stream.Part'
        test_score = stream.Score([stream.Part(), stream.Part()])
        test_ind = TestIndexer(test_score)
        self.assertTrue(isinstance(test_ind._score, list))
        self.assertSequenceEqual(test_score, test_ind._score)

    def test_indexer_init_2b(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 2b: stream.Part, given a Score (no parts in the Score)
        class TestIndexer(indexer.Indexer):
            required_score_type = 'stream.Part'
        test_score = stream.Score([])
        test_ind = TestIndexer(test_score)
        self.assertTrue(isinstance(test_ind._score, list))
        self.assertSequenceEqual(test_score, test_ind._score)

    def test_indexer_init_3(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 3: stream.Score, given a Score
        class TestIndexer(indexer.Indexer):
            required_score_type = 'stream.Score'
        test_score = stream.Score([stream.Part(), stream.Part()])
        test_ind = TestIndexer(test_score)
        self.assertTrue(isinstance(test_ind._score, stream.Score))
        self.assertSequenceEqual(test_score, test_ind._score)

    def test_indexer_init_4(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 4: pandas.Series, given a list of Series
        class TestIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        test_score = [pandas.Series(), pandas.Series()]
        test_ind = TestIndexer(test_score)
        self.assertTrue(isinstance(test_ind._score, list))
        self.assertSequenceEqual(test_score, test_ind._score)

    def test_indexer_init_5a(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 5a: pandas.Series, given a DataFrame
        class TestIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        the_index = pandas.MultiIndex.from_tuples([('NRI', '0'), ('NRI', '1')],
                                                  names=['Indexer', 'Parts'])
        series_list = [pandas.Series([2]), pandas.Series([1])]
        test_score = pandas.DataFrame(series_list, index=the_index).T
        test_ind = TestIndexer(test_score)
        self.assertTrue(isinstance(test_ind._score, list))
        self.assertSequenceEqual(list(series_list[0].index), list(test_ind._score[0].index))
        self.assertSequenceEqual(list(series_list[1].index), list(test_ind._score[1].index))
        self.assertSequenceEqual(list(series_list[0].values), list(test_ind._score[0].values))
        self.assertSequenceEqual(list(series_list[1].values), list(test_ind._score[1].values))

    def test_indexer_init_5b(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 5b: pandas.Series, given a DataFrame (but there are two indexers of results!)
        class TestIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        the_tuples = [('NRI', '0'), ('NRI', '1'), ('HII', '0'), ('HII', '1')]
        the_index = pandas.MultiIndex.from_tuples(the_tuples, names=['Indexer', 'Parts'])
        series_list = [pandas.Series([i]) for i in [2, 4, 6, 8]]  # who do we appreciate?
        test_score = pandas.DataFrame(series_list, index=the_index).T
        self.assertRaises(IndexError, TestIndexer, test_score)
        try:
            TestIndexer(test_score)
        except IndexError as inderr:
            self.assertEqual(indexer.Indexer._INIT_INDEX_ERR, inderr.args[0])

    def test_indexer_init_5c(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 5c: pandas.Series, given a DataFrame (but there is no MultiIndex)
        class TestIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        series_dict = {str(i): pandas.Series([i]) for i in [2, 4, 6, 8]}
        test_score = pandas.DataFrame(series_dict)
        self.assertRaises(IndexError, TestIndexer, test_score)
        try:
            TestIndexer(test_score)
        except IndexError as inderr:
            self.assertEqual(indexer.Indexer._INIT_INDEX_ERR, inderr.args[0])

    def test_indexer_init_5d(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 5d: pandas.Series, given a DataFrame (but there are no indexers)
        class TestIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        test_score = pandas.DataFrame()
        self.assertRaises(IndexError, TestIndexer, test_score)
        try:
            TestIndexer(test_score)
        except IndexError as inderr:
            self.assertEqual(indexer.Indexer._INIT_INDEX_ERR, inderr.args[0])

    def test_indexer_init_5e(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 5e: pandas.Series, given a DataFrame---make sure NaN values are dropped from the Series
        class TestIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        the_index = pandas.MultiIndex.from_tuples([('NRI', '0'), ('NRI', '1')],
                                                  names=['Indexer', 'Parts'])
        series_input = [pandas.Series([1, NaN, 2, NaN, 3, NaN, 4, NaN, NaN, 5]),
                        pandas.Series([42, 43, 44, NaN, NaN, NaN])]
        # NB: the first Series will have a strange index because of the "internal" NaNs
        expected = [pandas.Series([1, 2, 3, 4, 5], index=[0, 2, 4, 6, 9]),
                    pandas.Series([42, 43, 44])]
        test_score = pandas.DataFrame(series_input, index=the_index).T
        test_ind = TestIndexer(test_score)
        self.assertTrue(isinstance(test_ind._score, list))
        self.assertSequenceEqual(list(expected[0].index), list(test_ind._score[0].index))
        self.assertSequenceEqual(list(expected[1].index), list(test_ind._score[1].index))
        self.assertSequenceEqual(list(expected[0].values), list(test_ind._score[0].values))
        self.assertSequenceEqual(list(expected[1].values), list(test_ind._score[1].values))

    def test_indexer_init_6(self):
        # The first six tests ensure __init__() accepts the six valid types of "score" argument.
        # 6: pandas.DataFrame, given a DataFrame
        class TestIndexer(indexer.Indexer):
            required_score_type = 'pandas.DataFrame'
        the_index = pandas.MultiIndex.from_tuples([('NRI', '0'), ('NRI', '1')],
                                                  names=['Indexer', 'Parts'])
        series_list = [pandas.Series([2]), pandas.Series([1])]
        test_score = pandas.DataFrame(series_list, index=the_index).T
        test_ind = TestIndexer(test_score)
        self.assertTrue(isinstance(test_ind._score, pandas.DataFrame))
        self.assertSequenceEqual(list(series_list[0].index), list(test_ind._score['NRI']['0'].index))
        self.assertSequenceEqual(list(series_list[1].index), list(test_ind._score['NRI']['1'].index))
        self.assertSequenceEqual(list(series_list[0].values), list(test_ind._score['NRI']['0'].values))
        self.assertSequenceEqual(list(series_list[1].values), list(test_ind._score['NRI']['1'].values))

    def test_indexer_init_7(self):
        # That calling Indexer.__init__() with the wrong type results in the proper error message.
        class TestIndexer(indexer.Indexer):
            # Class with bare minimum changes, since we can't instantiate Indexer directly
            required_score_type = 'stream.Part'

        test_parts = [pandas.Series()]
        settings = {}
        self.assertRaises(TypeError, TestIndexer, test_parts, settings)
        if six.PY2:
            exp_err = "<class 'vis.tests.test_indexer.TestIndexer'>"
            exp_err = indexer.Indexer._INIT_TYPE_ERR.format(exp_err, "stream.Part")
        else:
            exp_err = "<class 'vis.tests.test_indexer.TestIndexerInit.test_indexer_init_7.<locals>.TestIndexer'>"
            exp_err = indexer.Indexer._INIT_TYPE_ERR.format(exp_err, "stream.Part")
        try:
            TestIndexer(test_parts, settings)
        except TypeError as err:
            self.assertEqual(exp_err, err.args[0])

    def test_indexer_init_8(self):
        # That _do_multiprocessing() passes the correct arguments to stream_indexer()
        class TestIndexer(indexer.Indexer):
            # Class with bare minimum changes, since we can't instantiate Indexer directly
            required_score_type = 'stream.Part'
            def run(self):
                self._do_multiprocessing([[0]])
        # the actual testing
        test_parts = [stream.Part()]
        settings = {}
        # prepare mocks
        with mock.patch('vis.analyzers.indexer.stream_indexer') as mpi_mock:
            # run test
            t_ind = TestIndexer(test_parts, settings)
            t_ind._indexer_func = fake_indexer_func
            t_ind.run()
            # check results
            mpi_mock.assert_called_once_with(test_parts, fake_indexer_func, None, False)

    def test_indexer_init_9(self):
        # That calling Indexer.__init__() with required_score_type set to an invalid value results
        # in the proper error message.
        class TestIndexer(indexer.Indexer):
            # Class with bare minimum changes, since we can't instantiate Indexer directly
            required_score_type = stream.Part

        test_parts = [pandas.Series()]
        settings = {}
        self.assertRaises(TypeError, TestIndexer, test_parts, settings)
        if six.PY2:
            exp_err = "<class 'vis.tests.test_indexer.TestIndexer'>"
            exp_err = indexer.Indexer._INIT_KEY_ERR.format(exp_err, "stream.Part")
        else:
            exp_err = "<class 'vis.tests.test_indexer.TestIndexerInit.test_indexer_init_9.<locals>.TestIndexer'>"
            exp_err = indexer.Indexer._INIT_KEY_ERR.format(exp_err, "stream.Part")
        try:
            TestIndexer(test_parts, settings)
        except TypeError as err:
            self.assertEqual(exp_err, err.args[0])

    def test_indexer_init_10(self):
        # when no "types" is specified, make sure it returns everything in the Stream
        # setup the input stream
        the_stream = stream.Stream()
        the_stream.append(note.Note('D#2', quarterLength=0.5))
        the_stream.append(note.Rest(quarterLength=0.5))
        the_stream.append(clef.TrebleClef())
        # setup the expected Series
        expected = pandas.Series({0.0: note.Note('D#2', quarterLength=0.5),
                                  0.5: note.Rest(quarterLength=0.5),
                                  1.0: clef.TrebleClef()})
        # run the test; verify results
        actual = indexer.stream_indexer([the_stream], verbatim_ser)
        self.assertEqual(3, len(actual))
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
    return 'Rest' if isinstance(arg[0], note.Rest) else six.u(str(arg[0].obj))


def verbatim_variable(iterable):
    return six.u(str(tuple(item.obj for item in iterable)))


# Jamie: pylint says we have 8 instance attributes on this bad boy, which is just too many.
# Christopher: pylint can shove it
class IndexerTestBase(unittest.TestCase):
    # pylint: disable=R0902
    def setUp(self):
        # prepare a valid list of ElementWrappers (with proper offset and duration)
        self.in_series = pandas.Series(range(100), index=[0.25 * x for x in range(100)])
        self.in_stream = stream.Stream(base.ElementWrapper(i) for i in range(100))
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
        for i in range(100):
            app_me = note.Rest(quarterLength=0.25)
            app_me.offset = i * 0.5
            mixed_series_offsets.append(app_me.offset)
            mixed_series_rests_offsets.append(app_me.offset)
            mixed_series_rests.append('Rest')
            mixed_series_data.append('Rest')
            self.mixed_list.append(app_me)
            app_me = base.ElementWrapper(str(i))
            app_me.offset = i * 0.5 + 0.25
            app_me.duration = duration.Duration(0.25)
            mixed_series_offsets.append(app_me.offset)
            mixed_series_notes_offsets.append(app_me.offset)
            mixed_series_data.append(str(i))
            mixed_series_notes.append(str(i))
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
        for i in range(100):
            app_me = note.Rest(quarterLength=0.25)
            app_me.offset = i * 0.25
            s_m_series_offsets.append(app_me.offset)
            s_m_series.append('Rest')
            s_m_rests_series.append('Rest')
            s_m_rests_series_offsets.append(app_me.offset)
            self.shared_mixed_list.append(app_me)
            app_me = base.ElementWrapper(i)
            app_me.offset = i * 0.25
            app_me.duration = duration.Duration(0.25)
            s_m_series_offsets.append(app_me.offset)
            s_m_series.append(str(i))
            self.shared_mixed_list.append(app_me)
        self.shared_mixed_list = stream.Stream(self.shared_mixed_list)
        self.shared_mixed_series = pandas.Series(s_m_series, index=s_m_series_offsets)
        self.shared_mixed_rests_series = pandas.Series(s_m_rests_series,
                                                       index=s_m_rests_series_offsets)


class TestIndexerSinglePart(IndexerTestBase):
    def test_series_indexer(self):
        result_uniform = indexer.series_indexer([self.in_series], verbatim_ser)
        # that we get a Series back when a Series is given
        self.assertIs(type(result_uniform), pandas.Series, msg='')
        # the verbatim_ser function is designed to produce exactly what is given
        self.assertSequenceEqual(list(result_uniform.index), list(self.in_series.index))
        self.assertSequenceEqual(list(result_uniform), list(self.in_series))
        result_mixed = indexer.series_indexer([self.mixed_series], verbatim_ser)
        # that a list with two types is not filtered when it's given as a Series
        self.assertEqual(len(self.mixed_series), len(result_mixed))
        expect_mixed = ['Rest' if isinstance(elt, note.Rest) else elt.obj
                        for elt in self.mixed_list]
        self.assertSequenceEqual(list(expect_mixed), list(result_mixed))

    def test_stream_indexer(self):
        result = indexer.stream_indexer([self.in_stream], verbatim, ('ElementWrapper',))
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
        actual = indexer.stream_indexer([self.in_stream], verbatim, ('ElementWrapper',))
        self.assertSequenceEqual(list(self.in_series.index), list(actual.index))
        self.assertSequenceEqual(list(self.in_series.values), list(actual.values))

    def test_mp_indexer_2(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> one event at each offset
        actual = indexer.stream_indexer([self.mixed_list], verbatim, ('ElementWrapper',))
        self.assertSequenceEqual(list(self.mixed_series_notes.index), list(actual.index))
        self.assertSequenceEqual(list(self.mixed_series_notes.values), list(actual.values))

    # def test_mp_indexer_3(self): # No longer relevant because pickling is no longer used.
    #     # same as test _2, but the Stream is pickled
    #     # ** inputted Streams are pickled
    #     # --> test values
    #     # --> one event at each offset
    #     input_stream = converter.freeze(stream.Stream(self.mixed_list), 'pickle')
    #     actual = indexer.stream_indexer([input_stream], verbatim, [base.ElementWrapper])[1]
    #     self.assertSequenceEqual(list(self.mixed_series_notes.index), list(actual.index))
    #     self.assertSequenceEqual(list(self.mixed_series_notes.values), list(actual.values))

    def test_mp_indexer_4(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test lengths
        # --> two events at each offset
        actual = indexer.stream_indexer([self.in_stream], verbatim, ('ElementWrapper',))
        self.assertSequenceEqual(list(self.in_series.index), list(actual.index))
        self.assertSequenceEqual(list(self.in_series.values), list(actual.values))

    def test_mp_indexer_5(self):
        # test _4, but we want both ElementWrapper and Rest objects (we should only get
        # the "first" events)
        actual = indexer.stream_indexer([self.shared_mixed_list], verbatim_rests, ('Rest',))
        self.assertSequenceEqual(list(self.shared_mixed_rests_series.index), list(actual.index))
        self.assertSequenceEqual(list(self.shared_mixed_rests_series.values), list(actual.values))

    def test_mp_indexer_6(self):
        # that a list with two types is properly filtered when it's given as a Stream
        # --> test values
        # --> two events at each offset
        actual = indexer.stream_indexer([self.shared_mixed_list],
                                        verbatim,
                                        ('ElementWrapper',))
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
    #         self.assertEqual(result[i], pandas.Series(['Rest', str(i)], index=[i, i]))

    # def test_mp_indexer_9(self):
    #     # that a list with two types is not filtered when it's given as a Series,
    #     # even if there's a value for the "types" parameter
    #     # --> test values
    #     # --> two events at each offset
    #     result = indexer.series_indexer(0, [self.shared_mixed_series], verbatim_rests)[1]
    #     for i in self.shared_mixed_series.index:
    #         self.assertEqual(result[i], pandas.Series(['Rest', str(i)], index=[i, i]))


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

    # def test_multi_event_1(self): # Not necessary if only 1 steam is ever indexed at a time.
    #     # Test this:
    #     # offset:  0.0  |  0.5  |  1.0  |  1.5  |  2.0
    #     # part 1:  [0]  |  [1]  |  [2]  |  [3]  |  [4]
    #     # part 2:  [0]  |  [1]  |  [2]  |  [3]  |  [4]
    #     part_1 = stream.Stream()
    #     for i in range(5):
    #         obj = base.ElementWrapper(i)
    #         obj.offset = 0.5 * i
    #         obj.duration = duration.Duration(0.5)
    #         part_1.append(obj)
    #     part_2 = stream.Stream()
    #     for i in range(5):
    #         obj = base.ElementWrapper(i)
    #         obj.offset = 0.5 * i
    #         obj.duration = duration.Duration(0.5)
    #         part_2.append(obj)
    #     expected = pandas.Series({0.0: '(0, 0)', 0.5: '(1, 1)', 1.0: '(2, 2)',
    #                               1.5: '(3, 3)', 2.0: '(4, 4)'})
    #     actual = indexer.stream_indexer([part_1, part_2], verbatim)
    #     self.assertSequenceEqual(list(expected.index), list(actual.index))
    #     self.assertSequenceEqual(list(expected), list(actual))

    # def test_multi_event_2(self): # Not necessray if only one stream is ever indexed at a time.
    #     # Test this:
    #     # offset:  0.0  |  0.5     |  1.0     |  1.5     |  2.0
    #     # part 1:  [1]  |  [2][6]  |  [3]     |  [4][7]  |  [5][8]
    #     # part 2:  [1]  |  [2][6]  |  [3][7]  |  [4]     |  [5][8]
    #     part_1 = stream.Stream()
    #     for i in range(5):
    #         obj = base.ElementWrapper(i)
    #         obj.offset = 0.5 * i
    #         obj.duration = duration.Duration(0.5)
    #         part_1.append(obj)
    #     part_2 = stream.Stream()
    #     for i in range(5):
    #         obj = base.ElementWrapper(i)
    #         obj.offset = 0.5 * i
    #         obj.duration = duration.Duration(0.5)
    #         part_2.append(obj)
    #     add_these = [(part_1, 0.5, 6), (part_1, 1.5, 7), (part_1, 2.0, 8),
    #                  (part_2, 0.5, 6), (part_2, 1.0, 7), (part_2, 2.0, 8)]
    #     for part, offset, number in add_these:
    #         zed = base.ElementWrapper(number)
    #         zed.duration = duration.Duration(0.5)
    #         part.insert(offset, zed)
    #     expected = pandas.Series({0.0: '(0, 0)', 0.5: '(1, 1)', 1.0: '(2, 2)',
    #                               1.5: '(3, 3)', 2.0: '(4, 4)'})
    #     actual = indexer.stream_indexer([part_1, part_2], verbatim)
    #     self.assertSequenceEqual(list(expected.index), list(actual.index))
    #     self.assertSequenceEqual(list(expected), list(actual))

    # def test_multi_event_3(self): # It would be better to just handle 'chord' objects in the stream_indexer.
    #     ## offset:  0.0  |  0.5     |  1.0        |  1.5     |  2.0
    #     ## part 1:  [1]  |  [2][6]  |  [3][7][8]  |  [4][9]  |  [5][10][11]
    #     ## part 2:  [1]  |  [2][6]  |  [3][7]     |  [4]     |  [5]
    #     ## part 3:  [1]  |  [2][6]  |  [3][7]     |  [4][8]  |  [5][9]
    #     part_1 = stream.Stream()
    #     for i in range(5):
    #         obj = base.ElementWrapper(i)
    #         obj.offset = 0.5 * i
    #         obj.duration = duration.Duration(0.5)
    #         part_1.append(obj)

    #     add_these = [(part_1, 0.5, 6), (part_1, 1.0, 7), (part_1, 1.0, 8), (part_1, 1.5, 9),
    #                  (part_1, 2.0, 10), (part_1, 2.0, 11)]
    #     for part, offset, number in add_these:
    #         zed = base.ElementWrapper(number)
    #         zed.duration = duration.Duration(0.5)
    #         part.insert(offset, zed)
    #     expected = pandas.Series({0.0: '(0,)', 0.5: '(1,)', 1.0: '(2,)',
    #                               1.5: '(3,)', 2.0: '(4,)'})
    #     actual = indexer.stream_indexer([part_1], verbatim)
    #     self.assertSequenceEqual(list(expected.index), list(actual.index))
    #     self.assertSequenceEqual(list(expected), list(actual))


# class TestMpiUniqueOffsets(unittest.TestCase): # mpi_unique_offsets() is no longer called.
#     def test_mpi_unique_offsets_1(self):
#         streams = int_indexer_short.test_1()
#         expected = [0.0]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_2(self):
#         streams = int_indexer_short.test_2()
#         expected = [0.0, 0.25]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_3(self):
#         streams = int_indexer_short.test_3()
#         expected = [0.0, 0.25]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_4(self):
#         streams = int_indexer_short.test_4()
#         expected = [0.0, 0.25]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_5(self):
#         streams = int_indexer_short.test_5()
#         expected = [0.0, 0.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_6(self):
#         streams = int_indexer_short.test_6()
#         expected = [0.0, 0.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_7(self):
#         streams = int_indexer_short.test_7()
#         expected = [0.0, 0.5, 1.0, 1.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_8(self):
#         streams = int_indexer_short.test_8()
#         expected = [0.0, 0.25, 0.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_9(self):
#         streams = int_indexer_short.test_9()
#         expected = [0.0, 0.25, 0.5, 1.0]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_10(self):
#         streams = int_indexer_short.test_10()
#         expected = [0.0, 0.25]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_12(self):
#         streams = int_indexer_short.test_12()
#         expected = [0.0, 0.25, 0.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_13(self):
#         streams = int_indexer_short.test_13()
#         expected = [0.0, 0.125, 0.25, 0.375, 0.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_14(self):
#         streams = int_indexer_short.test_14()
#         expected = [0.0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_15(self):
#         streams = int_indexer_short.test_15()
#         expected = [0.0, 0.5, 0.75, 1.0, 1.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_16(self):
#         streams = int_indexer_short.test_16()
#         expected = [0.0, 0.5, 0.75, 1.25, 1.5]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)

#     def test_mpi_unique_offsets_17(self):
#         streams = int_indexer_short.test_17()
#         expected = [0.0, 0.5, 0.75, 1.125, 1.25, 1.375, 2.0]
#         actual = indexer.mpi_unique_offsets(streams)
#         self.assertSequenceEqual(expected, actual)


class TestMakeReturn(unittest.TestCase):
    def test_make_return_1(self):
        # 1: the usual case
        # prepare
        violini = pandas.Series([x for x in range(10)])
        violinii = pandas.Series([x + 10 for x in range(10)])
        viola = pandas.Series([x + 20 for x in range(10)])
        cello = pandas.Series([x + 30 for x in range(10)])
        names = ['Violin I', 'Violin II', 'Viola', 'Violoncello']
        parts = [violini, violinii, viola, cello]
        class QuartetIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        # run
        test_ind = QuartetIndexer(parts)
        actual = test_ind.make_return(names, parts)
        # check
        self.assertEqual('test_indexer.QuartetIndexer', actual.columns.levels[0][0])

    def test_make_return_2(self):
        # 2: more parts than names
        # prepare
        clarinet = pandas.Series([x for x in range(10)])
        tuba = pandas.Series([x + 10 for x in range(10)])
        names = ['Clarinet']
        parts = [clarinet, tuba]
        class SadIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        # run
        test_ind = SadIndexer(parts)
        self.assertRaises(IndexError, test_ind.make_return, names, parts)
        # check
        try:
            test_ind.make_return(names, parts)
        except IndexError as inderr:
            self.assertEqual(indexer.Indexer._MAKE_RETURN_INDEX_ERR, inderr.message)

    def test_make_return_3(self):
        # 3: more names than parts
        # prepare
        clarinet = pandas.Series([x for x in range(10)])
        #tuba = pandas.Series([x + 10 for x in range(10)])
        names = ['Clarinet', 'Tuba']
        parts = [clarinet]
        class SadIndexer(indexer.Indexer):
            required_score_type = 'pandas.Series'
        # run
        test_ind = SadIndexer(parts)
        self.assertRaises(IndexError, test_ind.make_return, names, parts)
        # check
        try:
            test_ind.make_return(names, parts)
        except IndexError as inderr:
            self.assertEqual(indexer.Indexer._MAKE_RETURN_INDEX_ERR, inderr.message)


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
INDEXER_1_PART_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerSinglePart)
INDEXER_MULTI_EVENT_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerMultiEvent)
# UNIQUE_OFFSETS_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMpiUniqueOffsets)
INDEXER_INIT_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestIndexerInit)
MAKE_RETURN_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMakeReturn)
