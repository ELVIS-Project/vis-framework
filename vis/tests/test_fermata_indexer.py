#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_fermata_indexer.py
# Purpose:                Test indexing of fermatas.
#
# Copyright (C) 2013, 2014 Christopher Antila, Ryan Bannon
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
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import fermata
from vis import workflow
from numpy import isnan, NaN

# get the path to the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]


# pylint: disable=R0904
# pylint: disable=C0111
class AllVoiceFermatas(TestCase):

    def createExpectedFermataIndexerResult(self, number_of_parts, number_of_indices):
        """
        Returns expected data-frame (in the fermata.FermataIndexer 'style') with correct
        Fermata placement.
        """
        expected_data = [[NaN] * number_of_indices] * number_of_parts
        tuples = [(u'fermata.FermataIndexer', str(i)) for i in xrange(number_of_parts)]
        multiindex = pandas.MultiIndex.from_tuples(tuples, names=['Indexer', 'Parts'])
        expected = pandas.DataFrame(data = expected_data, index = multiindex, dtype = object)
        expected.set_value(('fermata.FermataIndexer', '0'), 10, 'Fermata')
        expected.set_value(('fermata.FermataIndexer', '3'), 10, 'Fermata')
        expected.set_value(('fermata.FermataIndexer', '0'), 19, 'Fermata')
        expected.set_value(('fermata.FermataIndexer', '3'), 19, 'Fermata')
        expected.set_value(('fermata.FermataIndexer', '0'), 31, 'Fermata')
        expected.set_value(('fermata.FermataIndexer', '3'), 31, 'Fermata')
        expected.set_value(('fermata.FermataIndexer', '0'), 46, 'Fermata')
        expected.set_value(('fermata.FermataIndexer', '3'), 46, 'Fermata')
        expected = expected.T
        expected = expected.drop(expected.index[[11, 12, 20, 32]])
        return expected

    def assertDataFramesEqual(self, exp, act):
        """Ensure that two DataFrame objects, ``exp`` and ``act``, are equal."""
        self.assertSequenceEqual(list(exp.columns), list(act.columns))
        for col_name in exp.columns:
            for loc_val in exp[col_name].index:
                self.assertTrue(loc_val in act.index)

                # Value check.
                if exp[col_name].loc[loc_val] != act[col_name].loc[loc_val]:

                    # Might be NaNs. Check.
                    if isnan(exp[col_name].loc[loc_val]) and isnan(act[col_name].loc[loc_val]):
                        continue

                    msg = '"{}" is {} but we expected {}'
                    raise AssertionError(msg.format(loc_val,
                                                    exp[col_name].loc[loc_val],
                                                    act[col_name].loc[loc_val]))

    def test_fermata_indexer_1(self):
        """all-voice fermatas; no WorkflowManager"""
        expected = self.createExpectedFermataIndexerResult(4, 47)
        ind_piece = IndexedPiece(os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv603.xml'))
        actual = ind_piece.get_data([fermata.FermataIndexer])
        self.assertDataFramesEqual(expected, actual)

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
FERMATA_INDEXER_SUITE = TestLoader().loadTestsFromTestCase(AllVoiceFermatas)
