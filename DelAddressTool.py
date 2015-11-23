import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from Ui_DelAddressDialog import Ui_DelAddressDialog
from AimsUI.AimsClient.AimsApi import AimsApi

class DelAddressTool(QgsMapToolIdentifyFeature):

    tolerance=5

    def __init__(self, iface, layerManager, controller):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self.activate()
        self._layers = layerManager

    def activate(self):
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click map to delete feature")
    
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
        retireIds = {"version":None,
                    "components":{"addressId":None, "fullAddress":None}}
        
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        if len(results) == 0: 
            return
        if len(results) == 1:
            fullAddress = results[0].mFeature.attribute('fullAddress')
            retireIds['version'] = results[0].mFeature.attribute('version')
            retireIds['components']['addressId'] = results[0].mFeature.attribute('addressId')
            retireIds['components']['roadName'] = results[0].mFeature.attribute('roadName')
            
            if QMessageBox.question(self._iface.mainWindow(), 
                 "Confirm Address Retirement",
                 fullAddress + "\n will be marked for retirement?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Ok ) == QMessageBox.Ok:
                
                retireFeatures.append(retireIds)
        else: # Stacked points
            dlg = DelAddressDialog( self._iface.mainWindow() )
        
        self.delAddress(retireFeatures)
        
    def delAddress(self, retireFeatures):
        ''' iterate through ids of features to be deleted an pass to del API '''
        for retireFeatures in retireFeatures:
            AimsApi().changefeedRetire(retireFeatures)
            # build dict
            # append to list
 
    
class DelAddressDialog( Ui_DelAddressDialog, QDialog ):

    def __init__( self, parent ):
        QDialog.__init__(self,parent)
        self.setupUi(self)

    def selectAddress( self, addresses ):
        self.uSadListView.setList(addresses,
                                 ['address','sad_id','rna_id','offset'])
        if self.exec_() == QDialog.Accepted:
            return self.uSadListView.selectedItem()
        return None
