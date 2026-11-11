"""
Inventaris validitas test: berapa test yang benar-benar memeriksa sistem EvMoto.

Pemakaian: python test_inventory.py            (ringkasan)
           python test_inventory.py --detail   (daftar test per kategori)

Aturan (keputusan 11 Nov 2026):
  VALID
    - ui_aplikasi   : test layar Admin/Mobile dengan assertion yang bisa gagal
    - http_staging  : test yang memanggil backend/Admin staging lewat HTTP
    - mock          : test API ke mock untuk endpoint yang belum ada di staging (dev/staging boleh pakai mock)
  BELUM VALID
    - placeholder   : hanya `assert True  # TODO(QA)`
    - tanpa_assert  : menjalankan langkah tanpa memeriksa hasil
    - simulator     : hanya menguji simulator/kalkulator Python, tidak menyentuh aplikasi atau backend
    - logika_lokal  : memeriksa nilai yang ditulis test itu sendiri (tidak memanggil aplikasi/backend)
    - skip          : sengaja di-skip dengan alasan (tidak dihitung lulus/gagal)
Klasifikasi dibaca dari kode (statis); hasil lulus/gagal ada di laporan run.
"""
import ast
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ADMIN = ROOT / "web-dashboard" if (ROOT / "web-dashboard").exists() else ROOT / "Automation_Project_EvMoto"
MOBILE = ROOT / "mobile-apps" if (ROOT / "mobile-apps").exists() else ROOT / "evmoto-user-mobile-automation"
CROSS = re.compile(r"^test_(admin_|dispatch_|drv_batch_|e2e_|drv_order_hall)")
UI_FIXTURES = {"driver", "driver_app", "authenticated_home", "booking_page", "tracking_page", "logged_in_home"}
HTTP_FIXTURES = {"admin_helper", "admin_rush_helper", "evmoto_client", "ecgo_client", "authenticated_driver_session",
                 "authenticated_user_session", "authenticated_ecgo_session", "actors", "record_property"}
SIM_FIXTURES = {"driver_sim", "pool_sim", "sim_3band", "driver_simulator", "fare_calculator"}
VALID = ("ui_aplikasi", "http_staging", "mock")

# Test API yang dijalankan ke mock bila USE_MOCK_SERVICES=1 (lihat api-testing/mock_layanan.py)
MOCK_FILES = {"test_new_features_api.py", "test_ecgo_connect_integrated_suite.py", "test_ecgo_swap_api.py"}
MOCK_TESTS = {"test_tc_api_usr_02_fare_estimation", "test_tc_api_usr_03_create_booking_order",
              "test_tc_api_usr_04_cancel_booking_order"}


def real_asserts(body):
    lines = [l for l in body.splitlines() if re.match(r"\s*(assert\b|self\.assert\w+\(|with pytest\.raises\()", l)]
    return [l for l in lines if "TODO(QA)" not in l and not re.match(r"\s*assert\s+True\b", l)
            and "assertTrue(True" not in l]


def classify(path, func, body, suite):
    args = {a.arg for a in func.args.args} - {"self"}
    if re.search(r"^\s*(pytest\.skip|self\.skipTest)\(", body, re.M) and not real_asserts(body):
        return "skip"
    if not real_asserts(body):
        return "placeholder" if "TODO(QA)" in body else "tanpa_assert"
    if suite == "admin":
        return "ui_aplikasi"
    if suite == "api":
        if path.name in MOCK_FILES or func.name in MOCK_TESTS:
            return "mock"
        return "http_staging"
    uses_ui = bool(args & UI_FIXTURES) or "self.driver" in body or re.search(r"\w+_page\.\w+\(", body)
    if uses_ui:
        return "ui_aplikasi"
    if args & HTTP_FIXTURES:
        return "http_staging"
    if args & SIM_FIXTURES or re.search(r"[Ss]imulator|AdminDashboardFareCalculator|calculate_", body):
        return "simulator"
    # Assertion hanya pada nilai yang ditulis test itu sendiri: tidak menguji sistem
    return "simulator" if suite == "cross" else "logika_lokal"


def scan():
    rows = []
    sources = [("admin", ADMIN / "Frontend/Feature/Step_Definition"), ("api", MOBILE / "api-testing/suites"),
               ("mobile", MOBILE / "Frontend/Feature/Step_Definition")]
    for suite, folder in sources:
        for path in sorted(folder.glob("test_*.py")):
            text = path.read_text(encoding="utf-8-sig")
            lines = text.splitlines()
            real_suite = "cross" if suite == "mobile" and CROSS.match(path.stem) else suite
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                    body = "\n".join(lines[node.lineno - 1:node.end_lineno])
                    rows.append((real_suite, path.name, node.name, classify(path, node, body, real_suite)))
    return rows


def main():
    rows = scan()
    by_suite = defaultdict(Counter)
    for suite, _, _, cat in rows:
        by_suite[suite][cat] += 1
    total = sum(sum(c.values()) for c in by_suite.values())
    valid = sum(c[k] for c in by_suite.values() for k in VALID)
    print(f"Total test: {total} | VALID: {valid} ({100 * valid / total:.1f}%) | belum valid: {total - valid}")
    for suite in ("admin", "api", "mobile", "cross"):
        c = by_suite[suite]
        v = sum(c[k] for k in VALID)
        print(f"  {suite:7} total {sum(c.values()):4} | valid {v:4} | " + ", ".join(f"{k}={n}" for k, n in sorted(c.items())))
    if "--detail" in sys.argv:
        for suite, file, name, cat in rows:
            if cat not in VALID:
                print(f"{cat:13} {suite:7} {file}::{name}")


if __name__ == "__main__":
    main()
