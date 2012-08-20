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
import re
# PyQt4
from PyQt4 import QtGui
from PyQt4 import Qt
#from PyQt4.QtCore import pyqtSlot, QObject
# music21
from music21 import converter # for analyze_this()
from music21.converter import ConverterException # for analyze_this()
from music21.converter import ConverterFileException # for analyze_this()
# vis
from qt.Ui_main_window import Ui_MainWindow
from qt.Ui_select_voices import Ui_select_voices
from vis import VIS_Settings
from vis import Vertical_Interval_Statistics
from analytic_engine import vis_these_parts
from problems import MissingInformationError
from file_output import file_outputter, file_inputter
from output_LilyPond import process_score as lily_process_score



# Subclass for Signal Handling -------------------------------------------------
class Vis_MainWindow( Ui_MainWindow ):
   
   # Create the settings and statistics objects for vis.
   def setup_vis( self ):
      self.settings = VIS_Settings()
      self.statistics = Vertical_Interval_Statistics()
      # Hold the list of filenames to analyze.
      self.analysis_files = []
      # Hold the list of instructions for doing targeted analysis.
      self.targeted_lily_options = []
   
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
      self.rdo_choose_every_file.toggled.connect( self.settings_file_choose )
      
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
      self.btn_targeted_add_black.clicked.connect( self.targeted_add_black )
      self.btn_targeted_add_colour.clicked.connect( self.targeted_add_colour )
      self.btn_targeted_colour_choose.clicked.connect( self.targeted_colour_choose )
      self.btn_targeted_colour_clear.clicked.connect( self.targeted_colour_clear )
      self.btn_targeted_choose_score.clicked.connect( self.targeted_choose_score )
      self.btn_targeted_produce.clicked.connect( self.targeted_produce )
   
   
   
   # "Settings" Tab ----------------------------------------
   # When users change "How to Choose Voices to Analyze"
   def settings_file_choose( self, choose_once ):
      if choose_once:
         self.settings.set_property( 'howToChooseVoices once' )
      else:
         self.settings.set_property( 'howToChooseVoices independently' )
   
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
   
   # When users change "How to Choose Voices to Analyze"
   def settings_choose_voices( self ):
      if True == self.rdo_choose_every_file.isChecked():
         self.settings.set_property( 'howToChooseVoices independently' )
      else: # Must be True == self.rdo_choose_just_once.isChecked()
         self.settings.set_property( 'howToChooseVoices once' )
   
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
      
      if 'once' == self.settings.get_property( 'howToChooseVoices' ):
         self.rdo_choose_every_file.setChecked( False )
         self.rdo_choose_just_once.setChecked( True )
         # DEBUG
         self.txt_filenames.setPlainText( 'choose once' )
         # END DEBUG
      else:
         self.rdo_choose_every_file.setChecked( True )
         self.rdo_choose_just_once.setChecked( False )
         # DEBUG
         self.txt_filenames.setPlainText( 'choose each' )
         # END DEBUG
      
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
      
      file_outputter( self.settings.export_settings(), filename, 'OVERWRITE' )
   
   # "Input" Tab -------------------------------------------
   # When users choose the "Analyze!" button.
   def analyze_button( self, sig ):
      # Update the text box on the "input" tab
      self.txt_filenames.setPlainText( 'Will analyze these files:\n' + str(self.analysis_files) + '\n\nProgress:\n' )
      # Call analyze_this()
      self.analyze_this()
      #self.analyze_this( [['these parts', [0, 3]], \
                         #['only annotate', '10 -2 10'], \
                         #['only colour', '12 +4 8'], \
                         #['annotate colour', '#red']] )
   
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
   
   # btn_targeted_add_black
   def targeted_add_black( self ):
      # Take the contents of the QLineEdit and append to the list of instructions
      self.targeted_lily_options.append( ['only annotate', \
                                          str(self.line_targeted_add_black.text())] )
      self.update_targeted_output_window()
      self.line_targeted_add_black.setText('')
   
   # btn_targeted_add_colour
   def targeted_add_colour( self ):
      # Take the contents of the QLineEdit and append to the list of
      # instructions. Coloured ngrams must be added to both lists.
      the_ngram = str(self.line_targeted_add_colour.text())
      self.targeted_lily_options.append( ['only colour', the_ngram] )
      self.targeted_lily_options.append( ['only annotate', the_ngram] )
      self.update_targeted_output_window()
      self.line_targeted_add_colour.setText('')
   
   # btn_targeted_colour_choose
   def targeted_colour_choose( self ):
      # Get the colour the user wants.
      user_colour = QtGui.QColorDialog.getColor()

      # Now make the str with the colour name
      new_colour = '#(rgb-color '
      new_colour += str(user_colour.red()) + ' '
      new_colour += str(user_colour.green()) + ' '
      new_colour += str(user_colour.blue()) + ')'
      
      # See if there's already a spot for colour and use it.
      for instr in self.targeted_lily_options:
         if 'annotate colour' == instr[0]:
            instr[1] = new_colour
      
      # Otherwise, we'll have to add a new instruction.
      self.targeted_lily_options.append( ['annotate colour', new_colour] )
      
      self.update_targeted_output_window()
   
   # btn_targeted_colour_clear
   def targeted_colour_clear( self ):
      # Go through the list of instructions; if there's a colour, remove it.
      for instr in self.targeted_lily_options:
         if 'annotate colour' == instr[0]:
            instr[1] = None
      self.update_targeted_output_window()
   
   # btn_targeted_choose_score
   def targeted_choose_score( self ):
      # Choose the file
      the_file = QtGui.QFileDialog.getOpenFileName( None, 'Choose Files to Analyze', '~', '*.pdf *.mxl *.krn *.abc *.mei' )
      # We'll store it in here, even though I think I may regret it later.
      # TODO: see if you regret this
      self.analysis_files = [str(the_file)]
   
   # btn_targeted_produce
   def targeted_produce( self ):
      # Start up the analysis engine!
      
      # To avoid mistakes, in cases where users select a colour but don't put
      # any ngrams in the "to colour" list. If there are no "only colour"
      # instructions, we'll remove the colour.
      for instr in self.targeted_lily_options:
         if 'only colour' == instr[0]:
            break
      else:
         self.targeted_colour_clear()
      
      # We have to make sure the "produceLabeledScore" option is enabled.
      if not self.settings.get_property( 'produceLabeledScore' ):
         self.settings.set_property( 'produceLabeledScore true' )
         self.analyze_this( self.targeted_lily_options )
         self.settings.set_property( 'produceLabeledScore false' )
      else:
         self.analyze_this( self.targeted_lily_options )
   
   
   
   #----------------------------------------------------------------------------
   def update_targeted_output_window( self ):
      '''
      This method updates the self.txt_results widget, formatting and showing
      contents of the instructions from the "Targeted LilyPond Output" tab.
      '''
      self.txt_results.setPlainText( str(self.targeted_lily_options) )
   
   
   
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
   def analyze_this( self, targeted_output = None ):
      '''
      Analyze a list of files and directories. Statistics will be added to, and
      settings will be used from, the "self" object. The list of files should
      also be specified in "self" as self.analysis_files as a list of str
      pathnames. This method analyzes all single files in that list, or all
      files in directories (and their subdirectories) in that list.
      
      The argument, targeted_output, is a list of instructions for creating a
      purpose-built LilyPond score. Each instruction is a list with a str and
      the value, if any. You could have:
      ['these parts', [int, int]]
      ['only annotate', '3 1 3'] (the second element is a str == str(NGram) that you want to annotate; you can include many)
      ['only colour', '3 1 3'] (the second element is a str == str(NGram) that you want to colour; you can include many; others remain #black)
      ['annotate colour', '#blue'] (the second element is a str that is the name of the colour you want)
         - #blue for "Normal colors"
         - #(x11-color 'DarkRed) for "X color names"
         - for a list of colours: http://lilypond.org/doc/v2.14/Documentation/notation/list-of-colors
      
      NB: If you do not specify only_annotate or only_colour, all annotations appear, and the colour is #black
      NB: If you specify annotate_colour without only_colour, all annotations appear, and the colour is annotate_colour
      NB: All annotations in only_colour should also appear in only_annotate.
      NB: All annotations in only_annotate but not only_colour will appear, but with the colour #black
      
      Therefore, if you want parts 0 and 3, and both '3 1 3' and '3 1 4' to be
      annotated, but only '3 1 4' with the colour #darkred, you would do this:
      >>> analyze_this( [['these parts', [0, 3], \
                         ['only annotate', '3 1 3'], \
                         ['only colour', '3 1 4'], \
                         ['annotate colour', '#darkred']] )
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
      
      # Hold the list of parts to examine. Must be here because targeted_output
      # may contain instructions.
      parts_to_examine = None
      
      # Go through all the instructions
      if targeted_output is not None:
         # Do we have instructions on which voices to analyze? This is
         # actually the only instruction we need in this method. Everything
         # else will be passed onto vis_these_parts()
         for instruction in targeted_output:
            if 'these parts' == instruction[0]:
               parts_to_examine = instruction[1]
      # End parsing of targeted_output ---------------------
      
      # How do we choose voices?
      how_to_choose = self.settings.get_property( 'howToChooseVoices' )
      
      # If we only choose once, let's do it now.
      if 'once' == how_to_choose and parts_to_examine is None:
         part_finder = Vis_Select_Voices()
         parts_to_examine = part_finder.trigger()
      
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
         
         # If necessary, figure out which parts to analyze.
         if 'independently' == how_to_choose and parts_to_examine is None:
            # Find out the available part names
            available_parts = []
            i = 0
            for part in the_score.parts:
               instr = part.getInstrument()
               if instr is None:
                  available_parts.append( str(i) )
               else:
                  available_parts.append( instr.bestName() )
               i += 1
            # Display the QDialog
            part_finder = Vis_Select_Voices()
            parts_to_examine = part_finder.trigger( available_parts )
         
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
                  this_took, ly = vis_these_parts( [higher,lower], \
                                                   self.settings, \
                                                   self.statistics, \
                                                   targeted_output )
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
               it_took, ly = vis_these_parts( [higher,lower], \
                                              self.settings, \
                                              self.statistics, \
                                              targeted_output )
               # Add this duration to the cumulative duration.
               cumulative_analysis_duration += it_took
               # Print this duration.
               self.txt_filenames.appendPlainText( '   finished in ' + str(it_took) )
            
            # Now do the LilyPond portion, if needed.
            if True == self.settings.get_property( 'produceLabelledScore' ):
               # Add the annotated part to the score
               the_score.append( ly )
               # Send the score for processing
               lily_process_score( the_score )
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
#-------------------------------------------------------------------------------



class Vis_Select_Voices( Ui_select_voices ):
   
   # self._chk_voice : a list of the "part" selection checkboxes
   
   def trigger( self, list_of_parts = [] ):
      '''
      Causes the "Select Voices to Analyze" window to be shown. The argument
      should be a list. If the list is empty, we'll hide the portion of the
      window that lists specific parts. Otherwise the list should contain many
      str objects that specify the name of the part in the score associated with
      that index value.
      
      For example, for a SATB piece, the list will be:
      ['Soprano', 'Alto', 'Tenor', 'Bass']
      The 'Soprano' part should be found in score.parts[0], the 'Alto' part in
      score.parts[1], and so on.
      
      The return value is either a two-element list of int, the str 'all', or
      a two-element list of int and the str 'bs' (for "basso seguente"). This
      is the user's choice of parts.
      
      For example:
      >>> which_parts = Vis_Select_Voices()
      >>> result = which_parts.trigger( ['oboe', 'cello', 'tuba'] )
      >>> # The user chooses which parts
      >>> print( str(result) )
      [0, 2]
      '''
      
      # UI setup stuff
      self.select_voices = QtGui.QDialog()
      self.v_s_v = Vis_Select_Voices()
      self.v_s_v.setupUi( self.select_voices )
      
      # Is there no list of parts?
      if 0 == len(list_of_parts):
         # Hide the specific-part-choosing stuff
         self.v_s_v.rdo_choose_these.hide()
         self.v_s_v.chk_voice_0.hide()
      else:
         # Display the names of the parts in the checkboxes, creating new
         # checkboxes as required. The first part/checkbox is already there.
         self.v_s_v.chk_voice_0.setText( list_of_parts[0] )
         self.v_s_v.chk_voice_0.setEnabled( False )
         self.chk_voice = [self.v_s_v.chk_voice_0]
         i = 1
         for part_name in list_of_parts[1:]:
            # Make a new checkbox
            self.chk_voice.append( QtGui.QCheckBox(self.v_s_v.widget_8) )
            self.chk_voice[i].setObjectName("chk_voice_" + str(i))
            self.v_s_v.verticalLayout_3.addWidget(self.chk_voice[i])
            self.chk_voice[i].setText( list_of_parts[i] )
            self.chk_voice[i].setEnabled( False )
            i += 1
      
      # Final UI setup
      self.setup_signals()
      self.select_voices.exec_()
      
      # ... and our user chooses...
      
      # Now we have to find out what they did and return it.
      if self.v_s_v.rdo_all.isChecked():
         # "Compare all part combinations"
         return 'all'
      elif self.v_s_v.rdo_these_parts.isChecked():
         # "Compare these parts"
         parts_to_examine = self.v_s_v.line_these_parts.text()
         parts_to_examine = list(set([int(n) for n in re.findall('(-?\d+)', parts_to_examine)]))
         return parts_to_examine[:2]
      elif self.v_s_v.rdo_part_and_bs.isChecked():
         # "Compare this part with basso seguente"
         part_to_examine = self.v_s_v.line_part_and_bs.text()
         part_to_examine = list(set([int(n) for n in re.findall('(-?\d+)', part_to_examine)]))
         part_to_examine = part_to_examine[:1]
         part_to_examine.append( 'bs' )
         return part_to_examine
      else:
         # "Choose two specific voices"
         # TODO: yell if there are fewer or greater than 2 voices selected
         post = []
         for i in xrange(len(self.chk_voice)):
            if self.chk_voice[i].isChecked():
               post.append( i )
         return post
   
   # Link all the signals with their methods.
   def setup_signals( self ):
      # "Settings" Tab
      self.v_s_v.rdo_choose_these.toggled.connect( self.able_checks )
      self.v_s_v.rdo_these_parts.toggled.connect( self.compare_radio )
      self.v_s_v.rdo_part_and_bs.toggled.connect( self.bs_radio )
      self.v_s_v.btn_continue.clicked.connect( self.continue_button )
   
   # When users enable or disable "Choose two specific voices"
   def able_checks( self, state ):
      # If the radio button is enabled, we're going to enable the checkboxes;
      # if the   '    '     is disabled, we're going to disable the checkboxes.
      
      # Go through each checkbox and apply the correct state to it.
      for box in self.chk_voice:
         box.setEnabled( state )
   
   # When users enable or disable "Compare these parts"
   def compare_radio( self, state ):
      # If the radio button is enabled, we're going to enable the QLineEdit;
      # if the   '    '     is disabled, we're going to disable the QLineEdit.
      self.v_s_v.line_these_parts.setEnabled( state )
   
   # When users enable or disable "Compare this part with basso seguente"
   def bs_radio( self, state ):
      # If the radio button is enabled, we're going to enable the QLineEdit;
      # if the   '    '     is disabled, we're going to disable the QLineEdit.
      self.v_s_v.line_part_and_bs.setEnabled( state )
   
   # When users choose "Continue"
   def continue_button( self ):
      self.select_voices.accept()
#-------------------------------------------------------------------------------



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
