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
 
    def __init__(self, data = None, headerdata = None,parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.dummyData = {('','', '', '', ''): [['', '', '', '', '']]}
        if not data: data = self.dummyData # dummy data if nothing return from dm
        self._data = data
        self.headerdata = headerdata
        self.dict_key = self._data.keys()[0] # on init, storing any old key until the users updates it. issue when none returned....
                        
    def setKey(self, key = None):
        self.beginResetModel()
        self.dict_key = key
        self.endResetModel()

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        if self._data == self.dummyData: return 0
        return len(self._data[self.dict_key])

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        #if self._data == self.dummyData: return 0
        try:
            return len(self._data[self.dict_key][0])
        except: return 0 # no data for the group class
        
    def data(self, QModelIndex, int_role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if int_role == Qt.DisplayRole:
            return unicode(self._data[self.dict_key][row][column])
    
    def refreshData(self, data):
        if data:
            self._data = data
            # reset dict key
            self.dict_key = self._data.keys()[0]
        
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerdata[col]
        return None

    def listClicked(self, index):
        ''' return the clicked on objs key '''
        if self._data == self.dummyData: return
        if type(self._data[self.dict_key][index][0]) is int:
            fData = self._data[self.dict_key][index][0]
        else: fData = self._data[self.dict_key][index][0][0]
        if fData: return fData
        
class GroupTableModel(QAbstractTableModel):
    def __init__(self, data = None, featureModel = None, headerdata = None, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.dummyData = {('','', '', '', ''): [['', '', '', '', '']]}
        if not data: data = self.dummyData # dummy data if nothing return from dm
        self._data = sorted(data.keys())
        self.groupModel = featureModel
        self.headerdata = headerdata
        self._lookup = None

    def listClicked(self, row):
        self.setKey(row)
        return (self._data[row][0],self._data[row][1])
        
    def setKey(self, row):
        key = self._data[row]
        self.groupModel.setKey(key)
        
    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        if self._data == self.dummyData: return 0
        return len(self._data)
    
    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        if self._data == self.dummyData: return 0
        return len(self._data[0])
#         try:
#             return len(self._data[0])
#         except: 0

    def data(self, index, int_role=None):
        row =index.row()
        col =index.column()
        if int_role == Qt.DisplayRole:
            return str(self._data[row][col])
    
    def refreshData(self, data):
        if data:
            self._data = sorted(data.keys())
    
    def getObjRef(self, rowIndex):
        return (self._data[rowIndex.row()][0], self._data[rowIndex.row()][1]) 
    
    def getUsers(self):
        try:# hack to ensure working demo - it seems when an conflict is raised the below list cannot be compiled
            return list(set([i[3] for i in self._data]))
        except: return [] 
        
    def getOrgs(self):
        return list(set([i[2] for i in self._data]))
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerdata[col]
        return None

    def flags(self, QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def altSelectionId(self, row):
        ''' return the "next" row '''
        if row+1 == self.rowCount(): return row
        return self._data[row+1][0]
     
    def findfield(self, recId):
        ''' returns QmodelIndex when matched with 
            an aims record Id '''
        startindex = self.index(0, 0)
        items = self.match(startindex, Qt.DisplayRole, recId, 1, Qt.MatchExactly | Qt.MatchWrap) # chnage to only search the first instance
        try:
            return items[0]
        except IndexError:
            return QModelIndex()
  