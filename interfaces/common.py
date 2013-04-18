#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:             vis
# Program Description:      Measures sequences of vertical intervals.
#
# Filename: interfaces/common.py
# Purpose: Base classes for vis' interfaces.
#
# Attribution: Based on the 'harrisonHarmony.py' module available at...
#              https://github.com/crantila/harrisonHarmony/
#
# Copyright (C) 2013 Christopher Antila, Jamie Klassen
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
'''
This module contains the VisInterface class -- the core functionality
for connecting controllers & models to views.
'''
import types

class _ViewsTmp:
   '''
   This class is private to the __init__ module. It is merely used
   as a placeholder for the view-getting functions of a VisInterface
   while it is being imported into the interpreter.
   '''
   views = {}

class _InterfaceMeta(type):
   '''
   Metaclass for all VisInterfaces. This enables the nice API-like
   syntactic sugar used in coding up a VisInterface -- in particular
   the use of the `view_getter` decorator.
   '''
   def __new__(cls, name, bases, attrs):
      # VisInterface itself is only a base class, so
      # don't tally up its view-getters
      if not 'VisInterface' == name:
         for func in _ViewsTmp.views.itervalues():
            # remove the view-getters from the class definition;
            # these will go in its `views` dictionary
            if func.__name__ in attrs:
               attrs.pop(func.__name__)
      attrs.update(views=_ViewsTmp.views)
      # now we've put the view-getting functions back in the class,
      # clear out _ViewsTmp for the next interface to be imported.
      _ViewsTmp.views = {}
      return super(_InterfaceMeta, cls).__new__(cls, name, bases, attrs)

def view_getter(class_name):
   '''
   Decorator for functions in a VisInterface subclass. Use this decorator
   with the name of a `viewable` vis class (either a model or a controller),
   and the object returned by the decorated function will be used in generating
   a view for that class.
   '''
   def wrap(func):
      # keep the association between the decorated function and the class
      # it returns views for, at least until the interface is done being imported.
      _ViewsTmp.views[class_name] = func
      return func
   return wrap

class VisInterface(object):
   '''
   Base class for interfaces between models/controllers (so-called `viewables`)
   and views.
   '''
   __metaclass__ = _InterfaceMeta
   def get_view(self, viewable, **kwargs):
      '''
      Given a viewable object, return a useful view object for it. This function
      is just a wrapper to access the functions which have been decorated with
      view_getter by the class they get views for.
      '''
      # this is a safe bet; every class has a name
      class_name = viewable.__class__.__name__
      if isinstance(viewable, types.MethodType):
         # this is to account for functions, which always have names
         # unless they're lambdas. And if you're storing a lambda in
         # here, Guido have mercy on your soul.
         class_name = viewable.__name__
      # it is possible (likely) that we should somehow traverse the
      # tree of base classes (as long as they're viewable) and return
      # some magic conglomerated thing here. I guess it can wait, though.
      return self.__class__.views[class_name](self, viewable, **kwargs)
