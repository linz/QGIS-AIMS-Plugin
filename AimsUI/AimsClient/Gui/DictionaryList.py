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
from qgis.core import * # temp for testing

# DictionaryListView and DictionaryListModel.  


class DictionaryListView( QTableView ):

    rowSelected = pyqtSignal( int, name="rowSelected" )
    rowDoubleClicked = pyqtSignal( int, name="rowDoubleClicked" )
    rowSelectionChanged = pyqtSignal( name="rowSelectionChanged" )
    modelReset = pyqtSignal( name="modelReset" )

    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )
        # Change default settings
        if parent.__class__.__name__ in  ('DelAddressDialog', 'MoveAddressDialog'):            
            self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        else: 
            self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(17)
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.setStyleSheet("* { gridline-color: gray }")

        # Own variables
        self._model=None
        self._dictionaryList = None
        self._selectedId =None
        self._alternativeId =None

        self.doubleClicked.connect( self.onDoubleClicked )

    # Reimplemented QTableView functions
    
    def selectionChanged( self, selected, deselected ):
        QTableView.selectionChanged( self, selected, deselected )
        self.rowSelectionChanged.emit()
        row = self.selectedRow()
        if row != None:
            self.rowSelected.emit( row )

    def setList( self, list, columns=None, headers=None  ):
        self.setModel( DictionaryListModel(list,columns,headers))

    def setModel( self, model ):
        QTableView.setModel( self, model )
        if self._model:
            self._model.modelReset.disconnect( self._onModelReset )
            self._model.layoutAboutToBeChanged.disconnect( self._saveSelectedRow )
            self._model.layoutChanged.disconnect( self._restoreSelectedRow )
        if self._dictionaryList:
            self._dictionaryList.resettingModel.disconnect( self._saveSelectedRow )
        self._model = model 
        self._dictionaryList = self._model if isinstance(self._model,DictionaryListModel) else None
        if self._model:
            self._model.modelReset.connect( self._onModelReset )
            self._model.layoutAboutToBeChanged.connect( self._saveSelectedRow )
            self._model.layoutChanged.connect( self._restoreSelectedRow )
        if self._dictionaryList:
            self._dictionaryList.resettingModel.connect( self._saveSelectedRow )
        self._onModelReset()

    # Select first row by default

    def _saveSelectedRow( self ):
        if not self._dictionaryList:
            self._selectedId = None
            self._alternativeId = None
            return
        self._selectedId = self.selectedId()
        if self._selectedId != None:
            row = self.selectedRow() + 1
            self._alternativeId = self._dictionaryList.getId( row )

    def _restoreSelectedRow( self ):
        if not self.selectId(self._selectedId) and not self.selectId( self._alternativeId ):
            self.selectRow(0)

    def _onModelReset(self):
        self.modelReset.emit()
        if self.rowCount() > 0:
            self.resizeColumnsToContents()
            self._restoreSelectedRow()
        else:
            self.rowSelected.emit( -1 )

    def onDoubleClicked( self, index ):
        row = self.selectedRow()
        if row != None:
            self.rowDoubleClicked.emit( row )

    def selectId( self, id ):
        if self._dictionaryList and id != None:
            row = self._dictionaryList.getIdDisplayRow( id )
            if row != None:
                self.selectRow( row )
                return True
        return False

    def selectedRow( self ):
        rows = self.selectionModel().selectedIndexes()
        if len(rows) == 1:
            return rows[0].row()
        
    def selectedId( self ):
        if not self._dictionaryList:
            return None
        row = self.selectedIndexes()
        return self._dictionaryList.getId( row )

    def selectedItem( self ):
        if not self._dictionaryList:
            return None
        row = self.selectedIndexes()
        return self._dictionaryList.getItem( row )# row == index

    def selectedRows( self ):
        return [r.row() for r in self.selectionModel().selectedIndexes()]

    def selectedItems( self ):
        if self._dictionaryList:
            list = self._dictionaryList
            return [list.getItem(r) for r in self.selectedIndexes()]
        return []

    def rowCount( self ):
        model = self.model()
        if not model:
            return 0
        return model.rowCount(QModelIndex())

class DictionaryListModel( QAbstractTableModel ):

    itemUpdated = pyqtSignal( int, name="itemUpdated" )
    resettingModel = pyqtSignal( name="resettingModel" )

    def __init__( self, list=None, columns=None, headers=None, idColumn=None ):
        QAbstractTableModel.__init__(self)
        self._columns = []
        self._headers = []
        self._editCols = []
        self._editable = []
        self._idColumn = id
        self._filter = None
        self._sortColumn = None
        self._sortReverse = False
        self._index = []
        self._lookup = None
        self._idLookup = None
        self._readonlyBrush = None
        self.setList( list, columns, headers, id )

    def list( self ):
        return self._list

    def setList( self, list, columns=None, headers=None, idColumn=None ):
        self.resettingModel.emit()
        self._list = list if list != None else []
        if not columns: columns = []

        self._createIndex()
        if idColumn:
            self._idColumn = idColumn
        self._setColumns( columns, headers )
        self._resetList()

    def setEditColumns( self, editColumns ):
        self._editable = [False] * len(self._columns)
        self._editCols = editColumns
        if editColumns:
            for editCol in editColumns:
                for i, col in enumerate(self._columns):
                    if editCol == col:
                        self._editable[i] = True

    def setFilter( self, filter=None ):
        self.resettingModel.emit()
        self._filter = filter
        self._createIndex()
        self._resetList()

    def resetFilter( self ):
        self.resettingModel.emit()
        self._createIndex()
        self._resetList()

    def setColumns( self, columns=None, headers=None ):
        self.resettingModel.emit()
        self._setColumns( columns, headers )
        self._resetList()

    def _setColumns( self, columns, headers ):
        if columns:
            self._columns = columns
            self._headers = headers
        if self._list and not self._columns:
            self._columns = sorted(self._list[0].keys())
        if not self._headers or len(self._headers) != len(self._columns):
            self._headers = self._columns
        self._editable = [False] * len(self._columns)
        self.setIdColumn( self._idColumn )
        self.setEditColumns( self._editCols )

    def setIdColumn( self, idColumn ):
        self._idColumn = idColumn
        self._idLookup = None

    def setReadonlyColour( self, colour ):
        self._readonlyBrush = QBrush(colour)

    def _createIndex( self ):
        if self._filter:
            self._index = [i 
                           for i in range(len(self._list)) 
                           if self._filter(self._list[i])]
        else:
            self._index = range( len( self._list) )
        self._sortIndex()
        self._lookup = None

    def getDisplayRow( self, row ):
        if row == None:
            return None
        if row < 0 or row >= len(self._list):
            return None
        if self._lookup == None:
            lookup = [None] * len( self._list)
            for i in range(len(self._index)):
                lookup[self._index[i]] = i
            self._lookup = lookup
        return self._lookup[row]

    def _setupColumns( self ):
        if self._list and not self._columns:
            columns = [k for k in list[0].keys() if not k.startswith("_")]
            self._columns = sorted(columns)
        if not self._headers or len(self._headers) != len(self._columns):
            self._headers = self._columns

    def _resetList( self ):
        self.modelReset.emit()

    def count( self ):
        return len( self._index )

    def rowCount( self, parent ): 
        return len(self._index) if not parent.isValid() else 0

    def columnCount( self, parent ): 
        return len(self._columns) if not parent.isValid() else 0

    def getItem( self, row ):
        if row != None and row >= 0 and row < len( self._index ):
            return self._list[self._index[row]]
        return None

    def getItems( self, rows ):
        return [self.getItem(r) for r in rows]

    def getId( self, row ):
        item = self.getItem( row )
        return item.get(self._idColumn) if item else None

    def getIdRow( self, id ):
        if not self._idLookup:
            self._idLookup=dict()
            if self._idColumn:
                for i in range(len(self._list)):
                    itemid = self._list[i].get(self._idColumn)
                    if itemid:
                        self._idLookup[itemid] = i
        return self._idLookup.get(id)

    def getIdDisplayRow( self, id ):
        return self.getDisplayRow( self.getIdRow( id ))

    def flags( self, index ):
        flag = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if self._editable[index.column()]:
            flag |= Qt.ItemIsEditable
        return flag

    def data( self, index, role ):
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return unicode(self._list[self._index[row]].get(self._columns[col],''))
        elif role == Qt.BackgroundRole and not self._editable[col] and self._readonlyBrush:
            return self._readonlyBrush
        return None

    def setData( self, index, value, role ):
        if not index.isValid() or role != Qt.EditRole:
            return False
        row = index.row()
        col = index.column()
        if not self._editable[col]:
            return False
        item = self.getItem( row )
        item[self._columns[col]] = str(value)
        self.dataChanged.emit(index,index)
        return True

    def headerData( self, section, orientation, role ):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if self._headers and section < len(self._headers):
                    return self._headers[section]
        return None

    def sort( self, column, order ):
        self.layoutAboutToBeChanged.emit()
        self._sortColumn = column
        self._sortReverse = order == Qt.DescendingOrder
        self._sortIndex()
        self.layoutChanged.emit()

    def _sortIndex( self ):
        if self._sortColumn == None:
            return
        key = self._columns[self._sortColumn]
        keyfunc = lambda x: self._list[x].get(key)
        self._index.sort( None, keyfunc, self._sortReverse )
        self._lookup = None

    def updateItem( self, index ):
        row = self.getDisplayRow(index)
        showing = True
        if self._filter:
            showing = row != None
            show = self._filter(self._list[index])
            if showing != show:
                self.resettingModel.emit()
                self._createIndex()
                self._resetList()
        elif showing:
            self.dataChanged.emit(self.index(row,0),self.index(row,len(self._columns)))
        self.itemUpdated.emit( index )
