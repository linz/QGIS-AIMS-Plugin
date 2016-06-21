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
from AimsUtility import FeedType,FeatureType,UserActionType
from Const import SKIP_NULL, DEF_SEP
from User import User
from User import UserException
from AimsLogging import Logger
#from FeatureFactory import TemplateReader

#P = os.path.join(os.path.dirname(__file__),'../resources/')

ET = FeatureType.USERS

TP = {'users.admin': {u.lower():None for u in UserActionType.reverse.values()}}

aimslog = None

class UserTemplateReferenceException(UserException): pass    
class UserFieldRequiredException(UserException): pass
class UserFieldIncorrectException(UserException): pass
class UserConversionException(UserException): pass
class UserCreationException(UserException): pass

class UserFactory(FeatureFactory):
    ''' UserFactory class used to build user objects'''
     
    #PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    UFFT = FeedType.ADMIN
    DEF_FRT = FeedType.reverse[UFFT]
    usrtype = User
    reqtype = UserActionType
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, frt=DEF_FRT):        
        '''Initialise UserFactory object
        @param frt: FeedRef template reference used to select factory build
        @type frt: String
        '''
        if frt.k in TP.keys():
            self.frt = frt
        else: raise  UserTemplateReferenceException('{} is not a template key'.format(frt))
        self.template = self.readTemplate(TP)[self.frt.k]
    
    def __str__(self):
        return 'AFC.{}'.format(FeedType.reverse(self.UFFT)[:3])
    
    @staticmethod
    def getInstance(ft):
        '''Gets an instance of a factory to generate a particular (ft) type of user object
        @param ft: 
        '''
        return UserFactory(ft)
    
    #HACK to save rewriting getaddress at gfactory call
    def get(self,ref=None,usr=None,model=None,prefix=''):
        '''Creates a user object from a model (using the response template if model is not provided)
        @param ref: Application generated unique reference string
        @type ref: String
        @param usr: User object being populated
        @type usr: User
        @param model: Dictionary object (matching or derived from a template) containing address attribute information
        @param prefix: String value used to flatten/identify nested dictionary elements
        @type prefix: String   
        @return: (Minimally) Populated user object
        '''
        #overwrite = model OR NOT(address). If an address is provided only fill it with model provided, presume dont want template fill
        overwrite = False
        if not usr: 
            overwrite = True
            usr = self.usrtype(ref)
            
        if model:
            data = model
            overwrite = True
        else: data = self.template['response']
        
        if overwrite:
            try:
                #if SKIP_NULL: data = self._delNull(data)
                usr = self._read(usr, data, prefix)        
            except Exception as e:
                msg = 'Error creating address object using model {} with {}'.format(data,e)
                aimslog.error(msg)
                raise UserCreationException(msg)
        return usr
        
    def _read(self,usr,data,prefix):
        '''Recursive user setting attribute dict reader.
        @param usr: Active user object
        @type usr: User
        @param data: Active (subset) dict
        @param prefix: String value used to flatten/identify nested dictionary elements
        @type prefix: String   
        @return: Active (partially filled) user object
        '''
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            new_prefix = prefix+DEF_SEP+k
            if isinstance(data[k],dict): usr = self._read(usr=usr,data=data[k],prefix=new_prefix)
            #elif isinstance(data[k],list) and new_prefix == self.PBRANCH:
            #    pstns = [] 
            #    for pd in data[k]: pstns.append(Position.getInstance(pd,self))
            #    adr.setAddressPositions(pstns)
            else: getattr(usr,setter)(self.filterPI(data[k]) or None) if hasattr(usr,setter) else setattr(usr,new_prefix,self.filterPI(data[k]) or None)
        return usr
    
    def cast(self,usr):
        '''Casts user from current type to requested user-type, eg UserAdmin... <future enhancement?>
        @param usr: User being converted 
        @type usr: User
        @return: User cast to the self type
        '''
        #this is going to return the same thing since there is only one user type. *Left in as enhancement
        return User.clone(usr, self.get())
        
     
    def convert(self,usr,uat):
        '''Converts a user into its json payload equivalent
        @param usr: User objects being converted to JSON string
        @type usr: User
        @param uat: Action to perform on group
        @type uat: UserActionType
        @return: Representative JSON string (minimally compliant with type template) 
        '''
        full = None
        try:
            full = self._convert(usr, copy.deepcopy(self.template[self.reqtype.reverse[uat].lower()]))
            if SKIP_NULL: full = self._delNull(full)
        except Exception as e:
            msg = 'Error converting user object using AT{} with {}'.format(uat,e)
            aimslog.error(msg)
            raise UserConversionException(msg)
        return full
     
    def _convert(self,usr,dat,key=''):
        '''Recursive part of convert
        @param usr: Active user object
        @type usr: User
        @param dat: Active (subset) dict
        @param key: String value used to flatten/identify nested dictionary elements
        @type key: String   
        @return: Processed (nested) dict
        '''
        for attr in dat:
            new_key = key+DEF_SEP+attr
            #if new_key == self.PBRANCH:
            #    dat[attr] = usr.getConvertedAddressPositions()
            if isinstance(dat[attr],dict):
                dat[attr] = self._convert(usr, dat[attr],new_key)
            else:
                dat[attr] = self._assign(dat,usr,new_key)
        return dat
     
    def _assign(self,dat,usr,key):
        '''Validates group data value against template requirements reading tags to identify default and required data fields
        - `oneof` indicates field is required and is one of the values in the subsequent pipe separated list
        - `required` indicates the field is required. An error will be thrown if a suitable values is unavailable
        @param dat: Active (subset) dict
        @param usr: Active user object
        @type usr: User
        @param key: String value used to flatten/identify nested dictionary elements
        @type key: String   
        @return: Active (partially filled) address
        '''
        #TODO add default or remove from filterpi
        required,oneof,default,datatype = 4*(None,)
        val = usr.__dict__[key] if hasattr(usr,key) else None
        dft =  dat[key[key.rfind(DEF_SEP)+1:]]
        if dft and dft.startswith('#'):
            pi = dft.replace('#','').split(',')
            required = 'required' in pi
            oneof = [pv[6:].strip('()').split('|') for pv in pi if pv.startswith('oneof')]
            default = oneof[0][0] if required and oneof else None
        if required and not val:
            aimslog.error('AddressFieldRequired {}'.format(key))
            raise UserFieldRequiredException('Address field {} required'.format(key))
        if oneof and val and val not in oneof[0]:
            aimslog.error('AddressFieldIncorrect {}={}'.format(key,val))
            raise UserFieldIncorrectException('Address field {}={} not one of {}'.format(key,val,oneof[0]))
        return val if val else default


def test():
    from pprint import pprint as pp    
    from AimsUtility import FeedRef
    uf_f = UserFactory.getInstance(FeedRef(FeatureType.USERS,FeedType.ADMIN))
    
    uxx = uf_f.get()
    #uxx.setVersion(11112222)
    uxx.setUserId(22334455)
    uxx._version = 1
    uxx._userName = 'Scott Tiger'
    uxx._email = 'scott@oracle.com'
    uxx._requiresProgress = 'False'
    uxx._organisation = 'LINZ'
    uxx._role = 'follower'
    uc1 = uf_f.convert(uxx,UserActionType.ADD)
    uc2 = uf_f.convert(uxx,UserActionType.UPDATE)
    uc3 = uf_f.convert(uxx,UserActionType.DELETE)

    
    print 'ADD'
    pp(uc1)
    print 'UPD'
    pp(uc2)
    print 'DEL'
    pp(uc3)


            
if __name__ == '__main__':
    test()      