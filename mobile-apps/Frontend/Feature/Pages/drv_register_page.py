"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - REGISTRATION PAGE OBJECT (POM)
================================================================================
Aplikasi: EvMoto Driver Dev (com.evmoto.driver.app)
Target  : Layar Registrasi Mitra Driver Baru, Formulir 3 Tahap (Data Personal,
          Kendaraan ECGO/Non-ECGO, Plat Nomor, Upload Dokumen SIM/STNK/SKCK/KTP,
          dan Kode Referral).
Wording : Bersumber 100% dari strings resmi APK driver_lang_id.json
================================================================================
"""
import random
import time

from appium.webdriver.common.appiumby import AppiumBy
from config.config import Config
from core.base_page import BasePage
from Helper.foto_uji import siapkan_foto_uji
from utils.logger import get_logger

logger = get_logger("DrvRegisterPage")


class DrvRegisterPage(BasePage):
    """Page Object untuk Pendaftaran Mitra Pengemudi Baru EvMoto Driver."""

    # ==========================================================================
    # 1. TOMBOL AWAL & HEADER REGISTRASI
    # ==========================================================================
    CTA_REGISTER_NEW_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Daftar sebagai Driver baru') or contains(@text, 'Daftar sebagai Driver baru') or "
        "contains(@content-desc, 'Daftar') or contains(@text, 'Daftar')]"
    )
    # Alur pendaftaran (peta layar CI 18-19 Nov 2026, APK UAT): 'Nomor Handphone' -> 'Verifikasi Kode' (OTP) -> satu formulir yang digulir
    # ('Data Informasi Personal': data pribadi, foto KTP/SIM/STNK, nomor plat, layanan, lokasi, ECGO Ya/Tidak, SKCK, selfie, avatar) -> 'Lanjutkan'.
    TEXT_REGISTER_TITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Registrasi Driver Baru') or contains(@text, 'Registrasi Driver Baru') or "
        "contains(@content-desc, 'Data Informasi Personal') or contains(@text, 'Data Informasi Personal')]"
    )
    TEXT_STEP_PHONE = (
        AppiumBy.XPATH,
        "//*[@content-desc='Registrasi Driver Baru' or @text='Registrasi Driver Baru']"
    )
    # Penanda formulir data (bukan langkah nomor handphone): salah satu judul kolom formulir atau pesan 'Wajib Diisi' tampil
    PENANDA_FORMULIR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Data Informasi Personal') or contains(@content-desc, 'Nama Lengkap') or "
        "contains(@content-desc, 'Jenis Kelamin') or contains(@content-desc, 'Tempat Tinggal') or contains(@content-desc, 'No. KTP') or "
        "contains(@content-desc, 'Pengalaman Berkendara') or contains(@content-desc, 'Foto ') or contains(@content-desc, 'Nomor Plat') or "
        "contains(@content-desc, 'Layanan') or contains(@content-desc, 'ECGO Driver') or contains(@content-desc, 'Selfie') or "
        "contains(@content-desc, 'Wajib Diisi')]"
    )
    FIELD_PHONE = (AppiumBy.XPATH, "//android.widget.EditText")
    BTN_LANJUTKAN = (AppiumBy.XPATH, "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']")
    TEXT_OTP_STEP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Verifikasi Kode') or contains(@text, 'Verifikasi Kode')]"
    )
    FIELD_FULL_NAME = (AppiumBy.XPATH, "//android.widget.EditText[contains(@hint, 'nama lengkap') or contains(@text, 'nama lengkap')]")
    FIELD_KTP_NUMBER = (AppiumBy.XPATH, "//android.widget.EditText[contains(@hint, '102303040303') or contains(@text, '102303040303')]")
    FIELD_EXPERIENCE_DATE = (AppiumBy.XPATH, "//*[contains(@hint, 'Misalnya 20')]")
    DROPDOWN_PILIH = (
        AppiumBy.XPATH,
        "//android.widget.Button[starts-with(@content-desc, 'Pilih ') or starts-with(@text, 'Pilih ')]"
    )
    DATE_DAY_FIRST = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, '1, ') and contains(@content-desc, '20')]"
    )
    BTN_DATE_OK = (AppiumBy.XPATH, "//android.widget.Button[@content-desc='OKE' or @text='OKE' or @content-desc='OK' or @text='OK']")
    GALERI_OPTION = (AppiumBy.XPATH, "//*[@content-desc='Galeri' or @text='Galeri']")
    GALERI_FIRST_PHOTO = (AppiumBy.XPATH, "//*[starts-with(@content-desc, 'Foto diambil pada')]")
    TEXT_REGISTER_SUBTITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lengkapi data Anda untuk melanjutkan') or contains(@text, 'Lengkapi data Anda')]"
    )

    # ==========================================================================
    # 2. PERTANYAAN DRIVER ECGO & PLAT KENDARAAN
    # ==========================================================================
    TEXT_ECGO_DRIVER_QUESTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Apakah Anda ECGO Driver?') or contains(@text, 'Apakah Anda ECGO Driver?')]"
    )
    RADIO_ECGO_YES = (
        AppiumBy.XPATH,
        "//android.widget.RadioButton[@content-desc='Ya' or @text='Ya']"
    )
    RADIO_ECGO_NO = (
        AppiumBy.XPATH,
        "//android.widget.RadioButton[@content-desc='Tidak' or @text='Tidak']"
    )
    FIELD_PLATE_NUMBER = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'B1234ABC') or contains(@content-desc, 'Plat') or "
        "contains(@hint, 'Nomor Plat') or contains(@content-desc, 'B1234')]"
    )
    FIELD_REFERRAL_CODE = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'referral') or contains(@content-desc, 'referral') or "
        "contains(@hint, 'kode referral')]"
    )

    # ==========================================================================
    # 3. UPLOAD DOKUMEN & FOTO PERSYARATAN
    # ==========================================================================
    BTN_UPLOAD_SELFIE_KTP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Driver Selfie dengan KTP') or contains(@text, 'Driver Selfie dengan KTP') or "
        "contains(@content-desc, 'Selfie dengan KTP')]"
    )
    BTN_UPLOAD_STNK_FRONT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Foto STNK Depan') or contains(@text, 'Foto STNK Depan') or "
        "contains(@content-desc, 'STNK Depan')]"
    )
    BTN_UPLOAD_STNK_BACK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Foto STNK Belakang') or contains(@text, 'Foto STNK Belakang') or "
        "contains(@content-desc, 'STNK Belakang')]"
    )
    BTN_UPLOAD_SKCK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Foto SKCK') or contains(@text, 'Foto SKCK') or "
        "contains(@content-desc, 'SKCK')]"
    )

    # ==========================================================================
    # 4. ACTION BUTTONS & VALIDASI POPUP
    # ==========================================================================
    BTN_SUBMIT_REGISTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim') or contains(@text, 'Kirim') or "
        "contains(@content-desc, 'Lanjut') or contains(@text, 'Lanjut') or "
        "contains(@content-desc, 'Daftar') or contains(@text, 'Daftar')]"
    )
    BTN_BACK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kembali') or contains(@text, 'Kembali') or contains(@class, 'ImageView')][1]"
    )
    POPUP_SUCCESS_COMPLETE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'DATA  YANG DIKIRIM BERHASIL') or contains(@text, 'DATA  YANG DIKIRIM BERHASIL') or "
        "contains(@content-desc, 'Informasi Sudah Dilengkapi') or contains(@text, 'Informasi Sudah Dilengkapi')]"
    )
    TEXT_SUCCESS_NOTICE_2HOURS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '2 jam') or contains(@text, '2 jam') or "
        "contains(@content-desc, 'Tim kami akan menghubungi Anda')]"
    )
    WARNING_VALIDATION_MANDATORY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Wajib Diisi') or contains(@text, 'Wajib Diisi') or contains(@content-desc, 'wajib') or "
        "contains(@text, 'wajib') or contains(@content-desc, 'Harap isi') or contains(@text, 'tidak boleh kosong')]"
    )

    # ==========================================================================
    # METHODS / USER ACTIONS
    # ==========================================================================
    # --- Langkah 1 dan 2: nomor handphone dan OTP -----------------------------------------------------------------------------------------
    def click_daftar_driver_baru(self):
        """Membuka langkah 'Nomor Handphone' pendaftaran dari layar login (belum memasukkan nomor)."""
        self.click(self.CTA_REGISTER_NEW_DRIVER, label="CTA Daftar sebagai Driver Baru")

    def is_phone_step_displayed(self) -> bool:
        """Memeriksa apakah langkah 'Registrasi Driver Baru' (kolom Nomor Handphone) tampil."""
        return self.is_displayed(self.TEXT_STEP_PHONE, timeout=5)

    def lewati_verifikasi_nomor(self, nomor: str = None):
        """Dari langkah Nomor Handphone: isi nomor acak (awalan 899, tidak terhubung ke orang), Lanjutkan, OTP kode bypass dev, Lanjutkan.

        Berakhir di formulir 'Data Informasi Personal'. AssertionError bila langkah OTP atau formulir tidak tampil.
        """
        nomor = nomor or ("899" + "".join(str(random.randint(0, 9)) for _ in range(8)))
        kolom = self.find(self.FIELD_PHONE, timeout=10)
        kolom.click()
        time.sleep(0.5)
        kolom.send_keys(nomor)
        time.sleep(1)
        self._sembunyikan_keyboard()
        self._klik_langsung(self.BTN_LANJUTKAN, "Lanjutkan (nomor handphone)")
        assert self.is_displayed(self.TEXT_OTP_STEP, timeout=15), "Langkah 'Verifikasi Kode' (OTP) tidak tampil setelah nomor dikirim"
        otp = self.find(self.FIELD_PHONE, timeout=10)
        otp.click()
        time.sleep(0.5)
        for digit in str(Config.DRIVER_ACTIVE_PIN):
            self.driver.press_keycode(7 + int(digit))
            time.sleep(0.2)
        time.sleep(1)
        self._klik_langsung(self.BTN_LANJUTKAN, "Lanjutkan (OTP)")
        assert self.is_displayed(self.PENANDA_FORMULIR, timeout=20), "Formulir 'Data Informasi Personal' tidak tampil setelah OTP"

    def buka_formulir_pendaftaran(self):
        """Dari layar login sampai formulir data: tautan Daftar, nomor handphone, OTP."""
        self.click_daftar_driver_baru()
        assert self.is_phone_step_displayed(), "Langkah Nomor Handphone pendaftaran harus terbuka"
        self.lewati_verifikasi_nomor()

    def is_register_screen_displayed(self) -> bool:
        """Memeriksa apakah FORMULIR pendaftaran (bukan langkah nomor handphone) tampil: judul/kolom formulir atau pesan 'Wajib Diisi'."""
        return self.is_displayed(self.PENANDA_FORMULIR, timeout=5)

    # --- Pembantu gulir dan keyboard ------------------------------------------------------------------------------------------------------
    def _sembunyikan_keyboard(self):
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:  # noqa: BLE001 - keyboard bisa sudah tertutup
            pass

    def _gulir_formulir(self, konten_naik: bool):
        ukuran = self.driver.get_window_size()
        x = ukuran["width"] // 2
        if konten_naik:
            self.swipe(x, int(ukuran["height"] * 0.70), x, int(ukuran["height"] * 0.30), 500)
        else:
            self.swipe(x, int(ukuran["height"] * 0.30), x, int(ukuran["height"] * 0.70), 500)
        time.sleep(0.6)

    def _tampilkan(self, locator, konten_naik_dulu: bool = True, max_swipes: int = 12) -> bool:
        """Gulir formulir (satu halaman panjang) sampai elemen tampil; coba satu arah dulu, lalu arah sebaliknya."""
        if self.is_displayed(locator, timeout=2):
            return True
        for arah in (konten_naik_dulu, not konten_naik_dulu):
            for _ in range(max_swipes):
                self._gulir_formulir(konten_naik=arah)
                if self.is_displayed(locator, timeout=1):
                    return True
        return False

    def _ketik(self, locator, teks: str, label: str):
        """Ketuk kolom (agar fokus) lalu kirim teks; send_keys tanpa ketukan tidak mengisi kolom Flutter."""
        kolom = self.find(locator)
        kolom.click()
        time.sleep(0.4)
        kolom.send_keys(teks)
        logger.info(f"Input '{teks}' ke: {label}")
        time.sleep(0.4)

    def _klik_langsung(self, locator, label: str):
        """Tunggu tombol ada lalu ketuk langsung (tanpa jeda manusiawi); dipakai untuk 'Lanjutkan' di bawah keyboard."""
        tombol = self.find(locator, timeout=10)
        logger.info(f"Klik: {label}")
        tombol.click()

    @staticmethod
    def _kolom_setelah_label(label: str):
        """Kolom isian pertama setelah judul kolom (judul dan kolom berurutan di pohon layar Flutter)."""
        return (AppiumBy.XPATH, f"(//*[starts-with(@content-desc, '{label}')]/following::android.widget.EditText)[1]")

    # --- Pengisian formulir ----------------------------------------------------------------------------------------------------------------
    def select_ecgo_driver(self, is_ecgo: bool = True):
        """Memilih apakah driver menggunakan armada ECGO atau Non-ECGO (RadioButton Ya / Tidak)."""
        locator = self.RADIO_ECGO_YES if is_ecgo else self.RADIO_ECGO_NO
        assert self._tampilkan(locator), "Pilihan 'Apakah Anda ECGO Driver?' tidak ditemukan di formulir"
        self.click(locator, label="Opsi ECGO Driver: " + ("Ya" if is_ecgo else "Tidak"))

    def enter_plate_number(self, plate: str):
        """Memasukkan nomor plat kendaraan driver (nilai kosong = kolom dibiarkan kosong)."""
        locator = self._kolom_setelah_label("Nomor Plat Kendaraan")
        assert self._tampilkan(locator), "Kolom 'Nomor Plat Kendaraan' tidak ditemukan di formulir"
        if plate != "":
            self._ketik(locator, plate, "Field Plat Nomor Kendaraan")
        self._sembunyikan_keyboard()

    def enter_full_name(self, nama: str):
        locator = self._kolom_setelah_label("Nama Lengkap")
        assert self._tampilkan(locator, konten_naik_dulu=False), "Kolom 'Nama Lengkap' tidak ditemukan di formulir"
        self._ketik(locator, nama, "Field Nama Lengkap")
        self._sembunyikan_keyboard()

    def enter_ktp_number(self, nomor: str):
        locator = self._kolom_setelah_label("No. KTP")
        assert self._tampilkan(locator), "Kolom 'No. KTP' tidak ditemukan di formulir"
        self._ketik(locator, nomor, "Field No. KTP")
        self._sembunyikan_keyboard()

    def pilih_semua_dropdown(self, maks: int = 6):
        """Buka tiap dropdown 'Pilih ...' yang masih kosong (jenis kelamin, provinsi, kota, lokasi layanan) dan pilih opsi pertama."""
        for _ in range(maks):
            tombol = self.driver.find_elements(*self.DROPDOWN_PILIH)
            if not tombol:
                break
            tombol[0].click()
            time.sleep(2)
            opsi = [e for e in self.driver.find_elements("xpath", "//*[@clickable='true']")
                    if (e.get_attribute("content-desc") or "").strip()
                    and not (e.get_attribute("content-desc") or "").startswith(("Kembali", "Ping", "Pilih", "Lanjutkan", "Tutup"))]
            assert opsi, "Daftar opsi dropdown kosong"
            opsi[0].click()
            time.sleep(1.5)

    def pilih_tanggal_pengalaman(self):
        """Kolom 'Pengalaman Berkendara Sejak' adalah pemilih tanggal: pilih tanggal 1 bulan berjalan lalu OKE."""
        assert self._tampilkan(self.FIELD_EXPERIENCE_DATE), "Kolom 'Pengalaman Berkendara Sejak' tidak ditemukan di formulir"
        self.driver.find_elements(*self.FIELD_EXPERIENCE_DATE)[0].click()
        time.sleep(2)
        self.click(self.DATE_DAY_FIRST, label="Pilih tanggal 1", use_human_pacing=False)
        self.click(self.BTN_DATE_OK, label="OKE (pemilih tanggal)", use_human_pacing=False)
        time.sleep(1)

    def unggah_foto(self, label: str) -> bool:
        """Unggah foto uji lewat Galeri untuk kotak foto di bawah judul `label`. True bila aplikasi Driver kembali di depan."""
        siapkan_foto_uji()
        judul = (AppiumBy.XPATH, f"//*[starts-with(@content-desc, '{label}') or starts-with(@text, '{label}')]")
        assert self._tampilkan(judul), f"Judul '{label}' tidak ditemukan di formulir"
        rect = self.driver.find_elements(*judul)[0].rect
        ukuran = self.driver.get_window_size()
        if rect["y"] + rect["height"] + 80 > ukuran["height"] - 80:  # kotak foto di bawah judul harus terlihat sebelum Lanjutkan
            self._gulir_formulir(konten_naik=True)
            rect = self.driver.find_elements(*judul)[0].rect
        # Kotak foto tidak punya label; ketuk 35 px di bawah judul (kotak selfie lebih pendek dari kotak lain)
        self.driver.tap([(ukuran["width"] // 2, int(rect["y"] + rect["height"] + 35))], 150)
        time.sleep(2.5)
        self.click(self.GALERI_OPTION, label=f"Galeri ({label})", use_human_pacing=False)
        assert self.is_displayed(self.GALERI_FIRST_PHOTO, timeout=15), "Pemilih foto Android tidak menampilkan foto uji"
        self.click(self.GALERI_FIRST_PHOTO, label="Foto pertama di galeri", use_human_pacing=False)
        time.sleep(3)
        return self.driver.current_package == "com.evmoto.driver.app"

    def unggah_semua_dokumen(self):
        """Unggah foto uji untuk seluruh kotak berkas wajib."""
        for label in ("Foto ID KTP", "Foto SIM", "Foto STNK Depan", "Foto STNK Belakang", "Foto SKCK", "Driver Selfie dengan KTP", "Foto Avatar"):
            self.unggah_foto(label)

    def pilih_layanan(self, nama: str = "Motorcycle"):
        """Centang jenis layanan (kotak 'Layanan' berisi Motorcycle); wajib diisi."""
        locator = (AppiumBy.XPATH, f"//*[contains(@content-desc, '{nama}') or contains(@text, '{nama}')]")
        assert self._tampilkan(locator), f"Pilihan layanan '{nama}' tidak ditemukan di formulir"
        self.click(locator, label=f"Layanan {nama}", use_human_pacing=False)

    def has_referral_field(self) -> bool:
        """True bila formulir memiliki kolom kode referral (tidak ada pada formulir APK UAT hasil peta 19 Nov 2026)."""
        return self._tampilkan(self.FIELD_REFERRAL_CODE, max_swipes=6)

    def lengkapi_formulir(self, plate: str, is_ecgo: bool = False):
        """Isi SELURUH kolom wajib dengan data uji yang valid (kecuali plat dan pilihan ECGO dari pemanggil), tanpa menekan Lanjutkan."""
        self.enter_full_name("Uji Otomasi Mitra")
        self.pilih_semua_dropdown()
        self.enter_ktp_number("3171012345670001")
        self.pilih_tanggal_pengalaman()
        self.unggah_semua_dokumen()
        self.enter_plate_number(plate)
        self.pilih_layanan("Motorcycle")
        self.pilih_semua_dropdown()
        self.select_ecgo_driver(is_ecgo=is_ecgo)

    def enter_referral_code(self, code: str):
        """Memasukkan kode referral (kolom ini tidak ada di formulir APK UAT; AssertionError bila tidak ditemukan)."""
        assert self._tampilkan(self.FIELD_REFERRAL_CODE), "Kolom kode referral tidak ada di formulir pendaftaran APK ini"
        self._ketik(self.FIELD_REFERRAL_CODE, code, "Field Kode Referral")

    def click_upload_selfie_ktp(self):
        """Unggah foto selfie dengan KTP."""
        self.unggah_foto("Driver Selfie dengan KTP")

    def click_upload_stnk_front(self):
        """Unggah foto STNK depan."""
        self.unggah_foto("Foto STNK Depan")

    def click_upload_stnk_back(self):
        """Unggah foto STNK belakang."""
        self.unggah_foto("Foto STNK Belakang")

    def click_upload_skck(self):
        """Unggah foto SKCK."""
        self.unggah_foto("Foto SKCK")

    def is_photo_uploaded(self) -> bool:
        """Foto terunggah bila tombol 'Update Foto' tampil di layar saat ini."""
        return self.is_displayed((AppiumBy.XPATH, "//*[@content-desc='Update Foto' or @text='Update Foto']"), timeout=3)

    def submit_registration_form(self):
        """Menekan tombol 'Lanjutkan' di dasar formulir."""
        self._sembunyikan_keyboard()
        self._klik_langsung(self.BTN_LANJUTKAN, "Tombol Lanjutkan (kirim formulir)")
        time.sleep(3)

    def is_registration_success_displayed(self) -> bool:
        """Memeriksa apakah pop-up sukses 'DATA YANG DIKIRIM BERHASIL' tampil."""
        return self.is_displayed(self.POPUP_SUCCESS_COMPLETE, timeout=8)

    def is_mandatory_warning_displayed(self) -> bool:
        """Memeriksa apakah pesan 'Wajib Diisi' tampil pada kolom yang belum lengkap."""
        return self.is_displayed(self.WARNING_VALIDATION_MANDATORY, timeout=4)

    def click_back(self):
        """Mengetuk tombol kembali."""
        self.click(self.BTN_BACK, label="Tombol Kembali")
