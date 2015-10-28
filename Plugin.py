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

from LayerManager import LayerManager
from CreateNewTool import CreateNewTool

class Plugin( ):

    Name = "AimsClient"
    LongName="Address Information Management System Client"
    Version="1.0"
    QgisMinimumVersion="2.0"
    Author="splanzer@linz.govt.nz <Simon Planzer>"
    PluginUrl="tbc"
    Description="Client for loading address information into the Address Information Management System (AIMS)"
    SettingsBase="AimsClient/"

    def __init__( self, iface ):        
        self._iface = iface
        self._statusbar = iface.mainWindow().statusBar()
        self._layers = None
        
    def initGui(self):
        self._layers = LayerManager(self._iface)
        
        # Main address editing window
        self._loadaction = QAction(QIcon(":/plugins/AimsClient/loadaddress.png"), 
            "AIMS Client", self._iface.mainWindow())
        self._loadaction.setWhatsThis("Open the AIMS Client")
        self._loadaction.setStatusTip("Open the AIMS Client")
        self._loadaction.triggered.connect( self.loadEditor )
                       
        # Create new address
        self._createnewaddressaction = QAction(QIcon(":/plugins/AimsClient/newaddresspoint.png"), 
            "Create new address", self._iface.mainWindow())
        self._createnewaddressaction.setWhatsThis("place point for new address")
        self._createnewaddressaction.setStatusTip("place point for new address")
        self._createnewaddressaction.setEnabled(False)
        self._createnewaddressaction.triggered.connect( self.startNewAddressTool )
       
        # Add to own toolbar
        self._toolbar = self._iface.addToolBar("AIMS Client")
        self._toolbar.addAction(self._createnewaddressaction)

        # Add actions to menu and toolbar icon
        self._iface.addToolBarIcon(self._loadaction)
        self._iface.addPluginToMenu("&AIMS Client", self._loadaction)
        self._iface.addPluginToMenu("&AIMS Client", self._createnewaddressaction)

    def unload(self):      
        self._iface.mainWindow().removeToolBar(self._toolbar)
        self._iface.removeToolBarIcon(self._loadaction)
        self._iface.removePluginMenu("&AIMS Client",self._loadaction)
        self._iface.removePluginMenu("&AIMS Client", self._createnewaddressaction)
  
    # Connect to "open aims client"
    def loadEditor( self ):
        self.startNewAddressTool()
        self._layers.installRefLayers()
            
    def startNewAddressTool( self ):
        self._createnewaddressaction.setEnabled(True)
