#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: controller.py
# Purpose: The main controller component classes for vis.
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
from multiprocessing import Pool, Process


class Controller(object):
    """
    This class handles all the functions of vis, in particular all
    multiprocessing features. Any implementation should contain one
    global instance of this class.
    
    TODO: put a nice doctest here with the usual implementation.
    """
    def __init__(self):
        super(Controller, self).__init__()
        # start serving the application, initialize views,
        # whatever.
    

class Import(Process):
    """
    The process for importing pieces.
    """
    # TODO: add in appropriate arguments and
    # make this work.
    def __init__(self):
        super(Import, self).__init__()
    

class Analyze(Process):
    """
    The process for converting a :class:`music21.stream.Score` object
    to a :class:`vis.models.AnalysisRecord` object.
    """
    # TODO: add in appropriate arguments and
    # make this work.
    def __init__(self):
        super(Analyze, self).__init__()
    
class Experiment:
    """
    Base class for all experiments done in vis. It will have properly
    defined inputs and outputs, and may manage its own multiprocessing?
    """
    def __init__(self):
        super(Experiment, self).__init__()
    
