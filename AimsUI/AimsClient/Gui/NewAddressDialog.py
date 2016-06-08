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

class NewAddressDialog(Ui_NewAddressDialog, QDialog):
    
    @classmethod
    def newAddress(cls, addInstance, layerManager, controller,parent = None, coords = None):
        dlg = NewAddressDialog(parent, coords, addInstance, layerManager, controller)
        dlg.exec_()
  
    def __init__(self, parent, coords, addInstance, layerManager, controller):
        QDialog.__init__( self, parent )  
        self.setupUi(self)
        self.iface = iface
        self.coords = coords
        self.feature = addInstance
        self._layerManager = layerManager
        self._controller = controller
   
        # limit user inputs
        UiUtility.formMask(self)
        # set combo box defaults
        UiUtility.setFormCombos(self)
                    
        # Make connections
        self.uFullNum.textChanged.connect(self.fullNumChanged)
        self.uSubmitAddressButton.clicked.connect(self.submitAddress)
        self.uGetRclToolButton.clicked.connect(self.getRcl)
        self.uAbort.clicked.connect(self.closeDlg)
        self.show()

    def closeDlg (self):
        ''' close form '''
        self.reject()
        
    # now that 'update' requires the same concept - seems like this needs to be shipped somewhere modular
    def submitAddress(self):
        ''' take users input from form and submit to AIMS API '''
        # Run through the setters
        self.feature.set_x(self.coords.x()) 
        self.feature.set_y(self.coords.y())
        UiUtility.formToaddObj(self)
        # load address to AIMS Via API
        payload = self.feature.aimsObject()
        # Capture the returned response (response distilled down to list of errors)
        valErrors = self._controller.newAddress(payload)
        
        if len(valErrors) == 0:
            self.closeDlg()
        else:
            QMessageBox.warning(iface.mainWindow(),"Create Address Point", valErrors)
                 
    def fullNumChanged(self, newnumber):
        UiUtility.fullNumChanged(self, newnumber)
        
    def getRcl(self):
        pass
        #rcl = getRclTool(self.iface, self._layerManager)