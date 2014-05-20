#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/lilypond.py
# Purpose:                LilyPondIndxexer
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

The :class:`LilyPondIndexer` uses the :mod:`outputlilypond` module to produces the LilyPond file
that should produce a score of the input.
"""

# Disable "string statement has no effect"
# pylint: disable=W0105

from math import fsum
import pandas
from music21 import stream, note, duration
import outputlilypond
from outputlilypond import settings as oly_settings
from vis.analyzers import indexer


def annotation_func(obj):
    """
    Used by :class:`AnnotationIndexer` to make a "markup" command for LilyPond scores.

    :param obj: A single-element :class:`Series` with the string to wrap in a "markup" command.
    :type obj: :class:`pandas.Series` of ``unicode``

    :returns: The thing in a markup.
    :rtype: ``unicode``
    """
    return u''.join([u'_\\markup{ "', unicode(obj[0]), u'" }'])


def annotate_the_note(obj):
    """
    Used by :class:`AnnotateTheNoteIndexer` to make a :class:`~music21.note.Note` object with the
    annotation passed in. Take note (hahaha): the ``lily_invisible`` property is set to ``True``!

    :param obj: A single-element :class:`Series` with the string to put as the ``lily_markup``
        property of a new :class:`Note`.
    :type obj: :class:`pandas.Series` of ``unicode``

    :returns: An annotated note.
    :rtype: :class:`music21.note.Note`
    """
    post = note.Note()
    post.lily_invisible = True
    post.lily_markup = obj[0]
    return post


class LilyPondIndexer(indexer.Indexer):
    """
    Use the :mod:`outputlilypond` module to produce the LilyPond file that should produce a score
    of the input.
    """

    required_score_type = stream.Score
    """
    You must provide a :class:`music21.stream.Score` to this Indexer.
    """

    possible_settings = [u'run_lilypond', u'output_pathname', u'annotation part']
    """
    Possible settings for the :class:`LilyPondIndexer` include:

    :keyword u'run_lilypond': Whether to run LilyPond; if ``False`` or omitted, simply produce the \
        input file LilyPond requires.
    :type u'run_lilypond': boolean

    :keyword u'output_pathname': Pathname for the resulting LilyPond output file. If \
        ``u'run_lilypond'`` is ``True``, you must include this setting. If u'run_lilypond' is \
        ``False`` and you do not provide ``u'output_pathname'`` then the output file is returned \
        by :meth:`run` as a ``unicode``.
    :type u'output_pathname': ``basestring``

    :keyword u'annotation_part': A :class:`Part` or list of :class:`Part` objects with annotation
        instructions for :mod:`outputlilypond`. This :class:`Part` will be appended as last in
        the :class:`Score`.
    :type u'annotation_part': :class:`music21.stream.Part` or list of :class:`Part`
    """

    default_settings = {u'run_lilypond': False, u'output_pathname': None, u'annotation_part': None}
    """
    Default settings.
    """

    # error message for when settings say to run LilyPond, but we have no pathname
    error_no_pathname = u'LilyPondIndexer cannot run LilyPond without saving output to a file.'

    def __init__(self, score, settings=None):
        """
        :param score: The :class:`Score` object to output to LilyPond.
        :type score: singleton list of :class:`music21.stream.Score`

        :param settings: Your settings. There are no required settings.
        :type settings: ``dict`` or :const:`None`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``u'run_lilypond'`` is ``True`` but ``u'output_pathname'`` \
            is unspecified.
        """
        settings = {} if settings is None else settings
        self._settings = {}
        # dealing with output_pathname is a little complicated...
        if u'output_pathname' in settings:
            self._settings[u'output_pathname'] = settings[u'output_pathname']
            if u'run_lilypond' in settings:
                self._settings[u'run_lilypond'] = settings[u'run_lilypond']
        else:
            self._settings[u'output_pathname'] = LilyPondIndexer.default_settings[u'output_pathname']
            if u'run_lilypond' in settings and settings[u'run_lilypond'] is True:
                raise RuntimeError(LilyPondIndexer.error_no_pathname)
        # if they didn't specify whether to run LilyPond
        if u'run_lilypond' not in self._settings:
            self._settings[u'run_lilypond'] = LilyPondIndexer.default_settings[u'run_lilypond']
        # deal with the annotation_part
        if u'annotation_part' in settings:
            self._settings[u'annotation_part'] = settings[u'annotation_part']
            if not isinstance(self._settings[u'annotation_part'], list):
                self._settings[u'annotation_part'] = [self._settings[u'annotation_part']]
        else:
            self._settings[u'annotation_part'] = LilyPondIndexer.default_settings[u'annotation_part']
        super(LilyPondIndexer, self).__init__(score, None)
        # We won't use an indexer function; run() is just going to pass the Score to outputlilypond
        self._indexer_func = None

    def run(self):
        """
        Make a string with the LilyPond representation of each score. Run LilyPond, if we're
        supposed to.

        :returns: A list of strings, where each string is the LilyPond-format representation of the
            score that was in that index.
        :rtype: ``list`` of ``unicode``
        """
        lily_setts = oly_settings.LilyPondSettings()
        # append analysis part, if present
        if self._settings[u'annotation_part'] is not None:
            for part in self._settings[u'annotation_part']:
                self._score[0].insert(0, part)
        # because outputlilypond uses multiprocessing by itself, we'll just call it in series
        the_score = outputlilypond.process_score(self._score[0], lily_setts)
        # output the score, if given a pathname
        if self._settings[u'output_pathname'] is not None:
            with open(self._settings[u'output_pathname'], 'w') as handle:
                handle.write(the_score)
        # call LilyPond on each file, if required
        if self._settings[u'run_lilypond'] is True:
            outputlilypond.run_lilypond(self._settings[u'output_pathname'], lily_setts)
        return the_score


class AnnotationIndexer(indexer.Indexer):
    """
    From any other index, put ``_\\markup{""}`` around it.
    """

    required_score_type = pandas.Series
    possible_settings = []
    default_settings = {}

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: ``list`` of :class:`pandas.Series`

        :param settings: Nothing.
        :type settings: ``dict`` or :const:`None`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(AnnotationIndexer, self).__init__(score, None)
        self._indexer_func = annotation_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A list of the new indices. The index of each :class:`Series` corresponds to the
            index of the :class:`Part` used to generate it, in the order specified to the
            constructor. Each element in the :class:`Series` is a ``basestring``.
        :rtype: ``list`` of :class:`pandas.Series`
        """
        # Calculate each part separately:
        combinations = [[x] for x in xrange(len(self._score))]
        return self._do_multiprocessing(combinations)


class AnnotateTheNoteIndexer(indexer.Indexer):
    """
    Make a new :class:`~music21.note.Note` object with the input set to the ``lily_markup``
    property, the ``lily_invisible`` property set to ``True``, and everything else as a default
    :class:`Note`.
    """

    required_score_type = pandas.Series
    possible_settings = []
    default_settings = {}

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: ``list`` of :class:`pandas.Series`

        :param settings: Nothing.
        :type settings: ``dict`` or :const:`None`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(AnnotateTheNoteIndexer, self).__init__(score, None)
        self._indexer_func = annotate_the_note

    def run(self):
        """
        Make a new index of the piece.

        :returns: A list of the new indices. The index of each :class:`Series` corresponds to the
            index of the :class:`Part` used to generate it, in the order specified to the
            constructor. Each element in the :class:`Series` is a ``basestring``.
        :rtype: ``list`` of :class:`pandas.Series`
        """
        # Calculate each part separately:
        combinations = [[x] for x in xrange(len(self._score))]
        return self._do_multiprocessing(combinations)


class PartNotesIndexer(indexer.Indexer):
    """
    From a :class:`Series` full of :class:`Note` objects, craft a :class:`music21.stream.Part`. The
    offset of each :class:`Note` in the output matches its index in the input :class:`Series`, and
    each ``duration`` property is set to match.

    To print a "name" along with the first item in a part, for example to indicate to which part
    or part combinations the annotations belong, use the optional ``part_names`` setting.
    """

    required_score_type = pandas.Series
    default_settings = {}
    possible_settings = [u'part_names']
    """
    :param part_names: Names for the annotation parts, in order. If there are more part names than
        parts, extra names will be ignored. If there are fewer part names than parts, some parts
        will not be named.
    :type part_names: list of basestring
    """

    _IMPOSSIBLE_QUARTERLENGTH = u'Impossible \'quarterLength\': %s.'

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: ``list`` of :class:`pandas.Series` of :class:`music21.note.Note`

        :param settings: Nothing.
        :type settings: ``dict`` or :const:`None`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(PartNotesIndexer, self).__init__(score, None)
        self._indexer_func = None
        if settings is not None and 'part_names' in settings:
            self._settings['part_names'] = settings['part_names']
        else:
            settings = {}

    @staticmethod
    def _fill_space_between_offsets(start_o, end_o):
        """
        Given two offsets, finds the ``quarterLength`` values that fill the whole duration.

        :param start_o: The starting offset.
        :type start_o: ``float``
        :param end_o: The ending offset.
        :type end_o: ``float``

        :returns: The ``quarterLength`` values that fill the whole duration (see below).
        :rtype: ``list`` of ``float``

        The algorithm tries to use as few ``quarterLength`` values as possible, but prefers multiple
        values to a single dotted value. The longest single value is ``4.0`` (a whole note).
        """
        VALID_DURATIONS = (2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0)  # pylint: disable=invalid-name

        def find_highest_valid_ql(this_ql, recursor=0):
            """
            Returns the largest quarterLength that is less then "this_ql" but not greater than 2.0.
            """
            if VALID_DURATIONS[recursor] <= this_ql:
                return VALID_DURATIONS[recursor]
            else:
                return find_highest_valid_ql(this_ql, recursor + 1)

        def the_solver(ql_remains):
            """
            Given the "quarterLength that remains to be dealt with," this method returns
            the solution.
            """
            if 0.0 == ql_remains:
                return [0.0]
            elif 4.0 == ql_remains:
                return [4.0]
            elif ql_remains > 4.0:
                return [4.0] + the_solver(ql_remains - 4.0)
            elif 4.0 > ql_remains >= 0.015625:
                highest = find_highest_valid_ql(ql_remains)
                if highest == ql_remains:
                    return [ql_remains]
                else:
                    return [highest] + the_solver(ql_remains - highest)
            else:
                raise RuntimeError(PartNotesIndexer._IMPOSSIBLE_QUARTERLENGTH % (end_o - start_o))

        return the_solver(float(end_o) - float(start_o))

    @staticmethod
    def _set_durations(in_part):
        """
        Set the durations for (:class:`Note`) objects in a :class:`Part` according to the offset
        values. Each :class`Note` will either occupy all the time until the next, or :class:`Rest`
        objects will be inserted so all the time is filled regardless. The final :class:`Note`
        will have a duration of 1.0.

        :param in_part: The :class:`Part` with :class:`~music21.note.Note` objects
            of which the :attr:`~music21.note.Note.duration` attribute will be modified.
        :type param: :class:`music21.stream.Part`

        :returns: A *new* :class:`Part` with modified :class:`Note` objects.
        :rtype: :class:`music21.stream.Part`

        **Examples**

        Input: [Note(offset=0.0), Note(offset=4.0)]
        Output: [Note(offset=0.0, duration=4.0), Note(offset=4.0, duration=1.0)]

        Input: [Note(offset=0.0), Note(offset=3.0)]
        Output: [Note(offset=0.0, duration=2.0),
                 Rest(offset=2.0, duration=1.0),
                 Note(offset=4.0, duration=1.0)]
        """
        in_len = len(in_part)
        ret_part = stream.Part()
        for i in xrange(in_len):
            qls = None
            try:
                qls = PartNotesIndexer._fill_space_between_offsets(in_part[i].offset,
                                                                   in_part[i + 1].offset)
            except stream.StreamException:  # when we try to access the note after the last
                qls = [1.0]
            in_part[i].duration = duration.Duration(quarterLength=qls[0])
            ret_part.insert(in_part[i].offset, in_part[i])
            for j in xrange(len(qls[1:])):
                # the offset for insertion is...
                #   offset of the Note object, plus
                #   duration of the Note object, plus
                #   duration of all the previously-inserted Rest objects
                ret_part.insert(in_part[i].offset + qls[0] + fsum(qls[1:j + 1]),
                                note.Rest(quarterLength=qls[j + 1]))
        if hasattr(in_part, u'lily_analysis_voice'):
            ret_part.lily_analysis_voice = in_part.lily_analysis_voice
        if hasattr(in_part, u'lily_instruction'):
            ret_part.lily_instruction = in_part.lily_instruction
        return ret_part

    @staticmethod
    def _prepend_rests(in_part):
        """
        Prepends rest objects to fill empty space at the beginning of a :class:`Series`. That is,
        if the first object in the :class:`Series` doesn't have offset ``0.0``, we add a
        :class:`Rest` at offset ``0.0``, and enough additional :class:`Rest` objects to fill the
        duration until the first inputted object.

        If the first object in the inputed :class:`Series` is at offset 0.0, no changes are made.

        :param in_part: The part to fill in.
        :type in_part: :class:`pandas.Series`

        :returns: The filled-in part.
        :type in_part: :class:`pandas.Series`
        """
        if 0.0 != in_part.index[0]:
            durations = PartNotesIndexer._fill_space_between_offsets(0.0, in_part.index[0])
            offsets = [max(0.0, sum(durations[:i])) for i in xrange(len(durations))]
            for i, offset in enumerate(offsets):
                in_part[offset] = note.Rest(quarterLength=durations[i])
            return in_part.sort_index()
        else:
            return in_part

    def run(self):
        """
        Make a new index of the piece.

        :returns: A list of the new indices. The index of each :class:`Part` corresponds to the
            index of the :class:`Series` used to generate it, in the order specified to the
            constructor. Each element in the :class:`Part` is a :class:`Note`.
        :rtype: ``list`` of :class:`music21.stream.Part`
        """
        post = []
        for i, each_series in enumerate(self._score):
            each_series = PartNotesIndexer._prepend_rests(each_series)
            new_part = stream.Part()
            new_part.lily_analysis_voice = True
            if 'part_names' in self._settings:
                new_part.lily_instruction = (u'\t\\textLengthOn\n'
                                             u'\t\\set Staff.instrumentName = "%s"\n'
                                             u'\t\\set Staff.shortInstrumentName = "%s"\n'
                                             % (self._settings['part_names'][i],
                                                self._settings['part_names'][i]))
            else:
                new_part.lily_instruction = u'\t\\textLengthOn\n'
            # put the Note objects into a new stream.Part, using the right offset
            for off, obj in each_series.iteritems():
                new_part.insert(off, obj)

            post.append(PartNotesIndexer._set_durations(new_part))
        return post
