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

from AimsClient.Test.Address_Test import Test_0_AddressSelfTest as AT0
from AimsClient.Test.Address_Test import Test_1_AddressTestSetters as AT1
from AimsClient.Test.Database_Test import Test_0_DatabaseSelfTest as DT0
from AimsClient.Test.Database_Test import Test_1_DatabaseTestSetters as DT1
from AimsClient.Test.Database_Test import Test_2_DatabaseConnectivity as DT2
from AimsClient.AimsLogging import Logger

testlog = Logger.setup()


class FullSuite(unittest.TestSuite):

    def __init__(self):
        pass
    
    def suite(self):
        suites = ()
        suites += unittest.makeSuite(AT0)
        suites += unittest.makeSuite(AT1)
        suites += unittest.makeSuite(DT0)
        suites += unittest.makeSuite(DT1)
        suites += unittest.makeSuite(DT2)
        
        return unittest.TestSuite(suites)

    
def main():
    
    suite = FullSuite().suite()  
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
if __name__ == "__main__":
    main()

    