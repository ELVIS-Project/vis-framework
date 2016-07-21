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


def from_intvls(intervals):

    chords = []
    for intvls in intervals:
        note = music21.note.Note('c')
        chord = [note]
        for intvl in intvls:
            if intvl != 'Rest':
                note = note.transpose(music21.interval.Interval(intvl))
                chord.append(note)
        chords.append(chord)

    chords = map(music21.chord.Chord, chords)
    return chords


def from_horiz(score, length):

    chords = []
    indices = []
    for part in score:
        part_c = []
        part = score[part].dropna()
        part = part[part != 'Rest']
        index = part.index.tolist()
        part = part.tolist()
        for y in range(len(part) - length):
            chord = []
            x = 0
            for x in range(length):
                chord.append(part[y + x])
                x += 1
            part_c.append(chord)
        chords.append(part_c)
        indices.append(index[:-length])
    return {'chords': chords, 'indices': indices}


def makeChord(chord):

    chord = list(chord)
    while 'Rest' in chord:
        chord.remove('Rest')
    new_chord = map(music21.note.Note, chord)
    return music21.chord.Chord(new_chord)


def from_vert(score):

    chords = []
    for part in score.columns.values:
        chords.append(score[part].tolist())

    return zip(*chords)


def from_notes(tuples):

    chords = map(makeChord, tuples)

    return chords


def forteClass(chord):

    return chord.forteClass


def orderedPitchClassesString(chord):

    return chord.orderedPitchClassesString


def forteClassTnI(chord):

    return chord.forteClassTnI


def normalForm(chord):

    return chord.normalForm


def primeFormString(chord):

    return chord.primeFormString


def intervalVector(chord):

    return chord.intervalVector


class SetClassIndexer(indexer.Indexer):

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['label', 'length', 'type', 'forteType']

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
        :keyword 'forteType': The music21 function you want to view the
            setclass through.
        :type 'forteType': str
        """

        if settings is None or 'label' not in settings or 'type' not in settings or 'forteType' not in settings:
            raise RuntimeError(self._MISSING_SETTINGS)
        else:
            self._settings = settings

        name = str(score.columns.levels[0][0])

        if settings['type'] is 'horizontal':

            if 'length' not in settings:
                raise RuntimeError(self._MISSING_SETTINGS)

            elif settings['length'] > 12 or settings['length'] < 1:
                raise RuntimeError(self._WRONG_LENGTH)

        elif name == 'interval.IntervalIndexer':
            xs = []
            first = [0, 1]
            f = str(first[0]) + ',' + str(first[1])
            while f in score.columns.levels[1]:
                xs.extend([f])
                first[0] += 1
                first[1] += 1
                f = str(first[0]) + ',' + str(first[1])
            score = score[name][xs]

        super(SetClassIndexer, self).__init__(score, None)

        self._score = self._score.fillna(method='ffill')

        if settings['type'] is 'horizontal' and settings['label'] is 'noterest':
            self._score = repeat.FilterByRepeatIndexer(self._score).run()

    def run(self):
        """
        :returns: Make a new index of the set classes in the piece.
        :rtype: :class:`pandas.DataFrame`
        """
        if self._settings['type'] is 'horizontal':
            total = from_horiz(self._score, self._settings['length'])
            note_col = total['chords']
            indices = total['indices']
        else:
            note_col = [from_vert(self._score)]
            indices = [self._score.index.tolist()]

        label = {'noterest': from_notes,
                 'intervals': from_intvls}

        chords = map(label[self._settings['label']], note_col)

        if self._settings['type'] is 'horizontal':
            labels = self._score.columns.labels[1]
        else:
            labels = '0'

        parts = []
        forteTypes = {'forteClass': forteClass,
                      'orderedPitchClassesString': orderedPitchClassesString,
                      'forteClassTnI': forteClassTnI,
                      'normalForm': normalForm,
                      'primeFormString': primeFormString,
                      'intervalVector': intervalVector}

        for x, part in enumerate(chords):
            part = pandas.Series(part, index=indices[x], name=str(labels[x]))
            parts.append(part.apply(forteTypes[self._settings['forteType']]))

        result = pandas.concat(parts, axis=1)
        return self.make_return(result.columns, [result[name] for name in result.columns])
