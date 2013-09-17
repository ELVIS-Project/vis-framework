#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/experimenters/template.py
# Purpose:                Template experimenter
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
Template experimenter.
"""

from vis.analyzers import experimenter


# pylint: disable=W0613
def experimenter_func(obj):
    """
    docstring
    """
    return None


class TemplateExperimenter(experimenter.Experimenter):
    """
    Template for a class to perform an experiment on a music21 stream. Experiments return results
    that do not make sense to think of as happening at particular times in the piece.

    Use this class when you want to write a new Experimenter subclass.
    """

    required_indices = []
    required_experiments = []
    possible_settings = []  # list of strings
    default_settings = {}  # keys are strings, values are anything

    def __init__(self, index, settings=None):
        """
        Create a new Experimenter.

        Parameters
        ==========
        :param index: lists or nested lists of pandas.Series or pandas.DataFrame objects.
            A list (or list of lists) of Series. The minimum and maximum numbers, and whether to use
            embedded lists, depends on the Experimenter subclass.
        :type index: list of pandas.Series or pandas.DataFrame

        :param settings: A dict of all the settings required by this Experimenter. All required
            settings should be listed in subclasses. Default is None.
        :type settings: dict or None

        Raises
        ======
        :raises: RuntimeError, if required settings are not present in the ``settings`` argument.
        """

        # Check all required settings are present in the "settings" argument. You must ignore
        # extra settings.
        # If there are no settings, you may safely remove this.
        if settings is None:
            self._settings = {}

        # Change "TemplateExperimenter" to the current class name. The superclass will handle the
        # "index" and "mpc" arguments, but you should have processed "settings" above, so it should
        # not be sent to the superclass constructor.
        super(TemplateExperimenter, self).__init__(index, None)

    def run(self):
        """
        Run an experiment on a piece.

        Returns
        =======
        :returns: The result of the experiment. Data is stored uniquely depending on the Experiment.
        :rtype: pandas.Series or pandas.DataFrame
        """

        # NOTE: We recommend experimenting all possible combinations of anything, when feasible.

        # You will need to write this yourself; we recommend you use self._do_multiprocessing()
        # as an easy way to use the MPController for multiprocessing.
        pass
