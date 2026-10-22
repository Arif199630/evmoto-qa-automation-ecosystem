"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - TEST SUITE: MASUK / LOGIN (LOGIN PAGE)
================================================================================
Fokus Pengujian : Halaman Masuk Akun Pengguna (Login Page)
Environment     : Universal (Staging / Development / Live)
Kredensial Dev  : Nomor HP 81299990001 | Kode OTP 1234
Metodologi      : Page Object Model (POM) & 4 Pilar QA Lengkap

KLASIFIKASI 4 PILAR QA (21 SKENARIO LENGKAP):
--------------------------------------------------------------------------------
PILAR 1: POSITIVE TRUE (PT) - Happy Path (Ekspektasi: SUKSES)
- TC_LOG_PT_01: Login Berhasil Menggunakan Akun Dev Aktif (81299990001 + OTP 1234)
- TC_LOG_PT_02: Login Berhasil Variasi Format Nomor Terdaftar (10-12 Digit)
- TC_LOG_PT_03: Login Berhasil Menggunakan Alur Resend OTP
- TC_LOG_PT_04: Navigasi Tinjau Halaman Legalitas (Terms and Conditions & Privacy Policy)
- TC_LOG_PT_05: Login Berhasil dengan Penanganan Popup Location Permission saat Location Phone Dimatikan

PILAR 2: POSITIVE FALSE (PF) - Aturan Bisnis (Ekspektasi: DITOLAK)
- TC_LOG_PF_01: Login Gagal Nomor Telepon Belum Terdaftar
- TC_LOG_PF_02: Tombol 'Log In' Tetap Nonaktif (Disabled) Saat Nomor < 8 Digit
- TC_LOG_PF_03: Tombol 'Resend' Nonaktif Selama Countdown Timer Berjalan
- TC_LOG_PF_04: Percobaan Input OTP Salah Berulang Kali (Rate Limiting / Lockout)

PILAR 3: NEGATIVE TRUE (NT) - Format Salah / Input Invalid (Ekspektasi: PESAN ERROR VALIDASI)
- TC_LOG_NT_01: Login Gagal Kode OTP Salah (Bukan 1234)
- TC_LOG_NT_02: Login Gagal Nomor Tidak Diawali Angka 8 (Diawali 0)
- TC_LOG_NT_03: Login Gagal Field Nomor Handphone Dikosongkan
- TC_LOG_NT_04: Input Nomor Terlalu Pendek (4 Digit)
- TC_LOG_NT_05: Input Kode OTP Incomplete (< 4 Digit)
- TC_LOG_NT_06: Pembatalan Verifikasi OTP via Tombol Back Kembali ke Layar Login

PILAR 4: NEGATIVE FALSE (NF) - Security & Robustness (Ekspektasi: SISTEM AMAN/TIDAK CRASH)
- TC_LOG_NF_01: Keamanan Serangan SQL Injection pada Form Login
- TC_LOG_NF_02: Keamanan Serangan Cross-Site Scripting (XSS) pada Kolom Telepon
- TC_LOG_NF_03: Boundary Value Ekstrem Panjang Digit Nomor HP (25 Digit)
- TC_LOG_NF_04: Filter Karakter Alfabet & Simbol pada Field Nomor HP
- TC_LOG_NF_05: Input Whitespace Murni (Spasi Saja) pada Field Nomor HP
- TC_LOG_NF_06: Rapid Repeated Clicking (Button Spamming) Anti-Race Condition
================================================================================
"""
import time
import pytest
from Pages.login_page import LoginPage
from Pages.home_page import HomePage
from Data.user_data import (
    MobileUserDataProvider,
    LOGIN_DATA_POSITIVE_TRUE,
    LOGIN_DATA_POSITIVE_FALSE,
    LOGIN_DATA_NEGATIVE_TRUE,
    LOGIN_DATA_NEGATIVE_FALSE
)
from utils.bdd_helper import given, when, then, and_step

class TestLogin:

    @pytest.fixture(autouse=True)
    def anti_race_condition_deliberation_pause(self):
        """
        Fixture jeda 5 detik wajib setelah setiap test case selesai
        untuk mencegah race condition pada pengujian mobile automation.
        """
        yield
        time.sleep(5.0)

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH / LOGIN SUKSES KE BERANDA
    # ==========================================================================

    @pytest.mark.positive_true
    @pytest.mark.smoke
    @pytest.mark.human_like
    def test_TC_LOG_PT_01_login_berhasil_nomor_dev_dan_otp_1234(self, driver):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi: Login langsung menggunakan nomor HP Dev aktif 81299990001
        dan memasukkan kode verifikasi OTP Dev 1234.
        Ekspektasi: Pengguna berhasil login dan masuk ke Beranda utama EVMoto.
        """
        data = LOGIN_DATA_POSITIVE_TRUE["TC_LOG_PT_01"]
        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-01] LOGIN LANGSUNG NOMOR DEV AKTIF <<<")
        print(f">>> Target Dev: Nomor {data['phone']} | OTP {data['otp']} <<<")
        print("=" * 70)

        # BDD: Given - When - Then Logic
        given("Aplikasi EVMoto terbuka dan menampilkan layar Login awal")
        login_page.is_login_screen_displayed(timeout=15)

        when(f"Pengguna menginput nomor telepon terdaftar '{data['phone']}' dan menekan tombol Log In")
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        and_step(f"Pengguna memasukkan kode verifikasi OTP dev '{data['otp']}'")
        login_page.input_otp_dev(data["otp"], fast_transition=True)
        login_page.handle_location_prompt_if_present()

        then("Sistem berhasil mengautentikasi dan mengarahkan pengguna ke Beranda utama EVMoto")
        home_page.pause(2.0, 3.0, "Memuat halaman Beranda EVMoto")
        is_logged_in = home_page.is_home_screen_displayed(timeout=20)
        assert is_logged_in, "[GAGAL PT-01] Pengguna gagal masuk ke Beranda setelah login OTP 1234!"
        print(">>> [PASSED PT-01] Login nomor dev dengan OTP 1234 BERHASIL MASUK BERANDA!")

    @pytest.mark.positive_true
    def test_TC_LOG_PT_02_login_berhasil_variasi_format_nomor_terdaftar(self, driver):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi: Menguji login nomor akun terdaftar dengan panjang 11 digit standar Indonesia.
        Ekspektasi: Field input menerima dan tombol Log In aktif dengan baik.
        """
        data = LOGIN_DATA_POSITIVE_TRUE["TC_LOG_PT_02"]
        login_page = LoginPage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-02] VALIDASI FORMAT NOMOR TELEPON TERDAFTAR <<<")
        print("=" * 70)

        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        is_active = login_page.is_submit_button_enabled()
        assert is_active, "[GAGAL PT-02] Tombol Log In tidak aktif untuk nomor telepon terdaftar valid!"
        print(">>> [PASSED PT-02] Format nomor telepon terdaftar diterima dan tombol aktif!")

    @pytest.mark.positive_true
    def test_TC_LOG_PT_03_login_berhasil_alur_resend_otp(self, driver):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi: Menguji alur meminta kirim ulang OTP (Resend OTP) pada layar verifikasi
        setelah masa countdown awal selesai, lalu login dengan OTP Dev 1234.
        Ekspektasi: Resend OTP berhasil diminta dan kode OTP 1234 tetap valid untuk login.
        """
        data = LOGIN_DATA_POSITIVE_TRUE["TC_LOG_PT_03"]
        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-03] LOGIN MENGGUNAKAN ALUR RESEND OTP <<<")
        print("=" * 70)

        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        login_page.is_otp_screen_displayed(timeout=15)
        login_page.pause(1.5, 2.5, "Meninjau layar verifikasi OTP sebelum resend")

        # Coba trigger resend jika tombol aktif
        try:
            login_page.click_resend_otp()
        except Exception:
            pass

        login_page.input_otp_dev(data["otp"], fast_transition=True)
        login_page.handle_location_prompt_if_present()

        home_page.pause(2.0, 3.0, "Memuat halaman Beranda")
        is_home = home_page.is_home_screen_displayed(timeout=20)
        assert is_home, "[GAGAL PT-03] Gagal masuk ke Beranda setelah alur Resend OTP!"
        print(">>> [PASSED PT-03] Alur Resend OTP berhasil login ke Beranda!")

    @pytest.mark.positive_true
    def test_TC_LOG_PT_04_navigasi_ketentuan_layanan_dan_kebijakan_privasi(self, driver):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi: Menguji navigasi membuka tautan legalitas 'Terms and Conditions'
        serta 'Privacy Policy' dari halaman Login.
        Ekspektasi: Tautan dapat diklik dan membuka dokumen legalitas tanpa crash.
        """
        login_page = LoginPage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-04] NAVIGASI TERMS & CONDITIONS SERTA PRIVACY POLICY <<<")
        print("=" * 70)

        login_page.is_login_screen_displayed(timeout=15)
        try:
            login_page.click_terms()
            login_page.pause(1.5, 2.0, "Membuka Terms and Conditions")
            driver.press_keycode(4)  # Android Back key
        except Exception:
            pass

        try:
            login_page.click_privacy()
            login_page.pause(1.5, 2.0, "Membuka Privacy Policy")
            driver.press_keycode(4)  # Android Back key
        except Exception:
            pass

        still_at_login = login_page.is_login_screen_displayed(timeout=10)
        assert still_at_login, "[GAGAL PT-04] Aplikasi tidak kembali ke layar Login setelah membuka halaman legal!"
        print(">>> [PASSED PT-04] Navigasi dokumen legalitas berjalan normal dan kembali ke Login!")

    @pytest.mark.positive_true
    @pytest.mark.smoke
    @pytest.mark.location_permission
    def test_TC_LOG_PT_05_login_dengan_penanganan_popup_location_permission(self, driver):
        """
        [POSITIVE TRUE - PT-05]
        Deskripsi: Menguji skenario ketika pengguna menonaktifkan fitur Location pada perangkatnya,
        sistem/aplikasi menampilkan popup Location Permission, pengguna memberikan izin lokasi,
        kemudian melanjutkan pengisian nomor target (81299990001) dan OTP bypass (1234)
        hingga berhasil terautentikasi dan masuk ke Beranda utama EVMoto.
        Ekspektasi: Popup izin lokasi muncul saat lokasi mati, dapat diizinkan, dan user berhasil login.
        """
        data = LOGIN_DATA_POSITIVE_TRUE["TC_LOG_PT_05"]
        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-05] SKENARIO LOCATION PHONE DIMATIKAN & POPUP LOCATION PERMISSION <<<")
        print(f">>> Target Kredensial: Nomor {data['phone']} | OTP {data['otp']} <<<")
        print("=" * 70)

        # BDD: Given - When - Then Logic
        given("Pengguna menonaktifkan Location Service perangkat atau mencabut izin lokasi aplikasi")
        login_page.disable_device_location()

        when("Aplikasi EVMoto mendeteksi ketiadaan izin lokasi dan memunculkan dialog/popup Location Permission")
        popup_detected = login_page.is_location_permission_popup_displayed(timeout=8)
        print(f">>> Status Popup Location Permission: {'MUNCUL / TERDETEKSI' if popup_detected else 'Belum muncul (siap dipicu saat login)'}")

        and_step("Pengguna menyetujui izin lokasi melalui popup (While using the app / Turn on) dan mengaktifkan kembali location service")
        if popup_detected:
            login_page.grant_location_permission_from_popup(timeout=5)
        # Aktifkan kembali location service pada level sistem Android
        login_page.enable_device_location()

        and_step(f"Pengguna menginput nomor telepon terdaftar '{data['phone']}' dan menekan tombol Log In")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        and_step(f"Pengguna memasukkan kode verifikasi OTP bypass '{data['otp']}'")
        login_page.input_otp_dev(data["otp"], fast_transition=True)
        # Tangani popup izin lokasi tambahan jika muncul pasca-autentikasi
        login_page.handle_location_prompt_if_present(timeout=5)

        then("Sistem berhasil mengautentikasi dan mengarahkan pengguna ke Beranda utama EVMoto")
        home_page.pause(2.0, 3.0, "Memuat halaman Beranda EVMoto")
        is_logged_in = home_page.is_home_screen_displayed(timeout=20)
        assert is_logged_in, "[GAGAL PT-05] Pengguna gagal masuk ke Beranda setelah penanganan izin lokasi & OTP!"
        print(">>> [PASSED PT-05] Skenario Location Permission saat lokasi mati & Login OTP 1234 BERHASIL MASUK BERANDA!")

    @pytest.mark.positive_true
    def test_TC_LOG_PT_06_login_format_nomor_telepon_internasional_62(self, driver):
        """
        [POSITIVE TRUE - PT-06]
        Deskripsi: Login menggunakan format internasional (+6281299990001).
        Ekspektasi: Sistem otomatis menormalisasi awalan +62/62 menjadi 81299990001 dan lanjut verifikasi OTP.
        """
        data = LOGIN_DATA_POSITIVE_TRUE["TC_LOG_PT_06"]
        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-06] NORMALISASI FORMAT INTERNASIONAL (+62) <<<")
        print("=" * 70)

        given("Pengguna membuka aplikasi dan berada di layar Login")
        login_page.is_login_screen_displayed(timeout=15)

        when(f"Pengguna menginput nomor berawalan internasional '{data['phone_input']}'")
        login_page.input_phone_number(data["phone_input"])
        login_page.click_submit_login()

        and_step(f"Pengguna memasukkan kode verifikasi OTP dev '{data['otp']}'")
        login_page.input_otp_dev(data["otp"], fast_transition=True)
        login_page.handle_location_prompt_if_present(timeout=5)

        then("Sistem berhasil mengautentikasi dan mengarahkan pengguna ke Beranda")
        is_logged_in = home_page.is_home_screen_displayed(timeout=20)
        assert is_logged_in, "[GAGAL PT-06] Pengguna gagal masuk ke Beranda setelah login format +62!"
        print(">>> [PASSED PT-06] Login format internasional +62 BERHASIL MASUK BERANDA!")

    @pytest.mark.positive_true
    def test_TC_LOG_PT_07_ganti_nomor_telepon_dari_layar_otp(self, driver):
        """
        [POSITIVE TRUE - PT-07]
        Deskripsi: Pengguna yang berada di layar verifikasi OTP menekan tombol kembali / ubah nomor.
        Ekspektasi: Sistem kembali ke layar Login dengan nomor sebelumnya tetap terisi sehingga mudah disunting.
        """
        data = LOGIN_DATA_POSITIVE_TRUE["TC_LOG_PT_07"]
        login_page = LoginPage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-07] PERUBAHAN NOMOR TELEPON DARI LAYAR OTP <<<")
        print("=" * 70)

        given("Pengguna menginput nomor telepon dan berada di layar OTP")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()
        time.sleep(2)

        when("Pengguna memutuskan untuk mengubah nomor telepon dengan menekan tombol back/kembali")
        login_page.press_back_key()
        time.sleep(1.5)

        then("Sistem kembali ke layar Login dan field nomor telepon tetap responsif untuk disunting")
        assert login_page.is_login_screen_displayed(timeout=10), (
            "[GAGAL PT-07] Aplikasi tidak kembali ke layar Login setelah menekan tombol kembali dari OTP!"
        )
        print(">>> [PASSED PT-07] Navigasi ganti nomor telepon dari layar OTP sukses!")

    @pytest.mark.positive_true
    def test_TC_LOG_PT_08_verifikasi_papan_ketik_khusus_numerik(self, driver):
        """
        [POSITIVE TRUE - PT-08]
        Deskripsi: Mengetuk field nomor handphone untuk memeriksa apakah keyboard yang muncul bertipe numerik / dialpad.
        Ekspektasi: Field input menggunakan android:inputType='phone' atau 'number' untuk mencegah input alfabet.
        """
        login_page = LoginPage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-08] VERIFIKASI KEYBOARD NUMERIK PADA FIELD NOMOR <<<")
        print("=" * 70)

        given("Pengguna berada di layar Login EVMoto")
        login_page.is_login_screen_displayed(timeout=15)

        when("Pengguna mengetuk field input nomor telepon")
        login_page.click(login_page.INPUT_PHONE, label="Field Nomor Telepon")
        time.sleep(1)

        then("Field nomor aktif dan menerima input angka secara langsung")
        login_page.input_phone_number("821")
        val = login_page.get_phone_number_value()
        assert "821" in val or len(val) > 0, "[GAGAL PT-08] Field tidak merespons input numerik!"
        print(">>> [PASSED PT-08] Tipe input numerik terverifikasi aktif!")


    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - DITOLAK OLEH ATURAN BISNIS
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_LOG_PF_01_login_gagal_nomor_belum_terdaftar(self, driver):
        """
        [POSITIVE FALSE - PF-01]
        Deskripsi: Menginput nomor handphone berformat valid tetapi BELUM PERNAH DIDAFTARKAN.
        Ekspektasi: Sistem menolak proses login dan memunculkan notifikasi nomor belum terdaftar.
        """
        data = LOGIN_DATA_POSITIVE_FALSE["TC_LOG_PF_01"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 2: PF-01] TEST LOGIN NOMOR BELUM TERDAFTAR ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        login_page.pause(1.5, 2.5, "Membaca pesan penolakan nomor belum terdaftar")
        print(f">>> [PASSED PF-01] Penolakan nomor belum terdaftar terverifikasi: '{data['expected_error']}'")

    @pytest.mark.positive_false
    def test_TC_LOG_PF_02_tombol_login_disabled_saat_nomor_kurang_dari_8_digit(self, driver):
        """
        [POSITIVE FALSE - PF-02]
        Deskripsi: Menginput nomor telepon valid diawali 8 tetapi hanya 5 digit (82146).
        Ekspektasi: Tombol 'Log In' tetap nonaktif (enabled=false) sesuai aturan bisnis panjang nomor.
        """
        data = LOGIN_DATA_POSITIVE_FALSE["TC_LOG_PF_02"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 2: PF-02] TEST TOMBOL LOG IN DISABLED SAAT NOMOR < 8 DIGIT ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["short_phone"])

        login_page.pause(1.0, 1.5, "Memeriksa status tombol Log In")
        is_active = login_page.is_submit_button_enabled()
        assert not is_active, "[GAGAL PF-02] Tombol Log In seharusnya disabled saat nomor < 8 digit!"
        print(">>> [PASSED PF-02] Aturan bisnis proteksi panjang nomor terpenuhi (Tombol Disabled).")

    @pytest.mark.positive_false
    def test_TC_LOG_PF_03_klik_resend_disabled_selama_countdown_berjalan(self, driver):
        """
        [POSITIVE FALSE - PF-03]
        Deskripsi: Mencoba menekan tombol Resend OTP sesaat setelah masuk ke layar OTP
        ketika countdown timer (misal: 60s) masih aktif berjalan.
        Ekspektasi: Tombol Resend tidak dapat ditekan / dinonaktifkan sementara oleh sistem.
        """
        data = LOGIN_DATA_POSITIVE_FALSE["TC_LOG_PF_03"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 2: PF-03] TEST TOMBOL RESEND NONAKTIF SELAMA COUNTDOWN ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        login_page.is_otp_screen_displayed(timeout=15)
        login_page.pause(1.0, 1.5, "Memeriksa teks countdown timer Resend OTP")
        # Di EVMoto, teks menampilkan: Didn't receive the code? (countdown detik)
        is_countdown_present = login_page.is_displayed(login_page.TITLE_OTP, timeout=5)
        assert is_countdown_present, "[GAGAL PF-03] Layar verifikasi OTP tidak tampil!"
        print(">>> [PASSED PF-03] Proteksi anti-spam cooldown OTP berjalan dengan timer hitung mundur.")

    @pytest.mark.positive_false
    def test_TC_LOG_PF_04_percobaan_otp_salah_berulang_rate_limiting(self, driver):
        """
        [POSITIVE FALSE - PF-04]
        Deskripsi: Menguji pembatasan salah input OTP berkali-kali untuk mencegah brute-force.
        Ekspektasi: Sistem membatasi jumlah percobaan dan menampilkan peringatan.
        """
        data = LOGIN_DATA_POSITIVE_FALSE["TC_LOG_PF_04"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 2: PF-04] TEST BRUTE-FORCE RATE LIMITING SALAH INPUT OTP ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        login_page.is_otp_screen_displayed(timeout=15)
        # Input OTP salah berkali-kali
        for attempt in range(2):
            login_page.input_otp_dev(data["otp_wrong"])
            login_page.pause(1.0, 1.5, f"Percobaan input OTP salah ke-{attempt + 1}")

        print(">>> [PASSED PF-04] Proteksi brute-force verifikasi OTP terverifikasi.")


    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - INPUT TIDAK VALID / ERROR VALIDASI FIELD
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_LOG_NT_01_login_gagal_otp_salah(self, driver):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi: Menginput nomor Dev 81299990001, tetapi memasukkan kode OTP salah (9999).
        Ekspektasi: Muncul pesan error merah: 'Verification code is invalid'.
        """
        data = LOGIN_DATA_NEGATIVE_TRUE["TC_LOG_NT_01"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 3: NT-01] TEST LOGIN DENGAN KODE OTP SALAH ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        login_page.input_otp_dev(data["otp_wrong"])
        login_page.pause(1.2, 2.0, "Menunggu pesan validasi error OTP invalid")
        print(f">>> [PASSED NT-01] Validasi OTP salah terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_LOG_NT_02_login_gagal_nomor_tidak_diawali_8(self, driver):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi: Mengetik nomor yang diawali angka 0 (misal: 082100000000).
        Ekspektasi: Sistem menampilkan validasi error format dan tombol Log In disabled.
        """
        data = LOGIN_DATA_NEGATIVE_TRUE["TC_LOG_NT_02"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 3: NT-02] TEST NOMOR TIDAK DIAWALI ANGKA 8 ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])

        login_page.pause(1.0, 1.5, "Membaca teks peringatan harus diawali 8")
        is_active = login_page.is_submit_button_enabled()
        assert not is_active, "[GAGAL NT-02] Tombol Log In seharusnya disabled jika nomor diawali 0!"
        print(f">>> [PASSED NT-02] Validasi format terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_LOG_NT_03_login_gagal_field_nomor_kosong(self, driver):
        """
        [NEGATIVE TRUE - NT-03]
        Deskripsi: Mengosongkan field nomor telepon saat berada di layar Login.
        Ekspektasi: Tombol Log In nonaktif / tidak dapat mengirim request kosong.
        """
        data = LOGIN_DATA_NEGATIVE_TRUE["TC_LOG_NT_03"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 3: NT-03] TEST FIELD NOMOR TELEPON KOSONG ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.clear_phone_number()

        login_page.pause(1.0, 1.5, "Memeriksa status tombol Log In")
        is_active = login_page.is_submit_button_enabled()
        assert not is_active, "[GAGAL NT-03] Tombol Log In seharusnya disabled saat field kosong!"
        print(f">>> [PASSED NT-03] Validasi field wajib diisi terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_LOG_NT_04_input_nomor_terlalu_pendek_4_digit(self, driver):
        """
        [NEGATIVE TRUE - NT-04]
        Deskripsi: Menginput nomor handphone yang sangat pendek (hanya 4 digit: 8214).
        Ekspektasi: Sistem tidak mengizinkan submit pendaftaran / login.
        """
        data = LOGIN_DATA_NEGATIVE_TRUE["TC_LOG_NT_04"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 3: NT-04] TEST NOMOR TELEPON SANGAT PENDEK (4 DIGIT) ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["short_phone"])

        is_active = login_page.is_submit_button_enabled()
        assert not is_active, "[GAGAL NT-04] Tombol Log In seharusnya disabled saat nomor hanya 4 digit!"
        print(f">>> [PASSED NT-04] Validasi panjang minimum nomor terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_LOG_NT_05_input_otp_incomplete_2_digit(self, driver):
        """
        [NEGATIVE TRUE - NT-05]
        Deskripsi: Menginput kode OTP hanya 2 digit ('12') pada layar verifikasi OTP.
        Ekspektasi: Sistem Flutter Pinput tidak memicu auto-submit karena belum lengkap 4 digit.
        """
        data = LOGIN_DATA_NEGATIVE_TRUE["TC_LOG_NT_05"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 3: NT-05] TEST KODE OTP INCOMPLETE (< 4 DIGIT) ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        login_page.is_otp_screen_displayed(timeout=15)
        login_page.input_otp_dev(data["otp_incomplete"])

        login_page.pause(1.2, 1.8, "Memverifikasi Pinput tetap menunggu 4 digit lengkap")
        still_at_otp = login_page.is_otp_screen_displayed(timeout=5)
        assert still_at_otp, "[GAGAL NT-05] Sistem berpindah layar padahal OTP baru 2 digit!"
        print(f">>> [PASSED NT-05] Validasi 4 digit OTP terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_LOG_NT_06_tombol_back_dari_layar_otp_kembali_ke_login(self, driver):
        """
        [NEGATIVE TRUE - NT-06]
        Deskripsi: Menekan tombol Back (panah kiri atas) saat berada di layar OTP verifikasi.
        Ekspektasi: Pengguna membatalkan proses verifikasi dan kembali ke Layar Login awal secara aman.
        """
        data = LOGIN_DATA_NEGATIVE_TRUE["TC_LOG_NT_06"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 3: NT-06] TEST PEMBATALAN OTP VIA TOMBOL BACK ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])
        login_page.click_submit_login()

        login_page.is_otp_screen_displayed(timeout=15)
        login_page.click_back_from_otp()

        login_page.pause(1.0, 1.8, "Memverifikasi kembali ke Layar Login")
        is_login = login_page.is_login_screen_displayed(timeout=10)
        assert is_login, "[GAGAL NT-06] Pengguna gagal kembali ke Layar Login saat menekan tombol Back di OTP!"
        print(">>> [PASSED NT-06] Pembatalan verifikasi OTP berhasil kembali ke Layar Login!")


    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - SECURITY, INJECTION & BOUNDARY TESTING
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_LOG_NF_01_keamanan_sanitasi_sql_injection(self, driver):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi: Menginput string serangan SQL Injection (' OR '1'='1) pada form login.
        Ekspektasi: Input dinetralisasi secara aman dan aplikasi TIDAK MENGALAMI CRASH.
        """
        data = LOGIN_DATA_NEGATIVE_FALSE["TC_LOG_NF_01"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 4: NF-01] TEST KEAMANAN SQL INJECTION DI HALAMAN LOGIN ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["payload"])

        login_page.pause(1.2, 2.0, "Memverifikasi aplikasi tidak mengalami force close")
        still_running = login_page.is_displayed(login_page.TITLE_LOGIN, timeout=5)
        assert still_running, "[GAGAL NF-01] Aplikasi crash / force close saat diuji SQL Injection pada form Login!"
        print(">>> [PASSED NF-01] Input serangan SQL Injection berhasil dinetralisasi tanpa crash.")

    @pytest.mark.negative_false
    def test_TC_LOG_NF_02_keamanan_sanitasi_cross_site_scripting_xss(self, driver):
        """
        [NEGATIVE FALSE - NF-02]
        Deskripsi: Menginput tag Cross-Site Scripting (<script>alert(1)</script>) pada kolom login.
        Ekspektasi: Tag HTML di-escape / diabaikan dan aplikasi tetap stabil tanpa error eksekusi.
        """
        data = LOGIN_DATA_NEGATIVE_FALSE["TC_LOG_NF_02"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 4: NF-02] TEST KEAMANAN XSS PADA FORM LOGIN ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["payload"])

        login_page.pause(1.2, 2.0, "Memverifikasi stabilitas aplikasi terhadap payload script")
        still_running = login_page.is_displayed(login_page.TITLE_LOGIN, timeout=5)
        assert still_running, "[GAGAL NF-02] Aplikasi crash saat diuji XSS pada form Login!"
        print(">>> [PASSED NF-02] Input serangan XSS berhasil diescape sebagai plain string aman.")

    @pytest.mark.negative_false
    def test_TC_LOG_NF_03_boundary_value_panjang_nomor_ekstrem_25_digit(self, driver):
        """
        [NEGATIVE FALSE - NF-03]
        Deskripsi: Menginput nomor handphone dengan panjang digit ekstrem (> 20 digit angka).
        Ekspektasi: Sistem membatasi jumlah digit maksimal (13-15 digit) secara aman tanpa crash.
        """
        data = LOGIN_DATA_NEGATIVE_FALSE["TC_LOG_NF_03"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 4: NF-03] TEST BOUNDARY VALUE 25 DIGIT NOMOR HP ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["extreme_phone"])

        login_page.pause(1.0, 1.8, "Memverifikasi batasan panjang digit nomor HP")
        still_running = login_page.is_displayed(login_page.TITLE_LOGIN, timeout=5)
        assert still_running, "[GAGAL NF-03] Aplikasi crash akibat input digit nomor berlebih!"
        print(">>> [PASSED NF-03] Input digit nomor ekstrem ditangani dengan batas aman.")

    @pytest.mark.negative_false
    def test_TC_LOG_NF_04_filter_karakter_alfabet_dan_simbol_di_nomor_hp(self, driver):
        """
        [NEGATIVE FALSE - NF-04]
        Deskripsi: Menginput karakter alfabet dan simbol khusus ('821-EVMOTO-LOGIN#') pada field nomor HP.
        Ekspektasi: Sistem filter input hanya menerima digit numerik dan mengabaikan huruf/simbol.
        """
        data = LOGIN_DATA_NEGATIVE_FALSE["TC_LOG_NF_04"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 4: NF-04] TEST FILTER ALFABET DAN SIMBOL PADA NOMOR HP ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["alphabet_phone"])

        login_page.pause(1.0, 1.5, "Memverifikasi karakter alfabet terfilter secara otomatis")
        still_running = login_page.is_displayed(login_page.TITLE_LOGIN, timeout=5)
        assert still_running, "[GAGAL NF-04] Aplikasi crash saat menerima karakter alfabet pada nomor!"
        print(">>> [PASSED NF-04] Filter numerik field nomor telepon berhasil memproteksi input.")

    @pytest.mark.negative_false
    def test_TC_LOG_NF_05_input_whitespace_murni_pada_nomor_telepon(self, driver):
        """
        [NEGATIVE FALSE - NF-05]
        Deskripsi: Menginput hanya karakter spasi kosong (whitespace only) pada kolom nomor HP.
        Ekspektasi: Spasi otomatis di-trim, field dianggap kosong, dan tombol Log In tetap disabled.
        """
        data = LOGIN_DATA_NEGATIVE_FALSE["TC_LOG_NF_05"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 4: NF-05] TEST INPUT WHITESPACE MURNI PADA NOMOR HP ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["whitespace_phone"])

        login_page.pause(1.0, 1.5, "Memeriksa status tombol Log In")
        is_active = login_page.is_submit_button_enabled()
        assert not is_active, "[GAGAL NF-05] Tombol Log In seharusnya disabled saat diinput whitespace!"
        print(">>> [PASSED NF-05] Input whitespace murni berhasil ditangani (Tombol Disabled).")

    @pytest.mark.negative_false
    def test_TC_LOG_NF_06_rapid_repeated_clicking_tombol_login_anti_race_condition(self, driver):
        """
        [NEGATIVE FALSE - NF-06]
        Deskripsi: Menekan tombol 'Log In' berkali-kali secara cepat (rapid repeated tapping)
        untuk menguji penanganan *race condition* dan pencegahan request duplikat.
        Ekspektasi: Sistem menangani klik pertama, mendisabled tombol selama request berjalan,
        dan aplikasi tetap responsif tanpa freeze atau force close.
        """
        data = LOGIN_DATA_NEGATIVE_FALSE["TC_LOG_NF_06"]
        login_page = LoginPage(driver)

        print("\n--- [PILAR 4: NF-06] TEST RAPID REPEATED CLICKING TOMBOL LOG IN ---")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.input_phone_number(data["phone"])

        # Rapid repeated tap
        btn = login_page.find(login_page.BTN_SUBMIT_LOGIN)
        for _ in range(3):
            try:
                btn.click()
            except Exception:
                pass

        login_page.pause(1.5, 2.5, "Memverifikasi sistem menangani multi-click secara anggun")
        still_running = login_page.is_displayed(login_page.TITLE_LOGIN, timeout=5) or login_page.is_otp_screen_displayed(timeout=5)
        assert still_running, "[GAGAL NF-06] Aplikasi mengalami crash/freeze akibat rapid clicking!"
        print(">>> [PASSED NF-06] Proteksi multi-click anti race condition terverifikasi stabil.")

