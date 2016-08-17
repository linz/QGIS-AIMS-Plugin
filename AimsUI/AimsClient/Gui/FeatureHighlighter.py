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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

class FeatureHighlighter(QObject):
    """
    Manager the highlighting of selected AIMS features
    """
    
    _adrMarkerColor = QColor(76,255,0)
    _revMarkerColor = QColor(255,0,0)
    _newAdrMarkerColor = QColor(76,255,0)
    _rclMarkerColor = QColor(76,255,0)

    def __init__( self, iface, layerManager, controller=None ):
        """
        Set individual marker default values
        
        @param iface:  Base class defining interfaces exposed by QgisApp 
        @type  iface: QgisInterface()
        @param layerManager: Plugins layer manager
        @type  layerManager: AimsUI.LayerManager()
        @param controller: Instance of the plugins controller
        @type  controller: AimsUI.AimsClient.Gui.Controller()
        """
    
        QObject.__init__(self)
        self._iface = iface
        self._controller = controller
        self._canvas = iface.mapCanvas()
        self._layers = layerManager
        self._enabled = False

        self._adrMarker = QgsVertexMarker(self._canvas)
        self._adrMarker.hide()
        self._adrMarker.setColor(self._adrMarkerColor)
        self._adrMarker.setIconSize(15)
        self._adrMarker.setPenWidth(2)
        self._adrMarker.setIconType(QgsVertexMarker.ICON_BOX)
        
        self._newAdrMarker = QgsVertexMarker(self._canvas)
        self._newAdrMarker.hide()
        self._newAdrMarker.setColor(self._newAdrMarkerColor)
        self._newAdrMarker.setIconSize(15)
        self._newAdrMarker.setPenWidth(2)
        self._newAdrMarker.setIconType(QgsVertexMarker.ICON_CROSS)
        
        self._revMarker = QgsVertexMarker(self._canvas)
        self._revMarker.hide()
        self._revMarker.setColor(self._revMarkerColor)
        self._revMarker.setIconSize(15)
        self._revMarker.setPenWidth(2)
        self._revMarker.setIconType(QgsVertexMarker.ICON_BOX)

        self._rclMarker = QgsRubberBand(self._canvas,False)
        self._rclMarker.hide()
        self._rclMarker.setWidth(3)
        self._rclMarker.setColor(self._rclMarkerColor)

        self._crs = QgsCoordinateReferenceSystem()
        self._crs.createFromOgcWmsCrs('EPSG:4167')
        self._controller = controller

    def setEnabled( self, enabled ):
        """
        Toggle highlighting on/off

        @type  enabled: boolean
        """
        
        self._enabled = enabled
        if self._enabled and self.isVisible(self._layers.revLayer()):
            self._revMarker.show()
        else: 
            self._revMarker.hide() 
            self._adrMarker.hide()
            self._newAdrMarker.hide()  
            self._rclMarker.hide()     
        
    def setAddress( self, coords ):
        """
        Highlight AIMS Feature that has been selected by the user for
        either purposes of relocating, updating or retiring.
        
        @param coords: canvas extent
        @type  coords: QgsPoint()
        """
        
        if self.isVisible( self._layers.addressLayer() ):
            self.hideNewAddress()
            self._adrMarker.setCenter( QgsPoint(coords[0], coords[1]) )
            self._adrMarker.show()

    def hideAddress(self):
        """
        Hide AIMS feature marker
        """
    
        self._adrMarker.hide()
    
    def setNewAddress( self, coords ):
        """
        Add marker to the canvas indicating the position of feature being created        
        
        @param coords: canvas extent
        @type  coords: QgsPoint()
        """
        
        if self.isVisible( self._layers.addressLayer() ):
            self.hideAddress()
            self._newAdrMarker.setCenter( QgsPoint(coords[0], coords[1]) )
            self._newAdrMarker.show()
        
    def hideNewAddress(self):
        """
        Hide the Marker indicating the position of a pending new feautre
        """
        
        self._newAdrMarker.hide()
        
    def setReview( self, coords ):
        """
        Highlight the feature under review
        """
        
        self._revMarker.setCenter( QgsPoint(coords[0], coords[1]) )
        if self._enabled and self.isVisible(self._layers.revLayer()):
            self._revMarker.show()
    
    def hideReview(self):
        """
        Hide the highlighting of the last selected Review Feature
        """
        
        self._revMarker.hide()
    
    def setRcl( self, line):
        """
        Highlight the Road Centre Line the user has selected to associated 
        with an AIMS feature
        """
        
        rclLayer = self._layers.rclLayer()
        self._rclMarker.setToGeometry(QgsGeometry.fromPolyline(line[0]),None)#,rclLayer)
        self._rclMarker.show()

    def hideRcl(self):
        """
        Hide the highlighting of the last selected Road Centre Line
        """
        
        self._rclMarker.hide()
    
    def hideAll(self):
        self.hideRcl()
        self.hideReview()
        self.hideAddress()
    
    def isVisible(self, layer):
        """
        Test is the layer is visible to the user
        """
        
        return self._layers.isVisible(layer)
