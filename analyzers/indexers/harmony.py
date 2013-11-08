#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/harmony.py
# Purpose:                Indexers for Harmonic Function
#
# Copyright (C) 2013 Christopher Antila
#
# Attribution: This module is based on the harrisonHarmony program, originally developed without
#              the VIS framework. It's licensed under the GPL3+; you can find the source code at
#              https://github.com/crantila/harrisonHarmony
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

Indexers for harmonic function.

This module is based on the harrisonHarmony program, originally developed without the VIS
framework. It's licensed under the GPL3+; you can find the source code at
https://github.com/crantila/harrisonHarmony
"""

import pandas
from music21 import key, pitch, interval, note
from vis.analyzers import indexer


# Symbols we'll use to identify things
# the harmonic functions
FUNC_SUB = u'Subdominant'
FUNC_TON = u'Tonic'
FUNC_DOM = u'Dominant'
FUNC_UNK = u'Unknown'
# roles
ROLE_BA = u'base'
ROLE_AG = u'agent'
ROLE_AS = u'associate'
ROLE_UN = u'unknown'
# relative voice positions
POS_LOW = u'lowest voice'
POS_MID = u'inner voice'
POS_HIH = u'highest voice'
POS_SOL = u'solo voice'
# conditions for function
COND_GUAR = u'guaranteed'
COND_LOW = u'if lowest voice'  # (if the lowest voice is ___, this is the function)
COND_PRES = u'if other present'  # (if ___ is also present, this is the function)
COND_FOLL = u'if followed by'  # (if ___ is followed by ___, this is the function)


def scale_degree_func(obj):
    """
    Given a note and its key, find the scale degree.

    In the input, the first element should be from the output of :class:`NoteRestIndexer`, and
    the second should be from the output of :class:`KeyIndexer`.

    Parameters
    ==========
    :param obj: Name of the pitch and its key.
    :type obj: :class:`pandas.Series` of ``unicode`` and 2-tuple of ``unicode``

    Returns
    =======
    :returns: The note its scale degree.
    :rtype: ``unicode``
    """
    perfect_intervals = ['1', '4', '5']

    # Make pitches for the tonic and the note-in-question; ensure the note is higher than tonic.
    # Then find the interval from tonic to note.
    the_tonic = pitch.Pitch(obj[1][0] + '4')
    the_note = pitch.Pitch(obj[0] + '5')
    the_interval = interval.notesToInterval(the_tonic, the_note).simpleName

    if 2 == len(the_interval):
        if 'M' == the_interval[0] or 'P' == the_interval[0]:
            post = the_interval[1]
        elif 'm' == the_interval[0]:
            post = '-' + the_interval[1]
        elif 'A' == the_interval[0]:
            post = '#' + the_interval[1]
        elif 'd' == the_interval[0]:
            if the_interval[1] in perfect_intervals:
                post = '-' + the_interval[1]
            else:
                post = '--' + the_interval[1]
        else:
            post = ""
    elif 3 == len(the_interval):
        if 'AA' == the_interval[0:2]:
            post = '##' + the_interval[2]
        elif 'dd' == the_interval[0:2]:
            post = '--' + the_interval[2]
        else:
            post = ''
    else:
        post = ''
    return post


def _pc_of_degree(tonic, sc_deg):
    """
    Given a tonic pitch class and a scale degree, return the scale degree's pitch class.

    :param tonic: Tonic pitch class.
    :type tonic: ``basestring``
    :param sc_deg: Scale degree.
    :type tonic: ``basestring``

    :returns: A note with the pitch class of the scale degree.
    :rtype: :class:`music21.note.Note`
    """
    # TODO: test this
    poss_pc = key.Key(tonic).pitchFromDegree(int(sc_deg[-1])).name
    ch_mod = sc_deg[:-1]
    if 0 < len(ch_mod):
        qual = ['A' for _ in xrange(len(ch_mod))]
        if '-' == ch_mod[0]:
            qual.extend(['-', '1'])
        else:
            qual.extend(['1'])
        interv = interval.Interval(''.join(qual))
        interv.noteStart = note.Note(poss_pc)
        poss_pc = interv.noteEnd
    return poss_pc


def _tonic_of_f6(tonic, sc_deg):
    """
    Given a tonic pitch class and a scale degree, reinterpret the note as scale degree flat-6,
    then return the pitch class of the applied tonic.

    :param tonic: Tonic pitch class of the prevailing key.
    :type tonic: ``basestring``
    :param sc_deg: Scale degree of the note in the prevailing key.
    :type tonic: ``basestring``

    :returns: The pitch class of the applied Tonic base.
    :rtype: ``basestring``
    """
    interv = interval.Interval('M3')
    interv.noteStart = _pc_of_degree(tonic, sc_deg)
    return interv.noteEnd.name


def _tonic_of_7(tonic, sc_deg):
    """
    Given a tonic pitch class and a scale degree, reinterpret the note as scale degree 7,
    then return the pitch class of the applied tonic.

    :param tonic: Tonic pitch class of the prevailing key.
    :type tonic: ``basestring``
    :param sc_deg: Scale degree of the note in the prevailing key.
    :type tonic: ``basestring``

    :returns: The pitch class of the applied Tonic base.
    :rtype: ``basestring``
    """
    interv = interval.Interval('m2')
    interv.noteStart = _pc_of_degree(tonic, sc_deg)
    return interv.noteEnd.name


def poss_func_func(obj):
    """
    Given a scale degree, its key, and the relative position of the note, find the possible
    harmonic functions and their contingencies.

    In the input, the first element should be from the output of :class:`ScaleDegreeIndexer`,
    the second should be from the output of :class:`KeyIndexer`, and the third should be of the
    type produced by PossFuncIndexer to indicate voice position (i.e., POS_LOW, POS_MID, POS_HIH,
    POS_SOL).

    Parameters
    ==========
    :param obj: Scale degree, its key, and its relative position (see below for examples).
    :type obj: :class:`pandas.Series`

    Returns
    =======
    :returns: The note its harmonic functions and their contingencies.
    :rtype: list of ``unicode``

    * Examples *
    ============
    >>> in_val = pandas.Series(['1', ('E', 'minor'), POS_LOW])
    >>> poss_func_func(in_val)
    [(('E', FUNC_TON, ROLE_BA, '1'), COND_GUAR, None)]

    >>> in_val = pandas.Series(['1', ('E', 'minor'), POS_MID])
    >>> poss_func_func(in_val)
    [(('E', FUNC_TON, ROLE_BA, '1'), COND_PRES, ('E', FUNC_TON, ROLE_AG, '3')),
     (('E', FUNC_TON, ROLE_BA, '1'), COND_PRES, ('E', FUNC_TON, ROLE_AG, '-3')),
     (('E', FUNC_SUB, ROLE_AS, '1'), COND_PRES, ('E', FUNC_SUB, ROLE_AG, '6')),
     (('E', FUNC_SUB, ROLE_AS, '1'), COND_PRES, ('E', FUNC_SUB, ROLE_AG, '-6')),
     (('E', FUNC_SUB, ROLE_AS, '1'), COND_LOW, ('E', FUNC_SUB, ROLE_BA, '4'))]
    """
    post = []
    # these should make it clearer what's going on
    sc_deg = obj[0]
    tonic = obj[1][0]
    vox_pos = obj[2]

    # Part 1: for possibilities in another key

    if 2 == len(sc_deg) and '-6' != sc_deg:
        if '#' == sc_deg[0]:
            # this might be an applied Dominant agent; ask ourselves what that means
            # NB: it's "minus 5" below because we subtract one to make (e.g.) "scale degree 5"
            #     mean "index 4", and subtract four more to transpose down a diatonic fifth
            applied_d = _tonic_of_7(tonic, sc_deg)
            post.append(((applied_d, FUNC_DOM, ROLE_AG, '7'), COND_FOLL, (applied_d, FUNC_TON, ROLE_BA, '1')))
        elif '-' == sc_deg[0]:
            # this might be an applied Subdominant agent; ask ourselves what that means
            # NB: it's "minus 6" below because we subtract one to make (e.g.) "scale degree 6"
            #     mean "index 5", and subtract five more to transpose down a diatonic sixth
            applied_sd = _tonic_of_f6(tonic, sc_deg)
            post.append(((applied_sd, FUNC_SUB, ROLE_AG, '-6'), COND_FOLL, (applied_sd, FUNC_DOM, ROLE_BA, '5')))

    # Part 2: for possibilities in this key

    # agent is always (and only ever) agent
    if sc_deg in ['3', '-3']:
        post.append(((tonic, FUNC_TON, ROLE_AG, sc_deg), COND_GUAR, ''))
    elif sc_deg in ['6', '-6']:
        post.append(((tonic, FUNC_SUB, ROLE_AG, sc_deg), COND_GUAR, ''))
    elif sc_deg in ['7', '-7']:
        post.append(((tonic, FUNC_DOM, ROLE_AG, sc_deg), COND_GUAR, ''))
    # for things that aren't the agent...
    elif sc_deg in ['1', '4', '5']:
        # base is base if in lowest voice
        if POS_LOW == vox_pos:
            if '1' == sc_deg:
                post.append(((tonic, FUNC_TON, ROLE_BA, sc_deg), COND_GUAR, ''))
            elif '4' == sc_deg:
                post.append(((tonic, FUNC_SUB, ROLE_BA, sc_deg), COND_GUAR, ''))
            elif '5' == sc_deg:
                post.append(((tonic, FUNC_DOM, ROLE_BA, sc_deg), COND_GUAR, ''))
        # here we get things that accumulate multiple functions
        else:
            put = None
            if '1' == sc_deg:
                put = [((tonic, FUNC_TON, ROLE_BA, sc_deg), COND_PRES, (tonic, FUNC_TON, ROLE_AG, "3")),
                       ((tonic, FUNC_TON, ROLE_BA, sc_deg), COND_PRES, (tonic, FUNC_TON, ROLE_AG, "-3")),
                       ((tonic, FUNC_SUB, ROLE_AS, sc_deg), COND_PRES, (tonic, FUNC_SUB, ROLE_AG, "6")),
                       ((tonic, FUNC_SUB, ROLE_AS, sc_deg), COND_PRES, (tonic, FUNC_SUB, ROLE_AG, "-6")),
                       ((tonic, FUNC_SUB, ROLE_AS, sc_deg), COND_LOW, (tonic, FUNC_SUB, ROLE_BA, '4'))]
            elif '4' == sc_deg:
                put = [((tonic, FUNC_SUB, ROLE_BA, sc_deg), COND_PRES, (tonic, FUNC_SUB, ROLE_AG, "6")),
                       ((tonic, FUNC_SUB, ROLE_BA, sc_deg), COND_PRES, (tonic, FUNC_SUB, ROLE_AG, "-6"))]
            elif '5' == sc_deg:
                put = [((tonic, FUNC_DOM, ROLE_BA, sc_deg), COND_PRES, (tonic, FUNC_DOM, ROLE_AG, "7")),
                       ((tonic, FUNC_DOM, ROLE_BA, sc_deg), COND_PRES, (tonic, FUNC_DOM, ROLE_AG, "-7")),
                       ((tonic, FUNC_TON, ROLE_AS, sc_deg), COND_PRES, (tonic, FUNC_TON, ROLE_AG, "3")),
                       ((tonic, FUNC_TON, ROLE_AS, sc_deg), COND_PRES, (tonic, FUNC_TON, ROLE_AG, "-3")),
                       ((tonic, FUNC_TON, ROLE_AS, sc_deg), COND_LOW, (tonic, FUNC_TON, ROLE_BA, '1'))]
            post.extend(put)
    elif '2' == sc_deg:
        post.append(((tonic, FUNC_DOM, ROLE_AS, sc_deg), COND_PRES, (tonic, FUNC_DOM, ROLE_AG, "7")))
        post.append(((tonic, FUNC_DOM, ROLE_AS, sc_deg), COND_PRES, (tonic, FUNC_DOM, ROLE_AG, "-7")))
        if POS_LOW != vox_pos:
            post.append(((tonic, FUNC_DOM, ROLE_AS, sc_deg), COND_LOW, (tonic, FUNC_DOM, ROLE_BA, '5')))
    return post


def reconciliation_func(obj):
    """
    Given all the harmonic functional possibilities for all notes at a moment, determine for each
    note which is the most likely harmonic function. Voices must be given in descending order, so
    the voice at index 0 is the highest, and at index -1 is the lowest.

    Parameters
    ==========
    :param obj: The note its harmonic functions and their contingencies (the output of
        :func:`poss_func_func`).
    :type obj: :class:`pandas.Series`

    Returns
    =======
    :returns: A list of the the decided harmonic function (key, function, role, degree).
    :rtype: 4-tuple of ``unicode``

    * Examples *
    ============
    >>> res = [poss_func_func(('D', '1', POS_HIH)),
               poss_func_func(('D', '5', POS_MID)),
               poss_func_func(('D', '3', POS_MID)),
               poss_func_func(('D', '1', POS_LOW))]
    >>> reconciliation_func(res)
    [('D', FUNC_TON, ROLE_BA, '1'),
     ('D', FUNC_TON, ROLE_AS, '5'),
     ('D', FUNC_TON, ROLE_AG, '3'),
     ('D', FUNC_TON, ROLE_BA, '1')]
    """
    #print(str(obj))  # DEBUG
    post = [None for _ in xrange(len(obj))]
    # index of the bass voice
    bass_i = len(obj) - 1
    # This will hold the number of times we've been through the loop, and if we haven't come up
    # with an answer by safe_guard_limit, then we're probably not going to, so we'll just quit.
    safe_guard = 0
    safe_guard_limit = 100
    # Infinite Loop! Supposed to end when all of "post" has something useful.
    while True:
        safe_guard += 1
        # if lowest voice is undecided, decide the lowest voice
        if post[bass_i] is None:
            # look for a guaranteed function
            for possibility in obj[bass_i]:
                if COND_GUAR == possibility[1]:
                    post[bass_i] = possibility[0]
            # if we still don't have an answer...
            if post[bass_i] is None:
                # go through the list of possibilities again
                for possibility in obj[bass_i]:
                    # If a function is contingent on something else being present, look
                    # for "something else."
                    if COND_PRES == possibility[1]:
                        # we search the list of things we already know for sure
                        for confirmed in post:
                            if confirmed == possibility[2]:
                                post[bass_i] = possibility[0]
                                break
        # Go through upper voices.
        # We have to remember i numbers, so the voices are put in "post" in the right order.
        for i, func in obj[:-1].iteritems():
            # Do we still need to solve this i?
            # Look for functions that depend on the bass note.
            if post[i] is None:
                # if we have a confirmed bass note
                if post[bass_i] is not None:
                    # look through each of the conditions
                    for possibility in func:
                        # If a condition depends on the bass voice, and the bass voice is that
                        # function, assign it!
                        if COND_LOW == possibility[1] and post[bass_i] == possibility[2]:
                            post[i] = possibility[0]
            # Do we still need to solve this i?
            # Look for functions that depend on a non-bass note.
            if post[i] is None: # same algorithm as for bass notes
                for possibility in func:
                    if COND_PRES == possibility[1]:
                        for confirmed in post:
                            if confirmed == possibility[2]:
                                post[i] = possibility[0]
            # NB: The IsGuaranteed must go last, because of complicated reasons where it may not be
            # guaranteed. Do we still need to solve this i?
            # Look for a guaranteed function,
            if post[i] is None:
                for possibility in func:
                    if COND_GUAR == possibility[1]:
                        post[i] = possibility[0]
                        break
        # loop-finish check: do all the elements of "post" have something useful?
        if safe_guard > safe_guard_limit or 0 == post.count(None):
            # TODO: Make this more elegant...
            # I should be able to assign an "unknown" function/action as something other than a
            # last resort (i.e., I know in advance when it won't work).
            for i in xrange(len(post)):
                if post[i] is None:
                    #print('i: ' + str(i))  # DEBUG
                    #print('post: ' + str(post))  # DEBUG
                    #print('obj[i]: ' + str(obj[i]))  # DEBUG
                    # NB: this gives the key and scale degree of the first possibility; even though
                    # we can't confirm the key or anything, at least this way we don't lose what
                    # information we have
                    post[i] = (obj[i][0][0][0], FUNC_UNK, ROLE_UN, obj[i][0][0][3])
            return post


def chord_label_func(obj):
    """
    Given all the harmonic functions of all the notes at a moment, prepare a label

    Parameters
    ==========
    :param obj: A list of the the decided harmonic function (key, function, role, degree), as the
        output of :func:`reconciliation_func`.
    :type obj: :class:`pandas.Series`

    Returns
    =======
    :returns: A symbol for the harmonic functions present at the moment. Note that, if there is a
        superscript, the order of functions is S, T, D, U.
    :rtype: ``unicode``

    * Examples *
    ============
    >>> in_val = [('D', FUNC_TON, ROLE_BA, '1'),
                  ('D', FUNC_TON, ROLE_AS, '5'),
                  ('D', FUNC_TON, ROLE_AG, '3'),
                  ('D', FUNC_TON, ROLE_BA, '1')]
    >>> chord_label_func(in_val)
    u'T(1)'
    
    >>> in_val = [('D', FUNC_TON, ROLE_BA, '1'),
                  ('D', FUNC_TON, ROLE_AG, '3'),
                  ('D', FUNC_SUB, ROLE_AG, '6'),
                  ('D', FUNC_TON, ROLE_BA, '1')]
    >>> chord_label_func(in_val)
    u'T^S(1)'
    
    >>> in_val = [('D', FUNC_UNK, ROLE_UN, '2'),
                  ('D', FUNC_TON, ROLE_AG, '3'),
                  ('D', FUNC_SUB, ROLE_AG, '6'),
                  ('D', FUNC_TON, ROLE_BA, '1')]
    >>> chord_label_func(in_val)
    u'T^S/U(1)'
    """
    bass_func = unicode(obj[len(obj) - 1][1])
    bass_degree = unicode(obj[len(obj) - 1][3])
    # find the functions of upper voices
    upper_things = [False for _ in xrange(4)]  # boolean for whether there is S, T, D, U in upper
    for _, func_note in obj[:-1].iteritems():
        if all(upper_things):
            break
        elif FUNC_SUB == func_note[1] and FUNC_SUB != bass_func:
            upper_things[0] = True
        elif FUNC_TON == func_note[1] and FUNC_TON != bass_func:
            upper_things[1] = True
        elif FUNC_DOM == func_note[1] and FUNC_DOM != bass_func:
            upper_things[2] = True
        elif FUNC_UNK == func_note[1] and FUNC_UNK != bass_func:
            upper_things[3] = True
    # make the letters for upper voices
    upper_funcs = []
    if upper_things[0] is True:
        upper_funcs.append(u'S')
    if upper_things[1] is True:
        upper_funcs.append(u'T')
    if upper_things[2] is True:
        upper_funcs.append(u'D')
    if upper_things[3] is True:
        upper_funcs.append(u'U')
    if 0 == len(upper_funcs):
        return bass_func[0] + u'(' + bass_degree + u')'
    else:
        return bass_func[0] + u'^' + u'/'.join(upper_funcs) + u'(' + bass_degree + u')'


class ScaleDegreeIndexer(indexer.Indexer):
    """
    Given the results of :class:`~vis.analyzers.indexers.noterest.NoteRestIndexer` and
    :class:`~vis.analyzers.indexers.key.KeyIndexer`, turn the notes into scale degrees (Rest tokens
    are ignored).
    """

    required_score_type = pandas.Series
    possible_settings = []
    default_settings = {}

    def __init__(self, score, settings=None):
        """
        Parameters
        ==========
        :param score: A list of the :class:`KeyIndexer` and :class:`NoteRestIndexer` results. The
            result of :class:`KeyIndexer` should always be the *last* element, so that the index
            of each scale-degree index corresponds to that of the note-and-rest index from which
            it was produced.
        :type score: ``list`` of :class:`pandas.Series`

        :param settings: There are no required settings, so you may omit this.
        :type settings: ``dict`` or :const:`None`

        Raises
        ======
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(ScaleDegreeIndexer, self).__init__(score, None)
        self._indexer_func = scale_degree_func

    def run(self):
        """
        Make a new index of the piece that essentially converts each note name into a scale
        degree.

        Each scale degree is a string. Examples include ``'1'``, ``'#4'`` ``'-6'`` and so on.

        Returns
        =======
        :returns: A list of the new indices. The index of each :class:`Series` corresponds to the index of
            the :class:`Series` used to generate it.
        :rtype: ``list`` of :class:`pandas.Series`
        """
        # We'll need to send the indexer function pairs of Series: each Series and the last one.
        # For a four-part piece, this would be:
        # [a, b, c, d, e] ==> [[a, e], [b, e], [c, e], [d, e]]
        len_score = len(self._score) - 1  # it's really the index of the last element
        combinations = [(x, len_score) for x in xrange(len_score)]
        return self._do_multiprocessing(combinations)


class PossFuncIndexer(indexer.Indexer):
    """
    Given a scale degree and its key, produce a list of the possible harmonic functions and the
    contingencies on which they would rely.
    """

    required_score_type = pandas.Series
    possible_settings = []
    default_settings = {}

    def __init__(self, score, settings=None):
        """
        Parameters
        ==========
        :param score: A list of the :class:`KeyIndexer` and :class:`ScaleDegreeIndexer` results.
            The result of :class:`KeyIndexer` should always be the *last* element, so that the
            index of each functional-possibility index corresponds to that of the scale-degree
            index from which it was produced.
        :type score: ``list`` of :class:`pandas.Series`

        :param settings: There are no required settings, so you may omit this.
        :type settings: ``dict`` or :const:`None`

        Raises
        ======
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(PossFuncIndexer, self).__init__(score, None)
        self._indexer_func = poss_func_func

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        :returns: A list of the new indices. The index of each Series corresponds to the index of
            the Part used to generate it, in the order specified to the constructor. Each element
            in the Series is a basestring.
        :rtype: :obj:`list` of :obj:`pandas.Series`
        """
        # We'll need to send the indexer function triplets of Series: each Series and the last one,
        # plus one we make up depending on the voice's relative position.
        # For a four-part piece, where:
        # - a through d are ScaleDegreeIndexer outputs
        # - e is the KeyIndexer output
        # - f through i are "low", "middle", "high", and "solo" voice positions, respectively
        # [a, b, c, d, e, f, g, h, i] ==> [[a, e, h], [b, e, g], [c, e, g], [d, e, f]]

        # helper index values
        ind_key = len(self._score) - 1
        ind_low = ind_key + 1
        ind_mid = ind_key + 1
        ind_high = ind_key + 1
        ind_solo = ind_key + 1

        # add the voice-position indices
        v_pos_inds = [pandas.Series([pos]) for pos in [POS_LOW, POS_MID, POS_HIH, POS_SOL]]
        self._score.extend(v_pos_inds)

        # make the list of indices
        # TODO: test this with a mock
        if 1 == ind_key:
            combinations = [(0, ind_key, ind_solo)]
        elif 2 == ind_key:
            combinations = [(0, ind_key, ind_high),
                            (1, ind_key, ind_low)]
        else:
            combinations = [(0, ind_key, ind_high)]
            combinations.extend([(x, ind_key, ind_mid) for x in xrange(1, ind_key - 1)])
            combinations.extend([(ind_key - 1, ind_key, ind_low)])

        return self._do_multiprocessing(combinations)


class ChooseFuncIndexer(indexer.Indexer):
    """
    Knowing the possible functions of all the notes sounding at a moment, this indexer reconciles
    the requirements for each note and decides on its function (or labels as "unknown").
    """

    required_score_type = pandas.Series
    possible_settings = []
    default_settings = {}

    def __init__(self, score, settings=None):
        """
        Parameters
        ==========
        :param score: A list of the results from :class:`PossFuncIndexer`.
        :type score: ``list`` of :class:`pandas.Series`

        :param settings: There are no required settings, so you may omit this.
        :type settings: ``dict`` or :const:`None`

        Raises
        ======
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(ChooseFuncIndexer, self).__init__(score, None)
        self._indexer_func = reconciliation_func

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        :returns: A list of the new indices. The index of each Series corresponds to the index of
            the Part used to generate it, in the order specified to the constructor. Each element
            in the Series is a basestring.
        :rtype: :obj:`list` of :obj:`pandas.Series`
        """
        # all parts at once
        combinations = [x for x in xrange(len(self._score))]
        return self._do_multiprocessing(combinations)


class ChordLabelIndexer(indexer.Indexer):
    """
    Knowing the functions of all voices at a moment, prepare a label.
    """

    required_score_type = pandas.Series
    possible_settings = []
    default_settings = {}

    def __init__(self, score, settings=None):
        """
        Parameters
        ==========
        :param score: A list of the results from :class:`ChooseFuncIndexer`.
        :type score: ``list`` of :class:`pandas.Series`

        :param settings: There are no required settings, so you may omit this.
        :type settings: ``dict`` or :const:`None`

        Raises
        ======
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(ChordLabelIndexer, self).__init__(score, None)
        self._indexer_func = chord_label_func

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        :returns: A list of the new indices. The index of each Series corresponds to the index of
            the Part used to generate it, in the order specified to the constructor. Each element
            in the Series is a basestring.
        :rtype: :obj:`list` of :obj:`pandas.Series`
        """
        # all parts at once
        combinations = [x for x in xrange(len(self._score))]
        return self._do_multiprocessing(combinations)
