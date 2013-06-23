#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers.py
# Purpose:                Help with indexing data from musical scores.
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
The controllers that deal with indexing data from music21 Score objects.
"""

from music21 import stream, note
from vis.models.indexed_piece import IndexedPiece


class Indexer(object):
    """
    ASDF DOCZ!

    Use the "Indexer.needs_score" attribute to know whether the __init__() method should be given
    a subclass of music21.stream.Stream (if that attribute is False, give it an IndexedPiece).
    """

    # NB: you should re-implement this in subclasses
    needs_score = False

    def __init__(self, score):
        """
        Create a new Indexer.

        Parameters
        ==========
        score : vis.models.IndexedPiece or music21.stream.Stream
            Depending on how this Indexer works, this is either an IndexedPiece or a Stream
            subclass that we'll use when creating a new index. If it is an IndexedPiece, and it
            doesn't yet have the index/indices required for this Indexer, the appropriate indexers
            should be triggered by this Indexer.

        Raises
        ======
        RuntimeError :
            If the "score" argument is the wrong type.
        """
        # NOTE: This is the only method you should reimplement in subclasses.

        # Choose from these, as appropriate:
        if not (isinstance(IndexedPiece) or isinstance(stream.Stream)):
            raise RuntimeError('Indexer expects IndexedPiece or Stream')

        # Change the class name to the current class
        super(Indexer, self).__init__()

        # Leave this
        self._score = score

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = []

        # Change to the function you want to use
        self._indexer_func = lambda x: None

        # If self._score is an IndexedPiece, change this to the name of the Indexer's results you
        # want to use when creating this new index
        self._previous_indexer = None

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        pandas.Series :
            The new index. Each element is an instance of music21.base.ElementWrapper.
        """
        # NOTE-1: Do not reimplement this method in subclasses
        # NOTE-2: This method knows whether you're looking through a Stream or IndexedPiece, and
        #         handles them accordingly.
        # NOTE-3: When I write it, this method will go through everything in self._score, and if
        #         an element matches one of the things in self._types, it will be passed through
        #         the self._indexer_func function, then added to the new Series.
        pass


class NoteRestIndexer(Indexer):
    """
    Index music21.note.Note and Rest objects found in a music21.stream.Part.

    Rest objects are indexed as u'Rest', and Note objects as the unicode-format version of their
    "pitchWithOctave" attribute.
    """

    needs_score = True

    def __init__(self, score):
        """
        Create a new Indexer.

        Parameters
        ==========
        score : music21.stream.Part
            The part to index.

        Raises
        ======
        RuntimeError :
            If the "score" argument is the wrong type.
        """
        if not isinstance(score, stream.Part):
            raise RuntimeError('NoteRestIndexer requires a music21.stream.Part')
        super(NoteRestIndexer, self).__init__()
        self._score = score
        self._types = [note.Rest, note.Note]
        self._indexer_func = lambda x: u'Rest' if isinstance(x, note.Rest) else unicode(x.pitchWithOctave)
