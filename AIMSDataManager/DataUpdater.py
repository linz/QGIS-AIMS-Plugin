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

from datetime import datetime as DT
#from functools import wraps

import Image, ImageStat, ImageDraw
import urllib2
import StringIO
import random
import os
import sys
import re
import pickle
import getopt
import logging
import zipfile

import threading
import Queue
from AimsApi import AimsApi 
from AimsUtility import FeedRef,ActionType,ApprovalType,FeatureType,FeedType,AimsException
from Const import ENABLE_ENTITY_EVALUATION, MERGE_RESPONSE
from Address import Entity, EntityValidation, EntityAddress
from AimsLogging import Logger
from FeatureFactory import FeatureFactory
from Observable import Observable

aimslog = None

class DataUpdaterSelectionException(AimsException):pass

class DataUpdater(Observable):
    '''Mantenence thread comtrolling data updates and api interaction
    Instantiates an amisapi instance with wrappers for initialisation of local data store 
    and change/resolution feed updating
    '''
    #et = FeatureType.ADDRESS
    #ft = FeedType.FEATURES
    address = None
    page = 0
    changeId = 0
    
    global aimslog
    aimslog = Logger.setup()
    
    getfeat = None
    
    def __init__(self,params,queue):
        super(DataUpdater,self).__init__()
        self.ref,self.conf,self.afactory = params
        self.queue = queue
        self._stop = threading.Event()
        self.api = AimsApi(self.conf)    
        
    def setup(self,etft,sw,ne,page):
        '''request a page'''
        self.etft = etft
        self.sw,self.ne = sw,ne
        self.page = page

    def run(self):
        '''Main updater run method for feed cycling gets single page of addresses from API'''
        aimslog.info('GET.{} {} - Page{}'.format(self.ref,self.etft,self.page))
        featlist = []
        for page in self.api.getOnePage(self.etft,self.sw,self.ne,self.page):
            featlist.append(self.processPage(page,self.etft))            
        self.queue.put(featlist)
        self.notify(self.ref)
        
    def processPage(self,page,etft):
        '''process an individual page, pulling nested entities on 3E'''
        if etft.ft == FeedType.RESOLUTIONFEED and ENABLE_ENTITY_EVALUATION:
            cid = self.cid(page)
            feat = self.api.getOneFeature(etft,cid)
            if feat == {u'class': [u'error']}: 
                #if the page request returns the not-supposed-to-happen error, it gets special treatment
                aimslog.error('Invalid API response {}'.format(feat))
                #return self.getfeat(model=page['properties'])
            else:
                return self._processEntity(feat,cid,etft)
        else:
            #just return the main feedlevel address objects
            return self.getfeat(model=page['properties'])
    
    def _processEntity(self,feat,cid,etft):
        '''Select processing option'''
        if feat['class'][0] == 'validation':
            return self._processValidationEntity(feat)
            #e = EntityValidation.getInstance(feat)# self.getEntityInstance()
        #-------------------------------
        # Resolution Group
        elif feat['class'][0] == 'resolutiongroup':
            return self._processResolutionGroup(feat,cid,etft)
        # Address List
        elif feat['class'][0] == 'addressresolution':
            return self._processAddressResolution(feat)
        #--------------------------------
        # Simple Entity object
        else:
            return self._processSimpleEntity(self.getfeat,feat)
        
    def _processValidationEntity(self,feat):
        return EntityValidation.getInstance(feat)
    
    def _processAddressEntity(self,feat):
        #return EntityAddress.getInstance(feat)
        return self._processSimpleEntity(FeatureFactory.getInstance(FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))).getAddress,feat)
        
    def _processSimpleEntity(self,fact,feat):                
        '''this is the default processor, for gereric entities but the same as addr res'''
        featurelist = []
        a = fact(model=feat['properties'])
        if feat.has_key('entities'):
            for e in feat['entities']:
                featurelist.append(self._populateEntity(e))
            a._setEntities(featurelist)
        return a
    
    def _processAddressResolution(self,feat):                
        '''process entries in the addressresolution->entities list'''
        featurelist = []
        a = self.getfeat(model=feat['properties'])
        for e in feat['entities']:
            featurelist.append(self._populateEntity(e))
        a._setEntities(featurelist)
        return a
        
    def _processResolutionGroup(self,feat,cid,etft):
        '''process the entities in a res-group. these are res-address objects. in turn populate the sub entities as feature-addresses'''
        featurelist = []
        g = self.getfeat(model=feat['properties'])#group
        feat2 = self.api.getOneFeature(etft,'{}/address'.format(cid))#group entity/adr list
        etft2 = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
        afactory2 = FeatureFactory.getInstance(etft2)
        for f in feat2['entities']:
            a = afactory2.getAddress(model=f['properties'])
            elist2 = []
            for e in f['entities']:
                elist2.append(self._populateEntity(e))
            a._setEntities(elist2)
            featurelist.append(a)
        g._setEntities(featurelist)
        return g
        
    def _populateEntity(self,ent):
        if ent['class'][0] == 'validation':
            return self._processValidationEntity(ent)
        elif ent['class'][0] == 'address':
            ###res factory might work here instead
            #etft3 = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
            #afactory3 = FeatureFactory.getInstance(etft3)
            #return afactory3.getAddress(model=e['properties'])
            return self._processAddressEntity(ent)
        
        else:
            return Entity.getInstance(e)
        
    @staticmethod
    def getInstance(etft):
        if etft.et == FeatureType.GROUPS: return DataUpdaterGroup
        elif etft.et == FeatureType.ADDRESS: return DataUpdaterAddress
        else: raise DataUpdaterSelectionException('Select Grp or Adr')
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def close(self):
        aimslog.info('Queue {} stopped'.format(self.queue.qsize()))
        self.queue.task_done()
        
    #executed by subclass
    def cid(self): pass
        
#---------------------------------------------------------------
    
#simple subclasses to assign getaddress/getgroup function    
class DataUpdaterAddress(DataUpdater):
    def __init__(self,params,queue):
        super(DataUpdaterAddress,self).__init__(params,queue)
        self.getfeat = self.afactory.getAddress
        
    def cid(self,f):
        return f['properties']['changeId']
    
    def getEntityInstance(self,d,etft):
        return EntityValidation(d,etft)
        
        
class DataUpdaterGroup(DataUpdater):
    def __init__(self,params,queue):
        super(DataUpdaterGroup,self).__init__(params,queue)
        self.getfeat = self.afactory.getGroup   
         
    def cid(self,f):
        return f['properties']['changeGroupId']
        
    def getEntityInstance(self,d,etft):
        return EntityAddress(d,etft)
    
class DataUpdaterUser(DataUpdater):    
    def __init__(self,params,queue):
        super(DataUpdaterUser,self).__init__(params,queue)
        self.getfeat = self.afactory.getUser 
    
    

#TODO Consolidate group/address + action/approve subclasses. might be enough variation to retain seperate classes
#NOTES variables incl; oft=FF/RF,id=addressId/changeId/groupChangeId, action=approve/action/groupaction
class DataUpdaterDRC(DataUpdater):
    #instantiated in subclass
    oft,etft,identifier,payload,action,agu,at,build,requestId = 9*(None,)
    
    def version(self):
        jc = self.api.getOneFeature(FeedRef((self.etft.et,self.oft)),self.identifier)
        if jc['properties'].has_key('version'):
            return jc['properties']['version']
        else:
            #WORKAROUND
            aimslog.warn('No version number available for address/groupId={}'.format(self.identifier))
            return 1    
        
    def run(self):
        '''group change action on the CF'''
        aimslog.info('DUr.{} {} - Adr-Grp{}'.format(self.ref,ActionType.reverse[self.at],self.agu))
        err,resp = self.action(self.at,self.payload,self.identifier)
        featurelist = []
        feature = self.build(model=resp['properties'])
        for e in resp['entities']:
            featurelist.append(self._populateEntity(e))
        feature._setEntities(featurelist)
        #feature = self.processPage(feature,self.etft)
        #print 'feature',feature
        if err: feature.setErrors(err)
        if self.requestId: feature.setRequestId(self.requestId)
        if MERGE_RESPONSE:
            aimslog.info('Merge req/res for {}'.format(self.agu))
            self.agu.merge(feature)
            self.queue.put(self.agu)
        else: self.queue.put(feature)
        self.notify(self.ref)
        
        
class DataUpdaterAction(DataUpdaterDRC):
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.FEATURES
    def setup(self,etft,at,address):
        '''set address parameters'''
        self.etft = etft
        self.at = at
        self.agu = address
        self.identifier = self.agu.getAddressId()
        self.requestId = self.agu.getRequestId()
        if at!=ActionType.ADD: self.agu.setVersion(self.version())
        self.payload = self.afactory.convertAddress(self.agu,self.at)
        #run actions
        self.action = self.api.addressAction
        self.build = self.afactory.getAddress

class DataUpdaterApproval(DataUpdaterDRC):
    '''Updater to request and process response objects for resolution queue actions'''
    #et = FeatureType.ADDRESS
    #ft = FeedType.RESOLUTIONFEED
    oft = FeedType.RESOLUTIONFEED
    def setup(self,etft,at,address):
        '''set address parameters'''
        self.etft = etft
        self.at = at
        self.agu = address
        self.identifier = self.agu.getChangeId()
        self.requestId = self.agu.getRequestId()
        self.agu.setVersion(self.version())
        self.payload = self.afactory.convertAddress(self.agu,self.at)
        #run actions
        self.action = self.api.addressApprove
        self.build = self.afactory.getAddress

class DataUpdaterGroupAction(DataUpdaterDRC):
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.FEATURES
    def setup(self,etft,at,group):
        '''set group parameters'''
        self.etft = etft
        self.at = at
        self.agu = group
        self.identifier = self.agu.getChangeGroupId()
        self.requestId = self.agu.getRequestId()
        self.agu.setVersion(self.version())
        self.payload = self.afactory.convertGroup(self.agu,self.at)
        #run actions
        self.action = self.api.groupAction
        self.build = self.afactory.getGroup
        
class DataUpdaterGroupApproval(DataUpdaterDRC):
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.RESOLUTIONFEED
    def setup(self,etft,at,group):
        '''set group parameters'''
        self.etft = etft
        self.at = at
        self.agu = group
        self.identifier = self.agu.getChangeGroupId()
        self.requestId = self.agu.getRequestId()
        self.agu.setVersion(self.version())
        self.payload = self.afactory.convertGroup(self.agu,self.at)
        #run actions
        self.action = self.api.groupApprove
        self.build = self.afactory.getGroup
        
class DataUpdaterUserAction(DataUpdaterDRC):
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.ADMIN
    def setup(self,etft,at,user):
        '''set user parameters'''
        self.etft = etft
        self.at = at
        self.agu = user
        self.identifier = self.agu.getUserId()
        self.requestId = self.agu.getRequestId()
        #self.agu.setVersion(self.version())
        self.payload = self.afactory.convertUser(self.agu,self.at)
        #run actions
        self.action = self.api.userAction
        self.build = self.afactory.getUser
        
        
    
        
        