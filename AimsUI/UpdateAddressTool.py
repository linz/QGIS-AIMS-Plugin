import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from AimsClient.Gui.UpdateAddressDialog import UpdateAddressDialog
from AimsUI.AimsClient.Gui.Ui_UpdAddressDialog import Ui_UpdAddressDialog
from AimsUI.AimsClient.UiUtility import UiUtility


class UpdateAddressTool(QgsMapToolIdentify):

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
        sb.showMessage("Click map to update feature")
    
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
        self._feature = None
        self._iface.setActiveLayer(self._layers.addressLayer())
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        
        if len(results) == 0: 
            return
        elif len(results) == 1:
            # initialise an address object and populate from selected feature
            self._feature = UiUtility.mapResultsToAddObj(results[0], self._controller)

        else: # Stacked points
            identifiedFeatures=[] 
            for i in range (0,len(results)):
                identifiedFeatures.append(dict(
                fullAddress=results[i].mFeature.attribute('fullAddress'),
                addressId= results[i].mFeature.attribute('addressId')))
                
            dlg = updateAddressDialog(self._iface.mainWindow())
            updFeatures = dlg.selectFeatures(identifiedFeatures)

            if updFeatures: 
                updFeatureIds = [d['addressId'] for d in updFeatures]

                for result in results:
                    if result.mFeature.attribute('addressId') in updFeatureIds:
                        self._feature = UiUtility.mapResultsToAddObj(result, self._controller)
                        break
        # Open form
        if self._feature:
            UpdateAddressDialog.updateAddress(self._feature, self._layers, self._controller, self._iface.mainWindow())

class updateAddressDialog(Ui_UpdAddressDialog, QDialog ):

    def __init__( self, parent ):
        QDialog.__init__(self,parent)
        self.setupUi(self)
    
    def selectFeatures( self, identifiedFeatures ):
        self.uSadListView.setList(identifiedFeatures,
                                 ['fullAddress','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.uSadListView.selectedItems()
        return None