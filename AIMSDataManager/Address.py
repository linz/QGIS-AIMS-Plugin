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

#http://devassgeo01:8080/aims/api/address/features - properties
import re
from AimsUtility import ActionType,FeedType


DEF_SEP = '_'


DEF_ADDR = {
          FeedType.FEATURES:{
                "publishDate":'1970-01-01',
                "version":0,
                "components":{
                    "addressId":0,
                    "addressType":None,
                    "lifecycle":None,
                    "addressNumber":0,
                    "roadCentrelineId":0,
                    "roadName":None,
                    "roadType":None,
                    "suburbLocality":None,
                    "fullAddressNumber":0,
                    "fullRoadName":None,
                    "fullAddress":None
                },
                "addressedObject":{
                    "addressableObjectId":0,
                    "objectType":None,
                    "addressPosition":{
                        "type":None,
                        "coordinates":[0.0,0.0],
                        "crs":{
                            "type":None,
                            "properties":{
                                "name":"urn:ogc:def:crs:EPSG::4167"
                            }
                        }
                    },
                    "addressPositionType":None
                },
                "codes":{
                    "suburbLocalityId":0,
                    "parcelId":0,
                    "meshblock":None
                }
            },
          FeedType.CHANGEFEED:{
                "changeId":0,
                "changeType":None,
                "workflow":{
                    "submitterUserName":None,
                    "submittedDate":'1970-01-01',
                    "queueStatus":None,
                    "sourceOrganisation":None
                },
                "components":{
                    "addressId":0,
                    "addressType":None,
                    "lifecycle":None,
                    "addressNumber":0,
                    "roadCentrelineId":0,
                    "roadName":None,
                    "suburbLocality":None,
                    "townCity":None
                },
                "addressedObject":{
                    "objectType":"Parcel",
                    "addressPosition":{
                        "type":"Point",
                        "coordinates":[0.0,0.0],
                        "crs":{
                            "type":None,
                            "properties":{
                                "name":"urn:ogc:def:crs:EPSG::4167"
                            }
                        }
                    },
                    "externalObjectId":None
                }
             },
          FeedType.RESOLUTIONFEED:{
                "version":0,
                "changeId":0,
                "changeType":None,
                "workflow":{
                    "submitterUserName":None,
                    "submittedDate":'1970-01-01',
                    "queueStatus":None,
                    "sourceOrganisation":"e-Spatial"
                },
                "components":{
                    "addressId":0,
                    "addressType":None,
                    "lifecycle":None,
                    "addressNumber":0,
                    "roadCentrelineId":0,
                    "roadName":None,
                    "suburbLocality":None,
                    "townCity":None
                },
                "addressedObject":{
                    "objectType":None,
                    "addressPosition":{
                        "type":None,
                        "coordinates":[0.0,0.0],
                        "crs":{
                            "type":None,
                            "properties":{
                                "name":"urn:ogc:def:crs:EPSG::4167"
                            }
                        }
                    },
                    "externalObjectId":None
                }
            }
        }

    
class Address(object):
    ''' UI address class ''' 
    
    type = FeedType.FEATURES
    DA = DEF_ADDR[type]
    
    def __init__(self, ref=None): 
        #aimslog.info('AdrRef.{}'.format(ref))
        pass
    
    def __str__(self):
        return 'ADR.{}.{}.{}'.format(self.type,self._addressId,self._version)
        
    @classmethod
    def _import(cls,obj,model=None,prefix=''):
        '''Flatten properties dict into an (Address) object
        param obj : Address object to be pop'd
        param data: dict of data matching address obj
        '''
        data = model if model else cls.DA
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            if isinstance(data[k],dict): obj = cls._import(obj,data[k],prefix+DEF_SEP+k)
            else: getattr(obj,setter)(data[k] or None) if hasattr(obj,setter) else setattr(obj,prefix+DEF_SEP+k,data[k] or None)
        return obj
    
    @classmethod  
    def _export(cls,obj,model=None):
        data = model if model else cls.DA
        '''Match object attributes to a predefined (Address) dict'''
        for attr in [a for a in obj.__dict__.keys()]:#dir(obj) if not a.startswith('__')]:
            atlist = attr.split(DEF_SEP)[1:]
            reduce(dict.__getitem__, atlist[:-1], data)[atlist[-1:][0]] = getattr(obj,attr)
        return data
                
        
    #type filters, better queried off server but hardcoded for now
    RT = ('Road','Street','Avenue','Drive')
    
    #generic validators
    @staticmethod
    def _vString(sval): return isinstance(sval,str) #alpha only filter?
    @staticmethod
    def _vInt(ival): return isinstance(ival, int) #range filter?
    @staticmethod
    def _vDate(date): return Address._vString(date) and bool(re.match('^\d{4}-\d{2}-\d{2}$',date)) 
    
    # Set functions used to manipulate object properties   
    def setPublishDate(self,d): self._publishDate = d if Address._vDate(d) else None
    def setVersion (self, version): self._version = version if Address._vInt(version) else None
    
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
        return Address._export(self)
    
    def compare(self,other):
        '''Equality comparator'''
        #return False if isinstance(self,other) else hash(self)==hash(other)
        #IMPORTANT. Attribute value compare, relies on deep copy
        return all((getattr(self,a)==getattr(other,a) for a in self.__dict__.keys()))
        
class AddressChange(Address):
    ''' UI address change class ''' 
    type = FeedType.CHANGEFEED
    DA = DEF_ADDR[type]
    
    def __init__(self, ref=None): 
        super(AddressChange,self).__init__(ref)
        self._changeType = None
        self._submitterUserName = None
        self._submittedDate = None
        self._queueStatus = None
        self._version = None
        self._addressId = None
        
    def filter(self):
        pass
        
        
class AddressResolution(Address):
    ''' UI address res class ''' 
    type = FeedType.RESOLUTIONFEED
    DA = DEF_ADDR[type]

    def __init__(self, ref=None): 
        super(AddressResolution,self).__init__(ref)   
        self._changeType = None
        self._submitterUserName = None
        self._submittedDate = None
        self._queueStatus = None
        self._version = None
        self._addressId = None 
        
def test():
    import pprint
    a1 = Address._import(Address('one'))
    a2 = AddressChange._import(AddressChange('two'))
    a3 = AddressResolution._import(AddressResolution('three'))
    print a1,a2,a3
    r1 = Address._export(a1)
    r2 = AddressChange._export(a2)
    r3 = AddressResolution._export(a3)
    pprint.pprint (r1)
    pprint.pprint (r2)
    pprint.pprint (r3)

            
if __name__ == '__main__':
    test()      