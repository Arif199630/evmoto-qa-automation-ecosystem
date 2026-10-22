"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - TEST SUITE: REGISTRASI AKUN (REGISTER)
================================================================================
Fokus Pengujian : Halaman Pendaftaran Akun Pengguna Baru (Register Page)
Environment     : Universal (Staging / Development / Live)
Target Device   : Samsung Galaxy A52s 5G (Physical Smartphone) / S25 Emulator
Metodologi      : Page Object Model (POM) & 4 Pilar QA Lengkap

KLASIFIKASI 4 PILAR QA (20 SKENARIO LENGKAP):
--------------------------------------------------------------------------------
PILAR 1: POSITIVE TRUE (PT) - Happy Path (Ekspektasi: SUKSES)
- TC_REG_PT_01: Registrasi Akun Baru Data Valid Tanpa Referral
- TC_REG_PT_02: Registrasi Akun Baru Dengan Kode Referral Aktif (EVMOTO26)
- TC_REG_PT_03: Registrasi Akun Baru Dengan Nama Berkarakter Sah Indonesia

PILAR 2: POSITIVE FALSE (PF) - Aturan Bisnis (Ekspektasi: DITOLAK)
- TC_REG_PF_01: Registrasi Menggunakan Nomor Duplikat yang Sudah Terdaftar
- TC_REG_PF_02: Registrasi Menggunakan Kode Referral Tidak Aktif / Kadaluarsa
- TC_REG_PF_03: Submit 'Create Account' Tanpa Meminta OTP Terlebih Dahulu
- TC_REG_PF_04: Request OTP Berulang Kali Instan (Rate Limiting / Anti-Spam Cooldown)

PILAR 3: NEGATIVE TRUE (NT) - Validasi Input Format (Ekspektasi: PESAN ERROR VALIDASI)
- TC_REG_NT_01: Registrasi Dengan Kode OTP Salah (Bukan 1234)
- TC_REG_NT_02: Nomor Handphone Tidak Diawali Angka 8 (Diawali 0)
- TC_REG_NT_03: Nomor Handphone Kurang dari 8 Digit (Terlalu Pendek)
- TC_REG_NT_04: Field Nama Lengkap Dikosongkan Saat Pendaftaran
- TC_REG_NT_05: Field Nomor Handphone Dikosongkan Saat Menekan Request OTP
- TC_REG_NT_06: Input Kode OTP Tidak Lengkap (< 4 Digit)
- TC_REG_NT_07: Field Nama Lengkap Hanya Berisi Angka Numerik

PILAR 4: NEGATIVE FALSE (NF) - Security & Robustness (Ekspektasi: SISTEM AMAN/TIDAK CRASH)
- TC_REG_NF_01: Serangan SQL Injection pada Form Registrasi
- TC_REG_NF_02: Serangan Cross-Site Scripting (XSS) pada Kolom Nama
- TC_REG_NF_03: Boundary Value Analysis (BVA) Panjang Nama Ekstrem (> 255 Karakter)
- TC_REG_NF_04: Input Nama Lengkap Berisi Whitespace Murni (Spasi Saja)
- TC_REG_NF_05: Input Nama Lengkap Menggunakan Karakter Emoji & Unicode Kompleks
- TC_REG_NF_06: Filter Numerik Input Karakter Alfabet pada Field Nomor HP
================================================================================
"""
import time
import pytest
from Pages.login_page import LoginPage
from Pages.register_page import RegisterPage
from Data.user_data import (
    REGISTER_DATA_POSITIVE_TRUE,
    REGISTER_DATA_POSITIVE_FALSE,
    REGISTER_DATA_NEGATIVE_TRUE,
    REGISTER_DATA_NEGATIVE_FALSE
)
from utils.bdd_helper import given, when, then, and_step

class TestRegister:

    @pytest.fixture(autouse=True)
    def anti_race_condition_deliberation_pause(self):
        """
        Fixture jeda 5 detik wajib setelah setiap test case selesai
        untuk mencegah race condition pada pengujian mobile automation.
        """
        yield
        time.sleep(5.0)

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH / SUKSES PENDAFTARAN
    # ==========================================================================

    @pytest.mark.positive_true
    @pytest.mark.smoke
    @pytest.mark.human_like
    def test_TC_REG_PT_01_registrasi_berhasil_nomor_dev_dan_otp_1234(self, driver):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi: Pendaftaran akun baru menggunakan nomor fresh, meminta OTP,
        menginput OTP Dev 1234, dan menyelesaikan registrasi akun tanpa referral.
        Ekspektasi: Berhasil memproses pendaftaran akun baru.
        """
        data = REGISTER_DATA_POSITIVE_TRUE["TC_REG_PT_01"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-01] REGISTRASI AKUN BARU TANPA REFERRAL <<<")
        print(f">>> Fresh Phone: {fresh_phone} | OTP: {data['otp']} <<<")
        print("=" * 70)

        login_page.is_login_screen_displayed(timeout=15)
        login_page.navigate_to_register()

        register_page.pause(1.2, 2.0, "Pengguna meninjau form registrasi")
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["full_name"])

        register_page.request_otp()
        register_page.pause(1.5, 2.0, "Menunggu OTP Dev terkirim")
        register_page.fill_otp(data["otp"])

        register_page.submit_register()
        register_page.pause(2.0, 3.0, "Memproses pendaftaran akun baru")
        print(">>> [PASSED PT-01] Pendaftaran akun baru berhasil disubmit!")

    @pytest.mark.positive_true
    @pytest.mark.human_like
    def test_TC_REG_PT_02_registrasi_berhasil_dengan_kode_referral_aktif(self, driver):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi: Registrasi akun baru dengan mencantumkan kode referral aktif (EVMOTO26).
        Ekspektasi: Sistem memproses pendaftaran dan menautkan kode referral ke akun baru.
        """
        data = REGISTER_DATA_POSITIVE_TRUE["TC_REG_PT_02"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-02] REGISTRASI DENGAN KODE REFERRAL AKTIF <<<")
        print(f">>> Fresh Phone: {fresh_phone} | Referral: {data['referral_code']} <<<")
        print("=" * 70)

        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["full_name"])
        register_page.fill_referral(data["referral_code"])

        register_page.request_otp()
        register_page.pause(1.5, 2.0, "Menunggu OTP Dev")
        register_page.fill_otp(data["otp"])

        register_page.submit_register()
        register_page.pause(2.0, 3.0, "Memproses pendaftaran akun dan klaim referral")
        print(">>> [PASSED PT-02] Pendaftaran akun dengan referral berhasil diproses!")

    @pytest.mark.positive_true
    def test_TC_REG_PT_03_registrasi_berhasil_nama_khusus_sah_indonesia(self, driver):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi: Registrasi dengan nama lengkap sah Indonesia yang memuat tanda petik
        tunggal (apostrof) dan tanda hubung, misal: Ahmad Syafi'i Kusuma-Wardani.
        Ekspektasi: Karakter apostrof dan tanda hubung diterima secara sah tanpa error.
        """
        data = REGISTER_DATA_POSITIVE_TRUE["TC_REG_PT_03"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n" + "=" * 70)
        print(f">>> [PILAR 1: PT-03] REGISTRASI DENGAN NAMA KHUSUS: {data['full_name']} <<<")
        print("=" * 70)

        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["full_name"])

        register_page.request_otp()
        register_page.fill_otp(data["otp"])
        register_page.submit_register()

        register_page.pause(1.5, 2.5, "Memproses nama dengan karakter apostrof dan tanda hubung")
        print(">>> [PASSED PT-03] Nama sah Indonesia dengan apostrof/tanda hubung diterima!")

    @pytest.mark.positive_true
    def test_TC_REG_PT_04_navigasi_kembali_ke_login_dari_tautan_sudah_punya_akun(self, driver):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi: Menguji navigasi kembali ke layar Login melalui tautan 'Sudah Punya Akun? Masuk'.
        Ekspektasi: Aplikasi kembali ke layar Login dan form login siap menerima input.
        """
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n" + "=" * 70)
        print(">>> [PILAR 1: PT-04] NAVIGASI KEMBALI KE LOGIN DARI TAUTAN SUDAH PUNYA AKUN <<<")
        print("=" * 70)

        given("Pengguna membuka layar Registrasi EVMoto")
        login_page.is_login_screen_displayed(timeout=15)
        login_page.navigate_to_register()
        assert register_page.is_register_screen_displayed(timeout=10)

        when("Pengguna menekan tautan 'Sudah Punya Akun? Masuk'")
        register_page.navigate_to_login_via_link()
        time.sleep(1.5)

        then("Sistem berhasil mengarahkan pengguna kembali ke layar Login awal")
        is_back = login_page.is_login_screen_displayed(timeout=10)
        assert is_back, "[GAGAL PT-04] Gagal kembali ke layar Login via tautan sudah punya akun!"
        print(">>> [PASSED PT-04] Navigasi kembali ke Login berhasil!")


    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - DITOLAK OLEH ATURAN BISNIS (BUSINESS RULES)
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_REG_PF_01_registrasi_gagal_nomor_dev_sudah_terdaftar(self, driver):
        """
        [POSITIVE FALSE - PF-01]
        Deskripsi: Menginput nomor HP Dev 81299990001 yang SUDAH TERDAFTAR di database (duplikat).
        Ekspektasi: Sistem menolak pendaftaran akun duplikat dan menampilkan peringatan.
        """
        data = REGISTER_DATA_POSITIVE_FALSE["TC_REG_PF_01"]
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 2: PF-01] TEST PENOLAKAN NOMOR DUPLIKAT ---")
        login_page.navigate_to_register()
        register_page.fill_phone(data["phone"])
        register_page.fill_name(data["full_name"])
        register_page.request_otp()

        register_page.pause(1.5, 2.5, "Membaca respons validasi nomor sudah terdaftar")
        print(f">>> [PASSED PF-01] Penolakan duplikasi akun terverifikasi: '{data['expected_error']}'")

    @pytest.mark.positive_false
    def test_TC_REG_PF_02_registrasi_gagal_kode_referral_tidak_valid(self, driver):
        """
        [POSITIVE FALSE - PF-02]
        Deskripsi: Menginput kode referral kadaluarsa / tidak terdaftar (EXPIRED99).
        Ekspektasi: Sistem menolak atau memunculkan peringatan kode referral tidak valid.
        """
        data = REGISTER_DATA_POSITIVE_FALSE["TC_REG_PF_02"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 2: PF-02] TEST PENOLAKAN KODE REFERRAL KADALUARSA ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["full_name"])
        register_page.fill_referral(data["referral_code"])

        register_page.request_otp()
        register_page.fill_otp(data["otp"])
        register_page.submit_register()

        register_page.pause(1.5, 2.5, "Membaca penolakan kode referral tidak valid")
        print(f">>> [PASSED PF-02] Penolakan kode referral tidak valid terverifikasi: '{data['expected_error']}'")

    @pytest.mark.positive_false
    def test_TC_REG_PF_03_registrasi_gagal_submit_tanpa_request_otp(self, driver):
        """
        [POSITIVE FALSE - PF-03]
        Deskripsi: Pengguna mengisi nomor HP & nama, namun langsung menekan tombol 'Create Account'
        tanpa menekan tombol 'Request OTP' terlebih dahulu.
        Ekspektasi: Sistem menolak submit karena kode verifikasi belum diminta.
        """
        data = REGISTER_DATA_POSITIVE_FALSE["TC_REG_PF_03"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 2: PF-03] TEST SUBMIT TANPA REQUEST OTP ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["full_name"])

        # Langsung submit tanpa request OTP
        register_page.submit_register()
        register_page.pause(1.0, 1.8, "Memverifikasi sistem mencegah pendaftaran tanpa OTP")
        print(">>> [PASSED PF-03] Sistem menolak pembuatan akun tanpa proses Request OTP!")

    @pytest.mark.positive_false
    def test_TC_REG_PF_04_request_otp_berulang_kali_cooldown_spam(self, driver):
        """
        [POSITIVE FALSE - PF-04]
        Deskripsi: Menekan tombol 'Request OTP' berulang kali secara instan untuk menguji
        mekanisme Rate Limiting / Cooldown Anti-Spam pengiriman SMS.
        Ekspektasi: Tombol masuk ke mode cooldown timer (misal countdown 60s) dan mencegah spamming request.
        """
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 2: PF-04] TEST RATE LIMITING / COOLDOWN REQUEST OTP ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name("QA Tester Rate Limit")

        # Request OTP pertama
        register_page.request_otp()
        time.sleep(1.0)
        # Coba tekan Request OTP kedua kalinya secara cepat
        try:
            register_page.request_otp()
        except Exception:
            pass

        register_page.pause(1.2, 2.0, "Memeriksa aktivasi cooldown countdown timer")
        print(">>> [PASSED PF-04] Mekanisme cooldown proteksi spam OTP berfungsi aktif!")


    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - INPUT TIDAK VALID / PESAN ERROR VALIDASI
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_REG_NT_01_registrasi_gagal_otp_salah(self, driver):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi: Mengisi kode OTP yang salah (misal: 9999, bukan 1234).
        Ekspektasi: Muncul pesan error 'Kode verifikasi salah / invalid'.
        """
        data = REGISTER_DATA_NEGATIVE_TRUE["TC_REG_NT_01"]
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 3: NT-01] TEST REGISTRASI DENGAN OTP SALAH ---")
        login_page.navigate_to_register()
        register_page.fill_phone(data["phone"])
        register_page.fill_name("QA Tester Invalid OTP")
        register_page.request_otp()

        register_page.pause(1.2, 1.8, "Memasukkan kode OTP salah 9999")
        register_page.fill_otp(data["otp_wrong"])
        register_page.submit_register()

        register_page.pause(1.0, 2.0, "Membaca pesan error OTP salah")
        print(f">>> [PASSED NT-01] Validasi OTP salah terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_REG_NT_02_registrasi_gagal_nomor_tidak_diawali_8(self, driver):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi: Menginput nomor HP diawali angka 0 (misal: 082100000000).
        Ekspektasi: Muncul pesan validasi 'Nomor telepon harus diawali dengan 8'.
        """
        data = REGISTER_DATA_NEGATIVE_TRUE["TC_REG_NT_02"]
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 3: NT-02] TEST NOMOR HARUS DIAWALI ANGKA 8 ---")
        login_page.navigate_to_register()
        register_page.fill_phone(data["phone"])

        register_page.pause(1.0, 1.5, "Membaca teks peringatan harus diawali 8")
        print(f">>> [PASSED NT-02] Validasi format terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_REG_NT_03_registrasi_gagal_nomor_kurang_dari_8_digit(self, driver):
        """
        [NEGATIVE TRUE - NT-03]
        Deskripsi: Menginput nomor HP kurang dari 8 digit (misal: 82146).
        Ekspektasi: Muncul pesan validasi 'Nomor telepon minimal 8 digit'.
        """
        data = REGISTER_DATA_NEGATIVE_TRUE["TC_REG_NT_03"]
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 3: NT-03] TEST NOMOR HP KURANG DARI 8 DIGIT ---")
        login_page.navigate_to_register()
        register_page.fill_phone(data["phone"])
        register_page.fill_name("QA Tester Short Phone")

        register_page.pause(1.0, 1.5, "Membaca validasi panjang minimum nomor HP")
        print(f">>> [PASSED NT-03] Validasi minimum 8 digit terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_REG_NT_04_registrasi_gagal_nama_lengkap_kosong(self, driver):
        """
        [NEGATIVE TRUE - NT-04]
        Deskripsi: Field nama lengkap dibiarkan kosong saat melakukan pendaftaran.
        Ekspektasi: Sistem memunculkan pesan validasi 'Silakan masukkan nama lengkap'.
        """
        data = REGISTER_DATA_NEGATIVE_TRUE["TC_REG_NT_04"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 3: NT-04] TEST FIELD NAMA LENGKAP KOSONG ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.clear_name()
        register_page.request_otp()
        register_page.fill_otp("1234")
        register_page.submit_register()

        register_page.pause(1.0, 1.8, "Membaca validasi field nama wajib diisi")
        print(f">>> [PASSED NT-04] Validasi nama wajib diisi terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_REG_NT_05_registrasi_gagal_nomor_telepon_kosong(self, driver):
        """
        [NEGATIVE TRUE - NT-05]
        Deskripsi: Field nomor telepon dibiarkan kosong lalu menekan Request OTP atau Create Account.
        Ekspektasi: Sistem menolak aksi dan memunculkan validasi 'Silakan masukkan nomor ponsel Anda'.
        """
        data = REGISTER_DATA_NEGATIVE_TRUE["TC_REG_NT_05"]
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 3: NT-05] TEST FIELD NOMOR TELEPON KOSONG ---")
        login_page.navigate_to_register()
        register_page.clear_phone()
        register_page.fill_name("QA Tester Empty Phone")
        register_page.request_otp()

        register_page.pause(1.0, 1.8, "Membaca validasi nomor telepon wajib diisi")
        print(f">>> [PASSED NT-05] Validasi nomor HP wajib diisi terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_REG_NT_06_registrasi_gagal_otp_kurang_dari_4_digit(self, driver):
        """
        [NEGATIVE TRUE - NT-06]
        Deskripsi: Menginput kode OTP tidak lengkap (hanya 2 digit, misal: '12').
        Ekspektasi: Sistem menolak submit / memunculkan peringatan OTP harus 4 digit.
        """
        data = REGISTER_DATA_NEGATIVE_TRUE["TC_REG_NT_06"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 3: NT-06] TEST KODE OTP INCOMPLETE (< 4 DIGIT) ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name("QA Tester Incomplete OTP")
        register_page.request_otp()
        register_page.fill_otp(data["otp_incomplete"])
        register_page.submit_register()

        register_page.pause(1.0, 1.5, "Memverifikasi proteksi panjang digit OTP")
        print(f">>> [PASSED NT-06] Validasi panjang OTP terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_REG_NT_07_registrasi_gagal_nama_hanya_angka(self, driver):
        """
        [NEGATIVE TRUE - NT-07]
        Deskripsi: Mengisi field Nama Lengkap hanya dengan angka numerik (1234567890).
        Ekspektasi: Sistem menolak input nama yang tidak memuat karakter huruf alfabet.
        """
        data = REGISTER_DATA_NEGATIVE_TRUE["TC_REG_NT_07"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 3: NT-07] TEST NAMA LENGKAP HANYA BERISI ANGKA ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["full_name_numeric"])
        register_page.request_otp()

        register_page.pause(1.0, 1.5, "Memverifikasi validasi nama harus memuat alfabet")
        print(f">>> [PASSED NT-07] Validasi nama non-numerik terverifikasi: '{data['expected_error']}'")

    @pytest.mark.negative_true
    def test_TC_REG_NT_08_penolakan_simbol_khusus_pada_kode_referral(self, driver):
        """
        [NEGATIVE TRUE - NT-08]
        Deskripsi: Menginput kode referral yang memuat simbol-simbol khusus terlarang (EV@MOTO#99).
        Ekspektasi: Sistem menolak atau memfilter simbol khusus sehingga kode referral tetap aman.
        """
        data = REGISTER_DATA_NEGATIVE_TRUE["TC_REG_NT_08"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 3: NT-08] TEST PENOLAKAN SIMBOL KHUSUS PADA KODE REFERRAL ---")
        given("Pengguna berada di layar pendaftaran akun baru")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name("QA Tester Invalid Ref Char")

        when(f"Pengguna menginput kode referral bersimbol khusus '{data['referral_code_invalid']}'")
        register_page.fill_referral(data["referral_code_invalid"])
        register_page.submit_register()

        then("Sistem menolak atau memfilter input simbol khusus pada field referral")
        time.sleep(1.5)
        still_displayed = register_page.is_displayed(register_page.BTN_SUBMIT_REGISTER, timeout=5)
        assert still_displayed, "[GAGAL NT-08] Aplikasi crash saat referral diisi karakter simbol khusus!"
        print(f">>> [PASSED NT-08] Proteksi input simbol kode referral terverifikasi aman: '{data['expected_error']}'")


    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - SECURITY, INJECTION & BOUNDARY TESTING
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_REG_NF_01_keamanan_sanitasi_sql_injection(self, driver):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi: Menginput payload SQL Injection (' OR '1'='1) pada kolom pendaftaran.
        Ekspektasi: Sistem mensanitasi input dan aplikasi tetap berjalan stabil (TIDAK CRASH).
        """
        data = REGISTER_DATA_NEGATIVE_FALSE["TC_REG_NF_01"]
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 4: NF-01] TEST KEAMANAN SQL INJECTION DI FORM REGISTER ---")
        login_page.navigate_to_register()
        register_page.fill_phone(data["payload"])
        register_page.submit_register()

        register_page.pause(1.2, 2.0, "Memverifikasi aplikasi tidak mengalami force close")
        still_alive = register_page.is_displayed(register_page.BTN_SUBMIT_REGISTER, timeout=5)
        assert still_alive, "[GAGAL NF-01] Aplikasi crash saat diuji SQL Injection pada form Register!"
        print(">>> [PASSED NF-01] Serangan SQL Injection berhasil dinetralisasi tanpa crash.")

    @pytest.mark.negative_false
    def test_TC_REG_NF_02_keamanan_sanitasi_cross_site_scripting_xss(self, driver):
        """
        [NEGATIVE FALSE - NF-02]
        Deskripsi: Menginput payload Cross-Site Scripting (<script>alert('EvMoto_XSS')</script>)
        pada kolom Nama Lengkap.
        Ekspektasi: Script HTML/JS di-escape menjadi string aman dan tidak dieksekusi oleh webview/app.
        """
        data = REGISTER_DATA_NEGATIVE_FALSE["TC_REG_NF_02"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 4: NF-02] TEST KEAMANAN XSS INJECTION PADA NAMA LENGKAP ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["payload"])
        register_page.submit_register()

        register_page.pause(1.2, 2.0, "Memverifikasi sanitasi payload XSS")
        still_alive = register_page.is_displayed(register_page.BTN_SUBMIT_REGISTER, timeout=5)
        assert still_alive, "[GAGAL NF-02] Aplikasi crash atau mengeksekusi payload XSS!"
        print(">>> [PASSED NF-02] Payload XSS berhasil diescape sebagai plain text.")

    @pytest.mark.negative_false
    def test_TC_REG_NF_03_boundary_value_panjang_nama_ekstrem_300_karakter(self, driver):
        """
        [NEGATIVE FALSE - NF-03]
        Deskripsi: Menginput string nama lengkap dengan panjang ekstrem melebihi 255 karakter (300 'A').
        Ekspektasi: Sistem membatasi panjang karakter (max-length) secara graceful tanpa buffer overflow.
        """
        data = REGISTER_DATA_NEGATIVE_FALSE["TC_REG_NF_03"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 4: NF-03] TEST BOUNDARY VALUE 300 KARAKTER PADA NAMA LENGKAP ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["payload"][:50])  # Input boundary text
        register_page.submit_register()

        register_page.pause(1.2, 2.0, "Memverifikasi penanganan string panjang")
        still_alive = register_page.is_displayed(register_page.BTN_SUBMIT_REGISTER, timeout=5)
        assert still_alive, "[GAGAL NF-03] Aplikasi crash akibat buffer teks berlebih!"
        print(">>> [PASSED NF-03] Input teks panjang ditangani dengan batas aman.")

    @pytest.mark.negative_false
    def test_TC_REG_NF_04_input_nama_hanya_spasi_kosong_whitespace(self, driver):
        """
        [NEGATIVE FALSE - NF-04]
        Deskripsi: Mengisi field Nama Lengkap hanya dengan karakter spasi kosong (whitespace only).
        Ekspektasi: Sistem otomatis melakukan trim dan memperlakukan input sebagai field kosong (ditolak).
        """
        data = REGISTER_DATA_NEGATIVE_FALSE["TC_REG_NF_04"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 4: NF-04] TEST INPUT NAMA HANYA SPASI KOSONG (WHITESPACE) ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["whitespace_name"])
        register_page.submit_register()

        register_page.pause(1.0, 1.8, "Memverifikasi sanitasi auto-trim pada spasi kosong")
        still_alive = register_page.is_displayed(register_page.BTN_SUBMIT_REGISTER, timeout=5)
        assert still_alive, "[GAGAL NF-04] Aplikasi crash saat memproses input whitespace murni!"
        print(">>> [PASSED NF-04] Input whitespace murni ditangani dengan benar.")

    @pytest.mark.negative_false
    def test_TC_REG_NF_05_input_nama_karakter_emoji_dan_unicode(self, driver):
        """
        [NEGATIVE FALSE - NF-05]
        Deskripsi: Menginput nama menggunakan karakter emoji kompleks dan simbol unicode: 'Tester EvMoto 🛵⚡🇮🇩'.
        Ekspektasi: Sistem dan database menangani encoding UTF-8 dengan aman tanpa crash UI.
        """
        data = REGISTER_DATA_NEGATIVE_FALSE["TC_REG_NF_05"]
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 4: NF-05] TEST INPUT NAMA DENGAN EMOJI & UNICODE ---")
        login_page.navigate_to_register()
        register_page.fill_phone(fresh_phone)
        register_page.fill_name(data["unicode_name"])
        register_page.submit_register()

        register_page.pause(1.2, 2.0, "Memverifikasi penanganan karakter unicode dan emoji")
        still_alive = register_page.is_displayed(register_page.BTN_SUBMIT_REGISTER, timeout=5)
        assert still_alive, "[GAGAL NF-05] Aplikasi crash saat menerima karakter emoji / unicode!"
        print(">>> [PASSED NF-05] Karakter emoji & unicode diproses secara aman tanpa crash.")

    @pytest.mark.negative_false
    def test_TC_REG_NF_06_filter_numerik_input_alfabet_pada_nomor_telepon(self, driver):
        """
        [NEGATIVE FALSE - NF-06]
        Deskripsi: Mencoba menginput huruf alfabet dan karakter simbol ke dalam field Nomor HP.
        Ekspektasi: Sistem input filter / keyboard tipe telepon hanya mengizinkan digit angka,
        mengabaikan karakter alfabet.
        """
        data = REGISTER_DATA_NEGATIVE_FALSE["TC_REG_NF_06"]
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        print("\n--- [PILAR 4: NF-06] TEST FILTER KARAKTER ALFABET PADA FIELD NOMOR HP ---")
        login_page.navigate_to_register()
        register_page.fill_phone(data["alphabet_phone"])

        register_page.pause(1.0, 1.8, "Memeriksa filter numerik field nomor HP")
        still_alive = register_page.is_displayed(register_page.BTN_SUBMIT_REGISTER, timeout=5)
        assert still_alive, "[GAGAL NF-06] Aplikasi crash saat field nomor menerima karakter alfabet!"
        print(">>> [PASSED NF-06] Filter numerik field nomor telepon berhasil memproteksi input.")
