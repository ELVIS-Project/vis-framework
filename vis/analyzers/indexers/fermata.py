#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/fermata.py
# Purpose:                Index fermattas.
#
# Copyright (C) 2013, 2014, 2016 Christopher Antila, Ryan Bannon, 
# Alexander Morgan
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
# You should have received a copy of the GNU Affero General Public 
# License along with this program.  If not, see 
# <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------- #
"""
.. codeauthor:: Ryan Bannon <ryan.bannon@gmail.com>
.. codeauthor:: Alexander Morgan

Index fermatas.

"""

import six
from music21 import expressions
from vis.analyzers import indexer

def indexer_func(event):
    """
    Used internally by :class:`FermataIndexer`. Inspects 
    
    :class:`~music21.note.Note` and :class:`~music21.note.Rest` and 
        returns ``u'Fermata'`` if a fermata is associated, else NaN.

    :param event: An iterable (nominally a :class:`~pandas.Series`) with 
        an object to convert. Only the first object in the iterable is 
        processed.
    
    :type event: iterable of :class:`music21.note.Note` or 
        :class:`music21.note.Rest`

    :returns: If the first object in the list is a contains a 
        :class:`~music21.expressions.Fermata`, string ``u'Fermata'`` 
        is returned. Else, NaN.
    
    :rtype: str
    """
    
    if isinstance(event, float):
        return event
    for expression in event.expressions:
        if isinstance(expression, expressions.Fermata):
            return 'Fermata'


class FermataIndexer(indexer.Indexer):
    """
    Index :class:`~music21.expressions.Fermata`.

    Finds :class:`~music21.expressions.Fermata`s.

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ip.get_data('fermata')
    
    """

    required_score_type = 'stream.Part'

    def __init__(self, score, settings=None):
        """
        :param score: A dataframe of the note, rest, and chord objects 
            in a piece.
        
        :type score: pandas Dataframe
        
        :param settings: This indexer does not have any settings, so 
            this is just a place holder.
        
        :type settings: None

        :raises: :exc:`RuntimeError` if ``score`` is not a pandas 
            Dataframe.

        """
        super(FermataIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest', 'Chord')
        self._indexer_func = indexer_func

    # NB: The noterest indexer inherits the run() method from indexer.py

