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
        super(Indexer, self).__init__()
        self._score = score

    def run():
        """
        Make a new index of the piece.

        Returns
        =======
        pandas.Series :
            The new index. Each element is an instance of music21.base.ElementWrapper.
        """
        pass
