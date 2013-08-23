#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/aggregated_pieces.py
# Purpose:                Hold the model representing data from multiple IndexedPieces.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
The model representing data from multiple IndexedPieces.
"""


class AggregatedPieces(object):
    """
    Holds data from multiple IndexedPieces.
    """

    class Metadata(object):
        """
        Hold aggregated metadata about the IndexedPieces in an AggregatedPiece. Every list has no
        duplicate entries.

        - composers: list of all the composers in the IndexedPieces
        - dates: list of all the dates in the IndexedPieces
        - date_range: 2-tuple with the earliest and latest dates in the IndexedPieces
        - titles: list of all the titles in the IndexedPieces
        - locales: list of all the locales in the IndexedPieces
        - pathnames: list of all the pathnames in the IndexedPieces
        """
        __slots__ = (u'composers', u'dates', u'date_range', u'titles', u'locales', u'pathnames')

    # About the Data Model (for self._data)
    # =====================================
    # - ?

    # TODO: how to know which pieces are stored here?

    def __init__(self, pieces):
        """
        Instantiate an AggregatedPieces.

        Parameters
        ==========
        :param pieces: The IndexedPieces to collect.
        :type pieces: list of IndexedPiece
        """
        super(AggregatedPieces, self).__init__()
        self._pieces = pieces
        self._metadata = AggregatedPieces.Metadata()

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

    def metadata(self, field):
        """
        Get a metadata about the IndexedPieces stored in this AggregatedPieces.

        Valid fields are:
        - composers: list of all the composers in the IndexedPieces
        - dates: list of all the dates in the IndexedPieces
        - date_range: 2-tuple with the earliest and latest dates in the IndexedPieces
        - titles: list of all the titles in the IndexedPieces
        - locales: list of all the locales in the IndexedPieces
        - pathnames: list of all the pathnames in the IndexedPieces

        Parameters
        ==========
        :param field: The name of the field to be accessed or modified
        :type field: str or unicode

        Returns
        =======
        :returns: object -- the field accessed, or None -- if assigning a field or attempting to
            access a field that does not exist.

        Raises
        ======
        :raises: TypeError -- if ``field`` is not a basestring, AttributeError -- if attempting
            to set a field which is not in the :py:class:`IndexedPiece.Metadata` prototype.
        """
        if not isinstance(field, basestring):
            raise TypeError(u"parameter 'field' must be of type 'basestring'")
        elif hasattr(self._metadata, field):
            return getattr(self._metadata, field)
        else:
            return None

    def get_data(self, aggregated_experiments, independent_analyzers, settings=None):
        """
        Get the results of an Experimenter run on all the IndexedPieces. You must specify all
        indexers and experimenters to be run to get the results you want.

        The same settings dict will be given to all experiments and indexers.

        If you want the results from all IndexedPieces separately, provide an empty list as the
        "aggregated_experiments" argument.

        Parameters
        ==========
        :param aggregated_experiments: The Experimenters to run on aggregated data of all pieces,
            in the order you want to run them.
        :type aggregated_experiments: list of types

        :param independent_analyzers: The analyzers to run on each piece before aggregation, in the
            order you want to run them.
        :type independent_analyzers: list of types

        :param settings: the settings to be used with all analyzers
        :type settings: dict

        Returns
        =======
        :return: Either one DataFrame with all experimental results or a list of DataFrames, each
            with the experimental results for one piece.
        :rtype: pandas.DataFrame or list of pandas.DataFrame

        Raises
        ======
        TypeError: If the "analyzer_cls" is invalid or cannot be found.
        """
        pass
