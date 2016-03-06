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
from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *
from PyQt4.QtCore import QRegExp
import re

class UiUtility (object):
    ''' Where modular methods live and are leveraged '''
    
    uiObjMappings = {'uWarning':['_warning','setWarnings', 'getWarnings'],
                    'uNotes':['_workflow_sourceReason','setSourceReason', None],
                    'uAddressType':['_components_addressType','setAddressType', None], 
                    'ulifeCycle':['_components_lifecycle','setLifecycle', None],   
                    'uLevelType':['_components_levelType','setLevelType', None], 
                    'uLevelValue':['_components_levelValue','setLevelValue', None], 
                    'uUnitType':['_components_unitType','setUnitType', None],
                    'uUnit':['_components_unitValue','setUnitValue', None],
                    'uPrefix':['_components_addressNumberPrefix','setAddressNumberPrefix', None],
                    'uBase':['_components_addressNumber','setAddressNumber', None],
                    'uAlpha':['_components_addressNumberSuffix','setAddressNumberSuffix', None],
                    'uHigh':['_components_addressNumberHigh','setAddressNumberHigh', None],
                    'uExternalIdScheme':['_components_externalAddressIdScheme','setExternalAddressIdScheme', None],
                    'uExternalAddId':['_components_externalAddressId','setExternalAddressId', None], 
                    'uRclId':['_components_roadCentrelineId','setRoadCentrelineId', None],
                    'uRoadPrefix':['_components_roadSuffix','setRoadSuffix', None],
                    'uRoadName':['_components_roadName','setRoadName', None], 
                    'uRoadTypeName':['_components_roadType','setRoadType', None],   
                    'uRoadSuffix':['_components_roadSuffix','setRoadSuffix', None], 
                    'uWaterName':['_components_waterName','setWaterName', None], 
                    'uWaterRouteName':['_components_waterRoute','setWaterRoute', None],
                    'uObjectType':['_addressedObject_objectType','setObjectType', None],
                    'uObjectName':['_addressedObject_objectName','setObjectName', None],
                    'uExtObjectIdScheme':['_addressedObject_externalObjectIdScheme','setExternalObjectIdScheme', None],
                    'uExternalObjectId':['_addressedObject_externalObjectId','setExternalObjectId', None],
                    'uValuationReference':['_addressedObject_valuationReference','setValuationReference', None],
                    'uCertificateOfTitle':['_addressedObject_certificateOfTitle','setCertificateOfTitle', None],
                    'uAppellation':['_addressedObject_appellation','setAppellation', None],
                    }
    
    @staticmethod
    def transform (iface, coords, tgt=4167):       
        src_crs = iface.mapCanvas().mapSettings().destinationCrs()
        tgt_crs = QgsCoordinateReferenceSystem()
        tgt_crs.createFromOgcWmsCrs('EPSG:{}'.format(tgt))
        transform = QgsCoordinateTransform( src_crs, tgt_crs )
        return transform.transform( coords.x(), coords.y() ) 
            
    @staticmethod
    def highlight (iface, coords, iconType = QgsVertexMarker.ICON_BOX):
    #function may be moved later to a 'highlight' module
        adrMarker = QgsVertexMarker(iface.mapCanvas())
        adrMarker.setIconSize(15)
        adrMarker.setPenWidth(2)
        adrMarker.setIconType(iconType)
        adrMarker.setCenter( coords )
        adrMarker.show()
        return adrMarker
    
    @staticmethod
    def rclHighlight(canvas, geom, rclLayer):
        rclMarker = QgsRubberBand(canvas,False)
        rclMarker.hide()
        rclMarker.setWidth(3)
        rclMarker.setColor(QColor(76,255,0))
        rclMarker.setToGeometry(geom,rclLayer)
        rclMarker.show()
        return rclMarker
            
    @staticmethod
    def setFormCombos(self):
        #all no have the first value set as None - modal specific defualts now need to be
        # set from the parent
        self.uAddressType.addItems(['Road', 'Water'])
        self.ulifeCycle.addItems(['Current', 'Proposed', 'Retired'])
        self.uUnitType.addItems([None, 'Apartment', 'Kiosk', 'Room', 'Shop', 'Suite', 'Villa',  'Flat', 'Unit'])#require feed back as to approved values
        self.uLevelType.addItems([None, 'Floor', "Level"])
        self.uObjectType.addItems(['Parcel', 'Building'])
        self.uPositionType.addItems(['Unknown', 'Centroid', 'Label', 'Set Back off Road'])
        # if instance == chnagefeed or review object the also set 
        # uChangeType [new, update, retire]

    @staticmethod
    def formMask(self):        
        intValidator = QIntValidator()    
        self.uExternalAddId.setValidator(intValidator)
        self.uBase.setValidator(intValidator)
        self.uHigh.setValidator(intValidator)
        self.uAlpha.setValidator(QRegExpValidator(QRegExp(r'^[A-Za-z]{0,3}'), self))
        self.uUnit.setValidator(QRegExpValidator(QRegExp(r'^\w+'), self))
        self.uPrefix.setValidator(QRegExpValidator(QRegExp(r'^\w+'), self))
    
    @staticmethod
    def nullEqualsNone (uInput): #Now also handeling NULL
        ''' convert whitespace to None '''
        if uInput == '' or uInput == 'NULL':
            return None
        else: return uInput
    
    @staticmethod
    def featureToUi(self):
        """ for populating to update tool ui and queue edit ui """
        UiUtility.setEditability(self)
        
        for ui, objProp in UiUtility.uiObjMappings.items():
            # Test the UI has the relative UI component 
            if hasattr(self, ui):
                uiElement = getattr(self, ui)
            else: 
                continue
            # Test the object has the required property
            if hasattr(self.feature, objProp[0]):                                     
                if objProp[2]: 
                    # use getter
                    prop = str(getattr(self.feature, objProp[2]))
                else:
                    # go straight for the objects property 
                    prop = str(getattr(self.feature, objProp[0]))
                if isinstance(uiElement, QLineEdit) or isinstance(uiElement, QLabel):
                    if ui == 'uWarning': pass# or ui == 'uNotes': # if a warning we need to undertake some formatting
                    #    warnings = ''  
                    #    for warning in getattr(self)['warn']:
                    #        warnings+=(warning._severity).upper()+': '+warning._description+('\n'*2)
                    #    uiElement.setText(warnings)
                    else: 
                        uiElement.setText(prop)
                elif isinstance(uiElement, QComboBox):
                    uiElement.setCurrentIndex(0)  
                    uiElement.setCurrentIndex(QComboBox.findText(uiElement, prop))
    
    @staticmethod
    def formToObj(self):
        ''' serves both the gathering of user data
        from the purposes of new address creation and
        address feature updates ''' # should expanded scope to include queue views to obj

        for uiElement, objProp in UiUtility.uiObjMappings.items():              
            if hasattr(self, uiElement): # test if the ui widget/ form ... has the ui component
 
                uiElement = getattr(self, uiElement)                   
                setter = getattr(self.feature, objProp[1])
                if isinstance(uiElement, QLineEdit) and uiElement.text() != '' and uiElement.text() != 'NULL':
                    setter(uiElement.text().encode('utf-8'))
                elif isinstance(uiElement, QComboBox) and uiElement.currentText() != '' and uiElement.currentText() != 'NULL':
                        setter(uiElement.currentText())
                elif isinstance(uiElement, QPlainTextEdit)and uiElement.toPlainText() != '' and uiElement.toPlainText() != 'NULL':
                        setter(uiElement.toPlainText().encode('utf-8'))
    
    @staticmethod               
    def setEditability(self):
        
        widgetChildern = self.findChildren(QWidget, QRegExp(r'^u.*'))
        for child in widgetChildern:
            child.setEnabled(True)
            if isinstance(child, QLineEdit) or isinstance(child, QLabel):
                child.clear()
            elif isinstance(child, QComboBox) and not self.uAddressType:
                child.setCurrentIndex(0)
                          
        if self.uAddressType.currentText() == 'Road':
            waterChildern = self.findChildren(QWidget, QRegExp(r'Water.*'))
            for child in waterChildern:
                child.setDisabled(True)
                
        elif self.uAddressType.currentText() == 'Water':
            roadChildern = self.findChildren(QWidget, QRegExp(r'Road.*'))
            for child in roadChildern:
                child.setDisabled(True)  

    @staticmethod
    def fullNumChanged(obj, newnumber):
        ''' splits a full (user inputted) address string into address components '''
        # Set address components to None
        [i.setText(None) for i in ([obj.uPrefix, obj.uUnit, obj.uBase, obj.uAlpha, obj.uHigh])]
        # Split full address into components
        if '-' not in newnumber: 
            p = re.compile(r'^(?P<flat_prefix>[A-Z]+)?(?:\s)?(?P<flat>[0-9]+/\s*|^[A-Z]{,2}/\s*)?(?P<base>[0-9]+)(?P<alpha>[A-Z]+)?$') 
            m = p.match(newnumber.upper())
            try:
                if m.group('flat_prefix') is not None: obj.uPrefix.setText(m.group('flat_prefix'))
                if m.group('flat') is not None: obj.uUnit.setText(m.group('flat').strip('/'))
                if m.group('base') is not None: obj.uBase.setText(m.group('base'))
                if m.group('alpha') is not None: obj.uAlpha.setText(m.group('alpha'))
            except:
                pass #silently  
        else:
            p = re.compile(r'^(?P<flat_prefix>[A-Z]+)?(?:\s)?(?P<flat>[0-9]+/\s*|^[A-Z]{,2}/\s*)?(?P<base>[0-9]+)(?:-)(?P<high>[0-9]+)(?P<alpha>[A-Z]+)?$') 
            m = p.match(newnumber.upper())
            try:
                if m.group('flat_prefix') is not None: obj.uPrefix.setText(m.group('flat_prefix'))
                if m.group('flat') is not None: obj.uUnit.setText(m.group('flat').strip('/'))
                if m.group('base') is not None: obj.uBase.setText(m.group('base'))
                if m.group('high') is not None: obj.uHigh.setText(m.group('high'))
                if m.group('alpha') is not None: obj.uAlpha.setText(m.group('alpha'))
            except:
                pass #silently  
    
        