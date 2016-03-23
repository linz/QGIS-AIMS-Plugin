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
from AimsUtility import FeedRef,ActionType,ApprovalType,FeatureType,FeedType,ENABLE_RESOLUTION_FEED_WARNINGS
from Address import Entity
from AimsLogging import Logger

aimslog = None

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
        '''get single page of addresses from API'''
        aimslog.info('GET.{} {} - Page{}'.format(self.ref,self.etft,self.page))
        addrlist = []
        for entity in self.api.getOnePage(self.etft,self.sw,self.ne,self.page):
            if self.etft.ft == FeedType.RESOLUTIONFEED and ENABLE_RESOLUTION_FEED_WARNINGS:
                #get drill-down resolution address objects (if enabled)
                cid = entity['properties']['changeId']
                entitylist = []
                feat = self.api.getOneFeature(self.etft,cid)
                if feat == {u'class': [u'error']}: 
                    #if the feature request returns the not-supposed-to-happen error, it gets special treatment
                    aimslog.error('Invalid API response {}'.format(feat))
                    a = self.afactory.getAddress(model=entity['properties'])
                    entitylist.append(Entity.getInstance())
                else:
                    a = self.afactory.getAddress(model=feat['properties'])
                    for e in feat['entities']:
                        entitylist.append(Entity.getInstance(e))
                a._setEntities(entitylist)
            else:
                #just return the main feedlevel address objects
                a = self.afactory.getAddress(model=entity['properties'])
            addrlist += [a,]
        self.queue.put(addrlist)
        
    def version(self):
        jc = self.api.getOneFeature(FeedRef((self.etft.et,self.oft)),self.identifier)
        if jc['properties'].has_key('version'):
            return jc['properties']['version']
        else:
            #WORKAROUND
            aimslog.warn('No version number available for addressId={}'.format(self.identifier))
            return 1
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def close(self):
        aimslog.info('Queue {} stopped'.format(self.queue.qsize()))
        self.queue.task_done()
        
    #---------------------------------------------------------------
    
#TODO Consolidate group/address + action/approve subclasses. might be enough variation to retain seperate classes
#NOTES variables incl; oft=FF/RF,id=addressId/changeId/groupChangeId, action=approve/action/groupaction
class DataUpdaterDRC(DataUpdater):
    def version(self):
        jc = self.api.getOneFeature(FeedRef((self.etft.et,self.oft)),self.identifier)
        if jc['properties'].has_key('version'):
            return jc['properties']['version']
        else:
            #WORKAROUND
            aimslog.warn('No version number available for addressId={}'.format(self.identifier))
            return 1    
        
    def run(self):
        '''group change action on the CF'''
        aimslog.info('ACT.{} {} - Adr-Grp{}'.format(self.ref,ActionType.reverse[self.at],self.agobj))
        err,resp = self.action(self.at,self.payload)
        feature = self.build(model=resp)
        #print 'CHG_ADR',chg_adr
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
        self.identifier = self.agobj.getAddressId()
        self.requestId = self.agobj.getRequestId()
        self.agobj.setVersion(self.version())
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
        
        
    
        
        