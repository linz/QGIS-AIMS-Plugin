import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from AimsUI.Ui_MoveAddressDialog import Ui_MoveAddressDialog
from AimsUI.AimsClient.Address import Address
from AimsUI.AimsClient.AimsUtility import AimsUtility

class MoveAddressTool(QgsMapToolIdentifyFeature):

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
        self._marker = AimsUtility.highlight(self._iface, coords)

    def canvasReleaseEvent(self, mouseEvent):
        self._iface.setActiveLayer(self._layers.addressLayer())
        
        if mouseEvent.button() == Qt.LeftButton:
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            # Ensure feature list and highlighting is reset
            self._features = []
            self._canvas.scene().removeItem(self._marker)
            
            if len(results) == 0: 
                return
            if len(results) == 1:
                # Highlight feature
                coords = results[0].mFeature.geometry().asPoint()
                self.setMarker(coords)
                # create address object for feature. It is this obj properties that will be passed to API
                self._features.append(self.setAddObj(results[0]))
                                
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
                            self._features.append(self.setAddObj(result))
                    
                    self._sb.showMessage("Right click for features new location")
                    
                else: 
                    self._features = None
                    self._canvas.scene().removeItem(self._marker)
                
        if mouseEvent.button() == Qt.RightButton:
            if self._features:
                pt = mouseEvent.pos()
                coords = self.toMapCoordinates(QPoint(pt.x(), pt.y()))
                coords = AimsUtility.transform(self._iface, coords)
                
                for feature in self._features:          
                    feature.set_x(coords[0])
                    feature.set_y(coords[1])
                
                    payload = feature.aimsObject()
                    valErrors = self._controller.updateFeature(payload)
                
                    if len(valErrors) == 0:
                        pass #no errors
                    else:
                        QMessageBox.warning(self._iface.mainWindow(),"Move Feature", valErrors +'\n'*2 + feature.fullAddress )
                
                self._features = []
                self._canvas.scene().removeItem(self._marker)
                self._sb.clearMessage()
                
            else: QMessageBox.warning(self._iface.mainWindow(),"Move Feature", "You must first select a feature to move")
    
    def setAddObj(self, results):
        # init new address obj
        self.feature = self._controller.initialiseAddressObj()
        # set obj properties    
        self.feature.setFullAddress(str(results.mFeature.attribute('fullAddress')))                     
        self.feature.setAddressType(str(results.mFeature.attribute('addressType')))
        self.feature.setSuburbLocality(str(results.mFeature.attribute('suburbLocality')))
        self.feature.setTownCity(str(results.mFeature.attribute('townCity')))
        self.feature.setLifecycle(str(results.mFeature.attribute('lifecycle'))) 
        self.feature.setRoadPrefix(str(results.mFeature.attribute('roadPrefix')))
        self.feature.setRoadName(str(results.mFeature.attribute('roadName')))      
        self.feature.setRoadSuffix(str(results.mFeature.attribute('roadSuffix')))
        self.feature.setRoadTypeName(str(results.mFeature.attribute('roadTypeName')))
        self.feature.setRoadCentrelineId(str(results.mFeature.attribute('roadCentrelineId')))
        self.feature.setWaterRouteName(str(results.mFeature.attribute('waterRouteName')))
        self.feature.setWaterName(str(results.mFeature.attribute('waterName')))
        self.feature.setUnitValue(str(results.mFeature.attribute('unitValue')))
        self.feature.setUnitType(str(results.mFeature.attribute('unitType')))
        self.feature.setLevelType(str(results.mFeature.attribute('levelType')))
        self.feature.setLevelValue(str(results.mFeature.attribute('levelValue')))
        self.feature.setAddressNumberPrefix(str(results.mFeature.attribute('addressNumberPrefix')))
        self.feature.setAddressNumber(str(results.mFeature.attribute('addressNumber')))
        self.feature.setAddressNumberSuffix(str(results.mFeature.attribute('addressNumberSuffix')))
        self.feature.setAddressNumberHigh(str(results.mFeature.attribute('addressNumberHigh')))
        self.feature.setVersion(str(results.mFeature.attribute('version')))
        self.feature.setAddressId(str(results.mFeature.attribute('addressId')))
        self.feature.setAoType(str(results.mFeature.attribute('objectType')))
        self.feature.setAoName(str(results.mFeature.attribute('objectName')))
        self.feature.setAoPositionType(str(results.mFeature.attribute('addressPositionType')))
        return self.feature

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