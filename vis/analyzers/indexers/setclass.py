#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/contour.py
# Purpose:                Set Class Filter
#
# Copyright (C) 2016 Marina Borsodi-Benson
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
.. codeauthor:: Marina Borsodi-Benson <marinaborsodibenson@gmail.com>

"""

import music21
import pandas
from vis.analyzers import indexer
from vis.analyzers.indexers import repeat


# def from_intvls(intervals):

def from_horiz(score, length):

    chords = []
    for part in score:
        part_c = []
        part = score[part].dropna().tolist()
        while 'Rest' in part:
            part.remove('Rest')
        for y in range(len(part) - length):
            chord = []
            x = 0
            for x in range(length):
                chord.append(part[y + x])
                x += 1
            part_c.append(chord)
        chords.append(part_c)
    return chords


def makeChord(chord):

    new_chord = map(music21.note.Note, chord)
    return music21.chord.Chord(new_chord)


def from_vert(score):

    chords = []
    for part in score.columns.values:
        chords.append(score[part].tolist())

    return zip(*chords)


def from_notes(tuples):

    chords = map(makeChord, tuples)
    # for chord in tuples:
    #     chord = list(chord)
    #     chords.append(chord)

    return chords


class SetClassIndexer(indexer.Indexer):

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['label', 'length', 'type']

    _MISSING_SETTINGS = 'SetClassIndexer is missing required settings'
    _WRONG_LENGTH = 'The "length" setting must be between 1 and 12'

    def __init__(self, score, settings=None):
        """
        :keyword 'label': This is the label of the dataframe, whether the
            score stems from data retrieved by the noterest indexer or one of
            the interval indexers. The options are 'noterest' or 'interval'.
        :type 'label': str
        :keyword 'length': This is the desired length of note sequences when
            looking at horizontally occuring set classes. Must be between the
            numbers 1 and 12, inclusive.
        :type 'length': int
        :keyword 'type': This is the type of analysis you want to do, either
            looking at 'horizontal' or 'vertical' events.
        :type 'type': str
        """

        if 'label' not in settings or 'type' not in settings:
            raise RuntimeError(self._MISSING_SETTINGS)
        else:
            self._settings = settings

        if settings['type'] is 'horizontal':

            if 'length' not in settings:
                raise RuntimeError(self._MISSING_SETTINGS)

            elif settings['length'] > 12 or settings['length'] < 1:
                raise RuntimeError(self._WRONG_LENGTH)

        super(SetClassIndexer, self).__init__(score, None)

        self._score = self._score.fillna(method='ffill')

        if settings['type'] is 'horizontal' and settings['label'] is 'noterest':
            self._score = repeat.FilterByRepeatIndexer(self._score).run()

    def run(self):
        """
        :returns: Make a new index of the set classes in the piece.
        :rtype: :class:`pandas.DataFrame`
        """
        # types = {'interval': {'horizontal':, 'vertical'}, 'noterest': {'horizontal': , 'vertical'}}

        if self._settings['type'] is 'horizontal':
            note_col = from_horiz(self._score, self._settings['length'])
        else:
            note_col = from_vert(self._score)

        if self._settings['label'] is 'noterest':
            chords = []
            from_notes(note_col)
        else:
            chords = from_intvls(note_col)


        # chords = []
        # for each in from_horiz(self._score, 4):
        #     part = []
        #     for thing in from_notes(each):
        #         part.append(makeChord(thing))
        #     chords.append(part)

        # comb = []
        # for part in chords:
        #     comb.append(pandas.Series(part, index=self._score.index[:len(self._score.index)-4]))



























