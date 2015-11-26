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
#sys.path.append('.qgis2/python/plugins/QGIS-AIMS-Plugin')

from PyQt4.QtCore import *
from AimsUI.AimsClient.Address import Address
from AimsUI.LayerManager import LayerManager
from AimsUI.AimsClient.Config import ConfigReader
from NewAddressDialog import NewAddressDialog
from AimsUI.AimsClient.AimsApi import AimsApi


class Controller(QObject):
    '''For future use with multiple objects requesting address/layers etc'''
    _instance = None
    
    def __init__(self, iface, layerManager):
        
        QObject.__init__(self)
        _config = ConfigReader()
        self._iface = iface
        self._layers = layerManager
        self._api = AimsApi()
        self._user = _config.configSectionMap('user')['name']
        
        if Controller._instance == None:
            Controller._instance = self
        
    
    def initialiseAddressObj(self): 
        return Address(self._user)

    def newAddress(self, payload):   
        return self._api.changefeedAdd(payload)
    
    def retireAddress(self, retireFeatures):
        ''' retireFeatures == [] to account for single and multiple
        method iterates through the list of retirement payloads and pass to retire API '''
        for retiree in retireFeatures:
            return self._api.changefeedRetire(retiree) # reinitialising each time
    
    def loadRefLayers (self, iface):
        #self._layers = LayerManager(iface)
        self._layers.installRefLayers()
    
    def refreshlayer(self):
        pass

