#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/ngram.py
# Purpose:                k-part anything n-gram Indexer
#
# Copyright (C) 2013, 2014 Christopher Antila, Alexander Morgan
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

Indexer to find k-part any-object n-grams.
"""

# Turn off "string statement has no effect" warning; the strings are for Sphinx!
# pylint: disable=W0105

import pandas
from vis.analyzers import indexer


class NGramIndexer(indexer.Indexer):
    """
    Indexer that finds k-part n-grams from other indices.

    The indexer requires at least one "vertical" index, and supports "horizontal" indices that seem
    to "connect" instances in the vertical indices. Although we use "vertical" and "horizontal" to
    describe these index types, because the class is an abstraction of two-part interval n-grams,
    you can supply any information as either type of index. If you want one-part melodic n-grams
    for example, you should supply the relevant interval information as the "vertical" component.

    There is no relationship between the number of index types, though there must be at least one
    "vertical" index.

    The settings given to :meth:`__init__` specify which index values in ``score`` are
    horizontal or vertical intervals. They will be added in the n-gram in the order specified, so
    if the ``u'vertical'`` setting is ``[4, 1, 3]`` for lists of intervals, then for each\
    vertical event, objects will be listed in that order.

    In the output, groups of "vertical" events are enclosed in brackets, while groups of
    "horizontal" events are enclosed in parentheses.

    For cases where there is only one index in a particular direction, you can avoid printing the
    brackets or parentheses by setting the ``u'mark singles'`` setting to False (though the
    default is ``True``).

    If you want n-grams to terminate when finding one or several particular values, you can specify
    this with the ``u'terminator'`` setting.

    To show that a horizontal event continues, we use ``u'_'`` by default, but you can set this
    separately, for example to ``u'P1'`` ``u'0'``, as seems appropriate. Note that the default
    :class:`WorkflowManager` is set to override this setting by dynamically adjusting to whether
    interval quality is set to True or False or if the user chooses to pass a custom string for
    this setting.

    You can also use the :class:`NGramIndexer` to collect "stacks" of single vertical events. If
    you provide indices of intervals above a lowest part, for example, these "stacks" become the
    figured bass signature of a single moment. Set :obj:`u'n'` to 1 for this feature. Horizontal
    events are obviously ignored.
    """

    required_score_type = pandas.Series
    "The :class:`NGramIndexer` requires :class:`pandas.Series` as input."

    possible_settings = [u'horizontal', u'vertical', u'n', u'mark_singles', u'terminator',
                         u'continuer']
    """
    A list of possible settings for the :class:`NGramIndexer`.

    :keyword u'horizontal': The parts to consider as "horizontal."
    :type u'horizontal': ``list`` of ``int``
    :keyword u'vertical': The parts to consider as "vertical."
    :type u'vertical': ``list`` of ``int``
    :keyword u'n': The number of "vertical" events per n-gram.
    :type u'n': ``int``
    :keyword u'mark_singles': Whether to use delimiters around a direction's events when
        there is only one event in that direction (e.g., the "horizontal" maps only the activity
        of a single voice). (You may also use ``u'mark singles'``).
    :type u'mark_singles': ``bool``
    :keyword u'terminator': Do not find an n-gram with a vertical item that contains any of these
        values.
    :type u'terminator': ``list`` of ``basestring``
    :keyword u'continuer': When there is no "horizontal" event that corresponds to a vertical
        event, this is printed instead, to show that the previous "horizontal" event continues.
    :type u'continuer': ``basestring``
    """

    default_settings = {u'mark_singles': True, u'horizontal': [], u'terminator': [],
                        u'continuer': u'_'}
    "A :obj:`dict` of default settings for the :class:`NGramIndexer`."

    def __init__(self, score, settings=None):
        """
        :param score: A list of the "horizontal" and "vertical" indices to use for n-grams. You \
            can put the "horizontal" and "vertical" indices anywhere in the list, so long as you \
            use settings to specify the order.
        :type score: ``list`` of :class:`pandas.Series`
        :param settings: Required and optional settings. See descriptions in \
            :const:`possible_settings`.
        :type settings: ``dict``

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        :raises: :exc:`RuntimeError` if required settings are not present in ``settings``.
        :raises: :exc:`RuntimeError` if ``u'n'`` is less than ``1``.
        """
        # Check all required settings are present in the "settings" argument.
        if settings is None or u'vertical' not in settings or u'n' not in settings:
            msg = u'NGramIndexer requires "vertical" and "n" settings'
            raise RuntimeError(msg)
        elif settings[u'n'] < 1:
            msg = u'NGramIndexer requires an "n" value of at least 1'
            raise RuntimeError(msg)
        else:
            self._settings = {}
            self._settings[u'vertical'] = settings[u'vertical']
            self._settings[u'n'] = settings[u'n']
            self._settings[u'horizontal'] = settings[u'horizontal'] if u'horizontal' in settings \
                else NGramIndexer.default_settings[u'horizontal']
            if u'mark singles' in settings:
                self._settings[u'mark_singles'] = settings[u'mark singles']
            elif u'mark_singles' in settings:
                self._settings[u'mark_singles'] = settings[u'mark_singles']
            else:
                self._settings[u'mark_singles'] = NGramIndexer.default_settings[u'mark_singles']
            self._settings[u'terminator'] = settings[u'terminator'] if u'terminator' in settings \
                else NGramIndexer.default_settings[u'terminator']
            self._settings[u'continuer'] = settings[u'continuer'] if u'continuer' in settings \
                else NGramIndexer.default_settings[u'continuer']

        # Change "TemplateIndexer" to the current class name. The superclass will handle the
        # "score" and "mpc" arguments, but you should have processed "settings" above, so it should
        # not be sent to the superclass constructor.
        super(NGramIndexer, self).__init__(score, None)

        # not using it
        self._indexer_func = None

    @staticmethod
    def _format_thing(things, m_singles, markers=(u'[', u']'), terminator=None):
        """
        Format unicode objects by concatenating them with a space between and the appropriate
        grouping symbol, if relevant. This method is used by _format_vert() and _format_horiz().

        :param things: All the events for this moment.
        :type things: iterable of basestring

        :param m_singles: Whether to put marker characters around single-item iterables.
        :type m_singles: boolean

        :param markers: The "marker" strings to put around the output, if desired. Defualt is [].
        :type markers: 2-tuple of unicode

        :param terminator: If one of the events is in this iterale, raise a RuntimeError. Default
            is [None].
        :type terminator: list of unicode or None

        :returns: A unicode with a space between every event and marker characters if there is more
            than one event or m_singles is True.
        :rtype: unicode

        :raises: RuntimeWarning, if the one of the events is a "terminator."
        """
        terminator = [] if terminator is None else terminator
        post = []
        if len(things) > 1:
            post.append(markers[0])
            for obj in things:
                if obj in terminator:
                    raise RuntimeWarning(u'hit a terminator')
                else:
                    post.append(unicode(obj))
                    post.append(u' ')
            post = post[:-1] # remove last space
            post.append(markers[1])
        elif things[0] in terminator:
            raise RuntimeWarning(u'hit a terminator')
        elif m_singles:
            post.extend([markers[0], unicode(things[0]), markers[1]])
        else:
            post.append(things[0])
        return u''.join(post)

    @staticmethod
    def _format_vert(verts, m_singles, terminator=None):
        """
        Format "vertical" unicode objects by concatenating them with a space between and the
        appropriate grouping symbol, if relevant.

        :param verts: All the "vertical" events for this moment.
        :type verts: iterable of basestring

        :param m_singles: Whether to put marker characters around single-item iterables.
        :type m_singles: boolean

        :param terminator: If one of the events is in this iterale, raise a RuntimeError. Default
            is [None].
        :type terminator: list of unicode or None

        :returns: A unicode with a space between every event and marker characters if there is more
            than one event or m_singles is True.
        :rtype: unicode

        :raises: RuntimeWarning, if the one of the events is a "terminator."
        """
        return NGramIndexer._format_thing(verts, m_singles, (u'[', u']'), terminator)

    @staticmethod
    def _format_horiz(horizs, m_singles, terminator=None):
        """
        Format "horizontal" unicode objects by concatenating them with a space between and the
        appropriate grouping symbol, if relevant.

        :param verts: All the "horizontal" events for this moment.
        :type verts: iterable of basestring

        :param m_singles: Whether to put marker characters around single-item iterables.
        :type m_singles: boolean

        :param terminator: If one of the events is in this iterale, raise a RuntimeError. Default
            is [None].
        :type terminator: list of unicode or None

        :returns: A unicode with a space between every event and marker characters if there is more
            than one event or m_singles is True.
        :rtype: unicode

        :raises: RuntimeWarning, if the one of the events is a "terminator."
        """
        return NGramIndexer._format_thing(horizs, m_singles, (u'(', u')'), terminator)

    def run(self):
        """
        Make an index of k-part n-grams of anything.

        :returns: A single-item list with the new index.
        :rtype: ``list`` of :class:`pandas.Series`
        """
        # TODO: pylint says there are too many branches; it's right

        post = []
        post_offsets = []

        # for the formatting methods
        m_singles = self._settings[u'mark_singles']
        term = self._settings[u'terminator']

        # Order the parts as specified. We have to track "i" and "name" separately so we have a new
        # order for the dict but can keep self._score straight. We'll use these tuples to keep
        # vertical and horizontal events separated in the DataFrame with a MultiIndex
        events = {}
        for i, name in enumerate(self._settings[u'vertical']):
            events[(u'v', i)] = self._score[name]
        for i, name in enumerate(self._settings[u'horizontal']):
            events[(u'h', i)] = self._score[name]

        # Make the MultiIndex and DataFrame with all events
        events = pandas.DataFrame(events, columns=pandas.MultiIndex.from_tuples(events.keys()))

        # Fill in all "vertical" NaN values with the previous value
        for i in events[u'v'].columns:
            # NB: still have to test the fix, as stated in issue 261
            events.update(events.loc[:,(u'v', i)].fillna(method=u'ffill'))

        # Fill in all "horizontal" NaN values with the continuer
        if u'h' in events:
            for i in events[u'h'].columns:
                # NB: still have to test the fix, as stated in issue 261
                events.update(events.loc[:,(u'h', i)].fillna(value=self._settings[u'continuer']))

        # Iterate the offsets
        for i in xrange(len(events)):
            loop_post = None
            try:
                # first vertical event
                loop_post = [NGramIndexer._format_vert(list(events[u'v'].iloc[i].sort_index()),
                                                            m_singles,
                                                            term)]
            except RuntimeWarning:  # we hit a terminator
                continue
            try:
                for j in xrange(self._settings[u'n'] - 1):  # iterate to the end of 'n'
                    k = i + j + 1  # the index we need
                    ilp = None  # it means "Inner Loop Post"
                    if u'h' in events:  # are there "horizontal" events?
                        ilp = [u' ',
                               NGramIndexer._format_horiz(list(events[u'h'].iloc[k].sort_index()),
                                                          m_singles),
                               u' ',
                               NGramIndexer._format_vert(list(events[u'v'].iloc[k].sort_index()),
                                                         m_singles,
                                                         term)]
                    else:
                        ilp = [u' ',
                               NGramIndexer._format_vert(list(events[u'v'].iloc[k].sort_index()),
                                                         m_singles,
                                                         term)]
                    loop_post.extend(ilp)
            except (KeyError, IndexError, RuntimeWarning) as the_err:
                if isinstance(the_err, (IndexError, KeyError)):  # end of inputted Series
                    break
                else:  # we hit a terminator
                    continue
            post.append(u''.join(loop_post))
            post_offsets.append(events.index[i])

        return [pandas.Series(post, post_offsets)]
