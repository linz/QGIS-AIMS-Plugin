import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from Ui_DelAddressDialog import Ui_DelAddressDialog
from AimsUI.AimsClient.Address import Address
from AimsUI.AimsClient.AimsUtility import AimsUtility

class MoveAddressTool(QgsMapToolIdentifyFeature, QgsHighlight):

    tolerance=5

    def __init__(self, iface, layerManager, controller):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._canvas = iface.mapCanvas()
        self._layers = layerManager
        self._controller = controller
        self._feature = None
        self.hl = None
        self.activate()

    def activate(self):
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Select feature to move")
    
    def deactivate(self):
        sb = self._iface.mainWindow().statusBar()
        self._canvas.scene().removeItem(self.hl)
        sb.clearMessage()
    
    def setEnabled(self, enabled):
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()

    def canvasReleaseEvent(self, mouseEvent):
        layer = self._iface.setActiveLayer(self._layers.addressLayer())
        layer = self._iface.activeLayer()
        
        if mouseEvent.button() == Qt.LeftButton:
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            
            self._canvas.scene().removeItem(self.hl)
            
            if len(results) == 0: 
                return
            if len(results) == 1:
                self._feature = results[0].mFeature.id()
                   
                # Highlight feature    
                coords = results[0].mFeature.geometry().asPoint()
                self.hl = AimsUtility.highlight(self._iface, coords)
                
                # init new address obj
                self.address = self._controller.initialiseAddressObj()
                                        
                self.address.setAddressType(str(results[0].mFeature.attribute('addressType')))
                self.address.setSuburbLocality(str(results[0].mFeature.attribute('suburbLocality')))
                self.address.setTownCity(str(results[0].mFeature.attribute('townCity')))
                #self.address.xxxx(str(results[0].mFeature.attribute('meshblock')))
                self.address.setLifecycle(str(results[0].mFeature.attribute('lifecycle'))) 
                self.address.setRoadPrefix(str(results[0].mFeature.attribute('roadPrefix')))
                self.address.setRoadName(str(results[0].mFeature.attribute('roadName')))      
                self.address.setRoadSuffix(str(results[0].mFeature.attribute('roadSuffix')))
                self.address.setRoadTypeName(str(results[0].mFeature.attribute('roadTypeName')))
                self.address.setRoadCentrelineId(str(results[0].mFeature.attribute('roadCentrelineId')))
                self.address.setWaterRouteName(str(results[0].mFeature.attribute('waterRouteName')))
                self.address.setWaterName(str(results[0].mFeature.attribute('waterName')))
                self.address.setUnitValue(str(results[0].mFeature.attribute('unitValue')))
                self.address.setUnitType(str(results[0].mFeature.attribute('unitType')))
                self.address.setLevelType(str(results[0].mFeature.attribute('levelType')))
                self.address.setLevelValue(str(results[0].mFeature.attribute('levelValue')))
                self.address.setAddressNumberPrefix(str(results[0].mFeature.attribute('addressNumberPrefix')))
                self.address.setAddressNumber(str(results[0].mFeature.attribute('addressNumber')))
                self.address.setAddressNumberSuffix(str(results[0].mFeature.attribute('addressNumberSuffix')))
                self.address.setAddressNumberHigh(str(results[0].mFeature.attribute('addressNumberHigh')))
                self.address.setVersion(str(results[0].mFeature.attribute('version')))
                self.address.setAddressId(str(results[0].mFeature.attribute('addressId')))
                self.address.setAoType(str(results[0].mFeature.attribute('objectType')))
                self.address.setAoName(str(results[0].mFeature.attribute('objectName')))
                self.address.setAoPositionType(str(results[0].mFeature.attribute('addressPositionType')))
                
                sb = self._iface.mainWindow().statusBar()
                sb.showMessage("Right new feature location")
                
        if mouseEvent.button() == Qt.RightButton:
            if self._feature:
                pt = mouseEvent.pos()
                coords = self.toMapCoordinates(QPoint(pt.x(), pt.y()))
                coords = AimsUtility.transform(self._iface, coords)
                          
                self.address.set_x(coords[0])
                self.address.set_y(coords[1])
                
                payload = self.address.aimsObject()
                valErrors = self._controller.updateFeature(payload)
                
                if len(valErrors) == 0:
                    self._feature = None
                else:
                    QMessageBox.warning(self._iface.mainWindow(),"Create Address Point", valErrors)
                
            else: QMessageBox.warning(self._iface.mainWindow(),"Move Feature", "You must first select a feature to move")


"""
            retireIds = {}        
            retireIds['version'] = results[0].mFeature.attribute('version')
            retireIds['components'] = {'addressId': results[0].mFeature.attribute('addressId')}
            
            fullAddress = results[0].mFeature.attribute('fullAddress')
            
            if QMessageBox.question(self._iface.mainWindow(), 
                 "Confirm Address Retirement",
                fullAddress + "\n will be marked for retirement?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Ok ) == QMessageBox.Ok:    
                retireFeatures.append(retireIds)

        else: # Stacked points
            identifiedFeatures=[] 
            for i in range (0,len(results)):
                identifiedFeatures.append(dict(
                fullAddress=results[i].mFeature.attribute('fullAddress'),
                version= results[i].mFeature.attribute('version'),
                addressId= results[i].mFeature.attribute('addressId')
                ))
            # Open 'Retire' dialog showing selected AIMS features   
            dlg = DelAddressDialog(self._iface.mainWindow())
            retireFeatures = dlg.selectFeatures(identifiedFeatures)
        
        if retireFeatures: # else the user hit 'ok' and did not select any records            
            valErrors = self._controller.retireAddress(retireFeatures)
            if len(valErrors) != 0:
                QMessageBox.warning(self._iface.mainWindow(),"Retire Address Point", valErrors)
        return       
 
class DelAddressDialog( Ui_DelAddressDialog, QDialog ):

    def __init__( self, parent ):
        QDialog.__init__(self,parent)
        self.setupUi(self)
    
    def selectionToRetirementJson(self, selected):
        ''' Reformats the list of dict that represents the users selection 
        from the dialog into a list of AIMS json objects ''' 
        retireFeatures = []
        for i in selected:  
            retireIds = {}        
            retireIds['version'] = i['version']
            retireIds['components'] = {'addressId': i['addressId']}
            retireFeatures.append(retireIds)
        return retireFeatures        

    def selectFeatures( self, identifiedFeatures ):
        self.uSadListView.setList(identifiedFeatures,
                                 ['fullAddress','version','addressId'])
        if self.exec_() == QDialog.Accepted:
            return self.selectionToRetirementJson(self.uSadListView.selectedItems())
        return None
"""
