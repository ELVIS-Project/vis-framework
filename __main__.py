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
from os import path
from os import walk as os_walk
# PyQt4
from PyQt4 import QtGui
#from PyQt4.QtCore import pyqtSlot, QObject
# music21
from music21 import converter # for analyze_this()
from music21.converter import ConverterException # for analyze_this()
from music21.converter import ConverterFileException # for analyze_this()
# vis
from qt.Ui_main_window import Ui_MainWindow
from vis import VIS_Settings
from vis import Vertical_Interval_Statistics
from analytic_engine import vis_these_parts



# Subclass for Signal Handling -------------------------------------------------
class Vis_MainWindow( Ui_MainWindow ):
   
   # Create the settings and statistics objects for vis.
   def setup_vis( self ):
      self.settings = VIS_Settings()
      self.statistics = Vertical_Interval_Statistics()
      self.analysis_files = [] # Hold the list of filenames to analyze.
   
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
      self.btn_analyze.clicked.connect( self.analyze_button )
      self.btn_chooseFiles.clicked.connect( self.choose_files )
      self.btn_chooseDirectories.clicked.connect( self.choose_directories )
      
      # "Show" Tab
      self.score_slider.sliderMoved.connect( self.adjust_slider )
      self.btn_auto_n.clicked.connect( self.auto_fill_n )
   
   
   
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
   def analyze_button( self, sig ):
      # Update the text box on the "input" tab
      self.txt_filenames.setPlainText( 'Will analyze these files:\n' + str(self.analysis_files) + '\n\nProgress:\n' )
      # Call analyze_this()
      self.analyze_this()
   
   # When users choose the "Choose Files" button.
   def choose_files( self, sig ):
      list_of_files = QtGui.QFileDialog.getOpenFileNames( None, 'Choose Files to Analyze', '~', '*.pdf' )
      processed_str = ''
      self.analysis_files = []
      for each in list_of_files:
         processed_str += str(each) + '\n'
         self.analysis_files.append( str(each) )
      self.txt_filenames.setPlainText( processed_str )
   
   # When users choose the "Choose Directories" button.
   def choose_directories( self, sig ):
      direc = QtGui.QFileDialog.getExistingDirectory( None, 'Choose Directory to Analyze', '~' )
      self.analysis_files = [ direc ]
      self.txt_filenames.setPlainText( str(direc) )
   
   # "Show" Tab --------------------------------------------
   def adjust_slider( self, n ):
      # For fun...
      self.score_progress.setValue( n )
   
   # "Cardinalities" -------------------
   def auto_fill_n( self ):
      self.line_show_triangles_n.setText( str(self.settings.get_property( 'lookForTheseNs' )) )
   
   
   
   
   
   
   
   
   #----------------------------------------------------------------------------
   def analyze_this( self ):
      '''
      Analyze a list of files and directories. Statistics will be added to, and
      settings will be used from, the "self" object. The list of files should
      also be specified in "self" as self.analysis_files as a list of str
      pathnames. This method will analyze all single files in that list, and
      all files in a directory in that list, but will not recurse further.
      
      '''
      #-------------------------------------------------------
      def calculate_all_combis( upto ):
         # Calculate all combinations of integers, up to a given integer.
         # 
         # Includes a 0th item... the argument should be len(whatevs) - 1.
         post = []
         for left in xrange(upto):
            for right in xrange(left+1,upto+1):
               post.append( [left,right] )
         return post
      #-------------------------------------------------------
      
      # Prepare the list of files. Go through every element and see if it's a
      # directory. If so, bring out all the filenames to the top-level list.
      corrected_file_list = []
      for pathname in self.analysis_files:
         if path.isdir( pathname ):
            # TODO: something tells me this doesn't do what I had in mind
            for a, b, filename in os_walk( pathname ):
               corrected_file_list.append( filename )
         else:
            corrected_file_list.append( pathname )
      # Finally, replace analysis_files with corrected_file_list
      self.analysis_files = corrected_file_list
      
      # Hold a list of pieces that failed during analysis.
      files_not_analyzed = []
      
      # Accumulate the length of time spent in vis_these_parts()
      cumulative_analysis_duration = 0.0
      
      # Hold a list of parts to analyze.
      parts_to_analyze = []
      
      # Go through all the files/directories.
      for piece_name in self.analysis_files:
         # Figure out which parts to analyze.
         #parts_to_examine = list(set([int(n) for n in re.findall('(-?\d+)', parts_to_examine)]))
         parts_to_examine = 'all'
         
         # Hold this score
         the_score = None
         
         # Try to open this file
         self.txt_filenames.appendPlainText( 'Trying "' + piece_name + '"' )
         try:
            the_score = converter.parse( piece_name )
         except ConverterException as convexc:
            self.txt_filenames.appendPlainText( '   failed during import' )
            self.txt_filenames.appendPlainText( str(convexc) )
            files_not_analyzed.append( piece_name )
            continue
         except ConverterFileException as convfileexc:
            self.txt_filenames.appendPlainText( '   failed during import' )
            self.txt_filenames.appendPlainText( str(convfileexc) )
            files_not_analyzed.append( piece_name )
            continue
         except Exception as exc:
            self.txt_filenames.appendPlainText( '   failed during import' )
            self.txt_filenames.appendPlainText( str(exc) )
            files_not_analyzed.append( piece_name )
            continue
         else:
            self.txt_filenames.appendPlainText( '   successfully imported' )
         
         # Try to analyze this file
         try:
            if 'all' == parts_to_examine:
               # We have to examine all combinations of parts.
               # How many parts are in this piece?
               number_of_parts = len(the_score.parts)
               # Get a list of all the part-combinations to examine.
               parts_to_examine = calculate_all_combis( number_of_parts - 1 )
               # "Zero" it_took
               it_took = 0.0
               # Analyze every part combination.
               for set_of_parts in parts_to_examine:
                  higher = the_score.parts[set_of_parts[0]]
                  lower = the_score.parts[set_of_parts[1]]
                  this_took, ly = vis_these_parts( [higher,lower], self.settings, self.statistics )
                  it_took += this_took
               # Add this duration to the cumulative duration.
               cumulative_analysis_duration += it_took
               # Print how long it took
               self.txt_filenames.appendPlainText( '   finished in ' + str(it_took) )
            else:
               # We should only examine the specified parts.
               # Get the two parts.
               higher = the_score.parts[parts_to_examine[0]]
               lower = the_score.parts[parts_to_examine[1]]
               # Run the analysis
               it_took, ly = vis_these_parts( [higher,lower], self.settings, self.statistics )
               # Add this duration to the cumulative duration.
               cumulative_analysis_duration += it_took
               # Print this duration.
               self.txt_filenames.appendPlainText( '   finished in ' + str(it_took) )
            
            # Now do the LilyPond portion, if needed.
            if True == self.settings.get_property( 'produceLabelledScore' ):
               # Add the annotated part to the score
               the_score.append( ly )
               # Send the score for processing
               process_score( the_score )
               # TODO: decide how to dynamically decide filename, then move this into
               # a sub-section of the "show" command in the "main" method.
         # If something fails, we don't want the entire analysis to fail, but
         # we do need to tell our user.
         except Exception as exc:
            self.txt_filenames.appendPlainText( '   failed during analysis' )
            self.txt_filenames.appendPlainText( str(exc) )
            files_not_analyzed.append( piece_name )
            continue
         
      # Print how long the analysis took.
      self.txt_filenames.appendPlainText( '\n\n --> the analysis took ' + str(cumulative_analysis_duration) + ' seconds' )
      
      # If there are files we were asked to analyze, but we couldn't,
      # then say so.
      if len(files_not_analyzed) > 0:
         self.txt_filenames.appendPlainText( '*** Unable to analyze the following files:' )
         for filename in files_not_analyzed:
            pass
            self.txt_filenames.appendPlainText( filename )
      
      # TODO: remove this temporary thing
      # just print out the interval dictionary, so I know it worked
      self.txt_results.setPlainText( str( self.statistics._simple_interval_dict ) )
   # End function analyze_this() ---------------------------------------------------




























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












































