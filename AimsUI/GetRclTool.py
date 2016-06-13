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

from sip import setapi
setapi('QString', 2)
setapi('QVariant', 2)

from AimsUI.AimsClient.Gui.UiUtility import UiUtility

class GetRcl(QgsMapToolIdentifyFeature):
    """
    Tool for getting Road Centreline information
    """ 
    
    def __init__(self, iface, layerManager, controller):
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
        self._controller = controller
        self._layers = layerManager
        self._parent = None
        self._marker = None
        self._canvas = iface.mapCanvas()
        self.highlight = self._controller.highlighter
        #self.persistedRcl = None
        
        self.rcl = ''
        self.prefix = ''
        self.name = ''
        self.type = ''
        self.suffix = ''               
        self.waterName = ''
        self.rclLine = None

        
    def activate(self):
        """
        Activate RCL Tool
        """
        
        QgsMapTool.activate(self)
        self._parent = self._controller.rclParent
        self._iface.setActiveLayer(self._layers.rclLayer())
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage('Click map to select road centerline')
    
    def deactivate(self):
        """
        Deactivate RCL Tool
        """
        
        sb = self._iface.mainWindow().statusBar()
        #self._canvas.scene().removeItem(self._marker) 
        sb.clearMessage()
        
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
    
    def fillform(self):
        """
        Populate the Feature Editing form with Road Centreline information
        """
        
        self._parent.uRclId.setText(self.rcl)
        if self._parent.uAddressType.currentText() == 'Road':
            self._parent.uRoadPrefix.setText(UiUtility.nullEqualsNone(self.prefix))
            self._parent.uRoadName.setText(UiUtility.nullEqualsNone(self.name))
            self._parent.uRoadTypeName.setText(UiUtility.nullEqualsNone(self.type))
            self._parent.uRoadSuffix.setText(UiUtility.nullEqualsNone(self.suffix)) 
        else:
            self._parent.uWaterRouteName.setText(UiUtility.nullEqualsNone(self.waterName))
        
        if self._parent.__class__.__name__ != 'QueueEditorWidget':# and self._controller.rclcoords:
            self.highlight.setRcl(self.rclLine)
            
    def canvasReleaseEvent(self, mouseEvent):
        """
        Identify the Road Centreline the user clicked on

        @param mouseEvent: QtGui.QMouseEvent
        @type mouseEvent: QtGui.QMouseEvent
        """

        self.rclLayer = self._layers.rclLayer()        
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        
        if len(results) == 0: 
            return
        if len(results) == 1:            
            coords = results[0].mFeature.geometry()
            self.rclLine = coords.asMultiPolyline ()
            
            mapping = {'rcl' :'road_section_id', 'prefix' :'road_name_prefix_value', 
             'name' :'road_name_body', 'type' :'road_name_type_value', 'suffix' :'road_name_suffix_value', 
             'waterName' :'road_name_body',}
            
            for k, v in mapping.items():
                #setattr(self, k, UiUtility.nullEqualsNone(results[0].mFeature.attribute(v)))
                setattr(self, k, unicode(UiUtility.nullEqualsNone(results[0].mFeature.attribute(v))))
                
            self.fillform()
            self._controller.setPreviousMapTool() 
