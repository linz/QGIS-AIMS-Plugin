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
from Database_Test import DCONF 
import AimsUI.AimsClient.Database

from mock import Mock, patch
from openshot.uploads.vimeo.oauth2 import setter


QtCore.QCoreApplication.setOrganizationName('QGIS')
QtCore.QCoreApplication.setApplicationName('QGIS2')
testlog = Logger.setup('test')

LM_QMLR = 'AimsUI.LayerManager.QgsMapLayerRegistry'
LM_QDSU = 'AimsUI.LayerManager.QgsDataSourceURI'
LM_QVL = 'AimsUI.LayerManager.QgsVectorLayer'

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
        test_layers = 3*(ASM.getMock(ASM.ASMenum.LAYER)(),)
        with patch(LM_QMLR) as qmlr_mock:
            qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = test_layers
            for glayer in self._layermanager.layers():
                testlog.debug('testing layer (fetch) for {}'.format(glayer))
                self.assertEqual(isinstance(glayer, ASM.getMock(ASM.ASMenum.LAYER)().__class__), True,'Object returned not a layer type')
            
    def test20_findLayer(self):
        '''tests whether the find layer fiunction returns a named layer, uses layers() gen'''
        test_layeridlist = ('rcl','par','loc','adr')
        test_layerlist = len(test_layeridlist)*(ASM.getMock(ASM.ASMenum.LAYER)(),)
        test_layerdict = {x[0]:x[1] for x in zip(test_layeridlist,test_layerlist)}
        with patch(LM_QMLR) as qmlr_mock:
            qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = test_layerdict.values()
            for test_layerid in test_layerdict:
                testlog.debug('testing findlayer for layer type {}'.format(test_layerid))
                test_layerdict[test_layerid].customProperty.return_value = test_layerid
                test_layer = self._layermanager.findLayer(test_layerid)
                self.assertEqual(isinstance(test_layer, ASM.getMock(ASM.ASMenum.LAYER)().__class__), True,'Object returned not a layer type with name'.format(test_layerid))
    
    
    def test30_installLayers_find(self):
        '''tests install layer when layer is already installed in Qgis'''
        test_idlist = ('rcl','par','loc','adr')
        test_layer = ASM.getMock(ASM.ASMenum.LAYER)()
        
        for test_id in test_idlist:
            test_layer.customProperty.return_value = test_id
            #set up legendinterface to return legend mock!!!
            qlgd_mock =  ASM.getMock(ASM.ASMenum.QLGD)()
            self._layermanager._iface.legendInterface.return_value = qlgd_mock
    
            for lyr_vis in (True,False):
                #set legend visibility
                qlgd_mock.isLayerVisible.return_value = lyr_vis
                with patch(LM_QMLR) as qmlr_mock:
                    testlog.debug('testing installlayer 1 on layer with name {} and lgd visibility={}'.format(test_id,lyr_vis))
                    #set up findlayer to return test_layer
                    qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = [test_layer,]
                    res_layer = self._layermanager.installLayer(test_id, DCONF['aimsschema'], DCONF['table'], 'test_key', 'test_est', 'test_where', 'test_displayname')
        
                    self.assertEqual(test_layer,res_layer, 'installlayers and set layers dont match on layer with name {} and lgd visibility={}'.format(test_id,lyr_vis))
                        
    def test31_installLayers_db(self):
        '''tests installlayer's fetch from database if layer not available'''
        #This doesn't test the Database fetch part of the function and just internal logic. It isn't as useful as it could be
        test_idlist = ('rcl','par','loc','adr')
        test_layer = ASM.getMock(ASM.ASMenum.LAYER)() 
        for test_id in test_idlist:
            #set layerid to none to bypass active fetch
            with patch(LM_QMLR) as qmlr_mock:
                qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = ()
                with patch(LM_QVL) as qvl_mock:
                    testlog.debug('testing installlayer 2 on layer with name {}'.format(test_id))
                    qvl_mock.return_value = test_layer
                    res_layer = self._layermanager.installLayer(test_id, DCONF['aimsschema'], DCONF['table'], 'test_key', False, 'test_where', 'test_displayname')
                    self.assertEqual(test_layer, res_layer, 'installlayers and set layers dont match on fetched layer with name {}'.format(test_id))

        
    def test40_installRefLayers(self):
        '''tests whether ref layers have been installed following execution of the installreflayers method'''
        self._layermanager.installRefLayers()
        #TODO. uses the findlayer logic to test whether the layers have been fetched but mocks this functionality. rework! 
        test_layeridlist = ('rcl','par')
        test_layerlist = len(test_layeridlist)*(ASM.getMock(ASM.ASMenum.LAYER)(),)
        test_layerdict = {x[0]:x[1] for x in zip(test_layeridlist,test_layerlist)}
        with patch(LM_QMLR) as qmlr_mock:
            qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = test_layerdict.values()
            for test_layerid in test_layerdict:
                testlog.debug('testing installreflayers for layer type {}'.format(test_layerid))
                test_layerdict[test_layerid].customProperty.return_value = test_layerid
                test_layer = self._layermanager.findLayer(test_layerid)
                self.assertEqual(isinstance(test_layer, ASM.getMock(ASM.ASMenum.LAYER)().__class__), True,'Object returned not a layer type with name'.format(test_layerid))
    
        

    def test50_checkNewLayer(self):
        '''tests whether layer is assigned to correct attribute'''
        #NB ('adr','_adrLayer'),#can't easily test adr since it emits a signal and fails with mock parameters
        for ltype in (('rcl','_rclLayer'),
                      ('par','_parLayer'),
                      ('loc','_locLayer'),
                      ('adr','_adrLayer')):
            testlayer = ASM.getMock(ASM.ASMenum.LAYER)(id_rv=ltype[0])
            #TODO. consider moving id setting to local scope
            self._layermanager.setLayerId(testlayer,ltype[0])
            #testlayer.customProperty.return_value = ltype[0]
            self._layermanager.checkNewLayer(testlayer)
            self.assertEqual(self._layermanager.__getattribute__(ltype[1]),testlayer)
        
    def test60_checkRemovedLayer(self):
        '''checks layers get null'd'''
        pass      
    
    
    
if __name__ == "__main__":
    unittest.main()