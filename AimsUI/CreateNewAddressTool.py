# -*- coding: utf-8 -*-
################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
###############################################################################
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from AimsUI.AimsClient.Gui.UiUtility import UiUtility
from AIMSDataManager.AimsUtility import FEEDS
from AIMSDataManager.Address import Position
from AIMSDataManager.FeatureFactory import FeatureFactory

class CreateNewAddressTool(QgsMapToolIdentify):
    """
    Tool for creating new AIMS Features
    """ 

    def __init__(self, iface, layerManager, controller=None):
        """
        Intialise New Address Tool
        
        @param iface: QgisInterface Abstract base class defining interfaces exposed by QgisApp  
        @type iface: Qgisinterface Object
        @param layerManager: Plugins layer manager
        @type  layerManager: AimsUI.LayerManager()
        @param controller: Instance of the plugins controller
        @type  controller: AimsUI.AimsClient.Gui.Controller()
        """
            
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._layers = layerManager        
        self._controller = controller
        self.highlight = self._controller.highlighter
        self._canvas = iface.mapCanvas()
        self.af = FeatureFactory.getInstance(FEEDS['AC'])
        self.activate()
        
    def activate(self):
        """
        Activate New Address Tool
        """
        
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click map to create point")
        self.cursor = QCursor(Qt.CrossCursor)
        self.parent().setCursor(self.cursor)
    
    def deactivate(self):
        """
        Deactivate New Address Tool
        """
        
        sb = self._iface.mainWindow().statusBar()
        sb.clearMessage()

    def setEnabled(self, enabled):
        """ 
        When Tool related QAction is checked/unchecked,
        Activate / Disable the tool respectively

        @param enabled: Tool enabled. Boolean value
        @type enabled: boolean
        """
        
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()
 
    def canvasReleaseEvent(self,mouseEvent):
        """
        Capture users left click event coordinates for 
        the new AIMS Feature

        @param mouseEvent: QtGui.QMouseEvent
        @type mouseEvent: QtGui.QMouseEvent
        """

        self._iface.setActiveLayer(self._layers.addressLayer())
        
        if mouseEvent.button() == Qt.LeftButton:
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            # Ensure feature list and highlighting is reset            
            if len(results) == 0: 
                # no results - therefore we ain't snapping
                coords = self.toMapCoordinates(QPoint(mouseEvent.x(), mouseEvent.y()))
            else:
                # snap by taking the coords from the point within the 
                # tolerance as defined by QGIS maptool settings under options
                coords = results[0].mFeature.geometry().asPoint()
            self.NewAimsFeature(coords)
        
    def setMarker(self, coords):
        """
        Set marker on canvas to indicate the
        position of the feature they are creating

        @param coords: QgsPoint
        @type coords: QgsPoint
        """

        self.highlight.setNewAddress(coords)
    
    def hideMarker(self):
        """
        Remove the marker from the canvas
        """
        
        self.highlight.hideNewAddress()
        self.highlight.hideRcl()
   
   
    def NewAimsFeature( self, coords ):
        """
        Get New Address Instance. Make Address Editing Form
        visible to user

        @param coords: QgsPoint
        @type coords: QgsPoint
        """   
        # init new address object and open form
        #if self.formActive: return
        #self.formActive = True
        UiUtility.clearForm(self._controller._queues.tabWidget)
        coords = UiUtility.transform(self._iface, coords)
        self.setMarker(coords)        
        addInstance = self.af.get()
        self._controller._queues.uEditFeatureTab.setFeature('add', addInstance, coords)
        self._controller._queues.tabWidget.setCurrentIndex(0)
        UiUtility.setEditability(self._controller._queues.uEditFeatureTab)
