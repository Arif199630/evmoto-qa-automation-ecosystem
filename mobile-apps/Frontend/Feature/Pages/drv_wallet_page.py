"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - EWALLET & TARIK DANA PAGE OBJECT (POM)
================================================================================
Aplikasi: EvMoto Driver Dev (com.evmoto.driver.app)
Target  : Modul Keuangan Mitra Driver, Hubungkan eWallet ECGO, Auto Connect,
          Kirim Saldo, Bayar Tagihan, Tarik Dana, Rekening Bank Tersimpan,
          dan Riwayat Finansial.
Wording : Bersumber 100% dari strings resmi APK driver_lang_id.json
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("DrvWalletPage")


class DrvWalletPage(BasePage):
    """Page Object untuk Modul Finansial eWallet & Penarikan Dana Driver."""

    # ==========================================================================
    # 1. HEADER & KARTU UTAMA EWALLET
    # ==========================================================================
    HEADER_EWALLET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'eWallet') or contains(@text, 'eWallet')]"
    )
    CARD_SALDO_EVMOTO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo EVMoto') or contains(@text, 'Saldo EVMoto')]"
    )
    CARD_SALDO_ECGO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo ECGO') or contains(@text, 'Saldo ECGO')]"
    )
    TEXT_STATUS_TERHUBUNG = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Terhubung dengan ECGO') or contains(@text, 'Terhubung dengan ECGO') or "
        "contains(@content-desc, 'Terhubung') or contains(@text, 'Terhubung')]"
    )
    TEXT_STATUS_BELUM_TERHUBUNG = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tidak Terhubung dengan ECGO') or contains(@text, 'Tidak Terhubung dengan ECGO') or "
        "contains(@content-desc, 'Belum Terhubung') or contains(@text, 'Belum Terhubung')]"
    )

    # ==========================================================================
    # 2. HUBUNGKAN & PUTUSKAN EWALLET ECGO
    # ==========================================================================
    BTN_HUBUNGKAN_EWALLET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hubungkan') or contains(@text, 'Hubungkan')]"
    )
    TITLE_LINK_ECGO_MODAL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hubungkan EVMoto dengan ECGO') or contains(@text, 'Hubungkan EVMoto dengan ECGO')]"
    )
    CHECKLIST_INFO_INTRO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Yang harus Anda ketahui') or contains(@text, 'Yang harus Anda ketahui')]"
    )
    POPUP_LINK_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil Di Hubungkan') or contains(@text, 'Berhasil Di Hubungkan') or "
        "contains(@content-desc, 'Berhasil menghubungkan') or contains(@text, 'Berhasil menghubungkan')]"
    )
    BTN_PUTUSKAN_EWALLET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Putuskan eWallet') or contains(@text, 'Putuskan eWallet')]"
    )
    DIALOG_PUTUSKAN_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Jika diputuskan') or contains(@text, 'Jika diputuskan') or "
        "contains(@content-desc, 'Ya, Putuskan') or contains(@text, 'Ya, Putuskan')]"
    )
    BTN_CONFIRM_PUTUSKAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ya, Putuskan') or contains(@text, 'Ya, Putuskan')]"
    )

    # ==========================================================================
    # 3. PENGATURAN OTOMATIS (AUTO CONNECT / AUTO MOVE BALANCE)
    # ==========================================================================
    MENU_PENGATURAN_OTOMATIS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pengaturan Otomatis') or contains(@text, 'Pengaturan Otomatis') or "
        "contains(@content-desc, 'Atur Pembayaran Secara Otomatis') or contains(@text, 'Atur Pembayaran Secara Otomatis')]"
    )
    SWITCH_HUBUNGKAN_OTOMATIS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hubungkan Secara Otomatis') or contains(@text, 'Hubungkan Secara Otomatis') or "
        "contains(@class, 'Switch')]"
    )
    TRIGGER_JATUH_TEMPO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saat Tagihan Jatuh Tempo') or contains(@text, 'Saat Tagihan Jatuh Tempo')]"
    )
    TRIGGER_GI_CAIR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saat Guarantee Income Cair') or contains(@text, 'Saat Guarantee Income Cair')]"
    )
    TRIGGER_ORDER_SELESAI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Setiap Orderan Selesai') or contains(@text, 'Setiap Orderan Selesai')]"
    )
    SNACKBAR_AUTO_SAVE_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pengaturan otomatis berhasil disimpan') or contains(@text, 'Pengaturan otomatis berhasil disimpan')]"
    )

    # ==========================================================================
    # 4. KIRIM SALDO & BAYAR TAGIHAN (TRANSFER & BILLS)
    # ==========================================================================
    MENU_KIRIM_SALDO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirimkan Saldo') or contains(@text, 'Kirimkan Saldo') or "
        "contains(@content-desc, 'Kirimkan ke Saldo ECGO') or contains(@text, 'Kirimkan ke Saldo ECGO')]"
    )
    FIELD_NOMINAL_KIRIM = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Nominal') or contains(@content-desc, 'Nominal') or @class='android.widget.EditText']"
    )
    BTN_SUBMIT_KIRIM_SALDO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim') or contains(@text, 'Kirim')]"
    )
    MODAL_SUKSES_KIRIM_SALDO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pengiriman Saldo Berhasil') or contains(@text, 'Pengiriman Saldo Berhasil')]"
    )
    MENU_BAYAR_TAGIHAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bayar Tagihan') or contains(@text, 'Bayar Tagihan')]"
    )
    CHECKBOX_PILIH_SEMUA_TAGIHAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih Semua Tagihan') or contains(@text, 'Pilih Semua Tagihan') or contains(@class, 'CheckBox')]"
    )
    CARD_TOTAL_TUNGGAKAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Total Tunggakan') or contains(@text, 'Total Tunggakan') or "
        "contains(@content-desc, 'Tagihan Hari Ini') or contains(@text, 'Tagihan Hari Ini')]"
    )

    # ==========================================================================
    # 5. TARIK DANA (WITHDRAWAL ENGINE)
    # ==========================================================================
    MENU_TARIK_DANA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tarik Dana') or contains(@text, 'Tarik Dana')]"
    )
    CARD_SALDO_AKTIF_SAYA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo Aktif Saya') or contains(@text, 'Saldo Aktif Saya')]"
    )
    FIELD_NOMINAL_TARIK_DANA = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'nominal') or contains(@hint, 'Nominal') or @class='android.widget.EditText']"
    )
    TEXT_MINIMAL_PENARIKAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Minimal penarikan') or contains(@text, 'Minimal penarikan')]"
    )
    TEXT_BIAYA_ADMIN_BANK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Biaya admin') or contains(@text, 'Biaya admin')]"
    )
    BTN_KONFIRMASI_PENARIKAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Konfirmasi Penarikan Dana') or contains(@text, 'Konfirmasi Penarikan Dana') or "
        "contains(@content-desc, 'Tarik Dana') or contains(@text, 'Tarik Dana')]"
    )
    SNACKBAR_SUCCESS_WITHDRAW = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil pengajuan penarikan dana') or contains(@text, 'Berhasil pengajuan penarikan dana') or "
        "contains(@content-desc, 'Penarikan Dana berhasil') or contains(@text, 'Penarikan Dana berhasil')]"
    )
    SNACKBAR_EMPTY_AMOUNT_ERROR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Harap mengisi nominal penarikan dana') or contains(@text, 'Harap mengisi nominal penarikan dana')]"
    )
    SNACKBAR_MIN_AMOUNT_ERROR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Minimum penarikan dana') or contains(@text, 'Minimum penarikan dana')]"
    )

    # ==========================================================================
    # 6. NOMOR REKENING TERSIMPAN (CRUD BANK ACCOUNT)
    # ==========================================================================
    MENU_REKENING_TERSIMPAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Nomor Rekening Tersimpan') or contains(@text, 'Nomor Rekening Tersimpan')]"
    )
    EMPTY_STATE_REKENING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Ada Nomor Rekening') or contains(@text, 'Belum Ada Nomor Rekening')]"
    )
    BTN_TAMBAH_REKENING_BARU = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tambahhkan Nomor Rekening Baru') or contains(@text, 'Tambahhkan Nomor Rekening Baru') or "
        "contains(@content-desc, 'Tambah Rekening') or contains(@text, 'Tambah Rekening')]"
    )
    FIELD_SELECT_BANK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih Bank') or contains(@text, 'Pilih Bank') or "
        "contains(@content-desc, 'Pilih nama bank') or contains(@text, 'Pilih nama bank')]"
    )
    FIELD_INPUT_REKENING = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'nomor rekening') or contains(@hint, 'Nomor Rekening')]"
    )
    FIELD_INPUT_PEMILIK = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'nama pemilik') or contains(@hint, 'Nama Pemilik')]"
    )
    BTN_SIMPAN_REKENING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Simpan') or contains(@text, 'Simpan') or "
        "contains(@content-desc, 'Tambah') or contains(@text, 'Tambah')]"
    )
    SNACKBAR_TAMBAH_REKENING_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil menambah rekening penarikan') or contains(@text, 'Berhasil menambah rekening penarikan')]"
    )
    BTN_EDIT_REKENING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Edit') or contains(@text, 'Edit')]"
    )
    SNACKBAR_EDIT_REKENING_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil mengubah rekening penarikan') or contains(@text, 'Berhasil mengubah rekening penarikan')]"
    )
    BTN_HAPUS_REKENING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hapus') or contains(@text, 'Hapus')]"
    )
    DIALOG_CONFIRM_HAPUS_REKENING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Apakah Anda yakin ingin menghapus nomor rekening?') or "
        "contains(@text, 'Apakah Anda yakin ingin menghapus nomor rekening?')]"
    )
    BTN_CONFIRM_DELETE_REKENING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hapus') or contains(@text, 'Hapus')][last()]"
    )
    BTN_CANCEL_DELETE_REKENING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@text, 'Batal')]"
    )
    SNACKBAR_DELETE_REKENING_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil menghapus nomor rekening') or contains(@text, 'Berhasil menghapus nomor rekening')]"
    )

    # ==========================================================================
    # 7. RIWAYAT TRANSAKSI FINANSIAL
    # ==========================================================================
    BTN_RIWAYAT_TARIK_DANA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Riwayat Tarik Dana') or contains(@text, 'Riwayat Tarik Dana')]"
    )
    TAB_SELURUH_RIWAYAT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Seluruh Riwayat') or contains(@text, 'Seluruh Riwayat')]"
    )

    # ==========================================================================
    # USER ACTIONS / METHODS
    # ==========================================================================
    def is_wallet_screen_displayed(self) -> bool:
        """Memeriksa apakah layar modul eWallet aktif."""
        return self.is_displayed(self.HEADER_EWALLET, timeout=5) or self.is_displayed(self.CARD_SALDO_EVMOTO, timeout=3)

    def is_ecgo_connected(self) -> bool:
        """Memeriksa apakah eWallet terhubung dengan armada ECGO."""
        return self.is_displayed(self.TEXT_STATUS_TERHUBUNG, timeout=3)

    def open_hubungkan_modal(self):
        """Membuka modal panduan dan aktivasi Hubungkan eWallet ECGO."""
        self.click(self.BTN_HUBUNGKAN_EWALLET, label="Tombol Hubungkan eWallet")

    def click_putuskan_ewallet(self):
        """Mengetuk tombol putuskan sambungan eWallet ECGO."""
        self.click(self.BTN_PUTUSKAN_EWALLET, label="Tombol Putuskan eWallet")

    def confirm_putuskan_ewallet(self):
        """Mengonfirmasi pemutusan hubungan eWallet."""
        self.click(self.BTN_CONFIRM_PUTUSKAN, label="Konfirmasi Ya, Putuskan eWallet")

    def open_pengaturan_otomatis(self):
        """Membuka layar Pengaturan Otomatis transfer saldo."""
        self.click(self.MENU_PENGATURAN_OTOMATIS, label="Menu Pengaturan Otomatis")

    def open_tarik_dana(self):
        """Membuka layar Tarik Dana penarikan saldo."""
        self.click(self.MENU_TARIK_DANA, label="Menu Tarik Dana")

    def enter_nominal_tarik_dana(self, amount: str):
        """Memasukkan nominal penarikan dana."""
        self.type_text(self.FIELD_NOMINAL_TARIK_DANA, amount, label="Field Nominal Tarik Dana")

    def click_konfirmasi_penarikan(self):
        """Mengetuk tombol konfirmasi penarikan dana."""
        self.click(self.BTN_KONFIRMASI_PENARIKAN, label="Tombol Konfirmasi Penarikan")

    def open_rekening_tersimpan(self):
        """Membuka sub-menu Nomor Rekening Tersimpan."""
        self.scroll_down()
        self.click(self.MENU_REKENING_TERSIMPAN, label="Menu Nomor Rekening Tersimpan")

    def click_tambah_rekening_baru(self):
        """Mengetuk tombol tambah rekening bank baru."""
        self.click(self.BTN_TAMBAH_REKENING_BARU, label="Tombol Tambah Nomor Rekening Baru")

    def input_data_rekening(self, no_rek: str, nama: str):
        """Mengisi data nomor rekening dan nama pemilik."""
        self.type_text(self.FIELD_INPUT_REKENING, no_rek, label="Input Nomor Rekening")
        self.type_text(self.FIELD_INPUT_PEMILIK, nama, label="Input Nama Pemilik")

    def click_simpan_rekening(self):
        """Mengetuk tombol simpan rekening bank."""
        self.click(self.BTN_SIMPAN_REKENING, label="Tombol Simpan Rekening")

    def click_hapus_rekening(self):
        """Mengetuk tombol hapus rekening tersimpan."""
        self.click(self.BTN_HAPUS_REKENING, label="Tombol Hapus Rekening")

    def confirm_delete_rekening(self):
        """Mengonfirmasi hapus rekening bank."""
        self.click(self.BTN_CONFIRM_DELETE_REKENING, label="Konfirmasi Hapus Rekening")

    def cancel_delete_rekening(self):
        """Membatalkan hapus rekening bank."""
        self.click(self.BTN_CANCEL_DELETE_REKENING, label="Batal Hapus Rekening")

    def open_bayar_tagihan(self):
        """Membuka menu Bayar Tagihan driver."""
        self.click(self.MENU_BAYAR_TAGIHAN, label="Menu Bayar Tagihan")

    # ==========================================================================
    # 8. TOP-UP / ISI ULANG SALDO & SALIN TRANSAKSI
    # ==========================================================================
    MENU_ISI_ULANG_SALDO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Riwayat Isi Ulang Saldo') or contains(@text, 'Riwayat Isi Ulang Saldo') or "
        "contains(@content-desc, 'Top-up') or contains(@text, 'Top-up')]"
    )
    ROUTE_BANK_TO_EVMOTO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bank → Saldo EVMoto') or contains(@text, 'Bank → Saldo EVMoto')]"
    )
    ROUTE_QRIS_TO_EVMOTO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'QRIS → Saldo EVMoto') or contains(@text, 'QRIS → Saldo EVMoto')]"
    )
    ROUTE_ECGO_TO_EVMOTO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo ECGO → Saldo EVMoto') or contains(@text, 'Saldo ECGO → Saldo EVMoto')]"
    )
    BTN_SIMPAN_QRIS_GALLERY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Simpan') or contains(@text, 'Simpan') or contains(@content-desc, 'Gallery')]"
    )
    SNACKBAR_GALLERY_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil menyimpan gambar') or contains(@text, 'Berhasil menyimpan gambar')]"
    )
    BTN_SALIN_TXN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Salin') or contains(@text, 'Salin') or contains(@class, 'Copy')]"
    )
    SNACKBAR_TXN_COPIED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'No. transaksi berhasil disalin') or contains(@text, 'No. transaksi berhasil disalin')]"
    )
    EMPTY_STATE_RECHARGE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tidak Memiliki Riwayat Isi Ulang Saldo') or contains(@text, 'Tidak Memiliki Riwayat Isi Ulang Saldo')]"
    )

    def open_isi_ulang_saldo(self):
        """Membuka layar Isi Ulang Saldo / Top-up."""
        self.click(self.MENU_ISI_ULANG_SALDO, label="Menu Isi Ulang Saldo")

    def click_simpan_gambar_qris(self):
        """Mengetuk tombol simpan QRIS ke galeri ponsel."""
        self.click(self.BTN_SIMPAN_QRIS_GALLERY, label="Tombol Simpan QRIS ke Gallery")

    def click_salin_no_transaksi(self):
        """Mengetuk tombol salin nomor transaksi."""
        self.click(self.BTN_SALIN_TXN, label="Tombol Salin No Transaksi")

