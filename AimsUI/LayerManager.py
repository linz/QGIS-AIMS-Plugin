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
from os.path import dirname, abspath, join

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from AimsClient import Database
from AimsUI.AimsClient.AimsApi import *
from AimsUI.AimsLogging import Logger

aimslog = Logger.setup()



class InvalidParameterException(): pass

class LayerManager(QObject):

    _propBaseName='AimsClient.'
    _styledir = join(dirname(abspath(__file__)),'styles')
    _addressLayerId='adr'

    def __init__( self, iface ):
        QObject.__init__(self)
        self._iface = iface
        self._statusBar = iface.mainWindow().statusBar()
        self._adrLayer = None
        self._rclLayer = None
        self._parLayer = None
        
        # connect loading of features to mapcanvas event
        self._iface.mapCanvas().extentsChanged.connect(self.loadFeatures)
        
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.checkRemovedLayer)
        QgsMapLayerRegistry.instance().layerWasAdded.connect( self.checkNewLayer )

    def layerId(self, layer):
        idprop = self._propBaseName + 'Id' 
        return str(layer.customProperty(idprop))

    def setLayerId(self, layer, id):
        idprop = self._propBaseName + 'Id'
        layer.setCustomProperty(idprop,id)

    def layers(self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == layer.VectorLayer and self.layerId(layer):
                yield layer
    
    def checkRemovedLayer(self, id):
        if self._adrLayer and self._adrLayer.id() == id:
            self._adrLayer = None
            #self.addressLayerRemoved.emit() -- need to disbale any tools that use this layer back in plugin.py
        if self._rclLayer and self._rclLayer.id() == id:
            self._rclLayer = None
        if self._parLayer and self._parLayer.id() == id:
            self._parLayer = None
    
    def checkNewLayer( self, layer ):
        layerId = self.layerId(layer)
        if not layerId:
            return
        if layerId == self._addressLayerId:
            newlayer = self._adrLayer == None
            self._adrLayer = layer
            #if newlayer:
                #self.addressLayerAdded.emit(layer) -- need to enab'e any tools that use this layer back in plugin.py
        elif layerId == 'rcl':
            self._rclLayer = layer
        elif layerId == 'par':
            self._parLayer = layer
    
    def findLayer(self, name): 
        for layer in self.layers():
            if self.layerId(layer) == name:
                return layer
        return None

    def installLayer(self, id, schema, table, key, estimated, where, displayname):
        ''' install AIMS postgres layers '''
        layer = self.findLayer(id)
        if layer:
            legend = self._iface.legendInterface()
            if not legend.isLayerVisible(layer):
                legend.setLayerVisible(layer, True)
            return layer
        self._statusBar.showMessage("Loading layer " + displayname)
        layer = None
        try:
            uri = QgsDataSourceURI()
            uri.setConnection(Database.host(),Database.port(),Database.database(),Database.user(),Database.password())
            uri.setDataSource(schema,table,'shape',where,key)
            uri.setUseEstimatedMetadata( estimated )
            layer = QgsVectorLayer(uri.uri(),displayname,"postgres")
            self.setLayerId( layer, id )
            try:
                layer.loadNamedStyle(join(self._styledir,id+'_style.qml'))
            except:
                pass
            QgsMapLayerRegistry.instance().addMapLayer(layer)
        finally:
            self._statusBar.showMessage("")
        return layer

    def installRefLayers(self):
        ''' install AIMS postgres ref data '''
        
        schema = Database.aimsSchema()
        # Join rcl and road name (via rna) for labeling purposes. NOTE - only P1 rna used
        sql = '''(Select rcl.roadcentrelineid, rcl.roadcentrelinealtid,rcl.noncadastralroad, 
                  rcl.shape, rcl.organisationid, rn.roadname, rt.roadtypename  
                FROM reference.roadcentreline rcl JOIN reference.roadnameassociation rna 
                ON rcl.roadcentrelineid = rna.roadcentrelineid 
                JOIN reference.roadname rn ON rn.roadnameid =  rna.roadnameid 
                LEFT JOIN reference.roadtype rt on rn.roadtypeid = rt.roadtypeid
                WHERE rcl.roadcentrelinestatus = 'CURR' AND rna.rnapriority = 1 AND rn.roadnamestatus = 'CURR')'''
        
        self.installLayer( 'rcl', '', sql, 'roadcentrelineid', True, "",'Roads' )        
        self.installLayer( 'par', schema, 'parcel', 'id', True, 
                            "parceltype not in ('ROAD','RLWY')",'Parcels' )
        
    def loadFeatures(self):
        ''' load AIMS features '''
        # test if layer exists
        layerid = self._addressLayerId
        layer = self.findLayer(layerid)
        if layer:
            QgsMapLayerRegistry.instance().removeMapLayer( layer.id() )
            #delete
            pass
        #test if scale allows showing of features
        scale = self._iface.mapCanvas().mapRenderer().scale()
        if scale <= 1000:
            self.createFeaturesLayers()

    

    def createFeaturesLayers(self):
        ext = self._iface.mapCanvas().extent()
        r = AimsApi().getFeatures(ext.xMaximum(), ext.yMaximum(), ext.xMinimum(), ext.yMinimum())
        id =  'adr'
        #set srs
        layer = QgsVectorLayer("Point", "AimsFeatures", "memory")
        self.setLayerId(layer, id)
        provider = layer.dataProvider()
        
        # add fields
        provider.addAttributes([QgsField("fullNum", QVariant.String),
                            QgsField("fullRoad", QVariant.String)])
        layer.updateFields() # tell the vector layer to fetch changes from the provider
        
        for i in r['entities']:
        # add a feature
            coords = ( i['properties']['addressedObject']['addressPosition']['coordinates'] )
            fullNum = i['properties']['components']['fullAddressNumber']
            fullRoad = i['properties']['components']['fullRoadName']
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(coords[0],coords[1])))
            fet.setAttributes([fullNum,fullRoad])
            provider.addFeatures([fet])
        
        # commit to stop editing the layer
        layer.commitChanges()
    
        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        layer.updateExtents()
        # add layer to the legend
        
        #will have to hit - set layer id
        
        try:
            layer.loadNamedStyle(join(self._styledir,id+'_style.qml'))
        except:
            pass
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        
        
        
               
        # first need to test is layer already exists
        #layerid = self._featuresLayerId
        #layername = "AIMS Features"