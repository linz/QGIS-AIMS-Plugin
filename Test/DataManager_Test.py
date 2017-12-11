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
@author: aross
'''
import unittest
import inspect
import sys
import re
import random
import string
import time

sys.path.append('../AIMSDataManager/')

from AddressFactory import AddressFactory, AddressChangeFactory, AddressResolutionFactory
from Address import Address, Position, AddressChange, AddressResolution
from AimsLogging import Logger
from DataManager import DataManager
from AimsUtility import FeedRef,FeatureType,FeedType
from FeatureFactory import FeatureFactory
from Group import Group, GroupChange, GroupResolution
from GroupFactory import GroupFactory
from User import User

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
        testlog.debug('Test_0.20 Address instantiation test')
        with DataManager() as dm: 
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
    
    def test30_validdatastoreTest(self):
        '''Tests whether a valid address object is returned on json decoded arg'''
        initdata = self.dm.pull()
        self.assertIsNotNone(initdata,'Data manager pull incorrect')
        self.assertEquals(len(initdata),6,'Invalid ADL list length returned')
        
        self.assertTrue(isinstance(self.dm, DataManager), 'Data Manager not instantiated correctly')
    
    def test40_AddressPullTest(self):

	test = self.dm.startfeed(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES))
	self.assertTrue(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES) in self.dm.ds, 'StartFeed not correct')
	
	a = _getTestAddress(AddressFactory(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)))
	b = _getTestAddress(AddressChangeFactory(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED)))
	c = _getTestAddress(AddressResolutionFactory(FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED)))

	self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)] += [a]
	self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED)] += [b]
	self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED)] += [c]
	
	initdata = self.dm.pull()
	self.assertTrue(isinstance(initdata[FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)][0],Address), 'Invalid address returned')
	self.assertTrue(isinstance(initdata[FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED)][0], AddressChange), 'Invalid address returned')
	self.assertTrue(isinstance(initdata[FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED)][0], AddressResolution), 'Invalid address returned')
	

class Test_3_DataManagerCFRF(unittest.TestCase):
    '''tests whether the CF and RF feeds get populated'''
    def setUp(self):    
        self.dm = DataManager()
        self.af = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
        self.ac = FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))
        self.ar = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))

    def tearDown(self):
        self.dm.close()
        self.dm = None
        self.af = None
        self.ac = None
        self.ar = None
     
    @unittest.skip("Doesn't update since no address stored?") 
    def test10_cf(self):
        len1 = self.dm.persist.ADL[self.ac]
        print(len1)
        time.sleep(TS1)
        len2 = self.dm.persist.ADL[self.ac]
        print(len2)
        self.assertNotEqual(len1,len2,'Changefeed didn\'t update within {} seconds'.format(TS1))       
        
    @unittest.skip("same problem as test10_cf")
    def test20_rf(self):
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
        self.dm = None
        self.af = None
        self.ac = None
        self.ar = None
        
    @unittest.skip("same problem as test10_cf and test20_rf")    
    def test10_shift(self):
        len1 = self.dm.persist.ADL[self.af]
        self.dm.setbb(sw=SW1, ne=NE1)
        time.sleep(TS1)
        len2 = self.dm.persist.ADL[self.af]

        self.assertNotEqual(len1,len2,'Features feed didn\'t update within {} seconds'.format(TS1)) 

        
class Test_5_DataManagerChangeFeed(unittest.TestCase): 
    
    def setUp(self):    
        self.dm = DataManager()#ref_int)
        self.af = AddressFactory(FeedRef(FeatureType.ADDRESS,FeedType.FEATURES))
        self.ac = FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))
        self.ar = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
        
        self.afc = FeatureFactory.getInstance(self.ac)
        self.afr = FeatureFactory.getInstance(self.ar)
        self.addr_f = _getTestAddress(self.af)
        self.addr_f2 = _getTestAddress(self.af)

        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)] += [self.addr_f]
        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)] += [self.addr_f2]
        
        self.ver = 1000000

    def tearDown(self):
        self.dm.close()
        del self.addr_f
        self.dm = None
        self.af = None
        self.ac = None
        self.ar = None
        self.afc = None
        self.afr = None
    
    def test10_cast(self):
        addr_c = self.afc.cast(self.addr_f)
        self.assertTrue(isinstance(addr_c,AddressChange))
    
    def test20_add(self):
        addr_c = self.afc.cast(self.addr_f)
        addr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED)] += [addr_c]
        self.dm.addAddress(addr_c)
        
        mon = None
        mon = self.dm._monitor(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED))
        for m in mon:
	  self.assertTrue(isinstance(m, AddressChange))


    def test30_update(self):        
        addr_c = self.afc.cast(self.addr_f)
        addr_c.setFullAddress('Unit B, 16 Islay Street, Glenorchy')
        addr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED)] += [addr_c]
        self.dm.updateAddress(addr_c)
        
        mon = self.dm._monitor(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED))
	for m in mon:
	  self.assertTrue(isinstance(m, AddressChange))
            
 
    def test30_retire(self):        
        addr_c = self.afc.cast(self.addr_f)
        addr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED)] += [addr_c]
        self.dm.retireAddress(addr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED))
	for m in mon:
	  self.assertTrue(isinstance(m, AddressChange))
	  



class Test_6_DataManagerResolutionFeed(unittest.TestCase): 
    
    ver = 1000000
    
    def setUp(self):    
        self.dm = DataManager()#ref_int)
        self.af = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
        self.ac = FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED))
        self.ar = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
        
        self.afc = FeatureFactory.getInstance(self.ac)
        self.afr = FeatureFactory.getInstance(self.ar)
        self.addr_f = _getTestAddress(AddressFactory(self.af))
        

    def tearDown(self):
        self.dm.close()
        del self.addr_f
    
    def test10_cast(self):
        addr_c = self.afc.cast(self.af)
        self.assertTrue(isinstance(addr_c, AddressChange))
        addr_r = self.afr.cast(self.af)
        self.assertTrue(isinstance(addr_r, AddressResolution))
        

    def test20_accept(self):
        addr_c = self.afr.cast(self.addr_f)
        addr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED)] += [addr_c]
        self.dm.acceptAddress(addr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, AddressResolution))
          
    def test30_decline(self):        
        addr_c = self.afr.cast(self.addr_f)
        addr_c.setFullAddress('Unit 1, 1000 Islay Street, Glenorchy')
        addr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED)] += [addr_c]
        self.dm.declineAddress(addr_c)
        
        mon = self.dm._monitor(FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, AddressResolution))
	  
	  
    def test30_repair(self):        
        addr_c = self.afr.cast(self.addr_f)
        addr_c.setFullAddress('Unit 1, 1000 Islay Street, Glenorchy')
        addr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED)] += [addr_c]
        self.dm.repairAddress(addr_c)
        
        mon = self.dm._monitor(FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, AddressResolution))
	  
    def test30_supplement(self):        
        addr_c = self.afr.cast(self.addr_f)
        addr_c.setFullAddress('Unit 1, 1000 Islay Street, Glenorchy')
        addr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED)] += [addr_c]
        self.dm.supplementAddress(addr_c)
        
        mon = self.dm._monitor(FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, AddressResolution))

class Test_6_DataManagerGroupChangeFeed(unittest.TestCase): 
    
    ver = 1000000
    
    def setUp(self):    
        self.dm = DataManager()
        self.gc = FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED))
        self.gr = FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED))
        
        self.gfc = FeatureFactory.getInstance(self.gc)
        self.gfr = FeatureFactory.getInstance(self.gr)
        self.group_c = self.gfc.get()
        

    def tearDown(self):
        self.dm.close()
        del self.group_c       

    def test10_replace(self):
        gr_c = self.gfc.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)] += [gr_c]
        self.dm.replaceGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupChange))


    def test20_update(self):
        gr_c = self.gfc.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)] += [gr_c]
        self.dm.updateGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupChange))
	  
	  
    def test30_submit(self):
        gr_c = self.gfc.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)] += [gr_c]
        self.dm.submitGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupChange))
	  
	  
    def test40_close(self):
        gr_c = self.gfc.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)] += [gr_c]
        self.dm.closeGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupChange))
	  
    def test50_add(self):
        gr_c = self.gfc.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)] += [gr_c]
        self.dm.addGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupChange))
	  
    def test60_remove(self):
        gr_c = self.gfc.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)] += [gr_c]
        self.dm.removeGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupChange))
	  
	  
class Test_6_DataManagerGroupResolutionFeed(unittest.TestCase): 
	  
    ver = 1000000
    
    def setUp(self):    
        self.dm = DataManager()
        self.gc = FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED))
        self.gr = FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED))
        
        self.gfc = FeatureFactory.getInstance(self.gc)
        self.gfr = FeatureFactory.getInstance(self.gr)
        self.group_c = self.gfc.get()
        

    def tearDown(self):
        self.dm.close()
        del self.group_c       

    def test10_accept(self):
        gr_c = self.gfr.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED)] += [gr_c]
        self.dm.acceptGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupResolution))


    def test20_decline(self):
        gr_c = self.gfr.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED)] += [gr_c]
        self.dm.declineGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupResolution))
	  
	  
    def test30_repair(self):
        gr_c = self.gfr.cast(self.group_c)
        gr_c.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED)] += [gr_c]
        self.dm.repairGroup(gr_c)
        
	mon = self.dm._monitor(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
	
	for m in mon:
	  self.assertTrue(isinstance(m, GroupResolution))
    
class Test_6_DataManagerUserAdmin(unittest.TestCase): 
    ver = 1000000
    
    def setUp(self):    
        self.dm = DataManager()
        self.au = FeedRef((FeatureType.USERS,FeedType.ADMIN))
        
        self.auf = FeatureFactory.getInstance(self.au)
        self.user = self.auf.get()
        

    def tearDown(self):
        self.dm.close()
        del self.user       

    def test10_add(self):
        ur = self.user
        ur.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.USERS, FeedType.ADMIN)] += [ur]
        self.dm.addUser(ur)
        
	mon = self.dm._monitor(FeedRef(FeatureType.USERS, FeedType.ADMIN))
	
	for m in mon:
	  self.assertTrue(isinstance(m, User))
  
    def test20_remove(self):
        ur = self.user
        ur.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.USERS, FeedType.ADMIN)] += [ur]
        self.dm.removeUser(ur)
        
	mon = self.dm._monitor(FeedRef(FeatureType.USERS, FeedType.ADMIN))
	
	for m in mon:
	  self.assertTrue(isinstance(m, User))
	  
    def test30_update(self):
        ur = self.user
        ur.setVersion(self.ver)
        self.dm.persist.ADL[FeedRef(FeatureType.USERS, FeedType.ADMIN)] += [ur]
        self.dm.updateUser(ur)
        
	mon = self.dm._monitor(FeedRef(FeatureType.USERS, FeedType.ADMIN))
	
	for m in mon:
	  self.assertTrue(isinstance(m, User))

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
    a.setMeta()
    return a

if __name__ == "__main__":
    unittest.main()
