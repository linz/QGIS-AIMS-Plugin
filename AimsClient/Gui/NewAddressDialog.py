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
import re

from Ui_NewAddressDialog import Ui_NewAddressDialog
import Controller

class NewAddressDialog(Ui_NewAddressDialog, QDialog):
    
    @classmethod
    def newAddress( cls, parent=None):
        dlg = NewAddressDialog( parent )
        dlg.exec_()
    
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setupUi(self)

     
        # Connect uSubmitAddressButton to function
        #self.uSubmitAddressButton.clicked.connect(self.submitAddress)
        #self.uFullNum.textChanged.connect(self.FullNumChanged)
    
    def submitAddress( self ):
        ''' take users input from form and submit to AIMS API '''
        # Need to pass to validation function prior to the below
        pass
            
    def FullNumChanged(self):
        ''' sets address components based 
        on users supplied full address '''
        #reg ex
        self.prefixLabel.setText('')
        self.flatLabel.setText('')
        self.baseLabel.setText('')
        self.alphaLabel.setText('')
