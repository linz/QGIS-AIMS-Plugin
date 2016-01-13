
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

from Config import ConfigReader

class AimsApi(object):
    ''' make and receive all http requests / responses to AIMS API '''   
    
    def __init__(self):
        config = ConfigReader()
        self._url = config.configSectionMap('url')['api']
        self.user = config.configSectionMap('user')['name']
        self._password = config.configSectionMap('user')['pass']
        self._headers = {'content-type':'application/json', 'accept':'application/json'}
        
        self.h = httplib2.Http(".cache")
        self.h.add_credentials(self.user, self._password)
   
    def handleErrors(self, resp, content):
        ''' Return the reason for any critical errors '''        
        criticalErrors = []
        if str(resp) in ('400', '404') :
            for i in content['entities']:
                if i['properties']['severity'] == 'Reject':
                    criticalErrors.append( '- '+i['properties']['description']+'   \n' )
                else: return [] # <-- the error was not critical
        elif str(resp) == '409':
            #criticalErrors.append(content['properties']['reason'] +'\n'+ content['properties']['message'])
            criticalErrors.append('\n\n'+content['properties']['reason'] +' - '+ content['entities'][0]['properties']['description']+':'+'\n    ')
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

