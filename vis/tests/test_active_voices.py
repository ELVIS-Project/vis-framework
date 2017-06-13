#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_cadence.py
# Purpose:                Test indexing of cadence indexer.
#
# Copyright (C) 2016 Marina Cottrell, Alexander Morgan
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

from unittest import TestCase, TestLoader
import pandas
from vis.analyzers.indexers import active_voices
from vis.models.indexed_piece import IndexedPiece


class TestActiveVoicesIndexer(TestCase):

    def setUp(self):

        def make_dataframe(labels, indices, name):
            ret = pandas.concat(indices, levels=labels, axis=1)
            iterables = (name, labels)
            multi_index = pandas.MultiIndex.from_product(iterables, names=('Indexer', 'Parts'))
            ret.columns = multi_index
            return ret

        indices = [[0.0, 1.0, 1.5, 3.0, 3.5, 4.0, 7.5],
                   [0.0, 1.0, 1.5, 2.5, 3.5, 4.0, 4.5, 6.0],
                   [0.5, 1.5, 3.0, 3.5, 4.0, 5.0, 6.0],
                   [0.0, 2.5, 4.0, 7.5]]
        notes = [['G4', 'D4', 'G4', 'Rest', 'B4', 'D5', 'C5'],
                 ['G4', 'D4', 'Rest', 'B4', 'D5', 'C5', 'Rest', 'Rest'],
                 ['B4', 'D5', 'C5', 'Rest', 'Rest', 'D3', 'F3'],
                 ['B4', 'D5', 'C5', 'Rest']]

        name = 'noterest.NoteRestIndexer'
        results = []
        for x in range(len(indices)):
            results.append(pandas.Series(notes[x], index=indices[x], name=str(x)))
        result = pandas.concat(results, axis=1)
        self.NOTES = make_dataframe(result.columns.values, [result[nam] for nam in result.columns], name)

        indices = [0.0, 0.5, 1.5, 2.5, 3.0, 4.5, 5.0, 7.5]
        show_indices = [0.0, 0.5, 1.0, 1.5, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.5]
        att_indices = [0.0, 0.5, 1.0, 3.0, 3.5, 4.0, 4.5, 5.0]
        att_voices = [3, 1, 2, 1, 2, 3, 0, 1]
        voices = [3, 4, 3, 4, 3, 2, 3, 2]
        show_voices = [3, 4, 4, 3, 4, 3, 3, 3, 2, 3, 3, 2]
        title = 'active_voices.ActiveVoicesIndexer'

        result = pandas.DataFrame(pandas.Series(voices, indices, name='Active Voices'))
        self.EXPECTED = make_dataframe(result.columns.values, [result[name] for name in result.columns], title)

        result = pandas.DataFrame(pandas.Series(att_voices, att_indices, name='Active Voices'))
        self.ATT_EXPECTED = make_dataframe(result.columns.values, [result[name] for name in result.columns], title)

        result = pandas.DataFrame(pandas.Series(show_voices, show_indices, name='Active Voices'))
        self.SHOW_EXPECTED = make_dataframe(result.columns.values, [result[name] for name in result.columns], title)

    def tearDown(self):

        self.NOTES = None
        self.EXPECTED = None
        self.ATT_EXPECTED = None
        self.SHOW_EXPECTED = None

    def test_init1(self):
        """tests that __init__() works with no settings given"""
        actual = active_voices.ActiveVoicesIndexer(self.NOTES)
        self.assertEqual(actual._settings, {'attacked': False, 'show_all': False})

    def test_init2(self):
        """test that __init__() works with all settings given"""
        settings = {'attacked': True, 'show_all': True}
        actual = active_voices.ActiveVoicesIndexer(self.NOTES, settings)
        self.assertEqual(actual._settings, settings)

    def test_active(self):
        """tests that it gives the right results with no settings and that the get_data()
        method properly calls active_voices"""
        ip = IndexedPiece()
        ip._analyses['noterest'] = self.NOTES
        actual = ip.get_data('active_voices')
        self.assertTrue(actual.equals(self.EXPECTED))

    def test_with_data(self):
        """tests that it gives the right results with no settings and that the get_data()
        method properly calls active_voices"""
        ip = IndexedPiece()
        actual = ip.get_data('active_voices', data=self.NOTES)
        self.assertTrue(actual.equals(self.EXPECTED))

    def test_attacked(self):
        """tests that it gives the right results with attacked set to true"""
        settings = {'attacked': True}
        ip = IndexedPiece()
        ip._analyses['noterest'] = self.NOTES
        actual = ip.get_data('active_voices', settings=settings)
        self.assertTrue(actual.equals(self.ATT_EXPECTED))

    def test_show(self):
        """tests that the ``show_all`` argument works when True"""
        settings = {'show_all': True}
        ip = IndexedPiece()
        ip._analyses['noterest'] = self.NOTES
        actual = ip.get_data('active_voices', settings=settings)
        self.assertTrue(actual.equals(self.SHOW_EXPECTED))


ACTIVE_VOICES_INDEXER_SUITE = TestLoader().loadTestsFromTestCase(TestActiveVoicesIndexer)
