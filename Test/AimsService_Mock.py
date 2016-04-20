'''
v.0.0.1

QGIS-AIMS-Plugin - AimsService_Mock

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Tests on Controller class

Created on 24/11/2015

@author: jramsay
'''
import unittest
import inspect
import sys
import re


from mock import Mock, patch

resp = {
        "class":[
            "address",
            "collection"
        ],
        "links":[
            {
                "rel":[
                    "self"
                ],
                "href":"http://144.66.241.207:8080/aims/api/address/features?page=1"
            },
            {
                "rel":[
                    "next"
                ],
                "href":"http://144.66.241.207:8080/aims/api/address/features?page=2"
            }
        ],
        "actions":[
            {
                "name":"add",
                "method":"POST",
                "href":"http://144.66.241.207:8080/aims/api/address/changefeed/add"
            }
        ],
        "entities":[
            {
                "class":[
                    "address"
                ],
                "rel":[
                    "item"
                ],
                "links":[
                    {
                        "rel":[
                            "self"
                        ],
                        "href":"http://144.66.241.207:8080/aims/api/address/features/1"
                    }
                ],
                "properties":{
                    "publishDate":"2015-02-19",
                    "version":1622074,
                    "components":{
                        "addressId":1,
                        "addressType":"Road",
                        "lifecycle":"Current",
                        "addressNumber":523,
                        "roadCentrelineId":112967,
                        "roadName":"Waiatai",
                        "roadType":"Road",
                        "suburbLocality":"Wairoa",
                        "townCity":"Wairoa",
                        "fullAddressNumber":"523",
                        "fullRoadName":"Waiatai Road",
                        "fullAddress":"523 Waiatai Road, Wairoa"
                    },
                    "addressedObject":{
                        "addressableObjectId":1706002,
                        "objectType":"Parcel",
                        "addressPosition":{
                            "type":"Point",
                            "coordinates":[
                                1990322.0310298172,
                                5673091.026376988
                            ],
                            "crs":{
                                "type":"name",
                                "properties":{
                                    "name":"urn:ogc:def:crs:EPSG::4167"
                                }
                            }
                        }
                    },
                    "codes":{
                        "suburbLocalityId":2622,
                        "townCityId":100124,
                        "parcelId":4220123,
                        "meshblock":"1398600"
                    }
                }
            }
        ]
    }

def enum(*sequential, **named):
    #http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse'] = reverse
    return type('Enum', (), enums)


class _results(object):
    def mFeature(self):
        return _attribute()

class _AimsHttp(object):
    def call(self):
        pass
    def get(self):
        pass
    
class _QInterface(object):
    def __getattr__(self, *args, **kwargs):
        def dummy(*args, **kwargs):
            return self
        return dummy
    
    def __iter__(self):
        return self
    
    def next(self):
        raise StopIteration
    
    def layers(self): pass
        # simulate iface.legendInterface().layers()
        #return QgsMapLayerRegistry.instance().mapLayers().values()
    
    def mainWindow(self):
        return _MainWindow()
    
    def mapCanvas(self):
        return _MapCanvas()
    
    def legendInterface(self):
        return _Legend()
    
    def messageBar(self): pass
    
class _MapCanvas(object):
    def mapSettings(self):
        return _MapSettings()
    def extent(self): return _Extent()
    
class _MapSettings(object):
    def setDestinationCrs(self,_displayCrs):pass
    
class _Extent(object):
    def xMaximum(self):pass
    def yMaximum(self):pass
    def xMinimum(self):pass
    def yMinimum(self):pass
        
class _MainWindow(object):
    def statusBar(self): return None
    
class _Legend(object):
    def isLayerVisible(self, layer): pass
    def setLayerVisible(self, layer): pass
    
#------------------------------------------------------------------------------
    
class _Layer(object):
    Layer = True
    cp = {}
    def id(self):pass#id = None
    def setCustomProperty(self,prop,id): pass#self.cp[prop] = id 
    def customProperty(self,prop): pass#return self.cp[prop]
    def type(self): pass#return type(self)
    def dataProvider(self): return _Provider()
    def updateFields(self): pass
    def commitChanges(self): pass
    def loadNamedStyle(self):pass
    #def createFeaturesLayer(self):pass
    
class _VectorLayer(_Layer):
    VectorLayer = True
    
class _Provider(object):
    def addAttributes(self,listofattributes):pass
    
class _Feature(object):
    def setGeometry(self):pass
    def setAttributes(self):pass

class _Geometry(object):
    def fromPoint(self):return _Geometry()
    def asPoint(self):return _Geometry()
    
class _Point(object):
    def __init__(self,x,y):pass
#-------------------------------------------------------------

class _pyqtSignal(object):
    def emit(self): pass
    
#------------------------------------------------------------- 
#from contextlib import contextmanager
#@contextmanager
class ContextMock(Mock):
    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None): pass
    def __enter__(self): pass
    
class _QgsMapLayerRegistry(object):

    def instance(self): return self
    def mapLayers(self): return _MapLayers()
    
class _MapLayers(object):
    def values(self): return []
#-------------------------------------------------------------


class ASM(object):
    '''Aims Service Mock accessor'''
    
    ASMenum = enum('HTTP','QI','LAYER','FEATURE','GEOMETRY','POINT','SIGNAL','QMLR','QLGD')
    
    @classmethod
    def getMock(cls,type):
        return {cls.ASMenum.HTTP :      ASM.getAimsHttpMock,
                cls.ASMenum.QI :        ASM.getQIMock,
                cls.ASMenum.LAYER :     ASM.getLayerMock,
                cls.ASMenum.FEATURE :   ASM.getFeatureMock,
                cls.ASMenum.GEOMETRY :  ASM.getGeometryMock,
                cls.ASMenum.POINT :     ASM.getPointMock,
                cls.ASMenum.SIGNAL :    ASM.getPyQtSignalMock,
                cls.ASMenum.QMLR :      ASM.getQMLRMock,
                cls.ASMenum.QLGD :      ASM.getQLGDMock
                }[type]
    @classmethod            
    def getMockSpec(cls,type):
        '''doesn't work, getmock is evaluated before __class__'''
        m =  ASM.getMock(type)
        print type
        return ASM.getMock(type)().__class__
                
    @staticmethod
    def getAimsHttpMock():
        return Mock(spec=_AimsHttp)
    
    @staticmethod
    def getQIMock():
        return Mock(spec=_QInterface)
    
    @staticmethod
    def getLayerMock(idrv=None, cprv=None, vlrv=None,tprv=None):
        if vlrv:
            m = Mock(spec=_VectorLayer) #spec argument configures the mock to take its specification from another object
            m.type.return_value = m.VectorLayer
        else:
            m = Mock(spec=_Layer)
            m.type.return_value = m.Layer
        m.id.return_value = idrv
        m.customProperty.return_value = cprv

        return m
    
    @staticmethod
    def getFeatureMock():
        return Mock(spec=_Feature)       
    
    @staticmethod
    def getGeometryMock():
        return Mock(spec=_Geometry)    
    
    @staticmethod
    def getPointMock():
        return Mock(spec=_Point)
    
    @staticmethod
    def getPyQtSignalMock():
        m = Mock(spec=_pyqtSignal)
        return m    
    
    @staticmethod
    def getQMLRMock(qmlr_rv=[None,]):
        m = ContextMock(spec=_QgsMapLayerRegistry)
        m.instance().mapLayers().values().return_value = qmlr_rv
        return m    
    
    @staticmethod
    def getQLGDMock(qlgd_rv=None):
        m = Mock(spec=_Legend)
        return m


###------

def main():
    
    m = ASM.getLayerMock()
    print m.customProperty(2222)
    
    
    m = ASM.getAimsHttpMock()
    print m
    m.call()
        
    
if __name__ == "__main__":
    main()