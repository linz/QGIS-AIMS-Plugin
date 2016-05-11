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
import os
from AimsLogging import Logger

aimslog = Logger.setup()

class AimsException(Exception):
    def __init__(self,em,al=aimslog.error): al('ERR {} - {}'.format(type(self).__name__,em))
    
class InvalidEnumerationType(AimsException): pass

class Configuration(object):
    def __init__(self): 
        self.config = ConfigReader()
        
    def readConf(self):
        conf = {}
        conf['url'] = self.config.configSectionMap('url')['api']
        conf['org'] = self.config.configSectionMap('user')['org']
        conf['user'] = self.config.configSectionMap('user')['name']
        conf['password'] = self.config.configSectionMap('user')['pass']
        conf['headers'] = {'content-type':'application/json', 'accept':'application/json'}
        return conf

    
class LogWrap(object):
    #simple ligfile time stamp decorator 
    @classmethod
    def timediff(cls,func=None, prefix=''):
        msg = 'FUNC TIME {} {} (wrap)'.format(prefix,func)
        if func is None:
            return partial(cls.timediff)

        @wraps(func)
        def wrapper(*args, **kwargs):
            t1 = time.time()
            res = func(*args, **kwargs)
            tdif = time.time()-t1
            aimslog.debug(msg+' {}s'.format(tdif))
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

class FeedRef(object):
    '''Convenience container class holding Entity/Feed type key'''
    def __init__(self,arg1,arg2=None):
        if arg2:
            self._et = arg1
            self._ft = arg2
        else:
            self._et = arg1[0]
            self._ft = arg1[1]
        
    def __str__(self,trunc=3):
        return '{}{}'.format(FeatureType.reverse[self._et].title()[:trunc],FeedType.reverse[self._ft].title()[:trunc]) 
    
    def __hash__(self):
        return hash((self._et, self._ft))

    def __eq__(self, other):
        return isinstance(other,FeedRef) and self._et==other._et and self._ft==other._ft    

    def __ne__(self, other):
        return not(self == other)
    
    @property
    def k(self): return '{}.{}'.format(FeatureType.reverse[self._et].lower(),FeedType.reverse[self._ft].lower()) 
    @property
    def et(self): return self._et
    @et.setter
    def et(self,et): pass#self._et = et
    @property
    def ft(self): return self._ft
    @ft.setter
    def ft(self,ft): pass#self._ft = ft


FeedType = Enumeration.enum('FEATURES','CHANGEFEED','RESOLUTIONFEED','ADMIN')
FeatureType = Enumeration.enum('ADDRESS','GROUPS','USERS')

#address changefeed action
ActionType = Enumeration.enum('ADD', 'RETIRE','UPDATE')
ActionType.PATH =            ('add', 'retire','')
ActionType.HTTP =            ('POST','POST',  'PUT')

#resolutionfeed approval action
ApprovalType = Enumeration.enum('ACCEPT',  'DECLINE', 'UPDATE')
ApprovalType.LABEL =           ('Accepted','Declined','Under Review')
ApprovalType.PATH =            ('accept',  'decline', '')
ApprovalType.HTTP =            ('POST',    'POST',    'PUT')

#group changefeed action
GroupActionType = Enumeration.enum('REPLACE','UPDATE','SUBMIT','CLOSE','ADD', 'REMOVE','ADDRESS')
GroupActionType.PATH =            ('replace','',      'sumbit','close','add', 'remove','address','')
GroupActionType.HTTP =            ('POST',   'PUT',   'POST',  'POST', 'POST','POST',  'GET')

#group resolutionfeed approval
GroupApprovalType = Enumeration.enum('ACCEPT',  'DECLINE', 'ADDRESS', 'UPDATE')
GroupApprovalType.LABEL =           ('Accepted','Declined','Information','Under Review')
GroupApprovalType.PATH =            ('accept',  'decline', 'address', '')
GroupApprovalType.HTTP =            ('POST',    'POST',    'GET',     'PUT')

#user admin action
UserActionType = Enumeration.enum('ADD','DELETE','UPDATE')
UserActionType.PATH =            ('','','')
UserActionType.HTTP =            ('POST','DELETE','PUT')

FEED0 = {'UA':FeedRef((FeatureType.USERS,FeedType.ADMIN))}
FEEDS = {'AF':FeedRef((FeatureType.ADDRESS,FeedType.FEATURES)),'AC':FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED)),
         'AR':FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)),'GC':FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)),
         'GR':FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED))}
FEEDS.update(FEED0) 
FIRST = {'AC':FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED)),'AR':FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)),
         'GC':FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)), 'GR':FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED))}


   
