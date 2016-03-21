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
import os
import copy
from AimsUtility import EntityType,ActionType,ApprovalType,FeedType,InvalidEnumerationType
from AimsUtility import SKIP_NULL, DEF_SEP
from Address import Address,AddressChange,AddressResolution,Position
from AimsLogging import Logger

P = os.path.join(os.path.dirname(__file__),'../resources/')


ET = EntityType.ADDRESS

TP = {'{}.{}'.format(EntityType.reverse[ET].lower(),a):b for a,b in zip(
        [FeedType.reverse[ft].lower() for ft in FeedType.reverse],
        [   {},
            {ActionType.reverse[at].lower():None for at in ActionType.reverse},
            {ApprovalType.reverse[at].lower():None for at in ApprovalType.reverse}
        ]
        )
    }
#AT = {FeedType.FEATURES:Address,FeedType.CHANGEFEED:AddressChange,FeedType.RESOLUTIONFEED:AddressResolution}

aimslog = None
 
class AddressException(Exception): pass    
class AddressFieldRequiredException(AddressException): pass
class AddressFieldIncorrectException(AddressException): pass
class AddressConversionException(AddressException): pass
class AddressCreationException(AddressException): pass

class EntityFactory(object):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time an address is needed''' 
    PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    AFFT = FeedType.FEATURES
    DEF_REF = FeedType.reverse[AFFT]
    addrtype = Address
    reqtype = None
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=DEF_REF):
        pass
        #self.ref = ref
        #key = '{}.{}'.format(EntityType.reverse[ET].lower(),FeedType.reverse[ref].lower())
        #self.template = TemplateReader().get()[key]
    
    #def __str__(self):
    #    return 'AFC.{}'.format(FeedType.reverse(self.AFFT)[:3])
    
    @staticmethod
    def getInstance(et,ft):
        '''Gets an instance of a factory to generate a particular (ft) type of address object'''
        #NOTE. Double duty for ft, consider (et,ft) - since enums are just ints et.g=ft.f
        if et==EntityType.GROUPS:
            from GroupFactory import GroupChangeFactory,GroupResolutionFactory
            if ft==FeedType.CHANGEFEED: return GroupChangeFactory(ft)
            elif ft==FeedType.RESOLUTIONFEED: return GroupResolutionFactory(ft)
            else: raise InvalidEnumerationType('FeedType {} not available'.format(ft))
        elif et==EntityType.ADDRESS:
            from AddressFactory import AddressFactory,AddressChangeFactory,AddressResolutionFactory
            if ft==FeedType.FEATURES: return AddressFactory(ft)
            elif ft==FeedType.CHANGEFEED: return AddressChangeFactory(ft)
            elif ft==FeedType.RESOLUTIONFEED: return AddressResolutionFactory(ft)
            else: raise InvalidEnumerationType('FeedType {} not available'.format(ft))
        else: raise InvalidEnumerationType('EntityType {} not available'.format(ft))
    
    
    @staticmethod
    def filterPI(ppi):
        '''filters out possible Processing Instructions'''
        sppi = str(ppi)
        if sppi.find('#')>-1:
            dflt = re.search('default=(\w+)',sppi)
            oneof = re.search('oneof=(\w+)',sppi)#first as default
            return dflt.group(1) if dflt else (oneof.group(1) if oneof else None)
        return ppi
           