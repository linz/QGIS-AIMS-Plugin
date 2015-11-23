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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from PyQt4 import QtCore, QtGui, QtTest

import unittest
import inspect
import sys
import re

#from Test._QGisInterface import QgisInterface
from AimsUI.LayerManager import LayerManager, InvalidParameterException

from AimsUI.AimsLogging import Logger

QtCore.QCoreApplication.setOrganizationName('QGIS')
QtCore.QCoreApplication.setApplicationName('QGIS2')
testlog = Logger.setup('test')

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
        qi = DummyInterface()
        layermanager = LayerManager(qi)
        self.assertNotEqual(layermanager,None,'LayerManager not instantiated')
        
class Test_1_LayerManagerSetters(unittest.TestCase):

    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        #self.QI = QgisInterface(_Dummy_Canvas())
        self.QI = DummyInterface()
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

        testsuccesses = ('A','Z','#$%^&_)_#@)','māori','   ','')
        for ts in testsuccesses:
            self._layermanager.setLayerId(testlayer,ts)
            self.assertEqual(self._layermanager.layerId(testlayer),ts, 'Unable to set layer ID {}'.format(ts))
            
        testfailures = (None,0,float('nan'),float('inf'),object,self)
        for tf in testfailures:
            self.assertRaises(InvalidParameterException, self._layermanager.setLayerId,testlayer,tf)
            
    """       
    def test40_createFeatureLayer(self):
        '''Test AIMS Layer Created'''
        testlog.debug('Test_1.40 test the creation of feature mem layer')
        return True
        
        sampleResponse = {
                "class":[
                    "address",
                    "collection"
                ],
                "links":[
                    {
                        "rel":[
                            "self"
                        ],
                        "href":"http://144.66.241.207:8080/aims/api/address/features?page=1"
                    },
                    {
                        "rel":[
                            "next"
                        ],
                        "href":"http://144.66.241.207:8080/aims/api/address/features?page=2"
                    }
                ],
                "actions":[
                    {
                        "name":"add",
                        "method":"POST",
                        "href":"http://144.66.241.207:8080/aims/api/address/changefeed/add"
                    }
                ],
                "entities":[
                    {
                        "class":[
                            "address"
                        ],
                        "rel":[
                            "item"
                        ],
                        "links":[
                            {
                                "rel":[
                                    "self"
                                ],
                                "href":"http://144.66.241.207:8080/aims/api/address/features/1"
                            }
                        ],
                        "properties":{
                            "publishDate":"2015-02-19",
                            "version":1622074,
                            "components":{
                                "addressId":1,
                                "addressType":"Road",
                                "lifecycle":"Current",
                                "addressNumber":523,
                                "roadCentrelineId":112967,
                                "roadName":"Waiatai",
                                "roadTypeName":"Road",
                                "suburbLocality":"Wairoa",
                                "townCity":"Wairoa",
                                "fullAddressNumber":"523",
                                "fullRoadName":"Waiatai Road",
                                "fullAddress":"523 Waiatai Road, Wairoa"
                            },
                            "addressedObject":{
                                "addressableObjectId":1706002,
                                "objectType":"Parcel",
                                "addressPosition":{
                                    "type":"Point",
                                    "coordinates":[
                                        1990322.0310298172,
                                        5673091.026376988
                                    ],
                                    "crs":{
                                        "type":"name",
                                        "properties":{
                                            "name":"urn:ogc:def:crs:EPSG::2193"
                                        }
                                    }
                                }
                            },
                            "codes":{
                                "suburbLocalityId":2622,
                                "townCityId":100124,
                                "parcelId":4220123,
                                "meshblock":"1398600"
                            }
                        }
                    }
                ]
            }
        

        layerTest = self._layermanager.createFeaturesLayers(sampleResponse)
        self.assertTrue(layerTest.isValid(), 'Failed to load "{}".'.format(layerTest.source()))
        """

                
#------------------------------------------------------------------------------

        
class DummyInterface(object):
    
    def __getattr__(self, *args, **kwargs):
        def dummy(*args, **kwargs):
            return self
        return dummy
    def __iter__(self):
        return self
    def next(self):
        raise StopIteration
    def layers(self):
        # simulate iface.legendInterface().layers()
        return QgsMapLayerRegistry.instance().mapLayers().values()
    
class _Dummy_MainWindow(object):
    def statusBar(self): return None
    
class _Dummy_Layer(object):
    cp = {}
    def setCustomProperty(self,prop,id): self.cp[prop] = id 
    def customProperty(self,prop): return self.cp[prop]
    
    
if __name__ == "__main__":
    unittest.main()