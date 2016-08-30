#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/meter.py
# Purpose:                Indexers for metric concerns.
#
# Copyright (C) 2013-2015 Christopher Antila, Alexander Morgan
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

Indexers for metric concerns.
"""

# disable "string statement has no effect" warning---they do have an effect
# with Sphinx!
# pylint: disable=W0105

import pandas
from vis.analyzers import indexer
# import pandas # This is only needed for the measure indexer which is still
# experimental

axis_labels = ('Indexer', 'Parts') # Axis names for resultant dataframe.

def beatstrength_ind_func(event):
    """
    Used internally by :class:`NoteBeatStrengthIndexer`. Convert
    :class:`~music21.note.Note` and :class:`~music21.note.Rest` objects
    into a string.

    :param obj: An 2-tuple with an object to convert. Only the first object
        in the iterable is processed in this function.
    :type obj: a 2-tuple containing either a :class:`music21.note.Note` or a
        :class:`music21.note.Rest` as its first element and a list of the
        running results of this indexer_func as the second element.

    :returns: The :attr:`~music21.base.Music21Object.beatStrength` of obj[0]
        which is dependent on the prevailing time signature.
    :rtype: float
    """
    if isinstance(event, float):
        return event
    return event.beatStrength

def measure_ind_func(obj):
    """
    The function that indexes the measure numbers of each part in a piece. Unlike most other 
    indexers, this one returns int values. Measure numbering starts from 1 unless there is a pick-up 
    measure which gets the number 0. This can handle changes in time signature without problems.
    """
    return obj[0].measureNumber


class NoteBeatStrengthIndexer(indexer.Indexer):
    """
    Make an index of the :attr:`~music21.base.Music21Object.beatStrength` for all :class:`Note`
    and :class:`Rest` objects.

    .. note:: Unlike nearly all other indexers, this indexer returns a :class:`Series` of ``float``
    objects rather than ``unicode`` objects.
    """

    required_score_type = 'stream.Part'

    def __init__(self, score):
        """
        :param score: A list of the :class:`Part` objects to use for producing this index.
        :type score: list of :class:`music21.stream.Part`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """

        super(NoteBeatStrengthIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest')
        self._indexer_func = beatstrength_ind_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices. Refer to the example below. Note that each item is a float,
        rather than the usual basestring.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        import music21
        from vis.analyzers.indexers import meter

        score = music21.converter.parse('example.xml')
        notebeat = meter.NoteBeatStrengthIndexer(score).run()
        print(notebeat)
        """
        if len(self._score.index) == 0: # If parts have no note, rest, or chord events in them
            result = self._score.copy()
        else: # This is the normal case
            result = self._score.applymap(self._indexer_func) # Do indexing.
        result.columns = pandas.MultiIndex.from_product((('meter.NoteBeatStrengthIndexer',), # Apply multi-index to df.
            [str(x) for x in range(len(result.columns))]), names=axis_labels)
        return result


class DurationIndexer(indexer.Indexer):
    """
    Make an index of the :attr:`~music21.base.Music21Object.duration.quarterLength` for all
    :class:`Note` and :class:`Rest` objects.

    .. note:: Unlike nearly all other indexers, this indexer returns a :class:`Series` of ``float``
    objects rather than ``unicode`` objects. Also unlike most other indexers, this indexer does not 
    have an indexer func.
    """

    required_score_type = 'stream.Part'

    def __init__(self, score, part_streams):
        """
        :param score: A list of the :class:`Part` objects to use for producing this index.
        :type score: list of :class:`music21.stream.Part`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """

        super(DurationIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest')
        self._part_streams = part_streams

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices of the durations of each note or rest event in a score. Note that
            each item is a float, rather than the usual basestring.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        import music21
        from vis.analyzers.indexers import meter

        score = music21.converter.parse('example.xml')
        durations = meter.DurationIndexer(score).run()
        print(durations)
        """
        durations = []
        for part in range(len(self._score.columns)):
            indx = self._score.iloc[:, part].dropna().index
            new = indx.insert(len(indx), self._part_streams[part].highestTime)
            durations.append(pandas.Series((new[1:] - indx), index=indx))
        result = pandas.concat(durations, axis=1)
        result.columns = pandas.MultiIndex.from_product((('meter.DurationIndexer',), # Apply multi-index to df.
            [str(x) for x in range(len(result.columns))]), names=axis_labels)
        return result


class MeasureIndexer(indexer.Indexer): # MeasureIndexer is still experimental
    """
    Make an index of the measures in a piece. Time signatures changes do not cause a problem. Note 
    that unlike most other indexers this one returns integer values >= 0. Using music21's 
    part.measureTemplate() function is an alternative but it turned out to be much less efficient 
    to looping over the piece and doing it this way makes this indexer just like all the other 
    stream indexers in VIS. 
    """

    required_score_type = 'stream.Part'

    def __init__(self, score, settings=None):
        """
        :param score: :class:`Part` object to use for producing this index. It should be the highest
            part in the score.
        :type score: :class:`music21.stream.Part`
        :param settings: This indexer requires no settings so this parameter is ignored.
        :type settings: None
        
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(MeasureIndexer, self).__init__(score, None)
        self._types = ('Measure',)
        self._indexer_func = measure_ind_func

    def run(self):
        """
        Make a new index of the piece where the values are the measure numbers in each part and the 
        index contains the offsets at which those measures begin.

        :returns: The measure number of each measure in each part in a score. Note that
            each item is an integer, rather than the usual basestring. The index contains the
            offsets at which the observed measures begin.
        :rtype: :class:`pandas.DataFrame`
        """
        combinations = [[x] for x in range(len(self._score))]
        results = self._do_multiprocessing(combinations, True)
        return self.make_return([str(x)[1:-1] for x in combinations], results)
