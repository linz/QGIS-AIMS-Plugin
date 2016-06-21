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

# NOTE
# This is potentiall quite a dangerous way to set constants since it overwrites sys.modules and deletes the builtins.
# To prevent this we have to hold a _ref to sys to keep it from being deleted

import sys
from Config import ConfigReader

class const:
    '''Const class that reads config stored values and presents them as constant values that can be imported'''
    
    class ConstError(TypeError): pass
        
    def __init__(self):
        '''Initialises and sets sel attributes from configreader values in 'const' section'''
        CR = ConfigReader()
        for key in CR.configSectionMap('const'):
            val = CR.configSectionMap('const')[key]
            setattr(self, key.upper(), val) 
             
    def __setattr__(self,name,value):
        '''Overriding setattr method catching overwrites
        @param name: Attribute name
        @param value: Attribute value
        '''
        if self.__dict__.has_key(name):
            raise self.ConstError('Can\'t rebind const {}'.format(name))
        self.__dict__[name]=value
        
#sys.modules overwritten here but _ref holding builtins 
_ref, sys.modules[__name__] = sys.modules[__name__], const()
