#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/experimenters/__init__.py
# Purpose:                Init file.
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
The controllers that deal with experimenting on indices or the results of other experiments.
Whereas an Indexer produces information that can be attached to a particular moment of a score,
an Experimenter produces information that can't sensibly be described as starting at the beginning
and going to the end of a piece.
"""

__all__ = ['frequency', 'aggregator']

from vis.analyzers.experimenters import frequency
from vis.analyzers.experimenters import aggregator
