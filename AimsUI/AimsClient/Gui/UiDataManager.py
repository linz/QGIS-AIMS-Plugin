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
    """ 
    Handle all interaction between the UI and Data Manager.
    Also stores data as formatted for the UI 

    @param QObject: inherits from QObject Class
    @type QObject: QObject
    """

    rDataChangedSignal = pyqtSignal()
    fDataChangedSignal = pyqtSignal()
    
    #logging 
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    def __init__(self, iface, controller):
        """ 
        Initialise the UI Data Manager 

        @param iface: QgisInterface Abstract base class defining interfaces exposed by QgisApp  
        @type iface: Qgisinterface Object
        @param controller: instance of the plugins controller
        @type  controller: AimsUI.AimsClient.Gui.Controller
        """

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
        self.fDataChangedSignal.connect(self._controller.fDataChanged)
        
    def startDM(self):
        """
        Start running the DM observer thread and Listener
        (of the DM observer) thread when the plugin is enabled 
        """
        
        self.dm = DataManager()
        # common data obj
        self.DMData = DMData()           
        dmObserver = DMObserver(self.DMData, self.dm)
                
        listener = Listener(self.DMData)
        self.connect(listener, SIGNAL('dataChanged'), self.dataUpdated)
        #### Start Threads
        listener.start()
        dmObserver.start()
        uilog.info('dm started')
        
    def killDm(self):
        """
        Close DataManager at plugin unload
        """
        
        self.dm.close()
    
    ### Observer Methods ###
    def register(self, observer):
        """
        Listeners of the UIDataManager to regiester themselves to this method
        
        @param observer: listerning class
        @type  observer: AIMS class objects wishing to listen
        """

        self._observers.append(observer)

    @pyqtSlot()
    def dataUpdated(self, data, feedType = FEEDS['AR']):
        """
        Slot communicated to when Review data changed. Updates review layer and table data

        @param data: list of AIMS objects related for feed (as communicated in param feedtype)
        @type  data: list
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        """
        
        uilog.info("Signal Recieved")
        if data is None: return 
        self.setData(data,feedType)
        for observer in self._observers:
            observer.notify(feedType)

    def exlopdeGroup(self):
        """
        key groups agianst the group id and groups of single features against each group
        resultant format == 
            {(groupId, groupObj): {addId: addObj, addId: addObj}, (gro...}} 
        """

        gDict = {}
        for gId, gFeats in self.data[FEEDS['GR']].items():
            fDict = {}
            for gFeat in gFeats.meta._entities:
                fDict[gFeat._changeId]=gFeat
            gDict[(gId, gFeats)]=fDict
        self.data[FEEDS['GR']] = gDict
    
    def idProperty(self, feedtype):
        """
        Returns the property that the each object 
        should derive its reference id from  

        @return: Reference to which id should be used to reference each feedtype  
        @rtype: string
        """
        
        if feedtype == FEEDS['AF']: return '_components_addressId'
        if feedtype == FEEDS['AR']: return '_changeId'
        if feedtype == FEEDS['GR']: return '_changeGroupId'
        
    def keyData(self, listofFeatures, feedtype):
        """ Key Data from Data Manager

        @param dataRefresh: list of AIMS objects related for feed (as communicated in param feedtype)
        @type  dataRefresh: list
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        """

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
        # redundant? now straight to keyData?
        """ 
        Method receives new data from the data manager via the UIDM
        observer pattern and then starts the data update process        

        @param dataRefresh: list of AIMS objects related for feed (as communicated in param feedtype)
        @type  dataRefresh: list
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        """  
             
        self.keyData(dataRefresh, FeedType)

    def updateRdata(self, respFeature, feedType):
        """
        Between dm threaded interval data deliveries, temp
        AIMS review objects are created or render irrelevant 
        by user actions. This method updates the main data (self._data)
        to reflect these changes. 
        
        @param respFeature: Aims Address object
        @type  respFeature: AIMSDataManager.Address
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        """
        # remove from data
        if respFeature._queueStatus in ('Declined', 'Accepted'):
            del self.data[FEEDS['AR']][respFeature._changeId]
        else:                                
            # add to data 
            self.data[FEEDS['AR']][respFeature._changeId] = respFeature
            #uilog.info('new AR record with changeid: {}'.format(respFeature._changeId))
        self.rDataChangedSignal.emit()
        
    def updateFdata(self, respFeature):
        """
        Between dm threaded interval data deliveries, temp
        AIMS feature objects are created or render irrelevant 
        by user actions. This method updates the main data (self._data)
        to reflect these changes.

        @param respFeature: Aims Address object
        @type  respFeature: AIMSDataManager.Address
        """
        
        # responses do not have a 'full number'
        # as it is required for labeling it is set here
        respFeature.setFullAddressNumber(respFeature.getFullNumber())
        
        self.data[FEEDS['AF']][respFeature._components_addressId] = respFeature
        self.fDataChangedSignal.emit()
    
    def updateGdata(self, respFeature):
        groupKey = self.matchGroupKey(respFeature._changeGroupId)
        self.data[FEEDS['GR']][groupKey][respFeature._changeId] = respFeature
        
    def matchGroupKey(self, groupId):
        for groupKey in self.data.get(FEEDS['GR']).keys():
            if groupId in groupKey:
                return groupKey
    
    def setBbox(self, sw, ne):
        """
        Intermediate method, passes
        bboxes from layer manager to the DM
        
        @param sw: (x ,y)
        @type  sw: tuple
        @param ne: (x ,y)
        @type  ne: tuple         
        """
        #logging
        uilog.info('*** BBOX ***   New bbox passed to dm.setbb')
        self.dm.setbb(sw, ne) 
        uilog.info('*** BBOX ***   Bbox set')
    
    def reviewData(self):
        """
        Returns current group review data 

        @return: Dictionary of group formatted review data
        @rtype: dictionary
        """

        return self.data.get(FEEDS['AR'])
    
    def groupReviewData(self):
        ''' return (single and group) review data '''
        return self.data.get(FEEDS['GR'])
        
    def combinedReviewData(self):
        """ 
        De-nests group review data and combines with standard
        review data, Returning a complete "Review Data" set 
        
        @return: Flat dictionary of review items
        @rtype: dictionary
        """

        groupData = self.groupReviewData()
        addData = self.reviewData()
        
        combinedData = {}
        combinedData.update(addData)
        if not groupData: return addData 
        for k ,v in groupData.items():
            combinedData.update(v)
        return combinedData
        
    def featureData(self):
        """
        Returns feature data
        
        return: Dict of aims features {featureID: address obj,...}
        rtype: dictionary
        """
        return self.data.get(FEEDS['AF'])
    
    # --- DM convenience methods---
    
    def addAddress(self, feature, respId = None):
        """
        Passes an new AIMS Feature to DataManager 
        to add the feature to the AIM system

        @param feature: Aims Address object
        @type  feature: AIMSDataManager.Address
        @param respId: id used to match response 
        @type  respId: integer 
        """


        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'addAddress'))
        self.dm.addAddress(feature, respId)
        
    def retireAddress(self, feature, respId = None):
        """
        Passes an AIMS Feature to DataManager for retirement

        @param feature: Aims Address object
        @type  feature: AIMSDataManager.Address
        @param respId: id used to match response 
        @type  respId: integer 
        """


        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'retireAddress'))
        self.dm.retireAddress(feature, respId)
        
    def updateAddress(self, feature, respId = None):
        """
        Passes an AIMS Feature to the DataManager to 
        update a published feature

        @param feature: Aims Address object
        @type  feature: AIMSDataManager.Address
        @param respId: id used to match response 
        @type  respId: integer 
        """

        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'updateAddress'))
        self.dm.updateAddress(feature, respId)        

    def decline(self, feature, feedType, respId = None):
        """
        Passes an AIMS Feature to the DataManager 
        to decline a review item

        @param feature: Aims Address object
        @type  feature: AIMSDataManager.Address
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        @param respId: id used to match response 
        @type  respId: integer 
        """

        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'declineAddress'))
        if feedType == FEEDS['AR']:
            self.dm.declineAddress(feature, respId)
        else:
            self.dm.declineGroup(feature, respId)
    
    def accept(self, feature, feedType, respId = None):
        """
        Passes an AIMS Feature to the DataManager 
        to accept a review item

        @param feature: Aims Address object
        @type  feature: AIMSDataManager.Address
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        @param respId: id used to match response 
        @type  respId: integer 
        """
        
        if respId:
            uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'acceptAddress'))
            if feedType == FEEDS['AR']:
                self.dm.acceptAddress(feature, respId)
            else:
                self.dm.acceptGroup(feature, respId)
    
    def repairAddress(self, feature, respId = None):
        """
        Passes an updated AIMS Review Feature to the DataManager to
        be updated on the review feed

        @param feature: Aims Address object
        @type  feature: AIMSDataManager.Address
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        @param respId: id used to match response 
        @type  respId: integer 
        """
        
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'repairAddress'))
        self.dm.repairAddress(feature, respId)
    
    def supplementAddress(self, feature, reqid=None): 
        """
        Retrieve properties missing on the feature feed from 
        the last relevant resolution feed feature
        
        @param feature: Feature feed item that require supplement data
        @type  feature: AIMSDataManager.Address
        @param respId: id used to match response 
        @type  respId: integer 
        """
        
        self.dm.supplementAddress(feature, reqid)
    
    #--- Groups DM Methods ---
    
    def repairGroup(self, feature, respId = None):
        """
        Passes an updated AIMS Review Feature to the DataManager
        to be updated on the review feed

        @param feature: Aims Address object
        @type  feature: AIMSDataManager.Address
        @param respId: id used to match response 
        @type  respId: integer 
        """
        
        uilog.info('obj with respId: {0} passed to convenience method "{1}" '.format(respId, 'repairAddress'))
        self.dm.repairGroup(feature, respId)
        
# Lineage Related - ON HOLD
#     def openGroup(self):
#         self.dm.replaceGroup()
#         
#     def updateGroup(self):
#         self.dm.updateGroup()        
#         
#     def submitGroup(self):
#         self.dm.submitGroup()
#         
#     def closeGroup(self):
#         self.dm.closeGroup()  
#     
#     def addGroup(self):
#         self.dm.addGroup()
#     
#     def removeGroup(self):
#         self.dm.removeGroup()
#         
    def response (self, feedtype = None):
        """
        Returns DataMAnager response for a specific feedtype

        @param feedType: Type of AIMS feed
        @type feedType: AIMSDataManager.FeatureFactory.FeedRef

        @return: tuple of AIMSDataManager.Address
        @rtype: tuple
        """

        return self.dm.response(feedtype)
    
    def isNested(self, feat, prop):
        """
        Test if the class object has said nested entity

        @param feat: Group object
        @type  feat: AIMSDataManager.Address
        @param prop: address property
        @type  prop: string 
        """

        try: 
            return hasattr(getattr(getattr(feat, 'meta'), '_entities')[0],prop)
        except: 
            return False
        
    def nestedEntities(self, feat, prop):
        """
        Returns property from nested object

        @param feat: Group object
        @type  feat: AIMSDataManager.Address
        @param prop: address property
        @type  prop: string

        @return: AIMSDataManager.Address property
        @rtype: AIMSDataManager.Address property
        """
        
        return getattr(getattr(getattr(feat, 'meta'), '_entities')[0],prop)  

    def flatEntities(self, feat, prop):
        """
        Returns property from flat object

        @param feat: Group object
        @type  feat: AIMSDataManager.Address
        @param prop: address property
        @type  prop: string

        @return: AIMSDataManager.Address property
        @rtype: AIMSDataManager.Address property
        """

        return getattr(feat,prop)  
    
    def fullRoad(self, feat, feedtype):
        """ 
        Compiles a full road name 'label' for the UI 

        @param feat: Group object
        @type  feat: AIMSDataManager.Address
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef

        @return: Individual road components concatenated
        @rtype: string
        """

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
        """
        Returns data formatted for the group table model 

        @param obj: Group object
        @type  obj: AIMSDataManager.Group.GroupResolution
        @param groupProperties: list of properties required to format table data
        @type  groupProperties: list

        @return: return list reperesting a group entity. 
                Formatted:  ['changeGroupId', 'groupType', 'workflow_sourceOrganisation', 
                            'submitterUserName', 'submittedDate']
        @rtype: list
        """

        groupValues = []   
        for prop in groupProperties:            
            if hasattr(obj, prop):
                if getattr(obj, prop) != None:
                    groupValues.append(getattr(obj, prop))
                    #continue
            else: groupValues.append('')
        return groupValues
    
    def iterFeatProps(self, feat, featProperties, feedtype):
        """ 
        Iterate over AIMS class objects, Return those
        relevant to the parent model (that related to the feedtype)
        
        @param feat: Address object
        @type  feat: AIMSDataManager.Address
        @param featProperties: List of properties required to format table data
        @type  featProperties: list
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef

        @return: List of properties as formatted for relevant data model
        @rtype: list
        """
        
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
        """
        Returns data formatted for the feature table model 

        @param feature: Aims Address object
        @type  feature: dictionary
        @param featProperties: List of Address Properties required format Feature Table Data
        @type  featProperties: list
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        
        @return: List representing on row of feature table data 
        @rtype: list 
        """
        
        if feedtype == FEEDS['AR']:
            return self.iterFeatProps(feat, featProperties, feedtype)
        else:
            fValuesList = [] # AR
            for f in feat.values():                             
                fValues = self.iterFeatProps(f, featProperties, feedtype)
                fValuesList.append(fValues)
            return fValuesList   
 
    def addClassProps(self, feedtype):
        """
        Properties required to format Group and Feature data for the respective table models
        
        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef

        @return: Tuple of properties required to format the data related to the feedtype 
        @rtype: tuple
        """

        prop = {'AR':{'kProperties' : ['_changeId', '_changeType', '_workflow_sourceOrganisation', '_workflow_submitterUserName', '_workflow_submittedDate'],
                     'vProperties'  : ['_components_lifecycle', '_components_townCity' , '_components_suburbLocality']},
               'GR':{'kProperties'  : ['_changeGroupId', '_groupType', '_workflow_sourceOrganisation', '_submitterUserName', '_submittedDate'],
                     'vProperties'  : ['_components_lifecycle', '_components_townCity' , '_components_suburbLocality']}}
        
        if feedtype == FEEDS['AR']:
            return (prop['AR']['kProperties'],prop['AR']['vProperties'])
        return (prop['GR']['kProperties'],prop['AR']['vProperties'])

    def formatTableData(self, feedtypes):
        """
        Returns review data as formatted for the review data model 

        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef

        @return: data formated for feature table model
        @rtype: dictionary
        """
        
        fData = {}
        for feedtype in feedtypes:
            if self.data[feedtype]:
                props = self.addClassProps(feedtype)
                kProperties = props[0] 
                vProperties = props[1] 
                for k, v in self.data.get(feedtype).items():
                    if feedtype == FEEDS['AR']:
                        if v._queueStatus in  ('Declined', 'Accepted'):
                            continue
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
        """
        Returns a AIMS Address object that matches the object key

        @param feedType: Type of AIMS API feed
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        @param objkey: Feautre id
        @type  objkey: integer     
        """

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
        """
        Returns aims feautre object as per supplied data key(s)

        @param currentGroup: Current group key (groupId, changeType)
        @type  currentGroup: tuple
        @param currentFeatureKey: Current Feautre id
        @type  currentFeatureKey: integer

        @return: Address object
        @rtype: AIMSDataManager.Address
        """
        
        if currentGroup[1] not in ('Add', 'Update', 'Retire' ):
            for group in self.data.get(FEEDS['GR']).values():
                if group.has_key(currentFeatureKey):
                    return group[currentFeatureKey]
        else: 
            return self.data.get(FEEDS['AR']).get(currentFeatureKey)
    
    def reviewItemCoords(self, currentGroup, currentFeatureKey):
        """
        Returns the coords of a review obj

        @param currentGroup: Current group key (groupId, changeType)
        @type  currentGroup: tuple
        @param currentFeatureKey: Current Feautre id
        @type  currentFeatureKey: integer

        @return: list [x,y]
        @rtype: list
        """
        
        obj = self.currentReviewFeature(currentGroup, currentFeatureKey)
        #if not obj: return#temp
        if obj._changeType not in ('Update', 'Add') and not obj.meta.requestId:
            pos = obj.meta.entities[0].getAddressPositions()[0]._position_coordinates 
        else:
            pos = obj.getAddressPositions()[0]._position_coordinates
        return pos

    
class Listener(QThread):
    """ 
    Listener that checks for new data in the 
    common data store (DMData()) at defined intervals
    """

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
        """
        Compare the data as stored in the DMData object.
        If the is change update the UIDatamanager data
        """

        for k , v in self.data.items():
            if v and self.previousData[k] != v:
                self.emit(SIGNAL('dataChanged'), v, k) # failing as a new object is created for same obj in dm. Need new compare method
        self.previousData = self.data                   # probably comparing (add_id & version)
    
    def run(self):
        """
        Check for change on the DMData data
        """
        
        while True:
            self.data = self.DMData.getData()     
            self.compareData()
            QThread.sleep(1)

class DMData(object):
    """
    Common data object that is updated by the observer
    and read by the listener
    """

    def __init__(self):
        self.adrRes = None
        self.grpRes = None
        self.adrFea = None
        self.adrCha = None    
        self.grpCha = None
    
    def getData(self): 
        """
        Returns 

        @return: Dictionary {FeedType: data, ...}
        @rtype: dictionary
        """
        
        return { FEEDS['AR']:self.adrRes,
                FEEDS['GR']:self.grpRes,
                FEEDS['AF']:self.adrFea
                }
    
class DMObserver(QThread):
    """
    Observer registered with the DataManager
    """
    
    def __init__(self, DMData, dm):
        super(DMObserver, self).__init__()
        self.DMData = DMData
        self.dm = dm
        self.feedData = {FEEDS['GR']: 'grpRes' ,FEEDS['AR']: 'adrRes', 
                         FEEDS['AF']: 'adrFea', FEEDS['GC']: 'grpCha', FEEDS['AC']: 'adrCha'}
        
    def run (self):
        """
        Register the DMObserver with the DataManager
        """
        
        self.dm.registermain(self) 
               
    def observe(self,observable,*args,**kwargs):
        """
        Method Notified by DataManager when DataManager data has changed

        @param observable: Type of AIMS API feed
        @type  observable: AIMSDataManager.FeatureFactory.FeedRef
        @param args: tuple of data for relevant feed
        @type  args: tuple
        """
  
        fType = args[0]
        data = args[1]
        
        uilog.info('*** NOTIFY ***     Notify A[{}]'.format(observable))
        setattr(self.DMData, self.feedData.get(fType),data)
     