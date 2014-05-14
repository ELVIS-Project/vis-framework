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
from music21 import converter
from vis.analyzers.indexers import noterest, interval, dissonance, metre
from vis.models.indexed_piece import IndexedPiece
from vis.workflow import WorkflowManager
from numpy import NaN, isnan
import pandas

# the piece we'll analyze... currently Kyrie of Palestrina's Missa "Dies sanctificatus"
print(u'\n\nLoading the piece and running the NoteRestIndexer...\n')
piece_path = u'vis/tests/corpus/bwv77.mxl'
the_piece = IndexedPiece(piece_path)

# don't touch this (yet); it's settings required by DissonanceIndexer
setts = {u'quality': True, 'simple or compound': u'simple'}

# find the intervals
print(u'\n\nRunning the IntervalIndexer...\n')
notes = the_piece.get_data([noterest.NoteRestIndexer])
intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                interval.IntervalIndexer],
                               setts)
horiz_intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                      interval.HorizontalIntervalIndexer],
                                     setts)

# find the dissonances
print(u'\n\nRunning the DissonanceIndexer...\n')
dissonances = the_piece.get_data([dissonance.DissonanceIndexer], data=intervals)

# get and display the output from the "beatStrength" indexer
print(u'\n\nRunning the NoteBeatStrengthIndexer...\n')
beat_strengths = the_piece.get_data([metre.NoteBeatStrengthIndexer],
                                    data=converter.parse(piece_path))  # TODO: fix the model

# collect all the results into a single DataFrame
new_df = pandas.concat(objs=[notes, intervals, horiz_intervals, dissonances, beat_strengths],
                       axis=1, join='outer')


# "forward fill" the IntervalIndexer results (required by the "dissonance" module)
new_df = new_df.T
new_ints = new_df.loc['interval.IntervalIndexer'].fillna(method='ffill', axis=1)
new_multiindex = [('interval.IntervalIndexer', x) for x in list(new_ints.index)]
new_ints.index = pandas.MultiIndex.from_tuples(new_multiindex)
new_df.update(new_ints)
new_df = new_df.T
del new_ints

# run() for SuspensionIndexer
print(u'\n\nRunning the SuspensionIndexer...\n')
new_df = dissonance.SuspensionIndexer(new_df).run()

# output the whole DataFrame to a CSV file, for easy viewing
new_df.to_csv('test_output/nice_results.csv')
new_df.to_excel('test_output/nice_results.xlsx')

## LilyPond Output! ##
# break a WorkflowManager so we can get annotated score output
#print(u'\n\nPreparing and outputting the score, running LilyPond, etc.\n')
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
