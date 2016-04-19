
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
from PyQt4.QtCore import *
from qgis.core import QgsRectangle
import time

from AIMSDataManager.DataManager import DataManager
from AIMSDataManager.AimsLogging import Logger
from AIMSDataManager.AimsUtility import FeedType, FeedRef, FeatureType, FEEDS
from AimsUI.AimsClient.Gui.ReviewQueueWidget import ReviewQueueWidget

uilog = None
    
class UiDataManager(QObject):
    rDataChangedSignal = pyqtSignal()

    #logging 
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    def __init__(self, iface, controller):
        QObject.__init__(self)
        self._controller = controller
        with DataManager() as self.dm:
            self.dm.registermain(self)
        self.uptdFData = None
        self.refreshSuccess = False
        self._observers = []
        self.data = {   FEEDS['AF']:{},
                        FEEDS['AC']:{},
                        FEEDS['AR']:{},
                        FEEDS['GC']:{},
                        FEEDS['GR']:{}
                    }
        
        self.rDataChangedSignal.connect(self._controller.rDataChanged)
    
    ### Observer Methods ###
    def register(self, observer):
        self._observers.append(observer)
         
    def observe(self,observable,*args,**kwargs):
        uilog.info('*** NOTIFY ***     Notify A[{}]'.format(observable))
        self.setData(args,observable)
        if observable in (FEEDS['GR'] ,FEEDS['AR'], FEEDS['AF']):
            for observer in self._observers:            
                observer.notify(observable) # can filter further reviewqueue does not need AF
            
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
            li = dict((getattr(feat, keyId), feat) for feat in listofFeatures[0])
            self.data[feedtype] = li
            # [GroupKey:{AdKey:}]            
        if feedtype == FEEDS['GR']:
            # key group objects
            self.exlopdeGroup()
    
    def keyDatum(self, aimsFeature):
        pass

    def setData(self, dataRefresh, FeedType):        
        self.keyData(dataRefresh, FeedType)

    def updateRdata(self, respFeature, feedType):
        # remove from data
        if respFeature._queueStatus in ('Declined', 'Accepted'):
            del self.data[FEEDS['AR']][respFeature._changeId]
        else:                                
            # add to data 
            self.data[FEEDS['AR']][respFeature._changeId] = respFeature
        self.rDataChangedSignal.emit()
        
    def updateFdata(self, respFeature):
        # this is pretty ineffcient building the entire layer at the same time
        # ideally i should add an "add" feature and update "moves" and "updates"
        self.data[FEEDS['AF']][respFeature._components_addressId] = respFeature
        self._controller._layerManager.getAimsFeatures() # temp, will to switch to signal

    def setBbox(self, sw, ne):
         #need to ignore -185.7732089700440667,-188.0621082638667190 : 187.9902399660660706,106.1221897458003127
        #logging
        uilog.info('*** BBOX ***   New bbox passed to dm.setbb')
        self.dm.setbb(sw, ne) 
        uilog.info('*** BBOX ***   Bbox set')
    
    def reviewData(self):
        ''' return (single and group) review data '''
        return self.data.get(FEEDS['AR'])

    def featureData(self):
        ''' update data and return AIMS features '''
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

    def decline(self, feature, feedType, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'declineAddress'))
        if feedType == FEEDS['AR']:
            self.dm.declineAddress(feature, respId)
        else:
            self.dm.declineGroup(feature, respId)
    
    def accept(self, feature, feedType, respId = None):
        if respId:
            uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'acceptAddress'))
            if feedType == FEEDS['AR']:
                self.dm.acceptAddress(feature, respId)
            else:
                self.dm.acceptGroup(feature, respId)
    
    def repairAddress(self, feature, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'repairAddress'))
        self.dm.repairAddress(feature, respId)
    
    #--- Groups DM Methods ---
    def openGroup(self):
        self.dm.replaceGroup()
        
    def updateGroup(self):
        self.dm.updateGroup()        
        
    def submitGroup(self):
        self.dm.submitGroup()
        
    def closeGroup(self):
        self.dm.closeGroup()  
    
    def addGroup(self):
        self.dm.addGroup()
    
    def removeGroup(self):
        self.dm.removeGroup()
        
    def response (self, feedtype = None):
        return self.dm.response(feedtype)

    def fullRoad(self, k, feedtype):
        ''' compiles a full road name 'label' for the UI '''
        fullRoad = ''
        if feedtype == FEEDS['AR']:
            obj = k            
        else: obj = self.data.get(feedtype).get(k) # retrieve object# currently only handling review
        for prop in ['_components_roadPrefix', '_components_roadName', '_components_roadType', '_components_roadSuffix',
                      '_components_waterRoute', '_components_waterName']:
            if hasattr(obj, prop): 
                if getattr(obj,prop) != None: fullRoad+=str(getattr(obj,prop))+' '
        return fullRoad 

    def formatGroupTableData(self, obj, groupProperties):
        groupValues = []   
        for prop in groupProperties:            
            if hasattr(obj, prop):
                if getattr(obj, prop) != None:
                    groupValues.append(getattr(obj, prop))
                    continue
            else: groupValues.append('')
        return groupValues
    
    def iterFeatProps(self, feat, featProperties, feedtype):
        fValues = []
        fValues.extend([getattr(feat, '_changeId'),feat.getFullNumber(), self.fullRoad(feat ,feedtype)]) # address and road labels 
        for prop in featProperties:                                        
            if hasattr(feat, prop):
                if getattr(feat, prop) != None:
                    fValues.append(getattr(feat, prop))
                    continue
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

    def formatTableData(self, feedtypes):
        ''' return review data formatted for the review data model '''
        fData = {}
        for feedtype in feedtypes:
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
        ''' return the value of which is an aims review
            obj (group and single) for the keyed data '''
        if feedtype == FEEDS['AR']:
            return self.data.get(feedtype).get(objkey)
        elif feedtype == FEEDS['GR']:
            for k in self.data.get(feedtype):
                if objkey == k[0]: return k[1]
                #need to handle key errors?
                # raise, 'Where did you get that key from?'
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
        try: # temp try / except untill retire obj is complete
            return obj._addressedObject_addressPositions[0]._position_coordinates
        except: return None