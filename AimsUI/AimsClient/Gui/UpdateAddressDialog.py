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
from UiUtility import UiUtility

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
        self.rejected.connect(self.closeDlg)
        self.uFullNum.textEdited.connect(self.fullNumChanged)   
        self.uPrefix.textEdited.connect(self.partNumChanged)
        self.uUnit.textEdited.connect(self.partNumChanged)
        self.uBase.textEdited.connect(self.partNumChanged)
        self.uHigh.textEdited.connect(self.partNumChanged)
        self.uAlpha.textEdited.connect(self.partNumChanged)
        self.uGetRclToolButton.clicked.connect(self.getRcl) 
        self.uAddressType.currentIndexChanged.connect(self.setEditability)    
        # set forms feature values
        #UiUtility.addObjToForm(self, self.feature) < -- old form population method          
        UiUtility.featureToUi(self)     
        self.show()
    
    def setEditability(self):
        UiUtility.setEditability(self)
    
    def getRcl(self):
        self._controller.startRclTool(self)
    
    def closeDlg (self):
        ''' close form '''
        self._controller.setPreviousMapTool()
        self.reject()
    
    # now that 'update' requires the same concept - seems like this needs to be shipped somewhere modular
    def submitAddress(self):
        ''' take users input from form and submit to AIMS API '''
        # Run through the setters
        UiUtility.formToObj(self)
        # submit address obj to DM
        self._controller.dm.updateAddress(self.feature)
        # need to check the response 
        self.closeDlg()
        # old direct API method
        ''' 
        # load address to AIMS Via API
        payload = self.feature.aimsObject()
        # Capture the returned response (response distilled down to list of errors)
        valErrors = self._controller.updateFeature(payload)
        
        if len(valErrors) == 0:
            self.closeDlg()
        else:
            QMessageBox.warning(iface.mainWindow(),"Create Address Point", valErrors)
        '''
    def fullNumChanged(self, newnumber):
        UiUtility.fullNumChanged(self, newnumber)
    
    def partNumChanged(self,):
        if self.uUnit.text(): unit = self.uUnit.text()+'/' 
        else: unit = ''
        
        if self.uHigh.text(): high = '-'+self.uHigh.text()
        else: high = ''
        
        self.uFullNum.setText(self.uPrefix.text().upper()+unit+self.uBase.text()+high+self.uAlpha.text().upper())
                 