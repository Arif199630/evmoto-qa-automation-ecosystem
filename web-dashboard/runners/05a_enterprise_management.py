"""
=============================================================================
ENTRY POINT: MODUL 05A - BASIC INFORMATION - ENTERPRISE (MENU #5)
Implementasi: tests/test_05a_enterprise_management.py
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

from Step_Definition.test_05a_enterprise_management import TestEnterpriseManagement

if __name__ == "__main__":
    unittest.main(verbosity=2)
