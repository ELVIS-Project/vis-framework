#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: experimenting.py
# Purpose: The model classes for the Experimenter controller.
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
The model classes for the Experimenter controller.
'''



class ExperimentSettings(object):
   '''
   Hold settings relevant to performing experiments.

   All the possible settings:
   - experiment : name of the experiment to use
   - quality : whether or not to display interval quality
   - simple or compound : whether to use simple or compound intervals
   - topX : display on the "top X" number of results
   - threshold : stop displaying things after this point
   - values of n : a list of ints that is the values of 'n' to display
   - sort order : whether to sort things 'ascending' or 'descending'
   - sort by : whether to sort things by 'frequency' or 'name'
   - output format : choose the Display subclass for this experiment's results
   '''



   def __init__(self):
      '''
      Create an empty ExperimentSettings instance with no settings.
      '''
      self._settings = {}



   def set(self, setting, value):
      '''
      Set the value of a setting. If the setting does not yet exist, it is
      created and initialized to the value.
      '''
      self._settings[setting] = value



   def has(self, setting):
      '''
      Returns True if a setting already exists in this ExperimentSettings
      instance, or else False.
      '''
      return setting in self._settings



   def get(self, setting):
      '''
      Return the value of a setting, or None if the setting does not exist.
      '''
      if self.has(setting):
         return self._settings[setting]
      else:
         return None
