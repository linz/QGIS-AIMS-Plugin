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


class NewAddressDialog(Ui_NewAddressDialog, QDialog):
    
    @classmethod
    def newAddress( cls, coords, addInstance, parent=None):
        dlg = NewAddressDialog(parent, coords, addInstance)
        dlg.exec_()
    
    def __init__( self, parent, coords, addInstance ):
        QDialog.__init__( self, parent )
        self.setupUi(self)
        
        self.coords = coords
        self.address = addInstance
     
        # set form combobox default values
        self.uAddressType.addItems(['Road', 'Water'])
        self.ulifeCycle.addItems(['Current', 'Proposed', 'Retired'])
        self.uUnitType.addItems([None, 'Apartment', 'Villa', 'Shop', 'Banana'])
        self.uLevelType.addItems([None, 'Ground', 'Floor', 'Basement', 'Sub-basement', 'Sub-sub-basement', 'Mezzanine'])
        self.UObjectType.addItems(['Parcel', 'Building'])
                    
        # Connect uSubmitAddressButton to function
        self.uFullNum.textChanged.connect(self.FullNumChanged)
        self.uSubmitAddressButton.clicked.connect(self.submitAddress)
        # Need to connect abort button and ensure address instance destroyed
             
    
    def wsEqualsNone (self, uInput):
        ''' convert whitespace to None '''
        if uInput == '':
            return None
        else: return uInput
        
        
    def submitAddress( self ):
        ''' take users input from form and submit to AIMS API '''
        # Need to pass to validation function prior to the below 
        self.address.setAddressType(str(self.uAddressType.currentText()))
        self.address.setExternalAddressId(self.wsEqualsNone(str(self.uExternalAddId.text())))

        self.address.setExternalAddressId(self.wsEqualsNone(str(self.uExternalAddId.text())))
        self.address.setExternalAddressIdScheme(self.wsEqualsNone(str(self.uExternalAddressIdScheme.text())))
        self.address.setLifecycle(str(self.ulifeCycle.currentText()))
        self.address.setUnitType(self.wsEqualsNone(str(self.uUnitType.currentText())))
        self.address.setUnitValue(self.wsEqualsNone(str(self.uUnit.text())))
        self.address.setLevelType(self.wsEqualsNone(str(self.uLevelType.currentText())))
        self.address.setLevelValue(self.wsEqualsNone(str(self.uLevelValue.text())))
        self.address.setAddressNumberPrefix(self.wsEqualsNone(str(self.uPrefix.text())))         
        self.address.setAddressNumberSuffix(self.wsEqualsNone(str(self.uAlpha.text())))
        
        # Below must be int, else set to None
        self.address.setAddressNumber(int(self.uBase.text())) if self.uBase.text().isnumeric() else self.address.setAddressNumber(None)
        self.address.setAddressNumberHigh(int(self.uHigh.text())) if self.uHigh.text().isnumeric() else self.address.setAddressNumberHigh(None)
        self.address.setRoadCentrelineId(int(self.uRoadCentrelineId.text())) if self.uRoadCentrelineId.text().isnumeric() else self.address.setRoadCentrelineId(None)

        self.address.setRoadPrefix(self.wsEqualsNone(str(self.uRoadPrefix.text())))
        self.address.setRoadName(self.wsEqualsNone(str(self.uRoadName.text())))
        self.address.setRoadTypeName(self.wsEqualsNone(str(self.uRoadTypeName.text())))
        self.address.setRoadSuffix(self.wsEqualsNone(str(self.uRoadSuffix.text())))
        self.address.setWaterRouteName(self.wsEqualsNone(str(self.uWaterRouteName.text())))
        self.address.setWaterName(self.wsEqualsNone(str(self.uWaterName.text())))
        self.address.setAoType(str(self.UObjectType.currentText()))
        self.address.setAoName(self.wsEqualsNone(str(self.uObjectName.text())))  
        self.address.set_x(self.coords.x()) 
        self.address.set_y(self.coords.y())
        #address.setCrsType(self.  )
        #address.setCrsProperties(self.  )
        self.address.setExternalObjectId(str(self.uExternalObjectId.text()))
        self.address.setExternalObjectIdScheme(str(self.uExtObjectIdScheme.text()))
        self.address.setValuationReference(str(self.uValuationReference.text())) 
        self.address.setCertificateOfTitle(str(self.uCertificateOfTitle.text()))
            
        # load address to AIMS Via API
        payload = Address.objectify(self.address)
        success = AimsApi().changefeedAdd(payload)
        
        if success:
            pass
            
        
    def createNewApi(self):
        pass
                        
    def FullNumChanged(self, newnumber):
        ''' sets address components based on user supplied full address '''
        # set address components to None
        [i.setText(None) for i in ([self.uPrefix, self.uUnit, self.uBase, self.uAlpha, self.uHigh])]
        # split full address into components
        p = re.compile(r'^(?P<flat_prefix>[A-Z]+)?(?:\s)?(?P<flat>[0-9]+/\s*|^[A-Z]{,2}/\s*)?(?P<base>[0-9]+)(?P<alpha>[A-Z]+)?$') 
        m = p.match(newnumber.upper())
        try:
            if m.group('flat_prefix') is not None: self.uPrefix.setText(m.group('flat_prefix'))
            if m.group('flat') is not None: self.uUnit.setText(m.group('flat').strip('/'))
            if m.group('base') is not None: self.uBase.setText(m.group('base'))
            if m.group('alpha') is not None: self.uAlpha.setText(m.group('alpha'))
        except:
            pass #silently