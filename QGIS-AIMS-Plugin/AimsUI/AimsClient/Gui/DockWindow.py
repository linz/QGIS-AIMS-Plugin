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

from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import QgisInterface
from qgis.utils import iface
iface:QgisInterface = iface

class DockWindow( QDockWidget ):
    unloadPlugin = pyqtSignal()
    
    def __init__( self, parent, widget, name, title='' ):
        QDockWidget.__init__( self, parent )
        self._parent = parent
        self._name = name
        if not title:
            title = name
        self.setWindowTitle( title )
        self.setWidget(widget)
        self.setObjectName('AIMSDockWidget')
        self._parent.addDockWidget( Qt.LeftDockWidgetArea, self )
        # iface.addDockWidget(Qt.LeftDockWidgetArea, self)
        layerdock = self._parent.findChild(QDockWidget, "Layers")
        self._parent.tabifyDockWidget(layerdock, self)
        
        self.restoreLocation(True)
        self.topLevelChanged.connect( self.saveLocation )

        # Set active tab
        self.show()
        self.raise_()

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

    def reDock(self):
        self.setFloating(True)
        self.setFloating(False)
        self.show()
        self.raise_()
        # iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)

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

    def closeEvent(self, event):
        self.unloadPlugin.emit()
        event.accept()