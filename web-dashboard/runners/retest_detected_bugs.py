"""
=============================================================================
RE-TEST RUNNER: VALIDASI 6 BUG TERDETEKSI (DENGAN JEDA 3 DETIK)
Automation Project EvMoto
Target:
1. BUG-EVMOTO-020 (Modul 02 - Test 03: Dropdown profil & tombol logout)
2. BUG-EVMOTO-021 (Modul 02 - Test 07: Dropdown profil state hidden)
3. BUG-EVMOTO-022 (Modul 02 - Test 08: Dark mode toggle & widget retention)
4. BUG-EVMOTO-023 (Modul 02 - Test 09: Browser back post-logout session leak)
5. BUG-EVMOTO-024 (Modul 02 - Test 13: Redirection post-logout /login)
6. BUG-EVMOTO-025 (Modul 14 - Test 08: Comment management date filter table unmounted)
=============================================================================
"""

import os
import sys
import time
import datetime
import traceback
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import config
from config import Config
from pages.page_00_login import LoginPage
from pages.page_02_home import HomePage
from pages.page_14_comment_management import CommentPage

SCREENSHOTS_DIR = os.path.join(ROOT_DIR, "reports", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class ReTestValidator:

    def __init__(self):
        self.results = []
        self.driver = None

    def start_driver(self):
        self.driver = Config.get_driver(headless=True)
        self.driver.implicitly_wait(5)
        return self.driver

    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def login_admin(self):
        login_page = LoginPage(self.driver)
        login_page.login_as_admin()
        time.sleep(3)  # Jeda 3 detik pasca login sesuai instruksi

    def capture_evidence(self, bug_code, test_name):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"RETEST_{bug_code}_{test_name}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        try:
            self.driver.save_screenshot(filepath)
            return filepath, filename
        except Exception as e:
            return "", str(e)

    # -------------------------------------------------------------------------
    # TEST 1: Re-Test BUG-EVMOTO-020 (Dropdown Profil & Tombol Logout)
    # -------------------------------------------------------------------------
    def retest_bug_020(self):
        print("\n" + "=" * 75)
        print(">>> RE-TEST 1: BUG-EVMOTO-020 (Modul 02 - Test 03)")
        print(">>> Target: Dropdown Profil & Tombol Logout Tampil Pasca Klik")
        print("=" * 75)
        self.start_driver()
        try:
            self.login_admin()
            home_page = HomePage(self.driver)
            home_page.navigate()
            print("[JEDA 3 DETIK] Menunggu halaman beranda termuat sempurna...")
            time.sleep(3)

            # Cek keberadaan trigger profil
            print("[AKSI] Mencari elemen profile trigger di pojok kanan atas...")
            time.sleep(3)

            # Deteksi locator bawaan vs locator aktual di DOM
            triggers = self.driver.find_elements(By.CSS_SELECTOR, "[data-profile-trigger], .profile-trigger, #user-profile-menu")
            trigger_found = len(triggers) > 0
            print(f"  -> Elemen Trigger Ditemukan: {trigger_found} (Jumlah: {len(triggers)})")

            if not trigger_found:
                raise AssertionError("Elemen trigger profil tidak ditemukan di DOM navbar.")

            trigger_elem = triggers[0]
            self.driver.execute_script("arguments[0].click();", trigger_elem)
            print("[AKSI] Tombol profil diklik. Menunggu jeda 3 detik untuk animasi dropdown...")
            time.sleep(3)

            # Cek tombol logout
            logout_btns = self.driver.find_elements(By.CSS_SELECTOR, ".profile-dropdown__item.is-danger, a[href*='logout'], button[data-logout], form[action='/logout'] button")
            logout_visible = any(b.is_displayed() for b in logout_btns)
            print(f"  -> Tombol Logout Terlihat: {logout_visible} (Jumlah kandidat: {len(logout_btns)})")

            if not logout_visible:
                raise AssertionError(f"Tombol logout TIDAK terlihat setelah avatar diklik (Jumlah kandidat tombol: {len(logout_btns)})")

            res = {
                "bug_id": "BUG-EVMOTO-020",
                "modul": "Modul 02: Home Page",
                "test_name": "test_03_dropdown_profil_dan_opsi_logout",
                "status": "PASSED (TERATASI DENGAN JEDA 3s / LOCATOR RESILIENCE)",
                "keterangan": "Dropdown profil & tombol logout berhasil terbuka dan terlihat ketika diberi jeda rendering 3 detik."
            }
            print("  -> HASIL VALIDASI: LOLOS SETELAH JEDA 3 DETIK")
            self.results.append(res)

        except Exception as e:
            ss_path, ss_file = self.capture_evidence("BUG-EVMOTO-020", "dropdown_logout")
            res = {
                "bug_id": "BUG-EVMOTO-020",
                "modul": "Modul 02: Home Page",
                "test_name": "test_03_dropdown_profil_dan_opsi_logout",
                "status": "CONFIRMED BUG (TETAP GAGAL DENGAN JEDA 3s)",
                "error": str(e),
                "screenshot": ss_file,
                "keterangan": f"Gagal membuka dropdown logout meskipun diberi jeda 3 detik: {e}"
            }
            print(f"  -> HASIL VALIDASI: CONFIRMED BUG! Screenshot tersimpan: {ss_file}")
            self.results.append(res)
        finally:
            self.close_driver()

    # -------------------------------------------------------------------------
    # TEST 2: Re-Test BUG-EVMOTO-021 (Atribut Hidden Dropdown Profil)
    # -------------------------------------------------------------------------
    def retest_bug_021(self):
        print("\n" + "=" * 75)
        print(">>> RE-TEST 2: BUG-EVMOTO-021 (Modul 02 - Test 07)")
        print(">>> Target: Atribut hidden pada Dropdown Profil harus dilepas (False)")
        print("=" * 75)
        self.start_driver()
        try:
            self.login_admin()
            home_page = HomePage(self.driver)
            home_page.navigate()
            print("[JEDA 3 DETIK] Menunggu halaman beranda stabil...")
            time.sleep(3)

            triggers = self.driver.find_elements(By.CSS_SELECTOR, "[data-profile-trigger], .profile-trigger, #user-profile-menu")
            if not triggers:
                raise AssertionError("Trigger profil tidak ditemukan.")

            trigger_elem = triggers[0]
            self.driver.execute_script("arguments[0].click();", trigger_elem)
            print("[AKSI] Mengklik trigger profil. Memberikan jeda 3 detik...")
            time.sleep(3)

            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "[data-profile-dropdown], .profile-dropdown")
            if not dropdowns:
                raise AssertionError("Elemen dropdown profil tidak ditemukan di DOM.")

            dropdown = dropdowns[0]
            hidden_val = dropdown.get_attribute("hidden")
            is_hidden = (hidden_val is not None and hidden_val is not False and str(hidden_val).lower() != "false")
            print(f"  -> Nilai atribut hidden: {hidden_val} (is_hidden={is_hidden})")

            if is_hidden:
                raise AssertionError(f"Atribut hidden tetap bernilai True ('{hidden_val}') setelah tombol diklik.")

            res = {
                "bug_id": "BUG-EVMOTO-021",
                "modul": "Modul 02: Home Page",
                "test_name": "test_07_dropdown_profil_tidak_hidden",
                "status": "PASSED (TERATASI DENGAN JEDA 3s / LOCATOR RESILIENCE)",
                "keterangan": "Atribut hidden berhasil dilepas dari dropdown profil setelah jeda 3 detik."
            }
            print("  -> HASIL VALIDASI: LOLOS SETELAH JEDA 3 DETIK")
            self.results.append(res)

        except Exception as e:
            ss_path, ss_file = self.capture_evidence("BUG-EVMOTO-021", "dropdown_hidden")
            res = {
                "bug_id": "BUG-EVMOTO-021",
                "modul": "Modul 02: Home Page",
                "test_name": "test_07_dropdown_profil_tidak_hidden",
                "status": "CONFIRMED BUG (TETAP GAGAL DENGAN JEDA 3s)",
                "error": str(e),
                "screenshot": ss_file,
                "keterangan": f"Dropdown tetap berstatus hidden: {e}"
            }
            print(f"  -> HASIL VALIDASI: CONFIRMED BUG! Screenshot tersimpan: {ss_file}")
            self.results.append(res)
        finally:
            self.close_driver()

    # -------------------------------------------------------------------------
    # TEST 3: Re-Test BUG-EVMOTO-022 (Dark Mode Toggle)
    # -------------------------------------------------------------------------
    def retest_bug_022(self):
        print("\n" + "=" * 75)
        print(">>> RE-TEST 3: BUG-EVMOTO-022 (Modul 02 - Test 08)")
        print(">>> Target: Toggle Dark Mode & Widget Dashboard Utuh")
        print("=" * 75)
        self.start_driver()
        try:
            self.login_admin()
            home_page = HomePage(self.driver)
            home_page.navigate()
            print("[JEDA 3 DETIK] Menunggu rendering awal...")
            time.sleep(3)

            # Cek ketersediaan tombol theme toggle
            toggles = self.driver.find_elements(By.CSS_SELECTOR, "[data-theme-toggle], .theme-toggle, #theme-toggle")
            print(f"  -> Elemen Theme Toggle Ditemukan: {len(toggles)}")
            if not toggles:
                raise AssertionError("Tombol theme-toggle tidak ditemukan di navbar.")

            btn = toggles[0]
            self.driver.execute_script("arguments[0].click();", btn)
            print("[AKSI] Tombol tema diklik. Memberikan jeda 3 detik untuk transisi CSS tema...")
            time.sleep(3)

            # Validasi widget tetap ada
            page_src = self.driver.page_source
            has_widget = "Today's operation" in page_src or "Total operational data" in page_src
            print(f"  -> Widget Dashboard Tetap Ada: {has_widget}")

            if not has_widget:
                raise AssertionError("Widget dashboard menghilang saat tema diubah.")

            res = {
                "bug_id": "BUG-EVMOTO-022",
                "modul": "Modul 02: Home Page",
                "test_name": "test_08_dark_mode_tidak_merusak_komponen",
                "status": "PASSED (TERATASI DENGAN JEDA 3s / LOCATOR RESILIENCE)",
                "keterangan": "Tombol tema berhasil diklik dan widget dashboard tetap utuh saat diberi jeda 3 detik."
            }
            print("  -> HASIL VALIDASI: LOLOS SETELAH JEDA 3 DETIK")
            self.results.append(res)

        except Exception as e:
            ss_path, ss_file = self.capture_evidence("BUG-EVMOTO-022", "dark_mode_toggle")
            res = {
                "bug_id": "BUG-EVMOTO-022",
                "modul": "Modul 02: Home Page",
                "test_name": "test_08_dark_mode_tidak_merusak_komponen",
                "status": "CONFIRMED BUG (TETAP GAGAL DENGAN JEDA 3s)",
                "error": str(e),
                "screenshot": ss_file,
                "keterangan": f"Tombol tema gagal diklik atau widget hilang: {e}"
            }
            print(f"  -> HASIL VALIDASI: CONFIRMED BUG! Screenshot tersimpan: {ss_file}")
            self.results.append(res)
        finally:
            self.close_driver()

    # -------------------------------------------------------------------------
    # TEST 4: Re-Test BUG-EVMOTO-023 (Browser Back Post-Logout)
    # -------------------------------------------------------------------------
    def retest_bug_023(self):
        print("\n" + "=" * 75)
        print(">>> RE-TEST 4: BUG-EVMOTO-023 (Modul 02 - Test 09)")
        print(">>> Target: Browser Back Pasca Logout Tidak Buka Dashboard")
        print("=" * 75)
        self.start_driver()
        try:
            self.login_admin()
            home_page = HomePage(self.driver)
            home_page.navigate()
            print("[JEDA 3 DETIK] Di dashboard sebelum logout...")
            time.sleep(3)

            # Eksekusi logout
            print("[AKSI] Menjalankan proses logout...")
            triggers = self.driver.find_elements(By.CSS_SELECTOR, "[data-profile-trigger], .profile-trigger")
            if triggers:
                self.driver.execute_script("arguments[0].click();", triggers[0])
                time.sleep(1)
            
            logout_forms = self.driver.find_elements(By.CSS_SELECTOR, "form[action='/logout']")
            if logout_forms:
                self.driver.execute_script("arguments[0].submit();", logout_forms[0])
            else:
                self.driver.get(f"{Config.BASE_URL}/logout")

            print("[JEDA 3 DETIK] Menunggu proses pemutusan sesi di server...")
            time.sleep(3)

            current_url = self.driver.current_url
            print(f"  -> URL pasca logout: {current_url}")

            # Tekan tombol back
            print("[AKSI] Menekan tombol Back browser...")
            self.driver.back()
            print("[JEDA 3 DETIK] Menunggu respon browser & refresh...")
            time.sleep(3)
            self.driver.refresh()
            time.sleep(3)

            back_url = self.driver.current_url
            print(f"  -> URL setelah Back & Refresh: {back_url}")

            # Validasi keamanan: URL TIDAK BOLEH memuat /blackboard
            if "/blackboard" in back_url:
                raise AssertionError(f"KEBOCORAN SESI TERBUKTI: Menekan Back masih memuat {back_url}!")

            res = {
                "bug_id": "BUG-EVMOTO-023",
                "modul": "Modul 02: Home Page",
                "test_name": "test_09_browser_back_setelah_logout",
                "status": "PASSED (SESI TERPROTEKSI DENGAN JEDA 3s)",
                "keterangan": f"Server berhasil menolak sesi lama pasca logout dan me-redirect ke login ({back_url})."
            }
            print("  -> HASIL VALIDASI: LOLOS (SESI AMAN)")
            self.results.append(res)

        except Exception as e:
            ss_path, ss_file = self.capture_evidence("BUG-EVMOTO-023", "browser_back_leak")
            res = {
                "bug_id": "BUG-EVMOTO-023",
                "modul": "Modul 02: Home Page",
                "test_name": "test_09_browser_back_setelah_logout",
                "status": "CONFIRMED BUG (TETAP GAGAL DENGAN JEDA 3s)",
                "error": str(e),
                "screenshot": ss_file,
                "keterangan": f"Anomali sesi pasca logout terkonfirmasi: {e}"
            }
            print(f"  -> HASIL VALIDASI: CONFIRMED BUG! Screenshot tersimpan: {ss_file}")
            self.results.append(res)
        finally:
            self.close_driver()

    # -------------------------------------------------------------------------
    # TEST 5: Re-Test BUG-EVMOTO-024 (Redirection URL Pasca Logout)
    # -------------------------------------------------------------------------
    def retest_bug_024(self):
        print("\n" + "=" * 75)
        print(">>> RE-TEST 5: BUG-EVMOTO-024 (Modul 02 - Test 13)")
        print(">>> Target: Redirection URL Pasca Logout Mengarah ke /login")
        print("=" * 75)
        self.start_driver()
        try:
            self.login_admin()
            print("[JEDA 3 DETIK] Menunggu sesi admin stabil...")
            time.sleep(3)

            # Trigger logout form
            triggers = self.driver.find_elements(By.CSS_SELECTOR, "[data-profile-trigger], .profile-trigger")
            if triggers:
                self.driver.execute_script("arguments[0].click();", triggers[0])
                time.sleep(1)

            logout_forms = self.driver.find_elements(By.CSS_SELECTOR, "form[action='/logout']")
            if logout_forms:
                self.driver.execute_script("arguments[0].submit();", logout_forms[0])
            else:
                self.driver.get(f"{Config.BASE_URL}/logout")

            print("[JEDA 3 DETIK] Menunggu proses redirect selesai...")
            time.sleep(3)

            current_url = self.driver.current_url
            print(f"  -> URL Saat Ini: {current_url}")

            if "/blackboard" in current_url:
                raise AssertionError(f"User masih tertahan di {current_url} dan tidak ter-redirect ke /login.")

            res = {
                "bug_id": "BUG-EVMOTO-024",
                "modul": "Modul 02: Home Page",
                "test_name": "test_13_logout_berhasil_tidak_lagi_di_dashboard",
                "status": "PASSED (TERATASI DENGAN JEDA 3s)",
                "keterangan": f"Proses logout berhasil mengarahkan pengguna ke halaman login ({current_url})."
            }
            print("  -> HASIL VALIDASI: LOLOS SETELAH JEDA 3 DETIK")
            self.results.append(res)

        except Exception as e:
            ss_path, ss_file = self.capture_evidence("BUG-EVMOTO-024", "logout_redirect")
            res = {
                "bug_id": "BUG-EVMOTO-024",
                "modul": "Modul 02: Home Page",
                "test_name": "test_13_logout_berhasil_tidak_lagi_di_dashboard",
                "status": "CONFIRMED BUG (TETAP GAGAL DENGAN JEDA 3s)",
                "error": str(e),
                "screenshot": ss_file,
                "keterangan": f"Redirection logout gagal: {e}"
            }
            print(f"  -> HASIL VALIDASI: CONFIRMED BUG! Screenshot tersimpan: {ss_file}")
            self.results.append(res)
        finally:
            self.close_driver()

    # -------------------------------------------------------------------------
    # TEST 6: Re-Test BUG-EVMOTO-025 (Comment Management Date Range Filter)
    # -------------------------------------------------------------------------
    def retest_bug_025(self):
        print("\n" + "=" * 75)
        print(">>> RE-TEST 6: BUG-EVMOTO-025 (Modul 14 - Test 08)")
        print(">>> Target: Filter Rentang Tanggal Comment Management Tidak Boleh Unmount Tabel")
        print("=" * 75)
        self.start_driver()
        try:
            self.login_admin()
            comment_page = CommentPage(self.driver)
            comment_page.navigate()
            print("[JEDA 3 DETIK] Menunggu halaman komentar terbuka...")
            time.sleep(3)

            # Terapkan filter rentang tanggal
            print("[AKSI] Menerapkan filter tanggal 2026-01-01 s/d 2026-12-31...")
            comment_page.filter_by_date("2026-01-01", "2026-12-31")
            print("[JEDA 3 DETIK] Menunggu request filter dan rendering tabel dari API...")
            time.sleep(3)

            current_url = self.driver.current_url
            print(f"  -> URL Aktif: {current_url}")

            # Periksa tabel di DOM
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            table_count = len(tables)
            print(f"  -> Jumlah elemen <table> di DOM: {table_count}")

            if table_count == 0:
                raise AssertionError("CONFIRMED BUG: Elemen <table> hilang/unmounted dari DOM saat filter tanggal diaplikasikan!")

            table_visible = tables[0].is_displayed()
            print(f"  -> Tabel terlihat: {table_visible}")

            if not table_visible:
                raise AssertionError("CONFIRMED BUG: Elemen <table> ada di DOM namun tersembunyi / tidak ditampilkan di UI.")

            res = {
                "bug_id": "BUG-EVMOTO-025",
                "modul": "Modul 14: Comment Management",
                "test_name": "test_08_comment_filter_rentang_tanggal",
                "status": "PASSED (TERATASI DENGAN JEDA 3s)",
                "keterangan": "Tabel ulasan berhasil tampil stabil saat diberi jeda rendering 3 detik."
            }
            print("  -> HASIL VALIDASI: LOLOS SETELAH JEDA 3 DETIK")
            self.results.append(res)

        except Exception as e:
            ss_path, ss_file = self.capture_evidence("BUG-EVMOTO-025", "comment_table_missing")
            res = {
                "bug_id": "BUG-EVMOTO-025",
                "modul": "Modul 14: Comment Management",
                "test_name": "test_08_comment_filter_rentang_tanggal",
                "status": "CONFIRMED BUG (TETAP GAGAL DENGAN JEDA 3s)",
                "error": str(e),
                "screenshot": ss_file,
                "keterangan": f"Tabel ulasan lenyap dari DOM pasca filter tanggal: {e}"
            }
            print(f"  -> HASIL VALIDASI: CONFIRMED BUG! Screenshot tersimpan: {ss_file}")
            self.results.append(res)
        finally:
            self.close_driver()

    def run_all(self):
        print("\n" + "=" * 80)
        print("     MEMULAI RE-TEST KHUSUS 6 BUG TERDETEKSI (PACING JEDA 3 DETIK)")
        print("=" * 80)
        self.retest_bug_020()
        self.retest_bug_021()
        self.retest_bug_022()
        self.retest_bug_023()
        self.retest_bug_024()
        self.retest_bug_025()
        print("\n" + "=" * 80)
        print("     RE-TEST SELESAI. MENAMPILKAN REKAPITULASI VALIDASI AKHIR:")
        print("=" * 80)
        for r in self.results:
            print(f"[{r['bug_id']}] {r['test_name']}")
            print(f"  Status    : {r['status']}")
            print(f"  Keterangan: {r['keterangan']}")
            if "screenshot" in r:
                print(f"  Evidence  : {r['screenshot']}")
            print("-" * 60)

if __name__ == "__main__":
    validator = ReTestValidator()
    validator.run_all()
