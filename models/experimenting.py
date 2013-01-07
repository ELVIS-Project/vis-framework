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
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QComboBox, QCheckBox


# NOTE: if other Controllers require Settings like this, it
# will probably be worthwhile to put this in a separate file.
class Setting(object):
	"""
	Base class for any individual setting of a particular type,
	for any process which requires a "static" parameter.
	"""
	# A signal which is emitted if the user inputs something invalid
	invalid_value = pyqtSignal()
	
	def __init__(self, name, display_text, validator):
		"""
		Creates a Setting instance.
		
		INPUTS:
		-name: the internal `shorthand` name for the setting.
		-display_text: a detailed, user-readable description of
		what the setting does.
		-validator: a method which checks user input to ensure
		the setting has a logical value; it must accept a single
		argument and return a boolean value -- True if the value
		is valid, and False otherwise.
		"""
		self.name = name
		self.display_text = display_text
		self.validator = validator
		self.value = None
		
	def set_value(self, value):
		if self.validator(value):
			self.value = value
		else:
			self.invalid_value.emit(value)
	
	# NB: the following method is just an on-the-spot solution.
	# It may violate the MVC philosophy, but it's just easier to
	# keep track of right now.	
	def view_class(self):
		"""
		Abstract method. Subclasses must implement this method
		to return a Python class which is used to create form
		elements for this setting in views.
		"""
		pass
			
class ChoiceSetting(Setting):
	"""
	Setting which has a fixed discrete set of valid choices.
	"""
	def __init__(self, name, display_text, choices):
		"""
		Creates a ChoiceSetting instance.
		
		INPUTS:
		-choices: a list of the valid choices..
		"""
		self.choices = choices
		validate = lambda c: c in self.choices
		super(ChoiceSetting, self).__init__(name, display_text, validate)
	
	def view_class(self):
		return QComboBox

class BooleanSetting(Setting):
	"""
	Setting which can be True or False.
	"""
	def __init__(self, name, display_text):
		"""
		Creates a BooleanSetting instance.
		"""
		validate = lambda c: isinstance(c, bool)
		super(BooleanSetting, self).__init__(name, display_text, validate)
	
	def view_class(self):
		return QCheckBox