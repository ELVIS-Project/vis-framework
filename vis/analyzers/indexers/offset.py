#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/offset.py
# Purpose:                Indexer to regularize the observed offsets.
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
from vis.analyzers import indexer

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
    
    """

    required_score_type = 'pandas.Series'
    "The :class:`FilterByOffsetIndexer` uses :class:`pandas.Series` objects."

    possible_settings = ['quarterLength', 'method', 'mp']
    
    """
    A ``list`` of possible settings for the 
    :class:`FilterByOffsetIndexer`.

    :keyword 'quarterLength': The quarterLength duration between 
        observations desired in the output. This value must not have 
        more than three digits to the right of the decimal (i.e. 0.001 
        is the smallest possible value).
    
    :type 'quarterLength': float
    
    :keyword 'method': The value passed as the ``method`` kwarg to 
        :meth:`~pandas.DataFrame.reindex`. The default is ``'ffill'``, 
        which fills in missing indices with the previous value. This is
        useful for vertical intervals, but not for horizontal, where you 
        should use ``None`` instead.
    
    :type 'method': str or None
    
    :keyword 'mp': Multiprocesses when True (default) or processes 
        serially when False.
    
    :type 'mp': boolean

    **Example:**

    Prepare an indexed piece:

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('path_to_piece.xml')
    >>> notes = ip.get_data('noterest')
    >>> setts = {'quarterLength': 2}
    >>> ip.get_data('offset', data=notes, settings=setts)
    
    """
    
    default_settings = {'method': 'ffill', 'mp': True}

    _ZERO_PART_ERROR = (u'FilterByOffsetIndexer requires an index ' + 
        'with at least one part.')
    _NO_QLENGTH_ERROR = (u'FilterByOffsetIndexer requires a ' + 
        '"quarterLength" setting.')
    _QLENGTH_TOO_SMALL_ERROR = (u'FilterByOffsetIndexer requires a ' + 
        '"quarterLength" greater than 0.001.')

    def __init__(self, score, settings=None):
        """
        :param score: A list of Series you wish to filter by offset 
            values, stored in the Index.
        
        :type score: ``list`` of :class:`pandas.Series`
        
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
        elif settings[u'quarterLength'] < 0.001:
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

    def run(self):
        """
        Regularize the observed offsets for the inputted Series.

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
        post = self.make_return([six.u(str(x)) for x in range(len(post))], post)
        return post
