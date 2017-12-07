'''
v.0.0.1

QGIS-AIMS-Plugin - GroupFactory_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on Group class

Created on 29/10/2015

@author: aross
'''

import unittest
import sys
import re
import sys
import os


sys.path.append('../AIMSDataManager/')

from AddressFactory import AddressFactory
from AimsUtility import ActionType,ApprovalType, FeedType, FeatureType, FeedRef, GroupActionType, GroupApprovalType
from AimsLogging import  Logger
from GroupFactory import GroupFactory, GroupChangeFactory, GroupResolutionFactory
from Group import Group, GroupChange, GroupResolution

testlog = Logger.setup('test')


#----------------------------------------------------
#GROUPFactory

class Test_0_GroupTestInstantiate(unittest.TestCase):
  
  def setUp(self):
    pass
    
  def tearDown(self):
    pass
    
  def test10_groupFactoryTest(self):
    gfact = GroupFactory(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
    self.assertIsNotNone(gfact,'GroupFactory not instantiated')
    gchan = GroupChangeFactory((FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)))
    self.assertIsNotNone(gchan, 'GroupChangeFactory not instantiated')
    greso = GroupResolutionFactory((FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED)))
    self.assertIsNotNone(greso, 'GroupResolutionFactory not instantiated')
    
  def test20_groupFactoryGetInstanceTest(self):
    gt_c = AddressFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
    self.assertIsNotNone(gt_c,'GroupChangeFactory not instantiated correctly')
    gt_r = AddressFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
    self.assertIsNotNone(gt_r,'GroupResolutionFactory not instantiated correctly')
    
    gt_cg = GroupFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
    self.assertIsNotNone(gt_cg, 'Group Factory not instantiated correctly')
    self.assertTrue(isinstance(gt_cg, GroupFactory),'Group Factory not instantiated correctly')
    gchan = GroupChangeFactory((FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)))
    self.assertTrue(isinstance(gchan, GroupChangeFactory), 'Group Change Factory not instantiated correctly')
    
    gt_rg = GroupFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
    self.assertIsNotNone(gt_rg, 'Group Factory not instantiated correctly')
    self.assertTrue(isinstance(gt_rg, GroupFactory),'Group Factory not instantiated correctly')
    greso = GroupResolutionFactory((FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED)))
    self.assertTrue(isinstance(greso, GroupResolutionFactory), 'Group Resolution Factory not instantiated correctly') 
    
  def test30_groupGet(self):
    gfactory = GroupFactory(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
    group = gfactory.get()
    gfact = gfactory.get()
    self.assertTrue(isinstance(gfact, Group), 'Group incorrectly returned')
    gfact = gfactory.get('ref 1')
    self.assertEqual(gfact._ref, 'ref 1', 'Group incorrectly set')
    self.assertTrue(isinstance(gfact, Group), 'Group incorrectly returned')
    gfact = gfactory.get('ref 2', group)
    self.assertTrue(isinstance(gfact, Group), 'Group incorrectly returned')
    gfact = gfactory.get('ref 3', group, None, '.txt')
    self.assertTrue(isinstance(gfact, Group), 'Group incorrectly returned')
    
    
class Test_1_GroupTestConvert(unittest.TestCase):
  
  def setUp(self):
    testlog.debug("Instantiate factories")
    self.factories = {
      'CHANGEFEED': AddressFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)),
      'RESOLUTIONFEED': AddressFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
      }
    
  def tearDown(self):
    testlog.debug("Destroy Factories")
    self.factories = None
    
  def test20_convertGroupChange(self):
    caddrg = self.factories['CHANGEFEED'].get()
    caddrg.setVersion(1)
    caddrg.setChangeGroupId(12)
    caddrg._components_addressId = 100
    
    chg_rep = self.factories['CHANGEFEED'].convert(caddrg, GroupActionType.REPLACE)
    self.assertTrue(isinstance(chg_rep, dict), 'Change Replace action incorrect')
    
    chg_upd = self.factories['CHANGEFEED'].convert(caddrg, GroupActionType.UPDATE)
    self.assertTrue(isinstance(chg_upd, dict), 'Change Update action incorrect')
    
    chg_sub = self.factories['CHANGEFEED'].convert(caddrg, GroupActionType.SUBMIT)
    self.assertTrue(isinstance(chg_sub, dict), 'Change Submit action incorrect')
    
    chg_clo = self.factories['CHANGEFEED'].convert(caddrg, GroupActionType.CLOSE)
    self.assertTrue(isinstance(chg_clo, dict), 'Change Close action incorrect')
    
    chg_adr = self.factories['CHANGEFEED'].convert(caddrg, GroupActionType.ADDRESS)
    self.assertTrue(isinstance(chg_adr, dict), 'Change Address action incorrect')
    
    chg_add = self.factories['CHANGEFEED'].convert(caddrg, GroupActionType.ADD)
    self.assertTrue(isinstance(chg_add, dict), 'Change Add action incorrect')
    
    chg_rem = self.factories['CHANGEFEED'].convert(caddrg, GroupActionType.REMOVE)
    self.assertTrue(isinstance(chg_rem, dict), 'Change Remove action incorrect')
    
  
  def test30_convertGroupResolution(self):
    raddrg = self.factories['RESOLUTIONFEED'].get()
    raddrg.setVersion(2)
    raddrg.setChangeGroupId(13)
    res_acc = self.factories['RESOLUTIONFEED'].convert(raddrg, GroupApprovalType.ACCEPT)
    self.assertTrue(isinstance(res_acc, dict), 'Resolution Accept approval incorrect')
    
    res_dec = self.factories['RESOLUTIONFEED'].convert(raddrg, GroupApprovalType.DECLINE)
    self.assertTrue(isinstance(res_dec, dict), 'Resolution Decline approval incorrect')
    
    res_add = self.factories['RESOLUTIONFEED'].convert(raddrg, GroupApprovalType.ADDRESS)
    self.assertTrue(isinstance(res_add, dict), 'Resolution Accept approval incorrect')
    
    res_upd = self.factories['RESOLUTIONFEED'].convert(raddrg, GroupApprovalType.UPDATE)
    self.assertTrue(isinstance(res_upd, dict), 'Resolution Update approval incorrect')
    
    

       
class Test_4_GroupCast(unittest.TestCase):
    '''
    Test Adddress Factory Casting between Feature, ChangeFeed and ResolutionFeed.
    '''
  
    def setUp(self):
      testlog.debug('Instantiate Group Factories')
      self.factories = {
      'CHANGEFEED': GroupFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)),
      'RESOLUTIONFEED': GroupFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
      }
      
    def tearDown(self):
      testlog.debug('Destroy Null Groups')
      self.factories = None
      
    ''' Cast using AddressFactory '''
    def test40_castGroup(self):
      gcfact = AddressFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
      grfact = AddressFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
      gc = gcfact.get()
      gr = grfact.get()
      gccast = gcfact.cast(gc)
      self.assertTrue(isinstance(gccast, GroupChange), 'Group Change cast not correct')
      gccast = grfact.cast(gc)
      self.assertTrue(isinstance(gccast, GroupResolution), 'Group Resolution cast not correct')
    
    ''' Cast using GroupFactory '''
    def test41_castGroupFact(self):
      gcfact = GroupChangeFactory((FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)))
      grfact = GroupResolutionFactory((FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED)))
      gc = gcfact.get()
      gr = grfact.get()
      gccast = gcfact.cast(gr)
      self.assertTrue(isinstance(gccast, GroupChange), 'Group Change cast not correct')
      gccast = grfact.cast(gc)
      self.assertTrue(isinstance(gccast, GroupResolution), 'Group Resolution cast not correct')
      

#-----------------------------------------------------------------------------------------
#GROUP

class Test_5_GroupTest(unittest.TestCase):
  
  def setUp(self):
    testlog.debug('Instantiate Group Factories')
    self.factories = {
      'CHANGEFEED': GroupFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED)),
      'RESOLUTIONFEED': GroupFactory.getInstance(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
    }
    self.gcfact = GroupChangeFactory(FeedRef(FeatureType.GROUPS, FeedType.CHANGEFEED))
    self.grfact = GroupResolutionFactory(FeedRef(FeatureType.GROUPS, FeedType.RESOLUTIONFEED))
    
  
  def tearDown(self):
    testlog.debug('Destroy Null Groups')
    self.factories = None
  
  def test10_instanceGroup(self):
    g = self.factories['CHANGEFEED'].get()
    self.assertIsNotNone(g, 'Group not instantiated')
    self.assertTrue(isinstance(g, Group), 'Group not instantiated correctly')
    
    gc = self.gcfact.get()
    self.assertIsNotNone(gc, 'GroupChange not instantiated')
    self.assertTrue(isinstance(gc, GroupChange), 'GroupChange not instantiated correctly')
    
    gr = self.grfact.get()
    self.assertIsNotNone(gr, 'GroupResolution not instantiated')
    self.assertTrue(isinstance(gr, GroupResolution), 'GroupResolution not instantiated correctly')
    
    
  def test20_groupSetters(self):
    group = self.factories['CHANGEFEED'].get()
    group.setChangeGroupId(12)
    self.assertEqual(12, group._changeGroupId, 'Group setting incorrectly')
    self.assertEqual(12, group.getChangeGroupId(), 'Group getting incorrectly')
    
    group.setSourceReason('source reason ...')
    self.assertEqual('source reason ...', group._workflow_sourceReason, 'Group setting incorrectly')
    self.assertEqual('source reason ...', group.getSourceReason(), 'Group getting incorrectly')
    
    group.setSourceUser('source user ...')
    self.assertEqual('source user ...', group._workflow_sourceUser, 'Group setting incorrectly')
    self.assertEqual('source user ...', group.getSourceUser(), 'Group getting incorrectly')
    
    group.setSubmitterUserName('user name ...')
    self.assertEqual('user name ...', group._submitterUserName, 'Group setting incorrectly')
    self.assertEqual('user name ...', group.getSubmitterUserName(), 'Group getting incorrectly')


if __name__ == "__main__":
    unittest.main()