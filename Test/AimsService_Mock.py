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
                        "roadTypeName":"Road",
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
                                    "name":"urn:ogc:def:crs:EPSG::2193"
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
    
    def layers(self):
        # simulate iface.legendInterface().layers()
        return QgsMapLayerRegistry.instance().mapLayers().values()
    
    def mainWindow(self):
        return _MainWindow()
    
    def mapCanvas(self):
        return _MapCanvas()
    
class _MapCanvas(object):
    def mapSettings(self):
        return _MapSettings()
    
class _MapSettings(object):
    def setDestinationCrs(_displayCrs):
        pass
    
class _MainWindow(object):
    def statusBar(self): return None
    
#------------------------------------------------------------------------------
    
class _Layer(object):
    cp = {}
    def setCustomProperty(self,prop,id): self.cp[prop] = id 
    def customProperty(self,prop): return self.cp[prop]
    
class VectorLayer(_Layer):pass

#-------------------------------------------------------------


class ASM(object):
    ASMenum = enum('HTTP','QI','LAYER')
    @classmethod
    def getMock(cls,type):
        return {cls.ASMenum.HTTP : ASM.getAimsHttpMock,
                cls.ASMenum.QI : ASM.getQIMock,
                cls.ASMenum.LAYER : ASM.getLayerMock
                }[type]
                
    @classmethod
    def getAimsHttpMock(cls):
        return Mock(spec=_AimsHttp)
    @classmethod
    def getQIMock(cls):
        return Mock(spec=_QInterface)
    
    @classmethod
    def getLayerMock(cls,idrv=None):
        m = Mock(spec=_Layer)
        m.customProperty.return_value = idrv
        m.type = VectorLayer
        return m

###------

def main():
    
    m = getLayerMock()
    print m.customProperty(2222)
    
    
    m = getAimsHttpMock()
    print m
    m.call()
        
    
if __name__ == "__main__":
    main()