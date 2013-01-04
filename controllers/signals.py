#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: signals.py
# Purpose: Holds the signal mechanism for the MVC architecture in vis.
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
Holds the signal mechanism for the MVC architecture in vis.
'''
from weakref import WeakValueDictionary


# VisSignal class directly copied from
# http://code.activestate.com/recipes/
# 576477-yet-another-signalslot-implementation-in-python/

# NB: this is probably illegal?

class VisSignal(object):
   def __init__(self):
      self.__slots = WeakValueDictionary()

   def __call__(self, *args, **kargs):
      for key in self.__slots:
         func, _ = key
         func(self.__slots[key], *args, **kargs)

   def connect(self, slot):
      key = (slot.im_func, id(slot.im_self))
      self.__slots[key] = slot.im_self

   def disconnect(self, slot):
      key = (slot.im_func, id(slot.im_self))
      if key in self.__slots:
         self.__slots.pop(key)

   def clear(self):
      self.__slots.clear()