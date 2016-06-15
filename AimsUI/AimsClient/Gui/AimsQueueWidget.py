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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_AimsQueueWidget import Ui_AimsQueueWidget

class AimsQueueWidget( Ui_AimsQueueWidget, QWidget ):
    """
    QT tabWidget of which all AIMS UI components is embedded within
    
    @param Ui_AimsQueueWidget: QT tabWidget UI Component of which all main AIMS UI
                               components is embedded with in
    @type  Ui_AimsQueueWidget: QT tabWidget
    
    @param QWidget: Inherits from QtGui.QWidget
    @type QWidget: QtGui.QWidget()
    """
    
    def __init__( self, parent=None ):
        """
        Initialise the QT tabWidget
    
        @param parent: QtGui.QMainWindow
        @type  parent: QtGui.QMainWindow
        """
        
        QWidget.__init__( self, parent )
        self.setupUi(self)
        