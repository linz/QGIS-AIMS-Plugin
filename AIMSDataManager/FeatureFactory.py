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
import sys
import copy
from AimsUtility import FeatureType,ActionType,ApprovalType,FeedType,InvalidEnumerationType,AimsException
from Const import SKIP_NULL, DEF_SEP,RES_PATH
from Address import Address,AddressChange,AddressResolution,Position
from AimsLogging import Logger

P = os.path.join(os.path.dirname(__file__),'../resources/')

# ET = FeatureType.ADDRESS
# 
# TP = {'{}.{}'.format(FeatureType.reverse[ET].lower(),a):b for a,b in zip(
#         [FeedType.reverse[ft].lower() for ft in FeedType.reverse],
#         [   {},
#             {ActionType.reverse[at].lower():None for at in ActionType.reverse},
#             {ApprovalType.reverse[at].lower():None for at in ApprovalType.reverse}
#         ]
#         )
#     }
#AT = {FeedType.FEATURES:Address,FeedType.CHANGEFEED:AddressChange,FeedType.RESOLUTIONFEED:AddressResolution}

aimslog = None
 
class AddressException(AimsException): pass    
class AddressFieldRequiredException(AddressException): pass
class AddressFieldIncorrectException(AddressException): pass
class AddressConversionException(AddressException): pass
class AddressCreationException(AddressException): pass

class FeatureFactory(object):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time an address is needed''' 
    PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    AFFT = FeedType.FEATURES
    DEF_REF = FeedType.reverse[AFFT]
    addrtype = Address
    reqtype = None
    #RP = eval(RES_PATH)
    RP = os.path.join(os.path.dirname(__file__),'..',RES_PATH)
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=DEF_REF):
        pass
        #self.ref = ref
        #key = '{}.{}'.format(FeatureType.reverse[ET].lower(),FeedType.reverse[ref].lower())
        #self.template = TemplateReader().get()[key]
    
    #def __str__(self):
    #    return 'AFC.{}'.format(FeedType.reverse(self.AFFT)[:3])
    
    @staticmethod
    def getInstance(etft):
        '''Gets an instance of a factory to generate a particular (ft) type of address object'''
        #NOTE. Double duty for ft, consider (et,ft) - since enums are just ints et.g=ft.f
        if etft.et==FeatureType.GROUPS:
            from GroupFactory import GroupChangeFactory,GroupResolutionFactory
            if etft.ft==FeedType.CHANGEFEED: return GroupChangeFactory(etft)
            elif etft.ft==FeedType.RESOLUTIONFEED: return GroupResolutionFactory(etft)
            else: raise InvalidEnumerationType('FeedType {} not available'.format(etft))
        elif etft.et==FeatureType.ADDRESS:
            from AddressFactory import AddressFactory,AddressChangeFactory,AddressResolutionFactory
            if etft.ft==FeedType.FEATURES: return AddressFactory(etft)
            elif etft.ft==FeedType.CHANGEFEED: return AddressChangeFactory(etft)
            elif etft.ft==FeedType.RESOLUTIONFEED: return AddressResolutionFactory(etft)
            else: raise InvalidEnumerationType('FeedType {} not available'.format(etft.ft))
        elif etft.et==FeatureType.USERS:
            from UserFactory import UserFactory
            if etft.ft==FeedType.ADMIN: return UserFactory(etft)
            else: raise InvalidEnumerationType('FeedType {} not available'.format(etft.ft))
        else: raise InvalidEnumerationType('FeatureType {} not available'.format(etft.et))
    
    
    @staticmethod
    def filterPI(ppi):
        '''filters out possible Processing Instructions'''
        sppi = str(ppi)
        if sppi.find('#')>-1:
            dflt = re.search('default=(\w+)',sppi)
            oneof = re.search('oneof=(\w+)',sppi)#first as default
            return dflt.group(1) if dflt else (oneof.group(1) if oneof else None)
        return ppi
    
    @staticmethod
    def readTemplate(tp):
        for t1 in tp:
            for t2 in tp[t1]:
                with open(os.path.join(FeatureFactory.RP,'{}.{}.template'.format(t1,t2)),'r') as handle:
                    tstr = handle.read()
                    #print 'read template',t1t,t2t
                    tp[t1][t2] = eval(tstr) if tstr else ''
            #response address type is the template of the address-json we get from the api
            with open(os.path.join(FeatureFactory.RP,'{}.response.template'.format(t1)),'r') as handle:
                tstr = handle.read()
                tp[t1]['response'] = eval(tstr) if tstr else ''
        return tp
    
    def _delNull(self, obj):
        if hasattr(obj, 'items'):
            new_obj = type(obj)()
            for k in obj:
                #if k != 'NULL' and obj[k] != 'NULL' and obj[k] != None:
                if k and obj[k]:
                    res = self._delNull(obj[k])
                    if res: new_obj[k] = res
        elif hasattr(obj, '__iter__'):
            new_obj = [] 
            for it in obj:
                #if it != 'NULL' and it != None:
                if it: new_obj.append(self._delNull(it))
        else: return obj
        return type(obj)(new_obj)
    
           