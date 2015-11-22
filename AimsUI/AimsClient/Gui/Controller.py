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
import sys
from os.path import dirname, abspath
#sys.path.append('.qgis2/python/plugins/aims')

from PyQt4.QtCore import *
from AimsUI.AimsClient.Address import Address
from AimsUI.LayerManager import LayerManager


class Controller(QObject):
    '''For future use with multiple objects requesting address/layers etc'''
    _instance = None
    
    def __init__(self):
        self._layers = None
        QObject.__init__(self)
        if Controller._instance == None:
            Controller._instance = self
    
    def initialiseNewAddress(self): #rename initialiseAddressObj
        return Address()

    def destroyAddObj(self, address):   
        pass
    
    def loadRefLayers (self, iface):
        self._layers = LayerManager(iface)
        self._layers.installRefLayers()
    
    def refreshlayer(self):
        pass
