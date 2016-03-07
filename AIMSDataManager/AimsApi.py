
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

from Address import Address,AddressChange,AddressResolution,AimsWarning
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
        
#     def _handleErrors(self, url, resp, content):
#         ''' Return the reason for any critical errors '''        
#         criticalErrors = []
#         aimslog.error('Error {} fetching\n{}\nwith result\n{}'.format(resp,url,content))
#         if str(resp) == '400': raise Http400Exception('400 {}'.format(content))
#         elif str(resp) == '404': raise Http404Exception('404 {}'.format(content))
#         else: raise AimsHttpException('Error {} fetching\n{}\nwith result\n{}'.format(resp,url,content))

  
    
    def handleErrors(self, url, resp, jcontent):
        ''' Return the reason for any critical errors '''        
        critical = ()
        if str(resp) in ('400', '404') and jcontent.has_key('entities'):
            for entity in jcontent['entities']:
                if entity['properties']['severity'] == 'Reject':
                    critical += (entity['properties']['description'],)
        elif str(resp) == '409':
            #criticalErrors.append(content['properties']['reason'] +'\n'+ content['properties']['message'])
            critical += ('{} - {}'.format(jcontent['properties']['reason'],jcontent['entities'][0]['properties']['description']),)
        else:
            critical += ('General Exception {}'.format(resp),)
             
        return critical
    
    def handleResponse(self, url, resp, jcontent):
        ''' test http response
        [] == no errors, else list of critical errors'''
        errors = ()
        if str(resp) not in ('201', '200'):
            # list of validation errors
            errors = self.handleErrors(url, resp, jcontent)
        return errors,jcontent

#     def changefeedAdd(self, payload):
#         ''' Add an address to the Change feed '''
#         resp, content = self.h.request(self._url+'address/changefeed/add', "POST", json.dumps(payload), self._headers)
#         return self.handleResponse('',resp["status"], json.loads(content) )
#      
#     def changefeedRetire(self, retireFeatures):
#         ''' Retire address via Change feed '''
#         error = []
#         for payload in retireFeatures:
#             resp, content = self.h.request(self._url+'address/changefeed/retire', "POST", json.dumps(payload), self._headers)
#             errorHandling = (self.handleResponse('',resp["status"], json.loads(content)))
#             if errorHandling == []:
#                 continue
#             else: error.append(errorHandling)
#         return {'errors': error}
#     
#     def getFeatures( self, xMax, yMax, xMin, yMin ):
#         ''' get aims addresses within bbox'''
#         urlEnd ='address/features?count=1000&bbox={0},{1},{2},{3}'.format(xMin,yMin,xMax,yMax)
#         resp, content = self.h.request(self._url+urlEnd, 'GET', headers = self._headers)
#         return json.loads(content) # Validation ... 
#     
#     def updateFeature(self, payload):
#         ''' update aims address feature '''
#         resp, content = self.h.request(self._url+'address/changefeed/update', "POST", json.dumps(payload),headers = self._headers)
#         return self.handleResponse('',resp["status"], json.loads(content) )
#     
#     def newGroup(self, payload):
#         ''' opens a new group and returns the new groupId '''
#         resp, content = self.h.request(self._url+'groups/changefeed/replace', "POST", json.dumps(payload),headers = self._headers)
#         return {'errors': self.handleResponse('',resp["status"], json.loads(content)),
#                 'data':{'groupId':json.loads(content)['properties']['changeGroupId'],
#                 'groupVersionId':json.loads(content)['properties']['version']}}
# 
#     def addToGroup(self, groupId, groupData):
#         ''' add addresses to a lineage group '''
#         error = []
#         for payload in groupData:
#             resp, content = self.h.request(self._url+'groups/changefeed/{}/address/add/'.format(groupId),"POST" , json.dumps(payload), headers = self._headers)
#             errorHandling = (self.handleResponse('',resp["status"], json.loads(content)))
#             if errorHandling == []:
#                 continue
#             else: error.append(errorHandling+payload['address'])
#         return {'errors': error}
#     
#     def submitGroup(self, groupId, payload):
#         ''' add addresses to a lineage group '''
#         error = []
#         resp, content = self.h.request(self._url+'groups/changefeed/{}/submit/'.format(groupId),"POST" , json.dumps(payload), headers = self._headers)
#         #error=self.handleResponse(resp["status"], json.loads(content))
#         errorHandling = (self.handleResponse('',resp["status"], json.loads(content)))
#         if errorHandling != []:
#             error.append(errorHandling)
#         return {'errors': error}
#     
#     def groupVersion(self, groupId):
#         ''' opens a new group and returns the new groupId '''
#         resp, content = self.h.request(self._url+'groups/changefeed/{}'.format(groupId),'GET', headers = self._headers)
#         return {'errors': self.handleResponse('',resp["status"], json.loads(content)),
#                 'data':{'groupVersionId':json.loads(content)['properties']['version']}}
#         
#     def getResItemsHrefs (self):
#         """ get the reference to each resolution item associated with each resolution pages"""    
#         resp, content = self.h.request(self._url+'address/resolutionfeed?count=1000','GET', headers = self._headers) #under dev, currently only looking at the one page
#         content = json.loads(content)
#         for i in content['entities']:
#             yield i['links'][0]['href']
#     
#     def getResData(self):
#         ''' returns all res items '''
#         for href in self.getResItemsHrefs():        
#             content = self.h.request(href,'GET', headers = self._headers)
#             yield content # need to wrap in {'errors':error,data{data}}
            
            
    #-----------------------------------------------------------------------------------------------------------------------
    #--- A G G R E G A T E S  &  A L I A S E S -----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
    
    
    def getAllPages(self,ft,count=MAX_FEATURE_COUNT):
        '''Get all available pages sequentially'''
        return self.getPageUp(ft, page=1, count=count)
    
    def getPageUp(self,ft,page,count=MAX_FEATURE_COUNT):
        entities = 1
        addrlist = {}
        addrlist[ft] = ()
        while entities:
            addrlist[ft] += self.getOnePage(ft, page, count)
            page += 1
            aimslog.info('PageRef.{}'.format(page))
        return (page,addrlist)
            
    #-----------------------------------------------------------
    
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


    def getWarnings(self,ft,cid):
        '''Get warnings for a changeId'd resolutionfeed address'''
        url = '{}/{}/{}'.format(self._url,FeedType.reverse[ft].lower(),cid)
        resp, content = self.h.request(url,"GET", headers = self._headers)
        err, jcontent = self.handleResponse(url, resp["status"], json.loads(content))
        warnlist = {'error':err,'warn':()} if err else {'error':None,'warn':()}
        for entity in jcontent['entities']:
            warnlist['warn'] += (AimsWarning.getInstance(entity['properties']),)
        return warnlist
    
        
    def changefeedActionAddress(self,at,payload):
        '''Make a change to the feature list by posting a change on the changefeed'''
        url = '{}/changefeed/{}'.format(self._url,ActionType.reverse[at].lower())
        resp, content = self.h.request(url,"POST", json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )  
    
    def resolutionfeedApproveAddress(self,at,payload,cid):
        '''Approve/Decline a change by submitting address to resolutionfeed'''
        url = '{}/resolutionfeed/{}/{}'.format(self._url,cid,ApprovalType.reverse[at].lower())
        resp, content = self.h.request(url,"POST", json.dumps(payload), self._headers)
        return self.handleResponse(url,resp["status"], json.loads(content) )
    
       
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        