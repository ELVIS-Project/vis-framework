#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/offset.py
# Purpose:                Indexer to regularize the observed offsets.
#
# Copyright (C) 2013, 2014, 2016 Christopher Antila, Alexander Morgan
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
.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. codeauthor:: Alexander Morgan

Indexers that modify the "offset" values (floats stored as the "index" 
of a :class:`pandas.Series`), potentially adding repetitions of or 
removing pre-existing events, without modifying the events
themselves.

"""

import six
import pandas
import numpy
from vis.analyzers import indexer
from multi_key_dict import multi_key_dict as mkd

class FilterByOffsetIndexer(indexer.Indexer):
    """
    Indexer that regularizes the "offset" values of observations from 
    other indexers.

    The Indexer regularizes observations from offsets spaced any, 
    possibly irregular, ``quarterLength`` durations apart, so they are 
    instead observed at regular intervals. This has two effects:

    * events that do not begin at an observed offset will only be 
      included in the output if no other event occurs before the next 
      observed offset
    
    * events that last for many observed offsets will be repeated for 
      those offsets

    Since elements' durations are not recorded, the last observation in 
    a Series will always be included in the results. If it does not 
    start on an observed offset, it will be included as the next 
    observed offset---again, whether or not this is true in the actual 
    music. However, the last observation will only ever be counted once, 
    even if a part ends before others in a piece with many parts. See 
    the doctests for examples.

    **Examples:** 

    For all, the ``quarterLength`` is ``1.0``.

    When events in the input already appear at intervals of 
    ``quarterLength``, input and output are identical.

    +--------+-------+-------+-------+
    | offset | 0.0   | 1.0   | 2.0   |
    +========+=======+=======+=======+
    | input  | ``a`` | ``b`` | ``c`` |
    +--------+-------+-------+-------+
    | output | ``a`` | ``b`` | ``c`` |
    +--------+-------+-------+-------+

    When events in the input appear at intervals of ``quarterLength``, 
    but there are additional elements between the observed offsets, 
    those additional elements are removed.

    +--------+-------+-------+-------+-------+
    | offset | 0.0   | 0.5   | 1.0   | 2.0   |
    +========+=======+=======+=======+=======+
    | input  | ``a`` | ``A`` | ``b`` | ``c`` |
    +--------+-------+-------+-------+-------+
    | output | ``a``         | ``b`` | ``c`` |
    +--------+---------------+-------+-------+

    +--------+-------+-------+-------+-------+-------+
    | offset | 0.0   | 0.25  | 0.5   | 1.0   | 2.0   |
    +========+=======+=======+=======+=======+=======+
    | input  | ``a`` | ``z`` | ``A`` | ``b`` | ``c`` |
    +--------+-------+-------+-------+-------+-------+
    | output | ``a``                 | ``b`` | ``c`` |
    +--------+-----------------------+-------+-------+

    When events in the input appear at intervals of ``quarterLength``, 
    but not at every observed offset, the event from the previous offset 
    is repeated.

    +--------+-------+-------+-------+
    | offset | 0.0   | 1.0   | 2.0   |
    +========+=======+=======+=======+
    | input  | ``a``         | ``c`` |
    +--------+-------+-------+-------+
    | output | ``a`` | ``a`` | ``c`` |
    +--------+-------+-------+-------+

    When events in the input appear at offsets other than those observed 
    by the specified ``quarterLength``, the "most recent" event will 
    appear.

    +--------+-------+-------+-------+-------+-------+
    | offset | 0.0   | 0.25  | 0.5   | 1.0   | 2.0   |
    +========+=======+=======+=======+=======+=======+
    | input  | ``a`` | ``z`` | ``A``         | ``c`` |
    +--------+-------+-------+-------+-------+-------+
    | output | ``a``                 | ``A`` | ``c`` |
    +--------+-----------------------+-------+-------+

    When the final event does not appear at an observed offset, it will 
    be included in the output at the next offset that would be observed, 
    even if this offset does not appear in the score file to which the 
    results correspond.

    +--------+-------+-------+-------+-------+
    | offset | 0.0   | 1.0   | 1.5   | 2.0   |
    +========+=======+=======+=======+=======+
    | input  | ``a`` | ``b`` | ``d``         |
    +--------+-------+-------+-------+-------+
    | output | ``a`` | ``b``         | ``d`` |
    +--------+-------+---------------+-------+

    The behaviour in this last example can create a potentially 
    misleading result for some analytic situations that consider meter. 
    It avoids another potentially misleading situation where the final 
    chord of a piece would appear to be dissonant because of a 
    suspension. We chose to lose metric and rythmic precision, which 
    would be more profitably analyzed with indexers built for that 
    purpose. Consider this illustration, where the numbers correspond to 
    scale degrees.

    +--------+-------+-------+-------+-------+
    | offset | 410.0 | 411.0 | 411.5 | 412.0 |
    +========+=======+=======+=======+=======+
    | in-S   | 2     | 1                     |
    +--------+-------+-----------------------+
    | in-A   | 7     | 5                     |
    +--------+-------+-------+---------------+
    | in-T   | 4 ----------- | 3             |
    +--------+-------+-------+---------------+
    | in-B   | 5     | 1                     |
    +--------+-------+---------------+-------+
    | out-S  | 2     | 1             | 1     |
    +--------+-------+---------------+-------+
    | out-A  | 7     | 5             | 5     |
    +--------+-------+---------------+-------+
    | out-T  | 4     | 4             | 3     |
    +--------+-------+---------------+-------+
    | out-B  | 5     | 1             | 1     |
    +--------+-------+---------------+-------+

    If we left out the note event appear in the ``in-A`` part at offset 
    ``411.5``, the piece would appear to end with a dissonant sonority!

    *****

    Concerning the "dynamic-offset method", this can be accessed by 
    passing the string "dynamic" for the quarterLength setting. This 
    type of analysis is still experimental and comes with no guarantee 
    that it will work accurately. It has the important known limitation 
    that it only applies to Renaissance polyphony in which the 
    contrapuntal rhythm is only ever in duple groupings. For more on 
    contrapuntal rhythm, see:

    DeFord, Ruth. Tactus Mensuration, and Rhythm in Renaissance Music. 
        Cambridge: Cambridge University Press, 2015.

    For a more thorough explanation of the experimental dynamic-offset 
    method see (especially chapter 4):

    Morgan, Alexander. "Renaissance Interval-Succession Theory: Treatises 
        and Analysis." PhD diss., McGill University, 2017.
    
    Helper functions have been implemented to facilitate the use of the 
    dynamic-offset method, so you can run analyses in the following way:

    from vis.models.indexed_piece import Importer
    ip = Importer('full_path_to_piece_in_symbolic_notation.xml')
    # assuming you want to apply the offset filter to the noterest 
    # indexer results:
    nr = ip.get_data('noterest')
    setts = {'quarterLength': 'dynamic'}
    filtered_nr = ip.get_data('offset', data=nr, settings=setts)
    """

    required_score_type = 'pandas.Series'
    "The :class:`FilterByOffsetIndexer` uses :class:`pandas.Series` objects."

    possible_settings = ['quarterLength', 'dom_data', 'method', 'mp']
    
    """
    A ``list`` of possible settings for the 
    :class:`FilterByOffsetIndexer`.

    :keyword 'quarterLength': The quarterLength duration between 
        observations desired in the output. This value must not have 
        more than three digits to the right of the decimal (i.e. 0.001 
        is the smallest possible value). For dynamic (i.e. variable)
        and context-dependent value, pass the string 'dynamic'.
    
    :type 'quarterLength': float or string

    :keyword 'dom_data': A list of DataFrames and one integer is 
        required here if the 'quarterLength' setting is set to 
        'dynamic'. This list should contain the dissonance, duration, 
        beatstrength, and noterest indexer dataframes and finally the 
        "highest_time" of the piece or movement in that order. The 
        correct information is automatically fetched if this indexer is 
        called on an IndexedPiece object via the get_data method() if
        the 'data' argument in that method is not passed.
    
    :keyword 'method': The value passed as the ``method`` kwarg to 
        :meth:`~pandas.DataFrame.reindex`. The default is ``'ffill'``, 
        which fills in missing indices with the previous value. This is
        useful for vertical intervals, but not for horizontal, where you 
        should use ``None`` instead.
    
    :type 'method': str or None
    
    :keyword 'mp': Multiprocesses when True (default) or processes 
        serially when False.
    
    :type 'mp': boolean

    **Examples:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('path_to_piece.xml')
    >>> notes = ip.get_data('noterest')
    >>> setts = {'quarterLength': 2}
    >>> ip.get_data('offset', data=notes, settings=setts)

    # Note that other analysis results can be passed to the offset 
    # indexer too, such as the IntervalIndexer results as in the 
    # following example. Also, the original column names (or names of 
    # the series if a list of series was passed) are retained, though 
    # the highest level of the columnar multi-index gets overwritten

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('path_to_piece.xml')
    >>> intervals = ip.get_data('vertical_interval')
    >>> setts = {'quarterLength': 2}
    >>> ip.get_data('offset', data=intervals, settings=setts)
        
    """
    
    default_settings = {'method': 'ffill', 'mp': True, 'dom_data':[]}

    _ZERO_PART_ERROR = (u'FilterByOffsetIndexer requires an index ' + 
        'with at least one part.')
    _NO_QLENGTH_ERROR = (u'FilterByOffsetIndexer requires a ' + 
        '"quarterLength" setting.')
    _QLENGTH_TOO_SMALL_ERROR = (u'FilterByOffsetIndexer requires a ' + 
        '"quarterLength" greater than 0.001.')
    _IMPROPER_DYNAMIC_INPUT = 'FilterByOffsetIndexer requires its score \
parameter to be a list of the dissonance, duration, beatstrength, noterest, \
and timesignature indexers (in that order) if the "quarterLength" setting is \
set to "dynamic"'
    _UNSUPPORTED_TIME_SIGNATURE = 'FilterByOffsetIndexer only supports \
the following time signatures when the "quarterLength" setting is set to \
"dynamic": {}.'

    def __init__(self, score, settings=None):
        """
        :param score: A DataFrame or list of Series you wish to 
            filter by offset values, stored in the Index.
        
        :type score: :class:`pandas.DataFrame` or 
            ``list`` of :class:`pandas.Series` or 
            ``list`` of :class:`pandas.DataFrame`
        
        :param dict settings: There is one required setting. 
            See :const:`possible_settings`.

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the 
            same types.
        
        :raises: :exc:`RuntimeError` if the required setting is not 
            present in ``settings``.
        
        :raises: :exc:`RuntimeError` if the ``'quarterLength'`` setting 
            has a value less than ``0.001``.

        """
        super(FilterByOffsetIndexer, self).__init__(score, None)

        # check the settings instance has a u'quarterLength' property.
        if settings is None or u'quarterLength' not in settings:
            raise RuntimeError(FilterByOffsetIndexer._NO_QLENGTH_ERROR)
        elif (type(settings['quarterLength']) != str and
              settings[u'quarterLength'] < 0.001):
            raise RuntimeError(FilterByOffsetIndexer._QLENGTH_TOO_SMALL_ERROR)
        
        self._settings = FilterByOffsetIndexer.default_settings.copy()
        self._settings.update(settings)

        # If self._score is a Stream (subclass), change to a list of 
        # types you want to process.
        self._types = []

        # This Indexer uses pandas magic, not an _indexer_func().
        self._indexer_func = None

        # Ensure the score has at least one part.
        if len(self._score) == 0:
            raise RuntimeError(FilterByOffsetIndexer._ZERO_PART_ERROR)

        if (self._settings['quarterLength'] == 'dynamic' and
            len(self._settings['dom_data']) != 6):
            raise RuntimeError(FilterByOffsetIndexer._IMPROPER_DYNAMIC_INPUT)

        valid_meters = ['2/1', '2/2', '4/2', '4/4']
        if (self._settings['quarterLength'] == 'dynamic' and 
            self._settings['dom_data'][4].iloc[0, 0] not in valid_meters):
            raise RuntimeError(FilterByOffsetIndexer._UNSUPPORTED_TIME_SIGNATURE.format(valid_meters))

    def _dynamic_run(self):
        """
        Replacement run method for when the ``quarterLength`` setting 
        is set to 'dynamic'. It assigns context-dependent offset 
        values based on the dissonance types detected in the piece, 
        and its attack density. This setting should only be used for 
        the analysis of Renaissance music with duple divisions in the 
        metric level of the contrapuntal rhythm. For more on 
        contrapuntal rhythm, see Ruth DeFord, 2015.

        :returns: A :class:`DataFrame` with offset-indexed values for 
            all inputted parts. The pandas indices (holding music21 
            offsets) start at the first offset at which there is an
            event in any of the inputted parts. An offset appears at 
            durational intervals equal to the contrapuntal rhythm at 
            that moment in the piece. The value of this contrapuntal 
            rhythm duration is dynamic and can therefore change 
            throughout the course of a piece.
        
        :rtype: :class:`pandas.DataFrame`

        """
        dom_data = self._settings['dom_data']
        #Remove the upper level of the columnar multi-index.
        dds = dom_data[0].copy()
        dds.columns = range(len(dds.columns))
        ddr = dom_data[1].copy()
        ddr.columns = dds.columns
        bbs = dom_data[2].copy()
        bbs.columns = dds.columns
        nnr = dom_data[3].copy()
        nnr.columns = dds.columns
        ts = dom_data[4]

        w = 6

        # Remove weak dissonances
        weaks = ('R', 'D', 'L', 'U', 'E', 'C', 'A')
        indx, cols = numpy.where(dom_data[0].isin(weaks))
        for x in reversed(range(len(indx))):
            spot = ddr.iloc[:indx[x], cols[x]].last_valid_index()
            # Add the weak dissonance duration to the note that immediately precedes it.
            ddr.at[spot, cols[x]] += ddr.iat[indx[x], cols[x]]
            
        # Remove strong dissonances other than suspensions
        strongs = ('Q', 'H')
        indx, cols = numpy.where(dom_data[0].isin(strongs))
        for x in reversed(range(len(indx))):
            spot = ddr.iloc[indx[x]+1:, cols[x]].first_valid_index()
            # Add the strong dissonance duration to the note that immediately follows it.
            ddr.iat[indx[x], cols[x]] += ddr.at[spot, cols[x]]
            ddr.at[spot, cols[x]] = float('nan')
            nnr.iat[indx[x], cols[x]] = nnr.at[spot, cols[x]]
            nnr.at[spot, cols[x]] = float('nan')

        # Delete the duration entries of weak dissonances 
        ddr[dds.isin(weaks)] = float('nan')
        nnr[dds.isin(weaks)] = float('nan')

        # Delete the duration entries of strong dissonances other than suspensions
        ddr[dds.isin(strongs)] = float('nan')

        # Delete duration entries for rests
        ddr = ddr[nnr != 'Rest']
        ddr.dropna(how='all', inplace=True)

        # Attack-density analysis without most dissonances for the whole piece.
        combined = pandas.Series(ddr.index[1:] - ddr.index[:-1], index=ddr.index[:-1])
        comb_roll = combined.rolling(w).mean()

        # Broadcast any bs value to all columns of a df.
        cbs = pandas.concat([dom_data[2].T.bfill().iloc[0]]*len(bbs.columns), axis=1, ignore_index=True)

        diss_levs = mkd({('2/1w', '4/2w'): {.0625: 1, .125: 2, .25: 4, .5: 8, 1: 8}, #NB: things that happen on beats 1 and 3 are treated the same way.
                         ('2/1s', '4/2s'): {.0625: .25, .125: .5, .25: 1, .5: 2, 1: 2},
                         ('2/2w', '4/4w'): {.0625: .5, .125: 1, .25: 2, .5: 4, 1: 4}, #NB: things that happen on beats 1 and 3 are treated the same way.
                         ('2/2s', '4/4s'): {.0625: .125, .125: .25, .25: .5, .5: 1, 1: 1},
                         })

        # Get the beatstrength of the dissonances
        diss_cr = bbs[dds.isin(weaks)]
        time_sig = ts.iloc[0, 0]
        diss_cr.replace(diss_levs[time_sig + 'w'], inplace=True)
        
        swsus = ('S', 'Q', 'H')
        sbs = cbs[dds.isin(swsus)]
        sbs.replace(diss_levs[time_sig + 's'], inplace=True)

        # CR analysis based on dissonance types alone.
        diss_cr.update(sbs)

        cr = comb_roll.copy()
        ccr = cr.copy()
        # Snap the readings to a reasonable note-value grid.
        # The CR reading can only be an eighth, quarter, half, or whole note.
        mlt = 1.25 # top threshhold above which to round CR reading up.
        ccr[cr < .5*mlt] = .5
        ccr[cr > .5*mlt] = 1
        ccr[cr > 1*mlt] = 2
        ccr[cr > 2*mlt] = 4

        for i, val in enumerate(ccr):
            counts = diss_cr.iloc[i:i+w].stack().value_counts()
            lvi = ccr.iloc[:i].last_valid_index()
            if len(counts) > 0 and counts.index[0] == val: # If the most common diss in the window corresponds to the attack-density reading, leave the current val
                continue

            elif lvi is not None and ccr.at[lvi] == val: # There is no dissonance in this window, but the IR analysis has not changed, so the reading is valid
                continue
            else: # The new level has not been confirmed by a corresponding dissonance
                ccr.iat[i] = float('nan')

        ccr.ffill(inplace=True)
        ccr.bfill(inplace=True)
        ccr = ccr.loc[ccr.shift() != ccr] # Remove consecutive duplicates

        # Make the new index
        end_time = int(dom_data[5]) # "highest time" of first part.
        spots = list(ccr.index)
        spots.append(end_time) # Add the index value of the last moment of the piece which usually has no event at it.
        new_index = []
        for i, spot in enumerate(spots[:-1]):
            if spot % ccr.iat[i] != 0:
                spot -= (spot % ccr.iat[i])
            post = list(numpy.arange(spot, spots[i+1], ccr.iat[i])) # you can't use range() because range can't handle floats
            if bool(new_index) and bool(post) and post[0] in new_index:
                del post[0]
            new_index.extend(post)

        if isinstance(self._score, list):
            self._score = pandas.concat(self._score, axis=1)
        return self._score.reindex(index=pandas.Index(new_index)).ffill()

    def run(self):
        """
        Regularize the observed offsets for the Series input.

        :returns: A :class:`DataFrame` with offset-indexed values for 
            all inputted parts. The pandas indices (holding music21 
            offsets) start at the first offset at which there is an
            event in any of the inputted parts. An offset appears every 
            ``quarterLength`` until the final offset, which is either 
            the last observation in the piece (if it is divisible by
            the ``quarterLength``) or the next-highest value that is 
            divisible by ``quarterLength``.
        
        :rtype: :class:`pandas.DataFrame`
        
        """
        if self._settings['quarterLength'] == 'dynamic':
            return self._dynamic_run()
        # NB: we have to convert all the "offset" values to integers so 
        #     we can use the range() function to iterate through 
        #     offsets.
        post = []
        start_offset = None
        try:
            # usually this finds the first offset in the piece
            start_offset = int(min([part.index[0] for part in self._score]) * 1000)
        except (ValueError, IndexError):
            # if one of the parts has 0 length
            start_offset = []
            for part in self._score:
                if 0 < len(part.index):
                    start_offset.append(part.index[0])
            if 0 == len(start_offset):
                # all the parts have no length, so we need as many empty parts
                post = [pandas.Series() for _ in range(len(self._score))]
            else:
                start_offset = int(min(start_offset))
        if 0 == len(post):
            for part in self._score:
                if len(part.index) < 1:
                    post.append(part)
                else:
                    end_offset = int(part.index[-1] * 1000)
                    step = int(self._settings[u'quarterLength'] * 1000)
                    off_list = list(pandas.Series(range(start_offset, end_offset + step, step)).div(1000.0))  
                    # pylint: disable=C0301
                    post.append(part.reindex(index=off_list, method=self._settings['method']))
        post = self.make_return([ser.name[1] for ser in self._score], post)
        return post
