
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
import httplib2

from Address import Address,AddressChange,AddressResolution#,AimsWarning
from Config import ConfigReader
from AimsUtility import ActionType,ApprovalType,FeedType,MAX_FEATURE_COUNT
from AimsLogging import Logger


aimslog = Logger.setup()

class AimsHttpException(Exception):
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

    def getOnePage(self,ft,sw,ne,page,count=MAX_FEATURE_COUNT):
        '''Get a numbered page'''
        addrlist = []
        if sw and ne:
            bb = '{},{},{},{}'.format(sw[0],sw[1],ne[0],ne[1])
            url = '{}/{}?count={}&bbox={}&page={}'.format(self._url,FeedType.reverse[ft].lower(),count,bb,page)
        else:
            url = '{}/{}?count={}&page={}'.format(self._url,FeedType.reverse[ft].lower(),count,page)
        aimslog.debug('1P REQUEST {}'.format(url))
        resp, content = self.h.request(url,'GET', headers = self._headers)
        _,jcontent = self.handleResponse(url,resp["status"], json.loads(content))
        return jcontent['entities']    
    
    def getOneFeature(self,ft,cid):
        '''Get a CID numbered address including feature entities'''
        url = '{}/{}/{}'.format(self._url,FeedType.reverse[ft].lower(),cid)
        #aimslog.debug('FEAT REQUEST {}'.format(url))
        resp, content = self.h.request(url,'GET', headers = self._headers)
        _,jcontent = self.handleResponse(url,resp["status"], json.loads(content))
        return jcontent        
    
    # specific request response methods

#     @deprected
#     def getWarnings(self,ft,cid):
#         '''Get warnings for a changeId'd resolutionfeed address'''
#         url = '{}/{}/{}'.format(self._url,FeedType.reverse[ft].lower(),cid)
#         resp, content = self.h.request(url,"GET", headers = self._headers)
#         warnlist, jcontent = self.handleResponse(url, resp["status"], json.loads(content))
#         #entities->warnings
#         if jcontent.has_key('entities'):
#             for entity in jcontent['entities']:
#                 warnlist['warn'] += (AimsWarning.getInstance(entity['properties']),)
#         else:
#             warnlist['error'] += (AimsWarning.getInstance('Entities not available in JSON response'),)
#         #properties->version
#         if jcontent.has_key('properties') and jcontent['properties'].has_key('version'):
#             warnlist['version'] = jcontent['properties']['version']
#         return warnlist

        
    def changefeedActionAddress(self,at,payload):
        '''Make a change to the feature list by posting a change on the changefeed'''
        url = '{}/changefeed/{}'.format(self._url,ActionType.reverse[at].lower())
        resp, content = self.h.request(url,"POST", json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )  
    
    def resolutionfeedApproveAddress(self,at,payload,cid):
        '''Approve/Decline a change by submitting address to resolutionfeed'''
        url = '{}/resolutionfeed/{}/{}'.format(self._url,cid,ApprovalType.reverse[at].lower())
        resp, content = self.h.request(url,ApprovalType.HTTP[at], json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )
    
