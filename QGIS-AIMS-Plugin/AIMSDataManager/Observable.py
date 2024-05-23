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
from qgis.PyQt.QtCore import QThread

notify_lock = threading.RLock()
sync_lock = threading.RLock()

from AIMSDataManager.AimsLogging import Logger

aimslog = None

#TODO Split into observer and observed subclasses and multiply inherit depending on roles

class Observable(QThread):
    '''Class implementing interface for the observer pattern.
    Differs from regular pattern as it splits notify() into notify() and observe() functions'''

    global aimslog
    aimslog = Logger.setup()

    def __init__(self): 
        '''Initialise new observable class explicitly including threading stop function'''
        super(Observable,self).__init__()     
        self._observers = []

    def register(self, observer):
        '''Register a listener object with the observable
        @param observer: Observer object 
        '''
        self._observers.append(observer)
        
    def deregister(self,observer):
        '''De-Register a listener object from the observable
        @param observer: Observer object 
        '''
        if observer in self._observers: self._observers.remove(observer)
    
    def notify(self, *args, **kwargs):
        '''Notify all registered listeners.
        @param *args: Wrapped args
        @param **kwargs: Wrapped kwargs
        '''
        for observer in self._observers:
            with notify_lock:
                observer.observe(self,*args, **kwargs)
                
    def observe(self, observable, *args, **kwargs):
        '''Listen method called by notification, default calls in turm call notify but override this as needed.
        @param observable: Instance of the calling class
        @param *args: Wrapped args
        @param **kwargs: Wrapped kwargs
        '''
        if not self.stopped():
            self.notify(*args, **kwargs)