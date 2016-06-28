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

    def __init__( self, parent=None, controller=None ):
        """
        Intialise Queue Feature UI components
        """
        
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self.feature = None
        #self.uiToObjMappings = self.formObjMappings() < -- redundant? 4/3/16
        UiUtility.setFormCombos(self)
        self.uGetRclToolButton.clicked.connect(self.getRcl)      
        self.uUpdatePosButton.clicked.connect(self.updatePosition)     
        self.setController( controller )
        self.uAddressType.currentIndexChanged.connect(self.setEditability)
        self.setWarningColour()
    
        # Val Ref, Cert Title and App have been temp taken out of scope
        hide = (self.lAppellation, self.uAppellation, self.uCertificateOfTitle, 
                self.lCertTitle, self.uValuationReference, self.lValref)
        
        for uiElement in hide:
            uiElement.hide()
        
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
    
    def setWarningColour( self ):
        """
        Define the warning stylisation
        """
        
        style = ""
        style = self.warningStyle
        self.uWarning.setStyleSheet(style)
         
    def currentFeatureToUi(self, feature):
        """
        Populate the Edit Feature Form when the user selects an AIMS Feature 
        
        @param feature: AIMS Feature
        @type  feature: AIMSDataManager.Address()
        AIMSDataManager.Address
        """
        
        self.feature = feature
        UiUtility.featureToUi(self, 'r'+self.feature._changeType)
    
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
        