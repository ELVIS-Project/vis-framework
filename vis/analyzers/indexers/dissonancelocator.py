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

Template for writing a new indexer. Use this class to help write a new :class`Indexer` subclass. \
The :class:`TemplateIndexer` does nothing, and should only be used by programmers.

.. note:: Follow these instructions to write a new :class:`Indexer` subclass:

    . Replace my name with yours in the "codeauthor" directive above.
    . Change the "Filename" and "Purpose" on lines 7 and 8.
    . Modify the "Copyright" on line 10 *or* add an additional copyright line immediately below.
    . Remove the ``# pylint: disable=W0613`` comment just before :func:`indexer_func`.
    . Rename the class.
    . Adjust :attr:`required_score_type`.
    . Add settings to :attr:`possible_settings` and :attr:`default_settings`, as required.
    . Rewrite the documentation for :meth:`__init__`.
    #. Rewrite the documentation for :meth:`~TemplateIndexer.run`.
    #. Rewrite the documentation for :func:`indexer_func`.
    #. Write all relevant tests for :meth:`__init__`, :meth:`~TemplateIndexer.run`, and \
        :func:`indexer_func`.
    #. Follow the instructions in :meth:`__init__` to write that method.
    #. Follow the instructions in :meth:`~TemplateIndexer.run` to write that method.
    #. Write a new :func:`indexer_func`.
    #. Ensure your tests pass, adding additional ones as required.
    #. Finally, run ``pylint`` with the VIS style rules.
"""

import six
import pandas
from numpy import nan, isnan  # pylint: disable=no-name-in-module
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
from music21 import stream
from vis.analyzers import indexer


def indexer_func(obj):      ##TODO: Revise this with Ryan, should it be a DataFrame with the voice
                            ##pair names in the multi-index? Probably.
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


class DissonanceLocatorIndexer(indexer.Indexer):
    """
    Indexer that locates vertical dissonances between pairs of voices in a piece. Used internally by
    :class:`DissonanceClassifier`. Categorizes intervals as consonant or dissonant and in the case
    of fourths (perfect or augmented) and diminished fifths it examines the other parts sounding with that
    fourth or fifth (if there are any) to see if the interval can be considered consonant.
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, settings=None):
        """
        :param score: The output from :class:`~vis.analyzers.indexers.interval.IntervalIndexer`.
            You *must* include interval quality and *must* use simple intervals.
        :type score:  :class:`pandas.DataFrame`.
        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: NoneType

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(DissonanceLocatorIndexer, self).__init__(score, None)

        self._indexer_func = indexer_func

    def cons_check(voice_pair_name, interval_index, suspect_diss):       # TODO: Complete this function with Ryan
        """
        This function evaluates whether P4's, A4's, and d5's should be considered consonant based
        whether or not the lower voice of the suspect_diss forms an interval that causes us to deem
        the fourth or fifth consonant, as determined by the cons_makers list below. The function
        should be called once for each potentially consonant fourth or fifth.

        :param voice_pair_name: Name of pair that has the potentially consonant fourth or fifth.
        :type voice_pair_name: String in the format '0,2' if the pair in question is S and T in an
            SATB texture.
        :param interval_index: Index of 4th or 5th being analyzed taken from the index of its voice
            pair.
        :type interval_index: Integer.
        :param suspect_diss: Interval name with quality and direction (i.e. nothing or '-') that
            corresponds to the fourth or fifth to be examined.
        :type suspect_diss: String.
        """
        cons_makers = [('P4', [u'm3', u'M3', u'P5']), ('d5', [u'M6']), ('A4', [u'm3'])]
        diss_dura = interval.IntervalIndexer[voice_pair_index][interval_index].duration.quarterLength
        interval_end_index = interval_index + diss_dura
        cons_made = False   

        if '-' in suspect_diss:     # TODO: should .index go before .split? The result of the split
                                    # should be a string like '0,2' meaning soprano and tenor of an
                                    # SATB texture.
            lower_i = interval.IntervalIndexer[voice_pair_index].index.split(',')[0]
        else:
            lower_i = interval.IntervalIndexer[voice_pair_index].index.split(',')[1]

        for voice_combo in interval.IntervalIndexer
            if cons_made == True:
                break
            if voice_combo.index != voice_pair_name and lower_i in voice_comb.index.split(','):     # look at other pairs that have lower_i as one of their voices.
                for each_int in interval.IntervalIndexer[voice_combo]:      # look at each interval in qualifying voice pairs
                    e_ind = interval.IntervalIndexer[voice_combo][each_int].index   # e_ind = start offset of potential consonance maker
                    if e_ind >= interval_end_index:     # if the interval you're looking at begins at or after the end of the suspect_diss you've gone to far so move on to the next pair.
                        break
                    e_end_ind == e_ind + interval.IntervalIndexer[voice_combo].iloc[e_ind].duration.quarterLength   # find the end offset of the potential cons_maker you're looking at.
                    if e_end_ind <= interval_index:     # if it's before the the onset of the suspect_diss then move on to the next interval in the same voice pair.
                        continue
                    if ((e_ind >= interval_index and e_ind < interval_end_index) or     # if either the onset or end of the interval being examined is within the offset span of the suspect_diss, check this interval.
                        (e_end_ind > interval_index and e_end_ind <= interval_end_index)):
                        for x in cons_makers:       # depending on what suspect_diss is, check if this each_int is the corresponding list of consonance makers.
                            if x[0] in suspect_diss:
                                if '-' in suspect_diss:     # NB: Voice crossing in salvaging interval.
                                    if each_int[1:] in x[1]:
                                        cons_made = True
                                        break
                                else:                       # NB: No voice crossing in salvaging interval.
                                    if each_int in x[1]:
                                        cons_made = True
                                        break
                        if cons_made == True:       # as soon as you've found one consonance-making interval, stop looking for others.
                            break

        if cons_made == True:
            return NaN
        else:
            return ('D' + suspect_diss)     # This 'D' will let us know that the fourth or fifth analyzed turned out to be truly dissonant.

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` of the new indices. The columns have a :class:`MultiIndex`;
            refer to the example below for more details.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        >>> the_score = music21.converter.parse('sibelius_5-i.mei')
        >>> the_score.parts[5]
        (the first clarinet Part)
        >>> the_notes = NoteRestIndexer(the_score).run()
        >>> the_notes['noterest.NoteRestIndexer']['5']
        (the first clarinet Series)
        >>> the_intervals = IntervalIndexer(the_notes).run()
        >>> the_intervals['interval.IntervalIndexer']['5,6']
        (Series with vertical intervals between first and second clarinet)
        """

        # NOTE: We recommend indexing all possible voice combinations, whenever feasible.

        # To calculate all 2-part combinations:
        combinations = self._score['interval.IntervalIndexer']      # TODO: Check with Ryan. Should I pass the required settings here?

        ## The three lines below aren't needed since we're starting with the interval indexer results.
        # for left in xrange(len(self._score)):
        #     for right in xrange(left + 1, len(self._score)):
        #         combinations.append([left, right])


        CONSONANCES = [u'Rest', u'P1', u'm3', u'M3', u'P5', u'm6', u'M6', u'P8',
                       u'-m3', u'-M3', u'-P5', u'-m6', u'-M6', u'-P8']
        POTENTIAL_CONSONANCES = [u'P4', u'-P4', u'A4', u'-A4', u'd5', u'-d5']

        for j, voice_pair in enumerate(combinations):
            for k, interval in enumerate(voice_pair):
                if interval in CONSONANCES:
                    voice_pair[k] = NaN
                elif interval in POTENTIAL_CONSONANCES:
                    voice_pair[k] = cons_check(j, k, interval)
                # if the interval is a definite dissonance, just pass.






        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing.

        # Convert results to a DataFrame in the appropriate format, then return it. This will work
        # as written for nearly all cases, but refer to the documentation for make_return() for
        # more information. The string-slicing simply removes the ``'['`` and ``']'`` characters
        # that appear because each combination is a list.
        return self.make_return([six.u(x)[1:-1] for x in combinations], results)
