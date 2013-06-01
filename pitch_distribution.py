#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: pitch_distribution.py
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

from music21 import converter, graph
from collections import defaultdict
import sys

def main(argv):
    this, path = argv
    score = converter.parseFile(path)
    l = [(n.pitch.unicodeName, n.duration.quarterLength/score.duration.quarterLength) for n in score.flat.notes]
    d = defaultdict(float)
    for p, length in l: d[p] += length
    g = graph.GraphHistogram()
    g.setData(enumerate(int(v*100) for v in d.values()))
    g.setTicks('x', [(i+0.45, k) for k in d.keys()])
    g.process()

if __name__ == "__main__":
    main(sys.argv)