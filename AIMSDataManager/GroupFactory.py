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
from AimsUtility import FeatureType,GroupActionType,GroupApprovalType,FeedType,AimsException
from Const import SKIP_NULL, DEF_SEP
from Group import GroupChange,GroupResolution
from AimsLogging import Logger
#from FeatureFactory import TemplateReader

#P = os.path.join(os.path.dirname(__file__),'../resources/')

ET = FeatureType.GROUPS

#TP = {'{}.{}'.format(FeatureType.reverse[ET].lower(),FeedType.reverse[FeedType.CHANGEFEED].lower()):{b.lower():None for b in GroupActionType.reverse.values()}}

TP = {'{}.{}'.format(FeatureType.reverse[ET].lower(),a):b for a,b in zip(
        [FeedType.reverse[ft].lower() for ft in (FeedType.CHANGEFEED,FeedType.RESOLUTIONFEED)],
        [   {GroupActionType.reverse[at].lower():None for at in GroupActionType.reverse},
            {GroupApprovalType.reverse[at].lower():None for at in GroupApprovalType.reverse}
        ]
        )
    }
aimslog = None

class GroupException(AimsException): pass    
class GroupFieldRequiredException(GroupException): pass
class GroupFieldIncorrectException(GroupException): pass
class GroupConversionException(GroupException): pass
class GroupCreationException(GroupException): pass

class GroupFactory(FeatureFactory):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time an address is needed''' 
    #PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    GFFT = FeedType.CHANGEFEED
    DEF_REF = FeedType.reverse[GFFT]
    #grptype = Group
    #reqtype = GroupActionType
    
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
        return GroupFactory(ft)
    
    #HACK to save rewriting getaddress at gfactory call
    #def getAddress(self,ref=None,adr=None,model=None,prefix=''):self.getGroup(ref,adr,model,prefix)
    def getGroup(self,ref=None,grp=None,model=None,prefix=''):
        '''Creates an address object from a model (using the response template if model is not provided)'''
        #overwrite = model OR NOT(address). If an address is provided only fill it with model provided, presume dont want template fill
        overwrite = False
        if not grp: 
            overwrite = True
            grp = self.grptype(ref)
            
        if model:
            data = model
            overwrite = True
        else: data = self.template['response']
        
        if overwrite:
            try:
                #if SKIP_NULL: data = self._delNull(data)
                grp = self._readGroup(grp, data, prefix)        
            except Exception as e:
                msg = 'Error creating address object using model {} with {}'.format(data,e)
                aimslog.error(msg)
                raise GroupCreationException(msg)
        return grp
        
    def _readGroup(self,grp,data,prefix):
        '''Recursive address dict reader'''
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            new_prefix = prefix+DEF_SEP+k
            if isinstance(data[k],dict): grp = self._readGroup(grp=grp,data=data[k],prefix=new_prefix)
            #elif isinstance(data[k],list) and new_prefix == self.PBRANCH:
            #    pstns = [] 
            #    for pd in data[k]: pstns.append(Position.getInstance(pd,self))
            #    adr.setAddressPositions(pstns)
            else: getattr(grp,setter)(self.filterPI(data[k]) or None) if hasattr(grp,setter) else setattr(grp,new_prefix,self.filterPI(data[k]) or None)
        return grp
    
    def cast(self,grp):
        '''casts groups from curent to requested group-type'''
        return Group.clone(grp, self.getGroup())
    
#     @staticmethod
#     def filterPI(ppi):
#         '''filters out possible Processing Instructions'''
#         sppi = str(ppi)
#         if sppi.find('#')>-1:
#             dflt = re.search('default=(\w+)',sppi)
#             oneof = re.search('oneof=(\w+)',sppi)#first as default
#             return dflt.group(1) if dflt else (oneof.group(1) if oneof else None)
#         return ppi
        
     
    def convertGroup(self,grp,gat):
        '''Converts a group into its json payload equivalent '''
        full = None
        try:
            full = self._convert(grp, copy.deepcopy(self.template[self.reqtype.reverse[gat].lower()]))
            if SKIP_NULL: full = self._delNull(full)
        except Exception as e:
            msg = 'Error converting group object using AT{} with {}'.format(gat,e)
            aimslog.error(msg)
            raise GroupConversionException(msg)
        return full
     
    def _convert(self,grp,dat,key=''):
        for attr in dat:
            new_key = key+DEF_SEP+attr
            #if new_key == self.PBRANCH:
            #    dat[attr] = grp.getConvertedAddressPositions()
            if isinstance(dat[attr],dict):
                dat[attr] = self._convert(grp, dat[attr],new_key)
            else:
                dat[attr] = self._assign(dat,grp,new_key)
        return dat
     
    def _assign(self,dat,grp,key):
        '''validates address data value against template requirements'''
        #TODO add default or remove from filterpi
        required,oneof,default,datatype = 4*(None,)
        val = grp.__dict__[key] if hasattr(grp,key) else None
        dft =  dat[key[key.rfind(DEF_SEP)+1:]]
        if dft and dft.startswith('#'):
            pi = dft.replace('#','').split(',')
            required = 'required' in pi
            oneof = [pv[6:].strip('()').split('|') for pv in pi if pv.startswith('oneof')]
            default = oneof[0][0] if required and oneof else None
        if required and not val:
            aimslog.error('AddressFieldRequired {}'.format(key))
            raise GroupFieldRequiredException('Address field {} required'.format(key))
        if oneof and val and val not in oneof[0]:
            aimslog.error('AddressFieldIncorrect {}={}'.format(key,val))
            raise GroupFieldIncorrectException('Address field {}={} not one of {}'.format(key,val,oneof[0]))
        return val if val else default

class GroupChangeFactory(GroupFactory):
    GFFT = FeedType.CHANGEFEED
    DEF_REF = FeedType.reverse[GFFT]
    grptype = GroupChange
    reqtype = GroupActionType
    def __init__(self,ref):
        super(GroupChangeFactory,self).__init__(ref)


class GroupResolutionFactory(GroupFactory):
    GFFT = FeedType.RESOLUTIONFEED
    DEF_REF = FeedType.reverse[GFFT]
    grptype = GroupResolution
    reqtype = GroupApprovalType
    def __init__(self,ref):
        super(GroupResolutionFactory,self).__init__(ref)

    
    
    
def test():
    from pprint import pprint as pp
    gf_f = GroupFactory.getInstance(FeedType.CHANGEFEED)
    
    axx = gf_f.getGroup()
    axx.setVersion(11112222)
    axx.setChangeGroupId(22334455)
    ac1 = gf_f.convertGroup(axx,GroupActionType.REPLACE)
    ac2 = gf_f.convertGroup(axx,GroupActionType.SUBMIT)
    ac3 = gf_f.convertGroup(axx,GroupActionType.CLOSE)
    ac4 = gf_f.convertGroup(axx,GroupActionType.ADDRESS)
    axx.setAddressId(99887766)
    ac5 = gf_f.convertGroup(axx,GroupActionType.ADD)     
    ac6 = gf_f.convertGroup(axx,GroupActionType.REMOVE)

    
    print 'CHGF-REP'
    pp(ac1)
    print 'CHGF-SUB'
    pp(ac2)
    print 'CHGF-CLS'
    pp(ac3)
    
    print 'RESF-ADR'
    pp(ac4)
    print 'RESF-ADD'
    pp(ac5)
    print 'RESF-REM'
    pp(ac6)

            
if __name__ == '__main__':
    test()      