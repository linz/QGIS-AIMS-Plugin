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
from AimsUI.AimsClient.Gui.AimsConfigureDialog import AimsConfigureDialog
ACD = AimsConfigureDialog()

from AimsUI.AimsClient.Gui.Controller import Controller
from AimsUI import AimsLogging
from qgis.core import QgsRectangle


class Plugin(object):
    ''' Initiate the AIMS plugin'''

    SettingsBase="QGIS-AIMS-Plugin/"

    def __init__(self, iface):
        """ Initialise the Controller  """
        self.iface = iface
        ACD.setIface(self.iface)
        self.controller = Controller(iface, ACD)
        
    def initGui(self):
        ''' Set up the Plugin's GUI '''
        self.controller.initGui()

    def unload(self): 
        ''' Remove the plugins UI components '''
        self.controller.unload()
