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
from PyQt4.QtGui import QColor, QIntValidator, QRegExpValidator, QComboBox
from PyQt4.QtCore import QRegExp
import re



class UiUtility (object):
    ''' Utility Class. Methods up for adoption
    Plans to find these a better home '''
        
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
    def setFormCombos(obj):
        #all no have the first value set as None - modal specific defualts now need to be
        # set from the parent
        obj.uAddressType.addItems([None,'Road', 'Water'])
        obj.ulifeCycle.addItems([None,'Current', 'Proposed', 'Retired'])
        obj.uUnitType.addItems([None, 'Apartment', 'Kiosk', 'Room', 'Shop', 'Suite', 'Villa',  'Flat', 'Unit'])#require feed back as to approved values
        obj.uLevelType.addItems([None, 'Floor', "Level"])
        obj.uObjectType.addItems([None,'Parcel', 'Building'])
        # if instance == chnagefeed or review object the also set 
        # uChangeType [new, update, retire]
        
        
        
    @staticmethod
    def formMask(obj):        
        intValidator = QIntValidator()    
        obj.uExternalAddId.setValidator(intValidator)
        obj.uBase.setValidator(intValidator)
        obj.uHigh.setValidator(intValidator)
        obj.uAlpha.setValidator(QRegExpValidator(QRegExp(r'^[A-Za-z]{0,3}'), obj))
        obj.uUnit.setValidator(QRegExpValidator(QRegExp(r'^\w+'), obj))
        obj.uPrefix.setValidator(QRegExpValidator(QRegExp(r'^\w+'), obj))
    
    @staticmethod
    def nullEqualsNone (uInput): #Now also handeling NULL
        ''' convert whitespace to None '''
        if uInput == '' or uInput == 'NULL':
            return None
        else: return uInput
    
    @staticmethod
    def mapResultsToAddObj (results, controller):
        # init new address obj
        feature = controller.initialiseAddressObj()
        # set obj properties    
        feature.setFullAddress(str(results.mFeature.attribute('fullAddress')))                     
        feature.setAddressType(str(results.mFeature.attribute('addressType')))
        feature.setSuburbLocality(str(results.mFeature.attribute('suburbLocality')))
        feature.setTownCity(str(results.mFeature.attribute('townCity')))
        feature.setLifecycle(str(results.mFeature.attribute('lifecycle'))) 
        feature.setRoadPrefix(str(results.mFeature.attribute('roadPrefix')))
        feature.setRoadName(str(results.mFeature.attribute('roadName')))      
        feature.setRoadSuffix(str(results.mFeature.attribute('roadSuffix')))
        feature.setRoadType(str(results.mFeature.attribute('roadType')))
        feature.setRoadCentrelineId(str(results.mFeature.attribute('roadCentrelineId')))
        feature.setWaterRoute(str(results.mFeature.attribute('waterRoute')))
        feature.setWaterName(str(results.mFeature.attribute('waterName')))
        feature.setUnitValue(str(results.mFeature.attribute('unitValue')))
        feature.setUnitType(str(results.mFeature.attribute('unitType')))
        feature.setLevelType(str(results.mFeature.attribute('levelType')))
        feature.setLevelValue(str(results.mFeature.attribute('levelValue')))
        feature.setAddressNumberPrefix(str(results.mFeature.attribute('addressNumberPrefix')))
        feature.setAddressNumber(str(results.mFeature.attribute('addressNumber')))
        feature.setAddressNumberSuffix(str(results.mFeature.attribute('addressNumberSuffix')))
        feature.setAddressNumberHigh(str(results.mFeature.attribute('addressNumberHigh')))
        feature.setVersion(str(results.mFeature.attribute('version')))
        feature.setAddressId(str(results.mFeature.attribute('addressId')))
        feature.setExternalAddressId(str(results.mFeature.attribute('externalAddressId')))
        feature.setExternalAddressIdScheme(str(results.mFeature.attribute('externalAddressIdScheme')))
        feature.setAoType(str(results.mFeature.attribute('objectType')))
        feature.setAoName(str(results.mFeature.attribute('objectName')))
        feature.setAoPositionType(str(results.mFeature.attribute('addressPositionType')))
        feature.set_x(results.mFeature.geometry().asPoint()[0]) 
        feature.set_y(results.mFeature.geometry().asPoint()[1])
        feature.setExternalObjectId(str(results.mFeature.attribute('externalObjectId')))
        feature.setExternalObjectIdScheme(str(results.mFeature.attribute('externalObjectIdScheme')))
        feature.setValuationReference(str(results.mFeature.attribute('valuationReference')))
        feature.setCertificateOfTitle(str(results.mFeature.attribute('certificateOfTitle')))
        feature.setAppellation(str(results.mFeature.attribute('appellation')))  
        return feature
    
    @staticmethod
    def formToaddObj(obj): 
        obj.feature.setAddressType(str(obj.uAddressType.currentText()))
        obj.feature.setExternalAddressId(UiUtility.nullEqualsNone(str(obj.uExternalAddId.text())))
        obj.feature.setExternalAddressIdScheme(UiUtility.nullEqualsNone(str(obj.uExternalAddressIdScheme.text())))
        obj.feature.setLifecycle(str(obj.ulifeCycle.currentText()))
        obj.feature.setUnitType(UiUtility.nullEqualsNone(str(obj.uUnitType.currentText())))
        obj.feature.setUnitValue(UiUtility.nullEqualsNone(str(obj.uUnit.text()).upper()))
        obj.feature.setLevelType(UiUtility.nullEqualsNone(str(obj.uLevelType.currentText())))
        obj.feature.setLevelValue(UiUtility.nullEqualsNone(str(obj.uLevelValue.text())))
        obj.feature.setAddressNumberPrefix(UiUtility.nullEqualsNone(str(obj.uPrefix.text()).upper()))         
        obj.feature.setAddressNumberSuffix(UiUtility.nullEqualsNone(str(obj.uAlpha.text()).upper()))     
        # Below must be int, else set to None ### Validation has made special handling of int redundant
        obj.feature.setAddressNumber(int(obj.uBase.text())) if obj.uBase.text().isnumeric() else obj.feature.setAddressNumber(None)
        obj.feature.setAddressNumberHigh(int(obj.uHigh.text())) if obj.uHigh.text().isnumeric() else obj.feature.setAddressNumberHigh(None)
        obj.feature.setRoadCentrelineId(int(obj.uRoadCentrelineId.text())) if obj.uRoadCentrelineId.text().isnumeric() else obj.feature.setRoadCentrelineId(None)
        # ROADS
        obj.feature.setRoadPrefix(UiUtility.nullEqualsNone(str(obj.uRoadPrefix.text())))
        obj.feature.setRoadName(UiUtility.nullEqualsNone(obj.uRoadName.text().encode('utf-8')))
        obj.feature.setRoadType(UiUtility.nullEqualsNone(str(obj.uRoadTypeName.text())))
        obj.feature.setRoadSuffix(UiUtility.nullEqualsNone(str(obj.uRoadSuffix.text())))
        obj.feature.setWaterRoute(UiUtility.nullEqualsNone(obj.uWaterRouteName.text().encode('utf-8')))
        obj.feature.setWaterName(UiUtility.nullEqualsNone(str(obj.uWaterName.text())))
        obj.feature.setAoType(str(obj.uObjectType.currentText()))
        obj.feature.setAoName(UiUtility.nullEqualsNone(obj.uObjectName.text().encode('utf-8'))) 
        obj.feature.setExternalObjectId(str(obj.uExternalObjectId.text()))
        obj.feature.setExternalObjectIdScheme(str(obj.uExtObjectIdScheme.text()))
        obj.feature.setValuationReference(str(obj.uValuationReference.text())) 
        obj.feature.setCertificateOfTitle(UiUtility.nullEqualsNone(obj.uCertificateOfTitle.text().encode('utf-8')))
        obj.feature.setAppellation(UiUtility.nullEqualsNone(obj.uAppellation.text().encode('utf-8')))
        obj.feature.setSourceReason(obj.uNotes.toPlainText().encode('utf-8'))   
        # positionType??
        
    @staticmethod
    def addObjToForm(obj, feature):      
        ''' used to populate the update form and 2x Queue Views
            obj = form or widget
            feature == the aims feature '''
        obj.uAddressType.setCurrentIndex(QComboBox.findText(obj.uAddressType, obj.feature._addressType))
        obj.uExternalAddId.setText(UiUtility.nullEqualsNone(obj.feature._externalAddressId))
        obj.uExternalAddressIdScheme.setText(UiUtility.nullEqualsNone(obj.feature._externalAddressIdScheme))
        obj.ulifeCycle.setCurrentIndex(QComboBox.findText(obj.ulifeCycle, obj.feature._lifecycle))
        obj.uUnitType.setCurrentIndex(QComboBox.findText(obj.uUnitType, obj.feature._unitType))
        obj.uUnit.setText(UiUtility.nullEqualsNone(obj.feature._unitValue))
        obj.uLevelType.setCurrentIndex(QComboBox.findText(obj.uLevelType, obj.feature._levelType))
        obj.uLevelValue.setText(UiUtility.nullEqualsNone(obj.feature._levelValue))
        obj.uPrefix.setText(UiUtility.nullEqualsNone(obj.feature._addressNumberPrefix))
        obj.uBase.setText(UiUtility.nullEqualsNone(obj.feature._addressNumber))
        obj.uAlpha.setText(UiUtility.nullEqualsNone(obj.feature._addressNumberSuffix))
        obj.uHigh.setText(UiUtility.nullEqualsNone(obj.feature._addressNumberHigh))
        obj.uRoadCentrelineId.setText(UiUtility.nullEqualsNone(obj.feature._roadCentrelineId))
        obj.uRoadPrefix.setText(UiUtility.nullEqualsNone(obj.feature._roadPrefix))
        obj.uRoadName.setText(UiUtility.nullEqualsNone(obj.feature._roadName))
        obj.uRoadTypeName.setText(UiUtility.nullEqualsNone(obj.feature._roadType))
        obj.uRoadSuffix.setText(UiUtility.nullEqualsNone(obj.feature._roadSuffix))
        obj.uWaterRouteName.setText(UiUtility.nullEqualsNone(obj.feature._waterRoute))
        obj.uWaterName.setText(UiUtility.nullEqualsNone(obj.feature._waterName))
        
        # addressable object
        obj.uObjectType.setCurrentIndex(QComboBox.findText(obj.uObjectType, obj.feature._aoType))
        obj.uObjectName.setText(UiUtility.nullEqualsNone(obj.feature._aoName))
        obj.uExternalObjectId.setText(UiUtility.nullEqualsNone(obj.feature._externalObjectId))
        obj.uExtObjectIdScheme.setText(UiUtility.nullEqualsNone(obj.feature._externalObjectIdScheme))
        obj.uValuationReference.setText(UiUtility.nullEqualsNone(obj.feature._valuationReference))
        obj.uCertificateOfTitle.setText(UiUtility.nullEqualsNone(obj.feature._certificateOfTitle))
        obj.uAppellation.setText(UiUtility.nullEqualsNone(obj.feature._appellation))
        from QueueEditorWidget import QueueEditorWidget
        if isinstance(obj, QueueEditorWidget):
            pass
            #warnings
            #chnageType
        
        
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
    
        