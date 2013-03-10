#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: analyzing.py
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
# python
import copy
# PyQt4
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
# music21
from music21.metadata import Metadata



class ListOfPieces(QAbstractTableModel):
   '''
   This model holds a filename, a music21 Score object, and various pieces of
   information about the Score, to ease preparation for processing by the
   Analyzer and Experiment controllers.

   You cannot currently change the number of columns, or their name as returned
   by headerData(), at run-time.
   '''

   # Here's the data model:
   # self._pieces : a list of lists. For each sub-list...
   #    sublist[0] : filename
   #    sublist[1] : a music21 score object (index 0) and piece title (index 1)
   #    sublist[2] : list of names of parts in the score
   #    sublist[3] : offset intervals to analyze
   #    sublist[4] : list of pairs of indices for part combinations to prepare
   #    sublist[5] : whether to repeat consecutive identcal events

   # Public class variables to track which column has which data
   # NOTE: Update _number_of_columns whenever you change the number of columns,
   #       since this variable is used by columnCount().
   # NOTE: Update _header_names whenever you change the number or definition of
   #       columns, since this variale is used by headerData().
   _number_of_columns = 6
   _header_names = ['Path', 'Title', 'List of Part Names', 'Offset',
                    'Part Combinations', 'Repeat Identical']
   filename = 0
   score = 1
   parts_list = 2
   offset_intervals = 3
   parts_combinations = 4
   repeat_identical = 5

   # A role for data() that means to return the Score object rather than title
   ScoreRole = 'This is an object for the ScoreRole'

   # This is the default values for every new row created
   default_row = ['', None, [], [0.5], '(no selection)', False]
   # NOTE:
   # When you change this default_row, you must also change the value in this test:
   # models.test_analyzing.TestListOfPiecesInsertAndRemoveRows.test_insert_7()



   def __init__(self, parent=QModelIndex()):
      '''
      Create a new ListOfPieces instance. Best to use no arguments.
      '''
      super(QAbstractTableModel, self).__init__() # required for QModelIndex
      self._pieces = []



   def rowCount(self, parent=QModelIndex()):
      '''
      Return the number of pieces in this list.
      '''
      return len(self._pieces)



   def columnCount(self, parent=QModelIndex()):
      '''
      Return the number of columns in this ListOfPieces.
      '''
      # Every time we change the number of columns, we change this class
      # variable... so it should be correct.
      return ListOfPieces._number_of_columns



   def data(self, index, role):
      '''
      Returns the data for the table cell corresponding to the index. The role can be either
      Qt.DisplayRole or ListOfPieces.ScoreRole. For a list of the columns that support ScoreRole,
      see the descriptions below.

      NOTE: This method always returns a QVariant object

      data() should return the following formats, but only if this specification
      was followed when calling setData(). If the index is...
      - ListOfPieces.filename : string
      - ListOfPieces.score : either...
         - music21.stream.Score (for ListOfPieces.ScoreRole)
         - string (for Qt.DisplayRole)
      - ListOfPieces.parts_list : either...
         - list of string objects that are the part names (for ListOfPiece.ScoreRole)
         - string (for Qt.DisplayRole)
      - ListOfPieces.offset_intervals : list of float
      - ListOfPieces.parts_combinations : either...
         - [[int, int], [int, int], ...]
         - [[int, 'bs'], [int, int], ...]
         - ['all']
         - ['all', 'bs']
         where 'all' means "all combinations" and 'bs' means "basso seguente."
      - ListOfPieces.repeat_identical : True or False
      '''
      # Set the row and column
      row = None
      column = None
      if isinstance(index, QModelIndex):
         # if the QModelIndex is invalid, we won't bother with it
         if not index.isValid():
            return None
         # otherwise, get the row and column from the QModelIndex
         row = index.row()
         column = index.column()
      else:
         row = index[0]
         column = index[1]

      # Return value
      post = None

      if 0 <= row < len(self._pieces) and 0 <= column < self._number_of_columns:
         # most things will have the Qt.DisplayRole
         if Qt.DisplayRole == role:
            # get the object
            post = self._pieces[row][column]
            # for the "score" column, we have to choose the right sub-index
            if column is ListOfPieces.score:
               post = post.toPyObject()[1] if isinstance(post, QVariant) else post[1]
            # for the "list of pieces" column, convert the list into a string
            elif column is ListOfPieces.parts_list:
               post = str(post.toPyObject()) if isinstance(post, QVariant) else str(post)
               post = post[1:-1]
         # some things will have the Qt.ScoreRole
         elif role is ListOfPieces.ScoreRole:
            # get the object
            post = self._pieces[row][column]
            # if it's the score
            if column is ListOfPieces.score:
               post = post.toPyObject()[0] if isinstance(post, QVariant) else post[0]
            # else if it's the list of parts
            elif column is ListOfPieces.parts_list:
               pass # just to avoid obliteration
            # everything else must return nothing
            else:
               post = None

      # Must always return a QVariant
      if not isinstance(post, QVariant):
         post = QVariant(post)

      return post



   def headerData(self, section, orientation, role):
      '''
      Return the column names for a ListOfPieces instance.

      Arguments:
      - section: the index of the column you want the name of
      - orientation: should be Qt.Horizontal; Qt.Vertical is ignored
      - role: should be Qt.DisplayRole; others are ignored

      If the section index is out of range, or the orientation or role is
      different than expected, an empty QVariant is returned.
      '''
      # All of the column titles are stored as class variables. I decided to
      # use the class name here, rather than "self," just in case they were
      # accidentally changed in this instance. We do not want to allow that.
      if Qt.Horizontal == orientation and Qt.DisplayRole == role and \
      0 <= section < ListOfPieces._number_of_columns:
         return ListOfPieces._header_names[section]
      else:
         return QVariant()



   def setData(self, index, value, role):
      '''
      Set the data in a particular cell. The index must be a QModelIndex as
      returned by, for example, ListOfPieces.createIndex. The value should be
      the appropriate type for the cell you are setting. The role must be
      Qt.EditRole, or no change is made.

      Returns True on setting the data in the cell, othwerise False.

      >>> a = ListOfPieces()
      >>> a.insertRows(0, 1)
      >>> index = a.createIndex(0, ListOfPieces.filename)
      >>> a.setData(index, 'kyrie.krn', Qt.EditRole)

      Use the following data formats:
      - ListOfPieces.filename : string
      - ListOfPieces.score : tuple, being (music21.stream.Score, string)
      - ListOfPieces.parts_list : list of string
      - ListOfPieces.offset_intervals : list of float
      - ListOfPieces.parts_combinations : either...
         - [[int, int], [int, int], ...]
         - [[int, 'bs'], [int, int], ...]
         - ['all']
         - ['all', 'bs']
         where 'all' means "all combinations" and 'bs' means "basso seguente."
      - ListOfPieces.repeat_identical : True or False

      This method does not check your argument is the right type.
      '''
      # Set the row and column
      row = None
      column = None
      if isinstance(index, QModelIndex):
         row = index.row()
         column = index.column()
      else:
         row = index[0]
         column = index[1]
         # we still need a QModelIndex for the dataChanged signal
         index = self.createIndex(row, column)

      # Set the data
      if Qt.EditRole == role:
         self._pieces[row][column] = value
         self.dataChanged.emit(index, index)
         return True
      else:
         return False



   def insertRows(self, row, count, parent=QModelIndex()):
      '''
      Insert a certain number of rows at a certain point in the ListOfPieces.

      The first argument is the index you want for the first row to be inserted.
      The second argument is the number of rows to insert.

      The elements already in the list, with an index lower than "row" will
      retain their index values. The elements at indices "row" and higher will
      have an index value that is their original value plus "count".

      Each row is initialized with the data contained in the class variable "default_row"
      '''
      self.beginInsertRows(parent, row, row+count-1)
      for zed in xrange(count):
         self._pieces.insert(row, copy.deepcopy(ListOfPieces.default_row))
      self.endInsertRows()



   def removeRows(self, row, count, parent=QModelIndex()):
      '''
      This is the opposite of insertRows(), and the arguments work in the same
      way.
      '''
      self.beginRemoveRows( parent, row, row+count-1 )
      self._pieces = self._pieces[:row] + self._pieces[row+count:]
      self.endRemoveRows()



   def __iter__(self):
      '''
      Create an iterator that returns each of the filenames in this ListOfFiles.
      '''
      for piece_data in self._pieces:
         yield piece_data
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
   #    _record[x][0] : holds the offset at which the event happened
   #    _record[x][1] : holds the event itself



   def __init__(self, metadata=None, part_names=None, offset=None, salami=None):
      '''
      Create a new AnalysisRecord. You should set the following keyword
      arguments when you make the AnalysisRecord:
      - metadata (with a music21 Metadata object)
      - _part_names (with a list of strings containing part names)
      - _offset (with a floating point number)
      - _salami (boolean)

      If you do not provide this information, sensible defaults will be used:
      - empty Metadata
      - _part_names : ['']
      - _offset : 0.0
      - _salami : False
      '''
      self._record = []

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



   def __getitem__(self, key):
      '''
      Access the event at a particular index in the AnalysisRecord.
      '''
      return self._record[key]



   def __len__(self):
      '''
      Returns the number of events in the AnalysisRecord.
      '''
      return len(self._record)



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
      return self._salami



   def append(self, offset, event):
      # TODO: replace append_event() with this
      self.append_event(offset, event)



   def append_event(self, offset, event):
      '''
      Add an event to the end of this AnalysisRecord.

      There are two arguments, both mandatory:
      - offset : (an int or float) the offset in the Score at which event happens
      - event : the object being analyzed
      '''
      self._record.append((offset, event))



   def most_recent_event(self):
      '''
      Returns the 2-tuple representing the most recently-recorded event's
      offset and the event itself.

      Returns (None, None) if no events have been recorded.
      '''
      # TODO: test this
      if 0 < len(self._record):
         return self._record[-1]
      else:
         return (None, None)
# End class AnalysisRecord -----------------------------------------------------



class AnalysisSettings(object):
   '''
   Hold settings relevant to conducting analyses.

   All the possible settings:
   - types : a list of 2-tuples, where element 0 is a type you want to count as an "event,"
             and element 1 is a function that produces a string version suitable for an
             AnalysisRecord instance.
   - offset : the minimum quarterLength offset between consecutive events
   - salami : if True, all events will be the offset distance from each
      other, even if this produces a series of identical events
   '''



   def __init__(self):
      '''
      Create an empty AnalysisSettings instance with no settings.
      '''
      self._settings = {}



   def set(self, setting, value):
      '''
      Set the value of a setting. If the setting does not yet exist, it is
      created and initialized to the value.
      '''
      self._settings[setting] = value



   def has(self, setting):
      '''
      Returns True if a setting already exists in this AnalysisSettings
      instance, or else False.
      '''
      return setting in self._settings



   def get(self, setting):
      '''
      Return the value of a setting, or None if the setting does not exist.
      '''
      if self.has(setting):
         return self._settings[setting]
      else:
         return None
# End class AnalysisSettings -----------------------------------------------------------------------
