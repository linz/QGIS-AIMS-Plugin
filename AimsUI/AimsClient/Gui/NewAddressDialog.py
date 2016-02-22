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
from AimsUI.AimsClient.Gui.UiUtility import UiUtility

from qgis.utils import iface

class NewAddressDialog(Ui_NewAddressDialog, QDialog):
    
    @classmethod
    def newAddress(cls, addInstance, layerManager, controller, parent = None, coords = None):
        dlg = NewAddressDialog(parent, coords, addInstance, layerManager, controller)
        dlg.exec_()
  
    def __init__(self, parent, coords, addInstance, layerManager, controller):
        QDialog.__init__( self, parent )  
        self.setupUi(self)
        self._iface = iface
        self.coords = coords
        self.feature = addInstance
        self._layerManager = layerManager
        self._controller = controller
                
        # limit user inputs
        UiUtility.formMask(self)
        # set combo box defaults
        UiUtility.setFormCombos(self)
                    
        # Make connections
        self.uFullNum.textEdited.connect(self.fullNumChanged)
        self.uPrefix.textEdited.connect(self.partNumChanged)
        self.uUnit.textEdited.connect(self.partNumChanged)
        self.uBase.textEdited.connect(self.partNumChanged)
        self.uHigh.textEdited.connect(self.partNumChanged)
        self.uAlpha.textEdited.connect(self.partNumChanged)
        
        self.uSubmitAddressButton.clicked.connect(self.submitAddress)
        self.uAbort.clicked.connect(self.closeDlg)
        self.rejected.connect(self.closeDlg)
        self.uGetRclToolButton.clicked.connect(self.getRcl)
        self.show()
    
    def getRcl(self):
        self._controller.startRclTool(self)
      
    def closeDlg (self):
        ''' close form '''
        self._controller.setPreviousMapTool() # revert back to NewAddTool
        self.reject()
        
    def submitAddress(self):
        ''' take users input from form and submit to AIMS API '''
        # Run through the setters
        
        #self.feature.set_x(self.coords.x()) <-- joe building setter now 
        #self.feature.set_y(self.coords.y())
        UiUtility.formToObj(self)
        
        
        # submit address obj to DM
        self._controller.dm.addAddress(self.feature)

        
        #need to add error handeling
        
        #if len(valErrors) == 0:
        #    self.closeDlg()
        #else:
        #    QMessageBox.warning(iface.mainWindow(),"Create Address Point", valErrors)
                 
    def fullNumChanged(self, newnumber):
        UiUtility.fullNumChanged(self, newnumber)
        
    def partNumChanged(self,):
        if self.uUnit.text(): unit = self.uUnit.text()+'/' 
        else: unit = ''
        
        if self.uHigh.text(): high = '-'+self.uHigh.text()
        else: high = ''
        
        self.uFullNum.setText(self.uPrefix.text().upper()+unit+self.uBase.text()+high+self.uAlpha.text().upper())