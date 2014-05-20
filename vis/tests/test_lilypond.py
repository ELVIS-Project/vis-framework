#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_lilypond.py
# Purpose:                Tests for the "lilypond" indexer module.
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
import mock
import pandas
from music21 import note, stream
from vis.analyzers.indexers import lilypond


class TestAnnotationIndexer(unittest.TestCase):
    def test_ind_func_1(self):
        in_val = pandas.Series(['my shirt'])
        expected = u'_\\markup{ "my shirt" }'
        actual = lilypond.annotation_func(in_val)
        self.assertEqual(expected, actual)

    def test_ind_func_2(self):
        in_val = pandas.Series([42])
        expected = u'_\\markup{ "42" }'
        actual = lilypond.annotation_func(in_val)
        self.assertEqual(expected, actual)

    def test_class_1(self):
        in_val = [pandas.Series(['this', 'is']),
                  pandas.Series(['how', 'we']),
                  pandas.Series(['do', 'it']),
                  pandas.Series(['baby', 'yeah'])]
        expected = [pandas.Series(['_\\markup{ "this" }', '_\\markup{ "is" }']),
                    pandas.Series(['_\\markup{ "how" }', '_\\markup{ "we" }']),
                    pandas.Series(['_\\markup{ "do" }', '_\\markup{ "it" }']),
                    pandas.Series(['_\\markup{ "baby" }', '_\\markup{ "yeah" }'])]
        actual = lilypond.AnnotationIndexer(in_val).run()
        for i in xrange(len(expected)):
            self.assertSequenceEqual(list(expected[i].index), list(actual[i].index))
            self.assertSequenceEqual(list(expected[i]), list(actual[i]))


class TestAnnotateTheNoteIndexer(unittest.TestCase):
    def test_ind_func_1(self):
        in_val = pandas.Series([u'_\\markup{ "my shirt" }'])
        actual = lilypond.annotate_the_note(in_val)
        self.assertTrue(isinstance(actual, note.Note))
        self.assertTrue(hasattr(actual, u'lily_invisible'))
        self.assertTrue(hasattr(actual, u'lily_markup'))
        self.assertEqual(True, actual.lily_invisible)
        self.assertEqual(u'_\\markup{ "my shirt" }', actual.lily_markup)

    def test_class_1(self):
        annotes = [['_\\markup{ "this" }', '_\\markup{ "is" }'],
                   ['_\\markup{ "how" }', '_\\markup{ "we" }'],
                   ['_\\markup{ "do" }', '_\\markup{ "it" }'],
                   ['_\\markup{ "baby" }', '_\\markup{ "yeah" }']]
        in_val = [pandas.Series(l) for l in annotes]
        actual = lilypond.AnnotateTheNoteIndexer(in_val).run()
        for i, each_part in enumerate(actual):
            for j, each_note in enumerate(each_part):
                self.assertTrue(isinstance(each_note, note.Note))
                self.assertTrue(hasattr(each_note, u'lily_invisible'))
                self.assertTrue(hasattr(each_note, u'lily_markup'))
                self.assertEqual(True, each_note.lily_invisible)
                self.assertEqual(annotes[i][j], each_note.lily_markup)


class TestPartNotesIndexer(unittest.TestCase):
    # NB: this is to help mock this method later
    FSBO_PATH = u'vis.analyzers.indexers.lilypond.PartNotesIndexer._fill_space_between_offsets'
    # the fill_space_between_offsets() tests were taken from vis7
    def test_fsbo_1(self):
        # pylint: disable=W0212
        in_1 = 0.0
        in_2 = 1.0
        expected = [1.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fsbo_2(self):
        # pylint: disable=W0212
        in_1 = 0.0
        in_2 = 4.0
        expected = [4.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fsbo_3(self):
        # pylint: disable=W0212
        in_1 = 0.0
        in_2 = 5.0
        expected = [4.0, 1.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fsbo_4(self):
        # pylint: disable=W0212
        in_1 = 0.0
        in_2 = 8.0
        expected = [4.0, 4.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fsbo_5(self):
        # pylint: disable=W0212
        in_1 = 0.0
        in_2 = 9.0
        expected = [4.0, 4.0, 1.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fsbo_6(self):
        # pylint: disable=W0212
        in_1 = 4.5
        in_2 = 5.0
        expected = [0.5]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fsbo_7(self):
        # pylint: disable=W0212
        in_1 = 7693.5
        in_2 = 7703.0
        expected = [4.0, 4.0, 1.0, 0.5]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fsbo_8(self):
        # pylint: disable=W0212
        in_1 = 0.0
        in_2 = 3.96875
        expected = [2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fsbo_9(self):
        # pylint: disable=W0212
        in_1 = 3.96875
        in_2 = 7.9375
        expected = [2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_set_durations_1(self):
        # when only one object is required (i.e., the notes are enough)
        # --> has lily_analysis_voice
        in_offsets = [0.0, 4.0]
        in_val = stream.Part([note.Note() for _ in xrange(len(in_offsets))])
        for i in xrange(len(in_offsets)):
            in_val[i].offset = in_offsets[i]
        in_val.lily_analysis_voice = 42
        expected = [(0.0, 4.0), (4.0, 1.0)]
        with mock.patch(TestPartNotesIndexer.FSBO_PATH) as mock_fsbo:
            mock_fsbo.side_effect = [[4.0]]
            actual = lilypond.PartNotesIndexer._set_durations(in_val)  # pylint: disable=W0212
            self.assertEqual(len(in_offsets) - 1, mock_fsbo.call_count)
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)
        self.assertEqual(in_val.lily_analysis_voice, actual.lily_analysis_voice)
        self.assertFalse(hasattr(actual, u'lily_instruction'))

    def test_set_durations_2(self):
        # when we must insert rests
        # --> has lily_instruction
        in_offsets = [0.0, 3.0]
        in_val = stream.Part([note.Note() for _ in xrange(len(in_offsets))])
        for i in xrange(len(in_offsets)):
            in_val[i].offset = in_offsets[i]
        in_val.lily_instruction = 66
        expected = [(0.0, 2.0), (2.0, 1.0), (3.0, 1.0)]
        with mock.patch(TestPartNotesIndexer.FSBO_PATH) as mock_fsbo:
            mock_fsbo.side_effect = [[2.0, 1.0]]
            actual = lilypond.PartNotesIndexer._set_durations(in_val)  # pylint: disable=W0212
            self.assertEqual(len(in_offsets) - 1, mock_fsbo.call_count)
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)
        self.assertEqual(in_val.lily_instruction, actual.lily_instruction)
        self.assertFalse(hasattr(actual, u'lily_analysis_voice'))

    def test_set_durations_3(self):
        # when we must insert rests
        # --> both lily_instruction and lily_analysis_voice
        in_offsets = [0.0, 2.75]
        in_val = stream.Part([note.Note() for _ in xrange(len(in_offsets))])
        for i in xrange(len(in_offsets)):
            in_val[i].offset = in_offsets[i]
        in_val.lily_analysis_voice = 42
        in_val.lily_instruction = 66
        expected = [(0.0, 2.0), (2.0, 0.5), (2.5, 0.25), (2.75, 1.0)]
        with mock.patch(TestPartNotesIndexer.FSBO_PATH) as mock_fsbo:
            mock_fsbo.side_effect = [[2.0, 0.5, 0.25]]
            actual = lilypond.PartNotesIndexer._set_durations(in_val)  # pylint: disable=W0212
            self.assertEqual(len(in_offsets) - 1, mock_fsbo.call_count)
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)
        self.assertEqual(in_val.lily_instruction, actual.lily_instruction)
        self.assertEqual(in_val.lily_analysis_voice, actual.lily_analysis_voice)

    def test_set_durations_4(self):
        # when we must insert rests
        # --> neither lily_analysis_voice nor lily_instruction
        in_offsets = [3.96875, 7.9375]
        in_val = stream.Part([note.Note() for _ in xrange(len(in_offsets))])
        for i in xrange(len(in_offsets)):
            in_val[i].offset = in_offsets[i]
        expected = [(3.96875, 2.0), (5.96875, 1.0), (6.96875, 0.5), (7.46875, 0.25),
                    (7.71875, 0.125), (7.84375, 0.0625), (7.90625, 0.03125), (7.9375, 1.0)]
        with mock.patch(TestPartNotesIndexer.FSBO_PATH) as mock_fsbo:
            mock_fsbo.side_effect = [[2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]]
            actual = lilypond.PartNotesIndexer._set_durations(in_val)  # pylint: disable=W0212
            self.assertEqual(len(in_offsets) - 1, mock_fsbo.call_count)
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)
        self.assertFalse(hasattr(actual, u'lily_analysis_voice'))
        self.assertFalse(hasattr(actual, u'lily_instruction'))

    def test_run_1(self):
        # test the whole thing! Oh my... kind of an integration test
        markups = [u'_\\markup{ "Réduire" }', u'_\\markup{ "l\'endettement" }']
        in_val = []
        for i in xrange(len(markups)):
            obj = note.Note('C4')
            obj.lily_invisible = True
            obj.lily_markup = markups[i]
            in_val.append(obj)
        in_val = [pandas.Series(in_val, index=[0.0, 2.75])]
        expected = [(0.0, 2.0), (2.0, 0.5), (2.5, 0.25), (2.75, 1.0)]
        actual = lilypond.PartNotesIndexer(in_val).run()[0]
        # Verify...
        # ... that the result is a Part with the proper LilyPond attributes
        self.assertTrue(isinstance(actual, stream.Part))
        self.assertTrue(hasattr(actual, 'lily_analysis_voice'))
        self.assertEqual(True, actual.lily_analysis_voice)
        self.assertTrue(hasattr(actual, 'lily_instruction'))
        self.assertEqual(u'\t\\textLengthOn\n', actual.lily_instruction)
        # ... that the objects have the right offsets and durations
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)
        # ... that the objects are of the right types
        for i in [0, 3]:
            self.assertTrue(actual[i], note.Note)
        for i in [1, 2]:
            self.assertTrue(actual[i], note.Rest)

    def test_run_2(self):
        # same as test_run_1(), but with a 'part_names' setting
        markups = [u'_\\markup{ "Réduire" }', u'_\\markup{ "l\'endettement" }']
        #u'\t\\textLengthOn\n\t\\set Staff.instrumentName = "the name"\n'
        in_val = []
        for i in xrange(len(markups)):
            obj = note.Note('C4')
            obj.lily_invisible = True
            obj.lily_markup = markups[i]
            in_val.append(obj)
        in_val = [pandas.Series(in_val, index=[0.0, 2.75])]
        setts = {'part_names': ['the name']}
        expected = [(0.0, 2.0), (2.0, 0.5), (2.5, 0.25), (2.75, 1.0)]
        actual = lilypond.PartNotesIndexer(in_val, setts).run()[0]
        # Verify...
        # ... that the result is a Part with the proper LilyPond attributes
        self.assertTrue(isinstance(actual, stream.Part))
        self.assertTrue(hasattr(actual, 'lily_analysis_voice'))
        self.assertEqual(True, actual.lily_analysis_voice)
        self.assertTrue(hasattr(actual, 'lily_instruction'))
        self.assertEqual(u'\t\\textLengthOn\n'
                         u'\t\\set Staff.instrumentName = "the name"\n'
                         u'\t\\set Staff.shortInstrumentName = "the name"\n', actual.lily_instruction)
        # ... that the objects have the right offsets and durations
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)
        # ... that the objects are of the right types
        for i in [0, 3]:
            self.assertTrue(actual[i], note.Note)
        for i in [1, 2]:
            self.assertTrue(actual[i], note.Rest)

    def test_prepend_rests_1(self):
        # simple: add one thing in front of one other thing
        in_val = pandas.Series(['first'], index=[2.0])
        expected = pandas.Series([note.Rest(quarterLength=2.0), 'first'], index=[0.0, 2.0])
        actual = lilypond.PartNotesIndexer._prepend_rests(in_val)  # pylint: disable=protected-access
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_prepend_rests_2(self):
        # simple: everything's already right
        in_val = pandas.Series(['first'], index=[0.0])
        expected = pandas.Series(['first'], index=[0.0])
        actual = lilypond.PartNotesIndexer._prepend_rests(in_val)  # pylint: disable=protected-access
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_prepend_rests_3(self):
        # complexer: everything's already right
        in_val = pandas.Series(['first', 'second', 'third', 'fourth'],
                               index=[0.0, 0.25, 400.369, 1024.1024])
        expected = pandas.Series(['first', 'second', 'third', 'fourth'],
                                 index=[0.0, 0.25, 400.369, 1024.1024])
        actual = lilypond.PartNotesIndexer._prepend_rests(in_val)  # pylint: disable=protected-access
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_prepend_rests_4(self):
        # complexer: add two things in front of one other thing
        in_val = pandas.Series(['first'], index=[6.0])
        expected = pandas.Series([note.Rest(quarterLength=4.0), note.Rest(quarterLength=2.0), 'first'],
                                 index=[0.0, 4.0, 6.0])
        actual = lilypond.PartNotesIndexer._prepend_rests(in_val)  # pylint: disable=protected-access
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_prepend_rests_5(self):
        # complexer: add three things in front of one other thing
        in_val = pandas.Series(['first'], index=[7.0])
        expected = pandas.Series([note.Rest(quarterLength=4.0),
                                  note.Rest(quarterLength=2.0),
                                  note.Rest(quarterLength=1.0),
                                  'first'],
                                 index=[0.0, 4.0, 6.0, 7.0])
        actual = lilypond.PartNotesIndexer._prepend_rests(in_val)  # pylint: disable=protected-access
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))

    def test_prepend_rests_6(self):
        # complexest: add three things in front of four other things
        in_val = pandas.Series(['first', 'second', 'third', 'fourth'],
                               index=[7.0, 7.25, 400.369, 1024.1024])
        expected = pandas.Series([note.Rest(quarterLength=4.0),
                                  note.Rest(quarterLength=2.0),
                                  note.Rest(quarterLength=1.0),
                                  'first',
                                  'second',
                                  'third',
                                  'fourth'],
                                 index=[0.0, 4.0, 6.0, 7.0, 7.25, 400.369, 1024.1024])
        actual = lilypond.PartNotesIndexer._prepend_rests(in_val)  # pylint: disable=protected-access
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected.values), list(actual.values))


class TestLilyPondIndexer(unittest.TestCase):
    @mock.patch('vis.analyzers.indexer.Indexer.__init__', new=lambda x, y, z: None)
    def test_init_1(self):
        # output_pathname unspecified; run lily (RuntimeError)
        setts = {u'run_lilypond': True}
        self.assertRaises(RuntimeError, lilypond.LilyPondIndexer, 12, setts)

    @mock.patch('vis.analyzers.indexer.Indexer.__init__', new=lambda x, y, z: None)
    def test_init_2(self):
        # output_pathname unspecified; don't run lily; have annotation part
        setts = {u'run_lilypond': False, u'annotation_part': 42}
        expected = {u'run_lilypond': False, u'annotation_part': [42], u'output_pathname': None}
        actual = lilypond.LilyPondIndexer(12, setts)
        self.assertEqual(expected, actual._settings)  # pylint: disable=W0212

    @mock.patch('vis.analyzers.indexer.Indexer.__init__', new=lambda x, y, z: None)
    def test_init_3(self):
        # output_pathname specified; run lily; no annotation part
        setts = {u'run_lilypond': True, u'output_pathname': u'PATH!'}
        expected = {u'run_lilypond': True, u'annotation_part': None, u'output_pathname': u'PATH!'}
        actual = lilypond.LilyPondIndexer(12, setts)
        self.assertEqual(expected, actual._settings)  # pylint: disable=W0212

    @mock.patch('vis.analyzers.indexer.Indexer.__init__', new=lambda x, y, z: None)
    def test_init_4(self):
        # output_pathname specified; don't run lily; two annotation parts
        setts = {u'run_lilypond': False, u'output_pathname': u'PATH!', u'annotation_part': [42, 52]}
        exp_setts = {u'run_lilypond': False, u'annotation_part': [42, 52], u'output_pathname': u'PATH!'}
        actual = lilypond.LilyPondIndexer(12, setts)
        self.assertEqual(exp_setts, actual._settings)  # pylint: disable=W0212

    def test_run_1(self):
        # with annotation_part; without output_pathname; not run_lilypond
        # prepare mocks
        mock_open = mock.mock_open()
        mock_score_cls = type('MockIndexer', (stream.Score,), {})
        mock_score = mock_score_cls()
        mock_score.insert = mock.MagicMock()
        mock_part = mock.MagicMock(spec_set=stream.Part)
        setts = {u'annotation_part': mock_part}
        oly_setts = mock.MagicMock()
        expected = mock.MagicMock(spec_set=unicode)
        run_ly = mock.MagicMock()
        # run test
        with mock.patch('vis.analyzers.indexers.lilypond.outputlilypond') as mock_oly:
            mock_oly.process_score.return_value = expected
            mock_oly.run_lilypond = run_ly
            with mock.patch('vis.analyzers.indexers.lilypond.oly_settings') as mock_oly_s:
                mock_oly_s.LilyPondSettings.return_value = oly_setts
                with mock.patch('__builtin__.open', mock_open):
                    actual = lilypond.LilyPondIndexer([mock_score], setts).run()
        # verify results
            mock_oly.process_score.assert_called_once_with(mock_score, oly_setts)
        self.assertEqual(0, mock_open.call_count)
        self.assertEqual(0, run_ly.call_count)
        mock_score.insert.assert_called_once_with(0, mock_part)
        self.assertEqual(expected, actual)

    def test_run_2(self):
        # without annotation_part; with output_pathname; do run_lilypond
        # prepare mocks
        mock_open = mock.mock_open()
        mock_score_cls = type('MockIndexer', (stream.Score,), {})
        mock_score = mock_score_cls()
        mock_score.insert = mock.MagicMock()
        setts = {u'run_lilypond': True, u'output_pathname': u'PATH!'}
        oly_setts = mock.MagicMock()
        expected = mock.MagicMock(spec_set=unicode)
        run_ly = mock.MagicMock()
        # run test
        with mock.patch('vis.analyzers.indexers.lilypond.outputlilypond') as mock_oly:
            mock_oly.process_score.return_value = expected
            mock_oly.run_lilypond = run_ly
            with mock.patch('vis.analyzers.indexers.lilypond.oly_settings') as mock_oly_s:
                mock_oly_s.LilyPondSettings.return_value = oly_setts
                with mock.patch('__builtin__.open', mock_open):
                    actual = lilypond.LilyPondIndexer([mock_score], setts).run()
        # verify results
            mock_oly.process_score.assert_called_once_with(mock_score, oly_setts)
        mock_open.assert_called_once_with(setts[u'output_pathname'], 'w')
        run_ly.assert_called_once_with(setts[u'output_pathname'], oly_setts)
        self.assertEqual(0, mock_score.insert.call_count)
        self.assertEqual(expected, actual)

    def test_run_3(self):
        # with many annotation_parts; without output_pathname; not run_lilypond
        # prepare mocks
        mock_open = mock.mock_open()
        mock_score_cls = type('MockIndexer', (stream.Score,), {})
        mock_score = mock_score_cls()
        mock_score.insert = mock.MagicMock()
        mock_parts = [mock.MagicMock(name=u'anno part 1', spec_set=stream.Part),
                      mock.MagicMock(name=u'anno part 2', spec_set=stream.Part)]
        setts = {u'annotation_part': mock_parts}
        oly_setts = mock.MagicMock()
        expected = mock.MagicMock(spec_set=unicode)
        run_ly = mock.MagicMock()
        # run test
        with mock.patch('vis.analyzers.indexers.lilypond.outputlilypond') as mock_oly:
            mock_oly.process_score.return_value = expected
            mock_oly.run_lilypond = run_ly
            with mock.patch('vis.analyzers.indexers.lilypond.oly_settings') as mock_oly_s:
                mock_oly_s.LilyPondSettings.return_value = oly_setts
                with mock.patch('__builtin__.open', mock_open):
                    actual = lilypond.LilyPondIndexer([mock_score], setts).run()
        # verify results
            mock_oly.process_score.assert_called_once_with(mock_score, oly_setts)
        self.assertEqual(0, mock_open.call_count)
        self.assertEqual(0, run_ly.call_count)
        self.assertEqual(len(mock_parts), mock_score.insert.call_count)
        for mock_part in mock_parts:
            mock_score.insert.assert_any_call(0, mock_part)
        self.assertEqual(expected, actual)


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
ANNOTATION_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestAnnotationIndexer)
ANNOTATE_NOTE_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestAnnotateTheNoteIndexer)
PART_NOTES_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPartNotesIndexer)
LILYPOND_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestLilyPondIndexer)
