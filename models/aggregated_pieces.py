#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/aggregated_pieces.py
# Purpose:                Hold the model representing data from multiple IndexedPieces.
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
The model representing data from multiple IndexedPieces.
"""


class AggregatedPieces(object):
    """
    Holds data from multiple IndexedPieces.
    """

    # About the Data Model (for self._data)
    # =====================================
    # - ?

    # TODO: how to know which pieces are stored here?

    def __init__(self, pathname, **args):
        super(AggregatedPieces, self).__init__(args)

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

    def experimenters_used(self):
        """
        Return a list of the names of the experimenters used so far in this AggregatedPieces.
        """
        pass

    def add_experiment(self, which_experiment, which_settings=None):
        """
        ?
        """
        if not which_settings:
            which_settings = {}
        pass

    def remove_experiment(self, **args):
        """
        ?
        """
        pass
