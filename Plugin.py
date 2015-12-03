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

from qgis.utils import iface


from AimsUI.AimsClient.Gui.Controller import Controller
from AimsUI import AimsLogging

# Dev only - debugging
try:
    import sys
    sys.path.append('/opt/eclipse/plugins/org.python.pydev_4.4.0.201510052309/pysrc')
    from pydevd import settrace
    settrace()
except:
    pass

class Plugin(object):
    
    def __init__(self, iface):
        self.iface = iface
        self.controller = Controller(iface)
        
    def initGui(self):
        self.controller.initGui()

    def unload(self): 
        self.controller.initGui()
