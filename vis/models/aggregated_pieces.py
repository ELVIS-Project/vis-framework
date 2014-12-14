#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/aggregated_pieces.py
# Purpose:                Hold the model representing data from multiple IndexedPieces.
#
# Copyright (C) 2013, 2014 Christopher Antila
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

The model representing data from multiple :class:`~vis.models.indexed_piece.IndexedPiece` instances.
"""

import six
import pandas
from vis.analyzers import experimenter


class AggregatedPieces(object):
    """
    Hold data from multiple :class:`~vis.models.indexed_piece.IndexedPiece` instances.
    """

    # When one of the "aggregated_experiments" classes in get_data() isn't an Experimenter subclass
    _NOT_EXPERIMENTER = 'AggregatedPieces requires Experimenters (received {})'

    # When metadata() gets a 'field' argument that isn't a string
    _FIELD_STRING = "parameter 'field' must be of type 'string'"

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

    def __init__(self, pieces=None):
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
        self._metadata = {}
        init_metadata()
        # set our "pathnames" metadata
        self._metadata['pathnames'] = [p.metadata('pathname') for p in self._pieces]

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

    def get_data(self, independent_analyzers, aggregated_experiments, settings=None, data=None):
        """
        Get the results of an :class:`Experimenter` run on all the :class:`IndexedPiece` objects.
        You must specify all indexers and experimenters to be run to get the results you want.

        The same settings dict will be given to all experiments and indexers.

        If you want the results from all :class:`IndexedPiece` objects separately, provide an empty
        list as the ``aggregated_experiments`` argument.

        Either the first analyzer in ``independent_analyzers`` should use a
        :class:`music21.stream.Score` or you must provide an argument for ``data`` that is the
        output from a previous call to this instance's :meth:`get_data` method.

        **Examples**

        Run analyzer A then B on each piece individually, then provide a list of those results to
        Experimenter C then D:::

            >>> pieces.get_data([A, B], [C, D])

        Run analyzer A then B on each piece individually, then return a list of those results:::

            >>> pieces.get_data([A, B])

        Run experimenter A then B on the results of a previous :meth:`get_data` call:::

            >>> piece.get_data([], [C, D], data=previous_results)

        .. note:: The analyzers in the ``independent_analyzers`` argument are run with
            :meth:`~vis.models.indexed_piece.IndexedPiece.get_data` from the :class:`IndexedPiece`
            objects themselves. Thus any exceptions raised there may also be raised here.

        :param independent_analyzers: The analyzers to run on each piece before aggregation, in the
            order you want to run them. For no independent analyzers, use ``[]`` or ``None``.
        :type independent_analyzers: list of types
        :param aggregated_experiments: The Experimenters to run on aggregated data of all pieces,
            in the order you want to run them.
        :type aggregated_experiments: list of types
        :param dict settings: Settings to be used with the analyzers.
        :param data: Input data for the first analyzer to run. If this argument is not ``None``,
            you must provide the output from a previous call to :meth:`get_data` of this instance.
        :type data: :class:`pandas.DataFrame` or list of :class:`DataFrame`

        :return: Either one :class:`pandas.DataFrame` with all experimental results or a list of
            :class:`DataFrame` objects, each with the experimental results for one piece.

        :raises: :exc:`TypeError` if an analyzer is invalid or cannot be found.
        """
        if [] == self._pieces:
            return [pandas.DataFrame()] if [] == aggregated_experiments else pandas.DataFrame()
        if aggregated_experiments is not None and len(aggregated_experiments) > 0:
            for each_cls in aggregated_experiments:
                if not issubclass(each_cls, experimenter.Experimenter):
                    raise TypeError(AggregatedPieces._NOT_EXPERIMENTER.format(each_cls))
        if independent_analyzers is not None and len(independent_analyzers) > 0:
            ind_res = None
            if data is not None:
                ind_res = [p.get_data(independent_analyzers, settings, data[i])
                           for i, p in enumerate(self._pieces)]
            else:
                ind_res = [p.get_data(independent_analyzers, settings) for p in self._pieces]
            return self.get_data(None, aggregated_experiments, settings, ind_res)
        elif aggregated_experiments is None or 0 == len(aggregated_experiments):
            return data
        elif 1 == len(aggregated_experiments):
            return aggregated_experiments[0](data, settings).run()
        else:
            return self.get_data(independent_analyzers,
                                 aggregated_experiments[1:],
                                 settings,
                                 aggregated_experiments[0](data, settings).run())
