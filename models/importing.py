#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: importing.py
# Purpose: The model classes for the Importer controller.
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
The model classes for the Importer controller.
'''


# Imports from...
# PyQt4
from PyQt4.QtCore import QAbstractListModel, QModelIndex, Qt, QVariant



class ListOfFiles(QAbstractListModel):
   # TODO: finish documenting this class
   # TODO: rewrite this class for vis8
   '''
   This model represents a list of filenames that the Importer controller should
   import, find data from, and put into a ListOfPieces for the Analyzer
   controller.
   '''
   def __init__( self, parent=None, *args ):
      QAbstractListModel.__init__(self, parent, *args)
      self.files = []

   def rowCount( self, parent=QModelIndex() ):
      return len( self.files )

   def data(self, index, role):
      if index.isValid() and Qt.DisplayRole == role:
         return QVariant( self.files[index.row()] )
      else:
         return QVariant()

   # NB: I *should* implement these, but I don't know how, so for now I won't
   #def headerData( self ):
      #pass

   #def flags():
      #pass

   def setData( self, index, value, role ):
      if Qt.EditRole == role:
         self.files[index.row()] = value
         self.dataChanged.emit( index, index )
         return True
      else:
         return False

   def insertRows( self, row, count, parent=QModelIndex() ):
      self.beginInsertRows( parent, row, row+count-1 )
      new_files = self.files[:row]
      for zed in xrange( count ):
         new_files.append( '' )
      new_files += self.files[row:]
      self.files = new_files
      self.endInsertRows()

   def alreadyThere( self, candidate ):
      # TODO: do we still need this non-standard method?
      '''
      Tests whether 'candidate' is already present in this list of files.
      '''
      return candidate in self.files

   def iterator( self ):
      for f in self.files:
         yield f

   def removeRows( self, row, count, parent=QModelIndex() ):
      self.beginRemoveRows(parent, row, row+count-1)
      self.files = self.files[:row] + self.files[row+count:]
      self.endRemoveRows()
# End class ListOfFiles --------------------------------------------------------
