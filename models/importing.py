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
"""
The model classes for the Importer controller.
"""

# Imports from...
# PyQt4
from PyQt4.QtCore import QAbstractListModel, QModelIndex, Qt


class ListOfFiles(QAbstractListModel):
    """
    This model represents a list of filenames that the Importer controller should
    import, find data from, and put into a ListOfPieces for the Analyzer
    controller.
    """

    def __init__(self, parent=None, *args):
        """
        Create a new ListOfFiles instance. Best to use no arguments.
        """
        super(ListOfFiles, self).__init__()  # required for QModelIndex
        self._files = []

    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of files in the list.
        """
        return len(self._files)

    def data(self, index, role):
        """
        Return the filename with the specified index as a QVariant.

        The first argument is the index to return. The second argument is the
        role, which should be QtCore.Qt.DisplayRole.

        The first argument may also be an int indicating the row you wish to
        view.

        >>> a = ListOfFiles()
        >>> a.insertRows(0, 2)
        >>> a.setData(a.createIndex(0), 'kyrie.krn', Qt.EditRole)
        >>> a.setData(a.createIndex(1), 'sanctus.krn', Qt.EditRole)
        >>> a.data(a.createIndex(1), Qt.DisplayRole)
        'sanctus.krn'
        >>> a.data(a.createIndex(0), Qt.DisplayRole)
        'kyrie.krn'
        """
        # Set the row
        row = None
        if isinstance(index, QModelIndex):
            row = index.row()
        else:
            row = index[0]

        # Return the requested data
        if Qt.DisplayRole == role and 0 <= row < len(self._files):
            return self._files[row]
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Returns the table header data for this ListOfFiles. This is always
        "filename".
        """
        return 'filename'

    def setData(self, index, value, role):
        """
        Set the data for the given row to the given filename.

        The first argument is the index to set. The second argument is the value
        to set it to. The third argument should be QtCore.Qt.EditRole.

        The first argument could also be an int indicating the row of the cell
        you wish to modify.

        >>> a = ListOfFiles()
        >>> a.insertRows(0, 2)
        >>> a.setData(a.createIndex(0, 0), 'kyrie.krn', Qt.EditRole)
        >>> a.setData(a.createIndex(1, 0), 'sanctus.krn', Qt.EditRole)
        """
        # Set the row
        row = None
        if isinstance(index, QModelIndex):
            row = index.row()
        else:
            row = index[0]
            # we still need a QModelIndex for the dataChanged signal
            index = self.createIndex(row, 0)

        # Set the data
        if Qt.EditRole == role and 0 <= row < len(self._files):
            self._files[row] = value
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Insert a certain number of rows at a certain point in the ListOfFiles.

        The first argument is the index you want for the first row to be inserted.
        The second argument is the number of rows to insert.

        The elements already in the list, with an index lower than "row" will
        retain their index values. The elements at indices "row" and higher will
        have an index value that is their original value plus "count".

        For example:
        >>> a = ListOfFiles()
        >>> a.insertRows(0, 3)
        >>> a.setData(a.createIndex(0), 'kyrie.krn', Qt.EditRole)
        >>> a.setData(a.createIndex(1), 'sanctus.krn', Qt.EditRole)
        >>> a.setData(a.createIndex(2), 'benedictus.krn', Qt.EditRole)
        This is ['kyrie.krn', 'sanctus.krn', 'benedictus.krn']
        >>> a.insertRows(1, 2)
        This is ['kyrie.krn', '', '', 'sanctus.krn', 'benedictus.krn']
        >>> a.setData(a.createIndex(1), 'gloria.krn', Qt.EditRole)
        >>> a.setData(a.createIndex(2), 'credo.krn', Qt.EditRole)
        This is ['kyrie.krn', 'gloria.krn', 'credo.krn', 'sanctus.krn',
                'benedictus.krn']

        Append files to the end of a list:
        >>> a = ListOfFiles()
        >>> a.insertRows(0, 1)
        >>> a.setData(a.createIndex(0), 'kyrie.krn', Qt.EditRole)
        This is ['kyrie.krn']
        >>> a.insertRows(a.rowCount(), 1)
        >>> a.setData(a.createIndex(a.rowCount()+0), 'gloria.krn', Qt.EditRole)
        This is ['kyrie.krn', 'gloria.krn']
        """
        self.beginInsertRows(parent, row, row + count - 1)
        new_files = self._files[:row]
        for zed in xrange(count):
            new_files.append('')
        new_files += self._files[row:]
        self._files = new_files
        self.endInsertRows()

    def isPresent(self, candidate):
        """
        Tests whether 'candidate' is present in this ListOfFiles.

        Returns a QModelIndex that points to the filename or False.

        If the argument is already a QModelIndex, it returned if it is a valid QModelIndex for this
        ListOfFiles.
        """
        if isinstance(candidate, QModelIndex):
            # return the QModelIndex if it represents a valid index for this ListOfFiles
            if 0 == candidate.column() and 0 <= candidate.row() <= len(self._files):
                return candidate
            else:
                return False
        elif candidate in self._files:
            for index in xrange(len(self._files)):
                if candidate == self._files[index]:
                    return self.createIndex(index, 0)
        else:
            return False

    def __iter__(self):
        """
        Create an iterator that returns each of the filenames in this ListOfFiles.
        """
        for filename in self._files:
            yield filename

    def removeRows(self, row, count, parent=QModelIndex()):
        """
        This is the opposite of insertRows(), and the arguments work in the same
        way.
        """
        self.beginRemoveRows(parent, row, row + count - 1)
        self._files = self._files[:row] + self._files[row + count:]
        self.endRemoveRows()
