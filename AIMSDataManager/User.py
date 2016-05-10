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
from AimsLogging import Logger
from Feature import Feature


#aimslog = None

        
#------------------------------------------------------------------------------
# G R O U P 

class User(Feature):
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=None): 
        #aimslog.info('AdrRef.{}'.format(ref))
        self._ref = ref
    
    def __str__(self):
        return 'USR.{}.{}'.format(self._ref,self.userId)
    
    def setUserId(self, userId):
        self._userId = userId
    def getUserId(self):
        return self._userId
    
    def setEmail(self, email):
        self._email = email if Feature._vEmail(email) else None


    
    
    