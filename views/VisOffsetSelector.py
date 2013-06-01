#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: VisOffsetSelector.py
# Purpose: The window that allows you to select a note duration for offset.
#
# Copyright (C) 2012, 2013 Jamie Klassen, Christopher Antila
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
'''
The window that allows you to select a note duration for offset.
'''



# Imports from...
# PyQt4
from Ui_select_offset import Ui_Select_Offset
from PyQt4.QtGui import QDialog


class VisOffsetSelector(object):
    '''
    Display and assign actions for the offset-selection window.
    '''



    def __init__(self):
        self.dialog = QDialog()
        self.ui = Ui_Select_Offset()
        self.ui.setupUi(self.dialog)



    def trigger(self):
        '''
        Set up and get information from a window that asks the user for an offest
        value. The return value corresponds to the quarterLength duration the
        user chose.
        '''

        # UI setup stuff
        #self.select_offset = QtGui.QDialog()
        #self.setupUi(self.select_offset)
        self.dialog.show()

        # Setup signals
        self.ui.btn_submit.clicked.connect(self.submit_button)
        self.ui.btn_8.clicked.connect(self.button_8)
        self.ui.btn_4.clicked.connect(self.button_4)
        self.ui.btn_2.clicked.connect(self.button_2)
        self.ui.btn_1.clicked.connect(self.button_1)
        self.ui.btn_0_5.clicked.connect(self.button_0_5)
        self.ui.btn_0_25.clicked.connect(self.button_0_25)
        self.ui.btn_0_125.clicked.connect(self.button_0_125)
        self.ui.btn_0_0625.clicked.connect(self.button_0_0625)

        # Variable to hold the currently-selected duration
        self.current_duration = 0.5

        # Show the form!
        self.dialog.exec_()

        # (User chooses stuff)

        # Return the currently-selected duration
        return '[' + str(self.current_duration) + ']'



    def submit_button(self):
        self.dialog.done(0)



    def button_8(self):
        self.current_duration = 8.0
        self.ui.line_music21_duration.setText(str(self.current_duration))



    def button_4(self):
        self.current_duration = 4.0
        self.ui.line_music21_duration.setText(str(self.current_duration))



    def button_2(self):
        self.current_duration = 2.0
        self.ui.line_music21_duration.setText(str(self.current_duration))



    def button_1(self):
        self.current_duration = 1.0
        self.ui.line_music21_duration.setText(str(self.current_duration))



    def button_0_5(self):
        self.current_duration = 0.5
        self.ui.line_music21_duration.setText(str(self.current_duration))



    def button_0_25(self):
        self.current_duration = 0.25
        self.ui.line_music21_duration.setText(str(self.current_duration))



    def button_0_125(self):
        self.current_duration = 0.125
        self.ui.line_music21_duration.setText(str(self.current_duration))



    def button_0_0625(self):
        self.current_duration = 0.0625
        self.ui.line_music21_duration.setText(str(self.current_duration))
