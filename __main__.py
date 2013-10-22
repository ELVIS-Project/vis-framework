#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:               vis
# Program Description:        Measures sequences of vertical intervals.
#
# Filename: __main__.py
# Purpose: Start vis with the PyQt4 interface.
#
# Copyright (C) 2012, 2013 Christopher Antila, Jamie Klassen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
.. codeauthor:: Jamie Klassen <michigan.j.frog@gmail.com>
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>

Start vis with the PyQt4 interface.
"""

# Ensure we can import "vis"
try:
    import imp
    imp.find_module('vis')
except ImportError:
    import sys
    sys.path.insert(0, '..')

import sys
from PyQt4 import QtCore, QtGui
from vis.views.main import VisQtMainWindow


class GuiController(QtCore.QObject):
    """
    Base class for all vis controllers.
    """

    def __init__(self):
        """
        Creates a new instance, and assigns the appropriate widget.
        """
        super(GuiController, self).__init__()
        self.app = QtGui.QApplication(sys.argv)
        self.window = VisQtMainWindow()

    def setup_signals(self):
        """
        Set methods of this controller as the slot for relevant signals emitted
        by the GUI.
        """
        pass


def main():
    """
    The main execution loop.
    """
    gui_controller = GuiController()
    sys.exit(gui_controller.app.exec_())


if __name__ == '__main__':
    main()
