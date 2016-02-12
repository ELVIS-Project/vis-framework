#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/ngram.py
# Purpose:                k-part anything n-gram Indexer
#
# Copyright (C) 2013-2016 Christopher Antila, Alexander Morgan
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
.. deprecated:: 2.4.0
	This indexer is deprecated and will be replaced in version 3.0 with  what is currently 
	called the new_ngram_indexer.
Indexer to find k-part any-object n-grams.
"""

# pylint: disable=pointless-string-statement

import six
import pandas
from vis.analyzers import indexer


class NGramIndexer(indexer.Indexer):
    """
    Warning: This indexer is deprecated and will be replaced in version 3.0 with  what is currently 
    called the new_ngram_indexer.
    
    Indexer to find k-part any-object n-grams.
    Indexer that finds k-part n-grams from other indices.
    The indexer requires at least one "vertical" index, and supports "horizontal" indices that seem
    to "connect" instances in the vertical indices. Although we use "vertical" and "horizontal" to
    describe these index types, because the class is an abstraction of two-part interval n-grams,
    you can supply any information as either type of index. If you want one-part melodic n-grams
    for example, you should supply the relevant interval information as the "vertical" component.
    There is no relationship between the number of index types, though there must be at least one
    "vertical" index.
    The ``'horizontal'`` and ``'vertical'`` settings determine which columns of the ``score``
    :class:`DataFrame` are included in the n-gram output. They are added to the n-gram in the order
    specified, so if the ``'vertical'`` setting is
    ``[('noterest.NoteRestIndexer', '1'), ('noterest.NoteRestIndexer', '0')]``, this will put the
    lower part (with index ``'1'``) before the higher part (with index ``'0'``). Note that both the
    indexer's name and the part-combination name must be included.
    This is an example minimum ``settings`` dictionary for making interval 3-grams:::
        {'vertical': [('interval.IntervalIndexer', '0,1')],
         'horizontal': [('interval.HorizontalIntervalIndexer', '1')],
         'n': 3}
    IMPORTANT: the data associated with the ``'horizontal'`` settings should have been generated
    with ``'horiz_attach_later'`` set to ``True``. If not, the resulting n-grams will have their
    "horizontal" intervals incorrectly offset.
    In the output, groups of "vertical" events are normally enclosed in brackets, while groups of
    "horizontal" events are enclosed in parentheses. For cases where there is only one index in a
    particular direction, you can avoid printing the brackets or parentheses by setting the
    ``'mark singles'`` setting to ``False`` (the default is ``True``).
    If you want n-grams to terminate when finding one or several particular values, you can specify
    this with the ``'terminator'`` setting.
    To show that a horizontal event continues, we use ``'_'`` by default, but you can set this
    separately, for example to ``'P1'`` ``'0'``, as seems appropriate. Note that the default
    :class:`WorkflowManager` overrides this setting by dynamically adjusting for interval quality,
    and also offers a ``'continuer'`` setting of its own, which is passed to this indexer.
    You can also use the :class:`NGramIndexer` to collect "stacks" of single vertical events. If
    you provide indices of intervals above a lowest part, for example, these "stacks" become the
    figured bass signature of a single moment. Set ``'n'`` to ``1`` for this feature. Horizontal
    events are obviously ignored in this case.
    """

    required_score_type = 'pandas.DataFrame'

    possible_settings = ['horizontal', 'vertical', 'n', 'mark_singles', 'terminator', 'continuer', 'mp']
    """
    A list of possible settings for the :class:`NGramIndexer`.
    :keyword 'horizontal': Selectors for the parts to consider as "horizontal."
    :type 'horizontal': list of (str, str) tuples
    :keyword 'vertical': Selectors for the parts to consider as "vertical."
    :type 'vertical': list of (str, str) tuples
    :keyword 'n': The number of "vertical" events per n-gram.
    :type 'n': int
    :keyword 'mark_singles': Whether to use delimiters around a direction's events when
        there is only one event in that direction (e.g., the "horizontal" maps only the activity
        of a single voice). (You may also use ``'mark singles'``).
    :type 'mark_singles': bool
    :keyword 'terminator': Do not find an n-gram with a vertical item that contains any of these
        values.
    :type 'terminator': list of str
    :keyword 'continuer': When there is no "horizontal" event that corresponds to a vertical
        event, this is printed instead, to show that the previous "horizontal" event continues.
    :type 'continuer': str
    :keyword 'mp': Multiprocesses when True (default) or processes serially when False.
    :type 'mp': boolean
    """

    default_settings = {'mark_singles': True, 'horizontal': [], 'terminator': [], 'continuer': '_', 'mp': True}

    _MISSING_SETTINGS = 'NGramIndexer requires "vertical" and "n" settings'
    _N_VALUE_TOO_LOW = 'NGramIndexer requires an "n" value of at least 1'

    def __init__(self, score, settings=None):
        """
        :param score: The :class:`DataFrame` to use for preparing n-grams. You must ensure the
            :class:`DataFrame` has the columns indicated in the ``settings``, or the :meth:`run`
            method will fail.
        :type score: :class:`pandas.DataFrame`
        :param dict settings: Required and optional settings. See descriptions in
            :const:`possible_settings`.
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        :raises: :exc:`RuntimeError` if required settings are not present in ``settings``.
        :raises: :exc:`RuntimeError` if ``'n'`` is less than ``1``.
        """
        # Check all required settings are present in the "settings" argument.
        if settings is None or 'vertical' not in settings or 'n' not in settings:
            raise RuntimeError(NGramIndexer._MISSING_SETTINGS)
        elif settings['n'] < 1:
            raise RuntimeError(NGramIndexer._N_VALUE_TOO_LOW)
        else:
            self._settings = NGramIndexer.default_settings.copy()
            self._settings.update(settings)
        if 'mark singles' in self._settings: 
            self._settings['mark_singles'] = self._settings.pop('mark singles')
            
        super(NGramIndexer, self).__init__(score, None)

    @staticmethod
    def _format_thing(things, m_singles, markers=('[', ']'), terminator=None):
        """
        Format str objects by concatenating them with a space between and the appropriate
        grouping symbol, if relevant. This method is used by _format_vert() and _format_horiz().
        :param things: All the events for this moment.
        :type things: iterable of str
        :param m_singles: Whether to put marker characters around single-item iterables.
        :type m_singles: boolean
        :param markers: The "marker" strings to put around the output, if desired. Defualt is [].
        :type markers: 2-tuple of str
        :param terminator: If one of the events is in this iterale, raise a RuntimeError. Default
            is [None].
        :type terminator: list of str or None
        :returns: A str with a space between every event and marker characters if there is more
            than one event or m_singles is True.
        :rtype: str
        :raises: RuntimeWarning, if the one of the events is a "terminator."
        """
        terminator = [] if terminator is None else terminator
        post = []
        if len(things) > 1:
            post.append(markers[0])
            for obj in things:
                if obj in terminator:
                    raise RuntimeWarning('hit a terminator')
                else:
                    post.append('{}'.format(obj))
                    post.append(' ')
            post = post[:-1]  # remove last space
            post.append(markers[1])
        elif things[0] in terminator:
            raise RuntimeWarning('hit a terminator')
        elif m_singles:
            post.extend([markers[0], six.u(str(things[0])), markers[1]])
        else:
            post.append(things[0])
        return ''.join(post)

    @staticmethod
    def _format_vert(verts, m_singles, terminator=None):
        """
        Format "vertical" str objects by concatenating them with a space between and the
        appropriate grouping symbol, if relevant.
        :param verts: All the "vertical" events for this moment.
        :type verts: iterable of str
        :param m_singles: Whether to put marker characters around single-item iterables.
        :type m_singles: boolean
        :param terminator: If one of the events is in this iterale, raise a RuntimeError. Default
            is [None].
        :type terminator: list of str or None
        :returns: A str with a space between every event and marker characters if there is more
            than one event or m_singles is True.
        :rtype: str
        :raises: RuntimeWarning, if the one of the events is a "terminator."
        """
        return NGramIndexer._format_thing(verts, m_singles, ('[', ']'), terminator)

    @staticmethod
    def _format_horiz(horizs, m_singles, terminator=None):
        """
        Format "horizontal" str objects by concatenating them with a space between and the
        appropriate grouping symbol, if relevant.
        :param verts: All the "horizontal" events for this moment.
        :type verts: iterable of str
        :param m_singles: Whether to put marker characters around single-item iterables.
        :type m_singles: boolean
        :param terminator: If one of the events is in this iterale, raise a RuntimeError. Default
            is [None].
        :type terminator: list of str or None
        :returns: A str with a space between every event and marker characters if there is more
            than one event or m_singles is True.
        :rtype: str
        :raises: RuntimeWarning, if the one of the events is a "terminator."
        """
        return NGramIndexer._format_thing(horizs, m_singles, ('(', ')'), terminator)

    def _make_column_label(self):
        """
        Make the part-combination column label for the returned DataFrame's MultiIndex. This
        involves a rather complex coordination between the "vertical," "horizontal," and
        "mark_singles" settings.
        Refer to the automated tests for examples of what happens.
        """
        verts = ['{}'.format(x[1]) for x in self._settings['vertical']]
        if len(verts) > 1 or self._settings['mark_singles']:
            verts = '[{}]'.format(' '.join(verts))
        else:
            verts = ' '.join(verts)

        if 'horizontal' in self._settings and len(self._settings['horizontal']) > 0:
            horizs = ['{}'.format(x[1]) for x in self._settings['horizontal']]
            if len(horizs) > 1 or self._settings['mark_singles']:
                horizs = '({})'.format(' '.join(horizs))
            else:
                horizs = ' '.join(horizs)
            return ['{} {}'.format(verts, horizs)]
        else:
            return [verts]

    def run(self):
        """
        Make an index of k-part n-grams of anything.
        :returns: A single-column :class:`~pandas.DataFrame` with the new index.
        """
        # NOTE: in an incredible stroke of luck, the VIS 1 run() algorithm works without change
        #       for the VIS 2.0 release...
        # - So in a future 2.x-series point release, we can add "true" multidimensional functionality
        #   while retaining the existing 'horizontal' and 'vertical' method of naming the dimensions.
        #   In other words, we'll break the API at release 2.0 while retaining the algorithm, and
        #   add new features along with a new algorithm later, without breaking the API.

        post = []
        post_offsets = []

        # for the formatting methods
        m_singles = self._settings['mark_singles']
        term = self._settings['terminator']

        # Order the parts as specified. We have to track "i" and "name" separately so we have a new
        # order for the dict but can keep self._score straight. We'll use these tuples to keep
        # vertical and horizontal events separated in the DataFrame with a MultiIndex
        events = {}
        for i, name in enumerate(self._settings['vertical']):
            events[('v', i)] = self._score[name].dropna()
        for i, name in enumerate(self._settings['horizontal']):
            events[('h', i)] = self._score[name].dropna()

        # Make the MultiIndex and DataFrame with all events
        events = pandas.DataFrame(events, columns=pandas.MultiIndex.from_tuples(events.keys()))

        # Fill in all "vertical" NaN values with the previous value
        for i in events['v'].columns:
            # NB: still have to test the fix, as stated in issue 261
            events.update(events.loc[:, ('v', i)].fillna(method='ffill'))

        # Fill in all "horizontal" NaN values with the continuer
        if 'h' in events:
            for i in events['h'].columns:
                # NB: still have to test the fix, as stated in issue 261
                events.update(events.loc[:, ('h', i)].fillna(value=self._settings['continuer']))

        # Iterate the offsets
        for i in range(len(events)):
            loop_post = None
            try:
                # first vertical event
                loop_post = [NGramIndexer._format_vert(list(events['v'].iloc[i].sort_index()),
                                                       m_singles,
                                                       term)]
            except RuntimeWarning:  # we hit a terminator
                continue
            try:
                for j in range(self._settings['n'] - 1):  # iterate to the end of 'n'
                    k = i + j + 1  # the index we need
                    ilp = None  # it means "Inner Loop Post"
                    if 'h' in events:  # are there "horizontal" events?
                        ilp = [' ',
                               NGramIndexer._format_horiz(list(events['h'].iloc[k].sort_index()),
                                                          m_singles),
                               ' ',
                               NGramIndexer._format_vert(list(events['v'].iloc[k].sort_index()),
                                                         m_singles,
                                                         term)]
                    else:
                        ilp = [' ',
                               NGramIndexer._format_vert(list(events['v'].iloc[k].sort_index()),
                                                         m_singles,
                                                         term)]
                    loop_post.extend(ilp)
            except (KeyError, IndexError, RuntimeWarning) as the_err:
                if isinstance(the_err, (IndexError, KeyError)):  # end of inputted Series
                    break
                else:  # we hit a terminator
                    continue
            post.append(''.join(loop_post))
            post_offsets.append(events.index[i])

        # prepare the part-combination labels
        combos = self._make_column_label()
        return self.make_return(combos, [pandas.Series(post, post_offsets)])