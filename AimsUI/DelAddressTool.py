################################################################################
#
# Copyright 2016 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import time

from AimsUI.AimsClient.Gui.Ui_ComfirmSelection import Ui_ComfirmSelection
from AIMSDataManager.AimsUtility import FeedType, FeedRef, FeatureType, FEEDS
from AIMSDataManager.AddressFactory import AddressFactory
from AimsUI.AimsClient.Gui.UiUtility import UiUtility

class DelAddressTool(QgsMapToolIdentify):
    """
    Tool for creating new AIMS Features
    """ 
   
    def __init__(self, iface, layerManager, controller):
        """
        Intialise New Address Tool
        
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
        self.af = {ft:AddressFactory.getInstance(FEEDS['AC']) for ft in FeedType.reverse}
        self.activate()
    
    def activate(self):
        """
        Activate Del Address Tool
        """
        
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click map to delete feature")
        self.cursor = QCursor(Qt.CrossCursor)
        self.parent().setCursor(self.cursor)
    
    def deactivate(self):
        """
        Deactivate New Address Tool
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

    def canvasReleaseEvent(self, mouseEvent):
        """
        Identify the features the user has selected for retirement

        @param mouseEvent: QtGui.QMouseEvent
        @type mouseEvent: QtGui.QMouseEvent
        """

        self._iface.setActiveLayer(self._layers.addressLayer())
        retireFeatures = []
        
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        if len(results) == 0: 
            return
        if len(results) == 1:
            retireIds = {}        
            retireIds['version'] = results[0].mFeature.attribute('version')
            retireIds['components'] = {'addressId': results[0].mFeature.attribute('addressId')}
            
            fullAddress = results[0].mFeature.attribute('fullAddress')
            
            if QMessageBox.question(self._iface.mainWindow(), 
                 "Confirm Address Retirement",
                fullAddress + "\n will be marked for retirement?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Ok ) == QMessageBox.Ok:    
                retireFeatures.append(retireIds)

        else: # Stacked points
            identifiedFeatures=[] 
            for i in range (0,len(results)):
                identifiedFeatures.append(dict(
                fullAddress=results[i].mFeature.attribute('fullAddress'),
                version= results[i].mFeature.attribute('version'),
                addressId= results[i].mFeature.attribute('addressId')
                ))
            # Open 'Retire' dialog showing selected AIMS features   
            dlg = DelAddressDialog(self._iface.mainWindow())
            retireFeatures = dlg.selectFeatures(identifiedFeatures)
        
        if retireFeatures: # else the user hit 'ok' and did not select any records            
            for retireFeature in retireFeatures:
                featureToRetire = self._controller.uidm.singleFeatureObj(retireFeature['components']['addressId'])
                featureToRetire = self.af[FeedType.CHANGEFEED].cast(featureToRetire)
                respId = int(time.time()) 
                self._controller.uidm.retireAddress(featureToRetire, respId)
                self._controller.RespHandler.handleResp(respId, FEEDS['AC'])
                
class DelAddressDialog( Ui_ComfirmSelection, QDialog ):
    """
    Dialog that is shown to the user if more than one feature selected to
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
    
    def selectionToRetirementJson(self, selected):
        """
        Reformats the list of dict that represents the users selection 
        from the dialog into a list of AIMS json objects

        @param selected: List of dictionaries representing refined selection
        @type  selected: list
        
        @return:  List of features formatted of retirement via the API
        @rtype: list
        """
        
        retireFeatures = []
        for i in selected:  
            retireIds = {}        
            retireIds['version'] = i['version']
            retireIds['components'] = {'addressId': i['addressId']}
            retireIds['address'] = i['fullAddress'] #bit of a hack. this data not required by the API but useful for error reporting
            retireFeatures.append(retireIds)
        return retireFeatures        

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
                                 ['fullAddress','version','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.selectionToRetirementJson(self.uSadListView.confirmSelection())
        return None
    