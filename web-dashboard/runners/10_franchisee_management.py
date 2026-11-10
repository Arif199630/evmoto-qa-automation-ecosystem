"""
=============================================================================
ENTRY POINT: MODUL 10 - FRANCHISEE MANAGEMENT (MENU #10)
Implementasi: tests/test_10_franchisee_management.py
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

from Step_Definition.test_10_franchisee_management import TestFranchiseeManagement

if __name__ == "__main__":
    unittest.main(verbosity=2)
