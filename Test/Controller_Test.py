'''
v.0.0.1

QGIS-AIMS-Plugin - CreateNewTool_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on Controller class

Created on 05/11/2015

@author: jramsay
'''
import unittest
import inspect
import sys
import re

#from Test._QGisInterface import QgisInterface
from AimsUI.AimsClient.Gui.Controller import Controller
from AimsUI.AimsClient.Address import Address

from AimsUI.AimsLogging import Logger

testlog = Logger.setup('test')

class Test_0_ControllerSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.10 Controller_Test Log') 
        self.assertNotEqual(testlog,None,'Testlog not instantiated')  
        
    def test20_controllerTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 Controller instantiation test')
        controller = Controller()
        self.assertNotEqual(controller,None,'Controller not instantiated')

class Test_1_ControllerTestSetupFunction(unittest.TestCase):
    
    def setUp(self): 
        self._controller = Controller()
    
    def tearDown(self):
        self._controller = None
        
    def test10_initControllerAddress(self):  
        testlog.debug('Test_1.10 Controller/Address instantiation test')
        self.assertEqual(isinstance(self._controller.initialiseNewAddress(),Address),True,'Cannot init Controller.Address')
        #self.assertIsInstance(self._controller.initialiseNewAddress(),Address,'Cannot init Controller.Address')
          
    
if __name__ == "__main__":
    unittest.main()