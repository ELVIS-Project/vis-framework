#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_harmony.py
# Purpose:                Tests for vis.analyzers.indexers.harmony
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
import pandas
from vis.analyzers.indexers import harmony
from vis.analyzers.indexers.harmony import scale_degree_func, poss_func_func, ScaleDegreeIndexer

class TestScaleDegreeIndexer(unittest.TestCase):
    # We've got a bunch of "extreme"-ish keys here, fully checked-out!
    def scdeg_checker(self, sc_deg, the_key, the_note):
        """
        Check that scale_degree_func() returns "sc_deg" when given "the_key" and "the_note".
        """
        self.assertEqual(sc_deg, scale_degree_func(pandas.Series([the_note, (the_key, '')])))
    
    def test_C_tonic(self):
        tonic = 'C'
        self.scdeg_checker('7', tonic, 'B')
        self.scdeg_checker('6', tonic, 'A')
        self.scdeg_checker('5', tonic, 'G')
        self.scdeg_checker('4', tonic, 'F')
        self.scdeg_checker('3', tonic, 'E')
        self.scdeg_checker('2', tonic, 'D')
        self.scdeg_checker('1', tonic, 'C')
        # flat scale degrees
        self.scdeg_checker('-7', tonic, 'B-')
        self.scdeg_checker('-6', tonic, 'A-')
        self.scdeg_checker('-5', tonic, 'G-')
        self.scdeg_checker('-4', tonic, 'F-')
        self.scdeg_checker('-3', tonic, 'E-')
        self.scdeg_checker('-2', tonic, 'D-')
        self.scdeg_checker('-1', tonic, 'C-')
        # sharp scale degrees
        self.scdeg_checker('#7', tonic, 'B#')
        self.scdeg_checker('#6', tonic, 'A#')
        self.scdeg_checker('#5', tonic, 'G#')
        self.scdeg_checker('#4', tonic, 'F#')
        self.scdeg_checker('#3', tonic, 'E#')
        self.scdeg_checker('#2', tonic, 'D#')
        self.scdeg_checker('#1', tonic, 'C#')
        # double-flat scale degrees
        self.scdeg_checker('--7', tonic, 'B--')
        self.scdeg_checker('--6', tonic, 'A--')
        self.scdeg_checker('--5', tonic, 'G--')
        self.scdeg_checker('--4', tonic, 'F--')
        self.scdeg_checker('--3', tonic, 'E--')
        self.scdeg_checker('--2', tonic, 'D--')
        self.scdeg_checker('--1', tonic, 'C--')
        # double-sharp scale degrees
        self.scdeg_checker('##7', tonic, 'B##')
        self.scdeg_checker('##6', tonic, 'A##')
        self.scdeg_checker('##5', tonic, 'G##')
        self.scdeg_checker('##4', tonic, 'F##')
        self.scdeg_checker('##3', tonic, 'E##')
        self.scdeg_checker('##2', tonic, 'D##')
        self.scdeg_checker('##1', tonic, 'C##')
       
    def test_D_tonic(self):
        tonic = 'D'
        self.scdeg_checker('7', tonic, 'C#')
        self.scdeg_checker('6', tonic, 'B')
        self.scdeg_checker('5', tonic, 'A')
        self.scdeg_checker('4', tonic, 'G')
        self.scdeg_checker('3', tonic, 'F#')
        self.scdeg_checker('2', tonic, 'E')
        self.scdeg_checker('1', tonic, 'D')
        # flat scale degrees
        self.scdeg_checker('-7', tonic, 'C')
        self.scdeg_checker('-6', tonic, 'B-')
        self.scdeg_checker('-5', tonic, 'A-')
        self.scdeg_checker('-4', tonic, 'G-')
        self.scdeg_checker('-3', tonic, 'F')
        self.scdeg_checker('-2', tonic, 'E-')
        self.scdeg_checker('-1', tonic, 'D-')
        # sharp scale degrees
        self.scdeg_checker('#7', tonic, 'C##')
        self.scdeg_checker('#6', tonic, 'B#')
        self.scdeg_checker('#5', tonic, 'A#')
        self.scdeg_checker('#4', tonic, 'G#')
        self.scdeg_checker('#3', tonic, 'F##')
        self.scdeg_checker('#2', tonic, 'E#')
        self.scdeg_checker('#1', tonic, 'D#')
        # double-flat scale degrees
        self.scdeg_checker('--7', tonic, 'C-')
        self.scdeg_checker('--6', tonic, 'B--')
        self.scdeg_checker('--5', tonic, 'A--')
        self.scdeg_checker('--4', tonic, 'G--')
        self.scdeg_checker('--3', tonic, 'F-')
        self.scdeg_checker('--2', tonic, 'E--')
        self.scdeg_checker('--1', tonic, 'D--')
        # double-sharp scale degrees
        self.scdeg_checker('##7', tonic, 'C###')
        self.scdeg_checker('##6', tonic, 'B##')
        self.scdeg_checker('##5', tonic, 'A##')
        self.scdeg_checker('##4', tonic, 'G##')
        self.scdeg_checker('##3', tonic, 'F###')
        self.scdeg_checker('##2', tonic, 'E##')
        self.scdeg_checker('##1', tonic, 'D##')

    def test_E_tonic(self):
        tonic = 'E-'
        self.scdeg_checker('7', tonic, 'D')
        self.scdeg_checker('6', tonic, 'C')
        self.scdeg_checker('5', tonic, 'B-')
        self.scdeg_checker('4', tonic, 'A-')
        self.scdeg_checker('3', tonic, 'G')
        self.scdeg_checker('2', tonic, 'F')
        self.scdeg_checker('1', tonic, 'E-')
        # flat scale degrees
        self.scdeg_checker('-7', tonic, 'D-')
        self.scdeg_checker('-6', tonic, 'C-')
        self.scdeg_checker('-5', tonic, 'B--')
        self.scdeg_checker('-4', tonic, 'A--')
        self.scdeg_checker('-3', tonic, 'G-')
        self.scdeg_checker('-2', tonic, 'F-')
        self.scdeg_checker('-1', tonic, 'E--')
        # sharp scale degrees
        self.scdeg_checker('#7', tonic, 'D#')
        self.scdeg_checker('#6', tonic, 'C#')
        self.scdeg_checker('#5', tonic, 'B')
        self.scdeg_checker('#4', tonic, 'A')
        self.scdeg_checker('#3', tonic, 'G#')
        self.scdeg_checker('#2', tonic, 'F#')
        self.scdeg_checker('#1', tonic, 'E')
        # double-flat scale degrees
        self.scdeg_checker('--7', tonic, 'D--')
        self.scdeg_checker('--6', tonic, 'C--')
        self.scdeg_checker('--5', tonic, 'B---')
        self.scdeg_checker('--4', tonic, 'A---')
        self.scdeg_checker('--3', tonic, 'G--')
        self.scdeg_checker('--2', tonic, 'F--')
        self.scdeg_checker('--1', tonic, 'E---')
        # double-sharp scale degrees
        self.scdeg_checker('##7', tonic, 'D##')
        self.scdeg_checker('##6', tonic, 'C##')
        self.scdeg_checker('##5', tonic, 'B#')
        self.scdeg_checker('##4', tonic, 'A#')
        self.scdeg_checker('##3', tonic, 'G##')
        self.scdeg_checker('##2', tonic, 'F##')
        self.scdeg_checker('##1', tonic, 'E#')

    def test_Csharp_tonic(self):
        tonic = 'C#'
        self.scdeg_checker('7', tonic, 'B#')
        self.scdeg_checker('6', tonic, 'A#')
        self.scdeg_checker('5', tonic, 'G#')
        self.scdeg_checker('4', tonic, 'F#')
        self.scdeg_checker('3', tonic, 'E#')
        self.scdeg_checker('2', tonic, 'D#')
        self.scdeg_checker('1', tonic, 'C#')
        # flat scale degrees
        self.scdeg_checker('-7', tonic, 'B')
        self.scdeg_checker('-6', tonic, 'A')
        self.scdeg_checker('-5', tonic, 'G')
        self.scdeg_checker('-4', tonic, 'F')
        self.scdeg_checker('-3', tonic, 'E')
        self.scdeg_checker('-2', tonic, 'D')
        self.scdeg_checker('-1', tonic, 'C')
        # sharp scale degrees
        self.scdeg_checker('#7', tonic, 'B##')
        self.scdeg_checker('#6', tonic, 'A##')
        self.scdeg_checker('#5', tonic, 'G##')
        self.scdeg_checker('#4', tonic, 'F##')
        self.scdeg_checker('#3', tonic, 'E##')
        self.scdeg_checker('#2', tonic, 'D##')
        self.scdeg_checker('#1', tonic, 'C##')
        # double-flat scale degrees
        self.scdeg_checker('--7', tonic, 'B-')
        self.scdeg_checker('--6', tonic, 'A-')
        self.scdeg_checker('--5', tonic, 'G-')
        self.scdeg_checker('--4', tonic, 'F-')
        self.scdeg_checker('--3', tonic, 'E-')
        self.scdeg_checker('--2', tonic, 'D-')
        self.scdeg_checker('--1', tonic, 'C-')
        # double-sharp scale degrees
        self.scdeg_checker('##7', tonic, 'B###')
        self.scdeg_checker('##6', tonic, 'A###')
        self.scdeg_checker('##5', tonic, 'G###')
        self.scdeg_checker('##4', tonic, 'F###')
        self.scdeg_checker('##3', tonic, 'E###')
        self.scdeg_checker('##2', tonic, 'D###')
        self.scdeg_checker('##1', tonic, 'C###')

    def test_Cflat_tonic(self):
        tonic = 'C-'
        self.scdeg_checker('7', tonic, 'B-')
        self.scdeg_checker('6', tonic, 'A-')
        self.scdeg_checker('5', tonic, 'G-')
        self.scdeg_checker('4', tonic, 'F-')
        self.scdeg_checker('3', tonic, 'E-')
        self.scdeg_checker('2', tonic, 'D-')
        self.scdeg_checker('1', tonic, 'C-')
        # flat scale degrees
        self.scdeg_checker('-7', tonic, 'B--')
        self.scdeg_checker('-6', tonic, 'A--')
        self.scdeg_checker('-5', tonic, 'G--')
        self.scdeg_checker('-4', tonic, 'F--')
        self.scdeg_checker('-3', tonic, 'E--')
        self.scdeg_checker('-2', tonic, 'D--')
        self.scdeg_checker('-1', tonic, 'C--')
        # sharp scale degrees
        self.scdeg_checker('#7', tonic, 'B')
        self.scdeg_checker('#6', tonic, 'A')
        self.scdeg_checker('#5', tonic, 'G')
        self.scdeg_checker('#4', tonic, 'F')
        self.scdeg_checker('#3', tonic, 'E')
        self.scdeg_checker('#2', tonic, 'D')
        self.scdeg_checker('#1', tonic, 'C')
        # double-flat scale degrees
        self.scdeg_checker('--7', tonic, 'B---')
        self.scdeg_checker('--6', tonic, 'A---')
        self.scdeg_checker('--5', tonic, 'G---')
        self.scdeg_checker('--4', tonic, 'F---')
        self.scdeg_checker('--3', tonic, 'E---')
        self.scdeg_checker('--2', tonic, 'D---')
        self.scdeg_checker('--1', tonic, 'C---')
        # double-sharp scale degrees
        self.scdeg_checker('##7', tonic, 'B#')
        self.scdeg_checker('##6', tonic, 'A#')
        self.scdeg_checker('##5', tonic, 'G#')
        self.scdeg_checker('##4', tonic, 'F#')
        self.scdeg_checker('##3', tonic, 'E#')
        self.scdeg_checker('##2', tonic, 'D#')
        self.scdeg_checker('##1', tonic, 'C#')

    def test_indexer_C_tonic(self):
        # this tests the indexer itself---not just the _inderxer_func()
        key_index = pandas.Series([('C', 'major')], index=[0.0])
        noterest_index = pandas.Series(['B', 'A', 'G', 'F', 'E', 'D', 'C', 'B-', 'A-', 'G-',
                                        'F-', 'E-', 'D-', 'C-', 'B#', 'A#', 'G#', 'F#', 'E#',
                                        'D#', 'C#', 'B--', 'A--', 'G--', 'F--', 'E--', 'D--',
                                        'C--', 'B##', 'A##', 'G##', 'F##', 'E##', 'D##', 'C##'])
        expected_index = pandas.Series(['7', '6', '5', '4', '3', '2', '1', '-7', '-6', '-5',
                                        '-4', '-3', '-2', '-1', '#7', '#6', '#5', '#4', '#3',
                                        '#2', '#1', '--7', '--6', '--5', '--4', '--3', '--2',
                                        '--1', '##7', '##6', '##5', '##4', '##3', '##2', '##1'])
        test_i = ScaleDegreeIndexer([noterest_index, key_index])
        actual = test_i.run()
        self.assertEqual(1, len(actual))
        actual = actual[0]
        self.assertSequenceEqual(list(expected_index), list(actual))


class TestPossFuncsIndexer(unittest.TestCase):
    def test_applied_things(self):
        self.assertSequenceEqual(poss_func_func(('#4', 'G', harmony.POS_MID)),
                                 [(('D', harmony.FUNC_DOM, harmony.ROLE_AG, '7'), harmony.COND_FOLL, ('D', harmony.FUNC_TON, harmony.ROLE_BA, '1'))])
        self.assertSequenceEqual(poss_func_func(('-2', 'D-', harmony.POS_LOW)),
                                 [(('G', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_FOLL, ('G', harmony.FUNC_DOM, harmony.ROLE_BA, '5'))])

    def test_agent_minor(self):
        # the flatted 3, 6, 7 degrees might also serve as applied Subdominant agent.
        self.assertSequenceEqual(poss_func_func(('-3', 'C', harmony.POS_LOW)),
                                 [(('G', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_FOLL, ('G', harmony.FUNC_DOM, harmony.ROLE_BA, '5')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('-6', 'C', harmony.POS_LOW)),
                                 [(('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('-7', 'C', harmony.POS_LOW)),
                                 [(('D', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_FOLL, ('D', harmony.FUNC_DOM, harmony.ROLE_BA, '5')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('-3', 'C', harmony.POS_MID)),
                                 [(('G', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_FOLL, ('G', harmony.FUNC_DOM, harmony.ROLE_BA, '5')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('-6', 'C', harmony.POS_MID)),
                                 [(('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('-7', 'C', harmony.POS_MID)),
                                 [(('D', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_FOLL, ('D', harmony.FUNC_DOM, harmony.ROLE_BA, '5')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('-3', 'C', harmony.POS_HIH)),
                                 [(('G', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_FOLL, ('G', harmony.FUNC_DOM, harmony.ROLE_BA, '5')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('-6', 'C', harmony.POS_HIH)),
                                 [(('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('-7', 'C', harmony.POS_HIH)),
                                 [(('D', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), harmony.COND_FOLL, ('D', harmony.FUNC_DOM, harmony.ROLE_BA, '5')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'), harmony.COND_GUAR, '')])

    def test_base_lowest(self):
        self.assertSequenceEqual(poss_func_func(('1', 'C', harmony.POS_LOW)),
                                 [(('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('4', 'C', harmony.POS_LOW)),
                                 [(('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'), harmony.COND_GUAR, '')])
        self.assertSequenceEqual(poss_func_func(('5', 'C', harmony.POS_LOW)),
                                 [(('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'), harmony.COND_GUAR, '')])

    def test_base_middle_highest(self):
        ## ^4 is kind of stuck
        self.assertSequenceEqual(poss_func_func(('4', 'C', harmony.POS_MID)),
                                 [(('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'), harmony.COND_PRES, ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6')),
                                  (('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'), harmony.COND_PRES, ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'))])
        self.assertSequenceEqual(poss_func_func(('4', 'C', harmony.POS_HIH)),
                                 [(('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'), harmony.COND_PRES, ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6')),
                                  (('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'), harmony.COND_PRES, ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'))])
        # ^1 and ^5 may also serve as associates
        # if T-agent is present, then ^1 is a T-base; if S-agent is present or S-base is harmony.POS_LOWest voice, then ^1 is S-associate
        self.assertSequenceEqual(poss_func_func(('1', 'C', harmony.POS_MID)),
                                 [(('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'), harmony.COND_PRES, ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'), harmony.COND_PRES, ('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3')),
                                  (('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'), harmony.COND_PRES, ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6')),
                                  (('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'), harmony.COND_PRES, ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6')),
                                  (('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'), harmony.COND_LOW, ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'))])
        self.assertSequenceEqual(poss_func_func(('1', 'C', harmony.POS_HIH)),
                                 [(('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'), harmony.COND_PRES, ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'), harmony.COND_PRES, ('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3')),
                                  (('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'), harmony.COND_PRES, ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6')),
                                  (('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'), harmony.COND_PRES, ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6')),
                                  (('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'), harmony.COND_LOW, ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'))])
        ## if D-agent is present, then ^5 is a D-base; if T-agent is present or T-base is harmony.POS_LOWest voice, then ^5 is T-associate
        self.assertSequenceEqual(poss_func_func(('5', 'C', harmony.POS_MID)),
                                 [(('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'), harmony.COND_PRES, ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'), harmony.COND_PRES, ('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'), harmony.COND_LOW, ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'))])
        self.assertSequenceEqual(poss_func_func(('5', 'C', harmony.POS_HIH)),
                                 [(('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'), harmony.COND_PRES, ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'), harmony.COND_PRES, ('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3')),
                                  (('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'), harmony.COND_LOW, ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'))])

    def test_diatonic_degree_2(self):
        # with ^2 in the lowest voice, the only thing that'll enable D-associate function is the D-agent
        self.assertSequenceEqual(poss_func_func(('2', 'C', harmony.POS_LOW)),
                                 [(('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'))])
        # with ^2 in a middle or the upper voice, either the D-agent being present or the D-base in the harmony.POS_LOWest voice will enable D-associate function
        self.assertSequenceEqual(poss_func_func(('2', 'C', harmony.POS_MID)),
                                 [(('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), harmony.COND_LOW, ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'))])
        self.assertSequenceEqual(poss_func_func(('2', 'C', harmony.POS_HIH)),
                                 [(('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), harmony.COND_PRES, ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7')),
                                  (('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), harmony.COND_LOW, ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'))])


class TestChooseFuncIndexer(unittest.TestCase):
    #@staticmethod
    #def equalsMaker(aaa, zzz):
        ## Given two model outputs from reconcilePossibleFunctions() outputs
        ## True or False depending on whether the contents of the outputs is
        ## the same. This function is required because, by default, assertEqual()
        ## only uses the == to test equality, and the things outputted by rPF()
        ## don't really like that.
        #if aaa.equal(zzz) and zzz.equal(aaa):
            #return True
        #else:
            #return False

    def setUp(self):
        ## The usual
        #harmony.FUNC_SUB = HarmonicFunction.Subdominant
        #harmony.FUNC_TON = HarmonicFunction.Tonic
        #harmony.FUNC_DOM = HarmonicFunction.Dominant
        #harmony.FUNC_UNK = HarmonicFunction.Unknown
        #harmony.ROLE_BA = FunctionalRole.Base
        #harmony.ROLE_AG = FunctionalRole.Agent
        #harmony.ROLE_AS = FunctionalRole.Associate
        #harmony.ROLE_UN = FunctionalRole.Unknown
        #harmony.POS_LOW = RelativeVoicePosition.Lowest
        #harmony.POS_MID = RelativeVoicePosition.Middle
        #harmony.POS_HIH = RelativeVoicePosition.Highest
        #harmony.COND_GUAR = ConditionForFunction.IsGuaranteed
        #harmony.COND_LOW = ConditionForFunction.IsLowestVoice
        #harmony.COND_PRES = ConditionForFunction.IsPresent
        ## Keys
        #self.CM = key.Key("C")
        #self.GM = key.Key("G")
        #self.EM = key.Key("E")
        #self.FM = key.Key("F")
        #self.AfM = key.Key("A-")
        # Scale Degrees
        self.lf1 = harmony.poss_func_func(pandas.Series(['-1', 'C', harmony.POS_LOW]))
        self.l1 = harmony.poss_func_func(pandas.Series(['1', 'C', harmony.POS_LOW]))
        self.lf2 = harmony.poss_func_func(pandas.Series(['-2', 'C', harmony.POS_LOW]))
        self.l2 = harmony.poss_func_func(pandas.Series(['2', 'C', harmony.POS_LOW]))
        self.ls2 = harmony.poss_func_func(pandas.Series(['#2', 'C', harmony.POS_LOW]))
        self.l3 = harmony.poss_func_func(pandas.Series(['3', 'C', harmony.POS_LOW]))
        self.lf3 = harmony.poss_func_func(pandas.Series(['-3', 'C', harmony.POS_LOW]))
        self.lf4 = harmony.poss_func_func(pandas.Series(['-4', 'C', harmony.POS_LOW]))
        self.l4 = harmony.poss_func_func(pandas.Series(['4', 'C', harmony.POS_LOW]))
        self.ls4 = harmony.poss_func_func(pandas.Series(['#4', 'C', harmony.POS_LOW]))
        self.l5 = harmony.poss_func_func(pandas.Series(['5', 'C', harmony.POS_LOW]))
        self.l6 = harmony.poss_func_func(pandas.Series(['6', 'C', harmony.POS_LOW]))
        self.lf6 = harmony.poss_func_func(pandas.Series(['-6', 'C', harmony.POS_LOW]))
        self.l7 = harmony.poss_func_func(pandas.Series(['7', 'C', harmony.POS_LOW]))
        self.lf7 = harmony.poss_func_func(pandas.Series(['-7', 'C', harmony.POS_LOW]))
        self.mf1 = harmony.poss_func_func(pandas.Series(['-1', 'C', harmony.POS_MID]))
        self.m1 = harmony.poss_func_func(pandas.Series(['1', 'C', harmony.POS_MID]))
        self.mf2 = harmony.poss_func_func(pandas.Series(['-2', 'C', harmony.POS_MID]))
        self.m2 = harmony.poss_func_func(pandas.Series(['2', 'C', harmony.POS_MID]))
        self.ms2 = harmony.poss_func_func(pandas.Series(['#2', 'C', harmony.POS_MID]))
        self.m3 = harmony.poss_func_func(pandas.Series(['3', 'C', harmony.POS_MID]))
        self.mf3 = harmony.poss_func_func(pandas.Series(['-3', 'C', harmony.POS_MID]))
        self.mf4 = harmony.poss_func_func(pandas.Series(['-4', 'C', harmony.POS_MID]))
        self.m4 = harmony.poss_func_func(pandas.Series(['4', 'C', harmony.POS_MID]))
        self.ms4 = harmony.poss_func_func(pandas.Series(['#4', 'C', harmony.POS_MID]))
        self.m5 = harmony.poss_func_func(pandas.Series(['5', 'C', harmony.POS_MID]))
        self.m6 = harmony.poss_func_func(pandas.Series(['6', 'C', harmony.POS_MID]))
        self.mf6 = harmony.poss_func_func(pandas.Series(['-6', 'C', harmony.POS_MID]))
        self.m7 = harmony.poss_func_func(pandas.Series(['7', 'C', harmony.POS_MID]))
        self.mf7 = harmony.poss_func_func(pandas.Series(['-7', 'C', harmony.POS_MID]))
        self.hf1 = harmony.poss_func_func(pandas.Series(['-1', 'C', harmony.POS_HIH]))
        self.h1 = harmony.poss_func_func(pandas.Series(['1', 'C', harmony.POS_HIH]))
        self.hf2 = harmony.poss_func_func(pandas.Series(['-2', 'C', harmony.POS_HIH]))
        self.h2 = harmony.poss_func_func(pandas.Series(['2', 'C', harmony.POS_HIH]))
        self.hs2 = harmony.poss_func_func(pandas.Series(['#2', 'C', harmony.POS_HIH]))
        self.h3 = harmony.poss_func_func(pandas.Series(['3', 'C', harmony.POS_HIH]))
        self.hf3 = harmony.poss_func_func(pandas.Series(['-3', 'C', harmony.POS_HIH]))
        self.hf4 = harmony.poss_func_func(pandas.Series(['-4', 'C', harmony.POS_HIH]))
        self.h4 = harmony.poss_func_func(pandas.Series(['4', 'C', harmony.POS_HIH]))
        self.hs4 = harmony.poss_func_func(pandas.Series(['#4', 'C', harmony.POS_HIH]))
        self.h5 = harmony.poss_func_func(pandas.Series(['5', 'C', harmony.POS_HIH]))
        self.h6 = harmony.poss_func_func(pandas.Series(['6', 'C', harmony.POS_HIH]))
        self.hf6 = harmony.poss_func_func(pandas.Series(['-6', 'C', harmony.POS_HIH]))
        self.h7 = harmony.poss_func_func(pandas.Series(['7', 'C', harmony.POS_HIH]))
        self.hf7 = harmony.poss_func_func(pandas.Series(['-7', 'C', harmony.POS_HIH]))

    def test_primary_root_and_first_inversion(self):
        # Tonic
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h5, self.m3, self.l1])),
                         [('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h5, self.m1, self.l3])),
                         [('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h5, self.mf3, self.l1])),
                         [('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h5, self.m1, self.lf3])),
                         [('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3')])
        # Subdominant
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h1, self.m6, self.l4])),
                         [('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h1, self.m4, self.l6])),
                         [('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h1, self.mf6, self.l4])),
                         [('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h1, self.m4, self.lf6])),
                         [('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6')])
        # Dominant
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h2, self.m7, self.l5])),
                         [('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h2, self.m5, self.l7])),
                         [('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h2, self.mf7, self.l5])),
                         [('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h2, self.m5, self.lf7])),
                         [('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7')])

    def test_primary_base_and_associate(self):
        # base in lowest voice, associate in highest voice; will it still register correctly?
        # S
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h1, self.l4])),
                         [('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')])
        # T
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h5, self.l1])),
                         [('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')])
        # D
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h2, self.l5])),
                         [('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5')])

    #def test_tonic_with_extra(self):
        ## Tonic primary triad, with extra pitches
        ## Extra ^1
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l1, self.m3, self.m1, self.h5]), \
                        #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),\
                        #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AS, '5')])))
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l1, self.m3, self.m5, self.h1]), \
                        #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),\
                        #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')])))
        ## Extra ^1 and ^3
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l1, self.m3, self.m1, self.m5, self.h3]), \
                        #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),\
                        #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')])))
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l1, self.m3, self.m5, self.m3, self.h1]), \
                        #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),\
                        #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')])))
        ## Extra ^1 and ^3 and ^5
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l1, self.m3, self.m1, self.m5, self.m3, self.h5]), \
                        #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),\
                        #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AS, '5')])))
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l1, self.m3, self.m5, self.m3, self.m5, self.h1]), \
                        #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),\
                        #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')])))

    def test_secondary_diatonic(self):
        # secondary diatonic triads in root position and first inversion
        # II
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h6, self.m4, self.l2])),
                        [('C', harmony.FUNC_UNK, harmony.ROLE_AG, '6'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_UN, '2')]) # ii
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.hf6, self.m4, self.l2])),
                        [('C', harmony.FUNC_UNK, harmony.ROLE_AG, '-6'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_UN, '2')]) # ii-dim (minor mode)
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h6, self.m2, self.l4])),
                        [('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6'),
                         ('C', harmony.FUNC_UNK, harmony.ROLE_UN, '2'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')]) # ii6
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.hf6, self.m2, self.l4])),
                        [('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'),
                         ('C', harmony.FUNC_UNK, harmony.ROLE_UN, '2'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')]) # ii-dim6 (minor mode)
        # III
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h7, self.m5, self.l3])),
                        [('C', harmony.FUNC_TON, harmony.ROLE_AG, '7'),
                         ('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),
                         ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '3')]) # iii
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.hf7, self.m5, self.lf3])),
                        [('C', harmony.FUNC_TON, harmony.ROLE_AG, '-7'), 
                         ('C', harmony.FUNC_TON, harmony.ROLE_AS, '5'),
                         ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-3')]) # flat-III
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h7, self.m3, self.l5])),
                        [('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7'),
                         ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                         ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5')]) # iii6
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.hf7, self.mf3, self.l5])),
                        [('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'),
                         ('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3'),
                         ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5')]) # flat-III6
        # VI
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h3, self.m1, self.l6])),
                        [('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                         ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')]) # vi
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.hf3, self.m1, self.lf6])),
                        [('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                         ('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3')]) # flat-VI
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h3, self.m6, self.l1])),
                        [('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6'),
                         ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')]) # vi6
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.hf3, self.mf6, self.l1])),
                        [('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'),
                         ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')]) # flat-VI6
        # VII
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h4, self.m2, self.l7])),
                        [('C', harmony.FUNC_DOM, harmony.ROLE_UN, '4'),
                         ('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                         ('C', harmony.FUNC_UNK, harmony.ROLE_AG, '7')]) # vii-dim
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h4, self.m2, self.lf7])),
                        [('C', harmony.FUNC_DOM, harmony.ROLE_UN, '4'),
                         ('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                         ('C', harmony.FUNC_UNK, harmony.ROLE_AG, '-7')]) # flat-VII
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h4, self.m7, self.l2])),
                        [('C', harmony.FUNC_DOM, harmony.ROLE_UN, '4'),
                         ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7'),
                         ('C', harmony.FUNC_UNK, harmony.ROLE_AS, '2')]) # vii-dim6
        self.assertTrue(harmony.reconciliation_func(pandas.Series([self.h4, self.mf7, self.l2])),
                        [('C', harmony.FUNC_DOM, harmony.ROLE_UN, '4'),
                         ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'),
                         ('C', harmony.FUNC_UNK, harmony.ROLE_AS, '2')]) # flat-VII6

    #def test_diatonic_second_inversion(self):
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l5, self.m3, self.h1]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')]))) # I
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l5, self.mf3, self.h1]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')]))) # i
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l6, self.m4, self.h2]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'),HarmonicFunctionalNote('C', harmony.FUNC_UNK, harmony.ROLE_UN,'2')]))) # ii
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.lf6, self.m4, self.h2]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'),HarmonicFunctionalNote('C', harmony.FUNC_UNK, harmony.ROLE_UN,'2')]))) # ii-dim
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l7, self.m5, self.h3]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')]))) # iii
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.lf7, self.m5, self.hf3]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'),HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3')]))) # flat-III
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l1, self.m6, self.h4]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6'),HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')]))) # IV
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l1, self.mf6, self.h4]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'),HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')]))) # iv
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l2, self.m7, self.h5]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7'),HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5')]))) # V
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l2, self.mf7, self.h5]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7'),HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5')]))) # v
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l3, self.m1, self.h6]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6')]))) # vi
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.lf3, self.m1, self.hf6]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_AG, '-3'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6')]))) # flat-VI
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l4, self.m2, self.h7]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7')]))) # vii-dim
        #self.assertTrue(self.equalsMaker(harmony.reconciliation_func(pandas.Series([self.l4, self.m2, self.hf7]), \
                #HarmonicFunctionalChord(HarmonicFunctionalNote('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'), \
                #[HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),HarmonicFunctionalNote('C', harmony.FUNC_DOM, harmony.ROLE_AG, '-7')]))) # flat-VII

    def test_seventh_chords(self):
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h4, self.m7, self.m2, self.l5])),
                         [('C', harmony.FUNC_UNK, harmony.ROLE_UN,'4'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5')]) # V7
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h5, self.m7, self.m2, self.l4])),
                         [('C', harmony.FUNC_DOM, harmony.ROLE_BA, '5'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_AG, '7'),
                          ('C', harmony.FUNC_DOM, harmony.ROLE_AS, '2'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')]) # V4/2
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h3, self.m6, self.m1, self.l4])),
                         [('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '6'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')]) # IV7
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h4, self.mf6, self.m1, self.l3])),
                         [('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_AG, '-6'),
                          ('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3')]) # iv4/2

    def test_past_failures(self):
        # things that used to fail
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h4, self.m2, self.m3, self.l1])),
                         [('C', harmony.FUNC_UNK, harmony.ROLE_UN,'4'),
                          ('C', harmony.FUNC_UNK, harmony.ROLE_UN,'2'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1')])
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h4, self.m1, self.m3, self.l2])),
                         [('C', harmony.FUNC_UNK, harmony.ROLE_UN,'4'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),
                          ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                          ('C', harmony.FUNC_UNK, harmony.ROLE_UN,'2')])
        # ^4 | ^2 ^3 ^1 ==> S^T(4)
        # Note the ^1 could be correctly analyzed as T-bas or S-ass
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h1, self.m2, self.m3, self.l4])),
                         #[('C', harmony.FUNC_TON, harmony.ROLE_BA, '1'),
                          #('C', harmony.FUNC_UNK, harmony.ROLE_UN,'2'),
                          #('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                          #('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')])
                        [('C', harmony.FUNC_SUB, harmony.ROLE_AS, '1'),
                         ('C', harmony.FUNC_UNK, harmony.ROLE_UN,'2'),
                         ('C', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                         ('C', harmony.FUNC_SUB, harmony.ROLE_BA, '4')])
        # all associates non-functional
        self.assertEqual(harmony.reconciliation_func(pandas.Series([self.h5, self.m1, self.l2])),
                         [('C', harmony.FUNC_UNK, harmony.ROLE_UN,'5'),
                          ('C', harmony.FUNC_UNK, harmony.ROLE_UN,'1'),
                          ('C', harmony.FUNC_UNK, harmony.ROLE_UN,'2')])


class TestChordLabelIndexer(unittest.TestCase):
    def test_1(self):
        in_val = pandas.Series([('D', harmony.FUNC_TON, harmony.ROLE_BA, '1'),
                                ('D', harmony.FUNC_TON, harmony.ROLE_AS, '5'),
                                ('D', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                                ('D', harmony.FUNC_TON, harmony.ROLE_BA, '1')])
        expected = u'T(1)'
        self.assertEqual(expected, harmony.chord_label_func(in_val))
    
    def test_2(self):
        in_val = pandas.Series([('D', harmony.FUNC_TON, harmony.ROLE_BA, '1'),
                                ('D', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                                ('D', harmony.FUNC_SUB, harmony.ROLE_AG, '6'),
                                ('D', harmony.FUNC_TON, harmony.ROLE_BA, '1')])
        expected = u'T^S(1)'
        self.assertEqual(expected, harmony.chord_label_func(in_val))
    
    def test_3(self):
        in_val = pandas.Series([('D', harmony.FUNC_UNK, harmony.ROLE_UN, '2'),
                                ('D', harmony.FUNC_TON, harmony.ROLE_AG, '3'),
                                ('D', harmony.FUNC_SUB, harmony.ROLE_AG, '6'),
                                ('D', harmony.FUNC_TON, harmony.ROLE_BA, '1')])
        expected = u'T^S/U(1)'
        self.assertEqual(expected, harmony.chord_label_func(in_val))

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
SCALE_DEGREE_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestScaleDegreeIndexer)
POSS_FUNCS_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPossFuncsIndexer)
CHOOSE_FUNC_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestChooseFuncIndexer)
CHORD_LABEL_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestChordLabelIndexer)