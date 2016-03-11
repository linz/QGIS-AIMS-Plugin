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
from AddressFactory import AddressFactory
#from DataUpdater import DataUpdater
from DataSync import DataSync,DataSyncFeatures,DataSyncChangeFeed,DataSyncResolutionFeed
from datetime import datetime as DT
from AimsUtility import ActionType,ApprovalType,FeedType,Configuration#,readConf
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
    
    
    def __init__(self,start=set( (FeedType.CHANGEFEED,FeedType.RESOLUTIONFEED) ),initialise=False):
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}   
        if start and hasattr(start,'__iter__'): self._start = set(start)
        self.persist = Persistence(initialise)
        self.conf = Configuration().readConf()
        self._initDS()
        
    def _initDS(self):
        '''initialise the data sync queues/threads'''
        self.ioq = {ft:None for ft in FeedType.reverse}
        self.ds = {ft:None for ft in FeedType.reverse}
        self.stamp = {ft:time.time() for ft in FeedType.reverse}
        
        #init the three different feed threads
        self.dsr = {
            FeedType.FEATURES:DataSyncFeatures,
            FeedType.CHANGEFEED:DataSyncChangeFeed,
            FeedType.RESOLUTIONFEED:DataSyncResolutionFeed
        }
        for ref in self.dsr:
            if ref in self._start: self.start(ref)
            
    def start(self,ft):
        self._start.update((ft,))
        self._initFeedDSChecker(ft)
        
    def notify(self, observable, *args, **kwargs):
        '''Do some housekeeping and notify listener'''
        aimslog.info('Notify A[{}], K[{}] - {}'.format(args,kwargs,observable))
        args += (self._monitor(args[0]),)
        if self.reg: self.reg.notify(observable, *args, **kwargs)
        self._check()
        
    def register(self,reg):
        '''Register single class as a listener'''
        self.reg = reg if hasattr(reg, 'notify') else None        
        
    def _initFeedDSChecker(self,ref):
        '''Starts a sync thread if conditions appropriate'''
        if ref == FeedType.FEATURES and self.persist.coords['sw'] == SWZERO and self.persist.coords['ne'] == NEZERO:                
            self.ds[ref] = None
        else:
            self.ds[ref] = self._initFeedDS(ref,self.dsr[ref])
            self.ds[ref].register(self)            
            self.ds[ref].start()
            
        
    def _initFeedDS(self,ft,feedclass): 
        ts = '{0:%y%m%d.%H%M%S}'.format(DT.now())
        params = ('ReqADU.{}.{}'.format(ft,ts),ft,self.persist.tracker[ft],self.conf)
        self.ioq[ft] = {n:Queue.Queue() for n in ('in','out','resp')}
        ds = feedclass(params,self.ioq[ft])
        ds.setup(self.persist.coords['sw'],self.persist.coords['ne'])
        ds.setDaemon(True)
        #ds.start()
        return ds    
        
    def close(self):
        '''shutdown closing/stopping ds threads and persisting data'''
        for ds in self.ds.values():
            if ds: ds.close()
        self.persist.write()
        
    def _check(self):
        '''If a DataSync thread crashes restart it'''
        for ft in self._start:#FeedType.reverse:
            if not self.ds.has_key(ft) or not self.ds[ft] or not self.ds[ft].isAlive():
                aimslog.warn('DS thread {} terminated, restarting'.format(FeedType.reverse[ft]))
                #del self.ds[ft]
                self._initFeedDSChecker(ft)
            
        
    #Client Access
    def setbb(self,sw=None,ne=None):
        '''Resetting the bounding box triggers a complete refresh of the features address data'''
        #TODO add move-threshold to prevent small moves triggering an update
        if self.persist.coords['sw'] != sw or self.persist.coords['ne'] != ne:
            #throw out the current features addresses
            self.persist.ADL[FeedType.FEATURES] = self.persist._initADL()[FeedType.FEATURES]
            #save the new coordinates
            self.persist.coords['sw'],self.persist.coords['ne'] = sw,ne
            #kill the old features thread
            if self.ds[FeedType.FEATURES] and self.ds[FeedType.FEATURES].isAlive():
                aimslog.info('Attempting Features Thread STOP')
                self.ds[FeedType.FEATURES].stop()
                self.ds[FeedType.FEATURES].join(THREAD_JOIN_TIMEOUT)
                #TODO investigate thread non-stopping issues
                if self.ds[FeedType.FEATURES].isAlive(): aimslog.warn('SetBB Features Thread JOIN timeout')
            del self.ds[FeedType.FEATURES]
            #reinitialise a new features DataSync
            self._initFeedDSChecker(FeedType.FEATURES)
    
    #@Deprecated     
    def restart(self,ft):
        '''Restart a specific thread type'''
        #NB UI feature request. 
        aimslog.warn('WARNING {} Thread Restart requested'.format(FeedType.reverse[ft]))
        if self.ds.has_key(ft) and self.ds[ft]:#.isAlive():
            self.ds[ft].stop() 
            self.ds[ft].join(THREAD_JOIN_TIMEOUT)
            if self.ds[ft].isAlive(): aimslog.warn('{} Thread JOIN timeout'.format(FeedType.reverse[ft]))
        #del self.ds[ft]
        self._check()
        
    #Push and Pull relate to features feed actions
    def push(self,newds):
        pass
        #return self._scan(newds)
        
    def pull(self):
        '''Return copy of the ADL. Speedup, insist on deepcopy at address level'''
        return self.persist.ADL
    
#     def refresh(self):
#         '''returns feed length counts without client having to do a pull/deepcopy'''
#         self._restart()
#         self._monitor()
#         return [(self.stamp[f],len(self.persist.ADL[f])) for f in FeedType.reverse]
        
    
    def action(self,at,address):
        '''Some user initiated approval action'''
        action = {at:[address,]}
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put(action)
        
        
    def _monitor(self,ft):
        '''for each feed check the out queue and put any new items into the ADL'''
        #for ft in self.ds:#FeedType.reverse:
        if self.ds[ft]:
            while not self.ioq[ft]['out'].empty():
                #because the queue isnt populated till all pages are loaded we can just swap out the ADL
                self.persist.ADL[ft] = self.ioq[ft]['out'].get()
                self.stamp[ft] = time.time()

        #self.persist.write()
        return self.persist.ADL[ft]
    
    def response(self,ft=FeedType.RESOLUTIONFEED):
        '''Returns any features lurking in the response queue'''
        resp = ()
        while not self.ioq[ft]['resp'].empty():
            resp += (self.ioq[ft]['resp'].get(),)
        return resp
        
      
    def _populate(self,address):
        '''Fill in any required+missing fields if a default value is known (in this case the configured user)'''
        if not hasattr(address,'_workflow_sourceUser') or not address.getSourceUser(): address.setSourceUser(self.conf['user'])
        return address
    
    #convenience methods 
    #---------------------------- 
    def addAddress(self,address,reqid=None):
        if reqid: address.setRequestId(reqid)
        self._populate(address).setChangeType(ActionType.reverse[ActionType.ADD].title())
        self.ioq[FeedType.CHANGEFEED]['in'].put({ActionType.ADD:(address,)})        
    
    def retireAddress(self,address,reqid=None):
        if reqid: address.setRequestId(reqid)
        self._populate(address).setChangeType(ActionType.reverse[ActionType.RETIRE].title())
        self.ioq[FeedType.CHANGEFEED]['in'].put({ActionType.RETIRE:(address,)})
    
    def updateAddress(self,address,reqid=None,srcusr=None):
        if reqid: address.setRequestId(reqid)
        self._populate(address).setChangeType(ActionType.reverse[ActionType.UPDATE].title())
        self.ioq[FeedType.CHANGEFEED]['in'].put({ActionType.UPDATE:(address,)})    
        
    #----------------------------
    def acceptAddress(self,address,reqid=None):
        if reqid: address.setRequestId(reqid)
        address.setQueueStatus(ApprovalType.revalt[ApprovalType.ACCEPT].title())
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put({ApprovalType.ACCEPT:(address,)})        
    
    def declineAddress(self,address,reqid=None):
        if reqid: address.setRequestId(reqid)
        address.setQueueStatus(ApprovalType.revalt[ApprovalType.DECLINE].title())
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put({ApprovalType.DECLINE:(address,)})
    
    def repairAddress(self,address,reqid=None):
        if reqid: address.setRequestId(reqid)
        address.setQueueStatus(ApprovalType.revalt[ApprovalType.UPDATE].title())
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put({ApprovalType.UPDATE:(address,)})
    
    #----------------------------
#     def getWarnings(self,address):
#         '''Manually request warning messages per address, useful if warnings not enabled by default'''
#         return
#         cid = address.getChangeId()
#         if address.type != FeedType.RESOLUTION:
#             aimslog.warn('Attempt to set warnings on non-resolution address, casting')
#             address = Address.clone(address, AddressFactory.getInstance(FeedType.RESOLUTIONFEED).getAddress())
#         #TODO! Fix! Not thinking straight here, this wont work
#         dsrf = self._initFeedDS(FeedType.RESOLUTIONFEED,None)
#         address.setWarnings( dsrf.updateWarnings(cid) )
#         dsrf.stop()
#         return address
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
            self.tracker[FeedType.FEATURES] =       {'page':[1,1],    'index':1,'threads':2,'interval':30}
            self.tracker[FeedType.CHANGEFEED] =     {'page':[NPV,NPV],'index':1,'threads':1,'interval':125}
            self.tracker[FeedType.RESOLUTIONFEED] = {'page':[1,1],    'index':1,'threads':1,'interval':10}
            #self.tracker[FeedType.FEATURES] =       {'page':[1,1],'index':1,'threads':2,'interval':30}    
            #self.tracker[FeedType.CHANGEFEED] =     {'page':[1,1],'index':1,'threads':1,'interval':1000}  
            #self.tracker[FeedType.RESOLUTIONFEED] = {'page':[1,1],'index':1,'threads':1,'interval':1000} 
            self.write() 
    
    def _initADL(self):
        '''Read ADL from serial and update from API'''
        return {FeedType.FEATURES:[],FeedType.CHANGEFEED:[],FeedType.RESOLUTIONFEED:[]}
    
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
        af = {ft:AddressFactory.getInstance(ft) for ft in FeedType.reverse}
    
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
        #self.testrestartCR(dm)
        
        #TEST SHIFT
        #self.testfeatureshift(dm)
        
        # TEST CF
        #self.testchangefeedAUR(dm,af)
        
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
        dm.restart(FeedType.FEATURES)
        time.sleep(10)
        dm.restart(FeedType.CHANGEFEED)
        time.sleep(10)
        dm.restart(FeedType.RESOLUTIONFEED)
        
        
    def testchangefeedAUR(self,dm,af):
        ver = 1000000
        cid = 2000000
        #pull address from features (map)
        addr_f = self.gettestdata(af[FeedType.FEATURES])
        #cast to addresschange type, to do cf ops
        addr_c = af[FeedType.CHANGEFEED].cast(addr_f)
        addr_c.setVersion(ver)
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
        addr_c.setVersion(ver)
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
        addr_c.setVersion(ver)
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
        cid = 4117724
        #pull address from features (map)
        addr_f = self.gettestdata(af[FeedType.FEATURES])
        #cast to addresschange type, to do cf ops
        addr_r = af[FeedType.RESOLUTIONFEED].cast(addr_f)
        addr_r.setVersion(ver)
        addr_r.setChangeId(cid)
#         aimslog.info('*** Resolution ACCEPT '+str(time.clock()))
#         rqid1 = 4567654
#         dm.acceptAddress(addr_r,rqid1)
#         resp = None
#         while True: 
#             resp = self.testresp(dm,FeedType.RESOLUTIONFEED)
#             if resp: 
#                 print rqid1,resp[0].meta.requestId
#                 break
#             time.sleep(5)
#         ver += 1
#     
#         
#         aimslog.info('*** Resolution UPDATE '+str(time.clock()))
#         rqid2 = 5678765
#         addr_r.setFullAddress('Unit B, 16 Islay Street, Glenorchy')
#         addr_r.setVersion(ver)
#         dm.repairAddress(addr_r,rqid2)
#         resp = None
#         while True: 
#             resp = self.testresp(dm,FeedType.RESOLUTIONFEED)
#             if resp: 
#                 print rqid2,resp[0].meta.requestId
#                 break
#             time.sleep(5)
#         ver += 1
        
        
        aimslog.info('*** Change DECLINE '+str(time.clock()))
        rqid3 = 6789876
        addr_r.setVersion(ver)
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
        a = ff.getAddress('change_add')
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