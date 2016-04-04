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
    class ConstError(TypeError): pass    
    def __init__(self):
        CR = ConfigReader()
        for key in CR.configSectionMap('const'):
            val = CR.configSectionMap('const')[key]
            if val.isdigit(): val = int(val)
            elif val.replace('.','',1).isdigit(): val = float(val)
            elif val.lower() in ('true','false'): val = bool(val)
            setattr(self, key.upper(), val) 
             
    def __setattr__(self,name,value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind const(%s)"%name
        self.__dict__[name]=value
        
_ref, sys.modules[__name__] = sys.modules[__name__], const()
