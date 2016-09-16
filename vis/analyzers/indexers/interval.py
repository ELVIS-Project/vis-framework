#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/interval.py
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
import pandas
from music21 import note, interval, pitch
from vis.analyzers import indexer

def real_indexer_func(simultaneity, analysis_type):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.

    :param simultaneity: A two-item iterable with the note names for the higher and lower parts, \
        respectively.
    :type simultaneity: list of string
    :param simple: Whether intervals should be reduced to their single-octave version.
    :type simple: boolean
    :param quality: Whether the interval's quality should be prepended.
    :type quality: boolean
    :param directed: Whether notes can be negative. If True, prepends a '-' before everything \
        else if the first note in simultaneity is higher than the second.
    :type directed: boolean

    :returns: ``'Rest'`` if one or more of the parts is ``'Rest'``; otherwise, the interval \
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
        return analysis_type(interv)


# We give the functions below to the multiprocessor; they're pickle-able and they basically help us 
# apply the appropriate analysis settings. The settings requested by the user are set in the init
# method and are all applied with the use of the xxxx_analysis functions. They appear below in the 
# same order as their position in the indexer_funcs list. Each indexer_xxxx method is immediately 
# followed by the xxxx_analysis method that it passes to real_indexer_func_func.


def indexer_dnq_dir_sim(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func_func` such that quality-free diatonic intervals that are directed and \
    simple (i.e. -8 to 8 with no zero) are returned.
    """
    return real_indexer_func(ecks, dnq_dir_sim_analysis)

def dnq_dir_sim_analysis(interv):
    return str(interv.generic.semiSimpleDirected)
#-----
def indexer_dwq_dir_sim(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that diatonic intervals with quality that are directed and \
    simple (i.e. -A8 to A8 with no zero) are returned.
    """
    return real_indexer_func(ecks, dwq_dir_sim_analysis)

def dwq_dir_sim_analysis(interv):
    post = '-' if interv.direction == -1 else ''
    return post + interv.semiSimpleName
#-----
def indexer_chr_dir_sim(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that chromatic intervals that are directed and simple \
    (i.e. -11 to 11) are returned.
    """
    return real_indexer_func(ecks, chr_dir_sim_analysis)

def chr_dir_sim_analysis(interv):
    return str(interv.chromatic.simpleDirected)
#-----
def indexer_icl_dir_sim(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that interval-class intervals that are directed and simple \
    (i.e. -6 to 6) are returned.
    """
    return real_indexer_func(ecks, icl_dir_sim_analysis)

def icl_dir_sim_analysis(interv):
    post = '-' if interv.direction == -1 else ''
    return post + str(interv.intervalClass)

#-----------------------------------------*

def indexer_dnq_und_sim(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that quality-free diatonic intervals that are undirected and \
    simple (i.e. 1 to 8) are returned.
    """
    return real_indexer_func(ecks, dnq_und_sim_analysis)

def dnq_und_sim_analysis(interv):
    return str(interv.generic.semiSimpleUndirected)
#-----
def indexer_dwq_und_sim(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that quality-free diatonic intervals that are undirected and \
    simple (i.e. P1 to A8) are returned.
    """
    return real_indexer_func(ecks, dwq_und_sim_analysis)

def dwq_und_sim_analysis(interv):
    return interv.semiSimpleName
#-----
def indexer_chr_und_sim(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that chromatic intervals that are undirected and simple \
    (i.e. 0 to 11) are returned.
    """
    return real_indexer_func(ecks, chr_und_sim_analysis)

def chr_und_sim_analysis(interv):
    return str(interv.chromatic.simpleUndirected)
#-----
def indexer_icl_und_sim(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that interval-class intervals that are undirected and simple \
    (i.e. 0 to 6) are returned.
    """
    return real_indexer_func(ecks, icl_und_sim_analysis)

def icl_und_sim_analysis(interv):
    return str(interv.intervalClass)


#-----------------------------------------*

def indexer_dnq_dir_com(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that quality-free diatonic intervals that are directed and \
    compound (i.e. negative infinity to infinity with no zero) are returned.
    """
    return real_indexer_func(ecks, dnq_dir_com_analysis)

def dnq_dir_com_analysis(interv):
    return str(interv.generic.directed)
#-----
def indexer_dwq_dir_com(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that diatonic intervals with quality that are directed and \
    compound (i.e. negative infinity to infinity with no zero) are returned.
    """
    return real_indexer_func(ecks, dwq_dir_com_analysis)

def dwq_dir_com_analysis(interv):
    post = '-' if interv.direction == -1 else ''
    return post + interv.name
#-----
def indexer_chr_dir_com(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that chromatic intervals that are directed and compound \
    (i.e. negative infinity to infinity) are returned.
    """
    return real_indexer_func(ecks, chr_dir_com_analysis)

def chr_dir_com_analysis(interv):
    return str(interv.semitones)

#-----------------------------------------*

def indexer_dnq_und_com(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that quality-free diatonic intervals that are undirected and \
    compound (i.e. 1 to infinity) are returned.
    """
    return real_indexer_func(ecks, dnq_und_com_analysis)

def dnq_und_com_analysis(interv):
    return str(interv.generic.undirected)
#-----
def indexer_dwq_und_com(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that diatonic intervals with quality that are undirected and \
    compound (i.e. P1 to infinity) are returned.
    """
    return real_indexer_func(ecks, dwq_und_com_analysis)

def dwq_und_com_analysis(interv):
    return interv.name
#-----
def indexer_chr_und_com(ecks):
    """
    Used internally by the :class:`IntervalIndexer` and :class:`HorizontalIntervalIndexer`.
    Calls :func:`real_indexer_func` such that chromatic intervals that are undirected and compound \
    (i.e. 0 to infinity) are returned.
    """
    return real_indexer_func(ecks, chr_und_com_analysis)

def chr_und_com_analysis(interv):
    return str(interv.chromatic.undirected)

#-----------------------------------------*

#                    NO_QUALITY      -    WITH_QUALITY    -     CHROMATIC      -  INTERVAL CLASS
indexer_funcs = (indexer_dnq_dir_sim, indexer_dwq_dir_sim, indexer_chr_dir_sim, indexer_icl_dir_sim,        # DIRECTED   & SIMPLE
                 indexer_dnq_und_sim, indexer_dwq_und_sim, indexer_chr_und_sim, indexer_icl_und_sim,        # UNDIRECTED & SIMPLE
                 indexer_dnq_dir_com, indexer_dwq_dir_com, indexer_chr_dir_com, None,                       # DIRECTED   & COMPOUND
                 indexer_dnq_und_com, indexer_dwq_und_com, indexer_chr_und_com, None)                       # UNDIRECTED & COMPOUND



class IntervalIndexer(indexer.Indexer):
    """
    Use :class:`music21.interval.Interval` to create an index of the vertical (harmonic) intervals
    between two-part combinations.

    You should provide the result of the :class:`~vis.analyzers.indexers.noterest.NoteRestIndexer`.
    However, to increase your flexibility, the constructor requires only a list of :class:`Series`.
    You may also provide a :class:`DataFrame` exactly as outputted by the
    :class:`NoteRestIndexer`.

    The settings for the :class:`IntervalIndexer` are as follows:
    :keyword str 'simple or compound': Whether intervals should be represented in their \
        single-octave form (either ``'simple'`` or ``'compound'``).
    :keyword bool or string 'quality': Whether to display diatonic intervals without quality \
        (either False or "diatonic no quality"), diatonic intervals with quality (either True or \
        'diatonic with quality'), chromatic intervals (use 'chromatic'), or interval class intervals \
        (use 'interval class').
    :keyword boolean 'directed': Whether we distinguish between which note is higher than the other. \
        If True (default), prepends a '-' before everything else if the first note passed is higher \
        than the second.
    :keyword boolean 'mp': Multiprocesses when True (default) or processes serially when False.
    """
    required_score_type = 'pandas.Series'
    default_settings = {'simple or compound': 'compound', 'quality': False, 'directed':True, 'mp': True}
    "A dict of default settings for the :class:`IntervalIndexer`."

    def __init__(self, score, settings=None):
        """
        :param score: The output of :class:`NoteRestIndexer` for all parts in a piece, or a list of
            :class:`Series` of the style produced by the :class:`NoteRestIndexer`.
        :type score: list of :class:`pandas.Series` or :class:`pandas.DataFrame`
        :param dict settings: Required and optional settings.
        """
        # TODO: add runtime warning for people who set compound

        self._settings = IntervalIndexer.default_settings.copy()
        if settings is not None:
            self._settings.update(settings)
        
        super(IntervalIndexer, self).__init__(score, None)

        if self._settings['simple or compound'] == 'compound' and self._settings['quality'] == 'interval class':
            raise RuntimeWarning('Interval class analysis cannot be compound, so the simple or compound setting has been reset to compound')
            self._settings['simple or compound'] = 'simple'

        # Use binary-inspired system to choose one of 14 indexer_funcs.
        indexer_number = 0

        # This block deals with the four quality settings. True and False are offered as options to
        # accommodate the old setting types when we only offered two options for interval quality.
        if self._settings['quality'] == False or self._settings['quality'] == 'diatonic no quality':
            pass
        elif self._settings['quality'] == True or self._settings['quality'] == 'diatonic with quality':
            indexer_number += 1
        elif self._settings['quality'] == 'chromatic':
            indexer_number += 2
        else: # i.e. self._settings['quality'] == 'interval class'
            indexer_number += 3

        # This block determines if the intervals are directed or not, that is, whether they can be negative or not.
        if not self._settings['directed']:
            indexer_number += 4

        # This block decides between simple, i.e. within an octave, or compound intervals.
        if self._settings['simple or compound'] == 'compound':
            indexer_number += 8

        self._indexer_func = indexer_funcs[indexer_number]



    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` of the new indices. The columns have a :class:`MultiIndex`;
            refer to the example below for more details.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        import music21
        from vis.analyzers.indexers import noterest, interval

        score = music21.converter.parse('example.xml')
        notes = noterest.NoteRestIndexer(score).run()
        v_ints = interval.IntervalIndexer(notes).run()

        # to see all the intervals 
        print(v_ints)

        # to see only one pair
        print(v_ints['interval.IntervalIndexer']['0,1'])

        """
        combinations = []
        combination_labels = []
        # To calculate all 2-part combinations:
        for left in range(len(self._score)):
            for right in range(left + 1, len(self._score)):
                combinations.append([left, right])
                combination_labels.append('{},{}'.format(left, right))

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations, on=self._settings['mp'])

        # Return the results.
        return self.make_return(combination_labels, results)


class HorizontalIntervalIndexer(IntervalIndexer):
    """
    Use :class:`music21.interval.Interval` to create an index of the horizontal (melodic) intervals
    in a single part.

    You should provide the result of :class:`~vis.analyzers.noterest.NoteRestIndexer`. Alternatively
    you could provide the results of the :class:'~vis.analyzers.offset.FilterByOffsetIndexer' if you
    want to check for horizontal intervals at regular durational intervals.

    These settings apply to the :class:`HorizontalIntervalIndexer` *in addition to* the settings
    available from the :class:`IntervalIndexer`.

    :keyword str 'simple or compound': Whether intervals should be represented in their \
        single-octave form (either ``'simple'`` or ``'compound'``).
    :keyword bool or string 'quality': Whether to display diatonic intervals without quality \
        (either False or "diatonic no quality"), diatonic intervals with quality (either True or \
        'diatonic with quality'), chromatic intervals (use 'chromatic'), or interval class intervals \
        (use 'interval class').
    :keyword boolean 'directed': Whether we distinguish between which note is higher than the other. \
        If True (default), prepends a '-' before everything else if the first note passed is higher \
        than the second.
    :keyword boolean 'horiz_attach_later': If ``True``, the offset for a horizontal interval is \
        the offset of the later note in the interval. The default is ``False``, which gives \
        horizontal intervals the offset of the first note in the interval.
    :keyword boolean 'mp': Multiprocesses when True (default) or processes serially when False.
    """

    default_settings = {'simple or compound': 'compound', 'quality': False, 'directed':True, 
                        'horiz_attach_later': False, 'mp': True}

    def __init__(self, score, settings=None):
        """
        The output format is described in :meth:`run`.

        :param score: The output of :class:`NoteRestIndexer` for all parts in a piece.
        :type score: list of :class:`pandas.Series`
        :param dict settings: Required and optional settings.
        """
        self._settings = HorizontalIntervalIndexer.default_settings.copy()
        if settings is not None:
            self._settings.update(settings)
        super(HorizontalIntervalIndexer, self).__init__(score, self._settings)

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices. Refer to the example below.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        import music21
        from vis.analyzers.indexers import noterest, interval

        score = music21.converter.parse('example.xml')
        notes = noterest.NoteRestIndexer(score).run()
        h_ints = interval.HorizontalIntervalIndexer(notes).run()

        # to see all the intervals
        print(h_ints)

        # to see only one part's intervals
        print(h_ints['interval.HorizontalIntervalIndexer']['0'])
        """
        # This indexer is a little tricky, since we must fake "horizontality" so we can use the
        # same _do_multiprocessing() method as in the IntervalIndexer.

        # First we'll make two copies of each part's NoteRest index. One copy will be missing the
        # first element, and the other will be missing the last element. We'll also use the index
        # values starting at the second element, so that each "horizontal" interval is presented
        # as occurring at the offset of the second note involved.
        combination_labels = [six.u(str(x)) for x in range(len(self._score))]
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
        combinations = [[new_zero + x, x] for x in range(new_zero)]

        results = self._do_multiprocessing(combinations, on=self._settings['mp'])
        return  self.make_return(combination_labels, results)
