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
#from AddressList import AddressList
#from AimsClient.Address import Address

class Controller( QObject ):
    def __init__( self ):
        QObject.__init__(self)
        self._currentAddress = None
        #if Controller._instance == None:
        #    Controller._instance = self