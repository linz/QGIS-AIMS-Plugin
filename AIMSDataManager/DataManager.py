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
from AimsLogging import Logger

LOCALADL = 'aimsdata'
LOCALDB = 'aimsdata.sb'
UPDATE_INTERVAL = 5#s
LOGFILE = 'admlog'
SW = (174.75918,-41.29515)
NE = (174.78509,-41.27491)


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
    
    
    def __init__(self):
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}        
        self.persist = Persistence()
        self.conf = readConf()
        self._initDS()
        
    def _initDS(self):
        '''initialise the data sync queues/threads'''
        self.ioq = {ft:None for ft in FeedType.reverse}
        self.ds = {ft:None for ft in FeedType.reverse}
        
        #init the three different feed threads
        self._initFeedDS(FeedType.FEATURES,DataSyncFeatures)
        self._initFeedDS(FeedType.CHANGEFEED,DataSyncChangeFeed)
        self._initFeedDS(FeedType.RESOLUTIONFEED,DataSyncResolutionFeed)


        
    def _initFeedDS(self,ft,feedclass): 
        ts = '{0:%y%m%d.%H%M%S}'.format(DT.now())
        params = ('ReqADU.{}.{}'.format(ft,ts),ft,self.persist.tracker[ft],self.conf)
        self.ioq[ft] = {n:Queue.Queue() for n in ('in','out','resp')}
        self.ds[ft] = feedclass(params,self.ioq[ft])
        self.ds[ft].setup(self.persist.coords['sw'],self.persist.coords['ne'])
        self.ds[ft].setDaemon(True)
        self.ds[ft].start()
        
    def close(self):
        '''shutdown closing/stopping ds threads and persisting data'''
        for ds in self.ds.values():
            #ds.close()
            #ds.stop()
            pass
        self.persist.write()

#     #==============================================================================================
#     #SQLite Access (might use this for CF and RF)
#     def _initDB(self):
#         '''One time job to setup the initial db'''
#         self.conn = sqlite3.connect(LOCALDB)
#         c = self.conn.cursor()
#         c.execute('create table CHANGEFEED (a int,b int)')
#         c.execute('create table RESOLUTIONFEED (a int,b int)')
#         self.conn.commit()
#         self.conn.close()
#          
#     def _readDB(self):
#         c = self.conn.cursor()
#         for cfrow in c.execute('select * from CHANGEFEED'):
#             self.ADL[FeedType.CHANGEFEED] += AddressChange._import(AddressChange(cfrow))
#         for rfrow in c.execute('select * from RESOLUTIONFEED'):
#             self.ADL[FeedType.RESOLUTIONFEED] += AddressResolution._import(AddressResolution(rfrow))
#              
#     def _writeDB(self):
#         c = self.conn.cursor()
#         for adr in self.ADL[FeedType.CHANGEFEED]:
#             #changefeed is only ever insert
#             c.execute('insert into CHANGEFEED values ({})'.format(adr.getInsert()))
#         for adr in self.ADL[FeedType.RESOLUTIONFEED]:
#             #resolutionfeed can be add/del
#             c.execute('insert into RESOLUTIONFEED values ({})'.format(adr.getInsert()))
#     #==============================================================================================
        
        
    #Client Access
    def setbb(self,sw=None,ne=None):
        '''Resetting the bounding box triggers a complete refresh of the features address data'''
        if self.persist.coords['sw'] != sw or self.persist.coords['ne'] != ne:
            #throw out the current features addresses
            self.persist.ADL[FeedType.FEATURES] = self.persist._initADL()[FeedType.FEATURES]
            #save the new coordinates
            self.persist.coords['sw'],self.persist.coords['ne'] = sw,ne
            #kill the old features thread
            self.ds[FeedType.FEATURES].stop()
            del self.ds[FeedType.FEATURES]
            #reinitialise a new features DataSync
            self._initFeedDS(FeedType.FEATURES,DataSyncFeatures)

        
    #Push and Pull relate to features feed actions
    def push(self,newds):
        return self._scan(newds)
        
    def pull(self):
        '''Return copy of the ADL. Speedup, insist on deepcopy at address level'''
        return copy.deepcopy(self.persist.ADL)
    
    def refresh(self):
        '''returns feed length counts without client having to do a pull/deepcopy'''
        self._monitor()
        return [len(self.persist.ADL[f]) for f in FeedType.reverse]
        
    
    def action(self,at,address):
        '''Some user initiated approval action'''
        action = {at:[address,]}
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put(action)
        
        
    def _monitor(self):
        '''for each feed check the out queue and put any new items into the ADL'''
        for ft in FeedType.reverse:
            while not self.ioq[ft]['out'].empty():
                #because the queue isnt populated till all pages are loaded we can just swap out the ADL
                self.persist.ADL[ft] = self.ioq[ft]['out'].get()

        #self.persist.write()
        return self.persist.ADL
    
    def response(self):
        resp = ()
        while not self.ioq[FeedType.CHANGEFEED]['resp'].empty():
            resp += (self.ioq[FeedType.CHANGEFEED]['resp'].get(),)
        return resp
        
        
    def _scan(self,ds):
        '''compare provided and current ADL. Split out deletes/adds/updates'''
        #self._synchroniseChangeFeed(ds)
        #self._synchroniseResolutionFeed(ds)
        self._scanChangeFeedChanges(ds[FeedType.CHANGEFEED])
        self._scanResolutionFeedChanges(ds[FeedType.RESOLUTIONFEED])
      
    #convenience methods  
    def addAddress(self,address):
        address.setChangeType(ActionType.reverse[ActionType.ADD].title())
        self.ioq[FeedType.CHANGEFEED]['in'].put({ActionType.ADD:(address,)})        
    
    def retireAddress(self,address):
        address.setChangeType(ActionType.reverse[ActionType.RETIRE].title())
        self.ioq[FeedType.CHANGEFEED]['in'].put({ActionType.RETIRE:(address,)})
    
    def updateAddress(self,address):
        address.setChangeType(ActionType.reverse[ActionType.UPDATE].title())
        self.ioq[FeedType.CHANGEFEED]['in'].put({ActionType.UPDATE:(address,)})    
        
    #----------------------------
    def acceptAddress(self,address):
        address.setQueueStatus(ApprovalType.revalt[ApprovalType.ACCEPT].title())
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put({ApprovalType.ACCEPT:(address,)})        
    
    def declineAddress(self,address):
        address.setQueueStatus(ApprovalType.revalt[ApprovalType.DECLINE].title())
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put({ApprovalType.DECLINE:(address,)})
    
    def repairAddress(self,address):
        address.setQueueStatus(ApprovalType.revalt[ApprovalType.UPDATE].title())
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put({ApprovalType.UPDATE:(address,)})
        
 
    def _enlist(self,address):
        return address if isinstance(address,collectionsIterable) else [address,]
        
  
#     contention with bg updates would require a snapshot for comparison per pull        
#     def _synchroniseChangeFeed(self,newds):
#         '''compare provided and current ADL. Split out deletes/adds/updates'''
#         #check changes etc
#         changes = {}
#         #identify changes in the feed and do the necessary updates by putting them in the queue
#         home,away = self.persist.ADL[FeedType.CHANGEFEED],newds[FeedType.CHANGEFEED]
#         changes[ActionType.ADD] = [a2 for a2 in away if a2 not in home]
#         changes[ActionType.RETIRE] = [a1 for a1 in home if a1 not in away]
#         #addresses not in adds/dels that have changed attributes
#         changes[ActionType.UPDATE] = [a2 for a2 in [x for x in away if x not in changes[ActionType.ADD]] \
#                                       for a1 in [x for x in home if x not in changes[ActionType.RETIRE]] \
#                                       if a1==a2 and not a1.compare(a2)]    
#         self.ioq[FeedType.CHANGEFEED]['in'].put(changes)
#         
#     def _synchroniseResolutionFeed(self,newds):
#         '''compare provided and current ADL. Split out deletes/adds/updates'''
#         #check changes etc
#         changes = {}
#         #identify changes in the feed and do the necessary updates by putting them in the queue
#         home,away = self.persist.ADL[FeedType.RESOLUTIONFEED],newds[FeedType.RESOLUTIONFEED]
#         changes[ApprovalType.ACCEPT] = [a2 for a2 in away if a2 not in home]
#         changes[ApprovalType.DECLINE] = [a1 for a1 in home if a1 not in away]
#         #addresses not in adds/dels that have changed attributes
#         changes[ApprovalType.UPDATE] = [a2 for a2 in [x for x in away if x not in changes[ApprovalType.ACCEPT]] \
#                                       for a1 in [x for x in home if x not in changes[ApprovalType.DECLINE]] \
#                                       if a1==a2 and not a1.compare(a2)] 
#             
#         #TODO. add logic for what changes trigger what updates Or just get all updates
#         self.ioq[FeedType.RESOLUTIONFEED]['in'].put(changes)
        
    def _scanChangeFeedChanges(self,ds):
        changes = {}
        changes[ApprovalType.ADD] = [a for a in ds if a.getChangeType()==ActionType.reverse[ActionType.ADD].title()]
        changes[ApprovalType.RETIRE] = [a for a in ds if a.getChangeType()==ActionType.reverse[ActionType.RETIRE].title()]
        changes[ApprovalType.UPDATE] = [a for a in ds if a.getChangeType()==ActionType.reverse[ActionType.UPDATE].title()]
        self.ioq[FeedType.CHANGEFEED]['in'].put(changes)    
        
    def _scanResolutionFeedChanges(self,ds):
        changes = {}
        changes[ApprovalType.ACCEPT] = [a for a in ds if a.getChangeType()==ApprovalType.reverse[ApprovalType.ACCEPT].title()]
        changes[ApprovalType.DECLINE] = [a for a in ds if a.getChangeType()==ApprovalType.reverse[ApprovalType.DECLINE].title()]
        changes[ApprovalType.UPDATE] = [a for a in ds if a.getChangeType()==ApprovalType.reverse[ApprovalType.UPDATE].title()]
        #self.ioq[FeedType.RESOLUTIONFEED]['in'].put(changes)

        
        
    #CM
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type=None, exc_val=None, exc_tb=None):
        return self.close()

        

class Persistence():
    '''static class for persisting config/long-lived information'''
    
    tracker,coords,ADL = 3*(None,)
    
    def __init__(self):

        if not self.read():
            self.ADL = self._initADL() 
            self.coords = {'sw':SW,'ne':NE}
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
            self.tracker,self.coords,self.ADL = archive
        except:
            return False
        return True
    
    def write(self, localds=LOCALADL):
        try:
            archive = [self.tracker,self.coords,self.ADL]
            pickle.dump(archive, open(localds,'wb'))
        except:
            return False
        return True

testdata = []
def test():
    aff = AddressFactory(FeedType.FEATURES)
    afc = AddressFactory(FeedType.CHANGEFEED)
    afr = AddressFactory(FeedType.RESOLUTIONFEED)
#     global testdata
#     testdata = {FeedType.FEATURES:[
#                 aff.getAddress('one'), 
#                 aff.getAddress('two'),
#                 aff.getAddress('three'),
#                 aff.getAddress('four'),
#                 aff.getAddress('five')
#                 ],
#             FeedType.CHANGEFEED:[
#                 afc.getAddress('one_c'), 
#                 afc.getAddress('two_c'), 
#                 afc.getAddress('three_c')     
#                 ],
#             FeedType.RESOLUTIONFEED:[
#                 afr.getAddress('one_r'), 
#                 afr.getAddress('two_r'), 
#                 afr.getAddress('three_r')       
#                 ]
#             } 
    
    with DataManager() as dm:
        test1(dm,(aff,afc,afr))
        
        
def test1(dm,f3):
    #cd <path>/git/SP-QGIS-AIMS-Plugin/AIMSDataManager
    #import sys
    #from DataManager import DataManager
    #start DM
    print 'start'
    
    #dm.persist.ADL = testdata
    #get some data
    dm.refresh()
    listofaddresses = dm.pull()
    #add
    #time.sleep(5)
    aimslog.info('*** Main ADD '+str(time.clock()))
    addr_7 = f3[0].getAddress('ninenintyseven')
    addr_8 = f3[0].getAddress('ninenintyeight')
    addr_9 = f3[0].getAddress('ninenintynine')
    
    addr_c = f3[0].getAddress('change_add')
    addr_r = f3[0].getAddress('resolution_accept')
    
    addr_c1 = gettestdata(f3[0])
    
#     listofaddresses[FeedType.FEATURES].append(addr_7)
#     listofaddresses[FeedType.FEATURES].append(addr_8)
#     listofaddresses[FeedType.FEATURES].append(addr_9)
#     dm.push(listofaddresses)
#     time.sleep(5)
#     testresp(dm)
#     #del
#     time.sleep(5)
#     aimslog.info('*** Main RETIRE '+str(time.clock()))
#     addr_0 = listofaddresses[FeedType.FEATURES][0]
#     addr_1 = listofaddresses[FeedType.FEATURES][1]
#     listofaddresses[FeedType.FEATURES].remove(addr_0)
#     listofaddresses[FeedType.FEATURES].remove(addr_1)
#     dm.push(listofaddresses)
#     time.sleep(5)
#     testresp(dm)
#     #chg
#     time.sleep(5)
#     aimslog.info('*** Main UPDATE '+str(time.clock()))
#     addr_2 = listofaddresses[FeedType.FEATURES][2]
#     addr_3 = listofaddresses[FeedType.FEATURES][3]
#     addr_2.setVersion(2222)
#     addr_3.setVersion(3333)
#     #listofaddresses[FeedType.FEATURES][2].setVersion(123456)
#     #listofaddresses[FeedType.FEATURES][3].setVersion(123457)
#     dm.push(listofaddresses)
#     time.sleep(5)
#     testresp(dm)
#     #shift
#     time.sleep(5)
#     aimslog.info('*** Main SHIFT '+str(time.clock()))
#     dm.setbb(sw=(174.76918,-41.28515), ne=(174.79509,-41.26491))
#     time.sleep(5)
#     testresp(dm)
#     time.sleep(5)
    
    aimslog.info('*** Change ADD '+str(time.clock()))
    #addr_c.setChangeType(ActionType.reverse[ActionType.ADD])
    #listofaddresses[FeedType.CHANGEFEED].append(addr_c)
    #dm.push(listofaddresses)
    addr_c.setAddressType('Road')
    addr_c.setAddressNumber(100)
    addr_c.setRoadName('Smith St')
    dm.addAddress(addr_c1)
    time.sleep(5)
    testresp(dm)
    time.sleep(5)
    
    aimslog.info('*** Resolution ADD '+str(time.clock()))
    #addr_r.setQueueStatus(ApprovalType.reverse[ApprovalType.ACCEPT])
    #listofaddresses[FeedType.RESOLUTIONFEED].append(addr_r)
    #dm.push(listofaddresses)
    
    #dm.acceptAddress(addr_r)
    #time.sleep(5)
    #testresp(dm)
    #time.sleep(5)
    
    
    print 'entering response mode'
    while True:
        aimslog.info('*** Main TICK '+str(time.clock()))
        testresp(dm)
        time.sleep(5)
        
def testresp(dm):
    
    aimslog.info('*** Main COUNT {}'.format(dm.refresh()))

        
    out = dm.pull()
    for o in out:
        #aimslog.info('*** Main OUTPUT {} - [{}]'.format(out[o],len(out[o])))
        aimslog.info('*** Main OUTPUT {} [{}]'.format(o,len(out[o])))
    
    resp = dm.response()
    for r in resp:
        #aimslog.info('*** Main RESP {} - [{}]'.format(r,len(resp))) 
        aimslog.info('*** Main RESP {} [{}]'.format(r,len(resp)))
            
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

    a.setAddressPosition(p)

    a._codes_suburbLocalityId = '2104'
    a._codes_parcelId = '3132748'
    a._codes_meshblock = '3174100'
    return a

    

            
if __name__ == '__main__':
    test()  