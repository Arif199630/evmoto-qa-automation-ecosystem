"""
================================================================================
EVMOTO & ECGO PERFORMANCE TEST RUNNER & SLA VALIDATOR
================================================================================
CLI runner otomatis untuk mengeksekusi pengujian performa Locust:
- Mode: Headless (dengan auto-generate HTML/CSV report) atau Interactive Web UI
- Tipe Pengujian: Load Testing, Stress Testing, Spike Testing
- Target Persona: Unified Ecosystem, Driver, Passenger, atau ECGO
- Validasi Otomatis Ambang Batas SLA (P95 Latency & Error Rate)
================================================================================
"""
import os
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Memastikan output Windows terminal mendukung karakter UTF-8
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Registrasi path
PERF_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PERF_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

if str(PERF_DIR) not in sys.path:
    sys.path.insert(0, str(PERF_DIR))

from config.perf_config import PerfConfig


def get_locustfile_and_shape(target: str, test_type: str):
    """Menentukan file skenario Locust dan bentuk profil beban yang sesuai."""
    # Target Locustfile
    if target == "driver":
        locustfile = PERF_DIR / "locustfiles" / "driver_locustfile.py"
    elif target == "passenger":
        locustfile = PERF_DIR / "locustfiles" / "passenger_locustfile.py"
    elif target == "ecgo":
        locustfile = PERF_DIR / "locustfiles" / "ecgo_locustfile.py"
    else:  # unified
        locustfile = PERF_DIR / "locustfiles" / "unified_locustfile.py"

    # Shape class
    shape_class = None
    if test_type == "load":
        shape_class = "shapes.load_test_shape.StandardLoadTestShape"
    elif test_type == "stress":
        shape_class = "shapes.stress_test_shape.StepUpStressTestShape"
    elif test_type == "spike":
        shape_class = "shapes.spike_test_shape.SuddenSpikeTestShape"

    return locustfile, shape_class


def parse_csv_results(csv_prefix: Path):
    """Membaca hasil statistik dari file CSV yang digenerate Locust."""
    stats_file = Path(f"{csv_prefix}_stats.csv")
    if not stats_file.exists():
        return None

    import csv
    summary = {}
    with open(stats_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Name") == "Aggregated":
                req_count = int(row.get("Request Count", 0))
                fail_count = int(row.get("Failure Count", 0))
                median_ms = float(row.get("Median Response Time", 0))
                avg_ms = float(row.get("Average Response Time", 0))
                p95_ms = float(row.get("95%", 0) if "95%" in row else row.get("95%tile", 0))
                p99_ms = float(row.get("99%", 0) if "99%" in row else row.get("99%tile", 0))
                rps = float(row.get("Requests/s", 0))

                fail_rate = (fail_count / req_count * 100) if req_count > 0 else 0.0

                summary = {
                    "total_requests": req_count,
                    "total_failures": fail_count,
                    "failure_rate": round(fail_rate, 2),
                    "median_ms": median_ms,
                    "avg_ms": round(avg_ms, 2),
                    "p95_ms": p95_ms,
                    "p99_ms": p99_ms,
                    "requests_per_sec": rps
                }
                break
    return summary


def run():
    parser = argparse.ArgumentParser(description="EvMoto & ECGO Performance Test Engine")
    parser.add_argument(
        "--target",
        choices=["unified", "driver", "passenger", "ecgo"],
        default="unified",
        help="Target persona pengujian (default: unified)"
    )
    parser.add_argument(
        "--type",
        choices=["load", "stress", "spike"],
        default="load",
        help="Tipe profil beban: load (normal), stress (step-up), spike (rush surge)"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Jalankan dalam mode Web UI interaktif di http://localhost:8089"
    )
    parser.add_argument(
        "--users",
        type=int,
        default=None,
        help="Jumlah virtual user manual (jika tidak menggunakan auto-shape)"
    )
    parser.add_argument(
        "--spawn-rate",
        type=int,
        default=None,
        help="Spawn rate user/detik (jika tidak menggunakan auto-shape)"
    )
    parser.add_argument(
        "--run-time",
        type=str,
        default=None,
        help="Durasi running manual (cth: 30s, 1m, 2m)"
    )

    args = parser.parse_args()

    locustfile, shape_class = get_locustfile_and_shape(args.target, args.type)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_tag = f"perf_{args.target}_{args.type}_{timestamp}"
    html_report = REPORTS_DIR / f"{report_tag}.html"
    csv_prefix = REPORTS_DIR / f"{report_tag}"

    print("\n" + "=" * 80)
    print("🚀 EVMOTO & ECGO PERFORMANCE TESTING AUTOMATION SUITE")
    print("=" * 80)
    print(f"📌 Target Skenario : {args.target.upper()} ECOSYSTEM")
    print(f"📊 Tipe Beban      : {args.type.upper()} TESTING")
    print(f"🌐 Target Server   : {PerfConfig.EVMOTO_BASE_URL} (Dev / Staging)")
    print(f"📁 Locustfile      : {locustfile.name}")

    if args.web:
        print(f"🖥️  Mode           : INTERACTIVE WEB UI (Buka di browser: http://localhost:8089)")
        cmd = [
            sys.executable, "-m", "locust",
            "-f", str(locustfile),
            "--host", PerfConfig.EVMOTO_BASE_URL
        ]
        print(f"🔧 Menjalankan: {' '.join(cmd)}")
        subprocess.run(cmd)
        return

    # Headless Mode
    print(f"⚙️  Mode           : HEADLESS AUTOMATED RUN")
    print(f"📄 HTML Report     : {html_report.name}")
    print(f"📈 CSV Metrics     : {csv_prefix.name}_*.csv")
    print("=" * 80)

    cmd = [
        sys.executable, "-m", "locust",
        "-f", str(locustfile),
        "--host", PerfConfig.EVMOTO_BASE_URL,
        "--headless",
        "--html", str(html_report),
        "--csv", str(csv_prefix)
    ]

    # Cek apakah menggunakan shape atau manual parameters
    if args.users and args.run_time:
        spawn_rate = args.spawn_rate or max(1, args.users // 10)
        cmd.extend(["-u", str(args.users), "-r", str(spawn_rate), "-t", args.run_time])
        print(f"⏱️  Parameter      : {args.users} Users, Spawn Rate: {spawn_rate}/s, Durasi: {args.run_time}")
    elif shape_class:
        # Load test shape script
        shape_file = PERF_DIR / "shapes" / f"{args.type}_test_shape.py"
        cmd.extend(["-f", str(locustfile), "-f", str(shape_file)])
        print(f"📈 Load Profile    : {shape_class} (Programmatic Shape Profile)")
    else:
        cmd.extend(["-u", "20", "-r", "2", "-t", "30s"])

    start_exec = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(PERF_DIR), capture_output=True, text=True)
    except KeyboardInterrupt:
        print("\n⚠️ Eksekusi dibatalkan oleh pengguna.")
        return

    elapsed_exec = round(time.time() - start_exec, 2)

    # Evaluasi Hasil
    print("\n" + "=" * 80)
    print("📊 RINGKASAN HASIL PENGUJIAN PERFORMA (SLA & METRICS)")
    print("=" * 80)

    summary = parse_csv_results(csv_prefix)
    if summary:
        p95 = summary["p95_ms"]
        fail_rate = summary["failure_rate"]
        sla_p95_pass = p95 <= PerfConfig.SLA_MAX_P95_MS
        sla_fail_pass = fail_rate <= PerfConfig.SLA_MAX_FAILURE_RATE

        print(f"  • Total HTTP Requests : {summary['total_requests']:,} req")
        print(f"  • Gagal (Failures)    : {summary['total_failures']} ({summary['failure_rate']}%)")
        print(f"  • Throughput Rata-rata: {summary['requests_per_sec']:.2f} Req/s")
        print(f"  • Response Time (Avg) : {summary['avg_ms']} ms")
        print(f"  • Median (P50)        : {summary['median_ms']} ms")
        print(f"  • Percentile 95 (P95) : {summary['p95_ms']} ms [SLA Limit: < {PerfConfig.SLA_MAX_P95_MS} ms] -> {'✅ PASSED' if sla_p95_pass else '❌ FAILED'}")
        print(f"  • Percentile 99 (P99) : {summary['p99_ms']} ms")
        print(f"  • Error Rate SLA      : {summary['failure_rate']}% [SLA Limit: < {PerfConfig.SLA_MAX_FAILURE_RATE}%] -> {'✅ PASSED' if sla_fail_pass else '❌ FAILED'}")
        print("-" * 80)

        overall_pass = sla_p95_pass and sla_fail_pass
        status_text = "🎉 SEMUA KRITERIA SLA TERPENUHI (PASSED)" if overall_pass else "⚠️ BEBERAPA AMBANG BATAS SLA TERLAMPAUI"
        print(f"🏁 KESIMPULAN PERFORMA : {status_text}")
    else:
        print("⚠️ Data CSV tidak ditemukan atau pengujian dihentikan lebih awal.")
        if proc.stderr:
            print("Log Error:", proc.stderr[:500])

    print(f"\n📂 Laporan HTML Lengkap: {html_report.resolve()}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run()
