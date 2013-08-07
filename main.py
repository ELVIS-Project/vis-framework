#! /usr/bin/python
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
# along with this program.   If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
Start vis with the PyQt4 interface.
"""

# Ensure we can import "vis"
try:
    import vis
except ImportError:
    import sys
    sys.path.insert(0, '..')

import sys
from vis.controllers.vis_controller import VisController
from multiprocessing import freeze_support


def main():
    """
    The main execution loop.
    """
    gui_controller = VisController(sys.argv)
    sys.exit(gui_controller.exec_())


if __name__ == '__main__':
    freeze_support()
    main()
