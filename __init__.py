# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RemoteDebug
                                 A QGIS plugin
 Plugin to connect different IDE remote debugger
                             -------------------
        begin                : 2012-07-30
        copyright            : (C) 2012 by Dr. Horst Düster / Pirmin Kalberer /Sourcepole AG
        email                : horst.duester@sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
def classFactory(iface):
    """Load LDSReplicate class from file LDSReplicate.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    
    #used for symlinked test environment
    import sys, os, inspect
    cmdfolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
    if cmdfolder not in sys.path:
        sys.path.insert(0, cmdfolder)
        
    from Plugin import Plugin
    return Plugin(iface)
