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

    def __init__(self, iface, layerManager, controller):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._controller = controller
        self._layers = layerManager
        self._parent = None
        self._marker = None
        self._canvas = iface.mapCanvas()
        self.highlight = self._controller.highlighter
        self.persistedRcl = None
        
        self.rcl = ''
        self.prefix = ''
        self.name = ''
        self.type = ''
        self.suffix = ''               
        self.waterName = ''
        
        self.rclcoords = None
        
        
    def activate(self):
        QgsMapTool.activate(self)
        self._parent = self._controller.rclParent
        self._iface.setActiveLayer(self._layers.rclLayer())
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage('Click map to select road centerline')
    
    def deactivate(self):
        sb = self._iface.mainWindow().statusBar()
        #self._canvas.scene().removeItem(self._marker) 
        sb.clearMessage()
    
    def removeMarker(self):
        self._canvas.scene().removeItem(self._marker)
        
    def setEnabled(self, enabled):
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()
    
    def fillform(self):
        self._parent.uRclId.setText(self.rcl)
        if self.addressClass == 'Road':
            self._parent.uRoadPrefix.setText(self.prefix)
            self._parent.uRoadName.setText(self.name)#
            self._parent.uRoadTypeName.setText(self.type)
            self._parent.uRoadSuffix.setText(self.suffix) 
        else:
            self._parent.uWaterRouteName.setText(self.waterName)
        
        if self._parent.__class__.__name__ != 'QueueEditorWidget' and self.rclcoords:
            self.highlight.setRcl(self.rclcoords)
            
    def canvasReleaseEvent(self, mouseEvent):
        try:
            self.removeMarker()
        finally:
            self.rclLayer = self._layers.rclLayer()        
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            
            if len(results) == 0: 
                return
            if len(results) == 1:            
                self.addressClass = self._parent.uAddressType.currentText()        
                self.rclcoords = results[0].mFeature.geometry()

                self.rcl = UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_section_id')))
                self.prefix = UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_prefix_value')))
                self.name = UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_body')))
                self.type = UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_type_value')))
                self.suffix = UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_suffix_value')))                    
                self.waterName = UiUtility.nullEqualsNone(str(results[0].mFeature.attribute('road_name_body')))
                self.fillform()
                self._controller.setPreviousMapTool() 
