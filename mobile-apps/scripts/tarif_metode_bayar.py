"""
Tarif di layar Place Order aplikasi User per kategori jarak x metode bayar (staging, akun utama).
Pickup: kantor pusat (EVMOTO_TEST_PICKUP, default 'Ecgo Evmoto Wijaya'). Metode: Cash, Saldo EVMoto, OVO
(GoPay hanya bila tertaut). TIDAK menekan 'Pesan EVMoto': hanya membaca tarif lalu kembali.

Harapan = rumus Price Admin (User) yang dibaca langsung dari Admin, sesuai jam saat tarif dibaca (WIB), keputusan
user 16 Nov 2026: jam sibuk (peakTime) dan malam (nightTime) = tarif awal + (jarak - startKm) x peakMileage/nightMileage
tanpa tier jarak jauh; jam normal = mileageFee s/d farFrom1, lalu farFee per KM tiap pita sebagai pengganti mileageFee.
E-wallet: gross-up ceil(x * 100 / (100 - rate)), GoPay 2%, OVO 1,665%. Kolom 'mode_tarif' = sibuk / malam / normal.
Hasil: reports/repro/tarif_metode_bayar/NN_<kategori>_<metode>.xml|.png, hasil.tsv, ringkasan.txt
"""
import math
import os
from datetime import datetime, timedelta, timezone
import re
import sys
import time
import traceback
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("TARIF_POOL_INDEX", "0")  # 0 = akun utama (Saldo EVMoto + OVO)
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from Pages.booking_page import BookingPage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "tarif_metode_bayar"
PICKUP = os.getenv("EVMOTO_TEST_PICKUP", "Ecgo Evmoto Wijaya")
TIERS = [
    ("Dekat", 0.0, 1.99, ["Starbucks Wijaya", "Wijaya Grand Centre", "Pasar Santa"]),
    ("Sedang", 1.99, 6.0, ["Senayan City", "Gandaria City", "Pondok Indah Mall"]),
    ("Jauh", 6.0, 19.99, ["Plaza Indonesia", "Grand Indonesia", "TMII"]),
    ("Sangat Jauh", 19.99, 60.0, ["Bandara Soekarno Hatta", "Ancol", "Summarecon Mall Bekasi"]),
]
METODE = [("cash", "Cash", 0.0), ("wallet", "Saldo EVMoto", 0.0), ("ovo", "OVO", 1.665), ("gopay", "GoPay", 2.0)]
step = 0
ringkasan = []


_KALK = None


def kalkulator():
    """Kalkulator dengan angka Price Admin User environment aktif; bila Admin tidak terbaca, angka staging 16 Nov 2026."""
    global _KALK
    if _KALK is None:
        from Frontend.Feature.Helper.admin_fare_calculator import AdminDashboardFareCalculator as K
        try:
            _KALK = K.from_admin("User")
        except Exception as ex:  # noqa: BLE001 - Admin tidak terjangkau: pakai angka staging yang terakhir dibaca
            ringkasan.append(f"Admin tidak terbaca ({type(ex).__name__}); memakai angka Price User staging 16 Nov 2026")
            _KALK = K()
            _KALK.START_PRICE, _KALK.START_KM, _KALK.MILEAGE_FEE = 6000.0, 1.99, 2600.0
            _KALK.FAR_FROM_1, _KALK.FAR_TO_1, _KALK.FAR_FEE_1 = 6.0, 19.99, 3300.0
            _KALK.FAR_FROM_2, _KALK.FAR_TO_2, _KALK.FAR_FEE_2 = 19.99, 100.0, 3000.0
            _KALK.FAR_FROM_3, _KALK.FAR_FEE_3 = 100.0, 3500.0
            _KALK.PEAK_TIME, _KALK.PEAK_START, _KALK.PEAK_MILEAGE = "07:00 - 16:00", 6000.0, 2600.0
            _KALK.NIGHT_TIME, _KALK.NIGHT_START, _KALK.NIGHT_MILEAGE = "00:00 - 06:00", 10500.0, 3100.0
    return _KALK


def jam_wib():
    return datetime.now(timezone(timedelta(hours=7))).time()


def argo_admin(km):
    return kalkulator().calculate_base_argo(km, jam_wib())["total_argo"]


def mode_tarif():
    return kalkulator().mode_tarif(jam_wib())


def gross_up(x, rate):
    return float(math.ceil(x * 100.0 / (100.0 - rate))) if rate and x > 0 else x


def angka(s):
    d = re.sub(r"[^\d]", "", s or "")
    return int(d) if d else 0


def save(d, nama):
    global step
    step += 1
    izinkan_lokasi(d)
    xml = dump_ringan(d)
    base = OUT / f"{step:02d}_{nama}"
    base.with_suffix(".xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(base.with_suffix(".png")))
    return xml


def beranda(d):
    d.terminate_app(config.APP_PACKAGE)
    time.sleep(1)
    d.activate_app(config.APP_PACKAGE)
    time.sleep(5)
    izinkan_lokasi(d)
    for _ in range(2):
        els = d.find_elements("xpath", "//*[@content-desc='Lanjutkan' or @text='Lanjutkan']")
        if els:
            els[0].click()
            time.sleep(1.5)


def tunggu_overlay(d, detik=20):
    """Tunggu overlay merah 'PlatformException ... newLatLngBounds' di Place Order hilang (menahan ketukan)."""
    deadline = time.time() + detik
    while time.time() < deadline and d.find_elements(
            "xpath", "//*[starts-with(@content-desc,'PlatformException') or starts-with(@text,'PlatformException')]"):
        time.sleep(1)


def diskon(d):
    els = d.find_elements("xpath", "//*[starts-with(@content-desc,'Diskon') or starts-with(@content-desc,'Belum ada promosi')]")
    return (els[0].get_attribute("content-desc") or "").strip() if els else ""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = ["kategori\ttujuan\tjarak_km\tmetode_terpilih\tsebelum_kupon\tdibayar\tdiskon\tharapan_admin\tmode_tarif\tstatus"]
    d = DriverFactory.create_driver(no_reset=True)
    try:
        lp = LoginPage(d)
        phone = os.getenv(os.getenv("TARIF_PHONE_VAR", "") or "_", "") or config.ACTIVE_PHONE
        if lp.is_login_screen_displayed(timeout=20):
            lp.input_phone_number(phone)
            lp.click_submit_login()
            lp.input_otp_dev(config.ACTIVE_OTP)
            time.sleep(5)
        ringkasan.append(f"akun {phone[:4]}****{phone[-2:]}, pickup '{PICKUP}', perangkat emulator CI, tanpa menekan 'Pesan EVMoto'")
        for kategori, lo, hi, tujuan_list in TIERS:
            km = None
            for tujuan in tujuan_list:
                try:
                    beranda(d)
                except Exception as e:
                    if "instrumentation" in str(e) or "socket hang up" in str(e) or "proxy" in str(e):
                        ringkasan.append(f"{kategori}: UiAutomator2 berhenti, sesi dibuat ulang")
                        try:
                            d.quit()
                        except Exception:
                            pass
                        d = DriverFactory.create_driver(no_reset=True)
                        beranda(d)
                    else:
                        raise
                bp = BookingPage(d)
                try:
                    bp.open_place_order(tujuan, pickup=PICKUP)
                except Exception as e:
                    traceback.print_exc()
                    ringkasan.append(f"{kategori}: '{tujuan}' gagal dibuka ({type(e).__name__}: {str(e)[:120]})")
                    try:
                        save(d, f"{kategori.replace(' ', '_')}_gagal_buka")
                    except Exception:
                        pass
                    if "instrumentation" in str(e) or "socket hang up" in str(e) or "proxy" in str(e):
                        ringkasan.append(f"{kategori}: UiAutomator2 berhenti, sesi dibuat ulang")
                        try:
                            d.quit()
                        except Exception:
                            pass
                        d = DriverFactory.create_driver(no_reset=True)
                    continue
                # run 43200263018: rute + kartu tarif baru tampil beberapa detik setelah Place Order terbuka
                km = None
                batas = time.time() + 40
                while km is None and time.time() < batas:
                    tunggu_overlay(d, 10)
                    km = bp.get_trip_distance_km()
                if km is None:
                    save(d, f"{kategori.replace(' ', '_')}_jarak_tak_terbaca")
                if km is not None and lo < km <= hi:
                    break
                ringkasan.append(f"{kategori}: '{tujuan}' jarak {km} km di luar rentang {lo}-{hi}")
                km = None
            if km is None:
                rows.append(f"{kategori}\t-\t-\t-\t-\t-\t-\t-\t-\ttujuan dalam rentang tidak ditemukan")
                continue
            for kode, nama, rate in METODE:
                try:
                    try:
                        tunggu_overlay(d)
                        bp.select_payment_method(kode)
                    except Exception:
                        # run 43197232012: ketukan pertama ke chip metode bayar tertahan overlay PlatformException
                        tunggu_overlay(d)
                        bp.select_payment_method(kode)
                    time.sleep(3)
                except Exception as e:
                    rows.append(f"{kategori}\t{tujuan}\t{km}\t{nama}\t-\t-\t-\t-\t-\ttidak bisa dipilih: {str(e)[:90]}")
                    save(d, f"{kategori.replace(' ', '_')}_{nama.replace(' ', '_')}_gagal")
                    try:
                        if d.find_elements(*bp.TITLE_PAYMENT_METHOD_SCREEN):
                            bp.click(bp.BTN_BACK, label="Back")
                            time.sleep(1)
                    except Exception:
                        pass
                    continue
                save(d, f"{kategori.replace(' ', '_')}_{nama.replace(' ', '_')}")
                terpilih = bp.get_selected_payment_method()
                sebelum, bayar = angka(bp.get_fare_before_discount()), angka(bp.get_estimated_fare())
                disk = diskon(d)
                harap = gross_up(argo_admin(km), rate)
                mode = mode_tarif()
                # jarak di layar dibulatkan 2 desimal: toleransi +-0,005 km
                lo_h = gross_up(argo_admin(km - 0.005), rate) - 1
                hi_h = gross_up(argo_admin(km + 0.005), rate) + 1
                if terpilih != nama:
                    status = f"metode di layar '{terpilih}', bukan {nama}"
                elif lo_h <= sebelum <= hi_h:
                    status = "SESUAI"
                else:
                    status = f"BERBEDA dari rumus (selisih {sebelum - harap:,.0f}; belum diverifikasi, bukan otomatis bug)"
                rows.append(f"{kategori}\t{tujuan}\t{km}\t{terpilih}\t{sebelum}\t{bayar}\t{disk}\t{harap:.0f}\t{mode}\t{status}")
                log(rows[-1])
        # kembalikan pilihan ke OVO (metode utama akun ini sebelum test)
        try:
            bp.select_payment_method("ovo")
        except Exception:
            pass
    except Exception as e:
        traceback.print_exc()
        ringkasan.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            save(d, "saat_error")
        except Exception:
            pass
    finally:
        (OUT / "hasil.tsv").write_text("\n".join(rows), encoding="utf-8")
        text = "\n".join(ringkasan + rows)
        (OUT / "ringkasan.txt").write_text(re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", text), encoding="utf-8")
        print(text)
        try:
            d.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
