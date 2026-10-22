"""Page Objects package."""
from .splash_page import SplashPage, SplashLocators
from .login_page import LoginPage, LoginLocators
from .register_page import RegisterPage, RegisterLocators
from .home_page import HomePage, HomeLocators
from .booking_page import BookingPage, BookingLocators
from .tracking_page import TrackingPage, TrackingLocators
from .profil_page import ProfilPage, ProfilePage, ProfilLocators, ProfileLocators
from .activity_page import ActivityPage, AktivitasPage, ActivityLocators, AktivitasLocators
from .drv_register_page import DrvRegisterPage
from .drv_login_page import DrvLoginPage
from .drv_home_page import DrvHomePage
from .drv_menu_page import DrvMenuPage
from .drv_wallet_page import DrvWalletPage
from .drv_activity_page import DrvActivityPage
from .drv_booking_page import DrvBookingPage

__all__ = [
    "SplashPage",
    "LoginPage",
    "RegisterPage",
    "HomePage",
    "BookingPage",
    "TrackingPage",
    "ProfilPage",
    "ProfilePage",
    "ActivityPage",
    "AktivitasPage",
    "DrvRegisterPage",
    "DrvLoginPage",
    "DrvHomePage",
    "DrvMenuPage",
    "DrvWalletPage",
    "DrvActivityPage",
    "DrvBookingPage",

    "SplashLocators",
    "LoginLocators",
    "RegisterLocators",
    "HomeLocators",
    "BookingLocators",
    "TrackingLocators",
    "ProfilLocators",
    "ProfileLocators",
    "ActivityLocators",
    "AktivitasLocators"
]

