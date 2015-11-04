'''
v.0.0.1

QGIS-AIMS-Plugin - AimsLogging

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Created on 29/10/2015

@author: jramsay
'''

import logging
import os

LOGDIR = '../log/'
mainlog = 'DEBUG'
aimslog = logging.getLogger(mainlog)

class Logger(object):
    '''Logging class, used for common setup of log files''' 
    

    @staticmethod
    def setup(lf=mainlog,ll=logging.DEBUG,ff=1):
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