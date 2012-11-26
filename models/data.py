#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: data.py
# Purpose: The model classes for "data-only" types (those with no business 
#          logic.)
#
# Copyright (C) 2012 Jamie Klassen, Christopher Antila
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
from inspect import getargspec
from problems.coreproblems import NonsensicalInputError


class VisFile(str):
    """
    Simple subclass of str for filenames whose file formats which vis
    can handle.
    """
    def __init__(self, arg):
        super(VisFile, self).__init__()
    

class PieceData(object):
    """
    Contains metadata for a VisFile; title, filename and a list of VoicePair
    objects.
    """
    def __init__(self):
        super(PieceData, self).__init__()
    

class VoicePair(object):
    """
    Contains data for a pair of voices; the piece the come from, and their names.
    """
    def __init__(self):
        super(VoicePair, self).__init__()
    

class Record(object):
    """
    Compact version of piece data; a list of simultaneities.
    """
    def __init__(self):
        super(Record, self).__init__()
    

class Settings(object):
    """
    Base class for the various 'application settings' classes in vis.
    Basically just an interface to a python dict with "typesafe" entries.
    """
    def __init__(self, *args):
        """
        Creates a new Settings instance.
        
        INPUTS:
        Either a list of strings, one for each of the variable names
        held by this Settings instance, or else each string as a 
        separate argument.
        """
        super(Settings, self).__init__()
        # has a list been passed?
        if 1 == len(args) and isinstance(args[0], list):
            # yes, so read it in
            self._data = {entry:None for entry in args[0]}
        else:
            # no, so read the entries individually
            self._data = {entry:None for entry in args}

