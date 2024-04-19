#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import traceback
import signal
import importlib
import unittest
from pathlib import Path

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QDir
from qgis.utils import iface

from console.console_output import writeOut

print('\n\RUN_TESTS.PY SUCCESSFULLY ENTERED')
if iface is None:
    sys.exit("Must be run from inside QGIS")


# Monkey patch QGIS Python console
def _write(self, m):
    sys.__stdout__.write(m)

writeOut.write = _write


def run_tests():
    app = QgsApplication.instance()
    try:
        test_module_name = os.environ["QGIS_TEST_MODULE"]
        test_class_name = os.environ["QGIS_TEST_CLASS"]
        test_name = os.environ["QGIS_TEST_NAME"]
        print(f'RUN_TESTS.PY (36) -- Environent Variables: {test_module_name} -- {test_class_name} -- {test_name}')
        if test_module_name != "" and test_class_name != "" and test_name != "":
            test_suite = unittest.TestLoader().loadTestsFromName(f"{test_class_name}.{test_name}", importlib.import_module(test_module_name))
        elif test_module_name != "" and test_class_name != "":
            test_suite = unittest.TestLoader().loadTestsFromName(test_class_name, importlib.import_module(test_module_name))
        elif test_module_name != "":
            test_suite = unittest.TestLoader().loadTestsFromModule(importlib.import_module(test_module_name))
        else:
            test_suite = unittest.TestLoader().discover(Path(app.arguments()[-1]).parent, pattern="*_Test.py")
        unittest.TextTestRunner(verbosity=3, stream=sys.stderr, tb_locals=True, descriptions=True).run(test_suite)
    except Exception as err:
        print(f"Exception of type {err.__class__.__name__}")
        traceback.print_exc(file=sys.stdout)
    os.kill(app.applicationPid(), signal.SIGTERM)


sys.path.append(QDir.current().path())  # Add current working dir to the python path
iface.initializationCompleted.connect(run_tests)


















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