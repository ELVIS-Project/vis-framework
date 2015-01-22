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
import six
import pandas
from numpy import nan, isnan  # pylint: disable=no-name-in-module
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
from music21 import stream
from vis.analyzers import indexer

def indexer_func(obj):      ##TODO: Ryan, should this function now be deleted?
    """
    The function that indexes.

    :param obj: The simultaneous event(s) to use when creating this index. (For indexers using a
        :class:`Series`).
    :type obj: :class:`pandas.Series` of strings

    :returns: "-" if the interval in question is regular a consonance, "C4" if a consonant fourth,
        "Cd5" if a consonant diminished fifth, or "D" if any other dissonance.
    :rtype: str
    """
    return None


class SimulIndexer(indexer.Indexer):
    """
    Used internally by the :class:`DissonanceIndexer`. This indexer forward fills the results of the
    interval indexer so that the dissonance indexer knows what intervals sound together. This
    information is used to classify fourths and fifths as consonant or dissonant.
    """
    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, settings=None):
        """
        :param score: The output from :class:`~vis.analyzers.indexers.interval.IntervalIndexer`.
            You must include interval quality and must use simple intervals.
        :type score:  :class:`pandas.DataFrame`.
        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: NoneType

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(SimulIndexer, self).__init__(score, None)
        self._indexer_func = indexer_func

    def run(self):
        """
        Make a new index of the piece in the same format as the :class:`IntervalIndexer` (i.e. a
        DataFrame of Series where each series corresponds to the intervals in a given voice pair).
        The difference between this and the interval indexer is that this one forward fills the
        interval results in order to make the simultaneities at any given offset easily accessible
        even if intervals that sound together don't have the same onset or same duration.

        :returns: A :class:`DataFrame` of the new indices. The columns have a :class:`MultiIndex`.
        :rtype: :class:`pandas.DataFrame`
        """
        # Copied from diss_sigs.py script and dissonance indexer in diss_sigs branch.
        setts = {u'quality': True, 'simple or compound': u'simple'}
        ffilled_intervals = the_piece.get_data([noterest.NoteRestIndexer, interval.IntervalIndexer], setts)
        ffilled_intervals = ffilled_intervals.T
        new_ints = ffilled_intervals.loc['interval.IntervalIndexer'].fillna(method='ffill', axis=1)
        new_multiindex = [('interval.IntervalIndexer', x) for x in list(new_ints.index)]
        new_ints.index = pandas.MultiIndex.from_tuples(new_multiindex)
        ffilled_intervals.update(new_ints)
        ffilled_intervals = ffilled_intervals.T
        del new_ints
        return ffilled_intervals


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
        super(DissonanceIndexer, self).__init__(score, None)
        self._indexer_func = indexer_func

    def check_4s_5s(self, pair_name, start_ind, suspect_diss):
        """
        This function evaluates whether P4's, A4's, and d5's should be considered consonant based
        whether or not the lower voice of the suspect_diss forms an interval that causes us to deem
        the fourth or fifth consonant, as determined by the cons_makers list below. The function
        should be called once for each potentially consonant fourth or fifth.

        :param pair_name: Name of pair that has the potentially consonant fourth or fifth.
        :type pair_name: String in the format '0,2' if the pair in question is S and T in an
            SATB texture.
        :param start_ind: Index of 4th or 5th being analyzed taken from the index of its voice
            pair.
        :type start_ind: Integer.
        :param suspect_diss: Interval name with quality and direction (i.e. nothing or '-') that
            corresponds to the fourth or fifth to be examined.
        :type suspect_diss: String.
        """
        cons_makers = {'P4':[u'm3', u'M3', u'P5'], 'd5':[u'M6'], 'A4':[u'm3'],
                       '-P4':[u'm3', u'M3', u'P5'], '-d5':[u'M6'], '-A4':[u'm3']}
        diss_dura = interval.IntervalIndexer[voice_pair_index][start_ind].duration.quarterLength
        end_ind = start_ind + diss_dura
        cons_made = False

        if '-' in suspect_diss: 
            lower_voice = pair_name.split(',')[0]
        else:
            lower_voice = pair_name.index.split(',')[1]

        for cn, voice_combo in enumerate(interval.IntervalIndexer.columns):
            if lower_voice == voice_combo[1].split(',')[0] and voice_combo[1] != pair_name: # look at other pairs that have lower_voice as their upper voice. Could be optimized.
                if any(SimulIndexer[SimulIndexer.columns[cn]][start_ind:end_ind] in cons_makers[suspect_diss]):
                    cons_made = True
                    break
           elif lower_voice == voice_combo[1].split(',')[1] and voice_combo[1] != pair_name: # look at other pairs that have lower_voice as their lower voice. Could be optimized.
                if any(SimulIndexer[SimulIndexer.columns[cn]][start_ind:end_ind][1:] in cons_makers[suspect_diss]):
                    cons_made = True
                    break
 
        if cons_made:   # 'C' is for consonant and it's good enough for me.
            return ('C' + suspect_diss)
        else:   # This 'D' shows that the fourth or fifth analyzed turned out to be truly dissonant.
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
        # To calculate all 2-part combinations:
        combinations = self._score['interval.IntervalIndexer']      # TODO: Check with Ryan. Should I pass the required settings here?
        consonances = [u'Rest', u'P1', u'm3', u'M3', u'P5', u'm6', u'M6', u'P8',
                       u'-m3', u'-M3', u'-P5', u'-m6', u'-M6', u'-P8']
        potential_consonances = [u'P4', u'-P4', u'A4', u'-A4', u'd5', u'-d5']

        for pair_index in combinations.columns:
            for j, event in enumerate(combinations[pair_index]):
                if event in consonances:
                    combinations[pair_index].iloc[j] = nan
                elif event in potential_consonances:
                    combinations[pair_index[j]] = self.check_4s_5s(pair_index[1], combinations.index[j], event)
                # NB: all other events are either dissonant or don't qualify as interval onsets.

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)
        return self.make_return([six.u(x)[1:-1] for x in combinations], results)
