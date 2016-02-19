# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/AimsClient/Gui/Ui_AimsQueueWidget.ui'
#
# Created: Thu Feb 18 10:49:45 2016
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

class Ui_AimsQueueWidget(object):
    def setupUi(self, AimsQueueWidget):
        AimsQueueWidget.setObjectName(_fromUtf8("AimsQueueWidget"))
        AimsQueueWidget.resize(661, 428)
        self.verticalLayout = QtGui.QVBoxLayout(AimsQueueWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(AimsQueueWidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.uChangeTab = ChangeQueueWidget()
        self.uChangeTab.setObjectName(_fromUtf8("uChangeTab"))
        self.tabWidget.addTab(self.uChangeTab, _fromUtf8(""))
        self.uResolutionTab = ReviewQueueWidget()
        self.uResolutionTab.setObjectName(_fromUtf8("uResolutionTab"))
        self.tabWidget.addTab(self.uResolutionTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uMessageLabel = QtGui.QLabel(AimsQueueWidget)
        self.uMessageLabel.setText(_fromUtf8(""))
        self.uMessageLabel.setObjectName(_fromUtf8("uMessageLabel"))
        self.horizontalLayout_5.addWidget(self.uMessageLabel)
        self.uNewJob = QtGui.QPushButton(AimsQueueWidget)
        self.uNewJob.setObjectName(_fromUtf8("uNewJob"))
        self.horizontalLayout_5.addWidget(self.uNewJob)
        self.uSelectJob = QtGui.QPushButton(AimsQueueWidget)
        self.uSelectJob.setObjectName(_fromUtf8("uSelectJob"))
        self.horizontalLayout_5.addWidget(self.uSelectJob)
        self.uSysAdmin = QtGui.QPushButton(AimsQueueWidget)
        self.uSysAdmin.setObjectName(_fromUtf8("uSysAdmin"))
        self.horizontalLayout_5.addWidget(self.uSysAdmin)
        self.uHelp = QtGui.QPushButton(AimsQueueWidget)
        self.uHelp.setObjectName(_fromUtf8("uHelp"))
        self.horizontalLayout_5.addWidget(self.uHelp)
        self.horizontalLayout_5.setStretch(0, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.retranslateUi(AimsQueueWidget)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(AimsQueueWidget)

    def retranslateUi(self, AimsQueueWidget):
        AimsQueueWidget.setWindowTitle(_translate("AimsQueueWidget", "Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.uChangeTab), _translate("AimsQueueWidget", "Change", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.uResolutionTab), _translate("AimsQueueWidget", "Review", None))
        self.uNewJob.setText(_translate("AimsQueueWidget", "?", None))
        self.uSelectJob.setText(_translate("AimsQueueWidget", "??", None))
        self.uSysAdmin.setText(_translate("AimsQueueWidget", "???", None))
        self.uHelp.setText(_translate("AimsQueueWidget", "Help", None))

from ReviewQueueWidget import ReviewQueueWidget
from ChangeQueueWidget import ChangeQueueWidget
