##! /usr/bin/python
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
      self.mainwindow = self.get_view(vis_controller)

   def exec_(self):
      self.mainwindow.show()
      return self.app.exec_()

   # Helper functions

   def get_multi_view(self, multi_setting, **kwargs):
      parent = kwargs['parent']
      groupBox = QtGui.QGroupBox(parent)
      groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
      groupBox.setTitle(self.translate(multi_setting.display_name))
      verticalLayout = QtGui.QVBoxLayout(groupBox)
      for chk in self.get_view(multi_setting.settings, **kwargs):
         verticalLayout.addWidget(chk)
      return groupBox

   def get_lbl_line(self, setting, **kwargs):
      parent = kwargs['parent']
      lbl = QtGui.QLabel(parent)
      lbl.setText(self.translate(setting.display_name))
      line = QtGui.QLineEdit(parent)
      line.setInputMask("")
      line.setMaxLength(256)
      line.setText(self.translate(setting.value))
      # TODO: connect signals
      return (lbl, line)

   def popup_error(self, component, description):
      '''
      Notify the user that an error has happened.
      INPUTS:
      `component` - the name of the component raising the error
      `description` - a useful description of the error
      '''
      # TODO: the `error` signals in the controllers should output a
      # (name, error) 2-tuple and this function can take that as an
      # argument instead of having the view-getter look at the controller's class.
      return QtGui.QMessageBox.warning(None,
                                       '{0} Error'.format(component),
                                       description,
                                       QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
                                       QtGui.QMessageBox.Ok)

   def setup_thread(self, controller):
      '''
      Does the basic configuration for a QThread
      subclass to use the "working" screen.
      '''
      @QtCore.pyqtSlot()
      def thread_started():
         self.main_screen.setCurrentWidget(self.work_page)
      controller.start.connect(thread_started)

      @QtCore.pyqtSlot(QtCore.QString)
      def update_progress(progress):
         '''
         Updates the "working" screen in the following ways:
         - If the argument is a two-character string that can be converted into
           an integer, or the string '100', the progress bar is set to that
           percentage completion.
         - If the argument is another string, the text below the progress bar is
           set to that string.
         '''
         #print 'update progress called with {0}'.format(progress) # DEBUGGING
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
         self.app.processEvents()
      controller.status.connect(update_progress)

      @QtCore.pyqtSlot(QtCore.QString)
      def popup_error(description):
         return self.popup_error(thread.__class__.__name__, description)
      controller.error.connect(popup_error)

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
      verticalLayout_21.addWidget(lbl_status_text)
      progress_bar = QtGui.QProgressBar(page_working)
      progress_bar.setMinimum(0)
      progress_bar.setMaximum(100)
      progress_bar.setValue(0)
      self.progress_bar = progress_bar
      verticalLayout_21.addWidget(progress_bar)
      lbl_currently_processing = QtGui.QLabel(page_working)
      lbl_currently_processing.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
      lbl_currently_processing.setText(self.translate("(processing)"))
      self.lbl = lbl_currently_processing
      verticalLayout_21.addWidget(lbl_currently_processing)
      spacerItem13 = QtGui.QSpacerItem(20,
                                       40,
                                       QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Expanding)
      verticalLayout_21.addItem(spacerItem13)
      return page_working

   def translate(self, text):
      ret = QtGui.QApplication.translate("MainWindow",
                                         str(text),
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

   # Settings Views

   @view_getter('BooleanSetting')
   def view(self, boolean_setting, **kwargs):
      parent = kwargs['parent']
      chk = QtGui.QCheckBox(parent)
      chk.setLayoutDirection(QtCore.Qt.LeftToRight)
      chk.setToolTip(self.translate(boolean_setting.extra_detail))
      chk.setText(self.translate(boolean_setting.display_name))
      chk.stateChanged.connect(lambda state: setattr(boolean_setting, 'value', state))
      return chk

   @view_getter('MultiChoiceSetting')
   def view(self, multi_choice_setting, **kwargs):
      return self.get_multi_view(multi_choice_setting, **kwargs)

   @view_getter('PartsComboSetting')
   def view(self, parts_combo_setting, **kwargs):
      return self.get_multi_view(parts_combo_setting, **kwargs)

   @view_getter('StringSetting')
   def view(self, string_setting, **kwargs):
      return self.get_lbl_line(string_setting, **kwargs)

   @view_getter('OffsetSetting')
   def view(self, offset_setting, **kwargs):
      lbl, line = self.get_lbl_line(offset_setting, **kwargs)
      line.setEnabled(False)
      parent = kwargs['parent']
      btn = QtGui.QPushButton(parent)
      btn.setEnabled(False)
      btn.setText(self.translate("Choose Offset Note"))
      # TODO: connect signals
      return (lbl, line, btn)

   @view_getter('Settings')
   def view(self, settings, **kwargs):
      for sett in settings:
         yield self.get_view(sett, **kwargs)

   # Model Views

   @view_getter('ListOfFiles')
   def view(self, list_of_files, **kwargs):
      parent = kwargs['parent']
      gui_file_list = QtGui.QListView(parent)
      gui_file_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
      gui_file_list.setModel(list_of_files)
      return gui_file_list

   @view_getter('Piece')
   def view(self, piece, **kwargs):
      parent = kwargs['parent']
      grp_settings_for_piece = QtGui.QGroupBox(parent)
      grp_settings_for_piece.setTitle(self.translate(piece.description))
      ((lbl_title, line_title),
       chk_all_parts,
       chk_basso_seguente,
       widget_curr_pts_comb,
       (lbl_offset, line_offset, btn_offset),
       chk_salami
      ) = self.get_view(piece.settings, parent=grp_settings_for_piece)
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
      gridLayout_3.addWidget(self.get_view(piece.add_parts_combo,
                                           parent=grp_settings_for_piece),
                             9, 0, 1, 1)
      gridLayout_3.addWidget(line_offset, 0, 1, 1, 1)
      gridLayout_3.addWidget(lbl_offset, 0, 0, 1, 1)
      gridLayout_3.addWidget(btn_offset, 0, 2, 1, 1)
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
      verticalLayout_22.addWidget(chk_all_parts)
      verticalLayout_22.addWidget(chk_basso_seguente)
      horizontalLayout_9.addWidget(widget_part_boxes)
      gridLayout_3.addWidget(widget_2, 8, 0, 1, 3)
      gridLayout_3.addWidget(line_title, 5, 1, 1, 2)
      gridLayout_3.addWidget(lbl_title, 5, 0, 1, 1)
      gridLayout_3.addWidget(chk_salami, 1, 0, 1, 3)
      return grp_settings_for_piece

   @view_getter('ListOfPieces')
   def view(self, list_of_pieces, **kwargs):
      parent = kwargs['parent']
      gui_pieces_list = QtGui.QTableView(parent)
      gui_pieces_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      gui_pieces_list.horizontalHeader().setMinimumSectionSize(2)
      gui_pieces_list.verticalHeader().setVisible(False)
      gui_pieces_list.setModel(list_of_pieces)
      return gui_pieces_list

   @view_getter('VisInfo')
   def view(self, info):
      page_about = QtGui.QWidget()
      verticalLayout_5 = QtGui.QVBoxLayout(page_about)
      groupBox_4 = QtGui.QGroupBox(page_about)
      groupBox_4.setTitle(self.translate(info.title))
      verticalLayout_6 = QtGui.QVBoxLayout(groupBox_4)
      label_copyright = QtGui.QLabel(groupBox_4)
      label_copyright.setText(self.translate(info.copyright))
      verticalLayout_6.addWidget(label_copyright)
      line = QtGui.QFrame(groupBox_4)
      line.setFrameShape(QtGui.QFrame.HLine)
      line.setFrameShadow(QtGui.QFrame.Sunken)
      verticalLayout_6.addWidget(line)
      label_about = QtGui.QLabel(groupBox_4)
      label_about.setText(self.translate(info.about))
      verticalLayout_6.addWidget(label_about)
      verticalLayout_5.addWidget(groupBox_4)
      return page_about

   # Main Window Views

   @view_getter('VisController')
   def view(self, vis_controller):
      MainWindow = QtGui.QMainWindow()
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
      # TODO: extra buttons for progressing from Experiment to Visualization,
      # and implement their associated VisController methods
      spacerItem = QtGui.QSpacerItem(40,
                                     20,
                                     QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Minimum)
      horizontalLayout.addItem(spacerItem)
      horizontalLayout.addWidget(self.get_view(vis_controller.get_info,
                                               parent=function_menu))
      verticalLayout.addWidget(function_menu)
      verticalLayout.addWidget(self.get_view(vis_controller.set_active_controller,
                                             parent=centralwidget))
      MainWindow.setCentralWidget(centralwidget)
      statusbar = QtGui.QStatusBar(MainWindow)
      MainWindow.setStatusBar(statusbar)
      MainWindow.setWindowTitle(self.translate("vis"))
      MainWindow.setGeometry(300, 300, 250, 150)
      return MainWindow

   @view_getter('set_active_controller')
   def view(self, set_active_controller, **kwargs):
      # This is a bit weird -- maybe it should go in the
      # main VisController view-getter
      parent = kwargs['parent']
      vis_controller = set_active_controller.__self__
      main_screen = QtGui.QStackedWidget(parent)
      controllers = [
         vis_controller.importer,
         vis_controller.analyzer,
         vis_controller.experimenter,
      ]
      widgets = {
         controller.__class__.__name__: self.get_view(controller)
         for controller in controllers
      }
      for widget in widgets.itervalues():
         main_screen.addWidget(widget)
      def switch_widget(class_name):
         main_screen.setCurrentWidget(widgets[str(class_name)])
      vis_controller.active_controller_changed.connect(switch_widget)
      self.work_page = self.working_page()
      main_screen.addWidget(self.work_page)
      info_widget = self.get_view(vis_controller.info)
      main_screen.addWidget(info_widget)
      def info_requested():
         main_screen.setCurrentWidget(info_widget)
      vis_controller.info_signal.connect(info_requested)
      self.main_screen = main_screen
      main_screen.setCurrentIndex(0)
      return main_screen

   @view_getter('choose_files')
   def view(self, choose_files, **kwargs):
      btn_choose_files = self.make_tool_button(":/icons/icons/choose_files.png",
                                               64,
                                               "Choose Files",
                                               kwargs['parent'])
      btn_choose_files.setChecked(True)
      btn_choose_files.clicked.connect(choose_files)
      return btn_choose_files

   @view_getter('import_files')
   def view(self, import_files, **kwargs):
      btn_step1 = self.make_tool_button(":/icons/icons/right-arrow.png",
                                        32,
                                        "Continue to Step 2",
                                        kwargs['parent'])
      btn_step1.clicked.connect(import_files)
      return btn_step1

   @view_getter('setup_analysis')
   def view(self, setup_analysis, **kwargs):
      btn_analyze = self.make_tool_button(":/icons/icons/analyze.png",
                                          64,
                                          "Prepare and Assemble for Analysis",
                                          kwargs['parent'])
      btn_analyze.setEnabled(False)
      btn_analyze.setChecked(False)
      btn_analyze.clicked.connect(setup_analysis)
      return btn_analyze

   @view_getter('analyze_pieces')
   def view(self, analyze_pieces, **kwargs):
      btn_step2 = self.make_tool_button(":/icons/icons/right-arrow.png",
                                        32,
                                        "Continue to the Step 3",
                                        kwargs['parent'])
      btn_step2.setEnabled(False)
      btn_step2.clicked.connect(analyze_pieces)
      return btn_step2

   @view_getter('setup_experiment')
   def view(self, setup_experiment, **kwargs):
      btn_experiment = self.make_tool_button(":/icons/icons/show_results.png",
                                             64,
                                             "Show and Save Results",
                                             kwargs['parent'])
      btn_experiment.setEnabled(False)
      btn_experiment.clicked.connect(setup_experiment)
      return btn_experiment

   @view_getter('get_info')
   def view(self, get_info, **kwargs):
      btn_about = self.make_tool_button(":/icons/icons/help-about.png",
                                        64,
                                        "About \"vis\"",
                                        kwargs['parent'])
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
      files_list_view = self.get_view(importer.list_of_files, parent=widget_3)
      horizontalLayout_4.addWidget(self.get_view(importer.add_directories,
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
      horizontalLayout_7.addWidget(self.get_view(importer.start_import,
                                                 parent=widget_5))
      horizontalLayout_7.addWidget(self.get_view(importer.multiprocess,
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

   @view_getter('add_directories')
   def view(self, add_directories, **kwargs):
      btn_dir_add = self.make_push_button(":/icons/icons/add-dir.png",
                                          32,
                                          "Add Directory",
                                          kwargs['parent'])
      def on_click():
         d = QtGui.QFileDialog.getExistingDirectory(
            None,
            "Choose Directory to Analyze",
            '',
            QtGui.QFileDialog.ShowDirsOnly
         )
         add_directories(str(d))
      btn_dir_add.clicked.connect(on_click)
      return btn_dir_add

   @view_getter('add_files')
   def view(self, add_files, **kwargs):
      btn_file_add = self.make_push_button(":/icons/icons/add-file.png",
                                           32,
                                           "Add Files",
                                           kwargs['parent'])
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
                                              kwargs['parent'])
      def on_click():
         currently_selected = files_list.selectedIndexes()
         remove_files(currently_selected)
      btn_file_remove.clicked.connect(on_click)
      return btn_file_remove

   @view_getter('start_import')
   def view(self, start_import, **kwargs):
      parent = kwargs['parent']
      btn_import = QtGui.QPushButton(parent)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                     QtGui.QSizePolicy.Fixed)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(btn_import.sizePolicy().hasHeightForWidth())
      btn_import.setSizePolicy(sizePolicy)
      btn_import.setLayoutDirection(QtCore.Qt.LeftToRight)
      btn_import.setText(self.translate("Import Pieces"))
      btn_import.clicked.connect(start_import)
      return btn_import

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
      gridLayout_2.addWidget(self.get_view(analyzer.thread.list_of_pieces, parent=groupBox),
                             2, 0, 6, 3)
      gridLayout_2.addWidget(self.get_view(analyzer.current_piece, parent=groupBox),
                             6, 4, 2, 1)
      widget_6 = QtGui.QWidget(groupBox)
      horizontalLayout_5 = QtGui.QHBoxLayout(widget_6)
      horizontalLayout_5.setMargin(0)
      for widget in self.get_view(analyzer.thread.settings, parent=widget_6):
         horizontalLayout_5.addWidget(widget)
      horizontalLayout_5.addWidget(self.get_view(analyzer.analyze, parent=widget_6))
      gridLayout_2.addWidget(widget_6, 0, 4, 1, 1)
      verticalLayout_23.addWidget(groupBox)
      self.setup_thread(analyzer)
      return page_analyze

   @view_getter('load_statistics')
   def view(self, load_statistics, **kwargs):
      parent = kwargs['parent']
      btn_load_statistics = QtGui.QPushButton(parent)
      btn_load_statistics.setEnabled(False)
      btn_load_statistics.setText(self.translate("Load Existing Statistics Database"))
      btn_load_statistics.clicked.connect(load_statistics)
      return btn_load_statistics

   @view_getter('add_parts_combo')
   def view(self, add_parts_combo, **kwargs):
      parent = kwargs['parent']
      btn_add_check_combo = QtGui.QPushButton(parent)
      btn_add_check_combo.setEnabled(False)
      btn_add_check_combo.setText(self.translate("Add Combination"))
      # TODO: connect signals
      return btn_add_check_combo

   @view_getter('analyze')
   def view(self, analyze, **kwargs):
      parent = kwargs['parent']
      btn_analyze_now = QtGui.QPushButton(parent)
      btn_analyze_now.setText(self.translate("Analyze Voice Pairs"))
      # TODO: connect signals
      return btn_analyze_now

   # "Experiment" Frame Views

   @view_getter('set_experiment')
   def view(self, set_experiment, **kwargs):
      parent = kwargs['parent']
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
      def experiment_error(description):
         return self.error_popup(experimenter.__class__.__name__, description)
      experimenter.error.connect(experiment_error)
      return page_show
