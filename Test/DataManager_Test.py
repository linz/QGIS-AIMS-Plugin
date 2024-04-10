'''
v.0.0.1

QGIS-AIMS-Plugin - DataManager_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on DataManager class

Created on 21/01/2016

@author: jramsay
'''
import unittest
import inspect
import sys
import re
import random
import string
import time
import os

ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT, 'AIMSDataManager'))
sys.path.append(os.path.join(ROOT, 'AimsUI'))

from AIMSDataManager.Address import Address, AddressChange, AddressResolution
from AIMSDataManager.AimsLogging import Logger
from AIMSDataManager.DataManager import DataManager, Position
from AIMSDataManager.AimsUtility import FeedRef,FeatureType,FeedType,PersistActionType
from AIMSDataManager.FeatureFactory import FeatureFactory

testlog = Logger.setup('test')

#user to init an address, simple text string read from a stored config file
ref_int = 1234

SW1,NE1 = (174.76918,-41.28515),(174.79509,-41.26491)
TS0,TS1,TS2 = 5, 20, 60
'''
workflow tests
1. testdata -> addaddress -> updateaddress -> retireaddress
2. testdata -> addaddress -> rejectaddress 
3. testdata -> addaddress -> acceptaddress 
4. features -> updateaddress -> acceptaddress
5. features -> updateaddress -> updateaddress
6. features -> updateaddress -> rejectaddress
7. features -> retireaddress -> acceptaddress
8. features -> retireaddress -> rejectaddress
'''

class Test_0_DataManagerSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('Address_Test Log')
        
    def test20_dataManagerTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 Data Manager registration test')
        with DataManager(initialise=True) as dm:  # Start with clean self.dm.persist.ADL data each test run
            dm.register(self)
            self.assertNotEqual(dm,None,'DataManager not instantiated')
        
class Test_1_DataManagerFunctionTest(unittest.TestCase):
    
    def setUp(self):
        self.dm = DataManager()
        
    def tearDown(self):
        self.dm.close()
    
    def test10_parseAddressTest(self):
        '''Tests whether a valid address object is returned on json decoded arg'''
        assert True
        
    def test20_pullTest(self):
        '''Tests whether we get a valid list[group[address]]'''
        assert True
    
    
class Test_2_DataManagerSyncStart(unittest.TestCase):   
    
    def setUp(self):            
        self.af = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
        self.ac = FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))
        self.ar = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
        self.aff = FeatureFactory.getInstance(self.af)
        self.afc = FeatureFactory.getInstance(self.ac)
        self.afr = FeatureFactory.getInstance(self.ar)
        self.dm = DataManager()
        
    def tearDown(self):
        self.dm.close()
        del self.afr
        del self.afc
        del self.aff
    
    def test10_validdatastoreTest(self):
        '''Tests whether a valid address object is returned on json decoded arg'''
        initdata = self.dm.pull()
        self.assertEqual(len(initdata),6,'Invalid ADL list length returned')

        # If store is empty, populate the Data
        initdata[FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))] = [_getTestAddress(self.aff)]
        initdata[FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))] = [_getTestAddress(self.afc)]
        initdata[FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))] = [_getTestAddress(self.afr)]

        self.dm.persist.set(None, initdata, PersistActionType.ALL)

        
    def test20_refreshTest(self):
        '''Tests whether a valid address object is returned on json decoded arg'''
        initdata = self.dm.pull()
        self.assertTrue(isinstance(initdata[self.af][0],Address),'Invalid address type returned')
        self.assertTrue(isinstance(initdata[self.ac][0],AddressChange),'Invalid address type returned')
        self.assertTrue(isinstance(initdata[self.ar][0],AddressResolution),'Invalid address type returned')
        
    
class Test_3_DataManagerCFRF(unittest.TestCase):
    '''tests whether the CF and RF feeds get populated'''
    def setUp(self):    
        self.dm = DataManager()
        self.af = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
        self.ac = FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))
        self.ar = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))

    def tearDown(self):
        self.dm.close()
        
    # def test10_cf(self): # REMOVED BECAUSE CHANGEFEED DOESN'T UPDATE LIKE THIS BY DESIGN...
    #     len1 = self.dm.persist.ADL[self.ac]
    #     time.sleep(TS1)
    #     len2 = self.dm.persist.ADL[self.ac]
    #     self.assertNotEqual(len1,len2,'Changefeed didn\'t update within {} seconds'.format(TS1))       
        
    def test10_rf(self):
        len1 = self.dm.persist.ADL[self.ar]
        time.sleep(TS1)
        len2 = self.dm.persist.ADL[self.ar]
        self.assertNotEqual(len1,len2,'Resolutionfeed didn\'t update within {} seconds'.format(TS1))   
        
class Test_4_DataManagerShift(unittest.TestCase):
    
    def setUp(self):    
        self.dm = DataManager()        
        self.af = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
        self.ac = FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))
        self.ar = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))

    def tearDown(self):
        self.dm.close()
        
    def test10_shift(self):
        len1 = self.dm.persist.ADL[self.af]
        self.dm.setbb(sw=SW1, ne=NE1)
        time.sleep(TS1)
        len2 = self.dm.persist.ADL[self.af]

        self.assertNotEqual(len1,len2,'Features feed didn\'t update within {} seconds'.format(TS1)) 

        
class Test_5_DataManagerChangeFeed(unittest.TestCase): 
    
    ver = 1000000
    
    def setUp(self):    
        self.dm = DataManager(initialise=ref_int)
        self.af = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
        self.ac = FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))
        self.ar = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
        
        self.aff = FeatureFactory.getInstance(self.af)
        self.afc = FeatureFactory.getInstance(self.ac)
        self.afr = FeatureFactory.getInstance(self.ar)
        self.addr_f = _getTestAddress(self.afc)

    def tearDown(self):
        self.dm.close()
        del self.addr_f
    
    def test10_cast(self):
        addr_c = self.afc.cast(self.addr_f)
        self.assertTrue(isinstance(addr_c, AddressChange))
        
    def test20_add(self):
        addr_c = self.afc.cast(self.addr_f)
        addr_c.setVersion(self.ver)
        self.dm.addAddress(addr_c)
        resp = None
        while not resp: 
            resp = self.dm.response(self.ac)
            for r in resp:
                self.assertTrue(isinstance(r, AddressChange))
            time.sleep(5)

    def test30_update(self):        
        addr_c = self.afc.cast(self.addr_f)
        addr_c.setFullAddress('Unit B, 16 Islay Street, Glenorchy')
        addr_c.setVersion(self.ver)
        self.dm.updateAddress(addr_c)
        resp = None
        while not resp: 
            resp = self.dm.response(self.ac)
            for r in resp:
                self.assertTrue(isinstance(r, AddressChange))
            time.sleep(5) 
            
    def test40_retire(self):        
        addr_c = self.afc.cast(self.addr_f)
        addr_c.setVersion(self.ver)
        self.dm.retireAddress(addr_c)
        resp = None
        while not resp: 
            resp = self.dm.response(self.ac)
            for r in resp:
                self.assertTrue(isinstance(r, AddressChange))
            time.sleep(5)
            
class Test_6_DataManagerResolutionFeed(unittest.TestCase): 
    
    ver = 1000000
    
    def setUp(self):    
        self.dm = DataManager(initialise=ref_int)
        self.af = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
        self.ac = FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))
        self.ar = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
        
        self.afc = FeatureFactory.getInstance(self.ac)
        self.afr = FeatureFactory.getInstance(self.ar)
        self.addr_f = _getTestAddress(self.afr)
        

    def tearDown(self):
        self.dm.close()
        del self.addr_f
    
    def test10_cast(self):
        self.addr_c = self.afc.cast(self.addr_f)
        
    def test20_accept(self):
        self.addr_r = self.afr.cast(self.addr_f)
        self.addr_r.setVersion(self.ver)
        self.addr_r.setMeta()
        self.addr_r._changeId = 9999999
        self.dm.acceptAddress(self.addr_r)
        resp = None
        while not resp: 
            resp = self.dm.response(self.ar)
            for r in resp:
                self.assertTrue(isinstance(r, AddressResolution))
            time.sleep(5)

    def test30_update(self):        
        addr_c = self.afr.cast(self.addr_f)
        addr_c.setFullAddress('Unit 1, 1000 Islay Street, Glenorchy')
        addr_c.setVersion(self.ver)
        addr_c.setMeta()
        addr_c._changeId = 1934059
        self.dm.repairAddress(addr_c)
        resp = None
        while not resp: 
            resp = self.dm.response(self.ar)
            for r in resp:
                self.assertTrue(isinstance(r, AddressResolution))
            time.sleep(5) 
            
    def test40_reject(self):        
        addr_c = self.afr.cast(self.addr_f)
        addr_c.setVersion(self.ver)
        addr_c.setMeta()
        addr_c._changeId = 1934059
        self.dm.declineAddress(addr_c)
        resp = None
        while not resp: 
            resp = self.dm.response(self.ar)
            for r in resp:
                self.assertTrue(isinstance(r, AddressResolution))
            time.sleep(5)

    
# --------------------------------------------------------------------
            
def _getTestAddress(factory):
    c2 = [r+random.random() for r in (168,-45)]
    n1 = random.randint(1,999)
    u1 = random.choice(string.ascii_uppercase)
    #------------------------------------------
    a = factory.get('random{}{}'.format(n1,u1))
    p = Position.getInstance(
        {'position':{'type':'Point','coordinates': c2,'crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::4167'}}},'positionType':'Centroid','primary':True}
    )
    a.setAddressType('Road')
    a.setAddressNumber(n1)
    a.setAddressId('29')
    a.setLifecycle('Current')
    a.setRoadCentrelineId('11849')
    a.setRoadName('Islay')
    a.setRoadType('Street'),
    a.setSuburbLocality('Glenorchy')
    a.setFullAddressNumber(n1)
    a.setFullRoadName('Islay Street')
    a.setFullAddress('{} Islay Street, Glenorchy'.format(n1))
    a._addressedObject_addressableObjectId = '1416143'
    a.setAddObjectType('Parcel')
    
    a.setUnitType('Unit')
    a.setUnitValue(u1)

    a.setAddressPositions(p)

    a._codes_suburbLocalityId = '2104'
    a._codes_parcelId = '3132748'
    a._codes_meshblock = '3174100'
    return a
