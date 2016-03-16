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
from AimsUtility import ActionType,ApprovalType,FeedType,ENABLE_RESOLUTION_FEED_WARNINGS
from Address import Entity
from AimsLogging import Logger

aimslog = None

class DataUpdater(threading.Thread):
    '''Mantenence thread comtrolling data updates and api interaction
    Instantiates an amisapi instance with wrappers for initialisation of local data store 
    and change/resolution feed updating
    '''
    ft = FeedType.FEATURES
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
        
    def setup(self,ft,sw,ne,page):
        '''request a page'''
        self.ft = ft
        self.sw,self.ne = sw,ne
        self.page = page

    def run(self):
        '''get single page of addresses from API'''
        aimslog.info('GET.{} {} - Page{}'.format(self.ref,FeedType.reverse[self.ft],self.page))
        addrlist = []
        for entity in self.api.getOnePage(self.ft,self.sw,self.ne,self.page):
            if self.ft == FeedType.RESOLUTIONFEED and ENABLE_RESOLUTION_FEED_WARNINGS:
                #get drill-down resolution address objects (if enabled)
                cid = entity['properties']['changeId']
                entitylist = []
                feat = self.api.getOneFeature(self.ft,cid)
                if feat == {u'class': [u'error']}: 
                    #if the feature is the not-supposed-to-happen error, it gets special treatment
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
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def close(self):
        aimslog.info('Queue {} stopped'.format(self.queue.qsize()))
        self.queue.task_done()
     

class DataUpdaterAction(DataUpdater):
    ft = FeedType.CHANGEFEED
    def setup(self,at,address):
        '''set address parameters'''
        self.at = at
        self.address = address
        self.addressId = address.getAddressId()
        self.requestId = address.getRequestId()
        self.address.setVersion(self.fetchVersion())
        self.payload = self.afactory.convertAddress(self.address,self.at)
        
    def fetchVersion(self):
        jc = self.api.getOneFeature(FeedType.FEATURES,self.addressId)
        if jc['properties'].has_key('version'):
            return jc['properties']['version']
        else:
            #WORKAROUND
            aimslog.warn('No version number available for addressId={}'.format(self.addressId))
            return 1
    
    def run(self):
        '''address change action on the CF'''
        aimslog.info('ACT.{} {} - Addr{}'.format(self.ref,ActionType.reverse[self.at],self.address))
        err,resp = self.api.changefeedActionAddress(self.at,self.payload)
        chg_adr = self.afactory.getAddress(model=resp)
        #print 'CHG_ADR',chg_adr
        if err: chg_adr.setErrors(err)
        if self.requestId: chg_adr.setRequestId(self.requestId)
        self.queue.put(chg_adr)

            
class DataUpdaterApproval(DataUpdater):
    '''Updater to request and process response objects for resolution queue actions'''
    ft=FeedType.RESOLUTIONFEED
    def setup(self,at,address):
        '''set address parameters'''
        self.at = at
        self.address = address
        self.changeId = address.getChangeId()
        self.requestId = address.getRequestId()
        self.address.setVersion(self.fetchVersion())
        self.payload = self.afactory.convertAddress(self.address,self.at)
        
    def fetchVersion(self):
        jc = self.api.getOneFeature(FeedType.CHANGEFEED,self.changeId)
        if jc['properties'].has_key('version'):
            return jc['properties']['version']
        else:
            #WORKAROUND
            aimslog.warn('No version number available for changeId={}'.format(self.changeId))
            return 1
        
    def run(self):
        '''approval action on the RF''' 
        aimslog.info('APP.{} {} - Addr{}'.format(self.ref,ApprovalType.reverse[self.at],self.address))
        err,resp = self.api.resolutionfeedApproveAddress(self.at,self.payload,self.changeId)
        res_adr = self.afactory.getAddress(model=resp)
        #print 'RES_ADR',res_adr
        if err: res_adr.setErrors(err)
        if self.requestId: res_adr.setRequestId(self.requestId)
        self.queue.put(res_adr)


        
    
        
        