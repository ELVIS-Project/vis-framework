#! /usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/ngram.py
# Purpose:                k-part anything n-gram Indexer
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
k-part anything n-gram Indexer.
"""

import pandas
from vis.analyzers import indexer


def indexer_func(obj):
    """
    docstring
    """
    return None


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

    Use settings in the constructor to specify which index values in the "score" object are
    horizontal or vertical intervals. They will be added in the n-gram in the order specified, so
    if the u'vertical' setting is [4, 1, 3] for lists of intervals, the for each vertical event,
    objects will be listed in that order.

    In the output, groups of "vertical" events are enclosed in brackets, while groups of
    "horizontal" events are enclosed in parentheses.

    For cases where there is only one index in a particular direction, you can avoid printing the
    brackets or parentheses by setting the u'mark singles' setting to False (though the default
    is True).

    If you want n-grams to terminate when finding one or several particular values, you can specify
    this with the u'terminator' setting.
    """

    required_indices = []  # empty list accepts results of any Indexer
    required_score_type = pandas.Series
    requires_score = False
    possible_settings = [u'horizontal', u'vertical', u'n', u'mark singles', u'terminator']
    default_settings = {u'mark singles': True, u'horizontal': [], u'terminator': []}

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new NGramIndexer.

        Parameters
        ==========
        :param score: A list of the "horizontal" and "vertical" indices to use for n-grams. You can
            put the "horizontal" and "vertical" indices anywhere in the list, so long as you use
            settings to specify the order.
        :type: list of pandas.Series

        :param settings: The required settings.
            - vertical: iterable indicating the index values of the "score" iterable where
                "vertical" events are held; they will be included in the output in the order given
            - horizontal: iterable indicating the index values of the "score" iterable where
                "horizontal" events are held; they will be included in the output in the order
                give. Optional; default is [].
            - n: number of "vertical" events to include per n-gram
            - mark singles: whether to include brackets or parentheses for directions of which
                there is only one index. Optional; default is True
            - terminator: do not find an n-gram that contains any of these values. A list. Optional;
                default is []
        :type: dict

        :param mpc: An optional instance of MPController. If this is present, the Indexer will use
            it to submit jobs for multiprocessing. If not present, jobs will be executed in series.
        :type: MPController

        Raises
        ======
        RuntimeError :
            - If the "score" argument is the wrong type.
            - If the "score" argument is not a list of the same types.
            - If required settings are not present in the "settings" argument or u'n' is less than 2
        """

        # Check all required settings are present in the "settings" argument.
        if settings is None or u'vertical' not in settings or u'n' not in settings:
            msg = u'NGramIndexer requires "vertical" and "n" settings'
            raise RuntimeError(msg)
        elif settings[u'n'] < 2:
            msg = u'NGramIndexer requires an "n" value of at least 2'
            raise RuntimeError(msg)
        else:
            self._settings = {}
            self._settings[u'vertical'] = settings[u'vertical']
            self._settings[u'n'] = settings[u'n']
            self._settings[u'horizontal'] = settings[u'horizontal'] if u'horizontal' in settings \
                else NGramIndexer.default_settings[u'horizontal']
            self._settings[u'mark singles'] = settings[u'mark singles'] if u'mark singles' in \
                settings else NGramIndexer.default_settings[u'mark singles']
            self._settings[u'terminator'] = settings[u'terminator'] if u'terminator' in settings \
                else NGramIndexer.default_settings[u'terminator']

        # Change "TemplateIndexer" to the current class name. The superclass will handle the
        # "score" and "mpc" arguments, but you should have processed "settings" above, so it should
        # not be sent to the superclass constructor.
        super(NGramIndexer, self).__init__(score, None, mpc)

        # TODO: decide what to do here
        self._indexer_func = indexer_func

    def run(self):
        """
        Make an index of k-part n-grams of anything.

        Returns
        =======
        :returns: A single-item list with the new index.
        :rtype: list of pandas.Series
        """

        post = []
        post_offsets = []
        
        # settings for formatting
        m_singles = self._settings[u'mark singles']
        n_verts = len(self._settings[u'vertical'])
        n_horizs = len(self._settings[u'horizontal'])

        # functions for formatting
        def format_vert(ins):
            """
            Format "vertical" things. Provide an iterable of all the vertical things. They'll be
            outputted with a space between them, with the appropriate grouping symbol.
            """
            post = u''
            if n_verts > 1:
                post = u'['
                for obj in ins:
                    post += obj + u' '
                post = post[:-1] + u']'  # remove last space
            elif m_singles:
                post = u''.join([u'[', ins[0][0], u']'])
            else:
                post = ins[0][0]
            return post

        def format_horiz(ins):
            """
            Format "horizontal" things. Provide an iterable of all the horizontal things. They'll be
            outputted with a space between them, with the appropriate grouping symbol.
            """
            post = u''
            if n_horizs > 1:
                post = u'('
                for obj in ins:
                    post += obj + u' '
                post = post[:-1] + u')'  # remove last space
            elif m_singles:
                post = u''.join([u'(', ins[ins.index[0]], u')'])
            else:
                post = ins[ins.index[0]]
            return post

        # get the parts in the order specified; we have to track "i" and "name" separately so we
        # have a new order for the dict but can keep self._score straight
        vert = {}
        for i, name in enumerate(self._settings[u'vertical']):
            vert[i] = self._score[name]
        vert = pandas.DataFrame(vert)
        horiz = {}
        for i, name in enumerate(self._settings[u'horizontal']):
            horiz[i] = self._score[name]
        horiz = pandas.DataFrame(horiz)
        
        for i in xrange(len(vert) - 1):  # iterate each offset
            zoop = format_vert(vert.ix[i])  # first vertical event
            try:
                for j in xrange(self._settings[u'n'] - 1):  # iterate to the end of 'n'
                    zoop += u' ' + format_horiz(horiz.ix[i + j]) + u' ' + \
                            format_vert(vert.ix[i + j + 1])
            except KeyError:
                break
            post.append(zoop)
            post_offsets.append(i)

        return [pandas.Series(post, post_offsets)]
