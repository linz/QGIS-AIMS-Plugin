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
from Const import ENABLE_ENTITY_EVALUATION
from Address import Entity, EntityValidation, EntityAddress
from AimsLogging import Logger
from FeatureFactory import FeatureFactory

aimslog = None

class DataUpdaterSelectionException(AimsException):pass

class DataUpdater(threading.Thread):
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
        threading.Thread.__init__(self)
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
        for feature in self.api.getOnePage(self.etft,self.sw,self.ne,self.page):
            featlist.append(self.process(feature,self.etft))            
        self.queue.put(featlist)
        
    def process(self,feature,etft):
        '''process an individual feature, pulling nested entities on 3E'''
        if etft.ft == FeedType.RESOLUTIONFEED and ENABLE_ENTITY_EVALUATION:
            cid = self.cid(feature)
            featurelist = []
            feat = self.api.getOneFeature(etft,cid)
            if feat == {u'class': [u'error']}: 
                #if the feature request returns the not-supposed-to-happen error, it gets special treatment
                aimslog.error('Invalid API response {}'.format(feat))
                a = self.getfeat(model=feature['properties'])
                featurelist.append(Entity.getInstance())
            elif feat['class'][0] == 'validation':
                e = Entity.getInstance('validation')
                e = self.getEntityInstance()
            #HACK (until we figure out what eS is delivering in next patch)
            #-------------------------------
            elif feat['class'][0] == 'resolutiongroup':
                g = self.getfeat(model=feat['properties'])#group
                feat2 = self.api.getOneFeature(etft,'{}/address'.format(cid))#group entity/adr list
                etft2 = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
                afactory2 = FeatureFactory.getInstance(etft2)
                for f in feat2['entities']:
                    a = afactory2.getAddress(model=f['properties'])
                    flist2 = []
                    for e in f['entities']:
                        flist2.append(Entity.getInstance(e))
                    a._setEntities(flist2)
                    featurelist.append(a)
                g._setEntities(featurelist)
                return g
            #--------------------------------    
            #elif etft.et==FeatureType.GROUPS:#feat['class'] == 'address':
            #    e = Entity.getInstance('address')
            else:
                #process any nested entities
                a = self.getfeat(model=feat['properties'])
                for e in feat['entities']:
                    featurelist.append(Entity.getInstance(e))
            a._setEntities(featurelist)
        else:
            #just return the main feedlevel address objects
            a = self.getfeat(model=feature['properties'])
        return a
        
        
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
    
    def getEntityInstance(self):
        return Entity.getInstance('validation')
        return EntityValidation()#TODO
        
        
class DataUpdaterGroup(DataUpdater):
    def __init__(self,params,queue):
        super(DataUpdaterGroup,self).__init__(params,queue)
        self.getfeat = self.afactory.getGroup   
         
    def cid(self,f):
        return f['properties']['changeGroupId']
        
    def getEntityInstance(self):
        return Entity.getInstance('validation')
        return EntityAddress()#TODO
    

#TODO Consolidate group/address + action/approve subclasses. might be enough variation to retain seperate classes
#NOTES variables incl; oft=FF/RF,id=addressId/changeId/groupChangeId, action=approve/action/groupaction
class DataUpdaterDRC(DataUpdater):
    #unstantiated in subclass
    oft,etft,identifier,payload,action,agobj,at,build,requestId = 9*(None,)
    
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
        aimslog.info('DUr.{} {} - Adr-Grp{}'.format(self.ref,ActionType.reverse[self.at],self.agobj))
        err,resp = self.action(self.at,self.payload,self.identifier)
        feature = self.build(model=resp)
        #print 'feature',feature
        if err: feature.setErrors(err)
        if self.requestId: feature.setRequestId(self.requestId)
        self.queue.put(feature)
        
        
class DataUpdaterAction(DataUpdaterDRC):
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.FEATURES
    def setup(self,etft,at,address):
        '''set address parameters'''
        self.etft = etft
        self.at = at
        self.agobj = address
        self.identifier = None#self.agobj.getAddressId()
        self.requestId = self.agobj.getRequestId()
        if at!=ActionType.ADD: self.agobj.setVersion(self.version())
        self.payload = self.afactory.convertAddress(self.agobj,self.at)
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
        self.agobj = address
        self.identifier = self.agobj.getChangeId()
        self.requestId = self.agobj.getRequestId()
        self.agobj.setVersion(self.version())
        self.payload = self.afactory.convertAddress(self.agobj,self.at)
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
        self.agobj = group
        self.identifier = self.agobj.getChangeGroupId()
        self.requestId = self.agobj.getRequestId()
        self.agobj.setVersion(self.version())
        self.payload = self.afactory.convertGroup(self.agobj,self.at)
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
        self.agobj = group
        self.identifier = self.agobj.getChangeGroupId()
        self.requestId = self.agobj.getRequestId()
        self.agobj.setVersion(self.version())
        self.payload = self.afactory.convertGroup(self.agobj,self.at)
        #run actions
        self.action = self.api.groupApprove
        self.build = self.afactory.getGroup
        
        
    
        
        