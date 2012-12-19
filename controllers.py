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
from multiprocessing import Process
from models.data import Settings
from views.Ui_new_main_window import Ui_MainWindow


class Controller(object):
    """
    Base class for all vis controllers.
    """
    def __init__(self, stylesheet):
        """
        Creates a new instance, and assigns the appropriate widget.
        """
        # view = stylesheet[self.__class__.__name__]()
        # self._view = view
        
    def setup_signals(self):
        pass

class VisController(Controller):
    """
    This class handles all the functions of vis, in particular all
    multiprocessing features. Any implementation should contain one
    global instance of this class.
    
    TODO: put a nice doctest here with the usual implementation.
    """
    def __init__(self, *args):
        """
        Creates a new VisController instance.
        
        INPUTS:
        -stylesheet: a stylesheet object containing the implementation
        details for each View class.
        """
        super(VisController, self).__init__(*args)
        self._stylesheet = stylesheet
        # sub controllers
        self.importer = Importer(stylesheet)
        self.analyzer = Analyzer(stylesheet)
        self.experimenter = Experimenter(stylesheet)
        self.display_handler = DisplayHandler(stylesheet)
    
    def run(self):
        """
        Run the application through its lifecycle.
        """
    

class Importer(Controller):
    """
    This class handles input for a user's choice of files and handles
    parsing them into PieceData instances.
    """
    def __init__(self, *args):
        """
        Creates a new Importer instance.
        """
        super(Importer, self).__init__(*args)
        self._widget.add_file.connect(self.add_file)
        self.files = []
        self.signals = [import_files, add_file, add_dir, remove_files]
    
    def import_files():
        """
        Try to import the selected files
        """

class Analyzer(Controller):
    """
    This class handles input for a user's choice of settings and voice
    pairs, then uses these settings to analyze a list of VoicePair
    objects into a list of Record objects.
    """
    def __init__(self, stylesheet, pieces):
        super(Analyzer, self).__init__(stylesheet)
        self.pieces = pieces
        self.settings = Settings()
    

class Experimenter(Controller):
    """
    This class handles input for a user's choice of Experiment and choice
    of associated Settings, then performs the experiment, returning the
    relevant Results object(s).
    """
    def __init__(self, stylesheet):
        super(Experimenter, self).__init__(stylesheet)
        self._experiment = None
    

class DisplayHandler(Controller):
    """
    This class handles input for a user's choice of Settings and takes the
    results of an Experiment, formats them according to the user's choices
    and displays them in the appropriate view.
    """
    def __init__(self, stylesheet, results):
        """
        Creates a new DisplayHandler instance
        
        INPUTS:
        results - a Results object containing data for the results of an
        Experiment
        """
        super(DisplayHandler, self).__init__()
        self._stylesheet = stylesheet
        self._results = results
    
    # def setup_signals(self):
    #   VisSignals.display_results.connect(self.display_results)
        