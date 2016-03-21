'''
Created on 29/01/2016

@author: splanzer
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class QueueView(QTableView):
    rowSelected = pyqtSignal( int, name="rowSelected" )
    rowSelectionChanged = pyqtSignal( name="rowSelectionChanged" )
    
    
    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )
        # Change default settings
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(17)
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.setStyleSheet("* { gridline-color: gray }")
           
    def selectionChanged( self, selected, deselected ): #1
        QTableView.selectionChanged( self, selected, deselected )
        self.rowSelectionChanged.emit()
        row = self.selectedRow()
        if row != None:
            self.rowSelected.emit( row )
    
    def selectedRow( self ):
        rows = self.selectionModel().selectedRows()
        if len(rows) == 1:
            return rows[0].row()
        return None

class FeatureTableModel(QAbstractTableModel):
 
    def __init__(self, data = {} , headerdata = None,parent=None):
        QAbstractTableModel.__init__(self, parent)
        if data == {}: data = {('','', '', '', ''): [['', '', '', '', '']]} # dummy data if nothing return from dm
        self._data = data
        self.headerdata = headerdata
        self.dict_key = self._data.keys()[0] # on init, storing any old key until the users updates it. issue when none returned....
                        
    def set_key(self, key = None):
        self.beginResetModel()
        self.dict_key = key
        self.endResetModel()

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data[self.dict_key])

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data[self.dict_key][0])

    def data(self, QModelIndex, int_role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if int_role == Qt.DisplayRole:
            return str(self._data[self.dict_key][row][column])
    
    def refreshData(self, data):
        self._data = data
        # reset dict key
        self.dict_key = self._data.keys()[0]
        
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerdata[col]
        return None

    def listClicked(self, index):
        ''' return the associated obj '''
        return self.dict_key[0]
            
        
class GroupTableModel(QAbstractTableModel):
    def __init__(self, data = {}, featureModel = None, headerdata = None, parent=None):
        QAbstractTableModel.__init__(self, parent)
        if data == {}: data = {('','', '', '', ''): [['', '', '', '', '']]}
        self._data = sorted(data.keys())
        self.groupModel = featureModel
        self.headerdata = headerdata

    def listClicked(self, row):
        key = self._data[row]
        self.groupModel.set_key(key)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data)
    
    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        try:
            return len(self._data[0])
        except: 0

    def data(self, index, int_role=None):
        row =index.row()
        col =index.column()
        if int_role == Qt.DisplayRole:
            return str(self._data[row][col])
    
    def refreshData(self, data):
        self._data = sorted(data.keys())
    
    def getObjRef(self, rowIndex):
        return self._data[rowIndex.row()][0] 
    
    def getUsers(self):
        return list(set([i[3] for i in self._data]))
    
    def getOrgs(self):
        return list(set([i[2] for i in self._data]))
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerdata[col]
        return None

    def flags(self, QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
  