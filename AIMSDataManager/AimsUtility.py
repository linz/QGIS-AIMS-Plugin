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


def readConf():
    conf = {}
    config = ConfigReader()
    conf['url'] = config.configSectionMap('url')['api']
    conf['user'] = config.configSectionMap('user')['name']
    conf['password'] = config.configSectionMap('user')['pass']
    conf['headers'] = {'content-type':'application/json', 'accept':'application/json'}
    return conf

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
    def enum(*sequential, **named):
        #http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
        enums = dict(zip(sequential, range(len(sequential))), **named)
        reverse = dict((value, key) for key, value in enums.iteritems())
        enums['reverse'] = reverse        
        #enums['__iter__'] = IterEnum.__iter__
        #enums['next'] = IterEnum.next
        #enums['index'] = 0
        return type('Enum', (IterEnum,), enums)
        #monkeypatch instance#t2 = type('eenum',(t,), {'next':IterEnum.next})
        #return t


        

ActionType = Enumeration.enum('ADD','RETIRE','UPDATE')
ApprovalType = Enumeration.enum('ACCEPT','DECLINE','UPDATE')
FeedType = Enumeration.enum('FEATURES','CHANGEFEED','RESOLUTIONFEED')
#RequestType = Enumeration.enum('BBOX','ADDRESS')

   
