# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/web_display.ui'
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

class Ui_Web_Display(object):
    def setupUi(self, Web_Display):
        Web_Display.setObjectName(_fromUtf8("Web_Display"))
        Web_Display.resize(814, 602)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Web_Display.sizePolicy().hasHeightForWidth())
        Web_Display.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/vis-1-32.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Web_Display.setWindowIcon(icon)
        Web_Display.setModal(False)
        self.verticalLayout = QtGui.QVBoxLayout(Web_Display)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.webview = QtWebKit.QWebView(Web_Display)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webview.sizePolicy().hasHeightForWidth())
        self.webview.setSizePolicy(sizePolicy)
        self.webview.setMouseTracking(False)
        self.webview.setAcceptDrops(False)
        self.webview.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webview.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.HighQualityAntialiasing|QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.webview.setObjectName(_fromUtf8("webview"))
        self.verticalLayout.addWidget(self.webview)
        self.widget = QtGui.QWidget(Web_Display)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.btn_png = QtGui.QPushButton(self.widget)
        self.btn_png.setObjectName(_fromUtf8("btn_png"))
        self.horizontalLayout.addWidget(self.btn_png)
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

        self.retranslateUi(Web_Display)
        QtCore.QObject.connect(self.btn_close, QtCore.SIGNAL(_fromUtf8("clicked()")), Web_Display.close)
        QtCore.QMetaObject.connectSlotsByName(Web_Display)

    def retranslateUi(self, Web_Display):
        Web_Display.setWindowTitle(_translate("Web_Display", "vis Results Display", None))
        self.label.setText(_translate("Web_Display", "Save as...", None))
        self.btn_png.setText(_translate("Web_Display", "&PNG Image", None))
        self.btn_csv.setText(_translate("Web_Display", "CS&V", None))
        self.btn_html.setText(_translate("Web_Display", "&Web Page", None))
        self.btn_excel.setText(_translate("Web_Display", "E&xcel", None))
        self.btn_close.setText(_translate("Web_Display", "&Close", None))

from PyQt4 import QtWebKit
import icons_rc
