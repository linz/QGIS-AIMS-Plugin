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

from Ui_ReviewQueueWidget import Ui_ReviewQueueWidget
from QueueEditorWidget import QueueEditorWidget
from AIMSDataManager.AimsUtility import FeedType, FEEDS
from QueueModelView import *
from UiUtility import UiUtility 
import time

import sys # temp

class ReviewQueueWidget( Ui_ReviewQueueWidget, QWidget ):
    ''' connects View <--> Proxy <--> Data Model 
        and passed data to data model'''
    #featureSelected = pyqtSignal( Address, name="featureSelected" )
     
    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self.setController( controller )
        self.iface = self._controller.iface
        self.uidm = self._controller.uidm
        self.reviewData = self.uidm.reviewTableData((FEEDS['AR'],))   
        self.currentFeatureKey = None
        self.currentAdrCoord = [0,0]
        self.feature = None
        self.currentGroup = () #(id, type)
        
        # Connections
        self.uDisplayButton.clicked.connect(self.display)
        self.uUpdateButton.clicked.connect(self.updateFeature)
        self.uRejectButton.clicked.connect(self.decline)
        self.uAcceptButton.clicked.connect(self.accept)
        self.uRefreshButton.clicked.connect(self.refreshData)

               
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
        groupHeader = ['Id', 'Change', 'Source Org.', 'Submitter Name', 'Date']   
        self.groupTableView = self.uGroupTableView
        self.groupModel = GroupTableModel(self.reviewData, self.featureModel, groupHeader)
        self._groupProxyModel.setSourceModel(self.groupModel)
        self.groupTableView.setModel(self._groupProxyModel)
        self.groupTableView.resizeColumnsToContents()
        self.groupTableView.rowSelected.connect( self.groupSelected )
                
        # connect combobox_users to view and model
        self.comboModelUser = QStandardItemModel()
        self.comboBoxUser.setView(QListView())
        self.comboBoxUser.setModel(self.comboModelUser)
        self.comboBoxUser.view().clicked.connect(self.applyFilter) # combo box checked
        self.comboBoxUser.view().pressed.connect(self.itemPressedUser) # or more probable, list item clicked
        self.popUserCombo()
    
    def refreshData(self): # < -- ALSO NEED TO REFRESH THE FILTER
        if self.uGroupFeedCheckBox.isChecked():
            self.reviewData = self.uidm.reviewTableData((FEEDS['AR'], FEEDS['GR']))
        else:
            self.reviewData = self.uidm.reviewTableData((FEEDS['AR'],))
        self.groupModel.beginResetModel()
        self.featureModel.beginResetModel()
        self.groupModel.refreshData(self.reviewData)        
        self.featureModel.refreshData(self.reviewData)
        self.groupModel.endResetModel()
        self.featureModel.endResetModel()
        self.popUserCombo()
                
    def setController( self, controller ):
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller
    
    def singleReviewObj(self, feedType, objKey):
        if objKey: 
            return self.uidm.singleReviewObj(feedType, objKey)
    
    def currentReviewFeature(self):
        return self.uidm.currentReviewFeature(self.currentGroup, self.currentFeatureKey)
            
    def featureSelected(self, row):
        if self.currentGroup:    
            self.currentFeatureKey = self.featureModel.listClicked(row)   
            self.uQueueEditor.currentFeatureToUi(self.currentReviewFeature())
        #emit feature chnaged --> editwidget to connect to signal
        #self.featureSelected.emit( feature )
        
    def groupSelected( self, row ): #rename Select Group
        proxy_index = self.groupTableView.selectionModel().currentIndex()
        sourceIndex = self._groupProxyModel.mapToSource(proxy_index)
        self.currentGroup = self.groupModel.listClicked(sourceIndex.row())
        self.featuresTableView.selectRow(0)
   
    def itemPressedUser(self, index):
        item = self.comboBoxUser.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.applyFilter(self.comboBoxUser)

    def groupsFilter(self, col, data):
        self._groupProxyModel.setFilterKeyColumn(-1)
        self._groupProxyModel.setFilterRegExp(data)      
      
    def applyFilter(self, parent):        
        uFilter = ''
        model = parent.model()
        for row in range(model.rowCount()): 
            item = model.item(row)
            if item.checkState() == Qt.Checked:
                uFilter+='|'+item.text()
        self.groupsFilter(row, str(uFilter)[1:])
                
    def popUserCombo(self):
        data = self.groupModel.getUsers()
        data.sort()
        self.popCombo(data, self.comboModelUser)
                 
    def popCombo(self, cElements, model):     
        for i in range(len(cElements)):
            item = QStandardItem(cElements[i])
            item.setCheckState(Qt.Checked)
            item.setCheckable(True)
            model.setItem(i,item)
    
    def formatUiData(self):
        rData = {}
        for k, v in self.reviewData.items():
            rData[(v._changeId, v._changeType, 'orgPlaceHolder', v._workflow_submitterUserName, v._workflow_submittedDate )] = [
                    [self.fullNumber(), self.fullRoad(k), v._lifecycle, v._townCity, v._suburbLocality ]
                    ]
        return rData
    
    #def refreshData(self):
    #    self.reviewData = self.uidm.reviewTableData()
    def updateFeature(self):
        self.feature = self.singleReviewObj(FEEDS['AR'],self.currentFeatureKey) # needs to modified to also search 'GR' 
        if self.feature: 
            UiUtility.formToObj(self)
            respId = int(time.time())
            self.uidm.repairAddress(self.feature, respId)
            UiUtility.handleResp(respId, self._controller, FeedType.RESOLUTIONFEED, self.iface)
            self.feature = None
    
    def reviewResolution(self, action):
        for row in self.groupTableView.selectionModel().selectedRows():
            objRef = ()
            objRef = self.groupModel.getObjRef(row)
            feedType = FEEDS['GR'] if objRef[1] == 'Replace' else FEEDS['AR']
            reviewObj = self.singleReviewObj(feedType, objRef[0])
            if reviewObj: 
                respId = int(time.time()) 
                if action == 'accept':
                    self.uidm.accept(reviewObj, respId)
                elif action == 'decline':
                    self.uidm.decline(reviewObj, respId)
                UiUtility.handleResp(respId, self._controller,feedType, self.iface)
    
    def decline(self):
        self.reviewResolution('decline')
    
    def accept(self):
        self.reviewResolution('accept')
        
    def display(self):
        if self.currentFeatureKey:
            coords = self.uidm.reviewItemCoords(self.currentGroup, self.currentFeatureKey) # should directly access coords
            if self.currentAdrCoord == coords: 
                return
            self.currentAdrCoord = coords
            buffer = .00100
            extents = QgsRectangle( coords[0]-buffer,coords[1]-buffer,
                                  coords[0]+buffer,coords[1]+buffer)
            self.iface.mapCanvas().setExtent( extents )
            self.iface.mapCanvas().refresh()
            #self.setMarker(coords) <-- perhaps the reveiw layer will suffice and no highlighted needed
    
    #def setMarker(self, coords):
    #    self._marker = UiUtility.highlight(self.iface, QgsPoint(coords[0],coords[1]))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    
    wnd = ReviewQueueWidget()
    wnd.show()
    sys.exit(app.exec_())
