#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/noterest.py
# Purpose:                Index note and rest objects.
#
# Copyright (C) 2013 Christopher Antila
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
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>

Index note and rest objects.
"""

from music21 import stream, note
from vis.analyzers import indexer

def indexer_func(obj):
    """
    Used internally by :class:`NoteRestIndexer`. Convert objects from the :mod:`music21.note` \
    module into a :obj:`unicode`.

    :param obj: A list with the object to convert.
    :type obj: :obj:`list` of :class:`music21.note.Note` or :class:`music21.note.Rest`

    :returns: If the first object in the list is a :class:`music21.note.Rest`, the string
        :obj:`u'Rest'`; otherwise the :attr:`nameWithOctave` attribute, which is the pitch class
        and octave of the :class:`music21.note.Note`.
    :rtype: :obj:`unicode`
    """
    return u'Rest' if isinstance(obj[0], note.Rest) else unicode(obj[0].nameWithOctave)


class NoteRestIndexer(indexer.Indexer):
    """
    Index :class:`music21.note.Note` and :class:`Rest` objects found in a
    :class:`music21.stream.Part`.

    Rest objects are indexed as :obj:`u'Rest'`, and Note objects as the unicode-format version of
    their :attr:`pitchWithOctave` attribute.
    """

    required_score_type = stream.Part
    "The :class:`NoteRestIndexer` uses :class:`Part` objects directly."

    def __init__(self, score, settings=None):
        """
        :param score: A list of all the Parts to index.
        :type score: :obj:`list` of :class:`music21.stream.Part`
        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: :obj:`dict` or :obj:`None`

        :raises: :exc:`RuntimeError` if :obj:`score` is not a list of the right type.
        """
        super(NoteRestIndexer, self).__init__(score, None)

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = [note.Note, note.Rest]

        # You probably do not want to change this
        self._indexer_func = indexer_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A list of the new indices. The index of each Series corresponds to the index of
            the Part used to generate it, in the order specified to the constructor. Each element
            in the Series is a unicode.
        :rtype: :obj:`list` of :obj:`pandas.Series`
        """

        combinations = [[x] for x in xrange(len(self._score))]  # calculate each voice separately
        return self._do_multiprocessing(combinations)
