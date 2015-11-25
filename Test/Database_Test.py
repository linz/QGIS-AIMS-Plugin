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

from functools import wraps
from multiprocessing import Process


from AimsUI.AimsClient import Database
from AimsUI.AimsLogging import Logger

testlog = Logger.setup('test')

DCONF = {'host':'127.0.0.1', 'port':3128, 'user':'postgres','password':'', \
         'name':'aims_ci_test','aimsschema':'aims', 'table':'aims_test_table'}
TIMEOUT = 10

class TimeoutError(Exception): pass

def timeout(seconds=5, message="Timeout"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            process = Process(None, func, None, args, kwargs)
            process.start()
            process.join(seconds)
            if process.is_alive():
                process.terminate()
                raise TimeoutError(message)

        return wraps(func)(wrapper)
    return decorator



class Test_0_DatabaseSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        testlog.debug('Test_0.10 Database_Test Log')
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        
#     def test20_databaseTest(self):
#         #assertIsNotNone added in 3.1        
#         testlog.debug('Test_0.20 Database instantiation test')
#         database = Database()
#         self.assertNotEqual(database,None,'Database not instantiated')
        
class Test_1_DatabaseTestSetters(unittest.TestCase):
    
    def setUp(self): 
        pass
    
    def tearDown(self):
        pass
        
    def test10_instSetters(self):
        '''Tests that all the setters set a matching attribute i.e. setAttribute("X") -> self._Attribute = "X"'''
        testlog.debug('Test_1.10 Instantiate basic setters')
        Database.setHost(DCONF['host'])
        self.assertEquals(Database.host(),DCONF['host'],'Host not set')        
        Database.setPort(DCONF['port'])
        self.assertEquals(Database.port(),DCONF['port'],'Port not set')        
        Database.setUser(DCONF['user'])
        self.assertEquals(Database.user(),DCONF['user'],'User not set')        
        Database.setPassword(DCONF['password'])
        self.assertEquals(Database.password(),DCONF['password'],'Pwd not set')
        Database.setDatabase(DCONF['name'])
        self.assertEquals(Database.database(),DCONF['name'],'DB not set')
        Database.setAimsSchema(DCONF['aimsschema'])
        self.assertEquals(Database.aimsSchema(),DCONF['aimsschema'],'Schema not set')          
        
class Test_2_DatabaseConnectivity(unittest.TestCase):
    
    conn = None
    cur = None
    res = None
    q1 = 'SELECT * FROM {};'.format(DCONF['table'])
    q2 = "INSERT INTO {}.{} VALUES(1000,'first');".format(DCONF['aimsschema'],DCONF['table'])
    q3 = "DELETE FROM {}.{} WHERE id=1000;".format(DCONF['aimsschema'],DCONF['table'])
    
    def setUp(self): 
        Database.setup(DCONF)
        
    def tearDown(self):
        self.conn = None
        self.cur = None
        self.res = None
    
    @timeout(seconds=TIMEOUT, message='Timeout connecting to database')
    def test10_connection(self):
        testlog.debug('Test_2.10 Test connection() function')
        self.conn = Database.connection()
        self.assertNotNull(self.conn,'Connection not established')
        
    @timeout(seconds=TIMEOUT, message='Timeout execution query on database')
    def test20_execute(self):
        testlog.debug('Test_2.20 Test query execution (SELECT) function')
        self.res = Database.execute(self.q1)
        self.assertNotNull(self.res,'Query "{}" failed with {}'.format(self.q1,self.res))
    
    def test30_executeScalar(self):
        pass
    
    def test40_executeRow(self):
        pass
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testLDSRead']
    unittest.main()