#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/experimenter.py
# Purpose:                Help with transforming time-attached analytic information to other types.
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

This module outlines the Experimenter base class, which helps with transforming time-attached
analytic information to other types.
"""


# noinspection PyUnusedLocal
class Experimenter(object):
    """
    Run an experiment on an IndexedPiece.

    Use the "Experimenter.required_indices" attribute to know which Indexer subclasses should be
    provided to this Experimenter's constructor. If the list is None or [], use the
    "Experimenter.required_experiments" attribute to know which Experimenter should be provided
    to the constructor.
    """

    # just the standard instance variables
    possible_settings = []
    default_settings = None
    # self._index

    # pylint: disable=W0613
    def __init__(self, index, settings=None):
        """
        Create a new Experimenter.

        :param index: lists or nested lists of pandas.Series or pandas.DataFrame objects.
            A list (or list of lists) of Series. The minimum and maximum numbers, and whether to use
            embedded lists, depends on the Experimenter subclass.

        :param settings: dict
            A dict of all the settings required by this Experimenter. All required settings should
            be listed in subclasses. Default is {}.

        :raises: RuntimeError, if required settings are not present in the "settings" argument.
        """

        # Call our superclass constructor, then set instance variables
        super(Experimenter, self).__init__()
        self._index = index
        if hasattr(self, u'_settings'):
            if self._settings is None:
                self._settings = {}
        else:
            self._settings = {}

    def run(self):
        """
        Run an experiment on a piece.

        :returns: The result of the experiment. Data is stored uniquely depending on the Experiment.
        :rtype: pandas.Series or pandas.DataFrame
        """
        pass

    def _do_multiprocessing(self, func, func_args):
        """
        Submit each of the argument lists in func_args to the function in func. In the future, this
        method may use multiprocessing.

        :param func: The function to call. The function should return a pandas.Series or DataFrame
        :type func: module-level function

        :param func_args: A nested list of the arguments to be passed to "func". Each outer list
            element will be a single call to "func".
        :type func_args: iterable of iterables of objects

        :returns: A list of whatever was returned by the "func" function.
        :rtype: list of pandas.Series or of pandas.DataFrame

        **Side Effects**

        Blocks until all calculations have completed.
        """
        post = []
        for arg_list in func_args:
            post.append(func(*arg_list))  # pylint: disable=W0142
        return post
