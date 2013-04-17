#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:            vis
# Program Description:     Measures sequences of vertical intervals.
#
# Filename: interfaces/visqtinterface.py
# Purpose: PyQt4 implementation of VisInterface.
#
# Attribution: Based on the 'harrisonHarmony.py' module available at...
#              https://github.com/crantila/harrisonHarmony/
#
# Copyright (C) 2013 Christopher Antila, Jamie Klassen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
'''
Holds the VisQtInterface class, responsible for all PyQt4 stuff.
'''
# imports
from common import VisInterface, view_getter
from PyQt4 import QtCore, QtGui
import icons_rc

# Just a note: This file is (probably) going to become bulging huge -- the
# point is to implement a proper MVC framework, not make things pretty. We'll
# do some aesthetic refactoring once the roles have been properly divided.

class VisQtInterface(VisInterface):
   '''
   Interface for desktop app via PyQt4
   '''
   def __init__(self, vis_controller, argv):
      self.app = QtGui.QApplication(argv)
      self.get_view(vis_controller).show()
   
   def exec_(self):
      return self.app.exec_()
   
   # Helper functions
   
   def setup_thread(self, thread, next):
      '''
      Does the basic configuration for a QThread
      subclass to use the "working" screen.
      '''
      # NB: it may be more canonical/sensical not to have the 'next'
      # argument. From an MVC perspective, this means requiring the
      # VisInterface (which should be strictly a view) to understand
      # some aspect of the inner workings of the program.
      def thread_started():
         self.main_screen.setCurrentIndex(main_screen.WORKING_INDEX)
      thread.started.connect(thread_started)
      def update_progress(status):
         if isinstance(progress, basestring):
            if '100' == progress:
               self.progress_bar.setValue(100)
            elif 3 > len(progress):
               try:
                  new_val = int(progress)
                  self.progress_bar.setValue(new_val)
               except ValueError:
                  self.lbl.setText(progress)
            else:
               self.lbl.setText(progress)
      thread.status.connect(update_progress)
      def thread_finished():
         self.main_screen.setCurrentIndex(next)
      thread.finished.connect(thread_finished)
   
   def working_page(self):
      page_working = QtGui.QWidget()
      verticalLayout_21 = QtGui.QVBoxLayout(page_working)
      spacerItem10 = QtGui.QSpacerItem(20,
                                       40,
                                       QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Expanding)
      verticalLayout_21.addItem(spacerItem10)
      horizontalLayout_8 = QtGui.QHBoxLayout()
      spacerItem11 = QtGui.QSpacerItem(40,
                                       20,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
      horizontalLayout_8.addItem(spacerItem11)
      btn_wait_clock = QtGui.QPushButton(page_working)
      btn_wait_clock.setEnabled(True)
      btn_wait_clock.setText("")
      btn_wait_clock.setToolTip(self.translate("Hi, mom!"))
      icon8 = QtGui.QIcon()
      icon8.addPixmap(QtGui.QPixmap(":/icons/icons/working.png"),
                      QtGui.QIcon.Normal,
                      QtGui.QIcon.Off)
      btn_wait_clock.setIcon(icon8)
      btn_wait_clock.setIconSize(QtCore.QSize(64, 64))
      btn_wait_clock.setCheckable(False)
      btn_wait_clock.setChecked(False)
      btn_wait_clock.setFlat(True)
      horizontalLayout_8.addWidget(btn_wait_clock)
      spacerItem12 = QtGui.QSpacerItem(40,
                                       20,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
      horizontalLayout_8.addItem(spacerItem12)
      verticalLayout_21.addLayout(horizontalLayout_8)
      lbl_status_text = QtGui.QLabel(page_working)
      lbl_status_text.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
      lbl_status_text.setText(self.translate("Please wait..."))
      self.lbl = lbl_status_text
      verticalLayout_21.addWidget(lbl_status_text)
      progress_bar = QtGui.QProgressBar(page_working)
      progress_bar.setProperty("value", 0)
      self.progress_bar = progress_bar
      verticalLayout_21.addWidget(progress_bar)
      lbl_currently_processing = QtGui.QLabel(page_working)
      lbl_currently_processing.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
      lbl_currently_processing.setText(self.translate("(processing)"))
      verticalLayout_21.addWidget(lbl_currently_processing)
      spacerItem13 = QtGui.QSpacerItem(20,
                                       40,
                                       QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Expanding)
      verticalLayout_21.addItem(spacerItem13)
      return page_working
   
   def translate(self, text):
      ret = QtGui.QApplication.translate("MainWindow",
                                         text,
                                         None,
                                         QtGui.QApplication.UnicodeUTF8)
      return ret
   
   def make_tool_button(self, icon_path, size, tooltip, parent):
      btn = QtGui.QToolButton(parent)
      icon = QtGui.QIcon()
      icon.addPixmap(QtGui.QPixmap(icon_path), 
                     QtGui.QIcon.Normal,
                     QtGui.QIcon.Off)
      btn.setIcon(icon)
      btn.setIconSize(QtCore.QSize(size, size))
      btn.setCheckable(True)
      btn.setAutoExclusive(True)
      btn.setAutoRaise(True)
      btn.setText("")
      btn.setToolTip(self.translate(tooltip))
      return btn
   
   def make_push_button(self, icon_path, size, tooltip, parent):
      btn = QtGui.QPushButton(parent)
      btn.setText("")
      icon = QtGui.QIcon()
      icon.addPixmap(QtGui.QPixmap(icon_path),
                      QtGui.QIcon.Normal,
                      QtGui.QIcon.Off)
      btn.setIcon(icon)
      btn.setIconSize(QtCore.QSize(size, size))
      btn.setFlat(True)
      btn.setToolTip(self.translate(tooltip))
      return btn
   
   # Main Window Views
   
   @view_getter('VisController')
   def view(self, vis_controller):
      MainWindow = QtGui.QMainWindow()
      MainWindow.resize(953, 678)
      centralwidget = QtGui.QWidget(MainWindow)
      verticalLayout = QtGui.QVBoxLayout(centralwidget)
      function_menu = QtGui.QWidget(centralwidget)
      horizontalLayout = QtGui.QHBoxLayout(function_menu)
      horizontalLayout.setMargin(0)
      horizontalLayout.addWidget(self.get_view(vis_controller.choose_files,
                                               parent=function_menu))
      horizontalLayout.addWidget(self.get_view(vis_controller.import_files,
                                               parent=function_menu))
      horizontalLayout.addWidget(self.get_view(vis_controller.setup_analysis,
                                               parent=function_menu))
      horizontalLayout.addWidget(self.get_view(vis_controller.analyze_pieces,
                                               parent=function_menu))
      horizontalLayout.addWidget(self.get_view(vis_controller.setup_experiment,
                                               parent=function_menu))
      spacerItem = QtGui.QSpacerItem(40,
                                     20,
                                     QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Minimum)
      horizontalLayout.addItem(spacerItem)
      horizontalLayout.addWidget(self.get_view(vis_controller.get_info,
                                               parent=function_menu))
      verticalLayout.addWidget(function_menu)
      main_screen = QtGui.QStackedWidget(centralwidget)
      self.IMPORTER_INDEX = 0
      self.ANALYZER_INDEX = 1
      self.EXPERIMENTER_INDEX = 2
      self.WORKING_INDEX = 3
      main_screen.addWidget(self.get_view(vis_controller.importer))
      main_screen.addWidget(self.get_view(vis_controller.analyzer))
      main_screen.addWidget(self.get_view(vis_controller.experimenter))
      main_screen.addWidget(self.get_view(self.working_page()))
      # TODO: refactor this
      page_about = QtGui.QWidget()
      verticalLayout_5 = QtGui.QVBoxLayout(page_about)
      groupBox_4 = QtGui.QGroupBox(page_about)
      groupBox_4.setTitle(self.translate("Information about vis"))
      verticalLayout_6 = QtGui.QVBoxLayout(groupBox_4)
      label_copyright = QtGui.QLabel(groupBox_4)
      label_copyright.setText(self.translate('''
      <html>
      <head/>
      <body>
         <p>
            <span style=\" text-decoration: underline;\">vis 9</span>
         </p>
         <p>
            Copyright (c) 2012, 2013 Christopher Antila, Jamie Klassen, Alexander Morgan
         </p>
         <p>
            This program is free software: you can redistribute it and/or modify<br/>it under
             the terms of the GNU General Public License as published by<br/>the Free Software
              Foundation, either version 3 of the License, or<br/>(at your option) any later
               version.
         </p>
         <p>
            This program is distributed in the hope that it will be
             useful,<br/>but WITHOUT ANY WARRANTY; without even the implied warranty
              of<br/>MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the<br/>GNU
               General Public License for more details.
         </p>
         <p>
            You should have received a copy
             of the GNU General Public License<br/>along with this program. If not, see
              &lt;http://www.gnu.org/licenses/&gt;.
         </p>
      </body>
      </html>'''))
      verticalLayout_6.addWidget(label_copyright)
      line = QtGui.QFrame(groupBox_4)
      line.setFrameShape(QtGui.QFrame.HLine)
      line.setFrameShadow(QtGui.QFrame.Sunken)
      verticalLayout_6.addWidget(line)
      label_about = QtGui.QLabel(groupBox_4)
      label_about.setText(self.translate('''
      <html>
      <head/>
      <body>
      <p>
         vis was written as part of McGill University\'s contribution to the ELVIS
          project.<br/>For more information about ELVIS, please refer to our 
          <a href=\"http://elvis.music.mcgill.ca/\">
            <span style=\" text-decoration: underline; color:#0057ae;\">
               web site
            </span>
         </a>.
      </p>
      <p>
         Funding for ELVIS was provided by the following organizations:<br/>- SSHRC (Social
          Sciences and Humanities Research Council) of Canada<br/>- NEH (National Endowment for
           the Humanities) of the United States of America<br/>- The Digging into Data
            Challenge
      </p>
      <p>
         vis is written in the Python programming language, and relies on the
          following<br/>software, all released under free licences:<br/>
         - <a href=\"http://mit.edu/music21/\">
            <span style=\" text-decoration: underline; color:#0057ae;\">
               music21<br/>
            </span>
         </a>
         - <a href=\"http://www.riverbankcomputing.co.uk/software/pyqt/download\">
            <span style=\" text-decoration: underline; color:#0057ae;\">
               PyQt4
            </span>
         </a>
         <br/>
         - <a href=\"http://www.oxygen-icons.org/\">
            <span style=\" text-decoration: underline; color:#0057ae;\">
               Oxygen Icons
            </span>
         </a>
      </p>
      </body>
      </html>'''))
      verticalLayout_6.addWidget(label_about)
      verticalLayout_5.addWidget(groupBox_4)
      # END TODO
      main_screen.addWidget(page_about)
      verticalLayout.addWidget(main_screen)
      self.main_screen = main_screen
      MainWindow.setCentralWidget(centralwidget)
      statusbar = QtGui.QStatusBar(MainWindow)
      MainWindow.setStatusBar(statusbar)
      MainWindow.setWindowTitle(self.translate("vis"))
      main_screen.setCurrentIndex(0)
      return MainWindow
   
   @view_getter('choose_files')
   def view(self, choose_files, **kwargs):
      btn_choose_files = self.make_tool_button(":/icons/icons/choose_files.png",
                                               64,
                                               "Choose Files",
                                               kwargs.pop('parent'))
      btn_choose_files.setChecked(True)
      btn_choose_files.clicked.connect(choose_files)
      return btn_choose_files

   @view_getter('import_files')
   def view(self, import_files, **kwargs):
      btn_step1 = self.make_tool_button(":/icons/icons/right-arrow.png",
                                        32,
                                        "Continue to Step 2",
                                        kwargs.pop('parent'))
      btn_step1.clicked.connect(import_files)
      return btn_step1

   @view_getter('setup_analysis')
   def view(self, setup_analysis, **kwargs):
      btn_analyze = self.make_tool_button(":/icons/icons/analyze.png",
                                          64,
                                          "Prepare and Assemble for Analysis",
                                          kwargs.pop('parent'))
      btn_analyze.setEnabled(False)
      btn_analyze.setChecked(False)
      btn_analyze.clicked.connect(setup_analysis)
      return btn_analyze

   @view_getter('analyze_pieces')
   def view(self, analyze_pieces, **kwargs):
      btn_step2 = self.make_tool_button(":/icons/icons/right-arrow.png",
                                        32,
                                        "Continue to the Step 3",
                                        kwargs.pop('parent'))
      btn_step2.setEnabled(False)
      btn_step2.clicked.connect(analyze_pieces)
      return btn_step2

   @view_getter('setup_experiment')
   def view(self, setup_experiment, **kwargs):
      btn_experiment = self.make_tool_button(":/icons/icons/show_results.png",
                                             64,
                                             "Show and Save Results",
                                             kwargs.pop('parent'))
      btn_experiment.setEnabled(False)
      btn_experiment.clicked.connect(setup_experiment)
      return btn_experiment

   @view_getter('get_info')
   def view(self, get_info, **kwargs):
      btn_about = self.make_tool_button(":/icons/icons/help-about.png",
                                        64,
                                        "About \"vis\"",
                                        kwargs.pop('parent'))
      btn_about.clicked.connect(get_info)
      return btn_about
   
   # "Import" Frame Views
   
   @view_getter('Importer')
   def view(self, importer):
      page_choose = QtGui.QWidget()
      verticalLayout_2 = QtGui.QVBoxLayout(page_choose)
      grp_choose_files = QtGui.QGroupBox(page_choose)
      grp_choose_files.setTitle(self.translate("Choose Files"))
      horizontalLayout_3 = QtGui.QHBoxLayout(grp_choose_files)
      widget_3 = QtGui.QWidget(grp_choose_files)
      verticalLayout_7 = QtGui.QVBoxLayout(widget_3)
      verticalLayout_7.setMargin(0)
      widget_4 = QtGui.QWidget(widget_3)
      horizontalLayout_4 = QtGui.QHBoxLayout(widget_4)
      horizontalLayout_4.setMargin(0)
      label_3 = QtGui.QLabel(widget_4)
      label_3.setText(self.translate("Files to Analyze:"))
      horizontalLayout_4.addWidget(label_3)
      spacerItem1 = QtGui.QSpacerItem(40,
                                      20,
                                      QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Minimum)
      horizontalLayout_4.addItem(spacerItem1)
      files_list_view = self.get_view(importer._list_of_files, parent=widget_3)
      horizontalLayout_4.addWidget(self.get_view(importer.add_folders,
                                                 parent=widget_4))
      horizontalLayout_4.addWidget(self.get_view(importer.add_files,
                                                 parent=widget_4))
      horizontalLayout_4.addWidget(self.get_view(importer.remove_files,
                                                 parent=widget_4,
                                                 files_list=files_list_view))
      verticalLayout_7.addWidget(widget_4)
      verticalLayout_7.addWidget(files_list_view)
      widget_5 = QtGui.QWidget(widget_3)
      widget_5.setLayoutDirection(QtCore.Qt.RightToLeft)
      horizontalLayout_7 = QtGui.QHBoxLayout(widget_5)
      horizontalLayout_7.setMargin(0)
      horizontalLayout_7.addWidget(self.get_view(importer.thread,
                                                 parent=widget_5))
      horizontalLayout_7.addWidget(self.get_view(importer.thread.set_import_multiproc,
                                                 parent=widget_5))

      spacerItem2 = QtGui.QSpacerItem(40,
                                      20,
                                      QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Minimum)
      horizontalLayout_7.addItem(spacerItem2)
      verticalLayout_7.addWidget(widget_5)
      horizontalLayout_3.addWidget(widget_3)
      widget = QtGui.QWidget(grp_choose_files)
      widget.setMaximumSize(QtCore.QSize(200, 16777215))
      verticalLayout_8 = QtGui.QVBoxLayout(widget)
      verticalLayout_8.setMargin(0)
      horizontalLayout_3.addWidget(widget)
      verticalLayout_2.addWidget(grp_choose_files)
      return page_choose
   
   @view_getter('add_folders')
   def view(self, add_folders, **kwargs):
      btn_dir_add = self.make_push_button(":/icons/icons/add-dir.png",
                                          32,
                                          "Add Directory",
                                          kwargs.pop('parent'))
      def on_click():
         d = QtGui.QFileDialog.getExistingDirectory(
            None,
            "Choose Directory to Analyze",
            '',
            QtGui.QFileDialog.ShowDirsOnly
         )
         add_folders(str(d))
      btn_dir_add.clicked.connect(on_click)
      return btn_dir_add
   
   @view_getter('add_files')
   def view(self, add_files, **kwargs):
      btn_file_add = self.make_push_button(":/icons/icons/add-file.png",
                                           32,
                                           "Add Files",
                                           kwargs.pop('parent'))
      def on_click():
         files = QtGui.QFileDialog.getOpenFileNames(
            None,
            "Choose Files to Analyze",
            '',
            '*.nwc *.mid *.midi *.mxl *.krn *.xml *.md',
            None)
         add_files(files)
      btn_file_add.clicked.connect(on_click)
      return btn_file_add
   
   @view_getter('remove_files')
   def view(self, remove_files, **kwargs):
      files_list = kwargs.pop('files_list')
      btn_file_remove = self.make_push_button(":/icons/icons/list-remove.png",
                                              32,
                                              "Remove Selected Items",
                                              kwargs.pop('parent'))
      def on_click():
         currently_selected = files_list.selectedIndexes()
         remove_files(currently_selected)
      btn_file_remove.clicked.connect(on_click)
      return btn_file_remove
   
   @view_getter('ListOfFiles')
   def view(self, list_of_files, **kwargs):
      parent = kwargs.pop('parent')
      gui_file_list = QtGui.QListView(parent)
      gui_file_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
      gui_file_list.setModel(list_of_files)
      return gui_file_list
   
   @view_getter('ImporterThread')
   def view(self, importer_thread, **kwargs):
      parent = kwargs.pop('parent')
      btn_import = QtGui.QPushButton(parent)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                     QtGui.QSizePolicy.Fixed)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(btn_import.sizePolicy().hasHeightForWidth())
      btn_import.setSizePolicy(sizePolicy)
      btn_import.setLayoutDirection(QtCore.Qt.LeftToRight)
      btn_import.setText(self.translate("Import Pieces"))
      self.setup_thread(importer_thread, self.ANALYZER_INDEX)
      btn_import.clicked.connect(importer_thread.start)
      return btn_import
   
   @view_getter('set_import_multiproc')
   def view(self, set_import_multiproc, **kwargs):
      parent = kwargs.pop('parent')
      chk_multi_import = QtGui.QCheckBox(parent)
      chk_multi_import.setLayoutDirection(QtCore.Qt.LeftToRight)
      chk_multi_import.setText(self.translate("Use multiprocessing (import in parallel)"))
      chk_multi_import.stateChanged.connect(set_import_multiproc)
      return chk_multi_import
   
   # "Analyze" Frame Views
   
   @view_getter('Analyzer')
   def view(self, analyzer):
      page_analyze = QtGui.QWidget()
      verticalLayout_23 = QtGui.QVBoxLayout(page_analyze)
      groupBox = QtGui.QGroupBox(page_analyze)
      groupBox.setTitle(self.translate("Assemble Results, Statistics, Analyses"))
      gridLayout_2 = QtGui.QGridLayout(groupBox)
      spacerItem3 = QtGui.QSpacerItem(20,
                                      40,
                                      QtGui.QSizePolicy.Minimum,
                                      QtGui.QSizePolicy.Expanding)
      gridLayout_2.addItem(spacerItem3, 4, 4, 1, 1)
      gridLayout_2.addWidget(self.get_view(analyzer.load_statistics, parent=groupBox),
                             0, 0, 1, 1)
      spacerItem4 = QtGui.QSpacerItem(40,
                                      20,
                                      QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Minimum)
      gridLayout_2.addItem(spacerItem4, 0, 2, 1, 1)
      lbl_select_piece = QtGui.QLabel(groupBox)
      lbl_select_piece.setAlignment(QtCore.Qt.AlignCenter)
      lbl_select_piece.setText(self.translate("Select piece(s) to see possible settings."))
      gridLayout_2.addWidget(lbl_select_piece, 3, 4, 1, 1)
      spacerItem5 = QtGui.QSpacerItem(20,
                                      40,
                                      QtGui.QSizePolicy.Minimum,
                                      QtGui.QSizePolicy.Expanding)
      gridLayout_2.addItem(spacerItem5, 2, 4, 1, 1)
      gridLayout_2.addWidget(self.get_view(analyzer._list_of_pieces, parent=groupBox),
                             2, 0, 6, 3)
      grp_settings_for_piece = QtGui.QGroupBox(groupBox)
      grp_settings_for_piece.setTitle(self.translate("Settings for Piece"))
      gridLayout_3 = QtGui.QGridLayout(grp_settings_for_piece)
      spacerItem6 = QtGui.QSpacerItem(20,
                                      40,
                                      QtGui.QSizePolicy.Minimum,
                                      QtGui.QSizePolicy.Expanding)
      gridLayout_3.addItem(spacerItem6, 3, 1, 1, 1)
      spacerItem7 = QtGui.QSpacerItem(20,
                                      40,
                                      QtGui.QSizePolicy.Minimum,
                                      QtGui.QSizePolicy.Expanding)
      gridLayout_3.addItem(spacerItem7, 6, 1, 1, 1)
      spacerItem8 = QtGui.QSpacerItem(40,
                                      20,
                                      QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Minimum)
      gridLayout_3.addItem(spacerItem8, 9, 1, 1, 2)
      gridLayout_3.addWidget(self.get_view(analyzer.add_parts_combo,
                                           parent=grp_settings_for_piece),
                             9, 0, 1, 1)
      gridLayout_3.addWidget(self.get_view(analyzer.set_offset_interval_txt,
                                           parent=grp_settings_for_piece),
                             0, 1, 1, 1)
      lbl_offset_interval = QtGui.QLabel(grp_settings_for_piece)
      lbl_offset_interval.setText(self.translate("Offset Interval:"))
      gridLayout_3.addWidget(lbl_offset_interval, 0, 0, 1, 1)
      gridLayout_3.addWidget(self.get_view(analyzer.set_parts_compare,
                                           parent=grp_settings_for_piece),
                             7, 1, 1, 2)
      lbl_compare_these_parts = QtGui.QLabel(grp_settings_for_piece)
      lbl_compare_these_parts.setText(self.translate("Compare These Parts:"))
      gridLayout_3.addWidget(lbl_compare_these_parts, 7, 0, 1, 1)
      gridLayout_3.addWidget(self.get_view(analyzer.set_offset_interval_gui,
                                           parent=grp_settings_for_piece),
                             0, 2, 1, 1)
      widget_2 = QtGui.QWidget(grp_settings_for_piece)
      horizontalLayout_9 = QtGui.QHBoxLayout(widget_2)
      horizontalLayout_9.setMargin(0)
      spacerItem9 = QtGui.QSpacerItem(40,
                                      20,
                                      QtGui.QSizePolicy.Maximum,
                                      QtGui.QSizePolicy.Minimum)
      horizontalLayout_9.addItem(spacerItem9)
      widget_part_boxes = QtGui.QWidget(widget_2)
      verticalLayout_22 = QtGui.QVBoxLayout(widget_part_boxes)
      verticalLayout_22.setMargin(0)
      verticalLayout_22.addWidget(self.get_view(analyzer.set_compare_all_parts,
                                                parent=widget_part_boxes))      
      verticalLayout_22.addWidget(self.get_view(analyzer.compare_basso_seguente,
                                                parent=widget_part_boxes))
      horizontalLayout_9.addWidget(widget_part_boxes)
      gridLayout_3.addWidget(widget_2, 8, 0, 1, 3)
      gridLayout_3.addWidget(self.get_view(analyzer.set_piece_title,
                                           parent=grp_settings_for_piece),
                             5, 1, 1, 2)
      lbl_piece_title = QtGui.QLabel(grp_settings_for_piece)
      lbl_piece_title.setText(self.translate("Piece Title:"))
      gridLayout_3.addWidget(lbl_piece_title, 5, 0, 1, 1)
      
      gridLayout_3.addWidget(self.get_view(analyzer.set_salami,
                                           parent=grp_settings_for_piece),
                             1, 0, 1, 3)
      gridLayout_2.addWidget(grp_settings_for_piece, 6, 4, 2, 1)
      widget_6 = QtGui.QWidget(groupBox)
      horizontalLayout_5 = QtGui.QHBoxLayout(widget_6)
      horizontalLayout_5.setMargin(0)
      horizontalLayout_5.addWidget(self.get_view(analyzer.set_analyze_multiprocess,
                                                 parent=widget_6))
      horizontalLayout_5.addWidget(self.get_view(analyzer.analyze, parent=widget_6))
      gridLayout_2.addWidget(widget_6, 0, 4, 1, 1)
      verticalLayout_23.addWidget(groupBox)
      # maybe connect some signals?
      return page_analyze
   
   @view_getter('load_statistics')
   def view(self, load_statistics, **kwargs):
      parent = kwargs.pop('parent')
      btn_load_statistics = QtGui.QPushButton(parent)
      btn_load_statistics.setEnabled(False)
      btn_load_statistics.setText(self.translate("Load Existing Statistics Database"))
      btn_load_statistics.clicked.connect(load_statistics)
      return btn_load_statistics

   @view_getter('ListOfPieces')
   def view(self, list_of_pieces, **kwargs):
      parent = kwargs.pop('parent')
      gui_pieces_list = QtGui.QTableView(parent)
      gui_pieces_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      gui_pieces_list.horizontalHeader().setMinimumSectionSize(2)
      gui_pieces_list.verticalHeader().setVisible(False)
      # TODO: connect signals
      return gui_pieces_list

   @view_getter('add_parts_combo')
   def view(self, add_parts_combo, **kwargs):
      parent = kwargs.pop('parent')
      btn_add_check_combo = QtGui.QPushButton(parent)
      btn_add_check_combo.setEnabled(False)
      btn_add_check_combo.setText(self.translate("Add Combination"))
      # TODO: connect signals
      return btn_add_check_combo

   # NOTE: this _txt, _gui thing is ugly. A better way to do this
   # would be to have multiple views for the same backend function,
   # and just return a tuple of them. Let the view-getter sort
   # out which is which.

   @view_getter('set_offset_interval_txt')
   def view(self, set_offset_interval, **kwargs):
      parent = kwargs.pop('parent')
      line_offset_interval = QtGui.QLineEdit(parent)
      line_offset_interval.setEnabled(False)
      line_offset_interval.setInputMask("")
      line_offset_interval.setMaxLength(256)
      line_offset_interval.setText(self.translate("0.5"))
      # TODO: connect signals
      return line_offset_interval

   @view_getter('set_offset_interval_gui')
   def view(self, set_offset_interval, **kwargs):
      parent = kwargs.pop('parent')
      btn_choose_note = QtGui.QPushButton(parent)
      btn_choose_note.setEnabled(False)
      btn_choose_note.setText(self.translate("Choose Offset Note"))
      # include all the GUI stuff the button does!
      return btn_choose_note

   @view_getter('set_parts_compare')
   def view(self, set_parts_compare, **kwargs):
      parent = kwargs.pop('parent')
      line_compare_these_parts = QtGui.QLineEdit(parent)
      line_compare_these_parts.setEnabled(False)
      line_compare_these_parts.setInputMask("")
      line_compare_these_parts.setText(self.translate("e.g., [0,3] or [[0,3],[1,3]]"))
      # TODO: connect signals
      return line_compare_these_parts

   @view_getter('set_compare_all_parts')
   def view(self, set_compare_all_parts, **kwargs):
      parent = kwargs.pop('parent')
      chk_all_voice_combos = QtGui.QCheckBox(parent)
      chk_all_voice_combos.setEnabled(False)
      chk_all_voice_combos.setToolTip(self.translate(
         "Collect Statistics for all Part Combinations"
      ))
      chk_all_voice_combos.setText(self.translate("All 2-Part Combinations"))
      # TODO: connect signals
      return chk_all_voice_combos

   @view_getter('set_piece_title')
   def view(self, set_piece_title, **kwargs):
      parent = kwargs.pop('parent')
      line_piece_title = QtGui.QLineEdit(parent)
      # TODO: connect signals
      return line_piece_title

   @view_getter('compare_basso_seguente')
   def view(self, compare_basso_seguente, **kwargs):
      parent = kwargs.pop('parent')
      chk_basso_seguente = QtGui.QCheckBox(parent)
      chk_basso_seguente.setEnabled(False)
      chk_basso_seguente.setToolTip(self.translate("Generate Basso Seguente Part"))
      chk_basso_seguente.setText(self.translate("Basso Seguente"))
      # TODO: connect signals
      return chk_basso_seguente

   @view_getter('set_salami')
   def view(self, set_salami, **kwargs):
      parent = kwargs.pop('parent')
      chk_repeat_identical = QtGui.QCheckBox(parent)
      chk_repeat_identical.setText(self.translate("Repeat consecutive identical events"))
      # TODO: connect signals
      return chk_repeat_identical

   @view_getter('analyze')
   def view(self, analyze, **kwargs):
      parent = kwargs.pop('parent')
      btn_analyze_now = QtGui.QPushButton(parent)
      btn_analyze_now.setText(self.translate("Analyze Voice Pairs"))
      # TODO: connect signals
      return btn_analyze_now

   @view_getter('set_analyze_multiprocess')
   def view(self, set_analyze_multiprocess, **kwargs):
      parent = kwargs.pop('parent')
      chk_analyze_multi = QtGui.QCheckBox(parent)
      chk_analyze_multi.setText(self.translate("Use multiprocessing (analyze in parallel)"))
      # TODO: connect signals
      return chk_analyze_multi
   
   # "Experiment" Frame Views
   
   @view_getter('set_experiment')
   def view(self, set_experiment, **kwargs):
      parent = kwargs.pop('parent')
      combo_choose_experiment = QtGui.QComboBox(parent)
      # TODO: connect signals
      return combo_choose_experiment
   
   @view_getter('Experimenter')
   def view(self, experimenter):
      page_show = QtGui.QWidget()
      verticalLayout_3 = QtGui.QVBoxLayout(page_show)
      groupBox_2 = QtGui.QGroupBox(page_show)
      groupBox_2.setLayoutDirection(QtCore.Qt.LeftToRight)
      groupBox_2.setTitle(self.translate("Conduct an Experiment"))
      formLayout = QtGui.QFormLayout(groupBox_2)
      formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
      formLayout.setContentsMargins(12, -1, -1, -1)
      formLayout.setWidget(0,
                           QtGui.QFormLayout.FieldRole,
                           self.get_view(experimenter.set_experiment,
                                         parent=groupBox_2))
      lbl_choose_experiment = QtGui.QLabel(groupBox_2)
      lbl_choose_experiment.setText(self.translate("Choose an Experiment:"))
      formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, lbl_choose_experiment)
      verticalLayout_3.addWidget(groupBox_2)
      return page_show
