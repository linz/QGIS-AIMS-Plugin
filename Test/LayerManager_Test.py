# coding=utf-8
'''
v.0.0.1

QGIS-AIMS-Plugin - LayerManager_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on LayerManager class

Created on 05/11/2015

@author: jramsay
'''
import unittest
import inspect
import sys
import re

#from Test._QGisInterface import QgisInterface
from AimsUI.LayerManager import LayerManager, InvalidParameterException

from AimsUI.AimsLogging import Logger

testlog = Logger.setup()

class Test_0_LayerManagerSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('LayerManager_Test Log')
    
    def test20_layerManagerTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 LayerManager instantiation test')
        qi = _Dummy_IFace()
        layermanager = LayerManager(qi)
        self.assertNotEqual(layermanager,None,'LayerManager not instantiated')
        
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

    def test11_instLayerIdRange(self):
        '''Example of success/fail test cases over range of input values'''
        testlog.debug('Test_1.11 Test range of layer ID values')
        testlayer = _Dummy_Layer()

        testsuccesses = ('A','Z','#$%^&_)_#@)','māori')
        for ts in testsuccesses:
            self._layermanager.setLayerId(testlayer,ts)
            self.assertEqual(self._layermanager.layerId(testlayer),ts, 'Unable to set layer ID {}'.format(ts))
            
        testfailures = (None,0,float('nan'),float('inf'),object,self)
        for tf in testfailures:
            self.assertRaises(InvalidParameterException, self._layermanager.setLayerId,testlayer,tf)

                
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