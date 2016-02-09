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
import sys
import Resources

from os.path import dirname, abspath
#sys.path.append('.qgis2/python/plugins/QGIS-AIMS-Plugin') 
sys.path.append('.qgis2/python/plugins/AIMS_Plugin_threaded') #temp

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from DockWindow import DockWindow
from AimsUI.AimsClient.Address import Address
from AimsUI.LayerManager import LayerManager
from NewAddressDialog import NewAddressDialog
from AimsUI.DelAddressTool import DelAddressTool
from AimsUI.MoveAddressTool import MoveAddressTool
from AimsUI.CreateNewAddressTool import CreateNewAddressTool
from AimsUI.UpdateAddressTool import UpdateAddressTool
from AimsUI.LineageTool import LineageTool
from AimsUI.GetRclTool import GetRcl
from AimsUI.AimsClient.AimsApi import AimsApi
from AimsQueueWidget import AimsQueueWidget
from AddressList import AddressList

from AIMSDataManager.DataManager import DataManager

from AimsUI import AimsLogging
from AimsUI.AimsLogging import Logger
aimslog = Logger.setup()

class Controller(QObject):
    '''For future use with multiple objects requesting address/layers etc'''
    _instance = None
    
    def __init__(self, iface):
        QObject.__init__(self)
        self._iface = iface
        self.api = AimsApi()
        self.user = self.api.user
        self._alist = AddressList()
        self._currentAddress = None
        self._queues = None
        self._currentMapTool = None
        self.actions = []
        if Controller._instance == None:
            Controller._instance = self
        
        self.dataManager = DataManager()
      
        aimslog.debug(iface)
        
        # set srs
        self._displayCrs = QgsCoordinateReferenceSystem()
        self._displayCrs.createFromOgcWmsCrs('EPSG:4167') 
        iface.mapCanvas().mapSettings().setDestinationCrs(self._displayCrs)

    def initGui(self):
        self._layers = LayerManager(self._iface, self)
                
        # Build an action list from QGIS navigation toolbar
        actionList = self._iface.mapNavToolToolBar().actions()
        self.actions = self._iface.mapNavToolToolBar().actions()
        # Main address editing window
        self._loadaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/loadaddress.png'), 
            'QGIS-AIMS-Plugin', self._iface.mainWindow())
        self._loadaction.setWhatsThis('Open the QGIS-AIMS-Plugin')
        self._loadaction.setStatusTip('Open the QGIS-AIMS-Plugin')
        self._loadaction.triggered.connect(self.loadQueues)
        self._loadaction.triggered.connect( self.loadLayers )
        
        # Create new address tool
        self._createnewaddressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/newaddresspoint.png'), 
            'Create AIMS Feature', self._iface.mainWindow())
        self._createnewaddressaction.setWhatsThis('Create AIMS Feature')
        self._createnewaddressaction.setStatusTip('Create AIMS Feature')
        self._createnewaddressaction.setEnabled(False)
        self._createnewaddressaction.setCheckable(True)
        self._createnewaddressaction.triggered.connect( self.startNewAddressTool )
        self._createnewaddresstool = CreateNewAddressTool( self._iface, self._layers, self)
        self._createnewaddresstool.setAction( self._createnewaddressaction )
        self.actions.append(self._createnewaddressaction)
        
        # Delete address point
        self._deladdressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/deleteaddress.png'), 
            'Delete AIMS Feature', self._iface.mainWindow())
        self._deladdressaction.setWhatsThis('Delete AIMS Feature')
        self._deladdressaction.setStatusTip('Delete AIMS Feature')
        self._deladdressaction.setEnabled(False)
        self._deladdressaction.setCheckable(True)
        self._deladdressaction.triggered.connect( self.startDelAddressTool )
        self._deladdtool = DelAddressTool( self._iface, self._layers, self)
        self._deladdtool.setAction( self._deladdressaction )        
        self.actions.append(self._deladdressaction)
        
        # Move address
        self._moveaddressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/moveaddress.png'), 
            'Move AIMS Feature(s)', self._iface.mainWindow())
        self._moveaddressaction.setWhatsThis('Move AIMS Feature(s)')
        self._moveaddressaction.setStatusTip('Move AIMS Feature(s)')
        self._moveaddressaction.setEnabled(False)
        self._moveaddressaction.setCheckable(True)
        self._moveaddressaction.triggered.connect( self.startMoveAddressTool )
        self._moveaddtool = MoveAddressTool( self._iface, self._layers, self)
        self._moveaddtool.setAction( self._moveaddressaction )      
        self.actions.append(self._moveaddressaction)
        
        # Update address
        self._updateaddressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/updateaddress.png'), 
            'Update AIMS Feature', self._iface.mainWindow())
        self._updateaddressaction.setWhatsThis('Update AIMS Feature')
        self._updateaddressaction.setStatusTip('Update AIMS Feature')
        self._updateaddressaction.setEnabled(False)
        self._updateaddressaction.setCheckable(True)
        self._updateaddressaction.triggered.connect( self.startUpdateAddressTool )
        self._updateaddtool = UpdateAddressTool( self._iface, self._layers, self)
        self._updateaddtool.setAction( self._updateaddressaction )  
        self.actions.append(self._updateaddressaction)
                    
        # RCL tools -- Not a QAction as triggered from many palaces but not the toolbar
        self._rcltool = GetRcl(self._iface, self._layers, self, parent = None)
       
        # Address lineage
        self._lineageaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/lineage.png'), 
            'Build Lineage Relationships Between Features', self._iface.mainWindow())
        self._lineageaction.setWhatsThis('Build Lineage Relationships Between Features')
        self._lineageaction.setStatusTip('Build Lineage Relationships Between Features')
        self._lineageaction.setEnabled(False)
        self._lineageaction.setCheckable(True)
        self._lineagetool = LineageTool( self._iface, self._layers, self)
        self._lineageaction.triggered.connect(self._lineagetool.setEnabled)
        self.actions.append(self._lineageaction)
        
        # Add to own toolbar
        self._toolbar = self._iface.addToolBar('QGIS-AIMS-Plugin')
        self._toolbar.addAction(self._createnewaddressaction)
        self._toolbar.addAction(self._deladdressaction)
        self._toolbar.addAction(self._updateaddressaction)
        self._toolbar.addAction(self._moveaddressaction)
        self._toolbar.addAction(self._lineageaction)
        
        # Add actions to menu and toolbar icon
        self._iface.addToolBarIcon(self._loadaction)
        self._iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._loadaction)
        self._iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._createnewaddressaction)
        self._iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._deladdressaction)
        self._iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._updateaddressaction)
        self._iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._moveaddressaction)
        
        # Make useful connections
        self._layers.addressLayerAdded.connect(self.enableAddressLayer)
        self._layers.addressLayerRemoved.connect(self.disableAddressLayer)
        # capture maptool selection changes
        QObject.connect( self._iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.mapToolChanged)

        # Add actions from QGIS attributes toolbar (handling QWidgetActions)
        tmpActionList = self._iface.attributesToolBar().actions()
        for action in tmpActionList:
            if isinstance(action, QWidgetAction):
                actionList.extend( action.defaultWidget().actions() )
            else:
                actionList.append( action )
        # ... could add other toolbars' action lists...

        # Build a group with actions from actionList
        group = QActionGroup( self._iface.mainWindow() )
        group.setExclusive(True)
        for qgisAction in actionList:
            group.addAction( qgisAction )

        # Add our own actions
        for action in self.actions:
            group.addAction( action )
    
    def mapToolChanged(self):
        if isinstance(self._iface.mapCanvas().mapTool(), GetRcl) == False:          
            self._currentMapTool = self._iface.mapCanvas().mapTool()

    # Plugin Management 
    def enableAddressLayer(self, layer):
        ''' enable tools that are dependent on the Address Layer
            only when the address layer exists '''
        self._deladdressaction.setEnabled(True)
        self._createnewaddressaction.setEnabled(True)
        self._moveaddressaction.setEnabled(True)
        self._updateaddressaction.setEnabled(True)
        self._lineageaction.setEnabled(True)
        
    def disableAddressLayer(self):
        ''' disable tools that are dependent on the Address Layer
            when the address does not exists '''
        self._deladdressaction.setEnabled(False)
        self._createnewaddressaction.setEnabled(False)
        self._moveaddressaction.setEnabled(False)
        self._updateaddressaction.setEnabled(False)
        self._lineageaction.setEnabled(False)

    def unload(self):
        if self._queues:
            self._queues.close()
            self._queues = None 
        self._iface.mainWindow().removeToolBar(self._toolbar)
        self._iface.removeToolBarIcon(self._loadaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin',self._loadaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin', self._createnewaddressaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin', self._deladdressaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin', self._updateaddressaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin', self._moveaddressaction)
        self._iface.removePluginMenu('&QGIS-AIMS-Plugin', self._lineageaction)

    def loadQueues( self ):
        ''' load the queue widgets '''
        queues = self.Queues()
        if not queues.isVisible():
            queues.parent().show()
               
    def Queues(self):
        if not self._queues:
            queues = AimsQueueWidget( self._iface.mainWindow(), self )
            DockWindow(self._iface.mainWindow(),queues,"AimsQueues","Aims Queues")
            self._queues = queues
        return self._queues
    
    def loadLayers(self):
        self._layers.initialiseExtentEvent()
        self._layers.installRefLayers()
    
    def setPreviousMapTool(self):
        ''' this allows for roll back to the maptool that called get rcl
        for a better ux'''
        self._iface.mapCanvas().setMapTool(self._currentMapTool)
        
    def startNewAddressTool(self):
        self._iface.mapCanvas().setMapTool(self._createnewaddresstool)
        self._createnewaddresstool.setEnabled(True)
    
    def startRclTool(self, parent = None):
        self._rcltool = GetRcl(self._iface, self._layers, self, parent)
        self._iface.mapCanvas().setMapTool(self._rcltool)
        self._rcltool.setEnabled(True)
    
    def startMoveAddressTool(self):
        self._iface.mapCanvas().setMapTool(self._moveaddtool)
        self._moveaddtool.setEnabled(True)
    
    def startUpdateAddressTool(self):
        self._iface.mapCanvas().setMapTool(self._updateaddtool)
        self._updateaddtool.setEnabled(True)
        
    def startDelAddressTool(self):
        self._iface.mapCanvas().setMapTool(self._deladdtool)
        self._deladdtool.setEnabled(True)
    
    def startLineageTool(self):
        self._iface.mapCanvas().setMapTool(self._lineagetool)
        self._deladdtool.setEnabled(True) 
             
    def initialiseAddressObj(self): 
        return Address(self.user)
  
    # API Methods
    def newAddress(self, payload):   
        return self.api.changefeedAdd(payload)
    
    def retireAddress(self, retireFeatures):
        return self.api.changefeedRetire(retireFeatures) 
    
    def getFeatures(self, xMaximum, yMaximum, xMinimum, yMinimum):
        return self.api.getFeatures(xMaximum, yMaximum, xMinimum, yMinimum)
    
    def updateFeature(self, payload):
        return self.api.updateFeature(payload)
    
    def newGroup(self, payload):
        return self.api.newGroup(payload)
    
    def addToGroup(self, groupId, payload):
        return self.api.addToGroup(groupId, payload)

    def submitGroup(self, groupId, payload):
        return self.api.submitGroup(groupId, payload)
    
    def groupVersion(self, groupId):
        return self.api.groupVersion(groupId)
    
    def refreshlayer(self):
        pass
    
    def getResData(self):
        return self.api.getResData()

# Singleton instance    
def instance():
    if Controller._instance == None:
        Controller._instance = Controller()
    return Controller._instance
