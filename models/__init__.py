#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: models/__init__.py
# Purpose: Load the vis models modules.
#
# Attribution:  Based on the 'harrisonHarmony.py' module available at...
#               https://github.com/crantila/harrisonHarmony/
#
# Copyright (C) 2012 Christopher Antila, Jamie Klassen
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



__all__ = ['analyzing', 'visualizing', 'experimenting', 'importing']#, 'ngram']

import analyzing
import visualizing
import experimenting
import importing
#import ngram


#from controllers.signals import VisSignal
#from PyQt4.QtCore import QAbstractItemModel


#class Model(object):
   #"""
   #Base class for all vis models. Basically Python has enough stuff builtin
   #that we might as well just have a really really simple interface to the
   #Python types with some basic signal/slot stuff to keep everything together.
   #"""
   #def __init__(self, data=None):
      #"""
      #Creates a new Model instance. The optional data parameter lets you
      #set the initial data when constructing the model.
      #"""
      #self._data = data
      #self.data_changed = VisSignal()
   #
   #@property
   #def data(self, *args):
      #return self._data
   #
   #@data.setter
   #def data(self, value):
      #if value != self._data:
         #self._data = value
         #self.data_changed(value)
