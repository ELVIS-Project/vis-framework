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
# PyQt4
from PyQt4.QtCore import Qt, QVariant
# vis
from models import importing



class TestBasics(unittest.TestCase):
   # Test the constructor, rowCount(), headerData(), flags()
   def setUp(self):
      self.lof = importing.ListOfFiles()



   def test_constructor_1(self):
      self.assertEqual([], self.lof._files)



   def test_rowCount_1(self):
      self.assertEqual(0, self.lof.rowCount())



   def test_rowCount_2(self):
      self.lof._files = ['allegro.midi']
      self.assertEqual(1, self.lof.rowCount())



   def test_rowCount_3(self):
      self.lof._files = ['allegro.midi', 'langsam.md']
      self.assertEqual(2, self.lof.rowCount())
# End TestInit -----------------------------------------------------------------



class TestData(unittest.TestCase):
   # Test data()
   def setUp(self):
      self.lof = importing.ListOfFiles()



   def test_data_1(self):
      self.lof._files = ['a']
      self.assertEqual('a', self.lof.data(self.lof.createIndex(0, 0), Qt.DisplayRole))



   def test_data_2(self):
      self.lof._files = ['a', 'b', 'c']
      self.assertEqual('a', self.lof.data(self.lof.createIndex(0, 0), Qt.DisplayRole))
      self.assertEqual('b', self.lof.data(self.lof.createIndex(1, 0), Qt.DisplayRole))
      self.assertEqual('c', self.lof.data(self.lof.createIndex(2, 0), Qt.DisplayRole))
      self.assertEqual(QVariant(), self.lof.data(self.lof.createIndex(3, 0), Qt.DisplayRole))



   def test_data_4(self):
      self.assertEqual(QVariant(), self.lof.data(self.lof.createIndex(0, 0), Qt.DisplayRole))
# End TestData -----------------------------------------------------------------




class TestSetData(unittest.TestCase):
   # Test setData()
   def setUp(self):
      self.lof = importing.ListOfFiles()


   def test_set_data_1(self):
      self.lof._files = ['']
      self.lof.setData(self.lof.createIndex(0, 0), 'kyrie.krn', Qt.EditRole)
      self.assertEqual(['kyrie.krn'], self.lof._files)


   def test_set_data_2(self):
      self.lof._files = ['', '', '', '', '']
      self.lof.setData(self.lof.createIndex(2, 0), 'kyrie.krn', Qt.EditRole)
      self.assertEqual(['', '', 'kyrie.krn', '', ''], self.lof._files)


   def test_set_data_3(self):
      self.lof._files = ['', '', '']
      self.lof.setData(self.lof.createIndex(3, 0), 'kyrie.krn', Qt.EditRole)
      self.assertEqual(['', '', ''], self.lof._files)


   def test_set_data_4(self):
      self.lof._files = ['', '', '', '', '']
      self.lof.setData(self.lof.createIndex(1, 0), 'kyrie.krn', Qt.EditRole)
      self.lof.setData(self.lof.createIndex(2, 0), 'gloria.krn', Qt.EditRole)
      self.lof.setData(self.lof.createIndex(3, 0), 'minuet.krn', Qt.EditRole)
      self.assertEqual(['', 'kyrie.krn', 'gloria.krn', 'minuet.krn', ''],
                       self.lof._files)
# End TestSetData --------------------------------------------------------------



class TestInsertRows(unittest.TestCase):
   # Test insertRows()
   def setUp(self):
      self.lof = importing.ListOfFiles()



   def test_insert_rows_1(self):
      #self.lof._files = []
      self.lof.insertRows(0, 1)
      self.assertEqual([''], self.lof._files)


   def test_insert_rows_2(self):
      #self.lof._files = []
      self.lof.insertRows(0, 2)
      self.assertEqual(['', ''], self.lof._files)


   def test_insert_rows_3(self):
      #self.lof._files = []
      self.lof.insertRows(0, 5)
      self.assertEqual(['', '', '', '', ''], self.lof._files)


   def test_insert_rows_4(self):
      self.lof._files = ['a']
      self.lof.insertRows(0, 1)
      self.assertEqual(['', 'a'], self.lof._files)


   def test_insert_rows_5(self):
      self.lof._files = ['a', 'b', 'c', 'd']
      self.lof.insertRows(0, 2)
      self.assertEqual(['', '', 'a', 'b', 'c', 'd'], self.lof._files)


   def test_insert_rows_6(self):
      self.lof._files = ['a', 'b', 'c', 'd']
      self.lof.insertRows(3, 1)
      self.assertEqual(['a', 'b', 'c', '', 'd'], self.lof._files)
# End TestInsertRows -----------------------------------------------------------



class TestIsPresent(unittest.TestCase):
   # Test isPresent()
   def setUp(self):
      self.lof = importing.ListOfFiles()



   def test_is_present_1(self):
      self.lof._files = ['a', 'b', 'c', 'd']
      self.assertTrue(self.lof.isPresent('b'))



   def test_is_present_2(self):
      self.lof._files = ['a']
      self.assertTrue(self.lof.isPresent('a'))



   def test_is_present_3(self):
      self.lof._files = ['a', 'b', 'c', 'd']
      self.assertFalse(self.lof.isPresent('l'))



   def test_is_present_4(self):
      self.assertFalse(self.lof.isPresent('anything'))
# End TestIsPresent ------------------------------------------------------------



class TestIterator(unittest.TestCase):
   # Test iterateRows()
   # TODO: how to test this?
   pass
# End TestIterator -------------------------------------------------------------



class TestRemoveRows(unittest.TestCase):
   # Test removeRows()
   def setUp(self):
      self.lof = importing.ListOfFiles()



   def test_remove_rows_1(self):
      self.lof._files = ['a', 'b', 'c']
      self.lof.removeRows(2, 1)
      self.assertEqual(['a', 'b'], self.lof._files)



   def test_remove_rows_2(self):
      self.lof._files = ['a', 'b', 'c']
      self.lof.removeRows(1, 2)
      self.assertEqual(['a'], self.lof._files)



   def test_remove_rows_3(self):
      self.lof._files = ['a', 'b', 'c']
      self.lof.removeRows(0, 1)
      self.assertEqual(['b', 'c'], self.lof._files)



   def test_remove_rows_4(self):
      self.lof._files = ['a', 'b', 'c']
      self.lof.removeRows(2, 4)
      self.assertEqual(['a', 'b'], self.lof._files)



   def test_remove_rows_5(self):
      self.lof._files = ['a', 'b', 'c']
      self.lof.removeRows(0, 3)
      self.assertEqual([], self.lof._files)
# End TestRemoveRows -----------------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
importing_basics_suite = unittest.TestLoader().loadTestsFromTestCase(TestBasics)
importing_data_suite = unittest.TestLoader().loadTestsFromTestCase(TestData)
importing_set_data_suite = unittest.TestLoader().loadTestsFromTestCase(TestSetData)
importing_insert_rows_suite = unittest.TestLoader().loadTestsFromTestCase(TestInsertRows)
importing_is_present_suite = unittest.TestLoader().loadTestsFromTestCase(TestIsPresent)
importing_iterator_suite = unittest.TestLoader().loadTestsFromTestCase(TestIterator)
importing_remove_rows_suite = unittest.TestLoader().loadTestsFromTestCase(TestRemoveRows)
