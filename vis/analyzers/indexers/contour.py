#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/template.py
# Purpose:                Template indexer
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

from vis.analyzers import indexer
import music21
import pprint
import pandas


def getContour(notes):

    notes = [x for x in notes if x != 'Rest']
    contour = list(map(music21.note.Note, notes))
    
    cseg = [0] * len(contour)

    for i in range(len(contour)):
        notes = []
        for x in range(len(contour)):
            if (music21.interval.getAbsoluteHigherNote(contour[i], contour[x]) == contour[i]) and (contour[i].nameWithOctave != contour[x].nameWithOctave) and (contour[x].nameWithOctave not in notes):
                notes.append(contour[x].nameWithOctave)
                cseg[i] += 1

    return str(cseg)


def COM_matrix(contour):

    com = []
    for x in contour:
        com.append([])

    for i in range(len(contour)):
        for x in range(len(contour)):
            if contour[i] == contour[x]:
                com[i].append("0")
            elif contour[i] > contour[x]:
                com[i].append("-")
            else:
                com[i].append("+")

    return com


def compare(contour1, contour2):

    count = 0
    l = len(contour1)
    for row in range(l):
        for c1, c2 in zip(contour1[row], contour2[row]):
            if c1 == c2:
                count += 1

    count = (count-l)/2
    total = (l*(l-1))/2
    return count/total


class ContourIndexer(indexer.Indexer):
    """
    Contour indexer class
    """

    required_score_type = 'pandas.DataFrame'

    possible_settings = ['length', 'type']

    default_settings = {'rests': 'on'}

    
    def __init__(self, score, settings=None):

        if settings is None:
            self._settings = self.default_settings
        self.score = score.dropna()
        self.settings = settings
        self.parts = len(self.score.columns.values)
        super(ContourIndexer, self).__init__(score, None)

    def run(self):

        index = []
        contours = []

        for y in range(0, len(self.score.index)-self.settings['length'], self.settings['length']):
            index.append(self.score.index[y])
            cont = []

            for x in range(self.settings['length']):
                cont.append([list(self.score[self.score.columns.values[name]])[x+y] for name in range(len(self.score.columns.values))])
            
            contours.append(zip(*cont))

        final_conts = []
        for ind in contours:
            final_conts.append(list(map(getContour, ind)))

        final_conts = zip(*final_conts)
        frames = []
        for x in range(self.parts):
            frames.append(pandas.DataFrame({str(x): pandas.Series([contour for contour in final_conts[x]], index=index)}))
        result = pandas.concat(frames, axis=1)

        return self.make_return(result.columns.values, [result[name] for name in result.columns])