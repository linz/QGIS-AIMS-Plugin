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

from AimsUI.AimsClient.Gui.Ui_DelAddressDialog import Ui_DelAddressDialog


class DelAddressTool(QgsMapToolIdentify):

    tolerance=5

    def __init__(self, iface, layerManager, controller):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._layers = layerManager
        self._controller = controller
        self.activate()
    
    def activate(self):
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click map to delete feature")
        self.cursor = QCursor(Qt.CrossCursor)
        self.parent().setCursor(self.cursor)
    
    def deactivate(self):
        sb = self._iface.mainWindow().statusBar()
        sb.clearMessage()
    
    def setEnabled(self, enabled):
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()

    def canvasReleaseEvent(self, mouseEvent):
        self._iface.setActiveLayer(self._layers.addressLayer())
        retireFeatures = []
        
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        if len(results) == 0: 
            return
        if len(results) == 1:
            retireIds = {}        
            retireIds['version'] = results[0].mFeature.attribute('version')
            retireIds['components'] = {'addressId': results[0].mFeature.attribute('addressId')}
            
            fullAddress = results[0].mFeature.attribute('fullAddress')
            
            if QMessageBox.question(self._iface.mainWindow(), 
                 "Confirm Address Retirement",
                fullAddress + "\n will be marked for retirement?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Ok ) == QMessageBox.Ok:    
                retireFeatures.append(retireIds)

        else: # Stacked points
            identifiedFeatures=[] 
            for i in range (0,len(results)):
                identifiedFeatures.append(dict(
                fullAddress=results[i].mFeature.attribute('fullAddress'),
                version= results[i].mFeature.attribute('version'),
                addressId= results[i].mFeature.attribute('addressId')
                ))
            # Open 'Retire' dialog showing selected AIMS features   
            dlg = DelAddressDialog(self._iface.mainWindow())
            retireFeatures = dlg.selectFeatures(identifiedFeatures)
        
        if retireFeatures: # else the user hit 'ok' and did not select any records            
            valErrors = self._controller.retireAddress(retireFeatures)
            if len(valErrors['errors']) != 0:
                #QMessageBox.warning(self._iface.mainWindow(),"Retire Address Point", valErrors)
                QMessageBox.warning(self._iface.mainWindow(),"Retire Feature Error", ''.join(valErrors['errors']))
        return       
 
class DelAddressDialog( Ui_DelAddressDialog, QDialog ):

    def __init__( self, parent ):
        QDialog.__init__(self,parent)
        self.setupUi(self)
    
    def selectionToRetirementJson(self, selected):
        ''' Reformats the list of dict that represents the users selection 
        from the dialog into a list of AIMS json objects ''' 
        retireFeatures = []
        for i in selected:  
            retireIds = {}        
            retireIds['version'] = i['version']
            retireIds['components'] = {'addressId': i['addressId']}
            retireIds['address'] = i['fullAddress'] #bit of a hack. this data not required by the API but useful for error reporting
            retireFeatures.append(retireIds)
        return retireFeatures        

    def selectFeatures( self, identifiedFeatures ):
        self.uSadListView.setList(identifiedFeatures,
                                 ['fullAddress','version','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.selectionToRetirementJson(self.uSadListView.selectedItems())
        return None

