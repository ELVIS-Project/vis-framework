#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:               vis
# Program Description:        Measures sequences of vertical intervals.
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
# along with this program.   If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
The model classes for the Analyzer controller.
"""


# Imports from...
# python
import copy
# PyQt4
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QObject, pyqtSignal
# music21
from music21.metadata import Metadata
from music21.note import Note, Rest
from music21.chord import Chord
from music21 import freezeThaw
from music21.stream import Score
# vis
import settings


class PartNameSetting(settings.StringSetting):
    """
    class docstring
    """
    pass


class OffsetSetting(settings.PositiveNumberSetting(settings.FloatSetting)):
    """
    Class docstring
    """
    pass


class PartsComboSetting(settings.MultiChoiceSetting):
    """
    Class docstring
    """
    def __init__(self, *args, **kwargs):
        super(PartsComboSetting, self).__init__(*args, **kwargs)
        setts = [(val, name, PartNameSetting(name))
                    for val, name in self.choices]
        for val, name, setting in setts:
            def value_changed():
                for key, sett in self.settings._settings.itervalues():
                    if sett is setting:
                        self.settings._settings.pop(key)
                        self.settings._settings[setting.val] = setting
            setting.value_changed.connect(value_changed)
        self.settings = settings.Settings({name: setting for val, name, setting in setts})


class Piece(object):
    """
    Class docstring
    """
    def __init__(self, path, score, title, part_names):
        """
        Method docstring
        """
        super(Piece, self).__init__()
        self.description = "Settings for Piece"
        self.path = path
        self.score = score
        self.part_names = part_names
        self.part_combos = []
        self.offset_intervals = []
        self.settings = settings.Settings({
            'types': settings.MultiChoiceSetting(
                 # TODO: include other interesting choices here, possibly
                 # dynamically drawn from music21
                 choices=[(Note, 'Note'),
                             (Rest, 'Rest'),
                             (Chord, 'Chord')],
                 display_name='Find these types of object'
             ),
            'title': settings.StringSetting(
                title,
                display_name='Piece Title:'
            ),
            'all_parts': settings.BooleanSetting(
                False,
                display_name='All 2-Part Combinations',
                extra_detail='Collect Statistics for all Part Combinations'
            ),
            'basso_seguente': settings.BooleanSetting(
                False,
                display_name='Basso Seguente',
                extra_detail='Generate Basso Seguente Part'
            ),
            'current_parts_combo': PartsComboSetting(
                choices=zip(self.score.parts, self.part_names),
                display_name='Compare these parts:'
            ),
            'current_offset': OffsetSetting(
                0.5,
                display_name='Offset Interval:'
            ),
            'salami': settings.BooleanSetting(
                False,
                display_name='Include repeated identical events'
            )
        })
        self.settings.all_parts.value_changed.connect(self.all_parts_changed.emit)
        self.settings.keys = ['title', 'all_parts', 'basso_seguente',
                                     'current_parts_combo', 'current_offset', 'salami']
    def update_basso_seguente(self, state):
        if state:
            self.settings.basso_seguente.display_name = 'Every part against Basso Seguente'
        else:
            self.settings.basso_seguente.display_name = 'Basso Seguente'
    
    def update(self, other_piece):
        """
        Change a Piece model to have all the same attributes
        as another piece model.
        """
        self.path = other_piece.path
        self.score = other_piece.score
        self.part_names = other_piece.part_names
        self.part_combos = other_piece.part_combos
        self.offset_intervals = other_piece.offset_intervals
        self.settings.title = other_piece.settings.title
        self.settings.current_parts_combo = other_piece.settings.current_parts_combo
        self.settings.current_offset = other_piece.settings.current_offset
        self.settings.salami = other_piece.settings.salami
    
    def add_parts_combo(self):
        """
        Method docstring
        """
        self.part_combos.append(self.settings.current_parts_combo)
        self.settings.current_parts_combo = []


class ListOfPieces(QAbstractTableModel):
    """
    This model holds a filename, a music21 Score object, and various pieces of
    information about the Score, to ease preparation for processing by the
    Analyzer and Experiment controllers.

    You cannot currently change the number of columns, or their name as returned
    by headerData(), at run-time.
    """

    # Here's the data model:
    # self._pieces : a list of lists. For each sub-list...
    #     sublist[0] : filename
    #     sublist[1] : a music21 score object (index 0) and piece title (index 1)
    #     sublist[2] : list of names of parts in the score
    #     sublist[3] : offset intervals to analyze
    #     sublist[4] : list of pairs of indices for part combinations to prepare
    #     sublist[5] : whether to repeat consecutive identcal events

    # Public class variables to track which column has which data
    # NOTE: Update _number_of_columns whenever you change the number of columns,
    #         since this variable is used by columnCount().
    # NOTE: Update _header_names whenever you change the number or definition of
    #         columns, since this variale is used by headerData().
    _number_of_columns = 6
    _header_names = ['Path', 'Title', 'List of Part Names', 'Offset',
                          'Part Combinations', 'Repeat Identical']
    
    # A role for data() that means to return the Score object rather than title
    ScoreRole = 'This is an object for the ScoreRole'
    columns = {
        'path': 0,
        'score': 1,
        'part_names': 2,
        'offset_intervals': 3,
        'part_combos': 4,
        'salami': 5
    }
    
    # This is the default values for every new row created
    default_row = Piece('', Score(), '', [])
    # NOTE:
    # When you change this default_row, you must also change the value in this test:
    # models.test_analyzing.TestListOfPiecesInsertAndRemoveRows.test_insert_7()
    def __init__(self, parent=QModelIndex()):
        """
        Create a new ListOfPieces instance. Best to use no arguments.
        """
        super(QAbstractTableModel, self).__init__() # required for QModelIndex
        self.columns = ListOfPieces.columns
        self._pieces = []



    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of pieces in this list.
        """
        return len(self._pieces)



    def columnCount(self, parent=QModelIndex()):
        """
        Return the number of columns in this ListOfPieces.
        """
        # Every time we change the number of columns, we change this class
        # variable... so it should be correct.
        return ListOfPieces._number_of_columns



    def data(self, index, role):
        """
        Returns the data for the table cell corresponding to the index. The role can be either
        Qt.DisplayRole or ListOfPieces.ScoreRole. For a list of the columns that support ScoreRole,
        see the descriptions below.

        NOTE: This method always returns a QVariant object

        data() should return the following formats, but only if this specification
        was followed when calling setData(). If the index is...
        - ListOfPieces.columns['path'] : string
        - ListOfPieces.score : either...
            - music21.stream.Score (for ListOfPieces.ScoreRole)
            - string (for Qt.DisplayRole)
        - ListOfPieces.columns['part_names'] : either...
            - list of string objects that are the part names (for ListOfPiece.ScoreRole)
            - string (for Qt.DisplayRole)
        - ListOfPieces.offset_intervals : list of float
        - ListOfPieces.parts_combinations : either...
            - [[int, int], [int, int], ...]
            - [[int, 'bs'], [int, int], ...]
            - ['all']
            - ['all', 'bs']
            where 'all' means "all combinations" and 'bs' means "basso seguente."
        - ListOfPieces.columns['salami'] : True or False
        """
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
            # get the object
            attr, = (k for k,v in self.columns.iteritems() if v == column)
            if hasattr(self._pieces[row], attr):
                post = getattr(self._pieces[row], attr)
            else:
                sett = getattr(self._pieces[row].settings, attr)
                post = sett.value
            # most things will have the Qt.DisplayRole
            if Qt.DisplayRole == role:
                # for the "score" column, we have to choose the right sub-index
                if column is self.columns['score']:
                    post = post.toPyObject()[1] if isinstance(post, QVariant) else post[1]
                # for the "list of parts" columns, convert the list into a string
                elif column is self.columns['part_names']:
                    post = str(post.toPyObject()) if isinstance(post, QVariant) else str(post)
                    # also trim the [] around the list
                    post = post[1:-1]
                # for the "list of offsets" columns, convert the list into a string
                elif column is self.columns['offset_intervals']:
                    post = str(post.toPyObject()) if isinstance(post, QVariant) else str(post)
            # some things will have the Qt.ScoreRole
            elif role is ListOfPieces.ScoreRole:
                # if the object is the score
                if column is self.columns['score']:
                    post = post.toPyObject()[0] if isinstance(post, QVariant) else post[0]
                # else if it's the list of parts
                elif column is self.columns['part_names']:
                    pass # just to avoid obliteration
                # everything else must return nothing
                else:
                    post = None

        # Must always return a QVariant
        if not isinstance(post, QVariant):
            post = QVariant(post)

        return post



    def headerData(self, section, orientation, role):
        """
        Return the column names for a ListOfPieces instance.

        Arguments:
        - section: the index of the column you want the name of
        - orientation: should be Qt.Horizontal; Qt.Vertical is ignored
        - role: should be Qt.DisplayRole; others are ignored

        If the section index is out of range, or the orientation or role is
        different than expected, an empty QVariant is returned.
        """
        # All of the column titles are stored as class variables. I decided to
        # use the class name here, rather than "self," just in case they were
        # accidentally changed in this instance. We do not want to allow that.
        if Qt.Horizontal == orientation and Qt.DisplayRole == role and \
        0 <= section < ListOfPieces._number_of_columns:
            return ListOfPieces._header_names[section]
        else:
            return QVariant()



    def setData(self, index, value, role):
        """
        Set the data in a particular cell. The index must be a QModelIndex as
        returned by, for example, ListOfPieces.createIndex. The value should be
        the appropriate type for the cell you are setting. The role must be
        Qt.EditRole, or no change is made.

        Returns True on setting the data in the cell, othwerise False.

        >>> a = ListOfPieces()
        >>> a.insertRows(0, 1)
        >>> index = a.createIndex(0, a.columns['path'])
        >>> a.setData(index, 'kyrie.krn', Qt.EditRole)

        Use the following data formats:
        - ListOfPieces.columns['path'] : string
        - ListOfPieces.score : tuple, being (music21.stream.Score, string)
        - ListOfPieces.columns['part_names'] : list of string
        - ListOfPieces.offset_intervals : list of float
        - ListOfPieces.parts_combinations : either...
            - [[int, int], [int, int], ...]
            - [[int, 'bs'], [int, int], ...]
            - ['all']
            - ['all', 'bs']
            where 'all' means "all combinations" and 'bs' means "basso seguente."
        - ListOfPieces.columns['salami'] : True or False

        This method does not check your argument is the right type.
        """
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
            attr, = (k for k,v in self.columns.iteritems() if v == column)
            if hasattr(self._pieces[row], attr):
                setattr(self._pieces[row], attr, value)
            else:
                sett = getattr(self._pieces[row].settings, attr)
                sett.value = value
            self.dataChanged.emit(index, index)
            return True
        else:
            return False



    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Insert a certain number of rows at a certain point in the ListOfPieces.

        The first argument is the index you want for the first row to be inserted.
        The second argument is the number of rows to insert.

        The elements already in the list, with an index lower than "row" will
        retain their index values. The elements at indices "row" and higher will
        have an index value that is their original value plus "count".

        Each row is initialized with the data contained in the class variable "default_row"
        """
        self.beginInsertRows(parent, row, row+count-1)
        for zed in xrange(count):
            self._pieces.insert(row, copy.deepcopy(ListOfPieces.default_row))
        self.endInsertRows()



    def removeRows(self, row, count, parent=QModelIndex()):
        """
        This is the opposite of insertRows(), and the arguments work in the same
        way.
        """
        self.beginRemoveRows( parent, row, row+count-1 )
        self._pieces = self._pieces[:row] + self._pieces[row+count:]
        self.endRemoveRows()
    
    def clear(self):
        self.removeRows(0, self.rowCount())



    def __iter__(self):
        """
        Create an iterator that returns each of the filenames in this ListOfFiles.
        """
        for piece_data in self._pieces:
            yield piece_data
# End Class ListOfPieces ------------------------------------------------------


class AnalysisRecord(object):
    """
    Stores an intermediate record of an analysis. This class does not hold
    statistics or other results, but rather represents a mid-point, where the
    information being analyzed is stored separately from the piece.
    
    Each AnalysisRecord contains the following information:
    - a (JSON-serialized) music21 Metadata object, with information about the 
      work and movement
    - the names of the parts being analyzed
    - the minimum quarterLength offset value between subsequent elements
    - the events in the parts being analyzed, and the offset at which they happen
    - whether the score was "salami sliced" (maintaining the same offset
      between events) or not (which does not include an event if it is equal to
      the previous offset)
    
    This class is iterable. Each iteration returns a 2-tuple, where index 0 is
    the offset at which the event occurs in the Score, and index 1 is the event
    itself.
    """
    # Instance Data:
    # ==============
    # metadata : a music21 Metadata object
    # _part_names : list of string objects that are the part names
    # _offset : the (minimum) offset value between events
    # _is_salami : whether the score was "salami sliced"
    # _record : a list representing a record of an analysis, such that:
    #     _record[x][0] : holds the offset at which the event happened
    #     _record[x][1] : holds the event itself
    def __init__(self, metadata=None, part_names=None, offset=None, salami=None):
        """
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
        """
        self._record = []
        
        if metadata is None:
            m = Metadata()
            jf = freezeThaw.JSONFreezer(m)
            self._metadata = jf.json
        else:
            jf = freezeThaw.JSONFreezer(metadata)
            self._metadata = jf.json
        
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
        """
        Iterate through the events in this AnalysisRecord.
        """
        for event in self._record:
            yield event
    
    def __getitem__(self, key):
        """
        Access the event at a particular index in the AnalysisRecord.
        """
        return self._record[key]
    
    def __len__(self):
        """
        Returns the number of events in the AnalysisRecord.
        """
        return len(self._record)
    
    def part_names(self):
        """
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
        """
        return self._part_names
    
    def offset(self):
        """
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
        """
        return self._offset
    
    def salami_sliced(self):
        """
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
        """
        return self._salami
    
    def metadata(self):
        """
        Return the music21 Metadata object stored in this AnalysisRecord.
        """
        jt = freezeThaw.JSONThawer()
        jt.json = self._metadata
        return jt.storedObject
    
    def append(self, offset, event):
        # TODO: replace append_event() with this
        self.append_event(offset, event)
    
    def append_event(self, offset, event):
        """
        Add an event to the end of this AnalysisRecord.

        There are two arguments, both mandatory:
        - offset : (an int or float) the offset in the Score at which event happens
        - event : the object being analyzed
        """
        self._record.append((offset, event))
    
    def most_recent_event(self):
        """
        Returns the 2-tuple representing the most recently-recorded event's
        offset and the event itself.

        Returns (None, None) if no events have been recorded.
        """
        # TODO: test this
        if 0 < len(self._record):
            return self._record[-1]
        else:
            return (None, None)
# End class AnalysisRecord -----------------------------------------------------
