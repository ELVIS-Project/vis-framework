# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/text_display.ui'
#
# Created: Sat Jun  1 17:18:45 2013
#      by: PyQt4 UI code generator 4.10.1
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

class Ui_Text_Display(object):
    def setupUi(self, Text_Display):
        Text_Display.setObjectName(_fromUtf8("Text_Display"))
        Text_Display.resize(698, 491)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Text_Display.sizePolicy().hasHeightForWidth())
        Text_Display.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/vis-1-32.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Text_Display.setWindowIcon(icon)
        Text_Display.setModal(False)
        self.gridLayout_2 = QtGui.QGridLayout(Text_Display)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.btn_save_as = QtGui.QPushButton(Text_Display)
        self.btn_save_as.setObjectName(_fromUtf8("btn_save_as"))
        self.gridLayout_2.addWidget(self.btn_save_as, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(332, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)
        self.btn_close = QtGui.QPushButton(Text_Display)
        self.btn_close.setObjectName(_fromUtf8("btn_close"))
        self.gridLayout_2.addWidget(self.btn_close, 1, 2, 1, 1)
        self.show_text = QtGui.QTextEdit(Text_Display)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier"))
        font.setPointSize(14)
        self.show_text.setFont(font)
        self.show_text.setReadOnly(True)
        self.show_text.setObjectName(_fromUtf8("show_text"))
        self.gridLayout_2.addWidget(self.show_text, 0, 0, 1, 3)

        self.retranslateUi(Text_Display)
        QtCore.QMetaObject.connectSlotsByName(Text_Display)

    def retranslateUi(self, Text_Display):
        Text_Display.setWindowTitle(_translate("Text_Display", "Text Display", None))
        self.btn_save_as.setText(_translate("Text_Display", "Save &As", None))
        self.btn_close.setText(_translate("Text_Display", "&Close Window", None))

import icons_rc
