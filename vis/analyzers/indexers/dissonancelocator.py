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
import numpy
from numpy import nan, isnan  # pylint: disable=no-name-in-module
from music21 import stream
from vis.analyzers import indexer
import pdb

_d3q_label = 'Q'
_pass_dp_label = 'D'
_pass_rp_label = 'R'
_neigh_ln_label = 'L'
_neigh_un_label = 'U'
_susp_label = 'S'
_fake_susp_label = 'F'
_dim_fake_susp_label = 'f'
_ant_label = 'A'
_camb_label = 'C'
_chan_idiom_label = 'H'
_echappee = 'E'
_no_diss_label = '-'
_unexplainable = 'Z'
_only_diss_w_diss = 'O'
_consonances = ['P1', 'm3', 'M3', 'CP4', 'CA4', 'Cd5', 'P5', 'm6', 'M6', 'P8', '-m3', '-M3', 'C-P4',
                'C-A4', 'C-d5', '-P5', '-m6', '-M6', '-P8']
_nan_rest = [nan, 'Rest']
_ignored = (_consonances + _nan_rest)
_go_ons = [_no_diss_label, _unexplainable]
_char_del = dict.fromkeys(map(ord, 'AaDdMmP'), None)
diss_ind = u'dissonance.DissonanceLocator'
h_ind = u'interval.HorizontalIntervalIndexer'
bs_ind = u'metre.NoteBeatStrengthIndexer'
dur_ind = u'metre.DurationIndexer'
diss_types = u'dissonance.DissonanceTypes'


class DissonanceClassifier(indexer.Indexer):
    """
    Assigns a dissonance type name or a consonance label for each voice at each offset.
    """
    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, settings=None):
        """
        :param score: The output from the following indexers: Dissonance, HorizontalInterval,
        BeatStrength, and Duration. You must include interval quality and use simple intervals.
        :type score:  :class:`pandas.DataFrame`.
        :param settings: This indexer uses no settings, so this is ignored.
        :type settings: NoneType

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(DissonanceClassifier, self).__init__(score)

    def _set_horiz_invl(self, locindx, voice):
        """
        Assigns the horizontal interval of the passed voice at the indx passed.
        """
        if self._score.loc[locindx, (h_ind, voice)] in _nan_rest:
            horiz_int = self._score.loc[locindx, (h_ind, voice)] 
        else:
            horiz_int = int(self._score.loc[locindx, (h_ind, voice)], 10)

        return horiz_int

    def _set_note_dur(self, locindx, voice):
        """
        Assigns the duration of the passed voice at the indx passed. NB, can return a nan value if 
        the voice has no onset at the indx passed.
        """
        return self._score.loc[locindx, (dur_ind, voice)]

    def _set_note_bs(self, locindx, voice):
        """
        Assigns the beat strength of the passed voice at the indx passed. NB, returns zero if the
        voice has no onset at the indx passed.
        """
        return self._score.loc[locindx, (bs_ind, voice)]

    def _is_d3q(self, locindx, pair):
        """
        A legal "dissonant 3rd quarter" is a dissonant 1 on a weak half, approached by step
        from above and preceded by a 2 or longer, and continuing by step in the same direction.
        The suspect dissonance occurs at the indx passed.

        :returns: A string of the part number and a dissonance label or else returns False if this
                    dissonance type was not detected.
        :rtype: 5-tuple with (True, number of the upper voice, label for upper voice, number of the 
                    lower voice, label for the lower voice), or a singleton tuple (False,) if the
                    dissonance in question is not a d3q.
        """
        # Figure out the (iloc) indecies of the four-event window. 
        # temp = self._score[diss_ind][pair].iloc[:indx].last_valid_index()
        # if temp == None:
        #     return (False,)
        # ev1_ind = numpy.where(self._score[diss_ind].index == temp)[0][0]
        # temp = score[diss_ind][pair].iloc[ev2_ind + 1:].first_valid_index()
        # ev3_ind = numpy.where(score[diss_ind].index == temp)[0][0]
        # temp = score[diss_ind][pair].iloc[ev3_ind + 1:].first_valid_index()
        # ev4_ind = numpy.where(score[diss_ind].index == temp)[0][0]


        upper = pair.split(',')[0] # Upper voice variables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        # print 'a_temp: ' + str(a_temp)
        # a_ind = numpy.where(self._score[h_ind].index == a_temp)[0][0]
        # print 'a_ind: ' + str(a_ind)

        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper)
        dur_a = self._set_note_dur(a_ind, upper)
        dur_b = self._set_note_dur(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)


        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        # x_ind = numpy.where(self._score[h_ind].index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower)
        dur_x = self._set_note_dur(x_ind, lower)
        dur_y = self._set_note_dur(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)


        # TODO: make the beatstrength requirements dependent on the detected meter. Right now it is hard-coded for 4/2 meter.
        if bs_b == .25 and dur_a >= 2 and dur_b == 1 and a == -2 and b == -2: # Upper voice is d3q
            return (True, upper, _d3q_label, lower, _no_diss_label)            
        elif bs_y == .25 and dur_x >= 2 and dur_y == 1 and x == -2 and y == -2: # Lower voice is d3q
            return (True, upper, _no_diss_label, lower, _d3q_label)
        else: # The dissonance is not a d3q.
            return (False,)

    def _is_passing(self, locindx, pair):
        """
        A passing tone moves by step obliquely (i.e. the other voice stands still while this one moves)
        creating a dissonant interval, continues stepwise in the same direction without resting, AND
        satisfies one of the following:
         -it is on a weak 2, preceded by a 2 or longer, and its duration is one 2,  OR
         -it is on a weak quarter and its duration is one quarter or less,  OR
         -it is on a weak eighth and its duration is one eighth or less.
        """
        # Figure out the (iloc) indecies of the four-event window. 
        ev1_ind = self._score.loc[:locindx, (diss_ind, pair)].iloc[:-1].last_valid_index()
        if ev1_ind == None:
            return (False,)
        # temp = score[diss_ind][pair].iloc[indx + 1:].first_valid_index()
        # ev3_ind = numpy.where(score[diss_ind].index == temp)[0][0]
        # temp = score[diss_ind][pair].iloc[ev3_ind + 1:].first_valid_index()
        # ev4_ind = numpy.where(score[diss_ind].index == temp)[0][0]

        upper = pair.split(',')[0] # Upper voice variables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper)
        dur_a = self._set_note_dur(a_ind, upper)
        dur_b = self._set_note_dur(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)
        if dur_a < dur_b:
            a2_ind = self._score.loc[:a_ind, (h_ind, upper)].iloc[:-1].last_valid_index()
            if a2_ind != None:
                a2 = self._set_horiz_invl(a2_ind, upper)
                if a2 == 1:
                    dur_a2 = self._set_note_dur(a2_ind, upper)
                    dur_a += dur_a2

        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower)
        dur_x = self._set_note_dur(x_ind, lower)
        dur_y = self._set_note_dur(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)
        if dur_x < dur_y:
            x2_ind = self._score[h_ind][lower].iloc[:a_ind].iloc[:-1].last_valid_index()
            if x2_ind != None:
                x2 = self._set_horiz_invl(x2_ind, lower)
                if x2 == 1:
                    dur_x2 = self._set_note_dur(x2_ind, lower)
                    dur_x += dur_x2


        p = self._score.loc[ev1_ind, (diss_ind, pair)]

        # # Figure out the (iloc) indecies of the four-event window. 
        # temp = self._score.loc[:, (diss_ind, pair)].iloc[:indx].last_valid_index()
        # if temp == None:
        #     return (False,)
        # ev1_ind = numpy.where(self._score[diss_ind].index == temp)[0][0]
        # # temp = score[diss_ind][pair].iloc[indx + 1:].first_valid_index()
        # # ev3_ind = numpy.where(score[diss_ind].index == temp)[0][0]
        # # temp = score[diss_ind][pair].iloc[ev3_ind + 1:].first_valid_index()
        # # ev4_ind = numpy.where(score[diss_ind].index == temp)[0][0]

        # upper = pair.split(',')[0] # Upper voice variables
        # a_temp = self._score[h_ind][upper].iloc[:indx].last_valid_index()
        # a_ind = numpy.where(self._score[h_ind].index == a_temp)[0][0]
        # a = self._set_horiz_invl(a_ind, upper)
        # b = self._set_horiz_invl(indx, upper)
        # dur_a = self._set_note_dur(a_ind, upper)
        # dur_b = self._set_note_dur(indx, upper)
        # bs_b = self._set_note_bs(indx, upper)
        # if dur_a < dur_b:
        #     a2_temp = self._score[h_ind][upper].iloc[:a_ind].last_valid_index()
        #     if a2_temp != None:
        #         a2_ind = numpy.where(self._score[h_ind].index == a2_temp)[0][0]
        #         a2 = self._set_horiz_invl(a2_ind, upper)
        #         if a2 == 1:
        #             dur_a2 = self._set_note_dur(a2_ind, upper)
        #             dur_a += dur_a2

        # lower = pair.split(',')[1] # Lower voice variables
        # x_temp = self._score[h_ind][lower].iloc[:indx].last_valid_index()
        # x_ind = numpy.where(self._score[h_ind].index == x_temp)[0][0]
        # x = self._set_horiz_invl(x_ind, lower)
        # y = self._set_horiz_invl(indx, lower)
        # dur_x = self._set_note_dur(x_ind, lower)
        # dur_y = self._set_note_dur(indx, lower)
        # bs_y = self._set_note_bs(indx, lower)
        # if dur_x < dur_y:
        #     x2_temp = self._score[h_ind][lower].iloc[:a_ind].last_valid_index()
        #     if x2_temp != None:
        #         x2_ind = numpy.where(self._score[h_ind].index == x2_temp)[0][0]
        #         x2 = self._set_horiz_invl(x2_ind, lower)
        #         if x2 == 1:
        #             dur_x2 = self._set_note_dur(x2_ind, lower)
        #             dur_x += dur_x2


        # p = self._score[diss_ind][pair].iloc[ev1_ind]


        if p not in _consonances: # The dissonance is can't be a passing tone.
            return (False,)
        elif (((dur_b == 2 and bs_b == .25) or (dur_b <= 1 and bs_b == .125) or 
               (dur_b <= .5 and bs_b == .0625)) and dur_a >= dur_b and (y is nan or x == 1)):
            if a == -2 and b == -2: # upper voice is descending
                return (True, upper, _pass_dp_label, lower, _no_diss_label)
            elif a == 2 and b == 2: # upper voice is rising
                return (True, upper, _pass_rp_label, lower, _no_diss_label)
        elif (((dur_y == 2 and bs_y == .25) or (dur_y <= 1 and bs_y == .125)
               or (dur_y <= .5 and bs_y == .0625)) and dur_x >= dur_y and (b is nan or a == 1)):
            if x == -2 and y == -2: # lower voice descending
                return (True, upper, _no_diss_label, lower, _pass_dp_label)
            elif x == 2 and y == 2: # lower voice rising
                return (True, upper, _no_diss_label, lower, _pass_rp_label)
        
        return (False,) # The dissonance is not a passing tone.

    def _is_neighbour(self, locindx, pair):
        """
        A neighbour tone moves obliquely by step creating a dissonant interval, without resting, by
        changing direction and returning by step to the same note that preceded it AND meets one of
        the following requirements:
         -it is on a weak half, preceded by a half note or longer, and its duration is one half note, OR
         -it is on a weak quarter and its duration is one quarter or less, OR
         -it is on a weak eighth and its duration is one eighth or less.
        """
        # Figure out the (iloc) indecies of the four-event window. 
        ev1_ind = self._score.loc[:locindx, (diss_ind, pair)].iloc[:-1].last_valid_index()
        if ev1_ind == None:
            return (False,)
        # temp = score[diss_ind][pair].iloc[indx + 1:].first_valid_index()
        # ev3_ind = numpy.where(score[diss_ind].index == temp)[0][0]
        # temp = score[diss_ind][pair].iloc[ev3_ind + 1:].first_valid_index()
        # ev4_ind = numpy.where(score[diss_ind].index == temp)[0][0]

        upper = pair.split(',')[0] # Upper voice variables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper)
        dur_a = self._set_note_dur(a_ind, upper)
        dur_b = self._set_note_dur(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)

        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower)
        dur_x = self._set_note_dur(x_ind, lower)
        dur_y = self._set_note_dur(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)


        p = self._score.loc[ev1_ind, (diss_ind, pair)]

        if p not in _consonances: # The dissonance is can't be a neighbour tone.
            return (False,)
        elif (((dur_b == 2 and bs_b == .25) or (dur_b <= 1 and bs_b == .125)
               or (dur_b <= .5 and bs_b == .0625)) and dur_a >= dur_b and (y is nan or x == 1)):
            if a == 2 and b == -2: # upper neighbour in upper part
                return (True, upper, _neigh_un_label, lower, _no_diss_label)
            elif a == -2 and b == 2: # lower neighbour in upper part
                return (True, upper, _neigh_ln_label, lower, _no_diss_label)
        elif (((dur_y == 2 and bs_y == .25) or (dur_y <= 1 and bs_y == .125)
               or (dur_y <= .5 and bs_y == .0625)) and dur_x >= dur_y and (b is nan or a == 1)):
            if x == 2 and y == -2: # upper neighbour in lower part
                return (True, upper, _no_diss_label, lower, _neigh_un_label)
            elif x == -2 and y == 2: # lower neighbour in lower part
                return (True, upper, _no_diss_label, lower, _neigh_ln_label)
        
        return (False,) # The dissonance is not a neighbour tone.

    def _is_suspension(self, locindx, pair): # Address mm. 136 and 142.
        """
        A note is considered a suspension if it is sustained or reattacked on the same pitch while
        another voice enters or moves by step or by leap to create a dissonant interval AND:
         -its next move (the "resolution") is downwards by step without resting (it may restrike the
          same note before resolving, though), AND
         -the resolution is on a weaker beat than the dissonance, or, if the dissonant note is a whole
          note in duration, the resolution is on a weaker-or-equally-strong beat.
        """
        upper = pair.split(',')[0] # Upper-voice vairables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper) # NB b doesn't correspond to a note onset in upper-voice suspensions
        dur_a = self._set_note_dur(a_ind, upper)
        dur_b = self._set_note_dur(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)
        c_ind = 0
        c = 0
        c_temp = numpy.where(self._score[h_ind].index == locindx)[0][0]
        c_ind = self._score.loc[:, (h_ind, upper)].iloc[c_temp + 1:].first_valid_index()
        if c_ind != None:
            c = self._set_horiz_invl(c_ind, upper)
            bs_c = self._set_note_bs(c_ind, upper)

        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower) # NB y doesn't correspond to a note onset in lower-voice suspensions
        dur_x = self._set_note_dur(x_ind, lower)
        dur_y = self._set_note_dur(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)
        z_ind = 0
        z = 0
        z_temp = numpy.where(self._score[h_ind].index == locindx)[0][0]
        z_ind = self._score.loc[:, (h_ind, lower)].iloc[z_temp + 1:].first_valid_index()
        if z_ind != None:
            z = self._set_horiz_invl(z_ind, lower)
            bs_z = self._set_note_bs(z_ind, lower)


        # NB this may need to be tweaked for the edge case where a consonant 4th becomes a dissonant fourth suspension without being restruck.
        if (c != 0 and ((a == -2 and b is nan) or (a == 1 and b == -2)) and (bs_y > bs_c or (dur_a == 4 and bs_y >= bs_c))):
            return (True, upper, _susp_label, lower, _no_diss_label) # Susp in upper voice
        elif (z != 0 and ((x == -2 and y is nan) or (x == 1 and y == -2)) and (bs_b > bs_z or (dur_x == 4 and bs_b >= bs_z))):
            return (True, upper, _no_diss_label, lower, _susp_label) # Susp in lower voice
        return (False,)

    def _is_fake_suspension(self, locindx, pair): 
        """
        A fake suspension is moved to by step obliquely and becomes a dissonant suspension by being tied
        to a dissonant note (or followed by the same note) whose next move is down by step, with
        a duration of either:
         -a weak half, with the ensuing suspended note (or part of note) falling on the following
          downbeat, OR
         -(diminished fake suspension) a weak quarter, with the ensuing suspended note (or part of note)
          falling on the following strong quarter.
        """
        # upper = pair.split(',')[0] # Upper-voice indecies
        # a_temp = self._score[h_ind][upper].iloc[:indx].last_valid_index()
        # a_ind = numpy.where(self._score[h_ind].index == a_temp)[0][0]
        # c_ind = 0
        # c = 0   
        # c_temp = self._score[h_ind][upper].iloc[indx + 1:].first_valid_index()
        # if c_temp != None:
        #     c_ind = numpy.where(self._score[h_ind].index == c_temp)[0][0]
        #     c = self._set_horiz_invl(c_ind, upper)

        # lower = pair.split(',')[1] # Lower-voice indecies
        # x_temp = self._score[h_ind][lower].iloc[:indx].last_valid_index()
        # x_ind = numpy.where(self._score[h_ind].index == x_temp)[0][0]
        # z_ind = 0
        # z = 0   
        # z_temp = self._score[h_ind][lower].iloc[indx + 1:].first_valid_index()
        # if z_temp != None:
        #     z_ind = numpy.where(self._score[h_ind].index == z_temp)[0][0]
        #     z = self._set_horiz_invl(z_ind, lower)

        # a = self._set_horiz_invl(a_ind, upper) # Upper-voice vairables
        # b = self._set_horiz_invl(indx, upper)
        # dur_b = self._set_note_dur(indx, upper)
        # bs_b = self._set_note_bs(indx, upper)
        
        # x = self._set_horiz_invl(x_ind, lower) # Lower voice variables
        # y = self._set_horiz_invl(indx, lower)
        # dur_y = self._set_note_dur(indx, lower)
        # bs_y = self._set_note_bs(indx, lower)


        upper = pair.split(',')[0] # Upper-voice vairables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper) # NB b doesn't correspond to a note onset in upper-voice suspensions
        dur_b = self._set_note_dur(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)
        c_ind = 0
        c = 0
        c_temp = numpy.where(self._score[h_ind].index == locindx)[0][0]
        c_ind = self._score.loc[:, (h_ind, upper)].iloc[c_temp + 1:].first_valid_index()
        if c_ind != None:
            c = self._set_horiz_invl(c_ind, upper)

        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower) # NB y doesn't correspond to a note onset in lower-voice suspensions
        dur_y = self._set_note_dur(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)
        z_ind = 0
        z = 0
        z_temp = numpy.where(self._score[h_ind].index == locindx)[0][0]
        z_ind = self._score.loc[:, (h_ind, lower)].iloc[z_temp + 1:].first_valid_index()
        if z_ind != None:
            z = self._set_horiz_invl(z_ind, lower)

        if a == 2 or a == -2:
            if bs_b == .25 and ((b == -2 and dur_b > 2) or (b == 1 and dur_b == 2 and c == -2)):
                return (True, upper, _fake_susp_label, lower, _no_diss_label) # Fake susp in upper voice
            elif bs_b == .125 and ((b == -2 and dur_b > 1) or (b == 1 and dur_b == 1 and c == -2)):
                return (True, upper, _dim_fake_susp_label, lower, _no_diss_label) # Diminished fake susp in upper voice
        elif x == 2 or x == -2:
            if bs_y == .25 and ((y == -2 and dur_y > 2) or (y == 1 and dur_y == 2 and z == -2)):
                return (True, upper, _no_diss_label, lower, _fake_susp_label) # Fake susp in lower voice
            elif bs_y == .125 and ((y == -2 and dur_y > 1) or (y == 1 and dur_y == 1 and z == -2)):
                return (True, upper, _no_diss_label, lower, _dim_fake_susp_label) # Diminished fake susp in lower voice
        return (False,)

    def _is_anticipation(self, locindx, pair): # Pick up here and account for mm. 142 and 150.
        """
        An anticipation occurs on a weak quarter-note, is approached obliquely by step from above, and
        is followed immediately (i.e. on the strong quarter, which might be a downbeat or a weak half)
        by the same pitch.
        """
        # upper = pair.split(',')[0] # Upper-voice indecies
        # a_temp = self._score[h_ind][upper].iloc[:indx].last_valid_index()
        # a_ind = numpy.where(self._score[h_ind].index == a_temp)[0][0]

        # lower = pair.split(',')[1] # Lower-voice indecies
        # x_temp = self._score[h_ind][lower].iloc[:indx].last_valid_index()
        # x_ind = numpy.where(self._score[h_ind].index == x_temp)[0][0]

        # a = self._set_horiz_invl(a_ind, upper) # Upper-voice vairables
        # b = self._set_horiz_invl(indx, upper)
        # dur_b = self._set_note_dur(indx, upper)
        # bs_b = self._set_note_bs(indx, upper)
        
        # x = self._set_horiz_invl(x_ind, lower) # Lower voice variables
        # y = self._set_horiz_invl(indx, lower)
        # dur_y = self._set_note_dur(indx, lower)
        # bs_y = self._set_note_bs(indx, lower)


        upper = pair.split(',')[0] # Upper voice variables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper)
        dur_b = self._set_note_dur(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)

        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower)
        dur_y = self._set_note_dur(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)

        if (bs_b == .125 and a == -2 and b == 1 and dur_b == 1):
            return (True, upper, _ant_label, lower, _no_diss_label)
        elif (bs_y == .125 and x == -2 and y == 1 and dur_y == 1):
            return (True, upper, _no_diss_label, lower, _ant_label)
        return (False,)

    def _is_cambiata(self, locindx, pair):
        """
        A nota cambiata figure moves obliquely by descending step to a dissonant weak half or quarter,
        then skips down a third before ascending by step to the note skipped over.
        """
        # QUESTION: is b on a weak half even if it lasts a quarter note?

        # upper = pair.split(',')[0] # Upper-voice indecies
        # a_temp = self._score[h_ind][upper].iloc[:indx].last_valid_index()
        # a_ind = numpy.where(self._score[h_ind].index == a_temp)[0][0]
        # c_ind = 0
        # c = 0   
        # c_temp = self._score[h_ind][upper].iloc[indx + 1:].first_valid_index()
        # if c_temp != None:
        #     c_ind = numpy.where(self._score[h_ind].index == c_temp)[0][0]
        #     c = self._set_horiz_invl(c_ind, upper)

        # lower = pair.split(',')[1] # Lower-voice indecies
        # x_temp = self._score[h_ind][lower].iloc[:indx].last_valid_index()
        # x_ind = numpy.where(self._score[h_ind].index == x_temp)[0][0]
        # z_ind = 0
        # z = 0   
        # z_temp = self._score[h_ind][lower].iloc[indx + 1:].first_valid_index()
        # if z_temp != None:
        #     z_ind = numpy.where(self._score[h_ind].index == z_temp)[0][0]
        #     z = self._set_horiz_invl(z_ind, lower)

        # a = self._set_horiz_invl(a_ind, upper) # Upper-voice vairables
        # b = self._set_horiz_invl(indx, upper)
        # dur_b = self._set_note_dur(indx, upper)
        # bs_b = self._set_note_bs(indx, upper)
        
        # x = self._set_horiz_invl(x_ind, lower) # Lower voice variables
        # y = self._set_horiz_invl(indx, lower)
        # dur_y = self._set_note_dur(indx, lower)
        # bs_y = self._set_note_bs(indx, lower)

        upper = pair.split(',')[0] # Upper-voice vairables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper) # NB b doesn't correspond to a note onset in upper-voice suspensions
        dur_b = self._set_note_dur(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)
        c_ind = 0
        c = 0
        c_temp = numpy.where(self._score[h_ind].index == locindx)[0][0]
        c_ind = self._score.loc[:, (h_ind, upper)].iloc[c_temp + 1:].first_valid_index()
        if c_ind != None:
            c = self._set_horiz_invl(c_ind, upper)

        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower) # NB y doesn't correspond to a note onset in lower-voice suspensions
        dur_y = self._set_note_dur(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)
        z_ind = 0
        z = 0
        z_temp = numpy.where(self._score[h_ind].index == locindx)[0][0]
        z_ind = self._score.loc[:, (h_ind, lower)].iloc[z_temp + 1:].first_valid_index()
        if z_ind != None:
            z = self._set_horiz_invl(z_ind, lower)


        if (a == -2 and ((dur_b == 2 and bs_b == .25) or (dur_b == 1 and bs_b == .125) and b == -3 and c == 2)):
            return (True, upper, _camb_label, lower, _no_diss_label) # Cambiata in upper voice
        elif (x == -2 and ((dur_y == 2 and bs_y == .25) or (dur_y == 1 and bs_y == .125) and y == -3 and z == 2)):
            return (True, upper, _no_diss_label, lower, _camb_label) # Cambiata in lower voice
        return (False,)

    def _is_chanson_idiom(self, locindx, pair):
        """
        The chanson idiom dissonance consists of a seventh or second, struck simultaneously or
        obliquely on the 3rd quarter of a whole note, involving a quarter in one voice ("the active
        voice") and a duration extending past the next downbeat in the other voice ("the inactive
        voice"), such that:
         -the active voice, at the 3rd quarter, is approached by descending step and proceeds down
          by step on the 4th quarter note, sounding the same pitch-class as the inactive voice, then
          returns upwards by step to a whole note on the downbeat
         -the inactive voice is extended past the downbeat, becoming a dissonant suspension that
          resolves down by step.
        """

        # upper = pair.split(',')[0] # Upper-voice indecies
        # a_temp = self._score[h_ind][upper].iloc[:indx].last_valid_index()
        # a_ind = numpy.where(self._score[h_ind].index == a_temp)[0][0]
        # c_ind = 0
        # c = 0
        # dur_c = 0
        # c_temp = self._score[h_ind][upper].iloc[indx + 1:].first_valid_index()
        # d_ind = 0
        # dur_d = 0
        # if c_temp != None:
        #     c_ind = numpy.where(self._score[h_ind].index == c_temp)[0][0]
        #     c = self._set_horiz_invl(c_ind, upper)
        #     dur_c = self._set_note_dur(c_ind, upper)
        #     d_temp = self._score[h_ind][upper].iloc[c_ind + 1:].first_valid_index()
        #     if d_temp != None:
        #         d_ind = numpy.where(self._score[h_ind].index == d_temp)[0][0]
        #         dur_d = self._set_note_dur(d_ind, upper)

        # lower = pair.split(',')[1] # Lower-voice indecies
        # x_temp = self._score[h_ind][lower].iloc[:indx].last_valid_index()
        # x_ind = numpy.where(self._score[h_ind].index == x_temp)[0][0]
        # z_ind = 0
        # z = 0
        # dur_z = 0
        # z_temp = self._score[h_ind][lower].iloc[indx + 1:].first_valid_index()
        # z2_ind = 0
        # dur_z2 = 0
        # if z_temp != None:
        #     z_ind = numpy.where(self._score[h_ind].index == z_temp)[0][0]
        #     z = self._set_horiz_invl(z_ind, lower)
        #     dur_z = self._set_note_dur(z_ind, lower)
        #     z2_temp = self._score[h_ind][lower].iloc[z_ind + 1:].first_valid_index()
        #     if z2_temp != None:
        #         z2_ind = numpy.where(self._score[h_ind].index == z2_temp)[0][0]
        #         dur_z2 = self._set_note_dur(z2_ind, lower)

        # a = self._set_horiz_invl(a_ind, upper) # Upper-voice vairables
        # b = self._set_horiz_invl(indx, upper)
        # dur_b = self._set_note_dur(indx, upper)
        
        # x = self._set_horiz_invl(x_ind, lower) # Lower voice variables
        # y = self._set_horiz_invl(indx, lower)
        # dur_y = self._set_note_dur(indx, lower)

        diss = int(self._score.loc[locindx, (diss_ind, pair)].translate(_char_del), 10)

        upper = pair.split(',')[0] # Upper-voice vairables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper) # NB b doesn't correspond to a note onset in upper-voice suspensions
        dur_a = self._set_note_dur(a_ind, upper)
        dur_b = self._set_note_dur(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)
        c_ind = 0
        c = 0
        c_temp = numpy.where(self._score[h_ind].index == locindx)[0][0]
        c_ind = self._score.loc[:, (h_ind, upper)].iloc[c_temp + 1:].first_valid_index()
        if c_ind != None:
            c = self._set_horiz_invl(c_ind, upper)
            dur_c = self._set_note_dur(c_ind, upper)
            dur_d = 0
            d_temp = numpy.where(self._score[h_ind].index == c_ind)[0][0]
            d_ind = self._score.loc[:, (h_ind, upper)].iloc[d_temp + 1:].first_valid_index()
            if d_ind != None:
                dur_d = self._set_note_dur(d_ind, upper)

        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower) # NB y doesn't correspond to a note onset in lower-voice suspensions
        dur_x = self._set_note_dur(x_ind, lower)
        dur_y = self._set_note_dur(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)
        z_ind = 0
        z = 0
        z_temp = numpy.where(self._score[h_ind].index == locindx)[0][0]
        z_ind = self._score.loc[:, (h_ind, lower)].iloc[z_temp + 1:].first_valid_index()
        if z_ind != None:
            z = self._set_horiz_invl(z_ind, lower)
            dur_z = self._set_note_dur(z_ind, lower)
            dur_z2 = 0
            z2_temp = numpy.where(self._score[h_ind].index == z_ind)[0][0]
            z2_ind = self._score.loc[:, (h_ind, lower)].iloc[z2_temp + 1:].first_valid_index()
            if z2_ind != None:
                dur_z2 = self._set_note_dur(z2_ind, lower)


        if ((diss == 2 or diss == -7) and dur_b == 1 and ((y == -2 and dur_y > 2) or (x == -2 and y
            is nan and int(z_ind) > float(locindx + 2))) and a == -2 and b == -2 and c == 2 and dur_c == 1 and dur_d > 2):
            return (True, upper, _chan_idiom_label, lower, _no_diss_label) # Chanson idiom in upper voice
        if ((diss == -2 or diss == 7) and dur_y == 1 and ((b == -2 and dur_b > 2) or (a == -2 and b
            is nan and int(c_ind) > float(locindx + 2))) and x == -2 and y == -2 and z == 2 and dur_z == 1 and dur_z2 > 2):
            return (True, upper, _no_diss_label, lower, _chan_idiom_label) # Chanson idiom in lower voice
        return (False,)

    def _is_echappee(self, locindx, pair):
        """
        A note is considered an échappée if it consists of a quarter-note dissonance on a weak
        quarter note that is approached by step and left by leap in the opposite direction.
        """

        # upper = pair.split(',')[0] # Upper-voice indecies
        # a_temp = self._score[h_ind][upper].iloc[:indx].last_valid_index()
        # a_ind = numpy.where(self._score[h_ind].index == a_temp)[0][0]

        # lower = pair.split(',')[1] # Lower-voice indecies
        # x_temp = self._score[h_ind][lower].iloc[:indx].last_valid_index()
        # x_ind = numpy.where(self._score[h_ind].index == x_temp)[0][0]

        # a = self._set_horiz_invl(a_ind, upper) # Upper-voice vairables
        # b = self._set_horiz_invl(indx, upper)
        # bs_b = self._set_note_bs(indx, upper)

        # x = self._set_horiz_invl(x_ind, lower) # Lower voice variables
        # y = self._set_horiz_invl(indx, lower)
        # bs_y = self._set_note_bs(indx, lower)

        upper = pair.split(',')[0] # Upper voice variables
        a_ind = self._score.loc[:locindx, (h_ind, upper)].iloc[:-1].last_valid_index()
        a = self._set_horiz_invl(a_ind, upper)
        b = self._set_horiz_invl(locindx, upper)
        bs_b = self._set_note_bs(locindx, upper)

        lower = pair.split(',')[1] # Lower voice variables
        x_ind = self._score.loc[:locindx, (h_ind, lower)].iloc[:-1].last_valid_index()
        x = self._set_horiz_invl(x_ind, lower)
        y = self._set_horiz_invl(locindx, lower)
        bs_y = self._set_note_bs(locindx, lower)

        if bs_b == .125 and ((a == 2 and b < -2) or (a == -2 and b > 2)): # Upper note échappée
            return (True, upper, _echappee, lower, _no_diss_label)
        if bs_y == .125 and ((x == 2 and y < -2) or (x == -2 and y > 2)): # Lower note échappée
            return (True, upper, _no_diss_label, lower, _echappee)
        return (False,)
        

    def _is_unexplainable(self, locindx, pair):
        """
        Neither note in the dissonant interval can be explained as one of the above. The voice that
        moved to the dissonance (if only one voice moved) will be taken to be the dissonant one. If
        they moved together to the dissonance the note that leaves the dissonance first will be
        labeled as the dissonant one. If they move to and from the dissonance together they will
        both be labeled dissonant.
        """ 
        # upper = pair.split(',')[0]
        # b = self._set_horiz_invl(indx, upper)
        # dur_b = self._set_note_dur(indx, upper)
        
        # lower = pair.split(',')[1]
        # y = self._set_horiz_invl(indx, lower)
        # dur_y = self._set_note_dur(indx, lower)


        upper = pair.split(',')[0] # Upper voice variables
        b = self._set_horiz_invl(locindx, upper)
        dur_b = self._set_note_dur(locindx, upper)

        lower = pair.split(',')[1] # Lower voice variables
        y = self._set_horiz_invl(locindx, lower)
        dur_y = self._set_note_dur(locindx, lower)
        
        if b is not nan and y is nan: # Upper voice is diss
            return (True, upper, _unexplainable, lower, _no_diss_label)
        elif y is not nan and b is nan: # Lower voice is diss
            return (True, upper, _no_diss_label, lower, _unexplainable)
        if b is not nan and y is not nan:
            if dur_b < dur_y: # Upper voice is diss
                return (True, upper, _unexplainable, lower, _no_diss_label)
            elif dur_y < dur_b: # Lower voice is diss
                return (True, upper, _no_diss_label, lower, _unexplainable)
        return (True, upper, _unexplainable, lower, _unexplainable)

    def classify(self, locindx, pair):
        """
        Checks the dissonance definitions to find a suitable label for the dissonance passed. If no
        identifiable dissonance type matches, returns an unknown dissonance label. Omits checking
        the pair if either voice was previously given a known dissonance label still in vigour at
        the given offset. Returns separate labels for each voice in the pair.
        """
        
        diss_types = [
                      self._is_passing,
                      self._is_suspension,
                      self._is_neighbour,
                      self._is_d3q,
                      self._is_fake_suspension,
                      self._is_cambiata,
                      self._is_chanson_idiom,
                      self._is_anticipation,
                      self._is_echappee,
                      self._is_unexplainable
                      ]

        for t in diss_types:
            result = t(locindx, pair)
            if result[0]:
                return result

    def run(self):
        iterables = [[diss_types], self._score[dur_ind].columns]
        d_types_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
        ret = pandas.DataFrame(index=self._score[diss_ind].index, columns=d_types_multi_index, dtype=str)
        for each_pair in self._score[diss_ind].columns:
            # for i, each_event in enumerate(self._score[diss_ind][each_pair]):
            for i in ret.index:
                each_event = self._score.loc[i, (diss_ind, each_pair)]
                voices = each_pair.split(',') # assign top and bottom voices as strings
                top_voice = min(voices)
                bott_voice = max(voices)
                # The interval must be dissonant and neither voice should already have a dissonance label assigned.
                if (each_event not in _ignored and 
                    ret.loc[i, (diss_types, top_voice)] in ('n', _no_diss_label, _unexplainable) and 
                    ret.loc[i, (diss_types, bott_voice)] in ('n', _no_diss_label, _unexplainable)):
                    diss_analysis = self.classify(i, each_pair)
                    ret.loc[i, (diss_types, diss_analysis[1])] = diss_analysis[2]
                    ret.loc[i, (diss_types, diss_analysis[3])] = diss_analysis[4]
                    # ret[diss_types][diss_analysis[1]].iloc[i] = diss_analysis[2]
                    # ret[diss_types][diss_analysis[3]].iloc[i] = diss_analysis[4]
        ret.replace('n', _no_diss_label, inplace=True)
        # ret[diss_types].replace('n', _no_diss_label, inplace=True)

        # Remove lingering unexplainable labels from notes that are only dissonant against identifiable dissonances.
        unknowns = numpy.where(ret.values == 'Z') # 2-tuple of a list of iloc indecies and a list of corresponding voice names.
        for x, ndx in enumerate(unknowns[0]):
            passable = True
            for pair in self._score[diss_ind].columns:
                v_to_check = pair.split(',')
                if str(unknowns[1][x]) not in v_to_check:
                    continue
                v_to_check.remove(str(unknowns[1][x]))
                v_temp = self._score[h_ind][v_to_check[0]].iloc[:ndx + 1].last_valid_index()
                v_ndx = numpy.where(self._score[h_ind].index == v_temp)[0][0]
                if self._score.loc[:, (diss_ind, pair)].iloc[ndx] in _ignored:
                    continue
                go_on = False
                for event in range(v_ndx, ndx + 1):
                    if ret.loc[:, (diss_types, v_to_check[0])].iloc[event] not in _go_ons:
                        go_on = True
                        break
                if go_on:
                    continue
                passable = False
                break
            if passable:
                # ret[diss_types][str(unknowns[1][x])].iloc[ndx] = _only_diss_w_diss
                ret.iloc[ndx, unknowns[1][x]] = _only_diss_w_diss

        # pdb.set_trace()

        return ret
                

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
        super(DissonanceIndexer, self).__init__(score)

    def ffiller(self, df):
        """
        Creates a 'forwardfilled' version of the passed dataframe and returns it. Forward filling
        often results in information loss and so should only be used if one is certain it is
        appropriate.
        """
        df_copy = df.copy(deep=True)
        ffilled_df = df_copy.ffill()
        del df_copy
        return ffilled_df

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
        # suspect_dura = self._score['group_durations'].loc[start_off, pair_name]

        for index, row in self._score['interval.IntervalIndexer'][start_off:].iterrows():
            if end_off != start_off:
                break
            elif end_off == start_off: # for the case where a 4th or 5th is in the last attack of the piece.
                end_off = self._score['interval.IntervalIndexer'].index[len(self._score['interval.IntervalIndexer'])-1]
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
        simuls = self.ffiller(self._score['interval.IntervalIndexer'])
        for pair_title in results:
            for j, event in enumerate(results[pair_title]):
                if event in potential_consonances: # NB: all other events are definite consonances or dissonances or don't qualify as interval onsets.
                    results[pair_title].iloc[j] = self.check_4s_5s(pair_title, j, results.index[j], event, simuls)
        
        # results = results.T     # Reapply the multi-index to the results dataframe
        # new_multiindex = [('dissonance.DissonanceLocator', x) for x in list(results.index)]
        # results.index = pandas.MultiIndex.from_tuples(new_multiindex)
        # results = results.T
        
        iterables = [['dissonance.DissonanceLocator'], self._score['interval.IntervalIndexer'].columns]
        results.columns = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])

        return results
