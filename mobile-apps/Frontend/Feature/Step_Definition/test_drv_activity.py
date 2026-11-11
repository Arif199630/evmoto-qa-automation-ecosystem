"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - TEST SUITE: AKTIVITAS SAYA & GUARANTEE INCOME
================================================================================
Aplikasi        : EvMoto Driver Dev (com.evmoto.driver.app)
Target File     : test_drv_activity.py
Environment     : Dev Golang (https://evmotodev.justkidding.app)
Akun Driver     : <TEST_USER_PHONE> | PIN Bypass <EVMOTO_OTP_BYPASS>
Metodologi      : Page Object Model (POM) & 4 Pilar QA Lengkap
Wording         : 100% Presisi strings resmi APK driver_strings_id.json
================================================================================
Catatan validitas:
- Test yang isinya bergantung data akun (riwayat GI, mutasi, referral) di-skip dengan alasan
  jelas bila data pra-kondisinya tidak ada, dan GAGAL bila data ada tetapi tampilannya salah.
- Test yang butuh simulasi GPS / backend / perangkat kedua di-skip (bukan assert palsu).
================================================================================
"""
import re
import time
import pytest
from Pages.drv_login_page import DrvLoginPage
from Pages.drv_home_page import DrvHomePage
from Pages.drv_activity_page import DrvActivityPage
from Frontend.Feature.Helper.admin_fare_calculator import AdminDashboardFareCalculator
from Data.drv_data import (
    DRIVER_ACTIVE_PHONE,
    DRIVER_ACTIVE_PIN,
    DRV_ACT_DATA_POSITIVE_TRUE,
    DRV_ACT_DATA_BUSINESS_LOGIC,
    DRV_ACT_DATA_NEGATIVE_TRUE,
    DRV_ACT_DATA_NEGATIVE_FALSE
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvActivity")


@pytest.mark.driver_app
@pytest.mark.drv_activity
class TestDrvActivity:
    """Test Suite Komprehensif untuk Layar Aktivitas Saya & Dashboard Guarantee Income (GI)."""

    @pytest.fixture(autouse=True)
    def anti_race_condition_pause(self):
        """Jeda deliberasi anti race condition antar test case."""
        yield
        time.sleep(3.0)

    def _ensure_driver_on_activity(self, driver_app):
        """Helper pra-kondisi: memastikan driver login dan membuka layar Aktivitas Saya."""
        login_pg = DrvLoginPage(driver_app)
        home_pg = DrvHomePage(driver_app)
        act_pg = DrvActivityPage(driver_app)

        login_pg.handle_system_permissions()
        if not home_pg.is_home_screen_displayed() and not act_pg.is_activity_screen_displayed():
            login_pg.login_as_driver(phone=DRIVER_ACTIVE_PHONE, otp=DRIVER_ACTIVE_PIN)

        if home_pg.is_home_screen_displayed():
            home_pg.navigate_to_activity()

    def _buka_tab_gi(self, driver_app) -> DrvActivityPage:
        """Pra-kondisi: driver berada di tab Guarantee Income yang berisi data program GI.

        Akun tanpa program GI menampilkan 'Belum Tersedia Gurantee Income'; isi dashboard
        tidak bisa diverifikasi sehingga test di-skip (bukan dianggap lulus).
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_gi_tab()
        if act_pg.is_gi_program_not_available():
            pytest.skip("Akun driver uji belum memiliki program Guarantee Income "
                        "(tampil 'Belum Tersedia Gurantee Income'); dashboard GI tidak bisa diverifikasi.")
        return act_pg

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH AKTIVITAS & GUARANTEE INCOME
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_01_akses_tab_aktivitas_saya(self, driver_app):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Membuka layar Aktivitas Saya melalui Bottom Navigation Bar.
        Ekspektasi: Layar Aktivitas Saya aktif dengan tab Pesanan, Guarantee Income, dan Pendapatan.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)

        given("Driver berada pada Halaman Beranda utama")
        when("Driver mengetuk tab navigasi 'Aktivitas Saya' pada Bottom Navigation Bar")
        then("Sistem mengarahkan driver ke Halaman Aktivitas Saya")
        assert act_pg.is_activity_screen_displayed()

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_02_beralih_ke_tab_guarantee_income(self, driver_app):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Beralih ke Tab Guarantee Income (GI) dari layar Aktivitas.
        Ekspektasi: Menampilkan dashboard dan indikator metrik jaminan pendapatan.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)

        given("Driver berada pada layar Aktivitas Saya")
        when("Driver mengetuk tab 'Guarantee Income'")
        act_pg.switch_to_gi_tab()
        then("Layar beralih menampilkan metrik jaminan pendapatan")
        assert act_pg.is_gi_dashboard_displayed()

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_03_verifikasi_kartu_total_guarantee_income(self, driver_app):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Memeriksa tampilan kartu TOTAL GUARANTEE INCOME pada dashboard GI.
        Ekspektasi: Menampilkan nominal total hak jaminan pendapatan harian.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver berada pada Tab Guarantee Income")
        when("Driver memeriksa kartu header utama")
        then("Komponen 'TOTAL GUARANTEE INCOME' tertera dengan jelas")
        assert act_pg.scroll_until_visible(act_pg.CARD_TOTAL_GI), \
            "Kartu 'TOTAL GUARANTEE INCOME' tidak tampil di tab Guarantee Income"
        nominal = act_pg.read_amount_near(act_pg.CARD_TOTAL_GI)
        assert nominal is not None, "Nominal Rupiah pada kartu 'TOTAL GUARANTEE INCOME' tidak terbaca"
        assert nominal >= 0, f"Total Guarantee Income tidak boleh negatif, tertulis Rp {nominal:,.0f}"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_04_verifikasi_rate_gi_per_hour(self, driver_app):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Memeriksa ketentuan Guarantee Income/Hour (*Per jam Rp 30.000).
        Ekspektasi: Taraf nominal per jam ditampilkan transparan sebagai acuan insentif.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver berada pada Tab Guarantee Income")
        when("Driver meninjau rate insentif per jam")
        then("Keterangan rate per jam tercantum pada antarmuka")
        assert act_pg.scroll_until_visible(act_pg.TEXT_GI_RATE_PER_JAM), \
            "Keterangan rate '*Per jam Rp ...' tidak tampil di tab Guarantee Income"
        rate = act_pg.read_amount_near(act_pg.TEXT_GI_RATE_PER_JAM)
        assert rate is not None and rate > 0, f"Rate GI per jam harus nominal Rupiah lebih dari 0, terbaca: {rate}"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_05_verifikasi_kartu_total_akumulasi_gi(self, driver_app):
        """
        [POSITIVE TRUE - PT-05]
        Deskripsi : Memeriksa kartu Total Akumulasi Guarantee Income driver.
        Ekspektasi: Akumulasi jam online dan pendapatan yang terkumpul terhitung sinkron.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver berada pada Tab Guarantee Income")
        when("Driver meninjau kartu 'Total Akumulasi Guarantee Income'")
        then("Nilai akumulasi pendapatan jaminan ditampilkan")
        assert act_pg.scroll_until_visible(act_pg.CARD_AKUMULASI_GI), \
            "Kartu 'Total Akumulasi Guarantee Income' tidak tampil"
        akumulasi = act_pg.read_amount_near(act_pg.CARD_AKUMULASI_GI)
        assert akumulasi is not None, "Nominal Rupiah 'Total Akumulasi Guarantee Income' tidak terbaca"
        assert akumulasi >= 0, f"Total akumulasi GI tidak boleh negatif, tertulis Rp {akumulasi:,.0f}"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_06_verifikasi_kartu_net_payment_of_guarantee(self, driver_app):
        """
        [POSITIVE TRUE - PT-06]
        Deskripsi : Memeriksa kartu Net Payment of Guarantee yang siap dicairkan ke saldo.
        Ekspektasi: Menampilkan nominal bersih hak subsidi jaminan pendapatan.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver berada pada Tab Guarantee Income")
        when("Driver memeriksa kartu 'Net Payment of Guarantee'")
        then("Nominal net payment ditampilkan sesuai hak subsidi mitra")
        assert act_pg.scroll_until_visible(act_pg.CARD_NET_PAYMENT_GI), "Kartu 'Net Payment of Guarantee' tidak tampil"
        net = act_pg.read_amount_near(act_pg.CARD_NET_PAYMENT_GI)
        assert net is not None, "Nominal Rupiah 'Net Payment of Guarantee' tidak terbaca"
        # Aturan APK (my_activity_not_minus): net payment tidak pernah minus
        assert net >= 0, f"Net Payment of Guarantee tidak boleh minus, tertulis Rp {net:,.0f}"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_07_verifikasi_komponen_dipotong_dari_gi(self, driver_app):
        """
        [POSITIVE TRUE - PT-07]
        Deskripsi : Memeriksa komponen 'Dipotong dari Guarantee Income' (Order Income offset).
        Ekspektasi: Nilai pendapatan trip yang mengurangi subsidi tercantum transparan.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver berada pada Tab Guarantee Income")
        when("Driver meninjau potongan pendapatan pesanan aktif")
        then("Komponen pemotong jaminan pendapatan tertera akurat")
        assert act_pg.scroll_until_visible(act_pg.CARD_DEDUCTION_GI), \
            "Komponen 'Dipotong dari Guarantee Income' tidak tampil"
        potongan = act_pg.read_amount_near(act_pg.CARD_DEDUCTION_GI)
        assert potongan is not None, "Nominal Rupiah 'Dipotong dari Guarantee Income' tidak terbaca"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_08_verifikasi_label_periode_jam_operasional(self, driver_app):
        """
        [POSITIVE TRUE - PT-08]
        Deskripsi : Memeriksa label rentang waktu operasional jaminan (Periode: 06:00 - 22:00).
        Ekspektasi: Jam mulai dan berakhirnya program Guarantee Income ditampilkan.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver berada pada Tab Guarantee Income")
        when("Driver membaca klausul jam operasional")
        then("Label periode operasional (Periode: start - end) tampil valid")
        teks = " ".join(act_pg.read_texts_near(act_pg.TEXT_GI_PERIODE))
        assert teks, "Label '(Periode: ... - ...)' tidak tampil di tab Guarantee Income"
        assert "{{" not in teks, f"Template periode belum terisi data: '{teks}'"
        assert re.search(r"Periode:\s*\d{1,2}[:.]\d{2}\s*-\s*\d{1,2}[:.]\d{2}", teks), \
            f"Format periode harus 'Periode: HH:MM - HH:MM', tertulis: '{teks}'"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_09_verifikasi_timer_sisa_waktu_jaminan_hari_ini(self, driver_app):
        """
        [POSITIVE TRUE - PT-09]
        Deskripsi : Memeriksa timer hitung mundur 'Sisa waktu jaminan hari ini'.
        Ekspektasi: Timer countdown aktif menghitung sisa durasi shift jaminan pendapatan.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver online di area Guarantee Income")
        if act_pg.is_gi_outside_area():
            pytest.skip("Driver uji sedang di luar area Guarantee Income; timer jaminan hari ini "
                        "hanya berjalan di dalam area (butuh lokasi GPS di area GI).")
        when("Driver memantau widget timer durasi")
        then("Widget 'Sisa waktu jaminan hari ini' aktif berjalan")
        assert act_pg.scroll_until_visible(act_pg.TIMER_REMAINING_TODAY), \
            "Widget 'Sisa waktu jaminan hari ini' tidak tampil"
        assert act_pg.read_time_near(act_pg.TIMER_REMAINING_TODAY), \
            "Nilai countdown (format HH:MM) pada 'Sisa waktu jaminan hari ini' tidak terbaca"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_10_verifikasi_timer_sisa_waktu_kembali_ke_area(self, driver_app):
        """
        [POSITIVE TRUE - PT-10]
        Deskripsi : Memeriksa timer 'Sisa waktu kembali ke area' saat driver melintasi batas zona.
        Ekspektasi: Tampil countdown toleransi waktu kembali sebelum benefit GI gugur.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver berada di luar area setelah menyelesaikan perjalanan")
        if not act_pg.is_gi_outside_area():
            pytest.skip("Pra-kondisi tidak terpenuhi: driver uji tidak sedang di luar area GI setelah "
                        "perjalanan (butuh simulasi GPS keluar area + trip selesai).")
        when("Driver melihat indikator batas waktu kembali")
        then("Timer 'Sisa waktu kembali ke area' tampil informatif")
        assert act_pg.scroll_until_visible(act_pg.TIMER_REMAINING_RETURN), \
            "Timer 'Sisa waktu kembali ke area' tidak tampil padahal driver di luar area GI"
        assert act_pg.read_time_near(act_pg.TIMER_REMAINING_RETURN), \
            "Nilai countdown pada 'Sisa waktu kembali ke area' tidak terbaca"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_11_verifikasi_notice_buffer_kembali_20_persen(self, driver_app):
        """
        [POSITIVE TRUE - PT-11]
        Deskripsi : Memeriksa klausul 'Batas waktu kembali dihitung durasi terakhir + 20%'.
        Ekspektasi: Aturan penambahan waktu toleransi kembali dijelaskan secara transparan.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver meninjau ketentuan toleransi perjalanan luar zona")
        when("Driver membaca catatan kaki batas waktu")
        then("Penjelasan perhitungan durasi terakhir + persentase buffer tertera")
        teks = " ".join(act_pg.read_texts_near(act_pg.NOTICE_RETURN_BUFFER))
        assert teks, "Catatan 'Batas waktu kembali dihitung durasi terakhir + ...%' tidak tampil"
        assert re.search(r"\+\s*\d+\s*%", teks), \
            f"Persentase buffer belum terisi angka (template '{{{{percent}}}}'?): '{teks}'"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_12_verifikasi_snackbar_memasuki_wilayah_gi(self):
        """
        [POSITIVE TRUE - PT-12]
        Deskripsi : Memeriksa snackbar 'Anda telah memasuki wilayah Gurantee Income'.
        Ekspektasi: Snackbar hijau tampil otomatis mengonfirmasi driver masuk zona GI.
        """
        given("Driver bergerak memasuki batas perimeter zona GI")
        when("Sistem mendeteksi koordinat GPS valid")
        then("Snackbar 'Anda telah memasuki wilayah Gurantee Income' muncul")
        pytest.skip("Butuh simulasi perpindahan GPS melintasi batas area GI; koordinat poligon area GI "
                    "dev belum tersedia untuk automation, jadi snackbar tidak bisa dipicu dari UI.")

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_13_verifikasi_snackbar_keluar_wilayah_gi(self):
        """
        [POSITIVE TRUE - PT-13]
        Deskripsi : Memeriksa snackbar 'Anda telah keluar wilayah Gurantee Income'.
        Ekspektasi: Peringatan visual muncul saat kendaraan melintasi batas luar zona.
        """
        given("Driver melintasi batas luar wilayah GI")
        when("Sistem mendeteksi perpindahan zona")
        then("Snackbar peringatan 'Anda telah keluar wilayah Gurantee Income' tampil")
        pytest.skip("Butuh simulasi perpindahan GPS keluar dari area GI; koordinat poligon area GI "
                    "dev belum tersedia untuk automation, jadi snackbar tidak bisa dipicu dari UI.")

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_14_akses_riwayat_guarantee_income_hari_ini(self, driver_app):
        """
        [POSITIVE TRUE - PT-14]
        Deskripsi : Membuka daftar riwayat 'Guarantee Income Hari Ini'.
        Ekspektasi: Rincian pendapatan jam kerja dan pesanan harian terdaftar runtut.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver berada pada Tab Guarantee Income")
        when("Driver meninjau seksi 'Guarantee Income Hari Ini'")
        then("Daftar histori pendapatan harian ditampilkan")
        assert act_pg.scroll_until_visible(act_pg.SECTION_GI_HARI_INI), \
            "Seksi 'Guarantee Income Hari Ini' tidak tampil"
        # Seksi harus berisi salah satu dari dua isi resmi: riwayat berstatus, atau teks
        # empty state 'Anda belum memiliki pendapatan Guarantee Income pada hari ini'.
        assert act_pg.has_gi_history_status_badge() or act_pg.is_gi_today_empty(), \
            "Seksi 'Guarantee Income Hari Ini' kosong: tidak ada riwayat berstatus maupun teks empty state"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_15_verifikasi_badge_status_sudah_dibayarkan(self, driver_app):
        """
        [POSITIVE TRUE - PT-15]
        Deskripsi : Memeriksa badge status GI 'Sudah Dibayarkan' (Paid).
        Ekspektasi: Badge berwarna hijau menunjukkan dana subsidi GI telah masuk saldo.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Terdapat transaksi subsidi GI yang telah dicairkan")
        if act_pg.is_gi_today_empty():
            pytest.skip("Akun driver uji belum memiliki riwayat Guarantee Income; badge status tidak bisa diverifikasi.")
        when("Driver memeriksa badge status transaksi")
        tampil_paid = act_pg.scroll_until_visible(act_pg.BADGE_STATUS_PAID, max_swipes=3)
        if not tampil_paid and act_pg.is_displayed(act_pg.BADGE_STATUS_WAITING, timeout=2):
            pytest.skip("Riwayat GI akun uji baru berstatus 'Menunggu Konfirmasi'; belum ada yang sudah dicairkan.")
        then("Status 'Sudah Dibayarkan' terverifikasi")
        assert tampil_paid, "Riwayat GI ada tetapi tidak satu pun menampilkan badge status 'Sudah Dibayarkan'"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_16_verifikasi_badge_status_menunggu_konfirmasi(self, driver_app):
        """
        [POSITIVE TRUE - PT-16]
        Deskripsi : Memeriksa badge status GI 'Menunggu Konfirmasi' (Pending Verification).
        Ekspektasi: Badge kuning tampil selama sistem memverifikasi integritas trip harian.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Shift harian baru saja berakhir")
        if act_pg.is_gi_today_empty():
            pytest.skip("Akun driver uji belum memiliki riwayat Guarantee Income; badge status tidak bisa diverifikasi.")
        when("Driver memantau status rekonsiliasi subsidi")
        tampil_waiting = act_pg.scroll_until_visible(act_pg.BADGE_STATUS_WAITING, max_swipes=3)
        if not tampil_waiting and act_pg.is_displayed(act_pg.BADGE_STATUS_PAID, timeout=2):
            pytest.skip("Semua riwayat GI akun uji sudah 'Sudah Dibayarkan'; tidak ada yang sedang menunggu verifikasi.")
        then("Status 'Menunggu Konfirmasi' ditampilkan sampai verifikasi tuntas")
        assert tampil_waiting, "Riwayat GI ada tetapi tidak satu pun menampilkan badge status 'Menunggu Konfirmasi'"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_17_ketuk_tombol_lihat_detail_riwayat_gi(self, driver_app):
        """
        [POSITIVE TRUE - PT-17]
        Deskripsi : Mengetuk tombol 'Lihat Detail' pada kartu riwayat pencairan GI.
        Ekspektasi: Muncul modal rincian kalkulasi: durasi online, order income, dan payout.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Driver melihat kartu riwayat GI")
        if act_pg.is_gi_today_empty():
            pytest.skip("Akun driver uji belum memiliki riwayat Guarantee Income; tombol 'Lihat Detail' tidak tersedia.")
        assert act_pg.scroll_until_visible(act_pg.BTN_LIHAT_DETAIL_GI), \
            "Riwayat GI ada tetapi tombol 'Lihat Detail' tidak tampil"
        when("Driver mengetuk tombol 'Lihat Detail'")
        act_pg.click_lihat_detail_gi()
        then("Modal rincian kalkulasi subsidi ditampilkan")
        assert act_pg.is_gi_detail_displayed(), \
            "Rincian GI ('Riwayat Guarantee Income' / 'Total Net Gurantee') tidak terbuka setelah mengetuk 'Lihat Detail'"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_18_beralih_ke_tab_riwayat_pendapatan_revenue_summary(self, driver_app):
        """
        [POSITIVE TRUE - PT-18]
        Deskripsi : Beralih ke Tab Riwayat Pendapatan (Revenue Summary).
        Ekspektasi: Menampilkan rekapitulasi finansial argo dan potongan operasional.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)

        given("Driver berada pada layar Aktivitas Saya")
        when("Driver mengetuk tab 'Revenue Summary' / Riwayat Pendapatan")
        act_pg.switch_to_revenue_tab()
        then("Halaman menampilkan ringkasan pendapatan driver")
        assert act_pg.is_revenue_summary_displayed()

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_19_verifikasi_kartu_ringkasan_pendapatan_driver(self, driver_app):
        """
        [POSITIVE TRUE - PT-19]
        Deskripsi : Memeriksa kartu ringkasan 'Pendapatan driver' dan 'Yang didapatkan driver'.
        Ekspektasi: Nilai kotor vs nilai bersih setelah potongan terpisah transparan.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_revenue_tab()

        given("Driver berada pada layar Revenue Summary")
        if act_pg.is_revenue_empty_state_displayed():
            pytest.skip("Akun driver uji belum memiliki riwayat pendapatan; kartu ringkasan tidak bisa diverifikasi.")
        when("Driver meninjau kartu rincian penghasilan")
        then("Nilai kotor dan penghasilan bersih tercantum jelas")
        # Label APK: my_activity_coupon_order_amount (kotor) dan my_activity_coupon_order_income (bersih)
        kotor = act_pg.read_amount_near(act_pg.TEXT_ORDER_AMOUNT)
        bersih = act_pg.read_amount_near(act_pg.TEXT_ORDER_INCOME)
        assert kotor is not None, "Nilai kotor 'Order Amount' tidak tampil/terbaca di ringkasan pendapatan"
        assert bersih is not None, "Nilai bersih 'Order Income' tidak tampil/terbaca di ringkasan pendapatan"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_20_verifikasi_klausul_potongan_platform_fee_10_persen(self):
        """
        [POSITIVE TRUE - PT-20]
        Deskripsi : Memeriksa klausul potongan Platform Fee (10% dari total biaya jarak tempuh).
        Ekspektasi: Biaya platform 10% tercatat sinkron dengan ketentuan backend produksi.
        """
        given("Driver meninjau potongan administrasi")
        when("Driver membaca rincian platform fee")
        then("Catatan '10% dari total biaya jarak tempuh' tercantum pada rincian")
        pytest.skip("Teks klausul platform fee 10% tidak ada di strings resmi APK (driver_strings_id.json), "
                    "jadi lokasi/teks yang harus diverifikasi belum bisa dipastikan; perlu konfirmasi desain layar.")

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_21_verifikasi_rincian_biaya_promo_disubsidi(self, driver_app):
        """
        [POSITIVE TRUE - PT-21]
        Deskripsi : Memeriksa komponen 'Biaya promo' voucher yang disubsidi sistem.
        Ekspektasi: Nilai voucher diskon penumpang tidak memotong pendapatan mitra driver.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_revenue_tab()

        given("Driver memeriksa transaksi bertiket promosi")
        if act_pg.is_revenue_empty_state_displayed():
            pytest.skip("Akun driver uji belum memiliki riwayat pendapatan; komponen 'Biaya promo' tidak bisa diverifikasi.")
        if not act_pg.scroll_until_visible(act_pg.TEXT_PROMO_FEE, max_swipes=3):
            pytest.skip("Riwayat pendapatan akun uji tidak memuat transaksi berpromo ('Biaya promo').")
        when("Driver melihat komponen 'Biaya promo'")
        then("Sistem mengonfirmasi subsidi promo ditanggung platform")
        promo = act_pg.read_amount_near(act_pg.TEXT_PROMO_FEE)
        assert promo is not None, "Komponen 'Biaya promo' tampil tanpa nominal Rupiah yang terbaca"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_22_verifikasi_pembukuan_perubahan_saldo_before_after(self, driver_app):
        """
        [POSITIVE TRUE - PT-22]
        Deskripsi : Memeriksa pembukuan ledger: Saldo sebelum, Perubahan saldo, Saldo sesudah.
        Ekspektasi: Seluruh mutasi kredit/debit tercatat secara matematis akurat.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_revenue_tab()

        given("Driver membuka detail mutasi transaksi")
        if act_pg.is_revenue_empty_state_displayed():
            pytest.skip("Akun driver uji belum memiliki mutasi pendapatan; ledger saldo tidak bisa diverifikasi.")
        when("Driver meninjau ledger audit saldo")
        then("Data Saldo Sebelum, Perubahan Saldo, dan Saldo Sesudah terverifikasi")
        assert act_pg.has_revenue_ledger(), "Riwayat pendapatan ada tetapi baris 'Saldo sebelum' tidak tampil"
        sebelum = act_pg.read_amount_near(act_pg.TEXT_SALDO_SEBELUM)
        perubahan = act_pg.read_amount_near(act_pg.TEXT_PERUBAHAN_SALDO)
        sesudah = act_pg.read_amount_near(act_pg.TEXT_SALDO_SESUDAH)
        assert None not in (sebelum, perubahan, sesudah), (
            f"Nominal ledger tidak lengkap terbaca: sebelum={sebelum}, perubahan={perubahan}, sesudah={sesudah}")
        assert abs((sebelum + perubahan) - sesudah) < 1, (
            f"Ledger tidak seimbang: Rp {sebelum:,.0f} + Rp {perubahan:,.0f} != Rp {sesudah:,.0f}")

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_23_beralih_ke_tab_riwayat_referral_income(self, driver_app):
        """
        [POSITIVE TRUE - PT-23]
        Deskripsi : Beralih ke Tab Riwayat Referral Income dari menu Aktivitas.
        Ekspektasi: Menampilkan performa komisi ajak mitra baru bergabung.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)

        given("Driver berada pada layar Aktivitas Saya")
        when("Driver mengetuk tab 'Referral Income'")
        act_pg.switch_to_referral_tab()
        then("Layar beralih menampilkan Riwayat Referral Income")
        assert act_pg.is_referral_income_displayed()

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_24_verifikasi_ringkasan_komisi_per_register(self, driver_app):
        """
        [POSITIVE TRUE - PT-24]
        Deskripsi : Memeriksa ringkasan insentif komisi 'Per Register'.
        Ekspektasi: Nilai bonus per pendaftaran mitra downline ditampilkan valid.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_referral_tab()

        given("Driver berada pada Tab Referral Income")
        when("Driver membaca rincian skema komisi")
        then("Keterangan komisi 'Per Register' tertera jelas")
        assert act_pg.scroll_until_visible(act_pg.TEXT_REFERRAL_PER_REGISTER), \
            "Keterangan komisi 'Per Register' tidak tampil di tab Referral"
        komisi = act_pg.read_amount_near(act_pg.TEXT_REFERRAL_PER_REGISTER)
        assert komisi is not None and komisi > 0, \
            f"Nilai komisi per register harus nominal Rupiah lebih dari 0, terbaca: {komisi}"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_25_ketuk_tombol_bagikan_kode_referral_mitra(self, driver_app):
        """
        [POSITIVE TRUE - PT-25]
        Deskripsi : Mengetuk tombol Bagikan kode referral ke media sosial atau chat.
        Ekspektasi: Muncul bottom sheet share intent Android dengan kode referral unik driver.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_referral_tab()

        given("Driver melihat kode referral pribadinya")
        when("Driver mengetuk tombol 'Bagikan'")
        act_pg.open_share_referral()
        then("Sistem membuka native share dialog Android")
        share_tampil = act_pg.is_android_share_sheet_displayed()
        if share_tampil:
            act_pg.close_share_sheet()
        assert share_tampil, "Dialog berbagi Android tidak terbuka setelah mengetuk 'Bagikan QR Code'"

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_26_beralih_ke_tab_pesanan_riwayat_order(self, driver_app):
        """
        [POSITIVE TRUE - PT-26]
        Deskripsi : Beralih ke Tab Pesanan pada layar Aktivitas Saya untuk meninjau riwayat order.
        Ekspektasi: Menampilkan daftar riwayat pesanan (Order ID, rute, tarif argo, dan status).
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)

        given("Driver berada pada layar Aktivitas Saya")
        when("Driver mengetuk tab 'Pesanan'")
        act_pg.switch_to_pesanan_tab()
        then("Layar beralih menampilkan daftar riwayat pesanan driver")
        assert act_pg.is_pesanan_tab_displayed()

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_27_buka_detail_pesanan_dan_invoice_driver(self, driver_app):
        """
        [POSITIVE TRUE - PT-27]
        Deskripsi : Membuka kartu pesanan untuk meninjau Invoice dan Rincian Tarif Pesanan Driver.
        Ekspektasi: Tampil rincian invoice: No. Pesanan, Jarak Tempuh, Far Fee, Waiting Fee, Potongan Platform 10%, Subsidi Kupon, dan Pendapatan Bersih Driver.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_pesanan_tab()

        given("Driver berada pada Tab Pesanan dengan riwayat order aktif")
        when("Driver mengetuk salah satu kartu pesanan")
        act_pg.click_order_item_to_view_invoice()
        then("Sistem membuka Layar Detail Pesanan (Invoice Driver)")
        assert act_pg.is_driver_order_invoice_displayed()

    @pytest.mark.positive_true
    def test_TC_DRV_ACT_PT_28_tutup_detail_invoice_kembali_ke_daftar_pesanan(self, driver_app):
        """
        [POSITIVE TRUE - PT-28]
        Deskripsi : Mengetuk tombol kembali dari Layar Detail Pesanan (Invoice Driver).
        Ekspektasi: Antarmuka kembali ke daftar riwayat pesanan tanpa reload/crash.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_pesanan_tab()
        act_pg.click_order_item_to_view_invoice()

        given("Layar Detail Pesanan (Invoice Driver) sedang terbuka")
        when("Driver mengetuk tombol 'Kembali'")
        act_pg.close_order_detail_invoice()
        then("Antarmuka kembali ke daftar riwayat pesanan")
        assert act_pg.is_pesanan_tab_displayed()

    # ==========================================================================
    # PILAR 2: BUSINESS LOGIC (BL) - ATURAN BISNIS & FORMULA GI
    # ==========================================================================

    def _baca_angka_gi(self, act_pg: DrvActivityPage) -> tuple:
        """Membaca (akumulasi, order income yang dipotong, net payment) dari dashboard GI."""
        akumulasi = act_pg.read_amount_near(act_pg.CARD_AKUMULASI_GI)
        dipotong = act_pg.read_amount_near(act_pg.CARD_DEDUCTION_GI)
        net = act_pg.read_amount_near(act_pg.CARD_NET_PAYMENT_GI)
        assert None not in (akumulasi, dipotong, net), (
            f"Angka dashboard GI tidak lengkap terbaca: akumulasi={akumulasi}, dipotong={dipotong}, net={net}")
        # Potongan bisa ditampilkan bertanda minus; yang dihitung adalah besarnya
        return akumulasi, abs(dipotong), net

    @pytest.mark.business_logic
    def test_TC_DRV_ACT_BL_01_formula_net_payment_gi_minus_order_income(self, driver_app):
        """
        [BUSINESS LOGIC - BL-01]
        Deskripsi : Formula Net Payment: Net Guarantee Payout = Guarantee Target - Order Income.
        Ekspektasi: Selisih kekurangan argo disubsidi secara presisi sesuai rumus PRD.
        """
        act_pg = self._buka_tab_gi(driver_app)
        given("Data GI akun uji hari ini (contoh PRD: target Rp 150.000, order income Rp 90.000 -> net Rp 60.000)")
        when("Sistem menjalankan formula subsidi rekonsiliasi harian")
        akumulasi, dipotong, net = self._baca_angka_gi(act_pg)
        then("Net Payment of Guarantee = Total Akumulasi - Order Income (tidak minus)")
        # Rumus dari APK: my_activity_accumulation_note '(Total Akumulasi - Order Income)' + my_activity_not_minus
        harapan = max(0.0, akumulasi - dipotong)
        assert abs(net - harapan) < 1, (
            f"Net Payment salah: tertulis Rp {net:,.0f}, seharusnya max(0, Rp {akumulasi:,.0f} - Rp {dipotong:,.0f}) "
            f"= Rp {harapan:,.0f}")

    @pytest.mark.business_logic
    def test_TC_DRV_ACT_BL_02_net_payment_terkunci_nol_rupiah_saat_target_tercapai(self, driver_app):
        """
        [BUSINESS LOGIC - BL-02]
        Deskripsi : Net payment terkunci Rp 0 jika order income mitra melampaui target jaminan.
        Ekspektasi: Keterangan 'Total Guarantee Payment tetap Rp0' muncul tanpa pemotongan saldo.
        """
        act_pg = self._buka_tab_gi(driver_app)
        given("Mitra memperoleh order income Rp 200.000 melebihi target GI Rp 150.000")
        akumulasi, dipotong, net = self._baca_angka_gi(act_pg)
        if dipotong < akumulasi:
            pytest.skip(f"Pra-kondisi tidak terpenuhi: order income hari ini (Rp {dipotong:,.0f}) belum melampaui "
                        f"target GI (Rp {akumulasi:,.0f}).")
        when("Sistem mengevaluasi selisih subsidi jaminan")
        then("Total Guarantee Payment bernilai Rp 0 dan pendapatan order tetap utuh")
        assert net == 0, f"Order income melampaui target, Net Payment harus Rp 0 tetapi tertulis Rp {net:,.0f}"
        assert act_pg.scroll_until_visible(act_pg.TEXT_GI_TOTAL_PAYMENT_ZERO), \
            "Keterangan 'Total Guarantee Payment tetap Rp0' tidak tampil"

    @pytest.mark.business_logic
    def test_TC_DRV_ACT_BL_03_penolakan_klaim_gi_jika_jam_online_kurang(self):
        """
        [BUSINESS LOGIC - BL-03]
        Deskripsi : Penolakan pencairan GI jika jam online kurang dari batas minimum operasional.
        Ekspektasi: Sistem membatalkan hak GI jika driver tidak 'Online di Jam Operasional'.
        """
        given("Driver hanya online selama 2 jam dari batas minimum shift 4 jam")
        when("Sistem melakukan evaluasi kualifikasi subsidi jaminan harian")
        then("Subsidi GI gugur karena tidak memenuhi syarat durasi operasional")
        pytest.skip("Evaluasi kualifikasi GI berjalan di batch backend setelah shift berakhir; durasi online "
                    "2 jam tidak bisa disusun dari UI dalam satu sesi test.")

    @pytest.mark.business_logic
    def test_TC_DRV_ACT_BL_04_penolakan_klaim_gi_saat_di_luar_working_area(self):
        """
        [BUSINESS LOGIC - BL-04]
        Deskripsi : Penolakan klaim GI saat status GPS terdeteksi di luar Working Area aktif.
        Ekspektasi: Muncul snackbar 'Manfaat Gurantee Income tidak berlaku di luar area'.
        """
        given("Driver berada di luar batas geofence operasional resmi")
        when("Driver mencoba mengakses klaim manfaat GI")
        then("Sistem menolak dan menampilkan peringatan batas wilayah kerja")
        pytest.skip("Butuh simulasi GPS di luar Working Area; koordinat geofence dev belum tersedia untuk automation.")

    @pytest.mark.business_logic
    def test_TC_DRV_ACT_BL_05_hangusnya_gi_saat_batas_waktu_kembali_area_habis(self):
        """
        [BUSINESS LOGIC - BL-05]
        Deskripsi : Hangusnya jaminan pendapatan saat batas waktu kembali ke area terlampaui.
        Ekspektasi: Status jaminan beralih ke diskualifikasi jika toleransi timer habis.
        """
        given("Timer sisa waktu kembali ke area telah mencapai batas 00:00")
        when("Driver belum kembali ke batas dalam zona GI")
        then("Hak jaminan pendapatan periode tersebut dinyatakan hangus")
        pytest.skip("Butuh driver keluar area GI setelah trip lalu menunggu timer kembali habis (simulasi GPS "
                    "+ trip nyata); tidak bisa disusun dari UI.")

    @pytest.mark.business_logic
    def test_TC_DRV_ACT_BL_06_validasi_pembagian_komisi_bersih_invoice_driver(self):
        """
        [BUSINESS LOGIC - BL-06]
        Deskripsi : Memvalidasi formula pembagian komisi bersih pada invoice pesanan driver.
        Formula   : Total Diterima Driver = Subtotal Argo - Platform Fee 10% + Waiting Fee + Subsidi Kupon.
        Ekspektasi: Nilai pendapatan bersih driver sinkron akurat antara invoice dan mutasi dompet.
        Catatan   : Diverifikasi di kalkulator invoice dua sisi (AdminDashboardFareCalculator),
                    tidak membutuhkan perangkat.
        """
        given("Pesanan rute 3.5 KM (Argo Rp 10.200) dengan Waiting Fee Rp 2.500 dan Kupon Rp 5.000")
        when("Sistem mengalkulasi Invoice Pendapatan Driver")
        invoice = AdminDashboardFareCalculator().generate_dual_side_invoice(
            distance_km=3.5, waiting_minutes=20, use_coupon=True, coupon_amount=5000.0
        )
        drv_inv = invoice["driver_invoice"]
        usr_inv = invoice["user_invoice"]
        then("Platform Fee 10% (Rp 1.020) terpotong dan subsidi kupon Rp 5.000 utuh diterima driver")
        assert drv_inv["fare_argo"] == 10200, f"Argo 3.5 KM harus Rp 10.200, hasil Rp {drv_inv['fare_argo']:,.0f}"
        assert usr_inv["waiting_fee"] == 2500, f"Waiting fee 20 menit harus Rp 2.500, hasil Rp {usr_inv['waiting_fee']:,.0f}"
        assert drv_inv["platform_fee_driver"] == 1020, \
            f"Platform fee driver harus 10% x Rp 10.200 = Rp 1.020, hasil Rp {drv_inv['platform_fee_driver']:,.0f}"
        assert drv_inv["coupon_subsidy"] == 5000, \
            f"Subsidi kupon untuk driver harus utuh Rp 5.000, hasil Rp {drv_inv['coupon_subsidy']:,.0f}"
        assert invoice["reconciliation"]["driver_protected_from_discount"] is True, \
            "Argo driver ikut terpotong kupon; seharusnya kupon ditanggung platform"

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - EMPTY STATES & FILTER BOUNDARIES
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_DRV_ACT_NT_01_empty_state_belum_ada_pendapatan_gi_hari_ini(self, driver_app):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi : Empty state 'Anda belum memiliki pendapatan Guarantee Income pada hari ini'.
        Ekspektasi: Tampilan informatif muncul saat driver baru memulai hari atau libur.
        """
        act_pg = self._buka_tab_gi(driver_app)

        given("Akun driver belum mencatatkan sesi kerja hari ini")
        if act_pg.has_gi_history_status_badge():
            pytest.skip("Akun driver uji sudah memiliki riwayat Guarantee Income; empty state tidak akan tampil.")
        when("Driver membuka tab Guarantee Income")
        then("Tampil ilustrasi dan teks 'Anda belum memiliki pendapatan Guarantee Income'")
        assert act_pg.is_gi_today_empty(), \
            "Tidak ada riwayat GI tetapi teks 'Anda belum memiliki pendapatan Guarantee Income pada hari ini' tidak tampil"

    @pytest.mark.negative_true
    def test_TC_DRV_ACT_NT_02_empty_state_belum_ada_riwayat_pendapatan(self, driver_app):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi : Empty state 'Belum Ada Riwayat' pada ringkasan pendapatan mitra baru.
        Ekspektasi: Menampilkan pesan 'Tidak ada riwayat pada bagian ini' secara rapi.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_revenue_tab()

        given("Akun driver baru belum pernah menyelesaikan transaksi perjalanan")
        if act_pg.has_revenue_ledger():
            pytest.skip("Akun driver uji sudah memiliki mutasi pendapatan; empty state tidak akan tampil.")
        when("Driver membuka tab Revenue Summary")
        then("Tampil empty state 'Belum Ada Riwayat'")
        assert act_pg.is_revenue_empty_state_displayed(), \
            "Tidak ada mutasi pendapatan tetapi empty state riwayat pendapatan tidak tampil"

    @pytest.mark.negative_true
    def test_TC_DRV_ACT_NT_03_empty_state_belum_ada_riwayat_referral(self, driver_app):
        """
        [NEGATIVE TRUE - NT-03]
        Deskripsi : Empty state 'Belum Ada Riwayat Referral' saat belum ada downline.
        Ekspektasi: Menampilkan ajakan 'Bagikan kode referral Anda untuk mulai mendapatkan komisi'.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_referral_tab()

        given("Driver belum mengajak rekan bergabung sebagai mitra")
        total_referral = act_pg.read_referral_total()
        if total_referral:
            pytest.skip(f"Akun driver uji sudah memiliki {total_referral} referral; empty state tidak akan tampil.")
        when("Driver membuka tab Referral Income")
        then("Tampil empty state 'Belum Ada Riwayat Referral' disertai ajakan berbagi")
        assert act_pg.scroll_until_visible(act_pg.EMPTY_STATE_REFERRAL), \
            "Belum ada referral tetapi empty state 'Belum Ada Riwayat Referral' tidak tampil"

    @pytest.mark.negative_true
    def test_TC_DRV_ACT_NT_04_filter_riwayat_rentang_tanggal_masa_depan(self):
        """
        [NEGATIVE TRUE - NT-04]
        Deskripsi : Filter riwayat dengan input rentang tanggal masa depan (invalid date range).
        Ekspektasi: Sistem memblokir pemilihan tanggal melebihi hari ini pada datepicker.
        """
        given("Driver membuka filter kalender tanggal riwayat pendapatan")
        when("Driver mencoba memilih tanggal di masa depan (tomorrow onwards)")
        then("Datepicker menonaktifkan seleksi tanggal masa depan")
        pytest.skip("Filter/datepicker tanggal di layar pendapatan belum terpetakan: strings APK tidak memuat "
                    "teks filter tanggal untuk layar ini, jadi tombol pembuka kalender belum bisa dilokasikan.")

    @pytest.mark.negative_true
    def test_TC_DRV_ACT_NT_05_akses_detail_transaksi_belum_tersedia(self):
        """
        [NEGATIVE TRUE - NT-05]
        Deskripsi : Akses detail transaksi yang datanya belum diproses tuntas oleh backend.
        Ekspektasi: Tampil snackbar 'Detail transaksi belum tersedia' tanpa membuat layar crash.
        """
        given("Terdapat rekonsiliasi yang masih dalam tahap batch processing")
        when("Driver mengetuk transaksi tersebut")
        then("Sistem menampilkan pesan 'Detail transaksi belum tersedia' secara aman")
        pytest.skip("Butuh transaksi yang sedang diproses batch backend pada saat test berjalan; "
                    "kondisi ini tidak bisa disusun dari UI.")

    @pytest.mark.negative_true
    def test_TC_DRV_ACT_NT_06_empty_state_riwayat_pesanan_belum_ada(self, driver_app):
        """
        [NEGATIVE TRUE - NT-06]
        Deskripsi : Memeriksa tampilan empty state 'Belum Ada Pesanan' saat mitra baru belum ada order.
        Ekspektasi: Tampil ilustrasi dan teks 'Belum Ada Pesanan' secara rapi dan informatif.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)
        act_pg.switch_to_pesanan_tab()

        given("Driver baru belum pernah menyelesaikan pesanan")
        if act_pg.has_order_history():
            pytest.skip("Akun driver uji sudah memiliki riwayat pesanan; empty state tidak akan tampil.")
        when("Driver membuka Tab Pesanan di Halaman Aktivitas")
        then("Tampil empty state 'Belum Ada Pesanan'")
        assert act_pg.is_pesanan_empty_state_displayed(), \
            "Tidak ada riwayat pesanan tetapi teks 'Belum Ada Pesanan' tidak tampil"

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - SECURITY, SPAMMING & ROBUSTNESS
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_DRV_ACT_NF_01_security_sqli_pada_kolom_pencarian_riwayat(self):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi : Injeksi payload SQL Injection pada kolom pencarian riwayat pendapatan.
        Ekspektasi: Input disanitasi ketat tanpa mengekspos error database internal.
        """
        given("Driver berada pada fitur pencarian nomor transaksi")
        when("Driver memasukkan query SQLi: ' OR '1'='1' --")
        then("Sistem mensanitasi input dan menampilkan 0 hasil tanpa crash")
        pytest.skip("Aplikasi Driver tidak memiliki kolom pencarian nomor transaksi di layar Aktivitas "
                    "(tidak ada di strings APK); skenario perlu dipindah ke API test riwayat.")

    @pytest.mark.negative_false
    def test_TC_DRV_ACT_NF_02_security_xss_pada_payload_referral_sharing(self):
        """
        [NEGATIVE FALSE - NF-02]
        Deskripsi : Injeksi payload script XSS pada pesan tautan referral sharing.
        Ekspektasi: Seluruh tag HTML/JavaScript di-escape menjadi teks biasa.
        """
        given("Driver memodifikasi teks referral dengan tag <script>alert(1)</script>")
        when("Teks dikirimkan melalui sistem sharing")
        then("Karakter khusus disanitasi tanpa eksekusi skrip berbahaya")
        pytest.skip("Teks berbagi referral dibuat aplikasi dan tidak bisa diubah driver; hasil escape hanya "
                    "terlihat di aplikasi penerima (perangkat/aplikasi lain).")

    @pytest.mark.negative_false
    def test_TC_DRV_ACT_NF_03_rapid_tab_switching_spamming_gi_revenue_referral(self, driver_app):
        """
        [NEGATIVE FALSE - NF-03]
        Deskripsi : Mengetuk tab GI, Pendapatan, dan Referral secara bergantian sangat cepat.
        Ekspektasi: State antarmuka stabil, request asinkronus dibatalkan rapi tanpa ANR.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)

        given("Driver berada pada layar Aktivitas Saya")
        when("Driver mengetuk tab navigasi secara beruntun dan cepat")
        act_pg.switch_to_gi_tab()
        act_pg.switch_to_revenue_tab()
        act_pg.switch_to_referral_tab()
        then("Aplikasi tetap responsif dan merender tab terakhir tanpa force close")
        assert act_pg.is_app_in_foreground(), "Aplikasi Driver tidak lagi di foreground (force close/ANR) setelah spam tab"
        assert not act_pg.is_error_screen_displayed(), "Layar error sistem muncul setelah perpindahan tab beruntun"
        assert act_pg.is_referral_income_displayed(), "Tab terakhir (Referral) tidak ter-render setelah perpindahan tab beruntun"

    @pytest.mark.negative_false
    def test_TC_DRV_ACT_NF_04_penanganan_lonjakan_sinyal_gps_jitter(self):
        """
        [NEGATIVE FALSE - NF-04]
        Deskripsi : Penanganan fluktuasi sinyal koordinat GPS (GPS jitter / lompatan lokasi).
        Ekspektasi: Sistem menerapkan kalman filtering agar status GI tidak flicker keluar masuk.
        """
        given("Sinyal GPS mengalami lompatan akurasi sesaat di batas geofence")
        when("Aplikasi mengevaluasi status batas wilayah")
        then("Damping delay aktif sehingga notifikasi status tetap konsisten")
        pytest.skip("Butuh rangkaian lokasi mock di sekitar batas geofence GI; koordinat area GI dev belum "
                    "tersedia untuk automation.")

    @pytest.mark.negative_false
    def test_TC_DRV_ACT_NF_05_resiliensi_koneksi_terputus_saat_muat_revenue(self, driver_app):
        """
        [NEGATIVE FALSE - NF-05]
        Deskripsi : Ketahanan aplikasi saat koneksi internet terputus saat memuat rincian pendapatan.
        Ekspektasi: Muncul tombol 'Muat Ulang' atau pesan jaringan tanpa layar putih/blank.
        """
        self._ensure_driver_on_activity(driver_app)
        act_pg = DrvActivityPage(driver_app)

        given("Koneksi data staging terputus sementara")
        if not act_pg.set_network_enabled(False):
            pytest.skip("Perangkat uji tidak mengizinkan Appium mematikan jaringan (mobile: setConnectivity).")
        try:
            when("Driver membuka tab Revenue Summary")
            act_pg.switch_to_revenue_tab()
            then("Aplikasi menampilkan placeholder offline dan tombol coba lagi")
            indikator_offline = act_pg.is_offline_indicator_displayed()
            app_hidup = act_pg.is_app_in_foreground()
        finally:
            # Jaringan selalu dipulihkan agar test berikutnya tidak ikut offline
            act_pg.set_network_enabled(True)
        assert app_hidup, "Aplikasi Driver tertutup/crash saat memuat pendapatan tanpa koneksi"
        assert indikator_offline, (
            "Saat offline tidak tampil pesan jaringan ('Tidak Ada Koneksi Internet' / 'Jaringan terputus') "
            "maupun tombol 'Muat Ulang' / 'Coba Lagi'")
