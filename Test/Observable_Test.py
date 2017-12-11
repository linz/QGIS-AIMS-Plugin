'''
v.0.0.1

QGIS-AIMS-Plugin - DataManager_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on Observable class

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

from Observable import Observable
from AimsLogging import Logger

testlog = Logger.setup('test')

class Test_0_ObservableSelfTest(unittest.TestCase):
    
    def setUp(self):
        self.ov = Observable()
        
    def tearDown(self):
        self.ov = None
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('Observer Log')
        
    def test20_observeTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 Observer instantiation test')
        self.assertIsNotNone(self.ov,'Observable not instantiated')
        self.assertEqual(self.ov._observers, [], 'Observable not instantiated correctly')
        
    def test30_observerRegister(self):
	self.ov.register("observer1")
	self.assertNotEqual(self.ov._observers, [], 'Observable not register correctly')
	
	self.ov.register("observer2")
	self.assertEqual(len(self.ov._observers), 2, 'Multiple observers not registered')
	
	self.ov.deregister("observer1")
	self.ov.deregister("observer2")
	self.assertEqual(self.ov._observers, [], 'Observable not deregister correctly')

if __name__ == "__main__":
    unittest.main()