#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: settings.py
# Purpose: The model classes for Setting and Settings objects.
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
"""
Model classes for Setting and Settings objects.
"""


# Imports from...
# Python
from numbers import Number
import copy
# PyQt4
from PyQt4.QtCore import pyqtSignal, QObject
# vis
from problems.coreproblems import SettingValidationError, MissingInformationError


class Setting(QObject):
    """
    Base class for all Settings to be used by the Analyzer & Experimenter
    controllers.

    PyQt4 Signals
    -------------
    .. py:attribute:: value_changed
        Emitted when the value of a Setting is changed through its setter method.
    """

    value_changed = pyqtSignal(object)
    display_name_changed = pyqtSignal(str)

    def __init__(self, value=None, **kwargs):
        """
        Make a new Setting instance.

        Parameters
        ----------
        All parameters are optional; default values are specified below.

        value : any type or class
            The value of a the Setting. Default is None.

        display_name : string
            The textual representation of this Setting in a GUI. Default is ''

        extra_detail : string
            Additional information about this Setting, such as that used by a tooltip. Deafult is ''
        """
        super(Setting, self).__init__()
        self._value = value
        self._display_name = kwargs.get('display_name', '')
        self._extra_detail = kwargs.get('extra_detail', '')

    @property
    def display_name(self):
        """
        Get the display name of this Setting.

        Returns
        -------

        s : string
            The preferred textual representaiton of this Setting in a GUI.
        """
        return self._display_name

    @display_name.setter
    def display_name(self, name):
        """
        Set the display name of this Setting.

        Returns
        -------

        i : zero
            Returns 0 to indicate the method has finished successfully.

        Emits
        -----

        :py:const:`Setting.display_name_changed` : If the name provided is
            different from the one previously stored in this Setting.
        """
        if self._display_name != name:
            self._display_name = name
            self.display_name_changed.emit(name)
        return 0

    @property
    def extra_detail(self):
        """
        Get additional information about this Setting, such as for use in a tooltip.

        Returns
        -------

        s : string
            Additional information about this Setting.
        """
        return self._extra_detail

    @property
    def value(self):
        """
        Get the value of this Setting.

        Returns
        -------

        v : any type
            Whatever "value" was provided to the constructor, or the value() setter method.
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set the value of this Setting.

        Parameters
        ----------

        value : any type
            The value to which the Setting should be changed.

        Returns
        -------

        i : zero
            Returns 0 to indicate the method has finished successfully.

        Emits
        -----

        :py:const:`Setting.value_changed` : If the value provided is different from the one
            previously stored in this Setting.

        Side Effects
        ------------

        Uses the :py:method:`Setting.validate` method to validate that the input is valid for the
        type of Setting.
        """
        value = self.validate(value)
        if self._value != value:
            self._value = value
            self.value_changed.emit(value)
        return 0

    def clean(self, value):
        """
        Modify or reformat a 'value' to be suitable for this Setting. Values given to this method
        should be known to be valid, though potentially improperly formatted.

        This method should be overridden in subclasses, since the default implementation simply
        returns the original value.

        Parameters
        ----------

        value : any type
            The object to be reformatted.

        Returns
        -------

        value : any type
            The unmodified parameter.
        """
        return value

    def validate(self, value):
        """
        Verify that a value is valid for this Setting, then format it correctly if so.

        This method should be overridden in subclasses, since the default implementation simply
        returns the original value.

        Parameters
        ----------

        value : any type
            The object to be verified and formatted.

        Returns
        -------

        value : any type
            The unmodified parameter.

        Side Effects
        ------------

        Uses :py:method:`Setting.clean` to properly format a valid value.

        Raises
        ------

        SettingValidationError :
            If the inputted value could not be properly validated and formatted.
        """
        return self.clean(value)
# End class Setting --------------------------------------------------------------------------------


class Settings(QObject):
    """
    Holds :py:class:`Setting` objects. This class is a wrapper for a dict.
    """

    def __init__(self, settings=None):
        """
        Create a new Settings object.

        Parameters
        ----------

        settings : dict
            The dict to use as the settings database.
        """
        super(Settings, self).__init__()
        self.keys = []
        if settings:
            self.keys = settings.keys()
            self.__dict__.update(settings)

    def __iter__(self):
        """
        Iterate the values of all settings.

        Returns
        -------

        All the values are returned, one at a time, in arbitrary order (the order they are stored
        in the internal dictionary).
        """
        for each_key in self.keys:
            yield getattr(self, each_key)

    def has(self, which_setting):
        """
        Know whether a Setting has a value in this Settings object.

        Parameters
        ----------

        which_setting : string
            The name of the Setting for which to check.

        Returns
        -------

        b : boolean
            Whether the Setting has been set in this Settings instance.
        """
        return hasattr(self, which_setting)

    def __deepcopy__(self, memo):
        """
        Used by copy.deepcopy() to make a deep copy of this Settings object.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for key, val in self.__dict__.items():
            setattr(result, key, copy.deepcopy(val, memo))
        return result
# End class Settings -------------------------------------------------------------------------------


class PositiveNumberSetting(type):
    """
    Metaclass to add a check for your numeric Setting to be positive.
    """

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
    """
    Hold a floating point number (i.e., one with a decimal).
    """
    def validate(self, value):
        """
        Verify that the value is or can be turned into a floating point number, then format it
        correctly if so.

        Parameters
        ----------

        value : string or number
            A string or number that should not raise an exception when run through float()

        Returns
        -------

        value : float
            The result of float(), run on the 'value' parameter.

        Raises
        ------

        SettingValidationError :
            If the inputted value could not be properly converted to a floating point number.


        Note: This method does not call clean(), as the default verify() implementation.
        """
        try:
            return float(value)
        except ValueError: # could not convert string to float
            msg = 'Value must produce a decimal number.'
            raise SettingValidationError(msg)


class StringSetting(Setting):
    """
    Hold a string.
    """
    def verify(self, value):
        """
        Verify that the value is or can be turned into a string, then format it correctly if so.

        Parameters
        ----------

        value : string or object
            A string or object that should not raise an exception when run through str()

        Returns
        -------

        value : string
            The result of str(), run on the 'value' parameter.

        Raises
        ------

        SettingValidationError :
            If the inputted value could not be properly converted to a string.


        Note: This method does not call clean(), as the default verify() implementation.
        """
        try:
            return str(value)
        except Exception:
            msg = 'Value must produce a string.'
            raise SettingValidationError(msg)


class BooleanSetting(Setting):
    """
    Hold a boolean value (True or False).
    """
    def clean(self, value):
        """
        Modify or reformat a 'value' to be a boolean value.

        Parameters
        ----------

        value : any type
            The object to be turned into a boolean.

        Returns
        -------

        value : boolean
            Either True or False.
        """
        return bool(value)


class MultiChoiceSetting(Setting):
    """
    Hold some :py:class:`BooleanSetting` objects. This would be represented on an interface with,
    for example, a set of checkboxes.

    For a set of boolean settings where only one may be selected at a time, as in a set of radio
    buttons, use :py:class:`SingleChoiceSetting`.
    """

    def __init__(self, *args, **kwargs):
        """
        Make a new MultiChoiceSetting.

        Parameters
        ----------

        value : list of any types
            The default value for which choices are selected.

        choices : iterable of 2-tuples
            Required keyword parameter. This should be a list of 2-tuples, where the first element
            is a string that corresponds to the name for a setting, and the second element is its
            value, which should be boolean.

        display_name : string
            The textual representation of the group of setting in a GUI. Default is ''

        extra_detail : string
            Additional information about the group of settings, such as that used by a tooltip.
            Deafult is ''

        Side Effects
        ------------

        Creates a Settings object with a set of BooleanSetting objects.
        """

        """
        Creates a new MultiChoiceSetting instance. The keyword argument `choices`
        is required, and must be an iterable of 2-tuples (value, label) where value
        is any Python type and label is a string to be used as the label of the option
        in the view widget for this Setting.

        Example:
        >>> mcs = MultiChoiceSetting(choices=[(0, 'Option A'),
        (1, 'Option B'),
        (2, 'Option C')])
        """
        super(MultiChoiceSetting, self).__init__(*args, **kwargs)

        # make sure we have the proper 'choices' keyword argument
        if not 'choices' in kwargs:
            msg = 'Missing required keyword argument: choices'
            raise MissingInformationError(msg)
        else:
            choices = kwargs.pop('choices')

        # validate-then-clean


        self.choices = choices
        self._value = []

        # We probably won't need this line
        settings = [(val, name, BooleanSetting(False,display_name=name))
                    for val, name in choices]

        # we'll probably still need this part
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





    def clean(self, value):
        """
        Modify or reformat a 'value' to be suitable for this Setting. Values given to this method
        should be known to be valid, though potentially improperly formatted.

        This method should be overridden in subclasses, since the default implementation simply
        returns the original value.

        Parameters
        ----------

        value : any type
            The object to be reformatted.

        Returns
        -------

        value : any type
            The unmodified parameter.
        """
        return value

    def validate(self, value):
        """
        Verify that 'value' is an iterable of 2-tuples, the first element of which can be a string and
        the second of which can be a boolean.

        Parameters
        ----------

        value : an iterable of 2-tuples

        Returns
        -------

        value : an iterable of 2-tuples
            With a guarantee that the first element in each is a string and the second is a boolean.

        Side Effects
        ------------

        Uses :py:method:`Setting.clean` to properly format each 2-tuple.

        Raises
        ------

        SettingValidationError :
            If the inputted value could not be properly formatted.
        """
        post = []
        try:
            for bool_sett in value:
                if 2 == len(bool_sett):
                    post.append(self.clean(bool_sett))
                else:
                    msg = 'An element in the iterable has too many elements.'
                    raise SettingValidationError(msg)
        except TypeError:
            msg = 'An element in the iterable has too many elements.'
            raise SettingValidationError(msg)

        return post
# End class MultiChoiceSetting ---------------------------------------------------------------------


class SingleChoiceSetting(Setting):
    """
    Hold some :py:class:`BooleanSetting` objects, only one of which may be True at a time. This
    would be represented on an interface with, for example, a set of radio buttons.

    For a set of boolean settings where many may be selected at a time, as in a set of checkboxes,
    use :py:class:`MultiChoiceSetting`.
    """
    pass
