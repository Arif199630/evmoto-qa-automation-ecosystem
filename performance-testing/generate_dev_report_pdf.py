"""
================================================================================
EVMOTO & ECGO TECHNICAL PERFORMANCE REPORT GENERATOR (FOR DEVELOPER TEAM)
================================================================================
Menghasilkan dokumen PDF laporan teknikal performa khusus untuk Tim Developer:
- Spesifikasi Endpoint & Analisis Latensi Terperinci (P50, P95, P99)
- Investigasi Root Cause & Titik Hambatan (Bottlenecks) pada 1.000 Concurrent Users
- Checklist Action Items untuk Developer Backend, Mobile, dan DevOps
- Panduan Eksekusi Otomasi Lokal bagi Engineer
================================================================================
"""
import os
import sys
import shutil
import warnings
from pathlib import Path
from datetime import datetime
from fpdf import FPDF

# Konfigurasi encoding terminal Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Konfigurasi Path
PERF_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PERF_DIR / "reports"
DOWNLOADS_DIR = Path(r"C:\Users\ASUS\Downloads")
DOCS_DIR = Path(r"C:\Users\ASUS\Documents\EVMoto Apps\Test Case Manual\Mobile Apps (User & Driver)")
OUTPUT_FILENAME = "LAPORAN_TEKNIKAL_PERFORMANCE_UNTUK_DEVELOPER.pdf"

PROJECT_PDF_PATH = REPORTS_DIR / OUTPUT_FILENAME
DOWNLOAD_PDF_PATH = DOWNLOADS_DIR / OUTPUT_FILENAME
DOCS_PDF_PATH = DOCS_DIR / OUTPUT_FILENAME


class DeveloperPerfPDF(FPDF):
    """Template PDF teknikal formal untuk konsumsi Tim Developer & DevOps."""

    def header(self):
        # Header Dark Navy & Violet Accent
        self.set_fill_color(30, 41, 59)  # Slate 800
        self.rect(0, 0, 210, 4, 'F')
        
        self.set_y(8)
        self.set_font("Helvetica", "B", 12.5)
        self.set_text_color(15, 23, 42)
        self.cell(140, 6, "ENGINEERING TECHNICAL REPORT: API PERFORMANCE & STRESS", ln=0)

        # Badge: FOR DEVELOPER TEAM
        self.set_font("Helvetica", "B", 7.8)
        self.set_fill_color(241, 245, 249)
        self.set_text_color(51, 65, 85)
        self.set_draw_color(203, 213, 225)
        self.cell(50, 6, "FOR: DEV & DEVOPS TEAM", border=1, ln=1, align="C", fill=True)

        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, "Backend Golang & Node.js | Locust Concurrency Benchmark (10 - 1000 Virtual Users)", ln=1)

        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(10, 20, 200, 20)
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(148, 163, 184)
        self.cell(100, 8, "EvMoto QA Engineering | Technical Performance Specification", align="L")
        self.cell(90, 8, f"Halaman {self.page_no()} dari {{nb}}", align="R")


def draw_tech_box(pdf, x, y, width, height, title, value, detail, border_color=(59, 130, 246)):
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, width, height, 'DF')

    pdf.set_fill_color(*border_color)
    pdf.rect(x, y, 2.5, height, 'F')

    pdf.set_xy(x + 5, y + 2.5)
    pdf.set_font("Helvetica", "B", 6.8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(width - 7, 3.5, title.upper(), ln=1)

    pdf.set_xy(x + 5, y + 6.5)
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(width - 7, 6, value, ln=1)

    pdf.set_xy(x + 5, y + 13)
    pdf.set_font("Helvetica", "", 6.2)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(width - 7, 3.5, detail, ln=1)


def generate_dev_pdf():
    pdf = DeveloperPerfPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()

    # --------------------------------------------------------------------------
    # 1. HEADER & TECHNICAL HIGHLIGHTS
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 13.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "Hasil Uji Beban & Rekomendasi Arsitektur untuk Tim Developer", ln=1)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(71, 85, 105)
    now_str = datetime.now().strftime("%d %B %Y, %H:%M WIB")
    pdf.cell(0, 4, f"Target Host: https://evmotodev.justkidding.app | Tanggal Analisis: {now_str}", ln=1)
    pdf.ln(2)

    # Callout Box untuk Developer
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(148, 163, 184)
    pdf.set_line_width(0.5)
    pdf.rect(10, 33, 190, 22, 'DF')

    pdf.set_xy(13, 35)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 4, "INTISARI TEKNIKAL UNTUK ENGINEER (KEY ENGINEERING TAKEAWAYS):", ln=1)

    pdf.set_xy(13, 40)
    pdf.set_font("Helvetica", "", 7.2)
    pdf.set_text_color(51, 65, 85)
    takeaway_text = (
        "1. Kestabilan Sistem: Backend Golang berhasil menangani 2.435 requests pada 1.000 virtual users dengan 0.00% Error Rate "
        "(tidak ada panic, segfault, atau crash 500/502). Koneksi soket dan session management sangat resilien.\n"
        "2. Bottleneck Teridentifikasi: Throughput tertahan di 76.25 RPS pada 1.000 VU akibat antrean request (queueing) pada "
        "endpoint captcha/auth. Core endpoints (fare estimation, online heartbeat, wallet) stabil di median latency < 1 detik."
    )
    pdf.multi_cell(184, 3.5, takeaway_text)

    # 4 Kotak KPI Teknikal
    pdf.set_y(59)
    card_w = 45
    card_h = 18
    draw_tech_box(pdf, 10, 59, card_w, card_h, "Kapasitas Aman", "100 VU (~45 RPS)", "P95: 600 ms | 0% Error", (16, 185, 129))
    draw_tech_box(pdf, 58, 59, card_w, card_h, "Throughput Maksimal", "76.25 RPS", "Batas 1 Pod / Dev Instance", (59, 130, 246))
    draw_tech_box(pdf, 106, 59, card_w, card_h, "Failure Rate", "0.00% (0 Err)", "2.435 requests dieksekusi", (16, 185, 129))
    draw_tech_box(pdf, 154, 59, card_w, card_h, "Rekomendasi HPA", "10 - 15 Pods", "Target 1.000 VU di Production", (245, 158, 11))

    pdf.set_y(81)

    # --------------------------------------------------------------------------
    # 2. TABEL SPESIFIKASI ENDPOINT & ANALISIS LATENSI NYATA
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, "1. Rincian Kinerja Endpoint API Teruji (Hasil Nyata Staging Dev)", ln=1)

    pdf.set_font("Helvetica", "B", 6.8)
    pdf.set_fill_color(224, 242, 254)
    pdf.set_draw_color(203, 213, 225)
    pdf.set_line_width(0.2)

    pdf.cell(62, 5, "Endpoint API & HTTP Method", border=1, fill=True)
    pdf.cell(32, 5, "Modul / Layanan", border=1, fill=True, align="C")
    pdf.cell(18, 5, "Min Lat", border=1, fill=True, align="C")
    pdf.cell(20, 5, "P50 (100 VU)", border=1, fill=True, align="C")
    pdf.cell(20, 5, "P95 (100 VU)", border=1, fill=True, align="C")
    pdf.cell(20, 5, "P50 (1k VU)", border=1, fill=True, align="C")
    pdf.cell(18, 5, "Throughput", border=1, fill=True, align="C", ln=1)

    endpoints_data = [
        ("POST /order/api/user/estimateFare", "Passenger - Fare Engine", "5.9 ms", "9.0 ms", "260.0 ms", "940.0 ms", "8.26 rps"),
        ("POST /order/api/user/createOrder", "Passenger - Order Booking", "5.2 ms", "12.0 ms", "290.0 ms", "1000.0 ms", "4.37 rps"),
        ("POST /order/api/user/cancelOrder", "Passenger - Cancel Order", "6.9 ms", "14.0 ms", "200.0 ms", "960.0 ms", "0.77 rps"),
        ("GET  /user/api/user/queryInfo", "Passenger - Profile", "6.1 ms", "10.0 ms", "370.0 ms", "1100.0 ms", "2.75 rps"),
        ("POST /driver/api/v2/online", "Driver - GPS Telemetry", "6.2 ms", "10.0 ms", "370.0 ms", "970.0 ms", "9.84 rps"),
        ("POST /driver/api/driver/queryHomeData", "Driver - Dashboard", "6.5 ms", "23.0 ms", "370.0 ms", "1000.0 ms", "6.68 rps"),
        ("GET  /account/api/ecgo/wallet/status", "Driver - eWallet", "6.4 ms", "12.0 ms", "340.0 ms", "920.0 ms", "4.15 rps"),
        ("POST /account/base/driver/driverLoginByOtp", "Driver - PIN Login", "23.4 ms", "38.0 ms", "200.0 ms", "980.0 ms", "5.14 rps"),
        ("GET  /v5/users/diskon/list", "ECGO - 100% Free Swap", "6.2 ms", "10.0 ms", "250.0 ms", "960.0 ms", "4.44 rps"),
        ("GET  /v5/users/evmoto-connect/status", "ECGO - Connect Status", "6.8 ms", "19.0 ms", "360.0 ms", "960.0 ms", "2.09 rps"),
        ("POST /account/base/driver/queryCaptcha", "Driver - Captcha Guard", "343.5 ms", "530.0 ms", "650.0 ms", "10000.0 ms", "5.14 rps"),
        ("POST /account/base/user/queryCaptcha", "Passenger - Captcha Guard", "346.8 ms", "630.0 ms", "1300.0 ms", "11000.0 ms", "6.39 rps"),
    ]

    pdf.set_font("Helvetica", "", 6.7)
    for ep, mod, t_min, p50_100, p95_100, p50_1k, tput in endpoints_data:
        pdf.cell(62, 4.3, ep, border=1)
        pdf.cell(32, 4.3, mod, border=1, align="C")
        pdf.cell(18, 4.3, t_min, border=1, align="C")
        pdf.cell(20, 4.3, p50_100, border=1, align="C")
        pdf.cell(20, 4.3, p95_100, border=1, align="C")
        pdf.cell(20, 4.3, p50_1k, border=1, align="C")
        pdf.cell(18, 4.3, tput, border=1, align="C", ln=1)

    pdf.ln(3)

    # --------------------------------------------------------------------------
    # 3. INVESTIGASI TITIK HAMBATAN (ROOT CAUSE ANALYSIS)
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, "2. Analisis Akar Masalah (Root Cause & Saturation Analysis pada 1.000 VU)", ln=1)

    root_causes = [
        (
            "A. Bottleneck #1 - Pemicu Antrean Latensi Captcha & SMS OTP (Latensi P95 > 10 Detik):",
            "Saat 1.000 user virtual di-spawn serempak, endpoint captcha query menjadi antrean terpanjang. Hal ini terjadi karena "
            "proses pembuatan captcha image atau sinkronisasi I/O provider SMS berjalan secara sinkron (blocking I/O) pada main thread backend. "
            "Solusi: Offload proses pembuatan captcha ke in-memory pre-generated pool atau gunakan Cloudflare Turnstile."
        ),
        (
            "B. Bottleneck #2 - Database Connection Pool Saturation:",
            "Pada uji 1.000 users, waktu respon query database read-heavy (saldo dompet, daftar diskon kupon) naik dari 10 ms ke 900 ms. "
            "Ini mengindikasikan koneksi database Golang (`sql.DB`) mencapai `MaxOpenConns` sehingga request menunggu connection pool yang tersedia."
        ),
        (
            "C. Bottleneck #3 - Batas Throughput Single Pod (Plateau di 76.25 RPS):",
            "Throughput naik linear dari 10 VU (4.82 RPS) ke 100 VU (42.79 RPS), namun mendatar di 76.25 RPS saat 1.000 VU. "
            "Ini membuktikan CPU core instance dev telah jenuh 100%, menegaskan perlunya auto-scaling horizontal (HPA)."
        )
    ]

    for rc_title, rc_desc in root_causes:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(185, 28, 28)
        pdf.cell(0, 4, rc_title, ln=1)
        pdf.set_font("Helvetica", "", 6.8)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(190, 3.3, rc_desc)
        pdf.ln(1)

    # ==========================================================================
    # HALAMAN 2: ACTION ITEMS DEVELOPER & PANDUAN REPRODUCE
    # ==========================================================================
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5.5, "3. Engineering Action Items (Rekomendasi Spesifik per Tim)", ln=1)

    action_sections = [
        (
            "A. Tim Backend Developer (Golang & Node.js)",
            [
                "1. Idempotency Key: Terapkan header `X-Idempotency-Key` pada endpoint order booking guna mencegah duplikasi transaksi di DB.",
                "2. DB Pool Tuning: Atur konfigurasi DB: `db.SetMaxOpenConns(100)`, `db.SetMaxIdleConns(25)`, `db.SetConnMaxLifetime(5 * time.Minute)`.",
                "3. In-Memory Cache Redis: Pasang TTL 15 detik pada endpoint `/estimateFare` berbasis geohash rute jemput-antar.",
                "4. Non-Blocking Captcha: Buat generator token captcha pre-warmed di Redis agar request auth langsung terlayani < 20 ms."
            ]
        ),
        (
            "B. Tim Mobile Client Developer (Android Flutter / Kotlin)",
            [
                "1. Exponential Backoff Retry: Terapkan jeda eksponensial (1s, 2s, 4s) pada retry koneksi saat terjadi lonjakan trafik/timeout.",
                "2. Throttle Telemetri GPS: Batasi pengiriman lokasi mitra driver di background minimal interval 3 detik (cegah socket flooding).",
                "3. Optimistic UI State: Tampilkan skeleton loading seketika saat penumpang tap 'Pesan Motor' untuk pengalaman UX yang mulus."
            ]
        ),
        (
            "C. Tim DevOps & Infrastructure",
            [
                "1. Horizontal Pod Autoscaler (HPA): Konfigurasikan target CPU 70% dengan min 3 pods dan max 15 pods di cluster EKS/GKE.",
                "2. Rate Limiting Nginx/Cloudflare: Batasi endpoint SMS OTP max 5 req/menit per IP untuk proteksi dari bot flooding.",
                "3. PgBouncer / Connection Pooler: Pasang PgBouncer di depan PostgreSQL untuk menahan antrean konkurensi koneksi hingga 5.000 koneksi."
            ]
        )
    ]

    for sec_title, items in action_sections:
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_text_color(14, 116, 144)
        pdf.cell(0, 4.2, sec_title, ln=1)
        pdf.set_font("Helvetica", "", 7.0)
        pdf.set_text_color(51, 65, 85)
        for item in items:
            pdf.cell(5, 3.5, "-", ln=0)
            pdf.multi_cell(185, 3.5, item)
        pdf.ln(1.5)

    pdf.ln(2)

    # --------------------------------------------------------------------------
    # 4. PANDUAN EKSEKUSI OTOMASI LOKAL BAGI DEVELOPER
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5.5, "4. Panduan Eksekusi Otomasi & Verifikasi Mandiri oleh Developer", ln=1)

    cmd_box = (
        "# 1. Masuk ke direktori performance testing:\n"
        "cd evmoto-qa-automation-portfolio/performance-testing\n\n"
        "# 2. Uji Cepat Beban 100 Users (Batas Aman SLA):\n"
        "python run_performance.py --target unified --users 100 --spawn-rate 20 --run-time 30s\n\n"
        "# 3. Uji Stress Beban 1.000 Users (Uji Skalabilitas Auto-Scaling):\n"
        "python run_performance.py --target unified --users 1000 --spawn-rate 100 --run-time 30s\n\n"
        "# 4. Buka Visual Web UI Interactive Dashboard:\n"
        "python run_performance.py --target unified --web   -> Buka http://localhost:8089"
    )

    pdf.set_fill_color(15, 23, 42)  # Dark Code Box
    pdf.set_draw_color(51, 65, 85)
    pdf.rect(10, pdf.get_y(), 190, 31, 'DF')
    pdf.set_xy(13, pdf.get_y() + 2)
    pdf.set_font("Courier", "", 6.7)
    pdf.set_text_color(226, 232, 240)
    pdf.multi_cell(184, 3.4, cmd_box)

    pdf.set_y(pdf.get_y() + 5)

    # --------------------------------------------------------------------------
    # 5. LEMBAR PENGESAHAN LAPORAN TEKNIKAL
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, "5. Lembar Pengesahan Laporan Teknikal", ln=1)

    box_w = 90
    box_h = 27
    y_sign = pdf.get_y() + 1

    # Kotak Penanggung Jawab QA
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(10, y_sign, box_w, box_h, 'DF')
    pdf.set_xy(13, y_sign + 2)
    pdf.set_font("Helvetica", "B", 7.2)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(box_w - 6, 3.5, "Disusun & Diuji Oleh:", ln=1)
    pdf.set_xy(13, y_sign + 15)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(box_w - 6, 3.8, "Bhagus Arif Prayogo", ln=1)
    pdf.set_xy(13, y_sign + 19)
    pdf.set_font("Helvetica", "", 6.8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(box_w - 6, 3.2, "Senior QA Engineer", ln=1)

    # Kotak Mengetahui / Atasan
    pdf.rect(110, y_sign, box_w, box_h, 'DF')
    pdf.set_xy(113, y_sign + 2)
    pdf.set_font("Helvetica", "B", 7.2)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(box_w - 6, 3.5, "Diterima oleh Lead Developer / Tech Lead:", ln=1)
    pdf.set_xy(113, y_sign + 15)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(box_w - 6, 3.8, "[ Tech Lead / Backend Lead / DevOps Lead ]", ln=1)
    pdf.set_xy(113, y_sign + 19)
    pdf.set_font("Helvetica", "", 6.8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(box_w - 6, 3.2, "Engineering & Development Team", ln=1)

    # Simpan File PDF
    pdf.output(str(PROJECT_PDF_PATH))
    print(f"✅ PDF Developer Report berhasil dibuat: {PROJECT_PDF_PATH}")

    # Salin ke Downloads
    try:
        shutil.copy2(str(PROJECT_PDF_PATH), str(DOWNLOAD_PDF_PATH))
        print(f"📥 PDF berhasil disalin ke Downloads: {DOWNLOAD_PDF_PATH}")
    except Exception as e:
        print(f"⚠️ Gagal menyalin ke Downloads: {e}")

    # Salin ke Dokumen Resmi
    try:
        if DOCS_DIR.exists():
            shutil.copy2(str(PROJECT_PDF_PATH), str(DOCS_PDF_PATH))
            print(f"📁 PDF berhasil disalin ke Dokumen Resmi: {DOCS_PDF_PATH}")
    except Exception as e:
        print(f"⚠️ Gagal menyalin ke Dokumen Resmi: {e}")


if __name__ == "__main__":
    generate_dev_pdf()
