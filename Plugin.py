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

from AimsUI.LayerManager import LayerManager
from AimsUI.CreateNewAddressTool import CreateNewAddressTool
from AimsUI.AimsClient.Gui.Controller import Controller
'''
#debugging
try:
    import sys
    sys.path.append('/opt/eclipse/plugins/org.python.pydev_4.4.0.201510052309/pysrc')
    from pydevd import settrace
    settrace()
except:
    pass
'''
class Plugin( ):

    Name = "AimsClient"
    LongName="Address Information Management System Client"
    Version="1.0"
    QgisMinimumVersion="2.0"
    Author="splanzer@linz.govt.nz <Simon Planzer>"
    PluginUrl="tbc"
    Description="Client for loading address information into the Address Information Management System (AIMS)"
    SettingsBase="QGIS-AIMS-Plugin/"

    def __init__( self, iface ):        
        self._iface = iface
        self._statusbar = iface.mainWindow().statusBar()
        self._layers = None
        
        self._controller = Controller()
        
        if iface.mapCanvas().mapRenderer().hasCrsTransformEnabled():
            my_crs = QgsCoordinateReferenceSystem(4167,QgsCoordinateReferenceSystem.EpsgCrsId)
            iface.mapCanvas().mapRenderer().setDestinationCrs(my_crs)

    def initGui(self):
        self._layers = LayerManager(self._iface)
        
        # Main address editing window
        self._loadaction = QAction(QIcon(":/plugins/QGIS-AIMS-Plugin/resources/loadaddress.png"), 
            "QGIS-AIMS-Plugin", self._iface.mainWindow())
        self._loadaction.setWhatsThis("Open the QGIS-AIMS-Plugin")
        self._loadaction.setStatusTip("Open the QGIS-AIMS-Plugin")
        self._loadaction.triggered.connect( self.loadEditor )
                       
        # Create new address
        self._createnewaddressaction = QAction(QIcon(":/plugins/QGIS-AIMS-Plugin/resources/newaddresspoint.png"), 
            "Create new address", self._iface.mainWindow())
        self._createnewaddressaction.setWhatsThis("place point for new address")
        self._createnewaddressaction.setStatusTip("place point for new address")
        self._createnewaddressaction.setEnabled(False)
        self._createnewaddressaction.triggered.connect( self.startNewAddressTool )
        self._CreateNewAddressTool = CreateNewAddressTool( self._iface, self._controller )
        self._CreateNewAddressTool.setAction( self._createnewaddressaction )
       
        # Add to own toolbar
        self._toolbar = self._iface.addToolBar("QGIS-AIMS-Plugin")
        self._toolbar.addAction(self._createnewaddressaction)

        # Add actions to menu and toolbar icon
        self._iface.addToolBarIcon(self._loadaction)
        self._iface.addPluginToMenu("&QGIS-AIMS-Plugin", self._loadaction)
        self._iface.addPluginToMenu("&QGIS-AIMS-Plugin", self._createnewaddressaction)

    def unload(self):      
        self._iface.mainWindow().removeToolBar(self._toolbar)
        self._iface.removeToolBarIcon(self._loadaction)
        self._iface.removePluginMenu("&QGIS-AIMS-Plugin",self._loadaction)
        self._iface.removePluginMenu("&QGIS-AIMS-Plugin", self._createnewaddressaction)
  
    # Connect to "open QGIS-AIMS-Plugin"
    def loadEditor( self ):
        self.startNewAddressTool()
        self._layers.installRefLayers()
        self._createnewaddressaction.setEnabled(True)
            
    def startNewAddressTool( self ):
        self._iface.mapCanvas().setMapTool( self._CreateNewAddressTool )
        self._CreateNewAddressTool.setEnabled( True )
