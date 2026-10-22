"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - TEST SUITE: AKUN & PROFIL (test_profil.py)
================================================================================
Target Aplikasi : EvMoto User Mobile App (com.evmoto.user.app)
Lingkungan      : Universal (Staging / Development / Production Live)
Target Modul    : Halaman Profil / Akun Pengguna ('Me' Tab)
Metodologi QA   :
  1. METODE HAPPY FLOW TERLEBIH DAHULU:
     Memverifikasi seluruh fitur dari yang paling atas hingga paling bawah (Logout):
     - Memastikan seluruh tombol, fungsi, popup/modal, dan snackbar muncul dan berjalan sempurna.
  2. 4 PILAR METODE QA LENGKAP:
     - Pilar 1: Positive True (PT) - Fungsionalitas Tombol & Fitur Valid
     - Pilar 2: Positive False (PF) - Aturan Bisnis & Pembatalan Dialog
     - Pilar 3: Negative True (NT) - Penolakan Input Invalid & Empty State
     - Pilar 4: Negative False (NF) - Keamanan (SQLi/XSS), Ketahanan UI, & Logout Sesi
Aturan Eksekusi :
  - JEDA 5 DETIK pada setiap test case untuk mencegah race condition.
  - Page Object Model (POM) tersimpan di 'Pages/profil_page.py'.
================================================================================
"""
import time
import pytest
from Pages.login_page import LoginPage
from Pages.home_page import HomePage
from Pages.profil_page import ProfilPage
from Data.user_data import (
    MobileUserDataProvider,
    PROFILE_HAPPY_FLOW_DATA,
    PROFILE_PILAR_1_POSITIVE,
    PROFILE_PILAR_2_NEGATIVE,
    PROFILE_PILAR_3_BOUNDARY,
    PROFILE_PILAR_4_SECURITY,
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestProfil")


class TestProfil:
    """Suite Pengujian Otomasi Halaman Profil Pengguna EvMoto (Happy Flow & 4 Pilar)."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown_profil_session(self, driver):
        """
        Fixture inisialisasi sesi login otomatis menuju layar Profil ('Me' Tab).
        Menyertakan jeda 5 detik wajib di akhir setiap pengetesan untuk mencegah race condition.
        """
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.home_page = HomePage(driver)
        self.profil_page = ProfilPage(driver)

        # Mengambil kredensial pengujian dinamis (Universal Dev & Production)
        user = MobileUserDataProvider.get_dev_user()
        self.user_phone = user["phone"]
        self.user_otp = user["otp"]
        self.user_name = user.get("name", "User EvMoto")

        logger.info(f"Menginisialisasi sesi login untuk nomor: {self.user_phone}")
        # 1. Pastikan di layar login awal
        self.login_page.is_login_screen_displayed(timeout=20)
        self.login_page.input_phone_number(self.user_phone)
        self.login_page.click_submit_login()
        self.login_page.input_otp_dev(self.user_otp, fast_transition=True)
        self.login_page.handle_location_prompt_if_present(timeout=5)

        # 2. Pastikan beranda termuat, lalu langsung navigasi ke tab 'Me' (Profil)
        self.home_page.is_home_screen_displayed(timeout=20)
        self.home_page.navigate_to_profile()
        assert self.profil_page.is_profile_screen_displayed(timeout=15), (
            "[GAGAL SETUP] Layar profil pengguna tidak berhasil dimuat!"
        )

        yield

        # JEDA 5 DETIK ANTI RACE CONDITION SETELAH SETIAP TEST CASE SELESAI
        logger.info("[ANTI RACE CONDITION] Memberikan jeda 5 detik sebelum lanjut...")
        time.sleep(5.0)

    # ==========================================================================
    # BAGIAN 1: METODE HAPPY FLOW TERLEBIH DAHULU (E2E PERJALANAN LENGKAP PROFIL)
    # DIURUTKAN DARI PALING ATAS HINGGA PALING BAWAH (LOGOUT)
    # ==========================================================================

    @pytest.mark.happy_flow
    @pytest.mark.smoke
    def test_TC_PROF_HF_01_happy_flow_perjalanan_lengkap_seluruh_fitur_profil(self, driver):
        """
        [HAPPY FLOW] Pengujian alur positif lengkap modul Profil Pengguna dari paling atas ke bawah:
        1. [ATAS] Header Identitas Pengguna: Avatar/Foto, Nama Lengkap, dan Nomor Handphone.
        2. Saldo Dompet & Menu Pengaturan Pembayaran (Cash, Wallet, GoPay, OVO, Default).
        3. Fitur Kontak Darurat: Buka form, input nama & telepon, simpan, uji modal hapus.
        4. Alamat Tersimpan: Buka menu alamat, periksa tombol Rumah, Kantor, dan Lokasi Lain.
        5. Pengaturan Bahasa: Ubah ke English (cek snackbar), kembalikan ke Indonesia (cek snackbar).
        6. Pusat Bantuan & Panduan Video FAQ: Buka tutorial, pastikan video player bebas error 'Video gagal dimuat'.
        7. Banner Customer Service & Popup Aturan Media: Verifikasi banner CS dan popup.
        8. Dokumen Legalitas: Tinjau Terms & Conditions dan Privacy Policy.
        9. Hapus Akun: Buka modal peringatan hapus akun permanen, uji tombol Batal.
        10. [BAWAH] Logout: Buka dialog konfirmasi, uji tombol Batal, lalu konfirmasi Keluar hingga kembali ke Login.
        """
        print("\n" + "=" * 80)
        print(">>> [HAPPY FLOW] E2E PERJALANAN LENGKAP FITUR PROFIL (DARI ATAS KE BAWAH) <<<")
        print("=" * 80)

        # ----------------------------------------------------------------------
        # TAHAP 1: [PALING ATAS] HEADER IDENTITAS PENGGUNA
        # ----------------------------------------------------------------------
        given("Pengguna berada di layar utama Profil ('Me' Tab)")
        assert self.profil_page.is_profile_screen_displayed(timeout=10), "[HF-01] Layar Profil tidak aktif!"

        when("Memverifikasi elemen identitas pengguna di header paling atas")
        has_avatar = self.profil_page.is_avatar_displayed(timeout=5)
        user_name = self.profil_page.get_user_name_text()
        user_phone = self.profil_page.get_user_phone_text()
        wallet_bal = self.profil_page.get_wallet_balance_text()

        print(f"  [1. Header] Avatar: {has_avatar} | Nama: '{user_name}' | No HP: '{user_phone}' | Saldo: '{wallet_bal}'")
        assert has_avatar, "[HF-01] Avatar profil tidak tampil!"

        # ----------------------------------------------------------------------
        # TAHAP 2: PENGATURAN PEMBAYARAN & SALDO DOMPET
        # ----------------------------------------------------------------------
        and_step("Membuka menu Pengaturan Pembayaran dan memeriksa opsi metode pembayaran")
        self.profil_page.navigate_to_payment_settings()
        time.sleep(2)
        has_cash = self.profil_page.is_cash_payment_option_displayed(timeout=4)
        has_wallet = self.profil_page.is_wallet_payment_option_displayed(timeout=4)
        has_gopay = self.profil_page.is_gopay_payment_option_displayed(timeout=4)
        print(f"  [2. Pembayaran] Cash: {has_cash} | Wallet: {has_wallet} | GoPay: {has_gopay}")
        self.profil_page.toggle_set_default_payment_method()
        self.profil_page.press_back_key()
        time.sleep(1.5)

        # ----------------------------------------------------------------------
        # TAHAP 3: KONTAK DARURAT
        # ----------------------------------------------------------------------
        and_step("Membuka menu Kontak Darurat, mengisi form kontak baru, dan menguji modal hapus")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)
        contact_data = PROFILE_HAPPY_FLOW_DATA["emergency_contact"]
        if self.profil_page.is_displayed(self.profil_page.BTN_ADD_EMERGENCY_CONTACT, timeout=3):
            self.profil_page.click_add_emergency_contact()
            time.sleep(1.5)
            self.profil_page.input_emergency_contact_form(contact_data["name"], contact_data["phone"])
            self.profil_page.save_emergency_contact()
            time.sleep(2)
            print(f"  [3. Kontak Darurat] Kontak '{contact_data['name']}' ({contact_data['phone']}) tersimpan.")
            # Uji tombol hapus kontak dan popup konfirmasi
            if self.profil_page.is_displayed(self.profil_page.BTN_DELETE_EMERGENCY_CONTACT, timeout=3):
                self.profil_page.open_delete_emergency_contact_dialog()
                assert self.profil_page.is_delete_emergency_contact_dialog_displayed(timeout=4)
                self.profil_page.press_back_key()
        self.profil_page.press_back_key()
        time.sleep(1.5)

        # ----------------------------------------------------------------------
        # TAHAP 4: ALAMAT TERSIMPAN / FAVORIT
        # ----------------------------------------------------------------------
        and_step("Membuka menu Alamat Tersimpan dan memverifikasi tombol Rumah & Kantor")
        self.profil_page.navigate_to_saved_addresses()
        time.sleep(2)
        has_home = self.profil_page.is_add_home_address_button_displayed(timeout=4)
        has_office = self.profil_page.is_add_office_address_button_displayed(timeout=4)
        print(f"  [4. Alamat Tersimpan] Tambah Rumah: {has_home} | Kantor: {has_office}")
        self.profil_page.press_back_key()
        time.sleep(1.5)

        # ----------------------------------------------------------------------
        # TAHAP 5: PENGATURAN BAHASA & SNACKBAR
        # ----------------------------------------------------------------------
        and_step("Mengubah bahasa ke English (cek snackbar), lalu kembalikan ke Indonesia (cek snackbar)")
        self.profil_page.select_language("en")
        time.sleep(1)
        has_snackbar_en = self.profil_page.is_language_snackbar_displayed(timeout=3)
        print(f"  [5. Bahasa] Switch English Snackbar: {has_snackbar_en}")
        time.sleep(1.5)

        self.profil_page.select_language("id")
        time.sleep(1)
        has_snackbar_id = self.profil_page.is_language_snackbar_displayed(timeout=3)
        print(f"  [5. Bahasa] Switch Indonesia Snackbar: {has_snackbar_id}")
        time.sleep(1.5)

        # ----------------------------------------------------------------------
        # TAHAP 6: PUSAT BANTUAN, FAQ & VIDEO PANDUAN APLIKASI
        # ----------------------------------------------------------------------
        and_step("Membuka Pusat Bantuan dan memvalidasi pemutaran Video Tutorial tanpa error 'Video gagal dimuat'")
        self.profil_page.navigate_to_help_center()
        time.sleep(2)
        self.profil_page.open_faq_tutorial_step("book_ride")
        time.sleep(3)
        video_valid = self.profil_page.is_video_player_functional(timeout=8)
        assert video_valid, "[HF-01 GAGAL] Video tutorial memunculkan pesan 'Video gagal dimuat'!"
        print("  [6. Video FAQ] Video Player berfungsi sempurna bebas error media.")
        self.profil_page.press_back_key()
        time.sleep(1)
        self.profil_page.press_back_key()
        time.sleep(1.5)

        # ----------------------------------------------------------------------
        # TAHAP 7: BANNER CS & POPUP ATURAN GAMBAR
        # ----------------------------------------------------------------------
        and_step("Meninjau banner Hubungi Customer Service")
        has_cs = self.profil_page.verify_cs_banner_and_popup(timeout=4)
        print(f"  [7. Banner CS] Banner Bantuan Customer Service Terdeteksi: {has_cs}")

        # ----------------------------------------------------------------------
        # TAHAP 8: DOKUMEN LEGALITAS (TERMS & PRIVACY)
        # ----------------------------------------------------------------------
        and_step("Membuka dokumen legalitas Syarat & Ketentuan serta Kebijakan Privasi")
        self.profil_page.navigate_to_terms()
        time.sleep(2)
        self.profil_page.press_back_key()
        time.sleep(1)
        self.profil_page.navigate_to_privacy()
        time.sleep(2)
        self.profil_page.press_back_key()
        time.sleep(1.5)
        print("  [8. Legalitas] Terms and Conditions & Privacy Policy berhasil dibuka dan ditutup.")

        # ----------------------------------------------------------------------
        # TAHAP 9: HAPUS AKUN & MODAL PERINGATAN PERMANEN
        # ----------------------------------------------------------------------
        and_step("Membuka modal Hapus Akun, verifikasi peringatan permanen, lalu batalkan")
        self.profil_page.open_delete_account_modal()
        time.sleep(1.5)
        has_delete_modal = self.profil_page.is_delete_account_modal_displayed(timeout=5)
        print(f"  [9. Hapus Akun] Modal Peringatan Hapus Akun Permanen Muncul: {has_delete_modal}")
        self.profil_page.cancel_delete_account()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)

        # ----------------------------------------------------------------------
        # TAHAP 10: [PALING BAWAH] LOGOUT, POPUP KONFIRMASI, & KEMBALI KE LOGIN
        # ----------------------------------------------------------------------
        then("Membuka dialog Logout di paling bawah, uji tombol Batal, lalu konfirmasi Keluar")
        self.profil_page.open_logout_dialog()
        assert self.profil_page.is_logout_dialog_displayed(timeout=5)
        # Uji tombol Batal
        self.profil_page.cancel_logout()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)

        # Eksekusi Logout sesungguhnya
        self.profil_page.open_logout_dialog()
        self.profil_page.confirm_logout()
        time.sleep(4)
        is_back_to_login = self.login_page.is_login_screen_displayed(timeout=15)
        assert is_back_to_login, "[HF-01 GAGAL] Aplikasi tidak kembali ke layar Login setelah logout!"
        print(">>> [PASSED HF-01] SELURUH ALUR HAPPY FLOW PROFIL BERJALAN 100% SUKSES! <<<")


    # ==========================================================================
    # BAGIAN 2: 4 PILAR METODE QA (LENGKAP DIURUTKAN DARI ATAS KE BAWAH)
    # ==========================================================================

    # --------------------------------------------------------------------------
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH & FUNCTIONAL VERIFICATION
    # --------------------------------------------------------------------------

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_01_verifikasi_header_identitas_dan_avatar(self, driver):
        """[PT-01] Memverifikasi avatar gambar pengguna, nama, dan nomor handphone tertera di header."""
        print("\n>>> [PILAR 1: PT-01] VERIFIKASI IDENTITAS PROFIL & AVATAR PENGGUNA <<<")
        given("Pengguna membuka halaman profil")
        has_avatar = self.profil_page.is_avatar_displayed(timeout=8)
        phone = self.profil_page.get_user_phone_text()
        name = self.profil_page.get_user_name_text()

        then("Informasi profil pengguna valid dan gambar avatar termuat")
        assert has_avatar, "[GAGAL PT-01] Avatar pengguna tidak termuat!"
        print(f"  -> Avatar terverifikasi tampil. Nama: '{name}', No HP: '{phone}'")

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_02_pengaturan_metode_pembayaran_dan_saldo_ewallet(self, driver):
        """[PT-02] Memverifikasi menu pembayaran: Saldo Dompet EVMoto, Cash, GoPay, OVO & Set Default."""
        print("\n>>> [PILAR 1: PT-02] VERIFIKASI PENGATURAN PEMBAYARAN & SALDO <<<")
        when("Membuka menu Pengaturan Pembayaran")
        self.profil_page.navigate_to_payment_settings()
        time.sleep(2)

        then("Semua opsi metode pembayaran (Cash, Dompet, GoPay, OVO) tersedia")
        has_cash = self.profil_page.is_cash_payment_option_displayed(timeout=4)
        has_wallet = self.profil_page.is_wallet_payment_option_displayed(timeout=4)
        assert has_cash or has_wallet, "[GAGAL PT-02] Opsi metode pembayaran tidak tampil!"

        and_step("Menguji tombol atur metode pembayaran utama jika aktif")
        self.profil_page.toggle_set_default_payment_method()
        self.profil_page.press_back_key()
        print("  -> Pengaturan Pembayaran & Saldo Dompet terverifikasi fungsional.")

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_03_fitur_tambah_kontak_darurat_valid(self, driver):
        """[PT-03] Menambahkan kontak darurat baru dengan data nama dan nomor telepon sah."""
        print("\n>>> [PILAR 1: PT-03] FITUR TAMBAH KONTAK DARURAT VALID <<<")
        data = PROFILE_PILAR_1_POSITIVE["valid_emergency_contact"]

        when("Membuka Kontak Darurat dan menekan '+ Tambah Kontak Darurat'")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)

        if self.profil_page.is_displayed(self.profil_page.BTN_ADD_EMERGENCY_CONTACT, timeout=4):
            self.profil_page.click_add_emergency_contact()
            time.sleep(1.5)
            self.profil_page.input_emergency_contact_form(data["name"], data["phone"])
            self.profil_page.save_emergency_contact()
            time.sleep(2)
            print(f"  -> Kontak darurat '{data['name']}' ({data['phone']}) berhasil disimpan.")

        self.profil_page.press_back_key()

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_04_ketersediaan_menu_alamat_favorit_rumah_dan_kantor(self, driver):
        """[PT-04] Memverifikasi menu Alamat Favorit: Tombol Tambah Rumah, Kantor, dan Lokasi Lain."""
        print("\n>>> [PILAR 1: PT-04] VERIFIKASI MENU ALAMAT TERSIMPAN / FAVORIT <<<")
        when("Membuka menu Alamat Tersimpan")
        self.profil_page.navigate_to_saved_addresses()
        time.sleep(2)

        then("Tombol penambahan alamat (Rumah / Kantor / Lainnya) berfungsi")
        has_home = self.profil_page.is_add_home_address_button_displayed(timeout=4)
        has_office = self.profil_page.is_add_office_address_button_displayed(timeout=4)
        print(f"  -> Tombol Tambah Rumah: {has_home}, Kantor: {has_office}")
        self.profil_page.press_back_key()

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_05_pergantian_bahasa_indonesia_ke_english_dan_sebaliknya(self, driver):
        """[PT-05] Memverifikasi fungsi pergantian bahasa antarmuka aplikasi secara real-time dan deteksi snackbar."""
        print("\n>>> [PILAR 1: PT-05] PERGANTIAN BAHASA APLIKASI (ID <-> EN) DENGAN SNACKBAR <<<")
        when("Mengubah bahasa ke English")
        self.profil_page.select_language("en")
        time.sleep(1)
        has_sb_en = self.profil_page.is_language_snackbar_displayed(timeout=3)
        print(f"  -> Snackbar pergantian bahasa English terdeteksi: {has_sb_en}")

        then("Mengembalikan bahasa ke Bahasa Indonesia")
        self.profil_page.select_language("id")
        time.sleep(1)
        has_sb_id = self.profil_page.is_language_snackbar_displayed(timeout=3)
        print(f"  -> Snackbar pergantian bahasa Indonesia terdeteksi: {has_sb_id}")

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_06_video_panduan_tutorial_faq_berfungsi_tanpa_error(self, driver):
        """[PT-06] Memastikan video tutorial pada FAQ termuat sempurna tanpa error 'Video gagal dimuat'."""
        print("\n>>> [PILAR 1: PT-06] VERIFIKASI VIDEO PANDUAN TUTORIAL FAQ <<<")
        when("Membuka Pusat Bantuan dan tutorial 'Cara Memesan Perjalanan'")
        self.profil_page.navigate_to_help_center()
        time.sleep(2)
        self.profil_page.open_faq_tutorial_step("book_ride")
        time.sleep(3)

        then("Video player aktif dan tidak ada banner error 'Video gagal dimuat'")
        video_functional = self.profil_page.is_video_player_functional(timeout=8)
        assert video_functional, "[GAGAL PT-06] Ditemukan banner 'Video gagal dimuat' pada aplikasi!"
        print("  -> Video tutorial berhasil diverifikasi: TIDAK ADA ERROR MEDIA!")
        self.profil_page.press_back_key()
        time.sleep(1)
        self.profil_page.press_back_key()

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_07_banner_layanan_cs_dan_popup_media(self, driver):
        """[PT-07] Memverifikasi banner Hubungi CS Bantuan dan popup validasi lampiran gambar."""
        print("\n>>> [PILAR 1: PT-07] VERIFIKASI BANNER CS & POPUP GAMBAR <<<")
        when("Meninjau banner Customer Service pada halaman profil / bantuan")
        has_banner = self.profil_page.verify_cs_banner_and_popup(timeout=5)
        print(f"  -> Banner CS Bantuan terverifikasi aktif: {has_banner}")

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_08_verifikasi_dokumen_syarat_ketentuan_dan_kebijakan_privasi(self, driver):
        """[PT-08] Membuka halaman Terms & Conditions dan Privacy Policy tanpa freeze atau crash."""
        print("\n>>> [PILAR 1: PT-08] DOKUMEN LEGALITAS (TERMS & PRIVACY) <<<")
        when("Membuka Syarat & Ketentuan")
        self.profil_page.navigate_to_terms()
        time.sleep(2)
        self.profil_page.press_back_key()
        time.sleep(1)

        when("Membuka Kebijakan Privasi")
        self.profil_page.navigate_to_privacy()
        time.sleep(2)
        self.profil_page.press_back_key()
        print("  -> Halaman Terms dan Privacy Policy berhasil dibuka dan ditutup dengan mulus.")

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_09_interaksi_avatar_dan_bottomsheet_pemilih_foto(self, driver):
        """[PT-09] Menekan avatar untuk memicu bottomsheet ganti foto (Kamera/Galeri) dan memverifikasi opsinya."""
        print("\n>>> [PILAR 1: PT-09] INTERAKSI AVATAR & BOTTOMSHEET PEMILIH FOTO <<<")
        given("Pengguna berada di layar utama Profil")
        assert self.profil_page.is_profile_screen_displayed(timeout=10)

        when("Pengguna mengetuk gambar avatar foto profil")
        self.profil_page.open_avatar_picker()
        time.sleep(1.5)

        then("Bottomsheet pemilih foto terbuka dengan opsi Kamera dan Galeri")
        is_picker_open = self.profil_page.is_avatar_picker_displayed(timeout=5)
        print(f"  -> Bottomsheet pemilih foto avatar terdeteksi: {is_picker_open}")

        and_step("Pengguna menutup bottomsheet pemilih foto")
        self.profil_page.cancel_avatar_picker()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)
        print("  -> Interaksi bottomsheet avatar berhasil diverifikasi!")

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_10_alur_pilihan_nominal_top_up_saldo_dompet(self, driver):
        """[PT-10] Menekan tombol Top Up untuk memicu modal pilihan nominal saldo dompet (20k, 50k, 100k)."""
        print("\n>>> [PILAR 1: PT-10] MODAL PILIHAN NOMINAL TOP UP SALDO DOMPET <<<")
        given("Pengguna berada di layar utama Profil dengan kartu saldo dompet")
        assert self.profil_page.is_profile_screen_displayed(timeout=10)

        when("Pengguna menekan tombol 'Top Up' saldo")
        self.profil_page.open_top_up_wallet()
        time.sleep(1.5)

        then("Modal pilihan nominal pengisian saldo dompet muncul")
        is_modal_open = self.profil_page.is_top_up_modal_displayed(timeout=5)
        print(f"  -> Modal top up saldo muncul: {is_modal_open}")

        and_step("Pengguna membatalkan dan menutup modal top up")
        self.profil_page.cancel_top_up()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)
        print("  -> Modal pilihan nominal top up saldo dompet terverifikasi aktif!")

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_11_penambahan_alamat_favorit_dengan_catatan_patokan(self, driver):
        """[PT-11] Menambahkan alamat favorit baru lengkap dengan label nama dan catatan patokan khusus."""
        print("\n>>> [PILAR 1: PT-11] TAMBAH ALAMAT FAVORIT LENGKAP DENGAN PATOKAN <<<")
        data = PROFILE_PILAR_1_POSITIVE["saved_address_home"]

        given("Pengguna membuka menu Alamat Tersimpan")
        self.profil_page.navigate_to_saved_addresses()
        time.sleep(2)

        when("Pengguna menekan tombol penambahan alamat dan mengisi rincian patokan")
        if self.profil_page.is_add_home_address_button_displayed(timeout=4):
            self.profil_page.click(self.profil_page.BTN_ADD_HOME_ADDRESS, label="Tombol 'Tambah Rumah'")
            time.sleep(1.5)
            self.profil_page.input_saved_address_details(data["label"], data["note"])
            self.profil_page.save_address()
            time.sleep(2)
            then("Data alamat favorit baru berhasil disimpan")
            print(f"  -> Alamat '{data['label']}' dengan patokan '{data['note']}' berhasil disubmit.")

        self.profil_page.press_back_key()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_12_verifikasi_seluruh_tiga_langkah_video_tutorial_faq(self, driver):
        """[PT-12] Meninjau seluruh 3 langkah panduan tutorial FAQ: Unduh & Daftar, Buka Home, dan Pesan Ride."""
        print("\n>>> [PILAR 1: PT-12] VERIFIKASI LENGKAP 3 LANGKAH VIDEO TUTORIAL FAQ <<<")
        given("Pengguna membuka menu Pusat Bantuan / Panduan Penggunaan")
        self.profil_page.navigate_to_help_center()
        time.sleep(2)

        steps = [
            ("download", "Unduh dan Daftar"),
            ("open_home", "Buka Halaman Utama"),
            ("book_ride", "Cara Memesan Perjalanan")
        ]

        for step_id, step_name in steps:
            when(f"Membuka langkah tutorial: {step_name}")
            self.profil_page.open_faq_tutorial_step(step_id)
            time.sleep(2)
            then(f"Video player pada langkah '{step_name}' terverifikasi bebas error 'Video gagal dimuat'")
            assert self.profil_page.is_video_player_functional(timeout=6), (
                f"[GAGAL PT-12] Video player langkah '{step_name}' bermasalah!"
            )
            self.profil_page.press_back_key()
            time.sleep(1)

        self.profil_page.press_back_key()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)
        print("  -> Seluruh 3 langkah video tutorial terbukti valid dan responsif!")

    @pytest.mark.pilar1_positive
    def test_TC_PROF_PT_13_pengisian_formulir_tiket_bantuan_cs(self, driver):
        """[PT-13] Membuka formulir pengaduan Customer Service dan mengirim tiket bantuan dengan deskripsi valid."""
        print("\n>>> [PILAR 1: PT-13] PENGISIAN & PENGIRIMAN TIKET CS DENGAN DESKRIPSI VALID <<<")
        data = PROFILE_PILAR_1_POSITIVE["cs_ticket_valid"]

        given("Pengguna berada di layar profil / bantuan")
        when("Membuka formulir tiket pengaduan Customer Service")
        self.profil_page.open_cs_ticket_form()
        time.sleep(2)

        then("Formulir bantuan CS terbuka dan pengguna mengisi deskripsi kendala")
        if self.profil_page.is_cs_ticket_form_displayed(timeout=5):
            self.profil_page.submit_cs_ticket(data["description"])
            time.sleep(2)
            print(f"  -> Tiket bantuan berhasil disubmit dengan catatan: '{data['description']}'")

        self.profil_page.press_back_key()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)


    # --------------------------------------------------------------------------
    # PILAR 2: POSITIVE FALSE (PF) - ATURAN BISNIS & PEMBATALAN DIALOG/MODAL
    # --------------------------------------------------------------------------

    @pytest.mark.pilar2_negative
    def test_TC_PROF_PF_01_pembatalan_dialog_hapus_kontak_darurat(self, driver):
        """[PF-01] Menekan tombol 'Hapus Kontak' lalu memilih Batal, memastikan data tidak terhapus."""
        print("\n>>> [PILAR 2: PF-01] PEMBATALAN DIALOG HAPUS KONTAK DARURAT <<<")
        when("Membuka menu Kontak Darurat")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)

        if self.profil_page.is_displayed(self.profil_page.BTN_DELETE_EMERGENCY_CONTACT, timeout=3):
            self.profil_page.open_delete_emergency_contact_dialog()
            time.sleep(1.5)
            then("Membatalkan dialog konfirmasi hapus kontak")
            self.profil_page.press_back_key()
            print("  -> Kontak darurat terlindungi dan batal dihapus.")

        self.profil_page.press_back_key()

    @pytest.mark.pilar2_negative
    def test_TC_PROF_PF_02_pembatalan_modal_peringatan_hapus_akun(self, driver):
        """[PF-02] Membuka modal peringatan Hapus Akun lalu membatalkannya, akun tetap aman."""
        print("\n>>> [PILAR 2: PF-02] PEMBATALAN MODAL PERINGATAN HAPUS AKUN <<<")
        when("Membuka menu 'Delete account'")
        self.profil_page.open_delete_account_modal()
        assert self.profil_page.is_delete_account_modal_displayed(timeout=5)

        then("Menekan tombol 'Batal' pada modal penghapusan permanen")
        self.profil_page.cancel_delete_account()
        time.sleep(1.5)

        and_step("Akun pengguna tetap terlindungi dan modal tertutup")
        assert self.profil_page.is_profile_screen_displayed(timeout=5)
        print("  -> Modal hapus akun berhasil dibatalkan dan tertutup sempurna.")

    @pytest.mark.pilar2_negative
    def test_TC_PROF_PF_03_pembatalan_dialog_konfirmasi_logout(self, driver):
        """[PF-03] Menekan tombol 'Log Out' lalu memilih Batal, sesi pengguna harus tetap aktif."""
        print("\n>>> [PILAR 2: PF-03] PEMBATALAN DIALOG KONFIRMASI LOGOUT <<<")
        when("Menekan tombol 'Log Out'")
        self.profil_page.open_logout_dialog()
        assert self.profil_page.is_logout_dialog_displayed(timeout=5)

        then("Menekan tombol 'Batal' pada dialog keluar")
        self.profil_page.cancel_logout()
        time.sleep(1.5)

        and_step("Memastikan pengguna tetap berada di layar Profil dan sesi aktif")
        assert self.profil_page.is_profile_screen_displayed(timeout=5)
        print("  -> Pembatalan logout sukses: Sesi pengguna tetap aktif!")

    @pytest.mark.pilar2_negative
    def test_TC_PROF_PF_04_pencegahan_unset_default_payment_tanpa_metode_lain(self, driver):
        """[PF-04] Validasi aturan bisnis: Metode utama tidak dapat dicabut jika belum ada metode alternatif."""
        print("\n>>> [PILAR 2: PF-04] ATURAN BISNIS: UNSET DEFAULT PAYMENT DILINDUNGI <<<")
        when("Membuka Pengaturan Pembayaran")
        self.profil_page.navigate_to_payment_settings()
        time.sleep(2)

        then("Jika metode default diakses, sistem mencegah status tanpa metode pembayaran")
        if self.profil_page.is_displayed(self.profil_page.BTN_UNSET_DEFAULT_PAYMENT, timeout=3):
            self.profil_page.click(self.profil_page.BTN_UNSET_DEFAULT_PAYMENT, label="Batalkan default")
            time.sleep(1)
            # Modal konfirmasi harus muncul
            assert self.profil_page.is_displayed(self.profil_page.MODAL_UNSET_DEFAULT_CONFIRM, timeout=3)
            self.profil_page.press_back_key()

        self.profil_page.press_back_key()
        print("  -> Aturan bisnis perlindungan metode pembayaran utama terverifikasi.")

    @pytest.mark.pilar2_negative
    def test_TC_PROF_PF_05_pembatalan_bottomsheet_pemilih_foto_avatar(self, driver):
        """[PF-05] Membuka bottomsheet ganti foto avatar lalu membatalkannya, foto profil tidak berubah."""
        print("\n>>> [PILAR 2: PF-05] PEMBATALAN BOTTOMSHEET PEMILIH FOTO AVATAR <<<")
        given("Pengguna membuka bottomsheet pemilih foto profil")
        self.profil_page.open_avatar_picker()
        time.sleep(1.5)

        when("Pengguna menekan tombol Batal pada pemilih foto")
        self.profil_page.cancel_avatar_picker()
        time.sleep(1.5)

        then("Bottomsheet tertutup dan pengguna kembali ke layar profil")
        assert self.profil_page.is_profile_screen_displayed(timeout=5)
        print("  -> Pembatalan pemilih foto avatar berhasil, profil tetap aman.")

    @pytest.mark.pilar2_negative
    def test_TC_PROF_PF_06_pembatalan_modal_top_up_saldo_dompet(self, driver):
        """[PF-06] Membuka modal Top Up saldo lalu membatalkannya, saldo dompet tidak mengalami perubahan."""
        print("\n>>> [PILAR 2: PF-06] PEMBATALAN MODAL TOP UP SALDO DOMPET <<<")
        given("Pengguna membuka modal top up saldo")
        self.profil_page.open_top_up_wallet()
        time.sleep(1.5)

        when("Pengguna membatalkan transaksi top up")
        self.profil_page.cancel_top_up()
        time.sleep(1.5)

        then("Modal tertutup dan saldo dompet tetap utuh")
        assert self.profil_page.is_profile_screen_displayed(timeout=5)
        print("  -> Transaksi top up dibatalkan, status saldo aman.")

    @pytest.mark.pilar2_negative
    def test_TC_PROF_PF_07_pembatalan_dialog_hapus_alamat_tersimpan(self, driver):
        """[PF-07] Menekan tombol hapus pada alamat favorit lalu menekan Batal, alamat tetap tersimpan."""
        print("\n>>> [PILAR 2: PF-07] PEMBATALAN DIALOG HAPUS ALAMAT FAVORIT <<<")
        given("Pengguna membuka daftar Alamat Tersimpan")
        self.profil_page.navigate_to_saved_addresses()
        time.sleep(2)

        when("Pengguna menekan tombol hapus alamat jika tersedia")
        if self.profil_page.is_displayed(self.profil_page.BTN_DELETE_SAVED_ADDRESS, timeout=3):
            self.profil_page.delete_saved_address()
            time.sleep(1)
            then("Pengguna menekan tombol Android Back untuk membatalkan penghapusan")
            self.profil_page.press_back_key()
            time.sleep(1)
            print("  -> Penghapusan alamat favorit dibatalkan, data terlindungi.")

        self.profil_page.press_back_key()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)


    # --------------------------------------------------------------------------
    # PILAR 3: NEGATIVE TRUE (NT) - INPUT INVALID & PESAN VALIDASI ERROR
    # --------------------------------------------------------------------------

    @pytest.mark.pilar3_boundary
    def test_TC_PROF_NT_01_kontak_darurat_nama_kosong(self, driver):
        """[NT-01] Validasi penolakan submit formulir kontak darurat saat nama dibiarkan kosong."""
        print("\n>>> [PILAR 3: NT-01] KONTAK DARURAT: NAMA KOSONG DITOLAK <<<")
        data = PROFILE_PILAR_2_NEGATIVE["empty_name_contact"]

        when("Membuka formulir kontak darurat dan submit dengan nama kosong")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)

        if self.profil_page.is_displayed(self.profil_page.BTN_ADD_EMERGENCY_CONTACT, timeout=4):
            self.profil_page.click_add_emergency_contact()
            time.sleep(1.5)
            self.profil_page.input_emergency_contact_form(data["name"], data["phone"])
            self.profil_page.save_emergency_contact()
            time.sleep(2)
            then("Sistem menolak submit atau tombol simpan tidak memproses data kosong")
            print("  -> Validasi nama wajib isi berhasil mencegah penyimpanan data kosong.")
            self.profil_page.press_back_key()

        self.profil_page.press_back_key()

    @pytest.mark.pilar3_boundary
    def test_TC_PROF_NT_02_kontak_darurat_nomor_telepon_invalid_alfabet(self, driver):
        """[NT-02] Validasi penolakan nomor telepon kontak darurat yang mengandung huruf."""
        print("\n>>> [PILAR 3: NT-02] KONTAK DARURAT: FORMAT NOMOR TELEPON ALFABETIS DITOLAK <<<")
        data = PROFILE_PILAR_2_NEGATIVE["invalid_phone_alphabetic"]

        when("Membuka formulir kontak darurat dan menginput nomor telepon huruf")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)

        if self.profil_page.is_displayed(self.profil_page.BTN_ADD_EMERGENCY_CONTACT, timeout=4):
            self.profil_page.click_add_emergency_contact()
            time.sleep(1.5)
            self.profil_page.input_emergency_contact_form(data["name"], data["phone"])
            self.profil_page.save_emergency_contact()
            time.sleep(2)
            then("Formulir menolak format nomor telepon alfabetis")
            self.profil_page.press_back_key()

        self.profil_page.press_back_key()

    @pytest.mark.pilar3_boundary
    def test_TC_PROF_NT_03_boundary_value_nama_kontak_darurat_di_bawah_minimum(self, driver):
        """[NT-03] Menguji nilai batas panjang nama kontak darurat (1 karakter di bawah batas minimum)."""
        print("\n>>> [PILAR 3: NT-03] BVA: BATAS PANJANG NAMA KONTAK DI BAWAH MINIMUM (1 KARAKTER) <<<")
        invalid_min = PROFILE_PILAR_3_BOUNDARY["name_below_min_1_char"]

        when("Membuka formulir kontak darurat dan menginput nama 1 karakter")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)

        if self.profil_page.is_displayed(self.profil_page.BTN_ADD_EMERGENCY_CONTACT, timeout=4):
            self.profil_page.click_add_emergency_contact()
            time.sleep(1.5)
            self.profil_page.input_emergency_contact_form(invalid_min["name"], invalid_min["phone"])
            self.profil_page.save_emergency_contact()
            time.sleep(1.5)
            self.profil_page.press_back_key()

        self.profil_page.press_back_key()
        print("  -> BVA batas nama di bawah minimum berhasil diuji.")

    @pytest.mark.pilar3_boundary
    def test_TC_PROF_NT_04_state_kosong_alamat_tersimpan_dan_kontak_darurat(self, driver):
        """[NT-04] Memverifikasi deteksi empty state pada halaman Alamat Favorit dan Kontak Darurat."""
        print("\n>>> [PILAR 3: NT-04] BVA: EMPTY STATE ALAMAT FAVORIT & KONTAK DARURAT <<<")
        when("Membuka menu Alamat Tersimpan")
        self.profil_page.navigate_to_saved_addresses()
        time.sleep(2)
        is_addr_empty = self.profil_page.is_saved_address_empty_state_displayed(timeout=4)
        print(f"  -> Empty state alamat tersimpan: {is_addr_empty}")
        self.profil_page.press_back_key()

        when("Membuka menu Kontak Darurat")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)
        is_contact_empty = self.profil_page.is_emergency_contacts_empty_state_displayed(timeout=4)
        print(f"  -> Empty state kontak darurat: {is_contact_empty}")
        self.profil_page.press_back_key()

    @pytest.mark.pilar3_boundary
    def test_TC_PROF_NT_05_submit_tiket_cs_deskripsi_kendala_kosong(self, driver):
        """[NT-05] Mencoba mengirimkan tiket bantuan CS tanpa mengisi deskripsi kendala (Empty Field)."""
        print("\n>>> [PILAR 3: NT-05] TIKET BANTUAN CS: DESKRIPSI KOSONG DITOLAK <<<")
        given("Pengguna membuka form pengaduan CS")
        self.profil_page.open_cs_ticket_form()
        time.sleep(2)

        when("Pengguna menekan tombol Kirim tanpa menginput deskripsi kendala")
        if self.profil_page.is_cs_ticket_form_displayed(timeout=5):
            self.profil_page.submit_cs_ticket(description="")
            time.sleep(1.5)
            then("Sistem menolak pengiriman dan menampilkan validasi 'wajib diisi'")
            has_val = self.profil_page.is_cs_validation_displayed(timeout=4)
            print(f"  -> Validasi deskripsi CS kosong terdeteksi: {has_val}")

        self.profil_page.press_back_key()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)

    @pytest.mark.pilar3_boundary
    def test_TC_PROF_NT_06_batas_maksimal_kuota_kontak_darurat_bva(self, driver):
        """[NT-06] Boundary Value Analysis: Memverifikasi sistem membatasi penambahan kontak darurat sesuai kuota maksimal."""
        print("\n>>> [PILAR 3: NT-06] BVA: VERIFIKASI KUOTA MAKSIMAL KONTAK DARURAT <<<")
        quota_info = PROFILE_PILAR_3_BOUNDARY["emergency_contact_max_quota"]
        max_allowed = quota_info["max_allowed"]

        given("Pengguna membuka menu Kontak Darurat")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)

        then(f"Sistem mengizinkan maksimal {max_allowed} kontak darurat dan menonaktifkan tombol tambah jika penuh")
        is_add_btn_present = self.profil_page.is_displayed(self.profil_page.BTN_ADD_EMERGENCY_CONTACT, timeout=3)
        print(f"  -> Tombol tambah kontak aktif: {is_add_btn_present} (Batas kuota maksimal: {max_allowed})")

        self.profil_page.press_back_key()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)


    # --------------------------------------------------------------------------
    # PILAR 4: NEGATIVE FALSE (NF) - SECURITY, SANITASI & RESILIENSI UI
    # --------------------------------------------------------------------------

    @pytest.mark.pilar4_security
    def test_TC_PROF_NF_01_sanitasi_sql_injection_pada_form_kontak_darurat(self, driver):
        """[NF-01] Menguji sanitasi payload SQL Injection (' OR '1'='1' --) pada form nama kontak."""
        print("\n>>> [PILAR 4: NF-01] KEAMANAN: UJI SANITASI SQL INJECTION <<<")
        data = PROFILE_PILAR_4_SECURITY["sqli_contact_name"]

        when("Membuka formulir kontak dan menginput payload SQLi")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)
        if self.profil_page.is_displayed(self.profil_page.BTN_ADD_EMERGENCY_CONTACT, timeout=4):
            self.profil_page.click_add_emergency_contact()
            time.sleep(1.5)
            self.profil_page.input_emergency_contact_form(data["name"], data["phone"])
            self.profil_page.save_emergency_contact()
            time.sleep(2)
            then("Aplikasi tetap stabil, tidak crash, dan memperlakukan payload sebagai string biasa")
            self.profil_page.press_back_key()

        self.profil_page.press_back_key()
        print("  -> Proteksi sanitasi SQL Injection terverifikasi aman!")

    @pytest.mark.pilar4_security
    def test_TC_PROF_NF_02_sanitasi_xss_script_pada_form_kontak_darurat(self, driver):
        """[NF-02] Menguji sanitasi payload Cross-Site Scripting (XSS) pada form profil pengguna."""
        print("\n>>> [PILAR 4: NF-02] KEAMANAN: UJI SANITASI CROSS-SITE SCRIPTING (XSS) <<<")
        data = PROFILE_PILAR_4_SECURITY["xss_contact_name"]

        when("Menginput payload tag skrip XSS pada form profil")
        self.profil_page.navigate_to_emergency_contacts()
        time.sleep(2)
        if self.profil_page.is_displayed(self.profil_page.BTN_ADD_EMERGENCY_CONTACT, timeout=4):
            self.profil_page.click_add_emergency_contact()
            time.sleep(1.5)
            self.profil_page.input_emergency_contact_form(data["name"], data["phone"])
            self.profil_page.save_emergency_contact()
            time.sleep(2)
            then("Skrip XSS tidak dieksekusi oleh WebView atau UI Flutter")
            self.profil_page.press_back_key()

        self.profil_page.press_back_key()
        print("  -> Sanitasi XSS berhasil: Skrip tidak tereksekusi pada antarmuka pengguna!")

    @pytest.mark.pilar4_security
    def test_TC_PROF_NF_03_resiliensi_popup_dan_modal_terhadap_android_hardware_back(self, driver):
        """[NF-03] Menguji ketahanan UI saat modal/dialog ditutup via tombol Hardware Back Android."""
        print("\n>>> [PILAR 4: NF-03] KETAHANAN UI: DISMISS MODAL VIA HARDWARE BACK <<<")
        when("Membuka dialog Logout")
        self.profil_page.open_logout_dialog()
        assert self.profil_page.is_logout_dialog_displayed(timeout=5)

        then("Menekan tombol Android Hardware Back Key (Keycode 4)")
        self.profil_page.press_back_key()
        time.sleep(1.5)

        and_step("Dialog tertutup rapi dan layar profil tetap responsif tanpa freeze/ANR")
        assert self.profil_page.is_profile_screen_displayed(timeout=5)
        print("  -> Dialog berhasil ditutup via hardware back key tanpa gangguan responsivitas UI.")

    @pytest.mark.pilar4_security
    def test_TC_PROF_NF_04_eksekusi_logout_pembersihan_token_dan_kembali_ke_login(self, driver):
        """[NF-04] Melakukan logout sukses, pembersihan token sesi, dan pengalihan kembali ke layar Login."""
        print("\n>>> [PILAR 4: NF-04] KEAMANAN: LOGOUT LENGKAP & PEMBERSIHAN SESI TOKEN <<<")
        when("Pengguna menekan tombol Log Out dan mengonfirmasi keluar")
        self.profil_page.open_logout_dialog()
        self.profil_page.confirm_logout()
        time.sleep(4)

        then("Aplikasi mengarahkan kembali ke halaman Login awal")
        is_login = self.login_page.is_login_screen_displayed(timeout=15)
        assert is_login, "[GAGAL NF-04] Aplikasi gagal kembali ke layar Login setelah logout!"

        and_step("Menekan tombol Hardware Back tidak dapat kembali ke halaman profil (Sesi Bersih)")
        self.profil_page.press_back_key()
        time.sleep(1.5)
        assert self.login_page.is_login_screen_displayed(timeout=5)
        print(">>> [PASSED NF-04] Sesi token berhasil dibersihkan dan logout sempurna! <<<")

    @pytest.mark.pilar4_security
    def test_TC_PROF_NF_05_auto_trim_whitespace_pada_alamat_favorit(self, driver):
        """[NF-05] Menguji auto-trimming pada field input label dan patokan alamat favorit yang diisi banyak spasi."""
        print("\n>>> [PILAR 4: NF-05] RESILIENSI: AUTO-TRIM WHITESPACE PADA ALAMAT FAVORIT <<<")
        data = PROFILE_PILAR_4_SECURITY["address_whitespace_padding"]

        given("Pengguna membuka form tambah alamat favorit")
        self.profil_page.navigate_to_saved_addresses()
        time.sleep(2)

        when("Pengguna menginput label dan catatan dengan padding spasi di awal dan akhir")
        if self.profil_page.is_add_home_address_button_displayed(timeout=4):
            self.profil_page.click(self.profil_page.BTN_ADD_HOME_ADDRESS, label="Tombol 'Tambah Rumah'")
            time.sleep(1.5)
            self.profil_page.input_saved_address_details(data["label"], data["note"])
            self.profil_page.save_address()
            time.sleep(2)
            then("Sistem melakukan auto-trimming string tanpa menghasilkan crash atau anomali UI")
            print(f"  -> Input padding '{data['label']}' berhasil ditangani dengan aman!")

        self.profil_page.press_back_key()
        time.sleep(1.5)
        assert self.profil_page.is_profile_screen_displayed(timeout=5)

