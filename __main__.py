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
from os.path import isfile, join, splitext
from os import walk
from itertools import chain
import re
import time
import pickle
# PyQt4
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThreadPool
from PyQt4.QtCore import pyqtSignal, QObject
# music21
from music21 import converter, graph, metadata, instrument
from music21.converter import ConverterException, ConverterFileException
# vis
from problems import NonsensicalInputWarning
from gui_files.Ui_compare_voice_pairs import Ui_Compare_Voice_Pairs
from gui_files.Ui_select_offset import Ui_Select_Offset
from gui_files.Ui_new_main_window import Ui_MainWindow
from gui_files.Ui_text_display import Ui_Text_Display
from problems import NonsensicalInputError, MissingInformationError
from Vertical_Interval_Statistics import Vertical_Interval_Statistics
from VIS_Settings import VIS_Settings
from analytic_engine import vis_these_parts, make_basso_seguente
from file_output import file_outputter
from output_LilyPond import LilyPond_Settings, make_lily_version_numbers, \
   detect_lilypond
from output_LilyPond import process_score as lily_process_score



# Subclass for Signal Handling -------------------------------------------------
class Vis_MainWindow( Ui_MainWindow ):

   # Create the settings and statistics objects for vis.
   def setup_vis( self ):
      self.gui_file_list.setModel( self.analysis_files )
      self.gui_pieces_list.setModel( self.analysis_pieces )
      self.statistics = Vertical_Interval_Statistics()
      self.settings = VIS_Settings()
      # Hold a lists of checkboxes, "Edit" buttons, and layouts that represent
      # the parts in a piece for the "assemble" panel
      self.part_checkboxes = None
      self.edit_buttons = None
      self.part_layouts = None
      # number of voice pairs analyzed so far
      self.pairs_so_far = 0
      # total number of voice pairs being analyzed
      self.total_pairs = 0
      # the time.time() when the analysis was started
      self.analysis_start_time = 0.0
      # a list of pathnames of files currently loaded
      self.loaded_files = []
      # Holds the signal emitted when a QRunnable finishes a voice pair
      self.vsc = Vis_Signals_Class()
      # Holds a list of instructions for producing targeted LilyPond output
      self.targeted_lily_options = []
      # Holds the version number of LilyPond installed on this system
      self.lilypond_version_numbers = None

      # These be the index values for columns in the list-of-pieces model.
      self.model_filename = 0 # filename of the piece
      self.model_score = 1 # Score object and title
      self.model_parts_list = 2 # list of names of parts
      self.model_offset = 3 # offset Duration between vertical intervals
      self.model_n = 4 # values of "n" to find
      self.model_compare_parts = 5 # list of two-element lists of part indices

   # Link all the signals with their methods.
   def setup_signals( self ):
      self.tool_analyze()
      self.btn_choose_files.clicked.connect( self.tool_choose )
      self.btn_about.clicked.connect( self.tool_about )
      self.btn_analyze.clicked.connect( self.tool_analyze )
      self.btn_show.clicked.connect( self.tool_show )
      self.btn_show_results.clicked.connect( self.show_results )
      self.rdo_intervals.clicked.connect( self.choose_intervals )
      self.rdo_ngrams.clicked.connect( self.choose_ngrams )
      self.rdo_compare.clicked.connect( self.choose_compare )
      self.rdo_targeted_score.clicked.connect( self.update_output_format )
      self.rdo_chart.clicked.connect( self.update_output_format )
      self.rdo_score.clicked.connect( self.update_output_format )
      self.rdo_list.clicked.connect( self.update_output_format )
      self.line_show_these_ns.editingFinished.connect( self.update_n_values_displayed )
      self.rdo_compound.clicked.connect( self.update_simple_compound )
      self.rdo_simple.clicked.connect( self.update_simple_compound )
      self.rdo_heedQuality.clicked.connect( self.update_heed_quality )
      self.rdo_noHeedQuality.clicked.connect( self.update_heed_quality )
      self.rdo_frequency.clicked.connect( self.update_sorted_by )
      self.rdo_name.clicked.connect( self.update_sorted_by )
      self.rdo_ascending.clicked.connect( self.update_sort_order )
      self.rdo_descending.clicked.connect( self.update_sort_order )
      self.btn_dir_add.clicked.connect( self.add_dir )
      self.btn_file_add.clicked.connect( self.get_files )
      self.btn_file_remove.clicked.connect( self.remove_files )
      self.chk_all_voice_combos.stateChanged.connect( self.adjust_bs )
      self.btn_step1.clicked.connect( self.progress_to_assemble )
      self.btn_load_statistics.clicked.connect( self.load_statistics )
      self.gui_pieces_list.clicked.connect( self.update_pieces_selection )
      self.chk_all_voice_combos.clicked.connect( self.all_voice_combos )
      self.chk_basso_seguente.clicked.connect( self.chose_bs )
      self.btn_add_check_combo.clicked.connect( self.add_parts_combination )
      self.line_compare_these_parts.editingFinished.connect( self.add_parts_combo_by_lineEdit )
      self.line_values_of_n.editingFinished.connect( self.update_values_of_n )
      self.line_offset_interval.editingFinished.connect( self.update_offset_interval )
      self.btn_choose_note.clicked.connect( self.launch_offset_selection )
      self.btn_step2.clicked.connect( self.progress_to_show )
      self.line_piece_title.editingFinished.connect( self.update_piece_title )
      self.line_output_most_common.editingFinished.connect( self.update_most_common )
      self.line_threshold.editingFinished.connect( self.update_threshold )
      self.line_ngram_in_colour.editingFinished.connect( self.targeted_add_colour ) # TODO
      self.line_ngram_in_black.editingFinished.connect( self.targeted_add_black ) # TODO
      self.btn_targeted_choose_colour.clicked.connect( self.targeted_colour_choose ) # TODO
      # This is for the QThreadPool threads to signal they've finished a
      # voice pair
      self.vsc.finishedVoicePair.connect( self.increment_analysis_progress )

   # GUI Things (Main Menu Toolbar) ------------------------
   def tool_choose( self ):
      self.main_screen.setCurrentWidget( self.page_choose )
      self.btn_analyze.setEnabled( False )
      self.btn_show.setEnabled( False )
      self.btn_step2.setEnabled( False )

   def tool_analyze( self ):
      self.main_screen.setCurrentWidget( self.page_analyze )

   def tool_working( self ):
      self.main_screen.setCurrentWidget( self.page_working )
      self.app.processEvents()

   def tool_show( self ):
      self.main_screen.setCurrentWidget( self.page_show )

   def tool_about( self ):
      self.main_screen.setCurrentWidget( self.page_about )

   # GUI Things ("Show" Panel) -----------------------------
   def generate_summary_score( self ):
      # This is the one where we have to make a score. Must set the formatting
      # options correctly for LilyPond!

      # Get a settings instance
      l_sets = LilyPond_Settings()

      # Set all the settings
      # - no indent
      # - no bar numbers
      l_sets.set_property( 'indent', '0\cm' )
      l_sets.set_property( 'bar numbers', "#'#(#f #f #f)" )

      # Make the score
      summary_score = self.statistics.make_summary_score( self.settings )

      # Ask where to save the LilyPond file
      out_file = str(QtGui.QFileDialog.getSaveFileName(\
         None,
         "Save LilyPond File Where?",
         "Statistics Summary.ly",
         '',
         None))

      # Pass the score to output_LilyPond for processing.
      lily_process_score( summary_score, the_settings=l_sets, filename=out_file )
   # End generate_summary_score() --------------------------



   def update_targeted_output_window( self ):
      self.txt_targeted_score.setPlainText( str(self.targeted_lily_options) )



   def targeted_add_black( self ):
      '''
      When the user finishes editing the "Annotate this n-gram in black" box
      '''

      # Get the contents of the QLineEdit
      the_ngram = str(self.line_ngram_in_black.text())

      # Should we bother adding it? Then do
      if '' != the_ngram:
         self.targeted_lily_options.append( ['only annotate', the_ngram] )
         self.update_targeted_output_window()
         self.line_ngram_in_black.setText('')



   def targeted_add_colour( self ):
      '''
      When the user finishes editing the "Annotate this n-gram in colour" box
      '''

      # Get the contents of the QLineEdit
      the_ngram = str(self.line_ngram_in_colour.text())

      # Should we bother adding it? Then do
      if '' != the_ngram:
         self.targeted_lily_options.append( ['only colour', the_ngram] )
         self.targeted_lily_options.append( ['only annotate', the_ngram] )
         self.update_targeted_output_window()
         self.line_ngram_in_colour.setText('')



   def targeted_colour_choose( self ):
      '''
      When the user wants to choose a colour in which to annotate some n-grams.
      '''

      # Get the colour the user wants.
      user_colour = QtGui.QColorDialog.getColor()

      # We need to know our LilyPond version.
      if self.lilypond_version_numbers is None:
         l_v = detect_lilypond()[1]
         self.lilypond_version_numbers = make_lily_version_numbers( l_v )

      # Make the str with the colour name
      if 2 == self.lilypond_version_numbers[0] and \
      14 >= self.lilypond_version_numbers[1]:
         # If LilyPond 2.14.x or older
         new_colour = '#(rgb-color '
         new_colour += str(user_colour.red()) + ' '
         new_colour += str(user_colour.green()) + ' '
         new_colour += str(user_colour.blue()) + ')'

      elif 2 == self.lilypond_version_numbers[0] and \
      16 <= self.lilypond_version_numbers[1]:
         # If LilyPond 2.16.x and newer?
         new_colour = '#(rgb-color '
         new_colour += str( float(user_colour.red()) / 255.0 ) + ' '
         new_colour += str( float(user_colour.green()) / 255.0 ) + ' '
         new_colour += str( float(user_colour.blue()) / 255.0 ) + ')'
      else:
         # If something else (3.x, 1.x, or 2.15.x)
         msg = 'Cannot use LilyPond 2.15.x with colours; please upgrade to 2.16.0 or downgrade to 2.14.2'
         raise IncompatibleSetupError( msg )

      # See if there's already a spot for colour, then use it
      for instr in self.targeted_lily_options:
         if 'annotate colour' == instr[0]:
            instr[1] = new_colour

      # Otherwise, we'll have to add a new instruction
      self.targeted_lily_options.append( ['annotate colour', new_colour] )

      self.update_targeted_output_window()
   # End targeted_colour_choose() --------------------------



   def generate_targeted_score( self ):
      '''
      Called by show_results() when we need to generate an annotated score
      with LilyPond.
      '''

      # First warn the user that vis will be unresponsive
      QtGui.QMessageBox.information(None,
         'Attention',
         """vis will not respond to input until annotation is complete!""",
         QtGui.QMessageBox.StandardButtons(\
            QtGui.QMessageBox.Ok),
         QtGui.QMessageBox.Ok)

      # Collect "jobs" for the QThreadPool
      jobs = []

      # There should only be one piece, but for ease-of-use and similarity with
      # the regular analysis thing, we'll use a loop here.
      for i, piece in enumerate( list(self.analysis_pieces.iterate_rows()), \
                                 start=0 ):
         # Find the name of this piece
         this_piece_name = None
         if piece[self.model_score].metadata is None:
            this_piece_name = 'asdf!'
         else:
            this_piece_name = piece[self.model_score].metadata.title

         # Prepare the multi-threading part
         job = Vis_Analyze_Piece()
         job.setup( piece, self, this_piece_name, \
                    targeted_output=self.targeted_lily_options )

         # Append this job to the list of jobs to calculate
         jobs.append( job )

      # Set this very high so that vis won't interfere with the end of analysis
      self.total_pairs = 5000

      # Schedule the jobs with QThreadPool
      for job in jobs:
         QThreadPool.globalInstance().start( job )

      # Wait for the jobs to finish
      QThreadPool.globalInstance().waitForDone()
   # End generate_targeted_score() -------------------------



   def show_results( self ):
      # For LilyPond, we'll have an "early interception"
      if 'score' == self.settings.get_property( 'outputFormat' ):
         self.generate_summary_score()
         return
      elif 'targeted score' == self.settings.get_property( 'outputFormat' ):
         self.generate_targeted_score()
         return

      # Should we output intervals or ngrams or comparison?
      content = self.settings.get_property( 'content' )

      # Hold the output
      formatted_output = None

      # Get the output
      try:
         if 'ngrams' == content:
            formatted_output = self.statistics.get_formatted_ngrams( self.settings )
         elif 'intervals' == content:
            formatted_output = self.statistics.get_formatted_intervals( self.settings )
         elif 'compare' == content:
            dialog = Vis_Compare_Voice_Pairs(self)
            v1,v2 = dialog.get_pairs()
            formatted_output = "dummy output"
      except NonsensicalInputWarning as niw:
         QtGui.QMessageBox.warning(None,
            "Cannot Display Results",
            str(niw),
            QtGui.QMessageBox.StandardButtons(\
               QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)
         return None

      # Display the output
      if isinstance( formatted_output, basestring ):
         # If in "list"
         dialog = Vis_Text_Display(formatted_output)
         dialog.trigger()
      elif isinstance( formatted_output, graph.Graph ):
         # If in "chart/graph"
         formatted_output.show()
      else:
         # array of graphs
         for g in formatted_output:
            g.show()
   # End show_results() ------------------------------------

   def choose_intervals( self ):
      self.groupBox_n.setEnabled( False )
      self.settings.set_property('content intervals')
      self.lbl_most_common.setText( 'most common intervals.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude intervals with fewer than' )
      self.rdo_name.setText( 'interval' )



   def choose_ngrams( self ):
      self.groupBox_n.setEnabled( True )
      self.settings.set_property('content ngrams')
      self.lbl_most_common.setText( 'most common n-grams.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude n-grams with fewer than' )
      self.rdo_name.setText( 'n-gram' )



   def choose_compare( self ):
      self.settings.set_property('content compare')
      self.lbl_most_common.setText( 'most common n-grams.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude n-grams with fewer than' )
      self.rdo_name.setText( 'n-gram' )



   def update_output_format( self ):
      if self.rdo_targeted_score.isChecked():
         self.choose_targeted_score()
         self.settings.set_property('outputFormat', 'targeted score')
      else:
         self.unchoose_targeted_score()
         if self.rdo_score.isChecked():
            self.settings.set_property('outputFormat', 'score')
         elif self.rdo_list.isChecked():
            self.settings.set_property('outputFormat', 'list')
         elif self.rdo_chart.isChecked():
            self.settings.set_property('outputFormat', 'graph')



   def choose_targeted_score( self ):
      '''
      When "targeted score" is selected as an output format, this method enables
      or disables things appropriately.
      '''

      self.groupBox_sorted_by.setEnabled( False )
      self.groupBox_sort_order.setEnabled( False )
      self.groupBox_targeted_score.setEnabled( True )
      # these things will eventually work
      self.line_output_most_common.setEnabled( False )
      self.line_threshold.setEnabled( False )
      self.groupBox_octaves.setEnabled( False )
      self.groupBox_quality.setEnabled( False )



   def unchoose_targeted_score( self ):
      '''
      When "targeted score" is selected as an output format, this method enables
      or disables things appropriately.
      '''

      self.groupBox_sorted_by.setEnabled( True )
      self.groupBox_sort_order.setEnabled( True )
      self.groupBox_targeted_score.setEnabled( False )
      # these things will eventually work
      self.line_output_most_common.setEnabled( True )
      self.line_threshold.setEnabled( True )
      self.groupBox_octaves.setEnabled( True )
      self.groupBox_quality.setEnabled( True )



   def update_n_values_displayed( self ):
      s = str(self.line_show_these_ns.text())
      self.settings.set_property('showTheseNs '+s)



   def update_simple_compound( self ):
      if self.rdo_compound.isChecked():
         self.settings.set_property('simpleOrCompound compound')
      else:
         self.settings.set_property('simpleOrCompound simple')



   def update_heed_quality( self ):
      if self.rdo_heedQuality.isChecked():
         self.settings.set_property('heedQuality true')
      else:
         self.settings.set_property('heedQuality false')



   def update_sorted_by( self ):
      if self.rdo_frequency.isChecked():
         self.settings.set_property('sortBy frequency')
      else:
         self.settings.set_property('sortBy name')



   def update_sort_order( self ):
      if self.rdo_descending.isChecked():
         self.settings.set_property('sortOrder descending')
      else:
         self.settings.set_property('sortOrder ascending')



   def update_most_common( self ):
      '''
      Updates the VIS_Settings object with the proper setting for "topX"
      '''

      # Get the possible X
      candidate_X = str(self.line_output_most_common.text())

      # Does it turn into an int?
      try:
         candidate_X = int(candidate_X)
      except ValueError:
         # If not, we'll just use "None"
         candidate_X = None

      # Then set it!
      self.settings.set_property( 'topX', candidate_X )


   def update_threshold( self ):
      '''
      Updates the VIS_Settings object with the proper setting for "threshold"
      '''

      # Get the possible threshold
      candidate_thresh = str(self.line_threshold.text())

      # Does it turn into an int?
      try:
         candidate_thresh = int(candidate_thresh)
      except ValueError:
         # If not, we'll just use "None"
         candidate_thresh = None

      # Then set it!
      self.settings.set_property( 'threshold', candidate_thresh )



   # GUI Things ("Choose Files" Panel) ---------------------
   def add_dir( self ):
      d = QtGui.QFileDialog.getExistingDirectory(\
          None,
          "Choose Directory to Analyze",
          '',
          QtGui.QFileDialog.ShowDirsOnly)
      d = str(d)
      extensions = ['.nwc.', '.mid','.midi','.mxl','.krn','.xml','.md']
      possible_files = chain(*[[join(path,fp) for fp in files if
                              splitext(fp)[1] in extensions]
                             for path,names,files in walk(d)])
      self.add_files(possible_files)



   def get_files( self ):
      # Get the list of files to add
      possible_files = QtGui.QFileDialog.getOpenFileNames(\
         None,
         "Choose Files to Analyze",
         '',
         '*.nwc *.mid *.midi *.mxl *.krn *.xml *.md',
         None)
      self.add_files(possible_files)



   def add_files( self, possible_files ):
      # Make sure we don't add files that are already there
      list_of_files = [fp for fp in possible_files if
                       not self.analysis_files.alreadyThere(fp)]

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
      # Move the GUI to the "working" panel by loading the pieces in the files
      # list and putting their metadata into the pieces list.

      # Make sure there are some files to load
      if 0 == self.analysis_files.rowCount():
         # Display a QMessageBox that we won't continue unless we have things
         QtGui.QMessageBox.warning(None,
            "Cannot Continue without Files",
            """Please select some symbolic music notation files to process.""",
            QtGui.QMessageBox.StandardButtons(\
               QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)
      else:
         self.btn_step1.setChecked( True )

         # Hold a list of files that don't work
         failed_files = []

         # Move the GUI to the "working" panel and update the GUI
         self.tool_working()
         self.progress_bar.setMinimum( 0 )
         self.progress_bar.setMaximum( self.analysis_files.rowCount() )

         # Go through all the pieces and try to import them
         for i, pathname in enumerate( list(self.analysis_files.iterator()), \
                                       start = 1 ):
            # Update the GUI's label of what piece we're on
            self.lbl_currently_processing.setText( "Importing " + pathname + \
                                                   "..." )
            self.progress_bar.setValue( i )
            self.app.processEvents()

            # Prepare and run the import thread
            thread = Vis_Load_Piece()
            thread.setup( pathname, self )
            thread.start()
            thread.wait()
            if thread.error is not None:
               failed_files.append( thread.error )

         # finally, move the GUI to the "assemble" panel
         self.btn_analyze.setEnabled( True )
         self.btn_analyze.setChecked( True )
         self.tool_analyze()

         # Enable the arrow to move to the "Show" panel
         self.btn_step2.setEnabled( True )

         # Return the "processing" label to its default value
         self.lbl_currently_processing.setText( '(processing)' )

         self.btn_step1.setChecked( False )

         self.update_piece_settings_visibility( False )
   # End progress_to_assemble() ----------------------------



   def progress_to_show( self ):
      '''
      Analyze a list of files and directories, supplementing with statistics
      from any Vertical_Interval_Statistics objects if relevant.

      Settings, files, directories, and stats will be used from the "self"
      object.
      '''

      self.btn_step2.setChecked( True )

      # Prepare the progress_bar
      self.progress_bar.setMinimum( 0 )
      self.progress_bar.setMaximum( 0 )
      self.progress_bar.setValue( 0 )
      self.lbl_currently_processing.setText( 'NB: The progress bar is the most important thing.' )

      # Move to the "working"/"please wait" panel
      self.tool_working()
      self.app.processEvents()

      # Hold a list of pieces that failed during analysis.
      #files_not_analyzed = []

      # Accumulate the length of time spent in vis_these_parts()
      self.analysis_start_time = time.time()

      # Increase the maximum number of threads, so the GUI doesn't sit around
      # occupying a core for itself the whole time.
      QThreadPool.globalInstance().setMaxThreadCount( QThreadPool.globalInstance().maxThreadCount() + 1 )

      # Collect the total number of voice pairs to be analyzed
      total_nr_of_voice_pairs = 0

      # Collect "jobs" for the QThreadPool
      jobs = []

      # Iterate all the files
      for i, piece in enumerate( list(self.analysis_pieces.iterate_rows()), start=0 ):
         # Find the name of this piece
         this_piece_name = None
         if piece[self.model_score].metadata is None:
            this_piece_name = 'asdf!'
         else:
            this_piece_name = piece[self.model_score].metadata.title

         # Prepare the multi-threading part
         job = Vis_Analyze_Piece()
         total_nr_of_voice_pairs += job.setup( piece, self, this_piece_name )

         # Make sure this piece has some parts selected
         if 1 > total_nr_of_voice_pairs:
            # For now at least, we'll stop the process and free all the memory
            # and warn the user what happened
            jobs = None
            QtGui.QMessageBox.warning(None,
               "You Must Choose Voice Pairs",
               """Please select at least one voice pair for analysis in every piece.""",
               QtGui.QMessageBox.StandardButtons(\
                  QtGui.QMessageBox.Ok))
            # Return to the "working/assemble" panel
            self.tool_analyze()
            # Return from this method
            return

         # Connect the job's voice-pair-completion signal
         #job.finishedVoicePair.connect( self.increment_analysis_progress )

         # Append this job to the list of jobs to calculate
         jobs.append( job )
      # (end of pieces loop)

      # Account for the number of voice pairs
      self.progress_bar.setMaximum( total_nr_of_voice_pairs )
      self.total_pairs = total_nr_of_voice_pairs

      # Schedule the jobs with QThreadPool
      for job in jobs:
         QThreadPool.globalInstance().start( job )
   # End function progress_to_show() -------------------------------------------



   @QtCore.pyqtSlot()
   def increment_analysis_progress( self ):
      '''
      Marks one voice pair as complete, then checks whether that means all the
      voice pairs are complete. If so, moves the GUI to the "show" panel.
      '''

      # Increment the number of voice pairs so far calculated
      self.pairs_so_far += 1
      self.progress_bar.setValue( self.pairs_so_far )
      self.app.processEvents()

      # Are we finished?
      if self.pairs_so_far == self.total_pairs:
         # Wait for all the threads to finish. This shouldn't really be
         # necessary, but I'm adding this to try to deal with Issue #96.
         QThreadPool.globalInstance().waitForDone()

         # Calculate and display how long the analysis took
         duration = round( time.time() - self.analysis_start_time, 2 )
         self.statusbar.showMessage( 'Everything analyzed in ' + \
                                     str(duration) + \
                                     ' seconds', 10000 )

         # If there is more than one piece, disable the "Annotated Score" output
         if 1 < self.analysis_pieces.rowCount():
            self.rdo_targeted_score.setEnabled( False )
         else:
            self.rdo_targeted_score.setEnabled( True )

         # Move the GUI to the "show results" panel
         self.main_screen.setCurrentWidget( self.page_show )
         self.btn_show.setEnabled( True )
         self.btn_show.setChecked( True )
         self.btn_step2.setChecked( False )

         # Disable the file-selection panel and the arrows to "progress" from
         # one stage of an analysis to the next. At this point, if somebody
         # wants different pieces in the analysis, they must restart.
         self.btn_choose_files.setEnabled( False )
         self.btn_step1.setEnabled( False )
         self.btn_step2.setEnabled( False )
   # End increment_analysis_progress() ---------------------



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
         except (NonsensicalInputError, MissingInformationError) as e:
            error_dialog = QtGui.QErrorMessage()
            error_dialog.showMessage('The selected statistics file is not valid: '+str(e))
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
         if self.part_checkboxes is not None:
            for box in self.part_checkboxes:
               box.setEnabled( False )

         self.btn_add_check_combo.setEnabled( False )
         part_spec = '[all]'
      else:
         # Disabling
         # Are there specific part names? If so, enable those checkboxes
         if self.part_checkboxes is not None:
            for box in self.part_checkboxes:
               box.setEnabled( True )

         self.btn_add_check_combo.setEnabled( True )
         part_spec = '(no selection)'

      self.update_parts_selection( part_spec )



   def chose_bs( self ):
      # When somebody chooses the "basso seguente" checkbox, if "all" is also
      # selected, we should update the QLineEdit
      if self.chk_all_voice_combos.isChecked():
         if self.chk_basso_seguente.isChecked():
            part_spec = '[all,bs]'
         else:
            part_spec = '[all]'

         self.update_parts_selection( part_spec )



   def update_piece_title( self ):
      '''
      When users change the piece title on the "assemble" panel.
      '''
      # Which piece is/pieces are selected?
      currently_selected = self.gui_pieces_list.selectedIndexes()

      # Find the piece title and update it
      for cell in currently_selected:
         if self.model_score == cell.column():
            # This is a little tricky, because we'll change the Score object's
            # Metadata object directly

            # Get the Score
            piece = self.analysis_pieces.data( cell, 'raw_list' ).toPyObject()

            # Make sure there's a Metadata object
            if piece.metadata is None:
               piece.insert( metadata.Metadata() )

            # Update the title
            piece.metadata.title = str(self.line_piece_title.text())



   def add_parts_combination( self ):
      '''
      When users choose the "Add Combination" button to add the currently
      selected part combination to the list of parts to analyze.
      '''

      # If there are no named parts, we can't do this
      if self.part_checkboxes is None:
         return None

      # Hold indices of the selected checkboxes
      selected_checkboxes = [i for i,cb in enumerate(self.part_checkboxes)
                             if cb.isChecked()]

      # Hold the vis-format specification
      vis_format = None

      # How many checkboxes are selected?
      if 1 == len(selected_checkboxes):
         # If we have one checkbox and bs, okay
         if self.chk_basso_seguente.isChecked():
            vis_format = '[' + str(selected_checkboxes[0]) + ',bs]'
         # Otherwise, complain
         else:
            QtGui.QMessageBox.warning(None,
               "Unusable Part Selection",
               "Please select two parts at a time.",
               QtGui.QMessageBox.StandardButtons(\
                  QtGui.QMessageBox.Ok),
               QtGui.QMessageBox.Ok)
      elif 2 == len(selected_checkboxes):
         # Is "basso seguente" also selected?
         if self.chk_basso_seguente.isChecked():
            # That's not good
            QtGui.QMessageBox.warning(None,
               "Cannot Add Part",
               "When you choose \"basso seguente,\" you can only choose one other part.",
               QtGui.QMessageBox.StandardButtons(\
                  QtGui.QMessageBox.Ok),
               QtGui.QMessageBox.Ok)
         else:
            # We have two parts; choose them.
            vis_format = '[' + str(selected_checkboxes[0]) + ',' + \
                               str(selected_checkboxes[1]) + ']'
      else:
         # Greater or fewer than two parts?
         QtGui.QMessageBox.warning(None,
            "Unusable Part Selection",
            "Please select two parts at a time.",
            QtGui.QMessageBox.StandardButtons(\
               QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)

      # Now update the lists
      if vis_format is not None:
         # Hold the new part-combinations specification
         new_spec = ''

         # What's the current specification?
         curr_spec = str(self.line_compare_these_parts.text())

         # Is curr_spec the default filler?
         if 'e.g., [0,3] or [[0,3],[1,3]]' == curr_spec or \
            '(no selection)' == curr_spec or \
            '' == curr_spec:
            # Then just make a new one
            new_spec = '[' + vis_format + ']'

            # Update the parts selection
            self.update_parts_selection( new_spec )
         # Does curr_spec contain vis_format?
         elif vis_format in curr_spec:
            pass
         # Else we must add this new thing
         else:
            # Otherwise, we should remove the final ']' in the list, and put
            # our new combo on the end
            new_spec = curr_spec[:-1] + ',' + vis_format + ']'

            # Update the parts selection
            self.update_parts_selection( new_spec )

      # Also clear the part-selection checkboxes
      self.chk_basso_seguente.setChecked( False )
      for box in self.part_checkboxes:
         box.setChecked( False )
   # End add_parts_combination() ---------------------------



   def add_parts_combo_by_lineEdit( self ):
      # TODO: input validation using QValidator

      # For now, just take the contents of the line_compare_these_parts and
      # put it in the pieces
      self.update_parts_selection( str(self.line_compare_these_parts.text()) )



   def update_parts_selection( self, part_spec ):
      '''
      Updates line_compare_these_parts and the model data for all selected
      pieces so that the "parts to compare" contains part_spec.
      '''

      # update the UI
      self.line_compare_these_parts.setText( part_spec )

      # Update the selected pieces
      # get the list of selected cells... for each one that is the "voices"
      # column(), set it to the thing specified
      selected_cells = self.gui_pieces_list.selectedIndexes()
      for cell in selected_cells:
         if self.model_compare_parts == cell.column():
            self.analysis_pieces.setData( cell, part_spec, QtCore.Qt.EditRole )



   def update_values_of_n( self ):
      # TODO: input validation using QValidator

      # For now, just take the contents of line_values_of_n and put it in
      # the pieces
      new_n = list(set([int(n) for n in re.findall('(-?\d+)', self.line_values_of_n.text())]))

      # Update the selected pieces
      # get the list of selected cells... for each one that is the "n"
      # column(), set it to the thing specified
      selected_cells = self.gui_pieces_list.selectedIndexes()
      for cell in selected_cells:
         if self.model_n == cell.column():
            self.analysis_pieces.setData( cell, new_n, QtCore.Qt.EditRole )



   def update_offset_interval( self ):
      # TODO: input validation using QValidator

      # For now, just take the contents of line_values_of_n and put it in
      # the pieces
      new_offset_interval = str(self.line_offset_interval.text())

      # Update the selected pieces
      # get the list of selected cells... for each one that is the "n"
      # column(), set it to the thing specified
      selected_cells = self.gui_pieces_list.selectedIndexes()
      for cell in selected_cells:
         if self.model_offset == cell.column():
            self.analysis_pieces.setData( cell, new_offset_interval, QtCore.Qt.EditRole )



   def update_piece_settings_visibility( self, set_to ):
      '''
      Given True or False, calls .setVisible() on all the widgets in the
      "Settings for Piece" QGroupBox with that value, and with the opposite
      value for self.lbl_select_piece
      '''

      self.line_values_of_n.setVisible( set_to )
      self.line_offset_interval.setVisible( set_to )
      self.btn_choose_note.setVisible( set_to )
      self.line_compare_these_parts.setVisible( set_to )
      self.chk_all_voice_combos.setVisible( set_to )
      self.chk_basso_seguente.setVisible( set_to )
      self.btn_add_check_combo.setVisible( set_to )
      self.line_piece_title.setVisible( set_to )
      self.lbl_piece_title.setVisible( set_to )
      self.lbl_compare_these_parts.setVisible( set_to )
      self.lbl_piece_title.setVisible( set_to )
      self.lbl_values_of_n.setVisible( set_to )
      self.lbl_offset_interval.setVisible( set_to )
      self.lbl_select_piece.setVisible( not set_to )



   def update_pieces_selection( self ):
      # TODO: finish the other things for this method
      # When the user changes the piece(s) selected in self.gui_pieces_list

      # Which piece is/pieces are selected?
      currently_selected = self.gui_pieces_list.selectedIndexes()

      # NB: we get a list of all the cells selected, and this is definitely done
      # in rows, so because each row has 6 things, if we have 6 cells, it means
      # we have only one row... but more than 6 cells means more than one row
      if len(currently_selected) == 0:
         # (1) Disable all the controls
         self.line_values_of_n.setEnabled( False )
         self.line_offset_interval.setEnabled( False )
         self.btn_choose_note.setEnabled( False )
         self.line_compare_these_parts.setEnabled( False )
         self.chk_all_voice_combos.setEnabled( False )
         self.chk_basso_seguente.setEnabled( False )
         self.btn_add_check_combo.setEnabled( False )
         self.line_piece_title.setEnabled( False )
         self.update_piece_settings_visibility( False )
         # (2) Remove the part list
         if self.part_checkboxes is not None:
            for part in self.part_checkboxes:
               self.verticalLayout_22.removeWidget( part )
               part.close()
            self.part_checkboxes = None
      elif len(currently_selected) > 6:
         # Multiple pieces selected... possible customization
         # (1) Enable all the controls
         self.line_values_of_n.setEnabled( True )
         self.line_offset_interval.setEnabled( True )
         self.btn_choose_note.setEnabled( True )
         self.line_compare_these_parts.setEnabled( True )
         self.chk_all_voice_combos.setEnabled( True )
         self.chk_basso_seguente.setEnabled( True )
         self.btn_add_check_combo.setEnabled( True )
         self.line_piece_title.setEnabled( False ) # not applicable
         self.update_piece_settings_visibility( True )
         # (2) if the pieces have the same part names, display them
         first_parts = None
         for cell in currently_selected:
            if self.model_parts_list == cell.column():
               if first_parts is None:
                  first_parts = self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()
               elif first_parts == self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject():
                  continue
               else:
                  first_parts = ''
                  break
         if '' != first_parts:
            # Then they all have the same name, so we can use them
            self.update_part_checkboxes( currently_selected )
         else:
            # Then they don't all have the same name.
            self.chk_all_voice_combos.setEnabled( True )
            self.chk_basso_seguente.setEnabled( True )
            self.adjust_bs()
            self.update_part_checkboxes( 'erase' )
         # (3) if the pieces have the same offset interval, display it
         first_offset = None
         for cell in currently_selected:
            if self.model_offset == cell.column():
               if first_offset is None:
                  first_offset = self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()
               elif first_offset == self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject():
                  continue
               else:
                  first_offset = ''
                  break
         self.line_offset_interval.setText( str(first_offset) )
         # (4) if the pieces have the same values of n, display them
         first_n = None
         for cell in currently_selected:
            if self.model_n == cell.column():
               if first_n is None:
                  first_n = self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()
               elif first_n == self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject():
                  continue
               else:
                  first_n = ''
                  break
         self.line_values_of_n.setText( first_n )
         # (5) Update "Compare These Parts"
         first_comp = None
         for cell in currently_selected:
            if self.model_compare_parts == cell.column():
               if first_comp is None:
                  first_comp = self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()
               elif first_comp == self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject():
                  continue
               else:
                  first_comp = ''
                  break
         if '' == first_comp:
            # Multiple parts have different specs
            self.line_compare_these_parts.setText( '' )
            self.chk_all_voice_combos.setChecked( False )
            self.chk_basso_seguente.setChecked( False )
            self.adjust_bs()
         else:
            # Multiple parts have the same spec
            self.update_comparison_parts( currently_selected )
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
         self.line_piece_title.setEnabled( True )
         self.update_piece_settings_visibility( True )
         # (2) Populate the part list
         self.update_part_checkboxes( currently_selected )
         # (3) Update "values of n"
         for cell in currently_selected:
            if self.model_n == cell.column():
               self.line_values_of_n.setText( str(self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()) )
               break
         # (4) Update "offset interval"
         for cell in currently_selected:
            if self.model_offset == cell.column():
               self.line_offset_interval.setText( str(self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()) )
               break
         # (5) Update "Compare These Parts"
         self.update_comparison_parts( currently_selected )
         # (6) Update "Pice Title"
         for cell in currently_selected:
            if self.model_score == cell.column():
               self.line_piece_title.setText( str(self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()) )
               break
   # End update_pieces_selection() -------------------------



   def update_comparison_parts( self, currently_selected ):
      '''
      When a different part combination is selected, call this method to update
      the "All Combinations" and "Basso Seguente" checkboxes.

      You should only call this method if all of the selected pieces have the
      same part names (which is true when only one part is selected).

      The argument should be a list of the currently selected cells.
      '''

      for cell in currently_selected:
         if self.model_compare_parts == cell.column():
            comparison_parts = str(self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject())
            self.line_compare_these_parts.setText( comparison_parts )
            if '[all]' == comparison_parts:
               self.chk_all_voice_combos.setChecked( True )
               self.chk_basso_seguente.setChecked( False )
               # Update the QCheckBox for "All Combinations" and "Basso Seguente"
               self.all_voice_combos()
               self.chose_bs()
            elif '[all,bs]' == comparison_parts:
               self.chk_all_voice_combos.setChecked( True )
               self.chk_basso_seguente.setChecked( True )
               # Update the QCheckBox for "All Combinations" and "Basso Seguente"
               self.all_voice_combos()
               self.chose_bs()
            else:
               self.chk_all_voice_combos.setChecked( False )
               self.chk_basso_seguente.setChecked( False )
            break

      # Adjust the text for "Basso Seguente," if needed
      self.adjust_bs()
   # End update_comparison_parts() -------------------------



   def edit_part_name( self, part_index = None ):
      # Get the current part name from the checkbox...
      current_name = str(self.part_checkboxes[part_index].text())

      # Get the new name
      new_name = QtGui.QInputDialog.getText(\
         None,
         "Part Name!",
         "Choose New Part Name",
         QtGui.QLineEdit.Normal,
         current_name)

      new_name = str(new_name[0])

      # Which piece is/pieces are selected?
      currently_selected = self.gui_pieces_list.selectedIndexes()

      # Find the parts lists and update them
      for cell in currently_selected:
         if self.model_parts_list == cell.column():
            # We're just going to change the part name in the model, not in the
            # actual Score object itself (which would require re-loading)

            # Get the Score
            parts_list = self.analysis_pieces.data( cell, 'raw_list' ).toPyObject()

            # Update the part name as requested
            parts_list[part_index] = new_name

            # Convert the part names to str objects (from QString)
            parts_list = [str(name) for name in parts_list]

            # Update the data model and QCheckBox objects
            self.analysis_pieces.setData( cell, parts_list, QtCore.Qt.EditRole )
            self.update_pieces_selection()
   # End edit_part_name() ----------------------------------

   def zarr_0( self ):
      self.edit_part_name( 0 )

   def zarr_1( self ):
      self.edit_part_name( 1 )

   def zarr_2( self ):
      self.edit_part_name( 2 )

   def zarr_3( self ):
      self.edit_part_name( 3 )

   def zarr_4( self ):
      self.edit_part_name( 4 )

   def zarr_5( self ):
      self.edit_part_name( 5 )

   def zarr_6( self ):
      self.edit_part_name( 6 )

   def zarr_7( self ):
      self.edit_part_name( 7 )

   def zarr_8( self ):
      self.edit_part_name( 8 )

   def zarr_9( self ):
      self.edit_part_name( 9 )

   def zarr_10( self ):
      self.edit_part_name( 10 )

   def zarr_11( self ):
      self.edit_part_name( 11 )

   def zarr_12( self ):
      self.edit_part_name( 12 )

   def zarr_13( self ):
      self.edit_part_name( 13 )

   def zarr_14( self ):
      self.edit_part_name( 14 )

   def zarr_15( self ):
      self.edit_part_name( 15 )

   def update_part_checkboxes( self, currently_selected ):
      '''
      Update the part-selection QCheckBox objects to reflect the currently
      selected part(s).

      You should only call this method if all of the selected pieces have the
      same part names (which is true when only one part is selected).

      The argument should be a list of the currently selected cells.

      If the argument is == 'erase' then the method removes all current
      checkboxes and stops.
      '''

      # (1) Remove previous checkboxes from the layout
      # NOTE: the .destroy() calls seem to do nothing
      if self.part_layouts is not None:
         for lay in self.part_layouts:
            for part in self.part_checkboxes:
               lay.removeWidget( part )
               part.close()
            for button in self.edit_buttons:
               lay.removeWidget( button )
               button.close()
            self.verticalLayout_22.removeItem( lay )
            lay.invalidate()

      self.part_layouts, self.part_checkboxes, self.edit_buttons = None, None, None

      # (1a) If currently_selected is "erase" then we should only erase the
      # current checkboxes, and we should stop now.
      if 'erase' == currently_selected:
         return

      # (2) Get the list of parts
      list_of_parts = None
      for cell in currently_selected:
         if self.model_parts_list == cell.column():
            list_of_parts = self.analysis_pieces.data( cell, 'raw_list' ).toPyObject()
            break

      # (3) Put up a checkbox for each part
      self.part_checkboxes = []
      self.edit_buttons = []
      self.part_layouts = []
      for i in xrange(len(list_of_parts)):
         part_name = str(list_of_parts[i])
         # This is the New CheckBox to select this part
         n_c_b = QtGui.QCheckBox( self.widget_part_boxes )
         n_c_b.setObjectName( 'chk_' + part_name )
         n_c_b.setText( part_name )

         # This is the New BuTtoN to "Edit" this part's name
         n_btn = QtGui.QPushButton( self.widget_part_boxes )
         n_btn.setObjectName( 'btn_' + part_name )
         n_btn.setText( 'Edit Part Name' )
         # NOTE: this should be improved later
         n_btn.clicked.connect( eval( 'self.zarr_' + str(i) ) )
         # This would have been better, but it always passes the *last* "i"
         # value of the method
         # n_btn.clicked.connect( lambda : self.edit_part_name( i ) )

         # Add the checkbox and button to the horizontal layout
         lay = QtGui.QHBoxLayout()
         lay.addWidget( n_c_b )
         lay.addWidget( n_btn )

         # Add the layout to the list of part-name checkboxes
         self.edit_buttons.append( n_btn )
         self.part_checkboxes.append( n_c_b )
         self.part_layouts.append( lay )

      # (4) Add all the widgets to the layout
      for part in self.part_layouts:
         #self.verticalLayout_22.addWidget( part )
         self.verticalLayout_22.addLayout( part )
   # End update_part_checkboxes() --------------------------



   def launch_offset_selection( self ):
      # Launch the offset-selection QDialog
      selector = Vis_Select_Offset()
      chosen_offset = selector.trigger()

      # Update the QLineEdit
      self.line_offset_interval.setText( str(chosen_offset) )

      # Set values in the model
      selected_cells = self.gui_pieces_list.selectedIndexes()
      for cell in selected_cells:
         if self.model_offset == cell.column():
            self.analysis_pieces.setData( cell, chosen_offset, QtCore.Qt.EditRole )
# End Class Vis_MainWindow -----------------------------------------------------



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
      self.beginInsertRows( parent, row, row+count-1 )
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

   def iterator( self ):
      for f in self.files:
         yield f

   def removeRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginRemoveRows( parent, row, row+count-1 )
      self.files = self.files[:row] + self.files[row+count:]
      self.endRemoveRows()
# End Class List_of_Files ------------------------------------------------------



# Model for "Assemble" Panel -----------------------------------------------
class List_of_Pieces( QtCore.QAbstractTableModel ):
   # Here's the data model:
   # self.pieces : a list of lists. For each sub-list...
   #    sublist[0] : filename
   #    sublist[1] : a music21 score object corresponding to the filename
   #    sublist[2] : list of names of parts in the score
   #    sublist[3] : offset interval
   #    sublist[4] : list of values of n to look for
   #    sublist[5] : list of pairs of indices for parts

   def __init__( self, parent=QtCore.QModelIndex() ):
      QtCore.QAbstractTableModel.__init__( self, parent )
      # "Constant" values for what each column is and the index blah
      # NOTE: When you change these, be sure to change them in Vis_MainWindow too!
      self.model_filename = 0 # filename of the piece
      self.model_score = 1 # Score object and title
      self.model_parts_list = 2 # list of names of parts
      self.model_offset = 3 # offset Duration between vertical intervals
      self.model_n = 4 # values of "n" to find
      self.model_compare_parts = 5 # list of two-element lists of part indices

      self.pieces = []

   def rowCount( self, parent=QtCore.QModelIndex() ):
      return len(self.pieces)

   def columnCount( self, parent=QtCore.QModelIndex() ):
      # There are 6 columns (see "data model" above)
      return 6

   def data(self, index, role):
      if index.isValid():
         if QtCore.Qt.DisplayRole == role:
            if self.model_score == index.column():
               score = self.pieces[index.row()][index.column()]
               if score.metadata is not None:
                  return QtCore.QVariant( score.metadata.title )
               else:
                  return QtCore.QVariant('')
            elif self.model_parts_list == index.column():
               # this is for the part names
               return QtCore.QVariant( str(self.pieces[index.row()][index.column()])[1:-1] )
            elif self.model_n == index.column():
               return QtCore.QVariant(",".join(str(n) for n in self.pieces[index.row()][index.column()]))
            else:
               return QtCore.QVariant( self.pieces[index.row()][index.column()] )
         elif 'raw_list' == role:
            return QtCore.QVariant( self.pieces[index.row()][index.column()] )
         else:
            return QtCore.QVariant()

   def headerData( self, section, orientation, role ):
      header_names = ['Path', 'Title', 'List of Part Names', 'Offset', 'n', \
                      'Compare These Parts']

      if QtCore.Qt.Horizontal == orientation and QtCore.Qt.DisplayRole == role:
         return header_names[section]
      else:
         return QtCore.QVariant()

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

   def insertRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginInsertRows( parent, row, row+count-1 )
      for zed in xrange(count):
         self.pieces.insert( row, ['', None, [], 0.5, [2], "(no selection)"] )
      self.endInsertRows()

   def removeRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginRemoveRows( parent, row, row+count-1 )
      self.pieces = self.pieces[:row] + self.pieces[row+count:]
      self.endRemoveRows()

   def iterate_rows( self ):
      for row in self.pieces:
         yield row
# End Class List_of_Pieces ------------------------------------------------------

class List_of_Voice_Pairs( QtCore.QAbstractTableModel ):
   def __init__( self, parent, data=[] ):
      QtCore.QAbstractTableModel.__init__( self, parent )
      self.model_name = 0
      self.model_pair = 1
      self.pairs = data

   def headerData( self, section, orientation, role ):
      header_names = ['Piece', 'Voice Pair']
      if QtCore.Qt.Horizontal == orientation and QtCore.Qt.DisplayRole == role:
         return header_names[section]
      else:
         return QtCore.QVariant()

   def setData( self, index, value, role ):
      if QtCore.Qt.EditRole == role:
         self.pairs[index.row()][index.column()] = value
         self.dataChanged.emit( index, index )
         return True
      else:
         return False

   def data( self, index, role ):
      if index.isValid():
         if QtCore.Qt.DisplayRole == role:
            if index.column() == self.model_pair:
               return QtCore.QVariant( str(self.pairs[index.row()][index.column()])[1:-1] )
            else:
               return QtCore.QVariant( self.pairs[index.row()][index.column()] )
      else:
         return QtCore.QVariant()

   def columnCount( self, parent=None ):
      return 2

   def rowCount( self, parent=None ):
      return len(self.pairs)

   def insertRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginInsertRows( parent, row, row+count-1 )
      for zed in xrange(count):
         self.pairs.insert(row,['',[]])
      self.endInsertRows()

   def removeRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginRemoveRows( parent, row, row+count-1 )
      self.data = self.pairs[:row] + self.pairs[row+count:]
      self.endRemoveRows()
# End Class List_of_Voice_Pairs -----------------------------------------------

class Vis_Load_Piece( QtCore.QThread ):
   def setup( self, pathname, widget ):
      self.pathname = pathname
      self.widget = widget
      self.error = None

   def run( self ):
      '''
      Load all the pieces from the files list into the pieces list
      '''

      # For convenience
      pieces = self.widget.analysis_pieces
      row_count = pieces.rowCount()

      # Hold the imported Score object
      score = None

      # Check whether this filename was already loaded
      if self.pathname in self.widget.loaded_files:
         return

      # Try to import the score
      try:
         score = converter.parse( str(self.pathname) )
      except ( ConverterException, ConverterFileException ):
         self.error = self.pathname
         return

      # Add a new row in the list of pieces
      pieces.insertRows( row_count, 1 )

      # Add pathname data to the list of pieces
      index = pieces.createIndex( row_count, pieces.model_filename )
      pieces.setData( index, self.pathname, QtCore.Qt.EditRole )

      # Add the score to the list of pieces
      index = pieces.createIndex( row_count, pieces.model_score )
      pieces.setData( index, score, QtCore.Qt.EditRole )

      # Add a list of part names to the list of pieces
      index = pieces.createIndex( row_count, pieces.model_parts_list )
      parts_list = []
      for part in score.parts:
         # If the part has an Instrument object, we'll use its name. Or else
         # we can just take the part's ID, which our user will hopefully
         # replace later with a more suitable name.
         le_nom = ''
         if isinstance( part[0], instrument.Instrument ):
            le_nom = part[0].bestName()
         else:
            le_nom = part.id
         parts_list.append( le_nom )

      pieces.setData( index, parts_list, QtCore.Qt.EditRole )

      # Add this pathname to the list of files loaded
      self.widget.loaded_files.append( self.pathname )

      return
# End Class Vis_Load_Piece -----------------------------------------------------



class Vis_Signals_Class( QObject ):
   # This is used by Vis_Analyze_Piece when it's finished analyzing
   # a voice pair
   finishedVoicePair = pyqtSignal()

class Vis_Analyze_Piece( QtCore.QRunnable ):
   @staticmethod
   def calculate_all_combis( upto ):
      # Calculate all combinations of integers between 0 and the argument.
      #
      # Includes a 0th item... the argument should be len(whatevs) - 1.
      post = []
      for left in xrange(upto):
         for right in xrange(left+1,upto+1):
            post.append( [left,right] )
      return post

   def setup( self, piece_data, widget, this_piece_name, targeted_output=None ):
      self.piece_data = piece_data
      self.widget = widget
      self.this_piece_name = this_piece_name
      self.voice_combos = None
      self.nr_of_voice_combos = 0
      self.targeted_output = targeted_output

      # Calculate the voice pairs to analyze
      if '[all]' == self.piece_data[self.widget.model_compare_parts]:
         # We have to examine all combinations of parts

         # How many parts are in this piece?
         number_of_parts = len(self.piece_data[self.widget.model_score].parts)

         # Get a list of all the part-combinations to examine
         self.voice_combos = Vis_Analyze_Piece.calculate_all_combis( number_of_parts - 1 )
      else:
         # Turn the str specification of parts into a list of int (or str)
         if '(no selection)' == self.piece_data[self.widget.model_compare_parts]:
            # This is what happens when no voice pairs were selected
            return 0
         else:
            # NOTE: Later, we should do this in a safer way
            self.voice_combos = eval( self.piece_data[self.widget.model_compare_parts] )

      self.nr_of_voice_combos = len(self.voice_combos)

      # Return the number of voice pairs
      return self.nr_of_voice_combos
   # End of setup() ---------------------------------------

   def run( self ):
      # "stats" is the V_I_S object
      # Hold the basso seguente part, if needed
      seguente_part = None

      # How long this piece took
      piece_duration = 0.0

      # Add the preferred part names to the part objects
      for i in xrange(len(self.piece_data[self.widget.model_score].parts)):
         self.piece_data[self.widget.model_score].parts[i].vis_part_name = \
               self.piece_data[self.widget.model_parts_list][i]

      # Analyze all the specified part combinations
      for combo in self.voice_combos:
         # Get the two parts
         higher = self.piece_data[self.widget.model_score].parts[combo[0]]
         lower = None

         if 'bs' == lower:
            if seguente_part is None:
               seguente_part = \
               make_basso_seguente( self.piece_data[self.widget.model_score] )

            lower = seguente_part
         else:
            lower = self.piece_data[self.widget.model_score].parts[combo[1]]

         # Change the settings object to hold the right "lookForTheseNs"
         ns = str( self.piece_data[self.widget.model_n] )[1:-1]
         self.widget.settings.set_property( 'lookForTheseNs ' + ns )

         # Run the analysis
         voices_took, ly, error = vis_these_parts( these_parts=[higher,lower], \
                                        settings=self.widget.settings, \
                                        the_statistics=self.widget.statistics, \
                                        the_piece=self.this_piece_name, \
                                        targeted_output=self.targeted_output )

         # Deal with annotated LilyPond score, if needed
         if 'targeted score' == \
         self.widget.settings.get_property( 'outputFormat' ):
            # Add the annotated part to the score
            self.piece_data[self.widget.model_score].append( ly )
            # Send the score for processing
            lily_process_score( self.piece_data[self.widget.model_score] )

         # Update the duration-tracking thing
         piece_duration += voices_took

         # Update the GUI
         self.widget.vsc.finishedVoicePair.emit()
      # (end of voice-pair loop)
# End Class Vis_Analyze_Piece --------------------------------------------------



class Vis_Select_Offset( Ui_Select_Offset ):
   '''
   Display and assign actions for the offset-selection window.
   '''

   def trigger( self ):
      '''
      Set up and get information from a window that asks the user for an offest
      value. The return value corresponds to the quarterLength duration the
      user chose.
      '''

      # UI setup stuff
      self.select_offset = QtGui.QDialog()
      self.setupUi( self.select_offset )

      # Setup signals
      self.btn_submit.clicked.connect( self.submit_button )
      self.btn_8.clicked.connect( self.button_8 )
      self.btn_4.clicked.connect( self.button_4 )
      self.btn_2.clicked.connect( self.button_2 )
      self.btn_1.clicked.connect( self.button_1 )
      self.btn_0_5.clicked.connect( self.button_0_5 )
      self.btn_0_25.clicked.connect( self.button_0_25 )
      self.btn_0_125.clicked.connect( self.button_0_125 )
      self.btn_0_0625.clicked.connect( self.button_0_0625 )

      # Variable to hold the currently-selected duration
      self.current_duration = 0.5

      # Show the form!
      self.select_offset.exec_()

      # (User chooses stuff)

      # Return the currently-selected duration
      return self.current_duration

   def submit_button( self ):
      self.select_offset.done( 0 )

   def button_8( self ):
      self.current_duration = 8.0
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_4( self ):
      self.current_duration = 4.0
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_2( self ):
      self.current_duration = 2.0
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_1( self ):
      self.current_duration = 1.0
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_0_5( self ):
      self.current_duration = 0.5
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_0_25( self ):
      self.current_duration = 0.25
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_0_125( self ):
      self.current_duration = 0.125
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_0_0625( self ):
      self.current_duration = 0.0625
      self.line_music21_duration.setText( str(self.current_duration) )
# End Class Vis_Select_Offset --------------------------------------------------



class Vis_Text_Display( Ui_Text_Display ):
   # TODO: what on earth does this do?!
   def __init__(self,text):
      # TODO: what on earth does this do?!
      self.text_display = QtGui.QDialog()
      self.setupUi( self.text_display )
      self.text = text
      self.show_text.setPlainText(text)

   def trigger( self ):
      # TODO: what on earth does this do?!
      self.btn_save_as.clicked.connect( self.save_as )
      self.btn_close.clicked.connect( self.close )
      self.text_display.exec_()

   def save_as( self ):
      # TODO: what on earth does this do?!
      filename = str( QtGui.QFileDialog.getSaveFileName( None, \
                                                         'Save As', \
                                                         '', \
                                                         '*.txt' ) )
      result = file_outputter( self.text, filename, 'OVERWRITE' )
      if result[1] is not None:
         QtGui.QMessageBox.information(None,
            self.trUtf8("File Output Failed"),
            result[1],
            QtGui.QMessageBox.StandardButtons(\
               QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)

   def close( self ):
      # TODO: what on earth does this do?!
      self.text_display.done(0)
# End Class Vis_Text_Display ---------------------------------------------------



class Vis_Compare_Voice_Pairs( Ui_Compare_Voice_Pairs ):
   # TODO: what on earth does this do?!
   def __init__(self,parent):
      # TODO: what on earth does this do?!
      self.compare_voice_pairs = QtGui.QDialog()
      self.setupUi( self.compare_voice_pairs )
      top_data = parent.analysis_pieces
      data = []
      for i,piece in enumerate(list(top_data.iterate_rows())):
         index = top_data.createIndex(i,top_data.model_score)
         piece_name = top_data.data(index,QtCore.Qt.DisplayRole).toPyObject()
         index = top_data.createIndex(i,top_data.model_filename)
         file_name = top_data.data(index,QtCore.Qt.DisplayRole).toPyObject()
         name = file_name if piece_name == '' else piece_name
         index = top_data.createIndex(i,top_data.model_compare_parts)
         parts = eval(str(top_data.data(index,'raw_list').toPyObject()))
         for pair in parts:
            data.append([name,pair])
      self.model_in_memory = List_of_Voice_Pairs(self.list_pairs_in_memory,data)
      self.list_pairs_in_memory.setModel(self.model_in_memory)
      self.model_compare_these = List_of_Voice_Pairs(self.list_compare_these)
      self.list_compare_these.setModel(self.model_compare_these)
      self.model_to_these = List_of_Voice_Pairs(self.list_to_these)
      self.list_to_these.setModel(self.model_to_these)
      self.list_pairs_in_memory.dragEnterEvent = self.drag
      self.list_compare_these.dragMoveEvent = self.drag
      self.list_compare_these.dragEnterEvent = self.drag
      self.list_to_these.dragMoveEvent = self.drag
      self.list_to_these.dragEnterEvent = self.drag
      self.list_pairs_in_memory.mouseMoveEvent = self.start_drag_top
      self.btn_submit.clicked.connect( self.submit )
      self.list_compare_these.dropEvent = self.drop_these
      self.list_to_these.dropEvent = self.drop_those

   def drag( self, event ):
      if event.mimeData().hasFormat("application/x-person"):
         event.setDropAction(QtCore.Qt.MoveAction)
         event.accept()
      else:
         event.ignore()

   def start_drag_top( self,event ):
      # TODO: what on earth does this do?!
      index = self.list_pairs_in_memory.indexAt(event.pos())
      if not index.isValid():
         return
      i1 = self.model_in_memory.createIndex(index.row(),self.model_in_memory.model_name)
      i2 = self.model_in_memory.createIndex(index.row(),self.model_in_memory.model_pair)
      d1 = self.model_in_memory.data(i1,QtCore.Qt.DisplayRole).toPyObject()
      d2 = self.model_in_memory.data(i2,QtCore.Qt.DisplayRole).toPyObject()
      selected = [d1,d2]
      bstream = pickle.dumps(selected)
      mimeData = QtCore.QMimeData()
      mimeData.setData("application/x-person",bstream)
      drag = QtGui.QDrag(self.list_pairs_in_memory)
      drag.setMimeData(mimeData)
      #pixmap = QtGui.QPixmap()
      #pixmap = pixmap.grabWidget(self.list_pairs_in_memory,self.list_pairs_in_memory.rectForIndex(index))
      #drag.setPixmap(pixmap)
      #drag.setHotSpot(QtCore.QPoint(pixmap.width()/2,pixmap.height()/2))
      # TODO: why is this assigned to "result"? What does this even do/mean?
      result = drag.start(QtCore.Qt.MoveAction)

   def get_pairs( self ):
      self.compare_voice_pairs.exec_()
      return (0,1)

   def drop_these( self, event ):
      #TODO: can't add the same pair twice
      # TODO: what on earth does this do?!
      data = event.mimeData()
      bstream = data.retrieveData("application/x-person",QtCore.QVariant.ByteArray)
      selected = pickle.loads(bstream.toByteArray())
      length = self.model_compare_these.rowCount()
      self.model_compare_these.insertRows(length,1)
      ind = self.model_compare_these.createIndex(length,self.model_compare_these.model_name)
      self.model_compare_these.setData(ind,selected[self.model_compare_these.model_name],QtCore.Qt.EditRole)
      ind = self.model_compare_these.createIndex(length,self.model_compare_these.model_pair)
      self.model_compare_these.setData(ind,selected[self.model_compare_these.model_pair],QtCore.Qt.EditRole)
      event.accept()

   def drop_those( self, event ):
      #TODO: can't add the same pair twice
      # TODO: what on earth does this do?!
      data = event.mimeData()
      bstream = data.retrieveData("application/x-person",QtCore.QVariant.ByteArray)
      selected = pickle.loads(bstream.toByteArray())
      length = self.model_to_these.rowCount()
      self.model_to_these.insertRows(length,1)
      ind = self.model_to_these.createIndex(length,self.model_to_these.model_name)
      self.model_to_these.setData(ind,selected[self.model_to_these.model_name],QtCore.Qt.EditRole)
      ind = self.model_to_these.createIndex(length,self.model_to_these.model_pair)
      self.model_to_these.setData(ind,selected[self.model_to_these.model_pair],QtCore.Qt.EditRole)
      event.accept()

   def submit( self ):
      self.compare_voice_pairs.done(0)
# End Class Vis_Compare_Voice_Pairs --------------------------------------------



# "Main" Method ----------------------------------------------------------------
def main():
   # Standard stuff
   app = QtGui.QApplication( sys.argv )
   MainWindow = QtGui.QMainWindow()
   vis_ui = Vis_MainWindow()
   vis_ui.app = app
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
