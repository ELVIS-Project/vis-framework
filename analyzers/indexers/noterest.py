#! /usr/bin/python
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
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Index note and rest objects.
"""

from music21 import stream, note
from vis.analyzers import indexer

def indexer_func(obj):
    """
    Convert the first item of a list to u'Rest' or its "nameWithOctave" attribute.
    """
    return u'Rest' if isinstance(obj[0], note.Rest) else unicode(obj[0].nameWithOctave)


class NoteRestIndexer(indexer.Indexer):
    """
    Index music21.note.Note and Rest objects found in a music21.stream.Part.

    Rest objects are indexed as u'Rest', and Note objects as the unicode-format version of their
    "pitchWithOctave" attribute.
    """

    required_indices = []
    required_score_type = stream.Part
    requires_score = True

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new Indexer.

        Parameters
        ==========
        :param score : [music21.stream.Part]
            A list of all the Parts to index.

        :param mpc : MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        RuntimeError :
            If the "score" argument is the wrong type.
        """
        super(NoteRestIndexer, self).__init__(score, None, mpc)

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = [note.Note, note.Rest]

        # You probably do not want to change this
        self._indexer_func = indexer_func

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        [pandas.Series] :
            A list of the new indices. The index of each Series corresponds to the index of the Part
            used to generate it, in the order specified to the constructor. Each element in the
            Series is an instance of music21.base.ElementWrapper.
        """

        combinations = [[x] for x in xrange(len(self._score))]  # calculate each voice separately
        return self._do_multiprocessing(combinations)
