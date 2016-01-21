#!/usr/bin/python
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

class Address(object):
    ''' UI address class ''' 

    def __init__(self, user):
        self._changeType = None
        self._submitterUserName = None
        self._submittedDate = None
        self._queueStatus = None
        self._version = None
        self._addressId = None
        
        # address values
        
        # the below is can no longer be considered private - This needs to be updated 
        self._sourceUser = user
        self._sourceReason = None
        self._addressType = None
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
        self._roadType = None
        self._roadSuffix = None
        self._waterRoute = None
        self._waterName = None
        self._suburbLocality = None
        self._townCity = None
        # _fullAddress only an attribute of 'Features'
        self._fullAddress = None
       
        # addressable object
        self._aoType = None
        self._aoName = None
        self._aoPositionType = 'Point'
        self._x = None
        self._y = None
        self._crsType = 'name'
        self._crsProperties = 'urn:ogc:def:crs:EPSG::4167' # New Address coords guaranteed to be supplied in 4167
        self._externalObjectId = None
        self._externalObjectIdScheme = None
        self._valuationReference = None
        self._certificateOfTitle = None
        self._appellation = None
    
    # Set functions used to manipulate object properties   
    def setVersion (self, version): self._version = version
    def setAddressId (self, addressId): self._addressId = addressId
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
    def setRoadType( self, roadType ): self._roadType = roadType 
    def setRoadSuffix( self, roadSuffix ): self._roadSuffix = roadSuffix 
    def setWaterRoute( self, waterRoute ): self._waterRoute = waterRoute 
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
    # realted to Features feed only
    def setFullAddress (self, fullAddress): self._fullAddress = fullAddress  
    
    def loadQueueItem( self, queueEntity ):
        r = loadResolutionItem( self.href )
        
        #Properties
        self.version = str(r.get('properties').get('version'))
        self.id = r.get('properties').get('changeId')
        self.changeTypeName = r.get('properties').get('changeTypeName')
        self.submitterUserName = r.get('properties').get('workflow').get('submitterUserName')
        self.submittedDate = r.get('properties').get('workflow').get('submittedDate')
        self.queueStatusName = r.get('properties').get('workflow').get('queueStatusName')
        self.sourceReason = r.get('properties').get('workflow').get('sourceReason')
        
        #Address Attributes
        self.addressId = r.get('properties').get('components').get('addressId')
        self.addressType = r.get('properties').get('components').get('addressType')     
        self.lifecycle = r.get('properties').get('components').get('lifecycle')   
        self.unitType = r.get('properties').get('components').get('unitType')                                          
        self.unitValue = r.get('properties').get('components').get('unitValue')
        self.levelType = r.get('properties').get('components').get('levelType')                                                 
        self.levelValue = r.get('properties').get('components').get('levelValue')
        self.addressNumberPrefix = r.get('properties').get('components').get('addressNumberPrefix')  
        self.addressNumber = r.get('properties').get('components').get('addressNumber')     
        self.addressNumberSuffix = r.get('properties').get('components').get('addressNumberSuffix')   
        self.addressNumberHigh = r.get('properties').get('components').get('addressNumberHigh')
        self.roadCentrelineId = r.get('properties').get('components').get('roadCentrelineId')
        self.roadPrefix = r.get('properties').get('components').get('roadPrefix')       
        self.roadName = r.get('properties').get('components').get('roadName')
        self.roadTypeName = r.get('properties').get('components').get('roadTypeName')
        self.roadSuffix = r.get('properties').get('components').get('roadSuffix')
        self.suburbLocality = r.get('properties').get('components').get('suburbLocality')    
        self.townCity = r.get('properties').get('components').get('townCity')
  
        #AddressableObject Attributes
        self.objectType = r.get('properties').get('addressedObject').get('objectType') #chainning used as this will return None if Key does not exists
        try:
            self.addressPositionType = r.get('properties').get('addressedObject').get('addressPosition').get('type')
        except: self.addressPositionType = 'NONE'
        try:
            self.addressPositionCoords = r.get('properties').get('addressedObject').get('addressPosition').get('coordinates')
        except: self.addressPositionCoords ='NONE'
        
        #Warnings / Info
        info = []
        warnings = []     
 
        for i in r.get('entities'):   
            if i.get('properties').get('severity') == 'Info':
                info.append(i.get('properties').get('description'))
            elif i.get('properties').get('severity') == 'Warning':
                warnings.append(i.get('properties').get('description')) 
        self.info = '\n'.join( info )+'\n'
        self.warnings = '\n'.join( warnings ) 

    def _delNull(self, o):
        if hasattr(o, 'items'):
            oo = type(o)()
            for k in o:
                if k != 'NULL' and o[k] != 'NULL' and o[k] != None:
                    oo[k] = self._delNull(o[k])
        elif hasattr(o, '__iter__'):
            oo = [ ] 
            for it in o:
                if it != 'NULL' and it != None:
                    oo.append(self._delNull(it))
        else: return o
        return type(o)(oo)


    def aimsObject(self):
        ''' Python address class to json object '''

        return self._delNull({
        'version':self._version,                      
        'workflow':{
            'sourceUser':self._sourceUser,
            'sourceReason':self._sourceReason
        },
        'components':{
            'addressId':self._addressId,
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
            'roadType':self._roadType,
            'roadSuffix':self._roadSuffix,
            'waterRoute':self._waterRoute,
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
