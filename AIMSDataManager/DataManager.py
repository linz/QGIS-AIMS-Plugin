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
from Address import Address, AddressChange, AddressResolution
from DataUpdater import DataUpdater
from DataSync import DataSync,DataSyncFeatures,DataSyncChangeFeed,DataSyncResolutionFeed
from datetime import datetime as DT
from AimsUtility import ActionType,FeedType,readConf
from AimsLogging import Logger


LOCALADL = 'aimsdata'
LOCALDB = 'aimsdata.sb'
UPDATE_INTERVAL = 5#s
LOGFILE = 'admlog'
SW = (174.75918,-41.29515)
NE = (174.78509,-41.27491)


aimslog = None
# testdata = {FeedType.FEATURES:{
#                 1: Address._import(Address('one')), 
#                 2: Address._import(Address('two')),
#                 3: Address._import(Address('three')),
#                 4: Address._import(Address('four')),
#                 5: Address._import(Address('five'))
#                 },
#             FeedType.CHANGEFEED:{
#                 11: AddressChange._import(AddressChange('one_c')), 
#                 12: AddressChange._import(AddressChange('two_c')), 
#                 13: AddressChange._import(AddressChange('three_c'))       
#                 },
#             FeedType.RESOLUTIONFEED:{
#                 21: AddressResolution._import(AddressResolution('one_r')), 
#                 22: AddressResolution._import(AddressResolution('two_r')), 
#                 23: AddressResolution._import(AddressResolution('three_r'))       
#                 }
#             } 
testdata = {FeedType.FEATURES:[
                Address._import(Address('one')), 
                Address._import(Address('two')),
                Address._import(Address('three')),
                Address._import(Address('four')),
                Address._import(Address('five'))
                ],
            FeedType.CHANGEFEED:[
                AddressChange._import(AddressChange('one_c')), 
                AddressChange._import(AddressChange('two_c')), 
                AddressChange._import(AddressChange('three_c'))       
                ],
            FeedType.RESOLUTIONFEED:[
                AddressResolution._import(AddressResolution('one_r')), 
                AddressResolution._import(AddressResolution('two_r')), 
                AddressResolution._import(AddressResolution('three_r'))       
                ]
            } 

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
        '''non abrupt shutdown saving persisted data'''
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
            #reinitialise a new features DataSync
            self._initFeedDS(FeedType.FEATURES,DataSyncFeatures)

        
    #Push and Pull relate to features feed actions
    def push(self,newds):
        return self._synchronise(newds)
        
    def pull(self):
        '''Return copy of the ADL. Speedup, insist on deepcopy at address level'''
        return copy.deepcopy(self.persist.ADL)
    
    def refresh(self):
        '''returns feed length counts without client having to do a pull/deepcopy'''
        self._monitor()
        return [len(self.persist.ADL[f]) for f in FeedType.reverse]
    
    def close(self):
        self.persist.write()
        
    
    def action(self,at,address):
        '''Some user initiated approval action'''
        action = {at:[address,]}
        self.ioq[FeedType.RESOLUTIONFEED]['in'].put(action)
        
        
    def _monitor(self):
        '''for each feed check the out queue and put any new items into the ADL'''
        for ft in FeedType.reverse:
            while not self.ioq[ft]['out'].empty():
                dat = self.ioq[ft]['out'].get()
                self.persist.ADL[ft] += dat
        #self.persist.write()
        return self.persist.ADL
    
    def response(self):
        resp = ()
        while not self.ioq[FeedType.FEATURES]['resp'].empty():
            resp += (self.ioq[FeedType.FEATURES]['resp'].get(),)
        return resp
        
        
    def _synchronise(self,newds):
        '''compare provided and current ADL. Split out deletes/adds/updates'''
        #check changes etc
        changes = {}
        for ft in (FeedType.FEATURES,):#FeedType.reverse:
            #identify changes in the feed and do the necessary updates by putting them in the queue
            home,away = self.persist.ADL[ft],newds[ft]
            changes[ActionType.ADD] = [a2 for a2 in away if a2 not in home]#[away[a2] for a2 in away if a2 not in home]
            changes[ActionType.RETIRE] = [a1 for a1 in home if a1 not in away]#[home[a1] for a1 in home if a1 not in away]
            #addresses not in adds/dels that have changed attributes
            changes[ActionType.UPDATE] = [a2 for a2 in [x for x in away if x not in changes[ActionType.ADD]] \
                                          for a1 in [x for x in home if x not in changes[ActionType.RETIRE]] \
                                          if a1==a2 and not a1.compare(a2)] 
                                        #[away[a2] for a2 in [x for x in away if x not in changes[ActionType.ADD]] \
                                        #for a1 in [x for x in home if x not in changes[ActionType.RETIRE]] \
                                        #if a1==a2 and not home[a1].compare(away[a2])]
            
        #TODO. add logic for what changes trigger what updates Or just get all updates
        aq = self._process(changes)
        
        
    def _process(self,changes):
        '''All user changes are posted to the CF inq'''
        self.ioq[FeedType.CHANGEFEED]['in'].put(changes)
        

class Persistence():
    '''static class for persisting config/long-lived information'''
    
    tracker,coords,ADL = 3*(None,)
    
    def __init__(self):

        if not self.read():
            self.ADL = self._initADL() 
            self.coords = {'sw':SW,'ne':NE}
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
        archive = [self.tracker,self.coords,self.ADL]
        pickle.dump(archive, open(localds,'wb'))


def test():
    try:
        dm = DataManager()
        test1(dm)
    finally:
        dm.close()
        
def test1(dm):
    #cd <path>/git/SP-QGIS-AIMS-Plugin/AIMSDataManager
    #import sys
    #from DataManager import DataManager
    #start DM
    print 'start'
    dm.persist.ADL = testdata
    #get some data
    dm.refresh()
    listofaddresses = dm.pull()
    #add
    time.sleep(5)
    aimslog.info('*** Main ADD '+str(time.clock()))
    addr_7 = Address._import(Address('ninenintyseven'))
    addr_8 = Address._import(Address('ninenintyeight'))
    addr_9 = Address._import(Address('ninenintynine'))
    listofaddresses[FeedType.FEATURES].append(addr_7)
    listofaddresses[FeedType.FEATURES].append(addr_8)
    listofaddresses[FeedType.FEATURES].append(addr_9)
    dm.push(listofaddresses)
    time.sleep(5)
    testresp(dm)
    #del
    time.sleep(5)
    aimslog.info('*** Main RETIRE '+str(time.clock()))
    addr_0 = listofaddresses[FeedType.FEATURES][0]
    addr_1 = listofaddresses[FeedType.FEATURES][1]
    listofaddresses[FeedType.FEATURES].remove(addr_0)
    listofaddresses[FeedType.FEATURES].remove(addr_1)
    dm.push(listofaddresses)
    time.sleep(5)
    testresp(dm)
    #chg
    time.sleep(5)
    aimslog.info('*** Main UPDATE '+str(time.clock()))
    addr_2 = listofaddresses[FeedType.FEATURES][2]
    addr_3 = listofaddresses[FeedType.FEATURES][3]
    addr_2.setVersion(2222)
    addr_3.setVersion(3333)
    #listofaddresses[FeedType.FEATURES][2].setVersion(123456)
    #listofaddresses[FeedType.FEATURES][3].setVersion(123457)
    dm.push(listofaddresses)
    time.sleep(5)
    testresp(dm)
    #shift
    time.sleep(5)
    aimslog.info('*** Main SHIFT '+str(time.clock()))
    dm.setbb(sw=(174.76918,-41.28515), ne=(174.79509,-41.26491))
    time.sleep(5)
    testresp(dm)
    time.sleep(5)
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
            

            
if __name__ == '__main__':
    test()  
