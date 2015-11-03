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
