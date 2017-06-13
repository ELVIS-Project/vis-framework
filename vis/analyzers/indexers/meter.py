#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/meter.py
# Purpose:                Indexers for metric concerns.
#
# Copyright (C) 2013-2016 Christopher Antila, Alexander Morgan
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

.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. codeauthor:: Alexander Morgan

Indexers for metric concerns.

"""

# disable "string statement has no effect" warning---they do have an 
# effect with Sphinx!
# pylint: disable=W0105

import pandas
from vis.analyzers import indexer


def beatstrength_ind_func(event):
    """
    Used internally by :class:`NoteBeatStrengthIndexer`. Convert
    :class:`~music21.note.Note` and :class:`~music21.note.Rest` objects
    into a string.

    :param event: A music21 note, rest, or chord object which get 
        queried for its beat strength. :type event: A music21 note, 
        rest, or chord object or NaN.

    :returns: The :attr:`~music21.base.Music21Object.beatStrength` of 
        the event which is dependent on the prevailing time signature.
    
    :rtype: float
    """
    if isinstance(event, float):
        return event
    return event.beatStrength

def measure_ind_func(event):
    """
    The function that indexes the measure numbers of each part in a 
    piece. Unlike most other indexers, this one returns int values. 
    Measure numbering starts from 1 unless there is a pick-up measure 
    which gets the number 0. This can handle changes in time signature 
    without problems.

    :param event: A music21 measure object which get queried for its 
        "number" attribute.
    
    :type event: A music21 measure object or NaN.

    :returns: The number attribute of the passed music21 measure.
    
    :rtype: int
    """
    if isinstance(event, float):
        return event
    return event.number


class NoteBeatStrengthIndexer(indexer.Indexer):
    """
    Make an index of the 
    :attr:`~music21.base.Music21Object.beatStrength` for all 
    :class:`Note`, :class:`Rest`, and :class:`Chord` objects.

    .. note:: Unlike nearly all other indexers, this indexer returns a 
        :class:`Series` of ``float`` objects rather than ``unicode`` 
        objects.
    
    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ip.get_data('beat_strength')
    
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score):
        """
        :param score: A dataframe of the note, rest, and chord objects 
            in a piece.
        
        :type score: pandas Dataframe

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        """

        super(NoteBeatStrengthIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest', 'Chord')
        self._indexer_func = beatstrength_ind_func

    # NB: This indexer inherits its run() method from indexer.py


class DurationIndexer(indexer.Indexer):
    """
    Make an index of the durations of all :class:`Note`, :class:`Rest`, 
    and :class:`Chord` objects. These are calculated based on the 
    difference in index positions of consecutive events.

    .. note:: Unlike nearly all other indexers, this indexer returns a 
        :class:`Series` of ``float`` objects rather than ``unicode`` 
        objects. Also unlike most other indexers, this indexer does not have 
        an indexer func.

    **Example:**
    
    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ip.get_data('duration')
    
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, part_streams):
        """
        :param score: A :class:`pandas.DataFrame` of the note, rest, and 
            chord objects in a piece.
    
        :type score: :class:`pandas.DataFrame`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        
        """

        super(DurationIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest', 'Chord')
        self._part_streams = part_streams

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices of the durations of each note or rest 
            event in a score. Note that each item is a float, rather 
            than the usual basestring.
        
        :rtype: :class:`pandas.DataFrame`
        
        """
        if len(self._score) == 0: # if there are no notes or rests
            result = self._score.copy()
        else:
            durations = []
            for part in range(len(self._score.columns)):
                indx = self._score.iloc[:, part].dropna().index
                new = indx.insert(len(indx), self._part_streams[part].highestTime)
                durations.append(pandas.Series((new[1:] - indx), index=indx))
            result = pandas.concat(durations, axis=1)
        return self.make_return(self._score.columns.get_level_values(1), result)

# The MeasureIndexer is still experimental
class MeasureIndexer(indexer.Indexer): 
    """
    Make an index of the measures in a piece. Time signatures changes do 
    not cause a problem. Note that unlike most other indexers this one 
    returns integer values >= 0. Using music21's part.measureTemplate() 
    function is an alternative but it turned out to be much less 
    efficient to looping over the piece and doing it this way makes this 
    indexer just like all the other stream indexers in VIS. 

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ip.get_data('measure')
    
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score):
        """
        :param score: :class:`pandas.DataFrame` of music21 measure 
            objects.
        
        :type score: :class:`pandas.DataFrame`
        
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        """
        super(MeasureIndexer, self).__init__(score, None)
        self._types = ('Measure',)
        self._indexer_func = measure_ind_func

    # NB: This indexer inherits its run() method from indexer.py
