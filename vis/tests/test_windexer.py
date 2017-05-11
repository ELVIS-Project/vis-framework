
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_windexer.py
# Purpose:                Test indexing of the windexer.
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
from vis.analyzers.indexers import windexer
import vis


def make_dataframe(labels, indices, name):
    ret = pandas.concat(indices, levels=labels, axis=1)
    iterables = (name, labels)
    multi_index = pandas.MultiIndex.from_product(iterables, names=('Indexer', 'Parts'))
    ret.columns = multi_index
    return ret


index = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]

notes = ['D5', 'E5', 'E5', 'D5', 'C5', 'B4']

note_name = 'noterest.NoteRestIndexer'
result = pandas.DataFrame({'0': pandas.Series(data=notes, index=index)})
NOTES = make_dataframe(result.columns.values, [result[name] for name in result.columns], note_name)


index = [1.0, 1.5, 2.0, 2.5, 1.5, 2.0, 2.5, 3.0, 2.0, 2.5, 3.0, 3.5]

notes = ['D5', 'E5', 'E5', 'D5', 'E5', 'E5', 'D5', 'C5', 'E5', 'D5', 'C5', 'B4']

note_name = 'noterest.NoteRestIndexer'
result = pandas.DataFrame({'0': pandas.Series(data=notes, index=index)})
WINDOW4 = make_dataframe(result.columns.values, [result[name] for name in result.columns], note_name)


index = [1.0, 1.5, 2.0, 1.5, 2.0, 2.5, 2.0, 2.5, 3.0, 2.5, 3.0, 3.5]

notes = ['D5', 'E5', 'E5', 'E5', 'E5', 'D5', 'E5', 'D5', 'C5', 'D5', 'C5', 'B4']

note_name = 'noterest.NoteRestIndexer'
result = pandas.DataFrame({'0': pandas.Series(data=notes, index=index)})
WINDOW3 = make_dataframe(result.columns.values, [result[name] for name in result.columns], note_name)


class TestWindexer(TestCase):

    def test_run(self):
        actual = windexer.Windexer(NOTES).run()
        self.assertTrue(actual.equals(WINDOW4))

    def test_run2(self):
        actual = windexer.Windexer(NOTES, {'window_size': 3}).run()
        self.assertTrue(actual.equals(WINDOW3))

    def test_init4(self):

        setts = {'window_size': 465}
        self.assertRaises(RuntimeError, windexer.Windexer, NOTES, setts)
        try:
            windexer.Windexer(NOTES, setts)
        except RuntimeError as run_err:
            self.assertEqual(windexer.Windexer._BIG_WINDOW, run_err.args[0])



#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
WINDEXER_SUITE = TestLoader().loadTestsFromTestCase(TestWindexer)
