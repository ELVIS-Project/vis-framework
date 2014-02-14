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

print(u'DEBUG 1')  # DEBUG

# Delightful hack to make sure we can import "vis"
import imp
try:
    imp.find_module(u'vis')
except ImportError:
    import sys
    sys.path.insert(0, u'..')

print(u'DEBUG 2')  # DEBUG

# now actually import vis
from vis.analyzers.indexers import noterest, interval, dissonance, metre
from vis.models.indexed_piece import IndexedPiece

print(u'DEBUG 3')  # DEBUG

# the piece we'll analyze... currently Kyrie of Palestrina's Missa "Dies sanctificatus"
the_piece = IndexedPiece(u'test_corpus/Kyrie.krn')

print(u'DEBUG 4')  # DEBUG

# don't touch this (yet); it's settings required by DissonanceIndexer
setts = {u'quality': True, 'simple or compound': u'simple'}

print(u'DEBUG 5')  # DEBUG

# find the intervals
intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                interval.IntervalIndexer],
                               setts)

print(u'DEBUG 6')  # DEBUG

# find the dissonances
interv_combos = intervals.keys()
interv_input = [intervals[combo] for combo in interv_combos]
dissonances = the_piece.get_data([dissonance.DissonanceIndexer], None, interv_input)
dissonances = {interv_combos[i]: dissonances[i] for i in xrange(len(interv_combos))}

print(u'DEBUG 7')  # DEBUG

# as an example, we'll just use voice-pair [0, 1] (highest and second-highest)
print(u'Output from DissonanceIndexer (top two voices):\n')
for label in intervals[u'0,1'].index:
    if dissonances[u'0,1'].loc[label] is None:
        print(str(label) + '\t' + str(intervals[u'0,1'].loc[label]))
    else:
        print(str(label) + '\t' + str(intervals[u'0,1'].loc[label]) + ' --> ' + str(dissonances[u'0,1'].loc[label]))


# get and display the output from the "beatStrength" indexer
print(u'\n\nOutput from NoteBeatStrengthIndexer (top two voices):\n')
beat_strengths = the_piece.get_data([metre.NoteBeatStrengthIndexer])
print(str(beat_strengths))
