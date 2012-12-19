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
    

class Setting(object):
    """
    Base class for a particular setting of a particular type,
    for any process which requires a static setting
    """
    def __init__(self, name, display_text, validator):
        """
        Creates a Setting instance.
        
        INPUTS:
        -name: the internal `shorthand` name for the setting
        -display_text: a detailed, user-readable description
        of what the setting does.
        -validator: a method which checks user input to ensure
        the setting has a logical value.
        """
        self.name = name
        self.display_text = display_text
        self.validate = validate
        self.value = None
        
    def set_value(self, value):
        if self.validate(value):
            self.value = value
        
class PositiveIntSetting(Setting):
    """
    A setting which must be a positive integer, like
    for the "n" value in an NGram query.
    """
    def __init__(self, name, display_text):
        def v(self, value):
            if not isinstance(value, int):
                return False
            if value <= 0:
                return False
            return True
        super(PositiveIntSetting, self).__init__(name, display_text, v)
