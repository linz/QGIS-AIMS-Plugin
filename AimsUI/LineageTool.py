import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

# from qgis.gui import QgsMapTool
# from qgis.gui import QgsMapToolIdentify as QMTI
# 
# from PyQt4.QtGui import QDialog
# from PyQt4.QtGui import QMessageBox

from AimsUI.AimsClient.Gui.Ui_LineageDialog import Ui_LineageDialog


class LineageTool(QObject):

    tolerance=5

    def __init__(self, iface, layerManager, controller):
        QObject.__init__(self)
        self._iface = iface
        self._layers = layerManager
        self._controller = controller
        
    def setEnabled( self, enabled ):
        self._enabled = enabled
        self.refineSelection()
    

    def refineSelection(self):
        groupFeatures=[]
        
        # Set address layer as the active layer
        self._iface.setActiveLayer(self._layers.addressLayer())
        self._layer = self._iface.activeLayer()
        
        # Get user selected features from the address layer 
        self._selection = self._layer.selectedFeatures()
        
        if len(self._selection) == 0: # <-- User made no selection
            QMessageBox.warning(self._iface.mainWindow(),'Selection Error','No Features Selected')
        else:
            for feature in self._selection:
                groupFeatures.append(dict(
                fullAddress=feature['fullAddress'],
                lifecycle=feature['lifecycle'],
                version=feature['version'],
                addressId=feature['addressId']))
            
            dlg = LineageDialog(self._iface.mainWindow())
            groupFeatures = dlg.selectFeatures(groupFeatures)
        
        if groupFeatures: # <-- else user hit 'ok' without selecting records
            # test if the user has supplied a group id, else request a new group form the API 
            if dlg.uGroupId.text(): 
                groupId = dlg.uGroupId.text() # <-- Group Id as supplied by user
            else: 
                apiNewGroup = self._controller.newGroup({"description":dlg.uGroupDescription.toPlainText()}) # <-- Group Id as supplied by API
                # Http Validation results for new group creation
                if len(apiNewGroup['errors']) == 0: # i.e no errors
                    groupId = apiNewGroup['data']['groupId']
                else: 
                    QMessageBox.warning(self._iface.mainWindow(),"Create Lineage", apiNewGroup['errors']) # <-- else http errors
                    return
   
            # Add all selected feautres to group
            apiAddToGroup = self._controller.addToGroup(groupId,groupFeatures)
            # Http Validation results for add to group
            if len(apiAddToGroup['errors']) != 0: # API error list is populated
                QMessageBox.warning(self._iface.mainWindow(),"Create Lineage Error", ''.join(apiAddToGroup['errors']))
                return

            # Submit to ResolutionFeed
            apiVersionId = self._controller.groupVersion(str(groupId)) #<-- add to group does not return version, so here we must go get it
            groupVersionId = apiVersionId['data']['groupVersionId']
            # Http Validation results for getting of groupVersion
            if len(apiVersionId['errors']) != 0: # API error list is populated
                QMessageBox.warning(self._iface.mainWindow(),"Error Submitting Group For Review", ''.join(groupVersionId['errors']))
                return 
            
            apiSubmitGroup = self._controller.submitGroup(groupId,
                                                            {"version":groupVersionId,
                                                            "changeGroupId":groupId})
            # Http Validation results for group submit
            if len(apiSubmitGroup['errors']) != 0: # API error list is populated
                QMessageBox.warning(self._iface.mainWindow(),"Error Submitting Group For Review", ''.join(apiSubmitGroup['errors']))
                
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
        self.uSadListView.setList(groupFeatures,
                                 ['fullAddress','lifecycle','version','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.groupSelection(self.uSadListView.selectedItems())
        return None
    
    def groupDescripChanged(self):
        if len(self.uGroupDescription.toPlainText()) != 0:
            self.uGroupId.setEnabled(False)
        else: self.uGroupId.setEnabled(True)

    def groupIdChanged(self):
        if len(self.uGroupId.text()) != 0:
            self.uGroupDescription.setEnabled(False)
        else: self.uGroupDescription.setEnabled(True)
        
