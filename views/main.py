#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:             vis
# Program Description:      Measures sequences of vertical intervals.
#
# Filename: main.py
# Purpose: The main view class.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------



# Imports from...
# Python
from itertools import chain
from os import walk
from os.path import splitext, join
# PyQt4
from PyQt4 import QtGui, uic, QtCore



class VisQtMainWindow(QtGui.QMainWindow, QtCore.QObject):
   # Signals for connecting to the controllers
   files_added = QtCore.pyqtSignal(list)
   files_removed = QtCore.pyqtSignal(list)
   show_import = QtCore.pyqtSignal()
   show_analyze = QtCore.pyqtSignal()
   show_working = QtCore.pyqtSignal()
   show_about = QtCore.pyqtSignal()
   show_experiment = QtCore.pyqtSignal()

   def __init__(self, vis_controller):
      '''
      The argument is the instance of VisController controlling this class. It's
      used to send signals.
      '''
      super(VisQtMainWindow, self).__init__() # required for signals
      self.vis_controller = vis_controller
      self.ui = uic.loadUi('views/ui/main_window.ui')
      self.tool_import()
      self.ui.show()
      # Setup GUI-only Signals
      mapper = [
         (self.show_import, self.tool_import),
         (self.show_analyze, self.tool_analyze),
         (self.show_working, self.tool_working),
         (self.show_about, self.tool_about),
         (self.show_experiment, self.tool_experiment),
         # TODO: decide whether we need these, or we should just use the signals from the previous line
         (self.ui.btn_choose_files.clicked, self.tool_import),
         (self.ui.btn_about.clicked, self.tool_about),
         (self.ui.btn_analyze.clicked, self.tool_analyze),
         (self.ui.btn_experiment.clicked, self.tool_experiment),
         (self.ui.btn_dir_add.clicked, self.add_dir),
         (self.ui.btn_file_add.clicked, self.add_files),
         (self.ui.btn_file_remove.clicked, self.remove_files),
         (self.ui.btn_step1.clicked, self.tool_working),
      ]
      for signal, slot in mapper:
         signal.connect(slot)



   # Methods Doing GUI Stuff ---------------------------------------------------
   # Pressing Buttons in the Toolbar -----------------------
   @QtCore.pyqtSlot()
   def tool_import(self):
      self.ui.main_screen.setCurrentWidget(self.ui.page_choose)
      self.ui.btn_about.setEnabled(True)
      self.ui.btn_choose_files.setEnabled(True)
      self.ui.btn_analyze.setEnabled(False)
      self.ui.btn_experiment.setEnabled(False)
      self.ui.btn_step1.setEnabled(True)
      self.ui.btn_step2.setEnabled(False)

   @QtCore.pyqtSlot()
   def tool_analyze(self):
      self.ui.main_screen.setCurrentWidget(self.ui.page_analyze)
      self.ui.btn_choose_files.setEnabled(False)
      self.ui.btn_analyze.setChecked(True)
      self.ui.btn_about.setEnabled(True)
      self.ui.btn_analyze.setEnabled(True)
      self.ui.btn_experiment.setEnabled(False)
      self.ui.btn_step1.setEnabled(False)
      self.ui.btn_step2.setEnabled(True)

   @QtCore.pyqtSlot()
   def tool_working(self):
      self.ui.main_screen.setCurrentWidget(self.ui.page_working)
      # make sure nothing is enabled
      self.ui.btn_about.setEnabled(False)
      self.ui.btn_choose_files.setEnabled(False)
      self.ui.btn_analyze.setEnabled(False)
      self.ui.btn_experiment.setEnabled(False)
      self.ui.btn_step1.setEnabled(False)
      self.ui.btn_step2.setEnabled(False)
      # make sure nothing is checked
      self.ui.btn_about.setChecked(False)
      self.ui.btn_analyze.setChecked(False)
      self.ui.btn_choose_files.setChecked(False)
      self.ui.btn_experiment.setChecked(False)
      # Disable the details-selection until a particular piece is selected
      self.ui.grp_settings_for_piece.setEnabled(False)
      self.ui.grp_settings_for_piece.setVisible(False)
      # Tell the vis_controller to run the import process
      self.vis_controller.run_the_import.emit()

   @QtCore.pyqtSlot()
   def tool_about(self):
      self.ui.main_screen.setCurrentWidget(self.ui.page_about)
      # leave enabled/disabled as-is, but make sure only "about" is checked
      self.ui.btn_about.setChecked(True)
      self.ui.btn_analyze.setChecked(False)
      self.ui.btn_choose_files.setChecked(False)
      self.ui.btn_experiment.setChecked(False)

   @QtCore.pyqtSlot()
   def tool_experiment(self):
      self.ui.main_screen.setCurrentWidget(self.ui.page_show)
      self.ui.btn_about.setEnabled(True)
      self.ui.btn_choose_files.setEnabled(False)
      self.ui.btn_analyze.setEnabled(True)
      self.ui.btn_experiment.setEnabled(True)
      self.ui.btn_experiment.setChecked(True)
      self.ui.btn_step1.setEnabled(False)
      self.ui.btn_step2.setEnabled(False)

   # Operations on the Importer panel ----------------------
   @QtCore.pyqtSlot()
   def add_files(self):
      files = QtGui.QFileDialog.getOpenFileNames(
         None,
         "Choose Files to Analyze",
         '',
         '*.nwc *.mid *.midi *.mxl *.krn *.xml *.md',
         None)
      if files:
         self.files_added.emit([str(f) for f in files])

   @QtCore.pyqtSlot()
   def add_dir(self):
      d = QtGui.QFileDialog.getExistingDirectory(\
         None,
         "Choose Directory to Analyze",
         '',
         QtGui.QFileDialog.ShowDirsOnly)
      d = str(d)
      extensions = ['.nwc.', '.mid','.midi','.mxl','.krn','.xml','.md']
      possible_files = chain(*[[join(path,fp) for fp in files if
                        splitext(fp)[1] in extensions]
                        for path,names,files in walk(d)])
      self.files_added.emit(list(possible_files))

   @QtCore.pyqtSlot()
   def remove_files(self):
      """
      Method which finds which files the user has selected for
      removal and emits a signal containing their names.
      """
      pass

   # Other Things ------------------------------------------
   @QtCore.pyqtSlot(str)
   def update_progress_bar(self, progress):
      pass
