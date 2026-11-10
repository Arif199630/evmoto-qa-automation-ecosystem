"""
=============================================================================
ENTRY POINT: MODUL 02 - HOME PAGE (MENU #2)
Implementasi: tests/test_02_home.py
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

from Step_Definition.test_02_home import TestHalamanBeranda

if __name__ == "__main__":
    unittest.main(verbosity=2)
