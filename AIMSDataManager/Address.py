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
from gtk._gtk import PositionType


DEF_SEP = '_'

#------------------------------------------------------------------------------
#W A R N I N G

class Warning(object):

    BRANCH = ('properties')
    
    def __init__(self):

        self._ruleId = None,
        self._description = None
        self._severity = None    
        
    @staticmethod
    def getInstance(d):
        w = Warning()
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
    
    BRANCH = ('addressedObject','addressPositions')#'{}addressedObject{}addressPositions'.format(*2*(DEF_SEP,))
    PDEF = {'position':{'type':'Point','coordinates':[0.0,0.0],'crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::4167'}}},'positionType':'Unknown','primary':True}
    
    def __init__(self, ref=None): 
        self._position_type = 'Point'
        self._position_coordinates = [0.0,0.0]
        self._position_crs_type = 'name'
        self._position_crs_properties_name = 'urn:ogc:def:crs:EPSG::4167'
        self._positionType = 'Unknown'
        self._primary = True
    
    def __str__(self):
        return 'POS'    

    @staticmethod
    def getInstance(d):
        p = Position()
        p.set(d)
        return p
        
    def set(self,d = PDEF):
        self._set(
            d['position']['type'],
            d['position']['coordinates'],
            d['position']['crs']['type'],
            d['position']['crs']['properties']['name'],
            d['positionType'],
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
    
    def __init__(self, ref=None): 
        #aimslog.info('AdrRef.{}'.format(ref))
        self._ref = ref
    
    def __str__(self):
        #return 'ADR.{}.{}.{}.{}'.format(self._ref,self.type,self.getAddressId(),self._version)
        return 'ADR.{}.{}'.format(self._ref,self.type)
    
        
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
    def setAddressPosition(self,p):
        '''adds (nb 'add' not 'set', bcse setter recogniser needs set) another position object'''
        if isinstance(p,Position): self._addressedObject_addressPositions = [p,]  
        else: raise InvalidPositionException('Cannot set non Position type {}'.format(p))
        
    def addAddressPositions(self,p, flush=False):
        '''adds (nb 'add' not 'set', bcse setter recogniser needs set) another position object'''
        if flush or not hasattr(self,'_addressedObject_addressPositions'): self._addressedObject_addressPositions = []
        if isinstance(p,Position):
            self._addressedObject_addressPositions.append(p)
        elif isinstance(p,dict):
            self._addressedObject_addressPositions.append(Position.getInstance(p))   
        elif isinstance(p,(tuple,list)): 
            for pos in p: self.setAddressPositions(pos)
        else: raise InvalidPositionException('Cannot parse/add Position {}'.format(p))
            
        
    def getAddressPositions(self):
        '''return a list of dict'd position objects'''
        return [p.get() for p in self._addressedObject_addressPositions]
    #---------------------------------------------------
    
#     def _delNull(self, o):
#         if hasattr(o, 'items'):
#             oo = type(o)()
#             for k in o:
#                 if k != 'NULL' and o[k] != 'NULL' and o[k] != None:
#                     oo[k] = self._delNull(o[k])
#         elif hasattr(o, '__iter__'):
#             oo = [ ] 
#             for it in o:
#                 if it != 'NULL' and it != None:
#                     oo.append(self._delNull(it))
#         else: return o
#         return type(o)(oo)

    
    def compare(self,other):
        '''Equality comparator'''
        #return False if isinstance(self,other) else hash(self)==hash(other)
        #IMPORTANT. Attribute value compare, relies on deep copy
        return all((getattr(self,a)==getattr(other,a) for a in self.__dict__.keys()))
        
#------------------------------------------------------------------------------

class AddressChange(Address):
    ''' UI address change class ''' 
    type = FeedType.CHANGEFEED
    #DA = DEF_ADDR[type]
    
    def __init__(self, ref=None): 
        super(AddressChange,self).__init__(ref)
        
    def filter(self):
        pass
        
#------------------------------------------------------------------------------
        
class AddressResolution(Address):
    ''' UI address res class ''' 
    type = FeedType.RESOLUTIONFEED
    #DA = DEF_ADDR[type]

    def __init__(self, ref=None): 
        super(AddressResolution,self).__init__(ref)   
        self._warnings = None
        
    def setWarnings(self,warnings):
        self._warnings = warnings
        
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

#------------------------------------------------------------------------------
            
if __name__ == '__main__':
    test()      

