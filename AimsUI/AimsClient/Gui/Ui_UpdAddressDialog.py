# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/Ui_UpdAddressDialog.ui'
#
# Created: Fri Dec 11 09:55:58 2015
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

class Ui_UpdAddressDialog(object):
    def setupUi(self, DelAddressDialog):
        DelAddressDialog.setObjectName(_fromUtf8("DelAddressDialog"))
        DelAddressDialog.resize(621, 270)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DelAddressDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(DelAddressDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.uSadListView = DictionaryListView(DelAddressDialog)
        self.uSadListView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.uSadListView.setObjectName(_fromUtf8("uSadListView"))
        self.verticalLayout_2.addWidget(self.uSadListView)
        self.buttonBox = QtGui.QDialogButtonBox(DelAddressDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(DelAddressDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DelAddressDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DelAddressDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DelAddressDialog)

    def retranslateUi(self, DelAddressDialog):
        DelAddressDialog.setWindowTitle(_translate("DelAddressDialog", "Select feature to update", None))
        self.label_2.setText(_translate("DelAddressDialog", "Select feature to update", None))

from AimsUI.AimsClient.Gui.DictionaryList import DictionaryListView
