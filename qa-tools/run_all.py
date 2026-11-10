"""
Satu perintah untuk regression EvMoto: quality gate -> pengaman staging -> test -> laporan PDF.

Contoh:
  python run_all.py --suite all                 # admin + api + mobile + lintas aplikasi
  python run_all.py --suite admin api           # hanya admin dan API
  python run_all.py --suite mobile --simulator  # mobile tanpa emulator (hasil = validasi kode test saja)
  python run_all.py --suite api --mock-services # endpoint yang belum ada di staging dijawab mock lokal

Mobile tanpa --simulator butuh Appium + emulator headless yang sudah jalan
(lihat ../evmoto-user-mobile-automation/scripts/start_headless_emulator.ps1).
Hasil ditulis ke runs/<tanggal_jam>/ beserta Laporan_Regression_EvMoto.pdf.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = HERE.parent
# Layout repo GitHub (web-dashboard/, mobile-apps/) atau layout lokal lama
ADMIN = SCRATCH / "web-dashboard" if (SCRATCH / "web-dashboard").exists() else SCRATCH / "Automation_Project_EvMoto"
MOBILE = SCRATCH / "mobile-apps" if (SCRATCH / "mobile-apps").exists() else SCRATCH / "evmoto-user-mobile-automation"
CROSS_FILES = r"^test_(admin_|dispatch_|drv_batch_|e2e_|drv_order_hall)"

# suite -> (project, folder test, filter env, jumlah proses paralel)
SUITES = {
    "admin": (ADMIN, "Frontend/Feature/Step_Definition", {}, 3),
    "api": (MOBILE / "api-testing", "suites", {}, 1),
    "mobile": (MOBILE, "Frontend/Feature/Step_Definition", {"FILE_EXCLUDE": CROSS_FILES}, 4),
    "cross": (MOBILE, "Frontend/Feature/Step_Definition", {"FILE_INCLUDE": CROSS_FILES}, 2),
}
GATE_PROJECT = {"admin": "admin", "api": "mobile", "mobile": "mobile", "cross": "mobile"}
MOCK_PORT = 8790
MOCK_URL = f"http://127.0.0.1:{MOCK_PORT}"


def run(cmd, env=None, cwd=None):
    print("$", " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, env=env, cwd=cwd).returncode


def start_mock(log_path):
    """Jalankan mock_services/mock_server.py di background, tunggu sampai /__health menjawab."""
    log = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen([sys.executable, "-I", str(HERE / "mock_services" / "mock_server.py"), "--port", str(MOCK_PORT)],
                            stdout=log, stderr=subprocess.STDOUT)
    for _ in range(50):
        try:
            urllib.request.urlopen(f"{MOCK_URL}/__health", timeout=1)
            print(f"Mock server aktif (PID {proc.pid}) di {MOCK_URL}, log: {log_path}")
            return proc
        except OSError:
            if proc.poll() is not None:
                break
            time.sleep(0.2)
    proc.terminate()
    raise SystemExit(f"Mock server gagal jalan (port {MOCK_PORT} sudah dipakai?). Lihat {log_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--suite", nargs="+", default=["all"], choices=["all", *SUITES])
    ap.add_argument("--simulator", action="store_true", help="mobile memakai HeadlessMobileDriver (bukan aplikasi)")
    ap.add_argument("--mock-services", action="store_true",
                    help="jalankan mock lokal untuk endpoint yang belum ada di staging (test-nya ditandai mock=true)")
    args = ap.parse_args()
    suites = list(SUITES) if "all" in args.suite else args.suite

    env = os.environ.copy()
    env.setdefault("ENVIRONMENT", "dev")
    env["HEADLESS"] = "true"
    env["LARK_WEBHOOK_URL"] = ""
    if args.simulator:
        env["HEADLESS_MOBILE"] = "1"
        env["HEADLESS_FAST"] = "1"

    # 1. Quality gate: pelanggaran baru menghentikan run
    for project in sorted({GATE_PROJECT[s] for s in suites}):
        if run([sys.executable, "-I", str(HERE / "quality_gate.py"), project]) != 0:
            print("Run dihentikan: perbaiki pelanggaran quality gate di atas lebih dulu.")
            return 1

    # 2. Pengaman staging: dijalankan juga oleh pytest_sessionstart di tiap project
    sys.path.insert(0, str(MOBILE / "core"))
    from staging_guard import ensure_not_production
    ensure_not_production()

    out = HERE / "runs" / datetime.now().strftime("%Y-%m-%d_%H%M")
    out.mkdir(parents=True, exist_ok=True)
    mobile_mode = "SIMULATOR (HeadlessMobileDriver)" if args.simulator else "Appium + emulator headless"
    (out / "run_info.json").write_text(json.dumps({
        "environment": env["ENVIRONMENT"], "started": datetime.now().strftime("%d %b %Y %H:%M"),
        "mobile_mode": mobile_mode, "suites": suites, "mock_services": args.mock_services}, indent=1), encoding="utf-8")

    # 3. Test per suite, tiap file test di prosesnya sendiri
    mock = None
    if args.mock_services:
        mock = start_mock(out / "mock_services.log")
        env["USE_MOCK_SERVICES"] = "1"
        env["MOCK_SERVICES_URL"] = MOCK_URL
    try:
        for suite in suites:
            project, tests_dir, filters, buckets = SUITES[suite]
            if suite in ("mobile", "cross") and not args.simulator:
                buckets = 1  # satu emulator = satu sesi Appium; paralel membuat sesi saling bertabrakan
            buckets = int(os.getenv(f"{suite.upper()}_BUCKETS", buckets))
            suite_env = {**env, **filters}
            run([sys.executable, "-I", str(HERE / "run_per_file.py"), str(project), tests_dir, str(out / suite), str(buckets)],
                env=suite_env)
    finally:
        if mock:
            mock.terminate()  # berhenti lewat PID proses ini saja
            mock.wait(timeout=10)
            print(f"Mock server (PID {mock.pid}) dihentikan.")

    # 4. Laporan
    run([sys.executable, "-I", str(HERE / "report.py"), str(out)])
    print("Selesai. Hasil:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
