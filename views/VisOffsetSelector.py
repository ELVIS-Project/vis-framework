#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: VisOffsetSelector.py
# Purpose: The window for selecting a note duration for offset interval.
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
"""
The window for selecting a note duration for offset interval.
"""

from Ui_select_offset import Ui_Select_Offset
from PyQt4 import QtGui, QtCore


class VisOffsetSelector(object):
    """
    Display and assign actions for the offset-selection window.
    """

    def __init__(self):
        self.dialog = QtGui.QDialog()
        self.ui = Ui_Select_Offset()
        self.ui.setupUi(self.dialog)

    def trigger(self):
        """
        Set up and get information from a window that asks the user for an offest value. The return
        value corresponds to the quarterLength duration the user chose.

        :returns: The interval offset chosen by the user, or "ALL," if relevant.
        :rtype: ``unicode``
        """
        self.dialog.show()
        # signals
        buttons = [self.ui.btn_8.clicked,
                   self.ui.btn_4.clicked,
                   self.ui.btn_2.clicked,
                   self.ui.btn_1.clicked,
                   self.ui.btn_0_5.clicked,
                   self.ui.btn_0_25.clicked,
                   self.ui.btn_0_125.clicked,
                   self.ui.btn_0_0625.clicked,
                   self.ui.btn_none.clicked]
        for btn_sig in buttons:
            btn_sig.connect(self._change_offset)
        # hold currently-selected duration
        self.current_duration = 0.5
        # show the form!
        self.dialog.exec_()
        # (User chooses stuff)
        # ... then...
        # Return the currently-selected duration
        return unicode(self.current_duration)

    @QtCore.pyqtSlot()
    def _change_offset(self):
        if self.ui.btn_8.isChecked():
            self.current_duration = 8.0
        elif self.ui.btn_4.isChecked():
            self.current_duration = 4.0
        elif self.ui.btn_2.isChecked():
            self.current_duration = 2.0
        elif self.ui.btn_1.isChecked():
            self.current_duration = 1.0
        elif self.ui.btn_0_5.isChecked():
            self.current_duration = 0.5
        elif self.ui.btn_0_25.isChecked():
            self.current_duration = 0.25
        elif self.ui.btn_0_125.isChecked():
            self.current_duration = 0.125
        elif self.ui.btn_0_0625.isChecked():
            self.current_duration = 0.0625
        elif self.ui.btn_none.isChecked():
            self.current_duration = u'ALL'
        self.ui.music21_durat.display(unicode(self.current_duration))
