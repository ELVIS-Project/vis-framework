#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: controllers.py
# Purpose: Holds the "controllers" for the MVC architecture in vis.
#
# Copyright (C) 2012 Jamie Klassen, Christopher Antila
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
'''
Holds the "controllers" for the MVC architecture in vis.
'''



# Imports from...
# Python
from multiprocessing import Process
# PyQt4
from PyQt4.QtCore import pyqtSignal, QObject
# vis
from views.Ui_main_window import Ui_MainWindow
from models.importer import ListOfFiles
from models.analyzer import ListOfPieces



class Controller(object):
   '''
   Base class for all vis controllers.
   '''



   def __init__(self):
      '''
      Creates a new instance, and assigns the appropriate widget.
      '''
      pass



   def setup_signals(self):
      '''
      Set methods of this controller as the slot for relevant signals emitted
      by the GUI.
      '''
      pass



class VisController(Ui_MainWindow):
   '''
   Subclasses the automatically-generated python code in Ui_main_window that
   creates the GUI. Although there is a dependency on QtCore, for the PyQt
   signals-and-slots mechanism, we must try to avoid using QtGui methods as
   much as possible, so that, in the future, we can use other GUIs without
   importing Ui_main_window from the PyQt GUI.

   This class creates the GUI and manages interaction between other Controller
   subclasses and the GUI. It is effectively both the GUI's controller and the
   super-controller for Importer, Analyzer, Experimenter, and DisplayHandler,
   since VisController also "translates" GUI actions into the signals expected
   by the other controller subclasses.

   TODO: doctest
   '''
   # NOTE: We will have to rewrite most of this class when we want to implement
   # other (non-PyQt4) interfaces, but the use patterns, and maybe even the
   # algorithms, should stay mostly the same.

   # NOTE2: We may need other methods for other interfaces, but for PyQt4, we
   # only need __init__().



   def __init__(self, interface='PyQt4', details=None):
      '''
      Create a new VisController instance.

      The first argument, "interface", is a string specifying which GUI to use:
      - 'PyQt4'
      - 'HTML5' (not implemented)
      - others?

      The second argument, "details", is a list of arguments specifying settings
      to be used when creating the specific interface. So far, there are none.
      '''
      # Setup things we need to know
      self.UI_type = interface

      # Setup signals for GUI-only things

      # Create long-term sub-controllers
      # self.importer = ?
      # self.analyzer = ?
      # self.experimenter = ?
      # self.displayer = ?

      # Setup signals TO the long-term sub-controllers
      # self.importer.setup_signals()
      # self.analyzer.setup_signals()
      # self.experimenter.setup_signals()
      # self.displayer.setup_signals()

      # Setup signals FROM the long-term sub-controllers

      # Set the models for the table views.
      self.gui_file_list.setModel(self.importer.list_of_files)
      self.gui_pieces_list.setModel(self.analyzer.list_of_pieces)
# End class VisController ------------------------------------------------------



class VisSignals(QObject):
   '''
   The VisSignals class holds signals used for communication between
   controllers and their views. We're using signals-and-slots because it helps
   us with the MVC separation: a controller need not know *which* GUI is being
   used, so long as it knows that it will receive particular signals.
   Furthermore, there need not be a one-to-one correspondence between GUI
   widgets and methods in the models.

   Currently depends on PyQt4.QtCore.QObject for the signals-and-slots
   implementation.
   '''
   # Create a signal like this:
   # signal_name = pyqtSignal(str)

   # Importer
   importer_add_pieces = pyqtSignal(list) # a list of str filenames
   importer_remove_pieces = pyqtSignal(list) # a list of str filenames
   importer_add_remove_success = pyqtSignal(bool) # whether the add/remove operation was successful
   importer_import = pyqtSignal(str) # create a ListOfPieces from the ListOfFiles; argument ignored
   importer_imported = pyqtSignal(ListOfPieces) # the result of importer_import
   importer_error = pyqtSignal(str) # description of an error in the Importer
   importer_status = pyqtSignal(str) # informs the GUI of the status for a currently-running import (if two or three characters followed by a '%' then it should try to update a progress bar, if available)

   # Analyzer
   # TODO: figure out what type "index" and "data" are
   analyzer_change_settings = pyqtSignal(index, data) # change the data of a cell in the ListOfPieces; the GUI will know how to create an index based on which rows are selected and which data is being changed (cross-referenced with the ListOfPieces' declaration of column indices)
   analyzer_analyze = pyqtSignal(str) # to tell the Analyzer controller to perform analysis
   analyzer_analyzed = pyqtSignal(list) # the result of analyzer_analyze; the result is a list of AnalysisRecord objects
   analyzer_error = pyqtSignal(str) # description of an error in the Analyzer
   analyzer_status = pyqtSignal(str) # informs the GUI of the status for a currently-running analysis (if two or three characters followed by a '%' then it should try to update a progress bar, if available)
# End class VisSignals ---------------------------------------------------------



class Importer(Controller):
   '''
   This class knows how to keep a list of filenames with pieces to be analyzed,
   and how to import the files with music21.

   The ListOfFiles model is always stored in the list_of_files property.
   '''



   def __init__(self, *args):
      '''
      Create a new Importer instance.
      '''
      self.list_of_files = ListOfFiles()



   def setup_signals(self):
      '''
      Set the methods of Importer as slots for the relevant methods emitted by
      the VisController.
      '''
      # importer_add_pieces
      # importer_remove_pieces
      # importer_import
      pass



   def add_pieces(self, pieces):
      '''
      Add the filenames to the list of filenames that should be imported. The
      argument is a list of strings. If a filename is a directory, all the files
      in that directory (and its subdirectories) are added to the list.

      If a filename does not exist, this method emits the
      VisSignals.importer_error signal, with a description of the error.

      Emits the VisSignals.importer_add_remove_success signal with True or
      False, depending on whether the operation succeeded.
      '''
      pass



   def remove_pieces(self, pieces):
      '''
      Remove the filenames from the list of filenames that should be imported.
      The argument is a list of strings. If a filename is a directory, all the
      files in that directory (and its subdirectories) are removed from the
      list.

      If a filename does not exist, it is ignored.

      Emits the VisSignals.importer_add_remove_success signal with True or
      False, depending on whether the operation succeeded.
      '''
      pass



   def import_pieces(self):
      '''
      Transforms the current ListOfFiles into a ListOfPieces by importing the
      files specified, then extracting data as needed.

      Emits VisSignals.importer_error if a file cannot be imported, but
      continues to import the rest of the files.

      Emits VisSignals.importer_imported with the ListOfPieces when the import
      operation is completed.
      '''
      pass
# End class Importer -----------------------------------------------------------



class Analyzer(Controller):
   '''
   This class performs analysis for series of vertical intervals, and manages
   the settings with which to analyze. Makes a list of AnalysisRecord objects
   that each holds a half-analyzed voice-pair that Experimenter will use to
   perform fuller analysis.

   The ListOfPieces model is always stored in the list_of_pieces property.
   '''



   def __init__(self, pieces, *args):
      '''
      Create a new Analyzer instance.

      The first arguent, "pieces", must be a ListOfPieces object, as created
      by the Importer controller.
      '''
      self.list_of_pieces = None



   def setup_signals(self):
      '''
      Set the methods of Analyzer as slots for the relevant methods emitted by
      the VisController.
      '''
      VisSignals.importer_imported.connect(self.catch_import)



   @pyqtSlot(ListOfPieces)
   def catch_import(self, pieces_list):
      '''
      Slot for the VisSignals.importer_imported signal. This method is called
      when the Importer controller has finished importing the list of pieces.

      The argument is a ListOfPieces object.
      '''
      self.list_of_pieces = pieces_list



   def set_data(self, index, change_to):
      '''
      Changes the data in a cell of the ListOfPieces model.

      The arguments here should be the same as sent to ListOfPieces.setData().
      '''
      pass



   def run_analysis(self):
      '''
      Runs the analysis specified in the ListOfPieces. Produces an
      AnalysisRecord object for each voice pair analyzed.

      Emits the VisSignal.analyzer_error signal if there is a problem, and
      continues to process.

      Emits the VisSignal.analyzer_analyzed signal upon completion, with a list
      of the AnalysisRecord objects generated.
      '''
      pass
# End class Analyzer -----------------------------------------------------------



class Experimenter(Controller):
   '''
   This class handles input for a user's choice of Experiment and choice
   of associated Settings, then performs the experiment, returning the
   relevant Results object(s).
   '''


   def __init__(self):
      self.list_of_analyses = None



   def setup_signals(self):
      '''
      Set the methods of Experimenter as slots for the relevant methods emitted
      by the VisController.
      '''
      VisSignals.analyzer_analyzed.connect(self.catch_analyses)



   @pyqtSlot(list)
   def catch_analyses(self, analyses_list):
      '''
      Slot for the VisSignals.analyzer_analyzed signal. This method is called
      when the Analyzer controller has finished analysis.

      The argument is a list of AnalysisRecord objects.
      '''
      self.list_of_analyses = analyses_list

   # TODO: etc.
# End class Experimenter -------------------------------------------------------



class DisplayHandler(Controller):
   '''
   This class handles input for a user's choice of Settings and takes the
   results of an Experiment, formats them according to the user's choices
   and displays them in the appropriate view.
   '''
   def __init__(self, stylesheet, results):
      '''
      Creates a new DisplayHandler instance

      INPUTS:
      results - a Results object containing data for the results of an
      Experiment
      '''
      super(DisplayHandler, self).__init__()
      self._stylesheet = stylesheet
      self._results = results

   def setup_signals(self):
      VisSignals.display_results.connect(self.display_results)
