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
from AimsUI.AimsClient import Database

from mock import Mock, patch

QtCore.QCoreApplication.setOrganizationName('QGIS')
QtCore.QCoreApplication.setApplicationName('QGIS2')
testlog = Logger.setup('test')

LM_QMLR = 'AimsUI.LayerManager.QgsMapLayerRegistry'
LM_QDSU = 'AimsUI.LayerManager.QgsDataSourceURI'
LM_QVL = 'AimsUI.LayerManager.QgsVectorLayer'
LM_QDP = 'AimsUI.LayerManager.QgsDataProvider'
LM_QF = 'AimsUI.LayerManager.QgsFeature'
LM_QG = 'AimsUI.LayerManager.QgsGeometry'
LM_QP = 'AimsUI.LayerManager.QgsPoint'

LM_coords = 'AimsUI.LayerManager.createFeaturesLayers.coords'

LCONF = {'id':'rcl', 'schema':'aims_schema', 'table':'aims_table', 'key':'id', 'estimated':True, 'where':'', 'displayname':'aims_layer'}

def getLConf(replace=None):
    if replace and isinstance(replace,dict):
        for r in replace:
            if r in LCONF: LCONF[r] = replace[r] 
    return LCONF

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
        testval = 't10'
        testlog.debug('Test_1.10 Instantiate layer ID')
        testlayer = ASM.getMock(ASM.ASMenum.LAYER)(cprv=testval,vlrv=True)

        self._layermanager.setLayerId(testlayer,testval)
        self.assertEqual(self._layermanager.layerId(testlayer),testval, 'Unable to set layer ID {}'.format(testval))

    def test11_instLayerIdRange(self):
        '''Example of success/fail test cases over range of input values'''
        testlog.debug('Test_1.11 Test range of layer ID values')

        testsuccesses = ('A','Z','#$%^&_)_#@)','māori','   ')
        for ts in testsuccesses:
            testlayer = ASM.getMock(ASM.ASMenum.LAYER)(cprv=ts,vlrv=True)
            self._layermanager.setLayerId(testlayer,ts)
            self.assertEqual(self._layermanager.layerId(testlayer),ts, 'Unable to set layer ID {}'.format(ts))
            
        #NB Can't set None as on Mock property since it is interpreted as no value so must be caught
        testfailures = (None,'',0,float('nan'),float('inf'),object,self)
        for tf in testfailures:
            testlayer = ASM.getMock(ASM.ASMenum.LAYER)(cprv=tf)
            #testlayer.customProperty.return_value = tf
            self.assertRaises(InvalidParameterException, self._layermanager.setLayerId, testlayer, tf)
            #ctx mgr doesn't work for some reason!
            #with self.assertRaises(InvalidParameterException):
            #    self._layermanager.setLayerId(testlayer,tf)            
            
class Test_2_LayerManagerConnection(unittest.TestCase):
    '''installreflayer->installlayer->findlayer->layers'''
    
    MLAYERS = (('rcl','_rclLayer'),('par','_parLayer'),('loc','_locLayer'),('adr','_adrLayer'))
    
    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        #self.QI = QgisInterface(_Dummy_Canvas())
        qi = ASM.getMock(ASM.ASMenum.QI)()
        controller = Controller(qi)
        self._layermanager = LayerManager(qi,controller)
        self._layermanager.addressLayerAdded = ASM.getMock(ASM.ASMenum.SIGNAL)()
        Database.setup(DCONF)

        
    def tearDown(self):
        testlog.debug('Destroy null layermanager')
        self._layermanager = None
        Database.setup({name:None for name in DCONF})                 

    def test10_layers_m(self):
        '''tests whether a layer generator is returned and it contains valid mock layers'''
        test_layers = 3*(ASM.getMock(ASM.ASMenum.LAYER)(vlrv=True),)
        with patch(LM_QMLR) as qmlr_mock:
            qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = test_layers
            for glayer in self._layermanager.layers():
                testlog.debug('T10 - testing layer (fetch) for {}'.format(glayer))
                self.assertEqual(isinstance(glayer, ASM.getMock(ASM.ASMenum.LAYER)().__class__), True,'Object returned not a layer type')    
                
    def test11_layers(self):
        '''tests whether a layer generator is returned and it contains valid layers'''
        #TODO install test layers even though installlayer functionality is untested. in the meantime returns none
        for glayer in self._layermanager.layers():
            testlog.debug('testing layer (fetch) for {}'.format(glayer))
            self.assertEqual(isinstance(glayer, QgsVectorLayer), True,'Object returned not a layer type')
            
            
    def test20_findLayer(self):
        '''tests whether the find layer fiunction returns a named layer, uses layers() gen'''
        test_layerdict = {test_layerid:ASM.getMock(ASM.ASMenum.LAYER)(cprv=test_layerid,vlrv=True) for test_layerid in ('rcl','par','loc','adr')}
        #test_layerlist = len(test_layeridlist)*(ASM.getMock(ASM.ASMenum.LAYER)(vlrv=True),)
        #test_layerdict = {x[0]:x[1] for x in zip(test_layeridlist,test_layerlist)}
        with patch(LM_QMLR) as qmlr_mock:
            qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = test_layerdict.values()
            for test_layerid in test_layerdict:
                testlog.debug('T20 testing findlayer for layer type {}'.format(test_layerid))
                #test_layerdict[test_layerid].customProperty.return_value = test_layerid
                test_layer = self._layermanager.findLayer(test_layerid)
                self.assertEqual(isinstance(test_layer, ASM.getMock(ASM.ASMenum.LAYER)(vlrv=True).__class__), True,'Object returned not a layer type with name'.format(test_layerid))
    

    def test30_installLayers_find(self):
        '''tests install layer when layer is already installed in Qgis'''
        for test_id in [l[0] for l in self.MLAYERS]:
            test_layer = ASM.getMock(ASM.ASMenum.LAYER)(cprv=test_id,vlrv=True)
            #set up legendinterface to return legend mock!!!
            qlgd_mock =  ASM.getMock(ASM.ASMenum.QLGD)()
            self._layermanager._iface.legendInterface.return_value = qlgd_mock
    
            for lyr_vis in (True,False):
                #set legend visibility
                qlgd_mock.isLayerVisible.return_value = lyr_vis
                with patch(LM_QMLR) as qmlr_mock:
                    testlog.debug('T30 - testing installlayer 1 on layer with name {} and lgd visibility={}'.format(test_id,lyr_vis))
                    #set up findlayer to return test_layer
                    qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = [test_layer,]
                    res_layer = self._layermanager.installLayer(**getLConf(replace={'id':test_id}))
        
                    self.assertEqual(test_layer,res_layer, 'installlayers and set layers dont match on layer with name {} and lgd visibility={}'.format(test_id,lyr_vis))
                        
    def test31_installLayers_db(self):
        '''tests installlayer's fetch from database if layer not available'''
        #This doesn't test the Database fetch part of the function and just internal logic. It isn't as useful as it could be
        test_layer = ASM.getMock(ASM.ASMenum.LAYER)() 
        for test_id in [l[0] for l in self.MLAYERS]:
            #set layerid to none to bypass active fetch
            with patch(LM_QMLR) as qmlr_mock:
                qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = ()
                with patch(LM_QVL) as qvl_mock:
                    testlog.debug('T40 - testing installlayer 2 on layer with name {}'.format(test_id))
                    qvl_mock.return_value = test_layer
                    res_layer = self._layermanager.installLayer(**getLConf(replace={'displayname':test_id}))
                    self.assertEqual(test_layer, res_layer, 'installlayers and set layers dont match on fetched layer with name {}'.format(test_id))


    #now that installlayers is tested we can use this to generate test layers
        
    def test32_installLayers_tst(self):
        '''tests whether fake layers have been installed following execution of the installlayers method'''
        test_layer_id = 't32'
        test_layer = self._layermanager.installLayer(**getLConf(replace={'displayname':test_layer_id}))
        #test_layer = ASM.getMock(ASM.ASMenum.LAYER)(cprv=test_layer_id) 
        with patch(LM_QMLR) as qmlr_mock:
            testlog.debug('T32 - testing installlayers on fake layer {}'.format(test_layer_id))
            self._layermanager.setLayerId(test_layer,test_layer_id)
            qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = (test_layer,)
            found_layer = self._layermanager.findLayer(test_layer_id)
            self.assertEqual(found_layer, test_layer,'returned layer does not match set layer using name {}'.format(test_layer_id))
    
    
    def test40_installRefLayers(self):
        '''tests whether ref layers have been installed following execution of the installreflayers method'''
        ref_layers = {a:b for a,b in zip([l[0] for l in self.MLAYERS][:2], self._layermanager.installRefLayers())}
        
        with patch(LM_QMLR) as qmlr_mock:
            qmlr_mock.instance.return_value.mapLayers.return_value.values.return_value = ref_layers.values()
            for test_layerid in ref_layers:
                testlog.debug('T40 - testing installreflayers for layer type {}'.format(test_layerid))
                self._layermanager.setLayerId(ref_layers[test_layerid],test_layerid)
                found_layer = self._layermanager.findLayer(test_layerid)
                self.assertEqual(found_layer, ref_layers[test_layerid],'returned layer does not match set layer using name {}'.format(test_layerid))
    
        

    def test50_checkNewLayer(self):
        '''tests whether layer is assigned to correct attribute'''
        #NB ('adr','_adrLayer'),#can't easily test adr since it emits a signal and fails with mock parameters
        for ltype in self.MLAYERS:
            testlog.debug('T50 - testing checknewlayer layer type {}'.format(ltype[0]))
            testlayer = ASM.getMock(ASM.ASMenum.LAYER)(cprv=ltype[0])
            #TODO. consider moving id setting to local scope
            self._layermanager.setLayerId(testlayer,ltype[0])
            #testlayer.customProperty.return_value = ltype[0]
            self._layermanager.checkNewLayer(testlayer)
            self.assertEqual(self._layermanager.__getattribute__(ltype[1]),testlayer)
        
    def test60_checkRemovedLayer(self):
        '''checks layers get null'd by first installing a layer then removing it'''
        test_layerdict = {test_layerpair:ASM.getMock(ASM.ASMenum.LAYER)(idrv=test_layerpair[0],cprv=test_layerpair[0],vlrv=True) for test_layerpair in self.MLAYERS}

        for test_layerpair in test_layerdict:
            #test_layerdict[test_layerpair].id.return_value = test_layerpair[0]
            self._layermanager.setLayerId(test_layerdict[test_layerpair],test_layerpair[0])
            self._layermanager.checkNewLayer(test_layerdict[test_layerpair])
            testlog.debug('T60a - testing checkremovelayer is added, layer type {}'.format(test_layerpair[0]))
            self.assertEqual(self._layermanager.__getattribute__(test_layerpair[1]),test_layerdict[test_layerpair],'Layer not initialised')
            
            self._layermanager.checkRemovedLayer(test_layerpair[0])
            testlog.debug('T60b - testing checkremovelayer is removed, layer type {}'.format(test_layerpair[0]))
            self.assertEqual(self._layermanager.__getattribute__(test_layerpair[1]),None,'Layer not removed')
            

    def test70_createFeaturesLayers(self):
        r = {'entities':[{'properties':{'version':1,'components':{},'addressedObject':{'addressPosition':{'coordinates':(0,0)}},'codes':{}}}]}
        #pqvl = patch(LM_QVL)
        #mock_qvl = pqvl.start()
        with patch(LM_QVL) as mock_qvl:
            mock_qvl.customProperty = 'adr'
            with patch(LM_QDP) as mock_qdp:
                with patch(LM_QF) as mock_qf:
                    #with patch(LM_QG) as mock_qg:
                        #mock_qg.fromPoint.return_value = ASM.getMock(ASM.ASMenum.GEOMETRY)()
                        #with patch(LM_QP) as mock_qp:
                            #mock_qp.return_value = ASM.getMock(ASM.ASMenum.POINT)()
                    with patch(LM_QMLR) as mock_qmlr:
                        self._layermanager.createFeaturesLayers(r)
                        #this method doesn't return anything testable so this test method just makes sure it runs without error given minimal input
                        self.assertEqual(True,True,'this cant be false')
                        
    
    def test_80_getAimsFeatures(self):
        self._layermanager._iface.mapCanvas.return_value.extent.return_value = 1000#ext?
        
    def test90_loadAimsFeatures(self):
        self._layermanager._iface.mapCanvas.return_value.mapSettings.return_value.scale.return_value = 9999999
        self._layermanager.loadAimsFeatures()
        self.assertEqual(1,1,'1')

        

    
    
if __name__ == "__main__":
    unittest.main()