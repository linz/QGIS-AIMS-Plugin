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
import time
import threading
import Queue

from DataUpdater import DataUpdater,DataUpdaterAction,DataUpdaterApproval,DataUpdaterWarning
from AimsApi import AimsApi 
from AimsLogging import Logger
from AimsUtility import ActionType,ApprovalType,FeedType,LogWrap
from AimsUtility import MAX_FEATURE_COUNT,THREAD_JOIN_TIMEOUT,PAGE_LIMIT,POOL_PAGE_CHECK_DELAY,QUEUE_CHECK_DELAY,FIRST_PAGE,LAST_PAGE_GUESS,ENABLE_RESOLUTION_FEED_WARNINGS,NULL_PAGE_VALUE as NPV
from AddressFactory import AddressFactory#,AddressChangeFactory,AddressResolutionFactory
aimslog = None

FPATH = os.path.join('..',os.path.dirname(__file__)) #base of local datastorage
#FNAME = 'data_hash'

#PAGES_INIT = 10
#PAGES_PERIOCDIC = 3
#FEED_REFRESH_DELAY = 10


class DataRequestChannel(threading.Thread):    
    '''Request response channel for user initiated actions eg add decline retire etc'''
    def __init__(self,client):
        threading.Thread.__init__(self)
        self.client = client
        self._stop = threading.Event()
        
    def run(self):
        '''Continual loop looking for input queue requests and running periodic updates'''
        while True:
            #if there are things in the client's input queue, process them, push to CF #TODO. there shouldnt ever be anything in the FF inq
            if not self.client.inq.empty():
                changelist = self.client.inq.get()    
                aimslog.info('DRC FT {} - found {} items in queue'.format(FeedType.reverse[self.client.ft],len(changelist)))
                self.client.processInputQueue(changelist)
                
            time.sleep(QUEUE_CHECK_DELAY)
            
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
class DataSync(threading.Thread):
    '''Background thread triggering periodic data updates and synchronising update requests from DM.  
    '''
    
    global aimslog
    aimslog = Logger.setup()
    
    lock = threading.Lock()
    duinst = {}
    
    #hash to compare latest fetched data
    data_hash = {ft:0 for ft in FeedType.reverse}
    
    sw,ne = None,None
    
    def __init__(self,params,queues):
        threading.Thread.__init__(self)
        #thread reference, ft to AD/CF/RF, config info
        self.ref,self.ft,self.ftracker,self.conf = params
        self.afactory = AddressFactory.getInstance(self.ft)
        self.inq = queues['in']
        self.outq = queues['out']
        self.respq = queues['resp']
        self._stop = threading.Event()
        
    def setup(self,sw=None,ne=None):
        '''Parameter setup'''
        self.sw,self.ne = sw,ne
        

    def run(self):
        '''Continual loop looking for input queue requests and running periodic updates'''
        while True:
            #TODO. there shouldnt ever be anything in the FF inq
            updates,_ = self.fetchFeedUpdates(self.ftracker['threads'])
            if updates != None: 
                self.syncFeeds(updates)
                aimslog.debug('FT {} sleeping {} with size(Qin)={}'.format(FeedType.reverse[self.ft],self.ftracker['interval'],self.inq.qsize())) 
                time.sleep(self.ftracker['interval'])
            else:
                #if updates are none, stop has been called
                return
            
    #start = int(time.time())  
    #now = int(time.time())   
    #if (now-start) % self.ftracker['interval']:pass        
    
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def close(self):
        self.inq.task_done()
        self.outq.task_done()

    #--------------------------------------------------------------------------            

    @LogWrap.timediff
    def fetchFeedUpdates(self,thr,lastpage=FIRST_PAGE):
        '''get full page loads'''
        exhausted = PAGE_LIMIT
        newaddr = []
        #setup pool
        #print 'LP {} {}->{}'.format(FeedType.reverse[self.ft][:2].capitalize(),lastpage,lastpage+thr)
        pool = [{'page':p,'ref':None} for p in range(lastpage,lastpage+thr)]
        for r in pool:
            r['ref'] = self.fetchPage(r['page'])
        
        while len(pool)>0:#any([p[2] for p in pool if p[2]>1])
            #print '{} {}'.format(FeedType.reverse[self.ft].capitalize(),'STOP' if self.stopped() else 'RUN')
            for r in pool:
                aimslog.debug('### Page {}{} pool={}'.format(FeedType.reverse[self.ft][:2].capitalize(), r['page'],[p['page'] for p in pool])) 
                #du = self.duinst[r['ref']]
                #close down on stop signal
                if self.stopped():
                    self.stopSubs(pool)
                    return None,None
                #    print 'halt' 
                du = self.duinst[r['ref']]
                if not du.isAlive():
                    #print '{}{} finished'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
                    alist = du.queue.get()
                    acount = len(alist)
                    newaddr += alist
                    nextpage = max([r2['page'] for r2 in pool])+1
                    del self.duinst[r['ref']]
                    pool.remove(r)
                    #if N>0 features return, spawn another thread
                    if acount<MAX_FEATURE_COUNT:
                        exhausted = r['page']
                    if acount>0:
                        lastpage = max(r['page'],lastpage)
                        if nextpage<exhausted:
                            ref = self.fetchPage(nextpage)
                            pool.append({'page':nextpage,'ref':ref})
                    else:
                        pass
                        #print 'No addresses found in page {}{}'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
                time.sleep(POOL_PAGE_CHECK_DELAY)
                #print '---------\n'

        #print 'Leaving {} with pool={} and #adr={}'.format(FeedType.reverse[self.ft][:2].capitalize(),[p['page'] for p in pool],len(newaddr))
        return newaddr,lastpage
    
    def stopSubs(self,pool):
        '''Stop all subordinate threads'''
        for r in pool:
            aimslog.info('Stopping DataUpdater thread {}'.format(r['ref']))
            self.duinst[r['ref']].stop()
            self.duinst[r['ref']].join(THREAD_JOIN_TIMEOUT)
            if self.duinst[r['ref']].isAlive():aimslog.warn('Thread timeout {}'.format(r['ref']))
            del self.duinst[r['ref']]
            pool.remove(r)

            
    def fetchPage(self,p):
        '''Regular page fetch, periodic or demand'''   
        ft2 = FeedType.reverse[self.ft][:2].capitalize()
        ref = 'Get.{0}.Page{1}.{2:%y%m%d.%H%M%S}.p{3}'.format(ft2,p,DT.now(),p)
        params = (ref,self.conf,self.afactory)
        adrq = Queue.Queue()
        self.duinst[ref] = DataUpdater(params,adrq)
        if self.ft==FeedType.FEATURES: self.duinst[ref].setup(self.ft,self.sw,self.ne,p)
        else: self.duinst[ref].setup(self.ft,None,None,p)
        self.duinst[ref].setDaemon(True)
        self.duinst[ref].start()
        return ref
        #self.duinst[ref].join()
        #return adrq.get()

    #NOTE. To override the behaviour, return feed once full, override this method
    def syncFeeds(self,new_addresses):
        '''check if the addresses are diferent from existing set and return in the out queue'''
        new_hash = hash(frozenset(new_addresses))
        if self.data_hash[self.ft] != new_hash:
            self.data_hash[self.ft] = new_hash
            self.outq.put(new_addresses)

    #--------------------------------------------------------------------------
    
    def returnResp(self,resp):
        aimslog.info('RESP.{}'.format(resp))
        self.respq.put(resp)


class DataSyncFeatures(DataSync):
    
    #ft = FeedType.FEATURES
    
    def __init__(self,params,queues):
        super(DataSyncFeatures,self).__init__(params,queues)
        #self.ftracker = {'page':[1,1],'index':1,'threads':2,'interval':30}    


class DataSyncFeeds(DataSync): 
    
    def __init__(self,params,queues):
        super(DataSyncFeeds,self).__init__(params,queues)
        self.drc = DataRequestChannel(self)
        self.drc.setDaemon(True)
        
    def run(self):
        self.drc.start()
        super(DataSyncFeeds,self).run()
    
    def stop(self):
        self.drc.stop()
        self._stop.set()

    def stopped(self):
        return self._stop.isSet() and self.drc.stopped() 
    
    
    def fetchFeedUpdates(self,thr):
        '''run forward updates and tack on a single backfill, update page count accordingly'''
        pages = self.ftracker['page']
        bp,lp = pages if pages and pages!=[NPV,NPV] else 2*[self._findLastPage(LAST_PAGE_GUESS),]
        res,lp = super(DataSyncFeeds,self).fetchFeedUpdates(thr,lp)
        #get just one backfill per fFU  #[for i in range(5):#do a bunch of backfills?]
        if bp>FIRST_PAGE:
            bdata,bp = self.backfillPage(bp-1)
            res += bdata
        self.managePage((bp,lp))
        return res,lp
        
    def _findLastPage(self,p_end):
        '''Inefficient way to find the last page in the feed sequence'''
        p_start = 0
        p_end = p_end*2
        while True:
            p = int((p_start+p_end)/2)
            ref = self.fetchPage(p)
            du = self.duinst[ref]
            while self.duinst[ref].isAlive():
                time.sleep(POOL_PAGE_CHECK_DELAY)
            else:
                acount = len(du.queue.get())
                aimslog.debug('Page Find p{}={}'.format(p,acount))
                if acount==MAX_FEATURE_COUNT:
                    if p == p_start: p_end = p_end*2 
                    p_start = p
                elif acount>0: return p
                else: p_end = p         
    
    def backfillPage(self,prevpage):
        '''backfills pages from requested page. non-pooled/non-tracked since non critical'''
        newaddr = []
                
        ref = self.fetchPage(prevpage)
        du = self.duinst[ref]
        while du.isAlive(): time.sleep(POOL_PAGE_CHECK_DELAY)
        alist = du.queue.get()
        acount = len(alist)
        newaddr += self._statusFilter(alist)
        del self.duinst[ref]
        if acount>0:
            prevpage = max(1,prevpage-1)
            ref = self.fetchPage(prevpage)                
        return newaddr,prevpage

    def _statusFilter(self,alist):
        #something like this
        return [a for a in alist if a.getQueueStatus().lower() not in ('expired','deleted')]
    
    #Processes the input queue sending address changes to the API
    @LogWrap.timediff
    def processInputQueue(self,changelist):
        '''Take the input change queue and split out individual address objects for DU processing'''
        #{ADD:addr_1,RETIRE:adr_2...
        for at in changelist:
            #self.outq.put(act[addr](changelist[addr]))
            for address in changelist[at]:
                resp = self.processAddress(at,address)
                aimslog.info('{} thread started'.format(str(resp)))
                
    def processAddress(self,at,address): 
        '''override'''
        pass
    
    def managePage(self,p):
        if p[0]: self.ftracker['page'][0] = p[0]
        if p[1]: self.ftracker['page'][1] = p[1]

class DataSyncChangeFeed(DataSyncFeeds):
      
    def __init__(self,params,queues):
        super(DataSyncChangeFeed,self).__init__(params,queues)
        #self.ftracker = {'page':[1,1],'index':1,'threads':1,'interval':125}

    def processAddress(self,at,addr):  
        '''Do an Add/Retire/Update request'''
        at2 = ActionType.reverse[at][:3].capitalize()      
        ref = 'Req{0}.{1:%y%m%d.%H%M%S}'.format(at2,DT.now())
        params = (ref,self.conf,self.afactory)
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}
        self.duinst[ref] = DataUpdaterAction(params,self.respq)
        self.duinst[ref].setup(at,addr)
        self.duinst[ref].setDaemon(True)
        self.duinst[ref].start()
        #self.duinst[ref].join()
        return ref


class DataSyncResolutionFeed(DataSyncFeeds):
    
    def __init__(self,params,queues):
        super(DataSyncResolutionFeed,self).__init__(params,queues)
        #self.ftracker = {'page':[1,1],'index':1,'threads':1,'interval':10}
        
    def processAddress(self,at,addr):
        '''Do an Approve/Decline/Update request'''
        at2 = ApprovalType.reverse[at][:3].capitalize()      
        ref = 'Req{0}.{1:%y%m%d.%H%M%S}'.format(at2,DT.now())
        params = (ref,self.conf,self.afactory)
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}
        self.duinst[ref] = DataUpdaterApproval(params,self.respq)
        self.duinst[ref].setup(at,addr)
        self.duinst[ref].setDaemon(True)
        self.duinst[ref].start()
        #self.duinst[ref].join()
        return ref    
    
    def fetchFeedUpdates(self,thr):
        '''Override feed updates adding an additional updater call fetching warning text per address'''
        res,_ = super(DataSyncResolutionFeed,self).fetchFeedUpdates(thr)
        if ENABLE_RESOLUTION_FEED_WARNINGS:
            for adr in res:
                cid = adr.getChangeId()
                adr.setWarnings(self.updateWarnings(cid))
        return res,FIRST_PAGE
    
    def updateWarnings(self,cid):
        '''Method to explicitly fetch warning message for a particular cid, blocks till return'''
        ref = 'Warn.{0:%y%m%d.%H%M%S}'.format(DT.now())
        params = (ref,self.conf,self.afactory)
        #reuse response queue
        duwarn = DataUpdaterWarning(params,self.respq)
        duwarn.setup(self.ft,cid)
        duwarn.setDaemon(True)
        duwarn.start()
        #run this as a single blocking process otherwise it will overwhelm the api
        duwarn.join()
        warn = self.respq.get()
        #if err: aimslog.info('Received errors "{}" for cid={}'.format(err,cid))
        if warn: aimslog.info('Received {} warnings for cid={}'.format(len(warn),cid))
        return warn
  
        
        
    

    
        
        