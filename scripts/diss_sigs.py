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
    sys.path.insert(0, u'.')  # NB: somehow, this lets us find the outputlilypond submodule
    sys.path.insert(1, u'..')

# now actually import vis
from vis.analyzers.indexers import noterest, interval, dissonance, metre
from vis.models.indexed_piece import IndexedPiece
from vis.workflow import WorkflowManager
import pandas

# the piece we'll analyze... currently Kyrie of Palestrina's Missa "Dies sanctificatus"
piece_path = u'test_corpus/bwv2.xml'
the_piece = IndexedPiece(piece_path)

# don't touch this (yet); it's settings required by DissonanceIndexer
setts = {u'quality': True, 'simple or compound': u'simple'}

# find the intervals
intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                interval.IntervalIndexer],
                               setts)

# find the dissonances
print(u'\n\nRunning the DissonanceIndexer...\n')
interv_combos = intervals.keys()
interv_input = [intervals[combo] for combo in interv_combos]
dissonances = the_piece.get_data([dissonance.DissonanceIndexer], None, interv_input)
dissonances = {interv_combos[i]: dissonances[i] for i in xrange(len(interv_combos))}

# as an example, we'll just use voice-pair [0, 1] (highest and second-highest)
print(u'Output from DissonanceIndexer (top two voices):\n')
new_df = pandas.DataFrame({'intervals': intervals['0,1'], 'dissonances': dissonances['0,1']})
print(new_df)
#for label in intervals[u'0,1'].index:
    #if label in dissonances[u'0,1'].index:
        #print(str(label) + '\t' + str(intervals[u'0,1'].loc[label]) + ' --> ' + str(dissonances[u'0,1'].loc[label]))
    #else:
        #print(str(label) + '\t' + str(intervals[u'0,1'].loc[label]))

## get and display the output from the "beatStrength" indexer
#print(u'\n\nRunning the NoteBeatStrengthIndexer...\n')
#beat_strengths = the_piece.get_data([metre.NoteBeatStrengthIndexer])
##print(u'Output from NoteBeatStrengthIndexer (top voice):\n')
##print(str(beat_strengths[0]))

## break a WorkflowManager so we can get annotated score output
#print(u'\n\nPreparing and outputting the score, running LilyPond, etc.\n')
## 1.) collect indicces for this part combo
#part_diss_orig = dissonances[u'0,1']
#beats_zero_orig = beat_strengths[0]
#beats_one_orig = beat_strengths[1]
## 2.) filter out where there isn't a dissonance
#part_diss = part_diss_orig[~part_diss_orig.isin([None])]
#beats_zero = beats_zero_orig[~part_diss_orig.isin([None])]
#beats_one = beats_one_orig[~part_diss_orig.isin([None])]
## 3.) mangle the WorkflowManager
#workm = WorkflowManager([piece_path])
#workm._result = [[part_diss, beats_zero, beats_one]]
#workm.output('LilyPond', 'test_output/asdf_diss')
