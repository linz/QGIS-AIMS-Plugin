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
from AimsUtility import FeatureType,ActionType,ApprovalType,FeedType
from AimsUtility import AimsException,InvalidEnumerationType
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
 
class FeatureException(AimsException): pass    
class FeatureFieldRequiredException(FeatureException): pass
class FeatureFieldIncorrectException(FeatureException): pass
class FeatureConversionException(FeatureException): pass
class FeatureCreationException(FeatureException): pass

class FeatureFactory(object):
    '''Factory class for Feature objects but used as super class with construction management duties. Saves overhead on template reading each time a feature is needed''' 
    
    PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    AFFT = FeedType.FEATURES
    DEF_FRT = FeedType.reverse[AFFT]
    addrtype = Address
    reqtype = None
    #RP = eval(RES_PATH)
    RP = os.path.join(os.path.dirname(__file__),'..',RES_PATH)
    
    global aimslog
    aimslog = Logger.setup()
    
    @staticmethod
    def getInstance(etft):
        '''Gets an instance of a factory to generate a particular FeedRef type of object
        @param etft: FeeedRefobject describing required featuretype, feedtype object required
        @type etft: FeedRef
        @return: Feature
        '''
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
        '''Filters out Processing Instructions from template declaration
        @param ppi: Processing instruction text
        @type ppi: String
        @return: List if possible attributes or a default attribute
        '''
        sppi = ppi.encode('utf8') if hasattr(ppi,'find') else str(ppi)
        if sppi.find('#')>-1:
            dflt = re.search('default=(\w+)',sppi)
            oneof = re.search('oneof=(\w+)',sppi)#first as default
            return dflt.group(1) if dflt else (oneof.group(1) if oneof else None)
        return ppi
    
    @staticmethod
    def readTemplate(tp):
        '''Reads and parses template file returning attribute dict
        @param tp: Dict of all feed type + feature type combinations used to construct template filenames
        @type tp: Dict of attributes for all Feature/Feed type combinations
        @return: Dict representing templates for JSON AIMS request/response 
        '''
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
    
    @staticmethod
    def _delNull(obj):
        '''Removes Null/empty attributes from dict of attributes
        @param obj: Object to strip of null values
        @return: Stripped down object
        '''
        if hasattr(obj, 'items'):
            new_obj = type(obj)()
            for k in obj:
                #if k != 'NULL' and obj[k] != 'NULL' and obj[k] != None:
                if k and obj[k]:
                    res = FeatureFactory._delNull(obj[k])
                    if res: new_obj[k] = res
        elif hasattr(obj, '__iter__'):
            new_obj = [] 
            for it in obj:
                #if it != 'NULL' and it != None:
                if it: new_obj.append(FeatureFactory._delNull(it))
        else: return obj
        return type(obj)(new_obj)
    
           