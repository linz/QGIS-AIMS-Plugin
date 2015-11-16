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
import os
import sys
import re
import ConfigParser
from string import whitespace

UNAME = os.environ['USERNAME'] if re.search('win',sys.platform) else os.environ['LOGNAME']
DEF_CONFIG = {'db':{'host':'127.0.0.1'},'user':{'name':UNAME}}
AIMS_CONFIG = os.path.join(os.path.dirname(__file__),'../aimsConfig.ini')

class ConfigReader(object):
    
    cp = ConfigParser.ConfigParser()
    
    def __init__(self):
        self.cp.read(AIMS_CONFIG)
        self._readConfig()
        self._fillConfig()
        
    def _readConfig(self):
        '''Read the CP to a dict'''
        self.d = {}
        for sect in self.cp.sections():
            self.d[sect] = {}
            for opt in self.cp.options(sect):
                val = self.cp.get(sect,opt)
                self.d[sect][opt] = val if val else None
                
    def _fillConfig(self):
        '''Attempt to fill missing values in config file with matching env vars'''
        #NOTE env vars must use aims_sec_opt=val format and are bypassed with null value
        for sect in self.d:
            for k,val in self.d[sect].items():
                if not val or val == 'None' or val == '' or all(i in whitespace for i in val):
                    eval = os.environ['aims_{}_{}'.format(sect,k)] if 'aims_{}_{}'.format(sect,k) in os.environ else None
                    dcval = DEF_CONFIG[sect][k] if sect in DEF_CONFIG and k in DEF_CONFIG[sect] else None
                    self.d[sect][k] = eval if eval else dcval
                    
    def _promptUser(self):
        '''If config cannot be populated with ini file and envvars prompt the user for missing values or report failure'''
        pass
                    
    def configSectionMap(self,section=None):
        '''per section config matcher'''
        return self.d[section] if section else self.d
        
    
        
        