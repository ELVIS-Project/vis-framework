#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/contour.py
# Purpose:                Contour Indexer
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
import pandas


def COM_matrix(contour):
    """
    Creates a matrix representing the contour given.
    """
    com = []

    contour = contour.replace(' ', '')
    contour = contour.replace('[', '')
    contour = contour.replace(']', '')
    contour = contour.split(',')

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


def getContour(notes):
    """
    Method used by the ContourIndexer to convert pitches into contour numbers.
    """

    contour = list(map(music21.note.Note, notes))

    cseg = [0] * len(contour)

    for i in range(len(contour)):
        notes = []

        for x in range(len(contour)):
            if ((music21.interval.getAbsoluteHigherNote(contour[i], contour[x]) == contour[i]) and 
                (contour[i].nameWithOctave != contour[x].nameWithOctave) and 
                (contour[x].nameWithOctave not in notes)):
                notes.append(contour[x].nameWithOctave)
                cseg[i] += 1

    return str(cseg)


def compare(contour1, contour2):
    """
    Additional method to compare COM_matrices.
    """

    count = 0
    l = len(contour1)
    for row in range(l):
        for c1, c2 in zip(contour1[row], contour2[row]):
            if c1 == c2:
                count += 1

    count = float((count - l) / 2)
    total = float((l * (l - 1)) / 2)
    return count / total


class ContourIndexer(indexer.Indexer):
    """
    Indexes the contours of a given length in a piece, where contour is a
    way of numbering the relative heights of pitches, beginning at 0 for the
    lowest pitch.

    :keyword 'length': This is the length of the contour you want to look at.
    :type 'length': int
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['length']

    _MISSING_LENGTH = 'ContourIndexer requires "length" setting.'
    _LOW_LENGTH = 'Setting "length" must have a value of at least 1.'


    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce the contour indexer results.
        :type score: :class:`pandas.DataFrame`
        :param settings: All the settings required by this indexer.
        :type settings: dict or None

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the required settings are not present in the ``settings`` argument.
        :raises: :exc:`RuntimeError` if the value of 'length' is below 1
        """

        if settings is None or 'length' not in settings:
            raise RuntimeError(self._MISSING_LENGTH)
        elif settings['length'] < 1:
            raise RuntimeError(self._LOW_LENGTH)
        else:
            self.settings = settings

        self.score = score
        self.parts = len(self.score.columns.values)
        super(ContourIndexer, self).__init__(score, None)


    def run(self):
        """
        Makes a new index of the contours in the piece.

        :returns: A :class:`DataFrame` of the contours.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        import music21
        from vis.analyzers.indexers import noterest, contour

        score = music21.converter.parse('example.xml')
        notes = noterest.NoteRestIndexer(score).run()

        settings = {'length': 3}
        contours = contour.ContourIndexer(notes).run()
        print(contours)
        """

        contours = []

        for v, voice in enumerate(self.score.columns.values):

            part = self.score[voice].tolist()
            index = self.score.index.tolist()
            new_index = []
            voice_con = []
            for x in range(len(part)-self.settings['length']+1):
                cont = []

                if part[x] == 'Rest' or type(part[x]) == float:
                    pass
                else:
                    cont.append(part[x])
                    y = 1
                    while (len(cont) < self.settings['length']) and (x+y < len(part)):
                        if part[x+y] == 'Rest' or type(part[x+y]) == float:
                            pass
                        else:
                            cont.append(part[x+y])
                        y+=1
                if len(cont) == self.settings['length']:
                    voice_con.append(getContour(cont))
                    new_index.append(index[x])

            voice = pandas.Series(voice_con, index=new_index, name=str(v))
            contours.append(voice)

        result = pandas.concat(contours, axis=1)

        return self.make_return(result.columns, [result[name] for name in result.columns])
