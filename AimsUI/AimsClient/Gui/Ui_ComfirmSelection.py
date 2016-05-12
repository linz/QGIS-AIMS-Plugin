# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/AimsClient/Gui/Ui_ComfirmSelection.ui'
#
# Created: Thu May 12 14:23:58 2016
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

class Ui_ComfirmSelection(object):
    def setupUi(self, ComfirmSelection):
        ComfirmSelection.setObjectName(_fromUtf8("ComfirmSelection"))
        ComfirmSelection.resize(621, 270)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ComfirmSelection)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(ComfirmSelection)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.uSadListView = DictionaryListView(ComfirmSelection)
        self.uSadListView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.uSadListView.setObjectName(_fromUtf8("uSadListView"))
        self.verticalLayout_2.addWidget(self.uSadListView)
        self.buttonBox = QtGui.QDialogButtonBox(ComfirmSelection)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(ComfirmSelection)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ComfirmSelection.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ComfirmSelection.reject)
        QtCore.QMetaObject.connectSlotsByName(ComfirmSelection)

    def retranslateUi(self, ComfirmSelection):
        ComfirmSelection.setWindowTitle(_translate("ComfirmSelection", "Select feature to update", None))
        self.label_2.setText(_translate("ComfirmSelection", "Please Confirm Your Selection:", None))

from AimsUI.AimsClient.Gui.DictionaryList import DictionaryListView
