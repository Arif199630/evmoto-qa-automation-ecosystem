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
