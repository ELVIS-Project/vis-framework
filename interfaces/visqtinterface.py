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
from interfaces import VisInterface, view_getter
from PyQt4 import QtCore, QtGui


class VisQtInterface(VisInterface):
   '''
   Interface for desktop app via PyQt4
   '''
   def __init__(self, argv):
      self.app = QtGui.QApplication(argv)
   
   def exec_(self):
      return self.app.exec_()
   
   def make_tool_button(self, icon_path, size, parent):
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
      return btn
   
   def make_push_button(self, icon_path, size, parent):
      btn = QtGui.QPushButton(parent)
      btn.setText("")
      icon = QtGui.QIcon()
      icon.addPixmap(QtGui.QPixmap(icon_path),
                      QtGui.QIcon.Normal,
                      QtGui.QIcon.Off)
      btn.setIcon(icon)
      btn.setIconSize(QtCore.QSize(size, size))
      btn.setFlat(True)
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
      horizontalLayout.addWidget(self.get_view(vis_controller.start_import,
                                               parent=function_menu))
      horizontalLayout.addWidget(self.get_view(vis_controller.setup_analysis,
                                               parent=function_menu))
      horizontalLayout.addWidget(self.get_view(vis_controller.start_analysis,
                                               parent=function_menu))
      horizontalLayout.addWidget(self.get_view(vis_controller.setup_experiment,
                                               parent=function_menu))
      spacerItem = QtGui.QSpacerItem(40,
                                     20,
                                     QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Minimum)
      horizontalLayout.addItem(spacerItem)
      horizontalLayout.addWidget(self.get_view(vis_controller.info,
                                               parent=function_menu))
      verticalLayout.addWidget(function_menu)
      main_screen = QtGui.QStackedWidget(centralwidget)
      main_screen.addWidget(self.get_view(vis_controller.importer))
      main_screen.addWidget(self.get_view(vis.controller.analyzer))
   
   @view_getter('_ChooseFiles')
   def view(self, choose_files, **kwargs):
      btn_choose_files = self.make_tool_button(":/icons/icons/choose_files.png",
                                               64,
                                               kwargs.pop('parent'))
      btn_choose_files.setChecked(True)
      # TODO: connect signals
      return btn_choose_files

   @view_getter('_StartImport')
   def view(self, start_import, **kwargs):
      btn_step1 = self.make_tool_button(":/icons/icons/right-arrow.png",
                                        32,
                                        kwargs.pop('parent'))
      # TODO: connect signals
      return btn_step1

   @view_getter('_SetupAnalysis')
   def view(self, setup_analysis, **kwargs):
      btn_analyze = self.make_tool_button(":/icons/icons/analyze.png",
                                          64,
                                          kwargs.pop('parent'))
      btn_analyze.setEnabled(False)
      btn_analyze.setChecked(False)
      # TODO: connect signals
      return btn_analyze

   @view_getter('_StartAnalysis')
   def view(self, start_analysis, **kwargs):
      btn_step2 = self.make_tool_button(":/icons/icons/right-arrow.png",
                                        32,
                                        kwargs.pop('parent'))
      btn_step2.setEnabled(False)
      # TODO: connect signals
      return btn_step2

   @view_getter('_SetupExperiment')
   def view(self, setup_experiment, **kwargs):
      btn_experiment = self.make_tool_button(":/icons/icons/show_results.png",
                                             64,
                                             kwargs.pop('parent'))
      btn_experiment.setEnabled(False)
      # TODO: connect signals
      return btn_experiment

   @view_getter('_Info')
   def view(self, info, **kwargs):
      btn_about = self.make_tool_button(":/icons/icons/help-about.png",
                                        64,
                                        kwargs.pop('parent'))
      # TODO: connect signals
      return btn_about
   
   # "Import" Frame Views
   
   @view_getter('Importer')
   def view(self, importer):
      page_choose = QtGui.QWidget()
      verticalLayout_2 = QtGui.QVBoxLayout(page_choose)
      grp_choose_files = QtGui.QGroupBox(page_choose)
      horizontalLayout_3 = QtGui.QHBoxLayout(grp_choose_files)
      widget_3 = QtGui.QWidget(grp_choose_files)
      verticalLayout_7 = QtGui.QVBoxLayout(widget_3)
      verticalLayout_7.setMargin(0)
      widget_4 = QtGui.QWidget(widget_3)
      horizontalLayout_4 = QtGui.QHBoxLayout(widget_4)
      horizontalLayout_4.setMargin(0)
      label_3 = QtGui.QLabel(widget_4)
      horizontalLayout_4.addWidget(label_3)
      spacerItem1 = QtGui.QSpacerItem(40,
                                      20,
                                      QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Minimum)
      horizontalLayout_4.addItem(spacerItem1)
      horizontalLayout_4.addWidget(self.get_view(importer.dir_adder,
                                                 parent=widget_4))
      horizontalLayout_4.addWidget(self.get_view(importer.file_adder,
                                                 parent=widget_4))
      horizontalLayout_4.addWidget(self.get_view(importer.file_remover,
                                                 parent=widget_4))
      verticalLayout_7.addWidget(widget_4)
      verticalLayout_7.addWidget(self.get_view(importer._list_of_files,
                                               parent=widget_3))
      widget_5 = QtGui.QWidget(widget_3)
      widget_5.setLayoutDirection(QtCore.Qt.RightToLeft)
      horizontalLayout_7 = QtGui.QHBoxLayout(widget_5)
      horizontalLayout_7.setMargin(0)
      horizontalLayout_7.addWidget(self.get_view(importer.file_importer,
                                                 parent=widget_5))
      horizontalLayout_7.addWidget(self.get_view(importer.multi_setter,
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
      # Maybe some signals here?
      return page_import
   
   @view_getter('_DirAdder')
   def view(self, dir_adder, **kwargs):
      btn_dir_add = self.make_push_button(":/icons/icons/add-dir.png",
                                          32,
                                          kwargs.pop('parent'))
      # TODO: connect signals
      return btn_dir_add
   
   @view_getter('_FileAdder')
   def view(self, file_adder, **kwargs):
      btn_file_add = self.make_push_button(":/icons/icons/add-file.png",
                                           32,
                                           kwargs.pop('parent'))
      # TODO: connect signals
      return btn_file_add
   
   @view_getter('_FileRemover')
   def view(self, file_remover, **kwargs):
      btn_file_remove = self.make_push_button(":/icons/icons/list-remove.png",
                                              32,
                                              kwargs.pop('parent'))
      # TODO: connect signals
      return btn_file_remove
   
   @view_getter('ListOfFiles')
   def view(self, list_of_files, **kwargs):
      parent = kwargs.pop('parent')
      gui_file_list = QtGui.QListView(parent)
      gui_file_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
      # TODO: connect signals
      return gui_file_list
   
   @view_getter('_FileImporter')
   def view(self, file_importer, **kwargs):
      parent = kwargs.pop('parent')
      btn_import = QtGui.QPushButton(parent)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                     QtGui.QSizePolicy.Fixed)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(btn_import.sizePolicy().hasHeightForWidth())
      btn_import.setSizePolicy(sizePolicy)
      btn_import.setLayoutDirection(QtCore.Qt.LeftToRight)
      # TODO: connect signals
      return btn_import
   
   @view_getter('_MultiImportSetter')
   def view(self, multi_setter, **kwargs):
      parent = kwargs.pop('parent')
      chk_multi_import = QtGui.QCheckBox(parent)
      chk_multi_import.setLayoutDirection(QtCore.Qt.LeftToRight)
      # TODO: connect signals
      return chk_multi_import
   
   # "Analyze" Frame Views
   
   @view_getter('Analyzer')
   def view(self, analyzer):
      page_analyze = QtGui.QWidget()
      verticalLayout_23 = QtGui.QVBoxLayout(page_analyze)
      groupBox = QtGui.QGroupBox(page_analyze)
      gridLayout_2 = QtGui.QGridLayout(groupBox)
      spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
      gridLayout_2.addItem(spacerItem3, 4, 4, 1, 1)
      
      btn_load_statistics = QtGui.QPushButton(groupBox)
      btn_load_statistics.setEnabled(False)
      
      gridLayout_2.addWidget(btn_load_statistics, 0, 0, 1, 1)
      
      spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
      gridLayout_2.addItem(spacerItem4, 0, 2, 1, 1)
      lbl_select_piece = QtGui.QLabel(groupBox)
      lbl_select_piece.setAlignment(QtCore.Qt.AlignCenter)
      gridLayout_2.addWidget(lbl_select_piece, 3, 4, 1, 1)
      spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
      gridLayout_2.addItem(spacerItem5, 2, 4, 1, 1)
      
      gui_pieces_list = QtGui.QTableView(groupBox)
      gui_pieces_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      gui_pieces_list.horizontalHeader().setMinimumSectionSize(2)
      gui_pieces_list.verticalHeader().setVisible(False)
      
      gridLayout_2.addWidget(gui_pieces_list, 2, 0, 6, 3)
      
      grp_settings_for_piece = QtGui.QGroupBox(groupBox)
      gridLayout_3 = QtGui.QGridLayout(grp_settings_for_piece)
      spacerItem6 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
      gridLayout_3.addItem(spacerItem6, 3, 1, 1, 1)
      spacerItem7 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
      gridLayout_3.addItem(spacerItem7, 6, 1, 1, 1)
      spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
      gridLayout_3.addItem(spacerItem8, 9, 1, 1, 2)
      
      btn_add_check_combo = QtGui.QPushButton(grp_settings_for_piece)
      btn_add_check_combo.setEnabled(False)
      
      gridLayout_3.addWidget(btn_add_check_combo, 9, 0, 1, 1)
      
      line_offset_interval = QtGui.QLineEdit(grp_settings_for_piece)
      line_offset_interval.setEnabled(False)
      line_offset_interval.setInputMask("")
      line_offset_interval.setMaxLength(256)
      
      gridLayout_3.addWidget(line_offset_interval, 0, 1, 1, 1)
      
      lbl_offset_interval = QtGui.QLabel(grp_settings_for_piece)
      gridLayout_3.addWidget(lbl_offset_interval, 0, 0, 1, 1)
      
      line_compare_these_parts = QtGui.QLineEdit(grp_settings_for_piece)
      line_compare_these_parts.setEnabled(False)
      line_compare_these_parts.setInputMask("")
      
      gridLayout_3.addWidget(line_compare_these_parts, 7, 1, 1, 2)
      
      lbl_compare_these_parts = QtGui.QLabel(grp_settings_for_piece)
      gridLayout_3.addWidget(lbl_compare_these_parts, 7, 0, 1, 1)
      
      btn_choose_note = QtGui.QPushButton(grp_settings_for_piece)
      btn_choose_note.setEnabled(False)
      
      gridLayout_3.addWidget(btn_choose_note, 0, 2, 1, 1)
      
      widget_2 = QtGui.QWidget(grp_settings_for_piece)
      horizontalLayout_9 = QtGui.QHBoxLayout(widget_2)
      horizontalLayout_9.setMargin(0)
      spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
      horizontalLayout_9.addItem(spacerItem9)
      widget_part_boxes = QtGui.QWidget(widget_2)
      verticalLayout_22 = QtGui.QVBoxLayout(widget_part_boxes)
      verticalLayout_22.setMargin(0)
      
      chk_all_voice_combos = QtGui.QCheckBox(widget_part_boxes)
      chk_all_voice_combos.setEnabled(False)
      
      verticalLayout_22.addWidget(chk_all_voice_combos)
      
      chk_basso_seguente = QtGui.QCheckBox(widget_part_boxes)
      chk_basso_seguente.setEnabled(False)
      
      verticalLayout_22.addWidget(chk_basso_seguente)
      
      horizontalLayout_9.addWidget(widget_part_boxes)
      gridLayout_3.addWidget(widget_2, 8, 0, 1, 3)
      
      line_piece_title = QtGui.QLineEdit(grp_settings_for_piece)
      
      gridLayout_3.addWidget(line_piece_title, 5, 1, 1, 2)
      
      lbl_piece_title = QtGui.QLabel(grp_settings_for_piece)
      gridLayout_3.addWidget(lbl_piece_title, 5, 0, 1, 1)
      
      chk_repeat_identical = QtGui.QCheckBox(grp_settings_for_piece)
      
      gridLayout_3.addWidget(chk_repeat_identical, 1, 0, 1, 3)
      
      gridLayout_2.addWidget(grp_settings_for_piece, 6, 4, 2, 1)
      widget_6 = QtGui.QWidget(groupBox)
      horizontalLayout_5 = QtGui.QHBoxLayout(widget_6)
      horizontalLayout_5.setMargin(0)
      
      chk_analyze_multi = QtGui.QCheckBox(widget_6)
      
      horizontalLayout_5.addWidget(chk_analyze_multi)
      
      btn_analyze_now = QtGui.QPushButton(widget_6)
      
      horizontalLayout_5.addWidget(btn_analyze_now)
      
      gridLayout_2.addWidget(widget_6, 0, 4, 1, 1)
      verticalLayout_23.addWidget(groupBox)
