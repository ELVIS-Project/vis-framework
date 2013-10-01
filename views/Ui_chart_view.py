# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/chart_view.ui'
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

class Ui_vis_graph_view(object):
    def setupUi(self, vis_graph_view):
        vis_graph_view.setObjectName(_fromUtf8("vis_graph_view"))
        vis_graph_view.resize(816, 604)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/vis-1-128.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        vis_graph_view.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(vis_graph_view)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.graphics_view = QtGui.QGraphicsView(vis_graph_view)
        self.graphics_view.setObjectName(_fromUtf8("graphics_view"))
        self.verticalLayout.addWidget(self.graphics_view)
        self.buttonBox = QtGui.QDialogButtonBox(vis_graph_view)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(vis_graph_view)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), vis_graph_view.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), vis_graph_view.reject)
        QtCore.QMetaObject.connectSlotsByName(vis_graph_view)

    def retranslateUi(self, vis_graph_view):
        vis_graph_view.setWindowTitle(_translate("vis_graph_view", "vis Chart Viewer", None))

import icons_rc
