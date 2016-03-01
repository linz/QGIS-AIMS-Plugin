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
        self.uiToObjMappings = self.formObjMappings()
        UiUtility.setFormCombos(self)
        self.uGetRclToolButton.clicked.connect(self.getRcl)         
        self.setController( controller )
        self.uAddressType.currentIndexChanged.connect(self.setEditability)
    
    def setController( self, controller ):
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller

    def formObjMappings(self):
        ''' {uiComponent[obj.property, settermethod]} '''
        
        return  {'uWarning':['_warning','setWarnings'],
                'uNotes':['_workflow_sourceReason','setSourceReason'],
                'uAddressType':['_components_addressType','setAddressType'], 
                'ulifeCycle':['_components_lifecycle','setLifecycle'],   
                'uLevelType':['_components_levelType','setLevelType'], 
                'uLevelValue':['_components_levelValue','setLevelValue'], 
                'uUnitType':['_components_unitType','setUnitType'],
                'uUnit':['_components_unitValue','setUnitValue'],
                'uPrefix':['_components_addressNumberPrefix','setAddressNumberPrefix'],
                'uBase':['_components_addressNumber','setAddressNumber'],
                'uAlpha':['_components_addressNumberSuffix','setAddressNumberSuffix'],
                'uHigh':['_components_addressNumberHigh','setAddressNumberHigh'],
                'uExternalIdScheme':['_components_externalAddressIdScheme','setExternalAddressIdScheme'],
                'uExternalAddId':['_components_externalAddressId','setExternalAddressId'], 
                'uRclId':['_components_roadCentrelineId','setRoadCentrelineId'],
                'uRoadPrefix':['_components_roadSuffix','setRoadSuffix'],
                'uRoadName':['_components_roadName','setRoadName'], 
                'uRoadTypeName':['_components_roadType','setRoadType'],   
                'uRoadSuffix':['_components_roadSuffix','setRoadSuffix'], 
                'uWaterName':['_components_waterName','setWaterName'], 
                'uWaterRouteName':['_components_waterRoute','setWaterRoute'],
                'uObjectType':['_addressedObject_objectType','setObjectType'],
                'uObjectName':['_addressedObject_objectName','setObjectName'],
                'uExtObjectIdScheme':['_addressedObject_externalObjectIdScheme','setExternalObjectIdScheme'],
                'uExternalObjectId':['_addressedObject_externalObjectId','setExternalObjectId'],
                'uValuationReference':['_addressedObject_valuationReference','setValuationReference'],
                'uCertificateOfTitle':['addressedObject_certificateOfTitle','setCertificateOfTitle'], 
                'uAppellation':['_addressedObject_appellation','setAppellation']}
    
    def currentFeatureToUi(self, feature):
        self.setEditability()
        for uiElement, objProp in self.uiToObjMappings.items():
            if hasattr(feature, objProp[0]):
                uiElement = getattr(self, uiElement)
                if isinstance(uiElement, QLineEdit):
                    uiElement.clear()
                    uiElement.setText(str(getattr(feature, objProp[0])))
                if isinstance(uiElement, QComboBox):
                    uiElement.setCurrentIndex(0)
                    uiElement.setCurrentIndex(QComboBox.findText(uiElement, str(getattr(feature, objProp[0]))))
     
        for uiElement, objProp in self.uiToObjMappings.items():
            uiElement = getattr(self, uiElement)
            if uiElement != '' and uiElement != 'NULL':
                setter = getattr(feature, objProp[1])
                if isinstance(uiElement, QLineEdit):
                    setter(uiElement.text())
                if isinstance(uiElement, QComboBox):
                    setter(uiElement.currentText())

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