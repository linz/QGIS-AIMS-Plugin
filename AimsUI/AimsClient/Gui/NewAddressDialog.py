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
from AimsUI.AimsClient.AimsApi import *
from qgis.utils import iface

class NewAddressDialog(Ui_NewAddressDialog, QDialog):
    
    @classmethod
    def newAddress( cls, coords, addInstance, parent=None):
        dlg = NewAddressDialog(parent, coords, addInstance)
        dlg.exec_()
  
    def __init__( self, parent, coords, addInstance):
        QDialog.__init__( self, parent )  
        self.setupUi(self)
        self.iface = iface
        self.coords = coords
        self.address = addInstance
   
        # limit user inputs
        intValidator = QIntValidator()    
        self.uExternalAddId.setValidator(intValidator)
        self.uBase.setValidator(intValidator)
        self.uHigh.setValidator(intValidator)

        self.uAlpha.setValidator(QRegExpValidator(QRegExp(r'^[A-Za-z]{0,3}'), self))
        self.uUnit.setValidator(QRegExpValidator(QRegExp(r'^\w+'), self))
        self.uPrefix.setValidator(QRegExpValidator(QRegExp(r'^\w+'), self))
 
        # Set form combobox default values
        self.uAddressType.addItems(['Road', 'Water'])
        self.ulifeCycle.addItems(['Current', 'Proposed', 'Retired'])
        self.uUnitType.addItems([None, 'Apartment', 'Villa', 'Shop', 'Banana'])
        self.uLevelType.addItems([None, 'Ground', 'Floor', 'Basement', 'Sub-basement', 'Sub-sub-basement', 'Mezzanine'])
        self.UObjectType.addItems(['Parcel', 'Building'])
                    
        # Make connections
        self.uFullNum.textChanged.connect(self.fullNumChanged)
        self.uSubmitAddressButton.clicked.connect(self.submitAddress)
        self.uGetRclToolButton.clicked.connect(self.getRcl)
        self.uAbort.clicked.connect(self.closeDlg)
        self.show()

        # Need to connect abort button and ensure address instance destroyed  
    def closeDlg (self):
        self.reject()
        # Need to destroy with with statement back at createNewAddressTool
    
    def wsEqualsNone (self, uInput): #
        ''' convert whitespace to None '''
        if uInput == '':
            return None
        else: return uInput
         
    def submitAddress( self ):
        ''' take users input from form and submit to AIMS API '''
        # Run through the setters
        self.address.setAddressType(str(self.uAddressType.currentText()))
        self.address.setExternalAddressId(self.wsEqualsNone(str(self.uExternalAddId.text())))
        self.address.setExternalAddressIdScheme(self.wsEqualsNone(str(self.uExternalAddressIdScheme.text())))
        self.address.setLifecycle(str(self.ulifeCycle.currentText()))
        self.address.setUnitType(self.wsEqualsNone(str(self.uUnitType.currentText())))
        self.address.setUnitValue(self.wsEqualsNone(str(self.uUnit.text()).upper()))
        self.address.setLevelType(self.wsEqualsNone(str(self.uLevelType.currentText())))
        self.address.setLevelValue(self.wsEqualsNone(str(self.uLevelValue.text())))
        self.address.setAddressNumberPrefix(self.wsEqualsNone(str(self.uPrefix.text()).upper()))         
        self.address.setAddressNumberSuffix(self.wsEqualsNone(str(self.uAlpha.text()).upper()))     
        # Below must be int, else set to None ### Validation has made special handling of int redundant
        self.address.setAddressNumber(int(self.uBase.text())) if self.uBase.text().isnumeric() else self.address.setAddressNumber(None)
        self.address.setAddressNumberHigh(int(self.uHigh.text())) if self.uHigh.text().isnumeric() else self.address.setAddressNumberHigh(None)
        self.address.setRoadCentrelineId(int(self.uRoadCentrelineId.text())) if self.uRoadCentrelineId.text().isnumeric() else self.address.setRoadCentrelineId(None)
        # Roads
        self.address.setRoadPrefix(self.wsEqualsNone(str(self.uRoadPrefix.text())))
        self.address.setRoadName(self.wsEqualsNone(self.uRoadName.text().encode('utf-8')))
        self.address.setRoadTypeName(self.wsEqualsNone(str(self.uRoadTypeName.text())))
        self.address.setRoadSuffix(self.wsEqualsNone(str(self.uRoadSuffix.text())))
        self.address.setWaterRouteName(self.wsEqualsNone(self.uWaterRouteName.text().encode('utf-8')))
        self.address.setWaterName(self.wsEqualsNone(str(self.uWaterName.text())))
        self.address.setAoType(str(self.UObjectType.currentText()))
        self.address.setAoName(self.wsEqualsNone(self.uObjectName.text().encode('utf-8'))) 
        self.address.set_x(self.coords.x()) 
        self.address.set_y(self.coords.y())
        # address.setCrsType(self.  )
        # address.setCrsProperties(self.  )
        # Address Object
        self.address.setExternalObjectId(str(self.uExternalObjectId.text()))
        self.address.setExternalObjectIdScheme(str(self.uExtObjectIdScheme.text()))
        self.address.setValuationReference(str(self.uValuationReference.text())) 
        self.address.setCertificateOfTitle(self.wsEqualsNone(self.uCertificateOfTitle.text().encode('utf-8')))
        self.address.setAppellation(self.wsEqualsNone(self.uAppellation.text().encode('utf-8')))
        self.address.setSourceReason(self.uNotes.toPlainText().encode('utf-8'))   

        # load address to AIMS Via API
        #payload = Address.objectify(self.address) 
        payload = self.address.objectify()
        # Capture the returned response (response distilled down to list of errors)
        valErrors = AimsApi().changefeedAdd(payload)
        
        if len(valErrors) == 0:
            self.closeDlg()
        else:
            QMessageBox.warning(iface.mainWindow(),"Create Address Point", valErrors)
                 
    def fullNumChanged(self, newnumber):
        ''' Sets address components based on user inputted "full address" '''
        # Set address components to None
        [i.setText(None) for i in ([self.uPrefix, self.uUnit, self.uBase, self.uAlpha, self.uHigh])]
        # Split full address into components
        if '-' not in newnumber: 
            p = re.compile(r'^(?P<flat_prefix>[A-Z]+)?(?:\s)?(?P<flat>[0-9]+/\s*|^[A-Z]{,2}/\s*)?(?P<base>[0-9]+)(?P<alpha>[A-Z]+)?$') 
            m = p.match(newnumber.upper())
            try:
                if m.group('flat_prefix') is not None: self.uPrefix.setText(m.group('flat_prefix'))
                if m.group('flat') is not None: self.uUnit.setText(m.group('flat').strip('/'))
                if m.group('base') is not None: self.uBase.setText(m.group('base'))
                if m.group('alpha') is not None: self.uAlpha.setText(m.group('alpha'))
            except:
                pass #silently  
        else:
            p = re.compile(r'^(?P<flat_prefix>[A-Z]+)?(?:\s)?(?P<flat>[0-9]+/\s*|^[A-Z]{,2}/\s*)?(?P<base>[0-9]+)(?:-)(?P<high>[0-9]+)$') 
            m = p.match(newnumber.upper())
            try:
                if m.group('flat_prefix') is not None: self.uPrefix.setText(m.group('flat_prefix'))
                if m.group('flat') is not None: self.uUnit.setText(m.group('flat').strip('/'))
                if m.group('base') is not None: self.uBase.setText(m.group('base'))
                if m.group('high') is not None: self.uHigh.setText(m.group('high'))
            except:
                pass #silently  
        
    def getRcl(self):
        pass