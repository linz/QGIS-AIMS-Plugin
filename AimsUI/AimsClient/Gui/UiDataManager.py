'''
Created on 11/02/2016

@author: splanzer
'''
from AIMSDataManager.DataManager import DataManager
from AIMSDataManager.AimsLogging import Logger
from AIMSDataManager.AimsUtility import FeedType
from PyQt4.QtCore import *
from qgis.core import QgsRectangle
import time

uilog = None

class UiDataManager(QObject):
    #dataChangedSignal = pyqtSignal()  <-- cannot have a non terminating program while testing
    #logging 
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    def __init__(self, iface, controller=None):
        QObject.__init__(self)
        self.dm = DataManager()
        #self.featData = []
        #self.resData = []
        self.dm.register(self)
        self.uptdFData = None
        self.uptdRData = None
        self.feedNum = 9
        self.data = {0:[],1:[],2:[]}
        
    #def returnData(self): < -- redundant?
    #    return self.data
        
    def keyData(self, listofAddresses, feedtype):
        if listofAddresses:
            li = []
            id = '_components_addressId' if feedtype == 0 else '_changeId'
            li = dict((getattr(x, id), x) for x in listofAddresses)
            self.data[feedtype] = li  

    def setData(self, dataRefresh, FeedType):        
        self.keyData(dataRefresh, FeedType)
        #self.dataChangedSignal.emit()
    
    '''
    @pyqtSlot()  <-- cannot have a non terminating program while testing
    def dataChanged(self):
        print self.data    
        print self.dm.refresh()  
    '''
    
    def notify(self,observable,args,kwargs):
        self.uptdData = kwargs
        self.feedNum = args
        
    def refresh(self, feedType):
        uilog.info('awaitng "notify" from observer for feedtype: {0}'.format(feedType))
        self.uptdData = []
        self.feedNum = 9            
        for i in range(0,16):
            time.sleep(1)
            if feedType == self.feedNum and self.uptdData :
                self.setData(self.uptdData, feedType)
                break
        #logging
        if i != 16:
            uilog.info('retrieved new data (feedType: {0}) via observer after {1} seconds '.format(feedType, i))
        else: 
            uilog.info('no new data retrieved via observer after {0} seconds '.format(i))
            
    def setBbox(self, sw, ne):
        self.dm.setbb(sw ,ne) 
        #logging
        uilog.info('new bbox passed to dm.setbb')

    def featureData(self):
        ''' update data and return AIMS features '''
        #self.newDataFlag = False
        self.refresh(0)
        try:
            return self.data.get(0)
        except: 
            return None
         
#     def reviewData(self):
#         ''' update data and return Review Items '''
#         self.refresh(2)
#         try:
#             return self.data.get(2)
#         except: 
#             return None
        
        # Temp 
        #data = self.dm.pull()
        #self.setData(data[2], 2)
        
    def restartDm(self, feedType):
        uilog.info('request sent to restart feed: {0}'.format(feedType))
        self.dm.restart(feedType)
    
    def addAddress(self, feature, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'addAddress'))
        self.dm.addAddress(feature, respId)
        
    def retireAddress(self, feature, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'retireAddress'))
        self.dm.retireAddress(feature, respId)
        
    def updateAddress(self, feature, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'updateAddress'))
        self.dm.updateAddress(feature, respId)        

    def decline(self, feature, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'declineAddress'))
        self.dm.declineAddress(feature, respId)
    
    def accept(self, feature, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'acceptAddress'))
        self.dm.acceptAddress(feature, respId)
    
    def repairAddress(self, feature, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'repairAddress'))
        self.dm.repairAddress(feature, respId)
        
    def response (self, feedtype = None):
        return self.dm.response(feedtype)

    def fullNumber(self, k):  # this has now been added to the review class. TO BE REMOVED
        ''' compiles a full number 'label' for the UI '''
        fullNumber = ''
        obj = self.data.get(2).get(k) # retrieve the object to display
        if hasattr(obj, '_components_unitValue'): fullNumber+=str(getattr(obj,'_components_unitValue'))+'/'
        if hasattr(obj, '_components_addressNumber'): fullNumber+=str(getattr(obj,'_components_addressNumber')) 
        if hasattr(obj, '_components_addressNumberHigh'): fullNumber+= ('-'+str(getattr(obj,'_components_addressNumberHigh')))
        if hasattr(obj, '_components_addressNumberSuffix'): fullNumber+=str(getattr(obj,'_components_addressNumberSuffix'))        
        return fullNumber 
        
    def fullRoad(self, k):
        ''' compiles a full road name 'label' for the UI '''
        fullRoad = ''
        obj = self.data.get(2).get(k) # retrieve object# currently only handling review
        for prop in ['_components_roadPrefix', '_components_roadName', '_components_roadType', '_components_roadSuffix',
                      '_components_waterRoute', '_components_waterName']:
            if hasattr(obj, prop): fullRoad+=str(getattr(obj,prop))+' '
        return fullRoad 
       
    def changeData(self):
        pass

    def reviewTableData(self):
        ''' review data as formatted for the review data model '''
        #restart feed
        self.restartDm(FeedType.RESOLUTIONFEED)
        self.refresh(2) 

        rData = {}
        kProperties = ['_changeId', '_changeType', '_workflow_sourceOrganisation', '_workflow_submitterUserName', '_workflow_submittedDate']
        vProperties = ['_components_lifecycle', '_components_townCity' , '_components_suburbLocality']
        try:
            for k, obj in self.data.get(2).items():
                reviewValues = []
                reviewKeys = []
                reviewValues.extend([self.fullNumber(k), self.fullRoad(k)]) # address and road labels
                for prop in vProperties:
                    if hasattr(obj, prop):
                        reviewValues.append(getattr(obj, prop))
                    else: reviewValues.append('')
                for prop in kProperties:
                    if hasattr(obj, prop):
                        reviewKeys.append(getattr(obj, prop))
                    else: reviewKeys.append('')
                rData[tuple(reviewKeys)] = [reviewValues]
            return rData
        except: # there is no data
            return {('','', '', '', ''): [['', '', '', '', '']]}
    
    def singleFeatureObj(self, objkey):
        return self.data.get(0).get(objkey)
    def singleReviewObj(self, objkey):
        return self.data.get(2).get(objkey)
    
    def reviewItemCoords(self, objkey):
        obj = self.data.get(2).get(objkey)
        #currently only storing one position, Hence the '[0]'
        return obj._addressedObject_addressPositions[0]._position_coordinates

