'''
v.0.0.1

QGIS-AIMS-Plugin - Database_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on Databae class functionality/connectivity

Created on 30/10/2015

@author: jramsay
'''
import unittest
import inspect
import sys
import re


from AimsClient import Database
from AimsClient.AimsLogging import Logger

testlog = Logger.setup()

class Test_0_DatabaseSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_1_selftest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('Database_Test Log')
        
class Test_1_DatabaseTestSetters(unittest.TestCase):
    
    def setUp(self): 
        self.d = {'host':'dummy.linz.govt.nz', 'port':3128,'user':'scott','password':'tiger','database':'aims'}
        
    def tearDown(self):
        self.d = None
        
    def test10_instSetters(self):
        '''Tests that all the setters set a matching attribute i.e. setAttribute("X") -> self._Attribute = "X"'''
        testlog.debug('Test10 Instantiate basic setters')
        Database.setHost(self.d['host'])
        self.assertEquals(Database.host(),self.d['host'],'Host not set')        
        Database.setPort(self.d['port'])
        self.assertEquals(Database.port(),self.d['port'],'Port not set')        
        Database.setUser(self.d['user'])
        self.assertEquals(Database.user(),self.d['user'],'User not set')        
        Database.setPassword(self.d['password'])
        self.assertEquals(Database.password(),self.d['password'],'Pwd not set')
        Database.setDatabase(self.d['database'])
        self.assertEquals(Database.database(),self.d['database'],'DB not set')        
        
class Test_2_DatabaseConnectivity(unittest.TestCase):
    
    def setUp(self): 
        self.d = {'host':'dummy.linz.govt.nz', 'port':3128,'user':'scott','password':'tiger','database':'aims'}
        
    def tearDown(self):
        self.d = None
    
    def test10_connection(self):
        pass
    
    def test20_execute(self):
        pass
    
    def test30_executeScalar(self):
        pass
    
    def test40_executeRow(self):
        pass
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testLDSRead']
    unittest.main()