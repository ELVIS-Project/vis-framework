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
    # the fill_space_between_offsets() tests were taken from vis7
    def test_fill_space_between_offsets_1(self):
        in_1 = 0.0
        in_2 = 1.0
        expected = [1.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fill_space_between_offsets_2(self):
        in_1 = 0.0
        in_2 = 4.0
        expected = [4.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fill_space_between_offsets_3(self):
        in_1 = 0.0
        in_2 = 5.0
        expected = [4.0, 1.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fill_space_between_offsets_4(self):
        in_1 = 0.0
        in_2 = 8.0
        expected = [4.0, 4.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fill_space_between_offsets_5(self):
        in_1 = 0.0
        in_2 = 9.0
        expected = [4.0, 4.0, 1.0]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fill_space_between_offsets_6(self):
        in_1 = 4.5
        in_2 = 5.0
        expected = [0.5]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fill_space_between_offsets_7(self):
        in_1 = 7693.5
        in_2 = 7703.0
        expected = [4.0, 4.0, 1.0, 0.5]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fill_space_between_offsets_8(self):
        in_1 = 0.0
        in_2 = 3.96875
        expected = [2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_fill_space_between_offsets_9(self):
        in_1 = 3.96875
        in_2 = 7.9375
        expected = [2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
        actual = lilypond.PartNotesIndexer._fill_space_between_offsets(in_1, in_2)
        self.assertEqual(len(expected), len(actual))
        self.assertSequenceEqual(expected, actual)

    def test_set_durations_1(self):
        # when only one object is required (i.e., the notes are enough)
        # TODO: mock _fill_space_between_offsets()
        in_offsets = [0.0, 4.0]
        in_val = stream.Part([note.Note() for _ in xrange(len(in_offsets))])
        for i in xrange(len(in_offsets)):
            in_val[i].offset = in_offsets[i]
        expected = [(0.0, 4.0), (4.0, 1.0)]
        actual = lilypond.PartNotesIndexer._set_durations(in_val)
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)

    def test_set_durations_2(self):
        # when we must insert rests
        # TODO: mock _fill_space_between_offsets()
        in_offsets = [0.0, 3.0]
        in_val = stream.Part([note.Note() for _ in xrange(len(in_offsets))])
        for i in xrange(len(in_offsets)):
            in_val[i].offset = in_offsets[i]
        expected = [(0.0, 2.0), (2.0, 1.0), (3.0, 1.0)]
        actual = lilypond.PartNotesIndexer._set_durations(in_val)
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)

    def test_set_durations_3(self):
        # when we must insert rests
        # TODO: mock _fill_space_between_offsets()
        in_offsets = [0.0, 2.75]
        in_val = stream.Part([note.Note() for _ in xrange(len(in_offsets))])
        for i in xrange(len(in_offsets)):
            in_val[i].offset = in_offsets[i]
        expected = [(0.0, 2.0), (2.0, 0.5), (2.5, 0.25), (2.75, 1.0)]
        actual = lilypond.PartNotesIndexer._set_durations(in_val)
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)

    def test_set_durations_4(self):
        # when we must insert rests
        # TODO: mock _fill_space_between_offsets()
        in_offsets = [3.96875, 7.9375]
        in_val = stream.Part([note.Note() for _ in xrange(len(in_offsets))])
        for i in xrange(len(in_offsets)):
            in_val[i].offset = in_offsets[i]
        expected = [(3.96875, 2.0), (5.96875, 1.0), (6.96875, 0.5), (7.46875, 0.25),
                    (7.71875, 0.125), (7.84375, 0.0625), (7.90625, 0.03125), (7.9375, 1.0)]
        actual = lilypond.PartNotesIndexer._set_durations(in_val)
        self.assertEqual(len(expected), len(actual))
        for i, obj in enumerate(actual):
            self.assertEqual(expected[i][0], obj.offset)
            self.assertEqual(expected[i][1], obj.duration.quarterLength)

    def test_run_1(self):
        # test the whole thing! Oh my...
        # TODO: mock _set_durations()
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


class TestLilyPondIndexer(unittest.TestCase):
    pass


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
ANNOTATION_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestAnnotationIndexer)
ANNOTATE_NOTE_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestAnnotateTheNoteIndexer)
PART_NOTES_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPartNotesIndexer)
LILYPOND_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestLilyPondIndexer)
