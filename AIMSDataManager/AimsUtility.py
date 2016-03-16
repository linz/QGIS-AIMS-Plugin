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
from Config import ConfigReader
from functools import wraps, partial
import time
from AimsLogging import Logger

# C O N S T A N T S

#time to wait for threads to join after stop has been called eg On BB move (s)
THREAD_JOIN_TIMEOUT = 5
#max number of features to request per page 
MAX_FEATURE_COUNT = 1000
#first page (to not backfill past)
FIRST_PAGE = 1
#upper limit on page number to request
PAGE_LIMIT = 1000
#time delay between thread checks to see if pooled page has returned (s) 
POOL_PAGE_CHECK_DELAY = 0.2
#time delay between thread checks to see if user action has returned a response (s) 
QUEUE_CHECK_DELAY = 1
#when backfilling pages guess start point to find last page in change feed
LAST_PAGE_GUESS = 10
#initial page number indicating page search is required
NULL_PAGE_VALUE = 0
#automatically inset warnings into resolution feed features. very slow, enable only if RF is small
ENABLE_RESOLUTION_FEED_WARNINGS = True
#filename for persisted feed data
LOCALADL = 'aimsdata'
#zero southwest coordinate used for instantiation and to prevent unnecessary feature fetching
SWZERO = (0.0, 0.0)
#zero northeast coordinate used for instantiation and to prevent unnecessary feature fetching
NEZERO = (0.0, 0.0)
#enable null value removal in json requests
SKIP_NULL = True
#address attribute to dict separator character
DEF_SEP = '_'


aimslog = Logger.setup()

# def constant(f):
#     def fset(self, value):
#         raise TypeError
#     def fget(self):
#         return f()
#     return property(fget, fset)
# 
# class _Const(object):
#     @constant 
#     def FOO(): return 'foo'
#     @constant
#     def BAR(): return 'bar'

class Configuration(object):
    def __init__(self): 
        self.config = ConfigReader()
        #self._setConst()
        
    def readConf(self):
        conf = {}
        conf['url'] = self.config.configSectionMap('url')['api']
        conf['user'] = self.config.configSectionMap('user')['name']
        conf['password'] = self.config.configSectionMap('user')['pass']
        conf['headers'] = {'content-type':'application/json', 'accept':'application/json'}
        return conf
    
    def _setConst(self):
        for key in self.config.configSectionMap('const'):
            val = self.config.configSectionMap('const')[key]
            if val.isdigit(): val = int(val)
            elif val.replace('.','',1).isdigit(): val = float(val)
            elif val.lower() in ('true','false'): val = bool(val)
            setattr(self, key.upper(), val)    
            
    #def __setattr__(self, *_):
    #    pass

    
class LogWrap(object):
    #simple ligfile time stamp decorator 
    @classmethod
    def timediff(cls,func=None, prefix=''):
        msg = 'TIME {} {}'.format(prefix,func.__name__)        
        if func is None:
            return partial(cls.timediff)

        @wraps(func)
        def wrapper(*args, **kwargs):
            t1 = time.time()
            res = func(*args, **kwargs)
            tdif = time.time()-t1
            aimslog.info(msg+' {}'.format(tdif))
            return res
        return wrapper
    
class IterEnum(object):
    index = 0
    reverse = {}
    def __iter__(self): return self
    def next(self):
        res = None
        try: res = self.reverse[self.index]
        except: raise StopIteration
        #self.index = (self.index + 1) % len(self.reverse)
        self.index += 1
        return res    

    
class Enumeration(object):
    @staticmethod
    def enum(*seq, **named):
        #http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
        enums = dict( zip([s for s in seq],range(len(seq))) ,**named)
        reverse = dict((value, key) for key, value in enums.iteritems())
        
        enums['reverse'] = reverse 
        enums['__iter__'] = IterEnum.__iter__
        enums['next'] = IterEnum.next
        enums['index'] = 0
        return type('Enum', (IterEnum,), enums)


class InvalidEnumerationType(Exception): pass



FeedType = Enumeration.enum('FEATURES','CHANGEFEED','RESOLUTIONFEED')
EntityType = Enumeration.enum('ADDRESS','GROUPS')

#address changefeed action
ActionType = Enumeration.enum('ADD','RETIRE','UPDATE')

#resolutionfeed approval action
ApprovalType = Enumeration.enum('ACCEPT',  'DECLINE', 'UPDATE')
ApprovalType.LABEL =           ('Accepted','Declined','Under Review')
ApprovalType.HTTP =            ('POST',    'POST',    'PUT')

#group changefeed action
GroupActionType = Enumeration.enum('REPLACE','UPDATE','SUBMIT','CLOSE','ADD', 'REMOVE','ADDRESS')
GroupActionType.PATH =            ('replace','',      'sumbit','close','add', 'remove','address','')
GroupActionType.HTTP =            ('POST',   'PUT',   'POST',  'POST', 'POST','POST',  'GET')


   
