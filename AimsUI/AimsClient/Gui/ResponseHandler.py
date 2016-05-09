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
from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *
import time

from AIMSDataManager.AddressFactory import AddressFactory
from AIMSDataManager.Address import Entity, FeedType
from AIMSDataManager.AimsUtility import FEEDS

from AIMSDataManager.AimsLogging import Logger

uilog = None

class ResponseHandler(object):
    
    # logging
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    def __init__(self, iface, uidm):
        self._iface = iface
        self.uidm = uidm
        self.afar= {ft:AddressFactory.getInstance(FEEDS['AR']) for ft in FeedType.reverse}
        self.afaf= {ft:AddressFactory.getInstance(FEEDS['AF']) for ft in FeedType.reverse} # new method to cast

    def updateData(self, respObj , feedType, action):# rather than action could monitor _queueStatus
        if hasattr(respObj, '_changeGroupId'):
            respObj = self.afar[FeedType.RESOLUTIONFEED].cast(respObj)  
            self.uidm.updateGdata(respObj)
        elif feedType == FEEDS['AC']:
            respObj = self.afar[FeedType.RESOLUTIONFEED].cast(respObj)
            self.uidm.updateRdata(respObj, feedType)
        if feedType == FEEDS['AR']:# and action == 'accept':
            respObj = self.afaf[FeedType.FEATURES].cast(respObj)
            self.uidm.updateRdata(respObj, feedType)
            if action == 'accept':
                self.uidm.updateFdata(respObj)
        return True
     
    def displayWarnings (self, warnings):
        ''' raise warning to the user '''
        message = ''
        for warning in warnings:
            message += u'\u2022 {}\n'.format(warning)
        QMessageBox.warning(self._iface.mainWindow(),"AIMS Warnings", message)
     
     
    def matchResp (self, response, respId, feedType, i, action):
        ''' compile a list of warnings that are at the "Reject" level.
        If warnings for the matching respID, proceed to update data'''
        
        warnings = []
        for resp in response:
            if resp.meta._requestId == respId:  
                #logging
                uilog.info(' *** DATA ***    response received from DM for respId: {0} of type: {1} after {2} seconds'.format(respId, feedType, i))    
                # hack to meet first testing release -- Review
                if resp.meta._errors['critical']:
                    self.displayWarnings(resp.meta.errors['critical'])
                    return True
                if resp.meta._errors['error'] and resp._queueStatus == 'Accepted':
                    self.displayWarnings(resp.meta.errors['error'])
                    return True
        
                else:                   
                # else captured resp and no critical warnings
                # precede to update self._data
                    self.updateData(resp, feedType, action)
                    return True
                    # return resp     
                         
    def handleResp(self, respId, feedType, action = None):
        ''' test for a response in the response
            queue with the relevant repId'''
        for i in range(0,20):
            time.sleep(1)
            resp = self.uidm.response(feedType)
            if resp and resp != (None,): # found and processed response
                if self.matchResp(resp, respId, feedType, i, action):
                    return                                                 
        #logging 
        uilog.info(' *** DATA ***    Time Out ({0} seconds): No response received from DM for respId: {1} of feedtype: {2}'.format(i, respId, feedType))    
    
           