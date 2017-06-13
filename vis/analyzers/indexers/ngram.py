#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/ngram.py
# Purpose:                k-part anything n-gram Indexer
#
# Copyright (C) 2013-2016 Alexander Morgan, Christopher Antila
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
# You should have received a copy of the GNU Affero General Public 
# License along with this program. If not, see 
# <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------- #
"""
.. codeauthor:: Alexander Morgan
.. codeauthor:: Christopher Antila <christopher@antila.ca>

Indexer to find k-part any-object n-grams. This file is a 
re-implimentation of the previous ngram_indexer.py file.

"""

# pylint: disable=pointless-string-statement

import pandas
from vis.analyzers import indexer


class NGramIndexer(indexer.Indexer):
    """
    Indexer that finds k-part n-grams from other indices.

    The indexer requires at least one "vertical" index, and supports 
    "horizontal" indices that seem to "connect" instances in the 
    vertical indices. Although we use "vertical" and "horizontal" to 
    describe these index types, because the class is an abstraction of 
    two-part interval n-grams, you can supply any information as either 
    type of index. If you want one-part melodic n-grams for example, you 
    should supply the relevant interval information as the "vertical" 
    component. The "vertical" and "horizontal" indices can contain an 
    arbitrary number of observations that can get condensed into one 
    value or kept separate in different columns. There is no 
    relationship between the number of index types, though there must be 
    at least one "vertical" index.

    The ``'vertical'`` and ``'horizontal'`` settings determine which 
    columns of the dataframes in ``score`` are included in the n-gram 
    output. ``score`` is a list of two dataframes, the vertical 
    observations :class:`DataFrame` and the horizontal observations 
    :class:`DataFrame`. 
    
    The format of the vertical and horizontal settings is very important 
    and will decide the structure of the resulting n-gram results. Both 
    the vertical and horizontal settings should be a list of tuples. If 
    the optional horizontal setting is passed, its list should be of the 
    same length as that of the vertical setting. Inside of each tuple, 
    enter the column names of the observations that you want to include 
    in each value. For example, if you want to make 3-grams of notes in 
    the tenor in a four-voice choral, use the following settings (NB: 
    there is no horizontal element in this simple query so no horizontal 
    setting is passed. In this scenario you would need to pass the 
    noterest indexer results as the only dataframe in the "score" list 
    of dataframes.):
    
    >>> settings = {
            'n': 3, 
            'vertical': [('2',)]
        }

    If you want to look at the 4-grams in the interval pairs between the 
    bass and soprano of a four-voice choral and track the melodic 
    motions of the bass, the ``score`` argument should be a 2-item list 
    containing the IntervalIndexer results dataframe and the 
    :class:`HorizontalIntervalIndexer` dataframe. Note that the 
    :class:`HorizontalIntervalIndexer` results must have been calculated 
    with the ``'horiz_attach_later'`` setting set to ``True`` (this is 
    in order to avoid an indexing nightmare). The settings dictionary to 
    pass to this indexer would be:

    >>> settings = {
            'n': 4, 
            'vertical': [('0,3',)], 
            'horizontal': [('3',)]
        }

    If you want to get 'figured-bass' 2-gram output from this same 
    4-voice choral, use the same 2-item list for the score argument, and 
    then put all of the voice pairs that sound against the bass in the 
    same tuple in the vertical setting. Here's what the settings should 
    be:

    >>> settings = {
            'n': 2, 
            'vertical': [('0,3', '1,3', '2,3')], 
            'horizontal': [('3',)]
        }

    In the example above, if you wanted stacks of vertical events 
    without the horizontal connecting events, you would just omit the 
    ``'horizontal'`` setting from the settings dictionary and also only 
    include the vertical observations in the ``score`` list of 
    dataframes.

    If instead you want to look at all the pairs of voices in the 
    4-voice piece, and always track the melodic motions of the lowest 
    voice in that pair, then put each pair in a different tuple, and in 
    the voice to track melodically in the corresponding tuple in the 
    horizontal list. Since there are 6 pairs of voices in a 4-voice 
    piece, both your vertical and horizontal settings should be a list 
    of six tuples. This will cause the resulting n-gram results 
    dataframe to have six columns of observations. Your settings should 
    look like this:

    >>> settings = {
            'n': 2, 'vertical': [
                ('0,1',), 
                ('0,2',), 
                ('0,3',), 
                ('1,2',), 
                ('1,3',), 
                ('2,3')
            ], 
            'horizontal': [
                ('1',), 
                ('2',), 
                ('3',), 
                ('2',), 
                ('3',), 
                ('3',)
            ]
        }

    Since we often want to look at all the pairs of voices in a piece, 
    you can set the ``'vertical'`` setting to ``'all'`` and this will 
    get all the column names from the first dataframe in the score list 
    of dataframes. Similarly, as we often want to always track the 
    melodic motions of the lowest or highest voice in the vertical 
    groups, the horizontal setting can be set to ``'highest'`` or 
    ``'lowest'`` to automate this voice selection. This means that the 
    preceeding query can also be accomplished with the following 
    settings:

    >>> settings = {
            'n': 2, 
            'vertical': 'all', 
            'horizontal': 'lowest'
        }

    The ``'brackets'`` setting will set off all the vertical events at each 
    time point in square brackets '[]' and horizontal observations will 
    appear in parentheses '()'. This is particularly useful if there are 
    multiple observations in each vertical or horizontal slice. For 
    example, if we wanted to redo the query above where n = 4, but this 
    time tracking the melodic motions of both the upper and the lower 
    voice, it would be a good idea to set 'brackets' to ``True`` to make 
    the results easier to read. The settings would look like this:

    >>> settings = {
            'n': 4, 
            'vertical': [('0,3',)], 
            'horizontal': [('0', '3',)], 
            'brackets': True
        }

    If you want n-grams to terminate when finding one or several 
    particular values, you can specify this by passing a list of strings 
    as the ``'terminator'`` setting.

    To show that a horizontal event continues, we use ``'_'`` by 
    default, but you can set this separately, for example to ``'P1'`` 
    ``'0'``, as seems appropriate.

    Once you've chosen the appropriate settings, to actually run the 
    indexer call it like this:

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ngram_settings = {
            'n': 2, 
            'vertical': 'all', 
            'horizontal': 'lowest'
        }
    >>> vert_settings = {
            'quality': 'chromatic', 
            'simple or compound': 'simple', 
            'directed': True
        }
    >>> horiz_settings = {
            'quality': 'diatonic with quality', 
            'simple or compound': 'simple', 
            'directed': True, 
            'horiz_attach_later': True
        }
    >>> vert_ints = ip.get_data('vertical_interval', settings=vert_settings)
    >>> horiz_ints = ip.get_data('horizontal_interval', settings=horiz_settings)
    >>> ip.get_data('ngram', data=[vert_ints, horiz_ints], settings=ngram_settings)
    
    """

    required_score_type = 'pandas.DataFrame'

    possible_settings = [
        'horizontal', 
        'vertical', 
        'n', 
        'open-ended', 
        'brackets', 
        'terminator',
        'continuer', 
        'align'
    ]
    
    """
    A list of possible settings for the :class:`NGramIndexer`.

    :keyword 'horizontal': Selectors for the columns to consider as 
        "horizontal."
    
    :type 'horizontal': list of tuples of strings, default [].
    
    :keyword 'vertical': Selectors for the column names to consider as 
        "vertical."
    
    :type 'vertical': list of tuples of strings, default 'all'.
    
    :keyword 'n': The number of "vertical" events per n-gram.
    
    :type 'n': int
    
    :keyword 'open-ended': Appends the next horizontal observation to 
        n-grams leaving them open-ended.
    
    :type 'open-ended': boolean, default ``False``.
    
    :keyword 'brackets': Whether to use delimiters around event 
        observations. Square brakets [] are used to set off vertical 
        events and round brackets () are used to set off horizontal 
        events. This is particularly important to leave as ``True`` 
        (default) for better legibility when there are multiple vertical 
        or multiple horizontal observations at each slice.
    
    :type 'brackets': bool, default True.
    
    :keyword 'terminator': Do not find an n-gram with a vertical item 
        that contains any of these values.
    
    :type 'terminator': list of str, default [].
    
    :keyword 'continuer': When there is no "horizontal" event that corresponds to a vertical
        event, this is printed instead, to show that the previous "horizontal" event continues.
    
    :type 'continuer': str, default '_'.
    
    """

    default_settings = {
        'brackets': True, 
        'horizontal': [], 
        'open-ended': False, 
        'terminator': [], 
        'vertical': 'all', 
        'continuer': '_', 
        'align': 'left'
    }

    _MISSING_SETTINGS = ("NGramIndexer requires 'vertical' and 'n' " + 
        "settings.")
    _MISSING_HORIZONTAL_SETTING = ("If you provide a list of two " + 
        "DataFrames as the score, you must also specify the columns " +
        "to examine in the second DataFrame with the 'horizontal' " + 
        "setting.")
    _MISSING_HORIZONTAL_DATA = ("NGramIndexer needs a dataframe of " + 
        "horizontal observations if you want to include a horizontal " +
        "dimension in your ngrams.")
    _SUPERFLUOUS_HORIZONTAL_DATA = ("If n is set to 1 and the " + 
        "'open_ended' setting is set to False, no horizontal " + 
        "observations will be included in ngrams so you should leave " + 
        "the 'horizontal' setting blank.")
    _HORIZONTAL_OUT_OF_RANGE = ("Not all of the specified " + 
        "'horizontal' columns are in the DataFrame of horizontal " + 
        "observations. If you're doing a query on multiple pieces, " + 
        "it can be convenient to pass 'all' as the 'horizontal' " + 
        "setting which dynamically selects all of the columns of the " +
        "DataFrame of horizontal observations.")
    _VERTICAL_OUT_OF_RANGE = ("Not all of the specified 'vertical' " + 
        "columns are in the DataFrame of vertical observations. If " + 
        "you're doing a query on multiple pieces, it can be " + 
        "convenient to pass 'all' as the 'vertical' setting which " + 
        "dynamically selects all of the columns of the DataFrame of " +
        "vertical observations.")
    _N_VALUE_TOO_LOW = ("NGramIndexer requires an 'n' value of at " +
        "least 1.")
    _N_VALUE_TOO_HIGH = ("NGramIndexer is unlikely to return results " +
        "when the value of n is greater than the number of passed " +
        "observations in either of the passed dataframes.")
    _WRONG_ALIGN_SETTING = ("Incorrect 'align' setting passed. " + 
        "Please use 'left', 'right', 'l', or 'r'.")

    def __init__(self, score, settings=None):
        """
        :param score: The :class:`DataFrame` to use for preparing 
            n-grams. You must ensure the :class:`DataFrame` has the 
            columns indicated in the ``settings``, or the :meth:`run`
            method will fail.
        
        :type score: :class:`pandas.DataFrame`
        
        :param dict settings: Required and optional settings. See 
            descriptions in :const:`possible_settings`.

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the 
            same types.
        
        :raises: :exc:`RuntimeError` if required settings are not 
            present in ``settings``.
        
        :raises: :exc:`RuntimeError` if ``'n'`` is less than ``1``.
        """
        # Check all required settings are present in the "settings" argument.
        if (settings is None or 'vertical' not in settings 
            or 'n' not in settings):
            raise RuntimeError(NGramIndexer._MISSING_SETTINGS)
        elif (settings['n'] < 1):
            raise RuntimeError(NGramIndexer._N_VALUE_TOO_LOW)
        else:
            self._settings = NGramIndexer.default_settings.copy()
            self._settings.update(settings)
        
        self._cut_off = self._settings['n'] if not self._settings['open-ended'] else self._settings['n'] + 1
        if (all(self._cut_off > len(df) for df in score)):
            raise RuntimeWarning(NGramIndexer._N_VALUE_TOO_HIGH)

        super(NGramIndexer, self).__init__(score, None)

        self._vertical_indexer_name = self._score[0].columns[0][0]

        if self._settings['horizontal']:
            if len(self._score) != 2:
                raise RuntimeError(NGramIndexer._MISSING_HORIZONTAL_DATA)
            elif self._settings['n'] == 1 and not self._settings['open-ended']:
                raise RuntimeWarning(NGramIndexer._SUPERFLUOUS_HORIZONTAL_DATA)
            elif (self._settings['horizontal'] not in ('lowest', 'highest') 
                and not all([col_name in self._score[1].columns.levels[1] 
                             for tup in settings['horizontal'] 
                             for col_name in tup])):
                raise RuntimeError(NGramIndexer._HORIZONTAL_OUT_OF_RANGE)
            self._horizontal_indexer_name = self._score[1].columns[0][0]
        elif len(self._score) != 1: 
            # there is a df of horizontal observations,
            # but no horizontal columns specified in settings.
            raise RuntimeError(NGramIndexer._MISSING_HORIZONTAL_SETTING)

        if self._settings['vertical'] != 'all':
            if not all([col_name in self._score[0].columns.levels[1] for
                        tup in settings['vertical'] for col_name in tup]):
                raise RuntimeError(NGramIndexer._VERTICAL_OUT_OF_RANGE)
        else: # i.e. self._settings['vertical'] == 'all'
            self._settings['vertical'] = [(x,) for x in
                                          self._score[0].columns.levels[1]]

        if self._settings['horizontal'] == 'lowest':
            temp = [x[0].split(',') for x in self._settings['vertical']]
            self._settings['horizontal'] = [(y[1],) for y in temp]
        elif self._settings['horizontal'] == 'highest':
            temp = [x[0].split(',') for x in self._settings['vertical']]
            self._settings['horizontal'] = [(y[0],) for y in temp]

        if self._settings['align'] not in ('left', 'right', 'L', 'R', 'l', 'r', 'Left',
                                           'Right', 'LEFT', 'RIGHT'):
            raise RuntimeWarning(NGramIndexer._WRONG_ALIGN_SETTING)

    def run(self):
        """
        Make an index of k-part n-grams of anything.

        :returns: A new index of the piece in the form of a 
            class:`~pandas.DataFrame` with as many columns as there are 
            tuples in the 'vertical' setting of the passed settings.
        
        """
        n = self._settings['n']        
        post = []
        cols = []
        # Each i in this loop will be a dataframe column of ngrams for a 
        # voice combination passed by the user
        for i, verts in enumerate(self._settings['vertical']):
            events = {}
            col_label = []
            if self._settings['brackets']:
                events[('v', 'v0')] = '['

            for j, name in enumerate(verts):
                if j > 0: # add a space if it's a non-first observation
                    events[('v', 'v' +str(j + .5))] = ' '
                events[('v', 'v' + str(j + 1))] = self._score[0].loc[:, (self._vertical_indexer_name, name)].dropna()
                col_label.append(name)

            if self._settings['brackets']:
                events[('v', 'v' + str(len(verts) + 1))] = ']'
            # add a space after all vertical observations
            events[('v', 'v' + str(len(verts) + 1.5))] = ' '

            if self._settings['horizontal']: # NB: the bool value of an empty list is False.
                horizs = self._settings['horizontal'][i]
                if self._settings['brackets']:
                    events[('h', 'h0')] = '('
                col_label.append(':')

                for j, name in enumerate(horizs):
                    if (j > 0): # add a space if it's a non-first observation
                        events[('h', 'h' + str(j + .5))] = ' '
                    events[('h', 'h' + str(j + 1))] = self._score[1].loc[:, (self._horizontal_indexer_name, name)].dropna()
                    col_label.append(name)

                if self._settings['brackets']:
                    events[('h', 'h' + str(len(horizs) + 1))] = ')'
                # add a space after all horizontal observations
                events[('h', 'h' + str(len(horizs) + 1.5))] = ' '

            cols.append(' '.join(col_label))
            events = pandas.DataFrame.from_dict(events)

            # Forward fill all the "vertical" events
            v_filled = events.loc[:, 'v'].fillna(method='ffill')
            # Fill in all "horizontal" NaN values with the continuer
            if 'h' in events:
                h_filled = events.loc[:, 'h'].fillna(value=self._settings['continuer'])
                ffilled_events = pandas.concat((h_filled, v_filled), axis=1)
                chunks = [v_filled]
                if n > 1:
                    chunks.extend([ffilled_events.shift(-x) 
                        for x in range(1, n)])
            # If there were no "horizontal" events set the chunks to the 
            # vertical slices
            else:
                chunks = [v_filled.shift(-x) for x in range(n)]

            # Add a column of horizontal events if 'open-ended' setting 
            # is True
            if self._settings['open-ended']:
                chunks.append(h_filled.shift(-n))

            # Make a dataframe which each vertical or horizontal 
            # component of the ngrams is a column
            ngram_df = pandas.concat(chunks, axis=1)

            # Apply the right alignment if the user asked for it.
            if (n > 1 and self._settings['align'] in ('right', 'Right', 'RIGHT', 'r', 'R')):
                new_index = ngram_df.index[n-1:]
                # It doesn't really matter what we put on the end 
                # because this will get cut off anyway,
                # but the values do always have to increase.
                ngram_df.index = new_index.append(pandas.Index([new_index[-1] + x 
                    for x in range(1, n)]))

            # Get rid of the observations that contain any of the 
            # terminators and trim the trailing rows that contain nans
            if self._settings['terminator']:
                ngram_df = ngram_df.replace(self._settings['terminator'], float('nan')).dropna()
            # if there are no terminators then we need to trim the 
            # trailing rows that contain nans
            elif self._cut_off > 1:
                ngram_df = ngram_df.iloc[:(-self._cut_off + 1), :]

            # Try to concatenate strings of each row to turn df into a 
            # series. If you encounter type other than string, first 
            # convert the values to strings then do the concatenation.
            try:
                res = ngram_df.iloc[:, 0].str.cat([ngram_df.iloc[:, x] 
                    for x in range(1, len(ngram_df.columns))])
            except AttributeError:
                ngram_df = ngram_df.applymap(str)
                res = ngram_df.iloc[:, 0].str.cat([ngram_df.iloc[:, x] 
                    for x in range(1, len(ngram_df.columns))])
            
            # Get rid of the trailing space in each ngram and add this 
            # combination to post
            post.append(res.str.rstrip())

        return self.make_return(cols, post)
