#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: controllers.py
# Purpose: Holds the "controllers" for the MVC architecture in vis.
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
Holds the "controllers" for the MVC architecture in vis.
'''



# Imports
from PyQt4.QtCore import pyqtSignal, QObject
from models.analyzing import ListOfPieces



class Controller(QObject):
   '''
   Base class for all vis controllers.
   '''



   def __init__(self):
      '''
      Creates a new instance, and assigns the appropriate widget.
      '''
      super(Controller, self).__init__()



   def setup_signals(self):
      '''
      Set methods of this controller as the slot for relevant signals emitted
      by the GUI.
      '''
      pass
