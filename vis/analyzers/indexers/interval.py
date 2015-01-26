#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/interval.py
# Purpose:                Index vertical intervals.
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
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>

Index intervals. Use the :class:`IntervalIndexer` to find vertical (harmonic) intervals between two
parts. Use the :class:`HorizontalIntervalIndexer` to find horizontal (melodic) intervals in the
same part.
"""

# disable "string statement has no effect"... it's for sphinx
# pylint: disable=W0105

import six
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
import pandas
from music21 import note, interval, pitch
from vis.analyzers import indexer


def real_indexer(simultaneity, simple, quality):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.

    :param simultaneity: A two-item iterable with the note names for the higher and lower parts,
        respectively.
    :type simultaneity: list of string
    :param simple: Whether intervals should be reduced to their single-octave version.
    :type simple: boolean
    :param quality: Whether the interval's quality should be prepended.
    :type quality: boolean

    :returns: ``'Rest'`` if one or more of the parts is ``'Rest'``; otherwise, the interval
        between the parts.
    :rtype: string
    """

    if 2 != len(simultaneity):
        return None
    else:
        try:
            upper, lower = simultaneity
            interv = interval.Interval(note.Note(lower), note.Note(upper))
        except pitch.PitchException:
            return 'Rest'
        post = '-' if interv.direction < 0 else ''
        if quality:
            # We must get all of the quality, and none of the size (important for AA, dd, etc.)
            q_str = ''
            for each in interv.name:
                if each in 'AMPmd':
                    q_str += each
            post += q_str
        if simple:
            post += six.u(str(interv.generic.semiSimpleUndirected))
        else:
            post += six.u(str(interv.generic.undirected))
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

    You should provide the result of the :class:`~vis.analyzers.indexers.noterest.NoteRestIndexer`.
    However, to increase your flexibility, the constructor requires only a list of :class:`Series`.
    You may also provide a :class:`DataFrame` exactly as outputted by the
    :class:`NoteRestIndexer`.
    """

    required_score_type = 'pandas.Series'
    possible_settings = ['simple or compound', 'quality']
    """
    A list of possible settings for the :class:`IntervalIndexer`.

    :keyword str 'simple or compound': Whether intervals should be represented in their \
        single-octave form (either ``'simple'`` or ``'compound'``).
    :keyword boolean 'quality': Whether to display an interval's quality.
    """

    default_settings = {'simple or compound': 'compound', 'quality': False}
    "A dict of default settings for the :class:`IntervalIndexer`."

    def __init__(self, score, settings=None):
        """
        :param score: The output of :class:`NoteRestIndexer` for all parts in a piece, or a list of
            :class:`Series` of the style produced by the :class:`NoteRestIndexer`.
        :type score: list of :class:`pandas.Series` or :class:`pandas.DataFrame`
        :param dict settings: Required and optional settings. Refer to descriptions in \
            :const:`possible_settings`.
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

        :returns: A :class:`DataFrame` of the new indices. The columns have a :class:`MultiIndex`;
            refer to the example below for more details.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        >>> the_score = music21.converter.parse('sibelius_5-i.mei')
        >>> the_score.parts[5]
        (the first clarinet Part)
        >>> the_notes = NoteRestIndexer(the_score).run()
        >>> the_notes['noterest.NoteRestIndexer']['5']
        (the first clarinet Series)
        >>> the_intervals = IntervalIndexer(the_notes).run()
        >>> the_intervals['interval.IntervalIndexer']['5,6']
        (Series with vertical intervals between first and second clarinet)
        """
        combinations = []
        combination_labels = []
        # To calculate all 2-part combinations:
        for left in xrange(len(self._score)):
            for right in xrange(left + 1, len(self._score)):
                combinations.append([left, right])
                combination_labels.append('{},{}'.format(left, right))

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Return the results.
        return self.make_return(combination_labels, results)


class HorizontalIntervalIndexer(IntervalIndexer):
    """
    Use :class:`music21.interval.Interval` to create an index of the horizontal (melodic) intervals
    in a single part.

    You should provide the result of :class:`~vis.analyzers.noterest.NoteRestIndexer`.
    """

    possible_settings = ['horiz_attach_later']
    """
    This setting applies to the :class:`HorizontalIntervalIndexer` *in addition to* the settings
    available from the :class:`IntervalIndexer`.

    :keyword boolean 'horiz_attach_later': If ``True``, the offset for a horizontal interval is
        the offset of the later note in the interval. The default is ``False``, which gives
        horizontal intervals the offset of the first note in the interval.
    """

    default_settings = {'horiz_attach_later': False}

    def __init__(self, score, settings=None):
        """
        The output format is described in :meth:`run`.

        :param score: The output of :class:`NoteRestIndexer` for all parts in a piece.
        :type score: list of :class:`pandas.Series`
        :param dict settings: Required and optional settings. See descriptions in \
            :const:`IntervalIndexer.possible_settings`.
        """
        if settings is None:
            settings = {}

        super(HorizontalIntervalIndexer, self).__init__(score, settings)

        if 'horiz_attach_later' in settings:
            self._settings['horiz_attach_later'] = settings['horiz_attach_later']
        else:
            self._settings['horiz_attach_later'] = HorizontalIntervalIndexer.default_settings['horiz_attach_later']  # pylint: disable=line-too-long

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices. Refer to the example below.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        >>> the_score = music21.converter.parse('sibelius_5-i.mei')
        >>> the_score.parts[5]
        (the first clarinet Part)
        >>> the_notes = NoteRestIndexer(the_score).run()
        >>> the_notes['noterest.NoteRestIndexer']['5']
        (the first clarinet Series)
        >>> the_intervals = HorizontalIntervalIndexer(the_notes).run()
        >>> the_intervals['interval.HorizontalIntervalIndexer']['5']
        (Series with melodic intervals of the first clarinet)
        """
        # This indexer is a little tricky, since we must fake "horizontality" so we can use the
        # same _do_multiprocessing() method as in the IntervalIndexer.

        # First we'll make two copies of each part's NoteRest index. One copy will be missing the
        # first element, and the other will be missing the last element. We'll also use the index
        # values starting at the second element, so that each "horizontal" interval is presented
        # as occurring at the offset of the second note involved.
        combination_labels = [six.u(str(x)) for x in xrange(len(self._score))]
        if self._settings['horiz_attach_later']:
            new_parts = [x.iloc[1:] for x in self._score]
            self._score = [pandas.Series(x.values[:-1], index=x.index[1:]) for x in self._score]
        else:
            new_parts = [pandas.Series(x.values[1:], index=x.index[:-1]) for x in self._score]
            self._score = [pandas.Series(x.values[:-1], index=x.index[:-1]) for x in self._score]

        new_zero = len(self._score)
        self._score.extend(new_parts)

        # Calculate each voice with its copy. "new_parts" is put first, so it's considered the
        # "upper voice," so ascending intervals don't get a direction.
        combinations = [[new_zero + x, x] for x in xrange(new_zero)]

        results = self._do_multiprocessing(combinations)
        return  self.make_return(combination_labels, results)
