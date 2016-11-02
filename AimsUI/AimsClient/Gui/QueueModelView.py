################################################################################
#
# Copyright 2016 Crown copyright (c)
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
    """
    View for AIMS Queues
    
    @param QTableView: Inherits from QtGui.QWidget
    @param QTableView: QtGui.QTableView()
    """
    
    rowSelected = pyqtSignal( int, name="rowSelected" )
    rowSelectionChanged = pyqtSignal( name="rowSelectionChanged" )
    #rowActivated = pyqtSignal( int, name="rowActivated" )
    
    def __init__( self, parent=None ):
        """ 
        Initialise  View for AIMS Queues
        """
        
        QTableView.__init__( self, parent )
        # Change default settings
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(17)
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.AllEditTriggers)
       
    def selectionChanged( self, selected, deselected ):
        """
        When a tables selection is changed emit the row
        """
        
        QTableView.selectionChanged(self, selected, deselected)
        self.rowSelectionChanged.emit()
        row = self.selectedRow()
        if row != None:
            self.rowSelected.emit(row)
     
    def selectedRow( self ):
        """
        Returns the row as indicated by the selection model
        
        @return: The selected row number
        @rtype: integer
        """
        
        rows = self.selectionModel().selectedRows()
        if len(rows) == 1:
            return rows[0].row()
        return None
                
class FeatureTableModel(QAbstractTableModel):
    """
    Model for Queue Table Views

    @param QAbstractTableModel: Inherits from QAbstractTableModel
    @type QAbstractTableModel: QAbstractTableModel
    """
    
    def __init__(self, data = None, headerdata = None,parent=None):
        """        
        Table Model for Feature Views

        @param data: Data as formatted by the UIDataManager. The dictionary is formated
                    where by the key is a tuple repersenting thr group and the values 
                    are the feautres within the group  
        @type data: dictionary
        @param headerdata: Tables Headers
        @type headerdata: list    
        @param parent: QAbstractTableModel
        @type parent: QAbstractTableModel()
        """
        
        QAbstractTableModel.__init__(self, parent)
        self.dummyData = {('','', '', '', ''): [['', '', '', '', '']]}
        if not data: data = self.dummyData
        self._data = data
        self.headerdata = headerdata
        self.dict_key = self._data.keys()[0]
                        
    def setKey(self, key = None):
        """
        Update the dictionary key the represents the selected group

        @param key: Tuple that is a self._data key of which
                    represents a group record.
        @type key: tuple
        """
        
        self.beginResetModel()
        self.dict_key = key
        self.endResetModel()

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        """
        Return the number of rows in a table
        
        @return: number of rows in a table
        @rtype: integer
        """
        
        if self._data == self.dummyData or not self.dict_key: return 0
        return len(self._data[self.dict_key])

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        """
        Return the number of column in a table
        
        @return: number of column in a table
        @rtype: integer
        """
        
        try:
            return len(self._data[self.dict_key][0])
        except: return 0
        
    def data(self, QModelIndex, int_role=None):
        """ 
        Returns the data stored under the given role for 
        the item referred to by the index.

        @param index: QModelIndex
        @type index: index
        @param int_role: Qt.DisplayRole
        @type int_role: interger
        
        @return: data as stored under the given role for 
                the item referred to by the index.
        @rtype: data
        """
        
        row = QModelIndex.row()
        column = QModelIndex.column()
        if int_role == Qt.DisplayRole:
            return unicode(self._data[self.dict_key][row][column])
    
    def refreshData(self, data):
        """
        Update the models data and key indicating the current selected feature

        @param data: Data as formatted bu UIDataManager
        @type data: dictionary
        """
        
        if data:
            self._data = data
            # reset dict key
            self.dict_key = self._data.keys()[0]
    
    def headerData(self, col, orientation, role):
        """ 
        Returns the data for the given role and section in the header with the specified orientation
        """
        
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerdata[col]
        return None

    def tableSelectionMade(self, index):
        """ 
        Returns the refference to the selected group data

        @param row: The row the user selected
        @type row: interger
                
        @return: Refference (FeatureId) to the selected feature data
        @rtype: integer
        """
        
        if self._data == self.dummyData: return
        
        if type(self._data[self.dict_key][index][0]) is int:
            fData = self._data[self.dict_key][index][0]
        else: fData = self._data[self.dict_key][index][0][0]
        
        if fData: return fData

    def findfield(self, recId):
        """ 
        Returns a QmodelIndex when matched the record Id
        matches a record Id in table model

        @param recId: The Id the repersents an AIMS feature
        @type recId: string
                
        @return: QmodelIndex reffernce to the index of the item in the table
                that matches the recid param
        @rtype: QmodelIndex
        """
        
        startindex = self.index(0, 0)
        items = self.match(startindex, Qt.DisplayRole, recId, 1, Qt.MatchExactly | Qt.MatchWrap)
        try:
            return items[0]
        except IndexError:
            return QModelIndex()
        
class GroupTableModel(QAbstractTableModel):
    """ 
    Table Model for Group Tables
    
    @param QAbstractTableModel: Inherits from QAbstractTableModel
    @type QAbstractTableModel: QAbstractTableModel
    """
    
    def __init__(self, data = None, featureModel = None, headerdata = None, parent=None):
        """        
        Initialise table Model for Group Tables

        @param data: Data as formatted bu UIDataManager
        @type data: dictionary
        @param featureModel: The Feature Model that is related to the Group Model
        @type featureModel: AimsUI.AimsClient.Gui.QueueModelView.FeatureTableModel()
        @param headerdata: Tables Headers
        @type headerdata: list    
        @param parent: Inherits from QtGui.QWidget

        """
        
        QAbstractTableModel.__init__(self, parent)
        self.dummyData = {('','', '', '', ''): [['', '', '', '', '']]}
        if not data: data = self.dummyData
        self._data = sorted(data.keys())
        self.groupModel = featureModel
        self.headerdata = headerdata
        self._lookup = None

    def tableSelectionMade(self, row):
        """ 
        Returns the reference to the selected group data

        @param row: The row the user selected
        @type row: integer
                
        @return: Reference to the selected group data. Formatted as: 
                (GroupId, ChnageType)
        @rtype: tuple
        """
        
        self.setKey(row)
        return (self._data[row][0],self._data[row][1])
        
    def setKey(self, row):
        """
         Update the dictionary key the represents the selected group

        @param row: The row the user selected
        @type row: integer
        """
        
        if row == -1:
            key = None
        else:
            key = self._data[row]
        self.groupModel.setKey(key)
        
    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        """
        Return the number of rows in a table
        
        @return: number of rows in a table
        @rtype: integer
        """
        
        if self._data == self.dummyData: return 0
        return len(self._data)
    
    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        """
        Return the number of columns in a table
        
        @return: number of columns in a table
        @rtype: integer
        """
        
        if self._data == self.dummyData: return 0
        return len(self._data[0])

    def data(self, index, int_role=None):
        """ 
        Returns the data stored under the given role for 
        the item referred to by the index.

        @param index: QModelIndex
        @type index: index
        @param int_role: Qt.DisplayRole
        @type int_role: interger
        
        @return: data as stored under the given role for 
                the item referred to by the index.
        @rtype: data
        """
        
        row =index.row()
        col =index.column()
        if int_role == Qt.DisplayRole:
            return str(self._data[row][col])
    
    def refreshData(self, data):
        """
        Update the models data

        @param data: Data as formatted by UIDataManager
        @type data: dictionary
        """
        
        if data:
            self._data = sorted(data.keys())
    
    def getObjRef(self, rowIndex):
        """
        Update the models data

        @param rowIndex: QmodelIndex indicating the user selected row
        @type rowIndex: QmodelIndex

        @return: Feature identifier (featureId, ChangeType)
        @rtype: tuple   
        """
        
        return (self._data[rowIndex.row()][0], self._data[rowIndex.row()][1]) 
    
    def getUsers(self):
        """
        Return all unique sourceUsers as defined in self._data 
        
        @return: unique sourceUsers as defined in self._data 
        @rtype: list
        """
        return list(set([i[3] for i in self._data]))
        
    def getOrgs(self):
        """
        Return all unique sourceOrganisations as defined in self._data 
        
        @return: unique sourceOrganisations as defined in self._data 
        @rtype: list
        """
        
        return list(set([i[2] for i in self._data]))
        
    def headerData(self, col, orientation, role):
        """ 
        Returns the data for the given role and section in the header with the specified orientation
        """
        
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerdata[col]
        return None

    def flags(self, QModelIndex):
        """
        Returns the item flags for the given index.
        """
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def altSelectionId(self, row):
        """
        Returns the alternative selection. i.e; If the table is refreshed
        and the last user selection does exist the record returned here 
        is to be selected in the table as the current selection

        @param row: The row the user selected
        @type row: integer
        
        @return: The recid for the alternative selection
        @rtype: integer
        """
        
        if row+1 == self.rowCount():
            #last row, there is no 'next row'
            # rather than row below return row above as alt
            return self._data[row-1][0]
        return self._data[row+1][0]
     
    def findfield(self, recId):
        """ 
        Returns a QmodelIndex when matched the record Id
        matches a record Id in table model

        @param recId: The Id the repersents an AIMS feature
        @type recId: string
                
        @return: QmodelIndex reffernce to the index of the item in the table
                that matches the recid param
        @rtype: QmodelIndex
        """
        
        startindex = self.index(0, 0)
        items = self.match(startindex, Qt.DisplayRole, recId, 1, Qt.MatchExactly | Qt.MatchWrap)
        try:
            return items[0]
        except IndexError:
            return QModelIndex()
  