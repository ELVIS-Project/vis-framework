#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: data.py
# Purpose: The model classes for the Analyzer controller.
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
The model classes for the Analyzer controller.
'''


# Imports from...
# PyQt4
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
# music21
from music21.metadata import Metadata



class ListOfPieces(QAbstractTableModel):
   # TODO: finish documenting this class
   # TODO: rewrite this class for vis8
   '''
   This model holds a filename, a music21 Score object, and various pieces of
   information about the Score, to ease preparation for processing by the
   Analyzer and Experiment controllers.
   '''

   # Here's the data model:
   # self.pieces : a list of lists. For each sub-list...
   #    sublist[0] : filename
   #    sublist[1] : a music21 score object OR piece title (depending on "role" when data() is called)
   #    sublist[2] : list of names of parts in the score
   #    sublist[3] : offset intervals to analyze
   #    sublist[4] : list of pairs of indices for part combinations to prepare

   # Public class variables to track which column has which data
   filename = 0
   score = 1
   parts_list = 2
   offset_intervals = 3
   parts_combinations = 4

   def __init__( self, parent=QModelIndex() ):
      #QAbstractTableModel.__init__(self, parent)
      #super.__init__(self, part) ??????????

      self.pieces = []

   def rowCount( self, parent=QModelIndex() ):
      #return len(self.pieces)
      pass

   def columnCount( self, parent=QModelIndex() ):
      # There are 6 columns (see "data model" above)
      #return 6
      pass

   def data(self, index, role):
      #if index.isValid():
         #if Qt.DisplayRole == role:
            #if self.model_score == index.column():
               #score = self.pieces[index.row()][index.column()]
               #if score.metadata is not None:
                  #return QVariant( score.metadata.title )
               #else:
                  #return QVariant('')
            #elif self.model_parts_list == index.column():
               ## this is for the part names
               #return QVariant( str(self.pieces[index.row()][index.column()])[1:-1] )
            #elif self.model_n == index.column():
               #return QVariant(",".join(str(n) for n in self.pieces[index.row()][index.column()]))
            #else:
               #return QVariant( self.pieces[index.row()][index.column()] )
         #elif 'raw_list' == role:
            #return QVariant( self.pieces[index.row()][index.column()] )
         #else:
            #return QVariant()
      pass

   def headerData( self, section, orientation, role ):
      #header_names = ['Path', 'Title', 'List of Part Names', 'Offset', 'n', \
                      #'Compare These Parts']
      #
      #if Qt.Horizontal == orientation and Qt.DisplayRole == role:
         #return header_names[section]
      #else:
         #return QVariant()
      pass

   def setData( self, index, value, role ):
      pass
      # NB: use this pattern
      # index = self.analysis_pieces.createIndex( 0, 1 )
      # self.analysis_pieces.setData( index, 'ballz', QtCore.Qt.EditRole )
      # --
      #if Qt.EditRole == role:
         #self.pieces[index.row()][index.column()] = value
         #self.dataChanged.emit( index, index )
         #return True
      #else:
         #return False

   def insertRows( self, row, count, parent=QModelIndex() ):
      pass
      #self.beginInsertRows( parent, row, row+count-1 )
      #for zed in xrange(count):
         #self.pieces.insert( row, ['', None, [], 0.5, [2], "(no selection)"] )
      #self.endInsertRows()

   def removeRows( self, row, count, parent=QModelIndex() ):
      pass
      #self.beginRemoveRows( parent, row, row+count-1 )
      #self.pieces = self.pieces[:row] + self.pieces[row+count:]
      #self.endRemoveRows()

   def iterate_rows( self ):
      pass
      #for row in self.pieces:
         #yield row
# End Class ListOfPieces ------------------------------------------------------



class AnalysisRecord(object):
   '''
   Stores an intermediate record of an analysis. This class does not hold
   statistics or other results, but rather represents a mid-point, where the
   information being analyzed is stored separately from the piece.

   Each AnalysisRecord contains the following information:
   - a music21 Metadata object, with information about the work and movement
   - the names of the parts being analyzed
   - the minimum quarterLength offset value between subsequent elements
   - the events in the parts being analyzed, and the offset at which they happen
   - whether the score was "salami sliced" (maintaining the same offset
     between events) or not (which does not include an event if it is equal to
     the previous offset)

   This class is iterable. Each iteration returns a 2-tuple, where index 0 is
   the offset at which the event occurs in the Score, and index 1 is the event
   itself.

   You can access the Metadata object directly, through the "metadata" property.
   '''



   # Instance Data:
   # ==============
   # metadata : a music21 Metadata object
   # _part_names : list of string objects that are the part names
   # _offset : the (minimum) offset value between events
   # _is_salami : whether the score was "salami sliced"
   # _record : a list representing a record of an analysis, such that:
   #    _record[0] : holds the offset at which the event happened in the Score
   #    _record[1] : holds the event itself



   def __init__(self, metadata=None, part_names=None, offset=None, salami=None):
      '''
      Create a new AnalysisRecord. You should set the following keyword
      arguments when you make the AnalysisRecord:
      - metadata (with a music21 Metadata object)
      - part_names (with a list of strings containing part names)
      - offset (with a floating point number)
      - salami (boolean)

      If you do not provide this information, sensible defaults will be used:
      - empty Metadata
      - part_names : ['']
      - offset : 0.0
      - salami : False
      '''
      if metadata is None:
         self.metadata = Metadata()
      else:
         self.metadata = metadata

      if part_names is None:
         self._part_names = ['']
      else:
         self._part_names = part_names

      if offset is None:
         self._offset = 0.0
      else:
         self._offset = offset

      if salami is None:
         self._salami = False
      else:
         self._salami = salami



   def __iter__(self):
      '''
      Iterate through the events in this AnalysisRecord.
      '''
      for event in self._record:
         yield event



   def part_names(self):
      '''
      Return a list of strings that represent the part names involved in this
      AnalysisRecord.

      >>> a = AnalysisRecord(part_names=['Clarinet', 'Tuba'])
      >>> a.part_names()
      ['Clarinet', 'Tuba']
      >>> a = AnalysisRecord(part_names=['Piano'])
      >>> a.part_names()
      ['Piano']
      >>> a = AnalysisRecord()
      >>> a.part_names()
      ['']
      '''
      return self._part_names



   def offset(self):
      '''
      Return the minimum offset between events in this AnalysisRecord. If
      salami_sliced() reutrns True, then all events are this offset from each
      other.

      >>> a = AnalysisRecord(offset=1)
      >>> a.offset()
      1
      >>> a = AnalysisRecord(offset=0.5)
      >>> a.offset()
      0.5
      >>> a = AnalysisRecord()
      >>> a.offset()
      0.0
      '''
      return self._offset



   def salami_sliced(self):
      '''
      Return whether or not the score was "salami sliced" to produce this
      AnalysisRecord.

      >>> a = AnalysisRecord(salami=True)
      >>> a.salami_sliced()
      True
      >>> a = AnalysisRecord(salami=False)
      >>> a.salami_sliced()
      False
      >>> a = AnalysisRecord()
      >>> a.salami_sliced()
      False
      '''
      return self._is_salami



   def append_event(self, offset, event):
      '''
      Add an event to the end of this AnalysisRecord.

      There are two arguments, both mandatory:
      - offset : (an int or float) the offset in the Score at which event happens
      - event : the object being analyzed
      '''
      self._record.append((offset, event))
# End class AnalysisRecord -----------------------------------------------------
