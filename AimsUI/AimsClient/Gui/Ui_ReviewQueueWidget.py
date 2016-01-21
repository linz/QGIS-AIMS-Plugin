# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/AimsClient/Gui/Ui_ReviewQueueWidget.ui'
#
# Created: Thu Jan 21 12:17:52 2016
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

class Ui_ReviewQueueWidget(object):
    def setupUi(self, ReviewQueueWidget):
        ReviewQueueWidget.setObjectName(_fromUtf8("ReviewQueueWidget"))
        ReviewQueueWidget.resize(563, 1007)
        self.verticalLayout_8 = QtGui.QVBoxLayout(ReviewQueueWidget)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.label = QtGui.QLabel(ReviewQueueWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_8.addWidget(self.label)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.tableView_3 = AddressListView(ReviewQueueWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_3.sizePolicy().hasHeightForWidth())
        self.tableView_3.setSizePolicy(sizePolicy)
        self.tableView_3.setObjectName(_fromUtf8("tableView_3"))
        self.horizontalLayout_7.addWidget(self.tableView_3)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.pushButton_2 = QtGui.QPushButton(ReviewQueueWidget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.verticalLayout_4.addWidget(self.pushButton_2)
        self.pushButton = QtGui.QPushButton(ReviewQueueWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout_4.addWidget(self.pushButton)
        self.horizontalLayout_7.addLayout(self.verticalLayout_4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.uAddressListView = AddressListView(ReviewQueueWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uAddressListView.sizePolicy().hasHeightForWidth())
        self.uAddressListView.setSizePolicy(sizePolicy)
        self.uAddressListView.setObjectName(_fromUtf8("uAddressListView"))
        self.horizontalLayout_4.addWidget(self.uAddressListView)
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.horizontalLayout_4.addLayout(self.verticalLayout_7)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.tableWidget_2 = QtGui.QTableWidget(ReviewQueueWidget)
        self.tableWidget_2.setObjectName(_fromUtf8("tableWidget_2"))
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.horizontalLayout_6.addWidget(self.tableWidget_2)
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.pushButton_3 = QtGui.QPushButton(ReviewQueueWidget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.verticalLayout_6.addWidget(self.pushButton_3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem)
        self.horizontalLayout_6.addLayout(self.verticalLayout_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.verticalLayout_8.addLayout(self.verticalLayout_2)

        self.retranslateUi(ReviewQueueWidget)
        QtCore.QMetaObject.connectSlotsByName(ReviewQueueWidget)

    def retranslateUi(self, ReviewQueueWidget):
        ReviewQueueWidget.setWindowTitle(_translate("ReviewQueueWidget", "Form", None))
        self.label.setText(_translate("ReviewQueueWidget", "Proof of concept only ", None))
        self.pushButton_2.setText(_translate("ReviewQueueWidget", "Accept", None))
        self.pushButton.setText(_translate("ReviewQueueWidget", "Reject", None))
        self.pushButton_3.setText(_translate("ReviewQueueWidget", "update", None))

from AddressList import AddressListView
