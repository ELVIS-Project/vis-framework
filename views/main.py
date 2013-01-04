#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
from PyQt4 import QtGui, uic
from controllers.signals import VisSignal


class VisQtMainWindow(QtGui.QMainWindow):
	def __init__(self):
		super(VisQtMainWindow, self).__init__()
		self.ui = uic.loadUi('views/ui/new_main_window.ui')
		self.tool_import()
		self.ui.show()
		self.files_chosen = VisSignal()
	
	def tool_import(self):
		self.ui.main_screen.setCurrentWidget(self.ui.page_choose)
		self.ui.btn_analyze.setEnabled(False)
		self.ui.btn_show.setEnabled(False)
		self.ui.btn_step2.setEnabled(False)
		
	def get_files(self):
		files = QtGui.QFileDialog.getOpenFileNames(
			None,
			"Choose Files to Analyze",
			'',
			'*.nwc *.mid *.midi *.mxl *.krn *.xml *.md',
			None)
		if files:
			self.files_chosen([str(f) for f in files])
	
	def tool_analyze(self):
		self.ui.main_screen.setCurrentWidget(self.ui.page_analyze)
	
	def tool_working(self):
		self.ui.main_screen.setCurrentWidget(self.ui.page_working)
	
	def tool_about(self):
		self.ui.main_screen.setCurrentWidget(self.ui.page_about)
	
	#def tool_experiment(self):
	#	self.ui.main_screen.setCurrentWidget(self.ui.page_experiment)