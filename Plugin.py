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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.utils import *

import Resources

from AimsUI.CreateNewAddressTool import CreateNewAddressTool
from AimsUI.LayerManager import LayerManager
from AimsUI.DelAddressTool import DelAddressTool
from AimsUI.AimsClient.Gui.Controller import Controller
from AimsUI import AimsLogging

# Dev only - debugging
try:
    import sys
    sys.path.append('/opt/eclipse/plugins/org.python.pydev_4.4.0.201510052309/pysrc')
    from pydevd import settrace
    settrace()
except:
    pass

from AimsUI.AimsLogging import Logger
aimslog = Logger.setup()

class Plugin( ):

    def __init__(self, iface):        
        self._iface = iface
        self._statusbar = iface.mainWindow().statusBar()
        self._deladdtool = None
        
        aimslog.debug(iface)
        
        # set srs
        self._displayCrs = QgsCoordinateReferenceSystem()
        self._displayCrs.createFromOgcWmsCrs('EPSG:2193') 
        iface.mapCanvas().mapSettings().setDestinationCrs(self._displayCrs)

    def initGui(self):
        self._controller = Controller(iface)
        self._layers = LayerManager(self._iface, self._controller)
        # Main address editing window
        self._loadaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/loadaddress.png'), 
            'QGIS-AIMS-Plugin', self._iface.mainWindow())
        self._loadaction.setWhatsThis('Open the QGIS-AIMS-Plugin')
        self._loadaction.setStatusTip('Open the QGIS-AIMS-Plugin')
        self._loadaction.triggered.connect(self.loadEditor)
                       
        # Create new address
        self._createnewaddressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/newaddresspoint.png'), 
            'Create new address', self._iface.mainWindow())
        self._createnewaddressaction.setWhatsThis('place point for new address')
        self._createnewaddressaction.setStatusTip('place point for new address')
        self._createnewaddressaction.setEnabled(False)
        self._createnewaddressaction.triggered.connect( self.startNewAddressTool )
        self._CreateNewAddressTool = CreateNewAddressTool( self._iface, self._layers, self._controller )
        self._CreateNewAddressTool.setAction( self._createnewaddressaction )
        
        # Delete address point
        self._deladdressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/deleteaddress.png'), 
            'Delete AIMS Feature', self._iface.mainWindow())
        self._deladdressaction.setWhatsThis('Delete AIMS Feature')
        self._deladdressaction.setStatusTip('Delete AIMS Feature')
        self._deladdressaction.setEnabled(False)
        self._deladdressaction.triggered.connect( self.startDelAddressTool )
        self._deladdtool = DelAddressTool( self._iface, self._layers, self._controller )
        self._deladdtool.setAction( self._deladdressaction )
       
        # Add to own toolbar
        self._toolbar = self._iface.addToolBar('QGIS-AIMS-Plugin')
        self._toolbar.addAction(self._createnewaddressaction)
        self._toolbar.addAction(self._deladdressaction)

        # Add actions to menu and toolbar icon
        self._iface.addToolBarIcon(self._loadaction)
        self._iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._loadaction)
        self._iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._createnewaddressaction)
        self._iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._deladdressaction)
        
        # Make useful connections!
        self._layers.addressLayerAdded.connect(self.enableAddressLayer)
        self._layers.addressLayerRemoved.connect(self.disableAddressLayer)
        
    def enableAddressLayer(self, layer):
        ''' enable tools that are dependent on the Address Layer
            only when the address layer exists '''
        self._deladdressaction.setEnabled(True)
        self._createnewaddressaction.setEnabled(True)
       
    def disableAddressLayer(self):
        ''' disable tools that are dependent on the Address Layer
            when the address does not exists '''
        self._deladdressaction.setEnabled(False)
        self._createnewaddressaction.setEnabled(False)

    def unload(self):      
        self._iface.mainWindow().removeToolBar(self._toolbar)
        self._iface.removeToolBarIcon(self._loadaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin',self._loadaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin', self._createnewaddressaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin', self._deladdressaction)
        
    def loadEditor(self):
        self._layers.initialiseExtentEvent()
        self._layers.installRefLayers()
                    
    def startNewAddressTool(self):
        self._iface.mapCanvas().setMapTool(self._CreateNewAddressTool)
        self._CreateNewAddressTool.setEnabled(True)
        
    def startDelAddressTool(self):
        self._iface.mapCanvas().setMapTool(self._deladdtool)
        self._deladdtool.setEnabled(True)
