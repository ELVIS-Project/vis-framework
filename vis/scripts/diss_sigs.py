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
"""
.. codeauthor:: Christopher Antila <christopher@antila.ca>

What will it do?!
"""

from collections import defaultdict

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
from vis.analyzers.experimenters import aggregator, frequency
from vis.models.indexed_piece import IndexedPiece
from vis.workflow import WorkflowManager
from numpy import NaN, isnan
import pandas

# the piece we'll analyze... currently Kyrie of Palestrina's Missa "Dies sanctificatus"
print(u'\n\nLoading the piece and running the NoteRestIndexer...\n')
piece_path = u'vis/tests/corpus/Palestrina-Lhomme_arme_1582-Agnus_I.krn'
#piece_path = u'vis/tests/corpus/bwv77.mxl'
the_piece = IndexedPiece(piece_path)

# don't touch this (yet); it's settings required by DissonanceIndexer
setts = {u'quality': True, 'simple or compound': u'simple'}

# find the intervals
print(u'\n\nRunning the IntervalIndexer...\n')
intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                interval.IntervalIndexer],
                               setts)
horiz_intervals = the_piece.get_data([noterest.NoteRestIndexer,
                                      interval.HorizontalIntervalIndexer],
                                     setts)

# find the dissonances
print(u'\n\nRunning the DissonanceIndexer...\n')
dissonances = the_piece.get_data([noterest.NoteRestIndexer,
                                  interval.IntervalIndexer,
                                  dissonance.DissonanceIndexer],
                                 setts)

# get and display the output from the "beatStrength" indexer
print(u'\n\nRunning the NoteBeatStrengthIndexer...\n')
beat_strengths = the_piece.get_data([metre.NoteBeatStrengthIndexer], setts)

# collect all the results into a single DataFrame
new_df = pandas.concat(objs=[intervals, horiz_intervals, dissonances, beat_strengths],
                       axis=1,
                       join='outer')

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
susp_df = dissonance.SuspensionIndexer(new_df).run()
neigh_df = dissonance.NeighbourNoteIndexer(new_df).run()
pass_df = dissonance.PassingNoteIndexer(new_df).run()

combined_df = susp_df['dissonance.SuspensionIndexer'].combine_first(neigh_df['dissonance.NeighbourNoteIndexer'])

# output the whole DataFrame to a CSV file, for easy viewing
print('\nOutputting per-piece results to a spreadsheet\n')
combined_df.to_excel('test_output/combined_dissonances.xlsx')
neigh_df.to_excel('test_output/neighbours.xlsx')

# Make the one-column-per-part DataFrame
# NOTE: this requires that *every* value is prefixed with a voice number (i.e., you can't have called fillna() yet)
post = {str(i): defaultdict(lambda *x: NaN) for i in xrange(len(the_piece.metadata('parts')))}
for combo_i in combined_df:
    for i, value in combined_df[combo_i].iteritems():
        if (not isinstance(value, basestring)) and isnan(value):
            continue
        split_value = value.split(':')
        which_part_i = split_value[0]
        post[which_part_i][i] = split_value[1]
for key in post.iterkeys():
    post[key] = pandas.Series(post[key])
combined_df = pandas.DataFrame(post)
del post

# Replace all the NaNs with '_'.
combined_df = combined_df.fillna(value='_')

# TODO: NOTE: TEST: this is temporary
combined_df = pass_df['dissonance.PassingNoteIndexer'].fillna(value='_')

# aggregate results and count frequency, then output that
# NOTE: for this to work, I'll have to prepare ColumnAggregator and FrequencyExperimenter for vis-framework-2.0.0
#print('\nCalculating and outputting aggregated frequencies\n')
#freq_results = the_piece.get_data([aggregator.ColumnAggregator, frequency.FrequencyExperimenter],
                                  #None,
                                  #new_df['dissonance.SuspensionIndexer'])
#freq_results.sort(ascending=False)
#freq_results.to_excel('test_output/aggregated_results.xlsx')

## LilyPond Output! ##
# break a WorkflowManager so we can get annotated score output
print(u'\n\nPreparing and outputting the score, running LilyPond, etc.\n')
# 1.) collect indices for this part combo
#part_diss_orig = dissonances[u'0,1']
#beats_zero_orig = beat_strengths[0]
#beats_one_orig = beat_strengths[1]
# 2.) filter out where there isn't a dissonance
#susp_index = new_df['dissonance.SuspensionIndexer']['0,1']
#part_diss = part_diss_orig[~part_diss_orig.isin([None])]
#beats_zero = beats_zero_orig[~part_diss_orig.isin([None])]
#beats_one = beats_one_orig[~part_diss_orig.isin([None])]
# 3.) mangle the WorkflowManager
workm = WorkflowManager([piece_path])
workm.settings(None, 'voice combinations', '[[0, 1]]')
workm.settings(None, 'count frequency', False)
#workm._result = [new_df['dissonance.SuspensionIndexer']]
#workm._result = [new_df['dissonance.NeighbourNoteIndexer']]
#workm._result = [new_df['dissonance.PassingNoteIndexer']]
workm._result = [combined_df]
workm.output('LilyPond', 'test_output/combined_dissonances')
