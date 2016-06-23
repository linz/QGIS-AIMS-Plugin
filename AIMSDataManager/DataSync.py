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

import os
import sys
import re
import logging
import time
import threading
import Queue

from Observable import Observable
from DataUpdater import DataUpdater,DataUpdaterAction,DataUpdaterApproval,DataUpdaterGroupAction,DataUpdaterGroupApproval,DataUpdaterUserAction
from AimsApi import AimsApi 
from AimsLogging import Logger
from AimsUtility import ActionType,ApprovalType,GroupActionType,GroupApprovalType,UserActionType,FeedType,FeatureType,FeedRef,LogWrap,FEEDS
from AimsUtility import AimsException
from Const import MAX_FEATURE_COUNT,THREAD_JOIN_TIMEOUT,PAGE_LIMIT,POOL_PAGE_CHECK_DELAY,THREAD_KEEPALIVE,FIRST_PAGE,LAST_PAGE_GUESS,ENABLE_ENTITY_EVALUATION,NULL_PAGE_VALUE as NPV
from FeatureFactory import FeatureFactory
aimslog = None

FPATH = os.path.join('..',os.path.dirname(__file__)) #base of local datastorage
#FNAME = 'data_hash'

#PAGES_INIT = 10
#PAGES_PERIOCDIC = 3
#FEED_REFRESH_DELAY = 10

pool_lock = threading.Lock()

class IncorrectlyConfiguredRequestClientException(AimsException):pass


class DataRequestChannel(Observable):
    '''Observable class providing request/response channel for user initiated actions '''
    
    def __init__(self,client):
        '''Initialises a new DRC using an instance of a feeds DataSync to communincate with contained feed functions
        @param client: DataSync object used as proxy to communicate with API
        @type client: DataSyncFeeds
        '''
        super(DataRequestChannel,self).__init__()
        if hasattr(client,'etft') and hasattr(client,'inq') and hasattr(client,'processInputQueue'):
            self.client = client
        else:
            raise IncorrectlyConfiguredRequestClientException('Require client with [ etft,inq,pIQ() ] attributes')
        
    def run(self):
        '''Run method using loop for thread keepalive'''
        while not self.stopped():
            aimslog.debug('DRC {} listening'.format(self.client.etft))
            time.sleep(THREAD_KEEPALIVE)
    
    def observe(self,_,*args,**kwargs):
        '''Override of observe method receiving calls from DataManager to trigger requests, on client
        @param _: Discarded observable.
        @param *args: Wrapped args
        @param **kwargs: Wrapped kwargs
        '''
        if self.stopped(): 
            aimslog.warn('DM attempt to call stopped DRC listener {}'.format(self.getName()))
            return
        aimslog.info('Processing request {}'.format(args[0]))
        if self.client.etft==args[0] and not self.client.inq.empty():
            changelist = self.client.inq.get()    
            aimslog.info('DRC {} - found {} items in queue'.format(self.client.etft,len(changelist)))
            self.client.processInputQueue(changelist)

    
class DataSync(Observable):
    '''Background thread triggering periodic data updates and synchronising update requests from DM.'''
    
    global aimslog
    aimslog = Logger.setup()
    
    duinst = {}
    
    #hash to compare latest fetched data
    #from DataManager import FEEDS
    #data_hash = {dh:0 for dh in DataManager.FEEDS}
    
    sw,ne = None,None
    
    def __init__(self,params,queues):
        '''Initialise new DataSync object splitting out config parameters
        @param params: List of configuration parameters
        @type params: List<?>
        @param queues: List of IOR queues
        @type queues: Dict<String,Queue.Queue>        
        '''
        #from DataManager import FEEDS
        super(DataSync,self).__init__()
        #thread reference, ft to AD/CF/RF, config info
        self.start_time = time.time()
        self.updater_running = False
        self.ref,self.etft,self.ftracker,self.conf = params
        self.data_hash = {dh:0 for dh in FEEDS.values()}
        self.factory = FeatureFactory.getInstance(self.etft)
        self.updater = DataUpdater.getInstance(self.etft) # unevaluated class
        self.inq = queues['in']
        self.outq = queues['out']
        self.respq = queues['resp']
        #self._stop = threading.Event()
        
    def setup(self,sw=None,ne=None):
        '''Parameter setup for coordinate feature requests.
        @param sw: South-West corner, coordinate value pair (optional)
        @type sw: List<Double>{2}
        @param ne: North-East corner, coordinate value pair (optional)
        @type ne: List<Double>{2}
        '''
        self.sw,self.ne = sw,ne

    def run(self):
        '''Continual loop running periodic feed fetch updates'''
        while not self.stopped():
            if not self.updater_running: self.fetchFeedUpdates(self.ftracker['threads'])
            time.sleep(self.ftracker['interval'])
            
    #@override
    def stop(self):
        '''Thread stop override to also stop subordinate threads'''
        #brutal stop on du threads
        for du in self.duinst.values():
            du.stop()
        self._stop.set()
    
    def close(self):
        '''Alias of stop'''
        self.stop()
        #self.inq.task_done()
        #self.outq.task_done()
        
    def observe(self,_,*args, **kwargs):
        '''Overridden observe method calling thread management function
        @params _: Discarded observable
        @param *args: Wrapped args, where we only use the first arg as the managePage ref value
        @param **kwargs: Wrapped kwargs, discarded
        '''
        if not self.stopped():
            self._managePage(args[0])
        
    def _managePage(self,ref):
        '''Thread management function called when a periodic thread ends, posting new data and starting a new thread in pool if required
        @param ref: Unique reference string
        @type ref: String
        '''
        #print '{}{} finished'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
        aimslog.info('Extracting queue for DU pool {}'.format(ref))
        #print [r['ref'] for r in self.pool]
        #print 'extracting queue for DU pool {}'.format(ref)
        r = None
        with pool_lock:
            aimslog.info('{} complete'.format(ref))
            #print 'POOLSTATE',self.pool  
            #print 'POOLREMOVE',ref
            r = [x for x in self.pool if x['ref']==ref][0] 
            alist = self.duinst[ref].queue.get()
            acount = len(alist)
            self.newaddr += alist
            nextpage = max([r2['page'] for r2 in self.pool])+1
            #del self.duinst[ref]#ERROR? this cant be good, removing the DU during its own call to notify
            aimslog.debug('PAGE TIME {} {}s'.format(ref,time.time()-r['time']))
            #print 'POOLTIME {} {}'.format(ref,time.time()-r['time'])
            self.pool.remove(r)
            #if N>0 features return, spawn another thread
            if acount<MAX_FEATURE_COUNT:
                #non-full page returned, must be the last one
                self.exhausted = r['page']
            if acount>0:
                #features returned, not zero and not less than max so get another
                self.lastpage = max(r['page'],self.lastpage)
                if nextpage<self.exhausted:
                    ref = self._monitorPage(nextpage)
                    self.pool.append({'page':nextpage,'ref':ref,'time':time.time()})
                    #print 'POOLADD 2',ref
            else:
                pass
                #print 'No addresses found in page {}{}'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
            
        if len(self.pool)==0:
            self.syncFeeds(self.newaddr)#syncfeeds does notify DM
            self.managePage((None,self.lastpage))
            aimslog.debug('FULL TIME {} took {}s'.format(ref,time.time()-self.start_time))
            self.updater_running = False
            #print 'POOLCLOSE',ref,time.strftime('%Y-%M-%d %H:%m:%S')


    #--------------------------------------------------------------------------            

    #@LogWrap.timediff
    def fetchFeedUpdates(self,thr,lastpage=FIRST_PAGE):
        '''Main feed updater method
        @param thr: Number of updater threads to spawn into pool, this can be negative to count back from a lastpage value
        @type thr; Integer
        @param lastpage: Initial page number for feed requests
        @type lastpage: Integer
        '''
        self.updater_running = True
        self.exhausted = PAGE_LIMIT
        self.lastpage = lastpage
        self.newaddr = []
        #print 'LP {} {}->{}'.format(FeedType.reverse[self.ft][:2].capitalize(),lastpage,lastpage+thr)
        with pool_lock: self.pool = self._buildPool(lastpage,thr)

    def _buildPool(self,lastpage,thr):
        '''Builds a pool based on page spec provided, accepts negative thresholds for backfill requests
        @param thr: Number of updater threads to spawn into pool, this can be negative to count back from a lastpage value
        @type thr; Integer
        @param lastpage: Initial page number for feed requests
        @type lastpage: Integer
        '''
        span = range(min(lastpage,lastpage+thr),max(lastpage,lastpage+thr))
        return [{'page':pno,'ref':self._monitorPage(pno),'time':time.time()} for pno in span]
    
    def _monitorPage(self,pno):
        '''Initialise and store a DataUpdater instance for a single page request
        @param pno: Page number to build DataUpdater request from
        @type pno: Integer
        @return: DataUpdater reference value
        '''
        ref = 'FP.{0}.Page{1}.{2:%y%m%d.%H%M%S}.p{3}'.format(self.etft,pno,DT.now(),pno)
        aimslog.info('init DU {}'.format(ref))
        self.duinst[ref] = self._fetchPage(ref,pno)
        self.duinst[ref].register(self)
        self.duinst[ref].start()
        return ref    
    
    def _fetchPage(self,ref,pno):
        '''Build DataUpdate instance          
        @param ref: Unique reference string
        @type ref: String      
        @param pno: Page number to build DataUpdater request from
        @type pno: Integer
        @return: DataUpdater
        '''   
        params = (ref,self.conf,self.factory)
        adrq = Queue.Queue()
        pager = self.updater(params,adrq)
        #address/feature requests called with bbox parameters
        if self.etft==FEEDS['AF']: pager.setup(self.etft,self.sw,self.ne,pno)
        else: pager.setup(self.etft,None,None,pno)
        pager.setName(ref)
        pager.setDaemon(True)
        return pager

    #NOTE. To override the behaviour, return feed once full, override this method RLock
    def syncFeeds(self,new_addresses):
        '''Checks if supplied addresses are different from a saved existing set and return in the out queue, with notification
        @param new_addresses: List of all fetched pages from a full feed request, spanning all pages
        @type new_addresses: List<Feature>
        '''
        #new_hash = hash(frozenset(new_addresses))
        new_hash = hash(frozenset([na.getHash() for na in new_addresses]))
        if self.data_hash[self.etft] != new_hash:
            #print '>>> Changes in {} hash\n{}\n{}'.format(self.etft,self.data_hash[self.etft],new_hash)
            self.data_hash[self.etft] = new_hash
            #with sync_lock:
            self.outq.put(new_addresses)
            self.outq.task_done()
            self.notify(self.etft)

    #--------------------------------------------------------------------------
    
    def returnResp(self,resp):
        '''I{DEPRECATED} Function to put response objects in DataSync response queue
        @param resp: Response object, 
        @type resp: Feature
        '''
        aimslog.info('RESP.{}'.format(resp))
        self.respq.put(resp)
    
    #null method for features since page count not saved
    def managePage(self,p):pass


class DataSyncFeatures(DataSync):
    '''DataSync subclass for the Features feed'''
    
    #ft = FeedType.FEATURES
    
    def __init__(self,params,queues):
        '''Initialisation for DataSync Features feed reader
        @param params: List of configuration parameters
        @type params: List<?>
        @param queues: List of IOR queues
        @type queues: Dict<String,Queue.Queue>
        '''
        super(DataSyncFeatures,self).__init__(params,queues)
        #self.ftracker = {'page':[1,1],'index':1,'threads':2,'interval':30}

        
class DataSyncFeeds(DataSync): 
    '''DataSync subclass for the Change and Resolution feeds'''
    
    parameters = {FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED)):{'atype':ActionType,'action':DataUpdaterAction},
                  FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)):{'atype':ApprovalType,'action':DataUpdaterApproval},
                  FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)):{'atype':GroupActionType,'action':DataUpdaterGroupAction},
                  FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED)):{'atype':GroupApprovalType,'action':DataUpdaterGroupApproval}
                  #FeedRef((FeatureType.USERS,FeedType.ADMIN)):{'atype':UserActionType,'action':DataUpdaterUserAction}
                  }
    
    def __init__(self,params,queues):
        '''Create an additional DRC thread to watch the feed input queue
        @param params: List of configuration parameters
        @type params: List<?>
        @param queues: List of IOR queues
        @type queues: Dict<String,Queue.Queue>   
        '''
        super(DataSyncFeeds,self).__init__(params,queues)
        self.drc = DataSyncFeeds.setupDRC(self,params[0])
        
    @staticmethod
    def setupDRC(client,p0):
        '''Static method to set up a request listener containing a instance of a matching DataSyncFeeds client
        @param client: DataSync object used as proxy to communicate with API
        @type client: DataSyncFeeds
        @param p0: The zero indexed parameter containing the client ref string
        @type p0: String
        @return: DataRequestChannel
        '''
        drc = DataRequestChannel(client)
        drc.setName('DRC.{}'.format(p0))
        drc.setDaemon(True)
        return drc
        
    def run(self):
        '''Start the DRC thread and then start self (doing periodic updates) using the super run'''
        self.drc.start()
        super(DataSyncFeeds,self).run()
    
    def stop(self):
        '''Thread stop also stops related DRC thread'''
        self.drc.stop()
        super(DataSyncFeeds,self).stop()

    def stopped(self):
        return super(DataSyncFeeds,self).stopped() and self.drc.stopped() 
    
    
    #Processes the input queue sending address changes to the API
    #@LogWrap.timediff
    def processInputQueue(self,changelist):
        '''Take the requests from an input queue and split out individual address objects for DU processing
        @param changelist: Dictionary of address lists taken from the input queue
        @type changelist: Dictionary<FeedRef,List<Feature>>  
        '''
        #{ADD:addr_1,RETIRE:adr_2...
        for at in changelist:
            #self.outq.put(act[addr](changelist[addr]))
            for feature in changelist[at]:
                duref = self.processFeature(at,feature)
                aimslog.info('{} thread started'.format(str(duref)))
                
    def processFeature(self,at,feature): 
        '''Individual feature request processor.
        @param at: Address/Group Action/Approval type indicator
        @type at: Integer 
        @param feature: Feature being acted upon/approved
        @type feature: Feature
        @return: Reference value for DataUpdater thread
        '''
        at2 = self.parameters[self.etft]['atype'].reverse[at][:3].capitalize()      
        ref = 'PR.{0}.{1:%y%m%d.%H%M%S}'.format(at2,DT.now())
        params = (ref,self.conf,self.factory)
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}
        self.duinst[ref] = self.parameters[self.etft]['action'](params,self.respq)
        self.duinst[ref].setup(self.etft,at,feature,None)
        print 'PROCESS FEAT',self.etft,ref
        self.duinst[ref].setName(ref)
        self.duinst[ref].setDaemon(True)
        self.duinst[ref].start()
        #self.duinst[ref].join()
        return ref
    
    def managePage(self,p):
        '''Saves page numbers back to tracker array
        @param p: first and last page numbers
        @type p: List<Integer>{2}
        '''
        if p[0]: self.ftracker['page'][0] = p[0]
        if p[1]: self.ftracker['page'][1] = p[1]
        
class DataSyncAdmin(DataSyncFeeds):
    '''Admin DS class that doesn't update and is only used as a admin client request channel'''
    
    parameters = {FeedRef((FeatureType.USERS,FeedType.ADMIN)):{'atype':UserActionType,'action':DataUpdaterUserAction}}
        
    def __init__(self,params,queues):
        '''Admin feed initialiser
        @param params: List of configuration parameters
        @type params: List<?>
        @param queues: List of IOR queues
        @type queues: Dict<String,Queue.Queue>
        '''
        super(DataSyncAdmin,self).__init__(params,queues)
        #self.drc = DataSyncAdmin.setupDRC(self,params[0])
        
    def run(self):
        '''Admin feed run but with no requirement to read admin feed only starts the DRC'''
        self.drc.start()
        
  
        
        
    

    
        
        