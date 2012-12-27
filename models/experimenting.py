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



class Experiment(object):
    """
    Base class for all Experiments done in vis.
    """
    def __init__(self, records):
        """
        INPUTS:
        -records: a list of Record objects; this is the data
        which will be experimented with.
        """
        super(Experiment, self).__init__()
        self._settings = None
        self._records = records

    def run():
        """
        This method must be implemented in subclasses to be
        where the main busines logic/processing for the
        experiment is done.
        """
        missing = [s for s in self._settings if s.value is None]
        if missing:
            raise Exception("settings " + str(missing) + " are missing")


class NGramHistogram(Experiment):
    """
    Prepares a summary of all the NGrams in all the samples
    which have been analyzed.
    """
    def __init__(self, arg):
        super(NGramHistogram, self).__init__()
        self._settings = [PositiveIntSetting('n','Length of NGram'),
                          PositiveIntSetting('thresh', 'Exclude NGrams with fewer occurences than'),
                          PositiveIntSetting('topX', 'Include these many different NGrams with the highest frequencies')]

    def run(self):
        """
        Finds all the N-Grams and prepares them into a histogram.
        """
        super(NGramHistogram, self).run()
