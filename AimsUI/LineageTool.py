import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from AimsUI.AimsClient.Gui.Ui_LineageDialog import Ui_LineageDialog

class LineageTool(QObject):

    def __init__(self, iface, layerManager, controller):
        QObject.__init__(self)
        self._iface = iface
        self._layers = layerManager
        self._controller = controller
        self.dlg = None
        
    def setEnabled( self, enabled ):
        self._enabled = enabled
        self.refineSelection()
    
    def showWarning(self, header, message):
        QMessageBox.warning(self._iface.mainWindow(),header,message)
    
    def refineSelection(self):
        ''' populate dialog from map selection and allow 
            the user to refine and confirm the map selection '''
        groupEntities=[]
        # Set address layer as the active layer
        self._iface.setActiveLayer(self._layers.addressLayer())
        self._layer = self._iface.activeLayer()
        
        # Get user selected features from the address layer 
        self._selection = self._layer.selectedFeatures()
        if len(self._selection) == 0: # <-- User made no selection
            self.showWarning('Selection Error','No Features Selected')
        else:
            for feature in self._selection:
                groupEntities.append(dict(
                fullAddress=feature['fullAddress'],
                lifecycle=feature['lifecycle'],
                version=feature['version'],
                addressId=feature['addressId']))
            
            self.dlg = LineageDialog(self._iface.mainWindow())
            groupEntities = self.dlg.selectFeatures(groupEntities)
        
        if groupEntities: # <-- else user hit 'ok' without selecting any records
            self.assignGroup(groupEntities)
        else: return # don't really need this
         
    def assignGroup(self, groupEntities):
        ''' open a new group if user the provides a new group description
            and return the new groupId. Else, assign any user provided 
            Id to the groupId Variable '''
        if self.dlg.uGroupId.text(): 
            groupId = self.dlg.uGroupId.text() # <-- Group Id as supplied by user
        else: 
            apiNewGroup = self._controller.newGroup({"description":self.dlg.uGroupDescription.toPlainText()}) # <-- Group Id as supplied by API
            # Http Validation results for new group creation
            if len(apiNewGroup['errors']) == 0: # i.e no errors
                groupId = apiNewGroup['data']['groupId']
            else: 
                self.showWarning("Create Lineage", apiNewGroup['errors']) # <-- else http errors
                return
        self.addToGroup(groupId, groupEntities)
        
    def addToGroup(self, groupId,groupFeatures ):
        ''' add the users selected AIMS features to a Lineage group '''
        # Add all selected feautres to group
        apiAddToGroup = self._controller.addToGroup(groupId,groupFeatures)
        # Http Validation results for add to group
        if len(apiAddToGroup['errors']) != 0: # API error list is populated
            self.showWarning("Create Lineage Error", ''.join(apiAddToGroup['errors']))
            return
        self.getVersion(groupId)
            
    def getVersion(self, groupId):
        ''' request the latest group version id'''
        apiVersionId = self._controller.groupVersion(str(groupId)) #<-- add to group does not return version, so here we must go get it
        groupVersionId = apiVersionId['data']['groupVersionId']
        # Http Validation results for getting of groupVersion
        if len(apiVersionId['errors']) != 0: # API error list is populated
            self.showWarning("Error Submitting Group For Review", ''.join(groupVersionId['errors']))
            return 
        self.submitGroup(groupId, groupVersionId)
        
    def submitGroup(self, groupId, groupVersionId):
        ''' submit a group for review '''
        apiSubmitGroup = self._controller.submitGroup(groupId,
                                                        {"version":groupVersionId,
                                                        "changeGroupId":groupId})
        # Http Validation results for group submit
        if len(apiSubmitGroup['errors']) != 0: # API error list is populated
            self.showWarning("Error Submitting Group For Review", ''.join(apiSubmitGroup['errors']))
                
class LineageDialog( Ui_LineageDialog, QDialog ):
    ''' QDialog Box requesting the user to refine and confirm
    their selection of features grouped as a common lineage  '''

    def __init__( self, parent ):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        # Signals
        self.uGroupDescription.textChanged.connect(self.groupDescripChanged)
        self.uGroupId.textChanged.connect(self.groupIdChanged)
    
    def groupSelection(self, selected):
        ''' Reformats the list of dict that represents the users selection 
        from the dialog into a list of AIMS json objects ''' 
        groupFeatures = []
        for i in selected:  
            groupIds = {}    
            # cant the below be one line    
            groupIds['version'] = i['version']
            groupIds['components'] = {'addressId': i['addressId']}
            groupIds['address'] = i['fullAddress']
            groupFeatures.append(groupIds)
        return groupFeatures        

    def selectFeatures( self, groupFeatures ):
        ''' return the records as selected by the user'''
        self.uSadListView.setList(groupFeatures,
                                 ['fullAddress','lifecycle','version','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.groupSelection(self.uSadListView.selectedItems())
        return None
    
    def groupDescripChanged(self):
        ''' if a description is provided, disable the user inputted group Id  '''
        if len(self.uGroupDescription.toPlainText()) != 0:
            self.uGroupId.setEnabled(False)
        else: self.uGroupId.setEnabled(True)

    def groupIdChanged(self):
        ''' id a group Id   is provided, disable the abiltiy to add a new description '''
        if len(self.uGroupId.text()) != 0:
            self.uGroupDescription.setEnabled(False)
        else: self.uGroupDescription.setEnabled(True)
        