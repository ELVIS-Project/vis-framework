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
from numpy import nan as NaN
import pandas

# the piece we'll analyze... currently Kyrie of Palestrina's Missa "Dies sanctificatus"
piece_path = u'test_corpus/bwv77.mxl'
the_piece = IndexedPiece(piece_path)

# don't touch this (yet); it's settings required by DissonanceIndexer
setts = {u'quality': True, 'simple or compound': u'simple'}

# find the intervals
notes = the_piece.get_data([noterest.NoteRestIndexer])
intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                interval.IntervalIndexer],
                               setts)
horiz_intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                interval.HorizontalIntervalIndexer],
                               setts)


# find the dissonances
print(u'\n\nRunning the DissonanceIndexer...\n')
interv_combos = intervals.keys()
interv_input = [intervals[combo] for combo in interv_combos]
dissonances = the_piece.get_data([dissonance.DissonanceIndexer], None, interv_input)
dissonances = {interv_combos[i]: dissonances[i] for i in xrange(len(interv_combos))}

# get and display the output from the "beatStrength" indexer
print(u'\n\nRunning the NoteBeatStrengthIndexer...\n')
beat_strengths = the_piece.get_data([metre.NoteBeatStrengthIndexer])

# as an example, we'll just use voice-pair [0, 1] (highest and second-highest)
#print(u'Output (top two voices):\n')
the_columns = pandas.MultiIndex.from_tuples([('NoteRestIndexer', 0), ('NoteRestIndexer', 1),
                                             ('NoteBeatStrengthIndexer', 0), ('NoteBeatStrengthIndexer', 1),
                                             ('HorizontalIntervalIndexer', 0), ('HorizontalIntervalIndexer', 1),
                                             ('IntervalIndexer', '0,1'), ('DissonanceIndexer', '0,1')])
new_df = pandas.DataFrame({0: notes[0],
                           1: notes[1],
                           2: beat_strengths[0],
                           3: beat_strengths[1],
                           4: horiz_intervals[0],
                           5: horiz_intervals[1],
                           6: intervals['0,1'],
                           7: dissonances['0,1']})
new_df.columns = the_columns
#print(new_df)
#print('=============\noffset 25.00:\n=============')
#print(new_df.loc[25.00])


# indexer function for SuspendionIndexer
# - x: melodic interval of lower part into suspension, not unison (upper part is unison)
# - d: dissonant harmonic interval
# - y: melodic interval of lower part out of suspension (upper part is -2)
# - z: d-y if y >= 1 else d-y-2 (it's the resolution vert-int)
def susp_detector(one_row, next_row, offset):
    # is there a dissonance?
    if one_row['DissonanceIndexer']['0,1'] is not NaN:
        # check x (lower part of melodic into diss)
        if one_row['HorizontalIntervalIndexer'][1] == 'P1':
            return 'other diss'
        # set d (diss vert int)
        d = int(one_row['DissonanceIndexer']['0,1'][-1:])
        # set y (lower part melodic out of diss)
        y = 1 if next_row['HorizontalIntervalIndexer'][1] is NaN else int(next_row['HorizontalIntervalIndexer'][1][-1:])
        # set z (vert int after diss)
        z = int(next_row['IntervalIndexer']['0,1'][-1:])
        # deal with z
        if (y >= y and d - y == z) or (d - y - 2 == z):
            return 'susp'
        else:
            return 'other diss'
    else:
        return NaN

# run() for SuspensionIndexer
results = []
for i in xrange(len(new_df.index) - 1):
    results.append(susp_detector(new_df.iloc[i], new_df.iloc[i + 1], i))
results.append(NaN)  # because we did the "- 1" thing in the loop above

# This is a bit of a hack to get the new results into the existing MultiIndex DataFrame...
# I still need to figure out how to specify both levels, so we can specify voice pairs
new_df.T.loc['SuspensionIndexer'] = None
new_df['SuspensionIndexer'] = pandas.Series(results, index=new_df.index)

# output the whole DataFrame to a CSV file, for easy viewing
new_df.to_csv('test_output/nice_results.csv')

## LilyPond Output! ##
# break a WorkflowManager so we can get annotated score output
print(u'\n\nPreparing and outputting the score, running LilyPond, etc.\n')
# 1.) collect indicces for this part combo
#part_diss_orig = dissonances[u'0,1']
#beats_zero_orig = beat_strengths[0]
#beats_one_orig = beat_strengths[1]
# 2.) filter out where there isn't a dissonance
#susp_index = new_df['SuspensionIndexer']
#susp_index = susp_index[susp_index == 'susp']
#part_diss = part_diss_orig[~part_diss_orig.isin([None])]
#beats_zero = beats_zero_orig[~part_diss_orig.isin([None])]
#beats_one = beats_one_orig[~part_diss_orig.isin([None])]
# 3.) mangle the WorkflowManager
#workm = WorkflowManager([piece_path])
#workm._result = [[susp_index]]
#workm.output('LilyPond', 'test_output/asdf_diss')
