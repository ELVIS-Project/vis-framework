#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/template.py
# Purpose:                Template indexer
#
# Copyright (C) 2013-2016 Christopher Antila, Alexander Morgan
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
# License along with this program.  If not, see 
# <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------- #
"""
.. codeauthor:: Alexander Morgan
.. codeauthor:: Christopher Antila <christopher@antila.ca>
"""
import pandas
import numpy
from numpy import nan  # pylint: disable=no-name-in-module
from vis.analyzers import indexer
from multi_key_dict import multi_key_dict as mkd
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
_weights = mkd({(
    _d3q_label, 
    _pass_dp_label, 
    _pass_rp_label, 
    _neigh_ln_label, 
    _neigh_un_label,
    _susp_label, 
    _fake_susp_label, 
    _dim_fake_susp_label, 
    _ant_label, 
    _camb_label,
    _chan_idiom_label, _echappee): 3, 
    _no_diss_label: 2, 
    _unexplainable: 1
})
_consonances = set(['P1', 'm3', 'M3', 'CP4', 'CA4', 'Cd5', 'P5', 'm6', 
    'M6', 'P8', '-m3', '-M3', 'C-P4', 'C-A4', 'C-d5', '-P5', '-m6', 
    '-M6', '-P8'])
_potential_consonances = set([u'P4', u'-P4', u'A4', u'-A4', u'd5', 
    u'-d5'])
_cons_makers = {
    'P4':set([u'm3', u'M3', u'P5']), 
    'd5':[u'M6'], 
    'A4':[u'm3'], 
    '-P4':set([u'm3', u'M3', u'P5']), 
    '-d5':[u'M6'], 
    '-A4':[u'm3']
}
_Xed_makers = {
    'P4':set([u'-m3', u'-M3', u'-P5']), 
    'd5':[u'-M6'], 
    'A4':[u'-m3'],
    '-P4':set([u'-m3', u'-M3', u'-P5']), 
    '-d5':[u'-M6'], 
    '-A4':[u'-m3']
}
_nan_rest = set([nan, 'Rest'])
_ignored = _consonances.union(['Rest'])
_go_ons = set([_no_diss_label, _unexplainable])
_passes = set((nan, _no_diss_label, _unexplainable))
int_ind = u'interval.IntervalIndexer'
diss_ind = u'dissonance.DissonanceLocator'
h_ind = u'interval.HorizontalIntervalIndexer'
bs_ind = u'meter.NoteBeatStrengthIndexer'
dur_ind = u'meter.DurationIndexer'
diss_types = u'dissonance.DissonanceIndexer'


class DissonanceIndexer(indexer.Indexer):
    """
    Indexer that locates vertical dissonances between pairs of voices in 
    a piece. It then categorizes intervals as consonant or dissonant and 
    in the case of fourths (perfect or augmented) and diminished fifths 
    it examines the other parts sounding with that fourth or fifth (if 
    there are any) to see if the interval can be considered consonant. 
    This dissonance analysis allows for the assignment of a dissonance 
    type name or a consonance label for each voice at each offset. This 
    last step is the DataFrame that gets returned.
    The score type must be a list of dataframes of the results of the 
    following indexers (order matters): beatstrength, duration, 
    horizontal, vertical. To simplify things, however, it is better to 
    use the ``get_data()`` on an ``indexed_piece`` object to get results 
    from the dissonance indexer as per the example below.
    The results of the disonance indexer are in the form of one cell in 
    the resultant dataframe in each part at every offset where there is 
    a new note, rest, or chord onset in any part. These cells contain 
    one-character strings which are an abbreviation of what the 
    dissonance type for that part at that moment is. The abbreviations 
    correspoond to the following dissonance types:
    
    - 'Q': Dissonant third quarter (special type of accented passing 
           tone)
    - 'D': Descending passing tone
    - 'R': Ascending ("rising") passing tone
    - 'L': Lower neighbour
    - 'U': Upper neighbour
    - 'S': Suspension
    - 'F': Fake suspension
    - 'f': Diminished fake suspension
    - 'A': Anticipation
    - 'C': Nota cambiata
    - 'H': Chanson idiom
    - 'E': Echappée (escape tone)
    - '-': Either no dissonance, or the part in question is not 
           considered to be the dissonant note of the dissonance it's in
    
    **Example:**
    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('symbolic_notation_file_location.xml')
    >>> ip.get_data('dissonance')
    """
    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, settings=None):
        """
        :param score: The output from 
            :class:`~vis.analyzers.indexers.interval.IntervalIndexer`.
            You must include interval quality and use simple intervals.
        
        :type score:  :class:`pandas.DataFrame`.
        
        :param settings: This indexer uses no settings, so this is 
            ignored.
        
        :type settings: NoneType
        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the 
            same types.
        
        """
        super(DissonanceIndexer, self).__init__(score)
        self._score = pandas.concat(score, axis=1)

    def _set_horiz_invl(self, indx, col_indx):
        """
        Assigns the horizontal interval of the passed voice at the index 
        passed.
        
        """
        if self._score.iat[indx, col_indx] in _nan_rest:
            horiz_int = self._score.iat[indx, col_indx] 
        else:
            horiz_int = int(self._score.iat[indx, col_indx], 10)

        return horiz_int

    def _is_passing_or_neigh(self, indx, pair, event, prev_event):
        """
        A *passing tone* moves by step obliquely (i.e. the other voice 
        stands still while this one moves) creating a dissonant 
        interval, continues stepwise in the same direction without 
        resting, AND satisfies one of the following:
        * it is on a weak half, preceded by a half or longer, and its 
          duration is one half note, OR
        
        * it is on a weak quarter and its duration is one quarter or 
          less, OR
        
        * it is on a weak eighth and its duration is one eighth or less.
        
        A neighbour tone moves obliquely by step creating a dissonant 
        interval, without resting, by changing direction and returning 
        by step to the same note that preceded it AND meets one of the 
        above metric requirements.
        Passing and neighbour tone detection have been grouped to 
        improve analysis speed because their requirements are almost 
        identical. This function takes four parameters to situate the
        analysis in a specific pair of voices at a given moment in the 
        piece and returns the results of that analysis. The labels 
        assigned can be modified by changing the file-wide labels at the 
        top of this file. The variables assigned at the beginning of 
        this and all the other dissonance type definition functions are 
        as follows (note that not all appear in each function):
        a2 == horizontal motion of the upper voice into the note or rest 
              at a_ind
        a == horizontal motion of upper voice into dissonance
        
        b == horizontal motion of upper voice out of dissonance
        
        c == horizontal motion of upper voice out of the note or rest 
             after the dissonance
        
        x2, x, y, z, z2 correspond to a2, a, b, c, d respectively but 
        for the lower voice. ``h_upper_col``, ``d_upper_col``, and 
        ``bs_upper_col`` correspond to the column indecies in 
        ``self._score`` where the ``horizontal``, ``duration``, and 
        ``beatStrength`` information of the upper voice can be found. 
        These columns are also calculated for the lower voice, replacing 
        'upper' with 'lower'.
        
        'letter'_temp == label-based index letter's row position
        
        'letter'_ind == int-based index of letter's row position
        
        dur_'letter' == duration of note or rest at the passed position
        
        bs_'letter' == beatStrength of note or rest at the passed 
                       position
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method check_4s_5s.
        
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or None if there was no previous event.
        :returns: If it finds a suspension a five-tuple with True as the 
            first argument, the upper-voice number stored as a string as 
            the second argument, the label to assign the upper voice as 
            the third argument, the lower-voice number as a string as 
            the fourth argument, and the label to assign the lower voice 
            as the fifth argument. If the analysis does not find a 
            suspension the function returns a 1-tuple with False as the 
            argument.
        
        :rtype: tuple
        
        """
        if prev_event is None:
            return (False,)
        # Upper voice variables
        upper = pair.split(',')[0] 
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        bs_upper_col = self._score.columns.get_loc((bs_ind, upper))
        a_temp = self._score.iloc[:indx, h_upper_col].last_valid_index()
        a_ind = numpy.where(self._score.index == a_temp)[0][0]
        a = self._set_horiz_invl(a_ind, h_upper_col)
        b = self._set_horiz_invl(indx, h_upper_col)
        dur_a = self._score.iat[a_ind, d_upper_col]
        dur_b = self._score.iat[indx, d_upper_col]
        bs_b = self._score.iat[indx, bs_upper_col]
        if dur_a < dur_b:
            a2_temp = self._score.iloc[:a_ind, h_upper_col].last_valid_index()
            a2_ind = numpy.where(self._score.index == a2_temp)[0][0]
            if a2_ind != None:
                a2 = self._set_horiz_invl(a2_ind, h_upper_col)
                if a2 == 1:
                    dur_a2 = self._score.iat[a2_ind, d_upper_col]
                    dur_a += dur_a2

        # Lower voice variables
        lower = pair.split(',')[1] 
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        bs_lower_col = self._score.columns.get_loc((bs_ind, lower))
        x_temp = self._score.iloc[:indx, h_lower_col].last_valid_index()
        x_ind = numpy.where(self._score.index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, h_lower_col)
        y = self._set_horiz_invl(indx, h_lower_col)
        dur_x = self._score.iat[x_ind, d_lower_col]
        dur_y = self._score.iat[indx, d_lower_col]
        bs_y = self._score.iat[indx, bs_lower_col]
        if dur_x < dur_y:
            x2_temp = self._score.iloc[:x_ind, h_lower_col].last_valid_index()
            x2_ind = numpy.where(self._score.index == x2_temp)[0][0]
            if x2_ind != None:
                x2 = self._set_horiz_invl(x2_ind, h_lower_col)
                if x2 == 1:
                    dur_x2 = self._score.iat[x2_ind, d_lower_col]
                    dur_x += dur_x2

        # The dissonance can't be a passing tone.
        if prev_event not in _consonances: 
            return (False,)
        elif (((dur_b == 2 and bs_b == .25) or (dur_b <= 1 and bs_b == .125) or 
               (dur_b <= .5 and bs_b == .0625)) and dur_a >= dur_b and (y is nan or x == 1)):
            if b == 2:
                if a == 2:
                    return (True, upper, _pass_rp_label, lower, _no_diss_label)
                elif a == -2:
                    return (True, upper, _neigh_ln_label, lower, _no_diss_label)
            elif b == -2:
                if a == -2:
                    return (True, upper, _pass_dp_label, lower, _no_diss_label)
                elif a == 2:
                    return  (True, upper, _neigh_un_label, lower, _no_diss_label)
            
        elif (((dur_y == 2 and bs_y == .25) or (dur_y <= 1 and bs_y == .125) 
               or (dur_y <= .5 and bs_y == .0625)) and dur_x >= dur_y and (b is nan or a == 1)):
            if y == 2:
                if x == 2:
                    return (True, upper, _no_diss_label, lower, _pass_rp_label)
                elif x == -2:
                    return (True, upper, _no_diss_label, lower, _neigh_ln_label)
            elif y == -2:
                if x == -2:
                    return (True, upper, _no_diss_label, lower, _pass_dp_label)
                elif x == 2:
                    return (True, upper, _no_diss_label, lower, _neigh_un_label)
            
        
        return (False,) # The dissonance is not a passing tone.

    def _is_suspension(self, indx, pair, event, prev_event):
        """
        A note is considered a *suspension* if it is sustained or 
        re-attacked on the same pitch while another voice enters or 
        moves by step or by leap to create a dissonant interval AND:
        
        * its next move (the "resolution") is downwards by step without 
          resting (it may restrike the same note before resolving, 
          though), AND
        * the resolution is on a weaker beat than the dissonance, or, if 
          the dissonant note is a whole note in duration, the resolution 
          is on a weaker-or-equally-strong beat.
        This function takes four parameters to situate the analysis in a 
        specific pair of voices at a given moment in the piece and 
        returns the results of that analysis. For the meaning of the
        numerous variables assigned at the beginning of this function, 
        please refer to the doc string of ``_is_passing_or_neigh``. The 
        labels assigned can be modified by changing the file-wide labels 
        at the top of this file.
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method ``check_4s_5s``.
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or None if there was no previous event.
        :returns: If it finds a suspension a five-tuple with True as the 
            first argument, the upper-voice number stored as a string as 
            the second argument, the label to assign the upper voice as 
            the third argument, the lower-voice number as a string as 
            the fourth argument, and the label to assign the lower voice 
            as the fifth argument. If the analysis does not find a 
            suspension the function returns a 1-tuple with False as the 
            argument.
        
        :rtype: tuple
        """
        if prev_event is None:
            return (False,)
        upper = pair.split(',')[0] # Upper voice variables
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        bs_upper_col = self._score.columns.get_loc((bs_ind, upper))
        a_temp = self._score.iloc[:indx, h_upper_col].last_valid_index()
        a_ind = numpy.where(self._score.index == a_temp)[0][0]
        a = self._set_horiz_invl(a_ind, h_upper_col)
        b = self._set_horiz_invl(indx, h_upper_col) 
        # NB b doesn't correspond to a note onset in upper-voice 
        # suspensions
        dur_a = self._score.iat[a_ind, d_upper_col]
        dur_b = self._score.iat[indx, d_upper_col]
        bs_b = self._score.iat[indx, bs_upper_col]
        c_ind = 0
        c = 0
        c_temp = self._score.iloc[indx + 1:, h_upper_col].first_valid_index()
        if c_temp != None:
            c_ind = numpy.where(self._score.index == c_temp)[0][0]
            c = self._set_horiz_invl(c_ind, h_upper_col)
            bs_c = self._score.iat[c_ind, bs_upper_col]

        lower = pair.split(',')[1] # Lower voice variables
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        bs_lower_col = self._score.columns.get_loc((bs_ind, lower))
        x_temp = self._score.iloc[:indx, h_lower_col].last_valid_index()
        x_ind = numpy.where(self._score.index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, h_lower_col)
        y = self._set_horiz_invl(indx, h_lower_col) 
        # NB y doesn't correspond to a note onset in lower-voice 
        # suspensions
        dur_x = self._score.iat[x_ind, d_lower_col]
        dur_y = self._score.iat[indx, d_lower_col]
        bs_y = self._score.iat[indx, bs_lower_col]
        z_ind = 0
        z = 0
        z_temp = self._score.iloc[indx + 1:, h_lower_col].first_valid_index()
        if z_temp != None:
            z_ind = numpy.where(self._score.index == z_temp)[0][0]
            z = self._set_horiz_invl(z_ind, h_lower_col)
            bs_z = self._score.iat[z_ind, bs_lower_col]

        # NB this may need to be tweaked for the edge case where a 
        # consonant 4th becomes a dissonant fourth suspension without 
        # being restruck.
        if (c != 0 and ((a == -2 and b is nan) or (a == 1 and b == -2)) 
            and (bs_y > bs_c or (dur_a == 4 and bs_y >= bs_c))):
            return (True, upper, _susp_label, lower, _no_diss_label) 
            # Susp in upper voice
        elif (z != 0 and ((x == -2 and y is nan) 
            or (x == 1 and y == -2)) and (bs_b > bs_z 
            or (dur_x == 4 and bs_b >= bs_z))):
            return (True, upper, _no_diss_label, lower, _susp_label) 
            # Susp in lower voice
        return (False,)

    def _is_fake_suspension(self, indx, pair, event, prev_event): 
        """
        A *fake suspension* (more accurately a "*fake preparation*") is 
        a dissonant preparation to a suspension. It is moved to by step 
        obliquely and becomes a dissonant suspension by being tied to a 
        dissonant note (or followed by the same note) whose next move is 
        down by step, with a duration of either:
        
        * a weak half, with the ensuing suspended note (or part of note) 
          falling on the following downbeat, OR
        * (diminished fake suspension) a weak quarter, with the ensuing 
          suspended note (or part of note) falling on the following 
          strong quarter.
        This function takes four parameters to situate the analysis in a 
        specific pair of voices at a given moment in the piece and 
        returns the results of that analysis. For the meaning of the
        numerous variables assigned at the beginning of this function, 
        please refer to the doc string of ``_is_passing_or_neigh``. The 
        labels assigned can be modified by changing the file-wide labels 
        at the top of this file.
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method ``check_4s_5s``.
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or None if there was no previous event.
        
        :returns: If it finds a fake suspension a five-tuple with 
            ``True`` as the first argument, the upper-voice number 
            stored as a string as the second argument, the label to 
            assign the upper voice as the third argument, the 
            lower-voice number as a string as the fourth argument, and 
            the label to assign the lower voice as the fifth argument. 
            If the analysis does not find a suspension the function 
            returns a 1-tuple with False as the argument.
        
        :rtype: tuple
        
        """
        if prev_event is None:
            return (False,)
        upper = pair.split(',')[0] # Upper voice variables
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        bs_upper_col = self._score.columns.get_loc((bs_ind, upper))
        a_temp = self._score.iloc[:indx, h_upper_col].last_valid_index()
        a_ind = numpy.where(self._score.index == a_temp)[0][0]
        a = self._set_horiz_invl(a_ind, h_upper_col)
        b = self._set_horiz_invl(indx, h_upper_col) 
        # NB b doesn't correspond to a note onset in upper-voice 
        # suspensions
        dur_b = self._score.iat[indx, d_upper_col]
        bs_b = self._score.iat[indx, bs_upper_col]
        c_ind = 0
        c = 0
        c_temp = self._score.iloc[indx + 1:, h_upper_col].first_valid_index()
        if c_temp != None:
            c_ind = numpy.where(self._score.index == c_temp)[0][0]
            c = self._set_horiz_invl(c_ind, h_upper_col)

        lower = pair.split(',')[1] # Lower voice variables
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        bs_lower_col = self._score.columns.get_loc((bs_ind, lower))
        x_temp = self._score.iloc[:indx, h_lower_col].last_valid_index()
        x_ind = numpy.where(self._score.index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, h_lower_col)
        y = self._set_horiz_invl(indx, h_lower_col) 
        # NB y doesn't correspond to a note onset in lower-voice 
        # suspensions
        dur_y = self._score.iat[indx, d_lower_col]
        bs_y = self._score.iat[indx, bs_lower_col]
        z_ind = 0
        z = 0
        z_temp = self._score.iloc[indx + 1:, h_lower_col].first_valid_index()
        if z_temp != None:
            z_ind = numpy.where(self._score.index == z_temp)[0][0]
            z = self._set_horiz_invl(z_ind, h_lower_col)

        if a == 2 or a == -2:
            if bs_b == .25 and ((b == -2 and dur_b > 2) 
                or (b == 1 and dur_b == 2 and c == -2)):
                return (True, upper, _fake_susp_label, lower, _no_diss_label) 
                # Fake susp in upper voice
            elif bs_b == .125 and ((b == -2 and dur_b > 1) 
                or (b == 1 and dur_b == 1 and c == -2)):
                return (True, upper, _dim_fake_susp_label, lower, _no_diss_label) 
                # Diminished fake susp in upper voice
        elif x == 2 or x == -2:
            if bs_y == .25 and ((y == -2 and dur_y > 2) 
                or (y == 1 and dur_y == 2 and z == -2)):
                return (True, upper, _no_diss_label, lower, _fake_susp_label) 
                # Fake susp in lower voice
            elif bs_y == .125 and ((y == -2 and dur_y > 1) 
                or (y == 1 and dur_y == 1 and z == -2)):
                return (True, upper, _no_diss_label, lower, _dim_fake_susp_label) 
                # Diminished fake susp in lower voice
        return (False,)

    def _is_d3q(self, indx, pair, event, prev_event):
        """
        A legal "*dissonant 3rd quarter*" is a dissonant 1 on a weak 
        half, approached by step from above and preceded by a 2 or 
        longer, and continuing by step in the same direction. The 
        suspect dissonance occurs at the indx passed.
        This function takes four parameters to situate the analysis in a 
        specific pair of voices at a given moment in the piece and 
        returns the results of that analysis. For the meaning of the 
        numerous variables assigned at the beginning of this function, 
        please refer to the doc string of ``_is_passing_or_neigh``. The 
        labels assigned can be modified by changing the file-wide labels 
        at the top of this file.
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method ``check_4s_5s``.
        
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or None if there was no previous event.
        
        :returns: If it finds a dissonant 3rd quarter a five-tuple with 
            True as the first argument, the upper-voice number stored as 
            a string as the second argument, the label to assign the 
            upper voice as the third argument, the lower-voice number as 
            a string as the fourth argument, and the label to assign the 
            lower voice as the fifth argument. If the analysis does not 
            find a suspension the function returns a 1-tuple with 
            ``False`` as the argument.
        
        :rtype: tuple
        
        """
        if prev_event is None:
            return (False,)
        upper = pair.split(',')[0] # Upper voice variables
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        bs_upper_col = self._score.columns.get_loc((bs_ind, upper))
        a_temp = self._score.iloc[:indx, h_upper_col].last_valid_index()
        a_ind = numpy.where(self._score.index == a_temp)[0][0]
        a = self._set_horiz_invl(a_ind, h_upper_col)
        b = self._set_horiz_invl(indx, h_upper_col)
        dur_a = self._score.iat[a_ind, d_upper_col]
        dur_b = self._score.iat[indx, d_upper_col]
        bs_b = self._score.iat[indx, bs_upper_col]

        lower = pair.split(',')[1] # Lower voice variables
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        bs_lower_col = self._score.columns.get_loc((bs_ind, lower))
        x_temp = self._score.iloc[:indx, h_lower_col].last_valid_index()
        x_ind = numpy.where(self._score.index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, h_lower_col)
        y = self._set_horiz_invl(indx, h_lower_col)
        dur_x = self._score.iat[x_ind, d_lower_col]
        dur_y = self._score.iat[indx, d_lower_col]
        bs_y = self._score.iat[indx, bs_lower_col]

        '''
        .. todo:: make the beatstrength requirements dependent on the 
            detected meter. Right now it is hard-coded for 4/2 meter.
        '''

        if (bs_b == .25 and dur_a >= 2 and dur_b == 1 
            and a == -2 and b == -2): 
            # Upper voice is d3q
            return (True, upper, _d3q_label, lower, _no_diss_label)            
        elif (bs_y == .25 and dur_x >= 2 and dur_y == 1 
            and x == -2 and y == -2): 
            # Lower voice is d3q
            return (True, upper, _no_diss_label, lower, _d3q_label)
        else: # The dissonance is not a d3q.
            return (False,)

    def _is_anticipation(self, indx, pair, event, prev_event):
        """
        An anticipation occurs on a weak quarter-note, is approached 
        obliquely by step from above, and is followed immediately (i.e. 
        on the strong quarter, which might be a downbeat or a weak half) 
        by the same pitch.
        This function takes four parameters to situate the analysis in a 
        specific pair of voices at a given moment in the piece and 
        returns the results of that analysis. For the meaning of the
        numerous variables assigned at the beginning of this function, 
        please refer to the doc string of ``_is_passing_or_neigh``. The 
        labels assigned can be modified by changing the file-wide labels 
        at the top of this file.
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method check_4s_5s.
        
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or None if there was no previous event.
        
        :returns: If it finds an anticipation a five-tuple with ``True`` 
            as the first argument, the upper-voice number stored as a 
            string as the second argument, the label to assign the
            upper voice as the third argument, the lower-voice number as 
            a string as the fourth argument, and the label to assign the 
            lower voice as the fifth argument. If the analysis does not 
            find a suspension the function returns a 1-tuple with 
            ``False`` as the argument.
        
        :rtype: tuple
        
        """
        if prev_event is None:
            return (False,)
        upper = pair.split(',')[0] # Upper voice variables
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        bs_upper_col = self._score.columns.get_loc((bs_ind, upper))
        a_temp = self._score.iloc[:indx, h_upper_col].last_valid_index()
        a_ind = numpy.where(self._score.index == a_temp)[0][0]
        a = self._set_horiz_invl(a_ind, h_upper_col)
        b = self._set_horiz_invl(indx, h_upper_col)
        dur_b = self._score.iat[indx, d_upper_col]
        bs_b = self._score.iat[indx, bs_upper_col]

        lower = pair.split(',')[1] # Lower voice variables
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        bs_lower_col = self._score.columns.get_loc((bs_ind, lower))
        x_temp = self._score.iloc[:indx, h_lower_col].last_valid_index()
        x_ind = numpy.where(self._score.index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, h_lower_col)
        y = self._set_horiz_invl(indx, h_lower_col)
        dur_y = self._score.iat[indx, d_lower_col]
        bs_y = self._score.iat[indx, bs_lower_col]

        if (bs_b == .125 and a == -2 and b == 1 and dur_b == 1):
            return (True, upper, _ant_label, lower, _no_diss_label)
        elif (bs_y == .125 and x == -2 and y == 1 and dur_y == 1):
            return (True, upper, _no_diss_label, lower, _ant_label)
        return (False,)

    def _is_cambiata(self, indx, pair, event, prev_event):
        """
        A *nota cambiata* figure moves obliquely by descending step to a 
        dissonant weak half or quarter then skips down a third before 
        ascending by step to the note skipped over.
        This function takes four parameters to situate the analysis in a 
        specific pair of voices at a given moment in the piece and 
        returns the results of that analysis. For the meaning of the
        numerous variables assigned at the beginning of this function, 
        please refer to the doc string of ``_is_passing_or_neigh``. The 
        labels assigned can be modified by changing the file-wide labels 
        at the top of this file.
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method ``check_4s_5s``.
        
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or ``None`` if there was no previous event.
        
        :returns: If it finds a nota cambiata a five-tuple with ``True`` 
            as the first argument, the upper-voice number stored as a 
            string as the second argument, the label to assign the upper 
            voice as the third argument, the lower-voice number as a 
            string as the fourth argument, and the label to assign the 
            lower voice as the fifth argument. If the analysis does not 
            find a suspension the function returns a 1-tuple with 
            ``False`` as the argument.
        
        :rtype: tuple
        
        """  
        # QUESTION: is b on a weak half even if it lasts a quarter note?
        
        if prev_event is None:
            return (False,)
        upper = pair.split(',')[0] # Upper voice variables
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        bs_upper_col = self._score.columns.get_loc((bs_ind, upper))
        a_temp = self._score.iloc[:indx, h_upper_col].last_valid_index()
        a_ind = numpy.where(self._score.index == a_temp)[0][0]
        a = self._set_horiz_invl(a_ind, h_upper_col)
        b = self._set_horiz_invl(indx, h_upper_col) 
        # NB b doesn't correspond to a note onset in upper-voice 
        # suspensions
        dur_b = self._score.iat[indx, d_upper_col]
        bs_b = self._score.iat[indx, bs_upper_col]
        c_ind = 0
        c = 0
        c_temp = self._score.iloc[indx + 1:, h_upper_col].first_valid_index()
        if c_temp != None:
            c_ind = numpy.where(self._score.index == c_temp)[0][0]
            c = self._set_horiz_invl(c_ind, h_upper_col)

        lower = pair.split(',')[1] # Lower voice variables
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        bs_lower_col = self._score.columns.get_loc((bs_ind, lower))
        x_temp = self._score.iloc[:indx, h_lower_col].last_valid_index()
        x_ind = numpy.where(self._score.index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, h_lower_col)
        y = self._set_horiz_invl(indx, h_lower_col) 
        # NB y doesn't correspond to a note onset in lower-voice 
        #suspensions
        dur_y = self._score.iat[indx, d_lower_col]
        bs_y = self._score.iat[indx, bs_lower_col]
        z_ind = 0
        z = 0
        z_temp = self._score.iloc[indx + 1:, h_lower_col].first_valid_index()
        if z_temp != None:
            z_ind = numpy.where(self._score.index == z_temp)[0][0]
            z = self._set_horiz_invl(z_ind, h_lower_col)


        if (a == -2 and ((dur_b == 2 and bs_b == .25) 
            or (dur_b == 1 and bs_b == .125) and b == -3 and c == 2)):
            return (True, upper, _camb_label, lower, _no_diss_label) 
            # Cambiata in upper voice
        elif (x == -2 and ((dur_y == 2 and bs_y == .25) 
            or (dur_y == 1 and bs_y == .125) and y == -3 and z == 2)):
            return (True, upper, _no_diss_label, lower, _camb_label) 
            # Cambiata in lower voice
        return (False,)

    #m.136 in alto? What about diminished lengths?
    def _is_chanson_idiom(self, indx, pair, event, prev_event): 
        """
        The *chanson* idiom dissonance consists of a seventh or second, 
        struck simultaneously or obliquely on the 3rd quarter of a whole 
        note, involving a quarter in one voice ("the active voice") and 
        a duration extending past the next downbeat in the other voice 
        ("the inactive voice"), such that:
        
        * the active voice, at the 3rd quarter, is approached by 
          descending step and proceeds down by step on the 4th quarter 
          note, sounding the same pitch-class as the inactive voice, 
          then returns upwards by step to a whole note on the downbeat
        
        * the inactive voice is extended past the downbeat, becoming a 
          dissonant suspension that resolves down by step.
        This function takes four parameters to situate the analysis in a 
        specific pair of voices at a given moment in the piece and 
        returns the results of that analysis. For the meaning of the
        numerous variables assigned at the beginning of this function, 
        please refer to the doc string of ``_is_passing_or_neigh``. The 
        labels assigned can be modified by changing the file-wide labels 
        at the top of this file.
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method ``check_4s_5s``.
        
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or ``None`` if there was no previous event.
        
        :returns: If it finds a chanson idiom a five-tuple with ``True`` 
            as the first argument, the upper-voice number stored as a 
            string as the second argument, the label to assign the upper 
            voice as the third argument, the lower-voice number as a 
            string as the fourth argument, and the label to assign the 
            lower voice as the fifth argument. If the analysis does not 
            find a suspension the function returns a 1-tuple with 
            ``False`` as the argument.
        
        :rtype: tuple
        
        """
        if prev_event is None:
            return (False,)
        diss = int(''.join(dig for dig in event if dig.isdigit()), 10) 
        # delete all non-digit characters from event string and convert 
        # to int.

        upper = pair.split(',')[0] # Upper voice variables
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        bs_upper_col = self._score.columns.get_loc((bs_ind, upper))
        a_temp = self._score.iloc[:indx, h_upper_col].last_valid_index()
        a_ind = numpy.where(self._score.index == a_temp)[0][0]
        a = self._set_horiz_invl(a_ind, h_upper_col)
        b = self._set_horiz_invl(indx, h_upper_col) 
        # NB b doesn't correspond to a note onset in upper-voice 
        # suspensions
        dur_a = self._score.iat[a_ind, d_upper_col]
        dur_b = self._score.iat[indx, d_upper_col]
        bs_b = self._score.iat[indx, bs_upper_col]
        c_ind = 0
        c = 0
        c_temp = self._score.iloc[indx + 1:, h_upper_col].first_valid_index()
        if c_temp != None:
            c_ind = numpy.where(self._score.index == c_temp)[0][0]
            c = self._set_horiz_invl(c_ind, h_upper_col)
            dur_c = self._score.iat[c_ind, d_upper_col]
            dur_d = 0
            d_temp = self._score.iloc[c_ind + 1:, h_upper_col].first_valid_index()
            if d_temp != None:
                d_ind = numpy.where(self._score.index == d_temp)[0][0]
                dur_d = self._score.iat[d_ind, d_upper_col]

        lower = pair.split(',')[1] # Lower voice variables
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        bs_lower_col = self._score.columns.get_loc((bs_ind, lower))
        x_temp = self._score.iloc[:indx, h_lower_col].last_valid_index()
        x_ind = numpy.where(self._score.index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, h_lower_col)
        y = self._set_horiz_invl(indx, h_lower_col) 
        # NB y doesn't correspond to a note onset in lower-voice 
        # suspensions
        dur_x = self._score.iat[x_ind, d_lower_col]
        dur_y = self._score.iat[indx, d_lower_col]
        bs_y = self._score.iat[indx, bs_lower_col]
        z_ind = 0
        z = 0
        z_temp = self._score.iloc[indx + 1:, h_lower_col].first_valid_index()
        if z_temp != None:
            z_ind = numpy.where(self._score.index == z_temp)[0][0]
            z = self._set_horiz_invl(z_ind, h_lower_col)
            dur_z = self._score.iat[z_ind, d_lower_col]
            dur_z2 = 0
            z2_temp = self._score.iloc[z_ind + 1:, h_lower_col].first_valid_index()
            if z2_temp != None:
                z2_ind = numpy.where(self._score.index == z2_temp)[0][0]
                dur_z2 = self._score.iat[z2_ind, d_lower_col]

        if ((diss == 2 or diss == -7) and dur_b == 1 
            and ((y == -2 and dur_y > 2) or (y == 1 and dur_y == 2)) 
            and a == -2 and b == -2 and c == 2 and dur_c == 1 and dur_d >= 2):
            return (True, upper, _chan_idiom_label, lower, _no_diss_label) 
            # Chanson idiom in upper voice
        if ((diss == -2 or diss == 7) and dur_y == 1 
            and ((b == -2 and dur_b > 2) or (b == 1 and dur_b == 2)) and
            x == -2 and y == -2 and z == 2 and dur_z == 1 and dur_z2 >= 2):
            return (True, upper, _no_diss_label, lower, _chan_idiom_label) 
            # Chanson idiom in lower voice
        return (False,)

    def _is_echappee(self, indx, pair, event, prev_event):
        """
        A note is considered an *échappée* if it consists of a 
        quarter-note dissonance on a weak quarter note that is 
        approached by step and left by leap in the opposite direction.
        This function takes four parameters to situate the analysis in a 
        specific pair of voices at a given moment in the piece and 
        returns the results of that analysis. For the meaning of the 
        numerous variables assigned at the beginning of this function, 
        please refer to the doc string of ``_is_passing_or_neigh``. The 
        labels assigned can be modified by changing the file-wide labels 
        at the top of this file.
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method ``check_4s_5s``.
        
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or ``None`` if there was no previous event.
        
        :returns: If it finds an *échappée* a five-tuple with ``True`` 
            as the first argument, the upper-voice number stored as a 
            string as the second argument, the label to assign the
            upper voice as the third argument, the lower-voice number as 
            a string as the fourth argument, and the label to assign the 
            lower voice as the fifth argument. If the analysis does not 
            find a suspension the function returns a 1-tuple with 
            ``False`` as the argument.
        
        :rtype: tuple
        
        """
        if prev_event is None:
            return (False,)
        upper = pair.split(',')[0] # Upper voice variables
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        bs_upper_col = self._score.columns.get_loc((bs_ind, upper))
        a_temp = self._score.iloc[:indx, h_upper_col].last_valid_index()
        a_ind = numpy.where(self._score.index == a_temp)[0][0]
        a = self._set_horiz_invl(a_ind, h_upper_col)
        b = self._set_horiz_invl(indx, h_upper_col)
        dur_b = self._score.iat[indx, d_upper_col]
        bs_b = self._score.iat[indx, bs_upper_col]

        lower = pair.split(',')[1] # Lower voice variables
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        bs_lower_col = self._score.columns.get_loc((bs_ind, lower))
        x_temp = self._score.iloc[:indx, h_lower_col].last_valid_index()
        x_ind = numpy.where(self._score.index == x_temp)[0][0]
        x = self._set_horiz_invl(x_ind, h_lower_col)
        y = self._set_horiz_invl(indx, h_lower_col)
        dur_y = self._score.iat[indx, d_lower_col]
        bs_y = self._score.iat[indx, bs_lower_col]

        if bs_b == .125 and ((a == 2 and b < -2) or (a == -2 and b > 2)): 
            # Upper note *échappée*
            return (True, upper, _echappee, lower, _no_diss_label)
        if bs_y == .125 and ((x == 2 and y < -2) or (x == -2 and y > 2)): 
            # Lower note *échappée*
            return (True, upper, _no_diss_label, lower, _echappee)
        return (False,)
        

    def _is_unexplainable(self, indx, pair, event, prev_event):
        """
        Neither note in the dissonant interval can be explained as one 
        of the above. The voice that moved to the dissonance (if only 
        one voice moved) will be taken to be the dissonant one. If they 
        moved together to the dissonance the note that leaves the 
        dissonance first will be labeled as the dissonant one. If they 
        move to and from the dissonance together they will both be 
        labeled dissonant.
        This function takes four parameters to situate the analysis in a 
        specific pair of voices at a given moment in the piece and 
        returns the results of that analysis. By this point, none of the 
        known dissonance types have been detected so this function 
        determines which voice of the pair should get the dissonance 
        label, or whether both should. For the meaning of the numerous 
        variables assigned at the beginning of this function, please 
        refer to the doc string of ``_is_passing_or_neigh``. The labels 
        assigned can be modified by changing the file-wide labels at the 
        top of this file.
        :param indx: The position-based (iloc) index of the dissonance 
            being analyzed.
        
        :type indx: int
        
        :param pair: name of the voice pair in which the dissonance 
            happens.
        
        :type pair: string with the lower numbered voice first and a 
            comma separating the two voices.
        
        :param event: the interval that has been analyzed as a 
            dissonance to be classified.
        
        :type event: string of dissonant interval with quality. All 
            fourths and fifths should be dissonant fourths and fifths 
            based on the analysis of method check_4s_5s.
        
        :param prev_event: previous event in the same voice pair which 
            may be a consonance, a dissonance, a rest, or non-existent 
            if there was no previous event in the pair.
        
        :type prev_event: string of previous event in the same voice 
            pair or ``None`` if there was no previous event.
        
        :returns: A five-tuple with True as the first argument, the 
            upper-voice number stored as a string as the second 
            argument, the label to assign the upper voice as the third
            argument, the lower-voice number as a string as the fourth 
            argument, and the label to assign the lower voice as the 
            fifth argument. If the analysis does not find a suspension
            the function returns a 1-tuple with False as the argument.
        
        :rtype: tuple
        
        """
        upper = pair.split(',')[0] # Upper voice variables
        h_upper_col = self._score.columns.get_loc((h_ind, upper))
        d_upper_col = self._score.columns.get_loc((dur_ind, upper))
        b = self._set_horiz_invl(indx, h_upper_col)
        dur_b = self._score.iat[indx, d_upper_col]

        lower = pair.split(',')[1] # Lower voice variables
        h_lower_col = self._score.columns.get_loc((h_ind, lower))
        d_lower_col = self._score.columns.get_loc((dur_ind, lower))
        y = self._set_horiz_invl(indx, h_lower_col)
        dur_y = self._score.iat[indx, d_lower_col]
        
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

    def classify(self, indx, pair, event, prev_event):
        """
        Checks the dissonance definitions to find a suitable label for 
        the dissonance passed. If no identifiable dissonance type 
        matches, returns an unknown dissonance label. Omits checking the 
        pair if either voice was previously given a known dissonance 
        label still in vigour at the given offset. It only takes its 
        four arguments to pass them on to the dissonance-type functions 
        it calls.
        :returns: A 5-tuple that can be unpacked to assign separate 
            labels for each voice in the pair. If none of the known 
            dissonance types were detected the 5-tuple will have the
            labels to mark one or both of the voices as dissonant.
        
        :rtype: tuple
        
        """
        diss_types = [
            self._is_passing_or_neigh,
            self._is_suspension,
            self._is_d3q,
            self._is_fake_suspension,
            self._is_chanson_idiom,
            self._is_cambiata,
            self._is_anticipation,
            self._is_echappee,
            self._is_unexplainable
        ]

        for t in diss_types:
            result = t(indx, pair, event, prev_event)
            if result[0]:
                return result

    def check_4s_5s(self, pair_name, iloc_indx, suspect_diss, simuls):
        """
        This function evaluates whether P4's, A4's, and d5's should be 
        considered consonant based whether or not the lower voice of the 
        suspect_diss forms an interval that causes us to deem the fourth 
        or fifth consonant, as determined by the cons_makers list below. 
        The function should be called once for each potentially 
        consonant fourth or fifth.
        :param pair_name: Name of pair that has the potentially 
            consonant fourth or fifth.
        
        :type pair_name: String in the format '0,2' if the pair in 
            question is S and T in an SATB texture.
        
        :param iloc_indx: Pandas iloc number of interval's row in 
            dataframe.
        
        :type iloc_indx: Integer.
        
        :param suspect_diss: Interval name with quality and direction 
            (i.e. nothing or '-') that corresponds to the fourth or 
            fifth to be examined.
        
        :type suspect_diss: String.
        
        :returns: string representing analysis of fourth or fifth in 
            question where a 'C' or 'D' has been prepended to the 
            interval name with quality to show that it was considered
            consonant or dissonant respectively.
        
        :rtype: string
        
        """
        cons_made = False
        # Find the offset of the next event in the voice pair to know 
        # when the interval ends.
        end_temp = self._score.loc[:, (int_ind, pair_name)].iloc[iloc_indx +1:].first_valid_index()
        if end_temp != None: 
            # for the case where a 4th or 5th is in the last attack of 
            # the piece.
            end_iloc = numpy.where(self._score.index == end_temp)[0][0]
        else:
            end_iloc = len(self._score) + 1

        if '-' in suspect_diss: 
            # set the voice that is spelled lower 
            # as the lower voice.
            lower_voice = pair_name.split(',')[0]
        else:
            lower_voice = pair_name.split(',')[1]

        for voice_combo in simuls:
            if (lower_voice == voice_combo.split(',')[0] 
                and voice_combo != pair_name): 
                # look at other pairs that have lower_voice as their 
                # upper voice. Could be optimized.
                if (simuls[voice_combo].iloc[iloc_indx:end_iloc].any() 
                    in _cons_makers[suspect_diss]): 
                    # this chained-indexing is actually faster than the 
                    # alternative.
                    cons_made = True
                    break
            elif (lower_voice == voice_combo.split(',')[1] 
                and voice_combo != pair_name): 
                # look at other pairs that have lower_voice as their 
                # lower voice. Could be optimized.
                if (simuls[voice_combo].iloc[iloc_indx:end_iloc].any() 
                    in _Xed_makers[suspect_diss]):
                    cons_made = True
                    break

        if cons_made:   
            # 'C' is for consonant and it's good enough for me.
            return ('C' + suspect_diss)
        else:   
            # 'D' shows that the fourth or fifth analyzed turned out to 
            # be dissonant.
            return ('D' + suspect_diss)   

    def run(self):
        """
        Make a new index of the piece which consists of a DataFrame with 
        as many columns as there are voices in the piece. The index is 
        the offset of the dissonance analyses. Another DataFrame 
        (``diss_ints``) is calculated but not returned. It is in the 
        same format as the :class:`IntervalIndexer` (i.e. a DataFrame of 
        Series where each series corresponds to the intervals in a given 
        voice pair). The difference between this and the interval 
        indexer is that this one figures out whether fourths or 
        diminished fifths should be considered consonant for the 
        purposes of dissonance classification. diss_ints is not 
        calculated separately because it essentially consists of the 
        same loop needed for dissonance classification.
        :returns: A :class:`DataFrame` of the new indices. The columns 
            have a :class:`MultiIndex`.
        
        :rtype: :class:`pandas.DataFrame`
        
        """
        diss_ints = self._score[int_ind].copy(deep=True)
        simuls = diss_ints.ffill()

        iterables = [[diss_types], self._score[dur_ind].columns]
        d_types_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
        ret = pandas.DataFrame(index=self._score.index, columns=d_types_multi_index)
        ret.fillna(_no_diss_label, inplace=True)

        for col, pair_title in enumerate(diss_ints.columns):
            voices = pair_title.split(',') 
            # assign top and bottom voices as integers
            top_voice = self._score[dur_ind].columns.get_loc(voices[0])
            bott_voice = self._score[dur_ind].columns.get_loc(voices[1])
            for i, event in enumerate(diss_ints[pair_title]):
                if event in _potential_consonances: 
                    # NB: all other events are definite consonances or 
                    # dissonances or don't qualify as interval onsets.
                    event = self.check_4s_5s(pair_title, i, event, simuls)
                    diss_ints.iat[i, col] = event

                # The interval must be dissonant and neither voice 
                # should already have a dissonance label assigned.
                if (event not in _ignored):
                    # and ret.iat[i, top_voice] in _passes
                    # and ret.iat[i, bott_voice] in _passes):
                    prev_event = diss_ints[pair_title].iloc[:i].last_valid_index()
                    if prev_event is not None:
                        prev_event = diss_ints.at[prev_event, pair_title]
                    # if prev_event not in _consonances and i > 0 
                    #   and (ret.iat[i-1, top_voice] in
                    #   (_pass_rp_label, _pass_dp_label) 
                    #   or ret.iat[i-1, bott_voice] in
                    #   (_pass_rp_label, _pass_dp_label)):
                    #   prev_event = 'm3' 
                    # If there's a passing tone at the preceding note, 
                    # call the prev_event a consonance (any consonance 
                    # will do) so that there can be two passing tones in 
                    # a row.
                    diss_analysis = self.classify(i, pair_title, event, prev_event)
                    if (_weights[ret.iat[i, top_voice]] < _weights[diss_analysis[2]]):
                        ret.iat[i, top_voice] = diss_analysis[2]
                    if (_weights[ret.iat[i, bott_voice]] < _weights[diss_analysis[4]]):
                        ret.iat[i, bott_voice] = diss_analysis[4]

        '''
        # Remove lingering unexplainable labels from notes that are only 
        # dissonant against identifiable dissonances.
        unknowns = numpy.where(ret.values == _unexplainable) 
        # 2-tuple of a list of iloc indecies and a list of corresponding 
        # voice integers.
        for x, ndx in enumerate(unknowns[0]):
            passable = True
            for col, pair in enumerate(diss_ints.columns):
                v_to_check = pair.split(',')
                if str(unknowns[1][x]) not in v_to_check: 
                    # does this pair include the voice with the 
                    # unexplained dissonance?
                    continue
                if diss_ints.iat[ndx, col] in _ignored: 
                    # go to the next line if this pair was a dissonance, 
                    # otherwise continue.
                    continue
                v_to_check.remove(str(unknowns[1][x])) 
                # remove voice with unexplained dissonance to see what 
                # the other voice is doing.
                v_temp = self._score.iloc[:ndx + 1, int(v_to_check[0], 10)].last_valid_index() 
                # since the h_ind is the first df in the concat list, a 
                # voice's integer works to reference its horiz column.
                v_ndx = numpy.where(self._score.index == v_temp)[0][0]
                go_on = False
                for event in range(v_ndx, ndx + 1):
                    if ret.iat[event, int(v_to_check[0])] not in _go_ons:
                        go_on = True
                        break
                if go_on:
                    continue
                passable = False
                break
             if passable:
                ret.iat[ndx, unknowns[1][x]] = _only_diss_w_diss
        '''

        return ret