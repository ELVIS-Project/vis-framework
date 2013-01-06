#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         TestSorting.py
# Purpose:      Unit tests for the NGram class.
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



# Imports from...
# python
import unittest
# music21
from music21 import converter
# PyQt4
from PyQt4.QtCore import Qt, QVariant
# vis
from models import analyzing



class TestListOfPiecesBasics(unittest.TestCase):
   # Test __init__(); rowCount(); columnCount()
   def setUp(self):
      self.lop = analyzing.ListOfPieces()



   def test_init_1(self):
      # test all the statics
      self.assertEqual(5, self.lop._number_of_columns)
      self.assertEqual(0, self.lop.filename)
      self.assertEqual(1, self.lop.score)
      self.assertEqual(2, self.lop.parts_list)
      self.assertEqual(3, self.lop.offset_intervals)
      self.assertEqual(4, self.lop.parts_combinations)



   def test_init_2(self):
      self.assertEqual([], self.lop._pieces)



   def test_column_count_1(self):
      self.assertEqual(5, self.lop.columnCount())



   def test_row_count_1(self):
      self.lop._pieces = []
      self.assertEqual(0, self.lop.rowCount())



   def test_row_count_2(self):
      self.lop._pieces = [[]]
      self.assertEqual(1, self.lop.rowCount())



   def test_row_count_3(self):
      self.lop._pieces = [[],[]]
      self.assertEqual(2, self.lop.rowCount())



   def test_row_count_4(self):
      self.lop._pieces = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
      self.assertEqual(18, self.lop.rowCount())
# End TestListOfPiecesBasics ---------------------------------------------------



class TestListOfPiecesInsertAndRemoveRows(unittest.TestCase):
   # Test insertRows() and removeRows()
   def setUp(self):
      self.lop = analyzing.ListOfPieces()
      self.default_row = ['', None, [], [0.5], [2], '(no selection)']

   def test_insert_1(self):
      #self.lop._pieces = []
      self.insertRows(0, 1)
      self.assertEqual([self.default_row], self.lop._pieces)



   def test_insert_2(self):
      #self.lop._pieces = []
      self.insertRows(0, 5)
      for each_row in self.lop._pieces:
         self.assertEqual(self.default_row, each_row)



   def test_insert_3(self):
      self.lop._pieces = ['a', 'b', 'c', 'd']
      self.insertRows(0, 1)
      self.assertEqual([self.default_row, 'a', 'b', 'c', 'd'], self.lop._pieces)



   def test_insert_4(self):
      self.lop._pieces = ['a', 'b', 'c', 'd']
      self.insertRows(2, 1)
      self.assertEqual(['a', 'b', self.default_row, 'c', 'd'], self.lop._pieces)



   def test_insert_5(self):
      self.lop._pieces = ['a', 'b', 'c', 'd']
      self.insertRows(3, 5)
      self.assertEqual(['a', 'b', 'c', 'd'], self.lop._pieces[:3])
      for each_row in self.lop._pieces[4:]:
         self.assertEqual(self.default_row, each_row)
# End TestListOfPiecesInsertAndRemoveRows --------------------------------------



class TestListOfPiecesHeaderData(unittest.TestCase):
   # Test headerData()

   def setUp(self):
      self.lop = analyzing.ListOfPieces()



   def test_header_data_1(self):
      self.assertEqual('Path',
                       self.lop.headerData(ListOfPieces.filename,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_2(self):
      self.assertEqual('Title',
                       self.lop.headerData(ListOfPieces.filename,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_3(self):
      self.assertEqual('List of Part Names',
                       self.lop.headerData(ListOfPieces.filename,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_4(self):
      self.assertEqual('Offset',
                       self.lop.headerData(ListOfPieces.filename,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_5(self):
      self.assertEqual('Part Combinations',
                       self.lop.headerData(ListOfPieces.filename,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_6(self):
      self.assertEqual(QVariant(),
                       self.lop.headerData(-1,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_7(self):
      self.assertEqual(QVariant(),
                       self.lop.headerData(ListOfPieces._number_of_columns+1,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_8(self):
      self.assertEqual(QVariant(),
                       self.lop.headerData(-1000,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_9(self):
      self.assertEqual(QVariant,
                       self.lop.headerData(1000,
                                           Qt.Horizontal,
                                           Qt.DisplayRole))



   def test_header_data_10(self):
      self.assertEqual(QVariant,
                       self.lop.headerData(1,
                                           Qt.Vertical,
                                           Qt.DisplayRole))



   def test_header_data_11(self):
      self.assertEqual(QVariant,
                       self.lop.headerData(1,
                                           Qt.Horizontal,
                                           Qt.EditRole))
# End TestListOfPiecesHeaderData -----------------------------------------------



class TestListOfPiecesIterateRows(unittest.TestCase):
   # Test iterateRows()
   # TODO: figure out how to write this
   pass
# End TestListOfPiecesIterateRows ----------------------------------------------



class TestListOfPiecesSetData(unittest.TestCase):
   # Test setData()
   def setUp(self):
      self.lop = analyzing.ListOfPieces()
      self.default_row = ['', None, [], [0.5], [2], '(no selection)']



   def test_set_data_1(self):
      self.lop._pieces = [self.default_row]
      index = self.lop.makeIndex(0, ListOfPieces.filename)
      self.setData(index, '../test_corpus/Kyrie.krn', Qt.EditRole)
      self.assertEqual('../test_corpus/Kyrie.krn',
                       self.lop._pieces[0][ListOfPieces.filename])



   def test_set_data_2(self):
      self.lop._pieces = [self.default_row]
      index = self.lop.makeIndex(0, ListOfPieces.score)
      test_score = converter.parse('../test_corpus/bwv77.mxl')
      self.setData(index, (test_score, 'Chorale!'), Qt.EditRole)
      self.assertEqual((test_score, 'Chorale!'),
                       self.lop._pieces[0][ListOfPieces.score])



   def test_set_data_3(self):
      self.lop._pieces = [self.default_row]
      index = self.lop.makeIndex(0, ListOfPieces.parts_list)
      self.setData(index, ['a', 'b', 'c', 'd'], Qt.EditRole)
      self.assertEqual(['a', 'b', 'c', 'd'],
                       self.lop._pieces[0][ListOfPieces.parts_list])



   def test_set_data_4(self):
      self.lop._pieces = [self.default_row]
      index = self.lop.makeIndex(0, ListOfPieces.offset_intervals)
      self.setData(index, [0.25], Qt.EditRole)
      self.assertEqual([0.25],
                       self.lop._pieces[0][ListOfPieces.offset_intervals])



   def test_set_data_5(self):
      self.lop._pieces = [self.default_row]
      index = self.lop.makeIndex(0, ListOfPieces.parts_combinations)
      self.setData(index, [[0, 1], [0, 'bs']], Qt.EditRole)
      self.assertEqual([[0, 1], [0, 'bs']],
                       self.lop._pieces[0][ListOfPieces.parts_combinations])



   def test_set_data_6(self):
      self.lop._pieces = [self.default_row, self.default_row, self.default_row]
      index = self.lop.makeIndex(1, ListOfPieces.filename)
      self.setData(index, '../test_corpus/madrigal51.mxl', Qt.EditRole)
      self.assertEqual('../test_corpus/madrigal51.mxl',
                       self.lop._pieces[1][ListOfPieces.filename])
# End TestListOfPiecesSetData --------------------------------------------------



class TestListOfPiecesData(unittest.TestCase):
   # Test data()
   def setUp(self):
      self.lop = analyzing.ListOfPieces()
      self.default_row = ['', None, [], [0.5], [2], '(no selection)']



   def test_data_1(self):
      self.lop._pieces = [self.default_row]
      the_field = '../test_corpus/Kyrie.krn'
      self.lop._pieces[0][ListOfPieces.filename] = the_field
      index = self.lop.makeIndex(0, ListOfPieces.filename)
      self.assertEqual(the_field, self.lop.data(index, Qt.DisplayRole))



   def test_data_2(self):
      self.lop._pieces = [self.default_row]
      the_field = (converter.parse('../test_corpus/bwv77.mxl'), 'Chorale!')
      self.lop._pieces[0][ListOfPieces.score] = the_field
      index = self.lop.makeIndex(0, ListOfPieces.score)
      self.assertEqual(the_field[1], self.lop.data(index, Qt.DisplayRole))



   def test_data_3(self):
      self.lop._pieces = [self.default_row]
      the_field = (converter.parse('../test_corpus/bwv77.mxl'), 'Chorale!')
      self.lop._pieces[0][ListOfPieces.score] = the_field
      index = self.lop.makeIndex(0, ListOfPieces.score)
      self.assertEqual(the_field[0],
                       self.lop.data(index, ListOfPieces.ScoreRole))



   def test_data_4(self):
      self.lop._pieces = [self.default_row]
      the_field = ['a', 'b', 'c', 'd']
      self.lop._pieces[0][ListOfPieces.parts_list] = the_field
      index = self.lop.makeIndex(0, ListOfPieces.parts_list)
      self.assertEqual(the_field, self.lop.data(index, Qt.DisplayRole))



   def test_data_5(self):
      self.lop._pieces = [self.default_row]
      the_field = [0.25]
      self.lop._pieces[0][ListOfPieces.offset_intervals] = the_field
      index = self.lop.makeIndex(0, ListOfPieces.offset_intervals)
      self.assertEqual(the_field, self.lop.data(index, Qt.DisplayRole))



   def test_data_6(self):
      self.lop._pieces = [self.default_row]
      the_field = [[0, 1], [0, 'bs']]
      self.lop._pieces[0][ListOfPieces.parts_combinations] = the_field
      index = self.lop.makeIndex(0, ListOfPieces.parts_combinations)
      self.assertEqual(the_field, self.lop.data(index, Qt.DisplayRole))



   def test_data_7(self):
      self.lop._pieces = [self.default_row, self.default_row]
      the_field = '../test_corpus/madrigal51.mxl'
      self.lop._pieces[1][ListOfPieces.filename] = the_field
      index = self.lop.makeIndex(1, ListOfPieces.filename)
      self.assertEqual(the_field, self.lop.data(index, Qt.DisplayRole))



   def test_data_8(self):
      # just to make sure the tricky one works in higher rows... (1 of 2)
      self.lop._pieces = [[], [], [], [], self.default_row, [], []]
      the_field = (converter.parse('../test_corpus/bwv77.mxl'), 'Chorale!')
      self.lop._pieces[4][ListOfPieces.score] = the_field
      index = self.lop.makeIndex(4, ListOfPieces.score)
      self.assertEqual(the_field[1], self.lop.data(index, Qt.DisplayRole))



   def test_data_9(self):
      # just to make sure the tricky one works in higher rows... (2 of 2)
      self.lop._pieces = [[], [], [], [], self.default_row, [], []]
      the_field = (converter.parse('../test_corpus/bwv77.mxl'), 'Chorale!')
      self.lop._pieces[4][ListOfPieces.score] = the_field
      index = self.lop.makeIndex(4, ListOfPieces.score)
      self.assertEqual(the_field[0],
                       self.lop.data(index, ListOfPieces.ScoreRole))
# End TestListOfPiecesData -----------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
lop_basics_suite = unittest.TestLoader().loadTestsFromTestCase(TestListOfPiecesBasics)
lop_insert_and_remove_suite = unittest.TestLoader().loadTestsFromTestCase(TestListOfPiecesInsertAndRemoveRows)
lop_iterate_rows_suite = unittest.TestLoader().loadTestsFromTestCase(TestListOfPiecesIterateRows)
lop_set_data_suite = unittest.TestLoader().loadTestsFromTestCase(TestListOfPiecesSetData)
lop_header_data_suite = unittest.TestLoader().loadTestsFromTestCase(TestListOfPiecesHeaderData)
lop_data_suite = unittest.TestLoader().loadTestsFromTestCase(TestListOfPiecesData)
