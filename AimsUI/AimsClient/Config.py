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
import ConfigParser
from string import whitespace

config_path = os.path.join(os.path.dirname(__file__),'../aimsConfig.ini')
config = ConfigParser.ConfigParser()
config.read(config_path) #if we go down this path will need to decide on common OPA and Ubuntu location

def ConfigSectionMap(section):
    ''' obtain system variables as stored locally '''
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            dict1[option] = None
    return dict1


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
        #NOTE env vars must use sec-opt=val format and are bypassed with null value
        for sect in self.d:
            for k,val in self.d[sect].items():
                if not val or val == 'None' or val == '' or all(i in whitespace for i in val):
                    self.d[sect][k] = os.environ['aims_{}_{}'.format(sect,k)]
                    
    def configSectionMap(self,section):
        '''per section config matcher'''
        return self.d[section]
        
    
        
        