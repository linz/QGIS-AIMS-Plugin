
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.utils import *

from Ui_ReviewQueueWidget import Ui_ReviewQueueWidget
from QueueModelView import *
#from UiUtility import UiUtility 

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
        self.uidm = self._controller.UidataManager        
        self.reviewData = self.uidm.reviewData()
        self.buttonDisplay.clicked.connect(self.display)
        self.currentObjKey = None
        
        # Features View 
        featuresHeader = ['Full Number', 'Full Road', 'Life Cycle', 'Town', 'Suburb Locality']
        self.featuresTableView = self.uFeaturesTableView
        self.featureModel = FeatureTableModel(self.reviewData, featuresHeader)
        #VIEW <------> PROXY MODEL <------> DATA MODEL
        self.featuresTableView.setModel(self.featureModel)
        self.featuresTableView.rowSelected.connect(self.featureClicked)
        self.featuresTableView.resizeColumnsToContents()
        self.featuresTableView.setColumnHidden(5, True)
        
        # Group View 
        self._groupProxyModel = QSortFilterProxyModel()
        self._groupProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        groupHeader = ['Id', 'Change', 'Source Org.', 'Submitter Name', 'Date']   
        self.groupTableView = self.uGroupTableView
        self.groupModel = GroupTableModel(self.reviewData, self.featureModel, groupHeader)
        #VIEW <------> PROXY MODEL <------> DATA MODEL
        self._groupProxyModel.setSourceModel(self.groupModel)
        self.groupTableView.setModel(self._groupProxyModel)
        self.groupTableView.resizeColumnsToContents()
        self.groupTableView.rowSelected.connect( self.selectAddress )

        # connect combobox_users to view and model
        self.comboModelUser = QStandardItemModel()
        self.comboBoxUser.setView(QListView())
        self.comboBoxUser.setModel(self.comboModelUser)
        self.comboBoxUser.view().clicked.connect(self.applyFilter) # combo box checked
        self.comboBoxUser.view().pressed.connect(self.itemPressedUser) # or more probable, list item clicked
        self.popUserCombo()
    
    def setController( self, controller ):
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller
    
    def singleReviewObj(self, objKey):
        return self.uidm.singleReviewObj(objKey)
            
    def featureClicked(self, row):
        self.currentObjKey = self.featureModel.listClicked(row)        
        #emit feature chnaged --> editwidget to connect to signal
        #self.featureSelected.emit( feature )
        self.uQueueEditor.currentFeature(self.singleReviewObj(self.currentObjKey))
        
    def selectAddress( self, row ): #rename Select Group
        self.groupModel.listClicked(row)
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
            #if len(rData) == 10: break
            rData[(v._changeId, v._changeType, 'orgPlaceHolder', v._workflow_submitterUserName, v._workflow_submittedDate )] = [[self.fullNumber(), self.fullRoad(k), v._lifecycle, v._townCity, v._suburbLocality ]]
        return rData
    
    def display(self):
        coords = self.uidm.reviewItemCoords(self.currentObjKey)
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
