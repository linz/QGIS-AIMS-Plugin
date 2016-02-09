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

    def setController( self, controller ):
        import Controller
        if not controller:
            controller = Controller.instance()
        self._controller = controller

    def currentFeature(self, feature):
        pass
        #UiUtility.addObjToForm(self, self.feature)
        self.uLevelValue.setText('hi')
        self.uRoadCentrelineId.setText('000000000000000000')
    
    def getRcl(self):
        
        self._controller.startRclTool(self)