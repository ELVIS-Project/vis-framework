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

import unittest
from music21 import interval, note, chord
from models.ngram import IntervalNGram, ChordNGram


class TestIntervalNGram(unittest.TestCase):
    def setUp(self):
        # 'm3 P1 m3'
        self.a = [interval.Interval(note.Note('A4'), note.Note('C5')),
                  interval.Interval(note.Note('A4'), note.Note('C5'))]
        self.a_distance = [interval.Interval(note.Note('A4'), note.Note('A4'))]
        # 'm3 P1 M3'
        self.b = [interval.Interval(note.Note('A4'), note.Note('C5')),
                  interval.Interval(note.Note('A4'), note.Note('C#5'))]
        self.b_distance = [interval.Interval(note.Note('A4'), note.Note('A4'))]
        # 'm3 +P4 m3'
        self.c = [interval.Interval(note.Note('A4'), note.Note('C5')),
                  interval.Interval(note.Note('D5'), note.Note('F5'))]
        self.c_distance = [interval.Interval(note.Note('A4'), note.Note('D5'))]
        # 'm-3 +M2 M3'
        self.d = [interval.Interval(note.Note('C5'), note.Note('A4')),
                  interval.Interval(note.Note('D5'), note.Note('F#5'))]
        self.d_distance = [interval.Interval(note.Note('C5'), note.Note('D5'))]
        # 'm3 -P4 m3'
        self.e = [interval.Interval(note.Note('A4'), note.Note('C5')),
                  interval.Interval(note.Note('E4'), note.Note('G4'))]
        self.e_distance = [interval.Interval(note.Note('A4'), note.Note('E4'))]
        # 'm3 -m2 M-3'
        self.f = [interval.Interval(note.Note('A4'), note.Note('C5')),
                  interval.Interval(note.Note('G#4'), note.Note('E4'))]
        self.f_distance = [interval.Interval(note.Note('A4'), note.Note('G#4'))]
        # 'm3 +P4 M2 -m6 P5 +A9 M-10'
        self.g = [interval.Interval(note.Note('A4'), note.Note('C5')),
                  interval.Interval(note.Note('D5'), note.Note('E5')),
                  interval.Interval(note.Note('F#4'), note.Note('C#5')),
                  interval.Interval(note.Note('G##5'), note.Note('E#4'))]
        self.g_distance = [interval.Interval(note.Note('A4'), note.Note('D5')),
                           interval.Interval(note.Note('D5'), note.Note('F#4')),
                           interval.Interval(note.Note('F#4'), note.Note('G##5'))]
    # end set_up()

    def test_calculating_n(self):
        x = IntervalNGram(self.a)
        self.assertEqual(x.n(), 2)
        self.assertEqual(x._n, 2)
        y = IntervalNGram(self.g)
        self.assertEqual(y.n(), 4)
        self.assertEqual(y._n, 4)

    def test_constructor_assignment_1(self):
        # We have to make sure the settings are properly set, and that it works
        # for n-grams of multiple sizes/lengths.
        x = IntervalNGram(self.a)
        self.assertEqual(x._list_of_events, self.a)

    def test_constructor_assignment_2(self):
        # We have to make sure the settings are properly set, and that it works
        # for n-grams of multiple sizes/lengths.
        x = IntervalNGram(self.a)
        self.assertEqual(x._list_of_events, self.a)

    def test_constructor_assignment_3(self):
        # We have to make sure the settings are properly set, and that it works
        # for n-grams of multiple sizes/lengths.
        y = IntervalNGram(self.g)
        self.assertEqual(y._list_of_events, self.g)

    def test_constructor_assignment_4(self):
        # We have to make sure the settings are properly set, and that it works
        # for n-grams of multiple sizes/lengths.
        y = IntervalNGram(self.g)
        self.assertEqual(y._list_of_events, self.g)

    def test_distance_calculations(self):
        self.assertEqual(IntervalNGram(self.a)._list_of_connections, self.a_distance)
        self.assertEqual(IntervalNGram(self.b)._list_of_connections, self.b_distance)
        self.assertEqual(IntervalNGram(self.c)._list_of_connections, self.c_distance)
        self.assertEqual(IntervalNGram(self.d)._list_of_connections, self.d_distance)
        self.assertEqual(IntervalNGram(self.e)._list_of_connections, self.e_distance)
        self.assertEqual(IntervalNGram(self.f)._list_of_connections, self.f_distance)
        self.assertEqual(IntervalNGram(self.g)._list_of_connections, self.g_distance)

    def test_distance_calc_exception(self):
        self.temp = [interval.Interval(note.Note('A4'), note.Note('C5')),
                    interval.Interval('m3')]
        self.assertRaises(RuntimeError, IntervalNGram, self.temp)
        # Note that if we do this with
        # >>> self.g[2].noteEnd = None
        # then everything is okay because we only use the .noteStart to calculate
        # movement of the lower voice.
        try:
            self.g[2].noteEnd = None
        except AttributeError:
            pass
        self.assertEqual(IntervalNGram(self.g)._list_of_connections, self.g_distance)
        # But this should fail
        try:
            self.g[2].noteStart = None
        except AttributeError:
            pass
        self.assertRaises(RuntimeError, IntervalNGram, self.g)

    def test_equality_2(self):
        # if they aren't of the same "n, " they're not the same
        self.assertFalse(IntervalNGram(self.a) == IntervalNGram(self.g))
        self.assertFalse(IntervalNGram(self.a) == IntervalNGram(self.g))

    def test_equality_3(self):
        # they're all equal to themselves
        self.assertTrue(IntervalNGram(self.a) == IntervalNGram(self.a))
        self.assertTrue(IntervalNGram(self.b) == IntervalNGram(self.b))
        self.assertTrue(IntervalNGram(self.c) == IntervalNGram(self.c))
        self.assertTrue(IntervalNGram(self.d) == IntervalNGram(self.d))
        self.assertTrue(IntervalNGram(self.e) == IntervalNGram(self.e))
        self.assertTrue(IntervalNGram(self.f) == IntervalNGram(self.f))
        self.assertTrue(IntervalNGram(self.g) == IntervalNGram(self.g))

    def test_inequality_2(self):
        # if they aren't of the same "n, " they're not the same
        self.assertTrue(IntervalNGram(self.a) != IntervalNGram(self.g))

    def test_inequality_3(self):
        # they're all equal to themselves
        self.assertFalse(IntervalNGram(self.a) != IntervalNGram(self.a))
        self.assertFalse(IntervalNGram(self.b) != IntervalNGram(self.b))
        self.assertFalse(IntervalNGram(self.c) != IntervalNGram(self.c))
        self.assertFalse(IntervalNGram(self.d) != IntervalNGram(self.d))
        self.assertFalse(IntervalNGram(self.e) != IntervalNGram(self.e))
        self.assertFalse(IntervalNGram(self.f) != IntervalNGram(self.f))
        self.assertFalse(IntervalNGram(self.g) != IntervalNGram(self.g))

    def test_str_1(self):
        def run_test(with_this):
            return IntervalNGram(with_this).get_string_version(True, 'compound')
        self.assertEqual(run_test(self.a), 'm3 P1 m3')
        self.assertEqual(run_test(self.b), 'm3 P1 M3')
        self.assertEqual(run_test(self.c), 'm3 +P4 m3')
        self.assertEqual(run_test(self.d), 'm-3 +M2 M3')
        self.assertEqual(run_test(self.e), 'm3 -P4 m3')
        self.assertEqual(run_test(self.f), 'm3 -m2 M-3')
        self.assertEqual(run_test(self.g), 'm3 +P4 M2 -m6 P5 +A9 M-10')

    def test_str_2(self):
        def run_test(with_this):
            return IntervalNGram(with_this).get_string_version(False, 'compound')
        self.assertEqual(run_test(self.a), '3 1 3')
        self.assertEqual(run_test(self.b), '3 1 3')
        self.assertEqual(run_test(self.c), '3 +4 3')
        self.assertEqual(run_test(self.d), '-3 +2 3')
        self.assertEqual(run_test(self.e), '3 -4 3')
        self.assertEqual(run_test(self.f), '3 -2 -3')
        self.assertEqual(run_test(self.g), '3 +4 2 -6 5 +9 -10')

    def test_string_version_1(self):
        def run_test(with_this):
            return IntervalNGram(with_this).get_string_version(True, 'compound')
        self.assertEqual(run_test(self.a), 'm3 P1 m3')
        self.assertEqual(run_test(self.b), 'm3 P1 M3')
        self.assertEqual(run_test(self.c), 'm3 +P4 m3')
        self.assertEqual(run_test(self.d), 'm-3 +M2 M3')
        self.assertEqual(run_test(self.e), 'm3 -P4 m3')
        self.assertEqual(run_test(self.f), 'm3 -m2 M-3')
        self.assertEqual(run_test(self.g), 'm3 +P4 M2 -m6 P5 +A9 M-10')

    def test_string_version_2(self):
        def run_test(with_this):
            return IntervalNGram(with_this).get_string_version(True, 'simple')
        self.assertEqual(run_test(self.a), 'm3 P1 m3')
        self.assertEqual(run_test(self.b), 'm3 P1 M3')
        self.assertEqual(run_test(self.c), 'm3 +P4 m3')
        self.assertEqual(run_test(self.d), 'm-3 +M2 M3')
        self.assertEqual(run_test(self.e), 'm3 -P4 m3')
        self.assertEqual(run_test(self.f), 'm3 -m2 M-3')
        self.assertEqual(run_test(self.g), 'm3 +P4 M2 -m6 P5 +A2 M-3')

    def test_string_version_3(self):
        def run_test(with_this):
            return IntervalNGram(with_this).get_string_version(False, 'compound')
        self.assertEqual(run_test(self.a), '3 1 3')
        self.assertEqual(run_test(self.b), '3 1 3')
        self.assertEqual(run_test(self.c), '3 +4 3')
        self.assertEqual(run_test(self.d), '-3 +2 3')
        self.assertEqual(run_test(self.e), '3 -4 3')
        self.assertEqual(run_test(self.f), '3 -2 -3')
        self.assertEqual(run_test(self.g), '3 +4 2 -6 5 +9 -10')

    def test_string_version_4(self):
        def run_test(with_this):
            return IntervalNGram(with_this).get_string_version(False, 'simple')
        self.assertEqual(run_test(self.a), '3 1 3')
        self.assertEqual(run_test(self.b), '3 1 3')
        self.assertEqual(run_test(self.c), '3 +4 3')
        self.assertEqual(run_test(self.d), '-3 +2 3')
        self.assertEqual(run_test(self.e), '3 -4 3')
        self.assertEqual(run_test(self.f), '3 -2 -3')
        self.assertEqual(run_test(self.g), '3 +4 2 -6 5 +2 -3')

    def test_string_version_5(self):
        # This test ensure you don't get something like '7 1 6 -2 1' when you choose "simple" when
        # it should instead be '7 1 6 -2 8'.
        intervs = [interval.Interval(note.Note('C4'), note.Note('B4')),
                    interval.Interval(note.Note('C4'), note.Note('A4')),
                    interval.Interval(note.Note('B-3'), note.Note('B-4'))]
        tester = IntervalNGram(intervs)
        self.assertEqual(tester.get_string_version(False, 'simple'), '7 1 6 -2 8')
        self.assertEqual(tester.get_string_version(True, 'simple'), 'M7 P1 M6 -M2 P8')
        self.assertEqual(tester.get_string_version(False, 'compound'), '7 1 6 -2 8')
        self.assertEqual(tester.get_string_version(True, 'compound'), 'M7 P1 M6 -M2 P8')

    def test_repr_1(self):
        exp = "IntervalNGram([Interval(Note('A4'), Note('C5')), Interval(Note('A4'), Note('C5'))])"
        self.assertEqual(IntervalNGram(self.a).__repr__(), exp)

    def test_repr_2(self):
        exp = "IntervalNGram([Interval(Note('A4'), Note('C5')), Interval(Note('A4'), Note('C#5'))])"
        self.assertEqual(IntervalNGram(self.b).__repr__(), exp)

    def test_voice_crossing_1(self):
        self.assertFalse(IntervalNGram(self.a).voice_crossing())

    def test_voice_crossing_2(self):
        self.assertFalse(IntervalNGram(self.b).voice_crossing())

    def test_voice_crossing_3(self):
        self.assertTrue(IntervalNGram(self.f).voice_crossing())

    def test_voice_crossing_4(self):
        self.assertTrue(IntervalNGram(self.g).voice_crossing())

    def test_retrograde_1(self):
        self.assertEqual(IntervalNGram(self.a).retrograde(),
                        IntervalNGram(self.a))

    def test_retrograde_2(self):
        self.assertEqual(IntervalNGram(self.b).retrograde(),
                         IntervalNGram([interval.Interval(note.Note('A4'), note.Note('C#5')),
                                        interval.Interval(note.Note('A4'), note.Note('C5'))]))

    def test_retrograde_3(self):
        self.assertEqual(IntervalNGram(self.c).retrograde(),
                         IntervalNGram([interval.Interval(note.Note('D5'), note.Note('F5')),
                                        interval.Interval(note.Note('A4'), note.Note('C5'))]))

    def test_retrograde_4(self):
        self.assertEqual(IntervalNGram(self.d).retrograde(),
                         IntervalNGram([interval.Interval(note.Note('D5'), note.Note('F#5')),
                                        interval.Interval(note.Note('C5'), note.Note('A4'))]))

    def test_retrograde_5(self):
        self.assertEqual(IntervalNGram(self.e).retrograde(),
                         IntervalNGram([interval.Interval(note.Note('E4'), note.Note('G4')),
                                        interval.Interval(note.Note('A4'), note.Note('C5'))]))

    def test_retrograde_6(self):
        self.assertEqual(IntervalNGram(self.f).retrograde(),
                         IntervalNGram([interval.Interval(note.Note('G#4'), note.Note('E4')),
                                        interval.Interval(note.Note('A4'), note.Note('C5'))]))

    def test_retrograde_7(self):
        self.assertEqual(IntervalNGram(self.g).retrograde(),
                         IntervalNGram([interval.Interval(note.Note('G##5'), note.Note('E#4')),
                                        interval.Interval(note.Note('F#4'), note.Note('C#5')),
                                        interval.Interval(note.Note('D5'), note.Note('E5')),
                                        interval.Interval(note.Note('A4'), note.Note('C5'))]))

    def test_canonical_1(self):
        # m-3 +M2 M3
        actual = IntervalNGram(self.d)
        self.assertEqual(actual.canonical(True, 'compound'), 'm3 +M2 M3')
        self.assertEqual(actual.canonical(True, 'simple'), 'm3 +M2 M3')
        self.assertEqual(actual.canonical(False, 'compound'), '3 +2 3')
        self.assertEqual(actual.canonical(False, 'simple'), '3 +2 3')

    def test_canonical_2(self):
        # m3 -P4 m3
        actual = IntervalNGram(self.e)
        self.assertEqual(actual.canonical(True, 'compound'), 'm3 -P4 m3')
        self.assertEqual(actual.canonical(True, 'simple'), 'm3 -P4 m3')
        self.assertEqual(actual.canonical(False, 'compound'), '3 -4 3')
        self.assertEqual(actual.canonical(False, 'simple'), '3 -4 3')

    def test_canonical_3(self):
        # m3 -P4 M-3
        actual = IntervalNGram(self.f)
        self.assertEqual(actual.canonical(True, 'compound'), 'm3 -m2 M3')
        self.assertEqual(actual.canonical(True, 'simple'), 'm3 -m2 M3')
        self.assertEqual(actual.canonical(False, 'compound'), '3 -2 3')
        self.assertEqual(actual.canonical(False, 'simple'), '3 -2 3')

    def test_canonical_4(self):
        # m3 +P4 M2 -m6 P5 -m2 M-10
        actual = IntervalNGram(self.g)
        self.assertEqual(actual.canonical(True, 'compound'), 'm3 +P4 M2 -m6 P5 +A9 M10')
        self.assertEqual(actual.canonical(True, 'simple'), 'm3 +P4 M2 -m6 P5 +A2 M3')
        self.assertEqual(actual.canonical(False, 'compound'), '3 +4 2 -6 5 +9 10')
        self.assertEqual(actual.canonical(False, 'simple'), '3 +4 2 -6 5 +2 3')

    def test_inversion_1(self):
        # m3 M+2 P4 ==(12/up)==> M-10 +M2 M-9
        i1 = interval.Interval(note.Note('A4'), note.Note('C5'))
        i2 = interval.Interval(note.Note('B4'), note.Note('E5'))
        ng = IntervalNGram([i1, i2])
        inv_ng = ng.get_inversion_at_the(12, 'up')
        self.assertEqual(inv_ng.get_string_version(True, 'compound'), 'M-10 +M2 M-9')
        self.assertEqual(inv_ng._list_of_events[0].noteStart.nameWithOctave, 'E6')
        self.assertEqual(inv_ng._list_of_events[0].noteEnd.nameWithOctave, 'C5')
        self.assertEqual(inv_ng._list_of_events[1].noteStart.nameWithOctave, 'F#6')
        self.assertEqual(inv_ng._list_of_events[1].noteEnd.nameWithOctave, 'E5')

    def test_inversion_2(self):
        # m3 M+2 P4 ==(12/down)==> M-10 +M2 M-9
        i1 = interval.Interval(note.Note('A4'), note.Note('C5'))
        i2 = interval.Interval(note.Note('B4'), note.Note('E5'))
        ng = IntervalNGram([i1, i2])
        inv_ng = ng.get_inversion_at_the(12, 'down')
        self.assertEqual(inv_ng.get_string_version(True, 'compound'), 'M-10 +M2 M-9')
        self.assertEqual(inv_ng._list_of_events[0].noteStart.nameWithOctave, 'A4')
        self.assertEqual(inv_ng._list_of_events[0].noteEnd.nameWithOctave, 'F3')
        self.assertEqual(inv_ng._list_of_events[1].noteStart.nameWithOctave, 'B4')
        self.assertEqual(inv_ng._list_of_events[1].noteEnd.nameWithOctave, 'A3')

    def test_make_from_str_1(self):
        # Does it work in general?
        # a : 'm3 P1 m3'
        str_ng = IntervalNGram.make_from_str('m3 P1 m3')
        orig_ng = IntervalNGram(self.a)
        self.assertEqual(str_ng._list_of_events, orig_ng._list_of_events)
        self.assertEqual(str_ng._list_of_connections, orig_ng._list_of_connections)

    def test_make_from_str_2(self):
        # Does it work in general?
        # c : 'm3 +P4 m3'
        str_ng = IntervalNGram.make_from_str('m3 +P4 m3')
        orig_ng = IntervalNGram(self.c)
        self.assertEqual(str_ng._list_of_events, orig_ng._list_of_events)
        self.assertEqual(str_ng._list_of_connections, orig_ng._list_of_connections)

    def test_make_from_str_3(self):
        # Does it work in general?
        # f : 'm3 -m2 M-3'
        str_ng = IntervalNGram.make_from_str('m3 -m2 M-3')
        orig_ng = IntervalNGram(self.f)
        self.assertEqual(str_ng._list_of_events, orig_ng._list_of_events)
        self.assertEqual(str_ng._list_of_connections, orig_ng._list_of_connections)

    def test_make_from_str_4(self):
        # negative and positive intervals in input string
        # g : 'm3 +P4 M2 -m6 P5 +A9 M-10'
        str_ng = IntervalNGram.make_from_str('m3 +P4 M2 -m6 P5 +A9 M-10')
        orig_ng = IntervalNGram(self.g)
        self.assertEqual(str_ng._list_of_events, orig_ng._list_of_events)
        self.assertEqual(str_ng._list_of_connections, orig_ng._list_of_connections)

    def test_make_from_str_5(self):
        # heedQuality set as per whether there was quality on the way in
        str_ng = IntervalNGram.make_from_str('m3 P1 m3')
        orig_ng = IntervalNGram(self.a)
        self.assertEqual(str_ng.get_string_version(True, 'compound'),
                         orig_ng.get_string_version(True, 'compound'))

    def test_make_from_str_6(self):
        # heedQuality set as per whether there was quality on the way in
        str_ng = IntervalNGram.make_from_str('3 1 3')
        orig_ng = IntervalNGram(self.a)
        self.assertEqual(str_ng.get_string_version(False, 'compound'),
                         orig_ng.get_string_version(False, 'compound'))

    def test_make_from_str_7(self):
        # wrong number of intervals in input string
        self.assertRaises(RuntimeError, IntervalNGram.make_from_str, '3 1 3 1')

    def test_make_from_str_8(self):
        # wrong number of intervals in input string
        self.assertRaises(RuntimeError, IntervalNGram.make_from_str, '3 12')

    def test_make_from_str_9(self):
        # intervals (perfect and non-perfect) larger than P23
        str_ng = IntervalNGram.make_from_str('24 1 24')
        self.assertEqual(str_ng.get_string_version(False, 'compound'), '24 1 24')

    def test_make_from_str_10(self):
        # intervals (perfect and non-perfect) larger than P23
        str_ng = IntervalNGram.make_from_str('m24 P1 M24')
        self.assertEqual(str_ng.get_string_version(True, 'compound'), 'm24 P1 M24')

    def test_make_from_str_11(self):
        # intervals (perfect and non-perfect) larger than P23
        str_ng = IntervalNGram.make_from_str('26 1 26')
        self.assertEqual(str_ng.get_string_version(False, 'compound'), '26 1 26')

    def test_make_from_str_12(self):
        # intervals (perfect and non-perfect) larger than P23
        str_ng = IntervalNGram.make_from_str('P26 P1 d26')
        self.assertEqual(str_ng.get_string_version(True, 'compound'), 'P26 P1 d26')

    def test_make_from_str_13(self):
        # putting the '-' for negative intervals in all kinds of places
        str_ng = IntervalNGram.make_from_str('M3 -M2 M3')
        self.assertEqual(str_ng.get_string_version(True, 'compound'), 'M3 -M2 M3')

    # the following two tests currently fail... does it make sense for
    # them to produce valid NGrams? Those are really weird looking
    # strings.

    #def test_make_from_str_14(self):
        # putting the '-' for negative intervals in all kinds of places
        #str_ng = IntervalNGram.make_from_str('M3 M-2 M3')
        #self.assertEqual(str(str_ng), 'M3 -M2 M3')

    #def test_make_from_str_15(self):
        # putting the '-' for negative intervals in all kinds of places
        #str_ng = IntervalNGram.make_from_str('M3 M2- M3')
        #self.assertEqual(str(str_ng), 'M3 -M2 M3')


class TestChordNGram(unittest.TestCase):
    def test_finds_transformations(self):
        '''
        Whether the constructor correctly calculates the transformations from a
        C major triad to every other minor and major triad.
        '''
        # each element in this list is a tuple, where the first is a string that
        # will be passed to chord.Chord to create the second Chord object to be
        # passed to the ChordNGram constructor, and the second is a string that
        # represents the value of ChordNGram._list_of_connections[0]
        correct_transforms = [('c# e g#', 'LPR'), ('c# e# g#', 'LPRP'),
                                ('d f a', 'RLR'), ('d f# a', 'LRLR'),
                                ('e- g- b-', 'PRP'), ('e- g b-', 'PR'),
                                ('e g b', 'L'), ('e g# b', 'LP'),
                                ('f a- c', 'PLR'), ('f a c', 'RL'),
                                ('f# a c#', 'RPR'), ('f# a# c#', 'PRPR'),
                                ('g b- d', 'LRP'), ('g b d', 'LR'),
                                ('g# b d#', 'LPL'), ('a- c e-', 'PL'),
                                ('a c e', 'R'), ('a c# e', 'RP'),
                                ('b- d- f', 'LRPRP'), ('b- d f', 'LRPR'),
                                ('b d f#', 'LRL'), ('b d# f#', 'LPLR'),
                                ('c e- g', 'P'),
                            ]

        # Everybody's favourite triad
        cmaj = chord.Chord('c e g')

        for simultaneity, transform in correct_transforms:
            this_ngram = ChordNGram([cmaj, chord.Chord(simultaneity)])
            self.assertEqual(this_ngram._list_of_connections[0], transform)

    # test __repr__()
    def test_repr_1(self):
        expected = "ChordNGram([Chord('C E G'), Chord('D F A')])"
        actual = ChordNGram([chord.Chord('c e g'), chord.Chord('d f a')])
        self.assertEqual(actual.__repr__(), expected)

    def test_repr_2(self):
        expected = "ChordNGram([Chord('C E G'), Chord('D F A C')])"
        actual = ChordNGram([chord.Chord('c e g'), chord.Chord('d f a c')])
        self.assertEqual(actual.__repr__(), expected)

    def test_repr_3(self):
        expected = "ChordNGram([Chord('C E G'), Chord('D F A'), Chord('E G B')])"
        actual = ChordNGram([chord.Chord('c e g'), chord.Chord('d f a'), chord.Chord('e g b')])
        self.assertEqual(actual.__repr__(), expected)

    def test_repr_4(self):
        expected = "ChordNGram([Chord('C E G'), Chord('D F A'), Chord('E G B'), Chord('F A C')])"
        actual = ChordNGram([chord.Chord('c e g'),
                             chord.Chord('d f a'),
                             chord.Chord('e g b'),
                             chord.Chord('f a c')])
        self.assertEqual(actual.__repr__(), expected)

    def test_repr_5(self):
        expected = "ChordNGram([Chord('C E G'), Chord('D F A C'), Chord('E G B'), Chord('F A C')])"
        actual = ChordNGram([chord.Chord('C E G'),
                             chord.Chord('D F A C'),
                             chord.Chord('E G B'),
                             chord.Chord('F A C')])
        self.assertEqual(actual.__repr__(), expected)

    def test_repr_6(self):
        expected = "ChordNGram([Chord('C E G B'), Chord('D F A')])"
        actual = ChordNGram([chord.Chord('C E G B'), chord.Chord('D F A')])
        self.assertEqual(actual.__repr__(), expected)

    def test_repr_7(self):
        expected = "ChordNGram([Chord('C E- E G'), Chord('D E F'), Chord('E')])"
        actual = ChordNGram([chord.Chord('C E- E G'), chord.Chord('D E F'), chord.Chord('E')])
        self.assertEqual(actual.__repr__(), expected)

    # test get_string_version()
    def test_str_1(self):
        expected = "<C E G> ==RLR=> <D F A>"
        actual = ChordNGram([chord.Chord('c e g'), chord.Chord('d f a')])
        self.assertEqual(actual.get_string_version(), expected)

    def test_str_2(self):
        expected = "<C E G> ==?=> <D F A C>"
        actual = ChordNGram([chord.Chord('c e g'), chord.Chord('d f a c')])
        self.assertEqual(actual.get_string_version(), expected)

    def test_str_3(self):
        expected = "<C E G> ==RLR=> <D F A> ==LRPR=> <E G B>"
        actual = ChordNGram([chord.Chord('c e g'), chord.Chord('d f a'), chord.Chord('e g b')])
        self.assertEqual(actual.get_string_version(), expected)

    def test_str_4(self):
        expected = "<C E G> ==RLR=> <D F A> ==LRPR=> <E G B> ==LRL=> <F A C>"
        actual = ChordNGram([chord.Chord('c e g'),
                             chord.Chord('d f a'),
                             chord.Chord('e g b'),
                             chord.Chord('f a c')])
        self.assertEqual(actual.get_string_version(), expected)

    def test_str_5(self):
        expected = "<C E G> ==?=> <D F A C> ==?=> <E G B> ==LRL=> <F A C>"
        actual = ChordNGram([chord.Chord('C E G'),
                             chord.Chord('D F A C'),
                             chord.Chord('E G B'),
                             chord.Chord('F A C')])
        self.assertEqual(actual.get_string_version(), expected)

    def test_str_6(self):
        expected = "<C E G B> ==?=> <D F A>"
        actual = ChordNGram([chord.Chord('C E G B'), chord.Chord('D F A')])
        self.assertEqual(actual.get_string_version(), expected)

    def test_str_7(self):
        expected = "<C E- E G> ==?=> <D E F> ==?=> <E>"
        actual = ChordNGram([chord.Chord('C E- E G'), chord.Chord('D E F'), chord.Chord('E')])
        self.assertEqual(actual.get_string_version(), expected)


#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
test_interval_ngram_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalNGram)
test_chord_ngram_suite = unittest.TestLoader().loadTestsFromTestCase(TestChordNGram)
