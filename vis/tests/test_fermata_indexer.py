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
from six.moves import range  # pylint: disable=import-error,redefined-builtin
from vis.models.indexed_piece import Importer, IndexedPiece
from vis.analyzers.indexers import fermata
# get the path to the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]


# pylint: disable=R0904
# pylint: disable=C0111
class AllVoiceFermatas(TestCase):

    def test_fermata_indexer_1(self):
        """all-voice fermatas; no WorkflowManager"""
        # Create expected.
        parts = [pandas.Series(['Fermata']*4, index=[10,19,31,46]),
                 pandas.Series(), pandas.Series(),
                 pandas.Series(['Fermata']*4, index=[10,19,31,46])]        
        expected = pandas.concat(parts, axis=1)
        indx = pandas.Index(range(47))
        expected = expected.reindex(index=indx)
        expected.drop([11, 12, 20, 32], inplace=True)

        # Test.
        ind_piece = Importer(os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv603.xml'))
        expected.columns = ind_piece.metadata('parts')
        actual = ind_piece._get_fermata()
        self.assertTrue(actual['fermata.FermataIndexer'].equals(expected))

    def test_fermata_indexer_2(self):
        """rest fermatas; no WorkflowManager"""
        # Create expected.
        temp = [pandas.Series(['Fermata'], index=[6]), pandas.Series(['Fermata'], index=[6])]
        expected = pandas.concat(temp, axis=1).reindex(pandas.Index([0,1,2,3,4,6]))
        # Test.
        ind_piece = Importer(os.path.join(VIS_PATH, 'tests', 'corpus', 'test_fermata_rest.xml'))
        expected.columns = ind_piece.metadata('parts')
        actual = ind_piece._get_fermata()
        self.assertTrue(actual['fermata.FermataIndexer'].equals(expected))

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
FERMATA_INDEXER_SUITE = TestLoader().loadTestsFromTestCase(AllVoiceFermatas)
