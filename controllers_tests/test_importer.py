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
      path = '../test_converter/bwv77.mxl'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_jos2308_krn(self):
      path = '../test_converter/Jos2308.krn'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_jos2308_mei(self):
      # Because music21 doesn't support MEI, this will not work
      path = '../test_converter/Jos2308.mei'
      self.assertRaises(converter.ConverterFileException,
                        converter.parse,
                        path)
      self.assertRaises(converter.ConverterFileException,
                        Importer._piece_getter,
                        path)

   def test_kyrie(self):
      path = '../test_converter/Kyrie.krn'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_laPlusDesPlus(self):
      path = '../test_converter/laPlusDesPlus.abc'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_madrigal51(self):
      path = '../test_converter/madrigal51.mxl'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_sinfony(self):
      path = '../test_converter/sinfony.md'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)

   def test_sqOp76_4_i(self):
      path = '../test_converter/sqOp76-4-i.midi'
      my_import = converter.parse(path)
      test_import = Importer._piece_getter(path)
      self.assertEqual(my_import, test_import)
# End TestPieceGetter ----------------------------------------------------------



class TestPartsAndTitles(unittest.TestCase):
   # Testing Importer._find_part_names() and Importer._find_piece_title

   def test_bwv77(self):
      path = '../test_converter/bwv77.mxl'
      title = 'bwv77'
      parts = ['Soprano', 'Alto', 'Tenor', 'Bass']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_jos2308_krn(self):
      path = '../test_converter/Jos2308.krn'
      title = 'Jos2308'
      parts = ['spine_3', 'spine_2', 'spine_1', 'spine_0']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_kyrie(self):
      path = '../test_converter/Kyrie.krn'
      title = 'Kyrie'
      parts = ['spine_4', 'spine_3', 'spine_2', 'spine_1', 'spine_0']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_laPlusDesPlus(self):
      path = '../test_converter/laPlusDesPlus.abc'
      title = 'La plus des plus'
      parts = ['68786512', '68784656', '141162896']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_madrigal51(self):
      path = '../test_converter/madrigal51.mxl'
      title = 'madrigal51'
      parts = ['Canto', 'Alto', 'Tenor', 'Quinto', 'Basso', 'Continuo']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_sinfony(self):
      path = '../test_converter/sinfony.md'
      title = 'Messiah'
      parts = ['Violino I', 'Violino II', 'Viola', 'Basssi']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)

   def test_sqOp76_4_i(self):
      path = '../test_converter/sqOp76-4-i.midi'
      title = 'sqOp76-4-i'
      parts = ['118617936', '9674896', '174769616', '197486544']
      the_score = converter.parse(path)
      test_title = Importer._find_piece_title(the_score)
      test_parts = Importer._find_part_names(the_score)
      self.assertEqual(title, test_title)
      self.assertEqual(parts, test_parts)
# End TestImportPieces ---------------------------------------------------------



class TestImportPieces(unittest.TestCase):
   # For the method Importer.import_pieces()

   def test_all_pieces_calling(self):
      pass
      ## Tests importing the whole test corpus through calling and return value
      #paths = ['../test_converter/bwv77.mxl',
               #'../test_converter/Jos2308.krn',
               #'../test_converter/Kyrie.krn',
               #'../test_converter/laPlusDesPlus.abc',
               #'../test_converter/madrigal51.mxl',
               #'../test_converter/sinfony.md',
               #'../test_converter/sqOp76-4-i.midi']
      #control = Importer()
      ## add some pieces
      #returned = control.import_pieces()

      ## (1) Make my "correct" ListOfPieces
      #my_imports = ListOfPieces()
      #my_imports.insertRows(0, len(paths))
      ## add filenames
      #for i in xrange(len(paths)):
         #index = my_imports.createIndex(ListOfPieces.filename, i)
         #my_imports.setData(index, paths[i], Qt.EditRole)
# End TestImportPieces ---------------------------------------------------------



#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------
piece_getter_suite = unittest.TestLoader().loadTestsFromTestCase(TestPieceGetter)
part_and_titles_suite = unittest.TestLoader().loadTestsFromTestCase(TestPartsAndTitles)
import_pieces_suite = unittest.TestLoader().loadTestsFromTestCase(TestImportPieces)
