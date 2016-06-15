#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################

#http://devassgeo01:8080/aims/api/address/features - properties
import re
import os
import sys
import copy
from FeatureFactory import FeatureFactory
from AimsUtility import FeatureType,ActionType,ApprovalType,FeedType,InvalidEnumerationType,FeedRef
from Const import SKIP_NULL, DEF_SEP
from Address import Address,AddressChange,AddressResolution,Position
from Address import AddressException
from AimsLogging import Logger
#from FeatureFactory import TemplateReader

#P = os.path.join(os.path.dirname(__file__),'../resources/')

ET = FeatureType.ADDRESS

TP = {'{}.{}'.format(FeatureType.reverse[ET].lower(),a):b for a,b in zip(
        [FeedType.reverse[ft].lower() for ft in FeedType.reverse],
        [   {},
            {ActionType.reverse[at].lower():None for at in ActionType.reverse},
            {ApprovalType.reverse[at].lower():None for at in ApprovalType.reverse}
        ]
        )
    }
#AT = {FeedType.FEATURES:Address,FeedType.CHANGEFEED:AddressChange,FeedType.RESOLUTIONFEED:AddressResolution}

aimslog = None
   
class AddressTemplateReferenceException(AddressException): pass  
class AddressFieldRequiredException(AddressException): pass
class AddressFieldIncorrectException(AddressException): pass
class AddressConversionException(AddressException): pass
class AddressCreationException(AddressException): pass

class AddressFactory(FeatureFactory):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time an address is needed''' 
    PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    AFFT = FeedType.FEATURES
    DEF_FRT = FeedType.reverse[AFFT]
    addrtype = Address
    reqtype = None
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, frt=DEF_FRT):
        '''Initialises an address factory with static templates.
        @param frt: FeedRef template reference used to select factory build
        @type frt: String
        '''     
        if frt.k in TP.keys():
            self.frt = frt
        else: raise  AddressTemplateReferenceException('{} is not a template key'.format(frt))
        self.template = self.readTemplate(TP)[self.frt.k]
    
    def __str__(self):
        return 'AFC.{}'.format(FeedType.reverse(self.AFFT)[:3])    

    def get(self,ref=None,adr=None,model=None,prefix=''):
        '''Creates an address object from a model (using the response template if model is not provided)
        @param ref: Application generated unique reference string
        @type ref: String
        @param adr: Address object being populated
        @type adr: Address
        @param model: Dictionary object (matching or derived from a template) containing address attribute information
        @param prefix: String value used to flatten/identify nested dictionary elements
        @type prefix: String   
        @return: (Minimally) Populated address object
        '''
        #overwrite = model OR NOT(address). If an address is provided only fill it with model provided, presume dont want template fill
        overwrite = False
        if not adr: 
            overwrite = True
            adr = self.addrtype(ref)
            
        if model:
            data = model
            overwrite = True
        else: data = self.template['response']
        
        if overwrite:
            try:
                #if SKIP_NULL: data = self._delNull(data) #breaks position on template, coords[0,0]->None
                adr = self._read(adr, data, prefix)        
            except Exception as e:
                msg = 'Error creating address object using model {} with message "{}"'.format(data,e)
                raise AddressCreationException(msg)
        return adr
        
    def _read(self,adr,data,prefix):
        '''Recursive address setting attribute dict reader.
        @param adr: Active address object
        @type adr: Address
        @param data: Active (subset) dict
        @param prefix: String value used to flatten/identify nested dictionary elements
        @type prefix: String   
        @return: Active (partially filled) address
        '''
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            new_prefix = prefix+DEF_SEP+k
            if isinstance(data[k],dict): adr = self._read(adr=adr,data=data[k],prefix=new_prefix)
            elif isinstance(data[k],list) and new_prefix == self.PBRANCH:
                pstns = [] 
                for pd in data[k]: pstns.append(Position.getInstance(pd,self))
                adr.setAddressPositions(pstns)
            else: getattr(adr,setter)(self.filterPI(data[k]) or None) if hasattr(adr,setter) else setattr(adr,new_prefix,self.filterPI(data[k]) or None)
        return adr
    
    def cast(self,adr):
        '''Casts address from current type to requested address-type, eg AddressFeature -> AddressChange
        @param adr: Address being converted 
        @type adr: Address
        @return: Address cast to the self type
        '''
        return Address.clone(adr, self.get())
        

class AddressFeedFactory(AddressFactory):
    '''Factory class to generate Address change/resolution (feed) objects'''
    def convert(self,adr,at):
        '''Converts an address into its json payload equivalent
        @param adr: Address objects being converted to JSON string
        @type adr: Address
        @param at: Action to perform on address
        @type at: Action|ApprovalType
        @return: Representative JSON string (minimally compliant with type template)
        '''
        full = None
        try:
            full = self._convert(adr, copy.deepcopy(self.template[self.reqtype.reverse[at].lower()]))
            if SKIP_NULL: full = self._delNull(full)
        except Exception as e:
            msg = 'Error converting address object using AT{} with {}'.format(at,e)
            raise AddressConversionException(msg)
        return full
    
    def _convert(self,adr,dat,key=''):        
        '''Recursive part of convert
        @param adr: Active address object
        @type adr: Address
        @param dat: Active (subset) dict
        @param key: String value used to flatten/identify nested dictionary elements
        @type key: String   
        @return: Processed (nested) dict
        '''
        for attr in dat:
            new_key = key+DEF_SEP+attr
            if new_key == self.PBRANCH:
                dat[attr] = adr.getConvertedAddressPositions()
            elif isinstance(dat[attr],dict):
                dat[attr] = self._convert(adr, dat[attr],new_key)
            else:
                dat[attr] = self._assign(dat,adr,new_key)
        return dat
    
    def _assign(self,dat,adr,key):
        '''Validates address data value against template requirements reading tags to identify default and required data fields
        - `oneof` indicates field is required and is one of the values in the subsequent pipe separated list
        - `required` indicates the field is required. An error will be thrown if a suitable values is unavailable
        @param dat: Active (subset) dict
        @param adr: Active address object
        @type adr: Address
        @param key: String value used to flatten/identify nested dictionary elements
        @type key: String   
        @return: Active (partially filled) address
        '''
        #TODO add default or remove from filterpi
        required,oneof,default,datatype = 4*(None,)
        val = adr.__dict__[key] if hasattr(adr,key) else None
        dft =  dat[key[key.rfind(DEF_SEP)+1:]]
        if dft and dft.startswith('#'):
            pi = dft.replace('#','').split(',')
            required = 'required' in pi
            oneof = [pv[6:].strip('()').split('|') for pv in pi if pv.startswith('oneof')]
            default = oneof[0][0] if required and oneof else None
        if required and not val:
            aimslog.error('AddressFieldRequired {}'.format(key))
            raise AddressFieldRequiredException('Address field {} required'.format(key))
        if oneof and val and val not in oneof[0]:
            aimslog.error('AddressFieldIncorrect {}={}'.format(key,val))
            raise AddressFieldIncorrectException('Address field {}={} not one of {}'.format(key,val,oneof[0]))
        return val if val else default         
        
class AddressChangeFactory(AddressFeedFactory):
    '''Const setting AddressFactory subclass specifically for changefeed addreses'''
    AFFT = FeedType.CHANGEFEED
    DEF_FRT = FeedType.reverse[AFFT]
    addrtype = AddressChange
    reqtype = ActionType
    def __init__(self,frt):
        super(AddressChangeFactory,self).__init__(frt)


class AddressResolutionFactory(AddressFeedFactory):
    '''Const setting AddressFactory subclass specifically for resolutionfeed addreses'''
    AFFT = FeedType.RESOLUTIONFEED
    DEF_FRT = FeedType.reverse[AFFT]
    addrtype = AddressResolution
    reqtype = ApprovalType
    def __init__(self,frt):
        super(AddressResolutionFactory,self).__init__(frt)
        
#     def get(self,frtNone,adr=None,model=None,prefix='',warnings=[]):
#         '''Sets a default address object and adds empty warning attribute'''
#         adrr = super(AddressResolutionFactory,self).get(ref,adr,model,prefix)
#         #adrr.setWarnings(warnings)
#         return adrr

    
def test():
    from pprint import pprint as pp
    af_f = FeatureFactory.getInstance(FeedRef(FeatureType.ADDRESS,FeedType.FEATURES))
    af_c = FeatureFactory.getInstance(FeedRef(FeatureType.ADDRESS,FeedType.CHANGEFEED))
    af_r = FeatureFactory.getInstance(FeedRef(FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
    
    
    axx = af_r.get()
    ac1 = af_f.get()
    #ac1._addressedObject_externalObjectId = 1000
    ac1._components_addressType = 'Road'
    ac1._components_addressNumber = 100
    ac1._components_roadName = 'The Terrace'
    ac1._version = 1
    ac1._components_addressId = 100
    ac1._workflow_sourceUser = 'e-Spatial'
    
    ac1a = af_c.convert(ac1,ActionType.ADD)
    ac1r = af_c.convert(ac1,ActionType.RETIRE)
    ac1u = af_c.convert(ac1,ActionType.UPDATE)
    
    #------------------------------------------------
    
    ar1 = af_c.get()
    ar1._version = 100
    ar1._changeId = 100
    ar1._components_addressType = 'Road'
    ar1._components_addressNumber = 100
    ar1._components_roadName = 'The Terrace'
    
    ar1a = af_r.convert(ar1,ApprovalType.ACCEPT)
    ar1d = af_r.convert(ar1,ApprovalType.DECLINE)
    ar1u = af_r.convert(ar1,ApprovalType.UPDATE)
    
    print 'CHGF-ADD'
    pp(ac1a)
    print 'CHGF-RET'
    pp(ac1r)
    print 'CHGF-UPD'
    pp(ac1u)
    
    print 'RESF-ACC'
    pp(ar1a)
    print 'RESF-DEC'
    pp(ar1d)
    print 'RESF-UPD'
    pp(ar1u)

            
if __name__ == '__main__':
    test()      