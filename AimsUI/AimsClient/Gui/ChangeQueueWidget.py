
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_ChangeQueueWidget import Ui_ChangeQueueWidget
from QueueModelView import *

import sys # temp

class ChangeQueueWidget( Ui_ChangeQueueWidget, QWidget ):
    ''' connects View <--> Proxy <--> Data Model 
        and passed data to data model'''
     
    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self.setController( controller )
        
        self.mock_data = self.build_mock_data() # temp
    
        # Features View 
        featuresHeader = ['Full Number', 'Full Road', 'Life Cycle', 'Town', 'Suburb Locality', 'hidden']
        self.featuresTableView = self.uFeaturesTableView
        featureModel = FeatureTableModel(self.mock_data, featuresHeader)
        #VIEW <------> PROXY MODEL <------> DATA MODEL
        self.featuresTableView.setModel(featureModel)
        #self.featuresTableView.clicked.connect(self.featureSelected)
        self.featuresTableView.resizeColumnsToContents()
        self.featuresTableView.setColumnHidden(5, True)
        
        # Group View 
        self._groupProxyModel = QSortFilterProxyModel()
        self._groupProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        groupHeader = ['Id', 'Change', 'Source Org.', 'Submitter Name', 'Date']   
        self.groupTableView = self.uGroupTableView
        self.groupModel = GroupTableModel(self.mock_data, featureModel, groupHeader)
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
    
    def build_mock_data(self):
        return  {('090001','Update', 'Alk City', 'Milo', '2016-01-11'):     [['12', 'Test Road', 'Current', 'Somewhere Town',  'Somewhere', 'AddressObject1']],
                 ('4098018','Replace', 'Alk City', 'Nately', '2016-01-11'):  [['14', 'Fake Street', 'Current', 'Somewhere Town', 'Somewhere', 'AddressObject2'],
                                                                                     ['10', 'Goa Way', 'Current', 'Somewhere Town', 'Somewhere',  'AddressObject3'],
                                                                                     ['10A', 'Road Way',  'Current','Somewhere Town', 'Somewhere',  'AddressObject4']], 
                 ('4098018','Retire', 'Rotorua', 'Yossarian', '2016-02-34'): [['100', 'The Terrace', 'Retire','Somewhere Town', 'Somewhere', 'AddressObject5']],
                 ('4098018','Add', 'Wellington City',  'Appleby', '2016-01-11'):      [['100000', 'Busy Road', 'Current', 'Somewhere Town', 'Somewhere', 'AddressObject6']],
                 }