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
import hashlib
import re
from AimsUtility import FeatureType,ActionType,ApprovalType,FeedType
from AimsLogging import Logger


aimslog = None

# ref is time variable, adrpo is nested and covered by changeid, meta contains non object attrs
HASH_EXCLUDES = ('_ref', '_address_positions','meta')

class Feature(object):
    '''Feature data object representing AIMS primary objects Addresses, Groups and Users'''
    
    type = FeedType.FEATURES
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=None): 
        #aimslog.info('AdrRef.{}'.format(ref))
        self._ref = ref
        #self._hash = self._hash()#no point, empty

    
    #generic validators
    @staticmethod
    def _vString(sval): return isinstance(sval,str) #alpha only filter?
    @staticmethod
    def _vInt(ival): return isinstance(ival, int) #range filter?
    @staticmethod
    def _vDate(date): return Feature._vString(date) and bool(re.match('^\d{4}-\d{2}-\d{2}$',date)) 
    @staticmethod
    def _vEmail(email): return Feature._vString(email) and bool(re.match('^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$',email)) 
    

    #COMMON---------------------------------------------
    #version not used on non feed feaures types but its inclusion here won't matter
    def setVersion (self, version): 
        self._version = version if Feature._vInt(version) else None
    def getVersion(self): 
        return self._version
    
    def setSourceUser (self, sourceUser): 
        self._workflow_sourceUser = sourceUser    
    def getSourceUser (self): 
        return self._workflow_sourceUser    
    def setSourceOrganisation (self, sourceOrganisation): 
        self._workflow_sourceOrganisation = sourceOrganisation    
    def getSourceOrganisation (self): 
        return self._workflow_sourceOrganisation
    def setChangeType(self, changeType):
        self._changeType = changeType
    def getChangeType(self):
        return self._changeType
    
    def setQueueStatus(self, queueStatus):
        self._queueStatus = queueStatus
    def getQueueStatus(self):
        return self._queueStatus
    
    #---------------------------------------------------
    
    def _setEntities(self,entities):
        self.setMeta()
        self.meta.entities = entities
 
    def _getEntities(self):
        return self.meta.entities
    
    def setMeta(self, meta = None):
        if not hasattr(self,'meta'): self.meta = meta if meta else FeatureMetaData()
        
    def getMeta(self): 
        return self.meta if hasattr(self, 'meta') else None    
    
#     def compare(self,other):
#         '''Feature equality comparator using simple attribute comparison
#         @param other: Another Feature object whose attributes will be compared to selfs
#         @return: Boolean
#         '''
#         #return False if isinstance(self,other) else hash(self)==hash(other)
#         #IMPORTANT. Attribute value compare only useful with distinct (deepcopy'd) instances
#         return all((getattr(self,a)==getattr(other,a) for a in self.__dict__.keys()))
    
    def merge(self,other):
        '''Merges new (other) atributes into existing (self) object
        @param other: Another Feature object whose attributes will be added to selfs attributes
        @return: Feature
        '''
        for key in other.__dict__.keys():
            setattr(self,key, getattr(other,key))
        return self
    
    
    #---------------------------------
    
    def setRequestId(self,requestId):
        '''Set meta requestid variable on Feature object
        @param requestId: User generated variable attatched to and identifying AIMS individual requests. Integer type restricted at meta setter
        @type requestId: Integer
        '''
        self.setMeta()
        self.meta.requestId = requestId      
           
    def getRequestId(self):
        return self.meta.requestId if hasattr(self,'meta') else None
     
    def setErrors(self,errors): 
        '''Set meta error variable on Feature object
        @param error: Error string typically set from HTTP error message returned at API interface
        @type error: String
        '''
        self.setMeta()
        self.meta.errors = errors
           
    def getErrors(self):
        return self.meta.errors if hasattr(self,'meta') else None

    #object hash of attributes for page comparison
    def getHash(self):
        '''Generates unique hash values for Feature objects. 
        Hashes are calculated by reading all attributes excluding the ref, meta and position attributes. 
        Numeric values are converted to string and unicode values are encoded
        The resulting string attributes are append reduced and their md5 calculated.
        The hexdigest of this hash is returned  
        @return: 32 digit hexdigest representing hash code
        '''
        #discard all list/nested attributes? This should be okay since we capture the version addess|changeId in the top level
        s0 = [getattr(self,z) for z in self.__dict__.keys() if z not in HASH_EXCLUDES]
        s1 = [str(z) for z in s0 if isinstance(z,(int,float,long,complex))]
        s2 = [z.encode('utf8') for z in s0 if isinstance(z,(basestring)) and z not in s1]
        #return reduce(lambda x,y: x.update(y), s1+s2,hashlib.md5()) #reduce wont recognise haslib objs
        self.setMeta()
        self.meta.hash = hashlib.md5(reduce(lambda x,y: x+y, s1+s2)).hexdigest()
        return self.meta.hash
    
    @staticmethod
    def clone(a,b=None):
        '''Clones attributes of A to B and instantiates B (as type A) if not provided
        @param a: Feature object to-be cloned
        @type a: Feature
        @param b: Feature object being overwritten (optional)
        @type b: Feature
        @return: Manual deepcop of Feature object 
        '''
        #duplicates only attributes set in source object
        from FeatureFactory import FeatureFactory
        if not b: b = FeatureFactory.getInstance(a.type).get()
        for attr in a.__dict__.keys(): setattr(b,attr,getattr(a,attr))
        return b

    @staticmethod
    def compare(a,b):
        '''Compares supplied feature with each other using computed hash values
        @param a: One of the features being compared
        @type a: Feature        
        @param b: The other feature being compared
        @type b: Feature
        '''
        #TODO implement an ordering criteria for sorting
        return a.getHash()==b.getHash()
    

class FeatureMetaData(object):
    '''Embedded container for address meta information and derived attributes eg warnings, errors and tracking'''
    def __init__(self):
        '''Initialise metadata container with al null equivalents'''
        self._requestId,self._statusMessage,self._errors,self._entities, self._hash = 0,'',[],[],None
    
    @property
    def requestId(self): return self._requestId
    @requestId.setter
    def requestId(self, requestId): self._requestId = requestId if Feature._vInt(requestId) else None
    
    @property
    def entities(self): return self._entities  
    @entities.setter
    def entities(self,entities): self._entities = entities 
     
    @property
    def errors(self): return self._errors  
    @errors.setter
    def errors(self,errors): self._errors = errors
    
    @property
    def hash(self): return self._hash  
    @hash.setter
    def hash(self,hash): self._hash = hash
    
