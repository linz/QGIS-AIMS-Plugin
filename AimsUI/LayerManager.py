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
from qgis.gui import *

from AimsClient import Database
from AimsUI.AimsClient.AimsApi import *
from AimsUI.AimsLogging import Logger

aimslog = Logger.setup()

class InvalidParameterException(Exception): pass

class LayerManager(QObject):

    _propBaseName='AimsClient.'
    _styledir = join(dirname(abspath(__file__)),'styles')
    _addressLayerId='adr'
    
    addressLayerAdded = pyqtSignal( QgsMapLayer, name="addressLayerAdded")
    addressLayerRemoved = pyqtSignal( name="addressLayerRemoved")

    def __init__(self, iface, controller):
        QObject.__init__(self)
        self._iface = iface
        self._controller = controller
        self._statusBar = iface.mainWindow().statusBar()
        self._adrLayer = None
        self._rclLayer = None
        self._parLayer = None
        self._locLayer = None
        
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.checkRemovedLayer)
        QgsMapLayerRegistry.instance().layerWasAdded.connect( self.checkNewLayer )
    
    def initialiseExtentEvent(self):  
        ''' Once plugin loading triggered initialise loading of AIMS Feautres '''
        self._iface.mapCanvas().extentsChanged.connect(self.loadAimsFeatures)
    
    def layerId(self, layer):
        idprop = self._propBaseName + 'Id' 
        res = layer.customProperty(idprop)
        if isinstance(res,QVariant): res = res.toPyObject()
        return str(res)

    def setLayerId(self, layer, id):
        if id and isinstance(id,str):
            idprop = self._propBaseName + 'Id'
            layer.setCustomProperty(idprop,id)
            id2 = self.layerId(layer)
            if id2<>id: aimslog.warn('input id={} <> (layerid={}, cprop={})'.format(id,id2,layer.customProperty(idprop)))
        else: raise InvalidParameterException("'{}' is not a valid id".format(id))

    def layers(self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == layer.VectorLayer and self.layerId(layer):
                yield layer
    
    def addressLayer( self ):
        return self._adrLayer
    
    def checkRemovedLayer(self, id):
        if self._adrLayer and self._adrLayer.id() == id:
            self._adrLayer = None
            self.addressLayerRemoved.emit()
        if self._rclLayer and self._rclLayer.id() == id:
            self._rclLayer = None
        if self._parLayer and self._parLayer.id() == id:
            self._parLayer = None
        if self._locLayer and self._locLayer.id() == id:
            self._locLayer = None
            
    def checkNewLayer( self, layer ):
        layerId = self.layerId(layer)
        if not layerId:
            return
        if layerId == self._addressLayerId:
            newlayer = self._adrLayer == None
            self._adrLayer = layer
            if newlayer:
                self.addressLayerAdded.emit(layer)
        elif layerId == 'rcl':
            self._rclLayer = layer
        elif layerId == 'par':
            self._parLayer = layer
        elif layerId == 'loc':
            self._locLayer = layer
    
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
        
        rcl = self.installLayer( 'rcl', schema, 'aimsroads', 'roadcentrelineid', True, "",'Roads' )        
        par = self.installLayer( 'par', schema, 'parcel', 'id', True, 
                            "parceltype not in ('ROAD','RLWY')",'Parcels' )
        return rcl,par    
        
    def loadAimsFeatures(self):
        ''' load AIMS features '''
        # test if layer exists
        layerid = self._addressLayerId
        layer = self.findLayer(layerid)
        if layer:
            QgsMapLayerRegistry.instance().removeMapLayer( layer.id() )
        #test if scale allows showing of features
        scale = self._iface.mapCanvas().mapSettings().scale()
        if scale <= 10000: # would be a bit of reconjiggering to ensure persistent layer but then we could get scale from user settings
            self.getAimsFeatures()
    
    def getAimsFeatures(self):
        ext = self._iface.mapCanvas().extent()
        r = self._controller.getFeatures(ext.xMaximum(), ext.yMaximum(), ext.xMinimum(), ext.yMinimum()) 
        # all or nothing. i.e if the API limit of 1000 feature is met dont give the user any features
        if len(r['entities']) == 1000:
            return
        self.createFeaturesLayers(r)
        
    def createFeaturesLayers(self, r):
        id = self._addressLayerId
        layer = QgsVectorLayer("Point?crs=EPSG:2193", "AIMS Features", "memory") #rather not hard code crs
        self.setLayerId(layer, id)
        provider = layer.dataProvider()
        provider.addAttributes([QgsField('addressType', QVariant.String),
                                QgsField('fullAddress', QVariant.String),
                                QgsField('fullAddressNumber', QVariant.String),
                                QgsField('fullRoadName', QVariant.String),
                                QgsField('suburbLocality', QVariant.String),
                                QgsField('townCity', QVariant.String),
                                QgsField('meshblock', QVariant.String),
                                QgsField('lifecycle', QVariant.String), 
                                QgsField('roadPrefix', QVariant.String),
                                QgsField('roadName', QVariant.String),      
                                QgsField('roadSuffix', QVariant.String),
                                QgsField('roadTypeName', QVariant.String),
                                QgsField('roadCentrelineId', QVariant.String),
                                QgsField('waterRouteName', QVariant.String),
                                QgsField('waterName', QVariant.String),
                                QgsField('unitValue', QVariant.String),
                                QgsField('unitType', QVariant.String),
                                QgsField('levelType', QVariant.String),
                                QgsField('levelValue', QVariant.String),
                                QgsField('addressNumberPrefix', QVariant.String),
                                QgsField('addressNumber', QVariant.String),
                                QgsField('addressNumberSuffix', QVariant.String),
                                QgsField('addressNumberHigh', QVariant.String),
                                QgsField('version', QVariant.String),
                                QgsField('addressId', QVariant.String),
                                QgsField('addressableObjectId', QVariant.String),
                                QgsField('objectType', QVariant.String),
                                QgsField('objectName', QVariant.String),
                                QgsField('addressPositionType', QVariant.String),
                                QgsField('suburbLocalityId', QVariant.String),
                                QgsField('parcelId', QVariant.String)])
        # add fields

       
        layer.updateFields() # tell the vector layer to fetch changes from the provider
        
        # Fairly simple implementation (but simple to read and explicit) would like
        # would like to come back and do something more intelligent here
    
        for e in r['entities']:
            version = e['properties']['version']
            c = e['properties']['components']
            fullAddress = c['fullAddress'] if c.has_key('fullAddress') else None
            fullAddressNumber = c['fullAddressNumber'] if c.has_key('fullAddressNumber') else None
            fullRoadName = c['fullRoadName'] if c.has_key('fullRoadName') else None 
            addressId = c['addressId'] if c.has_key('addressId') else None 
            addressType = c['addressType'] if c.has_key('addressType') else None 
            lifecycle = c['lifecycle']if c.has_key('lifecycle') else None 
            unitType =c['unitType'] if c.has_key('unitType') else None 
            unitValue = c['unitValue'] if c.has_key('unitValue') else None 
            levelType = c['levelType'] if c.has_key('levelType') else None 
            levelValue = c['levelValue'] if c.has_key('levelValue') else None 
            addressNumberPrefix = c['addressNumberPrefix'] if c.has_key('addressNumberPrefix') else None 
            addressNumber = c['addressNumber'] if c.has_key('addressNumber') else None 
            addressNumberSuffix = c['addressNumberSuffix'] if c.has_key('addressNumberSuffix') else None 
            addressNumberHigh = c['addressNumberHigh'] if c.has_key('addressNumberHigh') else None 
            roadCentrelineId = c['roadCentrelineId'] if c.has_key('roadCentrelineId') else None 
            roadPrefix = c['roadPrefix'] if c.has_key('roadPrefix') else None 
            roadName = c['roadName'] if c.has_key('roadName') else None 
            roadTypeName = c['roadTypeName'] if c.has_key('roadTypeName') else None 
            roadSuffix = c['roadSuffix'] if c.has_key('roadSuffix') else None 
            waterRouteName = c['waterRouteName'] if c.has_key('waterRouteName') else None 
            waterName = c['waterName'] if c.has_key('waterName') else None 
            suburbLocality = c['suburbLocality'] if c.has_key('suburbLocality') else None
            townCity = c['townCity'] if c.has_key('townCity') else None 
            
            o = e['properties']['addressedObject']
            addressableObjectId = o['addressableObjectId'] if o.has_key('addressableObjectId') else None  
            objectType = o['objectType'] if o.has_key('objectType') else None     
            objectName = o['objectName'] if o.has_key('objectName') else None    
            addressPositionType = o['addressPosition']['type'] if o['addressPosition'].has_key('type') else None
            coords = o['addressPosition']['coordinates'] if o['addressPosition'].has_key('coordinates') else None 
            
            codes = e['properties']['codes'] 
            suburbLocalityId = codes['suburbLocalityId'] if codes.has_key('suburbLocalityId') else None  # does the user require these???
            townCityId = codes['townCityId'] if codes.has_key('townCityId') else None  # does the user require these???
            parcelId = codes['parcelId'] if codes.has_key('parcelId') else None  # does the user require these???
            meshblock = codes['meshblock'] if codes.has_key('meshblock') else None 
                 
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(coords[0],coords[1])))
            fet.setAttributes([ addressType,
                                fullAddress,
                                fullAddressNumber,
                                fullRoadName,
                                suburbLocality,
                                townCity,
                                meshblock,
                                lifecycle, 
                                roadPrefix,
                                roadName,      
                                roadSuffix,
                                roadTypeName,
                                roadCentrelineId,
                                waterRouteName,
                                waterName,
                                unitValue,
                                unitType,
                                levelType,
                                levelValue,
                                addressNumberPrefix,
                                addressNumber,
                                addressNumberSuffix,
                                addressNumberHigh,
                                version,
                                addressId,
                                addressableObjectId,
                                objectType,
                                objectName,
                                addressPositionType,
                                suburbLocalityId,
                                parcelId])
            provider.addFeatures([fet])

        # commit to stop editing the layer
        layer.commitChanges()
        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        #layer.updateExtents()
        try:
            layer.loadNamedStyle(join(self._styledir,id+'_style.qml'))
        except:
            pass
        QgsMapLayerRegistry.instance().addMapLayer(layer)

        if layer.featureCount() > 1000:
            self._iface.messageBar().pushMessage("Warning", "Not all features shown: API limit of 1000 features met", level=QgsMessageBar.CRITICAL)
