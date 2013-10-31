#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: analyzing.py
# Purpose: Model classes for the PyQt4 GUInterface to the VIS contrapuntal analysis application.
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
Model classes for the PyQt4 GUInterface to the VIS contrapuntal analysis application. This includes
:class:`ListOfPathnames` for a list of pathnames that have not been imported to a
:class:`~vis.workflow.WorkflowManager`, and :class:`WorkflowWrapper`, which is a wrapper to allow
a :class:`WorkflowManager` instance to be a :class:`QAbstractTableModel`.
"""

from PyQt4.QtCore import QAbstractTableModel, QAbstractListModel, QModelIndex, Qt, QVariant
from vis.workflow import WorkflowManager


class WorkflowWrapper(QAbstractTableModel):
    """
    This is a wrapper class for the :class:`vis.workflow.WorkflowManager` that allows its use as a
    :class:`QAbstractTableModel` for PyQt4. This class only wraps :meth:`metadata` and
    :meth:`setting`, which are those methods needed by PyQt. For all other :class:`Workflowmanager`
    methods, access the internally-stored instance with :meth:`get_workflow_manager`.

    ** How to Use the WorkflowWrapper: **

    The :class:`WorkflowWrapper` always returns valid values, and will not raise exceptions of its
    own. However, "valid" values are not always "correct" or "expected." We recommend you use the
    :class:`WorkflowWrapper` like this:

    #. Instantiate the object.
    #. Set the object as the model for its view.
    #. Call :meth:`insertRows` with the total number of pieces to be added.
    #. Call :meth:`setData` once per piece to set the pathname.
    #. Once each row has a pathname, the object will instantiate its internal
        :class:`WorkflowManager` instance and call its :meth:`load` method to import the score,
        run the :class:`NoteRestIndexer`, and save its metadata.
    #. Subsequent calls to :meth:`data` will return the most correct information available.

    ** How not to Use the WorkflowWrapper: **

    We recommend you do not use the :class:`WorkflowWrapper` like this:

    * Do not add pieces by calling :meth:`insertRows` then :meth:`setData` with the pathname, then
        :meth:`insertRows` then :meth:`setData` with the pathname, and so on. In this case, the
        :class:`WorkflowWrapper` would create a new :class:`WorkflowManager` after each call to
        :meth:`setData`, which would import each piece many times.
    * Do not add pieces after you modify a metadata or setting field. When you add a piece, a new
        :class:`WorkflowManager` instance is created. The new instance replaces any customized
        settings and metadata with the default values.
    * Do not call :meth:`data` before you add the pathnames of all pieces. Real metadata is only
        available after the :class:`WorkflowManager` is created, which happens after all the pieces
        have a pathname. If you call :meth:`data` when there is no :class:`WorkflowManager`, the
        return value will always be ``None``.

    ** Columns in the Data Model: **

    The :class:`WorkflowWrapper` creates a two-dimensional data model, where each row represents an
    :class:`IndexedPiece` stored in the :class:`WorkflowManager` and each column represents either
    a setting or a metadatum field. The following six fields are different for each piece, and
    should be displayed in the :class:`QTableView` widget:

    * filename
    * title
    * parts_list
    * offset_interval
    * parts_combinations
    * repeat_identical

    The :class:`WorkflowManager` additionally wraps these data fields, which are shared by all
    pieces, and will therefore not apear in the :class:`QTableView` widget:

    * quality
    * simple_ints

    Use class properties with those names to specify columns to :meth:`data` and :meth:`getData`.
    For example:

    >>> workm.data((0, WorkflowWrapper.title), Qt.DisplayRole)
    u'02_eleva'
    >>> workm.setData((0, WorkflowWrapper.title), u'Elevator Love Letter', Qt.EditRole)
    >>> workm.data((0, WorkflowWrapper.parts_list), Qt.DisplayRole)
    [u'Amy Milan', u'Torquil Campbell', u'Evan Cranley', u'Chris Seligman', u'Pat McGee']
    """

    # Public class variables to track which column has which data
    # NOTE: Update _num_cols whenever you change the number of columns,
    #       since this variable is used by columnCount().
    # NOTE: Update _header_names whenever you change the number or definition of
    #       columns, since this variale is used by headerData().
    _num_cols = 6
    _header_names = ['Path', 'Title', 'List of Part Names', 'Offset Interval',
                    'Part Combinations', 'Repeat Identical']
    # displayed fields
    filename = 0
    title = 1
    parts_list = 2
    offset_interval = 3
    parts_combinations = 4
    repeat_identical = 5

    # non-displayed fields
    quality = 100
    simple_ints = 101

    # instead of DisplayRole; used to tell data() to return the list of part names as a list
    ListRole = 4000

    # when a value hasn't been set, return a QVariant with this in it
    default_value = u'(unset)'

    def __init__(self, parent=QModelIndex()):
        """
        Create a new :class:`WorkflowWrapper` instance.
        """
        super(WorkflowWrapper, self).__init__()
        self._pathnames = []  # hold a list of pathnames for before the WorkflowManager
        self._workm = None  # hold the WorkflowManager
        self._settings_changed = False  # whether setData() was called (for settings_changed())

    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of pieces in this list. If the internal :class:`WorkflowManager` exists,
        this is the number of piece stored there; otherwise it is the number of places for
        pathnames.

        :returns: The number of pieces in this list.
        :rtype: ``int``
        """
        if self._workm is None:
            return len(self._pathnames)
        else:
            return len(self._workm)

    def columnCount(self, parent=QModelIndex()):
        "Return the number of columns in this WorkflowWrapper."
        return WorkflowWrapper._num_cols

    def data(self, index, role):
        """
        Get the data for the piece and metadatum or setting specified. Only the "parts_list" column
        responds to the WorkflowWrapper.ListRole, in which case a list of strings is returned
        instead of a comma-separated list of part names.

        :param index: The row-and-column index you wish to access. Either you can use a
            :class:`QModelIndex` or a 2-tuple where the first element is an ``int`` representing the
            index of the piece in the models, and the second element is one of the class properties
            described above in "Columns in the Data Model."
        :type index: :class:`QModelIndex` or 2-tuple of ``int``

        :param role: Either Qt.DisplayRole or WorkflowWrapper.ListRole
        :type role: ``int``

        :returns: The requested data or, if ``index`` or ``role`` is invalid, ``None``.
        :rtype: :class:`QVariant`

        .. note:: The method always returns a :class:`QVariant`. Access the Python object with the
            :meth:`toPyObject` method.

        .. note:: If the internal :class:`WorkflowManager` has not been instantiated, the return
            value is always ``None``.

        .. note:: This method never actually returns ``None``, but rather an empty :class:`QVariant`
            that will be ``None`` when you call :meth:`toPyObject` on it.
        """
        if self._workm is None or (Qt.DisplayRole != role and WorkflowWrapper.ListRole != role):
            return QVariant()

        # Set the row and column
        row = None
        column = None
        if isinstance(index, QModelIndex):
            # if the QModelIndex is invalid, we won't bother with it
            if not index.isValid():
                return QVariant()
            # otherwise, get the row and column from the QModelIndex
            row = index.row()
            column = index.column()
        else:
            row = index[0]
            column = index[1]

        # Verify the row and column
        if row >= self.rowCount() or column >= self._num_cols and \
        (column != WorkflowWrapper.quality and column != WorkflowWrapper.simple_ints):
            return QVariant()

        post = None
        if Qt.DisplayRole == role:
            # displayed fields
            if WorkflowWrapper.filename == column:
                post = self._workm.metadata(row, u'pathname')
            elif WorkflowWrapper.title == column:
                post = self._workm.metadata(row, u'title')
            elif WorkflowWrapper.parts_list == column:
                post = u', '.join(self._workm.metadata(row, u'parts'))
            elif WorkflowWrapper.offset_interval == column:
                post = self._workm.settings(row, u'offset interval')
            elif WorkflowWrapper.parts_combinations == column:
                post = self._workm.settings(row, u'voice combinations')
            elif WorkflowWrapper.repeat_identical == column:
                # the wording in the GUI and WorkflowManager has opposite meanings
                post = not self._workm.settings(row, u'filter repeats')
            # non-displayed fields
            elif WorkflowWrapper.quality == column:
                post = self._workm.settings(None, u'interval quality')
            elif WorkflowWrapper.simple_ints == column:
                post = self._workm.settings(None, u'simple intervals')
            else:
                post = QVariant()
        elif WorkflowWrapper.ListRole == role:
            if WorkflowWrapper.parts_list == column:
                post = self._workm.metadata(row, u'parts')
            else:
                post = QVariant()
        else:
            post = QVariant()

        if not isinstance(post, QVariant):
            if post is None:
                post = WorkflowWrapper.default_value
            post = QVariant(post)
        return post

    def headerData(self, section, orientation, role):
        """
        Return the column names for a WorkflowWrapper instance.

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
        0 <= section < WorkflowWrapper._num_cols:
            return WorkflowWrapper._header_names[section]
        else:
            return QVariant()

    def setData(self, index, value, role):
        """
        Set the data for the piece and metadatum or setting specified. If the internal
            :class:`WorkflowManager` has not yet been created and this is the last pathname added,
            instantiate the :class:`WorkflowManager` and call :meth:`load`.

        :param index: The row-and-column index you wish to access. Either you can use a
            :class:`QModelIndex` or a 2-tuple where the first element is an ``int`` representing the
            index of the piece in the models, and the second element is one of the class properties
            described above in "Columns in the Data Model."
        :type index: :class:`QModelIndex` or 2-tuple of ``int``

        :param value: The desired value of the setting or metadatum. If you submit a
            :class:`QVariant`, we will call :meth:`toPyObject` before sending to the
            :class:`WorkflowManager`.
        :type value: :class:`QVariant` or any

        :param role: This should be Qt.EditRole.
        :type role: :class:`EditRole`

        :returns: Whether the data was successfully set.
        :rtype: ``True`` or ``False``

        .. note:: If the internal :class:`WorkflowManager` has not been instantiated, you can only
            set the ``pathname`` field. All other calls to :meth:`setData` will fail.
        """

        if Qt.EditRole != role:
            return False

        # Set the row and column
        row = None
        column = None
        if isinstance(index, QModelIndex):
            # if the QModelIndex is invalid, we won't bother with it
            if not index.isValid():
                return False
            # otherwise, get the row and column from the QModelIndex
            row = index.row()
            column = index.column()
        else:
            row = index[0]
            column = index[1]
            index = self.createIndex(row, column)

        # Verify the row and column
        if row >= self.rowCount() or column >= self._num_cols and \
        (column != WorkflowWrapper.quality and column != WorkflowWrapper.simple_ints):
            return False

        set_val = value.toPyObject() if isinstance(value, QVariant) else value

        # ensure we're trying to set a valid thing
        if self._workm is None:
            if WorkflowWrapper.filename != column:
                return False
            else:
                self._pathnames[row] = set_val
                ch_ind_1, ch_ind_2 = None, None
                if all(self._pathnames):
                    self._workm = WorkflowManager(self._pathnames)
                    self._workm.load(u'pieces')
                    # now that we imported, all the data's changed
                    ch_ind_1 = self.createIndex(0, 0)
                    ch_ind_2 = self.createIndex(len(self), self._num_cols - 1)
                else:
                    # only one cell has changed
                    ch_ind_1 = ch_ind_2 = self.createIndex(row, column)
                self.dataChanged.emit(ch_ind_1, ch_ind_2)
                return True

        # displayed fields
        if WorkflowWrapper.filename == column:
            self._workm.metadata(row, u'pathname', set_val)
        elif WorkflowWrapper.title == column:
            self._workm.metadata(row, u'title', set_val)
        elif WorkflowWrapper.parts_list == column:
            self._workm.metadata(row, u'parts', set_val)
        elif WorkflowWrapper.offset_interval == column:
            self._workm.settings(row, u'offset interval', set_val)
        elif WorkflowWrapper.parts_combinations == column:
            self._workm.settings(row, u'voice combinations', set_val)
        elif WorkflowWrapper.repeat_identical == column:
            # the wording in the GUI and WorkflowManager has opposite meanings
            self._workm.settings(row, u'filter repeats', not set_val)
        # non-displayed fields
        elif WorkflowWrapper.quality == column:
            self._workm.settings(None, u'interval quality', set_val)
        elif WorkflowWrapper.simple_ints == column:
            self._workm.settings(None, u'simple intervals', set_val)
        else:
            return False
        self._settings_changed = True
        self.dataChanged.emit(index, index)
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Append new rows to the data model. Yes---append, not insert.

        :param row: An argument that will be ignored.
        :type row: any
        :param count: The number of rows you want to append.
        :type count: ``int``

        .. note:: If the internal :class:`WorkflowManager` already exists, it is destroyed and all
            metadata and settings are lost.

        .. note:: We recommend you add all the rows you will need before you call :meth:`setData`
            to set the pathnames of the newly-added rows.
        """
        if self._workm is not None:
            self._workm = None
        self.beginInsertRows(parent, len(self._pathnames), len(self._pathnames) + count - 1)
        self._pathnames.extend([None for _ in xrange(count)])
        self.endInsertRows()

    def removeRows(self, row, count, parent=QModelIndex()):
        """
        This is the opposite of insertRows(), and the arguments work in the same
        way.
        """
        pass

    def __len__(self):
        "Alias for rowCount()."
        return self.rowCount()

    def __getitem__(self, index):
        "It's __getitem__(), what do you want?!"
        return self._workm[index]

    def get_workflow_manager(self):
        """
        Get the internal :class:`WorkflowManager` instance.
        """
        return self._workm

    def settings_changed(self):
        """
        Know whether there has been a call to :meth:`setData` since the last time this method was
        called.
        """
        ret = self._settings_changed
        self._settings_changed = False
        return ret


class ListOfFiles(QAbstractListModel):
    """
    Hold a list of pathnames.
    """

    def __init__(self, parent=None, *args):
        """
        Create a new :class:`ListOfFiles`.
        """
        super(ListOfFiles, self).__init__()  # required for QModelIndex
        self._files = []  # store a list of IndexedPiece

    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of files in the list.

        :returns: The number of files in the list.
        :rtype: ``int``
        """
        return len(self._files)

    def data(self, index, role):
        """
        Get the filename with the specified index as a :class:`QVariant`.

        :parameter index: Index of the filename to return.
        :type index: ``int`` or :class:`QModelIndex`
        :parameter role: The role (a PyQt formality).
        :type role: :class:`PyQt4.QtCore.Qt.DisplayRole`

        :returns: The filename at the requested index.
        :rtype: :class:`QVariant` with ``basestring``

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
            return QVariant(self._files[row])
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Get the table header data for this ``ListOfFiles``. This is always ``u'filename'``.

        :returns: The string "filename"
        :rtype: ``unicode``
        """
        return u'filename'

    def setData(self, index, value, role):
        """
        Set the filename in a row.

        :parameter index: Index of the filename to set.
        :type index: ``int`` or :class:`QModelIndex`
        :parameter value: The filename to set.
        :type value: ``basestring``
        :parameter role: The role (a PyQt formality).
        :type role: :class:`PyQt4.QtCore.Qt.EditRole`

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
            row = index
            # we still need a QModelIndex for the dataChanged signal
            index = self.createIndex(row, 0)

        # Set the data
        if Qt.EditRole == role and 0 <= row < len(self._files):
            self._files[row] = unicode(value)
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Insert a specific number of rows at a specific point in the ``ListOfFiles``.

        :parameter row: Index of the first new row to be inserted.
        :type index: :class:`QModelIndex`
        :parameter count: The number of rows to insert.
        :type count: ``int``

        The elements already in the list that have an index lower than ``row`` will keep the same
        index values. The elements at indices ``row`` and higher will have an index value that is
        their original value plus ``count``.

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
        for _ in xrange(count):
            new_files.append(u'')
        new_files += self._files[row:]
        self._files = new_files
        self.endInsertRows()

    def isPresent(self, candidate):
        """
        Tests whether a pathname was already added to this ``ListOfFiles``.

        :parameter candidate: The pathname you want to know about.
        :type candidate: ``basestring`` or :class:`QModelIndex`

        :returns: An index that points to the filename or ``False``.
        :rtype: :class:`QModelIndex` or ``boolean``
        """
        if isinstance(candidate, QModelIndex):
            # return the QModelIndex if it represents a valid index for this ListOfFiles
            if 0 == candidate.column() and 0 <= candidate.row() <= len(self._files):
                return candidate
            else:
                return False
        else:
            for ipiece in self._files:
                if candidate == ipiece.metadata(u'pathname'):
                    return True
            return False

    def __iter__(self):
        """
        Return a generator that returns the pathnames held in this ``ListOfFiles``.

        :returns: One of the pathnames.
        :rtype: ``basestring``
        """
        for filename in self._files:
            yield filename

    def removeRows(self, row, count, parent=QModelIndex()):
        """
        The opposite of :meth:`insertRows`.

        :parameter row: Index of the first row to be removed.
        :type index: :class:`QModelIndex`
        :parameter count: The number of rows to remove.
        :type count: ``int``
        """
        self.beginRemoveRows(parent, row, row + count - 1)
        self._files = self._files[:row] + self._files[row + count:]
        self.endRemoveRows()
