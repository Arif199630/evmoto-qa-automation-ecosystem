"""Bantuan bersama untuk skrip diagnosa/reproduksi (scripts/*.py) di emulator CI."""
import time

PERMISSION_ALLOW = (
    "//*[@text='Saat aplikasi digunakan' or @text='While using the app' or "
    "@text='Hanya kali ini' or @text='Only this time' or @text='Izinkan' or @text='Allow']"
)


def izinkan_lokasi(driver) -> bool:
    """Ketuk 'Saat aplikasi digunakan' bila dialog izin lokasi Android tampil. True bila dialog ditangani."""
    els = driver.find_elements("xpath", PERMISSION_ALLOW)
    if els:
        els[0].click()
        time.sleep(1)
        return True
    return False


def buka_aplikasi_bersih(driver, package: str):
    """Hapus data aplikasi (keluar dari akun), beri ulang izin lokasi, lalu buka aplikasi sampai tampil di depan.

    Menghapus data aplikasi ikut mencabut izin runtime, sehingga dialog izin lokasi Android akan menutupi layar
    (bukti diag 12 Nov 2026). Izin diberikan lagi lewat Appium; bila gagal, dialognya diketuk saat muncul.
    """
    driver.execute_script("mobile: clearApp", {"appId": package})
    time.sleep(1)
    try:
        driver.execute_script("mobile: changePermissions", {
            "permissions": ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"],
            "appPackage": package, "action": "grant",
        })
    except Exception as e:
        print(f"[diag] izin lokasi tidak bisa diberikan lewat Appium ({type(e).__name__}); dialog akan diketuk", flush=True)
    for _ in range(3):
        driver.activate_app(package)
        deadline = time.time() + 15
        while time.time() < deadline:
            if driver.query_app_state(package) == 4:  # 4 = berjalan di depan
                time.sleep(2)
                izinkan_lokasi(driver)
                return
            time.sleep(1)
    raise RuntimeError(f"Aplikasi {package} tidak tampil di depan setelah 3 kali dibuka")


def log(msg: str):
    print(f"[diag {time.strftime('%H:%M:%S')}] {msg}", flush=True)


ISI_LAYAR = ("//*[(string-length(@content-desc)>0 and not(starts-with(@content-desc,'Ping')) "
             "and not(starts-with(@content-desc,'PlatformException'))) or string-length(@text)>0 "
             "or contains(@class,'EditText')]")


def _layar_terbaca(driver, detik):
    deadline = time.time() + detik
    while time.time() < deadline:
        izinkan_lokasi(driver)
        if len(driver.find_elements("xpath", ISI_LAYAR)) >= 2:
            return True
        time.sleep(2)
    return False


def pindah_app(driver, package, udid=None, system_port=None):
    """Bawa aplikasi `package` ke depan dan pastikan isi layarnya terbaca. Mengembalikan driver yang dipakai.

    Bukti run 43180690535: setelah activate_app dari sesi aplikasi Driver, layar login aplikasi User hanya
    terbaca sebagai overlay 'Ping : Disconnected'. Urutannya: aktifkan + enableMultiWindows; bila tetap kosong,
    sesi ditutup dan dibuat ulang untuk aplikasi itu dengan noReset (data dan login aplikasi tidak dihapus).
    """
    driver.activate_app(package)
    time.sleep(3)
    try:
        driver.update_settings({"enableMultiWindows": True})
    except Exception:
        pass
    if _layar_terbaca(driver, 30):
        return driver
    log(f"isi layar {package} tidak terbaca, sesi dibuat ulang (noReset)")
    from config import config
    from core.driver_factory import DriverFactory
    try:
        driver.quit()
    except Exception:
        pass
    is_driver_app = package != config.APP_PACKAGE
    baru = DriverFactory.create_driver(no_reset=True, is_driver_app=is_driver_app, udid=udid, system_port=system_port)
    baru.activate_app(package)
    _layar_terbaca(baru, 40)
    return baru
