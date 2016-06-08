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
from qgis.gui import QgsVertexMarker
from PyQt4.QtGui import QColor, QIntValidator, QRegExpValidator
from PyQt4.QtCore import QRegExp
import re



class UiUtility (object):
    ''' Utility Class. Methods up for adoption
    Plans to find these a better home '''
    
    
    # ---
    # - Scope for several classes here
    # ---

    
    @staticmethod
    def transform (iface, coords, tgt=2193):       
        src_crs = iface.mapCanvas().mapSettings().destinationCrs()
        tgt_crs = QgsCoordinateReferenceSystem()
        tgt_crs.createFromOgcWmsCrs('EPSG:{}'.format(tgt))
        transform = QgsCoordinateTransform( src_crs, tgt_crs )
        return transform.transform( coords.x(), coords.y() ) 
            
    @staticmethod
    def highlight (iface, coords):
    #function may bve mopved later to a 'highlight' module
        adrMarker = QgsVertexMarker(iface.mapCanvas())
        adrMarker.setIconSize(15)
        adrMarker.setPenWidth(2)
        adrMarker.setIconType(QgsVertexMarker.ICON_BOX)
        adrMarker.setCenter( coords )
        adrMarker.show()
        return adrMarker
    
    @staticmethod
    def setFormCombos(obj):
        #this need to be moved to a config file
        obj.uAddressType.addItems(['Road', 'Water'])
        obj.ulifeCycle.addItems(['Current', 'Proposed', 'Retired'])
        obj.uUnitType.addItems([None, 'Apartment', 'Villa', 'Shop', 'Banana'])#require feed back as to approved values
        obj.uLevelType.addItems([None, 'Ground', 'Floor', 'Basement', 'Sub-basement', 'Sub-sub-basement', 'Mezzanine'])
        obj.uObjectType.addItems(['Parcel', 'Building'])

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
        feature.setRoadTypeName(str(results.mFeature.attribute('roadTypeName')))
        feature.setRoadCentrelineId(str(results.mFeature.attribute('roadCentrelineId')))
        feature.setWaterRouteName(str(results.mFeature.attribute('waterRouteName')))
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
        obj.feature.setRoadTypeName(UiUtility.nullEqualsNone(str(obj.uRoadTypeName.text())))
        obj.feature.setRoadSuffix(UiUtility.nullEqualsNone(str(obj.uRoadSuffix.text())))
        obj.feature.setWaterRouteName(UiUtility.nullEqualsNone(obj.uWaterRouteName.text().encode('utf-8')))
        obj.feature.setWaterName(UiUtility.nullEqualsNone(str(obj.uWaterName.text())))
        obj.feature.setAoType(str(obj.uObjectType.currentText()))
        obj.feature.setAoName(UiUtility.nullEqualsNone(obj.uObjectName.text().encode('utf-8'))) 
        obj.feature.setExternalObjectId(str(obj.uExternalObjectId.text()))
        obj.feature.setExternalObjectIdScheme(str(obj.uExtObjectIdScheme.text()))
        obj.feature.setValuationReference(str(obj.uValuationReference.text())) 
        obj.feature.setCertificateOfTitle(UiUtility.nullEqualsNone(obj.uCertificateOfTitle.text().encode('utf-8')))
        obj.feature.setAppellation(UiUtility.nullEqualsNone(obj.uAppellation.text().encode('utf-8')))
        obj.feature.setSourceReason(obj.uNotes.toPlainText().encode('utf-8'))   

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
            p = re.compile(r'^(?P<flat_prefix>[A-Z]+)?(?:\s)?(?P<flat>[0-9]+/\s*|^[A-Z]{,2}/\s*)?(?P<base>[0-9]+)(?:-)(?P<high>[0-9]+)$') 
            m = p.match(newnumber.upper())
            try:
                if m.group('flat_prefix') is not None: obj.uPrefix.setText(m.group('flat_prefix'))
                if m.group('flat') is not None: obj.uUnit.setText(m.group('flat').strip('/'))
                if m.group('base') is not None: obj.uBase.setText(m.group('base'))
                if m.group('high') is not None: obj.uHigh.setText(m.group('high'))
            except:
                pass #silently  
        