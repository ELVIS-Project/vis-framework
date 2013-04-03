#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: settings.py
# Purpose: The model classes for Setting objects.
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
'''
This module contains the model classes for Setting objects, used in VIS by
the Analyzer and Experimenter controllers.
'''


#Imports from...
#PyQt4
from PyQt4.QtCore import pyqtSignal, QObject
#vis
from problems.coreproblems import SettingValidationError



class Setting(object, QObject):
   '''
   Base class for all Settings to be used by the Analyzer & Experimenter
   controllers.
   '''
   # emitted when a user changes the value contained in this Setting.
   value_changed = pyqtSignal()
   # emitted when the relevant view widget for this Setting must be created.
   initialize = pyqtSignal()
   
   def __init__(self, value=None, **kwargs):
      '''
      Creates a new Setting instance with the value `value`.
      
      Other relevant information that can be passed via the keyword arguments:
      `display_name` - a string containing a short description of this field to
      display in a view.
      '''
      self._value = value
      self._display_name = kwargs.get('display_name')
   
   @property
   def display_name(self):
      '''
      Wrapper for private variable _display_name.
      '''
      return self._display_name
   
   @property
   def value(self):
      '''
      Wrapper for private variable _value.
      '''
      return self._value
   
   @value.setter
   def value(self, value):
      '''
      Wrapper for private variable _value.
      '''
      value = self.validate(value)
      self._value = value
   
   def clean(self, value):
      '''
      Modify or reformat the data being passed into the setting so that it
      is suitable for internal use by the application. This method can be
      overridden in subclasses. The default implementation is simply to
      return the value passed in.
      '''
      return value
   
   def validate(self, value):
      '''
      Check to see if the value is valid for its uses, and return a valid
      value for the setting. Otherwise, raise a SettingValidationError.
      Overriding this method in subclasses is encouraged; default
      implementation is to simply return `self.clean(value)`.
      '''
      return self.clean(value)



class PositiveIntSetting(Setting):
   '''
   class docstring
   '''
   pass