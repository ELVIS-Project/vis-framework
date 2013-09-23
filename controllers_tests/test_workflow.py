#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_workflow.py
# Purpose:                Tests for the WorkflowController
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
"""
Tests for the WorkflowController
"""

from unittest import TestCase, TestLoader
import mock
#import pandas
from vis.controllers.workflow import WorkflowController
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import noterest  # , interval, ngram
#from vis.analyzers.experimenters import frequency


# pylint: disable=R0904
# pylint: disable=C0111
class WorkflowTests(TestCase):
    def test_init_1(self):
        # with a list of basestrings
        with mock.patch(u'vis.models.indexed_piece.IndexedPiece') as mock_ip:
            in_val = [u'help.txt', 'path.xml', u'why_you_do_this.rtf']
            a = WorkflowController(in_val)
            self.assertEqual(3, mock_ip.call_count)
            for val in in_val:
                mock_ip.assert_any_call(val)
            self.assertEqual(3, len(a._data))
            for each in a._data:
                self.assertTrue(isinstance(each, mock.MagicMock))

    def test_init_2(self):
        # with a list of IndexedPieces
        in_val = [IndexedPiece(u'help.txt'), IndexedPiece('path.xml'),
                  IndexedPiece(u'why_you_do_this.rtf')]
        a = WorkflowController(in_val)
        self.assertEqual(3, len(a._data))
        for each in a._data:
            self.assertTrue(each in in_val)

    def test_init_3(self):
        # with a mixed list of valid things
        in_val = [IndexedPiece(u'help.txt'), 'path.xml', u'why_you_do_this.rtf']
        a = WorkflowController(in_val)
        self.assertEqual(3, len(a._data))
        self.assertEqual(in_val[0], a._data[0])
        for each in a._data[1:]:
            self.assertTrue(isinstance(each, IndexedPiece))

    def test_init_4(self):
        # with mostly basestrings but a few ints
        in_val = [u'help.txt', 'path.xml', 4, u'why_you_do_this.rtf']
        a = WorkflowController(in_val)
        self.assertEqual(3, len(a._data))
        for each in a._data:
            self.assertTrue(isinstance(each, IndexedPiece))

    def test_load_1(self):
        # that "get_data" is called correctly on each thing
        a = WorkflowController([])
        a._data = [mock.MagicMock(spec=IndexedPiece) for _ in xrange(5)]
        a.load(u'pieces')
        for mock_piece in a._data:
            mock_piece.get_data.assert_called_once_with([noterest.NoteRestIndexer])

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
WORKFLOW_TESTS = TestLoader().loadTestsFromTestCase(WorkflowTests)
