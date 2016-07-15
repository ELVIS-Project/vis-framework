#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/fermata.py
# Purpose:                Index fermattas.
#
# Copyright (C) 2013, 2014 Christopher Antila, Ryan Bannon
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
.. codeauthor:: Ryan Bannon <ryan.bannon@gmail.com>

Index fermatas.
"""

import six
from numpy import NaN  # pylint: disable=no-name-in-module
from music21 import expressions
from vis.analyzers import indexer

def indexer_func(obj):
    """
    Used internally by :class:`FermataIndexer`. Inspects :class:`~music21.note.Note` and
    :class:`~music21.note.Rest` and returns ``u'Fermata'`` if a fermata is associated, else NaN.

    :param obj: An iterable (nominally a :class:`~pandas.Series`) with an object to convert. Only
        the first object in the iterable is processed.
    :type obj: iterable of :class:`music21.note.Note` or :class:`music21.note.Rest`

    :returns: If the first object in the list is a contains a :class:`~music21.expressions.Fermata`,
    string ``u'Fermata'`` is returned. Else, NaN.
    :rtype: str
    """
    for expression in obj[0].expressions:
        if isinstance(expression, expressions.Fermata):
            return 'Fermata'
    return NaN


class FermataIndexer(indexer.Indexer):
    """
    Index :class:`~music21.expressions.Fermata`.

    Finds :class:`~music21.expressions.Fermata`s.
    """

    required_score_type = 'stream.Part'

    def __init__(self, score, settings=None):
        """
        :param score: A list of all the Parts to index.
        :type score: list of :class:`music21.stream.Part`
        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: NoneType

        :raises: :exc:`RuntimeError` if ``score`` is not a list of the right type.
        """
        super(FermataIndexer, self).__init__(score, None)
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
        from vis.analyzers.indexers import fermata

        score = music21.converter.parse('example.xml')
        fermatas = fermata.FermataIndexer(score).run()
        print(fermatas)
        """
        combinations = [[x] for x in range(len(self._score))]  # calculate each voice separately
        results = self._do_multiprocessing(combinations)
        return self.make_return([six.u(str(x))[1:-1] for x in combinations], results)
