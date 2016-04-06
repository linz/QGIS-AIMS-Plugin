################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from AimsUI.AimsClient.Gui.UiUtility import UiUtility

class GetRcl(QgsMapToolIdentifyFeature):

    def __init__(self, iface, layerManager, controller, parent):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._controller = controller
        self._layers = layerManager
        self.parent = parent
        self._marker = None
        self._canvas = iface.mapCanvas()
        #self.activate() # re,ove?
        
    def activate(self):
        QgsMapTool.activate(self)
        self.removeMarker()
        self._iface.setActiveLayer(self._layers.rclLayer())
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage('Click map to select road centerline')
    
    def deactivate(self):
        sb = self._iface.mainWindow().statusBar()
        self._canvas.scene().removeItem(self._marker) 
        sb.clearMessage()
    
    def removeMarker(self):
        if self._marker:
            self._canvas.scene().removeItem(self._marker)
        
    def setEnabled(self, enabled):
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()

    def canvasReleaseEvent(self, mouseEvent):
        rclLayer = self._layers.rclLayer()        
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        
        if len(results) == 0: 
            return
        if len(results) == 1:            
            self._canvas.scene().removeItem(self._marker) 
            addressClass = self.parent.uAddressType.currentText()        
            coords = results[0].mFeature.geometry()
            
            if addressClass == 'Road':
                self.parent.uRclId.setText(UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_section_id'))))
                self.parent.uRoadPrefix.setText(UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_prefix_value'))))
                self.parent.uRoadName.setText(UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_body'))))#
                self.parent.uRoadTypeName.setText(UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_type_value'))))
                self.parent.uRoadSuffix.setText(UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_suffix_value')))) 
            else:
                self.parent.uRclId.setText(UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_section_id'))))
                self.parent.uWaterRouteName.setText(UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_body'))))
            
            if self.parent.__class__.__name__ != 'QueueEditorWidget':
                self._marker = UiUtility.rclHighlight(self._canvas, coords,rclLayer)
            else:
                self._controller.setPreviousMapTool() 
   