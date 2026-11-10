"""
TEMPLATE TEST FITUR BARU (Mobile User / Driver App)

Cara pakai:
  1. Salin file ini ke Frontend/Feature/Step_Definition/test_<nama_fitur>.py
  2. Tambahkan locator dan aksi layar baru di Frontend/Feature/Pages/<nama>_page.py (bukan di file test).
  3. Ganti semua bagian bertanda GANTI.
  4. Jalankan: python ../evmoto-qa-tools/run_all.py --suite mobile
     Quality gate akan menolak bila ada method yang belum dibuat atau assertion palsu.

Aturan:
  - Setiap test punya minimal satu assertion yang BISA gagal, dengan pesan yang jelas.
  - Data uji milik test sendiri; jangan memakai data production.
  - Logika angka (tarif, subsidi, saldo) diuji lewat API di api-testing/, bukan lewat layar.
"""
import pytest

from utils.bdd_helper import given, when, then
from login_page import LoginPage      # GANTI bila fitur butuh Page Object lain
from home_page import HomePage
from config import config


@pytest.fixture
def logged_in_home(driver):
    """Prasyarat: pengguna sudah login dan berada di Beranda."""
    login_page = LoginPage(driver)
    home_page = HomePage(driver)
    if not home_page.is_home_screen_displayed(timeout=5):
        login_page.login(phone=config.ACTIVE_PHONE, otp=config.ACTIVE_OTP)
    assert home_page.is_home_screen_displayed(timeout=20), "Prasyarat gagal: Beranda tidak tampil setelah login"
    return home_page


@pytest.mark.regression
@pytest.mark.pilar1
def test_FITUR_P1_01_happy_path(logged_in_home):          # GANTI nama: test_<KODE>_P1_01_<deskripsi>
    """[Pilar 1] GANTI: kalimat ekspektasi bisnis yang diuji."""
    given("Pengguna berada di Beranda")
    home_page = logged_in_home

    when("Pengguna membuka fitur baru")                    # GANTI
    home_page.click_service_evride()                       # GANTI dengan aksi Page Object yang ada

    then("Layar fitur baru tampil")                        # GANTI
    assert home_page.is_booking_screen_displayed(), "Layar fitur baru harus tampil setelah menu dibuka"


@pytest.mark.regression
@pytest.mark.pilar3
def test_FITUR_P3_01_input_invalid_ditolak(logged_in_home):
    """[Pilar 3] GANTI: input tidak valid ditolak dengan pesan yang tepat."""
    pytest.skip("GANTI: tulis skenario input tidak valid untuk fitur ini")
