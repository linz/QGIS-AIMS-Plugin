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
from AimsUtility import ActionType,ApprovalType,FeedType
from AimsLogging import Logger
from Feature import Feature 


#aimslog = None

        
#------------------------------------------------------------------------------
# G R O U P 

class  Group(Feature):
    
    #global aimslog
    #aimslog = Logger.setup()
    
    def __init__(self, ref=None): 
        #aimslog.info('AdrRef.{}'.format(ref))
        super(Group,self).__init__(ref)
    
    def __str__(self):
        return 'GRP.{}.{}'.format(self._ref,self.type)
    
    
    def setVersion (self, version): 
        self._version = version
    def getVersion(self): 
        return self._version
    
    def setChangeGroupId (self, changeGroupId): 
        self._changeGroupId = changeGroupId
    def getChangeGroupId(self): 
        return self._changeGroupId

          
    def setSourceReason (self, sourceReason): 
        self._workflow_sourceReason = sourceReason       
    def getSourceReason (self): 
        return self._workflow_sourceReason 
        
    def setSourceUser (self, sourceUser): 
        self._workflow_sourceUser = sourceUser    
    def getSourceUser (self): 
        return self._workflow_sourceUser
    
    
    def compare(self,other):
        '''Equality comparator'''
        #return False if isinstance(self,other) else hash(self)==hash(other)
        #IMPORTANT. Attribute value compare only useful with distinct (deepcopy'd) instances
        return all((getattr(self,a)==getattr(other,a) for a in self.__dict__.keys()))
    
    
    @staticmethod
    def clone(a,b=None):
        '''clones attributes of A to B and instantiates B (as type A) if not provided'''
        #duplicates only attributes set in source object
        from GroupFactory import GroupFactory
        if not b: b = GroupFactory.getInstance(a.type).getAddress()
        for attr in a.__dict__.keys(): setattr(b,attr,getattr(a,attr))
        return b
    

class GroupRequestFeed(Group):          
    def setVersion (self, version): self._version = version if Feature._vInt(version) else None
    
#     def setMeta(self, meta = None):
#         if not hasattr(self,'meta'): self.meta = meta if meta else FeatureMetaData()
#         
#     def getMeta(self): 
#         return self.meta if hasattr(self, 'meta') else None    
#     
#     def setRequestId(self,requestId):
#         self.setMeta()
#         self.meta.requestId = requestId      
#           
#     def getRequestId(self):
#         return self.meta.requestId if hasattr(self,'meta') else None
#     
#     def setErrors(self,errors):
#         self.setMeta()
#         self.meta.errors = errors      
#           
#     def getErrors(self):
#         return self.meta.errors if hasattr(self,'meta') else None
    
      
class GroupChange(GroupRequestFeed):
    ''' UI address change class ''' 
    type = FeedType.CHANGEFEED
    #DA = DEF_ADDR[type]
    
    def __init__(self, ref=None): 
        super(GroupChange,self).__init__(ref)    
        
    def __str__(self):
        return 'GRPC.{}.{}'.format(self._ref,self.type)
    
    def filter(self):
        pass
    
class GroupResolution(GroupRequestFeed):
    ''' UI address change class ''' 
    type = FeedType.RESOLUTIONFEED
    #DA = DEF_ADDR[type]
    
    def __init__(self, ref=None): 
        super(GroupResolution,self).__init__(ref)    
        
    def __str__(self):
        return 'GRPR.{}.{}'.format(self._ref,self.type)
    
    def filter(self):
        pass
    
    
    