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
"""
Draws a histogram of the pitches occurring in a music file.
"""
from music21 import converter, graph
from collections import defaultdict
import sys


def main(argv):
    """
    Draw a histogram of pitch frequencies
    :rtype : None
    :param argv: the command-line arguments. Should just be one file.
    """
    _, path = argv
    score = converter.parseFile(path)
    pitches_lengths = [
        (n.pitch.unicodeName, n.duration.quarterLength / score.duration.quarterLength) for n in
        score.flat.notes]
    freqs = defaultdict(float)
    for pitch, length in pitches_lengths:
        freqs[pitch] += length
    hist = graph.GraphHistogram()
    hist.setData(enumerate(int(v * 100) for v in freqs.values()))
    hist.setTicks('x', [(i + 0.45, k) for i, k in enumerate(freqs.keys())])
    hist.process()


if __name__ == "__main__":
    main(sys.argv)