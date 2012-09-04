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
# PyQt4
from PyQt4 import QtGui
from PyQt4 import Qt
#from PyQt4.QtCore import pyqtSlot, QObject
# music21
# vis
from qt.Ui_new_main_window import Ui_MainWindow
from qt.Ui_select_voices import Ui_select_voices

# TEMPORARY
from time import sleep



# Subclass for Signal Handling -------------------------------------------------
class Vis_MainWindow( Ui_MainWindow ):

   # "self" Objects
   #---------------
   # self.analysis_files : a list of pathnames for analysis
   # self.lilypond_version_numbers : the 3-tuplet of a LilyPond version
   # self.settings : a VIS_Settings instance
   # self.statistics : a Vertical_Interval_Statistics instance
   # self.targeted_lily_options : options for "targeted LilyPond output"

   # Create the settings and statistics objects for vis.
   def setup_vis( self ):
      pass
      #self.settings = VIS_Settings()
      #self.statistics = Vertical_Interval_Statistics()
      ## Hold the list of filenames to analyze.
      #self.analysis_files = []
      ## Hold the list of instructions for doing targeted analysis.
      #self.targeted_lily_options = []
      ## Hold a 3-tuplet of the LilyPond version number
      #self.lilypond_version_numbers = None

   # Link all the signals with their methods.
   def setup_signals( self ):
      self.tool_analyze()
      self.btn_about.clicked.connect( self.tool_about )
      self.btn_analyze.clicked.connect( self.tool_analyze )
      self.btn_show.clicked.connect( self.tool_show )
      self.btn_settings.clicked.connect( self.tool_settings )
      self.btn_files_analyze.clicked.connect( self.main_screen_working )
      self.btn_show_results.clicked.connect( self.main_screen_working_2 )
      self.rdo_intervals.clicked.connect( self.choose_intervals )
      self.rdo_ngrams.clicked.connect( self.choose_ngrams )
      self.rdo_targeted_score.clicked.connect( self.choose_targeted_score )
      self.rdo_chart.clicked.connect( self.unchoose_targeted_score )
      self.rdo_score.clicked.connect( self.unchoose_targeted_score )
      self.rdo_list.clicked.connect( self.unchoose_targeted_score )

   # Main Menu Toolbar
   def tool_analyze( self ):
      self.main_screen.setCurrentWidget( self.page_analyze )

   def tool_show( self ):
      self.main_screen.setCurrentWidget( self.page_show )

   def tool_settings( self ):
      self.main_screen.setCurrentWidget( self.page_settings )

   def tool_about( self ):
      self.main_screen.setCurrentWidget( self.page_about )

   # Show "working" screen --- TEMPORARY for demonstration
   def main_screen_working( self ):
      self.main_screen.setCurrentWidget( self.page_working )
      for i in xrange(101):
         sleep( 0.1 )
         self.progress_bar.setValue( i )
      self.btn_show.setChecked( True )
      self.tool_show()

   # Show "working" screen --- TEMPORARY for demonstration
   def main_screen_working_2( self ):
      self.progress_bar.setValue( 21 )
      self.main_screen.setCurrentWidget( self.page_working )
      for i in xrange(22,60):
         sleep( 0.1 )
         self.progress_bar.setValue( i )
      for i in xrange(60,45,-1):
         sleep( 0.05 )
         self.progress_bar.setValue( i )
      for i in xrange(45,101):
         sleep( 0.025 )
         self.progress_bar.setValue( i )
      self.btn_show.setChecked( True )
      self.tool_show()

   def choose_intervals( self ):
      self.groupBox_n.setEnabled( False )
      self.lbl_most_common.setText( 'most common intervals.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude intervals with fewer than' )
      self.rdo_name.setText( 'interval' )

   def choose_ngrams( self ):
      self.groupBox_n.setEnabled( True )
      self.lbl_most_common.setText( 'most common triangles.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude triangles with fewer than' )
      self.rdo_name.setText( 'triangle' )

   def choose_targeted_score( self ):
      self.groupBox_sorted_by.setEnabled( False )
      self.groupBox_sort_order.setEnabled( False )
      self.groupBox_targeted_score.setEnabled( True )

   def unchoose_targeted_score( self ):
      self.groupBox_sorted_by.setEnabled( True )
      self.groupBox_sort_order.setEnabled( True )
      self.groupBox_targeted_score.setEnabled( False )

# "Main" Method ----------------------------------------------------------------
def main():
   # Standard stuff
   app = QtGui.QApplication( sys.argv )
   MainWindow = QtGui.QMainWindow()
   vis_ui = Vis_MainWindow()
   vis_ui.setupUi( MainWindow )
   # vis stuff
   vis_ui.setup_vis()
   vis_ui.setup_signals()
   # Standard stuff
   MainWindow.show()
   sys.exit( app.exec_() )

if __name__ == "__main__":
   main()
