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

# indexer function for SuspendionIndexer
# - x: melodic interval of lower part into suspension, not unison (upper part is unison)
# - d: dissonant harmonic interval
# - y: melodic interval of lower part out of suspension (upper part is -2)
# - z: d-y if y >= 1 else d-y-2 (it's the resolution vert-int)
def susp_detector(one_row, next_row, offset):
    post = []
    for combo in one_row['dissonance.DissonanceIndexer'].index:
        upper_i = int(combo.split(u',')[0])
        lower_i = int(combo.split(u',')[0])
        # is there a dissonance?
        if (isinstance(one_row['dissonance.DissonanceIndexer'][combo], basestring) or
            (not isnan(one_row['dissonance.DissonanceIndexer'][combo]))):
            # check x (lower part of melodic into diss)
            if one_row['interval.HorizontalIntervalIndexer'][lower_i] == 'P1':
                post.append('other diss')
                continue
            # set d (diss vert int)
            d = int(one_row['dissonance.DissonanceIndexer'][combo][-1:])
            # set y (lower part melodic out of diss)
            y = (1 if (not isinstance(next_row['interval.HorizontalIntervalIndexer'][lower_i], basestring)
                       and isnan(next_row['interval.HorizontalIntervalIndexer'][lower_i]))
                 else int(next_row['interval.HorizontalIntervalIndexer'][lower_i][-1:]))
            # set z (vert int after diss)
            try:
                z = int(next_row['interval.IntervalIndexer'][combo][-1:])
            except TypeError:
                z = 1
            # deal with z
            if (y >= y and d - y == z) or (d - y - 2 == z):
                post.append('susp')
            else:
                post.append('other diss')
        else:
            post.append(NaN)
    return pandas.Series(post, index=one_row['dissonance.DissonanceIndexer'].index)

# run() for SuspensionIndexer
print(u'\n\nRunning the faux SuspensionIndexer...\n')
results = []
for i in xrange(len(new_df.index) - 1):
    results.append(susp_detector(new_df.iloc[i], new_df.iloc[i + 1], i))
results.append(pandas.Series([NaN for _ in xrange(len(results[0]))]))  # because we did the "- 1" thing in the loop above
tuples = [(u'prelim-SuspensionIndexer', combo) for combo in results[0].index]
multiindex = pandas.MultiIndex.from_tuples(tuples, names=[u'Indexer', u'Parts'])
for i in xrange(len(results)):
    results[i] = pandas.Series(results[i].values, index=multiindex)
results = pandas.DataFrame({new_df.index[j]: results[i] for i, j in enumerate(new_df.index)}).T

# add the prelim-SuspensionIndexer results onto the existing results
new_df = pandas.concat(objs=[new_df, results], axis=1, join='outer')

# output the whole DataFrame to a CSV file, for easy viewing
new_df.to_csv('test_output/nice_results.csv')

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
