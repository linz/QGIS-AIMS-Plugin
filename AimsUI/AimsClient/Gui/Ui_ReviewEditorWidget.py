# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/AimsClient/Gui/Ui_ReviewEditorWidget.ui'
#
# Created: Fri Jan  8 12:34:13 2016
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

class Ui_ReviewEditorWidget(object):
    def setupUi(self, ReviewEditorWidget):
        ReviewEditorWidget.setObjectName(_fromUtf8("ReviewEditorWidget"))
        ReviewEditorWidget.resize(414, 565)
        self.gridLayout_2 = QtGui.QGridLayout(ReviewEditorWidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.uReviewAttributes = QtGui.QTableView(ReviewEditorWidget)
        self.uReviewAttributes.setObjectName(_fromUtf8("uReviewAttributes"))
        self.horizontalLayout_2.addWidget(self.uReviewAttributes)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 3, 0, 1, 1)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.rFilterButton = QtGui.QPushButton(ReviewEditorWidget)
        self.rFilterButton.setObjectName(_fromUtf8("rFilterButton"))
        self.horizontalLayout_7.addWidget(self.rFilterButton)
        self.gridLayout_2.addLayout(self.horizontalLayout_7, 4, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, -1, -1)
        self.gridLayout.setVerticalSpacing(3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_12 = QtGui.QLabel(ReviewEditorWidget)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout.addWidget(self.label_12, 5, 0, 1, 1)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.rChangeType = QtGui.QLabel(ReviewEditorWidget)
        self.rChangeType.setText(_fromUtf8(""))
        self.rChangeType.setObjectName(_fromUtf8("rChangeType"))
        self.horizontalLayout_6.addWidget(self.rChangeType)
        self.gridLayout.addLayout(self.horizontalLayout_6, 1, 1, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.rStatus = QtGui.QLabel(ReviewEditorWidget)
        self.rStatus.setText(_fromUtf8(""))
        self.rStatus.setObjectName(_fromUtf8("rStatus"))
        self.horizontalLayout_3.addWidget(self.rStatus)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ReviewEditorWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.rMessage = QtGui.QLabel(ReviewEditorWidget)
        self.rMessage.setText(_fromUtf8(""))
        self.rMessage.setObjectName(_fromUtf8("rMessage"))
        self.gridLayout.addWidget(self.rMessage, 3, 1, 1, 1)
        self.label_14 = QtGui.QLabel(ReviewEditorWidget)
        self.label_14.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout.addWidget(self.label_14, 4, 0, 1, 1)
        self.label_3 = QtGui.QLabel(ReviewEditorWidget)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(ReviewEditorWidget)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.rWarnings = QtGui.QLabel(ReviewEditorWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.rWarnings.setFont(font)
        self.rWarnings.setText(_fromUtf8(""))
        self.rWarnings.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.rWarnings.setWordWrap(True)
        self.rWarnings.setObjectName(_fromUtf8("rWarnings"))
        self.horizontalLayout_5.addWidget(self.rWarnings)
        self.uSourceNumber = QtGui.QLabel(ReviewEditorWidget)
        self.uSourceNumber.setText(_fromUtf8(""))
        self.uSourceNumber.setObjectName(_fromUtf8("uSourceNumber"))
        self.horizontalLayout_5.addWidget(self.uSourceNumber)
        self.horizontalLayout_5.setStretch(0, 1)
        self.gridLayout.addLayout(self.horizontalLayout_5, 5, 1, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.rInfo = QtGui.QLabel(ReviewEditorWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rInfo.sizePolicy().hasHeightForWidth())
        self.rInfo.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.rInfo.setFont(font)
        self.rInfo.setText(_fromUtf8(""))
        self.rInfo.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.rInfo.setWordWrap(True)
        self.rInfo.setObjectName(_fromUtf8("rInfo"))
        self.horizontalLayout_4.addWidget(self.rInfo)
        self.gridLayout.addLayout(self.horizontalLayout_4, 4, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.rAttributeLabel = QtGui.QLabel(ReviewEditorWidget)
        self.rAttributeLabel.setObjectName(_fromUtf8("rAttributeLabel"))
        self.gridLayout_2.addWidget(self.rAttributeLabel, 2, 0, 1, 1)
        self.uAddressBeingEdited = QtGui.QLabel(ReviewEditorWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.uAddressBeingEdited.setFont(font)
        self.uAddressBeingEdited.setObjectName(_fromUtf8("uAddressBeingEdited"))
        self.gridLayout_2.addWidget(self.uAddressBeingEdited, 0, 0, 1, 1)

        self.retranslateUi(ReviewEditorWidget)
        QtCore.QMetaObject.connectSlotsByName(ReviewEditorWidget)

    def retranslateUi(self, ReviewEditorWidget):
        ReviewEditorWidget.setWindowTitle(_translate("ReviewEditorWidget", "Form", None))
        self.rFilterButton.setText(_translate("ReviewEditorWidget", "Filter", None))
        self.label_12.setText(_translate("ReviewEditorWidget", "warnings:", None))
        self.label_2.setText(_translate("ReviewEditorWidget", "Review Status:", None))
        self.label_14.setText(_translate("ReviewEditorWidget", "Info:", None))
        self.label_3.setText(_translate("ReviewEditorWidget", "Change Type:", None))
        self.label_4.setText(_translate("ReviewEditorWidget", "Review Message:", None))
        self.rAttributeLabel.setText(_translate("ReviewEditorWidget", "Review Item Attributes", None))
        self.uAddressBeingEdited.setText(_translate("ReviewEditorWidget", "No address selected", None))

