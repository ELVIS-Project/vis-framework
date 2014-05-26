#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/template.py
# Purpose:                Template indexer
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

Template for writing a new indexer. Use this class to help write a new :class`Indexer` subclass. \
The :class:`TemplateIndexer` does nothing, and should only be used by programmers.
"""
# NOTE: you should replace my name with yours, in the "codeauthor" directive above

from music21 import stream
from vis.analyzers import indexer


# NB: remove this comment and the "pylint: disable" comment below when you write a subclass
# pylint: disable=W0613
def indexer_func(obj):
    """
    The function that indexes.

    **Parameters for Indexers Using a Score**
    :param obj: The simultaneous event(s) to use when creating this index.
    :type obj: list of the types stored in self._types

    **Parameters for Indexers Using a Series**
    :param obj: The simultaneous event(s) to use when creating this index.
    :type obj: :obj:`pandas.Series` of :obj:`unicode`

    :returns: The value to store for this index at this offset.
    :rtype: :obj:`unicode`
    """
    return None


class TemplateIndexer(indexer.Indexer):
    """
    Template for an :class:`Indexer` subclass.
    """

    required_score_type = stream.Part
    """
    Depending on how this Indexer works, you'll either need to provide :class:`music21.stream.Part`,
    :class:`music21.stream.Score`, or :class:`pandas.Series`.
    """

    possible_settings = [u'fake_setting']
    """
    This is a list of basestrings that are the names of the settings used in this indexer. Specify
    the types and reasons for each setting as though it were an argument list, like this:

    :keyword u'fake_setting': This is a fake setting.
    :type u'fake_setting': boolean
    """

    default_settings = {}
    """
    The default values for settings named in :const:`possible_settings`. If a setting doesn't have
    a value in this constant, then it must be specified to the constructor at runtime, or the
    constructor should raise a :exc:`RuntimeException`.
    """

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: ``list`` of :class:`pandas.Series`, :class:`music21.stream.Part`, or \
            :class:`music21.stream.Score`
        :param settings: All the settings required by this Indexer. All required settings should be
            listed in subclasses. Default is None.
        :type settings: ``dict`` or ``None``

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        :raises: :exc:`RuntimeError` if required settings are not present in ``settings``.
        """

        # Check all required settings are present in the "settings" argument. You must ignore
        # extra settings.
        # If there are no settings, you may safely remove this.
        if settings is None:
            self._settings = {}

        # Change "TemplateIndexer" to the current class name. The superclass will handle the
        # "score" argument, but you should have processed "settings" above, so it should not be
        # sent to the superclass constructor.
        super(TemplateIndexer, self).__init__(score, None)

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = []

        # You probably do not want to change this
        # NB: The lambda function receives events in a list of all voices in the current voice
        #     combination; if this Indexer processes one voice at a time, it's a one-element list.
        #     The function receives the unmodified object, the type of which is either in
        #     self._types object or music21.base.ElementWrapper.
        # NB: For an example of how to use settings, see vis.analyzers.indexers.interval.py
        self._indexer_func = indexer_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A list of the new indices. The index of each Series corresponds to the index of
            the Part used to generate it, in the order specified to the constructor. Each element
            in the Series is a basestring.
        :rtype: :obj:`list` of :obj:`pandas.Series`
        """

        # NOTE: We recommend indexing all possible voice combinations, whenever feasible.

        # To calculate each part separately:
        combinations = [[x] for x in xrange(len(self._score))]

        # To calculate all 2-part combinations:
        #for left in xrange(len(self._score)):
        #    for right in xrange(left + 1, len(self._score)):
        #        combinations.append([left, right])

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing, like adding a label for voice combinations.

        # Return the results.
        return results
