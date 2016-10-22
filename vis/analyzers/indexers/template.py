#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/template.py
# Purpose:                Template indexer
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
# You should have received a copy of the GNU Affero General Public 
# License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------- #
"""
.. codeauthor:: Christopher Antila <christopher@antila.ca>

Template for writing a new indexer. Use this class to help write a new 
:class`Indexer` subclass. The :class:`TemplateIndexer` does nothing, and 
should only be used by programmers.

.. note:: Follow these instructions to write a new :class:`Indexer` 
    subclass:

    #. Replace my name with yours in the "codeauthor" directive above.
    #. Change the "Filename" and "Purpose" on lines 7 and 8.
    #. Modify the "Copyright" on line 10 *or* add an additional 
        copyright line immediately below.
    #. Remove the ``# pylint: disable=W0613`` comment just before 
        :func:`indexer_func`.
    #. Rename the class.
    #. Adjust :attr:`required_score_type`.
    #. Add settings to :attr:`possible_settings` and 
        :attr:`default_settings`, as required.
    #. Rewrite the documentation for :meth:`__init__`.
    #. Rewrite the documentation for :meth:`~TemplateIndexer.run`.
    #. Rewrite the documentation for :func:`indexer_func`.
    #. Write all relevant tests for :meth:`__init__`, 
        :meth:`~TemplateIndexer.run`, and :func:`indexer_func`.
    #. Follow the instructions in :meth:`__init__` to write that method.
    #. Follow the instructions in :meth:`~TemplateIndexer.run` to write 
        that method.
    #. Write a new :func:`indexer_func`.
    #. Ensure your tests pass, adding additional ones as required.
    #. Finally, run ``pylint`` with the VIS style rules.
"""

import six
from vis.analyzers import indexer


# pylint: disable=W0613

def indexer_func(obj):
    """
    The function that indexes.

    :param obj: The simultaneous event(s) to use when creating this 
        index. (For indexers using a :class:`Score`).
    :type obj: list of objects of the types stored in 
        :attr:`TemplateIndexer._types`

    **or**

    :param obj: The simultaneous event(s) to use when creating this 
        index. (For indexers using a :class:`Series`).
    
    :type obj: :class:`pandas.Series` of strings

    :returns: The value to store for this index at this offset.
    
    :rtype: str
    """
    return None


class TemplateIndexer(indexer.Indexer):
    """
    Template for an :class:`Indexer` subclass.
    """

    required_score_type = 'stream.Part'
    # required_score_type = 'stream.Score'
    # required_score_type = 'pandas.Series'
    # required_score_type = 'pandas.DataFrame'
    """
    Depending on how this indexer works, you must provide a 
    :class:`DataFrame`, a :class:`Score`, or list of :class:`Part` or 
    :class:`Series` objects. Only choose :class:`Part` or 
    :class:`Series` if the input will always have single-integer part 
    combinations (i.e., there are no combinations---it will be each part 
    independently).
    """

    possible_settings = ['fake_setting']
    """
    This is a list of string that are the names of the settings used in 
    this indexer. Specify the types and reasons for each setting as 
    though it were an argument list, like this:

    :keyword 'fake_setting': This is the description of a fake setting.
    :type 'fake_setting': boolean
    """

    default_settings = {}
    """
    The default values for settings named in :const:`possible_settings`. 
    If a setting doesn't have a value in this constant, then it must be 
    specified to the constructor at runtime, or the constructor should 
    raise a :exc:`RuntimeException`.
    """

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. Refer 
            to the superclass :class:`~vis.analyzers.indexer.Indexer` 
            for more information about what to require here.
        :type score: :class:`pandas.DataFrame`, 
            :class:`music21.stream.Score`, or list of 
            :class:`pandas.Series` or :class:`music21.stream.Part`
        :param settings: All the settings required by this Indexer. All 
            required settings should be listed in subclasses. Default is 
            ``None``.
        :type settings: dict or None

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong 
            type.
        :raises: :exc:`RuntimeError` if the required settings are not 
            present in the ``settings`` argument.
        :raises: :exc:`IndexError` if ``required_score_type`` is 
            ``'pandas.Series'`` and the ``score`` argument is an 
            improperly-formatted :class:`DataFrame` (e.g., it contains 
            the results of more than one indexer, does not contain 
            results of the required indexers, or the columns do not have 
            a :class:`MultiIndex`).
        """
        # NOTE: you should make the exceptions more specific, if 
        # possible
        # Check all required settings are present in the "settings" 
        # argument. You must ignore extra settings.
        # If there are no settings, you may safely remove this.
        if settings is None:
            self._settings = {}

        # Change "TemplateIndexer" to the current class name.
        # You must provide "score" here---do not modify it.
        # You must handle the settings by yourself.
        super(TemplateIndexer, self).__init__(score, None)

        # If self._score is a Stream (subclass), change to a list of 
        # types you want to process
        self._types = []

        # You probably do not want to change this
        # NB: The lambda function receives events in a list of all 
        #     voices in the current voice combination; if this Indexer 
        #     processes one voice at a time, it's a one-element list.
        #     The function receives the unmodified object, the type of 
        #     which is either in self._types object or 
        #     music21.base.ElementWrapper.
        # NB: For an example of how to use settings, see 
        #     vis.analyzers.indexers.interval.py
        self._indexer_func = indexer_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices. Refer to the note below.
        :rtype: :class:`pandas.DataFrame` or list of 
            :class:`pandas.Series`

        .. important:: Please be sure you read and understand the rules 
            about return values in the full documentation for 
            :meth:`~vis.analyzers.indexer.Indexer.run` and
            :func:`~vis.analyzers.indexer.Indexer.make_return`.
        """

        # NOTE: We recommend indexing all possible voice combinations, 
        #       whenever feasible.

        # To calculate each part separately:
        combinations = [[x] for x in range(len(self._score))]

        # To calculate all 2-part combinations:
        #for left in range(len(self._score)):
        #    for right in range(left + 1, len(self._score)):
        #        combinations.append([left, right])

        # This method returns once all computation is complete. The 
        # results are returned as a list of Series objects in the same 
        # order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing.

        # Convert results to a DataFrame in the appropriate format, then 
        # return it. This will work as written for nearly all cases, but 
        # refer to the documentation for make_return() for more 
        # information. The string-slicing simply removes the 
        # ``'['`` and ``']'`` characters that appear because each 
        # combination is a list.
        return self.make_return([six.u(x)[1:-1] 
            for x in combinations], results)
