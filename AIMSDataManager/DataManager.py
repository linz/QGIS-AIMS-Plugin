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

import os
import sys
import Queue
import pickle
import time
from Address import Address, AddressChange, AddressResolution,Position
from FeatureFactory import FeatureFactory
#from DataUpdater import DataUpdater
from DataSync import DataSync,DataSyncFeatures,DataSyncFeeds,DataSyncAdmin
from datetime import datetime as DT
from AimsUtility import FeedRef,ActionType,ApprovalType,GroupActionType,GroupApprovalType,UserActionType,FeatureType,FeedType,PersistActionType,Configuration,FEED0,FEEDS,FIRST
from AimsUtility import AimsException
from AimsLogging import Logger
from Const import THREAD_JOIN_TIMEOUT,RES_PATH,LOCAL_ADL,SWZERO,NEZERO,NULL_PAGE_VALUE as NPV
from Observable import Observable

aimslog = None   
    
class DataManager(Observable):
    '''Initialises maintenance thread and provides queue accessors and request channels'''

    global aimslog
    aimslog = Logger.setup()
    
  
    def __init__(self,start=FIRST,initialise=False):
        '''Initialises DataManager initialising DataSync objects, setting up persistence and reading configuration.
        @param start: List of sync objects to be started (excluded FeatureFeed by default until BBOX defined
        @param initialise: Flag to signal initialisation of persisted objects
        @type initialise: Boolean
        '''
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}   
        super(DataManager,self).__init__()
        if start and hasattr(start,'__iter__'): self._start = start.values()
        self.persist = Persistence(initialise)
        self.conf = Configuration().readConf()
        self._initDS()
        
    def _initDS(self):
        '''Initialises all DataSync, Queue and timestamping containers and begin check process'''
        self.ioq = {etft:None for etft in FEEDS.values()}
        self.ds = {etft:None for etft in FEEDS.values()}
        self.stamp = {etft:time.time() for etft in FEEDS.values()}
        
        #init the g2+a2+a1 different feed threads
        self.dsr = {f:DataSyncFeeds for f in FIRST.values()}
        self.dsr[FeedRef((FeatureType.ADDRESS,FeedType.FEATURES))] = DataSyncFeatures
        #Users feed not included in DSR for Release1.0
        for etft in self._start: self._checkDS(etft)
            
    def startfeed(self,etft):
        '''Add a requested (FeedRef) thread to startup list and initialise 
        @param etft: FeedRef of requested thread
        @type etft: FeedRef
        '''
        if not etft in self._start: self._start.append(etft)
        self._checkDS(etft)
        
    #local override of observe
    def observe(self, observable, *args, **kwargs):
        '''Local override of observe chaining observe calls without notification
        @param observable: Instance of the class calling the notification
        @param *args: Wrapped args
        @param **kwargs: Wrapped kwargs
        '''
        if self.stopped():
            aimslog.warn('Attempt to call stopped DM listener {}'.format(self.getName()))
            return
        aimslog.info('DM Listen A[{}], K[{}] - {}'.format(args,kwargs,observable))
        args += (self._monitor(args[0]),)#observable),)
        #chained notify/listen calls
        if hasattr(self,'registered') and self.registered: 
            self.registered.observe(observable, *args, **kwargs)
        self._check()
        
    #Second register/observer method for main calling class
    def registermain(self,reg):
        '''Register "single" object as the main listener, intended for DataManager calling class.
        @param reg: Registered (main) object
        '''
        self.registered = reg if hasattr(reg, 'observe') else None
        
    def _checkDS(self,etft):
        '''Starts a sync thread unless its a address-features feed with a zero bbox
        @param etft: FeedRef of requested thread
        @type etft: FeedRef
        '''
        if (etft == FEEDS['AF'] and self.persist.coords['sw'] == SWZERO and self.persist.coords['ne'] == NEZERO):# or int(self.persist.tracker[etft]['threads'])==0:                
            self.ds[etft] = None
        else:
            self.ds[etft],self.ioq[etft] = self._spawnDS(etft,self.dsr[etft])
            if etft.ft != FeedType.FEATURES: self.register(self.ds[etft].drc)
            self.ds[etft].register(self)
            #HACK to start DRC even if feed thread count is zero. If changefeed isn't running we may still want to send requests to it
            if int(self.persist.tracker[etft]['threads'])>0:
                self.ds[etft].start()
            else:
                self.ds[etft].drc.start()
            
        
    def _spawnDS(self,etft,feedclass): 
        '''Spawn and return a new DS matching the etft 
        @param etft: FeedRef of requested thread
        @type etft: FeedRef
        @param feedclass: Alias of Sync setup function
        @type feedclass: DataSync class alias
        @return: (DataSync, {IOR Queues})
        '''
        ts = '{0:%y%m%d.%H%M%S}'.format(DT.now())
        params = ('DSF..{}.{ts}'.format(etft,ts=ts),etft,self.persist.tracker[etft],self.conf)
        #self.ioq[etft] = {n:Queue.Queue() for n in ('in','out','resp')}
        dq =  {n:Queue.Queue() for n in ('in','out','resp')}
        ds = feedclass(params,dq)
        ds.setup(self.persist.coords['sw'],self.persist.coords['ne'])
        ds.setDaemon(True)
        ds.setName('DS{}'.format(etft))
        return ds,dq    
    
    def _cullDS(self,etft):
        '''Remove temporary queue and ds instances, this does the anti spawn
        @param etft: FeedRef of thread to stop
        @type etft: FeedRef
        '''
        del self.ioq[etft]
        self.deregister(self.uads.drc)
        del self.uads
        
    def close(self):
        '''Shutdown, closing/stopping DataSync threads and persist current data'''
        for ds in self.ds.values():
            if ds: ds.close()
        self.persist.write()
        
    def _check(self):
        '''Safety method to check if a DataSync thread has crashed and restart it'''
        for etft in self._start:
            if self._confirmstart(etft):
                aimslog.warn('DS thread {} absent, starting'.format(etft))
                #del self.ds[etft]
                self._checkDS(etft)
                
    def _confirmstart(self,etft):    
        '''Simple test to determine whether thread should be started or not
        - Tests: Max thread count non zero AND thread is not already running
        @param etft: FeedRef of requested thread test
        @type etft: FeedRef
        ''' 
        return int(self.persist.tracker[etft]['threads'])>0 and not (self.ds.has_key(etft) and self.ds[etft] and self.ds[etft].isAlive())
    
    #Client Access
    def setbb(self,sw=None,ne=None):
        '''Reset the saved bounding box on the current DataManager which triggers a complete refresh of the features address data.
        - Tests whether provided coordinates are nonzero and dont match existing saved BBOX coordinates
        - Function attempts to gracefully kill previously running features thread during THREAD_JOIN_TIMEOUT period
        @param sw: South-West corner, coordinate value pair (optional)
        @type sw: List<Double>{2}
        @param ne: North-East corner, coordinate value pair (optional)
        @type ne: List<Double>{2}
        '''
        #TODO add move-threshold to prevent small moves triggering an update
        if self.persist.coords['sw'] != sw or self.persist.coords['ne'] != ne:
            #throw out the current features addresses
            etft = FEEDS['AF']#(FeatureType.ADDRESS,FeedType.FEATURES)
            self.persist.set(etft,None,pat=PersistActionType.INIT)
            #save the new coordinates
            self.persist.coords['sw'],self.persist.coords['ne'] = sw,ne
            #kill the old features thread
            if self.ds[etft] and self.ds[etft].isAlive():
                aimslog.info('Attempting Features Thread STOP')
                self.ds[etft].stop()
                self.ds[etft].join(THREAD_JOIN_TIMEOUT)
                #TODO investigate thread non-stopping issues
                if self.ds[etft].isAlive(): aimslog.warn('SetBB Features. ! Thread JOIN timeout')
            del self.ds[etft]
            #reinitialise a new features DataSync
            #self._initFeedDSChecker(etft)
            self.startfeed(etft)
    
    #@Deprecated     
    def restart(self,etft):
        '''I{DEPRECATED} Restart method provided for calling application to explicitly kill running feed threads. 
        This was required by the plugin application when in single thread mode to clear up contention issues but discouraged due to 
        unpredictable thread hanging problems.         
        @param etft: FeedRef of requested restart thread
        @type etft: FeedRef
        ''' 
        #NB UI feature request. 
        aimslog.warn('WARNING {} Thread Restart requested'.format(etft))
        if self.ds.has_key(etft) and self.ds[etft] and self.ds[etft].isAlive():
            self.ds[etft].stop() 
            self.ds[etft].join(THREAD_JOIN_TIMEOUT)
            if self.ds[etft].isAlive(): aimslog.warn('{} ! Thread JOIN timeout'.format(etft))
        #del self.ds[etft]
        elif not isinstance(etft,FeedRef):
            aimslog.error('Invalid FeedRef on STOP request')
        else:
            aimslog.warn('Requested thread {} does not exist')
        self._check()
        
    def pull(self,etft=None):
        '''Return copy of the current list of Address objects (ADL).
        @param etft: Optional feedref arg indicating which feature class to return
        @type etft: FeedRef
        @return: Dictionary<FeedRef,List<Address>>
        '''
        return self.persist.get(etft)  
        
    def _monitor(self,etft):
        '''Intermittent data saving function which checks a requested feed's out queue and puts any new items into the ADL
        @param etft: FeedRef of requested restart thread
        @type etft: FeedRef
        @return: Dictionary<FeedRef*,List<Address>>
        ''' 
        #for etft in self.ds:#FeedType.reverse:
        if self.ds[etft]:
            while not self.ioq[etft]['out'].empty():
                #because the queue isnt populated till all pages are loaded we can just swap out the ADL
                self.persist.set(etft,self.ioq[etft]['out'].get(),pat=PersistActionType.REPLACE)
                self.stamp[etft] = time.time()

        #self.persist.write()
        return self.persist.get(etft)
    
    def response(self,etft=FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED))):
        '''Returns any features lurking in the response queue
        - Response queue contains esponses to user generated requests
        @param etft: FeedRef of response thread. Default=Address/Resolution
        @type etft: FeedRef
        @return: Feature
        '''
        resp = ()
        delflag = False
        #while self.ioq.has_key((et,ft)) and not self.ioq[(et,ft)]['resp'].empty():
        while etft in FEEDS.values() and not self.ioq[etft]['resp'].empty():
            resp += (self.ioq[etft]['resp'].get(),)
            #don't delete the queue while we're still getting items from it, instead mark it for deletion
            if etft in FEED0.values(): delflag = True
        if delflag: self._cullDS(etft)
        return resp
    
    #--------------------------------------------------------------------------
      
    def _populateAddress(self,feature):
        '''Fill in any required+missing fields if a default value is known (in this case the configured user/org)
        @param feature: Address object to test and populate
        @type feature: Address
        @return: Address
        '''
        if not hasattr(feature,'_workflow_sourceUser') or not feature.getSourceUser(): feature.setSourceUser(self.conf['user'])
        if not hasattr(feature,'_workflow_sourceOrganisation') or not feature.getSourceOrganisation(): feature.setSourceOrganisation(self.conf['org'])
        return feature    
    
    def _populateGroup(self,feature):
        '''Fill in any required+missing fields if a default value is known (in this case the configured user/submitter)
        @param feature: Group object to test and populate
        @type feature: Group
        @return: Group
        '''
        if not hasattr(feature,'_workflow_sourceUser') or not feature.getSourceUser(): feature.setSourceUser(self.conf['user'])
        if not hasattr(feature,'_submitterUserName') or not feature.getSubmitterUserName(): feature.setSubmitterUserName(self.conf['user'])
        return feature
    
    # Convenience Methods 
    #---------------------------- 
    def addAddress(self,address,reqid=None):
        '''Convenience method to send/add an Address to the changefeed.
        @param address: Address object to add
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._addressAction(address,ActionType.ADD,reqid)      
    
    def retireAddress(self,address,reqid=None):        
        '''Convenience method to send/retire an Address from the changefeed.
        @param address: Address object to retire
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._addressAction(address,ActionType.RETIRE,reqid)
    
    def updateAddress(self,address,reqid=None):        
        '''Convenience method to send/update an Address on the changefeed.
        @param address: Address object to update
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._addressAction(address,ActionType.UPDATE,reqid)
        
    def _addressAction(self,address,at,reqid=None):
        '''Address action method performing address/action on the change feed
        @param address: Address object to update
        @type address: Address
        @param at: Action function to perform
        @type at: ActionType
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        if reqid: address.setRequestId(reqid)
        self._populateAddress(address).setChangeType(ActionType.reverse[at].title())
        self._queueAction(FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED)), at, address)
    #----------------------------
    def acceptAddress(self,address,reqid=None):        
        '''Convenience method to send/accept an Address on the resolutionfeed.
        @param address: Address object to accept
        @type address: Address
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._addressApprove(address,ApprovalType.ACCEPT,reqid)    

    def declineAddress(self,address,reqid=None):        
        '''Convenience method to send/decline an Address on the resolutionfeed.
        @param address: Address object to decline
        @type address: Address
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._addressApprove(address,ApprovalType.DECLINE,reqid)
    
    def repairAddress(self,address,reqid=None):        
        '''Convenience method to send/update an Address on the resolutionfeed.
        @param address: Address object to update
        @type address: Address
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._addressApprove(address,ApprovalType.UPDATE,reqid)     
        
    def supplementAddress(self,address,reqid=None):        
        '''Convenience method to fetch additional info on an Address from the resolutionfeed.
        @param address: Address object to update
        @type address: Address
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        #HACK. Since a feature address doesn't have a changeid (but its needed for the construction of a resolution feed
        #request) we substitute the changeId for the version number. This usefully also provides the final component of 
        #the request URL. Note also, approval requests include a payload but for this GET request it isn't needed.
        ###address.setChangeId(address.getVersion())
        ###self._addressApprove(address,ApprovalType.SUPPLEMENT,reqid) 
        
        #HACK (2). Set changeid to flag supplemental request
        address.setChangeId('supplemental{}'.format(address.getAddressId()))
        self._addressApprove(address,ApprovalType.SUPPLEMENT,reqid) 
        
        
        
    def _addressApprove(self,address,at,reqid=None):
        '''Address approval method performing address/approve actions on the resolution feed
        @param address: Address object to update
        @type address: Address
        @param at: Approval function to perform
        @type at: ApprovalType
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        if reqid: address.setRequestId(reqid)
        address.setQueueStatus(ApprovalType.LABEL[at].title())
        self._queueAction(FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)), at, address)
        
    #============================
    
    def acceptGroup(self,group,reqid=None):        
        '''Convenience method to send/accept a Group on the resolutionfeed.
        @param group: Group object to accept
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupApprove(group, GroupApprovalType.ACCEPT, reqid)
        
    def declineGroup(self,group,reqid=None):        
        '''Convenience method to send/decline a Group on the resolutionfeed.
        @param group: Group object to decline
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupApprove(group, GroupApprovalType.DECLINE, reqid) 
        
    def repairGroup(self,group,reqid=None):        
        '''Convenience method to send/update a Group on the resolutionfeed.
        @param group: Group object to update
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupApprove(group, GroupApprovalType.UPDATE, reqid)   
        
    def _groupApprove(self,group,gat,reqid=None):
        '''Group approval method performing group/approve actions on the resolution feed
        @param group: Group object to update
        @type group: Group
        @param gat: Group approval function to perform
        @type gat: GroupApprovalType
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        if reqid: group.setRequestId(reqid)
        group.setQueueStatus(GroupApprovalType.LABEL[gat].title())
        self._queueAction(FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED)),gat,group)
          
    #----------------------------
    def replaceGroup(self,group,reqid=None):        
        '''Convenience method to send/replace a Group on the changefeed.
        @param group: Group object to replace
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupAction(group, GroupActionType.REPLACE, reqid)       
        
    def updateGroup(self,group,reqid=None):        
        '''Convenience method to send/update a Group on the changefeed.
        @param group: Group object to update
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupAction(group, GroupActionType.UPDATE, reqid)       
        
    def submitGroup(self,group,reqid=None):        
        '''Convenience method to send/submit a Group to the changefeed.
        @param group: Group object to submit
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupAction(group, GroupActionType.SUBMIT, reqid)    
    
    def closeGroup(self,group,reqid=None):        
        '''Convenience method to send/close a Group on the changefeed.
        @param group: Group object to close
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupAction(group, GroupActionType.CLOSE, reqid)
        
    def addGroup(self,group,reqid=None):        
        '''Convenience method to send/add a Group to the changefeed.
        @param group: Group object to add
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupAction(group, GroupActionType.ADD, reqid)
             
    def removeGroup(self,group,reqid=None):        
        '''Convenience method to send/remove a Group from the changefeed.
        @param group: Group object to remove
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._groupAction(group, GroupActionType.REMOVE, reqid)        
  
    def _groupAction(self,group,gat,reqid=None):        
        '''Group action method performing group/actions on the change feed
        @param group: Group object to update
        @type group: Group
        @param gat: Group action function to perform
        @type gat: GroupActionType
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''        
        if reqid: group.setRequestId(reqid)
        self._populateGroup(group).setChangeType(GroupActionType.reverse[gat].title())
        self._queueAction(FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)),gat,group)
    
    #----------------------------
    
    def _queueAction(self,feedref,atype,aorg):
        '''Queue and notify'''
        self.ioq[feedref]['in'].put({atype:(aorg,)})
        self.notify(feedref)
    
    #----------------------------
    '''User actions are on-demand only and because they won't be run very often are set up and torn down on each use'''
    
    def addUser(self,user,reqid=None):        
        '''Convenience method to send/add a User to the adminfeed.
        @param user: User object to add
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._userAction(user, UserActionType.ADD, reqid)
        
    def removeUser(self,user,reqid=None):        
        '''Convenience method to send/remove a User from the adminfeed.
        @param user: User object to remove
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._userAction(user, UserActionType.DELETE, reqid)
            
    def updateUser(self,user,reqid=None):        
        '''Convenience method to send/update a User on the adminfeed.
        @param user: User object to update
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''
        self._userAction(user, UserActionType.UPDATE, reqid)       
    
    def _userAction(self,user,uat,reqid=None): 
        '''User action method performing user/action on the admin feed
        @param user: User object to update
        @type user: User
        @param uat: User action function to perform
        @type uat: UserActionType
        @param reqid: User supplied reference value, used to coordinate asynchronous requests/responses
        @type reqid: Integer
        '''       
        if reqid: user.setRequestId(reqid)
        #self._populateUser(user).setChangeType(UserActionType.reverse[uat].title())
        #self._queueAction(FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)),gat,group)
        etft = FeedRef((FeatureType.USERS,FeedType.ADMIN))
        self.uads,self.ioq[etft] = self._spawnDS(etft,DataSyncAdmin)
        self.register(self.uads.drc)
        self.ioq[etft]['in'].put({uat:(user,)})
        self.notify(etft)
        
    #convenience method for address casting
    def castTo(self,requiredtype,address):
        '''Convenience method abstracting the casting function used to downcast address objects to the various feed required formats
        @param requiredtype: Address format requirement in FeedRef format 
        @type requiredtype: FeedRef
        @param address: Address object being cast
        @type address: Address
        @return: Address
        '''
        if not requiredtype in FeedType.reverse.keys(): raise Exception('unknown feed/address type')
        return FeatureFactory.getInstance(FeedRef((FeatureType.ADDRESS,requiredtype))).cast(address)
    
    #----------------------------
    #CM
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type=None, exc_val=None, exc_tb=None):
        return self.close()

        
class PersistenceException(AimsException): pass
class Persistence():
    '''Independent storage class for persisting configuration and session feature information'''
    
    tracker = {}
    coords = {'sw':SWZERO,'ne':NEZERO}
    ADL = None
    RP = os.path.join(os.path.dirname(__file__),'..',RES_PATH,LOCAL_ADL)
    
    def __init__(self,initialise=False):
        '''Setup stored/tracked data
        @param initialise: Re-read initial data values
        @type initialise: Boolean
        '''
        if initialise or not self.read():
            self.ADL = self._initADL() 
            #default tracker, gets overwrittens
            #page = (lowest page fetched, highest page number fetched)
            self.tracker[FEEDS['AF']] = {'page':[1,1],    'index':1,'threads':2,'interval':30}    
            self.tracker[FEEDS['AC']] = {'page':[NPV,NPV],'index':1,'threads':0,'interval':125}  
            self.tracker[FEEDS['AR']] = {'page':[1,1],    'index':1,'threads':1,'interval':10000}  #was 10
            self.tracker[FEEDS['GC']] = {'page':[1,1],    'index':1,'threads':0,'interval':100030}  #Was 130 
            self.tracker[FEEDS['GR']] = {'page':[1,1],    'index':1,'threads':1,'interval':55}          
            self.tracker[FEEDS['UA']] = {'page':[1,1],    'index':1,'threads':0,'interval':0}              
            
            self.write() 
    
    def _initADL(self):
        '''Read ADL from serial and update from API'''
        return {f:[] for f in FEEDS.values()}
    
    def get(self,etft):
        '''Get data from persistent storage.
        @param etft: Type is feature class to return
        @type etft: FeedRef
        @return: List of features
        '''
        if etft: 
            return self.ADL[etft]
        return self.ADL
    
    def set(self,etft,data=None,pat=PersistActionType.REPLACE):        
        '''Set some persistent data to the ADL.
        @param etft: Type is features being set or where to store them
        @type etft: FeedRef
        @param data: List of features to save
        @type data: List<Feature>
        @param append: Whether to append to overwrite data in store. Default to append
        @type append: Boolean
        '''
        #TODO validation of type vs data provided
        #append a particular type of feature to existing
        if pat == PersistActionType.APPEND:
            self.ADL[etft] += data
        #initialise data for a particular feature type
        elif pat == PersistActionType.INIT:
            self.ADL[etft] = self._initADL()[etft]
        #replace all of a particular feature type    
        elif pat == PersistActionType.REPLACE:
            self.ADL[etft] = data
        #replace all of the persisted data
        elif pat == PersistActionType.ALL:
            self.ADL = data
        else:
            raise PersistenceException('Unknown persistence action, {}'.format(pat))

    
    #Disk Access
    #TODO OS agnostic path sep
    def read(self,localds=RP):
        '''Read function that unpickles local file store
        @param localds: Path to local file store
        @type localds: String
        '''  
        try:
            archive = pickle.load(open(localds,'rb'))
            #self.tracker,self.coords,self.ADL = archive
            self.tracker,self.ADL = archive
        except:
            return False
        return True
    
    def write(self, localds=RP):        
        '''Write function that builds array and pickles this to a local file store
        @param localds: Path to local file store
        @type localds: String
        '''  
        try:
            #archive = [self.tracker,self.coords,self.ADL]
            archive = [self.tracker,self.ADL]
            pickle.dump(archive, open(localds,'wb'))
        except:
            return False
        return True


refsnap = None
