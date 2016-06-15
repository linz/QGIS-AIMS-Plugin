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
from AimsUtility import AimsException
from AimsLogging import Logger
from Feature import Feature 


#aimslog = None

        
class GroupException(AimsException): pass 

#------------------------------------------------------------------------------
# G R O U P 

class  Group(Feature):
    '''AIMS defined Group class which acts as a container for Feature objects'''
    
    #global aimslog
    #aimslog = Logger.setup()
    
    def __init__(self, ref=None):
        '''Initialses Group feature class
        @param ref: Unique reference string
        '''
        #aimslog.info('AdrRef.{}'.format(ref))
        super(Group,self).__init__(ref)
    
    def __str__(self):
        return 'GRP.{}.{}'.format(self._ref,self.type)
    
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
    
    def setSubmitterUserName (self, submitterUserName): 
        self._submitterUserName = submitterUserName    
    def getSubmitterUserName (self): 
        return self._submitterUserName

      
class GroupChange(Group):
    '''Group type class for Group objects retrieved from group requests'''
     
    type = FeedType.CHANGEFEED
    #DA = DEF_ADDR[type]
    
    def __init__(self, ref=None): 
        super(GroupChange,self).__init__(ref)    
        
    def __str__(self):
        return 'GRPC.{}.{}'.format(self._ref,self.type)
    
    #def filter(self):
    #    pass
    #    #appended for future functionality
    
class GroupResolution(Group):
    ''' UI address change class ''' 
    type = FeedType.RESOLUTIONFEED
    #DA = DEF_ADDR[type]
    
    def __init__(self, ref=None): 
        super(GroupResolution,self).__init__(ref)    
        
    def __str__(self):
        return 'GRPR.{}.{}'.format(self._ref,self.type)
    
    #def filter(self):
    #    pass
    #    #appended for future functionality
    
    
    