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
   run_the_import = QtCore.pyqtSignal()



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
      self.window = VisQtMainWindow(self)

      # Create long-term sub-controllers
      self.importer = Importer()
      self.analyzer = Analyzer()
      self.experimenter = Experimenter()
      self.displayer = DisplayHandler()

      # Setup signals
      #window = self.window
      #ui = window.ui
      mapper = [
         # GUI-only Signals
         # NB: These belong in the VisQtMainWindow class, since they depend
         #     on the particular GUI being used.
         # GUI-and-Controller Signals
         (self.importer.import_finished, self.window.show_analyze),
         (self.window.ui.btn_step1.clicked, self.prepare_import),
         (self.importer.status, self.window.update_progress_bar),
         (self.importer.status, self.processEvents),
         (self.window.files_removed, self.importer.remove_pieces),
         (self.window.files_added, self.importer.add_pieces),
         (self.run_the_import, self.prepare_import)
         # Inter-controller Signals
         #(self.importer.import_finished, self.analyzer.catch_import) # DEBUGGING... probably don't need this
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
      print('*** you are in prepare_import()') # DEBUGGING
      #self.window.ui.show_working.emit() # update the GUI
      self.importer.run_import.emit(self.analyzer._list_of_pieces) # run import



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
