#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         Test_Output_Formatting.py
# Purpose:      Unit tests for the get_formatted_ngrams() and
#               get_formatted_intervals() in the Vertical_Interval_Statistics
#               module.
#
# Copyright (C) 2012 Christopher Antila
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



import unittest
from Vertical_Interval_Statistics import Vertical_Interval_Statistics
from VIS_Settings import VIS_Settings
from music21 import converter
from analytic_engine import vis_these_parts



#------------------------------------------------------------------------------
class Test_Output_Formatting( unittest.TestCase ):
   def setUp( self ):
      self.vis = Vertical_Interval_Statistics()

   def test_basic_formatted_intervals( self ):
       ##TODO: test negative intervals
       ##TODO: test with quality
       ##TODO: test with simple
      expected_ascending_by_interval = '''All the Intervals:
------------------
8: 7
9: 3
10: 24
11: 3
12: 24
13: 14
14: 7
15: 9
16: 1
17: 5

'''
      expected_ascending_by_frequency = 'All the Intervals:\n------------------\n16: 1\n11: 3\n9: 3\n17: 5\n14: 7\n8: 7\n15: 9\n13: 14\n10: 24\n12: 24\n\n'
      expected_descending_by_frequency = '''All the Intervals:
------------------
10: 24
12: 24
13: 14
15: 9
14: 7
8: 7
17: 5
11: 3
9: 3
16: 1

'''
      expected_descending_by_interval = '''All the Intervals:
------------------
17: 5
16: 1
15: 9
14: 7
13: 14
12: 24
11: 3
10: 24
9: 3
8: 7

'''
      score = converter.parse( 'test_corpus/bwv77.mxl' )
      sets = VIS_Settings()
      vis_these_parts( [score.parts[0], score.parts[3]], sets, self.vis, 'test_corpus/bwv77.mxl' )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'ascending by interval' ), \
                        expected_ascending_by_interval )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'ascending by frequency' ), \
                        expected_ascending_by_frequency )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'descending by interval' ), \
                        expected_descending_by_interval )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'descending by frequency' ), \
                        expected_descending_by_frequency )

   def test_basic_formatted_ngrams( self ):
       ##TODO: test with voice crossing
       ##TODO: test with and without heedQuality
      ascending_by_frequency = '''All the 2-grams:
-----------------------------
8 -4 11: 1
12 +2 13: 1
8 -8 12: 1
15 1 8: 1
15 -4 18: 1
15 -4 17: 1
16 1 15: 1
17 +8 10: 1
4 1 5: 1
5 -2 6: 1
17 +4 15: 1
8 1 10: 1
15 -2 12: 1
17 +5 12: 1
11 +3 10: 1
13 -3 17: 1
7 1 8: 1
10 -4 12: 1
10 +4 7: 1
12 +4 10: 1
10 1 13: 1
14 +2 13: 1
10 -2 15: 1
10 -3 12: 1
10 +4 8: 1
12 1 8: 1
17 1 15: 1
11 -2 13: 1
5 1 6: 1
11 -2 12: 1
3 -2 5: 1
7 1 6: 1
8 -2 9: 1
8 -3 10: 1
15 +2 12: 1
6 1 7: 1
17 1 16: 1
5 -3 8: 1
15 +5 11: 1
15 +5 12: 1
8 +3 6: 1
12 -3 15: 1
17 +3 15: 2
11 +2 10: 2
17 +2 16: 2
17 +2 15: 2
10 +2 10: 2
6 -2 8: 2
15 -2 17: 2
9 1 8: 2
17 -2 18: 2
12 -4 15: 2
12 +3 10: 2
13 -2 17: 2
13 -2 13: 2
10 1 12: 2
14 +2 12: 2
10 -2 12: 2
16 +2 15: 2
13 +5 10: 2
15 +8 8: 2
12 -5 15: 2
12 1 10: 2
15 +2 13: 2
8 -2 10: 2
9 +2 8: 2
10 +2 9: 2
10 +2 8: 2
9 1 10: 2
15 +4 12: 3
12 +2 11: 3
15 1 17: 3
10 -2 13: 3
8 1 9: 3
12 -5 17: 3
11 1 12: 3
15 +2 14: 3
18 1 17: 3
17 +4 12: 4
12 -3 17: 4
10 1 9: 4
9 -2 10: 4
10 1 11: 4
17 -2 17: 5
10 -2 10: 5
12 1 13: 5
12 +2 10: 7
12 -2 13: 7
13 1 12: 7
10 -2 11: 7
12 1 11: 7
13 +2 12: 8
10 -5 15: 11
11 1 10: 15

'''
      descending_by_frequency = '''All the 2-grams:
-----------------------------
11 1 10: 15
10 -5 15: 11
13 +2 12: 8
12 +2 10: 7
12 -2 13: 7
13 1 12: 7
10 -2 11: 7
12 1 11: 7
17 -2 17: 5
10 -2 10: 5
12 1 13: 5
17 +4 12: 4
12 -3 17: 4
10 1 9: 4
9 -2 10: 4
10 1 11: 4
15 +4 12: 3
12 +2 11: 3
15 1 17: 3
10 -2 13: 3
8 1 9: 3
12 -5 17: 3
11 1 12: 3
15 +2 14: 3
18 1 17: 3
17 +3 15: 2
11 +2 10: 2
17 +2 16: 2
17 +2 15: 2
10 +2 10: 2
6 -2 8: 2
15 -2 17: 2
9 1 8: 2
17 -2 18: 2
12 -4 15: 2
12 +3 10: 2
13 -2 17: 2
13 -2 13: 2
10 1 12: 2
14 +2 12: 2
10 -2 12: 2
16 +2 15: 2
13 +5 10: 2
15 +8 8: 2
12 -5 15: 2
12 1 10: 2
15 +2 13: 2
8 -2 10: 2
9 +2 8: 2
10 +2 9: 2
10 +2 8: 2
9 1 10: 2
8 -4 11: 1
12 +2 13: 1
8 -8 12: 1
15 1 8: 1
15 -4 18: 1
15 -4 17: 1
16 1 15: 1
17 +8 10: 1
4 1 5: 1
5 -2 6: 1
17 +4 15: 1
8 1 10: 1
15 -2 12: 1
17 +5 12: 1
11 +3 10: 1
13 -3 17: 1
7 1 8: 1
10 -4 12: 1
10 +4 7: 1
12 +4 10: 1
10 1 13: 1
14 +2 13: 1
10 -2 15: 1
10 -3 12: 1
10 +4 8: 1
12 1 8: 1
17 1 15: 1
11 -2 13: 1
5 1 6: 1
11 -2 12: 1
3 -2 5: 1
7 1 6: 1
8 -2 9: 1
8 -3 10: 1
15 +2 12: 1
6 1 7: 1
17 1 16: 1
5 -3 8: 1
15 +5 11: 1
15 +5 12: 1
8 +3 6: 1
12 -3 15: 1

'''
      ascending_by_ngram = '''All the 2-grams:
-----------------------------
3 -2 5: 1
4 1 5: 1
5 1 6: 1
5 -2 6: 1
5 -3 8: 1
6 1 7: 1
6 -2 8: 2
7 1 6: 1
7 1 8: 1
8 1 9: 3
8 1 10: 1
8 -2 9: 1
8 -2 10: 2
8 +3 6: 1
8 -3 10: 1
8 -4 11: 1
8 -8 12: 1
9 1 8: 2
9 1 10: 2
9 +2 8: 2
9 -2 10: 4
10 1 9: 4
10 1 11: 4
10 1 12: 2
10 1 13: 1
10 +2 8: 2
10 +2 9: 2
10 +2 10: 2
10 -2 10: 5
10 -2 11: 7
10 -2 12: 2
10 -2 13: 3
10 -2 15: 1
10 -3 12: 1
10 +4 7: 1
10 +4 8: 1
10 -4 12: 1
10 -5 15: 11
11 1 10: 15
11 1 12: 3
11 +2 10: 2
11 -2 12: 1
11 -2 13: 1
11 +3 10: 1
12 1 8: 1
12 1 10: 2
12 1 11: 7
12 1 13: 5
12 +2 10: 7
12 +2 11: 3
12 +2 13: 1
12 -2 13: 7
12 +3 10: 2
12 -3 15: 1
12 -3 17: 4
12 +4 10: 1
12 -4 15: 2
12 -5 15: 2
12 -5 17: 3
13 1 12: 7
13 +2 12: 8
13 -2 13: 2
13 -2 17: 2
13 -3 17: 1
13 +5 10: 2
14 +2 12: 2
14 +2 13: 1
15 1 8: 1
15 1 17: 3
15 -2 12: 1
15 +2 12: 1
15 +2 13: 2
15 +2 14: 3
15 -2 17: 2
15 +4 12: 3
15 -4 17: 1
15 -4 18: 1
15 +5 11: 1
15 +5 12: 1
15 +8 8: 2
16 1 15: 1
16 +2 15: 2
17 1 15: 1
17 1 16: 1
17 +2 15: 2
17 +2 16: 2
17 -2 17: 5
17 -2 18: 2
17 +3 15: 2
17 +4 12: 4
17 +4 15: 1
17 +5 12: 1
17 +8 10: 1
18 1 17: 3

'''
      descending_by_ngram = '''All the 2-grams:
-----------------------------
18 1 17: 3
17 +8 10: 1
17 +5 12: 1
17 +4 15: 1
17 +4 12: 4
17 +3 15: 2
17 -2 18: 2
17 -2 17: 5
17 +2 16: 2
17 +2 15: 2
17 1 16: 1
17 1 15: 1
16 +2 15: 2
16 1 15: 1
15 +8 8: 2
15 +5 12: 1
15 +5 11: 1
15 -4 18: 1
15 -4 17: 1
15 +4 12: 3
15 -2 17: 2
15 +2 14: 3
15 +2 13: 2
15 -2 12: 1
15 +2 12: 1
15 1 17: 3
15 1 8: 1
14 +2 13: 1
14 +2 12: 2
13 +5 10: 2
13 -3 17: 1
13 -2 17: 2
13 -2 13: 2
13 +2 12: 8
13 1 12: 7
12 -5 17: 3
12 -5 15: 2
12 -4 15: 2
12 +4 10: 1
12 -3 17: 4
12 -3 15: 1
12 +3 10: 2
12 +2 13: 1
12 -2 13: 7
12 +2 11: 3
12 +2 10: 7
12 1 13: 5
12 1 11: 7
12 1 10: 2
12 1 8: 1
11 +3 10: 1
11 -2 13: 1
11 -2 12: 1
11 +2 10: 2
11 1 12: 3
11 1 10: 15
10 -5 15: 11
10 -4 12: 1
10 +4 8: 1
10 +4 7: 1
10 -3 12: 1
10 -2 15: 1
10 -2 13: 3
10 -2 12: 2
10 -2 11: 7
10 +2 10: 2
10 -2 10: 5
10 +2 9: 2
10 +2 8: 2
10 1 13: 1
10 1 12: 2
10 1 11: 4
10 1 9: 4
9 -2 10: 4
9 +2 8: 2
9 1 10: 2
9 1 8: 2
8 -8 12: 1
8 -4 11: 1
8 -3 10: 1
8 +3 6: 1
8 -2 10: 2
8 -2 9: 1
8 1 10: 1
8 1 9: 3
7 1 8: 1
7 1 6: 1
6 -2 8: 2
6 1 7: 1
5 -3 8: 1
5 -2 6: 1
5 1 6: 1
4 1 5: 1
3 -2 5: 1

'''
      score = converter.parse( 'test_corpus/Kyrie.krn' )
      sets = VIS_Settings()
      vis_these_parts( [score.parts[0], score.parts[-1]], sets, self.vis, 'test_corpus/Kyrie.krn' )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by ngram' ), \
                        ascending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by ngram' ), \
                        descending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by frequency' ), \
                        ascending_by_frequency )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by frequency' ), \
                        descending_by_frequency )

   def test_with_negative_intervals( self ):
      ascending_by_interval = '''All the Intervals:
------------------
1: 31
-2: 7
2: 17
3: 72
-3: 13
-4: 2
4: 78
-5: 6
5: 56
-6: 5
6: 107
7: 13
8: 29
9: 9
10: 15
11: 8
-12: 1
12: 1
13: 3

'''
      descending_by_interval = '''All the Intervals:
------------------
13: 3
-12: 1
12: 1
11: 8
10: 15
9: 9
8: 29
7: 13
-6: 5
6: 107
-5: 6
5: 56
-4: 2
4: 78
3: 72
-3: 13
-2: 7
2: 17
1: 31

'''
      ascending_by_frequency = 'All the Intervals:\n------------------\n-12: 1\n12: 1\n-4: 2\n13: 3\n-6: 5\n-5: 6\n-2: 7\n11: 8\n9: 9\n7: 13\n-3: 13\n10: 15\n2: 17\n8: 29\n1: 31\n5: 56\n3: 72\n4: 78\n6: 107\n\n'
      descending_by_frequency = 'All the Intervals:\n------------------\n6: 107\n4: 78\n3: 72\n5: 56\n1: 31\n8: 29\n2: 17\n10: 15\n7: 13\n-3: 13\n9: 9\n11: 8\n-2: 7\n-5: 6\n-6: 5\n13: 3\n-4: 2\n-12: 1\n12: 1\n\n'
      score = converter.parse( 'test_corpus/sinfony.md' )
      sets = VIS_Settings()
      vis_these_parts( [score.parts[0], score.parts[1]], sets, self.vis, 'test_corpus/sinfony.md' )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'ascending by interval' ), \
                        ascending_by_interval )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'descending by interval' ), \
                        descending_by_interval )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'ascending by frequency' ), \
                        ascending_by_frequency )
      self.assertEqual( self.vis.get_formatted_intervals( sets, 'descending by frequency' ), \
                        descending_by_frequency )

   def test_with_negative_ngrams( self ):
      ascending_by_ngram = '''All the 2-grams:
-----------------------------
1 1 2: 3
1 1 -2: 2
1 1 3: 1
1 1 4: 6
1 1 5: 2
1 1 6: 1
1 1 8: 1
1 +2 -2: 3
1 -2 2: 2
1 +2 -3: 1
1 -2 3: 1
1 -2 6: 1
1 +3 3: 1
1 -3 6: 1
1 -3 10: 1
1 -5 4: 1
1 -5 5: 1
2 1 1: 5
2 1 3: 4
-2 1 -3: 1
2 1 5: 2
-2 -2 1: 2
2 +2 1: 2
-2 +2 -3: 1
2 -2 3: 1
2 -2 6: 2
2 -2 8: 1
-2 +3 -5: 1
-2 -5 4: 1
3 1 1: 2
3 1 2: 6
-3 1 3: 1
-3 1 4: 1
3 1 4: 20
3 1 5: 2
3 1 -6: 1
3 1 6: 5
3 1 8: 1
3 +2 1: 1
-3 -2 -2: 2
3 +2 3: 3
3 -2 3: 4
-3 +2 -4: 2
3 -2 4: 6
-3 +2 -5: 1
-3 -2 5: 1
-3 -3 -3: 2
-3 -3 3: 1
3 -3 3: 1
3 -3 4: 2
3 -3 5: 4
3 -3 6: 3
3 -4 5: 1
-3 +4 -6: 1
3 -4 6: 1
3 +5 -5: 1
3 -5 5: 1
3 -5 6: 1
3 -6 5: 1
-3 -6 5: 1
3 -6 6: 1
3 -7 4: 1
3 -7 8: 1
3 +10 -12: 1
4 1 1: 3
4 1 2: 2
4 1 3: 11
4 1 5: 5
4 1 -5: 1
4 1 6: 1
4 1 9: 1
4 +2 1: 2
4 +2 3: 7
4 -2 3: 6
4 +2 4: 2
4 -2 4: 5
-4 +2 -5: 1
4 -2 5: 5
4 +2 6: 1
4 -2 6: 3
4 -2 8: 1
4 -3 3: 1
-4 -3 -3: 1
4 -3 5: 2
4 -3 6: 3
4 +4 6: 1
4 -4 6: 1
4 -5 5: 1
4 -5 6: 4
4 -5 7: 1
4 +6 6: 1
4 +7 3: 1
4 -8 6: 1
4 -8 10: 1
4 -8 11: 1
5 1 1: 1
5 1 3: 2
5 1 4: 6
5 1 6: 18
-5 1 -6: 2
5 1 8: 4
5 +2 3: 1
5 +2 4: 2
5 -2 5: 3
-5 -2 5: 1
5 -2 6: 4
-5 +2 -6: 1
-5 -3 -3: 1
5 +3 3: 1
5 +3 4: 1
5 -3 6: 5
5 -3 7: 1
5 +4 1: 1
5 -4 6: 1
5 -4 7: 1
5 -5 5: 1
5 -8 10: 1
6 1 -3: 1
6 1 3: 2
6 1 4: 2
6 1 5: 11
6 1 7: 1
6 1 8: 2
6 1 9: 2
6 1 11: 1
6 +2 1: 4
6 +2 3: 4
-6 -2 3: 1
6 -2 4: 1
6 +2 4: 1
-6 -2 -5: 1
6 +2 5: 6
6 -2 6: 10
6 +2 6: 14
6 -2 7: 5
6 -2 8: 2
6 +3 1: 1
6 -3 1: 1
-6 -3 -3: 1
6 +3 3: 2
6 +3 4: 1
6 -3 6: 3
6 -3 8: 1
6 -3 10: 1
6 +4 2: 2
6 +4 3: 4
6 +4 4: 7
6 +5 6: 1
-6 -5 6: 1
6 -5 8: 1
6 -5 11: 1
6 +6 3: 2
6 +6 4: 2
6 -6 8: 1
6 -8 6: 1
7 1 6: 2
7 1 8: 4
7 +2 6: 1
7 -2 8: 4
7 +4 4: 1
7 -5 10: 1
8 1 4: 1
8 1 6: 2
8 1 7: 2
8 1 11: 1
8 +2 5: 1
8 +2 7: 2
8 -2 9: 2
8 -2 10: 2
8 +3 3: 1
8 +3 5: 1
8 -4 4: 1
8 +4 4: 1
8 +4 6: 1
8 +5 3: 2
8 +5 -3: 1
8 +5 4: 2
8 +6 3: 2
8 +6 6: 2
9 1 8: 3
9 -2 10: 2
9 -3 10: 1
9 +4 5: 2
9 +5 6: 1
10 1 6: 2
10 1 9: 3
10 1 11: 4
10 +3 6: 1
10 -3 13: 1
10 +5 6: 1
11 +2 10: 1
11 -2 12: 1
11 +4 8: 1
11 +7 3: 2
11 +8 3: 1
12 -2 13: 1
13 +2 8: 1
13 +3 13: 1

'''
      descending_by_ngram = '''All the 2-grams:
-----------------------------
13 +3 13: 1
13 +2 8: 1
12 -2 13: 1
11 +8 3: 1
11 +7 3: 2
11 +4 8: 1
11 -2 12: 1
11 +2 10: 1
10 +5 6: 1
10 -3 13: 1
10 +3 6: 1
10 1 11: 4
10 1 9: 3
10 1 6: 2
9 +5 6: 1
9 +4 5: 2
9 -3 10: 1
9 -2 10: 2
9 1 8: 3
8 +6 6: 2
8 +6 3: 2
8 +5 4: 2
8 +5 3: 2
8 +5 -3: 1
8 +4 6: 1
8 -4 4: 1
8 +4 4: 1
8 +3 5: 1
8 +3 3: 1
8 -2 10: 2
8 -2 9: 2
8 +2 7: 2
8 +2 5: 1
8 1 11: 1
8 1 7: 2
8 1 6: 2
8 1 4: 1
7 -5 10: 1
7 +4 4: 1
7 -2 8: 4
7 +2 6: 1
7 1 8: 4
7 1 6: 2
6 -8 6: 1
6 -6 8: 1
6 +6 4: 2
6 +6 3: 2
6 -5 11: 1
6 -5 8: 1
6 +5 6: 1
-6 -5 6: 1
6 +4 4: 7
6 +4 3: 4
6 +4 2: 2
6 -3 10: 1
6 -3 8: 1
6 -3 6: 3
6 +3 4: 1
-6 -3 -3: 1
6 +3 3: 2
6 +3 1: 1
6 -3 1: 1
6 -2 8: 2
6 -2 7: 5
6 -2 6: 10
6 +2 6: 14
-6 -2 -5: 1
6 +2 5: 6
6 -2 4: 1
6 +2 4: 1
6 +2 3: 4
-6 -2 3: 1
6 +2 1: 4
6 1 11: 1
6 1 9: 2
6 1 8: 2
6 1 7: 1
6 1 5: 11
6 1 4: 2
6 1 -3: 1
6 1 3: 2
5 -8 10: 1
5 -5 5: 1
5 -4 7: 1
5 -4 6: 1
5 +4 1: 1
5 -3 7: 1
5 -3 6: 5
5 +3 4: 1
-5 -3 -3: 1
5 +3 3: 1
5 -2 6: 4
-5 +2 -6: 1
5 -2 5: 3
-5 -2 5: 1
5 +2 4: 2
5 +2 3: 1
5 1 8: 4
5 1 6: 18
-5 1 -6: 2
5 1 4: 6
5 1 3: 2
5 1 1: 1
4 -8 11: 1
4 -8 10: 1
4 -8 6: 1
4 +7 3: 1
4 +6 6: 1
4 -5 7: 1
4 -5 6: 4
4 -5 5: 1
4 +4 6: 1
4 -4 6: 1
4 -3 6: 3
4 -3 5: 2
4 -3 3: 1
-4 -3 -3: 1
4 -2 8: 1
4 +2 6: 1
4 -2 6: 3
-4 +2 -5: 1
4 -2 5: 5
4 +2 4: 2
4 -2 4: 5
4 +2 3: 7
4 -2 3: 6
4 +2 1: 2
4 1 9: 1
4 1 6: 1
4 1 5: 5
4 1 -5: 1
4 1 3: 11
4 1 2: 2
4 1 1: 3
3 +10 -12: 1
3 -7 8: 1
3 -7 4: 1
3 -6 6: 1
3 -6 5: 1
-3 -6 5: 1
3 -5 6: 1
3 +5 -5: 1
3 -5 5: 1
-3 +4 -6: 1
3 -4 6: 1
3 -4 5: 1
3 -3 6: 3
3 -3 5: 4
3 -3 4: 2
-3 -3 -3: 2
-3 -3 3: 1
3 -3 3: 1
-3 +2 -5: 1
-3 -2 5: 1
-3 +2 -4: 2
3 -2 4: 6
3 +2 3: 3
3 -2 3: 4
-3 -2 -2: 2
3 +2 1: 1
3 1 8: 1
3 1 -6: 1
3 1 6: 5
3 1 5: 2
-3 1 4: 1
3 1 4: 20
-3 1 3: 1
3 1 2: 6
3 1 1: 2
-2 -5 4: 1
-2 +3 -5: 1
2 -2 8: 1
2 -2 6: 2
-2 +2 -3: 1
2 -2 3: 1
-2 -2 1: 2
2 +2 1: 2
2 1 5: 2
2 1 3: 4
-2 1 -3: 1
2 1 1: 5
1 -5 5: 1
1 -5 4: 1
1 -3 10: 1
1 -3 6: 1
1 +3 3: 1
1 -2 6: 1
1 +2 -3: 1
1 -2 3: 1
1 +2 -2: 3
1 -2 2: 2
1 1 8: 1
1 1 6: 1
1 1 5: 2
1 1 4: 6
1 1 3: 1
1 1 2: 3
1 1 -2: 2

'''
      ascending_by_frequency = '''All the 2-grams:
-----------------------------
3 -6 5: 1
8 +2 5: 1
3 +2 1: 1
7 -5 10: 1
8 1 4: 1
12 -2 13: 1
-3 +4 -6: 1
4 -3 3: 1
4 +7 3: 1
4 1 9: 1
-5 -3 -3: 1
1 1 8: 1
4 1 6: 1
6 +3 1: 1
3 -4 5: 1
3 -4 6: 1
4 +2 6: 1
9 +5 6: 1
8 1 11: 1
1 +3 3: 1
6 -2 4: 1
10 +5 6: 1
5 +3 4: 1
5 +3 3: 1
-3 1 3: 1
-3 1 4: 1
-3 +2 -5: 1
-6 -3 -3: 1
8 -4 4: 1
3 1 -6: 1
4 +4 6: 1
1 +2 -3: 1
-3 -6 5: 1
6 -5 11: 1
6 -5 8: 1
11 +8 3: 1
-2 +2 -3: 1
6 -8 6: 1
3 -7 8: 1
6 -3 1: 1
6 +2 4: 1
6 -3 8: 1
5 +2 3: 1
4 -4 6: 1
-3 -3 3: 1
11 +2 10: 1
-2 -5 4: 1
3 -3 3: 1
8 +4 6: 1
8 +4 4: 1
-5 +2 -6: 1
5 -3 7: 1
13 +3 13: 1
6 -3 10: 1
1 -3 10: 1
4 -8 6: 1
7 +2 6: 1
-2 +3 -5: 1
1 -5 5: 1
10 -3 13: 1
1 -3 6: 1
5 1 1: 1
3 -7 4: 1
5 -8 10: 1
5 -5 5: 1
-6 -2 -5: 1
-5 -2 5: 1
1 -2 3: 1
1 -2 6: 1
6 1 11: 1
11 -2 12: 1
6 +5 6: 1
6 1 -3: 1
3 -6 6: 1
-4 -3 -3: 1
-6 -5 6: 1
6 +3 4: 1
1 1 6: 1
10 +3 6: 1
3 +5 -5: 1
5 +4 1: 1
3 1 8: 1
4 -5 5: 1
4 -5 7: 1
2 -2 3: 1
11 +4 8: 1
2 -2 8: 1
-4 +2 -5: 1
4 -2 8: 1
-3 -2 5: 1
5 -4 6: 1
5 -4 7: 1
6 1 7: 1
3 +10 -12: 1
7 +4 4: 1
3 -5 5: 1
3 -5 6: 1
13 +2 8: 1
-2 1 -3: 1
8 +5 -3: 1
1 1 3: 1
4 -8 10: 1
8 +3 5: 1
9 -3 10: 1
-6 -2 3: 1
8 +3 3: 1
6 -6 8: 1
4 +6 6: 1
4 -8 11: 1
1 -5 4: 1
4 1 -5: 1
8 +2 7: 2
8 1 6: 2
8 1 7: 2
-3 -3 -3: 2
9 +4 5: 2
4 -3 5: 2
1 1 5: 2
4 1 2: 2
6 -2 8: 2
8 +6 3: 2
8 +6 6: 2
-3 +2 -4: 2
-2 -2 1: 2
4 +2 1: 2
4 +2 4: 2
6 +4 2: 2
5 +2 4: 2
2 +2 1: 2
7 1 6: 2
3 -3 4: 2
11 +7 3: 2
2 -2 6: 2
5 1 3: 2
1 -2 2: 2
3 1 5: 2
9 -2 10: 2
6 +3 3: 2
8 -2 9: 2
8 +5 3: 2
1 1 -2: 2
8 +5 4: 2
3 1 1: 2
6 1 8: 2
6 1 9: 2
6 1 3: 2
8 -2 10: 2
6 1 4: 2
-5 1 -6: 2
-3 -2 -2: 2
2 1 5: 2
6 +6 4: 2
6 +6 3: 2
10 1 6: 2
3 +2 3: 3
4 -3 6: 3
4 1 1: 3
1 1 2: 3
5 -2 5: 3
9 1 8: 3
10 1 9: 3
1 +2 -2: 3
6 -3 6: 3
3 -3 6: 3
4 -2 6: 3
5 -2 6: 4
7 -2 8: 4
6 +4 3: 4
10 1 11: 4
3 -3 5: 4
2 1 3: 4
6 +2 1: 4
5 1 8: 4
7 1 8: 4
3 -2 3: 4
4 -5 6: 4
6 +2 3: 4
4 1 5: 5
6 -2 7: 5
2 1 1: 5
3 1 6: 5
4 -2 5: 5
4 -2 4: 5
5 -3 6: 5
5 1 4: 6
3 -2 4: 6
4 -2 3: 6
3 1 2: 6
1 1 4: 6
6 +2 5: 6
4 +2 3: 7
6 +4 4: 7
6 -2 6: 10
4 1 3: 11
6 1 5: 11
6 +2 6: 14
5 1 6: 18
3 1 4: 20

'''
      descending_by_frequency = '''All the 2-grams:
-----------------------------
3 1 4: 20
5 1 6: 18
6 +2 6: 14
4 1 3: 11
6 1 5: 11
6 -2 6: 10
4 +2 3: 7
6 +4 4: 7
5 1 4: 6
3 -2 4: 6
4 -2 3: 6
3 1 2: 6
1 1 4: 6
6 +2 5: 6
4 1 5: 5
6 -2 7: 5
2 1 1: 5
3 1 6: 5
4 -2 5: 5
4 -2 4: 5
5 -3 6: 5
5 -2 6: 4
7 -2 8: 4
6 +4 3: 4
10 1 11: 4
3 -3 5: 4
2 1 3: 4
6 +2 1: 4
5 1 8: 4
7 1 8: 4
3 -2 3: 4
4 -5 6: 4
6 +2 3: 4
3 +2 3: 3
4 -3 6: 3
4 1 1: 3
1 1 2: 3
5 -2 5: 3
9 1 8: 3
10 1 9: 3
1 +2 -2: 3
6 -3 6: 3
3 -3 6: 3
4 -2 6: 3
8 +2 7: 2
8 1 6: 2
8 1 7: 2
-3 -3 -3: 2
9 +4 5: 2
4 -3 5: 2
1 1 5: 2
4 1 2: 2
6 -2 8: 2
8 +6 3: 2
8 +6 6: 2
-3 +2 -4: 2
-2 -2 1: 2
4 +2 1: 2
4 +2 4: 2
6 +4 2: 2
5 +2 4: 2
2 +2 1: 2
7 1 6: 2
3 -3 4: 2
11 +7 3: 2
2 -2 6: 2
5 1 3: 2
1 -2 2: 2
3 1 5: 2
9 -2 10: 2
6 +3 3: 2
8 -2 9: 2
8 +5 3: 2
1 1 -2: 2
8 +5 4: 2
3 1 1: 2
6 1 8: 2
6 1 9: 2
6 1 3: 2
8 -2 10: 2
6 1 4: 2
-5 1 -6: 2
-3 -2 -2: 2
2 1 5: 2
6 +6 4: 2
6 +6 3: 2
10 1 6: 2
3 -6 5: 1
8 +2 5: 1
3 +2 1: 1
7 -5 10: 1
8 1 4: 1
12 -2 13: 1
-3 +4 -6: 1
4 -3 3: 1
4 +7 3: 1
4 1 9: 1
-5 -3 -3: 1
1 1 8: 1
4 1 6: 1
6 +3 1: 1
3 -4 5: 1
3 -4 6: 1
4 +2 6: 1
9 +5 6: 1
8 1 11: 1
1 +3 3: 1
6 -2 4: 1
10 +5 6: 1
5 +3 4: 1
5 +3 3: 1
-3 1 3: 1
-3 1 4: 1
-3 +2 -5: 1
-6 -3 -3: 1
8 -4 4: 1
3 1 -6: 1
4 +4 6: 1
1 +2 -3: 1
-3 -6 5: 1
6 -5 11: 1
6 -5 8: 1
11 +8 3: 1
-2 +2 -3: 1
6 -8 6: 1
3 -7 8: 1
6 -3 1: 1
6 +2 4: 1
6 -3 8: 1
5 +2 3: 1
4 -4 6: 1
-3 -3 3: 1
11 +2 10: 1
-2 -5 4: 1
3 -3 3: 1
8 +4 6: 1
8 +4 4: 1
-5 +2 -6: 1
5 -3 7: 1
13 +3 13: 1
6 -3 10: 1
1 -3 10: 1
4 -8 6: 1
7 +2 6: 1
-2 +3 -5: 1
1 -5 5: 1
10 -3 13: 1
1 -3 6: 1
5 1 1: 1
3 -7 4: 1
5 -8 10: 1
5 -5 5: 1
-6 -2 -5: 1
-5 -2 5: 1
1 -2 3: 1
1 -2 6: 1
6 1 11: 1
11 -2 12: 1
6 +5 6: 1
6 1 -3: 1
3 -6 6: 1
-4 -3 -3: 1
-6 -5 6: 1
6 +3 4: 1
1 1 6: 1
10 +3 6: 1
3 +5 -5: 1
5 +4 1: 1
3 1 8: 1
4 -5 5: 1
4 -5 7: 1
2 -2 3: 1
11 +4 8: 1
2 -2 8: 1
-4 +2 -5: 1
4 -2 8: 1
-3 -2 5: 1
5 -4 6: 1
5 -4 7: 1
6 1 7: 1
3 +10 -12: 1
7 +4 4: 1
3 -5 5: 1
3 -5 6: 1
13 +2 8: 1
-2 1 -3: 1
8 +5 -3: 1
1 1 3: 1
4 -8 10: 1
8 +3 5: 1
9 -3 10: 1
-6 -2 3: 1
8 +3 3: 1
6 -6 8: 1
4 +6 6: 1
4 -8 11: 1
1 -5 4: 1
4 1 -5: 1

'''
      score = converter.parse( 'test_corpus/sinfony.md' )
      sets = VIS_Settings()
      vis_these_parts( [score.parts[0], score.parts[1]], sets, self.vis, 'test_corpus/sinfony.md' )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by ngram' ), \
                        ascending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by ngram' ), \
                        descending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by frequency' ), \
                        ascending_by_frequency )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by frequency' ), \
                        descending_by_frequency )

   def test_2_and_3_grams( self ):
      ascending_by_ngram = '''All the 2-grams:
-----------------------------
3 1 6: 1
4 1 3: 1
5 +2 4: 1
5 -3 6: 1
6 1 5: 2
6 -2 8: 1
6 -3 8: 1
7 1 6: 1
8 1 5: 1
8 1 10: 1
8 +2 7: 1
8 -2 9: 4
8 -2 10: 1
8 -3 10: 1
9 1 8: 1
9 -2 10: 3
9 +2 10: 1
9 +3 6: 1
10 1 8: 1
10 1 9: 2
10 1 12: 3
10 +2 8: 1
10 +2 9: 1
10 +2 10: 4
10 -2 10: 10
10 -2 11: 4
10 -2 15: 2
10 -3 10: 3
10 -3 11: 1
10 -3 12: 2
10 -4 12: 1
10 -5 15: 3
10 +8 10: 1
11 1 10: 5
11 +2 10: 1
11 -2 12: 1
11 -2 15: 1
12 1 8: 1
12 1 11: 2
12 +2 10: 2
12 -2 13: 3
12 +3 10: 2
12 +5 8: 1
12 +5 10: 1
13 1 12: 1
13 -2 14: 3
14 +2 12: 1
14 -2 15: 2
14 -2 17: 1
15 1 14: 1
15 +2 13: 1
15 +4 12: 1
15 +5 11: 1
15 +8 8: 2
16 1 15: 1
17 -2 17: 1

All the 3-grams:
-----------------------------
3 1 6 -3 8: 1
4 1 3 1 6: 1
5 +2 4 1 3: 1
5 -3 6 1 5: 1
6 1 5 +2 4: 1
6 1 5 -3 6: 1
6 -2 8 1 5: 1
6 -3 8 +2 7: 1
7 1 6 -2 8: 1
8 1 10 -2 10: 1
8 +2 7 1 6: 1
8 -2 9 -2 10: 3
8 -2 10 -5 15: 1
8 -3 10 -2 11: 1
9 1 8 -2 10: 1
9 -2 10 -2 11: 2
9 -2 10 -2 15: 1
9 +2 10 -3 11: 1
9 +3 6 1 5: 1
10 1 8 1 10: 1
10 1 9 1 8: 1
10 1 9 +3 6: 1
10 1 12 -2 13: 2
10 +2 8 -3 10: 1
10 +2 9 +2 10: 1
10 +2 10 -2 10: 1
10 -2 10 -2 10: 5
10 +2 10 -3 10: 1
10 -2 10 -3 10: 2
10 -2 10 -3 12: 1
10 +2 10 -4 12: 1
10 -2 10 +8 10: 1
10 -2 11 1 10: 2
10 -2 11 -2 12: 1
10 -2 11 -2 15: 1
10 -3 10 +2 10: 2
10 -3 10 -2 10: 1
10 -3 11 +2 10: 1
10 -3 12 +3 10: 1
10 -3 12 +5 10: 1
10 -5 15 +8 8: 2
10 +8 10 1 8: 1
11 1 10 +2 8: 1
11 1 10 +2 10: 1
11 1 10 -5 15: 1
11 +2 10 -2 11: 1
11 -2 12 1 8: 1
11 -2 15 +4 12: 1
12 1 8 -2 9: 1
12 1 11 1 10: 2
12 +2 10 1 12: 1
12 +2 10 +2 9: 1
12 -2 13 -2 14: 3
12 +3 10 1 9: 1
12 +3 10 -2 10: 1
12 +5 10 -5 15: 1
13 1 12 +2 10: 1
13 -2 14 -2 15: 2
13 -2 14 -2 17: 1
14 +2 12 +2 10: 1
14 -2 15 1 14: 1
14 -2 15 +2 13: 1
14 -2 17 -2 17: 1
15 1 14 +2 12: 1
15 +2 13 1 12: 1
15 +4 12 1 11: 1
15 +5 11 1 10: 1
15 +8 8 -2 9: 1
16 1 15 +5 11: 1

'''
      descending_by_frequency = '''All the 2-grams:
-----------------------------
10 -2 10: 10
11 1 10: 5
8 -2 9: 4
10 +2 10: 4
10 -2 11: 4
10 -3 10: 3
9 -2 10: 3
13 -2 14: 3
12 -2 13: 3
10 -5 15: 3
10 1 12: 3
12 1 11: 2
12 +2 10: 2
10 -3 12: 2
10 1 9: 2
12 +3 10: 2
15 +8 8: 2
14 -2 15: 2
6 1 5: 2
10 -2 15: 2
15 +4 12: 1
8 +2 7: 1
12 +5 10: 1
10 -4 12: 1
17 -2 17: 1
8 1 5: 1
10 1 8: 1
12 1 8: 1
11 +2 10: 1
15 +2 13: 1
14 -2 17: 1
12 +5 8: 1
16 1 15: 1
11 -2 12: 1
15 1 14: 1
4 1 3: 1
11 -2 15: 1
8 -3 10: 1
9 +3 6: 1
10 -3 11: 1
5 -3 6: 1
13 1 12: 1
9 1 8: 1
15 +5 11: 1
10 +8 10: 1
6 -2 8: 1
8 1 10: 1
6 -3 8: 1
9 +2 10: 1
8 -2 10: 1
5 +2 4: 1
10 +2 9: 1
10 +2 8: 1
14 +2 12: 1
3 1 6: 1
7 1 6: 1

All the 3-grams:
-----------------------------
10 -2 10 -2 10: 5
8 -2 9 -2 10: 3
12 -2 13 -2 14: 3
10 -2 11 1 10: 2
10 -2 10 -3 10: 2
10 -3 10 +2 10: 2
12 1 11 1 10: 2
9 -2 10 -2 11: 2
10 1 12 -2 13: 2
10 -5 15 +8 8: 2
13 -2 14 -2 15: 2
11 1 10 +2 8: 1
15 1 14 +2 12: 1
10 +2 10 -3 10: 1
9 +3 6 1 5: 1
9 +2 10 -3 11: 1
6 1 5 -3 6: 1
14 +2 12 +2 10: 1
14 -2 17 -2 17: 1
12 +2 10 +2 9: 1
12 +3 10 -2 10: 1
14 -2 15 1 14: 1
8 +2 7 1 6: 1
10 -2 10 -3 12: 1
6 -2 8 1 5: 1
15 +5 11 1 10: 1
5 -3 6 1 5: 1
10 +2 10 -4 12: 1
8 -3 10 -2 11: 1
10 1 9 +3 6: 1
9 1 8 -2 10: 1
4 1 3 1 6: 1
15 +8 8 -2 9: 1
11 1 10 -5 15: 1
9 -2 10 -2 15: 1
15 +2 13 1 12: 1
10 +2 8 -3 10: 1
10 -3 11 +2 10: 1
13 1 12 +2 10: 1
10 -3 10 -2 10: 1
10 -2 10 +8 10: 1
10 1 8 1 10: 1
7 1 6 -2 8: 1
12 +2 10 1 12: 1
8 -2 10 -5 15: 1
6 -3 8 +2 7: 1
12 +3 10 1 9: 1
3 1 6 -3 8: 1
14 -2 15 +2 13: 1
6 1 5 +2 4: 1
12 +5 10 -5 15: 1
10 +2 10 -2 10: 1
11 +2 10 -2 11: 1
15 +4 12 1 11: 1
10 -3 12 +5 10: 1
5 +2 4 1 3: 1
10 +8 10 1 8: 1
16 1 15 +5 11: 1
8 1 10 -2 10: 1
11 1 10 +2 10: 1
11 -2 15 +4 12: 1
12 1 8 -2 9: 1
10 -2 11 -2 12: 1
10 1 9 1 8: 1
13 -2 14 -2 17: 1
10 -2 11 -2 15: 1
10 +2 9 +2 10: 1
11 -2 12 1 8: 1
10 -3 12 +3 10: 1

'''
      score = converter.parse( 'test_corpus/Jos2308.krn' )
      sets = VIS_Settings()
      sets.set_property( 'lookForTheseNs 2,3' )
      vis_these_parts( [score.parts[0][:100], score.parts[-1][:100]], sets, self.vis, 'test_corpus/Jos2308.krn' )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by ngram' ), \
                        ascending_by_ngram )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'descending by frequency' ), \
                        descending_by_frequency )

   def test_only_4_grams_with_negatives( self ):
      ascending_by_frequency = '''All the 4-grams:
-----------------------------
3 -2 3 -3 5 +2 4: 1
5 -3 8 +2 7 +2 -3: 1
3 +3 1 1 -2 1 -3: 1
5 1 6 +3 3 -2 4: 1
4 +2 2 1 3 1 4: 1
3 +2 3 +2 3 +2 3: 1
3 -3 5 +2 4 1 3: 1
-2 1 -3 1 -4 1 -5: 1
8 +3 6 1 5 1 6: 1
8 +3 6 1 5 1 4: 1
8 +3 6 1 5 1 3: 1
4 1 3 +2 3 1 4: 1
6 -2 6 -2 6 +2 6: 1
2 1 3 1 4 -2 5: 1
6 +5 3 -5 8 +2 7: 1
-5 -2 -4 -2 3 -2 4: 1
6 1 5 1 4 1 3: 1
4 -2 3 +4 3 -2 3: 1
5 1 4 1 3 1 5: 1
6 1 5 +3 1 1 2: 1
6 1 5 +3 1 1 3: 1
4 -2 6 1 7 1 8: 1
6 +2 4 1 3 -3 6: 1
7 +2 6 1 5 +2 3: 1
-3 1 -2 -5 5 +2 4: 1
3 -2 3 1 2 1 1: 1
6 -2 7 -2 8 1 7: 1
7 +2 6 +2 4 1 3: 1
3 1 2 -2 3 +2 1: 1
8 +3 6 -3 8 +2 6: 1
3 +4 3 1 2 1 1: 1
3 +3 1 1 3 +3 1: 1
-2 -2 1 1 2 1 3: 1
6 +2 5 1 4 -3 6: 1
6 -2 7 +2 6 +2 5: 1
5 +2 3 -2 3 1 1: 1
5 -3 8 +2 7 1 6: 1
2 -2 3 +2 6 +4 3: 1
6 +3 3 -2 4 -2 5: 1
3 1 -3 -2 -2 -2 5: 1
-3 +2 -3 1 -2 -5 5: 1
2 -2 3 1 -3 -2 -2: 1
4 1 3 -2 3 -3 5: 1
2 +3 1 1 2 1 3: 1
6 -3 8 +2 6 -3 8: 1
7 +2 6 -3 8 +2 6: 1
2 1 3 1 4 1 5: 1
6 1 7 1 8 +2 7: 1
6 -2 7 1 6 -2 8: 1
3 1 4 1 5 -3 7: 1
8 1 7 +2 5 -4 8: 1
3 -2 6 -2 8 +3 6: 1
4 1 3 1 4 1 8: 1
6 1 5 +2 3 -2 3: 1
3 1 1 -2 3 -2 3: 1
2 -2 -3 -2 -2 -2 1: 1
8 +2 5 1 6 -3 8: 1
3 +2 3 -2 3 1 2: 1
5 1 6 +5 3 -5 8: 1
3 +4 3 -2 3 +4 3: 1
6 -3 8 +2 5 1 6: 1
-2 -2 1 -2 2 -2 6: 1
4 +2 1 1 2 -2 3: 1
1 -5 5 1 6 +5 3: 1
8 +2 7 +2 6 -3 8: 1
5 +2 4 1 3 +8 -5: 1
4 +2 3 +2 3 -2 4: 1
6 -3 8 +2 6 -2 8: 1
1 -3 3 -2 6 -2 8: 1
4 -2 5 +2 3 -3 5: 1
7 +2 6 +2 5 +2 3: 1
1 1 2 1 3 1 4: 1
-3 1 3 -2 5 1 3: 1
4 +2 3 +2 3 +2 3: 1
1 1 8 -3 10 +3 6: 1
3 +2 3 -2 4 +2 3: 1
5 -2 6 -2 7 +2 6: 1
-4 1 -3 -2 -2 -2 1: 1
5 1 3 -2 5 -2 6: 1
4 1 3 1 5 -2 6: 1
6 +2 5 1 4 1 3: 1
-2 -2 1 +3 -4 -2 -3: 1
6 -2 7 +2 6 +2 4: 1
8 +3 5 1 4 1 3: 1
-3 +2 -3 +2 -3 1 -2: 1
2 -2 6 +2 5 1 4: 1
7 1 8 +2 7 1 6: 1
6 1 5 1 6 +3 3: 1
6 -3 8 +2 7 1 6: 1
1 1 3 +3 1 1 -2: 1
3 1 2 1 1 1 -2: 1
5 +2 4 +2 1 1 2: 1
4 1 5 -3 6 +2 5: 1
-5 -5 1 +3 3 1 -3: 1
8 +2 7 1 6 -3 8: 1
4 1 8 1 7 1 6: 1
7 1 6 -2 8 +2 7: 1
2 1 1 1 -2 1 -3: 1
6 -2 8 +2 6 +2 4: 1
8 +2 7 +2 5 +2 4: 1
2 1 3 -2 5 -2 6: 1
-3 +2 -3 1 -6 -3 -3: 1
2 +2 3 -5 8 +3 -3: 1
5 1 1 -5 5 1 6: 1
1 +3 3 1 -3 -2 -2: 1
5 1 4 -3 6 -2 7: 1
6 -2 7 +2 4 +2 3: 1
-4 -2 3 -3 5 +2 4: 1
5 +5 1 -2 2 -2 -3: 1
3 1 -3 -2 -2 -2 1: 1
3 +2 3 1 4 -2 5: 1
3 -2 3 1 1 -2 3: 1
8 1 6 -2 8 +2 6: 1
5 -3 7 1 6 -2 8: 1
-3 1 -6 -3 -3 +2 -3: 1
-3 1 -2 1 1 1 -3: 1
6 1 7 1 8 1 6: 1
6 +3 3 -2 6 -2 8: 1
7 1 8 +3 6 1 5: 1
7 +2 5 -4 8 1 7: 1
5 -2 6 -2 6 -2 6: 1
3 -2 3 +4 3 1 2: 1
6 1 5 1 4 1 8: 1
6 -3 8 +3 5 1 4: 1
6 -2 6 +2 6 -2 8: 1
5 -2 6 -2 6 -2 8: 1
-3 1 -2 1 1 1 2: 1
-2 -2 5 -2 6 +2 1: 1
4 -2 5 -2 8 +3 6: 1
3 -2 4 -2 6 1 4: 1
3 1 5 -2 6 1 5: 1
5 1 6 -3 8 +4 5: 1
5 1 4 1 3 -2 3: 1
6 +2 5 -3 7 1 6: 1
5 1 4 1 3 -2 4: 1
4 1 3 -3 6 -2 8: 1
3 +3 1 1 2 1 3: 1
5 -2 8 +2 7 +2 5: 1
-3 -2 -2 -2 1 1 2: 1
10 +5 6 -5 10 1 9: 1
6 1 4 -2 5 +2 3: 1
6 1 5 1 3 1 4: 1
3 -3 5 +2 4 -2 3: 1
5 +3 1 1 3 -2 4: 1
6 1 7 1 8 +3 6: 1
1 1 -2 1 -3 1 -4: 1
6 1 8 +2 7 +2 6: 1
4 1 6 +3 3 +2 2: 1
8 +2 6 -3 8 +2 5: 1
9 +3 6 -3 8 +3 5: 1
3 +2 1 -3 3 -2 6: 1
6 +3 3 +2 2 +2 3: 1
3 1 2 +3 1 1 2: 1
4 -2 5 1 3 -2 5: 1
3 -3 4 1 3 +2 3: 1
6 +2 5 +2 3 1 2: 1
5 1 4 -2 3 1 4: 1
4 -2 3 1 4 -2 5: 1
6 +2 3 +2 1 1 5: 1
6 -3 8 +4 5 1 4: 1
7 -2 8 1 7 +2 5: 1
-5 -8 8 +3 6 -3 8: 1
5 +3 3 -2 4 -2 5: 1
6 -2 8 +3 6 1 5: 1
7 1 6 1 5 +2 4: 1
7 1 8 1 6 -2 8: 1
3 1 4 -2 5 +2 3: 1
2 1 1 1 2 -2 3: 1
5 -2 8 +3 6 1 5: 1
8 +2 7 +2 6 -2 7: 1
5 +2 3 1 2 -2 3: 1
4 -3 8 +2 7 +2 6: 1
3 +5 -3 -2 -2 -2 1: 1
3 +2 6 +4 3 -2 4: 1
3 -2 4 +2 3 +2 3: 1
7 1 6 1 5 1 6: 1
3 1 4 1 5 -3 6: 1
5 +2 3 +5 -3 -2 -2: 1
4 -2 6 +8 -3 -2 -2: 1
1 -2 2 -2 3 1 -3: 1
5 -3 6 +2 5 1 4: 1
7 +2 6 -2 7 +2 6: 1
4 -2 5 -2 6 -2 7: 1
6 1 5 1 6 1 7: 1
-3 -2 -2 -2 5 -2 6: 1
10 1 9 +3 6 -3 8: 1
-6 -3 -3 +2 -3 1 -2: 1
7 1 6 +2 5 -3 7: 1
3 1 4 1 8 1 7: 1
3 +2 3 1 1 -4 5: 1
5 1 3 1 4 -2 6: 1
7 +2 6 +2 5 -3 3: 1
-2 1 -3 +2 -3 1 -6: 1
7 +2 5 +2 4 +2 1: 1
5 -3 3 -3 8 1 7: 1
6 -5 10 1 9 +3 6: 1
4 -2 5 -2 8 +2 7: 1
-2 -5 5 +2 4 1 3: 1
6 +2 5 1 3 -2 6: 1
4 -2 5 1 4 1 3: 1
8 +2 7 +2 6 1 5: 1
5 +2 4 -2 3 +4 3: 1
5 +3 1 1 2 1 3: 1
5 -3 7 1 6 +2 5: 1
-4 -2 3 -2 4 -2 5: 1
5 -2 6 +2 1 1 2: 1
5 -4 8 1 7 1 6: 1
4 -2 6 1 4 -2 5: 1
3 1 2 1 1 1 2: 1
-3 1 -4 1 -3 -2 -2: 1
10 +3 6 1 8 +2 7: 1
-3 1 3 -2 4 -2 3: 1
4 1 5 -3 7 1 6: 1
8 +8 1 -2 2 -2 3: 1
5 +2 4 1 3 1 4: 1
3 -2 3 -3 4 1 3: 1
7 +2 6 +2 5 1 3: 1
4 -3 6 -2 7 1 6: 1
8 +4 5 1 4 -2 3: 1
3 +2 3 +2 3 -2 3: 1
6 1 5 +2 4 1 3: 1
5 -2 6 1 5 1 4: 1
4 -2 5 +2 3 +5 -3: 1
7 +2 -3 +2 -3 +2 -3: 1
8 -3 10 +3 6 1 8: 1
-2 1 1 1 -3 -2 1: 1
-2 1 1 1 2 1 3: 1
1 -2 2 -2 6 +2 5: 1
6 +4 3 -2 4 +2 2: 1
3 1 4 -2 6 +8 -3: 1
3 -5 8 +3 -3 1 3: 1
3 -2 4 -3 8 +2 7: 1
7 +2 4 +2 3 +2 3: 1
3 +2 2 +2 3 -5 8: 1
1 -2 2 -2 3 +2 6: 1
-3 -2 -2 -2 1 +3 -4: 1
3 -2 4 -2 5 1 3: 1
3 -3 8 1 7 1 6: 1
5 1 3 -2 6 -2 7: 1
4 1 6 +3 3 -2 6: 1
3 -5 8 +2 7 +2 6: 1
6 +2 5 -3 3 -3 8: 1
3 1 4 -2 5 1 4: 1
-3 +2 -3 1 -2 1 1: 1
3 -2 6 -2 7 -2 8: 1
3 1 4 -2 5 -2 6: 1
1 -2 2 -2 -3 -2 -2: 1
5 1 6 1 7 1 8: 1
-4 -2 -3 -2 -2 -2 1: 1
1 +3 -4 -2 -3 -2 -2: 1
8 +3 -3 1 3 -2 4: 1
3 -3 3 1 4 -2 6: 1
3 -2 4 +2 2 1 3: 1
6 +2 1 1 2 1 3: 1
8 +2 6 +2 4 +2 3: 1
6 -2 8 +2 7 +2 6: 1
5 -2 6 -2 7 +2 4: 1
1 -2 2 -2 3 1 4: 1
8 +2 7 +2 -3 +2 -3: 1
-3 1 -4 1 -5 -2 -3: 1
4 1 3 -2 4 -2 6: 1
7 1 6 -3 8 +2 7: 1
5 -2 6 +2 3 +2 1: 2
3 -2 4 -2 5 -2 6: 2
4 -2 6 1 7 1 6: 2
8 1 7 1 6 1 5: 2
1 1 2 1 3 -2 3: 2
3 -2 3 -2 3 -2 3: 2
-2 -2 1 -2 2 -2 3: 2
3 -2 5 -3 8 +2 7: 2
4 -3 6 1 5 +3 1: 2
1 1 2 -2 3 +2 1: 2
3 -2 5 -2 6 +2 3: 2
2 1 3 -2 3 -2 3: 2
8 +2 7 1 6 -2 8: 2
1 1 3 -2 4 -3 6: 2
4 -2 5 -2 6 -2 6: 2
3 -2 4 -3 6 1 5: 2
2 1 3 -2 5 -3 8: 2
7 1 6 1 5 1 4: 2
6 1 7 1 6 1 5: 2
8 +2 7 +2 6 +2 5: 3
3 -2 4 -2 5 -2 8: 3
1 1 2 1 3 -2 5: 3
3 1 4 -2 6 1 7: 3
-3 -2 -2 -2 1 -2 2: 4

'''
      score = converter.parse( 'test_corpus/Jos2308.krn' )
      sets = VIS_Settings()
      sets.set_property( 'lookForTheseNs 4' )
      vis_these_parts( [score.parts[0], score.parts[1]], sets, self.vis, 'test_corpus/Jos2308.krn' )
      self.assertEqual( self.vis.get_formatted_ngrams( sets, 'ascending by frequency' ), \
                        ascending_by_frequency )
# End Test_Output_Formatting() ------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
suite = unittest.TestLoader().loadTestsFromTestCase( Test_Output_Formatting )
