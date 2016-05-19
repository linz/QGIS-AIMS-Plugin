
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

class FeatureHighlighter( QObject ):

    _adrMarkerColor = QColor(255,0,0)
    _revMarkerColor = QColor(255,0,0)
    _newAdrMarkerColor = QColor(255,0,0)
    _rclMarkerColor = QColor(76,255,0)

    def __init__( self, iface, layerManager, controller=None ):
        QObject.__init__(self)
        self._iface = iface
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
        #if self._controller:
        #    self._controller.addressUpdated.connect( self.resetAddress )

    def setEnabled( self, enabled ):
        self._enabled = enabled
        if self._enabled:
            self._revMarker.show()
        else: self._revMarker.hide()
        
    def setAddress( self, coords ):
        if self.isVisible( self._layers.addressLayer() ):
            self.hideNewAddress()
            self._adrMarker.setCenter( QgsPoint(coords[0], coords[1]) )
            self._adrMarker.show()

    def hideAddress(self):
        self._adrMarker.hide()
    
    def setNewAddress( self, coords ):
        if self.isVisible( self._layers.addressLayer() ):
            self.hideAddress()
            self._newAdrMarker.setCenter( QgsPoint(coords[0], coords[1]) )
            self._newAdrMarker.show()
        
    def hideNewAddress(self):
        self._newAdrMarker.hide()
        
    def setReview( self, coords ):
        if self.isVisible( self._layers.revLayer() ):
            self._revMarker.setCenter( QgsPoint(coords[0], coords[1]) )
            self._revMarker.show()
    
    def hideReview(self):
        self._revMarker.hide()
    
    def setRcl( self, coords ):
        rclLayer = self._layers.rclLayer()
        self._rclMarker.setToGeometry(coords,rclLayer)
        self._rclMarker.show()

    def hideRcl(self):
        self._rclMarker.hide()

    def isVisible(self, layer):
        return self._layers.isVisible(layer)