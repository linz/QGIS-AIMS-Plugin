
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

from Address import Address,AddressChange,AddressResolution
from Config import ConfigReader
from AimsUtility import ActionType,ApprovalType,FeedType,MAX_FEATURE_COUNT
from AimsLogging import Logger


aimslog = None

class AimsApi(object):
    ''' make and receive all http requests / responses to AIMS API '''
      
    global aimslog
    aimslog = Logger.setup()
    
    def __init__(self,config,afactory):
        self._url = config['url']
        self._password = config['password']
        self.user = config['user']
        self._headers = config['headers']
        
        self.afactory = afactory

        self.h = httplib2.Http(".cache")
        self.h.add_credentials(self.user, self._password)
   
    def handleErrors(self, resp, content):
        ''' Return the reason for any critical errors '''        
        criticalErrors = []
        if str(resp) in ('400', '404') and content.has_key('entities'):
            for i in content['entities']:
                if i['properties']['severity'] == 'Reject':
                    criticalErrors.append( '- '+i['properties']['description']+'   \n' )
                else: return [] # <-- the error was not critical
        elif str(resp) == '409':
            #criticalErrors.append(content['properties']['reason'] +'\n'+ content['properties']['message'])
            criticalErrors.append('\n\n'+content['properties']['reason'] +' - '+ content['entities'][0]['properties']['description']+':'+'\n    ')
        else:
            criticalErrors = str(resp)
            
        return ''.join(criticalErrors)
    
    def handleResponse(self, resp, content):
        ''' test http response
        [] == no errors, else list of critical errors'''
        if str(resp) in ('201', '200'): #to be more inclusive i.e. 200 ...
            return [] #i.e. no errors
        else:
            # list of validation errors
            errors = self.handleErrors(resp, content)
            if errors == []:
                return errors #<-- there was an error but current only showing 'Reject'
            elif len(errors) > 0:
                return errors
            else:
                # Failing that give the user the direct http response
                return ' Please contact your system administrator \n HTTP Error:  ' + resp

    def changefeedAdd(self, payload):
        ''' Add an address to the Change feed '''
        resp, content = self.h.request(self._url+'address/changefeed/add', "POST", json.dumps(payload), self._headers)
        return self.handleResponse(resp["status"], json.loads(content) )
     
    def changefeedRetire(self, retireFeatures):
        ''' Retire address via Change feed '''
        error = []
        for payload in retireFeatures:
            resp, content = self.h.request(self._url+'address/changefeed/retire', "POST", json.dumps(payload), self._headers)
            errorHandling = (self.handleResponse(resp["status"], json.loads(content)))
            if errorHandling == []:
                continue
            else: error.append(errorHandling)
        return {'errors': error}
    
    def getFeatures( self, xMax, yMax, xMin, yMin ):
        ''' get aims addresses within bbox'''
        urlEnd ='address/features?count=1000&bbox={0},{1},{2},{3}'.format(xMin,yMin,xMax,yMax)
        resp, content = self.h.request(self._url+urlEnd, 'GET', headers = self._headers)
        return json.loads(content) # Validation ... 
    
    def updateFeature(self, payload):
        ''' update aims address feature '''
        resp, content = self.h.request(self._url+'address/changefeed/update', "POST", json.dumps(payload),headers = self._headers)
        return self.handleResponse(resp["status"], json.loads(content) )
    
    def newGroup(self, payload):
        ''' opens a new group and returns the new groupId '''
        resp, content = self.h.request(self._url+'groups/changefeed/replace', "POST", json.dumps(payload),headers = self._headers)
        return {'errors': self.handleResponse(resp["status"], json.loads(content)),
                'data':{'groupId':json.loads(content)['properties']['changeGroupId'],
                'groupVersionId':json.loads(content)['properties']['version']}}

    def addToGroup(self, groupId, groupData):
        ''' add addresses to a lineage group '''
        error = []
        for payload in groupData:
            resp, content = self.h.request(self._url+'groups/changefeed/{}/address/add/'.format(groupId),"POST" , json.dumps(payload), headers = self._headers)
            errorHandling = (self.handleResponse(resp["status"], json.loads(content)))
            if errorHandling == []:
                continue
            else: error.append(errorHandling+payload['address'])
        return {'errors': error}
    
    def submitGroup(self, groupId, payload):
        ''' add addresses to a lineage group '''
        error = []
        resp, content = self.h.request(self._url+'groups/changefeed/{}/submit/'.format(groupId),"POST" , json.dumps(payload), headers = self._headers)
        #error=self.handleResponse(resp["status"], json.loads(content))
        errorHandling = (self.handleResponse(resp["status"], json.loads(content)))
        if errorHandling != []:
            error.append(errorHandling)
        return {'errors': error}
    
    def groupVersion(self, groupId):
        ''' opens a new group and returns the new groupId '''
        resp, content = self.h.request(self._url+'groups/changefeed/{}'.format(groupId),'GET', headers = self._headers)
        return {'errors': self.handleResponse(resp["status"], json.loads(content)),
                'data':{'groupVersionId':json.loads(content)['properties']['version']}}
        
    def getResItemsHrefs (self):
        """ get the reference to each resolution item associated with each resolution pages"""    
        resp, content = self.h.request(self._url+'address/resolutionfeed?count=1000','GET', headers = self._headers) #under dev, currently only looking at the one page
        content = json.loads(content)
        for i in content['entities']:
            yield i['links'][0]['href']
    
    def getResData(self):
        ''' returns all res items '''
        for href in self.getResItemsHrefs():        
            content = self.h.request(href,'GET', headers = self._headers)
            yield content # need to wrap in {'errors':error,data{data}}
            
            
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
            
    def getOnePage(self,ft,sw,ne,page,count=MAX_FEATURE_COUNT):
        '''Get a numbered page'''
        addrlist = []
        if sw and ne:
            bb = '{},{},{},{}'.format(sw[0],sw[1],ne[0],ne[1])
            url = '{}/{}?count={}&bbox={}&page={}'.format(self._url,FeedType.reverse[ft].lower(),count,bb,page)
        else:
            url = '{}/{}?count={}&page={}'.format(self._url,FeedType.reverse[ft].lower(),count,page)
        print 'REQUEST',url
        resp, content = self.h.request(url,'GET', headers = self._headers)
        for entity in json.loads(content)['entities']:
            href = entity['links'][0]['href']#TODO specify address type
            addrlist += [self.afactory.getAddress(model=entity['properties']),]
        return addrlist

        
    def changefeedActionAddress(self,at,payload):
        '''Make a change to the feature list by posting a change on the changefeed'''
        jser = json.dumps(self.afactory.convertAddress(payload,at))#         AddressChange._export(payload))
        url = '{}address/changefeed/{}'.format(self._url,ActionType.reverse[at].lower())
        resp, content = self.h.request(url,"POST", jser, self._headers)
        return self.handleResponse(resp["status"], json.loads(content) )    
    
    def resolutionfeedActionAddress(self,at,payload):
        '''Approve/Decline a change by submitting address to resolutionfeed'''
        jser = json.dumps(self.afactory.convertAddress(payload,at))                       #AddressResolution._export(payload))
        url = '{}address/resolutionfeed/{}'.format(self._url,ApprovalType.reverse[at].lower())
        resp, content = self.h.request(url,"POST", jser, self._headers)
        return self.handleResponse(resp["status"], json.loads(content) )
    
    #not needed
    def featureAddAddress(self,payload): return self.changefeedActionAddress(ActionType.ADD, payload)    
    def featureRetireAddress(self,payload): return self.changefeedActionAddress(ActionType.RETIRE, payload)    
    def featureUpdateAddress(self,payload): return self.changefeedActionAddress(ActionType.UPDATE, payload)    

    def changefeedAddAddress(self,payload): return self.featureAddAddress(payload)
    def changefeedRetireAddress(self,payload): return self.featureRetireAddress(payload)
    def changefeedUpdateAddress(self,payload): return self.featureUpdateAddress(payload)
       
    def resolutionfeedApproveAddress(self,payload): return self.resolutionfeedActionAddress(ApprovalType.APPROVE, payload)   
    def resolutionfeedDeclineAddress(self,payload): return self.resolutionfeedActionAddress(ApprovalType.DECLINE, payload)   
    def resolutionfeedUpdateAddress(self,payload): return self.resolutionfeedActionAddress(ApprovalType.UPDATE, payload)   
       
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        