# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/text_display.ui'
#
# Created: Fri May 10 11:55:57 2013
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

class Ui_Text_Display(object):
    def setupUi(self, Text_Display):
        Text_Display.setObjectName(_fromUtf8("Text_Display"))
        Text_Display.resize(600, 400)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Text_Display.sizePolicy().hasHeightForWidth())
        Text_Display.setSizePolicy(sizePolicy)
        Text_Display.setModal(False)
        self.verticalLayout = QtGui.QVBoxLayout(Text_Display)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = QtGui.QWidget(Text_Display)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.show_text = QtGui.QTextEdit(self.widget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier"))
        font.setPointSize(14)
        self.show_text.setFont(font)
        self.show_text.setReadOnly(True)
        self.show_text.setObjectName(_fromUtf8("show_text"))
        self.gridLayout.addWidget(self.show_text, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.widget)
        self.layout = QtGui.QWidget(Text_Display)
        self.layout.setObjectName(_fromUtf8("layout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layout)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(332, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btn_save_as = QtGui.QPushButton(self.layout)
        self.btn_save_as.setObjectName(_fromUtf8("btn_save_as"))
        self.horizontalLayout_2.addWidget(self.btn_save_as)
        self.btn_close = QtGui.QPushButton(self.layout)
        self.btn_close.setObjectName(_fromUtf8("btn_close"))
        self.horizontalLayout_2.addWidget(self.btn_close)
        self.verticalLayout.addWidget(self.layout)

        self.retranslateUi(Text_Display)
        QtCore.QMetaObject.connectSlotsByName(Text_Display)

    def retranslateUi(self, Text_Display):
        Text_Display.setWindowTitle(_translate("Text_Display", "Text Display", None))
        self.btn_save_as.setText(_translate("Text_Display", "Save As", None))
        self.btn_close.setText(_translate("Text_Display", "Close Window", None))

import icons_rc
