'''
v.0.0.1

QGIS-AIMS-Plugin - DataManager_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on DataUpdater class

Created on 21/01/2016

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

from DataUpdater import DataUpdater, DataUpdaterAddress, DataUpdaterGroup, DataUpdaterUser, DataUpdaterDRC, DataUpdaterAction, DataUpdaterApproval, DataUpdaterGroupApproval, DataUpdaterUserAction, DataUpdaterGroupAction
from AimsLogging import Logger
from AimsUtility import FeedType, FeatureType, FeedRef, ActionType
from AddressFactory import AddressFactory
from Address import Position
from GroupFactory import GroupFactory
from UserFactory import UserFactory

testlog = Logger.setup('test')

class Test_0_DataUpdaterSelfTest(unittest.TestCase):
    
    def setUp(self):
	self.params = [1, 2, 3]
	self.queue = None
        self.du = DataUpdater(self.params, self.queue) 
        
    def tearDown(self):
        self.du = None
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('DataUpdater Log')
        
    def test20_dataUpdaterTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 DataUpdater instantiation test')
        self.assertIsNotNone(self.du,'DataUpdater not instantiated')
        self.assertTrue(isinstance(self.du, DataUpdater), 'DataUpdater not instantiated correctly')
        
    def test30_getInstanceTest(self):
	address = FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)
	group = FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)
	user = FeedRef(FeatureType.USERS, FeedType.ADMIN)

	self.assertEqual(self.du.getInstance(address), DataUpdaterAddress, 'Incorrect data updater address instance')
	self.assertEqual(self.du.getInstance(group), DataUpdaterGroup, 'Incorrect data updater group instance')
	self.assertEqual(self.du.getInstance(user), DataUpdaterUser, 'Incorrect data updater user instance')
	
    def test40_dataUpdaterInstance(self):
	dua = DataUpdaterAddress(self.params, self.queue)
	self.assertTrue(isinstance(dua, DataUpdaterAddress), 'DataUpdaterAddress instantiation incorrect')
	dug = DataUpdaterGroup(self.params, self.queue)
	self.assertTrue(isinstance(dug, DataUpdaterGroup), 'DataUpdaterGroup instantiation incorrect')
	duu = DataUpdaterUser(self.params, self.queue)
	self.assertTrue(isinstance(duu, DataUpdaterUser), 'DataUpdaterUser instantiation incorrect')
	
    def test50_dataUpdaterDRC(self):
	drc = DataUpdaterDRC(self.params, self.queue)
	self.assertTrue(isinstance(drc, DataUpdaterDRC), 'DataUpdaterDRC instantiation incorrect')
	
	duaDRC = DataUpdaterAction(self.params, self.queue)
	self.assertTrue(isinstance(duaDRC, DataUpdaterAction), 'DataUpdaterAction instantiation incorrect')
	address = _getTestAddress(AddressFactory(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)))
	duaDRC.setup(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES), ActionType.ADD, address, '')
	self.assertEqual(duaDRC.identifier, '29', 'Address Id does not match')
	
	duapDRC = DataUpdaterApproval(self.params, self.queue)
	self.assertTrue(isinstance(duapDRC, DataUpdaterApproval), 'DataUpdaterApproval instantiation incorrect')
	address._changeId = 1
	duapDRC.setup(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES), ActionType.UPDATE, address, '')
	self.assertEqual(duapDRC.identifier, 1, 'Change Id does not match')
	
	dugaDRC = DataUpdaterGroupAction(self.params, self.queue)
	self.assertTrue(isinstance(dugaDRC, DataUpdaterGroupAction), 'DataUpdaterGroupAction instantiation incorrect')
	group = GroupFactory(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)).get()
	group.setChangeGroupId(10)
	dugaDRC.setup(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED), ActionType.UPDATE, group, '')
	self.assertEqual(dugaDRC.identifier, 10, 'Change group Id does not match')
	
	dugapDRC = DataUpdaterGroupApproval(self.params, self.queue)
	self.assertTrue(isinstance(dugapDRC, DataUpdaterGroupApproval), 'DataUpdaterGroupApproval instantiation incorrect')
	group = GroupFactory(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)).get()
	group.setChangeGroupId(12)
	dugapDRC.setup(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED), ActionType.UPDATE, group, '')
	self.assertEqual(dugapDRC.identifier, 12, 'Change group Id does not match')
	
	duuaDRC = DataUpdaterUserAction(self.params, self.queue)
	self.assertTrue(isinstance(duuaDRC, DataUpdaterUserAction), 'DataUpdaterUserAction instantiation incorrect')
	user = UserFactory(FeedRef(FeatureType.USERS, FeedType.ADMIN)).get()
	user.setUserId(15)
	duuaDRC.setup(FeedRef(FeatureType.USERS, FeedType.ADMIN), ActionType.UPDATE, user, '')
	self.assertEqual(duuaDRC.identifier, 15, 'User Id does not match')
	
      
	

	
	
        
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