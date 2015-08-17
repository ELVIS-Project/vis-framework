#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               GeneralizedICIndexer.py
# Purpose:                Calculate and count occurrences of ngrams under invertible counterpoint
#                         operations and under complete voice-crossing scenarios.
#
# Copyright (C) 2014 Alexander Morgan
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
.. codeauthor:: Alexander Morgan

Note that this script is experimental and is neither tested nor in development at the moment.
It is related to github issue #55.
"""


import csv
import pandas
import numpy

# list of levels of IC ideally provided by the user and limited to between 5 (a fifth) and 14.
ic_levels = [5, 7, 8, 10, 11, 12, 13]

def mod7(x):
    """
    Takes a regular ngram in the form of a list and converts it to a mod7 representation of that
    ngram (i.e. where the unison equals zero, a second equals one, etc) also in the form of a list
    where each interval of the ngram is an int.
    """
    for p in x:
        spot = x.index(p)
        r = int(p)
        if r > 0:
            x[spot] = r - 1
        else:
            x[spot] = r + 1
    return x

def modmus(x):
    """
    Takes a mod7 ngram in the form of a list, returns a regular ngram also in the form of a string.
    Here 'x' is a list whose integer elements form an ngram.
    """
    ret = ''
    for g in x:
        spot = x.index(g)
        if g >= 0:
            x[spot] = g + 1
        else:
            x[spot] = g - 1
        ret += (str(x[spot]) + ' ')
    ret = ret[0:-1]      # Eliminate the superfluous space that was added at the end
    return ret

def icAny(level, ngram):
    """
    Takes a level of transposition represented as a positive integer (not in mod7) and an ngram already
    in mod7 (see mod7 function above) and in the form of a list, inverts it at the level of inversion
    indicated by the ``level`` parameter. Note that only ngrams whose vertical intervals are entirely
    contained within the level of invertible counterpoint or the level of invertible counterpoint plus
    one to nine octaves are used. Returns a mod7 version of that ic8 ngram.
    """
    verts = [] # vertical intervals in ngram
    horiz = [] # horizontal intervals in ngram
    for i, x in enumerate(ngram):
        if i % 2 == 0:
            verts.append(x)
        else:
            horiz.append(x)

    # Ignore the ngrams that include voice crossings
    if all(v >= 0 for v in verts):
        pass
    else:
        return 'N/A'

    # if all the vert intervals are within the same compound octave, keep reducing them until they get to the simple octave
    octs = range(6, 63, 7) # a range of octave spans between the double octave and the nine-fold octave
    if any([all(v > o and v < (o + level + 1) for v in verts) for o in octs]):
            for v in verts:
                verts[verts.index(v)] = v - 7
        for i, x in enumerate(verts):
            ngram[i*2] = x - 7
        return icAny(level, ngram)

    # this is the standard case
    elif all(v >= 0 and v <= lev for v in verts):
        for i, h in enumerate(horiz):    # calculate the new horiz intervals according to the level of inversion, NB: must be done before vert intervals
            ngram[i*2 + 1] = ngram[i*2 + 2] - ngram[i*2] + h
        for i, v in enumerate(verts):    # calculate the new vertical intervals according to the level of inversion
            ngram[i*2] = lev - v
        return ngram

    # NB: this corresponds to when the intervals are not contained in the ambitus of the level of transposition
    elif any(v > lev for v in verts):
        return 'N/A'

def crosser(i):
    """
    Takes a vertical interval and returns its negative value unless it's a unison which stays as a unison.
    """
    if i >= 0:
        return 0 - i
    else:
        return abs(i)

def totCross(ngram):
    """
    Takes an ngram in mod7 where each interval is an integer and returns the ngram (still in mod7)
    that would have been produced if both voices had swapped parts for the entirety of the ngram.
    """
    verts = [] # vertical intervals in ngram
    horiz = [] # horizontal intervals in ngram
    for i, x in enumerate(ngram):
        if i % 2 == 0:
            verts.append(x)
        else:
            horiz.append(x)
    for i, h in enumerate(horiz): # reassign the horizontal intervals, NB: must be done before verticals
        ngram[i*2 + 1] = ngram[i*2 + 2] - ngram[i*2] + h
    for i, v in enumerate(verts): # reassign the vertical intervals
        ngram[i*2] = crosser(v)
    return ngram


df = pandas.read_csv('/home/amor/Desktop/ELVIS_Meeting/J and P Lassus Files/July2014_Query/3gram Analysis July 11 2014/All_duos 3grams.csv')

# Figure out how long the ngrams are to creat an appropriate column title (N_label)
N_label = str(len(df.iloc[0][0].split())/2 + 1) + 'grams'

#make column 0 the ngram names and column 1 their number of occurrences
df.columns = [N_label, 'Occ']

# Convert ngrams to true mod7 representations and set up invertible counterpoint operations
for l in ic_levels:
    ic_inv_ngrams = []
    inv_freqs = []
    for z in range(len(df)):
        n_gram = df[N_label][z].split()
        n_gram = mod7(n_gram)
        n_gram = icAny(l, n_gram)
        if n_gram == 'N/A':
            ic_inv_ngrams.append(n_gram)
        else:
            n_gram = modmus(n_gram)
            ic_inv_ngrams.append(n_gram)

    # Find the frequency of inverted forms in the original ngram list
    for ngram in ic_inv_ngrams:
        try:
            spot = numpy.where(df[N_label] == ngram)[0][0]
        except IndexError:
            inv_freqs.append(0)
        else:
            inv_freqs.append(df['Occ'].iloc[spot])

    # Make appropriate column labels based on the level of invertible counterpoint used.
    ic_label = 'IC' + str(l)
    ic_occ_label = ic_label + ' Occ'
    # Append the IC# lists and their frequencies to the dataframe
    df[ic_label] = ic_inv_ngrams
    df[ic_occ_label] = inv_freqs

crossed_ngrams = []
crossed_freqs = []
for y in range(len(df)):
    n_gram = df[N_label][y].split()
    n_gram = mod7(n_gram)
    n_gram = totCross(n_gram)
    n_gram = modmus(n_gram)
    crossed_ngrams.append(n_gram)

# Find out how many times an ngram repeats exactly but under complete inversion (i.e. the two voices
# swap parts but the same horizontal melodies and vertical intervals are produced).
for ngram in crossed_ngrams:
    try:
        spot = (numpy.where(df[N_label]==ngram)[0])[0]
        crossed_freqs.append(df['Occ'].iloc[spot])
    except IndexError:
        crossed_freqs.append(0)

# Append the crossed version ngrams and their frequencies to the dataframe
df['Swapped'] = crossed_ngrams
df['Swap Occ'] = crossed_freqs

df.to_csv('/home/amor/Desktop/ELVIS_Meeting/J and P Lassus Files/July2014_Query/3gram Analysis July 11 2014/All duos ICMany.csv')


