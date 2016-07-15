#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
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
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
.. codeauthor:: Alexander Morgan
.. codeauthor:: Christopher Antila <christopher@antila.ca>

Indexer to find k-part any-object n-grams. This file is a reimplimentation 
of the previous ngram_indexer.py file.
"""

# pylint: disable=pointless-string-statement

import pandas
from vis.analyzers import indexer


class NewNGramIndexer(indexer.Indexer):
    """
    Indexer that finds k-part n-grams from other indices.

    The indexer requires at least one "vertical" index, and supports "horizontal" indices that seem
    to "connect" instances in the vertical indices. Although we use "vertical" and "horizontal" to
    describe these index types, because the class is an abstraction of two-part interval n-grams,
    you can supply any information as either type of index. If you want one-part melodic n-grams
    for example, you should supply the relevant interval information as the "vertical" component.
    The "vertical" and "horizontal" indices can contain an arbitrary number of observations that 
    can get condensed into one value or kept separate in different columns. There is no 
    relationship between the number of index types, though there must be at least one "vertical" 
    index.

    The ``'vertical'`` and ``'horizontal'`` settings determine which columns of the dataframes in 
    ``score`` are included in the n-gram output. ``score`` is a list of two dataframes, the 
    vertical observations :class:`DataFrame` and the horizontal observations :class:`DataFrame`. 
    The format of the vertical and horizontal settings is very important and will decide the 
    structure of the resulting n-gram results. Both the vertical and horizontal settings should 
    be a list of tuples. If the optional horizontal setting is passed, its list should be of the 
    same length as that of the vertical setting. Inside of each tuple, enter the column names of 
    the observations that you want to include in each value. For example, if you want to make 
    3-grams of notes in the tenor in a four-voice choral, use the following settings (NB: there 
    is no horizontal element in this simple query so no horizontal setting is passed. In this 
    scenario you would need to pass the noterest indexer results as the only dataframe in the 
    "score" list of dataframes.):
    
    settings = {'n': 3, 'vertical': [('2',)]}

    If you want to look at the 4-grams in the interval pairs between the bass and soprano of a 
    four-voice choral and track the melodic motions of the bass, the ``score`` argument should 
    be a 2-item list containing the IntervalIndexer results dataframe and the 
    HorizontalIntervalIndexer dataframe. Note that the HorizontalIntervalIndexer results must 
    have been calculated with the 'horiz_attach_later' setting set to True (this is in order 
    to avoid an indexing nightmare). The settings dictionary to pass to this indexer would be:

    settings = {'n': 4, 'vertical': [('0,3',)], 'horizontal': [('3',)]}

    If you want to get 'figured-bass' 2-gram output from this same 4-voice choral, use the same 
    2-item list for the score argument, and then put all of the voice pairs that sound against 
    the bass in the same tuple in the vertical setting. Here's what the settings should be:

    settings = {'n': 2, 'vertical': [('0,3', '1,3', '2,3')], 'horizontal': [('3',)]}

    In the example above, if you wanted stacks of vertical events without the horizontal 
    connecting events, you would just omit the 'horizontal' setting from the settings dictionary 
    and also only include the vertical observations in the ``score`` list of dataframes.

    If instead you want to look at all the pairs of voices in the 4-voice piece, and always track 
    the melodic motions of the lowest voice in that pair, then put each pair in a different tuple,
    and in the voice to track melodically in the corresponding tuple in the horizontal list. Since 
    there are 6 pairs of voices in a 4-voice piece, both your vertical and horizontal settings 
    should be a list of six tuples. This will cause the resulting n-gram results dataframe to have 
    six columns of observations. Your settings should look like this:

    settings = {'n': 2, 'vertical': [('0,1',), ('0,2',), ('0,3',), ('1,2',), ('1,3',), ('2,3')], 
                'horizontal': [('1',), ('2',), ('3',), ('2',), ('3',), ('3',)]}

    Since we often want to look at all the pairs of voices in a piece, you can set the 'vertical' 
    setting to 'all' and this will get all the column names from the first dataframe in the 
    score list of dataframes. Similarly, as we often want to always track the melodic motions of 
    the lowest or highest voice in the vertical groups, the horizontal setting can be set to 
    'highest' or 'lowest' to automate this voice selection. This means that the preceeding query 
    can also be accomplished with the following settings:

    settings = {'n': 2, 'vertical': 'all', 'horizontal': 'lowest'}

    The 'brackets' setting will set off all the vertical events at each time point in square 
    brackets '[]' and horizontal observations will appear in parentheses '()'. This is particularly 
    useful if there are multiple observations in each vertical or horizontal slice. For example, if 
    we wanted to redo the query above where n = 4, but this time tracking the melodic motions of 
    both the upper and the lower voice, it would be a good idea to set 'brackets' to True to make 
    the results easier to read. The settings would look like this:

    settings = {'n': 4, 'vertical': [('0,3',)], 'horizontal': [('0', '3',)], 'brackets': True}

    If you want n-grams to terminate when finding one or several particular values, you can specify
    this by passing a list of strings as the ``'terminator'`` setting.

    To show that a horizontal event continues, we use ``'_'`` by default, but you can set this
    separately, for example to ``'P1'`` ``'0'``, as seems appropriate. 
    """

    required_score_type = 'pandas.DataFrame'

    possible_settings = ['horizontal', 'vertical', 'n', 'open-ended', 'brackets', 'terminator', 'continuer']
    """
    A list of possible settings for the :class:`NewNGramIndexer`.

    :keyword 'horizontal': Selectors for the columns to consider as "horizontal."
    :type 'horizontal': list of tuples of strings, default [].
    :keyword 'vertical': Selectors for the column names to consider as "vertical."
    :type 'vertical': list of tuples of strings, default 'all'.
    :keyword 'n': The number of "vertical" events per n-gram.
    :type 'n': int
    :keyword 'open-ended': Appends the next horizontal observation to n-grams leaving them open-ended.
    :type 'open-ended': boolean, default False.
    :keyword 'brackets': Whether to use delimiters around event observations. Square brakets [] are used 
        to set off vertical events and round brackets () are used to set off horizontal events. This is 
        particularly important to leave as True (default) for better legibility when there are multiple 
        vertical or multiple horizontal observations at each slice.
    :type 'brackets': bool, default True.
    :keyword 'terminator': Do not find an n-gram with a vertical item that contains any of these
        values.
    :type 'terminator': list of str, default [].
    :keyword 'continuer': When there is no "horizontal" event that corresponds to a vertical
        event, this is printed instead, to show that the previous "horizontal" event continues.
    :type 'continuer': str, default '_'.
    """

    default_settings = {'brackets': True, 'horizontal': [], 'open-ended': False, 'terminator': [], 
                        'vertical': 'all', 'continuer': '_'}

    _MISSING_SETTINGS = 'NewNGramIndexer requires "vertical" and "n" settings.'
    _MISSING_HORIZONTAL_DATA = 'NewNGramIndexer needs a dataframe of horizontal observations if you want \
        to include a horizontal dimension in your ngrams.'
    _SUPERFLUOUS_HORIZONTAL_DATA = 'If n is set to 1, no horizontal observations will be included in ngrams \
        so you should leave the "horizontal" setting blank.'
    _N_VALUE_TOO_LOW = 'NewNGramIndexer requires an "n" value of at least 1.'
    _N_VALUE_TOO_HIGH = 'NewNGramIndexer is unlikely to return results when the value of n is greater than \
        the number of passed observations in either of the passed dataframes.'

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
            raise RuntimeError(NewNGramIndexer._MISSING_SETTINGS)
        elif settings['n'] < 1:
            raise RuntimeError(NewNGramIndexer._N_VALUE_TOO_LOW)
        else:
            self._settings = NewNGramIndexer.default_settings.copy()
            self._settings.update(settings)
        
        self._cut_off = self._settings['n'] if not self._settings['open-ended'] else self._settings['n'] + 1
        if all(self._cut_off > len(df) for df in score):
            raise RuntimeWarning(NewNGramIndexer._N_VALUE_TOO_HIGH)

        super(NewNGramIndexer, self).__init__(score, None)

        self._vertical_indexer_name = self._score[0].columns[0][0]

        if self._settings['horizontal']:
            if len(self._score) != 2:
                raise RuntimeError(NewNGramIndexer._MISSING_HORIZONTAL_DATA)
            if self._settings['n'] == 1 and not self._settings['open-ended']:
                raise RuntimeError(NewNGramIndexer._SUPERFLUOUS_HORIZONTAL_DATA)
            self._horizontal_indexer_name = self._score[1].columns[0][0]

        if self._settings['vertical'] == 'all':
            self._settings['vertical'] = [(x,) for x in self._score[0][self._vertical_indexer_name].columns]

        if self._settings['horizontal'] == 'lowest':
            temp = [list(map(int, x[0].split(','))) for x in self._settings['vertical']]
            self._settings['horizontal'] = [(str(max(y)),) for y in temp]
        elif self._settings['horizontal'] == 'highest':
            temp = [list(map(int, x[0].split(','))) for x in self._settings['vertical']]
            self._settings['horizontal'] = [(str(min(y)),) for y in temp]


    def run(self):
        """
        Make an index of k-part n-grams of anything.

        :returns: A new index of the piece in the form of a class:`~pandas.DataFrame` with as many 
            columns as there are tuples in the 'vertical' setting of the passed settings.

        **Example:**

        import music21
        from vis.analyzers.indexers import noterest, interval, new_ngram

        piece = music21.converter.parse('example.xml')
        score = noterest.NoteRestIndexer(piece).run()

        hints = interval.HorizontalIntervalIndexer(score).run()
        vints = interval.IntervalIndexer(score).run()

        settings = {'n': 3, 'vertical': '3'}
        ngrams = new_ngram.NewNGramIndexer([hints, vints], settings).run()
        print(ngrams)
        """
        n = self._settings['n']        
        post = []
        cols = []
        # Each i in this loop will be a dataframe column of ngrams for a voice combination passed by the user
        for i, verts in enumerate(self._settings['vertical']):
            events = {}
            col_label = []
            if self._settings['brackets']:
                events[('v', 'v0')] = '['

            for j, name in enumerate(verts):
                if j == 0:
                    events[('v', 'v1')] = self._score[0].loc[:, (self._vertical_indexer_name, name)].dropna()
                    col_label.append(name)
                else:
                    events[('v', 'v' + str(j + 1))] = ' ' + self._score[0].loc[:, (self._vertical_indexer_name, name)].dropna()
                    col_label.append(name)

            if self._settings['brackets']:
                events[('v', 'v' + str(len(verts) + 1))] = '] '
            else:
                events[('v', 'v' + str(len(verts) + 1))] = ' '

            if self._settings['horizontal']: # NB: the bool value of an empty list is False.
                horizs = self._settings['horizontal'][i]
                if self._settings['brackets']:
                    events[('h', 'h0')] = '('

                for j, name in enumerate(horizs):
                    if j == 0:
                        events[('h', 'h1')] = self._score[1].loc[:, (self._horizontal_indexer_name, name)].dropna()
                        col_label.extend((':', name))
                    else:
                        events[('h', 'h' + str(j + 1))] = ' ' + self._score[1].loc[:, (self._horizontal_indexer_name, name)].dropna()
                        col_label.append(name)

                if self._settings['brackets']:
                    events[('h', 'h' + str(len(horizs) + 1))] = ') '
                else:
                    events[('h', 'h' + str(len(horizs) + 1))] = ' '

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
                    chunks.extend([ffilled_events.shift(-x) for x in range(1, n)])
            # If there were no "horizontal" events set the chunks to the vertical slices
            else:
                chunks = [v_filled.shift(-x) for x in range(n)]

            # Add a column of horizontal events if 'open-ended' setting is True
            if self._settings['open-ended']:
                chunks.append(h_filled.shift(-n))

            # Make a dataframe which each vertical or horizontal component of the ngrams as a column
            ngram_df = pandas.concat(chunks, axis=1)

            # Concatenate strings of each row to turn df into a series and also remove the last n-1
            # observations since they can't contain valid n-grams.
            if self._cut_off == 1:
                res = ngram_df.iloc[:, 0].str.cat([ngram_df.iloc[:, x] for x in range(1, len(ngram_df.columns))])
            else:
                res = ngram_df.iloc[:(-self._cut_off + 1), 0].str.cat([ngram_df.iloc[:(-self._cut_off + 1), 
                               x] for x in range(1, len(ngram_df.columns))])
            
            # Get rid of the observations that contain any of the terminators
            if self._settings['terminator']:
                for term in self._settings['terminator']:
                    terminated = res.apply(lambda r : any([term in e for e in r]))
                    res = res[~terminated]

            # Get rid of the trailing space in each ngram and add this combination to post
            post.append(res.str.rstrip())

        return self.make_return(cols, post)
