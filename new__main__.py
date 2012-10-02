#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: __main__.py
# Purpose: Provide the graphical interface for vis.
#
# Attribution:  Based on the 'harrisonHarmony.py' module available at...
#               https://github.com/crantila/harrisonHarmony/
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

# Python
import sys
from os.path import isfile
# PyQt4
from PyQt4 import Qt, QtCore, QtGui
#from PyQt4.QtCore import pyqtSlot, QObject
# music21
# vis
from gui_files.Ui_new_main_window import Ui_MainWindow
from gui_files.Ui_select_voices import Ui_select_voices
from problems import NonsensicalInputError
from Vertical_Interval_Statistics import Vertical_Interval_Statistics

# TEMPORARY
from time import sleep



# Subclass for Signal Handling -------------------------------------------------
class Vis_MainWindow( Ui_MainWindow ):

   # "self" Objects
   #---------------
   # self.analysis_files : a list of pathnames for analysis
   # self.analysis_pieces : a List_of_Pieces object
   # self.lilypond_version_numbers : the 3-tuplet of a LilyPond version
   # self.settings : a VIS_Settings instance
   # self.statistics : a Vertical_Interval_Statistics instance
   # self.targeted_lily_options : options for "targeted LilyPond output"

   # Create the settings and statistics objects for vis.
   def setup_vis( self ):
      self.gui_file_list.setModel( self.analysis_files )
      self.gui_pieces_list.setModel( self.analysis_pieces )
      self.statistics = Vertical_Interval_Statistics()
      # Hold a list of checkboxes that represent the parts in a piece
      self.piece_checkboxes = None

      #self.settings = VIS_Settings()
      
      ## Hold the list of filenames to analyze.
      #self.analysis_files = []
      ## Hold the list of instructions for doing targeted analysis.
      #self.targeted_lily_options = []
      ## Hold a 3-tuplet of the LilyPond version number
      #self.lilypond_version_numbers = None

   # Link all the signals with their methods.
   def setup_signals( self ):
      self.tool_analyze()
      self.btn_choose_files.clicked.connect( self.tool_choose )
      self.btn_about.clicked.connect( self.tool_about )
      self.btn_analyze.clicked.connect( self.tool_analyze )
      self.btn_show.clicked.connect( self.tool_show )
      self.rdo_intervals.clicked.connect( self.choose_intervals )
      self.rdo_ngrams.clicked.connect( self.choose_ngrams )
      self.rdo_targeted_score.clicked.connect( self.choose_targeted_score )
      self.rdo_chart.clicked.connect( self.unchoose_targeted_score )
      self.rdo_score.clicked.connect( self.unchoose_targeted_score )
      self.rdo_list.clicked.connect( self.unchoose_targeted_score )
      self.btn_file_add.clicked.connect( self.add_files )
      self.btn_file_remove.clicked.connect( self.remove_files )
      self.chk_all_voice_combos.stateChanged.connect( self.adjust_bs )
      self.btn_step1.clicked.connect( self.progress_to_assemble )
      self.btn_load_statistics.clicked.connect( self.load_statistics )
      self.gui_pieces_list.clicked.connect( self.update_pieces_selection )
      self.chk_all_voice_combos.clicked.connect( self.all_voice_combos )
      self.chk_basso_seguente.clicked.connect( self.chose_bs )

   # GUI Things (Main Menu Toolbar) ------------------------
   def tool_choose( self ):
      self.main_screen.setCurrentWidget( self.page_choose )
      self.btn_analyze.setEnabled( False )

   def tool_analyze( self ):
      self.main_screen.setCurrentWidget( self.page_analyze )

   def tool_show( self ):
      self.main_screen.setCurrentWidget( self.page_show )

   def tool_about( self ):
      self.main_screen.setCurrentWidget( self.page_about )

   # GUI Things ("Show" Panel) -----------------------------
   def choose_intervals( self ):
      self.groupBox_n.setEnabled( False )
      self.lbl_most_common.setText( 'most common intervals.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude intervals with fewer than' )
      self.rdo_name.setText( 'interval' )

   def choose_ngrams( self ):
      self.groupBox_n.setEnabled( True )
      self.lbl_most_common.setText( 'most common n-grams.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude n-grams with fewer than' )
      self.rdo_name.setText( 'n-gram' )

   def choose_targeted_score( self ):
      self.groupBox_sorted_by.setEnabled( False )
      self.groupBox_sort_order.setEnabled( False )
      self.groupBox_targeted_score.setEnabled( True )

   def unchoose_targeted_score( self ):
      self.groupBox_sorted_by.setEnabled( True )
      self.groupBox_sort_order.setEnabled( True )
      self.groupBox_targeted_score.setEnabled( False )

   # GUI Things ("Choose Files" Panel) ---------------------
   def add_files( self ):
      # Get the list of files to add
      possible_files = QtGui.QFileDialog.getOpenFileNames(\
         None,
         "Choose Files to Analyze",
         '',
         '',
         None)

      # Make sure we don't add files that are already there
      list_of_files = []
      for file in possible_files:
         if not self.analysis_files.alreadyThere( file ):
            list_of_files.append( file )

      # Add the right number of rows to the list
      start_row = self.analysis_files.rowCount()
      self.analysis_files.insertRows( start_row, len(list_of_files), )

      # Add the files to the model
      i = start_row
      for file in list_of_files:
         index = self.analysis_files.createIndex( i, 0 )
         self.analysis_files.setData( index, file, QtCore.Qt.EditRole )
         i += 1
   # End add_files()

   def remove_files( self ):
      # get a list of QModelIndex objects to remove
      to_remove = self.gui_file_list.selectedIndexes()

      # remove them
      for file in to_remove:
         self.analysis_files.removeRows( file.row(), 1 )

   def progress_to_assemble( self ):
      # TODO: finish this

      # finally, move the GUI to the "assemble" panel
      self.btn_analyze.setEnabled( True )
      self.btn_analyze.setChecked( True )
      self.tool_analyze()

   # GUI Things ("Assemble" Panel) -------------------------
   def load_statistics( self ):
      statistics_file = QtGui.QFileDialog.getOpenFileName(\
                        self.centralwidget,\
                        "Choose Statistics File",\
                        "",
                        "JSON Files (*.json)",
                        None)
      if isfile(statistics_file):
         fp = open(statistics_file,"r")
         json_string = fp.read()
         new_vis = None
         try:
            new_vis = Vertical_Interval_Statistics.from_json(json_string)
         except NonsensicalInputError as nie:
            error_dialog = QtGui.QErrorMessage()
            error_dialog.showMessage('The selected statistics file is not valid: '+str(nie))
            error_dialog.exec_()
            return
         self.statistics.extend(new_vis)

   def adjust_bs( self ):
      # Adjusts the "basso seguente" checkbox depending on whether "all
      # combinations" is selected
      if self.chk_all_voice_combos.isChecked():
         self.chk_basso_seguente.setText( 'Every part against Basso Seguente' )
      else:
         self.chk_basso_seguente.setText( 'Basso Seguente' )

   def all_voice_combos( self ):
      # Are we enabling "all" or disabling?
      if self.chk_all_voice_combos.isChecked():
         # Enabling
         # Are there specific part names? If so, disable those checkboxes
         if self.piece_checkboxes is not None:
            for box in self.piece_checkboxes:
               box.setEnabled( False )
         # Update the QLineEdit, then update the selected pieces
         self.line_compare_these_parts.setText( 'all' )
         # TODO: update the selected pieces
      else:
         # Disabling
         # Are there specific part names? If so, enable those checkboxes
         if self.piece_checkboxes is not None:
            for box in self.piece_checkboxes:
               box.setEnabled( True )
         # Update the QLineEdit, then update the selected pieces
         self.line_compare_these_parts.setText( 'e.g., [0,3] or [[0,3],[1,3]]' )
         # TODO: update the selected pieces
   
   def chose_bs( self ):
      # When somebody chooses the "basso seguente" checkbox, if "all" is also
      # selected, we should update the QLineEdit
      if self.chk_all_voice_combos.isChecked():
         if self.chk_basso_seguente.isChecked():
            self.line_compare_these_parts.setText( '[all,bs]' )
            # TODO: update the selected pieces
         else:
            self.line_compare_these_parts.setText( 'all' )
            # TODO: update the selected pieces
   
   def update_pieces_selection( self ):
      # TODO: finish the other things for this method
      # When the user changes the piece(s) selected in self.gui_pieces_list
      
      # Which piece is/pieces are selected?
      currently_selected = self.gui_pieces_list.selectedIndexes()
      
      # NB: we get a list of all the cells selected, and this is definitely done
      # in rows, so because each row has 6 things, if we have 6 cells, it means
      # we have only one row... but more than 6 cells means more than one row
      if len(currently_selected) == 0:
         # (1) Enable all the controls
         self.line_values_of_n.setEnabled( False )
         self.line_offset_interval.setEnabled( False )
         self.btn_choose_note.setEnabled( False )
         self.line_compare_these_parts.setEnabled( False )
         self.chk_all_voice_combos.setEnabled( False )
         self.chk_basso_seguente.setEnabled( False )
         self.btn_add_check_combo.setEnabled( False )
         # (2) Remove the part list
         if self.piece_checkboxes is not None:
            for part in self.piece_checkboxes:
               self.verticalLayout_22.removeWidget( part )
            self.piece_checkboxes = None
      elif len(currently_selected) > 6:
         # Multiple pieces selected... can't customize for it
         # (1) Enable all the controls
         self.line_values_of_n.setEnabled( True )
         self.line_offset_interval.setEnabled( True )
         self.btn_choose_note.setEnabled( True )
         self.line_compare_these_parts.setEnabled( True )
         self.chk_all_voice_combos.setEnabled( True )
         self.chk_basso_seguente.setEnabled( True )
         self.btn_add_check_combo.setEnabled( True )
         # (2) Remove the part list
         if self.piece_checkboxes is not None:
            for part in self.piece_checkboxes:
               self.verticalLayout_22.removeWidget( part )
            self.piece_checkboxes = None
      else:
         # Only one piece... customize for it
         # (1) Enable all the controls
         self.line_values_of_n.setEnabled( True )
         self.line_offset_interval.setEnabled( True )
         self.btn_choose_note.setEnabled( True )
         self.line_compare_these_parts.setEnabled( True )
         self.chk_all_voice_combos.setEnabled( True )
         self.chk_basso_seguente.setEnabled( True )
         self.btn_add_check_combo.setEnabled( True )
         # (2) Populate the part list
         # (2a) Remove previous items from the layout
         if self.piece_checkboxes is not None:
            for part in self.piece_checkboxes:
               self.verticalLayout_22.removeWidget( part )
            self.piece_checkboxes = None
         # (2b) Get the list of parts
         list_of_parts = None
         for cell in currently_selected:
            if 2 == cell.column():
               list_of_parts = self.analysis_pieces.data( cell, \
                                                          QtCore.Qt.DisplayRole )
               break
         # (2c) Put up a checkbox for each part
         self.piece_checkboxes = []
         for part_name in list_of_parts:
            # n_c_b means "new check box"
            n_c_b = QtGui.QCheckBox( self.widget_5 )
            n_c_b.setObjectName( "chk_" + part_name )
            n_c_b.setText( part_name )
            self.piece_checkboxes.append( n_c_b )
         # (2d) Add all the widgets to the layout
         for part in self.piece_checkboxes:
            self.verticalLayout_22.addWidget( part )

# Model for "Choose Files" Panel -----------------------------------------------
class List_of_Files( QtCore.QAbstractListModel ):
   def __init__( self, parent=None, *args ):
      QtCore.QAbstractListModel.__init__(self, parent, *args)
      self.files = []

   def rowCount( self, parent=QtCore.QModelIndex() ):
      return len( self.files )

   def data(self, index, role):
      if index.isValid() and QtCore.Qt.DisplayRole == role:
         return QtCore.QVariant( self.files[index.row()] )
      else:
         return QtCore.QVariant()

   # NB: I *should* implement these, but I don't know how, so for now I won't
   #def headerData( self ):
      #pass

   #def flags():
      #pass

   def setData( self, index, value, role ):
      if QtCore.Qt.EditRole == role:
         self.files[index.row()] = value
         self.dataChanged.emit( index, index )
         return True
      else:
         return False

   def insertRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginInsertRows( parent, row, row+count )
      new_files = self.files[:row]
      for zed in xrange( count ):
         new_files.append( '' )
      new_files += self.files[row:]
      self.files = new_files
      self.endInsertRows()

   def alreadyThere( self, candidate ):
      '''
      Tests whether 'candidate' is already present in this list of files.
      '''
      return candidate in self.files

   def removeRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginRemoveRows( parent, row, row )
      self.files = self.files[:row] + self.files[row+count:]
      self.endRemoveRows()
# End Class List_of_Files ------------------------------------------------------



# Model for "Assemble" Panel -----------------------------------------------
class List_of_Pieces( QtCore.QAbstractTableModel ):
   # Here's the data model:
   # self.pieces : a list of lists. For each sub-list...
   #    sublist[0] : filename
   #    sublist[1] : piece name, if available, or ''
   #    sublist[2] : list of part names, if available, or a list of '' for each part
   #    sublist[3] : offset interval
   #    sublist[4] : n as a str
   #    sublist[5] : the "compare these parts" str

   def __init__( self, parent=QtCore.QModelIndex() ):
      QtCore.QAbstractTableModel.__init__( self, parent )
      #self.pieces = []
      self.pieces = [['/home/asdf.ly','Symphony',['S','A','T','B'],0.5,'2','all bs'], \
                     ['/home/dd.midi','Chorale',['violin','tuba'],0.5,'2,3','0 1']]

   def rowCount( self, parent=QtCore.QModelIndex() ):
      return len(self.pieces)

   def columnCount( self, parent=QtCore.QModelIndex() ):
      # There are 6 columns (see "data model" above)
      return 6

   def data(self, index, role):
      if index.isValid() and QtCore.Qt.DisplayRole == role:
         return self.pieces[index.row()][index.column()]
         #if 2 == index.column():
            ## TODO: make this nicer... formatting part names
            #return str(self.pieces[index.row()][2])[1:-1]
         #else:
            #return QtCore.QVariant( self.pieces[index.row()][index.column()] )
      else:
         return QtCore.QVariant()

   def headerData( self, section, orientation, role ):
      # TODO: why this no work?
      header_names = ['Path', 'Title', 'List of Part Names', 'Offset', 'n', \
                      'Compare These Parts']

      if QtCore.Qt.Horizontal == orientation:
         return header_names[section]
      else:
         return None

   def setData( self, index, value, role ):
      # NB: use this pattern
      # index = self.analysis_pieces.createIndex( 0, 1 )
      # self.analysis_pieces.setData( index, 'ballz', QtCore.Qt.EditRole )
      if QtCore.Qt.EditRole == role:
         self.pieces[index.row()][index.column()] = value
         self.dataChanged.emit( index, index )
         return True
      else:
         return False

   #def insertRows( self, row, count, parent=QtCore.QModelIndex() ):
      ## TODO: ballz
      #self.beginInsertRows( parent, row, row+count )
      #new_files = self.files[:row]
      #for zed in xrange( count ):
         #new_files.append( '' )
      #new_files += self.files[row:]
      #self.files = new_files
      #self.endInsertRows()

   #def removeRows( self, row, count, parent=QtCore.QModelIndex() ):
      ## TODO: ballz
      #self.beginRemoveRows( parent, row, row )
      #self.files = self.files[:row] + self.files[row+count:]
      #self.endRemoveRows()
# End Class List_of_Pieces ------------------------------------------------------



# "Main" Method ----------------------------------------------------------------
def main():
   # Standard stuff
   app = QtGui.QApplication( sys.argv )
   MainWindow = QtGui.QMainWindow()
   vis_ui = Vis_MainWindow()
   vis_ui.setupUi( MainWindow )
   # vis stuff
   vis_ui.analysis_files = List_of_Files( vis_ui.gui_file_list )
   vis_ui.analysis_pieces = List_of_Pieces( vis_ui.gui_pieces_list )
   vis_ui.setup_vis()
   vis_ui.setup_signals()
   vis_ui.tool_choose()
   # Standard stuff
   MainWindow.show()
   sys.exit( app.exec_() )

if __name__ == '__main__':
   main()
