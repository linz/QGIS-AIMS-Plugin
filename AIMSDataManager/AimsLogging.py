
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

import logging
import os

LOGDIR = '../log/'
aimslog = 'aims'
testlog = 'test'
#logger = logging.getLogger(aimslog)

class Logger(object):
    '''AIMS Logging class, used in the DataManager package for common setup of log files''' 
    

    @staticmethod
    def setup(lf=aimslog,ll=logging.DEBUG,ff=1):
        '''Initialises (one of three types of) new logging object.
        @param lf: Name of log file to create. default=aims
        @type lf: String
        @param ll: Level to run this logger at, debug,error,warn etc. default=DEBUG
        @type ll: logging.loglevel
        @param ff: Logging format preset (1..3). default=1
        @type ff: Integer
        @return: logging.logger
        '''
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