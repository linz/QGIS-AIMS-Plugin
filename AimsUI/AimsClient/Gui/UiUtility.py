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
import time

from AIMSDataManager.AimsLogging import Logger

uilog = None

class UiUtility (object):
    ''' Where modular methods live and are leveraged '''

    # logging
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    retainInfo = [ 'v0005', 'v0006', 'v0007', 'v0012', 'v0023', 'RP001', 'RP002' ]
        
    uiObjMappings = {'uWarning':['_warning','setWarnings', '_getEntities' ],
                    'uNotes':['_workflow_sourceReason','setSourceReason', ''],
                    'uAddressType':['_components_addressType','setAddressType', ''], 
                    'ulifeCycle':['_components_lifecycle','setLifecycle', ''],   
                    'uLevelType':['_components_levelType','setLevelType', ''], 
                    'uLevelValue':['_components_levelValue','setLevelValue', ''], 
                    'uUnitType':['_components_unitType','setUnitType', ''],
                    'uUnit':['_components_unitValue','setUnitValue', ''],
                    'uPrefix':['_components_addressNumberPrefix','setAddressNumberPrefix', ''],
                    'uBase':['_components_addressNumber','setAddressNumber', ''],
                    'uAlpha':['_components_addressNumberSuffix','setAddressNumberSuffix', ''],
                    'uHigh':['_components_addressNumberHigh','setAddressNumberHigh', ''],
                    'uExternalIdScheme':['_components_externalAddressIdScheme','setExternalAddressIdScheme', ''],
                    'uExternalAddId':['_components_externalAddressId','setExternalAddressId', ''], 
                    'uRclId':['_components_roadCentrelineId','setRoadCentrelineId', ''],
                    'uRoadPrefix':['_components_roadSuffix','setRoadSuffix', ''],
                    'uRoadName':['_components_roadName','setRoadName', ''], 
                    'uRoadTypeName':['_components_roadType','setRoadType', ''],   
                    'uRoadSuffix':['_components_roadSuffix','setRoadSuffix', ''], 
                    'uWaterName':['_components_waterName','setWaterName', ''], 
                    'uWaterRouteName':['_components_waterRoute','setWaterRoute', ''],
                    'uObjectType':['_addressedObject_objectType','setObjectType', ''],
                    'uObjectName':['_addressedObject_objectName','setObjectName', ''],
                    'uExtObjectIdScheme':['_addressedObject_externalObjectIdScheme','setExternalObjectIdScheme', ''],
                    'uExternalObjectId':['_addressedObject_externalObjectId','setExternalObjectId', ''],
                    'uValuationReference':['_addressedObject_valuationReference','setValuationReference', ''],
                    'uCertificateOfTitle':['_addressedObject_certificateOfTitle','setCertificateOfTitle', ''],
                    'uAppellation':['_addressedObject_appellation','setAppellation', ''],
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
        ''' highlight aims features '''
        adrMarker = QgsVertexMarker(iface.mapCanvas())
        adrMarker.setIconSize(15)
        adrMarker.setPenWidth(2)
        adrMarker.setIconType(iconType)
        adrMarker.setCenter( coords )
        adrMarker.show()
        return adrMarker
    
    @staticmethod
    def rclHighlight(canvas, geom, rclLayer):
        ''' highlight selected road centreline '''
        rclMarker = QgsRubberBand(canvas,False)
        rclMarker.hide()
        rclMarker.setWidth(3)
        rclMarker.setColor(QColor(76,255,0))
        rclMarker.setToGeometry(geom,rclLayer)
        rclMarker.show()
        return rclMarker
            
    @staticmethod
    def setFormCombos(self):
        ''' set combo boxes to defualt values '''
        # set from the parent
        self.uAddressType.addItems(['Road', 'Water'])
        self.ulifeCycle.addItems(['Current', 'Proposed', 'Retired'])
        self.uUnitType.addItems([None, 'Apartment', 'Kiosk', 'Room', 'Shop', 'Suite', 'Villa',  'Flat', 'Unit'])
        self.uLevelType.addItems([None, 'Floor', "Level"])
        self.uObjectType.addItems(['Parcel', 'Building'])
        self.uPositionType.addItems(['Unknown', 'Centroid', 'Label', 'Set Back off Road'])

    @staticmethod
    def formMask(self): 
        ''' mask form input values '''       
        intValidator = QIntValidator()    
        self.uExternalAddId.setValidator(intValidator)
        self.uBase.setValidator(intValidator)
        self.uHigh.setValidator(intValidator)
        self.uAlpha.setValidator(QRegExpValidator(QRegExp(r'^[A-Za-z]{0,3}'), self))
        self.uUnit.setValidator(QRegExpValidator(QRegExp(r'^\w+'), self))
        self.uPrefix.setValidator(QRegExpValidator(QRegExp(r'^\w+'), self))
    
    @staticmethod
    def nullEqualsNone (uInput): #Now also handling NULL
        ''' convert whitespace to None '''
        if uInput == '' or uInput == 'NULL':
            return None
        else: return uInput
    
    @staticmethod
    def featureToUi(self):
        """ populates update form and review editor queue from aims obj """
        UiUtility.setEditability(self)
        UiUtility.clearForm(self)
        
        for ui, objProp in UiUtility.uiObjMappings.items():
            # Test the UI has the relative UI component 
            if hasattr(self, ui):
                uiElement = getattr(self, ui)
            else: 
                continue
            # Test the object has the required property or a getter
            if hasattr(self.feature, objProp[0]) or hasattr(self.feature, objProp[2]):                                     
                if objProp[2]: 
                    # use getter
                    prop = (getattr(self.feature, objProp[2])())
                else:
                    # go straight for the objects property 
                    prop = str(getattr(self.feature, objProp[0]))
                if isinstance(uiElement, QLineEdit) or isinstance(uiElement, QLabel):
                    if ui == 'uWarning':
                        warnings = ''                        
                        for i in prop:
                            try: #<-- temp. currently retires are under going reformatting at the api level - then this can be removed 
                                if i._severity == 'Info' and i._ruleId not in UiUtility.retainInfo: continue
                                warnings += i._severity.upper()+': '+ i._description+('\n'*2)
                            except: pass #temp                             
                        uiElement.setText(warnings)
                    else: 
                        uiElement.setText(prop)
                elif isinstance(uiElement, QComboBox):
                    uiElement.setCurrentIndex(0)  
                    uiElement.setCurrentIndex(QComboBox.findText(uiElement, prop))
    
    @staticmethod
    def formToObj(self):
        ''' maps user input fromt he new and update form
            as well as queue editor widget to AIM objects '''
        try: 
            form = self.uQueueEditor 
        except: 
            form = self
        
        for uiElement, objProp in UiUtility.uiObjMappings.items():
            #user can not mod warnings ... continiue              
            if uiElement == 'uWarning':            
                continue            
            # test if the ui widget/ form ... has the ui component
            if hasattr(form, uiElement): 
                uiElement = getattr(form, uiElement)                   
                setter = getattr(self.feature, objProp[1])
                if isinstance(uiElement, QLineEdit):# and uiElement.text() != '' and uiElement.text() != 'NULL':
                    setter(uiElement.text().encode('utf-8'))
                elif isinstance(uiElement, QComboBox):# and uiElement.currentText() != '' and uiElement.currentText() != 'NULL':
                        setter(uiElement.currentText())
                elif isinstance(uiElement, QPlainTextEdit):#and uiElement.toPlainText() != '' and uiElement.toPlainText() != 'NULL':
                        setter(uiElement.toPlainText().encode('utf-8'))
                        
    @staticmethod 
    def clearForm(self):
        ''' clear UI forms and widgets '''              
        widgetChildern = self.findChildren(QWidget, QRegExp(r'^u.*'))
        for child in widgetChildern:
            child.setEnabled(True)
            if isinstance(child, QLineEdit) or isinstance(child, QLabel):
                child.clear()
            elif isinstance(child, QComboBox) and child.objectName() != 'uAddressType':
                child.setCurrentIndex(0)
        
    @staticmethod               
    def setEditability(self):  
        ''' toggle editable relevant fields depending 
            on the objects Address Type (road or water) '''
        for child in self.findChildren(QWidget):
            child.setEnabled(True)
                             
        if self.uAddressType.currentText() == 'Road':
            waterChildern = self.findChildren(QWidget, QRegExp(r'Water.*'))
            for child in waterChildern:
                child.clear() 
                child.setDisabled(True)
                
        elif self.uAddressType.currentText() == 'Water':
            roadChildern = self.findChildren(QWidget, QRegExp(r'Road.*'))
            for child in roadChildern:
                child.clear() 
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
    
    @staticmethod
    def displayWarnings (warnings, iface):
        ''' raise warning to the user '''
        message = ''
        for warning in warnings:
            message += u'\u2022 {}\n'.format(warning)
        QMessageBox.warning(iface.mainWindow(),"Create Address Point", message)
    
    @staticmethod
    def processWarnings (resp, respId, iface, feedType, i):
        ''' compile al ist of warnings that are at the "Reject" level '''
        warnings = []
        for r in resp:
            if r.meta._requestId == respId:  
                #logging
                uilog.info('response received from DM for respId: {0} of type: {1} after {2} seconds'.format(respId, feedType, i))    
                for warning in r._entities:
                    if warning['properties']['severity'] in ('Reject', 'critical'):
                        warnings.append(warning['properties']['description'])
                if warnings:
                    UiUtility.displayWarnings(warnings, iface)
                return True
    
    @staticmethod
    def handleResp(respId, controller, feedType, iface):
        ''' test for a response in the response
            queue with the relevant repId'''
        #return # temp
        for i in range(0,15):
            time.sleep(1)
            resp = controller.uidm.response(feedType)
            if resp:
                if UiUtility.processWarnings(resp, respId, iface, feedType, i):
                    return
            #logging 
        uilog.info('Time Out ({0} seconds): No response received from DM for respId: {1} of feedtype: {2}'.format(i, respId, feedType))    
   
           
        
            