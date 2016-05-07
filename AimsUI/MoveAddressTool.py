import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import time

from AimsUI.AimsClient.Gui.Ui_ComfirmSelection import Ui_ComfirmSelection
from AimsUI.AimsClient.Gui.UiUtility import UiUtility # remove?
from AimsUI.AimsClient.Gui.ResponseHandler import ResponseHandler
from AIMSDataManager.AimsUtility import FeedType, FEEDS
from AIMSDataManager.AddressFactory import AddressFactory
from AIMSDataManager.AimsLogging import Logger

uilog = None

class MoveAddressTool(QgsMapToolIdentify):
    # logging
    global uilog
    uilog = Logger.setup(lf='uiLog')

    def __init__(self, iface, layerManager, controller):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._canvas = iface.mapCanvas()
        self._layers = layerManager
        self._controller = controller
        self.RespHandler = ResponseHandler(self._iface, self._controller.uidm)
        self.highlighter = self._controller.highlighter
        self.af = {ft:AddressFactory.getInstance(FEEDS['AC']) for ft in FeedType.reverse}
        self._features = []
        self._sb = self._iface.mainWindow().statusBar()
        self.activate()

    def activate(self):
        QgsMapTool.activate(self)
        self._sb.showMessage("Select feature to move")
        self.cursor = QCursor(Qt.CrossCursor)
        self.parent().setCursor(self.cursor)
    
    def deactivate(self):
        self._sb.clearMessage()
    
    def setEnabled(self, enabled):
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()
    
    def setMarker(self, coords):
        self.highlighter.setAddress(coords)
    
    def hideMarker(self):
        self.highlighter.hideAddress()

    def canvasReleaseEvent(self, mouseEvent):
        self._iface.setActiveLayer(self._layers.addressLayer())
        
        if mouseEvent.button() == Qt.LeftButton:
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            # Ensure feature list and highlighting is reset
            self._features = []
            self.hideMarker()
            
            if len(results) == 0: 
                return
            elif len(results) == 1:
                # Highlight feature
                coords = results[0].mFeature.geometry().asPoint()
                self.setMarker(coords)
                # create address object for feature. It is this obj properties that will be passed to API
                self._features.append(self._controller.uidm.singleFeatureObj(results[0].mFeature.attribute('addressId')))
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
                            self._features.append(self._controller.uidm.singleFeatureObj(results[0].mFeature.attribute('addressId')))
                                           
                    self._sb.showMessage("Right click for features new location")
                    
                else: 
                    self._features = None
        
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
                coords = list(UiUtility.transform(self._iface, coords))

                for feature in self._features:
                    feature._addressedObject_addressPositions[0].setCoordinates(coords) # setter for this?
                    feature = self.af[FeedType.CHANGEFEED].cast(feature)
                    respId = int(time.time()) 
                    self._controller.uidm.updateAddress(feature, respId)
                    self.RespHandler.handleResp(respId, FEEDS['AC'])
                        
                self._features = []
                self.hideMarker()
                self._sb.clearMessage()

class MoveAddressDialog(Ui_ComfirmSelection, QDialog ):

    def __init__( self, parent ):
        QDialog.__init__(self,parent)
        self.setupUi(self)
    
    def selectFeatures( self, identifiedFeatures ):
        self.uSadListView.setList(identifiedFeatures,
                                 ['fullAddress','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.uSadListView.confirmSelection()
        return None