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
from AimsUtility import ActionType,ApprovalType,FeedType,readConf
from AimsUtility import THREAD_JOIN_TIMEOUT,LOCALADL,SWZERO,NEZERO
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
    
    
    def __init__(self,start=set( (FeedType.FEATURES,FeedType.CHANGEFEED,FeedType.RESOLUTIONFEED) )):
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}   
        if start and hasattr(start,'__iter__'): self._start = set(start)
        self.persist = Persistence()
        self.conf = readConf()
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
        
        
    def _initFeedDSChecker(self,ref):
        '''Starts a sync thread if conditions appropriate'''
        if ref == FeedType.FEATURES and self.persist.coords['sw'] == SWZERO and self.persist.coords['ne'] == NEZERO:                
            self.ds[ref] = None
        else:
            #self._initFeedDS(ref,self.dsr[ref])
            self.ds[ref] = self._initFeedDS(ref,self.dsr[ref])
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
        
#     def _initFeedDS(self,ft,feedclass): 
#         ts = '{0:%y%m%d.%H%M%S}'.format(DT.now())
#         params = ('ReqADU.{}.{}'.format(ft,ts),ft,self.persist.tracker[ft],self.conf)
#         self.ioq[ft] = {n:Queue.Queue() for n in ('in','out','resp')}
#         self.ds[ft] = feedclass(params,self.ioq[ft])
#         self.ds[ft].setup(self.persist.coords['sw'],self.persist.coords['ne'])
#         self.ds[ft].setDaemon(True)
#         self.ds[ft].start()
        
    def close(self):
        '''shutdown closing/stopping ds threads and persisting data'''
        for ds in self.ds.values():
            #ds.close()
            #ds.stop()
            pass
        self.persist.write()
        
    def _restart(self):
        '''If a DataSync thread crashes restart it'''
        for ft in self._start:#FeedType.reverse:
            if not self.ds[ft] or not self.ds[ft].isAlive():
                aimslog.warn('DS thread {} has died, restarting'.format(FeedType.reverse[ft]))
                del self.ds[ft]
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
                if self.ds[FeedType.FEATURES].isAlive(): aimslog.warn('Features Thread JOIN timeout')
            del self.ds[FeedType.FEATURES]
            #reinitialise a new features DataSync
            self._initFeedDSChecker(FeedType.FEATURES)

        
    #Push and Pull relate to features feed actions
    def push(self,newds):
        pass
        #return self._scan(newds)
        
    def pull(self):
        '''Return copy of the ADL. Speedup, insist on deepcopy at address level'''
        return self.persist.ADL
    
    def refresh(self):
        '''returns feed length counts without client having to do a pull/deepcopy'''
        self._restart()
        self._monitor()
        return [(self.stamp[f],len(self.persist.ADL[f])) for f in FeedType.reverse]
        
    
    def action(self,at,address):
        '''Some user initiated approval action'''
        action = {at:[address,]}
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put(action)
        
        
    def _monitor(self):
        '''for each feed check the out queue and put any new items into the ADL'''
        for ft in self.ds:#FeedType.reverse:
            if self.ds[ft]:
                while not self.ioq[ft]['out'].empty():
                    #because the queue isnt populated till all pages are loaded we can just swap out the ADL
                    self.persist.ADL[ft] = self.ioq[ft]['out'].get()
                    self.stamp[ft] = time.time()

        #self.persist.write()
        return self.persist.ADL
    
    def response(self,ft=FeedType.RESOLUTIONFEED):
        '''Returns any features lurking in the response queue'''
        resp = ()
        while not self.ioq[ft]['resp'].empty():
            resp += (self.ioq[ft]['resp'].get(),)
        return resp
        
      
    #convenience methods 
    #---------------------------- 
    def addAddress(self,address,reqid=None):
        if reqid: address.setRequestId(reqid)
        address.setChangeType(ActionType.reverse[ActionType.ADD].title())
        self.ioq[FeedType.CHANGEFEED]['in'].put({ActionType.ADD:(address,)})        
    
    def retireAddress(self,address,reqid=None):
        if reqid: address.setRequestId(reqid)
        address.setChangeType(ActionType.reverse[ActionType.RETIRE].title())
        self.ioq[FeedType.CHANGEFEED]['in'].put({ActionType.RETIRE:(address,)})
    
    def updateAddress(self,address,reqid=None):
        if reqid: address.setRequestId(reqid)
        address.setChangeType(ActionType.reverse[ActionType.UPDATE].title())
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
    def getWarnings(self,address):
        '''Manually request warning messages per address, useful if warnings not enabled by default'''
        return
        cid = address.getChangeId()
        if address.type != FeedType.RESOLUTION:
            aimslog.warn('Attempt to set warnings on non-resolution address, casting')
            address = Address.clone(address, AddressFactory.getInstance(FeedType.RESOLUTIONFEED).getAddress())
        #TODO. Fix! Not thinking straight here, this wont work
        dsrf = self._initFeedDS(FeedType.RESOLUTIONFEED)
        address.setWarnings( dsrf.updateWarnings(cid) )
        dsrf.stop()
        return address
    #CM
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type=None, exc_val=None, exc_tb=None):
        return self.close()

        

class Persistence():
    '''static class for persisting config/long-lived information'''
    
    tracker,coords,ADL = 3*(None,)
    
    def __init__(self):
        self.coords = {'sw':SWZERO,'ne':NEZERO}
        if not self.read():
            self.ADL = self._initADL() 
            #default tracker, gets overwritten
            self.tracker = {ft:{'page':[1,1],'index':1,'threads':1,'interval':5} for ft in FeedType.reverse}
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

def test():
    global refsnap
    refsnap = {0:None,1:None,2:None}
    af = {ft:AddressFactory.getInstance(ft) for ft in FeedType.reverse}

    #with DataManager(start=None) as dm:
    #    dm.start(FeedType.CHANGEFEED)
    with DataManager() as dm:
        test1(dm,af)
        
        
def test1(dm,af):
    print 'start test'
    
    #dm.persist.ADL = testdata
    #get some data
    dm.refresh()
    listofaddresses = dm.pull()

    
    # TEST CF
    testchangefeedAUR(dm,af)
    
    # TEST RF
    testresolutionfeedAUD(dm,af)
    
    #TEST SHIFT
    testfeatureshift(dm)
    
    aimslog.info('*** Resolution ADD '+str(time.clock()))    
    
    print 'entering response mode'
    while True:
        aimslog.info('*** Main TICK '+str(time.clock()))
        testresp(dm)
        time.sleep(5)
        
def testfeatureshift(dm):

    aimslog.info('*** Main SHIFT '+str(time.clock()))
    dm.setbb(sw=(174.76918,-41.28515), ne=(174.79509,-41.26491))
    time.sleep(10)
    resp = None
    while not checkrefresh(dm): 
        resp = testresp(dm)
        time.sleep(5)    
        
    dm.setbb(sw=(174.76928,-41.28515), ne=(174.79519,-41.26481))
    time.sleep(10)
    resp = None
    while not checkrefresh(dm): 
        resp = testresp(dm)
        time.sleep(5)
        
    dm.setbb(sw=(174.76928,-41.28515), ne=(174.79529,-41.26471))
    time.sleep(10)
    resp = None
    while not checkrefresh(dm): 
        resp = testresp(dm)
        time.sleep(5)
        
def checkrefresh(dm):        
    global refsnap
    rs2 = dm.refresh()
    if rs2 != refsnap:
        refsnap = rs2
        return True
    return False
    
def testchangefeedAUR(dm,af):
    ver = 1000000
    #pull address from features (map)
    addr_c = gettestdata(af[FeedType.FEATURES])
    #cast to addresschange type, to do cf ops
    addr_c = af[FeedType.CHANGEFEED].cast(addr_c)
    addr_c.setVersion(ver)
    aimslog.info('*** Change ADD '+str(time.clock()))
    #addr_c.setChangeType(ActionType.reverse[ActionType.ADD])
    #listofaddresses[FeedType.CHANGEFEED].append(addr_c)
    #dm.push(listofaddresses)
    rqid1 = 1234321
    dm.addAddress(addr_c,rqid1)
    resp = None
    while True: 
        resp = testresp(dm,FeedType.CHANGEFEED)
        if resp: 
            print rqid1,resp[0].meta.requestId
            break
        time.sleep(5)
    ver += 1

    
    aimslog.info('*** Change UPDATE '+str(time.clock()))
    #addr_c.setChangeType(ActionType.reverse[ActionType.ADD])
    #listofaddresses[FeedType.CHANGEFEED].append(addr_c)
    #dm.push(listofaddresses)
    rqid2 = 2345432
    addr_c.setFullAddress('Unit B, 16 Islay Street, Glenorchy')
    addr_c.setVersion(ver)
    dm.updateAddress(addr_c,rqid2)
    resp = None
    while True: 
        resp = testresp(dm,FeedType.CHANGEFEED)
        if resp: 
            print rqid2,resp[0].meta.requestId
            break
        time.sleep(5)
    ver += 1
    
    
    aimslog.info('*** Change RETIRE '+str(time.clock()))
    #addr_c.setChangeType(ActionType.reverse[ActionType.ADD])
    #listofaddresses[FeedType.CHANGEFEED].append(addr_c)
    #dm.push(listofaddresses)
    rqid3 = 3456543
    addr_c.setVersion(ver)
    dm.retireAddress(addr_c,rqid3)
    resp = None
    while not resp: 
        resp = testresp(dm,FeedType.CHANGEFEED)
        if resp: 
            print rqid3,resp[0].meta.requestId
            break
        time.sleep(5)     
    ver += 1

    
def testresolutionfeedAUD(dm,af):
    pass#addr_r = af.getAddress('resolution_accept')


def testresp(dm,ft=FeedType.CHANGEFEED):
    r = None
    aimslog.info('*** Main COUNT {}'.format(dm.refresh()))  
    out = dm.pull()
    for o in out:
        #aimslog.info('*** Main OUTPUT {} - [{}]'.format(out[o],len(out[o])))
        aimslog.info('*** Main OUTPUT {} [{}]'.format(o,len(out[o])))
    
    
    resp = dm.response(ft)
    for r in resp:
        #aimslog.info('*** Main RESP {} - [{}]'.format(r,len(resp))) 
        aimslog.info('*** Main RESP {} [{}]'.format(r,len(resp)))
        
    return resp
            
def gettestdata(ff):
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
    test()  