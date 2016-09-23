#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name:         scripts/melodies.py
# Purpose:      Finds occurences of melodies in a piece and what notes
#               they start on.
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
import pandas
import music21
from vis.analyzers.indexers import noterest, interval, new_ngram


# This function finds all the melodies in a piece and returns a dictionary of
# all the notes that each melody starts on.
# These functions can be adjusted to find other features, depending on which
# indexers you decide to call. Make sure to change all the details of this
# if you do decide to adjust things (for example, if you decide to look for 3
# note melodies instead of 4, make sure the melody you are searching for is
# also 3 notes long. Or, if you replace the example.xml file with a piece that
# has 6 voices, make sure to add those to the list of voices.)
def all_melodies(file):
    file = music21.converter.parse(file)
    notes = noterest.NoteRestIndexer(file).run()
    h_ints = interval.HorizontalIntervalIndexer(notes).run()

    voices = ['0', '1', '2', '3']
    settings = {'n': 4, 'vertical': voices}
    ngrams = new_ngram.NewNGramIndexer([h_ints], settings).run()

    combined = pandas.concat([notes, ngrams], axis=1)

    voices_list = []
    for voice in voices:
        voice_dict = {}
        for melody in ngrams['new_ngram.NewNGramIndexer'][voice].dropna().tolist():
            condition = combined.loc[:, 'new_ngram.NewNGramIndexer'][voice] == melody
            location = combined.loc[:, 'noterest.NoteRestIndexer'][voice]
            if melody not in voice_dict:
                voice_dict[melody] = location[condition].tolist()
        voices_list.append(voice_dict)

    melo_dict = {}
    for dictionary in voices_list:
        for entry in dictionary:
            if entry in melo_dict:
                melo_dict[entry].extend(dictionary[entry])
            else:
                melo_dict[entry] = dictionary[entry]

    return melo_dict


# this function takes as input a melody and returns all the notes that melody
# starts on
def from_melody(file, melody):
    file = music21.converter.parse(file)

    notes = noterest.NoteRestIndexer(file).run()
    h_ints = interval.HorizontalIntervalIndexer(notes).run()

    voices = ['0', '1', '2', '3']
    settings = {'n': 4, 'vertical': voices}
    ngrams = new_ngram.NewNGramIndexer([h_ints], settings).run()

    combined = pandas.concat([notes, ngrams], axis=1)

    all_voices = []
    for voice in voices:
        condition = combined.loc[:, 'new_ngram.NewNGramIndexer'][voice] == melody
        location = combined.loc[:, 'noterest.NoteRestIndexer'][voice]
        all_voices.extend(location[condition].tolist())
    return all_voices


file = 'example.xml'
print(all_melodies(file))
melody = '[2] [-2] [-2] [-2]'
print(from_melody(file, melody))
