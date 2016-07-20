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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *

from Ui_ReviewQueueWidget import Ui_ReviewQueueWidget
from QueueEditorWidget import QueueEditorWidget
from AIMSDataManager.AimsUtility import FeedType, FEEDS
from QueueModelView import *
from UiUtility import UiUtility 
import time

from AIMSDataManager.AimsLogging import Logger

import sys # temp

# Dev only - debugging
try:
    import sys
    sys.path.append('/opt/eclipse/plugins/org.python.pydev_4.4.0.201510052309/pysrc')
    from pydevd import settrace, GetGlobalDebugger
    settrace()

except:
    pass

uilog = None

class ReviewQueueWidget( Ui_ReviewQueueWidget, QWidget ):
    ''' connects View <--> Proxy <--> Data Model 
                and manage review data'''
    #logging 
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self.setController( controller )
        self._iface = self._controller.iface
        self.highlight = self._controller.highlighter
        self.uidm = self._controller.uidm
        self.uidm.register(self)
        self.reviewData = None
        self.currentFeatureKey = None
        self.currentAdrCoord = [0,0]
        self.feature = None
        self.currentGroup = (0,0) #(id, type)
        self.altSelectionId = ()
        
        
        # Connections
        self.uDisplayButton.clicked.connect(self.display)
        self.uUpdateButton.clicked.connect(self.updateFeature)
        self.uRejectButton.clicked.connect(self.decline)
        self.uAcceptButton.clicked.connect(self.accept)
        #self.uRefreshButton.clicked.connect(self.refreshData)
          
        # Features View 
        featuresHeader = ['Id','Full Num', 'Full Road', 'Life Cycle', 'Town', 'Suburb Locality']
        self.featuresTableView = self.uFeaturesTableView
        self.featureModel = FeatureTableModel(self.reviewData, featuresHeader)
        self.featuresTableView.setModel(self.featureModel)
        self.featuresTableView.rowSelected.connect(self.featureSelected)
        self.featuresTableView.resizeColumnsToContents()
        self.featuresTableView.setColumnHidden(5, True)
        self.featuresTableView.selectRow(0)
        
        # Group View 
        self._groupProxyModel = QSortFilterProxyModel()
        self._groupProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._groupProxyModel.layoutChanged.connect(self.groupSelected)
        groupHeader = ['Id', 'Change', 'Source Org.', 'Submitter Name', 'Date']   
        self.groupTableView = self.uGroupTableView
        
        self.groupModel = GroupTableModel(self.reviewData, self.featureModel, groupHeader)
        self._groupProxyModel.setSourceModel(self.groupModel)
        self.groupTableView.setModel(self._groupProxyModel)
        self.groupTableView.resizeColumnsToContents()
        #self.groupTableView.selectionModel().currentRowChanged.connect(self.groupSelected)
        #self.groupTableView.clicked.connect(self.groupSelected)
        self.groupTableView.rowSelectionChanged.connect(self.groupSelected)
                
        # connect combobox_users to view and model
        self.comboModelUser = QStandardItemModel()
        self.comboBoxUser.setView(QListView())
        self.comboBoxUser.setModel(self.comboModelUser)
        self.comboBoxUser.view().clicked.connect(self.applyFilter) # combo box checked
        self.comboBoxUser.view().pressed.connect(self.userFilterChanged) # or more probable, list item clicked
        self.popUserCombo()
    
    def setController( self, controller ):
        """  
        Access and assign the single instance of the Controller 
        
        @param controller: instance of the plugins controller
        @type  controller: AimsUI.AimsClient.Gui.Controller
        """
        
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller
    
    def notify(self, feedType):
        """
        Observer pattern, registered with uidm 
        
        @param feedType: feed type indicator
        """
        
        if feedType == FEEDS['AF']: return     
        uilog.info('*** NOTIFY ***     Notify A[{}]'.format(feedType))
        self.refreshData()

    def setMarker(self, coords):
        """
        Add a review marker to canvas if the highlight action action is checked 

        @param coords: list [x , y]
        @type coords: list
        """
        
        self.highlight.setReview(coords)
        
    def refreshData(self):
        """
        Update Review Queue data 
        """
        
        # request new data
        self.reviewData = self.uidm.formatTableData((FEEDS['GR'],FEEDS['AR']))
 
        self.groupModel.beginResetModel()
        self.groupModel.refreshData(self.reviewData)        
        self.groupModel.endResetModel()
        
        self.featureModel.beginResetModel()
        self.featureModel.refreshData(self.reviewData)
        self.featureModel.endResetModel()
        self.popUserCombo()
        
        uilog.info('*** NOTIFY ***     Table Data Refreshed')
        
        if self.reviewData:
            self.reinstateSelection()

    def reinstateSelection(self):
        """
        Select group item based on the last selected
        or alternative (next) feature in queue 
        """
        
        if self.currentFeatureKey:   
            #QgsMessageLog.logMessage("Primary: {0}, Alternative: {1}".format(self.currentGroup[0], self.altSelectionId), 'AIMS', QgsMessageLog.INFO)     
            matchedIndex = self.groupModel.findfield('{}'.format(self.currentGroup[0]))
            if matchedIndex.isValid() == False:
                matchedIndex = self.groupModel.findfield('{}'.format(self.altSelectionId)) or 0            
            row = matchedIndex.row()
            self.groupModel.setKey(row)
            #self.groupTableView.selectRow(row)
            if row != -1:
                self.groupTableView.selectRow(self._groupProxyModel.mapFromSource(matchedIndex).row())
                self.featuresTableView.selectRow(0)
                coords = self.uidm.reviewItemCoords(self.currentGroup, self.currentFeatureKey)
                self.setMarker(coords)
            else:
                self.uQueueEditor.clearForm()
                
        
    def singleReviewObj(self, feedType, objKey): # can the below replace this?
        """
        Return either single or group
        review object as per supplied key 
        
        @param feedType: feed type indicator
        @type feedType: AIMSDataManager.AimsUtility.FeedRef
        @param objKey: object reference id
        @type objKey: integer
        
        @return: AIMS Address Feature
        @rtype: AIMSDataManager.Address
        """
        
        if objKey: 
            return self.uidm.singleReviewObj(feedType, objKey)
    
    def currentReviewFeature(self):
        """
        Returns the current review feature as registered by last 
        review item selection 
        
        @return: AIMS Address Feature
        @rtype: AIMSDataManager.Address
        """
        
        return self.uidm.currentReviewFeature(self.currentGroup, self.currentFeatureKey)
            
    def featureSelected(self, row):
        """ 
        Sets the current feature reference when the user selects a feature

        @param row: The row the user has selected
        @type row: integer
        """

        if self.currentGroup[0]:  
            self.currentFeatureKey = self.featureModel.tableSelectionMade(row)   
            self.uQueueEditor.currentFeatureToUi(self.currentReviewFeature())
            
            self.setMarker(self.uidm.reviewItemCoords(self.currentGroup, self.currentFeatureKey))

    def groupSelected(self, row = None):
        """
        Set reference to current and alternative group records 

        @param row: The row the user has selected
        @type row: integer
        """

        proxyIndex = self.groupTableView.selectionModel().currentIndex()
        sourceIndex = self._groupProxyModel.mapToSource(proxyIndex)
        self.currentGroup = self.groupModel.tableSelectionMade(sourceIndex.row())

        altProxyIndex = self.groupTableView.model().index(proxyIndex.row()+1,0)
        
        if self._groupProxyModel.rowCount() == 0:
            self.currentGroup = None
            self.altSelectionId = 0
        elif self._groupProxyModel.rowCount() == 1:
            self.altSelectionId = 0
            self.featuresTableView.selectRow(0)
            return
        elif altProxyIndex.row() == -1:
            altProxyIndex = self.groupTableView.model().index(proxyIndex.row()-1,0)
            
        self.altSelectionId = self.groupTableView.model().data(altProxyIndex)
        self.featuresTableView.selectRow(0)

        #QgsMessageLog.logMessage("Primary: {0}, Alternative: {1}".format(self.currentGroup[0], self.altSelectionId), 'AIMS', QgsMessageLog.INFO) 
   
    def userFilterChanged(self, index):
        """ 
        Capture the user selection from filtering comboBox
        
        @param index: Combobox Index
        @type index: QModelIndex    
        """
        
        item = self.comboBoxUser.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.applyFilter(self.comboBoxUser)

    def groupsFilter(self, row, data):
        """
        Apply filter to group data
        
        @param data: String of active group filter item separated by vBars
        @type data: string     
        """
        
        self._groupProxyModel.setFilterKeyColumn(-1)
        self._groupProxyModel.setFilterRegExp(data)      
      
    def applyFilter(self, parent):
        """ 
        Filter Group Table when the comboBoxUser parameters are modified
        """
           
        uFilter = ''
        model = parent.model()
        for row in range(model.rowCount()): 
            item = model.item(row)
            if item.checkState() == Qt.Checked:
                uFilter+='|'+item.text()
        self.groupsFilter(row, str(uFilter)[1:])
                
    def popUserCombo(self):
        """
        Obtain all unique and active AIMS publisher values 
        """
        
        data = self.groupModel.getUsers()
        data.sort()
        self.popCombo(data, self.comboModelUser)
                 
    def popCombo(self, cElements, model):
        """
        Populate the comboBoxUser with unique system users
        
        @param cElements: List of Elements to populate combo box
        @type cElements: list
        @param model: The ComboBox ItemModel
        @type model: QtGui.QStandardItemModel
        """
        
        for i in range(len(cElements)):
            item = QStandardItem(cElements[i])
            item.setCheckState(Qt.Checked)
            item.setCheckable(True)
            model.setItem(i,item)    

   
    def updateFeature(self):
        """
        Update the properties of a review queue item 
        """
        
        self.feature = self.currentReviewFeature()
        if not self.feature:
            return 
        if self.feature._changeType == 'Retire':
            UiUtility.raiseErrorMesg(self._iface, 'Retire Items cannot be updated')
            return
        if UiUtility.formCompleteness('update', self.uQueueEditor, self._iface ):        
            UiUtility.formToObj(self)
            respId = int(time.time())
            self.uidm.repairAddress(self.feature, respId)
            self._controller.RespHandler.handleResp(respId, FEEDS['AR'])
            self.feature = None
    
    def reviewResolution(self, action):
        """
        Decline or Accept review item as per the action parameter  

        @param feedType: feed type indicator
        @type feedType: AIMSDataManager.AimsUtility.FeedRef
        """
        
        for row in self.groupTableView.selectionModel().selectedRows():
            sourceIndex = self._groupProxyModel.mapToSource(row)
            objRef = ()
            objRef = self.groupModel.getObjRef(sourceIndex)
            feedType = FEEDS['GR'] if objRef[1] not in ('Add', 'Update', 'Retire' ) else FEEDS['AR'] 
            reviewObj = self.singleReviewObj(feedType, objRef[0])
            if reviewObj: 
                respId = int(time.time()) 
                if action == 'accept':
                    self.uidm.accept(reviewObj,feedType, respId)
                elif action == 'decline':
                    self.uidm.decline(reviewObj, feedType, respId)
                    
                if self._controller.RespHandler.handleResp(respId, FEEDS['AR'], action):
                    self.highlight.hideReview()
                self.reinstateSelection()
                
    def decline(self):
        """
        Decline review item 
        """
        
        self.reviewResolution('decline')
        
    def accept(self):
        """
        Accept review item 
        """
        
        self.reviewResolution('accept')
        
    def display(self):
        """
        Zoom to Review Items Coordinates 
        """
        
        if self.currentFeatureKey:
            coords = self.uidm.reviewItemCoords(self.currentGroup, self.currentFeatureKey)
            if self.currentAdrCoord == coords: 
                return
            self.currentAdrCoord = coords
            buffer = .00100
            extents = QgsRectangle( coords[0]-buffer,coords[1]-buffer,
                                  coords[0]+buffer,coords[1]+buffer)
            self._iface.mapCanvas().setExtent( extents )
            self._iface.mapCanvas().refresh()
            self.setMarker(coords)

        
    @pyqtSlot()
    def rDataChanged (self):
        """
        Slot communicated to when the UIDataManager Modifies 
        the Review Data
        """
        
        self._queues.uResolutionTab.refreshData()

#   commented ou 14/6/2016  
#     
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     
#     
#     wnd = ReviewQueueWidget()
#     wnd.show()
#     sys.exit(app.exec_())