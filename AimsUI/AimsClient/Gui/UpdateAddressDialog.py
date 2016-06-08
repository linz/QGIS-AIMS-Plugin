# -*- coding: utf-8 -*-
################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re

from Ui_NewAddressDialog import Ui_NewAddressDialog
from AimsUI.AimsClient.Address import Address
from AimsUI.AimsClient.UiUtility import UiUtility

#from AimsUI.GetRclTool import *
from qgis.utils import iface

class UpdateAddressDialog(Ui_NewAddressDialog, QDialog):
    
    @classmethod
    def updateAddress( cls, feature, layerManager, controller, parent=None):
        dlg = UpdateAddressDialog(parent, feature, layerManager, controller)
        dlg.exec_()
  
    def __init__( self, parent, feature, layerManager, controller):
        QDialog.__init__( self, parent )  
        self.setupUi(self)
        self.iface = iface
        self.feature = feature
        self._layerManager = layerManager
        self._controller = controller
        
        # limit user inputs
        UiUtility.formMask(self)
        # set combo box defaults
        UiUtility.setFormCombos(self)
        
        self.uSubmitAddressButton.clicked.connect(self.submitAddress)
        self.uAbort.clicked.connect(self.closeDlg)
        self.uFullNum.textChanged.connect(self.fullNumChanged)        
        # set forms feature values
        self.uAddressType.setCurrentIndex(QComboBox.findText(self.uAddressType, self.feature._addressType))
        self.uExternalAddId.setText(UiUtility.nullEqualsNone(self.feature._externalAddressId))
        self.uExternalAddressIdScheme.setText(UiUtility.nullEqualsNone(self.feature._externalAddressIdScheme))
        self.ulifeCycle.setCurrentIndex(QComboBox.findText(self.ulifeCycle, self.feature._lifecycle))
        self.uUnitType.setCurrentIndex(QComboBox.findText(self.uUnitType, self.feature._unitType))
        self.uUnit.setText(UiUtility.nullEqualsNone(self.feature._unitValue))
        self.uLevelType.setCurrentIndex(QComboBox.findText(self.uLevelType, self.feature._levelType))
        self.uLevelValue.setText(UiUtility.nullEqualsNone(self.feature._levelValue))
        self.uPrefix.setText(UiUtility.nullEqualsNone(self.feature._addressNumberPrefix))
        self.uBase.setText(UiUtility.nullEqualsNone(self.feature._addressNumber))
        self.uAlpha.setText(UiUtility.nullEqualsNone(self.feature._addressNumberSuffix))
        self.uHigh.setText(UiUtility.nullEqualsNone(self.feature._addressNumberHigh))
        self.uRoadCentrelineId.setText(UiUtility.nullEqualsNone(self.feature._roadCentrelineId))
        self.uRoadPrefix.setText(UiUtility.nullEqualsNone(self.feature._roadPrefix))
        self.uRoadName.setText(UiUtility.nullEqualsNone(self.feature._roadName))
        self.uRoadTypeName.setText(UiUtility.nullEqualsNone(self.feature._roadTypeName))
        self.uRoadSuffix.setText(UiUtility.nullEqualsNone(self.feature._roadSuffix))
        self.uWaterRouteName.setText(UiUtility.nullEqualsNone(self.feature._waterRouteName))
        self.uWaterName.setText(UiUtility.nullEqualsNone(self.feature._waterName))
        
        # addressable object
        self.uObjectType.setCurrentIndex(QComboBox.findText(self.uObjectType, self.feature._aoType))
        self.uObjectName.setText(UiUtility.nullEqualsNone(self.feature._aoName))
        self.uExternalObjectId.setText(UiUtility.nullEqualsNone(self.feature._externalObjectId))
        self.uExtObjectIdScheme.setText(UiUtility.nullEqualsNone(self.feature._externalObjectIdScheme))
        self.uValuationReference.setText(UiUtility.nullEqualsNone(self.feature._valuationReference))
        self.uCertificateOfTitle.setText(UiUtility.nullEqualsNone(self.feature._certificateOfTitle))
        self.uAppellation.setText(UiUtility.nullEqualsNone(self.feature._appellation))

    def closeDlg (self):
        ''' close form '''
        self.reject()

    # now that 'update' requires the same concept - seems like this needs to be shipped somewhere modular
    def submitAddress(self):
        ''' take users input from form and submit to AIMS API '''
        # Run through the setters
        UiUtility.formToaddObj(self)
        # load address to AIMS Via API
        payload = self.feature.aimsObject()
        # Capture the returned response (response distilled down to list of errors)
        valErrors = self._controller.updateFeature(payload)
        
        if len(valErrors) == 0:
            self.closeDlg()
        else:
            QMessageBox.warning(iface.mainWindow(),"Create Address Point", valErrors)
                 
    def fullNumChanged(self, newnumber):
        UiUtility.fullNumChanged(self, newnumber)
       
    def getRcl(self):
        pass
        #rcl = getRclTool(self.iface, self._layerManager)
        
        