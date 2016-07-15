#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/noterest.py
# Purpose:                Index note and rest objects.
#
# Copyright (C) 2013, 2014, 2015 Christopher Antila, and Alexander Morgan
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
.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. codeauthor:: Alexander Morgan

Index note and rest objects.
"""

import six
from music21 import note
from vis.analyzers import indexer


def indexer_func(obj):
    """
    Used internally by :class:`NoteRestIndexer`. Convert :class:`~music21.note.Note` and
    :class:`~music21.note.Rest` objects into a string.

    :param obj: An 2-tuple with an object to convert. Only the first object in the iterable is
        processed in this function.
    :type obj: a 2-tuple containing either a :class:`music21.note.Note` or a
        :class:`music21.note.Rest` as its first element and a list of the running results of this
        indexer_func as the second element.

    :returns: If the first object in the list is a :class:`music21.note.Rest`, the string
        ``u'Rest'``; otherwise the :attr:`~music21.note.Note.nameWithOctave` attribute, which is
        the pitch class and octave of the :class:`Note`.
    :rtype: str
    """
    return 'Rest' if isinstance(obj[0], note.Rest) else six.u(str(obj[0].nameWithOctave))


class NoteRestIndexer(indexer.Indexer):
    """
    Index :class:`~music21.note.Note` and :class:`~music21.note.Rest` objects in a
    :class:`~music21.stream.Part`.

    :class:`Rest` objects become ``'Rest'``, and :class:`Note` objects become the string-format
    version of their :attr:`~music21.note.Note.nameWithOctave` attribute.
    """

    required_score_type = 'stream.Part'

    def __init__(self, score):
        """
        :param score: A list of all the Parts to index.
        :type score: list of :class:`music21.stream.Part`
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the right type.
        """
        super(NoteRestIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest')
        self._indexer_func = indexer_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` of the new indices. The columns have a :class:`MultiIndex`;
            refer to the example below for more details.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        import music21
        from vis.analyzers.indexers import noterest

        score = music21.converter.parse('example.xml')
        notes = noterest.NoteRestIndexer(score).run()

        # to see all the results
        print(notes)

        # to see only one part
        print(notes['noterest.NoteRestIndexer']['3'])
        """
        combinations = [[x] for x in range(len(self._score))]  # calculate each voice separately
        results = self._do_multiprocessing(combinations)
        return self.make_return([six.u(str(x))[1:-1] for x in combinations], results)
