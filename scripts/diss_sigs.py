#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               scripts/diss_sigs.py
# Purpose:                Demo scripts for our work with "dissonance signatures."
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

What will it do?!
"""

# Delightful hack to make sure we can import "vis"
import imp
try:
    imp.find_module(u'vis')
except ImportError:
    import sys
    sys.path.insert(0, u'..')

# now actually import vis
from vis.analyzers.indexers import noterest, interval, dissonance
from vis.models.indexed_piece import IndexedPiece

# the piece we'll analyze... currently Kyrie of Palestrina's Missa "Dies sanctificatus"
the_piece = IndexedPiece(u'test_corpus/Kyrie.krn')

# don't touch this (yet); it's settings required by DissonanceIndexer
setts = {u'quality': True, 'simple or compound': u'simple'}

# find the intervals
intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                interval.IntervalIndexer],
                               setts)

# find the dissonances
interv_combos = intervals.keys()
interv_input = [intervals[combo] for combo in interv_combos]
dissonances = the_piece.get_data([dissonance.DissonanceIndexer], None, interv_input)
dissonances = {interv_combos[i]: dissonances[i] for i in xrange(len(interv_combos))}

# as an example, we'll just use voice-pair [0, 1] (highest and second-highest)
for label in intervals[u'0,1'].index:
    if dissonances[u'0,1'].loc[label] is None:
        print(str(label) + '\t' + str(intervals[u'0,1'].loc[label]))
    else:
        print(str(label) + '\t' + str(intervals[u'0,1'].loc[label]) + ' --> ' + str(dissonances[u'0,1'].loc[label]))



#print(str(dissonances))

#for i, piece in enumerate(self._data):
    #vert_ints = piece.get_data([noterest.NoteRestIndexer, interval.IntervalIndexer], setts)
    ## figure out which combinations we need... this might raise a ValueError, but there's
    ## not much we can do to save the situation, so we might as well let it go up
    #combos = unicode(self.settings(i, u'voice combinations'))
    #if combos != u'all' and combos != u'all pairs' and combos != u'None':
        #combos = ast.literal_eval(combos)
        #vert_ints = WorkflowManager._remove_extra_pairs(vert_ints, combos)
    ## we no longer need to know the combinations' names, so we can make a list
    #vert_ints = list(vert_ints.itervalues())
    ## run the offset and repeat indexers, if required
    #post = self._run_off_rep(i, vert_ints)
    ## remove the "Rest" entries, if required
    #if self.settings(None, u'include rests') is not True:
        ## we'll just get a view that omits the "Rest" entries in the Series
        #for i, pair in enumerate(post):
            #post[i] = pair[pair != u'Rest']
    #self._result.append(post)
#if self.settings(None, 'count frequency') is True:
    #self._run_freq_agg()
#return self._result
