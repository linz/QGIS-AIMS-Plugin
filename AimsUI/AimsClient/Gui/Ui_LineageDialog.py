# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/AimsClient/Gui/Ui_LineageDialog.ui'
#
# Created: Tue Jun 14 09:56:34 2016
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
        LineageDialog.resize(621, 368)
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
        self.uGroupDescription = QtGui.QTextEdit(LineageDialog)
        self.uGroupDescription.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.uGroupDescription.sizePolicy().hasHeightForWidth())
        self.uGroupDescription.setSizePolicy(sizePolicy)
        self.uGroupDescription.setMaximumSize(QtCore.QSize(16777215, 60))
        self.uGroupDescription.setObjectName(_fromUtf8("uGroupDescription"))
        self.verticalLayout.addWidget(self.uGroupDescription)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_3 = QtGui.QLabel(LineageDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.uGroupId = QtGui.QLineEdit(LineageDialog)
        self.uGroupId.setObjectName(_fromUtf8("uGroupId"))
        self.horizontalLayout.addWidget(self.uGroupId)
        self.verticalLayout.addLayout(self.horizontalLayout)
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
        self.label.setText(_translate("LineageDialog", "Provide A Group Description To Add Features To A New Group:", None))
        self.label_3.setText(_translate("LineageDialog", "Or, Supply A Current Group Id To Add Feautres To An Existing Group:", None))

from AimsUI.AimsClient.Gui.DictionaryList import DictionaryListView
