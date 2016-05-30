#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/repeat.py
# Purpose:                Indexers that somehow consider repetition.
#
# Copyright (C) 2013, 2014 Christopher Antila
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

Indexers that consider repetition in any way.
"""

import six
from numpy import nan
from vis.analyzers import indexer


class FilterByRepeatIndexer(indexer.Indexer):
    """
    If the same event occurs many times in a row, remove all occurrences but the one with the \
    lowest ``offset`` value (i.e., the "first" event).

    Because of how a :class:`DataFrame`'s index works, many of the events that would have been
    filtered will instead be replaced with :const:`numpy.NaN`. Please be careful that the behaviour
    of this indexer matches your expectations.
    """

    required_score_type = 'pandas.Series'

    def __init__(self, score, settings=None):
        """
        :param score: The indices from which to remove consecutive identical events. There must be
            at least one part in the score.
        :type score: :class:`pandas.DataFrame` or list of :class:`pandas.Series`
        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: dict or NoneType

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(FilterByRepeatIndexer, self).__init__(score, None)

        # This Indexer uses pandas magic, not an _indexer_func().
        self._indexer_func = None

    def run(self):
        """
        Make a new index of the piece, removing any event that is identical to the preceding.

        :returns: A :class:`DataFrame` of the new indices.
        :rtype: :class:`pandas.DataFrame`

        ***Example:***

        import music21
        from vis.analyzers.indexers import noterest

        score = music21.converter.parse('example.xml')
        notes = noterest.NoteRestIndexer(score).run()

        repeats = repeat.FilterByRepeatIndexer(notes).run()
        print(repeats)
        """
        # I'm relying on pandas' efficiency. In the future, maybe we should use multiprocessing?
        post = []
        for part in self._score:
            if len(part.index) < 2:
                post.append(part)
                continue
            axe_me = []
            prev_off = None
            for offset in list(part.index):
                if prev_off is None:
                    pass  # prevent the other tests from being tried
                elif part[offset] == part[prev_off]:
                    axe_me.append(offset)
                prev_off = offset
            for axed in axe_me:
                part[axed] = nan
            post.append(part.dropna())

        # prepare the proper return type
        combinations = [[x] for x in range(len(self._score))]
        return self.make_return([six.u(str(x))[1:-1] for x in combinations], post)
