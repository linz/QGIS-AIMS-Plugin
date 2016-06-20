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
from AIMSDataManager.DataManager import DataManager

sys.path.append('.qgis2/python/plugins/QGIS-AIMS-Plugin') 

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from DockWindow import DockWindow
from AimsUI.LayerManager import LayerManager
from AimsUI.DelAddressTool import DelAddressTool
from AimsUI.MoveAddressTool import MoveAddressTool
from AimsUI.CreateNewAddressTool import CreateNewAddressTool
from AimsUI.UpdateAddressTool import UpdateAddressTool
from AimsUI.LineageTool import LineageTool
from AimsUI.GetRclTool import GetRcl
from AimsUI.UpdateReviewPosition import UpdateReviewPosition
from AimsQueueWidget import AimsQueueWidget
from AimsUI.AimsClient.Gui.UiDataManager import UiDataManager
from AimsUI.AimsClient.Gui.ResponseHandler import ResponseHandler
from AimsUI.AimsClient.Gui.FeatureHighlighter import FeatureHighlighter

from AIMSDataManager.AimsLogging import Logger

uilog = None

class Controller( QObject ):
    ''' 
    Managers all UI Components and Plugins Tools as well as 
    initialisation and dessimnation of Singleton Instances  
        
     '''
    # log
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    _instance = None
    
    def __init__(self, iface):
        """ 
        Initialise UI Data Manager and Response Handler 
        
        @param iface: QgisInterface Abstract base class defining interfaces exposed by QgisApp  
        @type iface: Qgisinterface Object
        """
        
        QObject.__init__(self)
        self.iface = iface
        self._queues = None
        self._currentMapTool = None
        self.rclParent = None
        self.currentRevItem = None
        self.actions = []
        if Controller._instance == None:
            Controller._instance = self
        self.uidm = UiDataManager(self.iface, self)
        self.RespHandler = ResponseHandler(self.iface, self.uidm)
        
        self.refLayer = None
        self.adrlayer = None
        self.revLayer = None
        
    def initGui(self):
        """ 
        Set up UI within QGIS 
        """
        
        # set srs
        self._displayCrs = QgsCoordinateReferenceSystem()
        self._displayCrs.createFromOgcWmsCrs('EPSG:4167') 
        self.iface.mapCanvas().mapSettings().setDestinationCrs(self._displayCrs)
        
        # init layerManager
        self._layerManager = LayerManager(self.iface, self)
        # init Highlighter
        self.highlighter = FeatureHighlighter(self.iface, self._layerManager, self)
        
        # Build an action list from QGIS navigation toolbar
        actionList = self.iface.mapNavToolToolBar().actions()
        self.actions = self.iface.mapNavToolToolBar().actions()
        
        # Main address editing window
        self._loadaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/loadaddress.png'), 
            'QGIS-AIMS-Plugin', self.iface.mainWindow())
        self._loadaction.setWhatsThis('Open the QGIS-AIMS-Plugin')
        self._loadaction.setStatusTip('Open the QGIS-AIMS-Plugin')
        self._loadaction.triggered.connect(self.loadQueues)
        self._loadaction.triggered.connect(self.loadLayers)
        self._loadaction.triggered.connect(self.enableAddressLayer)
        self._loadaction.triggered.connect(self.startDM)
        
        # Create new address tool
        self._createnewaddressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/newaddresspoint.png'), 
            'Create AIMS Feature', self.iface.mainWindow())
        self._createnewaddressaction.setWhatsThis('Create AIMS Feature')
        self._createnewaddressaction.setStatusTip('Create AIMS Feature')
        self._createnewaddressaction.setEnabled(False)
        self._createnewaddressaction.setCheckable(True)
        self._createnewaddressaction.triggered.connect( self.startNewAddressTool )
        self._createnewaddresstool = CreateNewAddressTool( self.iface, self._layerManager, self)
        self._createnewaddresstool.setAction( self._createnewaddressaction )
        self.actions.append(self._createnewaddressaction)

        # Delete address point
        self._deladdressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/deleteaddress.png'), 
            'Delete AIMS Feature', self.iface.mainWindow())
        self._deladdressaction.setWhatsThis('Delete AIMS Feature')
        self._deladdressaction.setStatusTip('Delete AIMS Feature')
        self._deladdressaction.setEnabled(False)
        self._deladdressaction.setCheckable(True)
        self._deladdressaction.triggered.connect( self.startDelAddressTool )
        self._deladdtool = DelAddressTool( self.iface, self._layerManager, self)
        self._deladdtool.setAction( self._deladdressaction )        
        self.actions.append(self._deladdressaction)

        # Move address
        self._moveaddressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/moveaddress.png'), 
            'Move AIMS Feature(s)', self.iface.mainWindow())
        self._moveaddressaction.setWhatsThis('Move AIMS Feature(s)')
        self._moveaddressaction.setStatusTip('Move AIMS Feature(s)')
        self._moveaddressaction.setEnabled(False)
        self._moveaddressaction.setCheckable(True)
        self._moveaddressaction.triggered.connect( self.startMoveAddressTool )
        self._moveaddtool = MoveAddressTool( self.iface, self._layerManager, self)
        self._moveaddtool.setAction( self._moveaddressaction )      
        self.actions.append(self._moveaddressaction)
        
        # Update address
        self._updateaddressaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/updateaddress.png'), 
            'Update AIMS Feature', self.iface.mainWindow())
        self._updateaddressaction.setWhatsThis('Update AIMS Feature')
        self._updateaddressaction.setStatusTip('Update AIMS Feature')
        self._updateaddressaction.setEnabled(False)
        self._updateaddressaction.setCheckable(True)
        self._updateaddressaction.triggered.connect( self.startUpdateAddressTool )
        self._updateaddtool = UpdateAddressTool( self.iface, self._layerManager, self)
        self._updateaddtool.setAction( self._updateaddressaction )  
        self.actions.append(self._updateaddressaction)
                    
        # RCL tool -- Not a QAction as triggered from many palaces but not the toolbar
        self._rcltool = GetRcl(self.iface, self._layerManager, self)
        
        # UpdateReview Position tool -- Not a QAction as triggered initiated from review queue form
        self._updateReviewPos = UpdateReviewPosition(self.iface, self._layerManager, self)
       
        # Address lineage
        self._lineageaction = QAction(QIcon(':/plugins/QGIS-AIMS-Plugin/resources/lineage.png'), 
            'Build Lineage Relationships Between Features', self.iface.mainWindow())
        self._lineageaction.setWhatsThis('Build Lineage Relationships Between Features')
        self._lineageaction.setStatusTip('Build Lineage Relationships Between Features')
        self._lineageaction.setEnabled(False)
        self._lineageaction.setCheckable(True)
        self._lineagetool = LineageTool( self.iface, self._layerManager, self)
        self._lineageaction.triggered.connect(self._lineagetool.setEnabled)
        self.actions.append(self._lineageaction)

        # Address highlighter
        self._highlightaction = QAction(QIcon(":/plugins/QGIS-AIMS-Plugin/resources/addresshighlight.png"), 
            "Electoral address highlighter", self.iface.mainWindow())
        self._highlightaction.setWhatsThis("Turn the electoral address highlighter on or off")
        self._highlightaction.setStatusTip("Turn the electoral address highlighter on or off")     
        self._highlightaction.setText('Highlightaction')
        self._highlightaction.setEnabled(False)
        self._highlightaction.setCheckable(True)
        self._highlightaction.toggled.connect( self.highlighter.setEnabled )

        # Add to own toolbar
        self._toolbar = self.iface.addToolBar('QGIS-AIMS-Plugin')
        self._toolbar.addAction(self._createnewaddressaction)
        self._toolbar.addAction(self._deladdressaction)
        self._toolbar.addAction(self._updateaddressaction)
        self._toolbar.addAction(self._moveaddressaction)
        self._toolbar.addAction(self._lineageaction)
        self._toolbar.addAction(self._highlightaction)
        
        # Add actions to menu and toolbar icon
        self.iface.addToolBarIcon(self._loadaction)
        self.iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._loadaction)
        self.iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._createnewaddressaction)
        self.iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._deladdressaction)
        self.iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._updateaddressaction)
        self.iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._moveaddressaction)
        self.iface.addPluginToMenu('&QGIS-AIMS-Plugin', self._highlightaction)

        # capture maptool selection changes
        QObject.connect(self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.mapToolChanged)

        # Add actions from QGIS attributes toolbar (handling QWidgetActions)
        tmpActionList = self.iface.attributesToolBar().actions()
        for action in tmpActionList:
            if isinstance(action, QWidgetAction):
                actionList.extend( action.defaultWidget().actions() )
            else:
                actionList.append( action )
        # ... could add other toolbars' action lists...

        # Build a group with actions from actionList
        group = QActionGroup( self.iface.mainWindow() )
        group.setExclusive(True)
        for qgisAction in actionList:
            group.addAction( qgisAction )

        # Add our own actions
        for action in self.actions:
            if action.text() == 'Highlightaction': continue
            group.addAction( action )
   
    # Plugin Management 
    def loadQueues( self ):
        """ 
        Initialise Loading of the queue widgets into QGIS 
        """
        queues = self.Queues()
        if not queues.isVisible():
            queues.parent().show()
               
    def Queues(self):
        """ 
        Load of the queue widgets into QGIS
        @rtype: QtGui.QTabWidget  
        @return: Docked QTabWidget with UI compinets for displaying and
                 editing AIMS features
        """
        if not self._queues:
            queues = AimsQueueWidget(self.iface.mainWindow())
            DockWindow(self.iface.mainWindow(),queues,"AimsQueues","Aims Queues")
            self._queues = queues
        return self._queues
    
    def startDM(self):
        """
        Start the Data Manager only once the user enables the Plugin
        """         
        self.uidm.startDM()
    
    def enableAddressLayer(self):
        """ 
        enable tools that are dependent on the Address Layer
        only when the address layer exists 
        """
        
        self._deladdressaction.setEnabled(True)
        self._createnewaddressaction.setEnabled(True)
        self._moveaddressaction.setEnabled(True)
        self._updateaddressaction.setEnabled(True)
        self._highlightaction.setEnabled(True)
        #self._lineageaction.setEnabled(True) # to be enale once lineage tool is in scope
        
    def loadLayers(self):
        """ 
        Install map layers
        """
        
        if not self.refLayer:
            self.refLayer = self._layerManager.installRefLayers()
        if not self.adrlayer:
            self.adrlayer = self._layerManager.installAimsLayer('adr', 'AIMS Features')
        if not self.revLayer:
            self.revLayer = self._layerManager.installAimsLayer('rev', 'AIMS Review')
        self._layerManager.initialiseExtentEvent()
    
    def mapToolChanged(self):
        """ 
        Track the current maptool (excluding rcl tool) to allow 
        for rollback to previous tool when the Rcltool is deactivated 
        """
            
        if (isinstance(self.iface.mapCanvas().mapTool(), GetRcl) == False and
                isinstance(self.iface.mapCanvas().mapTool(), UpdateReviewPosition) == False):          
            self._currentMapTool = self.iface.mapCanvas().mapTool()
            # logging 
            uilog.info('*** TOOL CHANGE ***    {0} started'.format(self.iface.mapCanvas().mapTool())) 
        
    def setPreviousMapTool(self):
        """ 
        Roll back to the previous maptool
        """
        if self.iface.mapCanvas().mapTool() != self._currentMapTool:
            self.iface.mapCanvas().setMapTool(self._currentMapTool)
    
    def startNewAddressTool(self):
        """
        Enable the 'create new address' map tool 
        """
        self.iface.mapCanvas().setMapTool(self._createnewaddresstool)
        self._createnewaddresstool.setEnabled(True)
    
    def startRclTool(self, parent = None):
        """
        Enable the 'get rcl tool' map tool 
        
        @param parent: Map that enabled the RCL tool. Based on the RCL tools
                        parent, different highlighting of features is performed
        @type  parent: string     
        """
        
        self.rclParent = parent
        self.iface.mapCanvas().setMapTool(self._rcltool)
        self._rcltool.setEnabled(True)
    
    def startUpdateReviewPosTool(self, revItem = None):
        """ 
        Enable the 'get update Review position tool' map tool
        @param revItem: The current Review Item that is assigned to self.currentRevItem 
        @type  revItem: AIMSDataManager.Address.AddressResolution() Object 
        """
        
        self.currentRevItem = revItem
        self.iface.mapCanvas().setMapTool(self._updateReviewPos)
        self._rcltool.setEnabled(True)
    
    def startMoveAddressTool(self):
        """ 
        Enable the 'move address' map tool 
        """
        
        self.iface.mapCanvas().setMapTool(self._moveaddtool)
        self._moveaddtool.setEnabled(True)
    
    def startUpdateAddressTool(self):
        """ 
        Enable the "update address" map tool 
        """
        
        self.iface.mapCanvas().setMapTool(self._updateaddtool)
        self._updateaddtool.setEnabled(True)
        
    def startDelAddressTool(self):
        """
        Enable the "delete address" map tool 
        """
        
        self.iface.mapCanvas().setMapTool(self._deladdtool)
        self._deladdtool.setEnabled(True)
    
    def startLineageTool(self):
        """ 
        Enable the "lineage" map tool 
        """
        self.iface.mapCanvas().setMapTool(self._lineagetool)
        self._deladdtool.setEnabled(True) 
 
    def unload(self):
        """
        Remove Plugins UI Elements From QGIS
        """
        self._layerManager.disconnectExtentEvent()
        if self._queues:
            self._queues.close()
            self._queues = None 
        self.iface.mainWindow().removeToolBar(self._toolbar)
        self.iface.removeToolBarIcon(self._loadaction)
        self.iface.removePluginMenu('&QGIS-AIMS-Plugin',self._loadaction)
        self.iface.removePluginMenu('&QGIS-AIMS-Plugin', self._createnewaddressaction)
        self.iface.removePluginMenu('&QGIS-AIMS-Plugin', self._deladdressaction)
        self.iface.removePluginMenu('&QGIS-AIMS-Plugin', self._updateaddressaction)
        self.iface.removePluginMenu('&QGIS-AIMS-Plugin', self._moveaddressaction)
        self.iface.removePluginMenu('&QGIS-AIMS-Plugin', self._lineageaction)
        self.iface.removePluginMenu("&QGIS-AIMS-Plugin'", self._highlightaction)
    
    @pyqtSlot()
    def rDataChanged(self):
        """ 
        Review data changed, update review layer and table 
        """
        
        self._queues.uResolutionTab.refreshData()
        self._layerManager.updateReviewLayer()
    
    @pyqtSlot()
    def fDataChanged(self):
        """
        Feature data changed, update review layer and table 
        """
        
        self._layerManager.getAimsFeatures()
 
# Singleton instance    
def instance():
    """
    Return instance of the Controller
    @return: The single Controller Instance      
    @rtype: AimsUI.AimsClient.Gui.Controller() Instance
    """
    
    if Controller._instance == None:
        Controller._instance = Controller()
    return Controller._instance
