#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name:         scripts/permutations.py
# Purpose:      Finds permutations of melodies.
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


def _permute(motif):

    if type(motif) == list:
        arr = motif
    else:
        arr = motif.split(' ')

    x = arr[0]
    new_arr = []

    for i in range(1, len(arr), 1):
        new_arr.append(arr[i])

    if len(arr) == 2:
        return _insert(x, new_arr)

    else:
        final = []

        if len(arr) > 2:
            for perm in _permute(new_arr):
                final.extend(_insert(x, perm))

        return final


def _insert(x, arr):

    group = []

    for i in range(0, len(arr) + 1, 1):
        group.append(list(arr))
        group[i].insert(i, x)

    return group


def find_permutations(file, motif):

    file = music21.converter.parse(file)
    notes = noterest.NoteRestIndexer(file).run()
    h_ints = interval.HorizontalIntervalIndexer(notes).run()

    voices = ['0', '1', '2', '3']
    settings = {'n': 4, 'vertical': voices}

    ngrams = new_ngram.NewNGramIndexer([h_ints], settings).run()

    perms1 = _permute(motif)
    perms = []
    for motif in perms1:
        perms.append(' '.join(motif))
    perms = list(set(perms))

    for motif in perms:
        condition = ngrams['new_ngram.NewNGramIndexer'] == motif
        print(notes[condition].dropna(how='all'))


motif = '[2] [-3] [4] [-2]'
find_permutations('example.xml', motif)
