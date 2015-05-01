#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/metre.py
# Purpose:                Indexers for metric concerns.
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
.. codeauthor::    Alexander Morgan

Indexers for metric concerns.
"""

# disable "string statement has no effect" warning---they do have an effect with Sphinx!
# pylint: disable=W0105

from music21 import note
from vis.analyzers import indexer
import pandas

def beatstrength_ind_func(obj):
    """
    The function that indexes the "beatStrength" of a whatever it's given.

    :param obj: A singleton list with an object of which to find the beatStrength.
    :type obj: list of :class:`~music21.base.Music21Object` subclasses.

    :returns: The :attr:`~music21.base.Music21Object.beatStrength` of the inputted object.
    :rtype: float
    """
    return obj[0].beatStrength

def duration_ind_func(obj):
    """
    The function that indexes the "duration" of a whatever it's given. Returns a negative
    value if the duration should be added on to the previous event in the part. This would
    happen if obj is part of a tie but not the first note in that tie group.

    .. warning:: May return a negative value.

    :param obj: A singleton list with an object of which to find the duration.
    :type obj: list of :class:`~music21.base.Music21Object` subclasses.

    :returns: The :attr:`~music21.base.Music21Object.duration` of the inputted object.
    :rtype: float
    """
    if hasattr(obj[0], 'tie') and obj[0].tie is not None:
        if obj[0].tie.type == 'start': # 'GeneralNote' object has a tie with a 'start' label
            return obj[0].duration.quarterLength
        else: # 'GeneralNote' object has a tie with a 'continue' or a 'stop' label
            obj[1][-1] += obj[0].duration.quarterLength
            return None
    else: # The 'GeneralNote' object has no tie or has a tie of type None
        return obj[0].duration.quarterLength


class NoteBeatStrengthIndexer(indexer.Indexer):
    """
    Make an index of the :attr:`~music21.base.Music21Object.beatStrength` for all :class:`Note`
    and :class:`Rest` objects.

    .. note:: Unlike nearly all other indexers, this indexer returns a :class:`Series` of ``float``
    objects rather than ``unicode`` objects.
    """

    required_score_type = 'stream.Part'

    def __init__(self, score, settings=None):
        """
        :param score: A list of the :class:`Part` objects to use for producing this index.
        :type score: list of :class:`music21.stream.Part`
        :param settings: This indexer requires no settings so this parameter is ignored.
        :type settings: any

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """

        super(NoteBeatStrengthIndexer, self).__init__(score, None)
        self._types = ('GeneralNote',)
        self._indexer_func = beatstrength_ind_func
        self._settings = settings

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices. Refer to the example below. Note that each item is a float,
        rather than the usual basestring.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        >>> the_score = music21.converter.parse('sibelius_5-i.mei')
        >>> the_score.parts[5]
        (the first clarinet Part)
        >>> the_notes = NoteBeatStrengthIndexer(the_score).run()
        >>> the_notes['metre.NoteBeatStrengthIndexer']['5']
        (the first clarinet Series of beatStrength float values)
        """

        combinations = [[x] for x in xrange(len(self._score))]
        results = self._do_multiprocessing(combinations)
        return self.make_return([unicode(x)[1:-1] for x in combinations], results)


class DurationIndexer(indexer.Indexer):
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
        :param settings: This indexer requires no settings so this parameter is ignored.
        :type settings: any

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """

        super(DurationIndexer, self).__init__(score, None)
        self._types = ('GeneralNote',)
        self._indexer_func = duration_ind_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices. Refer to the example below. Note that each item is a float,
        rather than the usual basestring.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        >>> the_score = music21.converter.parse('sibelius_5-i.mei')
        >>> the_score.parts[5]
        (the first clarinet Part)
        >>> the_notes = DurationIndexer(the_score).run()
        >>> the_notes['metre.DurationIndexer']['5']
        (the first clarinet Series of duration float values)
        """

        combinations = [[x] for x in xrange(len(self._score))]
        results = self._do_multiprocessing(combinations, True)
        return self.make_return([unicode(x)[1:-1] for x in combinations], results)


class MeasureIndexer(indexer.Indexer):
    """
    Make an index of the measures in a piece. Note that for simplicity, just the measures of the
    upper-most part are indexed so it is assumed that all parts have the same number of measures.
    Time signatures changes do not cause a problem provided that all parts change time signatures at
    the same time and in the same way.
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

    def run(self):
        measure_stream = self._score.measureTemplate()
        measure_numbers = []
        measure_offsets = []
        for m in measure_stream:
            measure_numbers.append(m.measureNumber)
            measure_offsets.append(m.offset)
        meas_ind = pandas.DataFrame(measure_numbers, index=measure_offsets)    
        iterables = [['metre.MeasureIndexer'], ['Measures']]
        meas_ind.columns = pandas.MultiIndex.from_product(iterables, names = ['Indexer', ''])

        return meas_ind

