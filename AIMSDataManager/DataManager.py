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

import Queue
import pickle
import copy
import time
import pprint
import collections
from Address import Address, AddressChange, AddressResolution,Position
from FeatureFactory import FeatureFactory
#from DataUpdater import DataUpdater
from DataSync import DataSync,DataSyncFeatures,DataSyncFeeds#,DataSyncChangeFeed,DataSyncResolutionFeed,DataSyncGroupChangeFeed,DataSyncGroupResolutionFeed
from datetime import datetime as DT
from AimsUtility import FeedRef,ActionType,ApprovalType,FeatureType,FeedType,Configuration,FEEDS,FIRST
from AimsUtility import THREAD_JOIN_TIMEOUT,LOCALADL,SWZERO,NEZERO,NULL_PAGE_VALUE as NPV
from AimsLogging import Logger


aimslog = None
    
class DataManager(object):
    '''Initialises maintenance thread and provides queue accessors'''
    # ADL - Address-Data List
    # {'features':{adr1_id:Address1, adr2_id:Address2...},'changefeed':{},'resolutionfeed':{}} 
    #ADL = {FeedType.FEATURES:{},FeedType.CHANGEFEED:{},FeedType.RESOLUTIONFEED:{}} 
    # conf = feat:(count,index),cfeed:(count,page,index),rfeed:(count,page,index)
    #conf = {}
    global aimslog
    aimslog = Logger.setup()
    
  
    def __init__(self,start=FIRST,initialise=False):
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}   
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
#         self.dsr = {
#             (FeatureType.ADDRESS,FeedType.FEATURES):DataSyncFeatures,
#             (FeatureType.ADDRESS,FeedType.CHANGEFEED):DataSyncChangeFeed,
#             (FeatureType.ADDRESS,FeedType.RESOLUTIONFEED):DataSyncResolutionFeed,
#             (FeatureType.GROUPS,FeedType.CHANGEFEED):DataSyncGroupChangeFeed,
#             (FeatureType.GROUPS,FeedType.RESOLUTIONFEED):DataSyncGroupResolutionFeed
#         }
        for ref in self.dsr:
            if ref in self._start: self.start(ref)
            
    def start(self,etft):
        #self._start.update((etft,))
        self._initFeedDSChecker(etft)
        
    def notify(self, observable, *args, **kwargs):
        '''Do some housekeeping and notify listener'''
        aimslog.info('Notify A[{}], K[{}] - {}'.format(args,kwargs,observable))
        args += (self._monitor(args[0]),)
        if hasattr(self,'reg') and self.reg: self.reg.notify(observable, *args, **kwargs)
        self._check()
        
    def register(self,reg):
        '''Register single class as a listener'''
        self.reg = reg if hasattr(reg, 'notify') else None        
        
    def _initFeedDSChecker(self,etft):
        '''Starts a sync thread unless its features with a zero bbox'''
        if etft == FEEDS['AF'] and self.persist.coords['sw'] == SWZERO and self.persist.coords['ne'] == NEZERO:                
            self.ds[etft] = None
        else:
            self.ds[etft] = self._initFeedDS(etft,self.dsr[etft])
            self.ds[etft].register(self)            
            self.ds[etft].start()
            
        
    def _initFeedDS(self,etft,feedclass): 
        ts = '{0:%y%m%d.%H%M%S}'.format(DT.now())
        params = ('DSF..{}.{ts}'.format(etft,ts=ts),etft,self.persist.tracker[etft],self.conf)
        self.ioq[etft] = {n:Queue.Queue() for n in ('in','out','resp')}
        ds = feedclass(params,self.ioq[etft])
        ds.setup(self.persist.coords['sw'],self.persist.coords['ne'])
        ds.setDaemon(True)
        ds.setName('DS{}'.format(etft))
        #ds.start()
        return ds    
        
    def close(self):
        '''shutdown closing/stopping ds threads and persisting data'''
        for ds in self.ds.values():
            if ds: ds.close()
        self.persist.write()
        
    def _check(self):
        '''If a DataSync thread crashes restart it'''
        for etft in self._start:
            if not self.ds.has_key(etft) or not self.ds[etft] or not self.ds[etft].isAlive():
                aimslog.warn('DS thread {} terminated, restarting'.format(etft))
                #del self.ds[etft]
                self._initFeedDSChecker(etft)
            
        
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
                if self.ds[etft].isAlive(): aimslog.warn('SetBB Features Thread JOIN timeout')
            del self.ds[etft]
            #reinitialise a new features DataSync
            self._initFeedDSChecker(etft)
    
    #@Deprecated     
    def restart(self,etft):
        '''Restart a specific thread type'''
        #NB UI feature request. 
        aimslog.warn('WARNING {} Thread Restart requested'.format(etft))
        if self.ds.has_key(etft) and self.ds[etft]:#.isAlive():
            self.ds[etft].stop() 
            self.ds[etft].join(THREAD_JOIN_TIMEOUT)
            if self.ds[etft].isAlive(): aimslog.warn('{} Thread JOIN timeout'.format(etft))
        #del self.ds[etft]
        self._check()
        
    #Push and Pull relate to features feed actions
    def push(self,newds):
        pass
        #return self._scan(newds)
        
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
    
    def response(self,et=FeatureType.ADDRESS,ft=FeedType.RESOLUTIONFEED):
        '''Returns any features lurking in the response queue'''
        resp = ()
        #while self.ioq.has_key((et,ft)) and not self.ioq[(et,ft)]['resp'].empty():
        while (et,ft) in FEEDS and not self.ioq[(et,ft)]['resp'].empty():
            resp += (self.ioq[(et,ft)]['resp'].get(),)
        return resp
        
      
    def _populate(self,entity):
        '''Fill in any required+missing fields if a default value is known (in this case the configured user)'''
        if not hasattr(entity,'_workflow_sourceUser') or not entity.getSourceUser(): entity.setSourceUser(self.conf['user'])
        return entity
    
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
        self._populate(address).setChangeType(ActionType.reverse[at].title())
        self.ioq[FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))]['in'].put({at:(address,)})   
        
    #----------------------------
    def acceptAddress(self,address,reqid=None):
        self._addressApprove(addrss,ApprovalType.ACCEPT,reqid)    

    def declineAddress(self,address,reqid=None):
        self._addressApprove(addrss,ApprovalType.DECLINE,reqid)
    
    def repairAddress(self,address,reqid=None):
        self._addressApprove(addrss,ApprovalType.UPDATE,reqid) 
        
    def _addressApprove(self,address,at,reqid=None):
        if reqid: address.setRequestId(reqid)
        address.setQueueStatus(ApprovalType.LABEL[at].title())
        self.ioq[FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))]['in'].put({at:(address,)})
        
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
        self.ioq[FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED))]['in'].put({gat:(address,)}) 
         
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
        #self._populate(group).setChangeType(GroupActionType.reverse[gat].title())
        self.setChangeType(GroupActionType.reverse[gat].title())
        self.ioq[FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED))]['in'].put({gat:(address,)})   
        
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
    
    def __init__(self,initialise=False):
        '''read or setup the tracked data'''
        if initialise or not self.read():
            self.ADL = self._initADL() 
            #default tracker, gets overwritten
            #page = (lowest page fetched, highest page number fetched)
            self.tracker[FEEDS['AF']] = {'page':[1,1],    'index':1,'threads':2,'interval':30}    
            self.tracker[FEEDS['AC']] = {'page':[NPV,NPV],'index':1,'threads':1,'interval':125}  
            self.tracker[FEEDS['AR']] = {'page':[1,1],    'index':1,'threads':1,'interval':10} 
            self.tracker[FEEDS['GC']] = {'page':[1,1],    'index':1,'threads':1,'interval':130}  
            self.tracker[FEEDS['GR']] = {'page':[1,1],    'index':1,'threads':1,'interval':55}             
            
#             self.tracker[(FeatureType.ADDRESS,FeedType.FEATURES)] =       {'page':[1,1],'index':1,'threads':2,'interval':1000}    
#             self.tracker[(FeatureType.ADDRESS,FeedType.CHANGEFEED)] =     {'page':[1,1],'index':1,'threads':1,'interval':1000}  
#             self.tracker[(FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)] = {'page':[1,1],'index':1,'threads':1,'interval':1000} 
#             self.tracker[(FeatureType.GROUPS, FeedType.CHANGEFEED)] =     {'page':[1,1],'index':1,'threads':1,'interval':1000} 
            self.write() 
    
    def _initADL(self):
        '''Read ADL from serial and update from API'''
        return {f:[] for f in FEEDS.values()}
#         return {(FeatureType.ADDRESS,FeedType.FEATURES):[],
#                 (FeatureType.ADDRESS,FeedType.CHANGEFEED):[],
#                 (FeatureType.ADDRESS,FeedType.RESOLUTIONFEED):[],
#                 (FeatureType.GROUPS,FeedType.CHANGEFEED):[]}
    
    #Disk Access
    def read(self,localds=LOCALADL):
        '''unpickle local store'''  
        try:
            archive = pickle.load(open(localds,'rb'))
            #self.tracker,self.coords,self.ADL = archive
            self.tracker,self.ADL = archive
        except:
            return False
        return True
    
    def write(self, localds=LOCALADL):
        try:
            #archive = [self.tracker,self.coords,self.ADL]
            archive = [self.tracker,self.ADL]
            pickle.dump(archive, open(localds,'wb'))
        except:
            return False
        return True


refsnap = None

class LocalTest():
    flag = False
    
    def notify(self,observable,args,kwargs):
        self.flag = True
        print observable
        print args
        print kwargs
        
    def test(self):
        global refsnap
        refsnap = {0:None,1:None,2:None}
        af = {ft:FeatureFactory.getInstance(FeedRef((FeatureType.ADDRESS,ft))) for ft in FeedType.reverse}
        af[3] = FeatureFactory.getInstance(FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)))
        #with DataManager(start=None) as dm:
        #    dm.start(FeedType.CHANGEFEED)
        with DataManager() as dm:
            dm.register(self)
            self.test1(dm,af)
            
            
    def test1(self,dm,af):
        
        #dm.persist.ADL = testdata
        #get some data
        listofaddresses = dm.pull()
        print 'addr list before feed checkin',[len(l) for l in listofaddresses.values()]
        
        #TEST RESTART
        self.testrestartCR(dm)
        
        #TEST SHIFT
        self.testfeatureshift(dm)
        
        # TEST CF
        self.testchangefeedAUR(dm,af)
        
        # TEST RF
        self.testresolutionfeedAUD(dm,af)
        
        #TEST SHIFT
        self.testfeatureshift(dm)
        
        aimslog.info('*** Resolution ADD '+str(time.clock()))   
        time.sleep(30) 
        #return
        print 'entering response mode'
        while True:
            aimslog.info('*** Main TICK '+str(time.clock()))
            self.testresp(dm)
            time.sleep(5)
            
    def testfeatureshift(self,dm):
    
        aimslog.info('*** Main SHIFT '+str(time.clock()))
        dm.setbb(sw=(174.76918,-41.28515), ne=(174.79509,-41.26491))
        time.sleep(10)
        resp = None
        while not self.flag: 
            time.sleep(5)   
        else:
            resp = self.testresp(dm) 
            
        dm.setbb(sw=(174.76928,-41.28515), ne=(174.79519,-41.26481))
        time.sleep(10)
        resp = None
        while not self.flag: 
            time.sleep(5)   
        else:
            resp = self.testresp(dm) 
            
        dm.setbb(sw=(174.76928,-41.28515), ne=(174.79529,-41.26471))
        time.sleep(10)
        resp = None
        while not self.flag: 
            time.sleep(5)   
        else:
            resp = self.testresp(dm) 
            
#     def checkrefresh(self,dm):        

#         global refsnap
#         rs2 = dm.refresh()
#         if rs2 != refsnap:
#             refsnap = rs2
#             return True
#         return False
        
    def testrestartCR(self,dm):
        time.sleep(10)
        dm.restart(FEEDS['AF'])
        time.sleep(10)
        dm.restart(FEEDS['AC'])
        time.sleep(10)
        dm.restart(FEEDS['AR'])
        
    #CHANGEFEED
    def testchangefeedAUR(self,dm,af):
        ver = 1000000
        cid = 2000000
        #pull address from features (map)
        addr_f = self.gettestdata(af[FeedType.FEATURES])
        #cast to addresschange type, to do cf ops
        addr_c = af[FeedType.CHANGEFEED].cast(addr_f)
        #addr_c.setVersion(ver)
        aimslog.info('*** Change ADD '+str(time.clock()))
        rqid1 = 1234321
        dm.addAddress(addr_c,rqid1)
        resp = None
        while True: 
            resp = self.testresp(dm,FeedType.CHANGEFEED)
            if resp: 
                err = resp[0].getErrors()
                print rqid1,resp[0].meta.requestId
                print 'e',err
                if not err:
                    cid = resp[0].getChangeId()
                break
            time.sleep(5)
        ver += 1
    
        
        aimslog.info('*** Change UPDATE '+str(time.clock()))
        rqid2 = 2345432
        addr_c.setFullAddress('Unit C, 16 Islay Street, Glenorchy')
        addr_c.setChangeId(cid)
        #addr_c.setVersion(ver)
        dm.updateAddress(addr_c,rqid2)
        resp = None
        while True: 
            resp = self.testresp(dm,FeedType.CHANGEFEED)
            if resp: 
                err = resp[0].getErrors()
                print rqid2,resp[0].meta.requestId
                print 'e',err
                if not err:
                    cid = resp[0].getChangeId()
                break
            time.sleep(5)
        ver += 1
        
        
        aimslog.info('*** Change RETIRE '+str(time.clock()))
        rqid3 = 3456543
        addr_c.setChangeId(cid)
        #addr_c.setVersion(ver)
        dm.retireAddress(addr_c,rqid3)
        resp = None
        while not resp: 
            resp = self.testresp(dm,FeedType.CHANGEFEED)
            if resp: 
                err = resp[0].getErrors()
                print rqid3,resp[0].meta.requestId
                print 'e',err
                if not err:
                    cid = resp[0].getChangeId()
            time.sleep(5)     
        ver += 1
    
        
    def testresolutionfeedAUD(self,dm,af):
        ver = 6977370
        #cid = 4117724
        cid = 4117720
        #pull address from features (map)
        addr_f = self.gettestdata(af[FeedType.FEATURES])
        #cast to addresschange type, to do cf ops
        addr_r = af[FeedType.RESOLUTIONFEED].cast(addr_f)
        #addr_r.setVersion(ver)
        addr_r.setChangeId(cid)
        
        aimslog.info('*** Resolution ACCEPT '+str(time.clock()))
        rqid1 = 4567654
        dm.acceptAddress(addr_r,rqid1)
        resp = None
        while True: 
            resp = self.testresp(dm,FeedType.RESOLUTIONFEED)
            if resp: 
                print rqid1,resp[0].meta.requestId
                break
            time.sleep(5)
        ver += 1
     
         
        aimslog.info('*** Resolution UPDATE '+str(time.clock()))
        rqid2 = 5678765
        addr_r.setFullAddress('Unit B, 16 Islay Street, Glenorchy')
        #addr_r.setVersion(ver)
        dm.repairAddress(addr_r,rqid2)
        resp = None
        while True: 
            resp = self.testresp(dm,FeedType.RESOLUTIONFEED)
            if resp: 
                print rqid2,resp[0].meta.requestId
                break
            time.sleep(5)
        ver += 1
        
        
        aimslog.info('*** Change DECLINE '+str(time.clock()))
        rqid3 = 6789876
        #addr_r.setVersion(ver)
        dm.declineAddress(addr_r,rqid3)
        resp = None
        while not resp: 
            resp = self.testresp(dm,FeedType.RESOLUTIONFEED)
            if resp: 
                print rqid3,resp[0].meta.requestId
                break
            time.sleep(5)     
        ver += 1
    
    
    def testresp(self,dm,ft=FeedType.CHANGEFEED):
        r = None
        #aimslog.info('*** Main COUNT {}'.format(dm.refresh()))  
        out = dm.pull()
        for o in out:
            #aimslog.info('*** Main OUTPUT {} - [{}]'.format(out[o],len(out[o])))
            aimslog.info('*** Main OUTPUT {} [{}]'.format(o,len(out[o])))
        
        
        resp = dm.response(ft)
        for r in resp:
            #aimslog.info('*** Main RESP {} - [{}]'.format(r,len(resp))) 
            aimslog.info('*** Main RESP {} [{}]'.format(r,len(resp)))
            
        return resp
                
    def gettestdata(self,ff):
        a = ff.getAddress('test_featuretype_address')
        p = Position.getInstance(
            {'position':{'type':'Point','coordinates': [168.38392191667,-44.8511013],'crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::4167'}}},'positionType':'Centroid','primary':True}
        )
        a.setAddressType('Road')
        a.setAddressNumber('16')
        a.setAddressId('29')
        a.setLifecycle('Current')
        a.setRoadCentrelineId('11849')
        a.setRoadName('Islay')
        a.setRoadType('Street'),
        a.setSuburbLocality('Glenorchy')
        a.setFullAddressNumber('16')
        a.setFullRoadName('Islay Street')
        a.setFullAddress('16 Islay Street, Glenorchy')
        a._addressedObject_addressableObjectId = '1416143'
        a.setObjectType('Parcel')
        
        a.setUnitType('Unit')
        a.setUnitValue('b')
    
        a.setAddressPositions(p)
    
        a._codes_suburbLocalityId = '2104'
        a._codes_parcelId = '3132748'
        a._codes_meshblock = '3174100'
        return a

    

            
if __name__ == '__main__':
    print 'start'
    lt = LocalTest()
    lt.test()  
    print 'finish'
