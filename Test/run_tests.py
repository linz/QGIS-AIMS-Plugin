'''
v.0.0.2

QGIS-AIMS-Plugin - run_tests

Copyright 2024 Crown copyright (c)
Land Information New Zealand and the New Zealand Government.
All rights reserved

This program is released under the terms of the new BSD license. See the 
LICENSE file for more information.

Test Suite runner based on existing example in the linz-data-importer repo

Created on 29/10/2015

@author: smccann
'''

import os
import sys
import unittest

__location__ = os.path.dirname(os.path.realpath(__file__))


def run_test_modules():
    """
    Loops through all TestCase instances in a test folder to find
    unique test modules
    """
    test_suite = unittest.TestLoader().discover(__location__, pattern="*_Test.py")
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(test_suite)