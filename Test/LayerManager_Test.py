'''
v.0.0.1

QGIS-AIMS-Plugin - Address_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on Address class

Created on 29/10/2015

@author: jramsay
'''
import unittest
import inspect
import sys
import re

#from Test._QGisInterface import QgisInterface
from AimsUI.LayerManager import LayerManager

from AimsUI.AimsLogging import Logger

testlog = Logger.setup()

class Test_0_LayerManagerSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_1_selftest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('LayerManager_Test Log')
        
class Test_1_LayerManagerSetters(unittest.TestCase):
    #QI = QgisInterface(_Dummy_Canvas())

    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        self.QI = _Dummy_IFace()
        self._layermanager = LayerManager(self.QI)

        
    def tearDown(self):
        testlog.debug('Destroy null layermanager')
        self._layermanager = None        
        
    def test10_instLayerID(self):
        '''Test the layer id setter'''
        testlog.debug('Test_1.10 Instantiate layer ID')
        testlayer = _Dummy_Layer()
        testval = 'AIMS1000'
        self._layermanager.setLayerId(testlayer,testval)
        self.assertEqual(self._layermanager.layerId(testlayer),testval, 'Unable to set layer ID {}'.format(testval))

#------------------------------------------------------------------------------

        
class _Dummy_IFace(object):
    def mainWindow(self):
        return _Dummy_MainWindow()
    
class _Dummy_MainWindow(object):
    def statusBar(self): return None
    
class _Dummy_Layer(object):
    cp = {}
    def setCustomProperty(self,prop,id): self.cp[prop] = id 
    def customProperty(self,prop): return self.cp[prop]
    
    
if __name__ == "__main__":
    unittest.main()