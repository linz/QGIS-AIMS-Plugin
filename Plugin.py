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
from AimsUI.AimsClient.Gui.Controller import Controller
from AimsUI import AimsLogging
import threading # temp - debugging only
from qgis.core import QgsRectangle
# Temp, Dev only - debugging
try:
    import sys
    sys.path.append('/opt/eclipse/plugins/org.python.pydev_4.4.0.201510052309/pysrc')
    from pydevd import settrace, GetGlobalDebugger
    settrace()

except:
    pass

class Plugin(object):
    ''' Initiate the AIMS plugin'''
    #try:      
    #    SettingsBase="QGIS-AIMS-Plugin/"
    #except:
    SettingsBase=" AIMS_Plugin_threaded/" # TEMP testing
        
    def __init__(self, iface):
        ''' Initialise the Controller  '''
        self.iface = iface
        self.controller = Controller(iface)
        
    def initGui(self):
        ''' Set up the Plugin's GUI '''
        self.controller.initGui()
        
    def unload(self): 
        ''' Remove the plugins UI components '''
        self.controller.unload()
