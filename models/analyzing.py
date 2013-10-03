#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: analyzing.py
# Purpose: The model class used on the "analyze" panel of the PyQt4 GUI.
#
# Copyright (C) 2012, 2013 Jamie Klassen, Christopher Antila
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
The model class used on the "analyze" panel of the PyQt4 GUI.
"""

import copy
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from music21.metadata import Metadata
from music21.note import Note, Rest
from music21.chord import Chord
from music21 import freezeThaw
from vis.workflow import WorkflowManager


class ListOfPieces(QAbstractTableModel):
    """
    This class manages various metadata and settings of IndexedPiece objects that will be used in
    an analysis, including:

    * path
    * title
    * list of part names
    * offset interval (optional)
    * part combinations
    * repeat identical
    """

    # Here's the data model:
    # self._pieces : a list of lists. For each sub-list...
    #    sublist[0] : filename
    #    sublist[1] : an IndexedPiece object (index 0) and piece title (index 1)
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
    default_row = ['', None, [], u'(optional)', u'(no selection)', False]
    # NOTE:
    # When you change this default_row, you must also change the value in this test:
    # models.test_analyzing.TestListOfPiecesInsertAndRemoveRows.test_insert_7()

    def __init__(self, parent=QModelIndex()):
        """
        Create a new ListOfPieces instance. Best to use no arguments.
        """
        super(ListOfPieces, self).__init__()  # required for QModelIndex
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

        Index is a 2-tuple. Element 0 is the row, it's an int corresponding to the IndexedPiece you
        want. Element 1 is the column, which is the attribute, which is a ListOfPieces class
        variable (see the list below).

        Note about Return Types:
        If the role is Qt.DisplayRole, then this method always wraps its return value in a QVariant
        object; otherwise, the original object type is returned.

        data() should return the following formats, but only if this specification
        was followed when calling setData(). If the index is...
        - ListOfPieces.filename : string
        - ListOfPieces.score : either...
            - vis.models.indexed_piece.IndexedPiece (for ListOfPieces.ScoreRole)
            - the piece title, a string (for Qt.DisplayRole)
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
            # most things will have the Qt.DisplayRole
            if Qt.DisplayRole == role:
                if ListOfPieces.filename is column:
                    post = self._pieces[row][1][0].metadata(u'pathname')
                elif ListOfPieces.score is column:
                    post = self._pieces[row][1][0].metadata(u'title')
                elif ListOfPieces.parts_list is column:
                    post = self._pieces[row][1][0].metadata(u'parts')
                    post = str(post.toPyObject()) if isinstance(post, QVariant) else str(post)
                    post = post[1:-1]  # trim the [] around the list
                else:  # the others can just do this
                    post = self._pieces[row][column]
                if ListOfPieces.offset_intervals == column:
                    post = str(post.toPyObject()) if isinstance(post, QVariant) else str(post)
            # some things will have the ListOfPieces.ScoreRole
            elif role is ListOfPieces.ScoreRole:
                if column is ListOfPieces.score:
                    post = self._pieces[row][1][0]
                elif column is ListOfPieces.parts_list:
                    post = self._pieces[row][1][0].metadata(u'parts')
            # everything else must return nothing
            else:
                post = None

        # If the role is Qt.DisplayRole, we must always return a QVariant
        if Qt.DisplayRole == role:
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
            self._pieces[row][column] = value
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
        self.beginInsertRows(parent, row, row + count - 1)
        for zed in xrange(count):
            self._pieces.insert(row, copy.deepcopy(ListOfPieces.default_row))
        self.endInsertRows()

    def removeRows(self, row, count, parent=QModelIndex()):
        """
        This is the opposite of insertRows(), and the arguments work in the same
        way.
        """
        self.beginRemoveRows(parent, row, row + count - 1)
        self._pieces = self._pieces[:row] + self._pieces[row + count:]
        self.endRemoveRows()

    def __iter__(self):
        """
        Create an iterator that returns each of the filenames in this ListOfFiles.
        """
        for piece_data in self._pieces:
            yield piece_data

    def __len__(self):
        "Alias for rowCount()."
        return self.rowCount()

    def get_workflow_manager(self, quality, simple):
        """
        Get a WorkflowManager instance with all the IndexedPiece objects and relevant settings
        as currently held in this ListOfPieces.

        :param quality: Whether to display interval quality.
        :type quality: boolean
        :param simple: Whether to show all intervals as simple intervals.
        :type simple: boolean
        """
        # create the WorkflowManager with the currently-held IndexedPieces
        l_o_ip = [self.data((i, ListOfPieces.score), ListOfPieces.ScoreRole) for i in xrange(len(self))]
        workm = WorkflowManager(l_o_ip)
        # set the metadata for each piece
        for i in xrange(len(self._pieces)):
            # set ListOfPieces.parts_list (maybe later?)
            # set ListOfPieces.score (for title) (maybe later?)
            # set ListOfPieces.offset_intervals
            val = self._pieces[i][ListOfPieces.offset_intervals]
            if u'(optional)' != val:
                workm.settings(i, u'offset interval', val)
            # set ListOfPieces.parts_combinations
            val = self._pieces[i][ListOfPieces.parts_combinations]
            if u'(no selection)' != val:
                workm.settings(i, u'voice combinations', val)
                # set ListOfPieces.repeat_identical
                # NOTE: we only want to do this if we're also using the offset filter
                val = self._pieces[i][ListOfPieces.repeat_identical]
                if val is False:
                    workm.settings(i, u'filter repeats', True)
            # quality
            workm.settings(i, u'interval quality', quality)
            # simple
            workm.settings(i, u'simple intervals', simple)
        return workm
