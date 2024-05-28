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
import os

ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT, 'AIMSDataManager'))
sys.path.append(os.path.join(ROOT, 'AimsUI'))

from functools import wraps
from multiprocessing import Process

from AIMSDataManager.AimsUtility import AimsException
from AimsUI.AimsClient import Database
from AimsUI.AimsLogging import Logger

testlog = Logger.setup('test')

DCONF = {'host':'postgres', 'port':'5432', 'user':'postgres','password':'postgres', \
         'name':'aims_ci_test','aimsschema':'aims', 'table':'aims_test_table'}

TIMEOUT = 30
#Bypass for timeout error raise. Delete in production
BYPASS = False

class TimeoutError(AimsException): pass

def timeout(seconds=5, message="Timeout"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            process = Process(None, func, None, args, kwargs)
            process.start()
            process.join(seconds)
            if process.isRunning():
                process.terminate()
                if not BYPASS:
                    raise TimeoutError(message)

        return wraps(func)(wrapper)
    return decorator



class Test_0_DatabaseSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        testlog.debug('Test_0.10 Database_Test Log')
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        
#     def test20_databaseTest(self):
#         '''Tests that database object can be instantiated'''        
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
        self.assertEqual(Database.host(),DCONF['host'],'Host not set')        
        Database.setPort(DCONF['port'])
        self.assertEqual(Database.port(),DCONF['port'],'Port not set')        
        Database.setUser(DCONF['user'])
        self.assertEqual(Database.user(),DCONF['user'],'User not set')        
        Database.setPassword(DCONF['password'])
        self.assertEqual(Database.password(),DCONF['password'],'Pwd not set')
        Database.setDatabase(DCONF['name'])
        self.assertEqual(Database.database(),DCONF['name'],'DB not set')
        Database.setAimsSchema(DCONF['aimsschema'])
        self.assertEqual(Database.aimsSchema(),DCONF['aimsschema'],'Schema not set')          
        
class Test_2_DatabaseConnectivity(unittest.TestCase):
    
    conn = None
    cur = None
    res = None
    q = 'CREATE SCHEMA aims;'
    q0 = 'CREATE TABLE aims.aims_test_table(id int, name varchar(32));'
    q1 = "INSERT INTO aims.aims_test_table VALUES (1, 'aims_test_data');"
    q2 = 'SELECT * FROM {}.{};'.format(DCONF['aimsschema'],DCONF['table'])
    q3 = "DELETE FROM {}.{} WHERE id=1;".format(DCONF['aimsschema'],DCONF['table'])
    q4 = 'DROP SCHEMA aims CASCADE;'
    
    def setUp(self): 
        Database.setup(DCONF)
        
    def tearDown(self):
        self.conn = None
        self.cur = None
        self.res = None
    
    # @timeout(seconds=TIMEOUT, message='Timeout connecting to database')
    def test10_connection(self):
        testlog.debug('Test_2.10 Test connection() function')
        self.conn = Database.connection()
        self.assertNotEqual(self.conn,None,'Connection not established')
        
    # @timeout(seconds=TIMEOUT, message='Timeout execution query on database')
    def test20_create_insert_select(self):
        '''checks database execution by testing whether a cursor is returned, which happens on commit'''
        testlog.debug('Test_2.20 Test query execution (CREATE TABLE, INSERT RECORDS< SELECT) functions')
        # Create Schema
        self.res = Database.execute(self.q)
        from psycopg2._psycopg import cursor as PPC
        self.assertEqual(isinstance(self.res,PPC),True,'Query "{}" failed with {}'.format(self.q,self.res))
        # Create Database
        self.res = Database.execute(self.q0)
        from psycopg2._psycopg import cursor as PPC
        self.assertEqual(isinstance(self.res,PPC),True,'Query "{}" failed with {}'.format(self.q0,self.res))
        # Insert Record
        self.res = Database.execute(self.q1)
        from psycopg2._psycopg import cursor as PPC
        self.assertEqual(isinstance(self.res,PPC),True,'Query "{}" failed with {}'.format(self.q1,self.res))
        # Select Records
        self.res = Database.execute(self.q2)
        from psycopg2._psycopg import cursor as PPC
        self.assertEqual(isinstance(self.res,PPC),True,'Query "{}" failed with {}'.format(self.q2,self.res))
        
    # @timeout(seconds=TIMEOUT, message='Timeout execution query on database')
    def test30_execute(self):
        '''checks database execution by testing whether a cursor is returned, which happens on commit'''
        testlog.debug('Test_2.30 Test query execution (DELETE) function')
        # Delete Record
        self.res = Database.execute(self.q3)
        from psycopg2._psycopg import cursor as PPC
        self.assertEqual(isinstance(self.res,PPC),True,'Query "{}" failed with {}'.format(self.q3,self.res))
        # Select Records
        self.res = Database.execute(self.q2)
        from psycopg2._psycopg import cursor as PPC
        self.assertEqual(isinstance(self.res,PPC),True,'Query "{}" failed with {}'.format(self.q2,self.res))
    
    def test40_drop_schema(self):
        '''drops the schema in case this test is run locally and we don't want to deal with existing objects'''
        testlog.debug('Test_2.40 drop database schema')
        # Drop Schema
        self.res = Database.execute(self.q4)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testLDSRead']
    unittest.main()