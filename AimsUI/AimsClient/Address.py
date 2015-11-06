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

import Config
from Config import ConfigReader

class Address(object):
    ''' UI address class ''' 

    def __init__(self):
        config = ConfigReader()
        self._changeTypeName = None
        self._submitterUserName = None
        self._submittedDate = None
        self._queueStatusName = None #default
        
        # address values
        self._sourceUser = config.configSectionMap('user')['name']
        self._sourceReason = None
        self._addressType = None #could set defaults?
        self._externalAddressId = None
        self._externalAddressIdScheme = None
        self._lifecycle = None
        self._unitType = None
        self._unitValue = None
        self._levelType = None
        self._levelValue = None
        self._addressNumberPrefix = None
        self._addressNumber = None
        self._addressNumberSuffix = None
        self._addressNumberHigh = None
        self._roadCentrelineId = None
        self._roadPrefix = None
        self._roadName = None
        self._roadTypeName = None
        self._roadSuffix = None
        self._waterRouteName = None
        self._waterName = None
        self._suburbLocality = None
        self._townCity = None
       
        # addressable object
        self._aoType = None
        self._aoName = None
        self._aoPositionType = 'Point'
        self._x = None
        self._y = None
        self._crsType = 'name'
        self._crsProperties = 'urn:ogc:def:crs:EPSG::2193' #need to guarantee supplied coords are in 2193
        self._externalObjectId = None
        self._externalObjectIdScheme = None
        self._valuationReference = None
        self._certificateOfTitle = None
        self._appellation = None
    
    #set functions used to manipulate object properties   
    def setSourceReason (self, sourceReason): self._sourceReason = sourceReason
    def setAddressType( self, addressType ): self._addressType = addressType    
    def setExternalAddressId( self, externalAddressId ): self._externalAddressId = externalAddressId 
    def setExternalAddressIdScheme( self, externalAddressIdScheme ): self._externalAddressIdScheme = externalAddressIdScheme 
    def setLifecycle( self, lifecycle ): self._lifecycle = lifecycle 
    def setUnitType( self, unitType ): self._unitType = unitType 
    def setUnitValue( self, unitValue ): self._unitValue = unitValue 
    def setLevelType( self, levelType ): self._levelType = levelType 
    def setLevelValue( self, levelValue ): self._levelValue = levelValue 
    def setAddressNumberPrefix( self, addressNumberPrefix ): self._addressNumberPrefix = addressNumberPrefix 
    def setAddressNumber( self, addressNumber ): self._addressNumber = addressNumber 
    def setAddressNumberSuffix( self, addressNumberSuffix ): self._addressNumberSuffix = addressNumberSuffix 
    def setAddressNumberHigh( self, addressNumberHigh ): self._addressNumberHigh = addressNumberHigh 
    def setRoadCentrelineId( self, roadCentrelineId ): self._roadCentrelineId = roadCentrelineId 
    def setRoadPrefix( self, roadPrefix ): self._roadPrefix = roadPrefix 
    def setRoadName( self, roadName ): self._roadName = roadName 
    def setRoadTypeName( self, roadTypeName ): self._roadTypeName = roadTypeName 
    def setRoadSuffix( self, roadSuffix ): self._roadSuffix = roadSuffix 
    def setWaterRouteName( self, waterRouteName ): self._waterRouteName = waterRouteName 
    def setWaterName( self, waterName ): self._waterName = waterName 
    def setSuburbLocality( self, suburbLocality ): self._suburbLocality = suburbLocality 
    def setTownCity( self, townCity ): self._townCity = townCity 
    def setAoType( self, aoType ): self._aoType = aoType
    def setAoName( self, aoName ): self._aoName = aoName  
    def setAoPositionType( self, aoPositionType ): self._aoPositionType = aoPositionType
    def set_x( self, x ): self._x = x  
    def set_y( self, y ): self._y = y  
    def setCrsType( self, crsType ): self._crsType = crsType  
    def setCrsProperties( self, crsProperties ): self._crsProperties = crsProperties
    def setExternalObjectId( self, externalObjectId ): self._externalObjectId = externalObjectId  
    def setExternalObjectIdScheme( self, externalObjectIdScheme ): self._externalObjectIdScheme = externalObjectIdScheme  
    def setValuationReference( self, valuationReference ): self._valuationReference = valuationReference  
    def setCertificateOfTitle( self, certificateOfTitle ): self._certificateOfTitle = certificateOfTitle  
    def setAppellation( self, appellation ): self._appellation = appellation    
         
    def delNone (self,d):
        ''' Removes key / value pairs from object whereby value is == to None '''
        for key, value in d.items():
            if value is None:
                del d[key]
        return d
        
    @staticmethod
    def _delNone(d): return {k:v for k,v in d.items() if v}

    def objectify(self):
        ''' Python address class to json object '''

        return self._delNone({
        'workflow':{
            'sourceUser':self._sourceUser,
            'sourceReason':self._sourceReason
        },
        'components':{
            'addressType':self._addressType,
            'externalAddressId':self._externalAddressId,
            'externalAddressIdScheme':self._externalAddressIdScheme,
            'lifecycle':self._lifecycle,
            'unitType':self._unitType,
            'unitValue':self._unitValue,
            'levelType':self._levelType,
            'levelValue':self._levelValue,
            'addressNumberPrefix':self._addressNumberPrefix,
            'addressNumber':self._addressNumber,
            'addressNumberSuffix':self._addressNumberSuffix,
            'addressNumberHigh':self._addressNumberHigh,
            'roadCentrelineId':self._roadCentrelineId,
            'roadPrefix':self._roadPrefix,
            'roadName':self._roadName,
            'roadTypeName':self._roadTypeName,
            'roadSuffix':self._roadSuffix,
            'waterRouteName':self._waterRouteName,
            'waterName':self._waterName,
            'suburbLocality':self._suburbLocality,
            'townCity':self._townCity
        },
        'addressedObject':{
            'objectType':self._aoType,
            'objectName':self._aoName,
            'addressPosition':{
                'type':self._aoPositionType,
                'coordinates':[
                   self._x,
                   self._y
                ],
                'crs':{
                    'type':self._crsType,
                    'properties':{
                        'name':self._crsProperties
                    }
                }
            },
            'externalObjectId':self._externalObjectId,
            'externalObjectIdScheme':self._externalObjectIdScheme,
            'valuationReference':self._valuationReference,
            'certificateOfTitle':self._certificateOfTitle,
            'appellation':self._appellation
        }
    })
