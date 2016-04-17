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

import threading

notify_lock = threading.RLock()
sync_lock = threading.RLock()

class Observable(threading.Thread):

    def __init__(self):        
        threading.Thread.__init__(self)
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)
    
    def notify(self, *args, **kwargs):
        '''Notify all registered listeners'''
        for observer in self._observers:
            with notify_lock:
                observer.observe(*args, **kwargs)
                
    def observe(self, *args, **kwargs):
        '''listen method called by notification, default calls in turm call notify but override this as needed'''
        self.notify(*args, **kwargs)