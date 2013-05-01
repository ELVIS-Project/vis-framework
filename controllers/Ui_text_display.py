# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'text_display.ui'
#
# Created: Fri Oct 12 19:04:04 2012
# by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

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
        Text_Display.setWindowTitle(QtGui.QApplication.translate("Text_Display", "Text Display", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_save_as.setText(QtGui.QApplication.translate("Text_Display", "Save As", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_close.setText(QtGui.QApplication.translate("Text_Display", "Close Window", None, QtGui.QApplication.UnicodeUTF8))

#import icons_rc
