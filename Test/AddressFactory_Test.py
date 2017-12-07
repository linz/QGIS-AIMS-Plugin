'''
v.0.0.1

QGIS-AIMS-Plugin - AddressFactory_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on Address class

Created on 29/10/2015

@author: jramsay
@edited: aross
'''
import unittest
import sys
import re
import sys
import os

sys.path.append('../AIMSDataManager/')

from AddressFactory import AddressFactory,AddressChangeFactory,AddressResolutionFactory, AddressFeedFactory
from Address import Address,AddressChange,AddressResolution
from AimsUtility import ActionType,ApprovalType, FeedType, FeatureType, FeedRef
from AimsLogging import  Logger

testlog = Logger.setup('test')

#user to init an address, simple text string read from a stored config file
#user_text = 'address.features'

@unittest.skip("TemplateReader No Longer Exists")
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
    '''
    Test AddressFactory instantiation and ablity to get the instance.
    '''
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('Address_Test Log')
    
    def test20_addressfactoryTest(self):     
        testlog.debug('Test_1.20 Address instantiation test')
        afact = AddressFactory(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES))
        self.assertNotEqual(afact,None,'AddressFactory not instantiated')    
        acfact = AddressChangeFactory(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED))
        self.assertNotEqual(acfact,None,'AddressChangeFactory not instantiated')    
        arfact = AddressResolutionFactory(FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED))
        self.assertNotEqual(arfact,None,'AddressResolutionFactory not instantiated')    
 
    def test30_addressfactoryGetInstanceTest(self):   
        testlog.debug('Test_1.30 Address instantiation test')
        afact = AddressFactory.getInstance(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES))
        self.assertNotEqual(afact,None,'Unable to getInstance of AddressFactory')
        acfact = AddressFactory.getInstance(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED))
        self.assertNotEqual(acfact,None,'Unable to getInstance of AddressChangeFactory')
        arfact = AddressFactory.getInstance(FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED))
        self.assertNotEqual(arfact,None,'Unable to getInstance of AddressResolutionFactory')
       
        


class Test_2_AddressTestConvert(unittest.TestCase):
   

    def setUp(self): 
        testlog.debug('Instantiate Address Factories')
        self.factories = {FeedType.reverse[ft]:AddressFactory.getInstance(FeedRef(FeatureType.USERS if ft == 3 else FeatureType.ADDRESS,ft)) for ft in FeedType.reverse}
        
     
    def tearDown(self):
        testlog.debug('Destroy null address')
        self.factories = None        
           
            
    def test20_convertChangeAddresses(self):
        ''' Tests that address factory changefeeds can be converted to json payload equivalent.'''
        caddr = self.factories['CHANGEFEED'].get()
        caddr.setVersion(1)
        caddr.setAddressId(1)
        caddr.setAddressNumber(100)
        caddr.setRoadName('One Road')
        caddr.setSourceUser('Source User')
        
        chg_add = self.factories['CHANGEFEED'].convert(caddr,ActionType.ADD)
        self.assertTrue(isinstance(chg_add,dict), 'Change Add request incorrect')
        chg_ret = self.factories['CHANGEFEED'].convert(caddr,ActionType.RETIRE)
        self.assertTrue(isinstance(chg_ret,dict), 'Change Retire request incorrect')
        chg_cup = self.factories['CHANGEFEED'].convert(caddr,ActionType.UPDATE)
        self.assertTrue(isinstance(chg_cup,dict), 'Change Update request incorrect')
        
        
    def test30_convertResolutionAddresses(self):
        ''' Tests that address factory resolutionfeeds can be converted to json payload equivalent.'''
        raddr = self.factories['RESOLUTIONFEED'].get()
        raddr.setVersion(1)
        raddr.setAddressNumber(100)
        raddr.setChangeId(100)
        raddr.setRoadName('One Road')
        chg_acc = self.factories['RESOLUTIONFEED'].convert(raddr,ApprovalType.ACCEPT)
        self.assertTrue(isinstance(chg_acc,dict), 'Resolution Accept request incorrect')
        chg_dec = self.factories['RESOLUTIONFEED'].convert(raddr,ApprovalType.DECLINE)
        self.assertTrue(isinstance(chg_dec,dict), 'Resolution Decline request incorrect')
        chg_rup = self.factories['RESOLUTIONFEED'].convert(raddr,ApprovalType.UPDATE)
        self.assertTrue(isinstance(chg_rup,dict), 'Resolution Update request incorrect')
        chg_sup = self.factories['RESOLUTIONFEED'].convert(raddr,ApprovalType.SUPPLEMENT)
        self.assertTrue(isinstance(chg_sup,dict), 'Resolution Supplement request incorrect')
        
class Test_3_AddressFeedFactory(unittest.TestCase):
  
    def setUp(self):
        testlog.debug('Instantiate Address Factories')
        self.acfact = AddressChangeFactory(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED))
        self.affact = AddressResolutionFactory(FeedRef(FeatureType.ADDRESS, FeedType.RESOLUTIONFEED))
        
      
    def tearDown(self):
        testlog.debug('Destroy null address')
        self.acfact = None
        self.affact = None
      
      
    def test10_convertChangeAddresses(self):
        ''' Tests that address change factory changefeeds can be converted to json payload equivalent.'''
        caddr = self.acfact.get()
        caddr.setVersion(1)
        caddr.setAddressId(1)
        caddr.setAddressNumber(100)
        caddr.setRoadName('One Road')
        caddr.setSourceUser('Source User')
        chg_add = self.acfact.convert(caddr,ActionType.ADD)
        self.assertTrue(isinstance(chg_add,dict), 'Change Add request incorrect')
        chg_ret = self.acfact.convert(caddr,ActionType.RETIRE)
        self.assertTrue(isinstance(chg_ret,dict), 'Change Retire request incorrect')
        chg_cup = self.acfact.convert(caddr,ActionType.UPDATE)
        self.assertTrue(isinstance(chg_cup,dict), 'Change Update request incorrect')
        
        
    def test20_convertResolutionAddresses(self):
        ''' Tests that address change factory changefeeds can be converted to json payload equivalent.'''
        raddr = self.affact.get()
        raddr.setVersion(1)
        raddr.setAddressNumber(100)
        raddr.setChangeId(100)
        raddr.setRoadName('One Road')
        chg_acc = self.affact.convert(raddr,ApprovalType.ACCEPT)
        self.assertTrue(isinstance(chg_acc,dict), 'Resolution Accept request incorrect')
        chg_dec = self.affact.convert(raddr,ApprovalType.DECLINE)
        self.assertTrue(isinstance(chg_dec,dict), 'Resolution Decline request incorrect')
        chg_rup = self.affact.convert(raddr,ApprovalType.UPDATE)
        self.assertTrue(isinstance(chg_rup,dict), 'Resolution Update request incorrect')
        chg_sup = self.affact.convert(raddr,ApprovalType.SUPPLEMENT)
        self.assertTrue(isinstance(chg_sup,dict), 'Resolution Supplement request incorrect')

class Test_4_AddressCast(unittest.TestCase):
    '''
    Test Adddress Factory Casting between Feature, ChangeFeed and ResolutionFeed.
    '''
  
    def setUp(self):
      testlog.debug('Instantiate Address Factories')
      self.factories = {FeedType.reverse[ft]:AddressFactory.getInstance(FeedRef(FeatureType.USERS if ft == 3 else FeatureType.ADDRESS,ft)) for ft in FeedType.reverse}
      
    def tearDown(self):
      testlog.debug('Destroy Null Addresses')
      self.factories = None
  
    def test10_castAddress(self):
      af = self.factories['FEATURES'].get()
      ac = self.factories['CHANGEFEED'].get()
      ar = self.factories['RESOLUTIONFEED'].get()
      
      af = self.factories['CHANGEFEED'].cast(af)
      self.assertTrue(isinstance(af, AddressChange), 'Address Feature to ChangeFeed Cast Incorrect')
      af = self.factories['FEATURES'].get()
      af = self.factories['RESOLUTIONFEED'].cast(af)
      self.assertTrue(isinstance(af, AddressResolution), 'Address Feature to ResolutionFeed Cast Incorrect')
      
      ac = self.factories['FEATURES'].cast(ac)
      self.assertTrue(isinstance(ac, Address), 'Address ChangeFeed to Feature Cast Incorrect')
      ac = self.factories['CHANGEFEED'].get()
      ac = self.factories['RESOLUTIONFEED'].cast(ac)
      self.assertTrue(isinstance(ac, AddressResolution), 'Address ChangeFeed to ResolutionFeed Cast Incorrect')
      
      ar = self.factories['FEATURES'].cast(ar)
      self.assertTrue(isinstance(ar, Address), 'Address ResolutionFeed to Feature Cast Incorrect')
      ar = self.factories['RESOLUTIONFEED'].get()
      ar = self.factories['CHANGEFEED'].cast(ar)
      self.assertTrue(isinstance(ar, AddressChange), 'Address ResolutionFeed to ChangeFeed Cast Incorrect')
            
        
class Test_5_AddressMeta(unittest.TestCase):
    '''
    Test address factory metadata setup.
    '''
  
    def setUp(self):
        testlog.debug('Instantiate Addres Factory')
        self.factories = {FeedType.reverse[ft]:AddressFactory.getInstance(FeedRef(FeatureType.USERS if ft == 3 else FeatureType.ADDRESS,ft)) for ft in FeedType.reverse}
        
    def tearDown(self):
        testlog.debug('Destroy Null Address')
        self.factories = None
        
    def test10_setMeta(self):
        adfeat = self.factories['FEATURES'].get()
        meta = "feature meta data"
        adfeat.setMeta(meta)
        self.assertEqual(adfeat.getMeta(), meta, 'Feature metadata not set correctly')
        
        adchan = self.factories['CHANGEFEED'].get()
        meta = "change meta data"
        adchan.setMeta(meta)
        self.assertEqual(adchan.getMeta(), meta, 'ChangeFeed metadata not set correctly')
        
        adreso = self.factories['RESOLUTIONFEED'].get()
        meta = "resolution meta data"
        adreso.setMeta(meta)
        self.assertEqual(adreso.getMeta(), meta, 'ResolutionFeed metadata not set correctly')
        
        

if __name__ == "__main__":
    unittest.main()
