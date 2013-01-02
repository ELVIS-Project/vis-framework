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
# TODO: test all of these with signals too


# Imports from...
# PyQt
from PyQt.QtCore import Qt
# music21
from music21 import converter
# vis
from controllers import importer
from models import importing, analyzing



class TestPieceGetter(unittest.TestCase):
   # For the method Importer._piece_getter()

   def test_bwv77(self):
      path = '../test_corpus/bwv77.mxl'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_jos2308_krn(self):
      path = '../test_corpus/Jos2308.krn'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_jos2308_mei(self):
      # Because music21 doesn't support MEI, this will not work
      path = '../test_corpus/Jos2308.mei'
      self.assertRaises(converter.ConverterFileException,
                        converter.parse,
                        path)
      self.assertRaises(converter.ConverterFileException,
                        Importer._piece_getter,
                        path)

   def test_kyrie(self):
      path = '../test_corpus/Kyrie.krn'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_laPlusDesPlus(self):
      path = '../test_corpus/laPlusDesPlus.abc'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_madrigal51(self):
      path = '../test_corpus/madrigal51.mxl'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_sinfony(self):
      path = '../test_corpus/sinfony.md'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_sqOp76_4_i(self):
      path = '../test_corpus/sqOp76-4-i.midi'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)
# End TestPieceGetter ----------------------------------------------------------



class TestPartsAndTitles(unittest.TestCase):
   # Testing Importer._find_part_names() and Importer._find_piece_title

   def test_bwv77(self):
      path = '../test_corpus/bwv77.mxl'
      title = 'bwv77'
      parts = ['Soprano', 'Alto', 'Tenor', 'Bass']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_jos2308_krn(self):
      path = '../test_corpus/Jos2308.krn'
      title = 'Jos2308'
      parts = ['spine_3', 'spine_2', 'spine_1', 'spine_0']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_kyrie(self):
      path = '../test_corpus/Kyrie.krn'
      title = 'Kyrie'
      parts = ['spine_4', 'spine_3', 'spine_2', 'spine_1', 'spine_0']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_laPlusDesPlus(self):
      path = '../test_corpus/laPlusDesPlus.abc'
      title = 'La plus des plus'
      parts = ['68786512', '68784656', '141162896']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_madrigal51(self):
      path = '../test_corpus/madrigal51.mxl'
      title = 'madrigal51'
      parts = ['Canto', 'Alto', 'Tenor', 'Quinto', 'Basso', 'Continuo']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_sinfony(self):
      path = '../test_corpus/sinfony.md'
      title = 'Messiah'
      parts = ['Violino I', 'Violino II', 'Viola', 'Basssi']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_sqOp76_4_i(self):
      path = '../test_corpus/sqOp76-4-i.midi'
      title = 'sqOp76-4-i'
      parts = ['118617936', '9674896', '174769616', '197486544']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)
# End TestImportPieces ---------------------------------------------------------



class TestAddPieces(unittest.TestCase):
   # For the method Importer.add_pieces()

   def setUp(self):
      self.control = Importer()

   # add one piece to an empty Importer
   def test_add_pieces_1(self):
      paths = ['../test_corpus/bwv77.mxl']
      self.control.add_piece(paths)
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add multiple to empty
   def test_add_pieces_2(self):
      paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn']
      self.control.add_piece(paths)
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add one conflict to one
   def test_add_pieces_3(self):
      paths = ['../test_corpus/bwv77.mxl']
      self.control.add_piece(paths)
      self.control.add_piece(paths)
      self.assertEqual(1, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add one conflict to multiple
   def test_add_pieces_4(self):
      paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn']
      self.control.add_piece(paths)
      self.control.add_piece(['../test_corpus/bwv77.mxl'])
      self.assertEqual(2, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add one to already-one
   def test_add_pieces_5(self):
      paths = ['../test_corpus/bwv77.mxl']
      self.control.add_piece(paths)
      paths = ['../test_corpus/Kyrie.krn']
      self.control.add_piece(paths)
      paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn']
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add multiple to already-one
   def test_add_pieces_6(self):
      paths = ['../test_corpus/bwv77.mxl']
      self.control.add_piece(paths)
      paths = ['../test_corpus/Kyrie.krn', '../test_corpus/madrigal51.mxl']
      self.control.add_piece(paths)
      paths = ['../test_corpus/Kyrie.krn', '../test_corpus/madrigal51.mxl',
               '../test_corpus/bwv77.mxl']
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add one to already-many
   def test_add_pieces_7(self):
      paths = ['../test_corpus/Kyrie.krn', '../test_corpus/madrigal51.mxl']
      self.control.add_piece(paths)
      paths = ['../test_corpus/bwv77.mxl']
      self.control.add_piece(paths)
      paths = ['../test_corpus/Kyrie.krn', '../test_corpus/madrigal51.mxl',
               '../test_corpus/bwv77.mxl']
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add many to already-many
   def test_add_pieces_8(self):
      paths = ['../test_corpus/Kyrie.krn', '../test_corpus/madrigal51.mxl']
      self.control.add_piece(paths)
      paths = ['../test_corpus/bwv77.mxl', '../test_corpus/sinfony.md']
      self.control.add_piece(paths)
      paths = ['../test_corpus/Kyrie.krn', '../test_corpus/madrigal51.mxl',
               '../test_corpus/bwv77.mxl', '../test_corpus/sinfony.md']
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add many including a conflict to already-many
   def test_add_pieces_9(self):
      paths = ['../test_corpus/Kyrie.krn', '../test_corpus/madrigal51.mxl']
      self.control.add_piece(paths)
      paths = ['../test_corpus/bwv77.mxl', '../test_corpus/sinfony.md',
               '../test_corpus/Kyrie.krn']
      self.control.add_piece(paths)
      paths = ['../test_corpus/Kyrie.krn', '../test_corpus/madrigal51.mxl',
               '../test_corpus/bwv77.mxl', '../test_corpus/sinfony.md']
      self.assertEqual(4, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add one non-existant filename
   def test_add_pieces_10(self):
      paths = ['../test_corpus/does_not.exist']
      self.control.add_piece(paths)
      self.assertEqual(0, self.control._list_of_pieces.rowCount())

   # add many filenames with one non-existant file
   def test_add_pieces_11(self):
      paths = ['../test_corpus/bwv77.mxl', '../test_corpus/does_not.exist',
               '../test_corpus/madrigal51.mxl']
      self.control.add_piece(paths)
      paths = ['../test_corpus/bwv77.mxl', '../test_corpus/madrigal51.mxl']
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)

   # add a directory from empty with no conflicts
   def test_add_pieces_12(self):
      paths = ['../test_corpus/bwv77.mxl',
               '../test_corpus/Jos2308.krn',
               '../test_corpus/Kyrie.krn',
               '../test_corpus/laPlusDesPlus.abc',
               '../test_corpus/madrigal51.mxl',
               '../test_corpus/sinfony.md',
               '../test_corpus/sqOp76-4-i.midi']
      self.control.add_piece(['../test_corpus'])
      for path in self.control._list_of_files:
         self.assertTrue(path in paths)
# End TestAddPieces ------------------------------------------------------------



class TestRemovePieces(unittest.TestCase):
   # For the method Importer.remove_pieces()

   def setUp(self):
      self.control = Importer()

   # remove one from empty list
   def test_remove_pieces_1(self):
      #add_paths = ['../test_corpus/']
      remove_paths = ['../test_corpus/bwv77.mxl']
      #expected_paths = ['../test_corpus/']
      expected_length = 0
      #self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      #for path in self.control._list_of_files:
         #self.assertTrue(path in expected_paths)

   # remove one from one-item list
   def test_remove_pieces_2(self):
      add_paths = ['../test_corpus/bwv77.mxl']
      remove_paths = ['../test_corpus/bwv77.mxl']
      expected_paths = ['../test_corpus/bwv77.mxl']
      expected_length = 1
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in expected_paths)

   # remove one from many-item list
   def test_remove_pieces_3(self):
      add_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn']
      remove_paths = ['../test_corpus/bwv77.mxl']
      expected_paths = ['../test_corpus/Kyrie.krn']
      expected_length = 1
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in expected_paths)

   # remove many from one-item list
   def test_remove_pieces_4(self):
      add_paths = ['../test_corpus/bwv77.mxl']
      remove_paths = ['../test_corpus/Kyrie.krn', '../test_corpus/bwv77.mxl']
      #expected_paths = ['../test_corpus/']
      expected_length = 0
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      #for path in self.control._list_of_files:
         #self.assertTrue(path in expected_paths)

   # remove many from many-item list
   def test_remove_pieces_5(self):
      add_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn',
                   '../test_corpus/madrigal51.mxl']
      remove_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn']
      expected_paths = ['../test_corpus/madrigal51.mxl']
      expected_length = 1
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in expected_paths)

   # remove one-not-present from one-item
   def test_remove_pieces_6(self):
      add_paths = ['../test_corpus/bwv77.mxl']
      remove_paths = ['../test_corpus/madrigal51.mxl']
      expected_paths = ['../test_corpus/bwv77.mxl']
      expected_length = 1
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in expected_paths)

   # remove one-not-present from many-item
   def test_remove_pieces_7(self):
      add_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn',
                   '../test_corpus/madrigal51.mxl']
      remove_paths = ['../test_corpus/sinfony.md']
      expected_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn',
                        '../test_corpus/madrigal51.mxl']
      expected_length = 3
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in expected_paths)

   # remove many-including-not-present from many-item
   def test_remove_pieces_8(self):
      add_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn',
                   '../test_corpus/madrigal51.mxl']
      remove_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn',
                      '../test_corpus/sinfony.md']
      expected_paths = ['../test_corpus/madrigal51.mxl']
      expected_length = 1
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in expected_paths)

   # remove all from many-item
   def test_remove_pieces_9(self):
      add_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn',
                   '../test_corpus/madrigal51.mxl']
      remove_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn',
                      '../test_corpus/madrigal51.mxl']
      #expected_paths = ['../test_corpus/']
      expected_length = 0
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      #for path in self.control._list_of_files:
         #self.assertTrue(path in expected_paths)

   # remove many from many-item
   def test_remove_pieces_10(self):
      add_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn',
                   '../test_corpus/madrigal51.mxl']
      remove_paths = ['../test_corpus/bwv77.mxl', '../test_corpus/Kyrie.krn']
      expected_paths = ['../test_corpus/madrigal51.mxl']
      expected_length = 1
      self.control.add_pieces(add_paths)
      self.control.remove_pieces(remove_paths)
      self.assertEqual(expected_length, self.control._list_of_files.rowCount())
      for path in self.control._list_of_files:
         self.assertTrue(path in expected_paths)

# End TestRemovePieces ------------------------------------------------------------



class TestImportPieces(unittest.TestCase):
   # For the method Importer.import_pieces()

   def test_all_pieces_calling(self):
      # Tests importing the whole test corpus through calling and return value

      # (1) Set up the Importer controller
      paths = ['../test_corpus/bwv77.mxl',
               '../test_corpus/Jos2308.krn',
               '../test_corpus/Kyrie.krn',
               '../test_corpus/laPlusDesPlus.abc',
               '../test_corpus/madrigal51.mxl',
               '../test_corpus/sinfony.md',
               '../test_corpus/sqOp76-4-i.midi']
      control = Importer()
      control.add_pieces(paths)

      # (2) Finish the "expected" lists
      # holds the Score objects
      pieces = [converter.parse(path) for path in paths]
      # holds the titles as strings
      titles = [Importer._find_piece_title(piece) for piece in pieces]
      # holds the part-name lists as lists of strings
      parts = [Importer._find_part_names(piece) for piece in pieces]

      # (3) Run the import
      returned = control.import_pieces()

      # (4) Check for correctness
      for row in xrange(len(paths)): # filenames
         index = ListOfPieces.createIndex(row, ListOfPieces.filename)
         self.assertEqual(paths[row], returned.data(index, Qt.DisplayRole))
      for row in xrange(len(paths)): # titles
         index = ListOfPieces.createIndex(row, ListOfPieces.score)
         self.assertEqual(titles[row], returned.data(index, Qt.DisplayRole))
      for row in xrange(len(paths)): # Score objects
         index = ListOfPieces.createIndex(row, ListOfPieces.score)
         self.assertEqual(pieces[row], returned.data(index, ListOfPieces.ScoreRole))
      for row in xrange(len(paths)): # lists of parts
         index = ListOfPieces.createIndex(row, ListOfPieces.parts_list)
         self.assertEqual(parts[row], returned.data(index, Qt.DisplayRole))
      for row in xrange(len(paths)): # offset intervals
         index = ListOfPieces.createIndex(row, ListOfPieces.offset_intervals)
         self.assertEqual([0.5], returned.data(index, Qt.DisplayRole))
      for row in xrange(len(paths)): # parts combinations
         index = ListOfPieces.createIndex(row, ListOfPieces.parts_combinations)
         self.assertEqual([], returned.data(index, Qt.DisplayRole))\
# End TestImportPieces ---------------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
piece_getter_suite = unittest.TestLoader().loadTestsFromTestCase(TestPieceGetter)
part_and_titles_suite = unittest.TestLoader().loadTestsFromTestCase(TestPartsAndTitles)
add_pieces_suite = unittest.TestLoader().loadTestsFromTestCase(TestAddPieces)
remove_pieces_suite = unittest.TestLoader().loadTestsFromTestCase(TestRemovePieces)
import_pieces_suite = unittest.TestLoader().loadTestsFromTestCase(TestImportPieces)
