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
from FeatureFactory import FeatureFactory
from AimsUtility import FeatureType,GroupActionType,GroupApprovalType,FeedType
from Const import SKIP_NULL, DEF_SEP
from Group import Group,GroupChange,GroupResolution
from Group import GroupException
from AimsLogging import Logger
#from FeatureFactory import TemplateReader

#P = os.path.join(os.path.dirname(__file__),'../resources/')

ET = FeatureType.GROUPS

TP = {'{}.{}'.format(FeatureType.reverse[ET].lower(),a):b for a,b in zip(
        [FeedType.reverse[ftcr].lower() for ftcr in (FeedType.CHANGEFEED,FeedType.RESOLUTIONFEED)],
        [   {GroupActionType.reverse[gact].lower():None for gact in GroupActionType.reverse},
            {GroupApprovalType.reverse[gapt].lower():None for gapt in GroupApprovalType.reverse}
        ]
        )
    }
aimslog = None

class GroupTemplateReferenceException(GroupException): pass    
class GroupFieldRequiredException(GroupException): pass
class GroupFieldIncorrectException(GroupException): pass
class GroupConversionException(GroupException): pass
class GroupCreationException(GroupException): pass

class GroupFactory(FeatureFactory):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time an address is needed''' 
    #PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    GFFT = FeedType.CHANGEFEED
    DEF_FRT = FeedType.reverse[GFFT]
    grptype = Group
    #reqtype = GroupActionType
    
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self, frt=DEF_FRT):
        '''Initialises a group factory with static templates.
        @param frt: FeedRef template reference used to select factory build
        @type frt: String
        '''
        if frt.k in TP.keys():
            self.frt = frt
        else: raise  GroupTemplateReferenceException('{} is not a template key'.format(frt))
        self.template = self.readTemplate(TP)[self.frt.k]
    
    def __str__(self):
        return 'AFC.{}'.format(FeedType.reverse(self.GFFT)[:3])
    
    @staticmethod
    def getInstance(ift):
        '''Gets an instance of a factory to generate a particular (ft) type of address object'''
        return GroupFactory(ift)
    
    #HACK to save rewriting getaddress at gfactory call
    #def get(self,ref=None,adr=None,model=None,prefix=''):self.get(ref,adr,model,prefix)
    def get(self,ref=None,grp=None,model=None,prefix=''):
        '''Creates a group object from a model (using the response template if model is not provided)
        @param ref: Application generated unique reference string
        @type ref: String
        @param grp: Group object being populated
        @type grp: Group
        @param model: Dictionary object (matching or derived from a template) containing group attribute information
        @param prefix: String value used to flatten/identify nested dictionary elements
        @type prefix: String   
        @return: (Minimally) Populated group object
        '''
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
                grp = self._read(grp, data, prefix)        
            except Exception as e:
                msg = 'Error creating address object using model {} with {}'.format(data,e)
                aimslog.error(msg)
                raise GroupCreationException(msg)
        return grp
        
    def _read(self,grp,data,prefix):
        '''Recursive group setting attribute dict reader.
        @param grp: Active group object
        @type grp: Group
        @param data: Active (subset) dict
        @param prefix: String value used to flatten/identify nested dictionary elements
        @type prefix: String   
        @return: Active (partially filled) group
        '''
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            new_prefix = prefix+DEF_SEP+k
            if isinstance(data[k],dict): grp = self._read(grp=grp,data=data[k],prefix=new_prefix)
            #elif isinstance(data[k],list) and new_prefix == self.PBRANCH:
            #    pstns = [] 
            #    for pd in data[k]: pstns.append(Position.getInstance(pd,self))
            #    adr.setAddressPositions(pstns)
            else: getattr(grp,setter)(self.filterPI(data[k]) or None) if hasattr(grp,setter) else setattr(grp,new_prefix,self.filterPI(data[k]) or None)
        return grp
    
    def cast(self,grp):
        '''Casts group from current type to requested group-type, eg GroupResolution -> GroupChange
        @param grp: Group being converted 
        @type grp: Group
        @return: Group cast to the self type
        '''
        return Group.clone(grp, self.get())
        
     
    def convert(self,grp,gat):
        '''Converts a group into its json payload equivalent.
        @param grp: Group objects being converted to JSON string
        @type grp: Group
        @param gat: Action to perform on group
        @type gat: GroupAction|ApprovalType
        @return: Representative JSON string (minimally compliant with type template)
        '''
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
        '''Recursive part of convert
        @param grp: Active group object
        @type grp: Group
        @param dat: Active (subset) dict
        @param key: String value used to flatten/identify nested dictionary elements
        @type key: String   
        @return: Processed (nested) dict
        '''
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
        '''Validates group data value against template requirements reading tags to identify default and required data fields
        - `oneof` indicates field is required and is one of the values in the subsequent pipe separated list
        - `required` indicates the field is required. An error will be thrown if a suitable values is unavailable
        @param dat: Active (subset) dict
        @param grp: Active group object
        @type grp: Group
        @param key: String value used to flatten/identify nested dictionary elements
        @type key: String   
        @return: Active (partially filled) address
        '''
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
    '''Const setting GroupFactory subclass specifically for changefeed groups'''
    GFFT = FeedType.CHANGEFEED
    DEF_FRT = FeedType.reverse[GFFT]
    grptype = GroupChange
    reqtype = GroupActionType
    def __init__(self,frt):
        super(GroupChangeFactory,self).__init__(frt)


class GroupResolutionFactory(GroupFactory):
    '''Const setting GroupFactory subclass specifically for resolutionfeed groups'''
    GFFT = FeedType.RESOLUTIONFEED
    DEF_FRT = FeedType.reverse[GFFT]
    grptype = GroupResolution
    reqtype = GroupApprovalType
    def __init__(self,frt):
        super(GroupResolutionFactory,self).__init__(frt)

    
def test():
    from pprint import pprint as pp
    from AimsUtility import FeedRef
    gf_f = GroupFactory.getInstance(FeedRef(FeatureType.GROUPS,FeedType.CHANGEFEED))
    
    axx = gf_f.get()
    axx.setVersion(11112222)
    axx.setChangeGroupId(22334455)
    ac1 = gf_f.convert(axx,GroupActionType.REPLACE)
    ac2 = gf_f.convert(axx,GroupActionType.SUBMIT)
    ac3 = gf_f.convert(axx,GroupActionType.CLOSE)
    ac4 = gf_f.convert(axx,GroupActionType.ADDRESS)
    axx.setAddressId(99887766)
    ac5 = gf_f.convert(axx,GroupActionType.ADD)     
    ac6 = gf_f.convert(axx,GroupActionType.REMOVE)

    
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