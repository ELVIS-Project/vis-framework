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

from math import log
import csv
import sys

from controllers.importer import Importer
from controllers.analyzer import Analyzer
from models.analyzing import ListOfPieces
from elvis_repetition import A_e, A_o, stringify


def piece_to_records(piece):
    importer, analyzer = Importer(), Analyzer()
    importer.add_pieces([piece])
    importer.import_finished.connect(analyzer.catch_import)
    # noinspection PyArgumentList

# noinspection PyArgumentList,PyArgumentList,PyArgumentList
l = importer.import_pieces()
analyzer.set_data(l.createIndex(0, ListOfPieces.parts_combinations),
                  [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]])
return analyzer.run_analysis()

if __name__ == '__main__':
    pieces = sys.argv[1:]

    with open('results.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        for piece in pieces:
            importer, analyzer = Importer(), Analyzer()
            importer.add_pieces([piece])
            importer.import_finished.connect(analyzer.catch_import)
            print 'importing', piece, '...'
            l = importer.import_pieces()
            print 'import finished.'
            info = list(l.iterateRows())
            analyzer.set_data(l.createIndex(0, ListOfPieces.parts_combinations),
                              [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]])
            print 'analyzing...'
            writer.writerow([info[0][1][1]])
            writer.writerow(['A_o', 'A_e (estimated)', 'I_r'])
            strs = [stringify(r)[0] for r in analyzer.run_analysis()]
            print strs
            n, d = A_o(*strs), A_e(*strs)
            writer.writerow([n, d, log(n / d)])
            print 'analysis finished.'
        print 'results written to "results.csv"'