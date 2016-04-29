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
    modelReset = pyqtSignal( name="modelReset" )
    
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
        #self.setStyleSheet("* { gridline-color: gray }")
        
        self._model = None
        self._groupTableModel = None
        self._selectedId = None
        self._alternativeId =None
        
    def setModel( self, model ):
        QTableView.setModel( self, model )
#         if self._model:
#             self._model.modelReset.disconnect( self._onModelReset )
#             self._model.layoutAboutToBeChanged.disconnect( self._saveSelectedRow )
#             self._model.layoutChanged.disconnect( self._restoreSelectedRow )
#         if self._groupTableModel:
#             self._groupTableModel.resettingModel.disconnect( self._saveSelectedRow )
#         self._model = model 
#         self._groupTableModel = self._model if isinstance(self._model,QSortFilterProxyModel) else None
#         if self._model:
#             self._model.modelReset.connect( self._onModelReset )
#             self._model.layoutAboutToBeChanged.connect( self._saveSelectedRow )
#             self._model.layoutChanged.connect( self._restoreSelectedRow )
#         if self._groupTableModel:
#             self._groupTableModel.resettingModel.connect( self._saveSelectedRow )
#         self._onModelReset()
#     
#     def _onModelReset(self):
#         self.modelReset.emit()
#         if self.rowCount() > 0:
#             self.resizeColumnsToContents()
#             self._restoreSelectedRow()
#         else:
#             self.rowSelected.emit( -1 )
    
    def rowCount( self ):
        model = self.model()
        if not model:
            return 0
        return model.rowCount(QModelIndex())
                
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
    
    def _saveSelectedRow( self ):
        if not self._groupTableModel:
            self._selectedId = None
            self._alternativeId = None
            return
        self._selectedId = self.selectedId()
        if self._selectedId != None:
            row = self.selectedRow() + 1
            self._alternativeId = self.GroupTableModel.getId( row )
    
    def _restoreSelectedRow( self ):
        if not self.selectId(self._selectedId) and not self.selectId( self._alternativeId ):
            self.selectRow(0)

    def selectId( self, id ):
        if self._groupTableModel and id != None:
            row = self._groupTableModel.getIdDisplayRow( id )
            if row != None:
                self.selectRow( row )
                return True
        return False
    
    def selectedId( self ):
        if not self._groupTableModel:
            return None
        row = self.selectedRow()
        return self._groupTableModel.getId( row )

class FeatureTableModel(QAbstractTableModel):
 
    def __init__(self, data, headerdata = None,parent=None):
        QAbstractTableModel.__init__(self, parent)
        if not data: data = {('','', '', '', ''): [['', '', '', '', '']]} # dummy data if nothing return from dm
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
        ''' return the clicked on objs key '''
        if type(self._data[self.dict_key][index][0]) is int:
            fData = self._data[self.dict_key][index][0]
        else: fData = self._data[self.dict_key][index][0][0]
        if fData: return fData
        
class GroupTableModel(QAbstractTableModel):
    def __init__(self, data, featureModel = None, headerdata = None, parent=None):
        QAbstractTableModel.__init__(self, parent)
        if not data: data = {('','', '', '', ''): [['', '', '', '', '']]}
        self._data = sorted(data.keys())
        self.groupModel = featureModel
        self.headerdata = headerdata
        self._lookup = None

    def listClicked(self, row):
        key = self._data[row]
        self.groupModel.set_key(key)
        return (self._data[row][0],self._data[row][1])

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
    
    def getIdDisplayRow( self, id ):
        return self.getDisplayRow( self.getIdRow( id ))
    
    def getDisplayRow( self, row ):
        if row == None:
            return None
        if row < 0 or row >= len(self._data):
            return None       
        if self._lookup == None:
            lookup = [None] * len( self._data)
            for i in range(len(self._index)):
                lookup[self._index[i]] = i
            self._lookup = lookup
        return self._lookup[row]
    
    def getId( self, row ):
        item = self.getItem( row )
        return item.get(self._idColumn) if item else None
  