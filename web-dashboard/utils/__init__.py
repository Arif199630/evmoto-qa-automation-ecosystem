"""
Utilities package for EvMoto Automation Project.
"""
from utils.bug_tracker import BugTracker
from utils.test_interceptor import install_bug_tracker_hook

# Otomatis pasang hook saat utils diimpor
install_bug_tracker_hook()

__all__ = ["BugTracker", "install_bug_tracker_hook"]
