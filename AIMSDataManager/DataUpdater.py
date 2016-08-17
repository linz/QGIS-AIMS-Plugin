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

from datetime import datetime as DT
#from functools import wraps

import os
import sys
import re
import logging

import threading
from AimsApi import AimsApi 
from AimsUtility import FeedRef,ActionType,ApprovalType,GroupActionType,GroupApprovalType,UserActionType,FeatureType,FeedType,SupplementalHack
from AimsUtility import AimsException
from Const import ENABLE_ENTITY_EVALUATION, MERGE_RESPONSE,MAX_FEATURE_COUNT
from Address import Entity, EntityValidation, EntityAddress
from AimsLogging import Logger
from FeatureFactory import FeatureFactory
from Observable import Observable

aimslog = None

class DataUpdaterSelectionException(AimsException):pass

class DataUpdater(Observable):
    '''Mantenence thread comtrolling data updates and api interaction.
    Instantiates an amisapi instance with wrappers for initialisation of local data store 
    and change/resolution feed updating
    '''
    #et = FeatureType.ADDRESS
    #ft = FeedType.FEATURES
    address = None
    pno = 0
    changeId = 0
    
    global aimslog
    aimslog = Logger.setup()
    
    getfeat = None
    
    def __init__(self,params,queue):
        '''DataUpdater base initialiser.
        @param params: List of configuration parameters
        @type params: List<?>
        @param queue: Response queue
        @type queues: Queue.Queue
        '''
        super(DataUpdater,self).__init__()
        self.ref,self.conf,self.factory = params
        self.queue = queue
        #self._stop = threading.Event()
        self.api = AimsApi(self.conf)    
        
    def setup(self,etft,sw,ne,pno):
        '''Parameter setup.
        @param etft: Feed/Feature identifier
        @type etft: FeedRef
        @param sw: South-West corner, coordinate value pair
        @type sw: List<Double>{2}
        @param ne: North-East corner, coordinate value pair
        @type ne: List<Double>{2}
        @param pno: Feed page number
        @type pno: Integer 
        '''
        self.etft = etft
        self.sw,self.ne = sw,ne
        self.pno = pno

    def run(self):
        '''Main updater run method fetching single page of addresses from API'''
        aimslog.info('GET.{} {} - Page{}'.format(self.ref,self.etft,self.pno))
        featlist = []
        #for page in self.api.getOnePage(self.etft,self.sw,self.ne,self.pno):
        #    featlist.append(self.processPage(page,self.etft))
        ce,pages = self.api.getOnePage(self.etft,self.sw,self.ne,self.pno)  
        if any(ce.values()): aimslog.error('Single-page request failure {}'.format(ce))       
        if pages.has_key('entities'): 
            for page in pages['entities']:
                featlist.append(self.processPage(page,self.etft))     
        else:
            aimslog.error('Single-page response missing entities')
        self.queue.put(featlist)
        self.notify(self.ref)
        
    def processPage(self,page,etft):
        '''Process an individual page. If page is resolution type optionally re-query at individual level        
        @param page: Processed results from pno request
        @type page: Dict<?>
        @param etft: Feed/Feature identifier
        @type etft: FeedRef
        '''
        if etft.ft == FeedType.RESOLUTIONFEED and ENABLE_ENTITY_EVALUATION:
            cid = self.cid(page)
            ce,feat = self.api.getOneFeature(etft,cid)
            if any(ce.values()): aimslog.error('Single-feature request failure {}'.format(ce))
            if feat == {u'class': [u'error']}: 
                #if the pno request returns the not-supposed-to-happen error, it gets special treatment
                aimslog.error('Invalid API response {}'.format(feat))
                #return self.factory.get(model=pno['properties'])
            else:
                return self._processEntity(feat,cid,etft)
        else:
            #just return the main feedlevel address objects
            return self.factory.get(model=page['properties'])
    
    def _processEntity(self,feat,cid,etft):
        '''Identify and select group, address or entity processing for a reolutionfeed feature        
        @param feat: dict representation of feature before object processing
        @type feat: Dict
        @param cid: Change ID or group change ID
        @type cid: Integer
        @param etft: Feed/Feature identifier
        @type etft: FeedRef
        @return: Instantiated feature object
        '''
        if feat['class'][0] == 'validation':
            return self._processValidationEntity(feat)
            #e = EntityValidation.getInstance(feat)# self.getEntityInstance()
        #-------------------------------
        # Resolution Group
        elif feat['class'][0] == 'resolutiongroup':
            return self._processResolutionGroup(feat,cid,etft)
        # Address List
        elif feat['class'][0] == 'addressresolution':
            return self._processAddressResolution(feat)
        #--------------------------------
        # Simple Entity object
        else:
            return self._processSimpleEntity(self.factory.get,feat)
        
    def _processValidationEntity(self,feat):
        '''Wraps call to validation entity instantiator
        @param feat: dict representation of feature before object processing
        @type feat: Dict
        @return: Instantiated validation Entity
        '''
        return EntityValidation.getInstance(feat)
    
    def _processAddressEntity(self,feat):        
        '''Processes feature data into address object
        @param feat: dict representation of feature before object processing
        @type feat: Dict
        @return: Instantiated Address entity
        '''
        #return EntityAddress.getInstance(feat)
        return self._processSimpleEntity(FeatureFactory.getInstance(FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))).get,feat)
        
    def _processSimpleEntity(self,fact,feat):                
        '''Default processor for generic entities but the same as address resolution processor (below).
        @param fact: Link to factory, object instantiation method
        @type fact: <Function>
        @param feat: dict representation of feature before object processing
        @type feat: Dict
        @return: Instantiated Address entity
        '''
        featurelist = []
        a = fact(model=feat['properties'])
        if feat.has_key('entities'):
            for e in feat['entities']:
                featurelist.append(self._populateEntity(e))
            a._setEntities(featurelist)
        return a
    
    def _processAddressResolution(self,feat):                
        '''Processes entries in the addressresolution entities list
        @param feat: dict representation of feature before object processing
        @type feat: Dict
        @return: Instantiated Address entity
        '''
        featurelist = []
        a = self.factory.get(model=feat['properties'])
        for e in feat['entities']:
            featurelist.append(self._populateEntity(e))
        a._setEntities(featurelist)
        return a
        
    def _processResolutionGroup(self,feat,cid,etft):
        '''Processes the res-address objects in a res-group. Subsequently populates the sub entities as feature-addresses.
        @param feat: dict representation of feature before object processing
        @type feat: Dict
        @param cid: Change ID or group change ID
        @type cid: Integer
        @param etft: Feed/Feature identifier
        @type etft: FeedRef
        @return: Instantiated feature object
        '''
        featurelist = []
        g = self.factory.get(model=feat['properties'])#group
        #HACK subst cid for cid+count string
        ce,feat2 = self.api.getOneFeature(etft,'{}/address?count={}'.format(cid,MAX_FEATURE_COUNT))#group entity/adr list
        if any(ce.values()): aimslog.error('Single-feature request failure {}'.format(ce))
        etft2 = FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))
        factory2 = FeatureFactory.getInstance(etft2)
        for f in feat2['entities']:
            a = factory2.get(model=f['properties'])
            elist2 = []
            for e in f['entities']:
                elist2.append(self._populateEntity(e))
            a._setEntities(elist2)
            featurelist.append(a)
        g._setEntities(featurelist)
        return g
        
    def _populateEntity(self,ent):
        '''Selects type and instantiates appropriate entity object.
        @param ent: dict representation of feature before object processing
        @type ent: Dict
        '''
        if ent['class'][0] == 'validation':
            return self._processValidationEntity(ent)
        elif ent['class'][0] == 'address':
            ###res factory might work here instead
            #etft3 = FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))
            #factory3 = FeatureFactory.getInstance(etft3)
            #return factory3.get(model=e['properties'])
            return self._processAddressEntity(ent)
        
        else:
            return Entity.getInstance(ent)
        
    @staticmethod
    def getInstance(etft):
        '''Based on the provided FeedRef this getInstance returns a group,address or user updater object 
        @param etft: Feed/Feature identifier
        @type etft: FeedRef
        '''
        if etft.et == FeatureType.GROUPS: return DataUpdaterGroup
        elif etft.et == FeatureType.ADDRESS: return DataUpdaterAddress
        elif etft.et == FeatureType.USERS: return DataUpdaterUser
        else: raise DataUpdaterSelectionException('Select Address,Groups or Users')
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def close(self):
        aimslog.info('Queue {} stopped'.format(self.queue.qsize()))
        self.queue.task_done()
        
    #executed by subclass
    def cid(self,_): pass
        
#---------------------------------------------------------------
    
#simple subclasses to assign getaddress/getgroup function    
class DataUpdaterAddress(DataUpdater):
    '''Dataupdater subclass for Address objects'''
    def __init__(self,params,queue):
        '''Initialises Address DataUpdater
        @param params: List of configuration parameters
        @type params: List<?>
        @param queue: Response queue
        @type queues: Queue.Queue
        '''
        super(DataUpdaterAddress,self).__init__(params,queue)
        
    def cid(self,f):
        return f['properties']['changeId']
    
#     def getEntityInstance(self,ref):
#         return EntityValidation(ref)
        
        
class DataUpdaterGroup(DataUpdater):
    '''Dataupdater subclass for Group objects'''
    def __init__(self,params,queue):        
        '''Initialises Group DataUpdater
        @param params: List of configuration parameters
        @type params: List<?>
        @param queue: Response queue
        @type queues: Queue.Queue
        '''
        super(DataUpdaterGroup,self).__init__(params,queue)
         
    def cid(self,f):
        return f['properties']['changeGroupId']
        
#     def getEntityInstance(self,ref):
#         return EntityAddress(ref)
    
class DataUpdaterUser(DataUpdater): 
    '''Dataupdater subclass for User objects'''   
    def __init__(self,params,queue):        
        '''Initialises User DataUpdater
        @param params: List of configuration parameters
        @type params: List<?>
        @param queue: Response queue
        @type queues: Queue.Queue
        '''
        super(DataUpdaterUser,self).__init__(params,queue)
    
#TODO Consolidate group/address + action/approve subclasses. might be enough variation to retain seperate classes
#NOTES variables incl; oft=FF/RF,id=addressId/changeId/groupChangeId, action=approve/action/groupaction
class DataUpdaterDRC(DataUpdater):
    '''Super class for DRC DataUpdater classes'''
    
    #instantiated in subclass
    oft,etft,identifier,payload,actiontype,action,agu,at,build,requestId = 10*(None,)
    
    def version(self):
        '''Quick self checker for existing version number to save additional request
        I{This functionality is under development in the API}
        '''
        return self.agu._version if hasattr(self.agu,'_version') and self.agu._version else self._version() 
    
    def _version(self):
        '''Function to read AIMS version value from single Feature pages
        @return: Integer. Feature version number 
        '''
        _,cid = SupplementalHack.strip(self.identifier)
        ce,jc = self.api.getOneFeature(FeedRef((self.etft.et,self.oft)),cid)
        if any(ce.values()): aimslog.error('Single-feature request failure {}'.format(ce))
        if jc['properties'].has_key('version'):
            return jc['properties']['version']
        else:
            #WORKAROUND
            aimslog.warn('No version number available for address/groupId={}'.format(self.identifier))
            return 1    
        
    def run(self):
        '''One pass run method to intercat with APi and return sincel page results
        - Call appropriate API method
        - Parse response Entities and attach to feature
        - Attach error messages and request ID
        - Merge response object with request object
        - Put featre on output queue
        - Notify listeners 
        '''
        aimslog.info('DUr.{} {} - AGU{}'.format(self.ref,self.actiontype.reverse[self.at],self.agu))
        payload = self.factory.convert(self.agu,self.at)
        err,resp = self.action(self.at,payload,self.identifier)
        featurelist = []
        feature = self.factory.get(model=resp['properties'])
        if hasattr(resp,'entities'):
            for e in resp['entities']:
                featurelist.append(self._populateEntity(e))
            feature._setEntities(featurelist)
        #feature = self.processPage(feature,self.etft)
        #print 'feature',feature
        if err: feature.setErrors(err)
        if self.requestId: feature.setRequestId(self.requestId)
        if MERGE_RESPONSE:
            aimslog.info('Merge req/res for {}'.format(self.agu))
            self.agu.setVersion(None)
            self.agu.merge(feature)
            self.queue.put(self.agu)
        else: self.queue.put(feature)
        self.notify(self.ref)
        
        
class DataUpdaterAction(DataUpdaterDRC): 
    '''DataUpdater class for Address Action requests on the changefeed'''
    
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.FEATURES
    
    def setup(self,etft,aat,address,_):
        '''Set Address Action specific parameters
        @param etft: Validation Entity feedref 
        @type etft: FeedRef
        @param aat: Action type for this address 
        @type aat: ActionType
        @param address: Address object detailing action changes
        @type address: Address
        '''
        self.etft = etft
        self.at = aat
        self.agu = address
        self.identifier = self.agu.getAddressId()
        self.requestId = self.agu.getRequestId()
        if aat != ActionType.ADD: self.agu.setVersion(self.version())
        #run actions
        self.actiontype = ActionType
        self.action = self.api.addressAction

class DataUpdaterApproval(DataUpdaterDRC):
    '''DataUpdater class for Address Approval requests on the resolutionfeed'''
    
    #et = FeatureType.ADDRESS
    #ft = FeedType.RESOLUTIONFEED
    oft = FeedType.RESOLUTIONFEED
    
    def setup(self,etft,aat,address,_):
        '''Set Address Approval specific parameters
        @param etft: Validation Entity feedref 
        @type etft: FeedRef
        @param aat: Approval type for this address 
        @type aat: ApprovalType
        @param address: Address object detailing approval action
        @type address: Address
        '''
        self.etft = etft
        self.at = aat
        self.agu = address
        self.identifier = self.agu.getChangeId()
        self.requestId = self.agu.getRequestId()
        self.agu.setVersion(self.version())
        #run actions
        self.actiontype = ApprovalType
        self.action = self.api.addressApprove

class DataUpdaterGroupAction(DataUpdaterDRC):
    '''DataUpdater class for Group Action requests on the changefeed'''
    
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.FEATURES
    
    def setup(self,etft,gat,group,_):
        '''Set Group Action specific parameters
        @param etft: Validation Entity feedref 
        @type etft: FeedRef
        @param gat: Group action type for this address 
        @type gat: GroupActionType
        @param address: Address object detailing action changes
        @type address: Address
        '''
        self.etft = etft
        self.at = gat
        self.agu = group
        self.identifier = self.agu.getChangeGroupId()
        self.requestId = self.agu.getRequestId()
        self.agu.setVersion(self.version())
        #run actions
        self.actiontype = GroupActionType
        self.action = self.api.groupAction
        
class DataUpdaterGroupApproval(DataUpdaterDRC):
    '''DataUpdater class for Group Approval requests on the resolutionfeed'''
    
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.RESOLUTIONFEED
    
    def setup(self,etft,gat,group,_):
        '''Set Group Approval specific parameters
        @param etft: Validation Entity feedref 
        @type etft: FeedRef
        @param gat: Group approval type for this address 
        @type gat: GroupApprovalType
        @param address: Address object detailing approval action
        @type address: Address
        '''
        self.etft = etft
        self.at = gat
        self.agu = group
        self.identifier = self.agu.getChangeGroupId()
        self.requestId = self.agu.getRequestId()
        self.agu.setVersion(self.version())
        #run actions
        self.actiontype = GroupApprovalType
        self.action = self.api.groupApprove
        
class DataUpdaterUserAction(DataUpdaterDRC):
    '''DataUpdater class for User Action requests on the adminfeed'''
    
    #et = FeatureType.ADDRESS
    #ft = FeedType.CHANGEFEED 
    oft = FeedType.ADMIN
    
    def setup(self,etft,uat,user,_):
        '''Set User specific parameters
        @param etft: Validation Entity feedref 
        @type etft: FeedRef
        @param uat: User action type for this user 
        @type uat: UserActionType
        @param user: User object detailing admin action
        @type user: User
        '''    
        self.etft = etft
        self.at = uat
        self.agu = user
        self.identifier = self.agu.getUserId()
        self.requestId = self.agu.getRequestId()
        #self.agu.setVersion(self.version())
        #run actions
        self.actiontype = UserActionType
        self.action = self.api.userAction
        
        
    
        
        