"""
=============================================================================
ENTRY POINT: MODUL 03 - SYSTEMS MANAGEMENT (MENU #3)
Implementasi: tests/test_03_system_management.py
Arsitektur  : Page Object Model (POM)
=============================================================================
"""

import unittest
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
import config

from Step_Definition.test_03_system_management import TestSystemManagement

if __name__ == "__main__":
    unittest.main(verbosity=2)
