#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name:         scripts/transformations.py
# Purpose:      Finds transformations of melodies.
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
import music21
from vis.analyzers.indexers import noterest, interval, new_ngram


def _find_inv(motif):

    invs = []
    new_motif = ""

    motif = motif.split(' ')
    for note in motif:
        note = note[1:-1]
        if note == 'Rest':
            pass
        else:
            note = int(note) * -1
        invs.append('[' + str(note) + ']')

    new_motif = ' '.join(invs)
    return new_motif


def _find_ret(motif):

    temp_ret = motif.split(' ')
    temp_ret.reverse()

    ret = ' '.join(temp_ret)

    return ret


def find_transformations(file, motif):

    file = music21.converter.parse(file)
    notes = noterest.NoteRestIndexer(file).run()
    h_ints = interval.HorizontalIntervalIndexer(notes).run()

    voices = ['0', '1', '2', '3']
    settings = {'n': 4, 'vertical': voices}

    motifs = new_ngram.NewNGramIndexer([h_ints], settings).run()

    condition = motifs['new_ngram.NewNGramIndexer'] == motif
    print(notes[condition].dropna(how='all'))

    inv = _find_inv(motif)
    condition = motifs['new_ngram.NewNGramIndexer'] == inv
    print(notes[condition].dropna(how='all'))

    ret = _find_ret(motif)
    condition = motifs['new_ngram.NewNGramIndexer'] == ret
    print(notes[condition].dropna(how='all'))

motif = '[2] [2] [2] [-2]'
find_transformations('example.xml', motif)
