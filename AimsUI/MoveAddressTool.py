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

import sys
import time
import traceback

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *

from AimsUI.AimsClient.Gui.Ui_ComfirmSelection import Ui_ComfirmSelection
from AimsUI.AimsClient.Gui.UiUtility import UiUtility # remove?
from AimsUI.AimsClient.Gui.ResponseHandler import ResponseHandler
from AIMSDataManager.AimsUtility import FeedType, FEEDS, FeedRef, FeatureType
from AIMSDataManager.AddressFactory import AddressFactory
from AIMSDataManager.FeatureFactory import FeatureFactory
from AIMSDataManager.AimsLogging import Logger

uilog = None

class MoveAddressTool(QgsMapToolIdentify):
    """
    Tool for relocating AIMS Features
    """ 

    # logging
    global uilog
    uilog = Logger.setup(lf='uiLog')

    def __init__(self, iface, layerManager, controller):
        """
        Intialise Move Address Tool
        
        @param iface: QgisInterface Abstract base class defining interfaces exposed by QgisApp  
        @type iface: Qgisinterface Object
        @param layerManager: Plugins layer manager
        @type  layerManager: AimsUI.LayerManager()
        @param controller: Instance of the plugins controller
        @type  controller: AimsUI.AimsClient.Gui.Controller()
        """
            
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._canvas = iface.mapCanvas()
        self._layers = layerManager
        self._controller = controller
        self.RespHandler = ResponseHandler(self._iface, self._controller.uidm)
        self.highlighter = self._controller.highlighter
        self.afc = {ft:AddressFactory.getInstance(FEEDS['AC']) for ft in FeedType.reverse}
        self.aff = FeatureFactory.getInstance(FeedRef(FeatureType.ADDRESS,FeedType.FEATURES))
        self._features = []
        self._sb = self._iface.mainWindow().statusBar()
        self.activate()

    def activate(self):
        """
        Activate Move Address Tool
        """
        
        QgsMapTool.activate(self)
        self._sb.showMessage("Select feature to move")
        self.cursor = QCursor(Qt.CrossCursor)
        self.parent().setCursor(self.cursor)
    
    def deactivate(self):
        """
        Deactivate Move Address Tool
        """
        
        self._sb.clearMessage()
    
    def setEnabled(self, enabled):
        """ 
        When Tool related QAction is checked/unchecked
        Activate / Disable respectively

        @param enabled: Tool enabled. Boolean value
        @type enabled: boolean
        """
        
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()
    
    def setMarker(self, coords):
        """
        Place marker on canvas to indicate the feature to be moved

        @param coords: QgsPoint
        @type coords: QgsPoint
        """

        self.highlighter.setAddress(coords)
    
    def hideMarker(self):
        """
        Remove the marker from the canvas
        """
        
        self.highlighter.hideAddress()

    def canvasReleaseEvent(self, mouseEvent):
        """
        Identify the AIMS Feature(s) the user clicked

        @param mouseEvent: QtGui.QMouseEvent
        @type mouseEvent: QtGui.QMouseEvent
        """

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
                # TODO: Investigate Address Object. Why is addressId a string not an integer...
                # uilog.info(f'Getting address feature at mouse click: {results[0].mFeature} - Type: {type(results[0].mFeature)}')
                # uilog.info(f'> Feature Fields: {list(results[0].mFeature.fields().field(i) for i in results[0].mFeature.fields().allAttributesList())}')
                # uilog.info(f'> Feature Attributes: {results[0].mFeature.attributes()}')
                # uilog.info(f'> Address Feature ID {results[0].mFeature.attribute("addressId")} which is type: {type({results[0].mFeature.attribute("addressId")})}')
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
                    
                    for featureId in moveFeaturesIds:
                        self._features.append(self._controller.uidm.singleFeatureObj(featureId))
                                           
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
                    # Hack to retrieve the properties missing on the
                    # feature feed from the resolution feed < 
                    respId = int(time.time()) 
                    self._controller.uidm.supplementAddress(feature, respId)
                    feature = self._controller.RespHandler.handleResp(respId, FEEDS['AR'], 'supplement')
                    # />
                    #feature.type = FEEDS['AF']

                    # below clone is part of a fix still to be tested - TODO: Reenable and understand why this was being investigated
                    # NOTE: Keep an eye out for any issues here via the UI error on failing to create clone.
                    try:
                        clone = feature.clone(feature, self.aff.get())
                    except:
                        uilog.error(f'Failed to create clone. {traceback.format_exc()}')
                    clone._addressedObject_addressPositions[0].setCoordinates(coords, )
                    if clone._codes_isMeshblockOverride != True:
                        clone.setMeshblock(None)
                    respId = int(time.time()) 
                    clone = self.afc[FeedType.CHANGEFEED].cast(clone)
                    self._controller.uidm.updateAddress(clone, respId)
                    self.RespHandler.handleResp(respId, FEEDS['AC'])
                    
                    # # Old Code ... taken from LINZ copy... why are these different?
                    # feature._addressedObject_addressPositions[0].setCoordinates(coords)
                    # if feature._codes_isMeshblockOverride != True:
                    #     feature.setMeshblock(None)
                    # # BUG: self.af doesn't exist.
                    # # feature = self.af[FeedType.CHANGEFEED].cast(feature)
                    # feature = self.afc[FeedType.CHANGEFEED].cast(feature)
                    # respId = int(time.time()) 
                    # self._controller.uidm.updateAddress(feature, respId)
                    # self.RespHandler.handleResp(respId, FEEDS['AC'])
                        
                self._features = []
                self.hideMarker()
                self._sb.clearMessage()

class MoveAddressDialog(Ui_ComfirmSelection, QDialog ):
    """
    Dialog that is shown to the user if more than one feature is selected to
    allow the user to refine and confirm their selection

    @param Ui_ComfirmSelection: Ui Dialog to allow user to refine selection
    @type  Ui_ComfirmSelection: AimsUI.AimsClient.Gui.Ui_ComfirmSelection
    """
        
    def __init__( self, parent ):
        """
        Intialise dialog
        
        @param parent: Main Window
        @type  parent: QtGui.QMainWindow
        """
        QDialog.__init__(self,parent)
        self.setupUi(self)
    
    def selectFeatures( self, identifiedFeatures ):
        """
        Show selected features to user and return the users
        refined selection

        @param identifiedFeatures: List of dictionaries representing each selected feature
        @type  identifiedFeatures: list
        
        @return: List of dictionaries representing the refined selection
        @rtype: list
        """
        
        self.uSadListView.setList(identifiedFeatures,
                                 ['fullAddress','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.uSadListView.confirmSelection()
        return None
