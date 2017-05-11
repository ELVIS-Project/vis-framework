
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_over_bass.py
# Purpose:                Test indexing of over the bass indexer.
#
# Copyright (C) 2016 Marina Cottrell
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

import os
from unittest import TestCase, TestLoader
import pandas
from vis.analyzers.indexers import over_bass
import vis


def make_dataframe(labels, indices, name):
    ret = pandas.concat(indices, levels=labels, axis=1)
    iterables = (name, labels)
    multi_index = pandas.MultiIndex.from_product(iterables, names=('Indexer', 'Parts'))
    ret.columns = multi_index
    return ret



index = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 8.0, 9.0, 9.5, 10.0]

horizontal = [['M2', 'P1', '-M2', '-M2', '-m2', 'm2', 'M2', 'P1', '-M2', '-m2', 'm2', 'P1', '-m2', '-M2', 'M2', 'P1', 'm2'], 
        ['P1', 'P1', '-m2', 'P1', 'm2', 'P1', '-m2', 'P1', '-M2', 'm3', 'P1', '-m2', 'm2', 'M2', '-M2', 'P1', 'P1'],
        ['m2', '-m2', '-M2', 'P1', 'P5', 'P1', '-P5', 'M2', 'm2', 'M3', '-M2', 'P1', 'P1', 'P1', 'P1', 'P1', '-P5'],
        ['-P5', 'P1', 'M2', 'P1', 'M2', 'P1', 'M2', 'm2', 'M2', 'P1', '-P5', 'P1', 'P4', '-m2', 'm2', '-m2', '-M2']]

horiz_name = 'interval.HorizontalIntervalIndexer'

result = pandas.DataFrame({str(x): pandas.Series([intvl for intvl in horizontal[x]], index=index) for x in range(len(horizontal))})
HORIZ = make_dataframe(result.columns.values, [result[name] for name in result.columns], horiz_name)

vertical = [['P5', 'M6', 'M6', 'm6', 'd5', 'M3', 'P4', 'm6', 'm6', 'm6', 'M3', 'P4', 'd5', 'M3', 'P1', 'M3', 'M3'], 
        ['m3', 'M3', 'P4', 'P4', 'm3', 'P5', 'm6', 'P4', 'm3', 'P8', 'P5', 'm7', 'm7', 'M6', 'P5', 'M6', 'M6'], 
        ['P5', 'M3', 'M3', 'P8', 'm7', 'P5', 'm6', 'm6', 'P5', 'm3', 'M2', 'm7', 'm7', 'M3', 'm3', 'M3', 'P4'],
        ['m6', 'P5', 'm6', 'M6', 'M6', 'm3', 'm3', 'M6', 'P5', 'M3', 'm3', 'P4', 'M3', 'P4', 'P5', 'P4', 'P4'], 
        ['P8', 'P5', 'P5', 'M3', 'M3', 'm3', 'm3', 'P8', 'M7', 'P5', 'm7', 'P4', 'M3', 'P8', 'm3', 'P8', 'm2'], 
        ['M3', 'P8', 'M7', 'P5', 'P5', 'P8', 'P8', 'm3', 'M3', 'm3', 'P5', 'P8', 'P8', 'P5', 'm6', 'P5', 'm6']]

vert_name = 'interval.IntervalIndexer'
label = ['0,1', '0,2', '0,3', '1,2', '1,3', '2,3']

result = pandas.DataFrame({label[x]: pandas.Series([intvl for intvl in vertical[x]], index=index) for x in range(len(label))})
VERT = make_dataframe(result.columns.values, [result[name] for name in result.columns], vert_name)

overs = [['-P5', 'P1', 'M2', 'P1', 'M2', 'P1', 'M2', 'm2', 'M2', 'P1', '-P5', 'P1', 'P4', '-m2', 'm2', '-m2', '-M2'],
        ['P5', 'M3', 'M3', 'P8', 'm7', 'P5', 'm6', 'm6', 'P5', 'm3', 'M2', 'm7', 'm7', 'M3', 'm3', 'M3', 'P4'],
        ['P8', 'P5', 'P5', 'M3', 'M3', 'm3', 'm3', 'P8', 'M7', 'P5', 'm7', 'P4', 'M3', 'P8', 'm3', 'P8', 'm2'],
        ['M3', 'P8', 'M7', 'P5', 'P5', 'P8', 'P8', 'm3', 'M3', 'm3', 'P5', 'P8', 'P8', 'P5', 'm6', 'P5', 'm6']]


label = '3 0,3 1,3 2,3'
over_name = 'over_bass.OverBassIndexer'

result = pandas.DataFrame({label: pandas.Series([str(intvl) for intvl in list(zip(*overs))], index=index)})
EXPECTED = make_dataframe(result.columns.values, [result[name] for name in result.columns], over_name)

notes = [['D5', 'E5', 'E5', 'D5', 'C5', 'B4', 'C5', 'D5', 'D5', 'C5', 'B4', 'C5', 'C5', 'B4', 'A4', 'B4', 'B4'], 
        ['G4', 'G4', 'G4', 'F#4', 'F#4', 'G4', 'G4', 'F#4', 'F#4', 'E4', 'G4', 'G4', 'F#4', 'G4', 'A4', 'G4', 'G4'], 
        ['B3', 'C4', 'B3', 'A3', 'A3', 'E4', 'E4', 'A3', 'B3', 'C4', 'E4', 'D4', 'D4', 'D4', 'D4', 'D4', 'D4'], 
        ['G3', 'C3', 'C3', 'D3', 'D3', 'E3', 'E3', 'F#3', 'G3', 'A3', 'A3', 'D3', 'D3', 'G3', 'F#3', 'G3', 'F#3']]

label = ['0', '1', '2', '3']
note_name = 'noterest.NoteRestIndexer'

result = pandas.DataFrame({label[x]: pandas.Series([intvl for intvl in notes[x]], index=index) for x in range(len(label))})
NOTES = make_dataframe(result.columns.values, [result[name] for name in result.columns], note_name)

for_notes = [['G3', 'C3', 'C3', 'D3', 'D3', 'E3', 'E3', 'F#3', 'G3', 'A3', 'A3', 'D3', 'D3', 'G3', 'F#3', 'G3', 'F#3'],
            ['P5', 'M3', 'M3', 'P8', 'm7', 'P5', 'm6', 'm6', 'P5', 'm3', 'M2', 'm7', 'm7', 'M3', 'm3', 'M3', 'P4'],
            ['P8', 'P5', 'P5', 'M3', 'M3', 'm3', 'm3', 'P8', 'M7', 'P5', 'm7', 'P4', 'M3', 'P8', 'm3', 'P8', 'm2'],
            ['M3', 'P8', 'M7', 'P5', 'P5', 'P8', 'P8', 'm3', 'M3', 'm3', 'P5', 'P8', 'P8', 'P5', 'm6', 'P5', 'm6']]

label = '3 0,3 1,3 2,3'
over_name = 'over_bass.OverBassIndexer'

result = pandas.DataFrame({label: pandas.Series([str(intvl) for intvl in list(zip(*for_notes))], index=index)})
EXPECTED_NOTES = make_dataframe(result.columns.values, [result[name] for name in result.columns], over_name)


class TestOverBassIndexer(TestCase):

    def test_init1(self):
        """that __init__() works properly without settings given"""

        actual = over_bass.OverBassIndexer([NOTES, VERT])
        self.assertEqual(actual._settings, {'type': 'notes', 'horizontal': 3})
        self.assertEqual(actual.horizontal_voice, 3)

    def test_init2(self):
        """that __init__() works properly with interval setting"""

        setts = {'type': 'intervals'}
        actual = over_bass.OverBassIndexer([HORIZ, VERT], setts).run()
        self.assertEqual(list(actual.columns), list(EXPECTED.columns))

    def test_init4(self):
        """that __init__() fails when the horizontal setting is not an available option"""

        setts = {'horizontal': 5}
        self.assertRaises(RuntimeError, over_bass.OverBassIndexer, [NOTES, VERT], setts)
        try:
            over_bass.OverBassIndexer([NOTES, VERT], setts)
        except RuntimeError as run_err:
            self.assertEqual(over_bass.OverBassIndexer._WRONG_HORIZ, run_err.args[0])

    def test_init5(self):
        """that __init__() fails when the given type doesn't match the given dataframe"""

        setts = {'type': 'notes'}
        self.assertRaises(RuntimeError, over_bass.OverBassIndexer, [HORIZ, VERT], setts)
        try:
            over_bass.OverBassIndexer([HORIZ, VERT], setts)
        except RuntimeError as run_err:
            self.assertEqual(over_bass.OverBassIndexer._WRONG_TYPE, run_err.args[0])

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
OVER_BASS_INDEXER_SUITE = TestLoader().loadTestsFromTestCase(TestOverBassIndexer)
