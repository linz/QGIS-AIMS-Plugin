
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.gui import *

from Ui_EditFeatureDialog import Ui_EditFeatureDialog
from AIMSDataManager.FeatureFactory import FeatureFactory
from UiUtility import UiUtility 
from AIMSDataManager.AimsUtility import FEEDS, FeedType
from AIMSDataManager.Address import Position

import time
import sys # temp
       

class EditFeatureWidget( Ui_EditFeatureDialog, QWidget ):

    def __init__(self, controller = None):
        QWidget.__init__( self )
        self.setupUi(self)
        self.setController( controller )
        self._iface = self._controller.iface
        self._layerManager = self._controller._layerManager
        self.highlight = self._controller.highlighter
        self.coords = None
        self.feature = None
 
        # Make connections
        self.uAddressType.currentIndexChanged.connect(self.setEditability)
        self.uFullNum.textEdited.connect(self.fullNumChanged)
        self.uPrefix.textEdited.connect(self.partNumChanged)
        self.uUnit.textEdited.connect(self.partNumChanged)
        self.uBase.textEdited.connect(self.partNumChanged)
        self.uHigh.textEdited.connect(self.partNumChanged)
        self.uAlpha.textEdited.connect(self.partNumChanged)
        
        self.uSubmitAddressButton.clicked.connect(self.submitAddress)
        self.uAbort.clicked.connect(self.closeDlg)
        #self.rejected.connect(self.closeDlg)
        self.uGetRclToolButton.clicked.connect(self.getRcl)
        self.af = {ft:FeatureFactory.getInstance(FEEDS['AC']) for ft in FeedType.reverse} # old method of casting
    
        
        # limit user inputs
        UiUtility.formMask(self)
        # set combo box defaults
        UiUtility.setFormCombos(self)
        # set addressType to trigger currentIndexChanged
        self.uAddressType.setCurrentIndex(QComboBox.findText(self.uAddressType,'Road'))
        self.show()
        
    def setController( self, controller ):
        '''  get an instance of plugins high level controller '''
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller
    
    def setFeature(self, parent,addInstance, coords = None ):
        self.parent = parent
        self.feature = addInstance
        self.coords = coords
        if parent == 'update':
            self.feature = self.af[FeedType.CHANGEFEED].cast(self.feature)
            UiUtility.featureToUi(self, parent) 
        elif parent == 'add' and self._controller._queues.uEditFeatureTab.uPersistRcl.isChecked():
            self._controller._rcltool.fillform()
    
    def hideMarker(self):
        self.highlight.hideNewAddress()
        self.highlight.hideRcl()
     
    def setEditability(self):
        UiUtility.setEditability(self)
            
    def getRcl(self):
        self._controller.startRclTool(self)
      
    def closeDlg (self):
        ''' close form '''
        # revert back to NewAddTool
        self._controller.setPreviousMapTool()
        # revert back to review tab 
        self._controller._queues.tabWidget.setCurrentIndex(1)
        self.hideMarker()
        
    def setPosition(self):
        coords = [self.coords.x(), self.coords.y()]
        pos = {"position":{
                    "type":'Point',
                    "coordinates":coords,
                    "crs":{
                         "type":'name',
                         "properties":{
                            "name":'urn:ogc:def:crs:EPSG::4167'
                         }
                    }
                },
                "positionType":'Unknown', # <-- need to add PT to form
                "primary":True
                }
        
        position = Position.getInstance(pos)
        self.feature.setAddressPositions(position)
    
    def raiseErrorMesg(self, mesg):
        QMessageBox.warning(self._iface.mainWindow(),"AIMS Warnings", '{0}'.format(mesg))
        
    def objCompleteness(self):
        ''' test the min required properties have been set '''
        if self.uAddressType.currentText() == 'Road' and not self.feature._components_roadName: 
            self.raiseErrorMesg('Please supply a Road Name')
            return False
        elif self.uAddressType.currentText() == 'Water' and not self.feature._components_waterRoute: 
            self.raiseErrorMesg('Please supply a Water Route Name')
            return False
        elif not self.feature._components_addressNumber:
            self.raiseErrorMesg('Please supply a Complete Address Number')
            return False
        else: return True
                
    def submitAddress(self):
        ''' take users input from form and submit to AIMS API '''
        respId = int(time.time())

        if self.parent == 'add': 
            self.setPosition() 
            UiUtility.formToObj(self)
            if not self.objCompleteness():
                return
            self.objCompleteness()
            self._controller.uidm.addAddress(self.feature, respId)
        
        elif self.parent == 'update': 
            UiUtility.formToObj(self)
            if not self.objCompleteness():
                return
            self.feature = self.af[FeedType.CHANGEFEED].cast(self.feature)            
            self._controller.uidm.updateAddress(self.feature, respId)
        
        # check the response 
        self._controller.RespHandler.handleResp(respId, FEEDS['AC'])
        # revert back to review tab 
        self._controller._queues.tabWidget.setCurrentIndex(1)
        self.hideMarker()
        
    def fullNumChanged(self, newnumber):
        UiUtility.fullNumChanged(self, newnumber)
        
    def partNumChanged(self,):
        if self.uUnit.text(): unit = self.uUnit.text()+'/' 
        else: unit = ''
        
        if self.uHigh.text(): high = '-'+self.uHigh.text()
        else: high = ''
        
        self.uFullNum.setText(self.uPrefix.text().upper()+unit+self.uBase.text()+high+self.uAlpha.text().upper())