#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/analyzers/indexers/lilypond.py
# Purpose:                Indxexers related to LilyPond output.
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

Indexers related to producing LilyPond-format output from the VIS Framework. Also refer to the
:mod:`vis.analyzers.experimenters.lilypond` module.
"""

import six
from vis.analyzers import indexer


def annotation_func(obj):
    """
    Used by :class:`AnnotationIndexer` to make a "markup" command for LilyPond scores.

    :param obj: A single-element :class:`Series` with the string to wrap in a "markup" command.
    :type obj: :class:`pandas.Series` of ``str``

    :returns: The thing in a markup.
    :rtype: str
    """
    return six.u(''.join(['_\\markup{ "', str(obj[0]), '" }']))


class AnnotationIndexer(indexer.Indexer):
    """
    From any other index, put ``_\\markup{""}`` around it.
    """

    required_score_type = 'pandas.Series'
    possible_settings = ['mp']
    default_settings = {'mp': True}

    """
    :keyword 'mp': Multiprocesses when True (default) or processes serially when False.
    :type 'mp': boolean
    """

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: list of :class:`pandas.Series`
        :param settings: Nothing.
        :type settings: dict or NoneType

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(AnnotationIndexer, self).__init__(score, None)
        self._indexer_func = annotation_func

        if settings is not None and 'mp' in settings:
            self._settings['mp'] = settings['mp']
        else:
            self._settings['mp'] = AnnotationIndexer.default_settings['mp']

    def run(self):
        """
        Make a new index of the piece.

        :returns: A list of the new indices. The index of each :class:`Series` corresponds to the
            index of the :class:`Part` used to generate it, in the order specified to the
            constructor. Each element in the :class:`Series` is a ``str``.
        :rtype: :class:`pandas.DataFrame`
        """
        # Calculate each part separately:
        combinations = [[x] for x in range(len(self._score))]
        results = self._do_multiprocessing(combinations, on=self._settings['mp'])
        return self.make_return([six.u(str(x))[1:-1] for x in combinations], results)
