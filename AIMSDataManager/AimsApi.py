
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
import json
import sys
import httplib2

from Address import Address,AddressChange,AddressResolution#,AimsWarning
from Config import ConfigReader
from AimsUtility import FeatureType,ActionType,ApprovalType,GroupActionType,GroupApprovalType,FeedType,AimsException,LogWrap
from Const import MAX_FEATURE_COUNT,TEST_MODE
from AimsLogging import Logger


aimslog = Logger.setup()
TESTPATH = 'test' if TEST_MODE else ''

class AimsHttpException(AimsException):
    def __init__(self,em,ll=aimslog.error): 
        ll('{} - {}'.format(type(self).__name__,em))

    
class Http404Exception(AimsHttpException): pass
class Http400Exception(AimsHttpException): pass

class AimsApi(object):
    ''' make and receive all http requests / responses to AIMS API '''
      
    #global aimslog
    #aimslog = Logger.setup()
    
    def __init__(self,config):
        self._url = config['url']
        self._password = config['password']
        self.user = config['user']
        self._headers = config['headers']

        self.h = httplib2.Http(".cache")
        self.h.add_credentials(self.user, self._password)
    
    def handleErrors(self, url, resp, jcontent):
        ''' Return the reason for any critical errors '''        
        ce = {'critical':(),'error':(),'warn':()}
        if str(resp) in ('400', '404') and jcontent.has_key('entities'):
            for entity in jcontent['entities']:
                if entity['properties']['severity'] == 'Reject':
                    ce['critical'] += (entity['properties']['description'],)
                else:
                    ce['error'] += (entity['properties']['description'],)
        elif str(resp) == '409':
            #criticalErrors.append(content['properties']['reason'] +'\n'+ content['properties']['message'])
            ce['critical'] += ('{} - {}'.format(jcontent['properties']['reason'],jcontent['entities'][0]['properties']['description']),)
        else:
            ce['critical'] += ('General Exception {}'.format(resp),)
             
        return ce
    
    def handleResponse(self, url, resp, jcontent):
        ''' test http response
        [] == no errors, else list of critical errors'''
        ce = {'critical':(),'error':(),'warn':()}
        if str(resp) not in ('201', '200'):
            # list of validation errors
            ce = self.handleErrors(url, resp, jcontent)
        return ce,jcontent

    #-----------------------------------------------------------------------------------------------------------------------
    #--- A G G R E G A T E S  &  A L I A S E S -----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
    @LogWrap.timediff(prefix='onePage')
    def getOnePage(self,etft,sw,ne,page,count=MAX_FEATURE_COUNT):
        '''Get a numbered page'''
        et = FeatureType.reverse[etft.et].lower()
        ft = FeedType.reverse[etft.ft].lower()
        addrlist = []
        if sw and ne:
            bb = ','.join([str(c) for c in (sw[0],sw[1],ne[0],ne[1])])
            url = '{}/{}/{}?count={}&bbox={}&page={}'.format(self._url,et,ft,count,bb,page)
        else:
            url = '{}/{}/{}?count={}&page={}'.format(self._url,et,ft,count,page)
        aimslog.debug('1P REQUEST {}'.format(url))
        resp, content = self.h.request(url,'GET', headers = self._headers)
        _,jcontent = self.handleResponse(url,resp["status"], json.loads(content))
        return jcontent['entities']
    
    @LogWrap.timediff(prefix='oneFeat')
    def getOneFeature(self,etft,cid):
        '''Get a CID numbered address including feature entities'''
        et = FeatureType.reverse[etft.et].lower()
        ft = FeedType.reverse[etft.ft].lower()
        url = '/'.join((self._url,et,ft.lower(),str(cid) if cid else '')).rstrip('/')
        resp, content = self.h.request(url,'GET', headers = self._headers)
        _,jcontent = self.handleResponse(url,resp["status"], json.loads(content))
        return jcontent        
    
    # specific request response methods
    
    @LogWrap.timediff(prefix='adrAct')  
    def addressAction(self,at,payload,cid):
        '''Make a change to the feature list by posting a change on the changefeed'''
        et = FeatureType.reverse[FeatureType.ADDRESS].lower()
        ft = FeedType.reverse[FeedType.CHANGEFEED].lower()
        url = '/'.join((self._url,et,ft,ActionType.reverse[at].lower(),TESTPATH)).rstrip('/')
        resp, content = self.h.request(url,"POST", json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )  
    @LogWrap.timediff(prefix='adrApp')
    def addressApprove(self,at,payload,cid):
        aimslog.debug('{0}'.format(payload))
        '''Approve/Decline a change by submitting address to resolutionfeed'''
        et = FeatureType.reverse[FeatureType.ADDRESS].lower()
        ft = FeedType.reverse[FeedType.RESOLUTIONFEED].lower()
        url = '/'.join((self._url,et,ft,str(cid),ApprovalType.PATH[at].lower(),TESTPATH)).rstrip('/')
        resp, content = self.h.request(url,ApprovalType.HTTP[at], json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )
    @LogWrap.timediff(prefix='grpAct')
    def groupAction(self,gat,payload,cid):
        '''Perform action on group changefeed'''
        et = FeatureType.reverse[FeatureType.GROUPS].lower()
        ft = FeedType.reverse[FeedType.CHANGEFEED].lower()
        url = '/'.join((self._url,et,ft,str(cid),GroupActionType.PATH[gat].lower(),TESTPATH)).rstrip('/')
        resp, content = self.h.request(url,GroupActionType.HTTP[gat], json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )    
    
    @LogWrap.timediff(prefix='grpApp')
    def groupApprove(self,gat,payload,cid):
        '''Approve/Decline a change by submitting group to resolutionfeed'''
        et = FeatureType.reverse[FeatureType.GROUPS].lower()
        ft = FeedType.reverse[FeedType.RESOLUTIONFEED].lower()
        url = '/'.join((self._url,et,ft,str(cid),GroupApprovalType.PATH[gat].lower(),TESTPATH)).rstrip('/')
        resp, content = self.h.request(url,GroupApprovalType.HTTP[gat], json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )
    
    
