# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/compare_voice_pairs.ui'
#
# Created: Tue May 14 18:00:48 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_Compare_Voice_Pairs(object):
    def setupUi(self, Compare_Voice_Pairs):
        Compare_Voice_Pairs.setObjectName(_fromUtf8("Compare_Voice_Pairs"))
        Compare_Voice_Pairs.resize(551, 424)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Compare_Voice_Pairs.sizePolicy().hasHeightForWidth())
        Compare_Voice_Pairs.setSizePolicy(sizePolicy)
        Compare_Voice_Pairs.setModal(False)
        self.verticalLayout = QtGui.QVBoxLayout(Compare_Voice_Pairs)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = QtGui.QWidget(Compare_Voice_Pairs)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lbl_instructions = QtGui.QLabel(self.widget)
        self.lbl_instructions.setObjectName(_fromUtf8("lbl_instructions"))
        self.verticalLayout_2.addWidget(self.lbl_instructions)
        self.lbl_pairs_in_memory = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_pairs_in_memory.setFont(font)
        self.lbl_pairs_in_memory.setObjectName(_fromUtf8("lbl_pairs_in_memory"))
        self.verticalLayout_2.addWidget(self.lbl_pairs_in_memory)
        self.list_pairs_in_memory = QtGui.QTableView(self.widget)
        self.list_pairs_in_memory.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.list_pairs_in_memory.setObjectName(_fromUtf8("list_pairs_in_memory"))
        self.list_pairs_in_memory.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.list_pairs_in_memory)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(Compare_Voice_Pairs)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.gridLayout = QtGui.QGridLayout(self.widget_2)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.list_compare_these = QtGui.QTableView(self.widget_2)
        self.list_compare_these.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.list_compare_these.setAcceptDrops(True)
        self.list_compare_these.setObjectName(_fromUtf8("list_compare_these"))
        self.list_compare_these.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.list_compare_these, 1, 0, 1, 1)
        self.list_to_these = QtGui.QTableView(self.widget_2)
        self.list_to_these.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.list_to_these.setAcceptDrops(True)
        self.list_to_these.setObjectName(_fromUtf8("list_to_these"))
        self.list_to_these.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.list_to_these, 1, 1, 1, 1)
        self.lbl_compare_these = QtGui.QLabel(self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_compare_these.setFont(font)
        self.lbl_compare_these.setObjectName(_fromUtf8("lbl_compare_these"))
        self.gridLayout.addWidget(self.lbl_compare_these, 0, 0, 1, 1)
        self.lbl_to_these = QtGui.QLabel(self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_to_these.setFont(font)
        self.lbl_to_these.setObjectName(_fromUtf8("lbl_to_these"))
        self.gridLayout.addWidget(self.lbl_to_these, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.widget_2)
        self.widget_3 = QtGui.QWidget(Compare_Voice_Pairs)
        self.widget_3.setObjectName(_fromUtf8("widget_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(332, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btn_submit = QtGui.QPushButton(self.widget_3)
        self.btn_submit.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/show_checkmark.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_submit.setIcon(icon)
        self.btn_submit.setIconSize(QtCore.QSize(32, 32))
        self.btn_submit.setObjectName(_fromUtf8("btn_submit"))
        self.horizontalLayout_2.addWidget(self.btn_submit)
        self.verticalLayout.addWidget(self.widget_3)

        self.retranslateUi(Compare_Voice_Pairs)
        QtCore.QMetaObject.connectSlotsByName(Compare_Voice_Pairs)

    def retranslateUi(self, Compare_Voice_Pairs):
        Compare_Voice_Pairs.setWindowTitle(_translate("Compare_Voice_Pairs", "Select Voice Pairs to Compare", None))
        self.lbl_instructions.setText(_translate("Compare_Voice_Pairs", "Drag and drop the desired voice pairs from the top box to the two lower boxes.", None))
        self.lbl_pairs_in_memory.setText(_translate("Compare_Voice_Pairs", "Voice pairs in memory:", None))
        self.lbl_compare_these.setText(_translate("Compare_Voice_Pairs", "Compare these:", None))
        self.lbl_to_these.setText(_translate("Compare_Voice_Pairs", "to these:", None))

import icons_rc
