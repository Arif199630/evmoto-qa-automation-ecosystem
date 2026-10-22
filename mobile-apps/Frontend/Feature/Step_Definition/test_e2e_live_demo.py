"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - LIVE DEMO E2E (REGISTER SAMPAI LOGIN)
================================================================================
Tujuan: Sesi Live Demo interaktif di hadapan Manajemen / Atasan.
Perangkat: Samsung Galaxy S25 Emulator (Android 16 API 37)
Pacing: Human-like Simulation (Visual touch ripple, thinking pauses, natural typing)

Alur End-to-End:
1. Mulai dari Layar Masuk / Login
2. Sentuh 'Register as a New User' -> Membuka form registrasi
3. Pengguna meninjau form, mengetik No HP & Nama Lengkap
4. Menekan 'Request OTP' -> Memasukkan kode OTP Dev 1234
5. Menekan 'Create Account' -> Memproses pendaftaran
6. Kembali ke Layar Masuk (Login)
7. Mengisi Nomor HP Dev 81299990001
8. Menekan 'Log In' -> Memasukkan kode OTP Dev 1234
9. Mengonfirmasi izin lokasi Google
10. Masuk sukses ke Beranda Utama EVMoto (Hi, where are you going today?)
================================================================================
"""
import time
import pytest
from Pages.login_page import LoginPage
from Pages.register_page import RegisterPage
from Pages.home_page import HomePage
from Data.user_data import (
    MobileUserDataProvider,
    LOGIN_DATA_POSITIVE_TRUE,
    REGISTER_DATA_POSITIVE_TRUE
)
from utils.bdd_helper import given, when, then, and_step

class TestLiveDemoE2E:

    @pytest.mark.human_like
    @pytest.mark.smoke
    @pytest.mark.record_video
    def test_live_demo_e2e_register_to_login(self, driver):
        """
        Skenario Live Demo End-to-End untuk dipresentasikan langsung ke Atasan.
        Mensimulasikan gerakan manusia nyata di emulator Samsung Galaxy S25.
        """
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)
        home_page = HomePage(driver)

        # Kredensial Pengujian
        login_creds = LOGIN_DATA_POSITIVE_TRUE["TC_LOG_PT_01"]
        fresh_register_phone = f"821{int(time.time()) % 100000000:08d}"
        tester_name = "QA Senior Tester EvMoto"

        print("\n" + "=" * 75)
        print(">>> [LIVE DEMO MANAJEMEN] MEMULAI E2E TESTING: REGISTER SAMPAI LOGIN <<<")
        print(f">>> Target Emulator: Samsung Galaxy S25 (Android API 37) <<<")
        print(f">>> Kredensial Dev: Login No {login_creds['phone']} | OTP {login_creds['otp']} <<<")
        print("=" * 75)

        # ----------------------------------------------------------------------
        # FASE 1: MEMBUKA APLIKASI & MENINJAU LAYAR MASUK AWAL (GIVEN)
        # ----------------------------------------------------------------------
        given("Aplikasi EVMoto dibuka di perangkat Samsung Galaxy S25")
        login_page.is_login_screen_displayed(timeout=20)
        login_page.pause(3.0, 3.0, "Pengguna melihat logo EVMoto & membaca 'Start your green ride'")

        # ----------------------------------------------------------------------
        # FASE 2: NAVIGASI KE PENDAFTARAN AKUN BARU (WHEN)
        # ----------------------------------------------------------------------
        when("Pengguna menekan tautan 'Register as a New User'")
        login_page.navigate_to_register()

        # ----------------------------------------------------------------------
        # FASE 3: MENGISI FORMULIR PENDAFTARAN (HUMAN TYPING)
        # ----------------------------------------------------------------------
        print("\n[FASE 3] Layar pendaftaran terbuka. Pengguna meninjau form...")
        register_page.pause(3.0, 3.0, "Pengguna menatap form pendaftaran akun")

        print(f"   -> Mengetik Nomor Handphone Dev Fresh: {fresh_register_phone}...")
        register_page.fill_phone(fresh_register_phone)
        register_page.pause(3.0, 3.0, "Jeda alami sebelum mengetik nama")

        print(f"   -> Mengetik Nama Lengkap: '{tester_name}'...")
        register_page.fill_name(tester_name)
        register_page.pause(3.0, 3.0, "Pengguna memeriksa nama yang diketik")

        # ----------------------------------------------------------------------
        # FASE 4: REQUEST OTP & INPUT KODE OTP DEV 1234
        # ----------------------------------------------------------------------
        print("\n[FASE 4] Menekan tombol 'Request OTP'...")
        register_page.request_otp()
        register_page.pause(3.0, 3.0, "Menunggu kode verifikasi OTP dev terkirim...")

        print(f"   -> Memasukkan Kode OTP Dev: 1234...")
        register_page.fill_otp("1234")
        register_page.pause(3.0, 3.0, "Jeda deliberasi sebelum konfirmasi pendaftaran")

        # ----------------------------------------------------------------------
        # FASE 5: SUBMIT REGISTRASI AKUN
        # ----------------------------------------------------------------------
        print("\n[FASE 5] Menekan tombol 'Create Account'...")
        register_page.submit_register()
        register_page.pause(3.0, 3.0, "Sistem memproses pembuatan akun pengguna baru")

        # ----------------------------------------------------------------------
        # FASE 6: KEMBALI KE HALAMAN LOGIN UNTUK VERIFIKASI AKUN AKTIF
        # ----------------------------------------------------------------------
        print("\n[FASE 6] Kembali ke Layar Masuk untuk login dengan akun Dev aktif...")
        try:
            register_page.click_back()
        except Exception:
            driver.press_keycode(4)  # Android Hardware Back key
        
        login_page.pause(3.0, 3.0, "Pengguna kembali berada di Layar Masuk EVMoto")
        login_page.is_login_screen_displayed(timeout=15)

        # ----------------------------------------------------------------------
        # FASE 7: LOGIN MENGGUNAKAN NOMOR DEV 81299990001
        # ----------------------------------------------------------------------
        print(f"\n[FASE 7] Mengisi Nomor Telepon Dev: {login_creds['phone']}...")
        login_page.input_phone_number(login_creds["phone"])
        login_page.pause(3.0, 3.0, "Pengguna memeriksa nomor HP dev")

        print("\n[FASE 8] Menekan tombol 'Log In'...")
        login_page.click_submit_login()

        # ----------------------------------------------------------------------
        # FASE 8: VERIFIKASI OTP DEV 1234 & IZIN LOKASI
        # ----------------------------------------------------------------------
        print(f"\n[FASE 9] Layar Verifikasi OTP 4 digit aktif, menginput OTP {login_creds['otp']}...")
        login_page.input_otp_dev(login_creds["otp"], fast_transition=True)

        print("\n[FASE 10] Menangani konfirmasi Google Location Accuracy...")
        login_page.handle_location_prompt_if_present()

        # ----------------------------------------------------------------------
        # FASE 9: VALIDASI BERHASIL MASUK KE BERANDA UTAMA EVMOTO
        # ----------------------------------------------------------------------
        print("\n[FASE 11] Memverifikasi tampilan Beranda utama EVMoto...")
        home_page.pause(3.0, 3.0, "Memuat data peta dan menu Beranda EVMoto")
        is_home_visible = home_page.is_home_screen_displayed(timeout=20)
        assert is_home_visible, "[GAGAL DEMO] Tidak berhasil masuk ke Beranda EVMoto!"

        print("\n" + "=" * 75)
        print(">>> [LIVE DEMO BERHASIL 100%] PENGGUNA BERHASIL MASUK KE BERANDA EVMOTO! <<<")
        print(">>> Tampilan 'Hi, where are you going today?' & Menu Ojol Aktif! <<<")
        print("=" * 75)

        # Berikan jeda 3-4 detik di Beranda agar atasan dapat melihat tampilan akhir dengan puas
        home_page.pause(3.0, 4.0, "Menampilkan Beranda utama EVMoto di hadapan Atasan")

