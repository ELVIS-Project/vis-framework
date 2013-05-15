# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/select_voices.ui'
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

class Ui_select_voices(object):
    def setupUi(self, select_voices):
        select_voices.setObjectName(_fromUtf8("select_voices"))
        select_voices.setWindowModality(QtCore.Qt.ApplicationModal)
        select_voices.resize(457, 223)
        self.verticalLayout = QtGui.QVBoxLayout(select_voices)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = QtGui.QWidget(select_voices)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.widget_5 = QtGui.QWidget(self.widget)
        self.widget_5.setObjectName(_fromUtf8("widget_5"))
        self.gridLayout = QtGui.QGridLayout(self.widget_5)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.rdo_all = QtGui.QRadioButton(self.widget_5)
        self.rdo_all.setChecked(True)
        self.rdo_all.setObjectName(_fromUtf8("rdo_all"))
        self.gridLayout.addWidget(self.rdo_all, 0, 0, 1, 1)
        self.rdo_these_parts = QtGui.QRadioButton(self.widget_5)
        self.rdo_these_parts.setObjectName(_fromUtf8("rdo_these_parts"))
        self.gridLayout.addWidget(self.rdo_these_parts, 1, 0, 1, 1)
        self.line_these_parts = QtGui.QLineEdit(self.widget_5)
        self.line_these_parts.setEnabled(False)
        self.line_these_parts.setMinimumSize(QtCore.QSize(148, 0))
        self.line_these_parts.setObjectName(_fromUtf8("line_these_parts"))
        self.gridLayout.addWidget(self.line_these_parts, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.rdo_part_and_bs = QtGui.QRadioButton(self.widget_5)
        self.rdo_part_and_bs.setObjectName(_fromUtf8("rdo_part_and_bs"))
        self.gridLayout.addWidget(self.rdo_part_and_bs, 2, 0, 1, 1)
        self.line_part_and_bs = QtGui.QLineEdit(self.widget_5)
        self.line_part_and_bs.setEnabled(False)
        self.line_part_and_bs.setMinimumSize(QtCore.QSize(148, 0))
        self.line_part_and_bs.setObjectName(_fromUtf8("line_part_and_bs"))
        self.gridLayout.addWidget(self.line_part_and_bs, 2, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 2, 1, 1)
        self.rdo_choose_these = QtGui.QRadioButton(self.widget_5)
        self.rdo_choose_these.setObjectName(_fromUtf8("rdo_choose_these"))
        self.gridLayout.addWidget(self.rdo_choose_these, 3, 0, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 3, 1, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 3, 2, 1, 1)
        self.verticalLayout_2.addWidget(self.widget_5)
        self.widget_7 = QtGui.QWidget(self.widget)
        self.widget_7.setObjectName(_fromUtf8("widget_7"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.widget_7)
        self.horizontalLayout_5.setMargin(0)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem6)
        self.widget_8 = QtGui.QWidget(self.widget_7)
        self.widget_8.setObjectName(_fromUtf8("widget_8"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget_8)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.chk_voice_0 = QtGui.QCheckBox(self.widget_8)
        self.chk_voice_0.setObjectName(_fromUtf8("chk_voice_0"))
        self.verticalLayout_3.addWidget(self.chk_voice_0)
        self.horizontalLayout_5.addWidget(self.widget_8)
        self.verticalLayout_2.addWidget(self.widget_7)
        self.verticalLayout.addWidget(self.widget)
        self.line = QtGui.QFrame(select_voices)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.widget_2 = QtGui.QWidget(select_voices)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.chk_preserve_voices_selction = QtGui.QCheckBox(self.widget_2)
        self.chk_preserve_voices_selction.setObjectName(_fromUtf8("chk_preserve_voices_selction"))
        self.horizontalLayout.addWidget(self.chk_preserve_voices_selction)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem7)
        self.btn_continue = QtGui.QPushButton(self.widget_2)
        self.btn_continue.setObjectName(_fromUtf8("btn_continue"))
        self.horizontalLayout.addWidget(self.btn_continue)
        self.verticalLayout.addWidget(self.widget_2)

        self.retranslateUi(select_voices)
        QtCore.QMetaObject.connectSlotsByName(select_voices)

    def retranslateUi(self, select_voices):
        select_voices.setWindowTitle(_translate("select_voices", "vis Voices Selector", None))
        self.label.setText(_translate("select_voices", "Choose which voices to analyze.", None))
        self.rdo_all.setText(_translate("select_voices", "Compare all part combinations.", None))
        self.rdo_these_parts.setText(_translate("select_voices", "Compare these parts:", None))
        self.rdo_part_and_bs.setText(_translate("select_voices", "Compare this part with basso seguente:", None))
        self.rdo_choose_these.setText(_translate("select_voices", "Choose two specific voices:", None))
        self.chk_voice_0.setText(_translate("select_voices", "CheckBox", None))
        self.chk_preserve_voices_selction.setText(_translate("select_voices", "Same for Remaining Files", None))
        self.btn_continue.setText(_translate("select_voices", "Continue", None))

