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
from AimsService_Mock import ASM

from AimsUI.LayerManager import LayerManager, InvalidParameterException
from AimsUI.AimsClient.Gui.Controller import Controller
from AimsUI.AimsLogging import Logger


from mock import Mock, patch


QtCore.QCoreApplication.setOrganizationName('QGIS')
QtCore.QCoreApplication.setApplicationName('QGIS2')
testlog = Logger.setup('test')

LM_QMLR = 'AimsUI.LayerManager.QgsMapLayerRegistry'

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
        qi = ASM.getMock(ASM.ASMenum.QI)()
        controller = Controller(qi)
        layermanager = LayerManager(qi,controller)
        self.assertNotEqual(layermanager,None,'LayerManager not instantiated')
        
class Test_1_LayerManagerSetters(unittest.TestCase):

    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        #self.QI = QgisInterface(_Dummy_Canvas())
        qi = ASM.getMock(ASM.ASMenum.QI)()
        controller = Controller(qi)
        self._layermanager = LayerManager(qi,controller)


        
    def tearDown(self):
        testlog.debug('Destroy null layermanager')
        self._layermanager = None        
        
    def test10_instLayerID(self):
        '''Test the layer id setter'''
        testval = 'AIMS1000'
        testlog.debug('Test_1.10 Instantiate layer ID')
        testlayer = ASM.getMock(ASM.ASMenum.LAYER)()
        testlayer.customProperty.return_value = testval
       
        self._layermanager.setLayerId(testlayer,testval)
        self.assertEqual(self._layermanager.layerId(testlayer),testval, 'Unable to set layer ID {}'.format(testval))

    def test11_instLayerIdRange(self):
        '''Example of success/fail test cases over range of input values'''
        testlog.debug('Test_1.11 Test range of layer ID values')

        testsuccesses = ('A','Z','#$%^&_)_#@)','māori','   ')
        for ts in testsuccesses:
            testlayer = ASM.getMock(ASM.ASMenum.LAYER)(id_rv=ts)
            self._layermanager.setLayerId(testlayer,ts)
            self.assertEqual(self._layermanager.layerId(testlayer),ts, 'Unable to set layer ID {}'.format(ts))
            
        #NB Can't set None as on Mock property since it is interpreted as no value so must be caught
        testfailures = (None,'',0,float('nan'),float('inf'),object,self)
        for tf in testfailures:
            testlayer = ASM.getMock(ASM.ASMenum.LAYER)(id_rv=tf)
            #testlayer.customProperty.return_value = tf
            self.assertRaises(InvalidParameterException, self._layermanager.setLayerId, testlayer, tf)
            #ctx mgr doesn't work for some reason!
            #with self.assertRaises(InvalidParameterException):
            #    self._layermanager.setLayerId(testlayer,tf)            
            
class Test_2_LayerManagerConnection(unittest.TestCase):
    '''installreflayer->installlayer->findlayer->layers'''
    
    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        #self.QI = QgisInterface(_Dummy_Canvas())
        qi = ASM.getMock(ASM.ASMenum.QI)()
        controller = Controller(qi)
        self._layermanager = LayerManager(qi,controller)
        self._layermanager.addressLayerAdded = ASM.getMock(ASM.ASMenum.SIGNAL)()

        
    def tearDown(self):
        testlog.debug('Destroy null layermanager')
        self._layermanager = None   
    
    def test10_layers(self):
        '''tests whether a layer generator is returned and it contains valid layers'''
        test_layers = [1,2,3]
        with (ASM.getMock(ASM.ASMenum.QMLR)(test_layers)) as QgsMapLayerRegistry:
            for glayer in self._layermanager.layers():
                self.assertTrue(isinstance(glayer, ASM.getMock(ASM.ASMenum.LAYER)), 'Object returned not a layer type')
                

    def test11_layers(self):
        '''tests whether a layer generator is returned and it contains valid layers'''
        test_layers = 3*[ASM.getMock(ASM.ASMenum.LAYER)(),]
        #with patch('qgis.core.QgsMapLayerRegistry') as qmlr_mock:
        conf = {'instance().mapLayers.values':test_layers}
        qmlr_spec = ASM.getMock(ASM.ASMenum.QMLR).__class__
        with patch(LM_QMLR) as qmlr_mock:
            qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = test_layers
            #qmlr_mock.configure_mock(**conf)
            for glayer in self._layermanager.layers():
                self.assertEqual(isinstance(glayer, ASM.getMock(ASM.ASMenum.LAYER)().__class__), True,'Object returned not a layer type')
            
    def test20_findLayer(self):
        '''tests whether the find layer fiunction returns a named layer, uses layers() gen'''
        rcltestlayer = ASM.getMock(ASM.ASMenum.LAYER)()
        self._layermanager.layers
        self._layermanager.findLayer('rcl')
        
    def test30_installLayers(self):
        '''tests install reflayers on the layer manager'''
        try: self._layermanager.installRefLayers()
        except Exception as e: raise AssertionError('Install reflayers failed. {}'.format(e))

        
    def test40_installRefLayers(self):
        '''tests install reflayers on the layer manager'''
        try: self._layermanager.installRefLayers()
        except Exception as e: raise AssertionError('Install reflayers failed. {}'.format(e))  
        
        

    def test50_checkNewLayer(self):
        '''tests whether layer is assigned to correct attribute'''
        #NB ('adr','_adrLayer'),#can't easily test adr since it emits a signal and fails with mock parameters
        for ltype in (('rcl','_rclLayer'),
                      ('par','_parLayer'),
                      ('loc','_locLayer'),
                      ('adr','_adrLayer')):
            testlayer = ASM.getMock(ASM.ASMenum.LAYER)(id_rv=ltype[0])
            self._layermanager.setLayerId(testlayer,ltype[0])
            #testlayer.customProperty.return_value = ltype[0]
            self._layermanager.checkNewLayer(testlayer)
            self.assertEqual(self._layermanager.__getattribute__(ltype[1]),testlayer)
        
    def test60_checkRemovedLayer(self):
        '''checks layers get null'd'''
        self._layermanager.installRefLayers()        
    
            
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