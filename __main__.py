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
from string import replace as str_replace
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
from problems import MissingInformationError
from file_output import file_outputter, file_inputter



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
      self.btn_save_settings.clicked.connect( self.settings_save )
      self.btn_load_settings.clicked.connect( self.settings_load )
      
      # "Input" Tab
      self.btn_analyze.clicked.connect( self.analyze_button )
      self.btn_chooseFiles.clicked.connect( self.choose_files )
      self.btn_chooseDirectories.clicked.connect( self.choose_directories )
      
      # "Show" Tab
      self.score_slider.sliderMoved.connect( self.adjust_slider )
      self.btn_auto_n.clicked.connect( self.auto_fill_n )
      self.btn_show_intervals.clicked.connect( self.show_intervals )
      self.btn_save_intervals.clicked.connect( self.save_intervals )
      self.btn_show_triangles.clicked.connect( self.show_triangles )
      self.btn_save_triangles.clicked.connect( self.save_triangles )
   
   
   
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
   
   # When users choose "Load" settings
   def settings_load( self ):
      filename = str(QtGui.QFileDialog.getOpenFileName(\
         None,
         "Load Which Settings File?",
         "vis_settings.txt",
         '',
         None))
      
      self.settings.import_settings( file_inputter( filename ) )
      
      # Now we also have to update the interface
      self.line_intervalOffset.setText( str(self.settings.get_property( 'offsetBetweenInterval' )) )
      self.line_n.setText( str(self.settings.get_property( 'lookForTheseNs' )) )
      
      if self.settings.get_property( 'heedQuality' ):
         self.rdo_heedQuality.setChecked( True )
         self.rdo_ignoreQuality.setChecked( False )
      else:
         self.rdo_ignoreQuality.setChecked( True )
         self.rdo_heedQuality.setChecked( False )
      
      if 'compound' == self.settings.get_property( 'simpleOrCompound' ):
         self.rdo_compoundIntervals.setChecked( True )
         self.rdo_simpleIntervals.setChecked( False )
      else:
         self.rdo_compoundIntervals.setChecked( False )
         self.rdo_simpleIntervals.setChecked( True )
      
      if self.settings.get_property( 'produceLabeledScore' ):
         self.rdo_yesScore.setChecked( True )
         self.rdo_noScore.setChecked( False )
      else:
         self.rdo_yesScore.setChecked( False )
         self.rdo_noScore.setChecked( True )
   # End settings_load()
   
   # When users choose "Save" settings
   def settings_save( self ):
      filename = str(QtGui.QFileDialog.getSaveFileName(\
         None,
         "Save Settings Where?",
         "vis_settings.txt",
         '',
         None))#,
         #QtGui.QFileDialog.Options(QtGui.QFileDialog.ConfirmOverwrite)))
      
      file_outputter( self.settings.export_settings(), filename )
   
   # "Input" Tab -------------------------------------------
   # When users choose the "Analyze!" button.
   def analyze_button( self, sig ):
      # Update the text box on the "input" tab
      self.txt_filenames.setPlainText( 'Will analyze these files:\n' + str(self.analysis_files) + '\n\nProgress:\n' )
      # Call analyze_this()
      self.analyze_this()
   
   # When users choose the "Choose Files" button.
   def choose_files( self, sig ):
	  # this should refer to some global constants involving which filenames we can use
      list_of_files = QtGui.QFileDialog.getOpenFileNames( None, 'Choose Files to Analyze', '~', '*.pdf *.mxl *.krn *.abc *.mei' )
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
   
   # When users choose "Show" for triangles
   def show_triangles( self, zoop ):
      self.show_specs_getter( 'ngram' )
   
   # When users choose "Show" for intervals
   def show_intervals( self, zoop ):
      self.show_specs_getter( 'interval' )
   
   # When users choose "Save" for triangles
   def save_triangles( self, zoop ):
      self.show_specs_getter( 'ngram file' )
   
   # When users choose "Save" for intervals
   def save_intervals( self, zoop ):
      self.show_specs_getter( 'interval file' )
   
   # "Cardinalities"
   def auto_fill_n( self ):
      self.line_show_triangles_n.setText( str(self.settings.get_property( 'lookForTheseNs' )) )
   
   
   
   
   #----------------------------------------------------------------------------
   def show_specs_getter( self, grob ):
      '''
      Given a str that contains either 'ngram' or 'interval' and optionally
      'file', this method finds the settings of the appropriate "Show" sub-tab,
      then call show_results() with the correct settings.
      '''
      post = grob
      
      # This method merely gets the settings, but doesn't do anything with them.
      
      if 'ngram' in post:
         # Check settings on the "Show"/"Triangles" tab
         # Sort Order
         if self.rdo_ascending_triangles.isChecked():
            post += ' ascending '
         else:
            post += ' descending '
         
         # Sort Object
         if self.rdo_ngrams_by_ngram.isChecked():
            post += ' by ngram '
         else:
            post += ' by frequency '
         
         # Graph
         if self.chk_graph_triangles.isChecked():
            post += ' graph '
         
         # n
         # We must remove any spaces in this box, because spaces are later
         # unerstood as the termination of the string
         enns = str(self.line_show_triangles_n.text())
         enns = str_replace( enns, ' ', '' )
         enns = str_replace( enns, '[', '' )
         enns = str_replace( enns, ']', '' )
         post += ' n=' + enns + ' '
         
      elif 'interval' in post:
         # Check settings on the "Show"/"Intervals" tab
         # Sort Order
         if self.rdo_ascending_intervals.isChecked():
            post += ' ascending '
         else:
            post += ' descending '
         
         # Sort Object
         if self.rdo_intervals_by_interval.isChecked():
            post += ' by interval '
         else:
            post += ' by frequency '
         
         # Graph
         if self.chk_graph_intervals.isChecked():
            post += ' graph '
      
      # Call show_results() to actually display things.
      # We'll try to catch exceptions and alert our user intelligently.
      # TODO: remove this debugging print()
      print( post )
      try:
         self.show_results( post )
      except MissingInformationError as mie:
         QtGui.QMessageBox.warning(None,
            "Yikes!",
            str(mie),
            QtGui.QMessageBox.StandardButtons(\
               QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)
   
   
   
   #----------------------------------------------------------------------------
   def show_results( self, specs ):
      '''
      Show the results of an analysis query. The argument should be a string
      that specifies what to show and how to show it. You must include the
      following components
      - 'ngram' or 'interval' : whether to display results of n-grams or
         intervals
      - 'by interval' or 'by ngram' or 'by frequency' : whether to sort results
         by discovered-thing or by the number of them
      - ('ascending' or 'low to high') or ('descending' or 'high to low') :
         which direction to sort results
      - 'graph' : to produce a chart rather than a list
      - 'file' : to output results to a file rather than the screen
      - 'n=XX' : for ngrams, to specify which values of n to show
      
      If you send the 'graph' option, the 'file' option is ignored.
      
      If you send the 'file' option, a 'Save As' dialogue window appears.
      '''
      
      # NB: I broke this apart for modularity, but I'm not sure we need it.
      
      # Hold the str we'll output.
      results = None
      
      # First, format the results.
      if 'ngram' in specs:
         # output ngrams
         results = self.statistics.get_formatted_ngrams( self.settings, specs )
      else:
         # output intervals
         results = self.statistics.get_formatted_intervals( self.settings, specs )
      
      # Second, deal with results output to a file.
      if 'file' in specs:
         # Get the file name to which to save results.
         output_filename = QtGui.QFileDialog.getSaveFileName(\
            None,
            "Save Results",
            '',
            '',
            None)
         
         # Use the file_output module's utility method.
         output_results = file_outputter( results, output_filename, 'OVERWRITE' )
         
         # If there's a str as the second element, there was an error.
         if isinstance( output_results[1], str ):
            self.txt_results.appendPlainText( 'Error during output:' )
            self.txt_results.appendPlainText( output_results[1] )
         else:
            self.txt_results.appendPlainText( 'Results outputted to ' + \
                                              output_filename[0] )
      # Third, deal with results shown in the window.
      else:
         self.txt_results.setPlainText( str(results)  )
   
   
   
   #----------------------------------------------------------------------------
   def analyze_this( self ):
      '''
      Analyze a list of files and directories. Statistics will be added to, and
      settings will be used from, the "self" object. The list of files should
      also be specified in "self" as self.analysis_files as a list of str
      pathnames. This method analyzes all single files in that list, or all
      files in directories (and their subdirectories) in that list. 
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
         # TODO: figure this out
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












































