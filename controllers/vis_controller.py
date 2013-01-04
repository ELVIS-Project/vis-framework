#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: vis_controller.py
# Purpose: Holds the VisController objects for the various GUIs.
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
Holds the VisController objects for the various GUIs.
'''



# Imports from...
# vis
from models.analyzing import ListOfPieces
from views.Ui_main_window import Ui_MainWindow
from controllers.controller import Controller
from controllers.importer import Importer
from controllers.analyzer import Analyzer
from controllers.experimenter import Experimenter
from controllers.display_handler import DisplayHandler



class VisController(Ui_MainWindow):
   '''
   Subclasses the automatically-generated python code in Ui_main_window that
   creates the GUI. Although there is a dependency on QtCore, for the PyQt
   signals-and-slots mechanism, we must try to avoid using QtGui methods as
   much as possible, so that, in the future, we can use other GUIs without
   importing Ui_main_window from the PyQt GUI.

   This class creates the GUI and manages interaction between other Controller
   subclasses and the GUI. It is effectively both the GUI's controller and the
   super-controller for Importer, Analyzer, Experimenter, and DisplayHandler,
   since VisController also "translates" GUI actions into the signals expected
   by the other controller subclasses.

   TODO: doctest
   '''
   # NOTE: We will have to rewrite most of this class when we want to implement
   # other (non-PyQt4) interfaces, but the use patterns, and maybe even the
   # algorithms, should stay mostly the same.

   # NOTE2: We may need other methods for other interfaces, but for PyQt4, we
   # only need __init__().



   def __init__(self, interface='PyQt4', details=None):
      '''
      Create a new VisController instance.

      The first argument, "interface", is a string specifying which GUI to use:
      - 'PyQt4'
      - 'HTML5' (not implemented)
      - others?

      The second argument, "details", is a list of arguments specifying settings
      to be used when creating the specific interface. So far, there are none.
      '''
      # Setup things we need to know
      self.UI_type = interface

      # Setup signals for GUI-only things

      # Create long-term sub-controllers
      # self.importer = ?
      # self.analyzer = ?
      # self.experimenter = ?
      # self.displayer = ?

      # Setup signals TO the long-term sub-controllers
      # self.importer.setup_signals()
      # self.analyzer.setup_signals()
      # self.experimenter.setup_signals()
      # self.displayer.setup_signals()

      # Setup signals for GUI-only things.

      # Create long-term sub-controllers
      self.importer = Importer()
      self.analyzer = Analyzer()
      self.experimenter = Experimenter()
      self.displayer = DisplayHandler()

      # Setup signals TO the long-term sub-controllers
      self.importer.setup_signals()
      self.analyzer.setup_signals()
      self.experimenter.setup_signals()
      self.displayer.setup_signals()

      # Setup signals FROM the long-term sub-controllers

      # Set the models for the table views.
      #self.gui_file_list.setModel(self.importer.list_of_files)
      #self.gui_pieces_list.setModel(self.analyzer.list_of_pieces)
# End class VisController ------------------------------------------------------
