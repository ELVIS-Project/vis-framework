#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_indexed_piece.py
# Purpose:                Integration tests with the "bwv2.xml" file.
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
Integration tests with the "bwv2.xml" file.
"""

from unittest import TestCase, TestLoader
import pandas
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import noterest, interval, ngram
from vis.analyzers.experimenters import frequency


# pylint: disable=R0904
# pylint: disable=C0111
class AllVoiceIntervalNGrams(TestCase):
    twograms = [(0.0, u'[12 10 8] 4 [10 8 5]'),
                (1.0, u'[10 8 5] 2 [8 6 3]'),
                (2.0, u'[8 6 3] 2 [6 6 3]'),
                (3.0, u'[6 6 3] -2 [11 6 3]'),
                (4.0, u'[11 6 3] -2 [12 8 3]'),
                (4.5, u'[12 8 3] -2 [13 10 3]'),
                (5.0, u'[13 10 3] 1 [12 10 3]'),
                (5.5, u'[12 10 3] 2 [10 5 3]'),
                (6.0, u'[10 5 3] 1 [10 6 4]'),
                (6.5, u'[10 6 4] -4 [12 10 8]'),
                (7.0, u'[12 10 8] -4 [17 13 12]'),
                (8.0, u'[17 13 12] 2 [15 13 10]'),
                (9.0, u'[15 13 10] 2 [14 12 9]'),
                (9.5, u'[14 12 9] 2 [12 10 8]'),
                (10.0, u'[12 10 8] 1 [12 10 7]'),
                (10.5, u'[12 10 7] 2 [10 10 5]'),
                (11.0, u'[10 10 5] 1 [10 9 5]'),
                (11.5, u'[10 9 5] -2 [12 9 7]'),
                (12.0, u'[12 9 7] -2 [14 10 8]'),
                (12.5, u'[14 10 8] 1 [15 10 8]'),
                (12.75, u'[15 10 8] 2 [13 8 3]'),
                (13.0, u'[13 8 3] 1 [13 8 4]'),
                (13.5, u'[13 8 4] 1 [12 8 4]'),
                (14.0, u'[12 8 4] 1 [12 8 3]'),
                (14.5, u'[12 8 3] -5 [15 12 10]'),
                (15.0, u'[15 12 10] 6 [10 6 3]'),
                (16.0, u'[10 6 3] 2 [10 5 1]'),
                (17.0, u'[10 5 1] -2 [10 6 3]'),
                (17.5, u'[10 6 3] -2 [10 8 5]'),
                (18.0, u'[10 8 5] 5 [5 3 1]'),
                (19.0, u'[5 3 1] -2 [6 4 2]'),
                (19.5, u'[6 4 2] -2 [6 6 3]'),
                (20.0, u'[6 6 3] -2 [8 6 3]'),
                (20.5, u'[8 6 3] -2 [10 8 5]'),
                (21.0, u'[10 8 5] -2 [11 11 6]'),
                (21.5, u'[11 11 6] -2 [13 11 8]'),
                (22.0, u'[13 11 8] 1 [13 10 8]'),
                (22.5, u'[13 10 8] -2 [15 10 5]'),
                (23.0, u'[15 10 5] 4 [10 8 5]'),
                (24.0, u'[10 8 5] 1 [10 7 5]'),
                (24.5, u'[10 7 5] 2 [10 5 3]'),
                (25.0, u'[10 5 3] 1 [11 6 3]'),
                # With [15 10 13], the tenor is sounding higher than the alto. This continues
                # to the end of the piece.
                (25.5, u'[11 6 3] -4 [15 10 13]'),
                (26.0, u'[15 10 13] 2 [14 9 12]'),
                (26.5, u'[14 9 12] 2 [12 8 10]'),
                (27.0, u'[12 8 10] -5 [17 12 15]'),
                (28.0, u'[17 12 15] 2 [15 10 14]'),
                (28.5, u'[15 10 14] 2 [13 8 10]'),
                (29.0, u'[13 8 10] 2 [12 7 9]'),
                (29.5, u'[12 7 9] 2 [10 5 8]'),
                (30.0, u'[10 5 8] -5 [15 10 12]'),
                (31.0, u'[15 10 12] 8 [8 3 5]'),
                (32.0, u'[8 3 5] -2 [13 3 6]'),
                (33.0, u'[13 3 6] 2 [10 1 5]'),
                (34.0, u'[10 1 5] -2 [11 2 6]'),
                (34.5, u'[11 2 6] -2 [13 3 8]'),
                (35.0, u'[13 3 8] -2 [14 4 9]'),
                (35.5, u'[14 4 9] -2 [16 6 11]'),
                (36.0, u'[16 6 11] -2 [17 7 12]'),
                (36.5, u'[17 7 12] 2 [15 5 10]'),
                (37.0, u'[15 5 10] 1 [15 2 11]'),
                (37.5, u'[15 2 11] 1 [14 3 12]'),
                (38.0, u'[14 3 12] 2 [12 3 8]')]

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
        # test that all-voice interval 2-grams work
        ind_piece = IndexedPiece(u'vis/tests/corpus/bwv2.xml')
        setts = {u'quality': False, u'simple': False}
        horiz_ints = ind_piece.get_data([noterest.NoteRestIndexer,
                                         interval.HorizontalIntervalIndexer],
                                        setts)
        vert_ints = ind_piece.get_data([noterest.NoteRestIndexer,
                                         interval.IntervalIndexer],
                                        setts)
        parts = [vert_ints[u'0,3'],
                 vert_ints[u'1,3'],
                 vert_ints[u'2,3'],
                 horiz_ints[3]]
        setts[u'vertical'] = [0, 1, 2]
        setts[u'horizontal'] = [3]
        setts[u'mark singles'] = False
        setts[u'continuer'] = u'1'
        setts[u'n'] = 2
        actual = ind_piece.get_data([ngram.NGramIndexer], setts, parts)
        self.assertEqual(1, len(actual))
        actual = actual[0]
        expected = AllVoiceIntervalNGrams.series_maker(AllVoiceIntervalNGrams.twograms)
        self.assertSequenceEqual(list(expected.index), list(actual.index))
        self.assertSequenceEqual(list(expected), list(actual))
        # TODO: add a frequency part

    #def test_ngrams_2(self):
        ## test frequency of bass-voice motion
        #ind_piece = IndexedPiece(u'vis/tests/corpus/bwv2.xml')
        #setts = {u'quality': True, u'simple': False}
        #actual = ind_piece.get_data([noterest.NoteRestIndexer,
                                         #interval.HorizontalIntervalIndexer,
                                         #frequency.FrequencyExperimenter],
                                        #setts)
        ## choose only the bass voice
        #actual = actual[u'[7, 3]']
        ##self.assertEqual(1, len(actual))
        ##actual = actual[0]
        #print(str(actual))  # DEBUG
        ## TODO: add a frequency part

    #def test_ngrams_3(self):
        ## test frequency of all-voice interval 1-grams
        #ind_piece = IndexedPiece(u'vis/tests/corpus/bwv2.xml')
        #setts = {u'quality': False, u'simple': False}
        #horiz_ints = ind_piece.get_data([noterest.NoteRestIndexer,
                                         #interval.HorizontalIntervalIndexer],
                                        #setts)
        #vert_ints = ind_piece.get_data([noterest.NoteRestIndexer,
                                         #interval.IntervalIndexer],
                                        #setts)
        #parts = [vert_ints[u'0,3'],
                 #vert_ints[u'1,3'],
                 #vert_ints[u'2,3'],
                 #horiz_ints[3]]
        #setts[u'vertical'] = [0, 1, 2]
        #setts[u'horizontal'] = [3]
        #setts[u'mark singles'] = False
        #setts[u'continuer'] = u'P1'
        #setts[u'n'] = 1
        #actual = ind_piece.get_data([ngram.NGramIndexer, frequency.FrequencyExperimenter], setts, parts)
        ##self.assertEqual(1, len(actual))
        ##actual = actual[0]
        #print(str(actual))  # DEBUG
        ## TODO: add a frequency part

#-------------------------------------------------------------------------------------------------#
# Definitions                                                                                     #
#-------------------------------------------------------------------------------------------------#
ALL_VOICE_INTERVAL_NGRAMS = TestLoader().loadTestsFromTestCase(AllVoiceIntervalNGrams)
