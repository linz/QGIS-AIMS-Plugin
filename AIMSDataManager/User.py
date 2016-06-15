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

#http://devassgeo01:8080/aims/api/sdmin/users
from AimsUtility import UserActionType
from AimsUtility import AimsException
from AimsLogging import Logger
from Feature import Feature
       
class UserException(AimsException): pass
 
#------------------------------------------------------------------------------
# U S E R

class User(Feature):
    '''Class representing AIMS user'''
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=None): 
        '''Initialise User object
        @param ref: Unique reference string
        '''
        #aimslog.info('AdrRef.{}'.format(ref))
        self._ref = ref
    
    def __str__(self):
        return 'USR.{}.{}'.format(self._ref,self._userId)
    
    def setUserId(self, userId):
        self._userId = userId
    def getUserId(self):
        return self._userId
    
    def setEmail(self, email):
        self._email = email if Feature._vEmail(email) else None
        


    
    
    