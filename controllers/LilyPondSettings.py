#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         LilyPondSettings.py
# Purpose:     Manages the runtime settings for OutputLilyPond
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
The LilyPondSettings module manages runtime settings for the OutputLilyPond
module.
"""

# Python
from subprocess import Popen, PIPE  # for running bash things
from platform import system as which_os


class LilyPondSettings:
    """
    Holds the settings relevant to output formatting of a LilyPond file.

    List of Settings:
    - bar_numbers : print bar numbers on 'every' bar, the start of every 'system'
        or 'never'
    - tagline : either 'default' ("Music engraving my LilyPond...") or a str
        that is what you want the tagline to be.
    - indent : either 'default' or a str that is the indentation you want (like
        "0\cm" for example)
    - print_instrument_names : True or False whether to print instrument names
    - lilypond_version : a str that contains the LilyPond version (default is
        auto-detection of whatever's installed)
    - lilypond_path : a str that is the full path to the LilyPond executable
    """

    def __init__(self):
        """
        Create a new LilyPondSettings instance.
        """
        # TODO: re-implmement all of the properties as str in _secret_settings
        # Hold a list of the part names in this Score
        self._parts_in_this_score = []
        # Hold a list of the parts that should be written with the
        # VisAnnotation context.
        self._analysis_notation_parts = []
        # Hold the other settings for this Score
        self._secret_settings = {}
        # Establish default values for settings in this Score
        # TODO: test this; it's in the "Part" section of process_stream()
        self._secret_settings['bar numbers'] = None
        self._secret_settings['tagline'] = ''
            # empty string means "default tagline"
            # None means "no tagline"
        self._secret_settings['indent'] = None  # TODO: test this
        self._secret_settings['print_instrument_names'] = True  # TODO: implement
        self._secret_settings['paper_size'] = 'letter'
        # Deal with the LilyPond path and version
        res = LilyPondSettings.detect_lilypond()
        self._secret_settings['lilypond_path'] = res[0]
        self._secret_settings['lilypond_version'] = res[1]
        self._secret_settings['lilypond_version_numbers'] = \
            LilyPondSettings.make_lily_version_numbers(res[1])

    def set_property(self, setting_name, setting_value):
        """
        Modify the value of an existing setting.

        >>> from output_LilyPond import *
        >>> the_settings = LilyPond_Settings()
        >>> the_settings.set_property('indent', '4\mm')
        >>> the_settings.get_property('indent')
        '4\mm'
        """
        # If the setting doesn't already exist, this will trigger a KeyError
        self._secret_settings[setting_name]

        # And if we're still going, it means we can set this setting
        self._secret_settings[setting_name] = setting_value

    def get_property(self, setting_name):
        """
        Returns the value assigned to a property. If the inputted string does not
        correspond to an existing property name, this method raises a KeyError.
        """
        return self._secret_settings[setting_name]

    @staticmethod
    def detect_lilypond():
        """
        Determine the path to LilyPond and its version.

        Returns a 2-tuple with two str objects:
        - the full path of the LilyPond executable
        - the version reported by that executable
        """

        # NB: On Windows, use registry key to find path...
        # HKLM/SOFTWARE/Wow6432Node/LilyPond/Install_Dir
        # and again different on 32-bit, probably
        # HKLM/SOFTWARE/LilyPond/Install_Dir

        if 'Windows' == which_os():
            # NOTE: this is just a temporary hack that allows vis to load on Windows
            # computers, but likely without enabling LilyPond supprt
            return ('lilypond.exe', '2.0.0')
        else:
            # On Linux/OS X/Unix systems, we'll assume a "bash" shell and hope it goes
            proc = Popen(['which', 'lilypond'], stdout=PIPE)
            lily_path = proc.stdout.read()[:-1]  # remove terminating newline
            proc = Popen([lily_path, '--version'], stdout=PIPE)
            version = proc.stdout.read()
            lily_verzh = version[version.find('LilyPond') + 9: version.find('\n')]

            return (lily_path, lily_verzh)

    @staticmethod
    def make_lily_version_numbers(version_str):
        """
        Take a str with three integers separated by the '.' character and returns
        a 3-tuplet with the integers.
        """
        major = int(version_str[:version_str.find('.')])
        version_str = version_str[version_str.find('.') + 1:]
        minor = int(version_str[:version_str.find('.')])
        version_str = version_str[version_str.find('.') + 1:]
        revision = int(version_str)

        return (major, minor, revision)
