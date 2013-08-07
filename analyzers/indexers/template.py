#! /usr/bin/python
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
Template indexer.
"""

from music21 import stream
from vis.analyzers import indexer


# pylint: disable=W0613
def indexer_func(obj):
    """
    docstring
    """
    return None


class TemplateIndexer(indexer.Indexer):
    """
    Template for a class to make an index of a music21 stream.

    Use this class when you want to write a new Indexer subclass.
    """

    required_indices = []  # empty list means the Indexer uses Part objects
    required_score_type = stream.Part  # or pandas.Series
    requires_score = True  # adjust according to previous
    possible_settings = []  # list of strings
    default_settings = {}  # keys are strings, values are anything

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new Indexer.

        Parameters
        ==========
        :param score: [pandas.Series] or [music21.stream.Part]
            Depending on how this Indexer works, this is a list of either Part or Series obejcts
            to use in creating a new index.

        :param settings: dict
            A dict of all the settings required by this Indexer. All required settings should be
            listed in subclasses. Default is {}.

        :param mpc : MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        RuntimeError :
            - If the "score" argument is the wrong type.
            - If the "score" argument is not a list of the same types.
            - If required settings are not present in the "settings" argument.
        """

        # Check all required settings are present in the "settings" argument. You must ignore
        # extra settings.
        if settings is None:
            self._settings = {}

        # Change "TemplateIndexer" to the current class name. The superclass will handle the
        # "score" and "mpc" arguments, but you should have processed "settings" above, so it should
        # not be sent to the superclass constructor.
        super(TemplateIndexer, self).__init__(score, None, mpc)

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

        Returns
        =======
        [pandas.Series] :
            A list of the new indices. The index of each Series corresponds to the index of the Part
            used to generate it, in the order specified to the constructor. Each element in the
            Series is an instance of music21.base.ElementWrapper.
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
