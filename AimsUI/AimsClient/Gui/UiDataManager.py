'''
Created on 11/02/2016

@author: splanzer
'''
from AIMSDataManager.DataManager import DataManager
from PyQt4.QtCore import *
from qgis.core import QgsRectangle
import time


class UiDataManager(QObject):
    #dataChangedSignal = pyqtSignal()  <-- cannot have a non terminating program while testing
    
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
        
    def returnData(self):
        return self.data
        
    def keyData(self, listofAddresses, feedtype):
        if listofAddresses:
            li = []
            id = '_components_addressId' if feedtype == 0 else '_changeId'
            li = dict((getattr(x, id), x) for x in listofAddresses)
            self.data[feedtype] = li  

    def setdata(self, dataRefresh, FeedType):        
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
        self.uptdData = []
        self.feedNum = 9
            
        for i in range(0,15):
            time.sleep(1)
            if feedType == self.feedNum and self.uptdData :
                self.setdata(self.uptdData, feedType)
                break


    def setBbox(self, sw, ne):
        self.dm.setbb(sw ,ne)   

    def featureData(self):
        ''' update data and return AIMS features '''
        #self.newDataFlag = False
        self.refresh(0)
        try:
            return self.data.get(0)
        except: 
            return None
        
    def reviewData(self):
        ''' update data and return Review Items '''
        self.refresh(2)
        try:
            return self.data.get(2)
        except: 
            return None
    
    def restartDm(self, feedType):
        self.dm.restart(feedType)
    
    def addAddress(self, feature):
        self.dm.addAddress(feature)
        
    def retireAddress(self, feature):
        self.dm.retireAddress(feature)
        
    def updateAddress(self, feature, respId = None):
        self.dm.updateAddress(feature, respId)        

    def decline(self, feature):
        self.dm.declineAddress(feature)
    
    def accept(self, feature):
        self.dm.acceptAddress(feature)
        r = self.dm.response()
        r = self.dm.response()
        r = self.dm.response()
        
    
    def repairAddress(self, feature):
        self.dm.repairAddress(feature)

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

