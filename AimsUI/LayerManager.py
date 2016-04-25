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
    _reviewLayerId='rev'
    
    addressLayerAdded = pyqtSignal( QgsMapLayer, name="addressLayerAdded")
    addressLayerRemoved = pyqtSignal( name="addressLayerRemoved")

    def __init__(self, iface, controller):
        QObject.__init__(self)
        self._iface = iface
        self._controller = controller
        self._statusBar = iface.mainWindow().statusBar()
        self._controller.uidm.register(self)
        self._adrLayer = None
        self._rclLayer = None
        self._parLayer = None
        self._locLayer = None
        self._revLayer = None
 
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.checkRemovedLayer)
        QgsMapLayerRegistry.instance().layerWasAdded.connect( self.checkNewLayer )
        
    def defaultExtent(self):
        ''' the extent the plugin first shows '''
        self._iface.mapCanvas().setExtent(QgsRectangle(174.77303,-41.28648, 174.77561,-41.28427))
        self._iface.mapCanvas().refresh()    
    
    def initialiseExtentEvent(self):  
        ''' Once plugin loading triggered initialise loading of AIMS Feautres '''
        self._iface.mapCanvas().extentsChanged.connect(self.setbbox)
                
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

    def styleLayer(self, layer, id):
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

        #return rcl,par
    def addAimsFields(self, layer, provider, id, fields):
        provider.addAttributes(fields)
        layer.updateFields()
        self.styleLayer(layer, id)     
        QgsMapLayerRegistry.instance().addMapLayer(layer)    
    
    def installAimsLayer(self, id, displayname):
        ''' initialise AIMS feautres and review layers '''
        
        layer = QgsVectorLayer("Point?crs=EPSG:4167", displayname, "memory") 
        self.setLayerId(layer, id)
        provider = layer.dataProvider()
        if id == 'adr' and not self.findLayer(id):
            self.addAimsFields(layer, provider, id, [QgsField(layerAttName, QVariant.String) for layerAttName in Mapping.adrLayerObjMappings.keys()] )
        elif id == 'rev' and not self.findLayer(id):
            self.addAimsFields(layer, provider, id, [QgsField('AddressNumber', QVariant.String),QgsField('Action', QVariant.String)])
        layer.updateFields()
        QgsMapLayerRegistry.instance().addMapLayer(layer)           

    def removeFeatures(self, layer):
        ids = [f.id() for f in layer.getFeatures()]
        layer.startEditing()
        for fid in ids:          
            layer.deleteFeature(fid)
        layer.commitChanges()
    
    def isVisible(self, layer):
        scale = self._iface.mapCanvas().mapRenderer().scale()
        return scale <= layer.maximumScale() and scale >= layer.minimumScale()
    
    def updateReviewLayer(self):#, rData):
        id = 'rev'
        layer = self.findLayer(id)
        if not layer: return
        provider = layer.dataProvider()
        self.removeFeatures(layer)
        rData = self._controller.uidm.reviewData() # moved out below of iteration to server log 
        uilog.info(' *** DATA ***    {} review items being loaded '.format(len(rData)))
        for reviewItem in rData.values():
            fet = QgsFeature()
            if reviewItem._changeType  in ('Replace', 'AddLineage', 'ParcelReferenceData' ):
                uilog.info(' *** DEBUG ***   {0}:  GROUP'.format(reviewItem._changeId)) 
                #uilog.info(' *** DEBUG ***   {0}: '.format(reviewItem._changeId))    
                point = reviewItem.meta.entities[0]._addressedObject_addressPositions[0]._position_coordinates
            elif reviewItem._changeType == 'Retire':
                uilog.info(' *** DEBUG ***   {0}:  RETIRE'.format(reviewItem._changeId)) 
                #uilog.info(' *** DEBUG ***   {0}: {1} '.format(reviewItem._changeId, reviewItem._addressedObject_addressPositions[0]._position_coordinates))    
                try:
                    point = reviewItem.meta.entities[0]._addressedObject_addressPositions[0]['position']['coordinates']
                except: # except when the retired item is derived from an resp obj
                    point = reviewItem._addressedObject_addressPositions[0]._position_coordinates
            else: point = reviewItem._addressedObject_addressPositions[0]._position_coordinates
            uilog.info(' *** DEBUG ***   {0}:  OTHER'.format(reviewItem._changeId)) 
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(point[0], point[1])))
            fet.setAttributes([ reviewItem.getFullNumber(), reviewItem._changeType])
            provider.addFeatures([fet])
        layer.commitChanges()
    
#     def isZoomin(self, ext):
#         ''' Test if the extent change was merely a zoom''' 
#         isZoomin = (ext.xMaximum() >= self.sw_x and ext.yMaximum() >= self.sw_y and 
#                     ext.xMinimum() >= self.ne_x and ext.yMinimum() >= self.ne_y)
#         
#         self.sw_x, self.sw_y, self.ne_x, self.ne_y = (ext.xMaximum(), ext.yMaximum(), ext.xMinimum(), ext.yMinimum())
#         return isZoomin                                             
    
    def setbbox(self):
        ext = self._iface.mapCanvas().extent()
        #if ext.asWktCoordinates() == '-185.77320897004406675 -120.40546550871380305, 187.99023996606607056 38.46554699064738969'
        if ext.width() > 100: return
        uilog.info(' *** BBOX ***    {} '.format(ext.toString()))    
        self._controller.uidm.setBbox(sw = (ext.xMaximum(), ext.yMaximum()), ne = (ext.xMinimum(), ext.yMinimum()))
                            
    def getAimsFeatures(self):
        ''' triggered when notify made aware of new features '''
        featureData = self._controller.uidm.featureData()
        if featureData:
            uilog.info(' *** DATA ***    {} AIMS features received '.format(len(featureData)))    
            self.updateFeaturesLayer(featureData)
    
    def notify(self, feedType):#, data):
        if feedType == FEEDS['AF']:
            self.getAimsFeatures()
        elif feedType == FEEDS['AR']:
            #self.updateReviewLayer(data)    
            self.updateReviewLayer()
    
    def updateFeaturesLayer(self, featureData):
        id = self._addressLayerId
        layer = self.findLayer(id)
        # ensure the user has not removed the layer 
        if not layer:
            self.installAimsLayer(id, 'AIMS Features')
            layer = self.findLayer(id) 
        # test the layer is visible
        #if not self.isVisible(layer):
        #    return             
        # ensure legend is visible
        legend = self._iface.legendInterface()
        if not legend.isLayerVisible(layer):
            legend.setLayerVisible(layer, True)
        # remove current features
        uilog.info(' *** CANVAS ***    Removing AIMS Features')    
        self.removeFeatures(layer)
        uilog.info(' *** CANVAS ***    Features Removed')  
        
        uilog.info(' *** CANVAS ***    Adding Features') 
        for feature in featureData.itervalues():
            fet = QgsFeature()
            point = feature._addressedObject_addressPositions[0]._position_coordinates
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(point[0], point[1])))
            fet.setAttributes([getattr(feature, v[0]) if hasattr (feature, v[0]) else '' for v in Mapping.adrLayerObjMappings.values()])
            layer.dataProvider().addFeatures([fet])
        layer.updateExtents()
        layer.reload()
        layer.setCacheImage(None)
        #self.canvas.refresh()
        uilog.info(' *** CANVAS ***    Features Added')  
        
        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        
        #self._iface.mapCanvas()
        #iface.mapCanvas().refresh()
#         if self._iface.mapCanvas().isCachingEnabled():
#             layer.setCacheImage(None)
#         else: