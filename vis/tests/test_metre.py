#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers_tests/test_metre.py
# Purpose:                Tests for metre-related indexers.
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

# NB: These are for the "pylint" source file checker.
# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import mock
import pandas
from music21 import base, note, stream
from music21 import meter as m21_meter
from vis.analyzers.indexers import metre


class TestBeatStrengthIndexer(unittest.TestCase):
    def test_ind_func_1(self):
        # Test beatstrength_ind_func() with a mock
        expected = 0.5
        in_val = [mock.MagicMock(spec_set=base.Music21Object)]
        bs_mock = mock.PropertyMock(return_value=expected)
        type(in_val[0]).beatStrength = bs_mock
        actual = metre.beatstrength_ind_func(in_val)
        bs_mock.assert_called_once_with()
        self.assertEqual(expected, actual)

    def test_ind_func_2(self):
        # Test beatstrength_ind_func() with a real music21 object
        expected = 1.0
        a_meas = stream.Measure()
        a_meas.timeSignature = m21_meter.TimeSignature('3/4')
        a_meas.append(note.Note(quarterLength=0.5))
        in_val = a_meas.notes
        actual = metre.beatstrength_ind_func(in_val)
        self.assertEqual(expected, actual)

    def test_ind_func_3(self):
        # Test the whole indexer, in part to make sure the DataFrame is well-formatted
        expected = {'0': pandas.Series([1.0, 0.25, 0.5, 0.25, 0.5, 0.25, 1.0, 0.25, 0.5, 0.25],
                                       index=[x/2.0 for x in xrange(10)])}
        some_part = stream.Part([m21_meter.TimeSignature('3/4')])
        some_part.repeatAppend(note.Note(quarterLength=0.5), 10)
        actual = metre.NoteBeatStrengthIndexer([some_part]).run()['metre.NoteBeatStrengthIndexer']
        self.assertEqual(len(expected), len(actual.columns))
        for key in expected.iterkeys():
            self.assertTrue(key in actual)
            self.assertSequenceEqual(list(expected[key].index), list(actual[key].index))
            self.assertSequenceEqual(list(expected[key]), list(actual[key]))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
BEATSTRENGTH_INDEXER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestBeatStrengthIndexer)
