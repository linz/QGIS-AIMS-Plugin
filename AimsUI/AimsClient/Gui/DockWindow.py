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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *

class DockWindow( QDockWidget ):

    def __init__( self, parent, widget, name, title='' ):
        QDockWidget.__init__( self, parent )
        self._name = name
        if not title:
            title = name
        self.setWindowTitle( title )
        self.setWidget(widget)
        parent.addDockWidget( Qt.LeftDockWidgetArea, self )
        self.restoreLocation(True)
        self.topLevelChanged.connect( self.saveLocation )

    def onTopLevelChanged( self, toplevel ):
        if self.isFloating():
            self.restoreLocation(False)
        self.saveLocation()

    def resizeEvent( self, event ):
        if self.isFloating():
            self.saveLocation()

    def moveEvent( self, event ):
        if self.isFloating():
            self.saveLocation()

    def saveLocation( self ):
        from Plugin import Plugin
        if not self._name:
            return
        base = Plugin.SettingsBase + self._name + '/'
        settings = QSettings()
        floating = self.isFloating()
        settings.setValue(base+"Floating",floating)
        if floating:
            location = ' '.join((
                str(self.pos().x()),
                str(self.pos().y()),
                str(self.size().width()),
                str(self.size().height())
                ))
            settings.setValue(base+"Location",location)

    def restoreLocation( self, restoreFloating ):
        if not self._name:
            return
        try: 
            from Plugin import Plugin
            base = Plugin.SettingsBase + self._name + '/'
            settings = QSettings()
            if restoreFloating:
                floating = settings.value(base+"Floating").toBool()
                self.setFloating( floating )
            if self.isFloating():
                location =settings.value(base+"Location")
                parts = location.split(' ')
                self.setSize(int(parts[0]),int(parts[1]))
                self.setPos(int(parts[2]),int(parts[3]))
        except:
            pass
