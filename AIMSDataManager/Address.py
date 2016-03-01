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
from AimsUtility import ActionType,ApprovalType,FeedType
from AimsLogging import Logger
from gtk._gtk import PositionType

aimslog = None

#------------------------------------------------------------------------------
# W A R N I N G

class AimsWarning(object):

    BRANCH = ('properties')
    
    def __init__(self):

        self._ruleId = None,
        self._description = None
        self._severity = None    
        
    @staticmethod
    def getInstance(d):
        w = AimsWarning()
        w.set(d)
        return w
    
    def set(self,d):
        self._set(
            d['ruleId'],
            d['description'],
            d['severity']
        )    
        
    def _set(self,ruleId, description,severity):
        '''sets object parameters'''
        self._ruleId = ruleId
        self._description = description
        self._severity = severity     
        
    def get(self):
        return {"ruleId":self._ruleId,
                "description":self._description,
                "severity":self._severity
                }
        
#------------------------------------------------------------------------------
# P O S I T I O N

class InvalidPositionException(Exception):pass
class Position(object):
    '''Position type for embedded address positions.
    Uses hardcoded attrs since it has a constant structure'''
    #branch in address structure where we should find position object
    BRANCH = ('addressedObject','addressPositions')
    PDEF = {'position':{'type':'Point','coordinates':[0.0,0.0],'crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::4167'}}},'positionType':'Unknown','primary':True}
    
    def __init__(self, ref=None): 
        self._position_type = 'Point'
        self._position_coordinates = [0.0,0.0]
        self._position_crs_type = 'name'
        self._position_crs_properties_name = 'urn:ogc:def:crs:EPSG::4167'
        self._positionType = 'Unknown'
        self._primary = True
    
    def __str__(self):
        return 'POS.{}'.format(self._position_type)    

    @staticmethod
    def getInstance(d,af=None):
        p = Position()
        p.set(d,af)
        return p
        
    def set(self,d = PDEF,af=None):

        self._set(
            d['position']['type'],
            d['position']['coordinates'],
            d['position']['crs']['type'],
            d['position']['crs']['properties']['name'],
            af.filterPI(d['positionType']) if af else d['positionType'],
            d['primary']
        )
        
    def _set(self,ptype,coordinates,ctype,cprops=None,positionType=None,primary=None):
        '''sets object parameters'''
        self.setType(ptype)
        self.setCoordinates(coordinates)
        self.setCrsType(ctype)
        self.setCrsPropertiesName(cprops)
        self.setPositionType(positionType)
        self.setPrimary(primary)
        
    def setType(self, _position_type): self._position_type = _position_type
    def setCoordinates(self, _position_coordinates): self._position_coordinates = _position_coordinates
    def setCrsType(self, _position_crs_type): self._position_crs_type = _position_crs_type
    def setCrsPropertiesName(self, _position_crs_properties_name): self._position_crs_properties_name = _position_crs_properties_name
    def setPositionType(self, _positionType): self._positionType = _positionType
    def setPrimary(self, _primary): self._primary = _primary    
        
    def get(self):
        return {"position":{
                    "type":self._position_type,
                    "coordinates":self._position_coordinates,
                    "crs":{
                         "type":self._position_crs_type,
                         "properties":{
                            "name":self._position_crs_properties_name
                         }
                    }
                },
                "positionType":self._positionType,
                "primary":self._primary
                }

#------------------------------------------------------------------------------
# A D D R E S S

class Address(object):
    ''' UI address class ''' 
    
    type = FeedType.FEATURES
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=None): 
        #aimslog.info('AdrRef.{}'.format(ref))
        self._ref = ref
    
    def __str__(self):
        #return 'ADR.{}.{}.{}.{}'.format(self._ref,self.type,self.getAddressId(),self._version)
        return 'ADR.{}.{}'.format(self._ref,self.type)
    
    #generic validators
    @staticmethod
    def _vString(sval): return isinstance(sval,str) #alpha only filter?
    @staticmethod
    def _vInt(ival): return isinstance(ival, int) #range filter?
    @staticmethod
    def _vDate(date): return Address._vString(date) and bool(re.match('^\d{4}-\d{2}-\d{2}$',date)) 
    
    # Set functions used to manipulate object properties   
    def setPublishDate(self,d): self._publishDate = d if Address._vDate(d) else None
    
    def setChangeId(self, changeId): 
        self._changeId = changeId
    def getChangeId(self): 
        return self._changeId
    
    def setChangeType(self, changeType):
        self._changeType = changeType
    def getChangeType(self):
        return self._changeType    
    
    def setQueueStatus(self, queueStatus):
        self._queueStatus = queueStatus
    def getQueueStatus(self):
        return self._queueStatus
    
    def setAddressId (self, addressId): 
        self._components_addressId = addressId
    def getAddressId(self): 
        return self._components_addressId        
    def setSourceReason (self, sourceReason): 
        self._workflow_sourceReason = sourceReason
        
    def setStatusNotes(self, statusNotes):
        self._workflow_statusNotes = statusNotes
    def getStatusNotes(self):
        return self._workflow_statusNotes
    
    def setAddressType( self, addressType ): 
        self._components_addressType = addressType            
    def setExternalAddressId( self, externalAddressId ): 
        self._components_externalAddressId = externalAddressId 
    def setExternalAddressIdScheme( self, externalAddressIdScheme ): 
        self._components_externalAddressIdScheme = externalAddressIdScheme
    def setLifecycle( self, lifecycle ): 
        self._components_lifecycle = lifecycle         
    def setUnitType( self, unitType ): 
        self._components_unitType = unitType 
    def setUnitValue( self, unitValue ): 
        self._components_unitValue = unitValue 
    def setLevelType( self, levelType ): 
        self._components_levelType = levelType 
    def setLevelValue( self, levelValue ): 
        self._components_levelValue = levelValue 
    def setAddressNumberPrefix( self, addressNumberPrefix ): 
        self._components_addressNumberPrefix = addressNumberPrefix 
    def setAddressNumber( self, addressNumber ): 
        self._components_addressNumber = addressNumber          
    def setAddressNumberSuffix( self, addressNumberSuffix ): 
        self._components_addressNumberSuffix = addressNumberSuffix         
    def setAddressNumberHigh( self, addressNumberHigh ): 
        self._components_addressNumberHigh = addressNumberHigh 
    def setRoadCentrelineId( self, roadCentrelineId ): 
        self._components_roadCentrelineId = roadCentrelineId         
    def setRoadPrefix( self, roadPrefix ): 
        self._components_roadPrefix = roadPrefix 
    def setRoadName( self, roadName ): 
        self._components_roadName = roadName         
    def setRoadType( self, roadType ): 
        self._components_roadType = roadType         
    def setRoadSuffix( self, roadSuffix ): 
        self._components_roadSuffix = roadSuffix 
    def setWaterRoute( self, waterRoute ): 
        self._components_waterRoute = waterRoute 
    def setWaterName( self, waterName ): 
        self._components_waterName = waterName 
    def setSuburbLocality( self, suburbLocality ): 
        self._components_suburbLocality = suburbLocality         
    def setTownCity( self, townCity ): 
        self._components_townCity = townCity
         
    def setObjectType( self, objectType ): 
        self._addressedObject_objectType = objectType    
    def setObjectName( self, objectName ): 
        self._addressedObject_objectName = objectName  
    #def setAoPositionType( self, aoPositionType ): self._aoPositionType = aoPositionType
    #def set_x( self, x ): self._x = x  
    #def set_y( self, y ): self._y = y  
    #def setCrsType( self, crsType ): self._crsType = crsType  
    #def setCrsProperties( self, crsProperties ): self._crsProperties = crsProperties
    def setExternalObjectId( self, externalObjectId ): 
        self._addressedObject_externalObjectId = externalObjectId          
    def setExternalObjectIdScheme( self, externalObjectIdScheme ):     
        self._addressedObject_externalObjectIdScheme = externalObjectIdScheme  
    def setValuationReference( self, valuationReference ): 
        self._addressedObject_valuationReference = valuationReference  
    def setCertificateOfTitle( self, certificateOfTitle ): 
        self._addressedObject_certificateOfTitle = certificateOfTitle  
    def setAppellation( self, appellation ): 
        self._addressedObject_appellation = appellation          
    # realted to Features feed only
    def setFullAddressNumber (self, fullAddressNumber): 
        self._components_fullAddressNumber = fullAddressNumber
        
    def setFullRoadName (self, fullRoadName): 
        self._components_fullRoadName = fullRoadName
          
    def setFullAddress (self, fullAddress): 
        self._components_fullAddress = fullAddress    
    
    #---------------------------------------------------         
    def setAddressPositions(self,pl):
        '''adds (nb 'add' not 'set', bcse setter recogniser needs set) another position object'''
        if isinstance(pl,list): self._addressedObject_addressPositions = pl  
        elif isinstance(pl,Position): self._addressedObject_addressPositions = [pl,]  
        else: raise InvalidPositionException('Cannot set non list-of-Position type {}'.format(pl))
            
        
    def getConvertedAddressPositions(self):
        '''return a list of dict'd position objects'''
        return [p.get() for p in self._addressedObject_addressPositions]    
    
    def getAddressPositions(self):
        '''return a list of position objects'''
        return self._addressedObject_addressPositions
    #---------------------------------------------------
    
    
    def compare(self,other):
        '''Equality comparator'''
        #return False if isinstance(self,other) else hash(self)==hash(other)
        #IMPORTANT. Attribute value compare only useful with distinct (deepcopy'd) instances
        return all((getattr(self,a)==getattr(other,a) for a in self.__dict__.keys()))
    
    
    @staticmethod
    def clone(a,b=None):
        '''clones attributes of A to B and instantiates B (as type A) if not provided'''
        #duplicates only attributes set in source object
        if not b: b = AddressFactory.getInstance(a.type).getAddress()
        for attr in a.__dict__.keys(): setattr(b,attr,getattr(a,attr))
        return b
    


#------------------------------------------------------------------------------

class AddressRequestFeed(Address):          
    def setVersion (self, version): self._version = version if Address._vInt(version) else None  

#------------------------------------------------------------------------------

class AddressChange(AddressRequestFeed):
    ''' UI address change class ''' 
    type = FeedType.CHANGEFEED
    #DA = DEF_ADDR[type]
    
    def __init__(self, ref=None): 
        super(AddressChange,self).__init__(ref)    
        
    def __str__(self):
        return 'ADRC.{}.{}'.format(self._ref,self.type)
    
    def filter(self):
        pass
        
#------------------------------------------------------------------------------
        
class AddressResolution(AddressRequestFeed):
    ''' UI address res class ''' 
    type = FeedType.RESOLUTIONFEED
    #DA = DEF_ADDR[type]

    def __init__(self, ref=None): 
        super(AddressResolution,self).__init__(ref)   
        self._warnings = None
        
    def __str__(self):
        return 'ADRR.{}.{}/{}'.format(self._ref,self.type,self._warnings)
        
    def setWarnings(self,warnings):
        self._warnings = warnings

    def getFullNumber(self):
        fullNumber = ''
        if hasattr(self, '_components_unitValue'): fullNumber+=str(self._components_unitValue)+'/'
        if hasattr(self, '_components_addressNumber'): fullNumber+=str(self._components_addressNumber) 
        if hasattr(self, '_components_addressNumberHigh'):  fullNumber+= ('-'+str(self._components_addressNumberHigh))
        if hasattr(self, '_components_addressNumberSuffix'):  fullNumber+=str(self._components_addressNumberSuffix)      
        return fullNumber 
        
def test():
    import pprint
    from AddressFactory import AddressFactory
    af1 = AddressFactory.getInstance(FeedType.FEATURES)
    a1 = af1.getAddress(ref='one_feat')
    
    af2 = AddressFactory.getInstance(FeedType.CHANGEFEED)
    a2 = af2.getAddress(ref='two_chg')
    a2.setVersion(100)
    a2.setObjectType('Parcel')
    a2.setAddressNumber(100)
    a2.setAddressId(100)
    a2.setRoadName('Smith Street')
    
    af3 = AddressFactory.getInstance(FeedType.RESOLUTIONFEED)
    a3 = af3.getAddress(ref='three_res')
    a3.setChangeId(200)
    a3.setVersion(200)
    a3.setAddressNumber(200)
    a3.setRoadName('Jones Road')
    
    
    print a1,a2,a3

    r2 = af2.convertAddress(a2,ActionType.UPDATE)
    r3 = af3.convertAddress(a3,ApprovalType.UPDATE)

    pprint.pprint (r2)
    pprint.pprint (r3)

#------------------------------------------------------------------------------
            
if __name__ == '__main__':
    test()      

