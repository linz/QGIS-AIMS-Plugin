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

import os
import sys
import Queue
import pickle
import copy
import time
import pprint
import collections
from Address import Address, AddressChange, AddressResolution,Position
from FeatureFactory import FeatureFactory
#from DataUpdater import DataUpdater
from DataSync import DataSync,DataSyncFeatures,DataSyncFeeds
from datetime import datetime as DT
from AimsUtility import FeedRef,ActionType,ApprovalType,GroupActionType,GroupApprovalType,FeatureType,FeedType,Configuration,FEEDS,FIRST
from AimsLogging import Logger
from Const import THREAD_JOIN_TIMEOUT,RES_PATH,LOCAL_ADL,SWZERO,NEZERO,NULL_PAGE_VALUE as NPV
from Observable import Observable

aimslog = None
    
    
class DataManager(Observable):
    '''Initialises maintenance thread and provides queue accessors'''

    global aimslog
    aimslog = Logger.setup()
    
  
    def __init__(self,start=FIRST,initialise=False):
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}   
        super(DataManager,self).__init__()
        if start and hasattr(start,'__iter__'): self._start = start.values()
        self.persist = Persistence(initialise)
        self.conf = Configuration().readConf()
        self._initDS()
        
    def _initDS(self):
        '''initialise the data sync queues/threads'''
        self.ioq = {etft:None for etft in FEEDS.values()}
        self.ds = {etft:None for etft in FEEDS.values()}
        self.stamp = {etft:time.time() for etft in FEEDS.values()}
        
        #init the three different feed threads
        self.dsr = {f:DataSyncFeeds for f in FIRST.values()}
        self.dsr[FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))] = DataSyncFeatures
        for etft in self._start: self._checkDS(etft)
            
    def start(self,etft):
        '''Add new thread to startup list and initialise'''
        if not etft in self._start: self._start.append(etft)
        self._checkDS(etft)
        
    #local override of observe
    def observe(self, observable, *args, **kwargs):
        '''Do some housekeeping and notify listener'''
        aimslog.info('DM Listen A[{}], K[{}] - {}'.format(args,kwargs,observable))
        args += (self._monitor(observable),)
        #chained notify/listen calls
        if hasattr(self,'registered') and self.registered: 
            self.registered.observe(observable, *args, **kwargs)
        self._check()
        
    #Second register/observer method for main calling class
    def registermain(self,reg):
        '''Register "single" class as a listener'''
        self.registered = reg if hasattr(reg, 'observe') else None
        
#     def register(self,reg):
#         '''redundant super call to catch/log registrees'''
#         super(DataManager,self).register(reg)
        
    def _checkDS(self,etft):
        '''Starts a sync thread unless its features with a zero bbox'''
        if (etft == FEEDS['AF'] and self.persist.coords['sw'] == SWZERO and self.persist.coords['ne'] == NEZERO) or int(self.persist.tracker[etft]['threads'])==0:                
            self.ds[etft] = None
        else:
            self.ds[etft] = self._spawnDS(etft,self.dsr[etft])
            self.ds[etft].register(self)         
            self.ds[etft].start()
            
        
    def _spawnDS(self,etft,feedclass): 
        ts = '{0:%y%m%d.%H%M%S}'.format(DT.now())
        params = ('DSF..{}.{ts}'.format(etft,ts=ts),etft,self.persist.tracker[etft],self.conf)
        self.ioq[etft] = {n:Queue.Queue() for n in ('in','out','resp')}
        ds = feedclass(params,self.ioq[etft])
        ds.setup(self.persist.coords['sw'],self.persist.coords['ne'])
        ds.setDaemon(True)
        ds.setName('DS{}'.format(etft))
        #ds.start()
        if etft.ft != FeedType.FEATURES: self.register(ds.drc)
        return ds    
        
    def close(self):
        '''shutdown closing/stopping ds threads and persisting data'''
        for ds in self.ds.values():
            if ds: ds.close()
        self.persist.write()
        
    def _check(self):
        '''If a DataSync thread crashes restart it'''
        for etft in self._start:
            if self._confirmstart(etft):
                aimslog.warn('DS thread {} absent, starting'.format(etft))
                #del self.ds[etft]
                self._checkDS(etft)
                
    def _confirmstart(self,etft):    
        '''simple test to determine whether thread shoule be started or not'''    
        return int(self.persist.tracker[etft]['threads'])>0 and not (self.ds.has_key(etft) and self.ds[etft] and self.ds[etft].isAlive())
    
    #Client Access
    def setbb(self,sw=None,ne=None):
        '''Resetting the bounding box triggers a complete refresh of the features address data'''
        #TODO add move-threshold to prevent small moves triggering an update
        if self.persist.coords['sw'] != sw or self.persist.coords['ne'] != ne:
            #throw out the current features addresses
            etft = FEEDS['AF']#(FeatureType.ADDRESS,FeedType.FEATURES)
            self.persist.ADL[etft] = self.persist._initADL()[etft]
            #save the new coordinates
            self.persist.coords['sw'],self.persist.coords['ne'] = sw,ne
            #kill the old features thread
            if self.ds[etft] and self.ds[etft].isAlive():
                aimslog.info('Attempting Features Thread STOP')
                self.ds[etft].stop()
                self.ds[etft].join(THREAD_JOIN_TIMEOUT)
                #TODO investigate thread non-stopping issues
                if self.ds[etft].isAlive(): aimslog.warn('SetBB Features. ! Thread JOIN timeout')
            del self.ds[etft]
            #reinitialise a new features DataSync
            #self._initFeedDSChecker(etft)
            self.start(etft)
    
    #@Deprecated     
    def restart(self,etft):
        '''Restart a specific thread type'''
        #NB UI feature request. 
        aimslog.warn('WARNING {} Thread Restart requested'.format(etft))
        if self.ds.has_key(etft) and self.ds[etft] and self.ds[etft].isAlive():
            self.ds[etft].stop() 
            self.ds[etft].join(THREAD_JOIN_TIMEOUT)
            if self.ds[etft].isAlive(): aimslog.warn('{} ! Thread JOIN timeout'.format(etft))
        #del self.ds[etft]
        elif not isinstance(etft,FeedRef):
            aimslog.error('Invalid FeedRef on STOP request')
        else:
            aimslog.warn('Requested thread {} does not exist')
        self._check()
        
    def pull(self):
        '''Return copy of the ADL. Speedup, insist on deepcopy at address level'''
        return self.persist.ADL    
        
    def _monitor(self,etft):
        '''for each feed check the out queue and put any new items into the ADL'''
        #for etft in self.ds:#FeedType.reverse:
        if self.ds[etft]:
            while not self.ioq[etft]['out'].empty():
                #because the queue isnt populated till all pages are loaded we can just swap out the ADL
                self.persist.ADL[etft] = self.ioq[etft]['out'].get()
                self.stamp[etft] = time.time()

        #self.persist.write()
        return self.persist.ADL[etft]
    
    def response(self,etft=FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))):
        '''Returns any features lurking in the response queue'''
        resp = ()
        #while self.ioq.has_key((et,ft)) and not self.ioq[(et,ft)]['resp'].empty():
        while etft in FEEDS.values() and not self.ioq[etft]['resp'].empty():
            resp += (self.ioq[etft]['resp'].get(),)
        return resp
        
      
    def _populateAddress(self,feature):
        '''Fill in any required+missing fields if a default value is known (in this case the configured user)'''
        if not hasattr(feature,'_workflow_sourceUser') or not feature.getSourceUser(): feature.setSourceUser(self.conf['user'])
        if not hasattr(feature,'_workflow_sourceOrganisation') or not feature.getSourceOrganisation(): feature.setSourceOrganisation(self.conf['org'])
        return feature    
    
    def _populateGroup(self,feature):
        '''Fill in any required+missing fields if a default value is known (in this case the configured user)'''
        if not hasattr(feature,'_workflow_sourceUser') or not feature.getSourceUser(): feature.setSourceUser(self.conf['user'])
        if not hasattr(feature,'_submitterUserName') or not feature.getSubmitterUserName(): feature.setSubmitterUserName(self.conf['user'])
        return feature
    
    #convenience methods 
    #---------------------------- 
    def addAddress(self,address,reqid=None):
        self._addressAction(address,ActionType.ADD,reqid)      
    
    def retireAddress(self,address,reqid=None):
        self._addressAction(address,ActionType.RETIRE,reqid)
    
    def updateAddress(self,address,reqid=None):
        self._addressAction(address,ActionType.UPDATE,reqid)
        
    def _addressAction(self,address,at,reqid=None):
        if reqid: address.setRequestId(reqid)
        self._populateAddress(address).setChangeType(ActionType.reverse[at].title())
        self._queueAction(FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED)), at, address)
    #----------------------------
    def acceptAddress(self,address,reqid=None):
        self._addressApprove(address,ApprovalType.ACCEPT,reqid)    

    def declineAddress(self,address,reqid=None):
        self._addressApprove(address,ApprovalType.DECLINE,reqid)
    
    def repairAddress(self,address,reqid=None):
        self._addressApprove(address,ApprovalType.UPDATE,reqid) 
        
    def _addressApprove(self,address,at,reqid=None):
        if reqid: address.setRequestId(reqid)
        address.setQueueStatus(ApprovalType.LABEL[at].title())
        self._queueAction(FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)), at, address)
        
    #============================
    def acceptGroup(self,group,reqid=None):
        self._groupApprove(group, GroupApprovalType.ACCEPT, reqid)
        
    def declineGroup(self,group,reqid=None):
        self._groupApprove(group, GroupApprovalType.DECLINE, reqid) 
        
    def repairGroup(self,group,reqid=None):
        self._groupApprove(group, GroupApprovalType.UPDATE, reqid)   
        
    def _groupApprove(self,group,gat,reqid=None):
        if reqid: group.setRequestId(reqid)
        group.setQueueStatus(GroupApprovalType.LABEL[gat].title())
        self._queueAction(FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED)),gat,group)
          
    #----------------------------
    def replaceGroup(self,group,reqid=None):
        self._groupAction(group, GroupActionType.REPLACE, reqid)       
        
    def updateGroup(self,group,reqid=None):
        self._groupAction(group, GroupActionType.UPDATE, reqid)       
        
    def submitGroup(self,group,reqid=None):
        self._groupAction(group, GroupActionType.SUBMIT, reqid)    
    
    def closeGroup(self,group,reqid=None):
        self._groupAction(group, GroupActionType.CLOSE, reqid)
        
    def addGroup(self,group,reqid=None):
        self._groupAction(group, GroupActionType.ADD, reqid)
             
    def removeGroup(self,group,reqid=None):
        self._groupAction(group, GroupActionType.REMOVE, reqid)        
  
    def _groupAction(self,group,gat,reqid=None):        
        if reqid: group.setRequestId(reqid)
        self._populateGroup(group).setChangeType(GroupActionType.reverse[gat].title())
        self._queueAction(FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)),gat,group)
    
    #----------------------------
    
    def _queueAction(self,feedref,atype,aorg):
        '''Queue and notify'''
        self.ioq[feedref]['in'].put({atype:(aorg,)})
        self.notify(feedref)
    
    #----------------------------
    
    #convenience method for address casting
    def castTo(self,requiredtype,address):
        if not requiredtype in FeedType.reverse.keys(): raise Exception('unknown feed/address type')
        return FeatureFactory.getInstance(FeedRef((FeatureType.ADDRESS,requiredtype))).cast(address)
    
    #----------------------------
    #CM
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type=None, exc_val=None, exc_tb=None):
        return self.close()

        

class Persistence():
    '''static class for persisting config/long-lived information'''
    
    tracker = {}
    coords = {'sw':SWZERO,'ne':NEZERO}
    ADL = None
    RP = os.path.join(os.path.dirname(__file__),'..',RES_PATH,LOCAL_ADL)
    
    def __init__(self,initialise=False):
        '''read or setup the tracked data'''
        if initialise or not self.read():
            self.ADL = self._initADL() 
            #default tracker, gets overwrittens
            #page = (lowest page fetched, highest page number fetched)
            self.tracker[FEEDS['AF']] = {'page':[1,1],    'index':1,'threads':2,'interval':30}    
            self.tracker[FEEDS['AC']] = {'page':[NPV,NPV],'index':1,'threads':1,'interval':125000}  
            self.tracker[FEEDS['AR']] = {'page':[1,1],    'index':1,'threads':1,'interval':10} 
            self.tracker[FEEDS['GC']] = {'page':[1,1],    'index':1,'threads':1,'interval':130000}  
            self.tracker[FEEDS['GR']] = {'page':[1,1],    'index':1,'threads':1,'interval':55}             
            
            self.write() 
    
    def _initADL(self):
        '''Read ADL from serial and update from API'''
        return {f:[] for f in FEEDS.values()}
    
    #Disk Access
    #TODO OS agnostic path sep
    def read(self,localds=RP):
        '''unpickle local store'''  
        try:
            archive = pickle.load(open(localds,'rb'))
            #self.tracker,self.coords,self.ADL = archive
            self.tracker,self.ADL = archive
        except:
            return False
        return True
    
    def write(self, localds=RP):
        try:
            #archive = [self.tracker,self.coords,self.ADL]
            archive = [self.tracker,self.ADL]
            pickle.dump(archive, open(localds,'wb'))
        except:
            return False
        return True


refsnap = None

