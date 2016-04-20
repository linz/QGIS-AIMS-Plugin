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

import Controller

class AimsQueueWidget( Ui_AimsQueueWidget, QWidget ):
    
    def __init__( self, parent=None, controller=None, jobid=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        