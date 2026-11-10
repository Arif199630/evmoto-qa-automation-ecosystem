"""
Package Pages: Page Object Model (POM) Implementation
Urutan Terstruktur Sesuai Menu eVMOTO ADMIN CONSOLE
"""

from .page_base import BasePage
from .page_visual_pacer import VisualPacer

from .page_00_login import LoginPage
from .page_01_account_cancellation import AccountCancellationPage
from .page_02_home import HomePage
from .page_03_system_management import SystemManagementPage
from .page_04_user_management import UserManagementPage
from .page_05a_enterprise_management import EnterprisePage
from .page_05b_agreement_management import AgreementPage
from .page_06_urban_management import UrbanPage
from .page_07_driver_management import DriverPage
from .page_08_vehicle_management import VehiclePage
from .page_09_branch_management import BranchPage
from .page_10_franchisee_management import FranchiseePage
from .page_11_travel_order_management import TravelOrderPage
from .page_12_app_management import AppManagementPage
from .page_13_withdrawal_management import WithdrawalPage
from .page_14_comment_management import CommentPage
from .page_15_system_setup import SystemSetupPage
from .page_16_complaint_management import ComplaintPage
from .page_17_sensitive_word_management import SensitiveWordPage
from .page_18_feedback_management import FeedbackPage
from .page_20_version_management import VersionPage
from .page_21_activity_management import ActivityPage
from .page_22_vehicle_model_setting import VehicleModelPage
from .page_23_price_control import PricePage
from .page_24_profile_navigation import ProfilePage

__all__ = [
    "BasePage",
    "VisualPacer",
    "LoginPage",
    "AccountCancellationPage",
    "HomePage",
    "SystemManagementPage",
    "UserManagementPage",
    "EnterprisePage",
    "AgreementPage",
    "UrbanPage",
    "DriverPage",
    "VehiclePage",
    "BranchPage",
    "FranchiseePage",
    "TravelOrderPage",
    "AppManagementPage",
    "WithdrawalPage",
    "CommentPage",
    "SystemSetupPage",
    "ComplaintPage",
    "SensitiveWordPage",
    "FeedbackPage",
    "VersionPage",
    "ActivityPage",
    "VehicleModelPage",
    "PricePage",
    "ProfilePage",
]
