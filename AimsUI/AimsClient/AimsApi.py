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
import Config
from Config import ConfigReader

class AimsApi( ):
    ''' make and receive all http requests / responses to AIMS API '''
#     def __init__(self):
#         self._changeUrl = Config.ConfigSectionMap('url')['address']
#         self._user = Config.ConfigSectionMap('user')['name']
#         self._password = Config.ConfigSectionMap('user')['pass']
#         self._headers = {'content-type':'application/json', 'accept':'application/json'}    
        
    def __init__(self):
        config = ConfigReader()
        self._changeUrl = config.configSectionMap('url')['address']
        self._user = config.configSectionMap('user')['name']
        self._password = config.configSectionMap('user')['pass']
        self._headers = {'content-type':'application/json', 'accept':'application/json'}
           
    def changefeedAdd( self, payload ):
        ''' Add an address to the Change feed '''
        requests.get(self._changeUrl, data=json.dumps(payload), auth=(self._user, self._password))
        #test for failure and if so trigger error module and show warning
               
      
    def changefeedUpdate( self, payload ):
        ''' Update an address on the Change feed '''
        pass 
       
    def changefeedDelete( self, payload ):
        ''' Delete a address via Change feed '''
        pass
    
