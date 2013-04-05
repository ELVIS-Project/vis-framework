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

# Imports from...
# vis
from settings import Settings



class ExperimentSettings(Settings):
   '''
   Hold settings relevant to performing experiments.
   
   All the possible settings:
   - experiment : name of the experiment to use
   - quality : whether or not to display interval quality
   - simple_or_compound : whether to use simple or compound intervals
   - topX : display on the "top X" number of results
   - threshold : stop displaying things after this point
   - values_of_n : a list of ints that is the values of 'n' to display
   - sort_order : whether to sort things 'ascending' or 'descending'
   - sort_by : whether to sort things by 'frequency' or 'name'
   - output_format : choose the Display subclass for this experiment's results
   '''
   pass
