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
from AimsUtility import ActionType,ApprovalType,FeedType,InvalidEnumerationType
from Address import Address,AddressChange,AddressResolution

P = os.path.join(os.path.dirname(__file__),'../resources/')

TP = {FeedType.FEATURES:{},
      FeedType.CHANGEFEED:{ActionType.reverse[at]:None for at in ActionType.reverse},
      FeedType.RESOLUTIONFEED:{ApprovalType.reverse[at]:None for at in ApprovalType.reverse}}

#AT = {FeedType.FEATURES:Address,FeedType.CHANGEFEED:AddressChange,FeedType.RESOLUTIONFEED:AddressResolution}

DEF_SEP = '_'

    
class AddressFactory(object):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time''' 
    AFFT = FeedType.FEATURES
    addrtype = Address
    reqtype = None
    
    def __init__(self, ref=None): 
        self.template = TemplateReader().get()[self.AFFT]
    
    def __str__(self):
        return 'AFC.{}'.format(FeedType.reverse(self.AFFT)[:3])
    
    @staticmethod
    def getInstance(ft):
        if ft==FeedType.FEATURES: return AddressFactory(ft)
        elif ft==FeedType.CHANGEFEED: return AddressChangeFactory(ft)
        elif ft==FeedType.RESOLUTIONFEED: return AddressResolutionFactory(ft)
        else: raise InvalidEnumerationType('FeedType {} not available'.format(ft))
    
    
    def getAddress(self,adr=None,model=None,prefix=''):
        '''Creates an address object from a model using a template if not provided'''
        adr = adr if adr else self.addrtype('<default>')
        data = model if model else self.template['response']   
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            if isinstance(data[k],dict): adr = self.getAddress(adr,data[k],prefix+DEF_SEP+k)
            else: getattr(adr,setter)(data[k] or None) if hasattr(adr,setter) else setattr(adr,prefix+DEF_SEP+k,data[k] or None)
        return adr
        

class AddressFeedFactory(AddressFactory):    
    
    def convertAddress(self,adr,at):
        '''Converts an address into its json payload equivalent '''
        #print 'CA {} {}'.format(self.reqtype.reverse,at)
        data = self.template[self.reqtype.reverse[at]]
        '''Match object attributes to a predefined (Address) dict'''
        for attr in [a for a in adr.__dict__.keys()]:#dir(obj) if not a.startswith('__')]:
            atlist = attr.split(DEF_SEP)[1:]
            reduce(dict.__getitem__, atlist[:-1], data)[atlist[-1:][0]] = getattr(adr,attr)
        return data
        
class AddressChangeFactory(AddressFeedFactory):
    AFFT = FeedType.CHANGEFEED
    addrtype = AddressChange
    reqtype = ActionType
    def __init__(self,ref=None):
        super(AddressChangeFactory,self).__init__(ref)


class AddressResolutionFactory(AddressFeedFactory):
    AFFT = FeedType.RESOLUTIONFEED
    addrtype = AddressResolution
    reqtype = ApprovalType
    def __init__(self,ref=None):
        super(AddressResolutionFactory,self).__init__(ref)




class TemplateReader(object):
    tp = TP
    def __init__(self):
        for t1 in self.tp:
            t1t = FeedType.reverse[t1].lower()
            for t2 in self.tp[t1]:
                #t2t = ActionType.reverse[t2].lower()
                t2t = t2.lower()
                with open(os.path.join(P,'{}.{}.template'.format(t1t,t2t)),'r') as handle:
                    tstr = handle.read()
                    #print 'read template',t1t,t2t
                    self.tp[t1][t2] = eval(tstr) if tstr else ''
            #response address type is the template of the address-json we get from the api
            with open(os.path.join(P,'{}.response.template'.format(t1t)),'r') as handle:
                tstr = handle.read()
                self.tp[t1]['response'] = eval(tstr) if tstr else ''

    def get(self):
        return self.tp
    
    
def test():
    af = AddressFactory.getInstance(FeedType.FEATURES)
    ac = AddressFactory.getInstance(FeedType.CHANGEFEED)
    ar = AddressFactory.getInstance(FeedType.RESOLUTIONFEED)
    
    a1 = ac.getAddress()
    a1j = ac.convertAddress(a1,ActionType.ADD)
    
    a2 = ar.getAddress()
    a2j = ar.convertAddress(a2,ApprovalType.DECLINE)
    
    print a1j
    print a2j

            
if __name__ == '__main__':
    test()      