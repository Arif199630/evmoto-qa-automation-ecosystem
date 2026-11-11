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
    # Label persis. contains('Terhubung') juga cocok dengan 'Tidak Terhubung dengan ECGO' / 'Belum Terhubung'.
    TEXT_STATUS_TERHUBUNG = (
        AppiumBy.XPATH,
        "//*[@content-desc='Terhubung dengan ECGO' or @text='Terhubung dengan ECGO' or "
        "@content-desc='Terhubung' or @text='Terhubung']"
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

    # ==========================================================================
    # 9. LOCATOR TAMBAHAN UNTUK VERIFIKASI HASIL (TEKS DARI driver_strings_id.json)
    # ==========================================================================
    # Label item riwayat isi ulang: ewallet_history_topup + rute isi ulang
    ITEM_RIWAYAT_ISI_ULANG = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Top-up Saldo') or contains(@text, 'Top-up Saldo') or "
        "contains(@content-desc, 'Bank → Saldo EVMoto') or contains(@text, 'Bank → Saldo EVMoto') or "
        "contains(@content-desc, 'QRIS → Saldo EVMoto') or contains(@text, 'QRIS → Saldo EVMoto') or "
        "contains(@content-desc, 'Saldo ECGO → Saldo EVMoto') or contains(@text, 'Saldo ECGO → Saldo EVMoto')]"
    )
    # ewallet_history_recharge_empty_description
    TEXT_EMPTY_RECHARGE_DESCRIPTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Anda belum pernah melakukan isi ulang saldo') or "
        "contains(@text, 'Anda belum pernah melakukan isi ulang saldo')]"
    )
    # ewallet_total_unpaid_title: 'Total Tunggakan {{amount}}'
    TEXT_TOTAL_TUNGGAKAN = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Total Tunggakan') or starts-with(@text, 'Total Tunggakan')]"
    )
    # ewallet_total_unpaid_description (penjelasan agar terhindar dari denda)
    TEXT_TUNGGAKAN_DESCRIPTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'mohon segera melunasi tunggakan') or contains(@text, 'mohon segera melunasi tunggakan')]"
    )
    # ewallet_no_outstanding
    TEXT_TIDAK_ADA_TUNGGAKAN = (
        AppiumBy.XPATH,
        "//*[@content-desc='Tidak ada tunggakan' or @text='Tidak ada tunggakan']"
    )
    # ewallet_no_bills_to_pay
    TEXT_TIDAK_ADA_TAGIHAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tidak ada tagihan yang dapat dibayar') or contains(@text, 'Tidak ada tagihan yang dapat dibayar')]"
    )
    # ewallet_bill_* : jenis tagihan armada
    ITEM_JENIS_TAGIHAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tagihan Swap Baterai') or contains(@text, 'Tagihan Swap Baterai') or "
        "contains(@content-desc, 'Tagihan Motor Bulanan') or contains(@text, 'Tagihan Motor Bulanan') or "
        "contains(@content-desc, 'Tagihan Motor Harian') or contains(@text, 'Tagihan Motor Harian') or "
        "contains(@content-desc, 'Tagihan Garansi Baterai Harian') or contains(@text, 'Tagihan Garansi Baterai Harian')]"
    )
    # ewallet_link_required_for_pay_bill
    TEXT_LINK_REQUIRED_FOR_PAY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hubungkan eWallet terlebih dahulu') or contains(@text, 'Hubungkan eWallet terlebih dahulu')]"
    )
    # ewallet_cancel_description (isi dialog putuskan eWallet)
    TEXT_PUTUSKAN_DESCRIPTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Jika diputuskan, eWallet EVMoto') or contains(@text, 'Jika diputuskan, eWallet EVMoto')]"
    )
    # Tombol batal di dialog putuskan: string resmi 'Batalkan' (cancel) atau 'Batal'
    BTN_CANCEL_PUTUSKAN = (
        AppiumBy.XPATH,
        "//android.widget.Button[@content-desc='Batalkan' or @text='Batalkan' or @content-desc='Batal' or @text='Batal']"
    )
    # ewallet_txn_copied
    SNACKBAR_TXN_COPIED_EXACT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'No. transaksi berhasil disalin') or contains(@text, 'No. transaksi berhasil disalin')]"
    )

    def scroll_down(self, ratio: float = 0.4):
        """Menggeser layar ke bawah (jari dari 70% ke 30% tinggi layar) memakai swipe dari BasePage."""
        size = self.driver.get_window_size()
        x = int(size["width"] / 2)
        start_y = int(size["height"] * 0.7)
        end_y = int(size["height"] * (0.7 - ratio))
        self.swipe(x, start_y, x, end_y, 500)
        time.sleep(0.5)

    def is_ecgo_not_connected(self) -> bool:
        """Memeriksa status 'Tidak Terhubung dengan ECGO' / 'Belum Terhubung'."""
        return self.is_displayed(self.TEXT_STATUS_BELUM_TERHUBUNG, timeout=3)

    def has_recharge_history_items(self) -> bool:
        """Memeriksa ada item riwayat isi ulang (Top-up Saldo / rute Bank, QRIS, Saldo ECGO)."""
        return self.is_displayed(self.ITEM_RIWAYAT_ISI_ULANG, timeout=4)

    def is_recharge_empty_state_displayed(self) -> bool:
        """Memeriksa empty state 'Tidak Memiliki Riwayat Isi Ulang Saldo'."""
        return self.is_displayed(self.EMPTY_STATE_RECHARGE, timeout=4)

    def is_recharge_empty_description_displayed(self) -> bool:
        """Memeriksa teks 'Anda belum pernah melakukan isi ulang saldo.'"""
        return self.is_displayed(self.TEXT_EMPTY_RECHARGE_DESCRIPTION, timeout=3)

    def is_txn_copied_snackbar_displayed(self) -> bool:
        """Memeriksa snackbar 'No. transaksi berhasil disalin.'"""
        return self.is_displayed(self.SNACKBAR_TXN_COPIED_EXACT, timeout=3)

    def get_clipboard_text(self) -> str:
        """Membaca isi clipboard perangkat Android lewat Appium."""
        return self.driver.get_clipboard_text() or ""

    def is_total_tunggakan_displayed(self) -> bool:
        """Memeriksa kartu 'Total Tunggakan Rp...'."""
        return self.is_displayed(self.TEXT_TOTAL_TUNGGAKAN, timeout=4)

    def is_tunggakan_description_displayed(self) -> bool:
        """Memeriksa penjelasan tunggakan agar terhindar dari denda."""
        return self.is_displayed(self.TEXT_TUNGGAKAN_DESCRIPTION, timeout=3)

    def is_no_outstanding_displayed(self) -> bool:
        """Memeriksa teks 'Tidak ada tunggakan'."""
        return self.is_displayed(self.TEXT_TIDAK_ADA_TUNGGAKAN, timeout=3)

    def is_no_bills_displayed(self) -> bool:
        """Memeriksa teks 'Tidak ada tagihan yang dapat dibayar.'"""
        return self.is_displayed(self.TEXT_TIDAK_ADA_TAGIHAN, timeout=3)

    def has_bill_type_items(self) -> bool:
        """Memeriksa ada item tagihan armada (Swap Baterai / Motor Bulanan / Motor Harian / Garansi Baterai)."""
        return self.is_displayed(self.ITEM_JENIS_TAGIHAN, timeout=4)

    def is_link_required_message_displayed(self) -> bool:
        """Memeriksa pesan 'Hubungkan eWallet terlebih dahulu untuk melakukan pembayaran tagihan.'"""
        return self.is_displayed(self.TEXT_LINK_REQUIRED_FOR_PAY, timeout=4)

    def is_link_ecgo_modal_displayed(self) -> bool:
        """Memeriksa modal 'Hubungkan EVMoto dengan ECGO'."""
        return self.is_displayed(self.TITLE_LINK_ECGO_MODAL, timeout=4)

    def is_putuskan_dialog_displayed(self) -> bool:
        """Memeriksa dialog putuskan eWallet: teks peringatan dan tombol 'Ya, Putuskan' tampil."""
        return self.is_displayed(self.TEXT_PUTUSKAN_DESCRIPTION, timeout=4) and self.is_displayed(self.BTN_CONFIRM_PUTUSKAN, timeout=2)

    def cancel_putuskan_ewallet(self):
        """Mengetuk tombol batal pada dialog putuskan eWallet."""
        self.click(self.BTN_CANCEL_PUTUSKAN, label="Tombol Batal Putuskan eWallet")

    def press_back(self):
        """Menekan tombol Back Android (menutup dialog yang terbuka)."""
        self.driver.back()
        time.sleep(0.5)
