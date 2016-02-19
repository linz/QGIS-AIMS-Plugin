import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_QueueEditorWidget import Ui_QueueEditorWidget
from UiUtility import UiUtility


class QueueEditorWidget( Ui_QueueEditorWidget, QWidget ):

    warningStyle = "* { color : red; font-weight: bold }"

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        UiUtility.setFormCombos(self)
        self.uGetRclToolButton.clicked.connect(self.getRcl)         
        self.setController( controller )
        self.uAddressType.currentIndexChanged.connect(self.setEditability)

    def setController( self, controller ):
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller

    def currentFeature(self, feature):
        self.setEditability()
        
        uiElements = [ self.uWarning, self.uNotes, self.uAddressType, self.uChangeType, 
                      self.ulifeCycle, self.uLevelType, self.uLevelValue, self.uUnitType, 
                      self.uUnit, self.uPrefix, self.uBase, self.uAlpha, self.uHigh,
                      self.uExternalIdScheme, self.uExternalAddId, self.uRclId, 
                      self.uRoadPrefix, self.uRoadName, self.uRoadTypeName,
                      self.uRoadSuffix, self.uWaterName, self.uWaterRouteName,
                      self.uObjectType, self.uObjectName, self.uPositionType, 
                      self.uExtObjectIdScheme, self.uExternalObjectId, self.uValuationReference,
                      self.uCertificateOfTitle, self.uAppellation ]
        
        featProps = ['_warning', '_notes', '_components_addressType', '_components_changeType', '_components_lifecycle',
                  '_components_levelType', '_components_levelValue', '_components_unitType',  '_components_unitValue', '_components_addressNumberPrefix',
                  '_components_addressNumber', '_components_addressNumberSuffix', '_components_addressNumberHigh','_components_externalAddressIdScheme',
                  '_components_externalAddressId', '_components_roadCentrelineId', '_components_roadPrefix', '_components_roadName', '_components_roadType',
                  '_components_roadSuffix', '_components_waterName', '_components_waterRoute', '_addressedObject_objectType', '_addressedObject_objectName' '_addressedObject_positionType', 
                  '_externalObjectIdScheme', '_addressedObject_externalObjectId', '_valuationReference', '_certificateOfTitle',
                  '_appellation']
        
        for ui , prop in zip(uiElements, featProps):
            if hasattr(feature, prop):
                if isinstance(ui, QLineEdit):
                    ui.clear()
                    ui.setText(str(getattr(feature, prop)))
                if isinstance(ui, QComboBox):
                    ui.setCurrentIndex(0)
                    ui.setCurrentIndex(QComboBox.findText(ui, str(getattr(feature, prop))))
                    
    def setEditability(self):
        widgetChildern = self.findChildren(QWidget, QRegExp(r'^u.*'))
        for child in widgetChildern:
            child.setEnabled(True)
        
        if self.uAddressType.currentText() == 'Road':
            waterChildern = self.findChildren(QWidget, QRegExp(r'Water.*'))
            for child in waterChildern:
                child.clear()
                child.setDisabled(True)
                
        elif self.uAddressType.currentText() == 'Water':
            roadChildern = self.findChildren(QWidget, QRegExp(r'Road.*'))
            for child in roadChildern:
                child.clear()
                child.setDisabled(True)
    
    def getRcl(self):
        
        self._controller.startRclTool(self)