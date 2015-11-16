# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""
 
def classFactory(iface):
  
    
     #used for symlinked test environment
    import sys, os, inspect
    cmdfolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
    if cmdfolder not in sys.path:
        sys.path.insert(0, cmdfolder)

    from Plugin import Plugin
    return Plugin(iface)