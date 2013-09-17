#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name:         scripts/entropy_script.py
# Purpose:      Computes the sample entropy of a user-specified n-gram prefix,
#               taken from a user-specified csv file.
#
# Copyright (C) 2013 Alex Morgan, Jamie Klassen
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
A little script for computing the sample entropy of a user-specified n-gram prefix,
taken from a user-specified csv file.
"""

import csv
import math


def main():
    """
    Get the csv file location, ngram prefix, number of its occurrences, base of the logarithm to
    use for computing entropy and preference for displaying the full probability distribution,
    and print the appropriate results to STDOUT.
    """
    print('Please enter the complete file location of a csv file of the results you want to '
          'calculate the entropy of.')
    filelocation = raw_input('File Location: ')
    with open(filelocation, 'rb') as csvfile:
        results = list(csv.reader(csvfile, delimiter=',', quotechar='|'))
    ng_prefix = raw_input('What Ngram prefix are you looking for?: ')
    prefix_occurrences = int(
        raw_input('How many times does {0!r} happen?: '.format(ng_prefix))
    )
    ngrams_w_prefix = [(ngram[:-1], float(freq)/prefix_occurrences) for ngram, freq, _, _, _
                       in results if ng_prefix == ngram[:len(ng_prefix)]]
    print("What log base would you like to use?  If you don't know, enter the number 2. For base"
          " e, type the letter e.")
    base = raw_input('Log base: ')
    base = math.e if base == 'e' else float(base)
    entropy = -sum(prob * math.log(prob, base) for ngram, prob in ngrams_w_prefix)
    print '\nThe entropy of the prefix {} is {}.\n'.format(ng_prefix, entropy)
    yesses = ['y', 'yes']
    calc_prob = raw_input(
        'Show the probability that each Ngram will happen after the given prefix? (y/n): '
    )
    if calc_prob.lower() in yesses:
        for ngram, prob in ngrams_w_prefix:
            print '{}: {:.2f}%'.format(ngram, prob * 100)


if __name__ == '__main__':
    main()
