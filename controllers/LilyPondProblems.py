#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Filename: LilyPondProblems.py
# Purpose: Exceptions and Errors for output_LilyPond
#
# Copyright (C) 2012 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
The LilyPondProblems module contains error and warning classes for the
output_LilyPond program.
"""


class BadFileError(Exception):
    """
    output_LilyPond uses this error when there is a problem loading or handling
    a file, not related to a more specific musical element.
    """
    pass

class UnidentifiedObjectError(Exception):
    """
    When something can't be identified.
    """
    pass

class ImpossibleToProcessError(Exception):
    """
    When something is identified, but for some reason cannot be processed.
    """
    pass
