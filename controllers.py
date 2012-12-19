#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: controllers.py
# Purpose: The controller component classes for vis.
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
from models.data import Settings
from views.Ui_new_main_window import Ui_MainWindow


class VisController(object):
    """
    This class handles all the functions of vis, in particular all
    multiprocessing features. Any implementation should contain one
    global instance of this class.
    
    TODO: put a nice doctest here with the usual implementation.
    """
    def __init__(self):
        super(VisController, self).__init__()
        self.window = Ui_MainWindow()
		# sub controllers
		self.importer = Importer()
		self.analyzer = Analyzer()
		self.experimenter = Experimenter()
		self.display_handler = DisplayHandler()
    
    def run(self):
        """
        Run the application through its lifecycle.
        """
    

class Importer(object):
    """
    This class handles input for a user's choice of files and handles
    parsing them into PieceData instances.
    """
    def __init__(self):
        super(Importer, self).__init__()
    

class Analyzer(object):
    """
    This class handles input for a user's choice of settings and voice
    pairs, then uses these settings to analyze a list of VoicePair
    objects into a list of Record objects.
    """
    def __init__(self, pieces):
        super(Analyzer, self).__init__()
        self.pieces = pieces
        self.settings = Settings()
    

class Experimenter(object):
    """
    This class handles input for a user's choice of Experiment and choice
    of associated Settings, then performs the experiment, returning the
    relevant Results object(s).
    """
    def __init__(self):
        super(Experimenter, self).__init__()
    

class DisplayHandler(object):
    """
    This class handles input for a user's choice of Settings and takes the
    results of an Experiment, formats them according to the user's choices
    and displays them in the appropriate view.
    """
    def __init__(self, results):
        super(DisplayHandler, self).__init__()
        self.results = results
        