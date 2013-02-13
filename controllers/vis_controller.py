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
#from vis.models import analyzing
from views.main import VisQtMainWindow
from controllers.controller import Controller
from controllers.importer import Importer
from controllers.analyzer import Analyzer
from controllers.experimenter import Experimenter
from controllers.display_handler import DisplayHandler
# PyQt4
from PyQt4.QtGui import QApplication
from PyQt4 import QtCore



class VisController(Controller):
   '''
   Main GUI Controller. Although there is a dependency on QtCore, for the PyQt
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



   # Signals
   # When the GUI knows the user wants to import the files in the list
   run_the_import = QtCore.pyqtSignal()
   # When a user adds or removes a file (or some files) to or from the list
   import_files_added = QtCore.pyqtSignal(list)
   import_files_removed = QtCore.pyqtSignal(list)
   # When the GUI knows the user wants to analyze the files
   run_the_analysis = QtCore.pyqtSignal()
   # When the GUI knows the user wants to run the experiment
   run_the_experiment = QtCore.pyqtSignal()
   # When the user changes a setting on the Experimenter's GUI representation
   experiment_setting = QtCore.pyqtSignal(tuple)



   def __init__(self, arg, interface='PyQt4', details=None):
      '''
      Create a new VisController instance.

      The first argument, "interface", is a string specifying which GUI to use:
      - 'PyQt4'
      - 'HTML5' (not implemented)
      - others?

      The second argument, "details", is a list of arguments specifying settings
      to be used when creating the specific interface. So far, there are none.
      '''
      super(Controller, self).__init__() # required for signals

      # Setup things we need to know
      self.UI_type = interface
      self.app = QApplication(arg)

      # NOTE: this will change when we allow multiple interfaces
      # NOTE-2: we should do this before the sub-controllers are setup, because
      #         the GUI shouldn't touch a sub-controller, and doing things in
      #         this order means that any such attempt will fail.
      self.window = VisQtMainWindow(self)

      # Create the sub-controllers
      self.importer = Importer()
      self.analyzer = Analyzer()
      self.experimenter = Experimenter()
      self.displayer = DisplayHandler()

      # Setup the sub-controller signals
      self.importer.setup_signals()
      self.analyzer.setup_signals()
      self.experimenter.setup_signals()
      self.displayer.setup_signals()

      # Setup signals
      mapper = [
         # GUI-only Signals
         # NB: These belong in the VisQtMainWindow class, since they depend
         #     on the particular GUI being used.
         # GUI-and-Controller Signals
         # TODO: remove all of these... things touching the GUIs should be moved
         #     into the GUIs themselves, and the GUIs should use signals to
         #     communicate with the vis_controller
         # Signals Sent between Controllers/GUIs -------------------------------
         (self.importer.import_finished, self.window.show_analyze.emit),
         (self.analyzer.analysis_finished, self.window.show_experiment.emit),
         (self.analyzer.analysis_finished, self.experimenter.catch_analyses),
         # status
         (self.importer.status, self.window.update_progress.emit),
         (self.analyzer.status, self.window.update_progress.emit),
         (self.experimenter.status, self.window.update_progress.emit),
         # error
         (self.importer.error, self.window.report_error.emit),
         (self.analyzer.error, self.window.report_error.emit),
         (self.experimenter.error, self.window.report_error.emit),
         # others
         (self.import_files_added, self.importer.add_pieces_signal.emit),
         (self.import_files_removed, self.importer.remove_pieces_signal.emit),
         # Signals Sent by GUIs (and Handled Here) -----------------------------
         (self.run_the_import, self.prepare_import),
         (self.run_the_analysis, self.analyzer.run_analysis.emit),
         (self.run_the_experiment, self.experimenter.run_experiment.emit),
         (self.experiment_setting, self.experimenter.set.emit),
         #(self.run_the_import, self.processEvents), # NOTE: does nothing?
         #(self.run_the_analysis, self.processEvents), # NOTE: does nothing?
         # Signals Sent by other Controllers (and Handled Here) ----------------
         (self.importer.status, self.processEvents),
         (self.analyzer.status, self.processEvents),
         (self.experimenter.status, self.processEvents),
         # TODO: connect these signals
         # self.importer.add_remove_success
         # self.change_settings ????????
         # self.experimenter.experiment_finished
      ]
      for signal, slot in mapper:
         signal.connect(slot)

      # Set the models for the table views.
      self.window.ui.gui_file_list.setModel(self.importer._list_of_files)
      self.window.ui.gui_pieces_list.setModel(self.analyzer._list_of_pieces)



   @QtCore.pyqtSlot()
   def prepare_import(self):
      '''
      Emits the signal Importer.import_pieces with the proper argument. This is
      needed because the GUI doesn't have access to the Analyzer controller,
      and therefore can't know where the proper ListOfPieces is.
      '''
      # Signal the Importer to run the import process
      self.importer.run_import.emit(self.analyzer._list_of_pieces)



   def processEvents(self, *args):
      '''
      This method is just an interface to 'forget' the arguments of a signal
      which requires updating the GUI.
      '''
      self.app.processEvents()



   def exec_(self):
      '''
      Runs the application.
      '''
      return self.app.exec_()
# End class VisController ------------------------------------------------------
