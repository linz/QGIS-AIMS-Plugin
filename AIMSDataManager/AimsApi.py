
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

import httplib2
import json
import re

from Address import Address,AddressChange,AddressResolution#,AimsWarning
from Config import ConfigReader
from AimsUtility import FeatureType,ActionType,ApprovalType,GroupActionType,GroupApprovalType,UserActionType,FeedType,LogWrap,FeedRef,SupplementalHack
from AimsUtility import AimsException
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
        '''Initialises API connector object with provided configuration.
        @param config: Dictionary of configuration values from CP
        '''
        self._url = config['url']
        self._password = ConfigReader.readp()
        self.user = config['user']
        self._headers = config['headers']

        self.h = httplib2.Http(".cache")
        self.h.add_credentials(self.user, self._password)
    
    def handleErrors(self, url, resp, jcontent):
        '''Process error messages flagging 400 class errors.
        @param url: URL of request (plan to use in err msg)
        @type url: String
        @param resp: Response code
        @type resp: int
        @param jcontent: Response message text
        @type jcontent: Dict
        @return: Dict of categorised error messages
        '''        
        ce = {'critical':(),'error':(),'warn':()}
        if str(resp) in ('400', '404') and jcontent.has_key('entities'):
            for entity in jcontent['entities']:
                if entity['properties']['severity'] == 'Reject':
                    ce['critical'] += (entity['properties']['description'],)
                else:
                    ce['error'] += (entity['properties']['description'],)
        
        elif str(resp) in ('200', '201'):
            pass
            
        elif str(resp) == '409':
            #criticalErrors.append(content['properties']['reason'] +'\n'+ content['properties']['message'])
            ce['critical'] += ('{} - {}'.format(jcontent['properties']['reason'],jcontent['entities'][0]['properties']['description']),)
        else:
            ce['critical'] += ('General Exception {}'.format(resp),)
             
        return ce
    
    def handleResponse(self, url, resp, jcontent):        
        '''Process HTTP response object intercepting errors/non-200 codes.
        @param url: URL of request
        @type url: String
        @param resp: Response code
        @type resp: int
        @param jcontent: Response message text
        @type jcontent: Dict
        @return: Dict of categorised error messages
        '''
        ce = {'critical':(),'error':(),'warn':()}
        if str(resp) not in ('101', '100', '200', '202'):
            # list of validation errors
            ce = self.handleErrors(url, resp, jcontent)
        return ce,jcontent
    
    def _xxxExtractLinkWorkaround(self,jcf):
        l = ''
        for link in jcf['links']:
            if link['rel'][0] == 'addressresolution':
                l = link['href']
                break
        match = re.search('.*\/(\d+)$',l)
        return match.group(1) if match else ''
        

    #-----------------------------------------------------------------------------------------------------------------------
    #--- A G G R E G A T E S  &  A L I A S E S -----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
    
    @LogWrap.timediff(prefix='LinkedFeatureHack')
    def _xxxGetLinkedFeatureWorkaround(self,cid1):
        '''Workaround to handle supplementary links
        @param etft: Feed/Feature identifier
        @type etft: FeedRef
        @param cid: ChangeId
        @type cid: Integer
        @return: Dict of JSON response
        '''
        etft1 = FeedRef(FeatureType.ADDRESS,FeedType.FEATURES)
        cef,jcf = self.getOneFeature(etft1, cid1)
        
        cid2 = self._xxxExtractLinkWorkaround(jcf)
        
        etft2 = FeedRef(FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)
        cer,jcr = self.getOneFeature(etft2, cid2)
        
        return cer,jcr
    
    
    def _request(self,*args,**kwargs):
        '''Wraps httplib2 requests for logging
        @param *args: Request arguments
        @type *args: List<?> 
        @param **kwargs: Request named arguments 
        @type **kwargs: Dict<String,?>
        @return: response,content
        '''
        aimslog.info("Request {}".format(args))
        return self.h.request(*args,**kwargs)
    
    @LogWrap.timediff(prefix='onePage')
    def getOnePage(self,etft,sw,ne,pno,count=MAX_FEATURE_COUNT):
        '''Retrieve a numbered page from a specific feed with optional bbox parameters
        @param etft: Feed/Feature identifier
        @type etft: FeedRef
        @param sw: South-West corner, coordinate value pair (optional)
        @type sw: List<Double>{2}
        @param ne: North-East corner, coordinate value pair (optional)
        @type ne: List<Double>{2}
        @param pno: Feed page number
        @type pno: Integer 
        @param count: Feature count (defaults to MAX_FEATURE_COUNT = 1000)
        @type count: Integer
        @return: Dictionary<Entity>
        '''
        et = FeatureType.reverse[etft.et].lower()
        ft = FeedType.reverse[etft.ft].lower()
        addrlist = []
        if sw and ne:
            bb = ','.join([str(c) for c in (sw[0],sw[1],ne[0],ne[1])])
            url = '{}/{}/{}?count={}&bbox={}&page={}'.format(self._url,et,ft,count,bb,pno)
        else:
            url = '{}/{}/{}?count={}&page={}'.format(self._url,et,ft,count,pno)
        resp, content = self._request(url,'GET', headers = self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content))
        #return jcontent['entities']
           
    @LogWrap.timediff(prefix='oneFeat')
    def getOneFeature(self,etft,cid):
        '''Get a CID numbered address including feature entities
        @param etft: Feed/Feature identifier
        @type etft: FeedRef
        @param cid: ChangeId
        @type cid: Integer
        @return: Dict of JSON response
        '''
        et = FeatureType.reverse[etft.et].lower()
        ft = FeedType.reverse[etft.ft].lower()
        url = '/'.join((self._url,et,ft.lower(),str(cid) if cid else '')).rstrip('/')
        #if count: url += '?count={}'.format(count)
        resp, content = self._request(url,'GET', headers = self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content))
        #return jcontent        
    
    # specific request response methods
    
    @LogWrap.timediff(prefix='adrAct')  
    def addressAction(self,at,payload,cid):
        '''Make an address change by posting a data to the AIMS changefeed
        @param at: Action type (add/del/upd) to AIMS address
        @type at: ActionType
        @param payload: JSON fomatted HTTP data request
        @type payload: String
        @param cid: ChangeId
        @type cid: Integer
        @return: Response from HTTP request
        '''
        et = FeatureType.reverse[FeatureType.ADDRESS].lower()
        ft = FeedType.reverse[FeedType.CHANGEFEED].lower()
        url = '/'.join((self._url,et,ft,ActionType.reverse[at].lower(),TESTPATH)).rstrip('/')
        resp, content = self._request(url,"POST", json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )  
    
    @LogWrap.timediff(prefix='adrApp')
    def addressApprove(self,at,payload,cid):
        '''Perform an address approval action by posting a change on the AIMS resolutionfeed
        @param at: Approval type (acc/rej/upd) to AIMS address
        @type at: ApprovalType
        @param payload: JSON fomatted HTTP data request
        @type payload: String
        @param cid: ChangeId
        @type cid: Integer
        @return: Response from HTTP request
        '''
        #<HACK> (2) Bypass on supplemental
        sup,cid = SupplementalHack.strip(cid)
        if sup: return self._xxxGetLinkedFeatureWorkaround(cid)
        #</HACK>
        #aimslog.debug('{0}'.format(payload))
        '''Approve/Decline a change by submitting address to resolutionfeed'''
        et = FeatureType.reverse[FeatureType.ADDRESS].lower()
        ft = FeedType.reverse[FeedType.RESOLUTIONFEED].lower()
        url = '/'.join((self._url,et,ft,str(cid),ApprovalType.PATH[at].lower(),TESTPATH)).rstrip('/')
        resp, content = self._request(url,ApprovalType.HTTP[at], json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )
    
    @LogWrap.timediff(prefix='grpAct')
    def groupAction(self,gat,payload,cid):
        '''Make a group change by posting a data to the AIMS changefeed
        @param gat: Action type (add/del/upd) to AIMS group
        @type gat: GroupActionType
        @param payload: JSON fomatted HTTP data request
        @type payload: String
        @param cid: ChangeId
        @type cid: Integer
        @return: Response from HTTP request
        '''
        et = FeatureType.reverse[FeatureType.GROUPS].lower()
        ft = FeedType.reverse[FeedType.CHANGEFEED].lower()
        url = '/'.join((self._url,et,ft,str(cid),GroupActionType.PATH[gat].lower(),TESTPATH)).rstrip('/')
        resp, content = self._request(url,GroupActionType.HTTP[gat], json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )    
    
    @LogWrap.timediff(prefix='grpApp')
    def groupApprove(self,gat,payload,cid):
        '''Perform a group approval action by posting a change on the AIMS resolutionfeed
        @param gat: Approval type (acc/rej/upd) to AIMS group
        @type gat: GroupApprovalType
        @param payload: JSON fomatted HTTP data request
        @type payload: String
        @param cid: ChangeId
        @type cid: Integer
        @return: Response from HTTP request
        '''
        et = FeatureType.reverse[FeatureType.GROUPS].lower()
        ft = FeedType.reverse[FeedType.RESOLUTIONFEED].lower()
        url = '/'.join((self._url,et,ft,str(cid),GroupApprovalType.PATH[gat].lower(),TESTPATH)).rstrip('/')
        resp, content = self._request(url,GroupApprovalType.HTTP[gat], json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )
    
    @LogWrap.timediff(prefix='usrAct')
    def userAction(self,uat,payload,uid):         
        '''Perform a user action by posting a change on the AIMS admin feed
        @param uat: User action type (add/del/upd) to AIMS user
        @type uat: UserActionType
        @param payload: JSON fomatted HTTP data request
        @type payload: String
        @param uid: UserId
        @type uid: Integer
        @return: Response from HTTP request
        '''
        #~/aims/api/admin/users {add/update/delete}
        url = '{}/admin/users/{}/{}'.format(self._url,uid,TESTPATH).rstrip('/')
        resp, content = self._request(url,UserActionType.HTTP[uat], json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        