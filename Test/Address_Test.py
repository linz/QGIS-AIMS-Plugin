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
@edited: aross
'''
import unittest
import inspect
import sys
import re
import sys
import os

sys.path.append('../AIMSDataManager/')

from Address import Address,AddressChange,AddressResolution,Position, Supplemental, Entity, AddressRequestFeed, EntityValidation, EntityAddress
from AddressFactory import AddressChangeFactory,AddressResolutionFactory, AddressFactory
from AimsUtility import ActionType, FeedType, FeatureType, FeedRef
from AimsLogging import  Logger
from FeatureFactory import FeatureFactory

testlog = Logger.setup('test')

#user to init an address, simple text string read from a stored config file
user_text = FeedRef(FeatureType.ADDRESS, FeedType.FEATURES)


class Test_0_AddressSelfTest(unittest.TestCase):
    '''
    Test Address Classes can be instantiated 
    '''
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        self.assertIsNotNone(testlog,'Testlog not instantiated')
        testlog.debug('Address_Test Log')
        
    def test20_addressTest(self):      
        testlog.debug('Test_0.20 Address instantiation test')
        address = Address(user_text)
        self.assertIsNotNone(address,'Address not instantiated')
        self.assertTrue(isinstance(address, Address), 'Address not instantiated correctly')
        
    def test30_positionTest(self):
        testlog.debug('Test_0.30 Position instantiation test')
        position = Position()
        self.assertIsNotNone(position, 'Position not instantiated')
        self.assertTrue(isinstance(position, Position), 'Position not instantiated correctly')
     
    def test40_supplementalTest(self):
        testlog.debug('Test_0.40 Supplemental instantiation test')
        sup = Supplemental()
        self.assertIsNotNone(sup, 'Supplemental not instantiated')
        self.assertTrue(isinstance(sup, Supplemental), 'Supplemental not instantiated correctly')
        
    def test50_entityTest(self):
        testlog.debug('Test_0.50 Entity instantiation test')
        ent = Entity()
        self.assertIsNotNone(ent, 'Entity not instantiated')
        self.assertTrue(isinstance(ent, Entity), 'Entity not instantiated correctly')
        
    def test60_addressRequestTest(self):
        testlog.debug('Test_0.60 Address Request Feed instantiation test')
        arf = AddressRequestFeed(Address(user_text))
        self.assertIsNotNone(arf, 'Address Request not instantiated')
        self.assertTrue(isinstance(arf, AddressRequestFeed), 'Address Request Feed not instantiated correctly')
        
    def test70_addressChangeTest(self):
        testlog.debug('Test_0_70 Address Change instantiation test')
        ac = AddressChange(AddressRequestFeed(Address(user_text)))
        self.assertIsNotNone(ac, 'Address Change not instantiated')
        self.assertTrue(isinstance(ac, AddressChange), 'Address Change not instantiated correctly')
        
    def test80_addressResolutionTest(self):
        testlog.debug('Test_0_80 Address Resolution instantiation test')
        ar = AddressResolution(AddressRequestFeed(Address(user_text)))
        self.assertIsNotNone(ar, 'Address Resolution not instantiated')
        self.assertTrue(isinstance(ar, AddressResolution), 'Address Resolution not instantiated correctly')
        
    def test90_entityValidationTest(self):
        testlog.debug('Test_0_90 Entity Validation instantiation test')
        ev = EntityValidation(Entity())
        self.assertIsNotNone(ev, 'Entity Validation not instantiated')
        self.assertTrue(isinstance(ev, EntityValidation), 'Entity Validation not instantiated correctly')
        
    def test100_entityAddressTest(self):
        testlog.debug('Test_0_100 Entity Address instantion test')
        ea = EntityAddress(Entity())
        self.assertIsNotNone(ea, 'Entity Address not instantiated')
        self.assertTrue(isinstance(ea, EntityAddress), 'Entity Address not instantiated correctly')
        

#--------------------------------------------------
# ADDRESS

class Test_1_AddressTestSetters(unittest.TestCase):
    '''
    Test Address Setters
    '''
    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        self._addFac = AddressFactory.getInstance(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED))
        self._addF = AddressFactory.getInstance(FeedRef(FeatureType.ADDRESS, FeedType.FEATURES))
        self._address = self._addFac.get()
        self._address_setters = [i for i in dict(inspect.getmembers(Address, predicate=inspect.ismethod)) if i[:3]=='set']
        self._skipped = []

        
    def tearDown(self):
        testlog.debug('Destroy null address')
        self._address = None
        self._address_setters = None
        self._addFac = None
        self._addF = None
        self._skipped = None
        
    def test10_instSetters(self):
        '''Tests that all the setters set a matching attribute i.e. setAttribute("X") -> self._Attribute = "X"
	   setAddressPositions, setVersion, setPublishDate, setRequestId, setErrors and setMeta tested separately
	   due to implementation. '''
        testlog.debug('Test_1.10 Instantiate all setters')
        skip = ['setAddressPositions', 'setVersion', 'setPublishDate', 'setRequestId', 'setErrors', 'setMeta']
        for asttr in self._address_setters:
          if asttr not in skip:
	    aval = self._generateAttrVal(asttr)
	    aname = self._generateAttrName(asttr)
	    getattr(self._address, asttr)(aval)
	    if aname != '':
	      self.assertEqual(getattr(self._address, aname), aval, 'set* : Setter {} not setting correct attribute value {}'.format(asttr,aval))
	    else:
	      self._skipped.append(asttr)
	
	while len(self._skipped) > 0:
	  each = self._skipped.pop()
	  if each not in skip:
	    aval = self._generateAttrVal(each)
	    aname = self._generateAttrName(each)
	    getattr(self._address, each)(aval)
	    self.assertEqual(getattr(self._address, aname), aval, 'set* : Setter {} not setting correct attribute value {}'.format(each,aval))
	    
	self.assertEqual(self._address.getChangeId(), self._generateAttrVal('setChangeId'), 'Change Id not getting correctly')
	self.assertEqual(self._address.getAddressId(), self._generateAttrVal('setAddresId'), 'Address Id not getting correctly')
	self._address.setRequestId(10)
	self.assertEqual(self._address.getFullNumber(),'UV/AN-ANHANS', 'Full Number not getting correctly')
	    
    def test20_addressPositionSetter(self):
      p = Position()
      self._address.setAddressPositions(p)
      self.assertEqual(getattr(self._address, '_addressedObject_addressPositions')[0], p, 'set*: Setter not setting correct attribute value')
      self.assertEqual(self._address.getAddressPositions()[0], p, 'Getter not getting correct attribute value')
      
      self.assertEqual(self._address.getConvertedAddressPositions(), getTestPosition5(), 'Position not correctly converted')
      p2a = Position()
      p2a.setPositionType("Position1")
      p2b = Position()
      p2b.setPositionType("Position 2")
      
      p2 = [p2a, p2b]
      self._address.setAddressPositions(p2)
      self.assertEqual(self._address.getConvertedAddressPositions(), getTestPosition4(), 'Positions not correctly converted')
      
    def test30_addressVersionSetter(self):
      self._address.setVersion(10)
      self.assertEqual(self._address.getVersion(), 10, 'Address Version not setting correctly')
      
      self._address.setVersion('10')
      self.assertIsNone(self._address.getVersion(), 'Address Version not setting correctly')
      
    def test40_addressPublishDate(self):
      self._address.setPublishDate('2017-12-05')
      self.assertEqual(self._address._publishDate, '2017-12-05', 'Address Publish Date not setting correctly')
      
      self._address.setPublishDate('2017/12/05')
      self.assertIsNone(self._address._publishDate, 'Address Publish Date not setting correctly')
      
      self._address.setPublishDate(2017-12-15)
      self.assertIsNone(self._address._publishDate, 'Address Publish Date not setting correctly')
      
      
    def test50_addressMetaData(self):
      meta = "metadata ...."
      self._address.setMeta(meta)
      self.assertEqual(meta, self._address.getMeta(), 'Metadata not set')
      self.assertEqual(meta, self._address.meta, 'Metadata not set correctly')
      
      add = AddressFactory.getInstance(FeedRef(FeatureType.ADDRESS, FeedType.CHANGEFEED)).get()
      self.assertIsNone(add.getMeta(), 'Metadata not returned correctly')
      
      add.setMeta()
      self.assertIsNotNone(add.getMeta(), 'Metadata not set correctly on default')
      
      
      
      add.setErrors('Error 1: ...')
      self.assertEqual(add.getErrors(), 'Error 1: ...', 'Errors not set')
      self.assertEqual(add.meta.errors, 'Error 1: ...', 'Errors not set correctly')
      
      
      add.setRequestId(10)
      self.assertEqual(add.getRequestId(), 10, 'Request Id not set')
      self.assertEqual(add.meta.requestId, 10, 'Request Id not set correctly')
      add.setRequestId('10')
      self.assertIsNone(add.meta.requestId, 'Request Id not set correctly')
      
      
      	    
#------------------------------------------------------------------------------    
    def _generateAttrVal(self,setmthd):
        s = self._special(setmthd)
        if s: return s
        setmthd = re.match('set_*(.*)',setmthd).group(1)
        return setmthd[:1].upper()+''.join([s for s in setmthd[1:] if ord(s)>64 and ord(s)<91])
    
    def _generateAttrName(self,setmthd):
        setmthd = re.match('set_*(.*)',setmthd).group(1)
        if setmthd[:3] == 'Add' and setmthd[:7] != 'Address':
	  setmthd = setmthd[3:]
        sm = '_'+setmthd[:1].lower()+setmthd[1:]
        #print(sm)
        if hasattr(self._address, sm):
	  return sm
	elif hasattr(self._address, '_components'+sm):
	  return '_components' + sm
	elif hasattr(self._address, '_workflow'+sm):
	  return '_workflow'+sm
	elif hasattr(self._address, '_addressedObject'+sm):
	  return '_addressedObject'+sm
	elif hasattr(self._address, '_codes'+sm):
	  return '_codes'+sm
	else:
	  return ''
	
    
    def _special(self,meth):
        if meth == 'setObjectType':return 'Parcel'
        if meth == 'setAddressType':return 'Road' 
        if meth == 'setLifecycle':return 'Current'
        return

  
#--------------------------------------
# ENTITY 

class Test_3_Entity(unittest.TestCase):
  '''
  Test Entity Instance 
  '''
  def setUp(self):
    testlog.debug('Instantiate Entity')
    self.entity = Entity(ref = 'entity1')
    self._d = {'class':'upper','rel':["rel", "rel2"],'properties':{'ruleId': "1",'description': "description .. ",'severity': "fine"}}
    self.entity_setters = [i for i in dict(inspect.getmembers(Entity, predicate=inspect.ismethod)) if i[:3]=='set']
    
  def tearDown(self):
    testlog.debug('Destroy Entity')
    self._d = None
    self.entity = None
    
  @unittest.expectedFailure
  def test10_getInstance(self):
     
    e = self.entity.getInstance(self._d)
    self.assertTrue(isinstance(e, Entity), 'Incorrect entity instance')
     
    vEntity = EntityValidation(Entity())
    self.assertTrue(isinstance(vEntity, EntityValidation), 'Entity Validation instance incorrect')
    aEntity = EntityAddress(Entity())
    self.assertTrue(isinstance(aEntity, EntityAddress), 'Entity Address instance incorrect')
    
    # Error with index out of range if no parameters sent to getInstance.
    self.assertTrue(isinstance(self.entity.getInstance(), Entity), 'Incorrect entity instance')
    
  def test20_entitySet(self):
    #Changed Address.py from self._ruleId to be all same as self._properties_ruleId
    
    self.assertIsNotNone(self.entity.get(), 'Entity returned empty')

    self.entity.set(self._d)
    self.assertEqual(self.entity.get(), self._d, 'Entity incorrectly set')

    for asm in self.entity_setters:
      if asm != 'set':
        aval = self._generateAttrVal(asm)
        getattr(self.entity, asm)(aval)
    self.assertEqual(self.entity.get(), getTestData3(), 'JSON Supplemental constructed incorrectly {}')

#------------------------------------------------------------------------------    
  def _generateAttrVal(self,setmthd):
    s = self._special(setmthd)
    if s: return s
    setmthd = re.match('set_*(.*)',setmthd).group(1)
    return setmthd[:1].upper()+''.join([s for s in setmthd[1:] if ord(s)>64 and ord(s)<91])
    
  def _generateAttrName(self,setmthd):
    setmthd = re.match('set_*(.*)',setmthd).group(1)
    return '_'+setmthd[:1].lower()+setmthd[1:]
    
  def _special(self,meth):
    if meth == 'setClass':return 'Middle'
    if meth == 'setSeverity':return 'Fine' 
    return    

#-------------------------------------------
# SUPPLEMENTAL

class Test_6_Supplemental(unittest.TestCase):
   '''
   Test Supplemental Instance
   '''
   def setUp(self):
    testlog.debug('Instantiate Supplemental')
    self.supplement = Supplemental(ref = 'sup1')
    self.supplement_setters = [i for i in dict(inspect.getmembers(Supplemental, predicate=inspect.ismethod)) if i[:3]=='set']
    self._d = {'class':'upper','rel':["rel", "rel2"],'properties':{'ruleId': "1",'description': "description .. ",'severity': "fine"}}
    
   def tearDown(self):
    testlog.debug('Destroy Supplemental')
    self.supplement_setters = None
    self._d = None
    self.supplement = None
    
   @unittest.expectedFailure
   def test10_getInstance(self):
     # Error with index out of range if no parameters sent to getInstance.
     self.assertTrue(isinstance(self.supplement.getInstance(), Supplemental), 'Incorrect supplemental instance')
     
     s = self.supplement.getInstance(self._d)
     self.assertTrue(isinstance(s, Supplemental), 'Incorrect supplemental instance')
    
   def test20_supplementSet(self):
    #Changed Address.py from self._ruleId to be all same as self._properties_ruleId
    
    self.assertIsNotNone(self.supplement.get(), 'Supplemental returned empty')

    self.supplement.set(self._d)
    self.assertEqual(self.supplement.get(), self._d, 'Supplemental incorrectly set')

    for asm in self.supplement_setters:
      if asm != 'set':
        aval = self._generateAttrVal(asm)
        getattr(self.supplement, asm)(aval)
    self.assertEqual(self.supplement.get(), getTestData3(), 'JSON Supplemental constructed incorrectly {}')
    

    
    
#------------------------------------------------------------------------------    
   def _generateAttrVal(self,setmthd):
    s = self._special(setmthd)
    if s: return s
    setmthd = re.match('set_*(.*)',setmthd).group(1)
    return setmthd[:1].upper()+''.join([s for s in setmthd[1:] if ord(s)>64 and ord(s)<91])
    
   def _generateAttrName(self,setmthd):
    setmthd = re.match('set_*(.*)',setmthd).group(1)
    return '_'+setmthd[:1].lower()+setmthd[1:]
    
   def _special(self,meth):
    if meth == 'setClass':return 'Middle'
    if meth == 'setSeverity':return 'Fine' 
    return    
    
  
#----------------------------------------
# POSITION

class Test_7_Position(unittest.TestCase):
  '''
  Test Position Instance
  '''
  def setUp(self):
    testlog.debug('Instantiate Position')
    self.position = Position()
    self._position_setters = [i for i in dict(inspect.getmembers(Position, predicate=inspect.ismethod)) if i[:3]=='set']
    self._pdef = {'position':{'type':'Line','coordinates':[[0.0,0.0],[0.1,0.1]],'crs':{'type':'crs name','properties':{'name':'urn:ogc:def:crs:EPSG::4168'}}},'positionType':'Position Type','primary':False}
  
  def tearDown(self):
    testlog.debug('Destroy Position')
    self._pdef = None
    self._position_setters = None
    self.position = None
    
  
  def test_10_getInstance(self):
    '''
    Test different parameters of getting and setting a position instance
    '''
    self.assertTrue(isinstance(self.position.getInstance(), Position), 'Incorrect position instance')
    
    p = self.position.getInstance(self._pdef)
    self.assertTrue(isinstance(p, Position), 'Incorrect position instance')
    
    self.assertIsNotNone(p.get(), 'Position returned empty')    
    self.assertEqual(p.get(), self._pdef, 'Position incorrectly set and returned')
    
    pa = self.position.getInstance(self._pdef, AddressFactory)
    self.assertTrue(isinstance(pa, Position), 'Incorrect position instance')
    self.assertEqual(p.get(), self._pdef, 'Position incorrectly set and returned')
    
      
    
  def test_20_setters(self):
    '''
    Test individual position setters
    '''
    for asm in self._position_setters:
      if asm != 'set':
        aval = self._generateAttrVal(asm)
        getattr(self.position, asm)(aval)
    self.assertEqual(self.position.get(), getTestData2(), 'JSON Position constructed incorrectly {}')
    
    self.position.set(self._pdef)
    self.assertEqual(self.position.get(), self._pdef, 'Position set not returned correctly')
    
    
#------------------------------------------------------------------------------    
  def _generateAttrVal(self,setmthd):
    s = self._special(setmthd)
    if s: return s
    setmthd = re.match('set_*(.*)',setmthd).group(1)
    return setmthd[:1].upper()+''.join([s for s in setmthd[1:] if ord(s)>64 and ord(s)<91])
    
  def _generateAttrName(self,setmthd):
    setmthd = re.match('set_*(.*)',setmthd).group(1)
    return '_'+setmthd[:1].lower()+setmthd[1:]
    
  def _special(self,meth):
    if meth == 'setCoordinates':return '[0.1,1.0,2.1]'
    if meth == 'setType':return 'Line' 
    return


def getTestPosition5():
  return [{'position': {'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::4167'}}, 'type': 'Point', 'coordinates': [0.0, 0.0]}, 'positionType': 'Unknown', 'primary': True}]


def getTestPosition4():
  return [{'position': {'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::4167'}}, 'type': 'Point', 'coordinates': [0.0, 0.0]}, 'positionType': 'Position1', 'primary': True}, {'position': {'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::4167'}}, 'type': 'Point', 'coordinates': [0.0, 0.0]}, 'positionType': 'Position 2', 'primary': True}]


def getTestData3():
  return {'class':'Middle', 'rel':'R', 'properties':{'ruleId':'RI', 'description':'D','severity':'Fine'}}

def getTestData2():
  return {'position': {'crs': {'type': 'CT', 'properties': {'name': 'CPN'}}, 'type': 'Line', 'coordinates' : '[0.1,1.0,2.1]'}, 'positionType': 'PT', 'primary': 'P'}
  
def getTestData(at):
    return {'addressedObject': {'addressPositions': [{'position': {'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::4167'}}, 'type': 'Point'}, 'positionType': 'Unknown', 'primary': True}], 'valuationReference': 'VR', 'externalObjectId': 'EOI', 'objectName': 'ON', 'certificateOfTitle': 'COT', 'externalObjectIdScheme': 'EOIS', 'objectType': 'Parcel'}, 'components': {'roadSuffix': 'RS', 'unitType': 'UT', 'addressType': 'Road', 'waterRoute': 'WR', 'levelType': 'LT', 'lifecycle': 'Current', 'addressNumberSuffix': 'ANS', 'addressNumberPrefix': 'ANP', 'roadName': 'RN', 'roadPrefix': 'RP', 'externalAddressIdScheme': 'EAIS', 'suburbLocality': 'SL', 'roadCentrelineId': 'RCI', 'waterName': 'WN', 'externalAddressId': 'EAI', 'roadType': 'RT', 'addressNumber': 'AN', 'levelValue': 'LV', 'townCity': 'TC', 'unitValue': 'UV'}, 'workflow': {'sourceUser': 'SU', 'sourceReason': 'SR'}}

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
