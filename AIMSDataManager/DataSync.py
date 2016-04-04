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

from DataUpdater import DataUpdater,DataUpdaterAction,DataUpdaterApproval
from AimsApi import AimsApi 
from AimsLogging import Logger
from AimsUtility import ActionType,ApprovalType,GroupActionType,GroupApprovalType,FeedType,FeatureType,FeedRef,LogWrap,FEEDS
from Const import MAX_FEATURE_COUNT,THREAD_JOIN_TIMEOUT,PAGE_LIMIT,POOL_PAGE_CHECK_DELAY,QUEUE_CHECK_DELAY,FIRST_PAGE,LAST_PAGE_GUESS,ENABLE_ENTITY_EVALUATION,NULL_PAGE_VALUE as NPV
from FeatureFactory import FeatureFactory
aimslog = None

FPATH = os.path.join('..',os.path.dirname(__file__)) #base of local datastorage
#FNAME = 'data_hash'

#PAGES_INIT = 10
#PAGES_PERIOCDIC = 3
#FEED_REFRESH_DELAY = 10

notify_lock = threading.RLock()
sync_lock = threading.RLock()

class DataRequestChannel(threading.Thread):    
    '''Request response channel for user initiated actions eg add decline retire etc. One for each feed class, client, whose pIQ method is accessed'''
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
                
                aimslog.info('DRC {} - found {} items in queue'.format(self.client.etft,len(changelist)))
                self.client.processInputQueue(changelist)
                
            time.sleep(QUEUE_CHECK_DELAY)
            
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
class Observable(threading.Thread):    
    def __init__(self):
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)
    
    def notify(self, *args, **kwargs):
        for observer in self._observers:
            with notify_lock:
                observer.notify(self, *args, **kwargs)

    
class DataSync(Observable):
    '''Background thread triggering periodic data updates and synchronising update requests from DM.  
    '''
    
    global aimslog
    aimslog = Logger.setup()
    
    duinst = {}
    
    #hash to compare latest fetched data
    #from DataManager import FEEDS
    #data_hash = {dh:0 for dh in DataManager.FEEDS}
    
    sw,ne = None,None
    
    def __init__(self,params,queues):
        from DataManager import FEEDS
        super(DataSync,self).__init__()
        threading.Thread.__init__(self)
        #thread reference, ft to AD/CF/RF, config info
        self.ref,self.etft,self.ftracker,self.conf = params
        self.data_hash = {dh:0 for dh in FEEDS.values()}
        self.afactory = FeatureFactory.getInstance(self.etft)
        self.updater = DataUpdater.getInstance(self.etft)
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
            updates = self.fetchFeedUpdates(self.ftracker['threads'])
            if updates != None: 
                self.syncFeeds(updates)
                aimslog.debug('ETFT {} sleeping {} with size(Qin)={}'.format(self.etft,self.ftracker['interval'],self.inq.qsize())) 
                time.sleep(self.ftracker['interval'])
            else:
                #if updates are none, stop has been called
                return
            
    #start = int(time.time())  
    #now = int(time.time())   
    #if (now-start) % self.ftracker['interval']:pass     
    def fetchFeedUpdates(self,val): pass   
    
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def close(self):
        self.stop()
        #self.inq.task_done()
        #self.outq.task_done()

    #--------------------------------------------------------------------------            

    @LogWrap.timediff
    def _fetchFeedUpdates(self,thr,lastpage=FIRST_PAGE):
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
                aimslog.debug('### Page {} pool={}'.format(self.etft, r['page'],[p['page'] for p in pool])) 
                #terminate the pooled objects on stop signal
                if self.stopped():
                    self.stopSubs(pool)
                    return None,None
                #    print 'halt' 
                if self.duinst.has_key(r['ref']) and not self.duinst[r['ref']].isAlive(): 
                    #print '{}{} finished'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
                    alist = self.duinst[r['ref']].queue.get()
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
            try:
                self.duinst[r['ref']].stop()
                self.duinst[r['ref']].join(THREAD_JOIN_TIMEOUT)
                if self.duinst[r['ref']].isAlive():aimslog.warn('Thread timeout {}'.format(r['ref']))
                del self.duinst[r['ref']]
            except Exception as e:
                aimslog.warn('Error stopping {}. {} '.format(r['ref'],e))
            pool.remove(r)

            
    def fetchPage(self,p):
        '''Regular page fetch, periodic or demand'''   
        ref = 'FP.{0}.Page{1}.{2:%y%m%d.%H%M%S}.p{3}'.format(self.etft,p,DT.now(),p)
        params = (ref,self.conf,self.afactory)
        adrq = Queue.Queue()
        self.duinst[ref] = self.updater(params,adrq)
        if self.etft==FEEDS['AF']: self.duinst[ref].setup(self.etft,self.sw,self.ne,p)
        else: self.duinst[ref].setup(self.etft,None,None,p)
        self.duinst[ref].setName(ref)
        self.duinst[ref].setDaemon(True)
        self.duinst[ref].start()
        return ref
        #self.duinst[ref].join()
        #return adrq.get()

    #NOTE. To override the behaviour, return feed once full, override this method RLock
    def syncFeeds(self,new_addresses):
        '''check if the addresses are diferent from existing set and return in the out queue'''
        new_hash = hash(frozenset(new_addresses))
        if self.data_hash[self.etft] != new_hash:
            self.data_hash[self.etft] = new_hash
            #with sync_lock:
            self.outq.put(new_addresses)
            self.outq.task_done()
        self.notify(self.etft)

    #--------------------------------------------------------------------------
    
    def returnResp(self,resp):
        aimslog.info('RESP.{}'.format(resp))
        self.respq.put(resp)


class DataSyncFeatures(DataSync):
    
    #ft = FeedType.FEATURES
    
    def __init__(self,params,queues):
        super(DataSyncFeatures,self).__init__(params,queues)
        #self.ftracker = {'page':[1,1],'index':1,'threads':2,'interval':30}    
        
    def fetchFeedUpdates(self,thr):
        res,_ = super(DataSyncFeatures,self)._fetchFeedUpdates(thr)
        return res


class DataSyncFeeds(DataSync): 
    
    parameters = {FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED)):{'atype':ActionType,'action':DataUpdaterAction},
                  FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)):{'atype':ApprovalType,'action':DataUpdaterApproval},
                  FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)):{'atype':GroupActionType,'action':DataUpdaterAction},
                  FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED)):{'atype':GroupApprovalType,'action':DataUpdaterApproval}
                  }
    
    def __init__(self,params,queues):
        '''Create an additional DRC thread to watch the feed input queue'''
        super(DataSyncFeeds,self).__init__(params,queues)
        self.drc = DataRequestChannel(self)
        self.drc.setName('DRC.{}'.format(params[0]))
        self.drc.setDaemon(True)
        
    def run(self):
        '''Start the DRC thread and then start self (doing periodic updates) using the super run'''
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
        res,lp = super(DataSyncFeeds,self)._fetchFeedUpdates(thr,lp)
        #get just one backfill per fFU  #[for i in range(5):#do a bunch of backfills?]
        if bp>FIRST_PAGE:
            bdata,bp = self.backfillPage(bp-1)
            res += bdata
        self.managePage((bp,lp))
        return res
        
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
        at2 = self.parameters[self.etft]['atype'].reverse[at][:3].capitalize()      
        ref = 'PR.{0}.{1:%y%m%d.%H%M%S}'.format(at2,DT.now())
        params = (ref,self.conf,self.afactory)
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}
        self.duinst[ref] = self.parameters[self.etft]['action'](params,self.respq)
        self.duinst[ref].setup(self.etft,at,address)
        self.duinst[ref].setName(ref)
        self.duinst[ref].setDaemon(True)
        self.duinst[ref].start()
        #self.duinst[ref].join()
        return ref
    
    def managePage(self,p):
        if p[0]: self.ftracker['page'][0] = p[0]
        if p[1]: self.ftracker['page'][1] = p[1]
        
  
        
        
    

    
        
        