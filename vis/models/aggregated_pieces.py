#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/aggregated_pieces.py
# Purpose:                Hold the model representing data from multiple IndexedPieces.
#
# Copyright (C) 2013, 2014, 2016 Christopher Antila, Alexander Morgan
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
#--------------------------------------------------------------------------------------------------
"""
.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. codeauthor:: Alexander Morgan
The model representing data from multiple :class:`~vis.models.indexed_piece.IndexedPiece` instances.
"""

import sys
import six
import os
import pandas
from vis.analyzers import experimenter
from vis.analyzers.experimenters import aggregator, barchart, frequency
# Only import dendrogram experiment if scipy and matplotlib have been installed.
try:
    from vis.analyzers.experimenters import dendrogram
except ImportError:
    pass
from multi_key_dict import multi_key_dict as mkd


class AggregatedPieces(object):
    """
    Hold data from multiple :class:`~vis.models.indexed_piece.IndexedPiece` instances.
    """

    # When get_data() is called but _pieces is still an empty list.
    _NO_PIECES = 'This aggregated_pieces object has no pieces assigned to it. This probably means \
that this aggregated_pieces object was instantiated incorrectly. Please refer to the documentation \
on the Importer() method in vis.models.indexed_piece.'

    # When a directory has no files in it.
    _NO_FILES = 'There are no files in the directory provided.'

    # When get_data() is missing the "settings" and/or data" argument but needed them, or was supplied .
    _SUPERFLUOUS_OR_INSUFFICIENT_ARGUMENTS = 'You made improper use of the settings and/or data \
arguments. Please refer to the {} documentation to see what it requires.'

    # When one of the "aggregated_experiments" classes in get_data() isn't an Experimenter subclass
    _NOT_EXPERIMENTER = 'The "combined_experimenter" argument of the AggregatedPieces.get_data() \
method requires an experimenter that can combine the results of multiple pieces but instead \
received {}. Please choose from one of the following: {}.'

    # When metadata() gets a 'field' argument that isn't a string
    _FIELD_STRING = "parameter 'field' must be of type 'string'"

    _UNKNOWN_INPUT = "The input type is not one of the supported options"

    class Metadata(object):
        """
        Used internally by :class:`AggregatedPieces` ... at least for now.
        Hold aggregated metadata about the IndexedPieces in an AggregatedPiece. Every list has no
        duplicate entries.
        - composers: list of all the composers in the IndexedPieces
        - dates: list of all the dates in the IndexedPieces
        - date_range: 2-tuple with the earliest and latest dates in the IndexedPieces
        - titles: list of all the titles in the IndexedPieces
        - locales: list of all the locales in the IndexedPieces
        - pathnames: list of all the pathnames in the IndexedPieces
        """
        __slots__ = ('composers', 'dates', 'date_range', 'titles', 'locales', 'pathnames')

    def __init__(self, pieces=None, metafile=None):
        """
        :param pieces: The IndexedPieces to collect.
        :type pieces: list of :class:`~vis.models.indexed_piece.IndexedPiece`
        """
        def init_metadata():
            """
            Initialize valid metadata fields with a zero-length string.
            """
            field_list = ['composers', 'dates', 'date_range', 'titles', 'locales',
                          'pathnames']
            for field in field_list:
                self._metadata[field] = None

        super(AggregatedPieces, self).__init__()
        self._pieces = pieces if pieces is not None else []
        self._metafile = metafile if metafile is not None else []
        self._metadata = {}
        init_metadata()
        # Multi-key dictionary for combined_experimenter calls to get_data()
        self._mkd = mkd({# Experimenters that can combine results from multiple pieces:
                        ('aggregator', 'aggregator.ColumnAggregator', aggregator.ColumnAggregator): aggregator.ColumnAggregator,
                        ('bar_chart', 'barchart.RBarChart', barchart.RBarChart): barchart.RBarChart,
                        ('frequency', 'frequency.FrequencyExperimenter', frequency.FrequencyExperimenter): frequency.FrequencyExperimenter})
        # Only include dendrogram experimenter if scipy and matplotlib were installed
        try:
            self._mkd[('dendrogram', 'dendrogram.HierarchicalClusterer', dendrogram.HierarchicalClusterer)] = self._get_dendrogram
        except NameError:
            pass



    @staticmethod
    def _make_date_range(dates):
        """
        Find the earliest and latest years in a list of music21 date strings.
        Each string should use one of the following two formats:
        - "----/--/--"
        - "----/--/-- to ----/--/--"
        where each - is an integer.
        :param dates: The date strings to use.
        :type dates: list of basesetring
        :returns: The earliest and latest years in the list of dates.
        :rtype: 2-tuple of string
        **Examples**
        >>> ranges = ['1987/09/09', '1865/12/08', '1993/08/08']
        >>> AggregatedPieces._make_date_range(ranges)
        ('1865', '1993')
        """
        post = []
        for poss_date in dates:
            if len(poss_date) > len('----/--/--'):
                # it's a date range, so we have "----/--/-- to ----/--/--"
                try:
                    post.append(int(poss_date[:4]))
                    post.append(int(poss_date[14:18]))
                except ValueError:
                    pass
            elif isinstance(poss_date, six.string_types):
                try:
                    post.append(int(poss_date[:4]))
                except ValueError:
                    pass
        if [] != post:
            return six.u(str(min(post))), six.u(str(max(post)))
        else:
            return None

    def _fetch_metadata(self, field):
        """
        Collect metadata from the IndexedPieces and store it in our own Metadata object.
        :param field: The metadata field to return
        :type field: str
        :returns: The requested metadata field.
        :rtype: list of str or tuple of str
        """
        post = None
        # composers: list of all the composers in the IndexedPieces
        if 'composers' == field:
            post = [p.metadata('composer') for p in self._pieces]
        # dates: list of all the dates in the IndexedPieces
        elif 'dates' == field:
            post = [p.metadata('date') for p in self._pieces]
        # date_range: 2-tuple with the earliest and latest dates in the IndexedPieces
        elif 'date_range' == field:
            post = AggregatedPieces._make_date_range([p.metadata('date') for p in self._pieces])
        # titles: list of all the titles in the IndexedPieces
        elif 'titles' == field:
            post = [p.metadata('title') for p in self._pieces]
        # locales: list of all the locales in the IndexedPieces
        elif 'locales' == field:
            post = [p.metadata('locale_of_composition') for p in self._pieces]
        elif 'pathnames' == field:
            post = [p._pathname for p in self._pieces]
        if post is not None:
            self._metadata[field] = post
        return post

    def metadata(self, field):
        """
        Get a metadatum about the IndexedPieces stored in this AggregatedPieces.
        If only some of the stored IndexedPieces have had their metadata initialized, this method
        returns incompelete metadata. Missing data will be represented as ``None`` in the list,
        but it will not appear in ``date_range`` unless there are no dates. If you need full
        metadata, we recommend running an Indexer that requires a :class:`Score` object on all the
        IndexedPieces (like :class:`vis.analyzers.indexers.noterest.NoteRestIndexer`).
        Valid fields are:
        * ``'composers``: list of all the composers in the IndexedPieces
        * ``'dates``: list of all the dates in the IndexedPieces
        * ``'date_range``: 2-tuple with the earliest and latest dates in the IndexedPieces
        * ``'titles``: list of all the titles in the IndexedPieces
        * ``'locales``: list of all the locales in the IndexedPieces
        * ``'pathnames``: list of all the pathnames in the IndexedPieces
        :param field: The name of the field to be accessed or modified.
        :type field: str
        :returns: The value of the requested field or None, if accessing a non-existant field or a
            field that has not yet been initialized in the IndexedPieces.
        :rtype: object or None
        :raises: :exc:`TypeError` if ``field`` is not a str.
        """
        if not isinstance(field, str):
            raise TypeError(AggregatedPieces._FIELD_STRING)
        elif field in self._metadata:
            if self._metadata[field] is None:
                return self._fetch_metadata(field)
            else:
                return self._metadata[field]
        else:
            return None

    def _get_dendrogram(self, data, settings=None):
        """Convenience method for plotting dendrograms. You can pass it a list of lists of pandas 
        dataframes. If there is more than one internal list, make sure to supply the ``weights`` 
        setting. See the dendrogram experimenter documentation for more details."""
        temp = []
        if isinstance(data[0][0], pandas.DataFrame):
            for i in data:
                freq = self.get_data('frequency', data=i)
                agg = self.get_data('aggregator', data=freq)
                sers = [df.iloc[:, 0] for df in agg]
                temp.append(sers)
        
        if temp:
            data = temp
        # import pdb
        # pdb.set_trace()

        return dendrogram.HierarchicalClusterer(data, settings).run()



    def get_data(self, ind_analyzer=None, combined_experimenter=None, settings=None, data=None):
        """
        Get the results of an :class:`Indexer` or an :class:`Experimenter` run on all the 
        :class:`IndexedPiece` objects either individually, or all together. If settings are 
        provided, the same settings dict will be used throughout.

        In VIS, analyzers are broken down into two categories: Indexers which associate observations 
        with a specific moment in a piece, and Experimenters which still work with musical 
        observations, but do not associate them with a specific moment in a specific IndexedPiece. 
        For example, the noterest.NoteRestIndexer associates each note and rest with a time point in 
        a given IndexedPiece, but if we then use the frequency.FrequencyExperimenter to count the 
        number of times each type of note or rest happens, these counts will not and cannot be 
        associated with a specific time point.

        All VIS Indexers and most Experimenters  run on each piece individually, and so if  these 
        results are desired, the analyzer in question should be assigned to the ``ind_analyzer`` 
        argument. The barchart.RBarChart and aggregator.ColumnAggregator experimenters often 
        combine the data of several pieces together. The frequency.FrequencyExperimenter can also 
        be used this way. If this is the desired behavior, supply the appropriate Experimenter as 
        the combined_experimenter argument.

        **Examples**

        .. note:: The analyzers in the ``analyzer_cls`` argument are run with
            :meth:`~vis.models.indexed_piece.IndexedPiece.get_data` from the :class:`IndexedPiece`
            objects themselves. Thus any exceptions raised there may also be raised here.
        Get the results of an Experimenter or Indexer run on this :class:`IndexedPiece`.

        :param ind_analyzer: The analyzer to run.
        :type ind_analyzer: str or VIS Indexer or Experimenter class.
        :param settings: Settings to be used with the analyzer. Only use if necessary.
        :type settings: dict
        :param data: Input data for the analyzer to run. If this is provided for an indexer that 
            normally caches its results (such as the NoteRestIndexer, the DurationIndexer, etc.), 
            the results will not be cached since it is uncertain if the input passed in the ``data`` 
            argument was calculated on this indexed_piece.
        :type data: Depends on the requirement of the analyzer designated by the ``analyzer_cls`` 
            argument. Usually a list of :class:`pandas.DataFrame`.
        :returns: Results of the analyzer.
        :rtype: Depending on the ``analyzer_cls``, either a :class:`pandas.DataFrame` or more often 
            a list of :class:`pandas.DataFrame`.
        :return: Either one :class:`pandas.DataFrame` with all experimental results or a list of
            :class:`DataFrame` objects, each with the experimental results for one piece.
        :raises: :exc:`TypeError` if an analyzer is invalid or cannot be found.
        """
        if not self._pieces: # if there are no pieces in this aggregated_pieces object
            raise RuntimeWarning(AggregatedPieces._NO_PIECES)

        if (combined_experimenter is not None and (combined_experimenter not in self._mkd.keys(str) 
            and combined_experimenter not in self._mkd.keys(type))): # make sure combined_experimenter is an appropriate experimenter
            raise TypeError(AggregatedPieces._NOT_EXPERIMENTER.format(combined_experimenter,
                                                                      sorted([k[0] for k in self._mkd.keys()])))

        args_dict = {} # Only pass the settings argument if it is not ``None``.
        if settings is not None:
            args_dict['settings'] = settings
        
        if ind_analyzer is not None: # for indexers or experimenters run individually on each indexed_piece in self._pieces
            if data is None:
                results = [p.get_data(ind_analyzer, **args_dict) for p in self._pieces]
            else:
                results = [p.get_data(ind_analyzer, data[i], **args_dict) for i, p in enumerate(self._pieces)]
        
        if combined_experimenter is not None: # for experimenters that combine all the results in the data argument
            if ind_analyzer is not None:
                data = results
            try:
                results = self._mkd[combined_experimenter](data, **args_dict)
                if hasattr(results, 'run'): # execute analyzer if there is no caching method for this one
                    results = results.run()
            except TypeError: # There is some issue with the 'settings' and/or 'data' arguments.
                raise RuntimeWarning(AggregatedPieces._SUPERFLUOUS_OR_INSUFFICIENT_ARGUMENTS.format(self._mkd[combined_experimenter]))

        return results
