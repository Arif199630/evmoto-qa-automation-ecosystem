"""
=============================================================================
ENTRY POINT: MODUL 24 - TOP HEADER PROFILE NAVIGATION
Implementasi: tests/test_24_profile_navigation.py
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

from Step_Definition.test_24_profile_navigation import TestProfileNavigation

if __name__ == "__main__":
    unittest.main(verbosity=2)
