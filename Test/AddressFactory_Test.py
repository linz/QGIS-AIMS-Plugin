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
import sys
import re
import sys
import os


sys.path.append('../AIMSDataManager/')

from AddressFactory import AddressFactory,AddressChangeFactory,AddressResolutionFactory,TemplateReader
from Address import Address,AddressChange,AddressResolution
from AimsUtility import ActionType,ApprovalType
from AimsUtility import FeedType
from AimsLogging import  Logger

testlog = Logger.setup('test')

#user to init an address, simple text string read from a stored config file
user_text = 'aims_user'

class Test_0_TemplateReaderSelfTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('TemplateReader_Test Log')
        
    def test20_templatereaderInitTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 TemplateReader instantiation test')
        tr = TemplateReader()
        self.assertNotEqual(tr,None,'TemplateReader not instantiated')        
        
    def test30_templatereaderGetTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 TemplateReader instantiation test')
        t = TemplateReader().get()
        self.assertNotEqual(t,None,'Template values not retrieved')    
    
class Test_1_AddressFactorySelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('Address_Test Log')
        
    def test20_addressfactoryTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_1.20 Address instantiation test')
        afact = AddressFactory(user_text)
        self.assertNotEqual(afact,None,'AddressFactory not instantiated')    
        acfact = AddressChangeFactory(user_text)
        self.assertNotEqual(acfact,None,'AddressChangeFactory not instantiated')    
        arfact = AddressResolutionFactory(user_text)
        self.assertNotEqual(arfact,None,'AddressResolutionFactory not instantiated')    
        
    def test30_addressfactoryGetInstanceTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_1.30 Address instantiation test')
        afact = AddressFactory.getInstance(FeedType.FEATURES)
        self.assertNotEqual(afact,None,'Unable to getInstance of AddressFactory')
        acfact = AddressFactory.getInstance(FeedType.CHANGEFEED)
        self.assertNotEqual(acfact,None,'Unable to getInstance of AddressChangeFactory')
        arfact = AddressFactory.getInstance(FeedType.RESOLUTIONFEED)
        self.assertNotEqual(arfact,None,'Unable to getInstance of AddressResolutionFactory')
        
class Test_2_AddressTestSetters(unittest.TestCase):

    def setUp(self): 
        testlog.debug('Instantiate addressfactories')
        self.factories = {FeedType.reverse[ft]:AddressFactory.getInstance(ft) for ft in FeedType.reverse}
        
    def tearDown(self):
        testlog.debug('Destroy null address')
        self.factories = None        
        
    def test10_instAddresses(self):
        '''Tests that all the setters set a matching attribute i.e. setAttribute("X") -> self._Attribute = "X"'''
        faddr = self.factories['FEATURES'].getAddress()
        self.assertTrue(isinstance(faddr,Address), 'Features address not instantiated correctly')
        caddr = self.factories['CHANGEFEED'].getAddress()
        self.assertTrue(isinstance(caddr,AddressChange), 'Change address not instantiated correctly')
        raddr = self.factories['RESOLUTIONFEED'].getAddress()
        self.assertTrue(isinstance(raddr,AddressResolution), 'Resolution address not instantiated correctly') 
        self.assertTrue(isinstance(raddr.getWarnings(),list), 'Resolution address doesnt have warnings atrbute')
            
            
    def test20_convertAddresses(self):
        caddr = self.factories['CHANGEFEED'].getAddress()
        caddr.setVersion(1)
        caddr.setAddressId(1)
        caddr.setAddressNumber(100)
        caddr.setRoadName('One Road')
        chg_add = self.factories['CHANGEFEED'].convertAddress(caddr,ActionType.ADD)
        self.assertTrue(isinstance(chg_add,dict), 'Change Add request incorrect')
        chg_ret = self.factories['CHANGEFEED'].convertAddress(caddr,ActionType.RETIRE)
        self.assertTrue(isinstance(chg_ret,dict), 'Change Retire request incorrect')
        chg_cup = self.factories['CHANGEFEED'].convertAddress(caddr,ActionType.UPDATE)
        self.assertTrue(isinstance(chg_cup,dict), 'Change Update request incorrect')
        
    def test30_convertAddresses(self):
        raddr = self.factories['RESOLUTIONFEED'].getAddress()
        raddr.setVersion(1)
        raddr.setAddressNumber(100)
        raddr.setChangeId(100)
        raddr.setRoadName('One Road')
        chg_acc = self.factories['RESOLUTIONFEED'].convertAddress(raddr,ApprovalType.ACCEPT)
        self.assertTrue(isinstance(chg_acc,dict), 'Resolution Accept request incorrect')
        chg_dec = self.factories['RESOLUTIONFEED'].convertAddress(raddr,ApprovalType.DECLINE)
        self.assertTrue(isinstance(chg_dec,dict), 'Resolution Decline request incorrect')
        chg_rup = self.factories['RESOLUTIONFEED'].convertAddress(raddr,ApprovalType.UPDATE)
        self.assertTrue(isinstance(chg_rup,dict), 'Resolution Update request incorrect')
        


if __name__ == "__main__":
    unittest.main()
