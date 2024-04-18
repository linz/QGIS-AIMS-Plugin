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

ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
 
from AIMSDataManager.Address import Address,AddressChange,AddressResolution,Position
from AIMSDataManager.AddressFactory import AddressChangeFactory,AddressResolutionFactory
from AIMSDataManager.AimsUtility import ActionType, FEEDS
from AIMSDataManager.Feature import Feature, FeatureMetaData
from AIMSDataManager.AimsLogging import  Logger

testlog = Logger.setup('test')

#user to init an address, simple text string read from a stored config file
user_text = 'aims_user'

def super_sort(obj):
    '''Function for rebuilding a dictionary with sorting applied by dictionary key and list objects'''
    if isinstance(obj, dict):
        obj = dict(sorted(obj.items()))
        for key, value in obj.items():
            obj[key] = super_sort(value)
    if isinstance(obj, list):
        obj = sorted(obj)
    return obj

class Test_0_AddressSelfTest(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test10_selfTest(self):
        #assertIsNotNone added in 3.1
        self.assertIsNotNone(testlog,'Testlog not instantiated')
        testlog.debug('Address_Test Log')
        
    def test20_addressTest(self):
        #assertIsNotNone added in 3.1        
        testlog.debug('Test_0.20 Address instantiation test')
        address = Address(user_text)
        self.assertIsNotNone(address,'Address not instantiated')
        
class Test_1_AddressTestSetters(unittest.TestCase):
    
    def setUp(self): 
        testlog.debug('Instantiate null address, address.setter list')
        self._address = Address(user_text)
        self._address_setters = [i for i in dict(inspect.getmembers(self._address, predicate=inspect.ismethod)) if i[:3]=='set']
        # self._address_setters.remove('setAddressPositions')

        
    def tearDown(self):
        testlog.debug('Destroy null address')
        self._address = None
        self._address_setters = None
        
        
    def test10_instSetters(self):
        '''Tests that all the setters set a matching attribute i.e. setAttribute("X") -> self._Attribute = "X"'''
        #this no longer works since changing to full path attribute names eg _components_roadName
        testlog.debug('Test_1.10 Instantiate all setters')
        for asttr in self._address_setters:
            if asttr in ('setAddressPositions', 'setMeta', 'setPublishDate'): continue     # Skip this in the instantiate setters
            aval = self._generateAttrVal(asttr)             # Generate mock value
            getattr(self._address, asttr)(aval)             # Get setter function and set the mock value
            aname = self._generateAttrName(asttr)           # Get the generated attribute name
            try:
                if 'meta.' in aname:
                    self.assertEqual(getattr(self._address.meta, aname.lstrip('meta.')), aval, 'set* : Setter {} not setting correct attribute value {}'.format(asttr,aval))
                else:
                    self.assertEqual(getattr(self._address, aname), aval, 'set* : Setter {} not setting correct attribute value {}'.format(asttr,aval))
            except Exception as e:
                print(e)
        return
            

    #@unittest.skip("Test skipped awaiting finalisation of Address Class structure")
    def test30_checkPopulatedAddressChangeDict(self):
        '''Tests whether JSON object gets created correctly'''
        #this function has moved to addressfactory
        testlog.debug('Test_1.30 Attributes set to match JSON sample and compare')
        #return True

        for asm in self._address_setters:
            if asm == 'setAddressPositions':
                getattr(self._address, asm)([Position(),])
                continue
            aval = self._generateAttrVal(asm)
            getattr(self._address, asm)(aval)

        self._address.setVersion(100)
        self._address.setAddressType('Road')
        self._address.setAddObjectType('Parcel')

        for at in (ActionType.ADD,ActionType.RETIRE,ActionType.UPDATE):
            acf = AddressChangeFactory(FEEDS['AC'])
            jresult = acf.convert(self._address,at)
            tresult = getTestData(at)
            self.assertEqual(jresult, tresult, 'JSON Address constructed incorrectly {}'.format(jresult))
        
    def test31_checkAddressDictNullRemoval(self):
        '''check whether JSON output is truncated correctly on null inputs'''
        pass
    
    def test32_checkAddressDictErrorRaisedOnNull(self):
        '''Check error raised if attempt to create JSON output on null address array'''
        pass
        
#------------------------------------------------------------------------------    
    def _generateAttrVal(self,setmthd):
        s = self._special(setmthd)
        if s: return s
        setmthd = re.match('set_*(.*)',setmthd).group(1)
        return setmthd[:1].upper()+''.join([s for s in setmthd[1:] if ord(s)>64 and ord(s)<91])
    
    def _generateAttrName(self,setmthd,check_meta=True):
        # set object and optionally include metadata
        objs = [self._address]
        meta = 'meta'
        if check_meta and hasattr(self._address, meta): objs.append(self._address.meta)
        # Full attribute names
        fpns = ['', '_codes', '_components', '_addressedObject', '_workflow']

        setmthd = re.match('set_*(.*)',setmthd).group(1)
        # Hack to deal with attributes that don't conform to the schema
        if 'Add' in setmthd and 'Address' not in setmthd: setmthd = setmthd.lstrip('Add')
        # Format to attribute schema
        aname = '_'+setmthd[:1].lower()+setmthd[1:]

        for obj in objs:
            for fpn in fpns:
                fname = f'{fpn}{aname}'
                if hasattr(obj, fname): 
                    if isinstance(obj, FeatureMetaData):
                        return f'{meta}.{fname}'
                    return fname
                
        if meta in aname:
            return meta
            
        return None
    
    def _special(self,meth):
        if meth == 'setObjectType':return 'Parcel'
        if meth == 'setAddressType':return 'Road' 
        if meth == 'setLifecycle':return 'Current'
        if meth == 'setRequestId':return 99 # Both of these are limited to integers on their setters
        if meth == 'setVersion':return 99   # Both of these are limited to integers on their setters
        return

    
def getTestData(at):
    test_data = {
        0 :  { # ADD
            'addressedObject' : {
                'addressPositions' : [{
                        'position' : {
                            'crs' : {
                                'type' : 'name',
                                'properties' : {
                                    'name' : 'urn:ogc:def:crs:EPSG::4167'
                                }
                            },
                            'type' : 'Point'
                        },
                        'positionType' : 'Unknown',
                        'primary' : True
                    }
                ],
                'valuationReference' : 'VR',
                'externalObjectId' : 'EOI',
                'objectName' : 'AON',
                'certificateOfTitle' : 'COT',
                'externalObjectIdScheme' : 'EOIS',
                'objectType' : 'Parcel',
                'appellation' : 'A'
            },
            'components' : {
                'roadSuffix' : 'RS',
                'unitType' : 'UT',
                'addressType' : 'Road',
                'waterRoute' : 'WR',
                'levelType' : 'LT',
                'lifecycle' : 'Current',
                'addressNumberHigh' : 'ANH',
                'addressNumberSuffix' : 'ANS',
                'addressNumberPrefix' : 'ANP',
                'roadName' : 'RN',
                'roadPrefix' : 'RP',
                'externalAddressIdScheme' : 'EAIS',
                'suburbLocality' : 'SL',
                'roadCentrelineId' : 'RCI',
                'waterName' : 'WN',
                'externalAddressId' : 'EAI',
                'roadType' : 'RT',
                'addressNumber' : 'AN',
                'levelValue' : 'LV',
                'townCity' : 'TC',
                'unitValue' : 'UV'
            },
            'workflow' : {
                'sourceUser' : 'SU',
                'sourceReason' : 'SR'
            },
            'codes' : {
                'meshblock' : 'M'
            }
        },
        1 : { # RETIRE
            'version' : 100,
            'workflow' : {
                'sourceUser' : 'SU',
                'sourceReason' : 'SR'
            },
            'components' : {
                'addressId' : 'AI'
            }
        },
        2: { # UPDATE
            'addressedObject': {
                'addressPositions': [
                    {
                        'position': {
                            'crs': {
                                'properties': {
                                    'name': 'urn:ogc:def:crs:EPSG::4167'
                                },
                                'type': 'name'
                            },
                            'type': 'Point'
                        },
                        'positionType': 'Unknown',
                        'primary': True
                    }
                ],
                'appellation': 'A',
                'certificateOfTitle': 'COT',
                'externalObjectId': 'EOI',
                'externalObjectIdScheme': 'EOIS',
                'objectName': 'AON',
                'objectType': 'Parcel',
                'valuationReference': 'VR'
            },
            'codes': {
                'meshblock': 'M'
            },
            'components': {
                'addressId': 'AI',
                'addressNumber': 'AN',
                'addressNumberHigh': 'ANH',
                'addressNumberPrefix': 'ANP',
                'addressNumberSuffix': 'ANS',
                'addressType': 'Road',
                'externalAddressId': 'EAI',
                'externalAddressIdScheme': 'EAIS',
                'levelType': 'LT',
                'levelValue': 'LV',
                'lifecycle': 'Current',
                'roadCentrelineId': 'RCI',
                'roadName': 'RN',
                'roadPrefix': 'RP',
                'roadSuffix': 'RS',
                'roadType': 'RT',
                'suburbLocality': 'SL',
                'townCity': 'TC',
                'unitType': 'UT',
                'unitValue': 'UV',
                'waterName': 'WN',
                'waterRoute': 'WR'
            },
            'version': 100,
            'workflow': {
                'sourceReason': 'SR',
                'sourceUser': 'SU'
            }
        }
    }
    return test_data[at]


if __name__ == "__main__":
    unittest.main()




