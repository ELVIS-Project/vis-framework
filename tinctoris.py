#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: tinctoris.py
# Purpose: ?
#
# Copyright (C) 2012, 2013 Jamie Klassen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
Basic analysis for Alex's Tinctoris project.
"""
from vis.controllers.importer import Importer
from vis.controllers.analyzer import Analyzer
from vis.models.analyzing import ListOfPieces
from PyQt4.QtCore import Qt
from music21.note import Note
from music21.interval import Interval, IntervalException
from itertools import chain
import csv
import sys


def piece_to_records(piece, tenor):
    """
    Get AnalysisRecords for the voice pairs in a piece with its tenor voice identified.

    :param piece: path to a music21-importable file
    :param tenor: - index of the tenor voice in the file
    :returns: A list of AnalysisRecord objects, one for each voice pair containing the tenor
    """
    importer, analyzer = Importer(), Analyzer()
    importer.add_pieces([piece])
    pieces_list = importer.import_pieces(analyzer.get_pieces())
    index = pieces_list.createIndex(0, ListOfPieces.parts_list)
    parts = range(len(pieces_list.data(index, Qt.DisplayRole)))
    parts.remove(tenor)
    index = pieces_list.createIndex(0, ListOfPieces.parts_combinations)
    analyzer.set_data(index, [[ind, tenor] for ind in parts])
    return analyzer.run_analysis()


def bigramify(first_lower, first_upper, next_lower, next_upper):
    """
    Get the bigram from four notes

    :param first_lower: first note in the lower voice
    :type first_lower: str
    :param first_upper: first note in the upper voice
    :type first_upper: str
    :param next_lower: second note in the lower voice
    :type next_lower: str
    :param next_upper: second note in the upper voice
    :type next_upper: str
    :return: the bigram composed of these notes
    :rtype: tuple
    :raises: IntervalException
    """
    first_vert = Interval(Note(first_lower), Note(first_upper)).generic.directed
    next_vert = Interval(Note(next_lower), Note(next_upper)).generic.directed
    horiz = Interval(Note(first_lower), Note(next_lower)).generic.directed
    return first_vert, horiz, next_vert


def analyze(piece, tenor):
    """
    INPUTS:
    piece - path to a music21-importable file
    tenor - index of the tenor voice in the file

    OUTPUT:
    a list of tuples (interval,
                      2-gram,
                      # of times the 2-gram occurs,
                      # of times/# of 2-grams starting with interval,
                      # of times/# of 2-grams with the same first and last interval,
                      # of times/# of 2-grams starting with interval and same melodic interval,
                      # of times/# of 2-grams with the same last interval,
                      # of times/# of 2-grams with the same melodic and final interval,
                      # of times/# of 2-grams with the same melodic interval)
    sorted by interval, for all the 2-grams appearing in the piece
    """
    records = piece_to_records(piece, tenor)
    print 'records', records
    bigrams = []
    intervs = []
    for record in records:
        for first, second in zip(record, list(record)[1:]):
            try:
                bgram = bigramify(first[1][0], first[1][1], second[1][0], second[1][1])
                bigrams.append(bgram)
                intervs.append(bgram[0])
            except IntervalException:
                continue
    intervs = sorted(set(intervs))
    histogram = {bigram: len([bg for bg in bigrams if bg == bigram])
                 for bigram in set(bigrams)}
    print 'histogram', histogram
    return list(chain(*[get_subtable(histogram, interv) for interv in intervs]))


def get_subtable(histogram, interval):
    """
    INPUTS:
    histogram - a frequency histogram for bigrams in a fixed piece
    interval - an interval occurring in that piece

    OUTPUT:
    a list of tuples of the form described in analyze(), but only containing
    bigrams beginning with `interval`.
    """
    sub_hg = {bigram: freq for bigram, freq in histogram.iteritems()
              if bigram[0] == interval}
    rows = []
    for bigram in sub_hg.iterkeys():
        freq = float(sub_hg[bigram])
        # same_ij is the number of bigrams in the piece which have the same
        # intervals at positions i and j (where 0 is the first vertical interval,
        # 1 is the horizontal interval and 2 is the second vertical interval)
        same_0 = sum(sub_hg.values())
        same_02 = sum(v for bg, v in sub_hg.iteritems() if bg[2] == bigram[2])
        same_01 = sum(v for bg, v in sub_hg.iteritems() if bg[1] == bigram[1])
        same_2s = [(bg, v) for bg, v in histogram.iteritems() if bg[2] == bigram[2]]
        print 'same_2s', same_2s
        same_2 = sum(v for bg, v in same_2s)
        same_12 = sum(v for bg, v in same_2s if bg[1] == bigram[1])
        same_1 = sum(v for bg, v in histogram.iteritems() if bg[1] == bigram[1])
        rows.append((interval, bigram, int(freq), freq / same_0, freq / same_02, freq / same_01,
                     freq / same_2, freq / same_12, freq / same_1))
    return rows


def main(args):
    """
    INPUTS:
    args - a list of music21-importable file names and the index of the tenor
    voice in each

    OUTPUT:
    Creates a CSV file containing various statistics about 2-grams where one of
    the voices is the designated tenor.
    """
    args = args[1:]
    pairs = []
    for i, (arg, next_arg) in enumerate(zip(args, args[1:])):
        if i % 2 == 0:
            pairs.append((arg, int(next_arg)))
    table = list(chain(*(analyze(voice1, voice2) for voice1, voice2 in pairs)))
    with open('results.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Interval', 'Bigram', 'Freq of bigram', 'freq/same_0',
                         'freq/same_02', 'freq/same_01', 'freq/same_2', 'freq/same_12',
                         'freq/same_1'])
        for row in table:
            writer.writerow(row)
        csvfile.close()


if __name__ == "__main__":
    main(sys.argv)