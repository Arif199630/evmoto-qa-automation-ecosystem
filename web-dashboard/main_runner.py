"""
=============================================================================
UNIFIED TEST RUNNER (MAIN RUNNER)
Automation Project EvMoto
Arsitektur: Page Object Model (POM)
Konsep    : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
=============================================================================
Urutan Pengujian Terstruktur Sesuai Menu eVMOTO ADMIN CONSOLE:
  00. Autentikasi: Halaman Login (tests/test_00_login.py)
  01. Account cancellation management (tests/test_01_account_cancellation.py)
  02. Home page (tests/test_02_home.py)
  03. Systems management (tests/test_03_system_management.py)
  04. User management (tests/test_04_user_management.py)
  05. Basic information management:
      - Enterprise Management (tests/test_05a_enterprise_management.py)
      - Agreement Management (tests/test_05b_agreement_management.py)
  06. Opening up urban management (tests/test_06_urban_management.py)
  07. Driver management (tests/test_07_driver_management.py)
  08. Vehicle management (tests/test_08_vehicle_management.py)
  09. Branch management (tests/test_09_branch_management.py)
  10. Franchisee management (tests/test_10_franchisee_management.py)
  11. Travel order management (tests/test_11_travel_order_management.py)
  12. App Management (tests/test_12_app_management.py)
  13. Withdrawal management (tests/test_13_withdrawal_management.py)
  14. Comment management (tests/test_14_comment_management.py)
  15. System setup (tests/test_15_system_setup.py)
  16. Complaint management (tests/test_16_complaint_management.py)
  17. Sensitive word management (tests/test_17_sensitive_word_management.py)
  18. Feedback management (tests/test_18_feedback_management.py)
  20. Version management (tests/test_20_version_management.py)
  21. Activity management (tests/test_21_activity_management.py)
  22. Vehicle model setting (tests/test_22_vehicle_model_setting.py)
  23. Price control (tests/test_23_price_control.py)
  24. Header Profile & Top Navigation Dropdown (tests/test_24_profile_navigation.py)
=============================================================================
"""

import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import config
from utils.test_interceptor import EvMotoTestRunner
from utils.bug_tracker import BugTracker

from tests.test_00_login import TestHalamanLogin
from tests.test_01_account_cancellation import TestAccountCancellation
from tests.test_02_home import TestHalamanBeranda
from tests.test_03_system_management import TestSystemManagement
from tests.test_04_user_management import TestUserManagement
from tests.test_05a_enterprise_management import TestEnterpriseManagement
from tests.test_05b_agreement_management import TestAgreementManagement
from tests.test_06_urban_management import TestUrbanManagement
from tests.test_07_driver_management import TestDriverManagement
from tests.test_08_vehicle_management import TestVehicleManagement
from tests.test_09_branch_management import TestBranchManagement
from tests.test_10_franchisee_management import TestFranchiseeManagement
from tests.test_11_travel_order_management import TestTravelOrderManagement
from tests.test_12_app_management import TestAppManagement
from tests.test_13_withdrawal_management import TestWithdrawalManagement
from tests.test_14_comment_management import TestCommentManagement
from tests.test_15_system_setup import TestSystemSetup
from tests.test_16_complaint_management import TestComplaintManagement
from tests.test_17_sensitive_word_management import TestSensitiveWordManagement
from tests.test_18_feedback_management import TestFeedbackManagement
from tests.test_20_version_management import TestVersionManagement
from tests.test_21_activity_management import TestActivityManagement
from tests.test_22_vehicle_model_setting import TestVehicleModelSetting
from tests.test_23_price_control import TestPriceControl
from tests.test_24_profile_navigation import TestProfileNavigation


def load_test_suite():
    """Mengumpulkan seluruh test suite dari folder tests/ sesuai urutan sidebar console."""
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # 00. Autentikasi: Login Page (12 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestHalamanLogin))

    # 01. Menu #1: Account Cancellation Management (13 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestAccountCancellation))

    # 02. Menu #2: Home Page (13 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestHalamanBeranda))

    # 03. Menu #3: Systems Management (15 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestSystemManagement))

    # 04. Menu #4: User Management (15 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestUserManagement))

    # 05. Menu #5: Basic Information Management - Enterprise (13 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestEnterpriseManagement))

    # 05. Menu #5: Basic Information Management - Agreement (21 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestAgreementManagement))

    # 06. Menu #6: Opening Up Urban Management (19 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestUrbanManagement))

    # 07. Menu #7: Driver Management (27 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestDriverManagement))

    # 08. Menu #8: Vehicle Management (32 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestVehicleManagement))

    # 09. Menu #9: Branch Management (20 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestBranchManagement))

    # 10. Menu #10: Franchisee Management (20 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestFranchiseeManagement))

    # 11. Menu #11: Travel Order Management (33 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestTravelOrderManagement))

    # 12. Menu #12: App Management (32 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestAppManagement))

    # 13. Menu #13: Withdrawal Management (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestWithdrawalManagement))

    # 14. Menu #14: Comment Management (25 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestCommentManagement))

    # 15. Menu #15: System Setup (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestSystemSetup))

    # 16. Menu #16: Complaint Management (28 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestComplaintManagement))

    # 17. Menu #17: Sensitive Word Management (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestSensitiveWordManagement))

    # 18. Menu #18: Feedback Management (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestFeedbackManagement))

    # 20. Menu #20: Version Management (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestVersionManagement))

    # 21. Menu #21: Activity Management (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestActivityManagement))

    # 22. Menu #22: Vehicle Model Setting (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestVehicleModelSetting))

    # 23. Menu #23: Price Control (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestPriceControl))

    # 24. Header Profile Dropdown (30 Test)
    suite.addTests(loader.loadTestsFromTestCase(TestProfileNavigation))

    return suite


if __name__ == "__main__":
    from utils.staging_guard import ensure_not_production
    ensure_not_production(extra_urls=[config.Config.get_base_url(), config.Config.get_backend_api_url()])
    print("=" * 85)
    print("      AUTOMATION TEST SUITE - EVMOTO ADMIN SERVICE (POM - 4 PILAR TESTING)")
    print("=" * 85)
    print("Konsep 4 Pilar Pengujian:")
    print("  1. Positif (True)  : Memastikan aksi berhasil mengembalikan kondisi BENAR")
    print("  2. Positif (False) : Memastikan saat kondisi normal, error bernilai SALAH/NIHIL")
    print("  3. Negatif (True)  : Memastikan proteksi keamanan dan pesan error BENAR-BENAR aktif")
    print("  4. Negatif (False) : Memastikan akses tidak sah/data fiktif DITOLAK (False)")
    print("-" * 85)
    print("Daftar Modul yang Siap Dijalankan (Sesuai Urutan Sidebar Console):")
    print("  00. Halaman Login / Autentikasi (12 Test)")
    print("  01. Account Cancellation Management / userExit (13 Test)")
    print("  02. Home Page / Blackboard (13 Test)")
    print("  03. Systems Management (/mgr, /role, /menu, /dept) (15 Test)")
    print("  04. User Management (/tUser) (15 Test)")
    print("  05a. Basic Information - Enterprise Management (/tCompany) (13 Test)")
    print("  05b. Basic Information - Agreement Management (/tAgreement) (21 Test)")
    print("  06. Opening Up Urban Management (/tOpenCity, /THotAddress, /service-area) (19 Test)")
    print("  07. Driver Management (/tDriver, /tDriverVerify, /tDriver/yesDriver, /tDriver/without) (27 Test)")
    print("  08. Vehicle Management (/tCarBrand, /tCarModel, /tCar, /tMotorModel) (32 Test)")
    print("  09. Branch Management (/tCompany) (20 Test)")
    print("  10. Franchisee Management (/tCompany/franchisee) (20 Test)")
    print("  11. Travel Order Management (/tOrderPrivateCar, /tOrderLogistics) (33 Test)")
    print("  12. App Management (/TChatSet, /tbBanner, /TVoice) (32 Test)")
    print("  13. Withdrawal Management (/tPubWithdrawal, /withdrawalConfig) (30 Test)")
    print("  14. Comment Management (/tOrderEvaluate) (25 Test)")
    print("  15. System Setup (/tSysReformist, /userDebtUnblock) (30 Test)")
    print("  16. Complaint Management (/tComplaint) (28 Test)")
    print("  17. Sensitive Word Management (/tSysSensitiveWords) (30 Test)")
    print("  18. Feedback Management (/tFeedback) (30 Test)")
    print("  20. Version Management (/tVersionManagement) (30 Test)")
    print("  21. Activity Management (/driverActivity) (30 Test)")
    print("  22. Vehicle Model Setting (/tMotorModel) (30 Test)")
    print("  23. Price Control (/tSystemPrice) (30 Test)")
    print("  24. Profile & Top Navigation Dropdown Across All Modules (30 Test)")
    print("=" * 85)

    test_suite = load_test_suite()
    runner = EvMotoTestRunner(verbosity=2)
    result = runner.run(test_suite)

    print("\n" + "=" * 85)
    print("HASIL AKHIR EKSEKUSI PENGUJIAN:")
    print(f"Total Test Dijalankan : {result.testsRun}")
    print(f"Sukses (Passed)       : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Gagal (Failures)      : {len(result.failures)}")
    print(f"Error (Errors)        : {len(result.errors)}")

    total_bugs = len(result.failures) + len(result.errors)
    if total_bugs > 0:
        print("-" * 85)
        print("🐞 REKAPITULASI BUG TRACKER OTOMATIS (EXCEL ONLINE & LARK BASE):")
        print(f"  -> Total Anomali Dicatat: {total_bugs} Bug")
        print(f"  -> File Excel (.xlsx)   : reports/Bug_Tracker_EvMoto.xlsx")
        print(f"  -> File CSV (Lark Base) : reports/Bug_Tracker_EvMoto.csv")
        print(f"  -> Interactive HTML     : reports/Bug_Tracker_EvMoto.html")
        print(f"  -> Direktori Screenshot : reports/screenshots/")
    else:
        print("-" * 85)
        print("✅ LUAR BIASA! Seluruh Test Case Lolos 100% (Zero Bug Detected).")
    print("=" * 85)

    sys.exit(0 if result.wasSuccessful() else 1)
