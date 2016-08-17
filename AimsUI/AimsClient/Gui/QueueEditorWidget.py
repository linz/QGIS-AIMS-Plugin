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

import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_QueueEditorWidget import Ui_QueueEditorWidget
from UiUtility import UiUtility




class QueueEditorWidget( Ui_QueueEditorWidget, QWidget ):
    """
    QWidget hosting the user fields used to edit an AIMS Feature
    
    @param Ui_QueueEditorWidget: QWidget hosting the user fields used to edit an AIMS Feature
    @type  Ui_QueueEditorWidget: QWidget
    
    @param QWidget: Inherits from QtGui.QWidget
    """

    warningStyle = "* { color : red; font-weight: bold }"
    fulladdressStyle = "* { color : black; font-weight: bold }"

    def __init__( self, parent=None, controller=None ):
        """
        Intialise Queue Feature UI components
        """
        
        QWidget.__init__( self, parent )
        self.setupUi(self)
        
        #icons for buttons
        moveIcon = QIcon()
        moveIcon.addPixmap(QPixmap(":/plugins/QGIS-AIMS-Plugin/resources/moveaddress.png"), QIcon.Normal, QIcon.On)
        self.uUpdatePosButton.setIcon(moveIcon)
        
        getRclIcon = QIcon()
        getRclIcon.addPixmap(QPixmap(":/plugins/QGIS-AIMS-Plugin/resources/selectrcl.png"), QIcon.Normal, QIcon.On)
        self.uGetRclToolButton.setIcon(getRclIcon)
        
        self.feature = None
        self.featureId = None
        UiUtility.setFormCombos(self)
        self.uGetRclToolButton.clicked.connect(self.getRcl)      
        self.uUpdatePosButton.clicked.connect(self.updatePosition)     
        self.setController(controller)
        self.uAddressType.currentIndexChanged.connect(self.setEditability)
        self.setStyle()
        
        # limit user inputs
        UiUtility.formMask(self)
        
        #Ext Object temp taken out of scope
        hide = (self.uExternalObjectId, self.uExtObjectIdScheme, 
                 self.lExtObjectIdScheme,  self.lExternalObjectId)
        for uiElement in hide:
            uiElement.hide()
        
        # connect all editing ui elements to 
        for uiElement, v in UiUtility.uiObjMappings.iteritems():    
            if isinstance(getattr(self, uiElement), QLineEdit):
                getattr(self, uiElement).textEdited.connect(getattr(self, v[1]))
            elif isinstance(getattr(self, uiElement), QComboBox):
                getattr(self, uiElement).activated.connect(getattr(self, v[1]))

    def setController( self, controller ):
        """
        Assign the controller to the QueueWditorWidget
        
        @param controller: controller Instance      
        @type  AimsUI.AimsClient.Gui.Controller() Instance
        """
        
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller
    
    def setStyle( self ):
        """
        Define the warning stylisation
        """
        
        style = ""
        self.uWarning.setStyleSheet(self.warningStyle)
         
    def currentFeatureToUi(self, feature):
        """
        Populate the Edit Feature Form when the user selects an AIMS Feature 
        
        @param feature: AIMS Feature
        @type  feature: AIMSDataManager.Address()

        AIMSDataManager.Address
        """
        
        if feature:
            self.feature = feature
            UiUtility.featureToUi(self, 'r'+self.feature._changeType)
            if self.featureId == self.feature._changeId:
                self.reinstateEdits()
            else:
                self.clearEdits()
            self.featureId = self.feature._changeId
            
    def clearForm(self):
        UiUtility.clearForm(self)
    
    def setEditability(self):
        """ 
        Set the editability of each user input field embedded with the feature 
        form based on the user supplied address class
        """ 
        
        UiUtility.setEditability(self)
   
    def getRcl(self):
        """ 
        Enable the Road Centre Line Tool allowing the user to 
        Populate the edit feature form with road information 
        """   
        self._controller.startRclTool(self)
    
    def updatePosition(self):
        """ 
        Enable the UpdateReviewPosTool and pass the current feautre to it
        for position editing
        """
        
        self._controller.startUpdateReviewPosTool(self.feature)
    
    def reinstateEdits(self):
        """
        If a Data Manager data supply occurs while editing 
        reinstate the user input values
        """
        
        for uiElement, v in UiUtility.uiObjMappings.iteritems():
            if hasattr(self, v[0]):
                if isinstance(getattr(self, uiElement), QLineEdit) and getattr(self,  v[0]):
                    getattr(self, uiElement).setText(getattr(self, v[0]))
                elif isinstance(getattr(self, uiElement), QComboBox) and getattr(self, v[0]):
                    getattr(self, uiElement).setCurrentIndex(QComboBox.findText(getattr(self, uiElement),getattr(self, v[0])))


                    #uiElement.setCurrentIndex(QComboBox.findText(uiElement, prop))
    def clearEdits(self):
        """
        set all temp properties to None
        """
        
        for v in UiUtility.uiObjMappings.values():
            setattr(self, v[0], None)
        
    # Setters used to track user edit between saves
    def setAddressType(self):     
        self._components_addressType = self.uAddressType.currentText()
    def setWarnings(self):
        self._warning = self.uWarning.text()
    def setSourceReason(self):
        self._workflow_sourceReason = self.uNotes.text()
    def setLifecycle(self):
        self._components_lifecycle = self.ulifeCycle.currentText()
    def setLevelType(self): 
        self._components_levelType = self.uLevelType.currentText()
    def setLevelValue(self): 
        self._components_levelValue = self.uLevelValue.text()
    def setUnitType(self):
        self._components_unitType = self.uUnitType.currentText()
    def setUnitValue(self):
        self._components_unitValue = self.uUnit.text()
    def setAddressNumberPrefix(self):
        self._components_addressNumberPrefix = self.uPrefix.text()
    def setAddressNumber(self):
        self._components_addressNumber = self.uBase.text()
    def setAddressNumberSuffix(self):
        self._components_addressNumberSuffix = self.uAlpha.text()
    def setAddressNumberHigh(self):
        self._components_addressNumberHigh = self.uHigh.text()
    def setExternalAddressIdScheme(self):
        self._components_externalAddressIdScheme = self.uExternalAddressIdScheme.text()
    def setExternalAddressId(self):
        self._components_externalAddressId = self.uExternalAddId.text()
    def setRoadCentrelineId(self):
        self._components_roadCentrelineId = self.uRclId.text()
    def setRoadPrefix(self):
        self._components_roadPrefix = self.uRoadPrefix.text()
    def setRoadName(self): 
        self._components_roadName = self.uRoadName.text()
    def setRoadType(self):
        self._components_roadType = self.uRoadTypeName.text()
    def setRoadSuffix(self): 
        self._components_roadSuffix = self.uRoadSuffix.text()
    def setWaterName(self): 
        self._components_waterName = self.uWaterName.text()
    def setWaterRoute(self):
        self._components_waterRoute = self.uWaterRouteName.text()
    def setAddObjectType(self):
        self._addressedObject_objectType = self.uObjectType.currentText()
    def setAddObjectName(self):
        self._addressedObject_objectName = self.uObjectName.text()
    def setExternalObjectIdScheme(self):
        self._addressedObject_externalObjectIdScheme = self.uExtObjectIdScheme.text()
    def setExternalObjectId(self):
        self._addressedObject_externalObjectId = self.uExternalObjectId.text()
    def setValuationReference(self):
        self._addressedObject_valuationReference = self.uValuationReference.text()
    def setCertificateOfTitle(self):
        self._addressedObject_certificateOfTitle = self.uCertificateOfTitle.text()
    def setAppellation(self):
        self._addressedObject_appellation = self.uAppellation.text()
    def setMeshblock(self):
        self._codes_meshblock = self.uMblkOverride.text()
      
    