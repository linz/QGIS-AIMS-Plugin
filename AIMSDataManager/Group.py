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
# G R O U P 

class  Group(object):
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=None): 
        #aimslog.info('AdrRef.{}'.format(ref))
        self._ref = ref
    
    def __str__(self):
        #return 'ADR.{}.{}.{}.{}'.format(self._ref,self.type,self.getAddressId(),self._version)
        return 'GRP.{}.{}'.format(self._ref,self.type)
    
    #generic validators
    @staticmethod
    def _vString(sval): return isinstance(sval,str) #alpha only filter?
    @staticmethod
    def _vInt(ival): return isinstance(ival, int) #range filter?
    @staticmethod
    def _vDate(date): return Group._vString(date) and bool(re.match('^\d{4}-\d{2}-\d{2}$',date)) 
    
    
    def setVersion (self, version): 
        self._version = version
    def getVersion(self): 
        return self._version
    
    def setChangeGroupId (self, changeGroupId): 
        self._changeGroupId = changeGroupId
    def getChangeGroupId(self): 
        return self._changeGroupId
    def setAddressId (self, addressId): 
        self._components_addressId = addressId
    def getAddressId(self): 
        return self._components_addressId   
          
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
    
    
    
    
    
    