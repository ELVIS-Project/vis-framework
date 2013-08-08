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
This module outlines the Experimenter base class.
"""


def _mp_wrapper(pipe_i, func, **args):
    """
    So subclass authors don't need to worry about the extra first parameter required by the
    MPController, we wrap their function in this function.
    """
    return pipe_i, func(args)


class Experimenter(object):
    """
    Run an experiment on an IndexedPiece.

    Use the "Experimenter.required_indices" attribute to know which Indexer subclasses should be
    provided to this Experimenter's constructor. If the list is None or [], use the
    "Experimenter.required_experiments" attribute to know which Experimenter should be provided
    to the constructor.
    """

    # just the standard instance variables
    required_indices = []
    required_experiments = []
    possible_settings = []
    default_settings = None
    # self._index

    # pylint: disable=W0613
    def __init__(self, index, settings=None, mpc=None):
        """
        Create a new Experimenter.

        Parameters
        ==========
        :param index: lists or nested lists of pandas.Series or pandas.DataFrame objects.
            A list (or list of lists) of Series. The minimum and maximum numbers, and whether to use
            embedded lists, depends on the Experimenter subclass.

        :param settings: dict
            A dict of all the settings required by this Experimenter. All required settings should
            be listed in subclasses. Default is {}.

        :param mpc: MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        RuntimeError :
            - If required settings are not present in the "settings" argument.
        """

        # Call our superclass constructor, then set instance variables
        super(Experimenter, self).__init__()
        self._index = index
        self._mpc = mpc
        if hasattr(self, u'_settings'):
            if self._settings is None:
                self._settings = {}
        else:
            self._settings = {}

    def run(self):
        """
        Run an experiment on a piece.

        Returns
        =======
        pandas.Series or pandas.DataFrame :
            The result of the experiment. Data is stored uniquely depending on the Experiment.
        """
        pass

    def _do_multiprocessing(self, func, func_args):
        """
        Dispatch jobs for completion, either through the MPController for multiprocessing (if one
        is present in this Experimenter) or serially (if no MPController is available). Await and
        return the results.

        Parameters
        ==========
        :param func: module-level function
            The function to call. The function should return a pandas.Series or DataFrame

        :param func_args: [[?]]
            A nested list of the arguments to be passed to "func". Each outer list element will be
            a single call to "func".

        Returns
        =======
        [pandas.Series] or [pandas.DataFrame]
            A list of whatever was returned by the "func" function.

        Side Effects
        ============
        1.) Blocks until all calculations have completed.
        """

        post = []

        if self._mpc is None:
            # use serial processing
            for arg_list in func_args:
                # pylint: disable=W0142
                post.append(func(*arg_list))
        else:
            # use the MPController for multiprocessing
            pipe_end = self._mpc.get_pipe()
            jobs_submitted = 0
            for arg_list in func_args:
                jobs_submitted += 1
                these_args = [func]
                these_args.extend(func_args)
                pipe_end.send((_mp_wrapper, these_args))
            for _ in xrange(jobs_submitted):
                post.append(pipe_end.recv())

        return post
