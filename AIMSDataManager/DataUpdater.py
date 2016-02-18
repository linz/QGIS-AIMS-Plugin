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

from urllib2 import HTTPError, base64, ProxyHandler
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
from AimsUtility import ActionType,FeedType

from AimsLogging import Logger

aimslog = None

class DataUpdater(threading.Thread):
    '''Mantenence thread comtrolling data updates and api interaction
    Instantiates an amisapi instance with wrappers for initialisation of local data store 
    and change/resolution feed updating
    '''
    address = None
    page = 0
    
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
        addr = []
        for entity in self.api.getOnePage(self.ft,self.sw,self.ne,self.page):
            addr += [self.afactory.getAddress(model=entity['properties']),]
        self.queue.put(addr)

        
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def close(self):
        aimslog.info('Queue {} stopped'.format(self.outq.qsize()))
        self.respq.task_done()
        
class DataUpdaterAction(DataUpdater):
    
    def setup(self,ft,address):
        '''set address parameters'''
        self.ft = ft
        self.address = address
        self.payload = self.afactory.convertAddress(self.address,self.ft)
        
    def run(self):
        '''address change action on the CF'''
        aimslog.info('ACT.{} {} - Addr{}'.format(self.ref,ActionType.reverse[self.ft],self.address))
        resp = self.api.changefeedActionAddress(self.ft,self.payload)
        chg_adr = self.afactory.getAddress(model=resp)
        print 'CHG_ADR',res_adr
        self.queue.put(chg_adr)

            
class DataUpdaterApproval(DataUpdater):
    
    def setup(self,ft,address):
        '''set address parameters'''
        self.ft = ft
        self.address = address
        self.cid = address.getChangeId()
        self.payload = self.afactory.convertAddress(self.address,self.ft)
        
    def run(self):
        '''approval action on the RF''' 
        aimslog.info('APP.{} {} - Addr{}'.format(self.ref,ApprovalType.reverse[self.ft],self.address))
        resp = self.api.resolutionfeedApproveAddress(self.ft,self.payload,self.cid)
        res_adr = self.afactory.getAddress(model=resp)
        print 'RES_ADR',res_adr
        res_adr.setWarning(self.api.getWarnings(self.cid))
        self.queue.put(res_adr)
        #self.queue.put({'resp':resp,'warn':warn})

        
    
        
        