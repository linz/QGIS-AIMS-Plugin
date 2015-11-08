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
import requests

from Config import ConfigReader

class AimsApi( ):
    ''' make and receive all http requests / responses to AIMS API '''   
        
    def __init__(self):
        config = ConfigReader()
        self._url = config.configSectionMap('url')['api']
        self._user = config.configSectionMap('user')['name']
        self._password = config.configSectionMap('user')['pass']
        self._headers = {'content-type':'application/json', 'accept':'application/json'}
    
    @staticmethod #or do i want classmethod?    
    def handleErrors( r ):
        ''' Return the reason for any critical errors '''        
        criticalErrors = []
        for i in r['entities']:
            if i['properties']['severity'] == 'Reject':
                criticalErrors.append( '- '+i['properties']['description']+'\n' )
        return ''.join(criticalErrors)

    @staticmethod       
    def handleResponse(cls, r ):
        ''' test http response'''
        if r.status_code == 201: #to be more inclusive i.e. 200 ...
            return [] #i.e. no errors
        return cls.handleErrors( r.json() )
    
    def changefeedAdd( self, payload ):
        ''' Add an address to the Change feed '''
        r = requests.post(self._url+'changefeed/add', headers = self._headers, data=json.dumps(payload), auth=(self._user, self._password))
        return self.handleResponse(self, r )
       
        #test for failure and if so trigger error module and show warning
               
      
    def changefeedUpdate( self, payload ):
        ''' Update an address on the Change feed '''
        pass 
       
    def changefeedDelete( self, payload ):
        ''' Delete a address via Change feed '''
        pass
