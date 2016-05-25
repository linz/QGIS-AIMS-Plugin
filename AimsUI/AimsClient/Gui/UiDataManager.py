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
from qgis.gui import QgsMessageBar
import time
import threading

from AIMSDataManager.DataManager import DataManager
from AIMSDataManager.AimsLogging import Logger
from AIMSDataManager.AimsUtility import FeedType, FeedRef, FeatureType, FEEDS
from AimsUI.AimsClient.Gui.ReviewQueueWidget import ReviewQueueWidget
# Dev only - debugging
try:
    import sys
    sys.path.append('/opt/eclipse/plugins/org.python.pydev_4.4.0.201510052309/pysrc')
    from pydevd import settrace, GetGlobalDebugger
    settrace()

except:
    pass

uilog = None
    
class UiDataManager(QObject):
    rDataChangedSignal = pyqtSignal()
    
    #logging 
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    def __init__(self, iface, controller):
        QObject.__init__(self)
        self._controller = controller
        self._iface = iface
        self.dm = None
        self._observers = []
        self.data = {   FEEDS['AF']:{},
                        FEEDS['AC']:{},
                        FEEDS['AR']:{},
                        FEEDS['GC']:{},
                        FEEDS['GR']:{}
                    }

        self.groups = ('Replace', 'AddLineage', 'ParcelReferenceData') # more to come...
        
        self.rDataChangedSignal.connect(self._controller.rDataChanged)
        
        
    def startDM(self):
        ''' start running 2x threads
            1: a DM observer thread
            2: a Listener of the DM observer '''
        
        self.dm = DataManager()
        # common data obj
        self.DMData = DMData()           
        dmObserver = DMObserver(self.DMData, self.dm)
                
        listener = Listener(self.DMData)
        self.connect(listener, SIGNAL('dataChanged'), self.dataUpdated)#, Qt.QueuedConnection)
        #### Start Threads
        listener.start()
        dmObserver.start()

    def killDm(self):
        self.dm.close()
    
    ### Observer Methods ###
    def register(self, observer):
        self._observers.append(observer)
#         
#     def observe(self,observable,*args,**kwargs):
#         uilog.info('*** NOTIFY ***     Notify A[{}]'.format(observable))
#         self.setData(args,observable)
#         if observable in (FEEDS['GR'] ,FEEDS['AR'], FEEDS['AF']):
#             for observer in self._observers:            
#                 observer.notify(observable) # can filter further reviewqueue does not need AF
#    
    @pyqtSlot()
    def dataUpdated(self, data, feedType = FEEDS['AR']):
        ''' review data changed, update review layer and table '''
        uilog.info("Signal Recieved")
        if data is None: return 
        self.setData(data,feedType)
        for observer in self._observers:
            observer.notify(feedType)

    def exlopdeGroup(self):
        ''' key groups and single addresses against each group
            resultant format == 
            {(groupId, groupObj): {addId: addObj, addId: addObj}, (gro...}} '''
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
        ''' create dict whereby each aims obj is a
            value and its Id as defined by the IdProperyy
            method its Key '''
        if listofFeatures:
            li = []
            keyId = self.idProperty(feedtype)
            li = dict((getattr(feat, keyId), feat) for feat in listofFeatures)
            self.data[feedtype] = li
            # [GroupKey:{AdKey:}]            
        if feedtype == FEEDS['GR']:
            # key group objects
            self.exlopdeGroup()

    def setData(self, dataRefresh, FeedType):
        ''' method receives new data from the
            data manger via its observer pattern
            and then starts the data update process '''        
        self.keyData(dataRefresh, FeedType)

    def updateRdata(self, respFeature, feedType):
        ''' Between dm threaded interval data deliveries, temp
            AIMS review objects are created or render irrelevant 
            by user actions. This method updates the main data (self._data)
            to reflect these chnages. '''
        # remove from data
        if respFeature._queueStatus in ('Declined', 'Accepted'):
            del self.data[FEEDS['AR']][respFeature._changeId]
        else:                                
            # add to data 
            self.data[FEEDS['AR']][respFeature._changeId] = respFeature
            #uilog.info('new AR record with changeid: {}'.format(respFeature._changeId))
        self.rDataChangedSignal.emit()
        
    def updateFdata(self, respFeature):
        ''' Between dm threaded interval data deliveries, temp
            AIMS feature objects are created or render irrelevant 
            by user actions. This method updates the main data (self._data)
            to reflect these changes. '''

        self.data[FEEDS['AF']][respFeature._components_addressId] = respFeature
    
    def updateGdata(self, respFeature):
        groupKey = self.matchGroupKey(respFeature._changeGroupId)
        self.data[FEEDS['GR']][groupKey][respFeature._changeId] = respFeature
        
    def matchGroupKey(self, groupId):
        for groupKey in self.data.get(FEEDS['GR']).keys():
            if groupId in groupKey:
                return groupKey
    
    def setBbox(self, sw, ne):
        ''' intermediate method, passes
            bboxes from layer manager to the DM
        '''
        #logging
        uilog.info('*** BBOX ***   New bbox passed to dm.setbb')
        self.dm.setbb(sw, ne) 
        uilog.info('*** BBOX ***   Bbox set')
    
    def reviewData(self):
        ''' return (single and group) review data '''
        return self.data.get(FEEDS['AR'])
    
    def groupReviewData(self):
        ''' return (single and group) review data '''
        return self.data.get(FEEDS['GR'])
        
    def combinedReviewData(self):
        ''' de-nests group review data and combines
            with address review data '''

        groupData = self.groupReviewData()
        addData = self.reviewData()
        
        combinedData = {}
        combinedData.update(addData)
        if not groupData: return addData 
        for k ,v in groupData.items():
            combinedData.update(v)
        return combinedData
        
    def featureData(self):
        ''' update data and return AIMS features '''
        return self.data.get(FEEDS['AF'])
    
    # --- DM convenience methods---
    
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
    
    def repairGroup(self, feature, respId = None):
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'repairAddress'))
        self.dm.repairGroup(feature, respId)
    
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
    
    def isNested(self, feat, prop):
        ''' test is the class object has said nested entity ''' 
        try: 
            return hasattr(getattr(getattr(feat, 'meta'), '_entities')[0],prop)
        except: 
            return False
        
    def nestedEntities(self, feat, prop):
        ''' get at and return the nested entity properties '''
        return getattr(getattr(getattr(feat, 'meta'), '_entities')[0],prop)  

    def flatEntities(self, feat, prop):
        ''' get at and return the nested entity properties '''
        return getattr(feat,prop)  
    
    def fullRoad(self, feat, feedtype):
        ''' compiles a full road name 'label' for the UI '''
        fullRoad = ''
        for prop in ['_components_roadPrefix', '_components_roadName', '_components_roadType', '_components_roadSuffix',
                      '_components_waterRoute', '_components_waterName']:
            addProp = None    
            # Groups have nested entities
            if feat._changeType in self.groups:
                if self.isNested(feat, prop):
                    addProp = self.nestedEntities(feat, prop) 
            # retired have nested entities except when the retired 
            # feature is derived from an response object    
            elif feat._changeType == 'Retire':
                #if self.isNested(feat, prop):
                if not feat.meta.requestId: 
                    if hasattr(getattr(getattr(feat, 'meta'), '_entities')[0],prop):
                        addProp = self.nestedEntities(feat, prop) 
                elif hasattr(feat,prop):  
                    addProp = self.flatEntities(feat, prop) 
            # else we have an Add or update of whoms 
            # properties are flat
            elif hasattr(feat,prop): 
                addProp = self.flatEntities(feat, prop) 
            else: continue                    
            if addProp != None: fullRoad+=addProp+' '
        return fullRoad 

    def formatGroupTableData(self, obj, groupProperties):
        ''' return data formatted for the group table model '''
        groupValues = []   
        for prop in groupProperties:            
            if hasattr(obj, prop):
                if getattr(obj, prop) != None:
                    groupValues.append(getattr(obj, prop))
                    #continue
            else: groupValues.append('')
        return groupValues
    
    def iterFeatProps(self, feat, featProperties, feedtype):
        ''' run over AIMS class objects, Return those
            relevant to the parent model'''
        fValues = []
        fValues.extend([getattr(feat, '_changeId'),feat.getFullNumber(), self.fullRoad(feat ,feedtype)]) # address and road labels 
        for prop in featProperties:
            # Groups have nested entities                                  
            if feat._changeType in self.groups and self.isNested(feat, prop):
                    fValues.append(self.nestedEntities(feat, prop))      
            # retired have nested entities except when the retired 
            # feature is derived from an response object    
            elif feat._changeType == 'Retire':
                if self.isNested(feat, prop):
                    fValues.append(self.nestedEntities(feat, prop))
                elif hasattr(feat,prop): 
                    fValues.append(self.flatEntities(feat, prop)) 
            # else we have an Add or update of whoms 
            # properties are flat
            elif hasattr(feat,prop):
                fValues.append(self.flatEntities(feat, prop)) #!= None:
            else: fValues.append('')
        return fValues
    
    def formatFeatureTableData(self, feat, featProperties, feedtype):
        ''' return data formatted for the feature table model '''
        if feedtype == FEEDS['AR']:
            return self.iterFeatProps(feat, featProperties, feedtype)
        else:
            fValuesList = [] # AR
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
            if self.data[feedtype]:
                props = self.addClassProps(feedtype)
                kProperties = props[0] 
                vProperties = props[1] 
                for k, v in self.data.get(feedtype).items():
                    featureValues = [] 
                    if feedtype == FEEDS['AR']:
                        groupValues = self.formatGroupTableData(v,kProperties) 
                        featureValues = [self.formatFeatureTableData(v,vProperties, feedtype)]
                    else: #GR
                        featureValues = []                    
                        groupValues = self.formatGroupTableData(k[1],kProperties) 
                        featureValues = self.formatFeatureTableData(v,vProperties, feedtype)
                    fData[tuple(groupValues)] = featureValues
        if fData:
            return fData # need to test a return == {}    
    
    def singleFeatureObj(self, objkey):
        ''' returns an AIMS object when its key is supplied '''
        return self.data.get(FEEDS['AF'])[(objkey)]
    
    def singleReviewObj(self, feedtype, objkey):
        ''' return the value of which is an aims review
            obj (group and single) for the keyed data '''
        if feedtype == FEEDS['AR']:
            return self.data.get(feedtype).get(objkey)
        elif feedtype == FEEDS['GR']:
            for k in self.data.get(feedtype):
                if objkey == k[0]: return k[1]
                 
    def currentReviewFeature(self, currentGroup, currentFeatureKey):
        ''' return aims feautre object as per supplied data key(s) '''
        if currentGroup[1] in ('Replace', 'AddLineage', 'ParcelReferenceData' ):
            for group in self.data.get(FEEDS['GR']).values():
                if group.has_key(currentFeatureKey):
                    return group[currentFeatureKey]
        else: 
            return self.data.get(FEEDS['AR']).get(currentFeatureKey)
    
    def reviewItemCoords(self, currentGroup, currentFeatureKey):
        ''' return the coords of a review obj'''
        obj = self.currentReviewFeature(currentGroup, currentFeatureKey)
        if not obj: return#temp
        if obj._changeType not in ('Update', 'Add'):
            pos = obj.meta.entities[0].getAddressPositions()[0]._position_coordinates 
        else:
            pos = obj.getAddressPositions()[0]._position_coordinates

        return pos

    
class Listener(QThread):
    #listenerSignal = pyqtSignal()
    def __init__(self, DMData):
        super(Listener, self).__init__()
        self.DMData = DMData
        self.data = {FEEDS['AF']:[],
                FEEDS['AC']:[],
                FEEDS['AR']:[],
                FEEDS['GC']:[],
                FEEDS['GR']:[]
                }
        self.previousData = {FEEDS['AF']:[],
                FEEDS['AC']:[],
                FEEDS['AR']:[],
                FEEDS['GC']:[],
                FEEDS['GR']:[]
                }
    
    def compareData(self):
        for k , v in self.data.items():
            if v and self.previousData[k] != v:
                self.emit(SIGNAL('dataChanged'), v, k) # failing as a new object is created for same obj in dm. Need new compare method
        self.previousData = self.data                   # probably comparing (add_id & version)
    
    def run(self):
        while True:
            self.data = self.DMData.getData()     
            self.compareData()
            QThread.sleep(1)

class DMData(object):
    def __init__(self):

        self.adrRes = None
        self.grpRes = None
        self.adrFea = None
        self.adrCha = None    
        self.grpCha = None
    
    def getData(self): 

        return { FEEDS['AR']:self.adrRes,
                FEEDS['GR']:self.grpRes,
                FEEDS['AF']:self.adrFea
                }
    
class DMObserver(QThread):
    def __init__(self, DMData, dm):
        super(DMObserver, self).__init__()
        self.DMData = DMData
        self.dm = dm
        self.feedData = {FEEDS['GR']: 'grpRes' ,FEEDS['AR']: 'adrRes', 
                         FEEDS['AF']: 'adrFea', FEEDS['GC']: 'grpCha', FEEDS['AC']: 'adrCha'}
        
    def run (self):
        self.dm.registermain(self) 
               
    def observe(self,observable,*args,**kwargs):        
        uilog.info('*** NOTIFY ***     Notify A[{}]'.format(observable))
        setattr(self.DMData, self.feedData.get(observable),args[0])
     