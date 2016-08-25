#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name:         scripts/4vv_parser.py
# Purpose:      Parses csv file to find dissonances.
#
# Copyright (C) 2016 Sam Howes
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
This script generates a list of sonority types according to Fuller (1986) from
the csv output of the vertical interval indexer. It measures intervals against
the lowest sounding note (first large for loop) and labels them according to
the characters they contain (second large for loop).
"""

import csv

fileName = raw_input('\nEnter file name\n>')

rows = []  # a list of the rows in the CSV file
sonorities = []  # a list of the sonorities in each row (as strings)
results = []  # a list of the results represented as letters (P, M, I, D, R)

# get rows
with open(fileName) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')

    for row in readCSV:
        if row[0] != 'Indexer' and row[0] != 'Parts' and row[0] != '':
            rows.append(row[-6:])

# get sonorities
for r in rows:

    # if 3 or more voices have rests
    if r.count('Rest') > 5:
        s = ['Rest']

    # if voice 3 has a rest
    elif r[2] == r[4] == r[5] == 'Rest':

        # if voice 2 also has a rest
        if r[1] == r[3] == 'Rest':
            if '-' in r[0]:
                s = [r[0][-2:]]
            else:
                s = [r[0]]

        # if voice 2 has a note
        else:
            if '-' in r[3]:
                s = [r[0], r[3][-2:]]
            elif '-' in r[1]:
                s = [r[0][-2:], r[1][-2:]]
            else:
                s = [r[1], r[3]]

    # if all four voices have notes
    elif r[2] != 'Rest' and r[4] != 'Rest' and r[5] != 'Rest':
        if '-' in r[5]:
            s = [r[1], r[3], r[5][-2:]]
        elif '-' in r[4]:
            s = [r[0], r[3][-2:], r[4][-2:]]
        else:
            s = [r[2], r[4], r[5]]

    # if voice 3 has a note and at least one of the other voices has a rest
    else:
        if '-' in r[5] and 'Rest' in r[1]:
            s = [r[3], r[5][-2:]]
        elif '-' in r[5] and 'Rest' in r[3]:
            s = [r[1], r[5][-2:]]
        elif '-' in r[4] and 'Rest' in r[5]:
            s = [r[0], r[4][-2:]]
        elif '-' in r[4] and 'Rest' in r[0]:
            s = [r[3][-2:], r[4][-2:]]
        else:
            s = [r[2], r[4], r[5]]

    sonorities.append(s)

# get results
for s in sonorities:

    ss = str(s)

    if ss == 'Rest':
        results.append('R')

    elif any(x in ss for x in ['d', 'A', '2', '7', '4']):
        results.append('D')

    elif '3' not in ss and '6' not in ss:
        results.append('P')

    elif '1' not in ss and '5' not in ss and '8' not in ss:
        results.append('I')

    elif '5' in ss and '6' in ss:  # the only special case
        results.append('D')

    else:
        results.append('M')

print(results)
