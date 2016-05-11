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
from AimsUtility import FeedType,FeatureType,UserActionType,AimsException
from Const import SKIP_NULL, DEF_SEP
from User import User
from AimsLogging import Logger
#from FeatureFactory import TemplateReader

#P = os.path.join(os.path.dirname(__file__),'../resources/')

ET = FeatureType.USERS

TP = {'users.admin': {u.lower():None for u in UserActionType.reverse.values()}}

aimslog = None

class UserException(AimsException): pass    
class UserFieldRequiredException(UserException): pass
class UserFieldIncorrectException(UserException): pass
class UserConversionException(UserException): pass
class UserCreationException(UserException): pass

class UserFactory(FeatureFactory):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time an address is needed''' 
    #PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    UFFT = FeedType.ADMIN
    DEF_REF = FeedType.reverse[UFFT]
    usrtype = User
    reqtype = UserActionType
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, ref=DEF_REF):
        self.ref = ref
        self.template = self.readTemplate(TP)[ref.k]
    
    def __str__(self):
        return 'AFC.{}'.format(FeedType.reverse(self.GFFT)[:3])
    
    @staticmethod
    def getInstance(ft):
        '''Gets an instance of a factory to generate a particular (ft) type of address object'''
        return UserFactory(ft)
    
    #HACK to save rewriting getaddress at gfactory call
    #def getAddress(self,ref=None,adr=None,model=None,prefix=''):self.getUser(ref,adr,model,prefix)
    def getUser(self,ref=None,usr=None,model=None,prefix=''):
        '''Creates an address object from a model (using the response template if model is not provided)'''
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
                usr = self._readUser(usr, data, prefix)        
            except Exception as e:
                msg = 'Error creating address object using model {} with {}'.format(data,e)
                aimslog.error(msg)
                raise UserCreationException(msg)
        return usr
        
    def _readUser(self,usr,data,prefix):
        '''Recursive address dict reader'''
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            new_prefix = prefix+DEF_SEP+k
            if isinstance(data[k],dict): usr = self._readUser(usr=usr,data=data[k],prefix=new_prefix)
            #elif isinstance(data[k],list) and new_prefix == self.PBRANCH:
            #    pstns = [] 
            #    for pd in data[k]: pstns.append(Position.getInstance(pd,self))
            #    adr.setAddressPositions(pstns)
            else: getattr(usr,setter)(self.filterPI(data[k]) or None) if hasattr(usr,setter) else setattr(usr,new_prefix,self.filterPI(data[k]) or None)
        return usr
    
    def cast(self,usr):
        '''casts Users from curent to requested User-type'''
        return User.clone(usr, self.getUser())
    
#     @staticmethod
#     def filterPI(ppi):
#         '''filters out possible Processing Instructions'''
#         sppi = str(ppi)
#         if sppi.find('#')>-1:
#             dflt = re.search('default=(\w+)',sppi)
#             oneof = re.search('oneof=(\w+)',sppi)#first as default
#             return dflt.user(1) if dflt else (oneof.group(1) if oneof else None)
#         return ppi
        
     
    def convertUser(self,usr,uat):
        '''Converts a user into its json payload equivalent '''
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
        '''validates address data value against template requirements'''
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
    
    uxx = uf_f.getUser()
    #uxx.setVersion(11112222)
    uxx.setUserId(22334455)
    uxx._version = 1
    uxx._userName = 'Scott Tiger'
    uxx._email = 'scott@oracle.com'
    uxx._requiresProgress = 'False'
    uxx._organisation = 'LINZ'
    uxx._role = 'follower'
    uc1 = uf_f.convertUser(uxx,UserActionType.ADD)
    uc2 = uf_f.convertUser(uxx,UserActionType.UPDATE)
    uc3 = uf_f.convertUser(uxx,UserActionType.DELETE)

    
    print 'ADD'
    pp(uc1)
    print 'UPD'
    pp(uc2)
    print 'DEL'
    pp(uc3)


            
if __name__ == '__main__':
    test()      