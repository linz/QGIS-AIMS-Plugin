################################################################################
#
# Copyright 2016 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################

import logging
import os

LOGDIR = '../log/'
aimslog = 'aims'
testlog = 'test'
#logger = logging.getLogger(aimslog)

class Logger(object):
    '''Logging class, used for common setup of log files''' 
    

    @staticmethod
    def setup(lf=aimslog,ll=logging.DEBUG,ff=1):
        formats = {1:'%(asctime)s - %(levelname)s - %(module)s %(lineno)d - %(message)s',
                   2:':: %(module)s %(lineno)d - %(message)s',
                   3:'%(asctime)s,%(message)s'}
        
        log = logging.getLogger(lf)
        log.setLevel(ll)
        
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), LOGDIR))
        if not os.path.exists(path):
            os.mkdir(path)
        df = os.path.join(path,lf.lower()+'.log')
        
        fh = logging.FileHandler(df,'w')
        fh.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(formats[ff])
        fh.setFormatter(formatter)
        log.addHandler(fh)
        
        return log