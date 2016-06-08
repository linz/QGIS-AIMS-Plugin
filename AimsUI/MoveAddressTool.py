import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from AimsUI.AimsClient.Gui.Ui_MoveAddressDialog import Ui_MoveAddressDialog
from AimsUI.AimsClient.Address import Address
from AimsUI.AimsClient.UiUtility import UiUtility

class MoveAddressTool(QgsMapToolIdentify):

    tolerance=5

    def __init__(self, iface, layerManager, controller):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._canvas = iface.mapCanvas()
        self._layers = layerManager
        self._controller = controller
        self._features = []
        self._marker = None
        self._sb = self._iface.mainWindow().statusBar()
        self.activate()

    def activate(self):
        QgsMapTool.activate(self)
        self._sb.showMessage("Select feature to move")
    
    def deactivate(self):
        self._canvas.scene().removeItem(self._marker)
        self._sb.clearMessage()
    
    def setEnabled(self, enabled):
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()
    
    def setMarker(self, coords):
        self._marker = UiUtility.highlight(self._iface, coords)

    def canvasReleaseEvent(self, mouseEvent):
        self._iface.setActiveLayer(self._layers.addressLayer())
        
        if mouseEvent.button() == Qt.LeftButton:
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            # Ensure feature list and highlighting is reset
            self._features = []
            self._canvas.scene().removeItem(self._marker)
            
            if len(results) == 0: 
                return
            elif len(results) == 1:
                # Highlight feature
                coords = results[0].mFeature.geometry().asPoint()
                self.setMarker(coords)
                # create address object for feature. It is this obj properties that will be passed to API
                self._features.append(UiUtility.mapResultsToAddObj(results[0], self._controller))
                self._sb.showMessage("Right click for features new location")
                
            else: # Stacked points
                identifiedFeatures=[] 
                coords = results[0].mFeature.geometry().asPoint()
                self.setMarker(coords)
                for i in range (0,len(results)):
                    identifiedFeatures.append(dict(
                    fullAddress=results[i].mFeature.attribute('fullAddress'),
                    addressId= results[i].mFeature.attribute('addressId')
                    ))
                    
                dlg = MoveAddressDialog(self._iface.mainWindow())
                moveFeatures = dlg.selectFeatures(identifiedFeatures)
                
                if moveFeatures: 
                    # Form a list of Ids as selected by the user
                    moveFeaturesIds = [d['addressId'] for d in moveFeatures]
                    
                    for result in results:
                        if result.mFeature.attribute('addressId') in moveFeaturesIds:
                            self._features.append(UiUtility.mapResultsToAddObj(result, self._controller))
                                           
                    self._sb.showMessage("Right click for features new location")
                    
                else: 
                    self._features = None
                    self._canvas.scene().removeItem(self._marker)
        
        # Right click for new position         
        if mouseEvent.button() == Qt.RightButton:
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            if self._features:
                if len(results) == 0:                     
                    coords = self.toMapCoordinates(QPoint(mouseEvent.x(), mouseEvent.y()))

                else:
                    # Snapping. i.e Move to stack
                    coords = results[0].mFeature.geometry().asPoint()    
                
                # set new coords for all selected features
                coords = UiUtility.transform(self._iface, coords)
                for feature in self._features:          
                        feature.set_x(coords[0])
                        feature.set_y(coords[1])  
                    
                payload = feature.aimsObject()
                valErrors = self._controller.updateFeature(payload)
            
                if len(valErrors) == 0:
                    pass #no errors
                else:
                    QMessageBox.warning(self._iface.mainWindow(),"Move Feature", valErrors +'\n'*2 + feature._fullAddress )
                
                self._features = []
                self._canvas.scene().removeItem(self._marker)
                self._sb.clearMessage()
                
            else: QMessageBox.warning(self._iface.mainWindow(),"Move Feature", "You must first select a feature to move")

class MoveAddressDialog(Ui_MoveAddressDialog, QDialog ):

    def __init__( self, parent ):
        QDialog.__init__(self,parent)
        self.setupUi(self)
    
    def selectFeatures( self, identifiedFeatures ):
        self.uSadListView.setList(identifiedFeatures,
                                 ['fullAddress','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.uSadListView.selectedItems()
        return None