#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/dissonance.py
# Purpose:                Indexers related to dissonance.
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

Indexers related to dissonance:

* :class:`DissonanceIndexer` removes non-dissonant intervals.
* :class:`SuspensionIndexer` distinguishes suspensions from other dissonances.

**Forward Fill the IntervalIndexer**

The :class:`DissonanceIndexer` and :class:`SuspensionIndexer` require you to "forward fill" the
:class:`IntervalIndexer`. You may do this in a variety of ways, including this, where ``input_df``
is the DataFrame you wish to modify::

    input_df = input_df.T
    new_intervals = input_df.loc['interval.IntervalIndexer'].fillna(method='ffill', axis=1)
    new_multiindex = [('interval.IntervalIndexer', x) for x in list(new_intervals.index)]
    new_intervals.index = pandas.MultiIndex.from_tuples(new_multiindex)
    input_df.update(new_intervals)
    input_df = input_df.T
"""

# disable "string statement has no effect" warning---they do have an effect with Sphinx!
# pylint: disable=W0105

from numpy import nan, isnan
import pandas
from vis.analyzers import indexer
from .interval import interval_to_int


# Used by susp_ind_func() as the labels for suspensions and other dissonances. They're module-level
# so they can be changed, and possibly withstand multiprocessing... and so the unit tests can
# modify them to more easily check the classification.
_SUSP_USUSP_LABEL = 'USUSP'  # for upper-voice suspensions
_SUSP_LSUSP_LABEL = 'LSUSP'  # for lower-voice suspensions
_SUSP_OTHER_LABEL = nan
_SUSP_NODISS_LABEL = nan


def susp_ind_func(obj):
    # TODO: what about rests?
    """
    Indexer function for the :class:`SuspensionIndexer`. This function processes all parts, and
    returns a :class:`Series` that should be used as a row for the :class:`DataFrame` that will be
    the resulting index returned by :class:`SuspensionIndexer`.

    The suspect dissonances occur in the second row.

    :param obj: A 3-element iterable with adjacent rows from the indexer's requested
        :class:`DataFrame`. If the first row has index ``i`` in the :class:`DataFrame`, the second
        row should have index ``i + 1``, and the third ``i + 2``.
    :type obj: 3-tuple of :class:`pandas.Series`

    :returns: A row for the new index's :class:`DataFrame`. The row's proper offset is that of the
        *second* :class:`Series` in the ``obj`` argument.
    :rtype: :class:`pandas.Series` of unicode string
    """
    # Description of the variables:
    # - x: melodic interval of lower part into suspension, not unison (upper part is unison)
    # - d: dissonant harmonic interval
    # - y: melodic interval of lower part out of suspension (upper part is -2)
    # - z: d-y if y >= 1 else d-y-2 (it's the resolution vert-int)

    # for better legibility (i.e., shorter lines)
    diss_ind = u'dissonance.DissonanceIndexer'
    horiz_int_ind = u'interval.HorizontalIntervalIndexer'
    int_ind = u'interval.IntervalIndexer'

    row_one, row_two, row_three = obj

    # this avoids the list's reallocation penalty if we used append()
    post = [None for _ in xrange(len(row_one[diss_ind].index))]
    for post_i, combo in enumerate(row_one[diss_ind].index):
        lower_i = int(combo.split(u',')[1])
        # is there a dissonance?
        if (isinstance(row_two[diss_ind][combo], basestring) or
            (not isnan(row_two[diss_ind][combo]))):
            # set x (melodic of lower part into diss)
            x = interval_to_int(row_one[horiz_int_ind][lower_i])
            # set d (the dissonant vertical interval)
            d = interval_to_int(row_two[diss_ind][combo][-1:])
            # set y (lower part melodic out of diss)
            y = interval_to_int(row_two[horiz_int_ind][lower_i])
            # set z (vert int after diss)
            z = interval_to_int(row_three[int_ind][combo])
            # deal with z
            if 1 == x and -2 == y:
                post[post_i] = _SUSP_LSUSP_LABEL
            elif 1 != x and ((y >= 1 and d - y == z) or  # if the lower voice ascends out of d
                             (d - y - 2 == z)):  # if the lower voice descends out of d
                post[post_i] = _SUSP_USUSP_LABEL
            else:
                post[post_i] = _SUSP_OTHER_LABEL
        else:
            post[post_i] = _SUSP_NODISS_LABEL
    return pandas.Series(post, index=row_one[diss_ind].index)


class DissonanceIndexer(indexer.Indexer):
    """
    Remove consonant intervals. All remaining intervals are a "dissonance." Refer to the
    :const:`CONSONANCES` constant for a list of consonances. A perfect fourth is sometimes
    consonant---refer to the ``'special_P4'`` setting for more information.
    """

    CONSONANCES = [u'P1', u'm3', u'M3', u'P5', u'm6', u'M6', u'P8']
    _CONSONANCE_MAKERS = [u'm3', u'M3', u'm6', u'M6']

    required_score_type = 'pandas.DataFrame'
    default_settings = {'special_P4': True, 'special_d5': True}
    possible_settings = ['special_P4', 'special_d5']
    """
    :keyword bool 'special_P4': Whether to account for the Perfect Fourth's "special"
        characteristic of being a dissonance only when no major or minor third or sixth appears
        below it. If this is ``True``, an additional indexing process is run that removes all
        fourths "under" which the following intervals appear: m3, M3, m6, M6.
    :keyword bool 'special_P5': Whether to account for the Diminished Fifth's "special"
        characteristic of being consonant when a Major Sixth appears at any point below the
        lowest note.
    """

    def __init__(self, score, settings=None):
        """
        :param score: The output from :class:`~vis.analyzers.indexers.interval.IntervalIndexer`.
            You *must* include interval quality and *must not* use compound intervals.
        :type score: :class:`pandas.DataFrame`
        :param NoneType settings: There are no settings.

        .. warning:: The :class:`DissonanceIndexer` requires the results of the
            :class:`IntervalIndexer` to have been "forward filled," or there will be errors. Do not
            "forward fill" other indices.

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        self._settings = {'special_P4': DissonanceIndexer.default_settings['special_P4'],
                          'special_d5': DissonanceIndexer.default_settings['special_d5']}
        if settings is not None:  # TODO: test this stuff
            if u'special_P4' in settings:
                self._settings[u'special_P4'] = settings[u'special_P4']
            if 'special_d5' in settings:
                self._settings['special_d5'] = settings['special_d5']
        super(DissonanceIndexer, self).__init__(score, None)

    @staticmethod
    def nan_consonance(simul):
        """
        Used internally by the :class:`DissonanceIndexer`.

        Convert all "consonant" values to nan. The "consonant" intervals are those contained in
        :const:`DissonanceIndexer.CONSONANCES`.

        :param simul: A simultaneity with arbitrary vertical intervals.
        :type simul: :class:`pandas.Series`

        :returns: A :class:`Series` of the same length, where all "consonances" have been replaced
            with nan.
        :rtype: :class:`pandas.Series`
        """
        return simul.map(lambda x: nan if x in DissonanceIndexer.CONSONANCES else x)

    @staticmethod
    def special_fourths(simul):
        """
        Used internally by the :class:`DissonanceIndexer`.

        Replace all consonant fourths in a :class:`Series` with nan. The method checks each part
        combination and, if it finds a ``'P4'``, checks all part combinations for a major or minor
        third or sixth sounding below the lower note of the fourth.

        For example, consider the following simultaneity:

        +------------------+----------+
        | Part Combination | Interval |
        +==================+==========+
        | 0,1              | M3       |
        +------------------+----------+
        | 0,2              | P4       |
        +------------------+----------+
        | 0,3              | M3       |
        +------------------+----------+
        | 1,2              | M3       |
        +------------------+----------+
        | 1,3              | M3       |
        +------------------+----------+
        | 2,3              | P8       |
        +------------------+----------+

        On encountering ``'P4'`` in the ``'0,2'`` part combination, :meth:`_special_fourths` only
        looks at the ``'2,3'`` combination for a third or sixth. Finding an octave, this fourth
        is considered "dissonant," and therefore retained.

        For this reason, it's very important that the index has good part-combination labels that
        follow the ``'int,int'`` format, as outputted by the :class:`IntervalIndexer`.
        """
        post = []
        for combo in simul.index:
            if u'P4' == simul.loc[combo]:
                lower_voice = combo.split(u',')[1]
                investigate_these = []
                for possibility in simul.index:
                    if possibility.split(u',')[0] == lower_voice:
                        investigate_these.append(possibility)
                found_one = False
                for possibility in investigate_these:
                    if simul.loc[possibility] in DissonanceIndexer._CONSONANCE_MAKERS:
                        found_one = True
                        break
                if found_one:
                    post.append(nan)
                else:
                    post.append(simul.loc[combo])
            else:
                post.append(simul.loc[combo])
        return pandas.Series(post, index=simul.index)

    @staticmethod
    def special_fifths(simul):
        """
        Used internally by the :class:`DissonanceIndexer`.

        Replace all consonant fifths in a :class:`Series` with nan. The method checks each part
        combination and, if it finds a ``'d5'``, checks all part combinations for a major sixth
        sounding below the lower note of the fifth.

        For example, consider the following simultaneity:

        +------------------+----------+
        | Part Combination | Interval |
        +==================+==========+
        | 0,1              | M3       |
        +------------------+----------+
        | 0,2              | d5       |
        +------------------+----------+
        | 0,3              | M3       |
        +------------------+----------+
        | 1,2              | M3       |
        +------------------+----------+
        | 1,3              | M3       |
        +------------------+----------+
        | 2,3              | P8       |
        +------------------+----------+

        On encountering ``'d5'`` in the ``'0,2'`` part combination, :meth:`_special_fourths` only
        looks at the ``'2,3'`` combination for a major sixth. Finding an octave, this fifth
        is considered "dissonant," and therefore retained.

        For this reason, it's very important that the index has good part-combination labels that
        follow the ``'int,int'`` format, as outputted by the :class:`IntervalIndexer`.
        """
        post = []
        for combo in simul.index:
            if u'd5' == simul.loc[combo]:
                lower_voice = combo.split(u',')[1]
                investigate_these = []
                for possibility in simul.index:
                    if possibility.split(u',')[0] == lower_voice:
                        investigate_these.append(possibility)
                found_one = False
                for possibility in investigate_these:
                    if 'M6' == simul.loc[possibility]:  # in DissonanceIndexer._CONSONANCE_MAKERS:
                        found_one = True
                        break
                if found_one:
                    post.append(nan)
                else:
                    post.append(simul.loc[combo])
            else:
                post.append(simul.loc[combo])
        return pandas.Series(post, index=simul.index)

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
        >>> the_dissonances = DissonanceIndexer(the_notes).run()
        >>> the_intervals['dissonance.DissonanceIndexer']['5,6']
        (Series with only the dissonant intervals between first and second clarinet)
        """
        post = self._score['interval.IntervalIndexer']
        if self._settings[u'special_P4'] is True:
            post = post.apply(DissonanceIndexer.special_fourths, axis=1)
        if self._settings[u'special_d5'] is True:
            post = post.apply(DissonanceIndexer.special_fifths, axis=1)  # TODO: test this branch works
        post = post.apply(DissonanceIndexer.nan_consonance, axis=1)
        return self.make_return([x for x in post.columns],
                                [post[x] for x in post.columns])


class SuspensionIndexer(indexer.Indexer):
    """
    Mark dissonant intervals as a suspension or another dissonance.

    Inputted results from the :mod:`interval` module require the same settings as were given to
    the :class:`DissonanceIndexer.
    """

    required_score_type = 'pandas.DataFrame'
    """
    Depending on how this indexer works, you must provide a :class:`DataFrame`, a :class:`Score`,
    or list of :class:`Part` or :class:`Series` objects. Only choose :class:`Part` or
    :class:`Series` if the input will always have single-integer part combinations (i.e., there are
    no combinations---it will be each part independently).
    """

    possible_settings = [u'suspension_label', u'other_label']
    """
    You may change the words used to label suspensions and other dissonances.

    :keyword 'suspension_label': The string used to label suspensions.
    :type 'suspension_label': basestring
    :keyword 'other_label': The string used to label other dissonances.
    :type 'other_label': basestring
    """

    default_settings = {u'suspension_label': u'susp', u'other_label': u''}

    # Text for the RuntimeError raised when a score has fewer than 3 event offsets.
    _TOO_SHORT_ERROR = u'SuspensionIndexer: input must have at least 3 events'

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. You must provide a
            :class:`DataFrame` with results from the
            :class:`~vis.analyzers.indexers.interval.IntervalIndexer`, the
            :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`, and the
            :class:`DissonanceIndexer. The :class:`DataFrame` may contain results from additional
            indexers, which will be ignored.
        :type score: :class:`pandas.DataFrame`
        :param settings: This indexer has no settings, so this is ignored.
        :type settings: NoneType

        .. warning:: The :class:`SuspensionIndexer` requires the results of the
            :class:`IntervalIndexer` to have been "forward filled," or there will be errors. Do not
            "forward fill" other indices.

        .. note:: The :meth:`run` method will raise a :exc:`KeyError` if ``score`` does not contain
            results from the required indices.

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the ``score`` argument has fewer than three event offsets,
            which is the minimum required for a suspension (preparation, dissonance, resolution).
            An exception here prevents an error later.
        """
        super(SuspensionIndexer, self).__init__(score, None)
        if len(score.index) < 3:
            raise RuntimeError(SuspensionIndexer._TOO_SHORT_ERROR)
        self._indexer_func = susp_ind_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` with suspensions labeled *and* all inputted indices.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`KeyError` if the ``score`` given to the constructor was an
            improperly-formatted :class:`DataFrame` (e.g., it does not contain results of the
            required indexers, or the columns do not have a :class:`MultiIndex`).
        """
        # NB: it's actually susp_ind_func() that raises the KeyError

        # this avoids the list's reallocation penalty if we used append()
        post = [None for _ in xrange(len(self._score.index))]
        for i in xrange(len(self._score.index) - 2):
            post[i + 1] = susp_ind_func((self._score.iloc[i],
                                         self._score.iloc[i + 1],
                                         self._score.iloc[i + 2]))

        # Add post for the final two offsets in the piece. They obviously can't be suspensions,
        # since they wouldn't  be prepared or resolved. (Make sure we use the same index as the
        # other rows, or we'll have empty columns in the output).
        for i in [0, -1]:
            post[i] = pandas.Series([_SUSP_NODISS_LABEL for _ in xrange(len(post[1]))],
                                    index=post[1].index)

        # Convert from the list of Series into a DataFrame. Each inputted Series becomes a row.
        post = pandas.DataFrame({j: post[i] for i, j in enumerate(self._score.index)}).T

        # the part names are the column names
        post = self.make_return(list(post.columns), [post[i] for i in post.columns])
        return pandas.concat(objs=[self._score, post], axis=1, join='outer')
