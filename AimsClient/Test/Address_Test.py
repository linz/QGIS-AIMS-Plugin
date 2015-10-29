'''
v.0.0.1

QGIS-AIMS-Plugin - Address_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests for command line URLs

Created on 29/10/2015

@author: jramsay
'''
import unittest
import inspect
import sys


sys.path.append('..')

from Address import Address
from AimsLogging import Logger

testlog = Logger.setup()

class Test_0_SelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_1_selftest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('Test message')
        
class Test_1_TestSetters(unittest.TestCase):
    
    def setUp(self): 
        testlog.debug('Instantiate null address')
        self._address = Address()
        self._address_setters = [ i for i in inspect.getmembers(Address, predicate=inspect.ismethod).keys() if i[:3]=='set']

        
    def tearDown(self):
        testlog.debug('Destroy null address')
        self._address = None
        self._address_setters = None
        
        
    def test1_inst(self):
        '''Tests that all the setters set a matching attribute i.e. setAttribute("X") -> self._Attribute = "X"'''
        testval = 1     
        for asm in self.address_setters:
            asa = asm[:4].replace('set','_').lower()+asm[4:]
            getattr(self._address, am)(testval)
            self.assertEqual(getattr(self._address, asa), testval, 'testval mismatch')
            
    def test2_nullremoval(self):
        '''Tests whether null values are removed from the object array'''
        pass
    
    def test3_checkJSON(self):
        '''Tests whether JSON object gets created correctly'''
        pass
    



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testLDSRead']
    unittest.main()