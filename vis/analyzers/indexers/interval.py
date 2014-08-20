#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/interval.py
# Purpose:                Index vertical intervals.
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

Index intervals. Use the :class:`IntervalIndexer` to find vertical (harmonic) intervals between two
parts. Use the :class:`HorizontalIntervalIndexer` to find horizontal (melodic) intervals in the
same part.
"""

# disable "string statement has no effect"... it's for sphinx
# pylint: disable=W0105

import pandas
from music21 import note, interval, pitch
from vis.analyzers import indexer
#from vis.analyzers.indexers.noterest import NoteRestIndexer


def key_to_tuple(key):
    """
    Transforms a key in the results of :meth:`IntervalIndexer.run` into a 2-tuple with the indices
    of the parts held therein.

    :param key: The key from :class:`IntervalIndexer`.
    :type key: unicode string
    :returns: The indices of parts referred to by the key.
    :rtype: tuple of int

    >>> key_to_tuple(u'5,6')
    (5, 6)
    >>> key_to_tuple(u'234522,98100')
    (234522, 98100)
    >>> var = key_to_tuple(u'1,2')
    >>> key_to_tuple(str(var[0]) + u',' + str(var[1]))
    (1, 2)
    """
    post = key.split(u',')
    return int(post[0]), int(post[1])


def real_indexer(simultaneity, simple, quality):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.

    Turn a notes-and-rests simultaneity into the name of the interval it represents. Note that,
    because of the ``'Rest'`` strings, you can compare the duration of the piece in which the two
    parts do or do not have notes sounding together.

    :param simultaneity: A two-item iterable with the note names (or :class:`u'Rest'`) for the top
        then lower voice.
    :type simultaneity: list of basestring
    :param simple: Whether intervals should be reduced to their single-octave version.
    :type simple: boolean
    :param quality: Whether the interval's quality should be prepended.
    :type quality: boolean

    :returns: :class:`u'Rest'` if one or more of the parts is :obj:`u'Rest'`; otherwise, the interval
        between parts.
    :rtype: unicode string
    """

    if 2 != len(simultaneity):
        return None
    else:
        try:
            upper, lower = simultaneity
            interv = interval.Interval(note.Note(lower), note.Note(upper))
        except pitch.PitchException:
            return u'Rest'
        post = u'-' if interv.direction < 0 else u''
        if quality:
            # We must get all of the quality, and none of the size (important for AA, dd, etc.)
            q_str = u''
            for each in interv.name:
                if each in u'AMPmd':
                    q_str += each
            post += q_str
        if simple:
            post += unicode(interv.generic.semiSimpleUndirected)
        else:
            post += unicode(interv.generic.undirected)
        return post


# We give these functions to the multiprocessor; they're pickle-able, they let us choose settings,
# and the function still only requires one argument at run-time from the Indexer.mp_indexer().
def indexer_qual_simple(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.

    Call :func:`real_indexer` with settings to print simple intervals with quality.
    """
    return real_indexer(ecks, True, True)


def indexer_qual_comp(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.

    Call :func:`real_indexer` with settings to print compound intervals with quality.
    """
    return real_indexer(ecks, False, True)


def indexer_nq_simple(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.

    Call :func:`real_indexer` with settings to print simple intervals without quality.
    """
    return real_indexer(ecks, True, False)


def indexer_nq_comp(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.

    Call :func:`real_indexer` with settings to print compound intervals without quality.
    """
    return real_indexer(ecks, False, False)


class IntervalIndexer(indexer.Indexer):
    """
    Use :class:`music21.interval.Interval` to create an index of the vertical (harmonic) intervals
    between two-part combinations.

    You should provide the result of :class:`~vis.analyzers.indexers.noterest.NoteRestIndexer`.
    """

    required_score_type = pandas.Series
    """
    The :class:`IntervalIndexer` requires a list of :class:`Series` as input. These should be the
    result of :class:`NoteRestIndexer`.
    """

    possible_settings = [u'simple or compound', u'quality']
    """
    A list of possible settings for the :class:`IntervalIndexer`.

    :keyword unicode u'simple or compound': Whether intervals should be represented in their \
        single-octave form (either ``u'simple'`` or ``u'compound'``).
    :keyword boolean u'quality': Whether to display an interval's quality.
    """

    default_settings = {u'simple or compound': u'compound', u'quality': False}
    "A dict of default settings for the :class:`IntervalIndexer`."

    def __init__(self, score, settings=None):
        """
        The output format is described in :meth:`run`.

        :param score: The output of :class:`NoteRestIndexer` for all parts in a piece.
        :type score: list of :class:`pandas.Series`
        :param settings: Required and optional settings. See descriptions in \
            :const:`possible_settings`.
        :type settings: dict
        """

        if settings is None:
            settings = {}

        # Check all required settings are present in the "settings" argument
        self._settings = {}
        if 'simple or compound' in settings:
            self._settings['simple or compound'] = settings['simple or compound']
        else:
            self._settings['simple or compound'] = \
                IntervalIndexer.default_settings['simple or compound']  # pylint: disable=C0301
        if 'quality' in settings:
            self._settings['quality'] = settings['quality']
        else:
            self._settings['quality'] = IntervalIndexer.default_settings['quality']

        super(IntervalIndexer, self).__init__(score, None)

        # Which indexer function to set?
        if self._settings['quality']:
            if 'simple' == self._settings['simple or compound']:
                self._indexer_func = indexer_qual_simple
            else:
                self._indexer_func = indexer_qual_comp
        else:
            if 'simple' == self._settings['simple or compound']:
                self._indexer_func = indexer_nq_simple
            else:
                self._indexer_func = indexer_nq_comp

    def run(self):
        """
        Make a new index of the piece.

        :returns: A dictionary of the new interval indices. Find part combinations by using the
            index of the parts as provided to the :meth:`__init__` method, set as a string with
            a comma. Refer to the "Example" below.
        :rtype: dict of :class:`pandas.Series`

        ** Example **

        To access the intervals between the two highest parts in a score:

        >>> result = an_interval_indexer.run()
        >>> result['0,1']
        Series([], type: object)  # whatever intervals
        """
        combinations = []
        # To calculate all 2-part combinations:
        for left in xrange(len(self._score)):
            # noinspection PyArgumentList
            for right in xrange(left + 1, len(self._score)):
                combinations.append([left, right])

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing, like adding a label for voice combinations.
        post = {}
        for i, combo in enumerate(combinations):
            post[unicode(combo[0]) + u',' + unicode(combo[1])] = results[i]

        # Return the results.
        return post


class HorizontalIntervalIndexer(IntervalIndexer):
    """
    Use :class:`music21.interval.Interval` to create an index of the horizontal (melodic) intervals
    in a single part.

    You should provide the result of :class:`NoteRestIndexer`.
    """

    def __init__(self, score, settings=None):
        """
        The output format is described in :meth:`run`.

        :param score: The output of :class:`NoteRestIndexer` for all parts in a piece.
        :type score: list of :class:`pandas.Series`
        :param settings: Required and optional settings. See descriptions in \
            :const:`IntervalIndexer.possible_settings`.
        :type settings: ``dict``
        """
        super(HorizontalIntervalIndexer, self).__init__(score, settings)

    def run(self):
        """
        Make a new index of the piece.

        :returns: A list of the new indices. The index of each Series corresponds to the index it \
            has in the list of :class:`Series` given to the constructor.
        :rtype: ``list`` of :class:`pandas.Series`
        """
        # This indexer is a little tricky, since we must fake "horizontality" so we can use the
        # same _do_multiprocessing() method as in the IntervalIndexer.

        # First we'll make two copies of each part's NoteRest index. One copy will be missing the
        # first element, and the other will be missing the last element. We'll also use the index
        # values starting at the second element, so that each "horizontal" interval is presented
        # as occurring at the offset of the second note involved.
        new_parts = [x.iloc[1:] for x in self._score]
        self._score = [pandas.Series(x.values[:-1], index=x.index.tolist()[1:]) for x in self._score]

        new_zero = len(self._score)
        self._score.extend(new_parts)

        # Calculate each voice with its copy. "new_parts" is put first, so it's considered the
        # "upper voice," so ascending intervals don't get a direction.
        combinations = [[new_zero + x, x] for x in xrange(new_zero)]

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        return self._do_multiprocessing(combinations)
