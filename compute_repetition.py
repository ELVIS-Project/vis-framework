#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: comput_repetition.py
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
Sample module for computing repetition, according to a method found in genomics.
"""
from vis.controllers.importer import Importer
from vis.controllers.analyzer import Analyzer
from vis.models.analyzing import ListOfPieces
from vis.elvis_repetition import a_expected, observed_a, stringify
from math import log
import csv
import sys


def piece_to_records(a_piece):
    """
    Get AnalysisRecords for the parts in a piece.
    :param a_piece: the path to a music file containing four voices
    :return: list of AnalysisRecords corresponding to the parts in the file
    """
    importer_, analyzer_ = Importer(), Analyzer()
    importer_.add_pieces([a_piece])
    pieces_list = importer_.import_pieces(analyzer_.get_pieces())
    analyzer_.set_data(pieces_list.createIndex(0, ListOfPieces.parts_combinations),
                       [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]])
    return analyzer_.run_analysis()


def main():
    """
    Compute repetition statistics for the pieces passed as command-line arguments,
    saving the results in the file `results.csv`.
    """
    pieces = sys.argv[1:]
    with open('results.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        for piece in pieces:
            importer, analyzer = Importer(), Analyzer()
            importer.add_pieces([piece])
            print 'importing', piece, '...'
            list_of_pieces = importer.import_pieces(analyzer.get_pieces())
            print 'import finished.'
            info = list(list_of_pieces.iterateRows())
            analyzer.set_data(list_of_pieces.createIndex(0, ListOfPieces.parts_combinations),
                              [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]])
            print 'analyzing...'
            writer.writerow([info[0][1][1]])
            writer.writerow(['A_o', 'A_e (estimated)', 'I_r'])
            strs = [stringify(r)[0] for r in analyzer.run_analysis()]
            print strs
            num, denom = observed_a(strs), a_expected(strs)
            writer.writerow([num, denom, log(num / denom)])
            print 'analysis finished.'
        print 'results written to "results.csv"'


if __name__ == '__main__':
    main()