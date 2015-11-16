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

#from AimsUI.AimsLogging import Logger

#aimslog = Logger.setup()

class InvalidParameterException(): pass

class LayerManager( QObject ):

    _propBaseName='AimsClient.'
    _styledir = join(dirname(abspath(__file__)),'styles')

    def __init__( self, iface ):
        QObject.__init__(self)
        self._iface = iface
        self._statusBar = iface.mainWindow().statusBar()
        self._adrLayer = None
        self._sadLayer = None
        self._rclLayer = None
        self._parLayer = None

    def layerId( self, layer ):
        idprop = self._propBaseName + 'Id' 
        return str(layer.customProperty(idprop))

    def setLayerId( self, layer, id ):
        if not isinstance(id,str): 
            #aimslog.error('Invalid Layer ID {}={}'.format(layer,id))
            raise InvalidParameterException()
        idprop = self._propBaseName + 'Id'
        layer.setCustomProperty(idprop,id)

    def layers( self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == layer.VectorLayer and self.layerId(layer):
                yield layer

    def findLayer( self, name ): 
        for layer in self.layers():
            if self.layerId(layer) == name:
                return layer
        return None

    def installLayer( self, id, schema, table, key, estimated, where, displayname ):
        layer = self.findLayer(id)
        if layer:
            legend = self._iface.legendInterface()
            if not legend.isLayerVisible(layer):
                legend.setLayerVisible(layer, True)
            return layer
        self._statusBar.showMessage("Loading layer " + displayname )
        layer = None
        try:
            uri = QgsDataSourceURI()
            uri.setConnection(Database.host(),Database.port(),Database.database(),Database.user(),Database.password())
            uri.setDataSource(schema,table,'shape',where,key)
            uri.setUseEstimatedMetadata( estimated ) #2.8 affected by Bug report #12478
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

    def installRefLayers( self ):
        schema = Database.aimsSchema()
        # Join rcl and road name (via rna) for labeling purposes. NOTE - only P1 rna used
        sql = '''(Select rcl.roadcentrelineid, rcl.roadcentrelinealtid,rcl.noncadastralroad, 
                  rcl.shape, rcl.organisationid, rn.roadname, rt.roadtypename  
                FROM reference.roadcentreline rcl JOIN reference.roadnameassociation rna 
                ON rcl.roadcentrelineid = rna.roadcentrelineid 
                JOIN reference.roadname rn ON rn.roadnameid =  rna.roadnameid 
                JOIN reference.roadtype rt on rn.roadtypeid = rt.roadtypeid
                WHERE rcl.roadcentrelinestatus = 'CURR' AND rna.rnapriority = 1 AND rn.roadnamestatus = 'CURR')'''
        
        self.installLayer( 'rcl', '', sql, 'roadcentrelineid', True, "",'Roads' )        
        self.installLayer( 'par', schema, 'parcel', 'id', True, 
                            "parceltype not in ('ROAD','RLWY')",'Parcels' )
