"""
================================================================================
EVMOTO MASTER RUNNER: RUSH HOUR DRIVER SUBSIDY E2E & REGRESSION TEST SUITE
================================================================================
Menjalankan pengujian terintegrasi secara otomatis via subprocess terisolasi:
  1. Web Dashboard Admin UI & API Suite (Settings & History): 9 Test Cases
  2. Mobile Apps Driver & User Pricing Engine Suite: 9 Test Cases
  3. 4-Pillars QA Suite (Fungsionalitas, Batas, Performa, Keamanan): 18 Test Cases
  4. Full Ecosystem Regression Suite (Auth, Wallet, Swap, User, Driver): 54 Test Cases
Total: 90 Test Cases
================================================================================
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def print_banner(text: str):
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)


def run_command_suite(name: str, cwd: str, cmd_args: list) -> bool:
    print_banner(f"RUNNING: {name}")
    print(f"Working Directory: {cwd}")
    print(f"Command          : {' '.join(cmd_args)}")

    t0 = time.time()
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{cwd};{BASE_DIR};{env.get('PYTHONPATH', '')}"

    proc = subprocess.run(
        [sys.executable, "-m", "pytest"] + cmd_args,
        cwd=cwd,
        env=env,
        capture_output=False,
        text=True
    )
    t1 = time.time()

    is_passed = proc.returncode == 0
    status = "PASSED (BERHASIL)" if is_passed else f"FAILED (KODE {proc.returncode})"
    print(f"\n--> Status: {status} | Durasi: {t1 - t0:.2f} detik")
    return is_passed


def main():
    start_total = time.time()
    print_banner("EVMOTO & ECGO ECOSYSTEM - RUSH HOUR SUBSIDY E2E & REGRESSION AUTOMATION")
    print(f"Waktu Eksekusi : {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}")
    print(f"Environment    : STAGING / DEV (Strictly Non-Production)")
    print(f"Target URL     : https://evmotoadmin.justkidding.app/rushHour/settings")
    print(f"Sub-halaman    : https://evmotoadmin.justkidding.app/rushHour/history")

    results = {}

    # 1. Admin Dashboard UI & API Suite (Settings & History)
    results["Web Admin UI & API (Settings & History)"] = run_command_suite(
        name="Web Admin Dashboard UI & API Suite",
        cwd=os.path.join(BASE_DIR, "web-dashboard"),
        cmd_args=["-v", "test_rush_hour_admin_ui_api.py"]
    )

    # 2. Mobile Apps Pricing & Driver Seamlessness Suite
    results["Mobile Apps Pricing & Driver Seamlessness"] = run_command_suite(
        name="Mobile Apps Driver & User Pricing Suite",
        cwd=os.path.join(BASE_DIR, "mobile-apps"),
        cmd_args=["-v", "Frontend/Feature/test_rush_hour_mobile_pricing.py"]
    )

    # 3. 4-Pillars QA Suite (Functionality, Boundary, Performance, Security)
    results["4-Pillars QA Rush Hour Suite"] = run_command_suite(
        name="4-Pillars QA Rush Hour Suite (18 TCs)",
        cwd=os.path.join(BASE_DIR, "api-testing"),
        cmd_args=["-v", "suites/test_rush_hour_subsidy_suite.py"]
    )

    # 4. Full Ecosystem Regression Suite (All 72 APIs)
    results["Full Ecosystem Regression Suite (All 72 APIs)"] = run_command_suite(
        name="Full Ecosystem Regression Suite",
        cwd=os.path.join(BASE_DIR, "api-testing"),
        cmd_args=["-v", "suites/"]
    )

    end_total = time.time()
    total_duration = end_total - start_total

    # Summary
    print_banner("REKAPITULASI HASIL PENGUJIAN END-TO-END & REGRESI")
    all_passed = True
    for module_name, is_passed in results.items():
        mark = "✓ PASSED" if is_passed else "✗ FAILED"
        print(f"[{mark}] {module_name}")
        if not is_passed:
            all_passed = False

    print(f"\nTotal Waktu Pengujian : {total_duration:.2f} detik")
    print(f"Hasil Akhir           : {'SELURUH PENGUJIAN 100% PASSED!' if all_passed else 'ADA TEST YANG GAGAL'}")
    print("=" * 80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
