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
BM=0xE

if BM & IMASK['adr']:
    from Test.Address_Test import Test_0_AddressSelfTest as AT0
    from Test.Address_Test import Test_1_AddressTestSetters as AT1
    from Test.AddressFactory_Test import Test_0_TemplateReaderSelfTest as AFT0
    from Test.AddressFactory_Test import Test_1_AddressFactorySelfTest as AFT1
    from Test.AddressFactory_Test import Test_2_AddressTestSetters as AFT2
    
if BM & IMASK['db']:
    from Test.Database_Test import Test_0_DatabaseSelfTest as DT0
    from Test.Database_Test import Test_1_DatabaseTestSetters as DT1
    from Test.Database_Test import Test_2_DatabaseConnectivity as DT2

if BM & IMASK['lm']:
    from Test.LayerManager_Test import Test_0_LayerManagerSelfTest as LMT0
    from Test.LayerManager_Test import Test_1_LayerManagerSetters as LMT1
    from Test.LayerManager_Test import Test_2_LayerManagerConnection as LMT2

if BM & IMASK['con']:
    from Test.Controller_Test import Test_0_ControllerSelfTest as CT0
    from Test.Controller_Test import Test_1_ControllerTestSetupFunction as CT1

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

    