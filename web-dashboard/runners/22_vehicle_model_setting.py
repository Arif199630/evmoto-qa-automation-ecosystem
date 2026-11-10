"""
=============================================================================
ENTRY POINT: MODUL 22 - VEHICLE MODEL SETTING (MENU #22)
Implementasi: tests/test_22_vehicle_model_setting.py
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

from Step_Definition.test_22_vehicle_model_setting import TestVehicleModelSetting

if __name__ == "__main__":
    unittest.main(verbosity=2)
