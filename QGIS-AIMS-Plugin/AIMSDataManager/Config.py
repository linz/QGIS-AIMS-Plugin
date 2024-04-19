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
import configparser
from string import whitespace

from qgis.core import QgsApplication

import getpass
import base64
try:
    # Unsure about the need/purpose for this. Could be replaced with the hashlib library however needs further investigation in
    # conjunction with LINZ. Currently we are storing the encryption details in this script which would be on the same machine as the hashed password. This is more or less useless...    
    from Crypto.Cipher import AES
    USE_PLAINTEXT = False
except:
    USE_PLAINTEXT = True

# HG Added
from .AimsLogging import Logger
aimslog = Logger.setup()

# UNAME = os.environ['USERNAME'] if re.search('win',sys.platform) else os.environ['LOGNAME']
UNAME = getpass.getuser()
DEF_CONFIG = {'db':{'host':'127.0.0.1'},'user':{'name':UNAME}}
AIMS_CONFIG = os.path.join(QgsApplication.qgisSettingsDirPath(), "aims", "aimsConfig.ini")

# For Unit Testing, outside of QGIS, set path to your .ini file here as QgsApplication.qgisSettingsDirPath() resolves to '' if not called from QGIS
if sys.platform == 'linux':
    # For testing via github actions, builds path to the repository aims_test_config.ini
    # AIMS_CONFIG = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Test', 'aims_test_config.ini')
    print(f'LINUX CI DETECTED - USING PATH: {AIMS_CONFIG}')

if AIMS_CONFIG == 'aims\\aimsConfig.ini':
    # Local testing 
    AIMS_CONFIG = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Test', 'aims_test_config.ini')

if not USE_PLAINTEXT:
    K='12345678901234567890123456789012'
    PADDING = '{'
    BLOCK_SIZE = 16
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

class ConfigReader(object):
    '''Reader class for configparser object'''
    cp = configparser.ConfigParser()
    
    def __init__(self):
        self.cp.read(AIMS_CONFIG)
        self._readConfig()
        self._fillConfig()
        
    def _readConfig(self):
        '''Read ConfigParser object to saved dict'''
        self.d = {}
        for sect in self.cp.sections():
            self.d[sect] = {}
            for opt in self.cp.options(sect):
                val = self._retype(self.cp.get(sect,opt).replace('"','').strip("'"))
                self.d[sect][opt] = val# or None (doesn't work if tryng to assign x=False)
                            
    def _retype(self,val):
        '''Utility function that attempts to cast String values to their correct type after reading from config file
        @param val: String or string representing some numeric/boolean
        @type val: String 
        '''    
        if val.isdigit(): val = int(val)
        elif val.replace('.','',1).isdigit(): val = float(val)
        elif val.lower() in ('true','false'): val = bool(val.lower()=='true')
        return val
                
    def _fillConfig(self):
        '''Attempt to fill missing local dict values not included in config file with matching environment variables.
        - I{This if needed to pass encrypted values when it is unsafe to be store them in a git repo}
        '''
        #NOTE env vars must use aims_sec_opt=val format and are bypassed with null value
        for sect in self.d:
            for k,val in self.d[sect].items():
                #check to see if config items are blank, if they are search in env vars
                if val is None or (isinstance(val,str) and ( val.strip() == '' or val == 'None' or all(i in whitespace for i in val) )):
                    envvar = 'aims_{}_{}'.format(sect,k)
                    eval = os.environ.get(envvar)
                    self.d[sect][k] = eval or DEF_CONFIG.get(sect,{}).get(k)
                    
    def _promptUser(self):
        '''I{unused}. If config cannot be populated with ini file and envvars prompt the user for missing values or report failure'''
        p = getpass.getpass()
                    
    def configSectionMap(self,section=None):
        '''Per section config matcher, used in constant reader class'''
        return self.d[section] if section else self.d
    
    #and now some security theatre for your amusement
    
    @staticmethod
    def _detect(p,cti):
        '''detects whether p has been ciphered or not, add conditions as required'''
        return bool(re.match('^{cti}.*$'.format(cti=cti),p))

    
    @staticmethod
    def readp():
        from .Const import CT_IND      
        cp = configparser.ConfigParser()
        cp.read(AIMS_CONFIG)
        sometext = cp.get('user','pass')
        if USE_PLAINTEXT:
            return sometext
        else:    
            if ConfigReader._detect(sometext,CT_IND):
                user = getpass.getuser()
                aes = AES.new(K, AES.MODE_CBC,pad(user))
                return DecodeAES(aes,sometext.strip(CT_IND))
            else:
                ConfigReader._writep(sometext)
                return sometext

    @staticmethod  
    def _writep(plaintext):
        from .Const import CT_IND      
        cp = configparser.ConfigParser()
        cp.read(AIMS_CONFIG)
        user = getpass.getuser()
        aes = AES.new(K, AES.MODE_CBC,pad(user))
        ciphertext = '{}{}'.format(CT_IND,EncodeAES(aes,plaintext))
        cp.set('user','pass',ciphertext)
        cp.write(open(AIMS_CONFIG,'w'))
        

            
def test():
    #ConfigReader.writep('secretpassword')
    p = ConfigReader.readp()
    print(p)
    
    p = ConfigReader.readp()
    print(p)
    
    ConfigReader._writep(p)
    
    
    
if __name__ == '__main__':
    test() 

        