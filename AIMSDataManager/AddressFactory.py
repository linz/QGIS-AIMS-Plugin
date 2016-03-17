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
import copy
from AimsUtility import EntityType,ActionType,ApprovalType,FeedType,InvalidEnumerationType
from AimsUtility import SKIP_NULL, DEF_SEP
from Address import Address,AddressChange,AddressResolution,Position
from AimsLogging import Logger

P = os.path.join(os.path.dirname(__file__),'../resources/')


ET = EntityType.ADDRESS

TP = {'{}.{}'.format(EntityType.reverse[ET].lower(),a):b for a,b in zip(
        [FeedType.reverse[ft].lower() for ft in FeedType.reverse],
        [   {},
            {ActionType.reverse[at].lower():None for at in ActionType.reverse},
            {ApprovalType.reverse[at].lower():None for at in ApprovalType.reverse}
        ]
        )
    }
#AT = {FeedType.FEATURES:Address,FeedType.CHANGEFEED:AddressChange,FeedType.RESOLUTIONFEED:AddressResolution}

aimslog = None
 
class AddressException(Exception): pass    
class AddressFieldRequiredException(AddressException): pass
class AddressFieldIncorrectException(AddressException): pass
class AddressConversionException(AddressException): pass
class AddressCreationException(AddressException): pass

class AddressFactory(object):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time an address is needed''' 
    PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    AFFT = FeedType.FEATURES
    DEF_REF = FeedType.reverse[AFFT]
    addrtype = Address
    reqtype = None
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=DEF_REF):
        self.ref = ref
        key = '{}.{}'.format(EntityType.reverse[ET].lower(),FeedType.reverse[ref].lower())
        self.template = TemplateReader().get()[key]
    
    def __str__(self):
        return 'AFC.{}'.format(FeedType.reverse(self.AFFT)[:3])
    
    @staticmethod
    def getInstance(ft):
        '''Gets an instance of a factory to generate a particular (ft) type of address object'''
        if ft==FeedType.FEATURES: return AddressFactory(ft)
        elif ft==FeedType.CHANGEFEED: return AddressChangeFactory(ft)
        elif ft==FeedType.RESOLUTIONFEED: return AddressResolutionFactory(ft)
        else: raise InvalidEnumerationType('FeedType {} not available'.format(ft))
    

    def getAddress(self,ref=None,adr=None,model=None,prefix=''):
        '''Creates an address object from a model (using the response template if model is not provided)'''
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
                adr = self._readAddress(adr, data, prefix)        
            except Exception as e:
                msg = 'Error creating address object using model {} with {}'.format(data,e)
                aimslog.error(msg)
                raise AddressCreationException(msg)
        return adr
        
    def _readAddress(self,adr,data,prefix):
        '''Recursive address dict reader'''
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            new_prefix = prefix+DEF_SEP+k
            if isinstance(data[k],dict): adr = self._readAddress(adr=adr,data=data[k],prefix=new_prefix)
            elif isinstance(data[k],list) and new_prefix == self.PBRANCH:
                pstns = [] 
                for pd in data[k]: pstns.append(Position.getInstance(pd,self))
                adr.setAddressPositions(pstns)
            else: getattr(adr,setter)(self.filterPI(data[k]) or None) if hasattr(adr,setter) else setattr(adr,new_prefix,self.filterPI(data[k]) or None)
        return adr
    
    def cast(self,adr):
        '''casts address from curent to requested address-type'''
        return Address.clone(adr, self.getAddress())
    
    @staticmethod
    def filterPI(ppi):
        '''filters out possible Processing Instructions'''
        sppi = str(ppi)
        if sppi.find('#')>-1:
            dflt = re.search('default=(\w+)',sppi)
            oneof = re.search('oneof=(\w+)',sppi)#first as default
            return dflt.group(1) if dflt else (oneof.group(1) if oneof else None)
        return ppi
        

class AddressFeedFactory(AddressFactory):
    
    def convertAddress(self,adr,at):
        '''Converts an address into its json payload equivalent '''
        full = None
        try:
            full = self._convert(adr, copy.deepcopy(self.template[self.reqtype.reverse[at].lower()]))
            full = self._delNull(full) if SKIP_NULL else full
        except Exception as e:
            msg = 'Error converting address object using AT{} with {}'.format(at,e)
            aimslog.error(msg)
            raise AddressConversionException(msg)
        return full
    
    def _convert(self,adr,dat,key=''):
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
        '''validates address data value against template requirements'''
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
    
    def _delNull(self, obj):
        if hasattr(obj, 'items'):
            new_obj = type(obj)()
            for k in obj:
                #if k != 'NULL' and obj[k] != 'NULL' and obj[k] != None:
                if k and obj[k]:
                    res = self._delNull(obj[k])
                    if res: new_obj[k] = res
        elif hasattr(obj, '__iter__'):
            new_obj = [] 
            for it in obj:
                #if it != 'NULL' and it != None:
                if it: new_obj.append(self._delNull(it))
        else: return obj
        return type(obj)(new_obj)

            
        
        
class AddressChangeFactory(AddressFeedFactory):
    AFFT = FeedType.CHANGEFEED
    DEF_REF = FeedType.reverse[AFFT]
    addrtype = AddressChange
    reqtype = ActionType
    def __init__(self,ref=DEF_REF):
        super(AddressChangeFactory,self).__init__(ref)


class AddressResolutionFactory(AddressFeedFactory):
    AFFT = FeedType.RESOLUTIONFEED
    DEF_REF = FeedType.reverse[AFFT]
    addrtype = AddressResolution
    reqtype = ApprovalType
    def __init__(self,ref=DEF_REF):
        super(AddressResolutionFactory,self).__init__(ref)
        
    def getAddress(self,ref=None,adr=None,model=None,prefix='',warnings=[]):
        '''Sets a refault address object and adds empty warning attribute'''
        adrr = super(AddressResolutionFactory,self).getAddress(ref,adr,model,prefix)
        #adrr.setWarnings(warnings)
        return adrr


class TemplateReader(object):
    tp = TP
    def __init__(self):
        for t1 in self.tp:
            for t2 in self.tp[t1]:
                with open(os.path.join(P,'{}.{}.template'.format(t1,t2)),'r') as handle:
                    tstr = handle.read()
                    #print 'read template',t1t,t2t
                    self.tp[t1][t2] = eval(tstr) if tstr else ''
            #response address type is the template of the address-json we get from the api
            with open(os.path.join(P,'{}.response.template'.format(t1)),'r') as handle:
                tstr = handle.read()
                self.tp[t1]['response'] = eval(tstr) if tstr else ''

    def get(self):
        return self.tp
    
    
def test():
    from pprint import pprint as pp
    af_f = AddressFactory.getInstance(FeedType.FEATURES)
    af_c = AddressFactory.getInstance(FeedType.CHANGEFEED)
    af_r = AddressFactory.getInstance(FeedType.RESOLUTIONFEED)
    
    
    axx = af_r.getAddress()
    ac1 = af_f.getAddress()
    #ac1._addressedObject_externalObjectId = 1000
    ac1._components_addressType = 'Road'
    ac1._components_addressNumber = 100
    ac1._components_roadName = 'The Terrace'
    ac1._version = 1
    ac1._components_addressId = 100
    
    ac1a = af_c.convertAddress(ac1,ActionType.ADD)
    ac1r = af_c.convertAddress(ac1,ActionType.RETIRE)
    ac1u = af_c.convertAddress(ac1,ActionType.UPDATE)
    
    #------------------------------------------------
    
    ar1 = af_c.getAddress()
    ar1._version = 100
    ar1._changeId = 100
    ar1._components_addressType = 'Road'
    ar1._components_addressNumber = 100
    ar1._components_roadName = 'The Terrace'
    
    ar1a = af_r.convertAddress(ar1,ApprovalType.ACCEPT)
    ar1d = af_r.convertAddress(ar1,ApprovalType.DECLINE)
    ar1u = af_r.convertAddress(ar1,ApprovalType.UPDATE)
    
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