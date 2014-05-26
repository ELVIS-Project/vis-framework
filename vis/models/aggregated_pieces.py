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
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>

The model representing data from multiple :class:`~vis.models.indexed_piece.IndexedPiece` instances.
"""

import pandas
from vis.analyzers import experimenter


class AggregatedPieces(object):
    """
    Hold data from multiple :class:`~vis.models.indexed_piece.IndexedPiece` instances.
    """

    # pylint: disable=R0903
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
        __slots__ = (u'composers', u'dates', u'date_range', u'titles', u'locales', u'pathnames')

    def __init__(self, pieces=None):
        """
        :param pieces: The IndexedPieces to collect.
        :type pieces: list of :class:`~vis.models.indexed_piece.IndexedPiece`
        """
        def init_metadata():
            """
            Initialize valid metadata fields with a zero-length unicode.
            """
            field_list = [u'composers', u'dates', u'date_range', u'titles', u'locales',
                          u'pathnames']
            for field in field_list:
                self._metadata[field] = None

        super(AggregatedPieces, self).__init__()
        self._pieces = pieces if pieces is not None else []
        self._metadata = {}
        init_metadata()
        # set our "pathnames" metadata
        self._metadata[u'pathnames'] = [p.metadata(u'pathname') for p in self._pieces]

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
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
        :rtype: 2-tuple of unicode

        **Examples**
        >>> ranges = [u'1987/09/09', u'1865/12/08', u'1993/08/08']
        >>> AggregatedPieces._make_date_range(ranges)
        (u'1865', u'1993')
        """
        post = []
        for poss_date in dates:
            if len(poss_date) > len(u'----/--/--'):
                # it's a date range, so we have "----/--/-- to ----/--/--"
                try:
                    post.append(int(poss_date[:4]))
                    post.append(int(poss_date[14:18]))
                except ValueError:
                    pass
            elif isinstance(poss_date, basestring):
                try:
                    post.append(int(poss_date[:4]))
                except ValueError:
                    pass
        if [] != post:
            return unicode(min(post)), unicode(max(post))
        else:
            return None

    def _fetch_metadata(self, field):
        """
        Collect metadata from the IndexedPieces and store it in our own Metadata object.

        :param field: The metadata field to return
        :type field: basestring

        :returns: The requested metadata field.
        :rtype: list of basestring or tuple of basestring
        """
        post = None
        # composers: list of all the composers in the IndexedPieces
        if u'composers' == field:
            post = [p.metadata(u'composer') for p in self._pieces]
        # dates: list of all the dates in the IndexedPieces
        elif u'dates' == field:
            post = [p.metadata(u'date') for p in self._pieces]
        # date_range: 2-tuple with the earliest and latest dates in the IndexedPieces
        elif u'date_range' == field:
            post = AggregatedPieces._make_date_range([p.metadata(u'date') for p in self._pieces])
        # titles: list of all the titles in the IndexedPieces
        elif u'titles' == field:
            post = [p.metadata(u'title') for p in self._pieces]
        # locales: list of all the locales in the IndexedPieces
        elif u'locales' == field:
            post = [p.metadata(u'locale_of_composition') for p in self._pieces]

        if post is not None:
            self._metadata[field] = post
        return post

    def metadata(self, field):
        """
        Get a metadatum about the IndexedPieces stored in this AggregatedPieces.

        If only some of the stored IndexedPieces have had their metadata initialized, this method
        returns incompelete metadata. Missing data will be represented as :obj:`None` in the list,
        but it will not appear in ``date_range`` unless there are no dates. If you need full
        metadata, we recommend running an Indexer that requires a :class:`Score` object on all the
        IndexedPieces (like :class:`vis.analyzers.indexers.noterest.NoteRestIndexer`).

        Valid fields are:

        * ``u'composers``: list of all the composers in the IndexedPieces
        * ``u'dates``: list of all the dates in the IndexedPieces
        * ``u'date_range``: 2-tuple with the earliest and latest dates in the IndexedPieces
        * ``u'titles``: list of all the titles in the IndexedPieces
        * ``u'locales``: list of all the locales in the IndexedPieces
        * ``u'pathnames``: list of all the pathnames in the IndexedPieces

        :param field: The name of the field to be accessed or modified.
        :type field: :obj:`basestring`

        :returns: The value of the requested field or None, if accessing a non-existant field or a
            field that has not yet been initialized in the IndexedPieces.
        :rtype: object or None

        :raises: :exc:`TypeError` if ``field`` is not a basestring.
        """
        if not isinstance(field, basestring):
            raise TypeError(u"parameter 'field' must be of type 'basestring'")
        elif field in self._metadata:
            if self._metadata[field] is None:
                return self._fetch_metadata(field)
            else:
                return self._metadata[field]
        else:
            return None

    def get_data(self, aggregated_experiments, independent_analyzers, settings=None, data=None):
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

        Run analyzer C then D on each piece individually, then provide a list of those results to
        Experimenter A then B.

        >>> pieces.get_data([A, B], [C, D])

        Run analyzer C then D on each piece individually, then return a list of those results.

        >>> pieces.get_data([], [C, D])

        Run analyzer A then B on the results of a previous :meth:`get_data` call.

        >>> piece.get_data([A, B], [], data=previous_results)

        :param aggregated_experiments: The Experimenters to run on aggregated data of all pieces,
            in the order you want to run them.
        :type aggregated_experiments: list of types
        :param independent_analyzers: The analyzers to run on each piece before aggregation, in the
            order you want to run them. For no independent analyzers, use ``[]`` or ``None``.
        :type independent_analyzers: list of types
        :param settings: Settings to be used with the analyzers.
        :type settings: dict
        :param data: Input data for the first analyzer to run. If this argument is not ``None``,
            you must provide the output from a previous call to :meth:`get_data` of this instance.
        :type data: list of :class:`pandas.Series` or :class:`pandas.DataFrame`

        :return: Either one :class:`DataFrame` with all experimental results or a list of
            :class:`DataFrame` objects, each with the experimental results for one piece.
        :rtype: :class:`pandas.DataFrame` or list of :class:`pandas.Series` or \
            :class:`pandas.DataFrame`

        :raises: :exc:`TypeError` if the ``analyzer_cls`` is invalid or cannot be found.
        """
        if [] == self._pieces:
            return [pandas.DataFrame()] if [] == aggregated_experiments else pandas.DataFrame()
        for each_cls in aggregated_experiments:
            if not issubclass(each_cls, experimenter.Experimenter):
                msg = u'AggregatedPieces requires Experimenters (received {})'.format(each_cls)
                raise TypeError(msg)
        if independent_analyzers is not None and len(independent_analyzers) > 0:
            ind_res = None
            if data is not None:
                ind_res = [p.get_data(independent_analyzers, settings, data[i]) \
                           for i, p in enumerate(self._pieces)]
            else:
                ind_res = [p.get_data(independent_analyzers, settings) for p in self._pieces]
            return self.get_data(aggregated_experiments, None, settings, ind_res)
        elif [] == aggregated_experiments:
            return data
        elif 1 == len(aggregated_experiments):
            return aggregated_experiments[0](data, settings).run()
        else:
            return self.get_data(aggregated_experiments[1:],
                                 independent_analyzers,
                                 settings,
                                 aggregated_experiments[0](data, settings).run())
