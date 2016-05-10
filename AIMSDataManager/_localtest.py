import os
import sys
import Queue
import pickle
import copy
import time
import pprint
import collections

from DataManager import DataManager
from AimsUtility import FeedRef,ActionType,ApprovalType,GroupActionType,GroupApprovalType,FeatureType,FeedType,Configuration,FEEDS,FIRST
from AimsLogging import Logger
from Const import THREAD_JOIN_TIMEOUT,RES_PATH,LOCAL_ADL,SWZERO,NEZERO,NULL_PAGE_VALUE as NPV
from Address import Address, AddressChange, AddressResolution,Position
from FeatureFactory import FeatureFactory
from DataSync import DataSync,DataSyncFeatures,DataSyncFeeds
from datetime import datetime as DT

aimslog = None

class LocalTest():
    flag = False    
    
    global aimslog
    aimslog = Logger.setup()
    
    def t2(self):
        #from Config import ConfigReader as CR
        import sys
        ref = sys.modules
        import Const# import const
        print Const.DEF_SEP
        
    
    def observe(self,observable,*args,**kwargs):
        self.flag = True
        print 'LOCALTEST observes:'
        print '*obs',observable
        print '*ARGS',args
        print '*KWARGS',kwargs
        
    def test(self):
        global refsnap
        refsnap = {0:None,1:None,2:None}
        af = {ft:FeatureFactory.getInstance(FeedRef((FeatureType.ADDRESS,ft))) for ft in (FeedType.FEATURES,FeedType.CHANGEFEED,FeedType.RESOLUTIONFEED)}
        gf = {ft:FeatureFactory.getInstance(FeedRef((FeatureType.GROUPS,ft))) for ft in (FeedType.CHANGEFEED,FeedType.RESOLUTIONFEED)}
        af[3] = FeatureFactory.getInstance(FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)))
        #with DataManager(start=None) as dm:
        #    dm.start(FeedType.CHANGEFEED)
        with DataManager() as dm:
            dm.registermain(self)
            self.test1(dm,af)
            
            
    def test1(self,dm,af):
        #time.sleep(100000) 
        #dm.persist.ADL = testdata
        #get some data
        listofaddresses = dm.pull()
        print 'addr list before feed checkin',[len(l) for l in listofaddresses.values()]
        
        #TEST RESTART
        self.testrestartCR(dm)
        
        #TEST SHIFT
        self.testfeatureshift(dm)
        
        # TEST ACF
        self.testchangefeedAUR(dm,af)
        
        # TEST ARF
        #self.testresolutionfeedAUD(dm,af)        
        
        # TEST GRF
        #self.testgrpresfeedAUD(dm,af)
        
        #TEST SHIFT
        #self.testfeatureshift(dm)
        
        aimslog.info('*** Resolution ADD '+str(time.clock()))   
        time.sleep(30) 
        #return
        print 'entering response mode'
        countdown = 10
        while countdown:
            aimslog.info('*** Main TICK '+str(time.clock()))
            self.testresp(dm)
            time.sleep(30)
            countdown -= 1
            
    def testfeatureshift(self,dm):
    
        aimslog.info('*** Main SHIFT '+str(time.clock()))
        dm.setbb(sw=(174.76918,-41.28515), ne=(174.79509,-41.26491))
        #time.sleep(60)
        resp = None
        while not self.flag: 
            time.sleep(5)   
        else:
            r1,r2 = self.testresp(dm) 
            
        dm.setbb(sw=(174.76928,-41.28515), ne=(174.79519,-41.26481))
        time.sleep(60)
        resp = None
        while not self.flag: 
            time.sleep(5)   
        else:
            r1,r2 = self.testresp(dm) 
            
        dm.setbb(sw=(174.76928,-41.28515), ne=(174.79529,-41.26471))
        time.sleep(60)
        resp = None
        while not self.flag: 
            time.sleep(5)   
        else:
            r1,r2 = self.testresp(dm)
        
    def testrestartCR(self,dm):
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
        addr_f = self.gettestaddress(af[FeedType.FEATURES])
        #cast to addresschange type, to do cf ops
        addr_c = dm.castTo(FeedType.CHANGEFEED,addr_f)
        #addr_c.setVersion(ver)
#         aimslog.info('*** Change ADD '+str(time.clock()))
#         rqid1 = 1234321
#         dm.addAddress(addr_c,rqid1)
#         resp = None
#         tout = 10
#         while True: 
#             resp,_ = self.testresp(dm,FeedType.CHANGEFEED)
#             if resp: 
#                 err = resp[0].getErrors()
#                 print rqid1,resp[0].meta.requestId
#                 print 'e',err
#                 if not err:
#                     cid = resp[0].getChangeId()
#                 break
#             if not tout: break
#             tout +- 1
#             time.sleep(5)
#         ver += 1
#        
#            
#         aimslog.info('*** Change UPDATE '+str(time.clock()))
#         rqid2 = 2345432
#         addr_c.setFullAddress('Unit C, 16 Islay Street, Glenorchy')
#         #addr_c.setChangeId(cid)
#         #addr_c.setVersion(ver)
#         dm.updateAddress(addr_c,rqid2)
#         resp = None
#         tout = 10
#         while True: 
#             resp,_ = self.testresp(dm,FeedType.CHANGEFEED)
#             if resp: 
#                 err = resp[0].getErrors()
#                 print rqid2,resp[0].meta.requestId
#                 print 'e',err
#                 if not err:
#                     cid = resp[0].getChangeId()
#                 break
#             if not tout: break
#             tout -= 1
#             time.sleep(5)
#         ver += 1
#         
        
        aimslog.info('*** Change RETIRE '+str(time.clock()))
        rqid3 = 3456543
        #addr_c.setChangeId(1837997)#cid)
        #addr_c.setVersion(ver)
        addr_c.setAddressId(20)#1,10,9,8
        dm.retireAddress(addr_c,rqid3)
        resp = None
        tout = 10
        while True: 
            resp,_ = self.testresp(dm,FeedType.CHANGEFEED)
            if resp: 
                err = resp[0].getErrors()
                print rqid3,resp[0].meta.requestId
                print 'e',err
                if not err:
                    cid = resp[0].getChangeId()
                break
            if not tout: break
            tout -= 1
            time.sleep(5)     
        ver += 1
        
    def testresolutionfeedAUD(self,dm,af):
        ver = 6977370
        #cid = 4117724
        cid = 4117720
        #pull address from features (map)
        addr_f = self.gettestaddress(af[FeedType.FEATURES])
        #cast to addresschange type, to do cf ops
        addr_r = dm.castTo(FeedType.RESOLUTIONFEED,addr_f)
        #addr_r = af[FeedType.RESOLUTIONFEED].cast(addr_f)
        #addr_r.setVersion(ver)
        addr_r.setChangeId(cid)
        
        aimslog.info('*** Resolution ACCEPT '+str(time.clock()))
        rqid1 = 4567654
        dm.acceptAddress(addr_r,rqid1)
        resp = None
        while True: 
            resp,_ = self.testresp(dm,FeedType.RESOLUTIONFEED)
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
            resp,_ = self.testresp(dm,FeedType.RESOLUTIONFEED)
            if resp: 
                print rqid2,resp[0].meta.requestId
                break
            time.sleep(5)
        ver += 1
        
        
        aimslog.info('*** Resolution DECLINE '+str(time.clock()))
        rqid3 = 6789876
        #addr_r.setVersion(ver)
        dm.declineAddress(addr_r,rqid3)
        resp = None
        while not resp: 
            resp,_ = self.testresp(dm,FeedType.RESOLUTIONFEED)
            if resp: 
                print rqid3,resp[0].meta.requestId
                break
            time.sleep(5)     
        ver += 1
            
    def testgrpresfeedAUD(self,dm,af):
        ver = 6977370
        #cid = 4117724
        cid = 4117720
        #pull address from features (map)
        grp_r = self.gettestgroup(FeatureFactory.getInstance(FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED))))
        
        aimslog.info('*** GROUP Resolution ACCEPT '+str(time.clock()))
        rqid1 = 4321234
        dm.acceptGroup(grp_r,rqid1)
        resp = None
        while True: 
            _,resp = self.testresp(dm,FeedType.RESOLUTIONFEED)
            if resp: 
                print rqid1,resp[0].meta.requestId
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
        
        etft = FeedRef((FeatureType.ADDRESS,ft))
        resp1 = dm.response(etft)
        for r in resp1:
            #aimslog.info('*** Main RESP {} - [{}]'.format(r,len(resp1))) 
            aimslog.info('*** Main RESP {} [{}]'.format(r,len(resp1)))        
            
        etft = FeedRef((FeatureType.GROUPS,ft))
        resp2 = dm.response(etft)
        for r in resp2:
            #aimslog.info('*** Main RESP {} - [{}]'.format(r,len(res2p))) 
            aimslog.info('*** Main GROUP RESP {} [{}]'.format(r,len(resp2)))
            
        return resp1,resp2
                
    def gettestaddress(self,ff):
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
        a.setFullAddressNumber('17')
        a.setFullRoadName('Islay Street')
        a.setFullAddress('17 Islay Street, Glenorchy')
        a._addressedObject_addressableObjectId = '1416143'
        a.setObjectType('Parcel')
        
        a.setUnitType('Unit')
        a.setUnitValue('b')
    
        a.setAddressPositions(p)
    
        a._codes_suburbLocalityId = '2104'
        a._codes_parcelId = '3132748'
        a._codes_meshblock = '3174100'
        return a

    
    def gettestgroup(self,ff):
        g = ff.getGroup('test_res_group')
        g.setChangeGroupId('4118268')#override this
        g.setVersion('9266184')#override this too
        return g
        
            
if __name__ == '__main__':
    print 'start'
    lt = LocalTest()
    #lt.t2()
    lt.test()  
    print 'finish'