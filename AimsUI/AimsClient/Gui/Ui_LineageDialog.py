# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/AimsClient/Gui/Ui_LineageDialog.ui'
#
# Created: Fri Jan  8 16:10:55 2016
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

class Ui_LineageDialog(object):
    def setupUi(self, LineageDialog):
        LineageDialog.setObjectName(_fromUtf8("LineageDialog"))
        LineageDialog.resize(621, 288)
        self.verticalLayout = QtGui.QVBoxLayout(LineageDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(LineageDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.uSadListView = DictionaryListView(LineageDialog)
        self.uSadListView.setObjectName(_fromUtf8("uSadListView"))
        self.verticalLayout.addWidget(self.uSadListView)
        self.label = QtGui.QLabel(LineageDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.uGroupId = QtGui.QLineEdit(LineageDialog)
        self.uGroupId.setObjectName(_fromUtf8("uGroupId"))
        self.verticalLayout.addWidget(self.uGroupId)
        self.buttonBox = QtGui.QDialogButtonBox(LineageDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LineageDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LineageDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LineageDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LineageDialog)

    def retranslateUi(self, LineageDialog):
        LineageDialog.setWindowTitle(_translate("LineageDialog", "Refine group selection", None))
        self.label_2.setText(_translate("LineageDialog", "Select freatures to add to Lineage Group", None))
        self.label.setText(_translate("LineageDialog", "Enter a current Group id, else leave blank to have features added to a new group:", None))

from AimsUI.AimsClient.Gui.DictionaryList import DictionaryListView
