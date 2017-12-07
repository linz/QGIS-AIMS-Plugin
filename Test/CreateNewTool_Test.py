'''
v.0.0.1

QGIS-AIMS-Plugin - CreateNewTool_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on CreateNewTool class

Created on 05/11/2015

@author: jramsay
'''
import unittest
import inspect
import sys
import re

sys.path.append('/home/aross/Documents/Github/QGIS-AIMS-Plugin/')
#from Test._QGisInterface import QgisInterface
from AimsUI.CreateNewAddressTool import CreateNewAddressTool
from AimsUI.LayerManager import LayerManager
from AimsUI.AimsLogging import Logger
from AimsUI.AimsClient.Gui.Controller import Controller

testlog = Logger.setup('test')

class Test_0_LayerManagerSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_1_selftest(self):
        self.assertIsNotNone(testlog,'Testlog not instantiated')
        testlog.debug('LayerManager_Test Log')
        
class Test_1_LayerManagerSetters(unittest.TestCase):

    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        self.QI = _Dummy_IFace()
        self._controller = Controller(self.QI)
        self._layermanager = LayerManager(self.QI, self._controller)

        
    def tearDown(self):
        testlog.debug('Destroy null layermanager')
        self._layermanager = None  
        self._controller = None
        self.QI = None
        
    def test10_instLayerID(self,testval='AIMS1000'):
        '''Test the layer id setter'''
        testlog.debug('Test_1.10 Instantiate layer ID')
        testlayer = _Dummy_Layer()
        self._layermanager.setLayerId(testlayer,testval)
        self.assertEqual(self._layermanager.layerId(testlayer),testval, 'Unable to set layer ID {}'.format(testval))
        
class Test_2_CreateNewAddressInit(unittest.TestCase):
    
    def setUp(self):
	self.QI = _Dummy_IFace()
	self._controller = Controller(self.QI)
	self._layermanager = LayerManager(self.QI, self._controller)
	
    
    def tearDown(self):
	self.QI = None
	self._controller = None
	self._layermanager = None
	
    #def test10_instantiate(self):
	#self._createNAT = CreateNewAddressTool(self.QI, self._layermanager, self._controller)
            
        

#------------------------------------------------------------------------------

        
class _Dummy_IFace(object):
    def mainWindow(self):
        return _Dummy_MainWindow()
    def mapCanvas(sel):
	return _Dummy_MapCanvas()
    
class _Dummy_MainWindow(object):
    def statusBar(self): return None
    
class _Dummy_MapCanvas(object):
    def mapSettings(self): return None
  
    def extent(self): return None
    
class _Dummy_Layer(object):
    cp = {}
    def setCustomProperty(self,prop,id): self.cp[prop] = id 
    def customProperty(self,prop): return self.cp[prop]
    
    
if __name__ == "__main__":
    unittest.main()