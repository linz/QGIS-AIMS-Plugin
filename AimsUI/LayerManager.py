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
    adrLayerObjMappings = {'addressType':['_components_addressType', None], # potential for mapping class?
                'fullAddress':['_components_fullAddress', None],
                'fullAddressNumber':['_components_fullAddressNumber', None],
                'fullRoadName':['_components_fullRoadName', None],
                'suburbLocality':['_components_suburbLocality', None],
                'townCity':['_components_townCity' '', None],
                'meshblock':['_codes_meshblock', None],
                'lifecycle':['_components_lifecycle', None], 
                'roadPrefix':['_components_roadSuffix',None],
                'roadName':['_components_roadName', None],                                
                'roadType':['_components_roadType',None],
                'roadSuffix':['_components_roadSuffix',None],
                'roadCentrelineId':['_components_roadCentrelineId',None],
                'waterRoute':['_components_waterRoute',None],
                'waterName':['_components_waterName',None],
                'unitValue':['_components_unitValue',None],
                'unitType':['_components_unitType',None],
                'levelType':['_components_levelType',None],
                'levelValue':['_components_levelValue',None],
                'addressNumberPrefix':['_components_addressNumberPrefix',None],
                'addressNumber':['_components_addressNumber',None],
                'addressNumberSuffix':['_components_addressNumberSuffix',None],
                'addressNumberHigh':['_components_addressNumberHigh',None],
                'addressId':['_components_addressId',None],
                'externalAddressId':['_components_externalAddressId',None],
                'externalAddressIdScheme':['_components_externalAddressIdScheme',None],
                'addressableObjectId':['_addressedObject_externalObjectId',None],
                'objectType':['_addressedObject_objectType',None],
                'objectName':['_addressedObject_objectName',None],
                #'addressPositionsType':["_addressedObject_addressPositions[0]['positionType']",None],
                'suburbLocalityId':['_codes_suburbLocalityId',None],
                'parcelId':['_codes_parcelId',None],
                'externalObjectId':['_addressedObject_externalObjectId',None],
                'externalObjectIdScheme':['_addressedObject_externalObjectIdScheme',None],
                'valuationReference':['_addressedObject_valuationReference',None],
                'certificateOfTitle':['_addressedObject_certificateOfTitle',None],
                'appellation':['_addressedObject_appellation',None]}

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
            #assert id == self.layerId(layer), 'ID return error'
        else: raise InvalidParameterException("'{}' is not a valid id".format(id))

    def layers(self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == layer.VectorLayer and self.layerId(layer):
                yield layer
    
    def addressLayer( self ):
        return self._adrLayer
    
    def rclLayer( self ):
        return self._rclLayer
    
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
        
        self.getAimsFeatures() 
        """
        ''' load AIMS features '''
        # test if layer exists
        self._controller
        
        # old api method below
        layerid = self._addressLayerId
        layer = self.findLayer(layerid)
        if layer:
            QgsMapLayerRegistry.instance().removeMapLayer( layer.id() )
        #test if scale allows showing of features
        scale = self._iface.mapCanvas().mapSettings().scale()
        if scale <= 10000: # would be a bit of reconjiggering to ensure persistent layer but then we could get scale from user settings
            self.getAimsFeatures()
        """
    def getAimsFeatures(self):
        ext = self._iface.mapCanvas().extent()
        self._controller.uidm.setBbox(sw = (ext.xMaximum(), ext.yMaximum()), ne = (ext.xMinimum(), ext.yMinimum()))
        featureData = self._controller.uidm.featureData()
        if featureData:
            self.createFeaturesLayer(featureData) # will move to once only initialisation 
            #self.updateFeaturesLayer(featureData)
            
        #else: ????
        '''
        ext = self._iface.mapCanvas().extent()
        # set bbbox
        # refresh
        #r = self._controller.getFeatures(ext.xMaximum(), ext.yMaximum(), ext.xMinimum(), ext.yMinimum()) 
        # all or nothing. i.e if the API limit of 1000 feature is met dont give the user any features
        if len(r['entities']) == 1000:
            return
        self.createFeaturesLayers(r)
        '''
    
    
#                'addressPositionsType':["_addressedObject_addressPositions[0]['position']['coordinates']",None],
 
    def createFeaturesLayer(self, featureData):
        id = self._addressLayerId
        layer = QgsVectorLayer("Point?crs=EPSG:4167", "AIMS Features", "memory") 
        self.setLayerId(layer, id)
        provider = layer.dataProvider()
        provider.addAttributes([QgsField(layerAttName, QVariant.String) for layerAttName in LayerManager.adrLayerObjMappings.keys()])

    
        layer.updateFields() # tell the vector layer to fetch changes from the provider
        
        # Fairly simple implementation (but simple to read and explicit) would like
        # would like to come back and do something more intelligent here
    
    #def updateFeaturesLayer(self, featureData):
        
        for feature in featureData.itervalues():
            fet = QgsFeature()
            point = feature._addressedObject_addressPositions[0]['position']['coordinates']
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(point[0], point[1])))
            fet.setAttributes([getattr(feature, v[0]) if hasattr (feature, v[0]) else '' for v in LayerManager.adrLayerObjMappings.values()])
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
