'''
v.0.0.1

QGIS-AIMS-Plugin - DataManager_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on AimsUtility class

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

from AimsLogging import Logger
from AimsUtility import Configuration, IterEnum, Enumeration, FeedRef, FeatureType, FeedType, ApprovalType, ActionType, GroupActionType, GroupApprovalType, UserActionType
testlog = Logger.setup('test')

class Test_0_ConfigurationTest(unittest.TestCase):
    
    def setUp(self):
	self.conf = Configuration()
        
    def tearDown(self):
	self.conf = None
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertIsNotNone(testlog,'Testlog not instantiated')
        testlog.debug('DataSync Log')
        
    def test20_Config(self):
	self.assertIsNotNone(self.conf, 'Configuration not instantiated')
	self.assertTrue(isinstance(self.conf, Configuration), 'Configuration not instantiated correctly')
	
	self.assertEqual(self.conf.readConf()['url'], 'https://devassgeo01:8080/aims/api', 'Configuration url not correct')

    def test30_IterEnum(self):
	iteE = IterEnum()
	self.assertIsNotNone(iteE, 'IterEnum not instantiated')
	self.assertTrue(isinstance(iteE,IterEnum), 'IterEnum not instantiated correctly')
	
    def test40_EnumerationTest(self):
	e = Enumeration()
	self.assertIsNotNone(e, 'Enumeration not instantiated')
	self.assertTrue(isinstance(e,Enumeration), 'Enumeration not instantiated correctly')
	en = e.enum('FEATURES','CHANGEFEED','RESOLUTIONFEED','ADMIN')
	reversed = {0: 'FEATURES', 1: 'CHANGEFEED', 2: 'RESOLUTIONFEED', 3: 'ADMIN'}
	self.assertEqual(reversed, en.reverse, 'reverse not correctly returned')
	
    def test50_FeedRefTest(self):
	fReef = FeedRef([FeatureType.ADDRESS,FeedType.FEATURES])

	self.assertIsNotNone(fReef)
	self.assertEqual(str(fReef), "AddFea")
	
	self.assertEqual(fReef.k, 'address.features')
	self.assertEqual(FeatureType.reverse[fReef.et], 'ADDRESS')
	self.assertEqual(FeedType.reverse[fReef.ft], 'FEATURES')
	
	fReef2 = FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)
	self.assertIsNotNone(fReef2)
	self.assertEqual(str(fReef2), "AddFea")
	
	self.assertTrue(fReef.__eq__(fReef2))
	self.assertFalse(fReef.__ne__(fReef2))
	
	fReef2 = FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED)
	self.assertIsNotNone(fReef2)
	self.assertEqual(str(fReef2), "AddCha")
	
	self.assertEqual(fReef2.k, 'address.changefeed')
	self.assertEqual(FeatureType.reverse[fReef2.et], 'ADDRESS')
	self.assertEqual(FeedType.reverse[fReef2.ft], 'CHANGEFEED')
	
        fReef2 = FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED)
	self.assertIsNotNone(fReef2)
	self.assertEqual(str(fReef2), "AddRes")
	
	self.assertEqual(fReef2.k, 'address.resolutionfeed')
	self.assertEqual(FeatureType.reverse[fReef2.et], 'ADDRESS')
	self.assertEqual(FeedType.reverse[fReef2.ft], 'RESOLUTIONFEED')
	
	fReef2 = FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)
	self.assertIsNotNone(fReef2)
	self.assertEqual(str(fReef2), "GroCha")
	
	self.assertEqual(fReef2.k, 'groups.changefeed')
	self.assertEqual(FeatureType.reverse[fReef2.et], 'GROUPS')
	self.assertEqual(FeedType.reverse[fReef2.ft], 'CHANGEFEED')
	
	fReef2 = FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED)
	self.assertIsNotNone(fReef2)
	self.assertEqual(str(fReef2), "GroRes")
	
	self.assertEqual(fReef2.k, 'groups.resolutionfeed')
	self.assertEqual(FeatureType.reverse[fReef2.et], 'GROUPS')
	self.assertEqual(FeedType.reverse[fReef2.ft], 'RESOLUTIONFEED')
	
	fReef2 = FeedRef(FeatureType.USERS, FeedType.ADMIN)
	self.assertIsNotNone(fReef2)
	self.assertEqual(str(fReef2), "UseAdm")
	
	self.assertEqual(fReef2.k, 'users.admin')
	self.assertEqual(FeatureType.reverse[fReef2.et], 'USERS')
	self.assertEqual(FeedType.reverse[fReef2.ft], 'ADMIN')
	
	self.assertFalse(fReef.__eq__(fReef2))
	self.assertTrue(fReef.__ne__(fReef2))
	

    def test60_FeedFeatureTypesTest(self):
	self.assertEqual(len(FeedType.reverse), 4)
	
	self.assertEqual(len(FeatureType.reverse), 3)
	
	self.assertEqual(len(ActionType.reverse), 3)
	
	self.assertEqual(len(ApprovalType.reverse), 4)
	
	self.assertEqual(len(GroupActionType.reverse), 7)
	
	self.assertEqual(len(GroupApprovalType.reverse), 4)
	
	self.assertEqual(len(UserActionType.reverse), 3)


if __name__ == "__main__":
    unittest.main()