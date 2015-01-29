#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/template.py
# Purpose:                Template indexer
#
# Copyright (C) 2013-2015 Christopher Antila, Alexander Morgan
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
"""
import pandas
from numpy import nan, isnan  # pylint: disable=no-name-in-module
from music21 import stream
from vis.analyzers import indexer

def indexer_func(obj):
    return None

class DissonanceIndexer(indexer.Indexer):
    """
    Indexer that locates vertical dissonances between pairs of voices in a piece. Used internally by
    :class:`DissonanceIndexer`. Categorizes intervals as consonant or dissonant and in the case
    of fourths (perfect or augmented) and diminished fifths it examines the other parts sounding
    with that fourth or fifth (if there are any) to see if the interval can be considered consonant.
    """
    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, settings=None):
        """
        :param score: The output from :class:`~vis.analyzers.indexers.interval.IntervalIndexer`.
            You must include interval quality and use simple intervals.
        :type score:  :class:`pandas.DataFrame`.
        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: NoneType

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        setts = {'quality': True, 'simple or compound': 'simple'}
        super(DissonanceIndexer, self).__init__(score, setts)
        self._indexer_func = indexer_func

    def simul_ints(self, intervalDataFrame):
        """
        Creates a 'forwardfilled' version of the passed dataframe and returns it. Eventually this
        could be its own class, but since the dissonance the function check_4s_5s is the only place 
        that should use forward filling (it interferes with results in most other contexts) it is
        just a function.
        """
        ints = intervalDataFrame.copy(deep=True)
        ffilled_ints = ints.ffill()
        del ints
        return ffilled_ints

    def check_4s_5s(self, pair_name, event_num, start_off, suspect_diss, simuls):
        """
        This function evaluates whether P4's, A4's, and d5's should be considered consonant based
        whether or not the lower voice of the suspect_diss forms an interval that causes us to deem
        the fourth or fifth consonant, as determined by the cons_makers list below. The function
        should be called once for each potentially consonant fourth or fifth.

        :param pair_name: Name of pair that has the potentially consonant fourth or fifth.
        :type pair_name: String in the format '0,2' if the pair in question is S and T in an
            SATB texture.
        :param event_num: Pandas iloc number of interval's row in dataframe.
        :type event_num: Integer.
        :param start_off: Beginning offset of 4th or 5th being analyzed.
        :type start_off: Integer.
        :param suspect_diss: Interval name with quality and direction (i.e. nothing or '-') that
            corresponds to the fourth or fifth to be examined.
        :type suspect_diss: String.
        """
        cons_makers = {'P4':[u'm3', u'M3', u'P5'], 'd5':[u'M6'], 'A4':[u'm3'], '-P4':[u'm3', u'M3', u'P5'], '-d5':[u'M6'], '-A4':[u'm3']}
        Xed_makers = {'P4':[u'-m3', u'-M3', u'-P5'], 'd5':[u'-M6'], 'A4':[u'-m3'],'-P4':[u'-m3', u'-M3', u'-P5'], '-d5':[u'-M6'], '-A4':[u'-m3']}
        cons_made = False
        end_off = start_off     # Find the offset of the next event in the voice pair to know when the interval ends.
        for index, row in self._score['interval.IntervalIndexer'][start_off:].iterrows():
            if end_off != start_off:
                break
            elif end_off == start_off:
                end_off = self._score['interval.IntervalIndexer'].index[len(self._score['interval.IntervalIndexer'])-1]  # for the case where a 4th or 5th is in the last attack of the piece.
            elif type(row[pair_name]) is unicode:
                    end_off = self._score['interval.IntervalIndexer'].index[event_num + index]

        if '-' in suspect_diss: 
            lower_voice = pair_name.split(',')[0]
        else:
            lower_voice = pair_name.split(',')[1]

        for voice_combo in self._score['interval.IntervalIndexer']:
            if lower_voice == voice_combo.split(',')[0] and voice_combo != pair_name: # look at other pairs that have lower_voice as their upper voice. Could be optimized.
                if simuls[voice_combo][start_off:end_off].any() in cons_makers[suspect_diss]:
                    cons_made = True
                    break
            elif lower_voice == voice_combo.split(',')[1] and voice_combo != pair_name: # look at other pairs that have lower_voice as their lower voice. Could be optimized.
                if simuls[voice_combo][start_off:end_off].any() in Xed_makers[suspect_diss]:
                    cons_made = True
                    break

        if cons_made:   # 'C' is for consonant and it's good enough for me.
            return ('C' + suspect_diss)
        else:   # 'D' shows that the fourth or fifth analyzed turned out to be dissonant.
            return ('D' + suspect_diss)   

    def run(self):
        """
        Make a new index of the piece in the same format as the :class:`IntervalIndexer` (i.e. a
        DataFrame of Series where each series corresponds to the intervals in a given voice pair).
        The difference between this and the interval indexer is that this one figures out whether
        fourths or diminished fifths should be considered consonant for the purposes of dissonance
        classification.

        :returns: A :class:`DataFrame` of the new indices. The columns have a :class:`MultiIndex`.
        :rtype: :class:`pandas.DataFrame`
        """
        results = self._score['interval.IntervalIndexer'].copy(deep=True)
        potential_consonances = [u'P4', u'-P4', u'A4', u'-A4', u'd5', u'-d5']
        simuls = self.simul_ints(self._score['interval.IntervalIndexer'])
        for pair_title in results:
            for j, event in enumerate(results[pair_title]):
                if event in potential_consonances: # NB: all other events are definite consonances or dissonances or don't qualify as interval onsets.
                    results[pair_title].iloc[j] = self.check_4s_5s(pair_title, j, results.index[j], event, simuls)
        
        results = results.T     # Reapply the multi-index to the results dataframe
        new_multiindex = [('dissonance.DissonanceLocator', x) for x in list(results.index)]
        results.index = pandas.MultiIndex.from_tuples(new_multiindex)
        results = results.T
        
        return results
