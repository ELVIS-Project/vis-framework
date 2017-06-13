#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_indexed_piece.py
# Purpose:                Integration tests with the "bwv2.xml" file.
#
# Copyright (C) 2013, 2014, 2016 Christopher Antila, Alexander Morgan
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
Integration tests with the "bwv2.xml" file.
"""

import os
from unittest import TestCase, TestLoader
import pandas
from vis.models.indexed_piece import Importer, IndexedPiece
from vis.analyzers.indexers import noterest, interval, ngram
from vis.analyzers.experimenters import frequency
from vis import workflow

# get the path to the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]


# pylint: disable=R0904
# pylint: disable=C0111
class AllVoiceIntervalNGrams(TestCase):
    two_grams = [(0.0, '[12 10 8] (4) [10 8 5]'),
                (1.0, '[10 8 5] (2) [8 6 3]'),
                (2.0, '[8 6 3] (2) [6 6 3]'),
                (3.0, '[6 6 3] (-2) [11 6 3]'),
                (4.0, '[11 6 3] (-2) [12 8 3]'),
                (4.5, '[12 8 3] (-2) [13 10 3]'),
                (5.0, '[13 10 3] (1) [12 10 3]'),
                (5.5, '[12 10 3] (2) [10 5 3]'),
                (6.0, '[10 5 3] (1) [10 6 4]'),
                (6.5, '[10 6 4] (-4) [12 10 8]'),
                (7.0, '[12 10 8] (-4) [17 13 12]'),
                (8.0, '[17 13 12] (2) [15 13 10]'),
                (9.0, '[15 13 10] (2) [14 12 9]'),
                (9.5, '[14 12 9] (2) [12 10 8]'),
                (10.0, '[12 10 8] (1) [12 10 7]'),
                (10.5, '[12 10 7] (2) [10 10 5]'),
                (11.0, '[10 10 5] (1) [10 9 5]'),
                (11.5, '[10 9 5] (-2) [12 9 7]'),
                (12.0, '[12 9 7] (-2) [14 10 8]'),
                (12.5, '[14 10 8] (1) [15 10 8]'),
                (12.75, '[15 10 8] (2) [13 8 3]'),
                (13.0, '[13 8 3] (1) [13 8 4]'),
                (13.5, '[13 8 4] (1) [12 8 4]'),
                (14.0, '[12 8 4] (1) [12 8 3]'),
                (14.5, '[12 8 3] (-5) [15 12 10]'),
                (15.0, '[15 12 10] (6) [10 6 3]'),
                (16.0, '[10 6 3] (2) [10 5 1]'),
                (17.0, '[10 5 1] (-2) [10 6 3]'),
                (17.5, '[10 6 3] (-2) [10 8 5]'),
                (18.0, '[10 8 5] (5) [5 3 1]'),
                (19.0, '[5 3 1] (-2) [6 4 2]'),
                (19.5, '[6 4 2] (-2) [6 6 3]'),
                (20.0, '[6 6 3] (-2) [8 6 3]'),
                (20.5, '[8 6 3] (-2) [10 8 5]'),
                (21.0, '[10 8 5] (-2) [11 11 6]'),
                (21.5, '[11 11 6] (-2) [13 11 8]'),
                (22.0, '[13 11 8] (1) [13 10 8]'),
                (22.5, '[13 10 8] (-2) [15 10 5]'),
                (23.0, '[15 10 5] (4) [10 8 5]'),
                (24.0, '[10 8 5] (1) [10 7 5]'),
                (24.5, '[10 7 5] (2) [10 5 3]'),
                (25.0, '[10 5 3] (1) [11 6 3]'),
                # With [15 10 13], the tenor is sounding higher than the alto. This continues
                # to the end of the piece.
                (25.5, '[11 6 3] (-4) [15 10 13]'),
                (26.0, '[15 10 13] (2) [14 9 12]'),
                (26.5, '[14 9 12] (2) [12 8 10]'),
                (27.0, '[12 8 10] (-5) [17 12 15]'),
                (28.0, '[17 12 15] (2) [15 10 14]'),
                (28.5, '[15 10 14] (2) [13 8 10]'),
                (29.0, '[13 8 10] (2) [12 7 9]'),
                (29.5, '[12 7 9] (2) [10 5 8]'),
                (30.0, '[10 5 8] (-5) [15 10 12]'),
                (31.0, '[15 10 12] (8) [8 3 5]'),
                (32.0, '[8 3 5] (-2) [13 3 6]'),
                (33.0, '[13 3 6] (2) [10 1 5]'),
                (34.0, '[10 1 5] (-2) [11 2 6]'),
                (34.5, '[11 2 6] (-2) [13 3 8]'),
                (35.0, '[13 3 8] (-2) [14 4 9]'),
                (35.5, '[14 4 9] (-2) [16 6 11]'),
                (36.0, '[16 6 11] (-2) [17 7 12]'),
                (36.5, '[17 7 12] (2) [15 5 10]'),
                (37.0, '[15 5 10] (1) [15 2 11]'),
                (37.5, '[15 2 11] (1) [14 3 12]'),
                (38.0, '[14 3 12] (2) [12 3 8]')]

    @staticmethod
    def series_maker(make_series):
        """
        Convert an iterable of 2-tuples into a pandas.Series. Each 2-tuple should have the "index"
        value at index 0 and the "value" itself at index 1.
        """
        post_ind = []
        post_vals = []
        for each in make_series:
            post_ind.append(each[0])
            post_vals.append(each[1])
        return pandas.Series(post_vals, index=post_ind)

    def test_ngrams_1(self):
        """Ngram integration test."""
        expected = AllVoiceIntervalNGrams.series_maker(AllVoiceIntervalNGrams.two_grams)
        expected = pandas.DataFrame({('ngram.NGramIndexer', 'Soprano,Bass Alto,Bass Tenor,Bass : Bass'): expected})
        ind_piece = Importer(os.path.join(VIS_PATH, 'tests', 'corpus', 'bwv2.xml'))
        setts = {'quality': False, 'simple': False, 'horiz_attach_later': True}
        horiz_ints = ind_piece.get_data('horizontal_interval', settings=setts)
        vert_ints = ind_piece.get_data('vertical_interval', settings=setts)
        setts = {'n': 2, 'continuer': '1', 'horizontal': 'lowest',
                 'vertical': [('Soprano,Bass', 'Alto,Bass', 'Tenor,Bass')], 'brackets': True,}
        actual = ind_piece.get_data('ngram', data=(vert_ints, horiz_ints), settings=setts)
        self.assertTrue(actual.equals(expected))

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
ALL_VOICE_INTERVAL_NGRAMS = TestLoader().loadTestsFromTestCase(AllVoiceIntervalNGrams)
