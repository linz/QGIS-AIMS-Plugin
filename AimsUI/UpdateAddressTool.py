import sys
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from AimsUI.AimsClient.Gui.Ui_ComfirmSelection import Ui_ComfirmSelection
from AimsUI.AimsClient.Gui.UiUtility import UiUtility
from AimsUI.AimsClient.Gui.ResponseHandler import ResponseHandler
from AIMSDataManager.Address import Position
from AIMSDataManager.AimsUtility import FeedType, FEEDS


class UpdateAddressTool(QgsMapToolIdentify):
    """
    Tool for updating published AIMS Features
    """ 
    
    def __init__(self, iface, layerManager, controller):
        """
        Intialise Update Address Tool
        
        @param iface: QgisInterface Abstract base class defining interfaces exposed by QgisApp  
        @type iface: Qgisinterface Object
        @param layerManager: Plugins layer manager
        @type  layerManager: AimsUI.LayerManager()
        @param controller: Instance of the plugins controller
        @type  controller: AimsUI.AimsClient.Gui.Controller()
        """
       
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._layers = layerManager
        self._controller = controller
        self.highlight = self._controller.highlighter
        self._canvas = iface.mapCanvas()
        self.activate()

    def activate(self):
        """
        Activate Update Address Tool
        """
        
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click map to update feature")
        self.cursor = QCursor(Qt.CrossCursor)
        self.parent().setCursor(self.cursor)
    
    def deactivate(self):
        """
        Deactivate Update Address Tool
        """
        
        sb = self._iface.mainWindow().statusBar()
        sb.clearMessage()
    
    def setEnabled(self, enabled):
        """ 
        When Tool related QAction is checked/unchecked
        Activate / Disable the tool respectively

        @param enabled: Tool enabled. Boolean value
        @type enabled: boolean
        """
           
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()
    
    def setMarker(self, coords):
        """
        Place marker on canvas to indicate the feature to be updated

        @param coords: QgsPoint
        @type coords: QgsPoint
        """

        self.highlight.setAddress(coords)

    def canvasReleaseEvent(self, mouseEvent):
        """
        Identify the AIMS Feature(s) the user clicked

        @param mouseEvent: QtGui.QMouseEvent
        @type mouseEvent: QtGui.QMouseEvent
        """

        self._feature = None
        self._iface.setActiveLayer(self._layers.addressLayer())
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        
        if len(results) == 0: 
            return
        elif len(results) == 1:
            # initialise an address object and populate from selected feature

            self._feature = self._controller.uidm.singleFeatureObj(results[0].mFeature.attribute('addressId'))
            
        else: # Stacked points
            identifiedFeatures=[] 
            for i in range (0,len(results)):
                identifiedFeatures.append(dict(
                fullAddress=results[i].mFeature.attribute('fullAddress'),
                addressId= results[i].mFeature.attribute('addressId')))
                
            dlg = updateAddressDialog(self._iface.mainWindow())
            updFeatures = dlg.selectFeatures(identifiedFeatures)

            if updFeatures: 
                updFeatureIds = [d['addressId'] for d in updFeatures]

                for result in results:
                    if result.mFeature.attribute('addressId') in updFeatureIds:
                        self._feature = self._controller.uidm.singleFeatureObj(result.mFeature.attribute('addressId'))
                        break
        # Open form
        if self._feature:
            # Hack to retrieve the properties missing on the
            # feature feed from the resolution feed 
            respId = int(time.time()) 
            self._controller.uidm.supplementAddress(self._feature, respId)
            self.feature = self._controller.RespHandler.handleResp(respId, FEEDS['AR'], 'supplement')
            # highlight feature             
            self.setMarker(results[0].mFeature.geometry().asPoint())
            self._controller._queues.uEditFeatureTab.setFeature('update', self._feature )
            self._controller._queues.tabWidget.setCurrentIndex(0)
            UiUtility.setEditability(self._controller._queues.uEditFeatureTab, 'update')

class updateAddressDialog(Ui_ComfirmSelection, QDialog ):
    """
    Dialog that is shown to the user if more than one feature is selected to
    allow the user to refine and confirm their selection

    @param Ui_ComfirmSelection: Ui Dialog to allow user to refine selection
    @type  Ui_ComfirmSelection: AimsUI.AimsClient.Gui.Ui_ComfirmSelection
    """
       

    def __init__( self, parent ):
        """
        Intialise dialog
        
        @param parent: Main Window
        @type  parent: QtGui.QMainWindow
        """
        
        QDialog.__init__(self,parent)
        self.setupUi(self)
    
    def selectFeatures( self, identifiedFeatures ):
        """
        Show selected features to user and return the users
        refined selection

        @param identifiedFeatures: List of dictionaries representing each selected feature
        @type  identifiedFeatures: list
        
        @return: List of dictionaries representing the refined selection
        @rtype: list
        """
        
        self.uSadListView.setList(identifiedFeatures,
                                 ['fullAddress','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.uSadListView.confirmSelection()
        return None