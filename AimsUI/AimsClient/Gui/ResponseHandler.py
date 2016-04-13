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

from AIMSDataManager.AimsLogging import Logger

from AIMSDataManager.AimsUtility import FEEDS

uilog = None

class ResponseHandler(object):
    
    # logging
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    def __init__(self, iface, uidm):
        self._iface = iface
        self.uidm = uidm
        self.af = {ft:AddressFactory.getInstance(FEEDS['AR']) for ft in FeedType.reverse}

    def updateData(self, respObj , feedType):
        if feedType == FEEDS['AC']:
            respObj = self.af[FeedType.RESOLUTIONFEED].cast(respObj)
        self.uidm.updateRdata(respObj, feedType)
        return True
     
    def displayWarnings (self, warnings):
        ''' raise warning to the user '''
        message = ''
        for warning in warnings:
            message += u'\u2022 {}\n'.format(warning)
        QMessageBox.warning(self._iface.mainWindow(),"Create Address Point", message)
     
     
    def matchResp (self, response, respId, feedType, i):
        ''' compile a list of warnings that are at the "Reject" level.
        If warnings for the matching respID, proceed to update data'''
        
        warnings = []
        for resp in response:
            if resp.meta._requestId == respId:  
                #logging
                uilog.info(' *** DATA ***    response received from DM for respId: {0} of type: {1} after {2} seconds'.format(respId, feedType, i))    
                
                resp.meta._entities
                for warning in resp.meta._entities:
                    if warning['properties']['severity'] in ('Reject', 'critical'):
                        warnings.append(warning['properties']['description'])
                # failed accepts return the bew formatted warning
                if hasattr(resp, '_properties_message'): warnings.append(resp._properties_message)
                if warnings:
                    # feature not created in aims via API
                    self.displayWarnings(warnings)
                    return True
                # else captured resp and no critical warnings
                self.updateData(resp, feedType)
                return True
                    # return resp
     
     
    def handleResp(self, respId, feedType):
        ''' test for a response in the response
            queue with the relevant repId'''
        for i in range(0,12):
            time.sleep(1)
            resp = self.uidm.response(feedType)
            if resp: # found and processed response
                if self.matchResp(resp, respId, feedType, i):
                    return

                                                  
        #logging 
        uilog.info(' *** DATA ***    Time Out ({0} seconds): No response received from DM for respId: {1} of feedtype: {2}'.format(i, respId, feedType))    
    
           
        