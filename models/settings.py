#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:               vis
# Program Description:        Measures sequences of vertical intervals.
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
# along with this program.   If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
'''
This module contains the model classes for Setting objects, used in vis by
the Analyzer and Experimenter controllers.
'''
# Imports from...
# Python
from numbers import Number
# PyQt4
from PyQt4.QtCore import pyqtSignal, QObject
# vis
from problems.coreproblems import SettingValidationError, MissingInformationError


class Setting(QObject):
    '''
    Base class for all Settings to be used by the Analyzer & Experimenter
    controllers.
    '''
    # emitted when a user changes the value contained in this Setting.
    value_changed = pyqtSignal()
    # # emitted when the relevant view widget for this Setting must be created.
    # initialize = pyqtSignal()
    
    def __init__(self, value=None, **kwargs):
        '''
        Creates a new Setting instance with the value `value`.
        
        Other relevant information that can be passed via the keyword arguments:
        `display_name` - a string containing a short description of this field to
        display in a view.
        '''
        super(Setting, self).__init__()
        self._value = value
        self._display_name = kwargs.get('display_name', '')
        self._extra_detail = kwargs.get('extra_detail', '')
    
    @property
    def display_name(self):
        '''
        Wrapper for private variable _display_name.
        '''
        return self._display_name
    
    @property
    def extra_detail(self):
        '''
        Wrapper for private variable _extra_detail
        '''
        return self._extra_detail
    
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
        if self._value != value:
            self._value = value
            self.value_changed.emit()
    
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


class Settings(QObject):
    '''
    Wrapper for a dictionary of Setting objects.
    '''
    def __init__(self, settings=None):
        '''
        Create a new Settings instance, optionally with the argument
        `settings`, a dict with (string, Setting) items.
        '''
        self.keys = []
        if settings:
            self.keys = settings.keys()
            self.__dict__.update(settings)
    
    def __iter__(self):
        '''
        Syntactic sugar for the values of the internal dictionary.
        '''
        for k in self.keys:
            yield getattr(self, k)
    
    def has(self, setting):
        '''
        Returns True if a setting already exists in this AnalysisSettings
        instance, or else False.
        '''
        return hasattr(self, setting)
    
    def __getattr__(self, setting):
        '''
        Return the value of a setting. If it does not exist, create it and
        populate it with value None first.
        '''
        if not self.has(setting):
            setattr(self, setting, Setting(None))
        return self.__getattribute__(setting)
    
    def __deepcopy__(self, memo):
        """
        Creates a deep copy of this Settings object.
        """
        from copy import deepcopy
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


class PositiveNumberSetting(type):
    '''
    Metaclass to add a check for your numeric Setting to be positive.
    '''
    def __new__(meta, cls):
        dct = dict(cls.__dict__)
        bases = (cls,)
        name = "Positive" + cls.__name__
        # NB: this is not safe; assumes the class 
        # you pass in has a method called `clean`.
        pre_clean = dct['clean']
        def clean(self, value):
            value = pre_clean(self, value)
            if isinstance(value, Number):
                if value <= 0:
                    msg = "Value must be positive"
                    raise SettingValidationError(msg)
                return value
            else:
                msg = "Value must be a number"
                raise SettingValidationError(msg)
        dct['clean'] = clean
        return type(name, bases, dct)


class FloatSetting(Setting):
    '''
    Setting to hold a floating-point number.
    '''
    def clean(self, value):
        __doc__ = Setting.clean.__doc__
        try:
            return float(value)
        except ValueError: # could not convert string to float
            msg = "Value must be a valid decimal number"
            raise SettingValidationError(msg)


class StringSetting(Setting):
    '''
    Setting to hold a string.
    '''
    def clean(self, value):
        __doc__ = Setting.clean.__doc__
        try:
            return str(value)
        except Exception:
            msg = "Value could not be cast to string"
            raise SettingValidationError(msg)


class BooleanSetting(Setting):
    '''
    Setting to hold a boolean (True or False) value.
    '''
    def clean(self, value):
        __doc__ = Setting.clean.__doc__
        return bool(value)


class MultiChoiceSetting(Setting):
    '''
    A setting with multiple values taken from a fixed set of options. Normally
    modified with a multiple-select widget of some kind.
    '''
    def __init__(self, *args, **kwargs):
        '''
        Creates a new MultiChoiceSetting instance. The keyword argument `choices`
        is required, and must be an iterable of 2-tuples (value, label) where value
        is any Python type and label is a string to be used as the label of the option
        in the view widget for this Setting.
        
        Example:
        >>> mcs = MultiChoiceSetting(choices=[(0, 'Option A'),
        (1, 'Option B'), 
        (2, 'Option C')])
        '''
        super(MultiChoiceSetting, self).__init__(*args, **kwargs)
        if not 'choices' in kwargs:
            msg = "Missing required keyword argument 'choices'"
            raise MissingInformationError(msg)
        choices = kwargs.pop('choices')
        try:
            for i, val in choices:
                if not isinstance(val, basestring):
                    s = "value '{0}' in kwarg 'choices' of incorrect type '{1}'"
                    msg = s.format(val, type(val))
                    raise SettingValidationError(msg)
                    break
        except ValueError: # too many values to unpack
            msg = "kwarg 'choices' must be an iterable of 2-tuples"
            raise SettingValidationError(msg)
        self.choices = choices
        self._value = []
        settings = [(val, name, BooleanSetting(False,display_name=name))
                        for val, name in choices]
        for val, name, setting in settings:
            def value_changed():
                if setting.value:
                    if not val in self.value:
                        self.value.append(val)
                else:
                    if val in self.value:
                        self.value.remove(val)
            setting.value_changed.connect(value_changed)
        self.settings = Settings({name: setting for val, name, setting in settings})
        super(MultiChoiceSetting, self).__init__(*args, **kwargs)
