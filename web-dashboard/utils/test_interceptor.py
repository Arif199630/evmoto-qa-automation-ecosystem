"""
=============================================================================
TEST INTERCEPTOR & RUNNER HOOK
Automation Project EvMoto
=============================================================================
Menyediakan mekanisme pencegatan otomatis (hook) pada siklus pengujian:
1. Menangkap setiap AssertionError (addFailure) atau Exception tak tertangani (addError).
2. Menginstruksikan BugTracker untuk mengambil tangkapan layar browser Selenium secara instan.
3. Mencatat seluruh anomali ke Excel (.xlsx), CSV, dan Interactive HTML Dashboard.
=============================================================================
"""

import sys
import unittest
from utils.bug_tracker import BugTracker

# Flag untuk mencegah instalasi ganda
_HOOK_INSTALLED = False


class BugTrackerTestResult(unittest.TextTestResult):
    """Kolektor hasil pengujian kustom yang langsung merekam kegagalan ke Bug Tracker."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self._recorded_tests = set()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        test_id = str(test)
        if test_id not in self._recorded_tests:
            self._recorded_tests.add(test_id)
            BugTracker.record_bug(test, err, failure_type="Failure (AssertionError)")

    def addError(self, test, err):
        super().addError(test, err)
        test_id = str(test)
        if test_id not in self._recorded_tests:
            self._recorded_tests.add(test_id)
            BugTracker.record_bug(test, err, failure_type="Error (Exception)")


class EvMotoTestRunner(unittest.TextTestRunner):
    """Test Runner terstandar dengan integrasi otomatis Bug Tracker & Evidence Screenshot."""

    resultclass = BugTrackerTestResult

    def __init__(self, *args, **kwargs):
        kwargs["resultclass"] = BugTrackerTestResult
        super().__init__(*args, **kwargs)


def install_bug_tracker_hook():
    """
    Memasang hook global pada unittest.TestResult.
    Dengan hook ini, pengujian yang dijalankan melalui unittest.main(), runner standar,
    maupun runner kustom akan otomatis terdeteksi jika terjadi bug/error.
    """
    global _HOOK_INSTALLED
    if _HOOK_INSTALLED:
        return

    orig_addFailure = unittest.TestResult.addFailure
    orig_addError = unittest.TestResult.addError

    def hooked_addFailure(self, test, err):
        orig_addFailure(self, test, err)
        # Hindari dobel rekam jika sudah ditangani oleh BugTrackerTestResult
        if not isinstance(self, BugTrackerTestResult):
            recorded = getattr(self, "_recorded_bug_tests", set())
            test_id = str(test)
            if test_id not in recorded:
                recorded.add(test_id)
                setattr(self, "_recorded_bug_tests", recorded)
                BugTracker.record_bug(test, err, failure_type="Failure (AssertionError)")

    def hooked_addError(self, test, err):
        orig_addError(self, test, err)
        # Hindari dobel rekam jika sudah ditangani oleh BugTrackerTestResult
        if not isinstance(self, BugTrackerTestResult):
            recorded = getattr(self, "_recorded_bug_tests", set())
            test_id = str(test)
            if test_id not in recorded:
                recorded.add(test_id)
                setattr(self, "_recorded_bug_tests", recorded)
                BugTracker.record_bug(test, err, failure_type="Error (Exception)")

    unittest.TestResult.addFailure = hooked_addFailure
    unittest.TestResult.addError = hooked_addError
    _HOOK_INSTALLED = True


class EvMotoBaseTestCase(unittest.TestCase):
    """
    Kelas dasar pengujian opsional yang dilengkapi pelindung inspeksi tearDown.
    """
    pass
