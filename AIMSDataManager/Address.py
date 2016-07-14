
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
'''Address module containing data classes representing basic address object as returned from the AIMS API feature.change and resolution feeds'''

#http://devassgeo01:8080/aims/api/address/features - properties
from AimsUtility import FeatureType,ActionType,ApprovalType,FeedType,FeedRef
from AimsUtility import AimsException
from AimsLogging import Logger
from Feature import Feature,FeatureMetaData
from collections import OrderedDict


#aimslog = None
#global aimslog
aimslog = Logger.setup()


class AddressException(AimsException): pass
      
#------------------------------------------------------------------------------
# P O S I T I O N

class InvalidPositionException(AddressException):pass
PDEF = {'position':{'type':'Point','coordinates':[0.0,0.0],'crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::4167'}}},'positionType':'Unknown','primary':True}
    
class Position(object):
    '''Position type for embedded address positions.
    - I{Uses hardcoded attrs since it has a constant structure}.
    '''
    #branch in address structure where we should find position object
    BRANCH = ('addressedObject','addressPositions')
  
    def __init__(self, ref=None):
        '''Initialise Position object
        @param ref: Unique reference string
        '''
        self._ref = ref        
        self._position_type = 'Point'
        self._position_coordinates = [0.0,0.0]
        self._position_crs_type = 'name'
        self._position_crs_properties_name = 'urn:ogc:def:crs:EPSG::4167'
        self._positionType = 'Unknown'
        self._primary = True
    
    def __str__(self):
        return 'POS.{}'.format(self._position_type)    

    @staticmethod
    def getInstance(d = PDEF,af=None):
        '''Gets instance of Position object taking optional position dict and args
        @param d: Dict containing Position object attributes
        @param af: AddressFactory instance used to filter processing instructions if included in position dict
        @type af: AddressFactory
        @return: Populated Position object 
        '''
        p = Position()
        p.set(d,af)
        return p
        
    def set(self,d = PDEF,af=None):
        '''Set for Position object taking optional position dict and  args
        @param d: Dict containing Position object attributes
        @param af: AddressFactory instance used to filter processing instructions if included in position dict
        @type af: AddressFactory
        @return: Populated Position object 
        '''
        self._set(
            d['position']['type'],
            d['position']['coordinates'],
            d['position']['crs']['type'],
            d['position']['crs']['properties']['name'],
            af.filterPI(d['positionType']) if af else d['positionType'],
            d['primary']
        )
        
    def _set(self,ptype,coordinates,ctype,cprops=None,positionType=None,primary=None):
        '''Position setter for full object parameters spread
        @param ptype: Position type, eg Point
        @type ptype: String
        @param coordinates: Coordinate pair, list of doubles
        @type coordinates: List<Double>
        @param ctype: CRS type
        @type ctype: String
        @param cprops: CRS properties name, something like urn:ogc:def:crs:EPSG::4167
        @type cprops: String
        @param positionType: Another position type, eg Centroid
        @type positionType: String
        @param primary: Flag indicating primary position
        @type primary: Boolean
        '''
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
        '''Returns dict of self, Position object
        @return: Dictionary
        '''
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
# S U P P L E M E N T A L
SDEF = {'class':[], 'rel':[],'properties':{'ruleId':None, 'description':None,'severity':None}}
class Supplemental(object):
    '''Additional class storing code data from extra data feature requests'''
    def __init__(self, ref=None):
        '''Initialise Supplemental object
        @param ref: Unique reference string
        '''
        #aimslog.info('AdrRef.{}'.format(ref))
        self._ref = ref        
        self._class = []
        self._rel = []
        self._properties_ruleId = None
        self._properties_description = None
        self._properties_severity = None
    
    def __str__(self):
        return 'SUP.{}.{}'.format(self._ref,self._class)
    
    @staticmethod
    def getInstance(d = SDEF):
        '''Gets instance of Supplemental object taking optional supplemental dict
        @param d: Dict containing Supplemental object attributes
        @return: Populated Supplemental object 
        '''
        s = Supplemental()
        #WORKAROUND
        if d<>SDEF and d['class'][0]=='validation': s.set(d)
        else: aimslog.debug('Supplemental something {}'.format(d['class'][0]))
        return s
        
    def set(self,d = SDEF):
        '''Set for Supplemental object taking optional supplemental dict
        @param d: Dict containing Supplemental object attributes
        @return: Populated Supplemental object 
        '''
        #try: print d['properties']['ruleId']
        #except: pass
        self._set(
            d['class'],
            d['rel'],
            d['properties']['ruleId'],
            d['properties']['description'],
            d['properties']['severity']
        )
        
    def _set(self,_class,rel,ruleId,description,severity):
        '''Supplemental setter for full object parameters spread
        @param _class: Supplemental class, eg Upper, Middle, Working, Lower, Bacteria, Dirt, NationalPartyVoter
        @param rel: The rel
        @type rel: String
        @param ruleId: The ruleId
        @type ruleId: String
        @param description: Description of the supplemental
        @type description: String
        @param severity: How severe it is, eg WetBusTicketSlap, DoingTheDishesForAWeek, Fine, Prison, FiringSquad
        @type severity: String
        '''
        self.setClass(_class)
        self.setRel(rel)
        self.setRuleId(ruleId)
        self.setDescription(description)
        self.setSeverity(severity)        
        
    def setClass(self, _class): self._class = _class
    def setRel(self,rel): self._rel = rel
    def setRuleId(self,ruleId): self._ruleId = ruleId
    def setDescription(self,description):self._description = description
    def setSeverity(self,severity): self._severity = severity
    
    def get(self):
        '''Returns dict of self, Supplemental object
        @return: Dictionary
        '''
        return {'class':self._class,
                'rel':self._rel,
                'properties':{
                    'ruleId':self._ruleId,
                    'description':self._description,
                    'severity':self._severity
                              }
            }
    
#------------------------------------------------------------------------------
# E N T I T Y 

EDEF = {'class':[], 'rel':[],'properties':{'ruleId':None, 'description':None,'severity':None}}
class Entity(object):
    '''Entity data class representing address embedded entity objects and subclassed for specific entity types'''
    #TODO Fix naming confusion between address held entities and Address/Group super feature
    def __init__(self, ref=None):
        '''Initialise Entity object
        @param ref: Unique reference string
        '''
        #aimslog.info('AdrRef.{}'.format(ref))
        self._ref = ref        
        self._class = []
        self._rel = []
        self._properties_ruleId = None
        self._properties_description = None
        self._properties_severity = None
    
    def __str__(self):
        return 'ETY.{}.{}'.format(self._ref,self._class)
    
    @staticmethod
    def getInstance(d = EDEF):
        '''Gets instance of Entity object taking optional entity dict
        @param d: Dict containing Entity object attributes
        @return: Populated Entity object 
        '''
        e = Entity()
        #WORKAROUND
        if d<>EDEF and d['class'][0]=='validation': e.set(d)
        else: aimslog.debug('Entites non-validation type {}'.format(d['class'][0]))
        return e
        
    def set(self,d = EDEF):
        '''Set for Entity object taking optional entity dict
        @param d: Dict containing Entity object attributes
        @return: Populated Entity object 
        '''
        #try: print d['properties']['ruleId']
        #except: pass
        self._set(
            d['class'],
            d['rel'],
            d['properties']['ruleId'],
            d['properties']['description'],
            d['properties']['severity']
        )
        
    def _set(self,_class,rel,ruleId,description,severity):
        '''Entity setter for full object parameters spread
        @param _class: Entity class, eg Upper, Middle, Working, Lower, Bacteria, Dirt, NationalPartyVoter
        @param rel: The rel
        @type rel: String
        @param ruleId: The ruleId
        @type ruleId: String
        @param description: Description of the entity
        @type description: String
        @param severity: How severe it is, eg WetBusTicketSlap, DoingTheDishesForAWeek, Fine, Prison, FiringSquad
        @type severity: String
        '''
        self.setClass(_class)
        self.setRel(rel)
        self.setRuleId(ruleId)
        self.setDescription(description)
        self.setSeverity(severity)        
        
    def setClass(self, _class): self._class = _class
    def setRel(self,rel): self._rel = rel
    def setRuleId(self,ruleId): self._ruleId = ruleId
    def setDescription(self,description):self._description = description
    def setSeverity(self,severity): self._severity = severity
    
    def get(self):
        '''Returns dict of self, Entity object
        @return: Dictionary
        '''
        return {'class':self._class,
                'rel':self._rel,
                'properties':{
                    'ruleId':self._ruleId,
                    'description':self._description,
                    'severity':self._severity
                              }
            }
  
class EntityValidation(Entity):
    '''Validation Entity representing object returned from AIMS with error/warning indicators'''
    
    def __init__(self,ref = 'validation'):        
        '''Initialise Validation Entity object
        @param ref: Unique reference string
        '''
        super(EntityValidation,self).__init__(ref)
        
    @staticmethod
    def getInstance(data):#,etft=None): 
        '''Gets instance of Entity object taking optional entity dict
        @param data: Dict containing Validation Entity object attributes
        #@param etft: Validation Entity feedref 
        #@type etft: FeedRef
        @return: Populated Entity object 
        '''
        return super(EntityValidation,EntityValidation).getInstance(data)

class EntityAddress(Entity):
    '''Address Entity representing object returned embedded in AIMS groups'''
    
    def __init__(self,ref = 'address'):
        '''Initialise Address Entity object
        @param ref: Unique reference string
        '''
        super(EntityAddress,self).__init__(ref)
        
    @staticmethod
    def getInstance(data,etft=FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))): 
        '''Gets instance of Entity object defaulting to Addressfeed/Feature
        @param data: Dict containing AF Entity object attributes
        @param etft: Address Entity feedref 
        @type etft: FeedRef
        @return: Populated Entity object 
        '''
        from FeatureFactory import FeatureFactory
        ff = FeatureFactory.getInstance(etft)
        return ff.get(model=data)
        

#------------------------------------------------------------------------------
# A D D R E S S

class Address(Feature):
    '''Base Address class''' 
    
    feature = FeatureType.ADDRESS
    type = FeedType.FEATURES
    
    #global aimslog
    #aimslog = Logger.setup()
    
    def __init__(self, ref=None): 
        '''Initialise Address object
        @param ref: Unique reference string
        '''
        #aimslog.info('AdrRef.{}'.format(ref))
        super(Address,self).__init__(ref)
    
    def __str__(self):
        return 'ADR.{}.{}.{}'.format(self._ref,self.feature,self.type)
    
    
    # Set functions used to manipulate object properties   
    def setPublishDate(self,d): self._publishDate = d if Feature._vDate(d) else None
    
    def setChangeId(self, changeId): 
        self._changeId = changeId
    def getChangeId(self): 
        return self._changeId 
    
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
    def setMeshblock(self, meshblock):
        self._codes_meshblock = meshblock
    def setIsMeshblockOverride(self, isMeshblockOverride):
        self._codes_isMeshblockOverride = isMeshblockOverride              
    # realted to Features feed only
    def setFullAddressNumber (self, fullAddressNumber): 
        self._components_fullAddressNumber = fullAddressNumber
        
    def setFullRoadName (self, fullRoadName): 
        self._components_fullRoadName = fullRoadName
          
    def setFullAddress (self, fullAddress): 
        self._components_fullAddress = fullAddress    
    
    #---------------------------------------------------         
    def setAddressPositions(self,pl):
        '''Setter for Address positions accepting single or list/multiple position objects
        @param pl: Position
        @type
        '''
        '''adds (nb 'add' not 'set', bcse setter recogniser needs set) another position object'''
        if isinstance(pl,list): self._addressedObject_addressPositions = pl  
        elif isinstance(pl,Position): self._addressedObject_addressPositions = [pl,]  
        else: raise InvalidPositionException('Cannot set non list-of-Position type {}'.format(pl))
            
        
    def getConvertedAddressPositions(self):
        '''Returns a list of position objects converted from stored dictionary
        @return: List<Position>
        '''
        return [p.get() for p in self._addressedObject_addressPositions]    
    
    def getAddressPositions(self):
        '''Returns a list of position objects
        @return: List<Position>
        '''
        return self._addressedObject_addressPositions

    #---------------------------------------------------
    
    def getFullNumber(self):
        '''Combines Address components to create a full address label
        @return: String'''
        # in some instance we could go to the API get 'full number' however this 
        # is not included in responses hence the need for this method
        d = OrderedDict(
            [('_components_unitValue','{}/'),('_components_addressNumber','{}'),
            ('_components_addressNumberHigh','-{}'),('_components_addressNumberSuffix','{}')])
        fullNumber = ''
        for k,v in d.items():
            if self._changeType in ('Update', 'Add') or self.meta.requestId: # request objs are flat
                if hasattr(self, k):
                    numComponent = getattr(self, k)
                    if numComponent: fullNumber += v.format(numComponent) # skip Nones in resp objs
            else:
                if hasattr(getattr(getattr(self,'meta'),'entities')[0],k):                
                    numComponent = getattr(getattr(getattr(self,'meta'),'entities')[0],k)
                    if numComponent: fullNumber += v.format(numComponent) 
        return fullNumber


#------------------------------------------------------------------------------
    
class AddressRequestFeed(Address):
    '''Subclass of address representing address types available from AIMS feed mechanism'''
    
    def __init__(self, ref=None): 
        super(AddressRequestFeed,self).__init__(ref)  
        
#     #TEST. set version demoted from Feature to prevent setting on objects without version information
#     #and those object getting passed to the API action feeds and causing conflict. 
#     def setVersion (self, version): 
#         self._version = version if Feature._vInt(version) else None
#         
#     def getVersion(self): 
#         return self._version

#------------------------------------------------------------------------------

class AddressChange(AddressRequestFeed):
    '''Subclass of address representing address sourced from the AIMS changefeed'''
    
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
    '''Subclass of address representing address sourced from the AIMS resolutionfeed'''
    
    type = FeedType.RESOLUTIONFEED
    #DA = DEF_ADDR[type]

    def __init__(self, ref=None): 
        super(AddressResolution,self).__init__(ref)   
        #self._warnings = None
        
    def __str__(self):
        return 'ADRR.{}.{}/{}'.format(self._ref,self.type,len(self._getEntities()))
               
#------------------------------------------------------------------------------   

   
def test():
    import pprint
    from FeatureFactory import FeatureFactory
    af1 = FeatureFactory.getInstance(FeatureType.ADDRESS,FeedType.FEATURES)
    a1 = af1.get(ref='one_feat')
    
    af2 = FeatureFactory.getInstance(FeatureType.ADDRESS,FeedType.CHANGEFEED)
    a2 = af2.get(ref='two_chg')
    a2.setVersion(100)
    a2.setObjectType('Parcel')
    a2.setAddressNumber(100)
    a2.setAddressId(100)
    a2.setRoadName('Smith Street')
    
    af3 = FeatureFactory.getInstance(FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)
    a3 = af3.get(ref='three_res')
    a3.setChangeId(200)
    a3.setVersion(200)
    a3.setAddressNumber(200)
    a3.setRoadName('Jones Road')
    
    
    print a1,a2,a3

    r2 = af2.convert(a2,ActionType.UPDATE)
    r3 = af3.convert(a3,ApprovalType.UPDATE)

    pprint.pprint (r2)
    pprint.pprint (r3)

#------------------------------------------------------------------------------
            
if __name__ == '__main__':
    test() 