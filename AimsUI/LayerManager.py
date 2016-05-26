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
from AimsUI.AimsLogging import Logger
from AIMSDataManager.AimsUtility import FEEDS

from collections import OrderedDict

aimslog = Logger.setup()

uilog = None

class Mapping():
    #format = feildname: [objProp, getter]
    adrLayerObjMappings = OrderedDict([
        ('addressType',['_components_addressType', None]),
        ('fullAddress',['_components_fullAddress', None]),
        ('fullAddressNumber',['_components_fullAddressNumber', None]),
        ('fullRoadName',['_components_fullRoadName', None]),
        ('suburbLocality',['_components_suburbLocality', None]),
        ('townCity',['_components_townCity' '', None]),
        ('meshblock',['_codes_meshblock', None]),
        ('lifecycle',['_components_lifecycle', None]), 
        ('roadPrefix',['_components_roadSuffix',None]),
        ('roadName',['_components_roadName', None]),                                
        ('roadType',['_components_roadType',None]),
        ('roadSuffix',['_components_roadSuffix',None]),
        ('roadCentrelineId',['_components_roadCentrelineId',None]),
        ('waterRoute',['_components_waterRoute',None]),
        ('waterName',['_components_waterName',None]),
        ('unitValue',['_components_unitValue',None]),
        ('unitType',['_components_unitType',None]),
        ('levelType',['_components_levelType',None]),
        ('levelValue',['_components_levelValue',None]),
        ('addressNumberPrefix',['_components_addressNumberPrefix',None]),
        ('addressNumber',['_components_addressNumber',None]),
        ('addressNumberSuffix',['_components_addressNumberSuffix',None]),
        ('addressNumberHigh',['_components_addressNumberHigh',None]),
        ('addressId',['_components_addressId',None]),
        ('externalAddressId',['_components_externalAddressId',None]),
        ('externalAddressIdScheme',['_components_externalAddressIdScheme',None]),
        ('addressableObjectId',['_addressedObject_externalObjectId',None]),
        ('objectType',['_addressedObject_objectType',None]),
        ('objectName',['_addressedObject_objectName',None]),
        ('addressPositionsType',["_addressedObject_addressPositions[0]._positionType",None]),
        ('suburbLocalityId',['_codes_suburbLocalityId',None]),
        ('parcelId',['_codes_parcelId',None]),
        ('externalObjectId',['_addressedObject_externalObjectId',None]),
        ('externalObjectIdScheme',['_addressedObject_externalObjectIdScheme',None]),
        ('valuationReference',['_addressedObject_valuationReference',None]),
        ('certificateOfTitle',['_addressedObject_certificateOfTitle',None]),
        ('appellation',['_addressedObject_appellation',None]),
        ('version',['_components_version',None])
        ])

class LayerManager(QObject):
    
    # logging
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    _propBaseName='AimsClient.'
    _styledir = join(dirname(abspath(__file__)),'styles')
    _addressLayerId='adr'
    
    addressLayerAdded = pyqtSignal( QgsMapLayer, name="addressLayerAdded")
    addressLayerRemoved = pyqtSignal( name="addressLayerRemoved")

    def __init__(self, iface, controller):
        QObject.__init__(self)
        self._iface = iface
        self._controller = controller
        self._canvas = self._iface.mapCanvas()
        self._statusBar = iface.mainWindow().statusBar()
        self._controller.uidm.register(self)
        self.rData = None
        self.prevExt = None
        self.prevRdata = None
        self._adrLayer = None
        self._rclLayer = None
        self._parLayer = None
        self._locLayer = None
        self._revLayer = None
        
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.checkRemovedLayer)
        QgsMapLayerRegistry.instance().layerWasAdded.connect( self.checkNewLayer )
    
    def initialiseExtentEvent(self):  
        ''' Once plugin loading triggered initialise loading of AIMS Feautres '''
        self._canvas.extentsChanged.connect(self.setbbox)
    
    def disconnectExtentEvent(self):  
        ''' At plugin unload, disconnect the 
            extent changed / bbox event'''
        self._canvas.extentsChanged.disconnect(self.setbbox)
      
    def layerId(self, layer):
        idprop = self._propBaseName + 'Id' 
        res = layer.customProperty(idprop)
        if isinstance(res,QVariant): res = res.toPyObject()
        return str(res)

    def setLayerId(self, layer, id):
        if id and isinstance(id,str):
            idprop = self._propBaseName + 'Id'
            layer.setCustomProperty(idprop,id)

    def layers(self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
                yield layer
    
    def addressLayer( self ):
        return self._adrLayer
    
    def rclLayer( self ):
        return self._rclLayer
    
    def revLayer( self ):
        return self._revLayer
    
    def checkRemovedLayer(self, id):
        if self._adrLayer and self._adrLayer.id() == id:
            self._adrLayer = None
            self.addressLayerRemoved.emit()
        if self._rclLayer and self._rclLayer.id() == id:
            self._rclLayer = None
        if self._parLayer and self._parLayer.id() == id:
            self._parLayer = None
        if self._revLayer and self._revLayer.id() == id:
            self._revLayer = None
            
    def checkNewLayer( self, layer ):
        ''' assign new layer to layer ref '''
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
        elif layerId == 'rev':
            self._revLayer = layer
    
    def findLayer(self, name):
        ''' return layer ''' 
        for layer in self.layers():
            if self.layerId(layer) == name:
                return layer
        return None

    def styleLayer(self, layer, id):
        ''' set layer style as pet the relevant .qml file '''
        try:
            layer.loadNamedStyle(join(self._styledir,id+'_style.qml'))
        except:
            pass
    
    def installLayer(self, id, schema, table, key, estimated, where, displayname):
        ''' install AIMS postgres layers '''
        layer = self.findLayer(id)
        if layer:
            legend = self._iface.legendInterface()
            if not legend.isLayerVisible(layer):
                legend.setLayerVisible(layer, True)
            return layer
        self._statusBar.showMessage("Loading layer " + displayname)
        try:
            uri = QgsDataSourceURI()
            uri.setConnection(Database.host(),str(Database.port()),Database.database(),Database.user(),Database.password())
            uri.setDataSource(schema,table,'shape',where,key)            
            uri.setUseEstimatedMetadata( estimated )            
            layer = QgsVectorLayer(uri.uri(),displayname,"postgres")
            self.setLayerId( layer, id )
            self.styleLayer(layer, id)            
            QgsMapLayerRegistry.instance().addMapLayer(layer)
        finally:
            self._statusBar.showMessage("")
        return layer

    def installRefLayers(self):
        ''' install AIMS postgres ref data '''
        
        refLayers ={'par':( 'par', 'lds', 'all_parcel_multipoly', 'gid', True, "",'Parcels' ) ,
                    'rcl':( 'rcl', 'roads', 'road_name_mview', 'gid', True, "",'Roads' )
                    }

        for layerId , layerProps in refLayers.items():
            if not self.findLayer(layerId):
                self.installLayer(* layerProps) 

    def addLayerFields(self, layer, provider, id, fields):
        ''' add fields to aims to a layer  '''
        provider.addAttributes(fields)
        layer.updateFields()
        self.styleLayer(layer, id)     
        QgsMapLayerRegistry.instance().addMapLayer(layer)    
    
    def installAimsLayer(self, id, displayname):
        ''' initialise AIMS features and review layers at start up'''        
        layer = QgsVectorLayer("Point?crs=EPSG:4167", displayname, "memory") 
        self.setLayerId(layer, id)
        provider = layer.dataProvider()
        if id == 'adr' and not self.findLayer(id):
            self.addLayerFields(layer, provider, id, [QgsField(layerAttName, QVariant.String) for layerAttName in Mapping.adrLayerObjMappings.keys()] )
        elif id == 'rev' and not self.findLayer(id):
            self.addLayerFields(layer, provider, id, [QgsField('AimsId', QVariant.String), QgsField('AddressNumber', QVariant.String),QgsField('Action', QVariant.String)])
        layer.updateFields()
        QgsMapLayerRegistry.instance().addMapLayer(layer)           
        
    def isVisible(self, layer):
        ''' test is an layer is visible '''
        if layer.hasScaleBasedVisibility():
            if layer.maximumScale() > self._canvas.scale() and layer.minimumScale() < self._canvas.scale():
                return True
            else: 
                return False
        else:
            return True    

    def removeFeatures(self, layer):
        ''' remove features from any layer '''
        ids = [f.id() for f in layer.getFeatures()]
        layer.startEditing()
        for fid in ids:          
            layer.deleteFeature(fid)
        layer.commitChanges()
    
    def addToLayer(self, rData, layer):
        ''' add aims review features to reveiw layer '''
        provider = layer.dataProvider()
        for k, reviewItem in rData.items():
            fet = QgsFeature()
            if reviewItem._changeType in ('Update', 'Add') or reviewItem.meta.requestId:
                point = reviewItem.getAddressPositions()[0]._position_coordinates
            else:
                point = reviewItem.meta.entities[0].getAddressPositions()[0]._position_coordinates 
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(point[0], point[1])))
            fet.setAttributes([ k, reviewItem.getFullNumber(), reviewItem._changeType])
            provider.addFeatures([fet])
        layer.updateExtents()
    
    def updateReviewLayer(self):
        ''' update review layer with new review data'''
        id = 'rev'
        layer = self.findLayer(id)
        if not layer: 
            return
        self.removeFeatures(layer)
        rData = self._controller.uidm.combinedReviewData()
        uilog.info(' *** DATA ***    {} review items being loaded '.format(len(rData)))
        self.addToLayer(rData, layer)
    
    def bboxWithPrevious(self, ext):
        ''' test if the last emitted canvas extent is within
        the previous extent. If so the user has zoomed in on an
        existing feature layer and no call to load feature data is required'''
        if not self.prevExt: return False
        elif QgsRectangle.contains(self.prevExt, ext):
            return True
        else: return False
                        
    def setbbox(self):
        ''' pass new extent to DM'''
        id = self._addressLayerId
        layer = self.findLayer(id)
        ext = self._canvas.extent()
        if self._canvas.scale() > layer.maximumScale() or self.bboxWithPrevious(ext): return 
        uilog.info(' *** BBOX ***    {} '.format(ext.toString()))    
        self._controller.uidm.setBbox(sw = (ext.xMinimum(), ext.yMinimum()), ne = (ext.xMaximum(), ext.yMaximum()))
        self.prevExt = ext
                            
    def getAimsFeatures(self):
        ''' triggered when notify made aware of new features '''
        featureData = self._controller.uidm.featureData()
        if featureData:
            uilog.info(' *** DATA ***    {} AIMS features received '.format(len(featureData)))    
            self.updateFeaturesLayer(featureData)
    
    def notify(self, feedType):
        uilog.info('*** NOTIFY ***     Notify A[{}]'.format(feedType))
        if feedType == FEEDS['AF']:
            self.getAimsFeatures()
        elif feedType == FEEDS['AR'] or feedType == FEEDS['GR']:
            self.updateReviewLayer()

    def updateFeaturesLayer(self, featureData):
        ''' add features to Aims published features layer '''
        id = self._addressLayerId
        layer = self.findLayer(id)
        # ensure the user has not removed the layer 
        if not layer:
            self.installAimsLayer(id, 'AIMS Features')
            layer = self.findLayer(id) 
        if not self.isVisible(layer): 
            return
        legend = self._iface.legendInterface()
        if not legend.isLayerVisible(layer):
            legend.setLayerVisible(layer, True)
        # remove current features 
        self.removeFeatures(layer)
        uilog.info(' *** CANVAS ***    Adding Features') 
        for feature in featureData.itervalues():
            fet = QgsFeature()
            point = feature.getAddressPositions()[0]._position_coordinates
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(point[0], point[1])))
            fet.setAttributes([getattr(feature, v[0]) if hasattr (feature, v[0]) else '' for v in Mapping.adrLayerObjMappings.values()])
            layer.dataProvider().addFeatures([fet])
        layer.updateExtents()
        layer.setCacheImage(None)
        uilog.info(' *** CANVAS ***    FEATURES ADDED')  
        