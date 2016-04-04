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
AIMS_CONFIG = os.path.join(os.path.dirname(__file__),'aimsConfig.ini')


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
                val = self._retype(self.cp.get(sect,opt).replace('"','').strip("'"))
                self.d[sect][opt] = val or None
                            
    def _retype(self,val):    
        if val.isdigit(): val = int(val)
        elif val.replace('.','',1).isdigit(): val = float(val)
        elif val.lower() in ('true','false'): val = bool(val)
        return val
                
    def _fillConfig(self):
        '''Attempt to fill missing values in config file with matching env vars'''
        #NOTE env vars must use aims_sec_opt=val format and are bypassed with null value
        for sect in self.d:
            for k,val in self.d[sect].items():
                #check to see if config items are blank, if they are search in env vars
                if val is None or (isinstance(val,str) and ( val.strip() == '' or val == 'None' or all(i in whitespace for i in val) )):
                    envvar = 'aims_{}_{}'.format(sect,k)
                    eval = os.environ.get(envvar)
                    self.d[sect][k] = eval or DEF_CONFIG.get(sect,{}).get(k)
                    
    def _promptUser(self):
        '''If config cannot be populated with ini file and envvars prompt the user for missing values or report failure'''
        pass
                    
    def configSectionMap(self,section=None):
        '''per section config matcher'''
        return self.d[section] if section else self.d
            

        
