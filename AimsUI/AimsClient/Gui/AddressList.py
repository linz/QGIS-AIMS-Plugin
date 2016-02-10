import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from DictionaryList import DictionaryListModel, DictionaryListView
import Controller
from AimsUI.AimsClient.Address import Address
#from ElectoralAddress.ResolutionData import ResolutionData

class AddressList( QObject ):
    '''
    Class for managing a list of Address objects and signalling changes 
    to addresses, for use by derived models/views
    '''

    itemChanged = pyqtSignal(int,name="itemChanged")
    listChanged = pyqtSignal(name="listChanged")

    

##################################################################


##################################################################

class AddressTableModel(QAbstractTableModel):
    def __init__(self, data = {}, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        #self.setList(data)
        self._headers = ['addressNumber' , 'addressNumberSuffix' , 'addressType' , 'lifecycle', 'roadName' , 'roadTypeName']
        # defualt key
        self.dict_key = 001 # will need to store the last key the user interacted with
    
    def set_key(self, key):
        self.beginResetModel()
        self.dict_key = key
        self.endResetModel()
        self.layoutChanged.emit()
    '''
    def setList( self, index, data ):
        #self.resettingModel.emit()
        self._data = data if data != None else {}
        self.dataChanged.emit(index, index)
        #self.layoutChanged.emit()
    '''
    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        #try:
        #    return len(self._data[self.dict_key])
        #except: return 0
        return 10
    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        #try:
        #   return len(self._data[self.dict_key][0])
        #except: return 0
        return 10 
    
    #def data(self, QModelIndex, int_role=None):
    #    row = QModelIndex.row()
    #    column = QModelIndex.column()
    #    if int_role == Qt.DisplayRole:
    #        return str(self._data[self.dict_key][row][column])

    def list_clicked(self, index):#rename table
        return self._data[self.dict_key][index.row()]
    



##################################################################

class AddressListModel(QAbstractListModel, AddressTableModel):
    def __init__(self, data, tableModel = None, parent=None):
        super(AddressListModel, self).__init__(parent)
        self._data = sorted(data.keys())
        self._tableModel = tableModel
        
    def setList( self, list ):
        #self.resettingModel.emit()
        self._list = list if list != None else []
        self.layoutChanged.emit()

    def list_clicked(self, index):
        row = index.row()
        key = self._data[row]
        self.set_key(key)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data)

    def data(self, QModelIndex, int_role=None):
        row = QModelIndex.row()
        if int_role == Qt.DisplayRole:
            return str(self._data[row])

    def flags(self, QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
