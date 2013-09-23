# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/main_window.ui'
#
# Created by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(947, 679)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/vis-1-512.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.function_menu = QtGui.QWidget(self.centralwidget)
        self.function_menu.setObjectName(_fromUtf8("function_menu"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.function_menu)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btn_choose_files = QtGui.QToolButton(self.function_menu)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/choose_files.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_choose_files.setIcon(icon1)
        self.btn_choose_files.setIconSize(QtCore.QSize(64, 64))
        self.btn_choose_files.setCheckable(True)
        self.btn_choose_files.setChecked(True)
        self.btn_choose_files.setAutoExclusive(True)
        self.btn_choose_files.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btn_choose_files.setAutoRaise(True)
        self.btn_choose_files.setObjectName(_fromUtf8("btn_choose_files"))
        self.horizontalLayout.addWidget(self.btn_choose_files)
        self.btn_step1 = QtGui.QToolButton(self.function_menu)
        self.btn_step1.setEnabled(True)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/right-arrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_step1.setIcon(icon2)
        self.btn_step1.setIconSize(QtCore.QSize(32, 32))
        self.btn_step1.setCheckable(False)
        self.btn_step1.setAutoRaise(True)
        self.btn_step1.setObjectName(_fromUtf8("btn_step1"))
        self.horizontalLayout.addWidget(self.btn_step1)
        self.btn_analyze = QtGui.QToolButton(self.function_menu)
        self.btn_analyze.setEnabled(False)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/analyze.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_analyze.setIcon(icon3)
        self.btn_analyze.setIconSize(QtCore.QSize(64, 64))
        self.btn_analyze.setCheckable(True)
        self.btn_analyze.setChecked(False)
        self.btn_analyze.setAutoExclusive(True)
        self.btn_analyze.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btn_analyze.setAutoRaise(True)
        self.btn_analyze.setObjectName(_fromUtf8("btn_analyze"))
        self.horizontalLayout.addWidget(self.btn_analyze)
        self.btn_step2 = QtGui.QToolButton(self.function_menu)
        self.btn_step2.setEnabled(False)
        self.btn_step2.setIcon(icon2)
        self.btn_step2.setIconSize(QtCore.QSize(32, 32))
        self.btn_step2.setCheckable(False)
        self.btn_step2.setAutoRaise(True)
        self.btn_step2.setObjectName(_fromUtf8("btn_step2"))
        self.horizontalLayout.addWidget(self.btn_step2)
        self.btn_experiment = QtGui.QToolButton(self.function_menu)
        self.btn_experiment.setEnabled(False)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/show_results.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_experiment.setIcon(icon4)
        self.btn_experiment.setIconSize(QtCore.QSize(64, 64))
        self.btn_experiment.setCheckable(True)
        self.btn_experiment.setAutoExclusive(True)
        self.btn_experiment.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btn_experiment.setAutoRaise(True)
        self.btn_experiment.setObjectName(_fromUtf8("btn_experiment"))
        self.horizontalLayout.addWidget(self.btn_experiment)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_about = QtGui.QToolButton(self.function_menu)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/help-about.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_about.setIcon(icon5)
        self.btn_about.setIconSize(QtCore.QSize(64, 64))
        self.btn_about.setCheckable(True)
        self.btn_about.setAutoExclusive(True)
        self.btn_about.setAutoRaise(True)
        self.btn_about.setObjectName(_fromUtf8("btn_about"))
        self.horizontalLayout.addWidget(self.btn_about)
        self.verticalLayout.addWidget(self.function_menu)
        self.main_screen = QtGui.QStackedWidget(self.centralwidget)
        self.main_screen.setObjectName(_fromUtf8("main_screen"))
        self.page_choose = QtGui.QWidget()
        self.page_choose.setObjectName(_fromUtf8("page_choose"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.page_choose)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.grp_choose_files = QtGui.QGroupBox(self.page_choose)
        self.grp_choose_files.setObjectName(_fromUtf8("grp_choose_files"))
        self.gridLayout_4 = QtGui.QGridLayout(self.grp_choose_files)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.grp_choose_files)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.btn_file_add = QtGui.QPushButton(self.grp_choose_files)
        self.btn_file_add.setText(_fromUtf8(""))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/add_files.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_file_add.setIcon(icon6)
        self.btn_file_add.setIconSize(QtCore.QSize(32, 32))
        self.btn_file_add.setFlat(True)
        self.btn_file_add.setObjectName(_fromUtf8("btn_file_add"))
        self.gridLayout_4.addWidget(self.btn_file_add, 0, 2, 1, 1)
        self.btn_file_remove = QtGui.QPushButton(self.grp_choose_files)
        self.btn_file_remove.setText(_fromUtf8(""))
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/list-remove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_file_remove.setIcon(icon7)
        self.btn_file_remove.setIconSize(QtCore.QSize(32, 32))
        self.btn_file_remove.setFlat(True)
        self.btn_file_remove.setObjectName(_fromUtf8("btn_file_remove"))
        self.gridLayout_4.addWidget(self.btn_file_remove, 0, 3, 1, 1)
        self.gui_file_list = QtGui.QListView(self.grp_choose_files)
        self.gui_file_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.gui_file_list.setObjectName(_fromUtf8("gui_file_list"))
        self.gridLayout_4.addWidget(self.gui_file_list, 2, 0, 2, 4)
        self.verticalLayout_2.addWidget(self.grp_choose_files)
        self.main_screen.addWidget(self.page_choose)
        self.page_analyze = QtGui.QWidget()
        self.page_analyze.setObjectName(_fromUtf8("page_analyze"))
        self.verticalLayout_23 = QtGui.QVBoxLayout(self.page_analyze)
        self.verticalLayout_23.setObjectName(_fromUtf8("verticalLayout_23"))
        self.groupBox = QtGui.QGroupBox(self.page_analyze)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.grp_settings_for_piece = QtGui.QGroupBox(self.groupBox)
        self.grp_settings_for_piece.setObjectName(_fromUtf8("grp_settings_for_piece"))
        self.gridLayout_3 = QtGui.QGridLayout(self.grp_settings_for_piece)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.btn_add_check_combo = QtGui.QPushButton(self.grp_settings_for_piece)
        self.btn_add_check_combo.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_add_check_combo.sizePolicy().hasHeightForWidth())
        self.btn_add_check_combo.setSizePolicy(sizePolicy)
        self.btn_add_check_combo.setObjectName(_fromUtf8("btn_add_check_combo"))
        self.gridLayout_3.addWidget(self.btn_add_check_combo, 8, 0, 1, 1)
        self.line_offset_interval = QtGui.QLineEdit(self.grp_settings_for_piece)
        self.line_offset_interval.setEnabled(False)
        self.line_offset_interval.setInputMask(_fromUtf8(""))
        self.line_offset_interval.setMaxLength(256)
        self.line_offset_interval.setObjectName(_fromUtf8("line_offset_interval"))
        self.gridLayout_3.addWidget(self.line_offset_interval, 0, 1, 1, 1)
        self.lbl_offset_interval = QtGui.QLabel(self.grp_settings_for_piece)
        self.lbl_offset_interval.setObjectName(_fromUtf8("lbl_offset_interval"))
        self.gridLayout_3.addWidget(self.lbl_offset_interval, 0, 0, 1, 1)
        self.line_compare_these_parts = QtGui.QLineEdit(self.grp_settings_for_piece)
        self.line_compare_these_parts.setEnabled(False)
        self.line_compare_these_parts.setInputMask(_fromUtf8(""))
        self.line_compare_these_parts.setObjectName(_fromUtf8("line_compare_these_parts"))
        self.gridLayout_3.addWidget(self.line_compare_these_parts, 6, 1, 1, 2)
        self.lbl_compare_these_parts = QtGui.QLabel(self.grp_settings_for_piece)
        self.lbl_compare_these_parts.setObjectName(_fromUtf8("lbl_compare_these_parts"))
        self.gridLayout_3.addWidget(self.lbl_compare_these_parts, 6, 0, 1, 1)
        self.btn_choose_note = QtGui.QPushButton(self.grp_settings_for_piece)
        self.btn_choose_note.setEnabled(False)
        self.btn_choose_note.setObjectName(_fromUtf8("btn_choose_note"))
        self.gridLayout_3.addWidget(self.btn_choose_note, 0, 2, 1, 1)
        self.widget_2 = QtGui.QWidget(self.grp_settings_for_piece)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout_9.setMargin(0)
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.widget_part_boxes = QtGui.QScrollArea(self.widget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_part_boxes.sizePolicy().hasHeightForWidth())
        self.widget_part_boxes.setSizePolicy(sizePolicy)
        self.widget_part_boxes.setFrameShape(QtGui.QFrame.NoFrame)
        self.widget_part_boxes.setFrameShadow(QtGui.QFrame.Plain)
        self.widget_part_boxes.setWidgetResizable(True)
        self.widget_part_boxes.setObjectName(_fromUtf8("widget_part_boxes"))
        self.part_box_widget = QtGui.QWidget()
        self.part_box_widget.setGeometry(QtCore.QRect(0, 0, 384, 76))
        self.part_box_widget.setObjectName(_fromUtf8("part_box_widget"))
        self.verticalLayout_part_boxes = QtGui.QVBoxLayout(self.part_box_widget)
        self.verticalLayout_part_boxes.setObjectName(_fromUtf8("verticalLayout_part_boxes"))
        self.chk_all_voices = QtGui.QCheckBox(self.part_box_widget)
        self.chk_all_voices.setEnabled(False)
        self.chk_all_voices.setObjectName(_fromUtf8("chk_all_voices"))
        self.verticalLayout_part_boxes.addWidget(self.chk_all_voices)
        self.chk_all_voice_combos = QtGui.QCheckBox(self.part_box_widget)
        self.chk_all_voice_combos.setEnabled(False)
        self.chk_all_voice_combos.setObjectName(_fromUtf8("chk_all_voice_combos"))
        self.verticalLayout_part_boxes.addWidget(self.chk_all_voice_combos)
        self.widget_part_boxes.setWidget(self.part_box_widget)
        self.horizontalLayout_9.addWidget(self.widget_part_boxes)
        self.gridLayout_3.addWidget(self.widget_2, 7, 0, 1, 3)
        self.line_piece_title = QtGui.QLineEdit(self.grp_settings_for_piece)
        self.line_piece_title.setObjectName(_fromUtf8("line_piece_title"))
        self.gridLayout_3.addWidget(self.line_piece_title, 4, 1, 1, 2)
        self.lbl_piece_title = QtGui.QLabel(self.grp_settings_for_piece)
        self.lbl_piece_title.setObjectName(_fromUtf8("lbl_piece_title"))
        self.gridLayout_3.addWidget(self.lbl_piece_title, 4, 0, 1, 1)
        self.chk_repeat_identical = QtGui.QCheckBox(self.grp_settings_for_piece)
        self.chk_repeat_identical.setObjectName(_fromUtf8("chk_repeat_identical"))
        self.gridLayout_3.addWidget(self.chk_repeat_identical, 1, 0, 1, 3)
        self.grp_quality = QtGui.QGroupBox(self.grp_settings_for_piece)
        self.grp_quality.setObjectName(_fromUtf8("grp_quality"))
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.grp_quality)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.rdo_heedQuality = QtGui.QRadioButton(self.grp_quality)
        self.rdo_heedQuality.setObjectName(_fromUtf8("rdo_heedQuality"))
        self.verticalLayout_10.addWidget(self.rdo_heedQuality)
        self.rdo_noHeedQuality = QtGui.QRadioButton(self.grp_quality)
        self.rdo_noHeedQuality.setChecked(True)
        self.rdo_noHeedQuality.setObjectName(_fromUtf8("rdo_noHeedQuality"))
        self.verticalLayout_10.addWidget(self.rdo_noHeedQuality)
        self.gridLayout_3.addWidget(self.grp_quality, 9, 0, 1, 1)
        self.grp_octaves = QtGui.QGroupBox(self.grp_settings_for_piece)
        self.grp_octaves.setObjectName(_fromUtf8("grp_octaves"))
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.grp_octaves)
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.rdo_compound = QtGui.QRadioButton(self.grp_octaves)
        self.rdo_compound.setChecked(True)
        self.rdo_compound.setObjectName(_fromUtf8("rdo_compound"))
        self.verticalLayout_13.addWidget(self.rdo_compound)
        self.rdo_simple = QtGui.QRadioButton(self.grp_octaves)
        self.rdo_simple.setObjectName(_fromUtf8("rdo_simple"))
        self.verticalLayout_13.addWidget(self.rdo_simple)
        self.gridLayout_3.addWidget(self.grp_octaves, 9, 1, 1, 1)
        self.gridLayout_2.addWidget(self.grp_settings_for_piece, 1, 2, 1, 1)
        self.widget_select_piece = QtGui.QWidget(self.groupBox)
        self.widget_select_piece.setObjectName(_fromUtf8("widget_select_piece"))
        self.verticalLayout_16 = QtGui.QVBoxLayout(self.widget_select_piece)
        self.verticalLayout_16.setMargin(0)
        self.verticalLayout_16.setObjectName(_fromUtf8("verticalLayout_16"))
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_16.addItem(spacerItem3)
        self.lbl_select_piece = QtGui.QLabel(self.widget_select_piece)
        self.lbl_select_piece.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_select_piece.setObjectName(_fromUtf8("lbl_select_piece"))
        self.verticalLayout_16.addWidget(self.lbl_select_piece)
        spacerItem4 = QtGui.QSpacerItem(20, 37, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_16.addItem(spacerItem4)
        self.gridLayout_2.addWidget(self.widget_select_piece, 4, 2, 1, 1)
        self.widget_6 = QtGui.QWidget(self.groupBox)
        self.widget_6.setObjectName(_fromUtf8("widget_6"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.widget_6)
        self.horizontalLayout_5.setMargin(0)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.gridLayout_2.addWidget(self.widget_6, 0, 2, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem5, 0, 0, 1, 1)
        class GuiPiecesList(QtGui.QTableView):
            selection_changed = QtCore.pyqtSignal()
            def selectionChanged(self, selected, deselected):
                self.selection_changed.emit()
                super(GuiPiecesList, self).selectionChanged(selected, deselected)
        self.gui_pieces_list = GuiPiecesList(self.groupBox)
        self.gui_pieces_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.gui_pieces_list.setObjectName(_fromUtf8("gui_pieces_list"))
        self.gui_pieces_list.horizontalHeader().setMinimumSectionSize(2)
        self.gui_pieces_list.verticalHeader().setVisible(False)
        self.gridLayout_2.addWidget(self.gui_pieces_list, 1, 0, 5, 1)
        self.verticalLayout_23.addWidget(self.groupBox)
        self.main_screen.addWidget(self.page_analyze)
        self.page_show = QtGui.QWidget()
        self.page_show.setObjectName(_fromUtf8("page_show"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.page_show)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.groupBox_2 = QtGui.QGroupBox(self.page_show)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem6, 5, 1, 1, 1)
        self.groupBox_5 = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.rdo_spreadsheet = QtGui.QRadioButton(self.groupBox_5)
        self.rdo_spreadsheet.setChecked(True)
        self.rdo_spreadsheet.setObjectName(_fromUtf8("rdo_spreadsheet"))
        self.verticalLayout_9.addWidget(self.rdo_spreadsheet)
        self.rdo_list = QtGui.QRadioButton(self.groupBox_5)
        self.rdo_list.setEnabled(True)
        self.rdo_list.setObjectName(_fromUtf8("rdo_list"))
        self.verticalLayout_9.addWidget(self.rdo_list)
        self.rdo_chart = QtGui.QRadioButton(self.groupBox_5)
        self.rdo_chart.setEnabled(True)
        self.rdo_chart.setObjectName(_fromUtf8("rdo_chart"))
        self.verticalLayout_9.addWidget(self.rdo_chart)
        self.rdo_score = QtGui.QRadioButton(self.groupBox_5)
        self.rdo_score.setEnabled(True)
        self.rdo_score.setObjectName(_fromUtf8("rdo_score"))
        self.verticalLayout_9.addWidget(self.rdo_score)
        self.gridLayout.addWidget(self.groupBox_5, 0, 1, 1, 1)
        self.groupBox_7 = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.rdo_consider_intervals = QtGui.QRadioButton(self.groupBox_7)
        self.rdo_consider_intervals.setEnabled(True)
        self.rdo_consider_intervals.setChecked(True)
        self.rdo_consider_intervals.setObjectName(_fromUtf8("rdo_consider_intervals"))
        self.verticalLayout_11.addWidget(self.rdo_consider_intervals)
        self.rdo_consider_interval_ngrams = QtGui.QRadioButton(self.groupBox_7)
        self.rdo_consider_interval_ngrams.setEnabled(True)
        self.rdo_consider_interval_ngrams.setChecked(False)
        self.rdo_consider_interval_ngrams.setObjectName(_fromUtf8("rdo_consider_interval_ngrams"))
        self.verticalLayout_11.addWidget(self.rdo_consider_interval_ngrams)
        self.rdo_consider_score = QtGui.QRadioButton(self.groupBox_7)
        self.rdo_consider_score.setObjectName(_fromUtf8("rdo_consider_score"))
        self.verticalLayout_11.addWidget(self.rdo_consider_score)
        self.gridLayout.addWidget(self.groupBox_7, 0, 0, 1, 1)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem7, 5, 0, 1, 1)
        self.grp_values_of_n = QtGui.QGroupBox(self.groupBox_2)
        self.grp_values_of_n.setObjectName(_fromUtf8("grp_values_of_n"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.grp_values_of_n)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label = QtGui.QLabel(self.grp_values_of_n)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_4.addWidget(self.label)
        self.line_values_of_n = QtGui.QLineEdit(self.grp_values_of_n)
        self.line_values_of_n.setObjectName(_fromUtf8("line_values_of_n"))
        self.verticalLayout_4.addWidget(self.line_values_of_n)
        self.gridLayout.addWidget(self.grp_values_of_n, 0, 2, 1, 1)
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem8, 5, 2, 1, 1)
        self.grp_ignore_inversion = QtGui.QGroupBox(self.groupBox_2)
        self.grp_ignore_inversion.setObjectName(_fromUtf8("grp_ignore_inversion"))
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.grp_ignore_inversion)
        self.verticalLayout_14.setObjectName(_fromUtf8("verticalLayout_14"))
        self.chk_ignore_inversion = QtGui.QCheckBox(self.grp_ignore_inversion)
        self.chk_ignore_inversion.setObjectName(_fromUtf8("chk_ignore_inversion"))
        self.verticalLayout_14.addWidget(self.chk_ignore_inversion)
        self.gridLayout.addWidget(self.grp_ignore_inversion, 2, 2, 1, 1)
        self.group_threshold = QtGui.QGroupBox(self.groupBox_2)
        self.group_threshold.setObjectName(_fromUtf8("group_threshold"))
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.group_threshold)
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.label_5 = QtGui.QLabel(self.group_threshold)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_12.addWidget(self.label_5)
        self.line_threshold = QtGui.QLineEdit(self.group_threshold)
        self.line_threshold.setObjectName(_fromUtf8("line_threshold"))
        self.verticalLayout_12.addWidget(self.line_threshold)
        self.gridLayout.addWidget(self.group_threshold, 2, 1, 1, 1)
        self.group_top_x = QtGui.QGroupBox(self.groupBox_2)
        self.group_top_x.setObjectName(_fromUtf8("group_top_x"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.group_top_x)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.label_2 = QtGui.QLabel(self.group_top_x)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_8.addWidget(self.label_2)
        self.line_top_x = QtGui.QLineEdit(self.group_top_x)
        self.line_top_x.setObjectName(_fromUtf8("line_top_x"))
        self.verticalLayout_8.addWidget(self.line_top_x)
        self.label_4 = QtGui.QLabel(self.group_top_x)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_8.addWidget(self.label_4)
        self.gridLayout.addWidget(self.group_top_x, 2, 0, 1, 1)
        self.grp_annotate_these = QtGui.QGroupBox(self.groupBox_2)
        self.grp_annotate_these.setObjectName(_fromUtf8("grp_annotate_these"))
        self.verticalLayout_15 = QtGui.QVBoxLayout(self.grp_annotate_these)
        self.verticalLayout_15.setObjectName(_fromUtf8("verticalLayout_15"))
        self.label_6 = QtGui.QLabel(self.grp_annotate_these)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout_15.addWidget(self.label_6)
        self.line_annotate_these = QtGui.QLineEdit(self.grp_annotate_these)
        self.line_annotate_these.setObjectName(_fromUtf8("line_annotate_these"))
        self.verticalLayout_15.addWidget(self.line_annotate_these)
        self.gridLayout.addWidget(self.grp_annotate_these, 3, 2, 1, 1)
        self.btn_show_results = QtGui.QPushButton(self.groupBox_2)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/show_checkmark.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_show_results.setIcon(icon8)
        self.btn_show_results.setIconSize(QtCore.QSize(64, 64))
        self.btn_show_results.setObjectName(_fromUtf8("btn_show_results"))
        self.gridLayout.addWidget(self.btn_show_results, 5, 3, 1, 1)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.main_screen.addWidget(self.page_show)
        self.page_working = QtGui.QWidget()
        self.page_working.setObjectName(_fromUtf8("page_working"))
        self.verticalLayout_21 = QtGui.QVBoxLayout(self.page_working)
        self.verticalLayout_21.setObjectName(_fromUtf8("verticalLayout_21"))
        spacerItem9 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_21.addItem(spacerItem9)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        spacerItem10 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem10)
        self.btn_wait_clock = QtGui.QPushButton(self.page_working)
        self.btn_wait_clock.setEnabled(True)
        self.btn_wait_clock.setText(_fromUtf8(""))
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/working.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_wait_clock.setIcon(icon9)
        self.btn_wait_clock.setIconSize(QtCore.QSize(64, 64))
        self.btn_wait_clock.setCheckable(False)
        self.btn_wait_clock.setChecked(False)
        self.btn_wait_clock.setFlat(True)
        self.btn_wait_clock.setObjectName(_fromUtf8("btn_wait_clock"))
        self.horizontalLayout_8.addWidget(self.btn_wait_clock)
        spacerItem11 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem11)
        self.verticalLayout_21.addLayout(self.horizontalLayout_8)
        self.lbl_status_text = QtGui.QLabel(self.page_working)
        self.lbl_status_text.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.lbl_status_text.setObjectName(_fromUtf8("lbl_status_text"))
        self.verticalLayout_21.addWidget(self.lbl_status_text)
        self.progress_bar = QtGui.QProgressBar(self.page_working)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.verticalLayout_21.addWidget(self.progress_bar)
        self.lbl_currently_processing = QtGui.QLabel(self.page_working)
        self.lbl_currently_processing.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.lbl_currently_processing.setObjectName(_fromUtf8("lbl_currently_processing"))
        self.verticalLayout_21.addWidget(self.lbl_currently_processing)
        spacerItem12 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_21.addItem(spacerItem12)
        self.btn_cancel_operation = QtGui.QPushButton(self.page_working)
        self.btn_cancel_operation.setObjectName(_fromUtf8("btn_cancel_operation"))
        self.verticalLayout_21.addWidget(self.btn_cancel_operation)
        self.main_screen.addWidget(self.page_working)
        self.page_about = QtGui.QWidget()
        self.page_about.setObjectName(_fromUtf8("page_about"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.page_about)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.groupBox_4 = QtGui.QGroupBox(self.page_about)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.label_copyright = QtGui.QLabel(self.groupBox_4)
        self.label_copyright.setObjectName(_fromUtf8("label_copyright"))
        self.verticalLayout_6.addWidget(self.label_copyright)
        self.line = QtGui.QFrame(self.groupBox_4)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_6.addWidget(self.line)
        self.label_about = QtGui.QLabel(self.groupBox_4)
        self.label_about.setObjectName(_fromUtf8("label_about"))
        self.verticalLayout_6.addWidget(self.label_about)
        self.verticalLayout_5.addWidget(self.groupBox_4)
        self.main_screen.addWidget(self.page_about)
        self.verticalLayout.addWidget(self.main_screen)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.main_screen.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "vis", None))
        self.btn_choose_files.setToolTip(_translate("MainWindow", "Choose Files", None))
        self.btn_choose_files.setText(_translate("MainWindow", "Importer", None))
        self.btn_step1.setToolTip(_translate("MainWindow", "Continue to Step 2", None))
        self.btn_analyze.setToolTip(_translate("MainWindow", "Prepare and Assemble for Analysis", None))
        self.btn_analyze.setText(_translate("MainWindow", "Analyzer", None))
        self.btn_step2.setToolTip(_translate("MainWindow", "Continue to the Step 3", None))
        self.btn_experiment.setToolTip(_translate("MainWindow", "Show and Save Results", None))
        self.btn_experiment.setText(_translate("MainWindow", "Experimenter", None))
        self.btn_about.setToolTip(_translate("MainWindow", "About \"vis\"", None))
        self.label_3.setText(_translate("MainWindow", "Add files to the list so they will be imported.", None))
        self.btn_file_add.setToolTip(_translate("MainWindow", "Add Files", None))
        self.btn_file_remove.setToolTip(_translate("MainWindow", "Remove Selected Items", None))
        self.grp_settings_for_piece.setTitle(_translate("MainWindow", "Settings for Selected Piece", None))
        self.btn_add_check_combo.setText(_translate("MainWindow", "&Add Combination", None))
        self.line_offset_interval.setText(_translate("MainWindow", "(optional)", None))
        self.lbl_offset_interval.setText(_translate("MainWindow", "Offset Interval:", None))
        self.line_compare_these_parts.setText(_translate("MainWindow", "e.g., [0,3] or [[0,3],[1,3]]", None))
        self.lbl_compare_these_parts.setText(_translate("MainWindow", "Compare These Parts:", None))
        self.btn_choose_note.setText(_translate("MainWindow", "Choose Offset Note", None))
        self.chk_all_voices.setText(_translate("MainWindow", "All Voices", None))
        self.chk_all_voice_combos.setToolTip(_translate("MainWindow", "Collect Statistics for all Part Combinations", None))
        self.chk_all_voice_combos.setText(_translate("MainWindow", "All Voice Pairs", None))
        self.lbl_piece_title.setText(_translate("MainWindow", "Piece Title:", None))
        self.chk_repeat_identical.setText(_translate("MainWindow", "Repeat consecutive identical events", None))
        self.grp_quality.setTitle(_translate("MainWindow", "Interval Quality", None))
        self.rdo_heedQuality.setText(_translate("MainWindow", "Display", None))
        self.rdo_noHeedQuality.setText(_translate("MainWindow", "Ignore", None))
        self.grp_octaves.setTitle(_translate("MainWindow", "Octaves", None))
        self.rdo_compound.setText(_translate("MainWindow", "Compound Intervals", None))
        self.rdo_simple.setText(_translate("MainWindow", "Simple Intervals", None))
        self.lbl_select_piece.setText(_translate("MainWindow", "Select piece(s) to see possible settings.", None))
        self.groupBox_5.setTitle(_translate("MainWindow", "How to Show Results", None))
        self.rdo_spreadsheet.setText(_translate("MainWindow", "Spreadsheet", None))
        self.rdo_list.setText(_translate("MainWindow", "List", None))
        self.rdo_chart.setText(_translate("MainWindow", "Chart/Graph", None))
        self.rdo_score.setText(_translate("MainWindow", "Score", None))
        self.groupBox_7.setTitle(_translate("MainWindow", "Object to Consider", None))
        self.rdo_consider_intervals.setText(_translate("MainWindow", "Intervals", None))
        self.rdo_consider_interval_ngrams.setText(_translate("MainWindow", "Interval N-grams", None))
        self.rdo_consider_score.setText(_translate("MainWindow", "Score", None))
        self.grp_values_of_n.setTitle(_translate("MainWindow", "Value of N", None))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p>The length of the n-gram you wish to produce.</p></body></html>", None))
        self.grp_ignore_inversion.setTitle(_translate("MainWindow", "Voice Crossing", None))
        self.chk_ignore_inversion.setText(_translate("MainWindow", "Ignore", None))
        self.group_threshold.setTitle(_translate("MainWindow", "Threshold Filter", None))
        self.label_5.setText(_translate("MainWindow", "<html><head/><body><p>Do not show results<br/>with fewer than this<br/>many occurrences:</p></body></html>", None))
        self.group_top_x.setTitle(_translate("MainWindow", "\"Top X\" Filter", None))
        self.label_2.setText(_translate("MainWindow", "Show only the ...", None))
        self.label_4.setText(_translate("MainWindow", "... highest results", None))
        self.grp_annotate_these.setTitle(_translate("MainWindow", "Annotate This N-Gram", None))
        self.label_6.setText(_translate("MainWindow", "<html><head/><body><p>Only the n-gram whose text matches the</p><p>text inputted below will be annotated on</p><p>the outputted score.</p></body></html>", None))
        self.btn_show_results.setText(_translate("MainWindow", "Process and &Show", None))
        self.btn_wait_clock.setToolTip(_translate("MainWindow", "Hi, mom!", None))
        self.lbl_status_text.setText(_translate("MainWindow", "Please wait...", None))
        self.lbl_currently_processing.setText(_translate("MainWindow", "(processing)", None))
        self.btn_cancel_operation.setText(_translate("MainWindow", "Cancel Operation", None))
        self.groupBox_4.setTitle(_translate("MainWindow", "Information about vis", None))
        self.label_copyright.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" text-decoration: underline;\">vis X-devel (&quot;Unstable&quot; Desktop Development Version)</span></p><p>Copyright (c) 2012, 2013 Christopher Antila, Jamie Klassen, Alexander Morgan, Saining Li</p><p>This program is free software: you can redistribute it and/or modify<br/>it under the terms of the GNU Affero General Public License as<br/>published by the Free Software Foundation, either version 3 of the<br/>License, or (at your option) any later version.</p><p>This program is distributed in the hope that it will be useful,<br/>but WITHOUT ANY WARRANTY; without even the implied warranty of<br/>MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<br/>GNU Affero General Public License for more details.</p><p>You should have received a copy of the GNU Affero General Public License<br/>along with this program.  If not, see &lt;http://www.gnu.org/licenses/&gt;.</p></body></html>", None))
        self.label_about.setText(_translate("MainWindow", "<html><head/><body><p>vis was written as part of McGill University\'s contribution to the ELVIS project.<br/>For more information about ELVIS, please refer to our <a href=\"http://elvis.music.mcgill.ca/\"><span style=\" text-decoration: underline; color:#0057ae;\">web site</span></a>.</p><p>Funding for ELVIS was provided by the following organizations:<br/>- SSHRC (Social Sciences and Humanities Research Council) of Canada<br/>- NEH (National Endowment for the Humanities) of the United States of America<br/>- The Digging into Data Challenge</p><p>vis is written in the Python programming language, and relies on the following<br/>software, all released under free licences:<br/>- <a href=\"http://mit.edu/music21/\"><span style=\" text-decoration: underline; color:#0057ae;\">music21<br/></span></a>- <a href=\"http://www.riverbankcomputing.co.uk/software/pyqt/download\"><span style=\" text-decoration: underline; color:#0057ae;\">PyQt4</span></a><br/>- <a href=\"http://www.oxygen-icons.org/\"><span style=\" text-decoration: underline; color:#0057ae;\">Oxygen Icons</span></a></p></body></html>", None))

import icons_rc
