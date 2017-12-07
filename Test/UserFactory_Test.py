'''
v.0.0.1

QGIS-AIMS-Plugin - UserFactory_Test

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on UserFactory class

Created on 29/10/2015

@author: aross
'''


import unittest
import sys
import re
import sys
import os
import inspect


sys.path.append('../AIMSDataManager/')
from FeatureFactory import FeatureFactory
from Feature import Feature
from AimsUtility import ActionType,ApprovalType, FeedType, FeatureType, FeedRef, UserActionType
from AimsLogging import  Logger
from UserFactory import UserFactory
from User import User

testlog = Logger.setup('test')

#---------------------------------------------------
# USERFactory
class Test_0_UserTestInstantiate(unittest.TestCase):
    
  def setUp(self):
    pass
    
  def tearDown(self):
    pass
    
  def test10_UserInstantiate(self):
    u = UserFactory(FeedRef(FeatureType.USERS, FeedType.ADMIN))
    self.assertIsNotNone(u, 'UserFactory not instantiated')
    self.assertTrue(isinstance(u, UserFactory), 'UserFactory not instantiated correctly')
    
  
  def test20_UserGetInstance(self):
    gt_c = UserFactory.getInstance(FeedRef(FeatureType.USERS, FeedType.ADMIN))
    self.assertIsNotNone(gt_c,'UserFactory not instantiated')
    self.assertEqual(gt_c.UFFT, FeedType.ADMIN, "UserFactory not correct type")
    
    
  def test30_UserGet(self):
    ufactory = UserFactory(FeedRef(FeatureType.USERS, FeedType.ADMIN))
    user = ufactory.get()
    ufact = ufactory.get()
    self.assertTrue(isinstance(ufact, User), 'User incorrectly returned')
    ufact = ufactory.get('ref 1')
    self.assertEqual(ufact._ref, 'ref 1', 'User incorrectly set')
    self.assertTrue(isinstance(ufact, User), 'User incorrectly returned')
    ufact = ufactory.get('ref 2', user)
    self.assertTrue(isinstance(ufact, User), 'User incorrectly returned')
    ufact = ufactory.get('ref 3', user, None, '.txt')
    self.assertTrue(isinstance(ufact, User), 'User incorrectly returned')
    
    

class Test_1_UserTestConvert(unittest.TestCase):
  
  def setUp(self):
    self.factory = UserFactory.getInstance(FeedRef(FeatureType.USERS, FeedType.ADMIN))
  
  def tearDown(self):
    self.factory = None
  
  def test10_instanceUser(self):
    uf = self.factory.get()
    self.assertTrue(isinstance(uf, User), 'User Not Instantiated Correctly')
    
  def test20_convertUser(self):
    uf = self.factory.get()
    uf.setVersion(1)
    uf.setUserId(2)
    uf.setEmail('a@email.com')
    uf._userName = 'user name'
    uf._requiresProgress = 'False'
    uf._organisation = 'org'
    uf._role = 'user role'
    
    u_add = self.factory.convert(uf, UserActionType.ADD)
    self.assertTrue(isinstance(u_add, dict), 'User add action incorrect')
    
    u_del = self.factory.convert(uf, UserActionType.DELETE)
    self.assertTrue(isinstance(u_del, dict), 'User delete action incorrect')
    
    u_upd = self.factory.convert(uf, UserActionType.UPDATE)
    self.assertTrue(isinstance(u_upd, dict), 'User update action incorrect')
    
  def test30_cast(self):
    ''' checks returns same thing, since is only one type. '''
    uf = self.factory.get()
    ucast = self.factory.cast(uf)
    self.assertTrue(isinstance(ucast, User))
    
#---------------------------------------------------------------------
# USER

class Test_2_User(unittest.TestCase):
  
  def setUp(self):
     self.user_setters = [i for i in dict(inspect.getmembers(User, predicate=inspect.ismethod)) if i[:3]=='set']
     self.user = User(FeedRef(FeatureType.USERS, FeedType.ADMIN))
    
  def tearDown(self):
    self.user_setters = None
    
  
  def test10_UserTest(self):      
    testlog.debug('Test_0.20 User instantiation test')
    self.assertIsNotNone(self.user,'User not instantiated')
    self.assertTrue(isinstance(self.user, User), 'User not instantiated correctly')
        
  def test20_UserSetters(self):
    self.user.setUserId(12)
    self.assertEqual(self.user._userId, 12, 'setter not correct')
    self.assertEqual(self.user.getUserId(), 12, 'getter not correct')
    
    self.user.setEmail('email')
    self.assertIsNone(self.user._email, 'email not set correct')
    self.user.setEmail('e@email.com')
    self.assertEqual(self.user._email, 'e@email.com', 'email not set correct')

  
if __name__ == "__main__":
    unittest.main()