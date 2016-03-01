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
THREAD_JOIN_TIMEOUT = 5
MAX_FEATURE_COUNT = 1000
PAGE_LIMIT = 1000
POOL_PAGE_CHECK_DELAY = 0.2
QUEUE_CHECK_DELAY = 1
LAST_PAGE_GUESS = 100
ENABLE_RESOLUTION_FEED_WARNINGS = False
LOCALADL = 'aimsdata'
SWZERO = (0.0, 0.0)
NEZERO = (0.0, 0.0)
SKIP_NULL = True
DEF_SEP = '_'

aimslog = Logger.setup()

def readConf():
    conf = {}
    config = ConfigReader()
    conf['url'] = config.configSectionMap('url')['api']
    conf['user'] = config.configSectionMap('user')['name']
    conf['password'] = config.configSectionMap('user')['pass']
    conf['headers'] = {'content-type':'application/json', 'accept':'application/json'}
    return conf


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
    def __iter__(self): return self
    def next(self):
        res = None
        try: res = self.reverse[self.index]
        except: raise StopIteration
        self.index += 1
        return res
    
class Enumeration():
    @staticmethod
    def enum(*seq, **named):
        #http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
        enums = dict( zip([s.split(':')[0] for s in seq],range(len(seq))) ,**named)
        alt = dict( zip([s.split(':')[1] for s in seq],range(len(seq))) ,**named) if all([s.find(':')+1 for s in seq]) else enums
        
        reverse = dict((value, key) for key, value in enums.iteritems())
        revalt = dict((value, key) for key, value in alt.iteritems())
        enums['reverse'] = reverse 
        enums['revalt'] = revalt  
      
        #enums['__iter__'] = IterEnum.__iter__
        #enums['next'] = IterEnum.next
        #enums['index'] = 0
        return type('Enum', (IterEnum,), enums)
        #monkeypatch instance#t2 = type('eenum',(t,), {'next':IterEnum.next})
        #return t

class InvalidEnumerationType(Exception): pass

ActionType = Enumeration.enum('ADD','RETIRE','UPDATE')
ApprovalType = Enumeration.enum('ACCEPT:Accepted','DECLINE:Declined','UPDATE:Under Review')
FeedType = Enumeration.enum('FEATURES','CHANGEFEED','RESOLUTIONFEED')
#RequestType = Enumeration.enum('BBOX','ADDRESS')

   
