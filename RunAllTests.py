'''
v.0.0.1

QGIS-AIMS-Plugin - RunAllTests

Copyright 2011 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Test Suite runner

Created on 29/10/2015

@author: jramsay
'''

import unittest

#bitmask imports
IMASK = {'all':0xF,'adr':0x1,'db':0x2,'lm':0x4,'con':0x8,'xdb':0xD}
BM=0xF

if BM & IMASK['adr']:
    from test.Address_Test import Test_0_AddressSelfTest as AT0
    from test.Address_Test import Test_1_AddressTestSetters as AT1
    from test.AddressFactory_Test import Test_0_AddressFactorySelfTest as AFT0
    from test.AddressFactory_Test import Test_1_AddressTestSetters as AFT1
    
if BM & IMASK['db']:
    from test.Database_Test import Test_0_DatabaseSelfTest as DT0
    from test.Database_Test import Test_1_DatabaseTestSetters as DT1
    from test.Database_Test import Test_2_DatabaseConnectivity as DT2

if BM & IMASK['lm']:
    from test.LayerManager_Test import Test_0_LayerManagerSelfTest as LMT0
    from test.LayerManager_Test import Test_1_LayerManagerSetters as LMT1
    from test.LayerManager_Test import Test_2_LayerManagerConnection as LMT2

if BM & IMASK['con']:
    from test.Controller_Test import Test_0_ControllerSelfTest as CT0
    from test.Controller_Test import Test_1_ControllerTestSetupFunction as CT1

from AimsUI.AimsLogging import Logger

testlog = Logger.setup()


class FullSuite(unittest.TestSuite):

    def __init__(self):
        pass
    
    def suite(self):        
        return unittest.TestSuite()

    
def main():
    
    suite = FullSuite().suite()  
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
if __name__ == "__main__":
    main()

    