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
#upper limit on page number to request
PAGE_LIMIT = 1000
#time delay between thread checks to see if pooled page has returned (s) 
POOL_PAGE_CHECK_DELAY = 0.2
#time delay between thread checks to see if user action has returned a response (s) 
QUEUE_CHECK_DELAY = 1
#when backfilling pages guess start point to find last page in change feed
LAST_PAGE_GUESS = 100
#automatically inset warnings into resolution feed features. very slow, enable only if RF is small
ENABLE_RESOLUTION_FEED_WARNINGS = False
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

   
