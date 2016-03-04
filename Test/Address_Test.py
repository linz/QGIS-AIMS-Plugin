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
import inspect
import sys
import re
import sys
import os

sys.path.append('../AIMSDataManager/')

from ..AIMSDataManager.Address import Address,AddressChange,AddressResolution
from AimsLogging import  Logger

testlog = Logger.setup('test')

#user to init an address, simple text string read from a stored config file
user_text = 'aims_user'

class Test_0_AddressSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertNotEqual(testlog,None,'Testlog not instantiated')
        testlog.debug('Address_Test Log')
        
    def test20_addressTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 Address instantiation test')
        address = Address(user_text)
        self.assertNotEqual(address,None,'Address not instantiated')
        
class Test_1_AddressTestSetters(unittest.TestCase):
    
    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        self._address = Address(user_text)
        self._address_setters = [i for i in dict(inspect.getmembers(Address, predicate=inspect.ismethod)) if i[:3]=='set']

        
    def tearDown(self):
        testlog.debug('Destroy null address')
        self._address = None
        self._address_setters = None
        
        
    def test10_instSetters(self):
        '''Tests that all the setters set a matching attribute i.e. setAttribute("X") -> self._Attribute = "X"'''
        #this no longer works since changing to full path attribute names eg _components_roadName
        return
        testlog.debug('Test_1.10 Instantiate all setters')
        for asttr in self._address_setters:
            aval = self._generateAttrVal(asttr)
            aname = self._generateAttrName(asttr)
            getattr(self._address, asttr)(aval)
            self.assertEqual(getattr(self._address, aname), aval, 'set* : Setter {} not setting correct attribute value {}'.format(asttr,aval))
            
    def test20_nullRemoval(self):
        '''Tests whether null values are removed from the object array'''
        #this function has moved to addressfactory
        return
        testlog.debug('Test_1.20 Instantiate sparse dict and test null removal')
        td1 = {'a': 111, 'b': None, 'c': 333, 'd': 'NULL', 'e': 555, 'f':{'fa': 'NULL','fb': 777}}
        td2 = {'a': 111, 'c': 333, 'e': 555, 'f': {'fb': 777}}
        td3 = self._address._delNull(td1)
        self.assertEqual(td3, td2, 'delNone : Dict null remover failure {}'.format(td3))

    #@unittest.skip("Test skipped awaiting finalisation of Address Class structure")
    def test30_checkPopulatedAddressDict(self):
        '''Tests whether JSON object gets created correctly'''
        #this function has moved to addressfactory
        return
        testlog.debug('Test_1.30 Attributes set to match JSON sample and compare')
        return True
        
        sample = {
            'workflow':{
                'sourceUser':'SU','sourceReason':'SR'},
            'components':{
                'addressType':'AT','externalAddressId':'EAI','externalAddressIdScheme':'EAIS',
                'lifecycle':'L','unitType':'UT','unitValue':'UV','levelType':'LT','levelValue':'LV',
                'addressNumberPrefix':'ANP','addressNumber':'AN',
                'addressNumberSuffix':'ANS','addressNumberHigh':'ANH',
                'roadCentrelineId':'RCLI','roadPrefix':'RP','roadName':'RN','roadType':'RTN','roadSuffix':'RS',
                'waterRoute':'WRN','waterName':'WN',
                'suburbLocality':'SL','townCity':'TC'},
            'addressedObject':{
                'objectType':'OT','objectName':'ON',
                'addressPosition':{
                    'type':'APT','coordinates':[1,1],
                    'crs':{'type':'CT','properties':{'name':'CP'}}},
            'externalObjectId':'EOI','externalObjectIdScheme':'EOIS',
            'valuationReference':'VR','certificateOfTitle':'COT','appellation':'A'
        }}
        
        for asm in self._address_setters:
            aval = self._generateAttrVal(asm)
            getattr(self._address, asm)(aval)
        jresult = self._address.objectify()
        self.assertEqual(jresult, sample, 'JSON Address constructed incorrectly {}'.format(jresult))
        
    def test31_checkAddressDictNullRemoval(self):
        '''check whether JSON output is truncated correctly on null inputs'''
        pass
    
    def test32_checkAddressDictErrorRaisedOnNull(self):
        '''Check error raised if attempt to create JSON output on null address array'''
        pass
        
#------------------------------------------------------------------------------    
    def _generateAttrVal(self,setmthd):
        setmthd = re.match('set_*(.*)',setmthd).group(1)
        return setmthd[:1].upper()+''.join([s for s in setmthd[1:] if ord(s)>64 and ord(s)<91])
    
    def _generateAttrName(self,setmthd):
        setmthd = re.match('set_*(.*)',setmthd).group(1)
        return '_'+setmthd[:1].lower()+setmthd[1:]


if __name__ == "__main__":
    unittest.main()
