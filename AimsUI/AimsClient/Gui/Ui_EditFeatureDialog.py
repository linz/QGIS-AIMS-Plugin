# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/AimsClient/Gui/Ui_EditFeatureDialog.ui'
#
# Created: Tue Sep  6 14:48:26 2016
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

class Ui_EditFeatureDialog(object):
    def setupUi(self, EditFeatureDialog):
        EditFeatureDialog.setObjectName(_fromUtf8("EditFeatureDialog"))
        EditFeatureDialog.resize(480, 1087)
        self.verticalLayout = QtGui.QVBoxLayout(EditFeatureDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(EditFeatureDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents_4 = QtGui.QWidget()
        self.scrollAreaWidgetContents_4.setGeometry(QtCore.QRect(0, 0, 460, 1067))
        self.scrollAreaWidgetContents_4.setObjectName(_fromUtf8("scrollAreaWidgetContents_4"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.lNumberSplitter = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lNumberSplitter.setFont(font)
        self.lNumberSplitter.setObjectName(_fromUtf8("lNumberSplitter"))
        self.horizontalLayout_11.addWidget(self.lNumberSplitter)
        self.uFullNum = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uFullNum.setMaximumSize(QtCore.QSize(200, 16777215))
        self.uFullNum.setObjectName(_fromUtf8("uFullNum"))
        self.horizontalLayout_11.addWidget(self.uFullNum)
        self.uAddressType = QtGui.QComboBox(self.scrollAreaWidgetContents_4)
        self.uAddressType.setObjectName(_fromUtf8("uAddressType"))
        self.horizontalLayout_11.addWidget(self.uAddressType)
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.lAlpha = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lAlpha.setFont(font)
        self.lAlpha.setObjectName(_fromUtf8("lAlpha"))
        self.gridLayout_4.addWidget(self.lAlpha, 0, 8, 1, 1)
        self.lPrefix = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lPrefix.setFont(font)
        self.lPrefix.setObjectName(_fromUtf8("lPrefix"))
        self.gridLayout_4.addWidget(self.lPrefix, 0, 0, 1, 1)
        self.lHigh = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lHigh.setFont(font)
        self.lHigh.setObjectName(_fromUtf8("lHigh"))
        self.gridLayout_4.addWidget(self.lHigh, 0, 6, 1, 1)
        self.uHigh = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uHigh.setMaximumSize(QtCore.QSize(65, 16777215))
        self.uHigh.setMaxLength(6)
        self.uHigh.setObjectName(_fromUtf8("uHigh"))
        self.gridLayout_4.addWidget(self.uHigh, 1, 6, 1, 1)
        self.uPrefix = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uPrefix.setMaximumSize(QtCore.QSize(65, 16777215))
        self.uPrefix.setText(_fromUtf8(""))
        self.uPrefix.setMaxLength(3)
        self.uPrefix.setObjectName(_fromUtf8("uPrefix"))
        self.gridLayout_4.addWidget(self.uPrefix, 1, 0, 1, 1)
        self.uBase = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uBase.setMaximumSize(QtCore.QSize(65, 16777215))
        self.uBase.setInputMethodHints(QtCore.Qt.ImhNone)
        self.uBase.setMaxLength(6)
        self.uBase.setObjectName(_fromUtf8("uBase"))
        self.gridLayout_4.addWidget(self.uBase, 1, 4, 1, 1)
        self.uUnit = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uUnit.setMaximumSize(QtCore.QSize(65, 16777215))
        self.uUnit.setMaxLength(6)
        self.uUnit.setObjectName(_fromUtf8("uUnit"))
        self.gridLayout_4.addWidget(self.uUnit, 1, 2, 1, 1)
        self.uAlpha = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uAlpha.setMaximumSize(QtCore.QSize(65, 16777215))
        self.uAlpha.setMaxLength(4)
        self.uAlpha.setObjectName(_fromUtf8("uAlpha"))
        self.gridLayout_4.addWidget(self.uAlpha, 1, 8, 1, 1)
        self.lUnit = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lUnit.setFont(font)
        self.lUnit.setObjectName(_fromUtf8("lUnit"))
        self.gridLayout_4.addWidget(self.lUnit, 0, 2, 1, 1)
        self.lBase = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lBase.setFont(font)
        self.lBase.setObjectName(_fromUtf8("lBase"))
        self.gridLayout_4.addWidget(self.lBase, 0, 4, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_4)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.formLayout_5 = QtGui.QFormLayout()
        self.formLayout_5.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_5.setObjectName(_fromUtf8("formLayout_5"))
        self.label_45 = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_45.setFont(font)
        self.label_45.setObjectName(_fromUtf8("label_45"))
        self.formLayout_5.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_45)
        self.lExternalAddressId = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lExternalAddressId.setObjectName(_fromUtf8("lExternalAddressId"))
        self.formLayout_5.setWidget(1, QtGui.QFormLayout.LabelRole, self.lExternalAddressId)
        self.uExternalAddId = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uExternalAddId.setText(_fromUtf8(""))
        self.uExternalAddId.setMaxLength(15)
        self.uExternalAddId.setObjectName(_fromUtf8("uExternalAddId"))
        self.formLayout_5.setWidget(1, QtGui.QFormLayout.FieldRole, self.uExternalAddId)
        self.lExternalAddressIdScheme = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lExternalAddressIdScheme.setObjectName(_fromUtf8("lExternalAddressIdScheme"))
        self.formLayout_5.setWidget(2, QtGui.QFormLayout.LabelRole, self.lExternalAddressIdScheme)
        self.uExternalAddressIdScheme = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uExternalAddressIdScheme.setText(_fromUtf8(""))
        self.uExternalAddressIdScheme.setMaxLength(100)
        self.uExternalAddressIdScheme.setObjectName(_fromUtf8("uExternalAddressIdScheme"))
        self.formLayout_5.setWidget(2, QtGui.QFormLayout.FieldRole, self.uExternalAddressIdScheme)
        self.lLifeCycle = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lLifeCycle.setObjectName(_fromUtf8("lLifeCycle"))
        self.formLayout_5.setWidget(3, QtGui.QFormLayout.LabelRole, self.lLifeCycle)
        self.ulifeCycle = QtGui.QComboBox(self.scrollAreaWidgetContents_4)
        self.ulifeCycle.setObjectName(_fromUtf8("ulifeCycle"))
        self.formLayout_5.setWidget(3, QtGui.QFormLayout.FieldRole, self.ulifeCycle)
        self.lUnitType = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lUnitType.setObjectName(_fromUtf8("lUnitType"))
        self.formLayout_5.setWidget(4, QtGui.QFormLayout.LabelRole, self.lUnitType)
        self.uUnitType = QtGui.QComboBox(self.scrollAreaWidgetContents_4)
        self.uUnitType.setObjectName(_fromUtf8("uUnitType"))
        self.formLayout_5.setWidget(4, QtGui.QFormLayout.FieldRole, self.uUnitType)
        self.lLevelType = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lLevelType.setObjectName(_fromUtf8("lLevelType"))
        self.formLayout_5.setWidget(5, QtGui.QFormLayout.LabelRole, self.lLevelType)
        self.uLevelType = QtGui.QComboBox(self.scrollAreaWidgetContents_4)
        self.uLevelType.setObjectName(_fromUtf8("uLevelType"))
        self.formLayout_5.setWidget(5, QtGui.QFormLayout.FieldRole, self.uLevelType)
        self.lLevelValue = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lLevelValue.setObjectName(_fromUtf8("lLevelValue"))
        self.formLayout_5.setWidget(6, QtGui.QFormLayout.LabelRole, self.lLevelValue)
        self.uLevelValue = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uLevelValue.setMaxLength(40)
        self.uLevelValue.setObjectName(_fromUtf8("uLevelValue"))
        self.formLayout_5.setWidget(6, QtGui.QFormLayout.FieldRole, self.uLevelValue)
        self.line_14 = QtGui.QFrame(self.scrollAreaWidgetContents_4)
        self.line_14.setFrameShape(QtGui.QFrame.HLine)
        self.line_14.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_14.setObjectName(_fromUtf8("line_14"))
        self.formLayout_5.setWidget(7, QtGui.QFormLayout.SpanningRole, self.line_14)
        self.label_46 = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_46.setFont(font)
        self.label_46.setObjectName(_fromUtf8("label_46"))
        self.formLayout_5.setWidget(8, QtGui.QFormLayout.LabelRole, self.label_46)
        self.lRoadCentrelineId = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lRoadCentrelineId.setFont(font)
        self.lRoadCentrelineId.setObjectName(_fromUtf8("lRoadCentrelineId"))
        self.formLayout_5.setWidget(9, QtGui.QFormLayout.LabelRole, self.lRoadCentrelineId)
        self.horizontalLayout_12 = QtGui.QHBoxLayout()
        self.horizontalLayout_12.setObjectName(_fromUtf8("horizontalLayout_12"))
        self.uRclId = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uRclId.setReadOnly(True)
        self.uRclId.setObjectName(_fromUtf8("uRclId"))
        self.horizontalLayout_12.addWidget(self.uRclId)
        self.uPersistRcl = QtGui.QCheckBox(self.scrollAreaWidgetContents_4)
        self.uPersistRcl.setText(_fromUtf8(""))
        self.uPersistRcl.setObjectName(_fromUtf8("uPersistRcl"))
        self.horizontalLayout_12.addWidget(self.uPersistRcl)
        self.uGetRclToolButton = QtGui.QToolButton(self.scrollAreaWidgetContents_4)
        self.uGetRclToolButton.setMinimumSize(QtCore.QSize(24, 0))
        self.uGetRclToolButton.setMaximumSize(QtCore.QSize(24, 16777215))
        self.uGetRclToolButton.setText(_fromUtf8(""))
        self.uGetRclToolButton.setObjectName(_fromUtf8("uGetRclToolButton"))
        self.horizontalLayout_12.addWidget(self.uGetRclToolButton)
        self.formLayout_5.setLayout(9, QtGui.QFormLayout.FieldRole, self.horizontalLayout_12)
        self.lRoadPrefix = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lRoadPrefix.setObjectName(_fromUtf8("lRoadPrefix"))
        self.formLayout_5.setWidget(10, QtGui.QFormLayout.LabelRole, self.lRoadPrefix)
        self.uRoadPrefix = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uRoadPrefix.setMaxLength(20)
        self.uRoadPrefix.setObjectName(_fromUtf8("uRoadPrefix"))
        self.formLayout_5.setWidget(10, QtGui.QFormLayout.FieldRole, self.uRoadPrefix)
        self.lRoadName = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lRoadName.setFont(font)
        self.lRoadName.setObjectName(_fromUtf8("lRoadName"))
        self.formLayout_5.setWidget(11, QtGui.QFormLayout.LabelRole, self.lRoadName)
        self.uRoadName = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uRoadName.setMaxLength(150)
        self.uRoadName.setObjectName(_fromUtf8("uRoadName"))
        self.formLayout_5.setWidget(11, QtGui.QFormLayout.FieldRole, self.uRoadName)
        self.lRoadTypeName = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lRoadTypeName.setFont(font)
        self.lRoadTypeName.setObjectName(_fromUtf8("lRoadTypeName"))
        self.formLayout_5.setWidget(12, QtGui.QFormLayout.LabelRole, self.lRoadTypeName)
        self.uRoadTypeName = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uRoadTypeName.setMaxLength(40)
        self.uRoadTypeName.setObjectName(_fromUtf8("uRoadTypeName"))
        self.formLayout_5.setWidget(12, QtGui.QFormLayout.FieldRole, self.uRoadTypeName)
        self.lRoadSuffix = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lRoadSuffix.setFont(font)
        self.lRoadSuffix.setObjectName(_fromUtf8("lRoadSuffix"))
        self.formLayout_5.setWidget(13, QtGui.QFormLayout.LabelRole, self.lRoadSuffix)
        self.uRoadSuffix = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uRoadSuffix.setMaxLength(40)
        self.uRoadSuffix.setReadOnly(False)
        self.uRoadSuffix.setObjectName(_fromUtf8("uRoadSuffix"))
        self.formLayout_5.setWidget(13, QtGui.QFormLayout.FieldRole, self.uRoadSuffix)
        self.lWaterRouteName = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lWaterRouteName.setObjectName(_fromUtf8("lWaterRouteName"))
        self.formLayout_5.setWidget(14, QtGui.QFormLayout.LabelRole, self.lWaterRouteName)
        self.uWaterRouteName = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uWaterRouteName.setMaxLength(100)
        self.uWaterRouteName.setReadOnly(False)
        self.uWaterRouteName.setObjectName(_fromUtf8("uWaterRouteName"))
        self.formLayout_5.setWidget(14, QtGui.QFormLayout.FieldRole, self.uWaterRouteName)
        self.lWaterName = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lWaterName.setObjectName(_fromUtf8("lWaterName"))
        self.formLayout_5.setWidget(15, QtGui.QFormLayout.LabelRole, self.lWaterName)
        self.uWaterName = QtGui.QLineEdit(self.scrollAreaWidgetContents_4)
        self.uWaterName.setMaxLength(100)
        self.uWaterName.setReadOnly(False)
        self.uWaterName.setObjectName(_fromUtf8("uWaterName"))
        self.formLayout_5.setWidget(15, QtGui.QFormLayout.FieldRole, self.uWaterName)
        self.line_16 = QtGui.QFrame(self.scrollAreaWidgetContents_4)
        self.line_16.setFrameShape(QtGui.QFrame.HLine)
        self.line_16.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_16.setObjectName(_fromUtf8("line_16"))
        self.formLayout_5.setWidget(17, QtGui.QFormLayout.SpanningRole, self.line_16)
        self.verticalLayout_3.addLayout(self.formLayout_5)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_47 = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.label_47.setFont(font)
        self.label_47.setObjectName(_fromUtf8("label_47"))
        self.horizontalLayout_2.addWidget(self.label_47)
        self.buttonAO = QtGui.QPushButton(self.scrollAreaWidgetContents_4)
        self.buttonAO.setMaximumSize(QtCore.QSize(22, 16777215))
        self.buttonAO.setObjectName(_fromUtf8("buttonAO"))
        self.horizontalLayout_2.addWidget(self.buttonAO)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.wAddObj = QtGui.QWidget(self.scrollAreaWidgetContents_4)
        self.wAddObj.setObjectName(_fromUtf8("wAddObj"))
        self.formLayout_2 = QtGui.QFormLayout(self.wAddObj)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setMargin(0)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.lObjectType = QtGui.QLabel(self.wAddObj)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lObjectType.setFont(font)
        self.lObjectType.setObjectName(_fromUtf8("lObjectType"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.lObjectType)
        self.uObjectType = QtGui.QComboBox(self.wAddObj)
        self.uObjectType.setObjectName(_fromUtf8("uObjectType"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.uObjectType)
        self.lObjectName = QtGui.QLabel(self.wAddObj)
        self.lObjectName.setObjectName(_fromUtf8("lObjectName"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.lObjectName)
        self.uObjectName = QtGui.QLineEdit(self.wAddObj)
        self.uObjectName.setMaxLength(250)
        self.uObjectName.setObjectName(_fromUtf8("uObjectName"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.uObjectName)
        self.lPositionType = QtGui.QLabel(self.wAddObj)
        self.lPositionType.setObjectName(_fromUtf8("lPositionType"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.lPositionType)
        self.uPositionType = QtGui.QComboBox(self.wAddObj)
        self.uPositionType.setObjectName(_fromUtf8("uPositionType"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.uPositionType)
        self.lExternalObjectId = QtGui.QLabel(self.wAddObj)
        self.lExternalObjectId.setObjectName(_fromUtf8("lExternalObjectId"))
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.LabelRole, self.lExternalObjectId)
        self.uExternalObjectId = QtGui.QLineEdit(self.wAddObj)
        self.uExternalObjectId.setMaxLength(15)
        self.uExternalObjectId.setObjectName(_fromUtf8("uExternalObjectId"))
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.FieldRole, self.uExternalObjectId)
        self.lExtObjectIdScheme = QtGui.QLabel(self.wAddObj)
        self.lExtObjectIdScheme.setObjectName(_fromUtf8("lExtObjectIdScheme"))
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.LabelRole, self.lExtObjectIdScheme)
        self.uExtObjectIdScheme = QtGui.QLineEdit(self.wAddObj)
        self.uExtObjectIdScheme.setMaxLength(100)
        self.uExtObjectIdScheme.setObjectName(_fromUtf8("uExtObjectIdScheme"))
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.FieldRole, self.uExtObjectIdScheme)
        self.lValref = QtGui.QLabel(self.wAddObj)
        self.lValref.setObjectName(_fromUtf8("lValref"))
        self.formLayout_2.setWidget(6, QtGui.QFormLayout.LabelRole, self.lValref)
        self.uValuationReference = QtGui.QLineEdit(self.wAddObj)
        self.uValuationReference.setBaseSize(QtCore.QSize(0, 50))
        self.uValuationReference.setMaxLength(30)
        self.uValuationReference.setObjectName(_fromUtf8("uValuationReference"))
        self.formLayout_2.setWidget(6, QtGui.QFormLayout.FieldRole, self.uValuationReference)
        self.lCertTitle = QtGui.QLabel(self.wAddObj)
        self.lCertTitle.setObjectName(_fromUtf8("lCertTitle"))
        self.formLayout_2.setWidget(7, QtGui.QFormLayout.LabelRole, self.lCertTitle)
        self.uCertificateOfTitle = QtGui.QLineEdit(self.wAddObj)
        self.uCertificateOfTitle.setMaxLength(20)
        self.uCertificateOfTitle.setObjectName(_fromUtf8("uCertificateOfTitle"))
        self.formLayout_2.setWidget(7, QtGui.QFormLayout.FieldRole, self.uCertificateOfTitle)
        self.lAppellation = QtGui.QLabel(self.wAddObj)
        self.lAppellation.setObjectName(_fromUtf8("lAppellation"))
        self.formLayout_2.setWidget(8, QtGui.QFormLayout.LabelRole, self.lAppellation)
        self.uAppellation = QtGui.QLineEdit(self.wAddObj)
        self.uAppellation.setMaxLength(500)
        self.uAppellation.setObjectName(_fromUtf8("uAppellation"))
        self.formLayout_2.setWidget(8, QtGui.QFormLayout.FieldRole, self.uAppellation)
        self.uMblkOverride = QtGui.QLineEdit(self.wAddObj)
        self.uMblkOverride.setMaxLength(7)
        self.uMblkOverride.setObjectName(_fromUtf8("uMblkOverride"))
        self.formLayout_2.setWidget(9, QtGui.QFormLayout.FieldRole, self.uMblkOverride)
        self.lMblk = QtGui.QLabel(self.wAddObj)
        self.lMblk.setObjectName(_fromUtf8("lMblk"))
        self.formLayout_2.setWidget(9, QtGui.QFormLayout.LabelRole, self.lMblk)
        self.verticalLayout_3.addWidget(self.wAddObj)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.line = QtGui.QFrame(self.scrollAreaWidgetContents_4)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_2.addWidget(self.line)
        self.formLayout_4 = QtGui.QFormLayout()
        self.formLayout_4.setObjectName(_fromUtf8("formLayout_4"))
        self.lNotes = QtGui.QLabel(self.scrollAreaWidgetContents_4)
        self.lNotes.setObjectName(_fromUtf8("lNotes"))
        self.formLayout_4.setWidget(1, QtGui.QFormLayout.LabelRole, self.lNotes)
        self.uNotes = QtGui.QPlainTextEdit(self.scrollAreaWidgetContents_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uNotes.sizePolicy().hasHeightForWidth())
        self.uNotes.setSizePolicy(sizePolicy)
        self.uNotes.setMinimumSize(QtCore.QSize(0, 20))
        self.uNotes.setMaximumSize(QtCore.QSize(16777215, 100))
        self.uNotes.setBaseSize(QtCore.QSize(0, 0))
        self.uNotes.setObjectName(_fromUtf8("uNotes"))
        self.formLayout_4.setWidget(1, QtGui.QFormLayout.FieldRole, self.uNotes)
        self.verticalLayout_2.addLayout(self.formLayout_4)
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem1)
        self.uAbort = QtGui.QPushButton(self.scrollAreaWidgetContents_4)
        self.uAbort.setObjectName(_fromUtf8("uAbort"))
        self.horizontalLayout_13.addWidget(self.uAbort)
        self.uSubmitAddressButton = QtGui.QPushButton(self.scrollAreaWidgetContents_4)
        self.uSubmitAddressButton.setObjectName(_fromUtf8("uSubmitAddressButton"))
        self.horizontalLayout_13.addWidget(self.uSubmitAddressButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_13)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_4)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(EditFeatureDialog)
        QtCore.QMetaObject.connectSlotsByName(EditFeatureDialog)
        EditFeatureDialog.setTabOrder(self.uFullNum, self.uAddressType)
        EditFeatureDialog.setTabOrder(self.uAddressType, self.uPrefix)
        EditFeatureDialog.setTabOrder(self.uPrefix, self.uUnit)
        EditFeatureDialog.setTabOrder(self.uUnit, self.uBase)
        EditFeatureDialog.setTabOrder(self.uBase, self.uHigh)
        EditFeatureDialog.setTabOrder(self.uHigh, self.uAlpha)
        EditFeatureDialog.setTabOrder(self.uAlpha, self.uExternalAddId)
        EditFeatureDialog.setTabOrder(self.uExternalAddId, self.uExternalAddressIdScheme)
        EditFeatureDialog.setTabOrder(self.uExternalAddressIdScheme, self.ulifeCycle)
        EditFeatureDialog.setTabOrder(self.ulifeCycle, self.uUnitType)
        EditFeatureDialog.setTabOrder(self.uUnitType, self.uLevelType)
        EditFeatureDialog.setTabOrder(self.uLevelType, self.uLevelValue)
        EditFeatureDialog.setTabOrder(self.uLevelValue, self.uRclId)
        EditFeatureDialog.setTabOrder(self.uRclId, self.uRoadPrefix)
        EditFeatureDialog.setTabOrder(self.uRoadPrefix, self.uRoadName)
        EditFeatureDialog.setTabOrder(self.uRoadName, self.uRoadTypeName)
        EditFeatureDialog.setTabOrder(self.uRoadTypeName, self.uRoadSuffix)
        EditFeatureDialog.setTabOrder(self.uRoadSuffix, self.uWaterRouteName)
        EditFeatureDialog.setTabOrder(self.uWaterRouteName, self.uWaterName)
        EditFeatureDialog.setTabOrder(self.uWaterName, self.uObjectType)
        EditFeatureDialog.setTabOrder(self.uObjectType, self.uObjectName)
        EditFeatureDialog.setTabOrder(self.uObjectName, self.uPositionType)
        EditFeatureDialog.setTabOrder(self.uPositionType, self.uExternalObjectId)
        EditFeatureDialog.setTabOrder(self.uExternalObjectId, self.uExtObjectIdScheme)
        EditFeatureDialog.setTabOrder(self.uExtObjectIdScheme, self.uValuationReference)
        EditFeatureDialog.setTabOrder(self.uValuationReference, self.uCertificateOfTitle)
        EditFeatureDialog.setTabOrder(self.uCertificateOfTitle, self.uAppellation)
        EditFeatureDialog.setTabOrder(self.uAppellation, self.uMblkOverride)
        EditFeatureDialog.setTabOrder(self.uMblkOverride, self.uNotes)
        EditFeatureDialog.setTabOrder(self.uNotes, self.uAbort)
        EditFeatureDialog.setTabOrder(self.uAbort, self.uSubmitAddressButton)
        EditFeatureDialog.setTabOrder(self.uSubmitAddressButton, self.uPersistRcl)
        EditFeatureDialog.setTabOrder(self.uPersistRcl, self.uGetRclToolButton)
        EditFeatureDialog.setTabOrder(self.uGetRclToolButton, self.buttonAO)
        EditFeatureDialog.setTabOrder(self.buttonAO, self.scrollArea)

    def retranslateUi(self, EditFeatureDialog):
        EditFeatureDialog.setWindowTitle(_translate("EditFeatureDialog", "Form", None))
        self.lNumberSplitter.setText(_translate("EditFeatureDialog", "Number Splitter:", None))
        self.lAlpha.setText(_translate("EditFeatureDialog", "Alpha:", None))
        self.lPrefix.setText(_translate("EditFeatureDialog", "Prefix:", None))
        self.lHigh.setText(_translate("EditFeatureDialog", "High:", None))
        self.lUnit.setText(_translate("EditFeatureDialog", "Unit:", None))
        self.lBase.setText(_translate("EditFeatureDialog", "Base:", None))
        self.label_45.setText(_translate("EditFeatureDialog", "Address Extras:", None))
        self.lExternalAddressId.setText(_translate("EditFeatureDialog", "External Address Id:", None))
        self.lExternalAddressIdScheme.setText(_translate("EditFeatureDialog", "Ext Address Id Scheme:", None))
        self.lLifeCycle.setText(_translate("EditFeatureDialog", "Life Cycle:", None))
        self.lUnitType.setText(_translate("EditFeatureDialog", "Unit Type:", None))
        self.lLevelType.setText(_translate("EditFeatureDialog", "Level Type:", None))
        self.lLevelValue.setText(_translate("EditFeatureDialog", "Level Value:", None))
        self.label_46.setText(_translate("EditFeatureDialog", "Road:", None))
        self.lRoadCentrelineId.setText(_translate("EditFeatureDialog", "Road Centreline Id:", None))
        self.lRoadPrefix.setText(_translate("EditFeatureDialog", "Road Prefix:", None))
        self.lRoadName.setText(_translate("EditFeatureDialog", "Road Name:", None))
        self.lRoadTypeName.setText(_translate("EditFeatureDialog", "Road Type:", None))
        self.lRoadSuffix.setText(_translate("EditFeatureDialog", "Road Suffix:", None))
        self.lWaterRouteName.setText(_translate("EditFeatureDialog", "Water Route Name:", None))
        self.lWaterName.setText(_translate("EditFeatureDialog", "Water Name:", None))
        self.label_47.setText(_translate("EditFeatureDialog", "Addressable Object:", None))
        self.buttonAO.setText(_translate("EditFeatureDialog", "⇅", None))
        self.lObjectType.setText(_translate("EditFeatureDialog", "Object Type:", None))
        self.lObjectName.setText(_translate("EditFeatureDialog", "Object Name:", None))
        self.lPositionType.setText(_translate("EditFeatureDialog", "Position Type:", None))
        self.lExternalObjectId.setText(_translate("EditFeatureDialog", "External Object Id:", None))
        self.lExtObjectIdScheme.setText(_translate("EditFeatureDialog", "Ext Object Id Scheme:", None))
        self.lValref.setText(_translate("EditFeatureDialog", "Valuation Reference:", None))
        self.lCertTitle.setText(_translate("EditFeatureDialog", "Certificate Of Title:", None))
        self.lAppellation.setText(_translate("EditFeatureDialog", "Appellation:", None))
        self.lMblk.setText(_translate("EditFeatureDialog", "Meshblock Override:", None))
        self.lNotes.setText(_translate("EditFeatureDialog", "Notes:", None))
        self.uAbort.setText(_translate("EditFeatureDialog", "Abort", None))
        self.uSubmitAddressButton.setText(_translate("EditFeatureDialog", "Submit", None))

