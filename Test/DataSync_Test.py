'''
v.0.0.1

QGIS-AIMS-Plugin - DataManager_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on DataSync class

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

from DataSync import DataSync, DataSyncFeatures, DataSyncFeeds, DataSyncAdmin, DataRequestChannel
from AimsLogging import Logger
from AimsUtility import FeedType, FeatureType, FeedRef, ActionType

testlog = Logger.setup('test')

class Test_0_DataSyncSelfTest(unittest.TestCase):
    
    def setUp(self):
	self.params = [1, FeedRef(FeatureType.ADDRESS, FeedType.FEATURES), 3, 4]
	self.queue = {'in':[], 'out':[], 'resp':[]}
        self.ds = DataSync(self.params, self.queue) 
        
    def tearDown(self):
	self.ds.close()
        self.ds = None
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertIsNotNone(testlog,'Testlog not instantiated')
        testlog.debug('DataSync Log')
        
    def test20_dataSyncTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 DataSync instantiation test')
        self.assertIsNotNone(self.ds,'DataSync not instantiated')
        self.assertTrue(isinstance(self.ds, DataSync), 'DataSync not instantiated correctly')
        
        self.ds.setup()
        self.assertIsNone(self.ds.sw)
        self.ds.setup([0,0])
        
        self.assertEqual(self.ds.sw, [0,0])
        self.assertIsNone(self.ds.ne)
        
        self.ds.setup([0,0], [3,3])
        self.assertEqual(self.ds.sw, [0,0])
        self.assertEqual(self.ds.ne, [3,3])
        
    def test30_dataSyncFeaturesTest(self):
	dsF = DataSyncFeatures(self.params, self.queue)
	self.assertIsNotNone(dsF, 'DataSyncFeatures instantiation test')
      
	self.assertTrue(isinstance(dsF, DataSyncFeatures), 'DataSyncFeatures not instantiated correctly')
      
      
    def test40_dataSyncFeedsTest(self):
	dsFee = DataSyncFeeds(self.params, self.queue)
	self.assertIsNotNone(dsFee, 'DataSyncFeeds instantiation test')
      
	self.assertTrue(isinstance(dsFee, DataSyncFeeds), 'DataSyncFeeds not instantiated correctly')
    
    
    def test50_dataSyncAdminTest(self):
	dsa = DataSyncAdmin(self.params, self.queue)
	self.assertIsNotNone(dsa, 'DataSyncAdmin instantiation test')
	
	self.assertTrue(isinstance(dsa, DataSyncAdmin), 'DataSyncAdmin not instantiated correctly')
	
    def test60_dataRequestChannelTest(self):
	drc = DataRequestChannel(DataSyncFeeds(self.params, self.queue))
	self.assertIsNotNone(drc, 'DataRequestChannel instantiation test')
	
	self.assertTrue(isinstance(drc, DataRequestChannel), 'DataRequestChannel not instantiated correctly')
	self.assertFalse(drc.stopped(), 'Data Request stopped')
	drc.stop()
	self.assertTrue(drc.stopped(), 'Data Request not stopped')
        

        


if __name__ == "__main__":
    unittest.main()