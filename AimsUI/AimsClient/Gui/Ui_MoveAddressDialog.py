# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/Ui_MoveAddressDialog.ui'
#
# Created: Thu Dec 10 10:00:56 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_MoveAddressDialog(object):
    def setupUi(self, MoveAddressDialog):
        MoveAddressDialog.setObjectName(_fromUtf8("MoveAddressDialog"))
        MoveAddressDialog.resize(621, 270)
        self.verticalLayout_2 = QtGui.QVBoxLayout(MoveAddressDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(MoveAddressDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.uSadListView = DictionaryListView(MoveAddressDialog)
        self.uSadListView.setObjectName(_fromUtf8("uSadListView"))
        self.verticalLayout_2.addWidget(self.uSadListView)
        self.buttonBox = QtGui.QDialogButtonBox(MoveAddressDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(MoveAddressDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MoveAddressDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MoveAddressDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MoveAddressDialog)

    def retranslateUi(self, MoveAddressDialog):
        MoveAddressDialog.setWindowTitle(_translate("MoveAddressDialog", "Select features to move", None))
        self.label_2.setText(_translate("MoveAddressDialog", "Select features to move", None))

from AimsUI.AimsClient.Gui.DictionaryList import DictionaryListView
