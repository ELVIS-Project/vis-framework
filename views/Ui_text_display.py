# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/text_display.ui'
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

class Ui_Text_Display(object):
    def setupUi(self, Text_Display):
        Text_Display.setObjectName(_fromUtf8("Text_Display"))
        Text_Display.resize(816, 604)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Text_Display.sizePolicy().hasHeightForWidth())
        Text_Display.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/vis-1-32.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Text_Display.setWindowIcon(icon)
        Text_Display.setModal(False)
        self.verticalLayout = QtGui.QVBoxLayout(Text_Display)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.text_browser = QtGui.QTextBrowser(Text_Display)
        self.text_browser.setObjectName(_fromUtf8("text_browser"))
        self.verticalLayout.addWidget(self.text_browser)
        self.buttonBox = QtGui.QDialogButtonBox(Text_Display)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Text_Display)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Text_Display.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Text_Display.reject)
        QtCore.QMetaObject.connectSlotsByName(Text_Display)

    def retranslateUi(self, Text_Display):
        Text_Display.setWindowTitle(_translate("Text_Display", "Text Display", None))

import icons_rc
