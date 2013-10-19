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
        Text_Display.resize(814, 602)
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
        self.webview = QtWebKit.QWebView(Text_Display)
        self.webview.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webview.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.HighQualityAntialiasing|QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.webview.setObjectName(_fromUtf8("webview"))
        self.verticalLayout.addWidget(self.webview)
        self.widget = QtGui.QWidget(Text_Display)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.btn_csv = QtGui.QPushButton(self.widget)
        self.btn_csv.setObjectName(_fromUtf8("btn_csv"))
        self.horizontalLayout.addWidget(self.btn_csv)
        self.btn_html = QtGui.QPushButton(self.widget)
        self.btn_html.setObjectName(_fromUtf8("btn_html"))
        self.horizontalLayout.addWidget(self.btn_html)
        self.btn_excel = QtGui.QPushButton(self.widget)
        self.btn_excel.setObjectName(_fromUtf8("btn_excel"))
        self.horizontalLayout.addWidget(self.btn_excel)
        self.line = QtGui.QFrame(self.widget)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.btn_close = QtGui.QPushButton(self.widget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/dialog-close.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_close.setIcon(icon1)
        self.btn_close.setDefault(True)
        self.btn_close.setFlat(False)
        self.btn_close.setObjectName(_fromUtf8("btn_close"))
        self.horizontalLayout.addWidget(self.btn_close)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(Text_Display)
        QtCore.QObject.connect(self.btn_close, QtCore.SIGNAL(_fromUtf8("clicked()")), Text_Display.close)
        QtCore.QMetaObject.connectSlotsByName(Text_Display)

    def retranslateUi(self, Text_Display):
        Text_Display.setWindowTitle(_translate("Text_Display", "Text Display", None))
        self.label.setText(_translate("Text_Display", "Save as...", None))
        self.btn_csv.setText(_translate("Text_Display", "CSV", None))
        self.btn_html.setText(_translate("Text_Display", "Web Page", None))
        self.btn_excel.setText(_translate("Text_Display", "Excel", None))
        self.btn_close.setText(_translate("Text_Display", "Close", None))

from PyQt4 import QtWebKit
import icons_rc
