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


ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)

from AIMSDataManager.AddressFactory import AddressFactory,AddressChangeFactory,AddressResolutionFactory
from AIMSDataManager.Address import Address,AddressChange,AddressResolution
from AIMSDataManager.AimsUtility import ActionType,ApprovalType, FeatureType, FeedType, FEEDS
from AIMSDataManager.AimsLogging import  Logger

testlog = Logger.setup('test')

#user to init an address, simple text string read from a stored config file
user_text = 'aims_user'
    
class Test_0_AddressFactorySelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        self.assertIsNotNone(testlog, 'Testlog not instantiated')
        testlog.debug('Address_Test Log')
        
    def test20_addressfactoryGetInstanceTest(self):  
        testlog.debug('Test_1.2 Address instantiation test')
        afact = AddressFactory.getInstance(FEEDS['AF'])
        self.assertIsNotNone(afact,'Unable to getInstance of AddressFactory')
        acfact = AddressFactory.getInstance(FEEDS['AC'])
        self.assertIsNotNone(acfact,'Unable to getInstance of AddressChangeFactory')
        arfact = AddressFactory.getInstance(FEEDS['AR'])
        self.assertIsNotNone(arfact,'Unable to getInstance of AddressResolutionFactory')
        
class Test_1_AddressTestSetters(unittest.TestCase):

    def setUp(self): 
        testlog.debug('Instantiate addressfactories')
        self.factories = {FeedType.reverse[f.ft]:AddressFactory.getInstance(f) for f in FEEDS.values() if f.et == FeatureType.ADDRESS}
        
    def tearDown(self):
        testlog.debug('Destroy null address')
        self.factories = None        
        
    def test10_instAddresses(self):
        '''Tests that all the setters set a matching attribute i.e. setAttribute("X") -> self._Attribute = "X"'''
        faddr = self.factories['FEATURES'].get()
        self.assertTrue(isinstance(faddr,Address), 'Features address not instantiated correctly')
        caddr = self.factories['CHANGEFEED'].get()
        self.assertTrue(isinstance(caddr,AddressChange), 'Change address not instantiated correctly')
        raddr = self.factories['RESOLUTIONFEED'].get()
        self.assertTrue(isinstance(raddr,AddressResolution), 'Resolution address not instantiated correctly') 
            
            
    def test20_convertAddresses(self):
        caddr = self.factories['CHANGEFEED'].get()
        caddr.setVersion(1)
        caddr.setAddressId(1)
        caddr.setAddressNumber(100)
        caddr.setRoadName('One Road')
        caddr._workflow_sourceUser = user_text
        chg_add = self.factories['CHANGEFEED'].convert(caddr,ActionType.ADD)
        self.assertTrue(isinstance(chg_add,dict), 'Change Add request incorrect')
        chg_ret = self.factories['CHANGEFEED'].convert(caddr,ActionType.RETIRE)
        self.assertTrue(isinstance(chg_ret,dict), 'Change Retire request incorrect')
        chg_cup = self.factories['CHANGEFEED'].convert(caddr,ActionType.UPDATE)
        self.assertTrue(isinstance(chg_cup,dict), 'Change Update request incorrect')
        
    def test30_convertAddresses(self):
        raddr = self.factories['RESOLUTIONFEED'].get()
        raddr.setVersion(1)
        raddr.setAddressNumber(100)
        raddr.setChangeId(100)
        raddr.setRoadName('One Road')
        raddr._workflow_reviewedUserName = user_text
        chg_acc = self.factories['RESOLUTIONFEED'].convert(raddr,ApprovalType.ACCEPT)
        self.assertTrue(isinstance(chg_acc,dict), 'Resolution Accept request incorrect')
        chg_dec = self.factories['RESOLUTIONFEED'].convert(raddr,ApprovalType.DECLINE)
        self.assertTrue(isinstance(chg_dec,dict), 'Resolution Decline request incorrect')
        chg_rup = self.factories['RESOLUTIONFEED'].convert(raddr,ApprovalType.UPDATE)
        self.assertTrue(isinstance(chg_rup,dict), 'Resolution Update request incorrect')
        


if __name__ == "__main__":
    unittest.main()
