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

    warningStyle = "* { color : red; font-weight: bold }"

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self.feature = None
        #self.uiToObjMappings = self.formObjMappings() < -- redundant? 4/3/16
        UiUtility.setFormCombos(self)
        self.uGetRclToolButton.clicked.connect(self.getRcl)         
        self.setController( controller )
        self.uAddressType.currentIndexChanged.connect(self.setEditability)
        self.setWarningColour()
        
    def setController( self, controller ):
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller
    
    def setWarningColour( self ):
        style = ""
        style = self.warningStyle
        self.uWarning.setStyleSheet(style)
         
    def currentFeatureToUi(self, feature ):
        self.feature = feature
        UiUtility.featureToUi(self)
    
    def setEditability(self):
        UiUtility.setEditability(self)
   
    def getRcl(self):        
        self._controller.startRclTool(self)