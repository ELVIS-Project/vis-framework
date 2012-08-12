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
#from PyQt4.QtCore import pyqtSlot, QObject
# music21
# vis
from qt.Ui_main_window import Ui_MainWindow
from vis import VIS_Settings
from vis import Vertical_Interval_Statistics



# Subclass for Signal Handling -------------------------------------------------
class Vis_MainWindow( Ui_MainWindow ):
   
   # Create the settings and statistics objects for vis.
   def setup_vis( self ):
      self.settings = VIS_Settings()
      self.statistics = Vertical_Interval_Statistics()
   
   # Link all the signals with their methods.
   def setup_signals( self ):
      # "Settings" Tab
      self.rdo_heedQuality.clicked.connect( self.settings_interval_quality )
      self.rdo_ignoreQuality.clicked.connect( self.settings_interval_quality )
      self.rdo_compoundIntervals.clicked.connect( self.settings_simple_compound )
      self.rdo_simpleIntervals.clicked.connect( self.settings_simple_compound )
      self.line_n.returnPressed.connect( self.settings_set_n )
      self.btn_setN.clicked.connect( self.settings_set_n )
      self.rdo_yesScore.clicked.connect( self.settings_LilyPond_score )
      self.rdo_noScore.clicked.connect( self.settings_LilyPond_score )
      self.line_intervalOffset.returnPressed.connect( self.settings_offset_interval )
      self.btn_setOffset.clicked.connect( self.settings_offset_interval )
      
      # "Input" Tab
      self.btnAnalyze.clicked.connect( self.analyze_this )
      
      # "Show" Tab
      
   
   # "Settings" Tab ----------------------------------------
   # When users change "Interval Quality"
   def settings_interval_quality( self ):
      if True == self.rdo_heedQuality.isChecked():
         self.settings.set_property( 'heedQuality true' )
      else: # Must be True == self.rdo_ignoreQuality.isChecked()
         self.settings.set_property( 'heedQuality false' )
   
   # When users change "Octaves" (simple/compound intervals)
   def settings_simple_compound( self ):
      if True == self.rdo_compoundIntervals.isChecked():
         self.settings.set_property( 'simpleOrCompound compound' )
      else: # Must be True == self.rdo_simpleIntervals.isChecked()
         self.settings.set_property( 'simpleOrCompound simple' )
   
   # When users choose "Set" for "Which Values of n?"
   def settings_set_n( self ):
      set_this_n = str(self.line_n.text())
      # TODO: see if there are input-checking things to do
      self.settings.set_property( 'lookForTheseNs ' + set_this_n )
   
   # When users choose to produce or not a LilyPond score
   def settings_LilyPond_score( self ):
      if True == self.rdo_yesScore.isChecked():
         self.settings.set_property( 'produceLabeledScore true' )
      else: # Must be True == self.rdo_noScore.isChecked()
         self.settings.set_property( 'produceLabeledScore false' )
   
   # When users change the offset between intervals
   def settings_offset_interval( self ):
      set_offset_interval = str(self.line_intervalOffset.text())
      # TODO: see if there are input-checking things to do
      self.settings.set_property( 'offsetBetweenInterval ' + set_offset_interval )
   
   # "Input" Tab -------------------------------------------
   # When users choose the "Analyze!" button.
   def analyze_this( self, sig ):
      # TODO: write the actual stuff here
      self.txt_results.setPlainText( str(self.settings._secret_settings_hash) )
   
   

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












































