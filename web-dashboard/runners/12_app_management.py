"""
=============================================================================
ENTRY POINT: MODUL 12 - APP MANAGEMENT (MENU #12)
Implementasi: tests/test_12_app_management.py
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

from Step_Definition.test_12_app_management import TestAppManagement

if __name__ == "__main__":
    unittest.main(verbosity=2)
