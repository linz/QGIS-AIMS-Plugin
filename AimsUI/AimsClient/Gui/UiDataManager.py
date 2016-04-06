'''
Created on 11/02/2016

@author: splanzer
'''
from AIMSDataManager.DataManager import DataManager
from AIMSDataManager.AimsLogging import Logger
from AIMSDataManager.AimsUtility import FeedType, FeedRef, FeatureType, FEEDS
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
        self.uptdFeedRef = None
        self.refreshSuccess = False
        self.data = {   FEEDS['AF']:[],
                        FEEDS['AC']:[],
                        FEEDS['AR']:[],
                        FEEDS['GC']:[],
                        FEEDS['GR']:[]
                    }
                                
    def exlopdeGroup(self):
        gDict = {}
        for gId, gFeats in self.data[FEEDS['GR']].items():
            fDict = {}
            for gFeat in gFeats.meta._entities:
                fDict[gFeat._changeId]=gFeat
            gDict[(gId, gFeats)]=fDict
        self.data[FEEDS['GR']] = gDict
    
    def idProperty(self, feedtype):
        ''' returns the property that the each object 
            should derive its reference id from  '''
        
        if feedtype == FEEDS['AF']: return '_components_addressId'
        if feedtype == FEEDS['AR']: return '_changeId'
        if feedtype == FEEDS['GR']: return '_changeGroupId'
        
    def keyData(self, listofFeatures, feedtype):
        if listofFeatures: # redundant? 
            li = []
            keyId = self.idProperty(feedtype)
            li = dict((getattr(feat, keyId), feat) for feat in listofFeatures)
            self.data[feedtype] = li
            # [GroupKey:{AdKey:}]
            
        if feedtype == FEEDS['GR']:
            # key group objects
           self.exlopdeGroup()

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
        uilog.info('*** NOTIFY ***     Notify A[{}]'.format(args))
        self.uptdData = kwargs
        self.uptdFeedRef = args
        
    def refresh(self, feedType):
        self.refreshSuccess = False
        uilog.info('*** NOTIFY ***    awaitng "notify" from observer for feedtype: {0}'.format(feedType))
        self.uptdData = []
        self.uptdFeedRef = None            
        for i in range(0,16):            
            #if self.uptdFeedRef:
            if feedType == self.uptdFeedRef and self.uptdData:
                self.setData(self.uptdData, feedType)
                self.refreshSuccess = True
                break
            else: time.sleep(1)
        # else it has failed to get data and the old data remains - 
        # should it remove data or keep the stale data?
        
        #logging
        if i != 15:
            uilog.info('*** DATA ***   Retrieved new data (feedType: {0}) via observer after {1} seconds '.format(feedType, i))
        else: 
            uilog.info('*** DATA ***   No new data retrieved via observer after {0} seconds '.format(i))
            
    def setBbox(self, sw, ne):
        self.dm.setbb(sw ,ne) 
        #logging
        uilog.info('new bbox passed to dm.setbb')

    def featureData(self):
        ''' update data and return AIMS features '''
        self.restartDm(FEEDS['AF'])
        self.refresh(FEEDS['AF']) 
        return self.data.get(FEEDS['AF'])
        
    def restartDm(self, feedType):
        uilog.info('*** RESTART ***    request sent to restart feed: {0}'.format(feedType))
        self.dm.restart(feedType)
        uilog.info('*** RESTART ***    {0} restarted'.format(feedType))
    
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

    def fullNumber(self, k, feedtype):  # this has now been added to the review class. TO BE REMOVED
        ''' compiles a full number 'label' for the UI '''
        fullNumber = ''
        if feedtype == FEEDS['AR']:
            obj = k            
        else: obj = self.data.get(feedtype).get(k) # retrieve object# currently only handling review
        if hasattr(obj, '_components_unitValue'): fullNumber+=str(getattr(obj,'_components_unitValue'))+'/'
        if hasattr(obj, '_components_addressNumber'): fullNumber+=str(getattr(obj,'_components_addressNumber')) 
        if hasattr(obj, '_components_addressNumberHigh'): fullNumber+= ('-'+str(getattr(obj,'_components_addressNumberHigh')))
        if hasattr(obj, '_components_addressNumberSuffix'): fullNumber+=str(getattr(obj,'_components_addressNumberSuffix'))        
        return fullNumber 
        
    def fullRoad(self, k, feedtype):
        ''' compiles a full road name 'label' for the UI '''
        fullRoad = ''
        if feedtype == FEEDS['AR']:
            obj = k            
        else: obj = self.data.get(feedtype).get(k) # retrieve object# currently only handling review
        for prop in ['_components_roadPrefix', '_components_roadName', '_components_roadType', '_components_roadSuffix',
                      '_components_waterRoute', '_components_waterName']:
            if hasattr(obj, prop): fullRoad+=str(getattr(obj,prop))+' '
        return fullRoad 
       
    def changeData(self):
        pass

    def formatGroupTableData(self, obj, groupProperties):
        groupValues = []   
        for prop in groupProperties:            
            if hasattr(obj, prop):
                groupValues.append(getattr(obj, prop))
            else: groupValues.append('')
        return groupValues
    
    def iterFeatProps(self, feat, featProperties, feedtype):
        fValues = []
        fValues.extend([getattr(feat, '_changeId'),self.fullNumber(feat, feedtype), self.fullRoad(feat ,feedtype)]) # address and road labels 
        for prop in featProperties:                                        
            if hasattr(feat, prop):
                fValues.append(getattr(feat, prop))
            else: fValues.append('')
        return fValues
    
    def formatFeatureTableData(self, feat, featProperties, feedtype):
        if feedtype == FEEDS['AR']:
            return self.iterFeatProps(feat, featProperties, feedtype)
        else:
            fValuesList = []
            for f in feat.values():                             
                fValues = self.iterFeatProps(f, featProperties, feedtype)
                fValuesList.append(fValues)
            return fValuesList   
 
    def addClassProps(self, feedtype):
        prop = {'AR':{'kProperties' : ['_changeId', '_changeType', '_workflow_sourceOrganisation', '_workflow_submitterUserName', '_workflow_submittedDate'],
                     'vProperties'  : ['_components_lifecycle', '_components_townCity' , '_components_suburbLocality']},
               'GR':{'kProperties'  : ['_changeGroupId', '_groupType', '_workflow_sourceOrganisation', '_submitterUserName', '_submittedDate'],
                     'vProperties'  : ['_components_lifecycle', '_components_townCity' , '_components_suburbLocality']}}
        
        if feedtype == FEEDS['AR']:
            return (prop['AR']['kProperties'],prop['AR']['vProperties'])
        return (prop['GR']['kProperties'],prop['AR']['vProperties'])
    
    def reviewTableData(self, feedtypes):
        ''' review data as formatted for the review data model '''
        fData = {}
        for feedtype in feedtypes:
           
            # Restart the DM  feed and catch the new data
            self.restartDm(feedtype)
            self.refresh(feedtype) 
            if self.refreshSuccess:  
                # turn this in to a dict and init it              
                props = self.addClassProps(feedtype)
                kProperties = props[0] 
                vProperties = props[1] 
                for k, v in self.data.get(feedtype).items():
                    featureValues = [] 
                    if feedtype == FEEDS['AR']:
                        groupValues = self.formatGroupTableData(v,kProperties) 
                        featureValues = [self.formatFeatureTableData(v,vProperties, feedtype)]
                    else:
                        featureValues = []                    
                        groupValues = self.formatGroupTableData(k[1],kProperties) 
                        featureValues = self.formatFeatureTableData(v,vProperties, feedtype)
                    fData[tuple(groupValues)] = featureValues
        if fData:
            return fData # need to test a return == {}    
    
    def singleFeatureObj(self, objkey):
        return self.data.get(FEEDS['AF'])[(objkey)]
    
    def singleReviewObj(self, feedtype, objkey):
        return self.data.get(feedtype).get(objkey)
    
    def currentReviewFeature(self, currentGroup, currentFeatureKey):
        ''' return aims feautre object as per supplied data key(s) '''
        if currentGroup[1] in ('Replace', 'AddLineage'):
            for group in self.data.get(FEEDS['GR']).values():
                if group.has_key(currentFeatureKey):
                    return group[currentFeatureKey]
        else: 
            return self.data.get(FEEDS['AR']).get(currentFeatureKey)
    
    def reviewItemCoords(self, currentGroup, currentFeatureKey):
        obj = self.currentReviewFeature(currentGroup, currentFeatureKey)
        #currently only storing one position, Hence the '[0]'
        return obj._addressedObject_addressPositions[0]._position_coordinates
