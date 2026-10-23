"""
================================================================================
EVMOTO & ECGO EXECUTIVE PERFORMANCE TESTING PDF REPORT GENERATOR
================================================================================
Menghasilkan dokumen PDF laporan performa eksekutif formal untuk atasan/manajemen:
- Breakdown Kapasitas Beban 3 Tingkatan: 10 Users vs 100 Users vs 1,000 Users
- Analisis Titik Kejenuhan (Saturation Threshold / Breaking Point)
- Evaluasi Throughput RPS, Latensi Median (P50), P95, dan Tingkat Kegagalan (0%)
- Rekomendasi Horizontal Auto-scaling (HPA) untuk Skala Produksi
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
OUTPUT_FILENAME = "LAPORAN_PERFORMANCE_TESTING_EVMOTO_ECGO.pdf"

PROJECT_PDF_PATH = REPORTS_DIR / OUTPUT_FILENAME
DOWNLOAD_PDF_PATH = DOWNLOADS_DIR / OUTPUT_FILENAME
DOCS_PDF_PATH = DOCS_DIR / OUTPUT_FILENAME


class ExecutivePerfPDF(FPDF):
    """Template PDF formal bertaraf eksekutif untuk laporan QA Performance Testing."""

    def header(self):
        # Top Accent Bar (EvMoto Electric Cyan & Emerald)
        self.set_fill_color(14, 165, 233)
        self.rect(0, 0, 210, 4, 'F')
        
        # Header Metadata
        self.set_y(8)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(15, 23, 42)
        self.cell(135, 7, "EVMOTO & ECGO SUPERAPPS ECOSYSTEM", ln=0)

        # Status Badge: HIGH RELIABILITY
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(224, 242, 254)  # Light cyan fill
        self.set_text_color(3, 105, 161)    # Deep cyan text
        self.set_draw_color(125, 211, 252)  # Cyan border
        self.cell(55, 6, "SCALABILITY BENCHMARK (10-1000 VU)", border=1, ln=1, align="C", fill=True)

        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, "Enterprise Quality Assurance | Capacity Tier Breakdown: 10, 100, & 1000 Concurrent Users", ln=1)

        # Horizontal Divider
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(10, 21, 200, 21)
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(148, 163, 184)
        page_str = f"Halaman {self.page_no()} dari {{nb}}"
        confidential_str = "Dokumen Rahasia Internal - eVMoto Tech QA & Engineering Management"
        self.cell(100, 8, confidential_str, align="L")
        self.cell(90, 8, page_str, align="R")


def draw_metric_card(pdf, x, y, width, height, title, value, subtitle, status_color=(16, 185, 129)):
    """Menggambar kartu metrik KPI dengan border elegan."""
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, width, height, 'DF')

    # Accent left border
    pdf.set_fill_color(*status_color)
    pdf.rect(x, y, 2.5, height, 'F')

    # Title
    pdf.set_xy(x + 5, y + 3)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(width - 7, 4, title.upper(), ln=1)

    # Big Value
    pdf.set_xy(x + 5, y + 7)
    pdf.set_font("Helvetica", "B", 12.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(width - 7, 7, value, ln=1)

    # Subtitle
    pdf.set_xy(x + 5, y + 14)
    pdf.set_font("Helvetica", "", 6.8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(width - 7, 4, subtitle, ln=1)


def generate_pdf():
    pdf = ExecutivePerfPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()

    # --------------------------------------------------------------------------
    # 1. JUDUL LAPORAN & EXECUTIVE CALLOUT
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 14.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "Executive Capacity & Load Tier Breakdown Report", ln=1)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(71, 85, 105)
    report_date = datetime.now().strftime("%d %B %Y, %H:%M WIB")
    pdf.cell(0, 4, f"Tanggal Analisis: {report_date}  |  Target Host: https://evmotodev.justkidding.app  |  Engine: Locust 2.46.7", ln=1)
    pdf.ln(2)

    # Executive Summary Box
    pdf.set_fill_color(240, 253, 250)
    pdf.set_draw_color(16, 185, 129)
    pdf.set_line_width(0.6)
    pdf.rect(10, 36, 190, 22, 'DF')

    pdf.set_xy(14, 38)
    pdf.set_font("Helvetica", "B", 8.8)
    pdf.set_text_color(4, 120, 87)
    pdf.cell(0, 5, "RINGKASAN EKSEKUTIF UNTUK MANAJEMEN / ATASAN:", ln=1)

    pdf.set_xy(14, 43)
    pdf.set_font("Helvetica", "", 7.6)
    pdf.set_text_color(15, 23, 42)
    summary_text = (
        "Tim QA telah melaksanakan evaluasi kapasitas beban berjenjang pada 3 skala pengguna bersamaan (10, 100, dan 1.000 "
        "Virtual Users). Temuan utama: Backend Golang sangat tangguh dengan 0.00% Error Rate (tanpa crash/500/502). Sistem beroperasi "
        "sangat optimal hingga 100 concurrent users (P95: 600 ms, Throughput: 42.79 RPS). Pada 1.000 concurrent users (2.435 requests), "
        "throughput mencapai batas saturasi instance tunggal (76.25 RPS) dengan antrean request. Untuk beban 1.000+ pengguna di production, "
        "diperlukan konfigurasi Horizontal Pod Autoscaler (HPA) sebanyak 10-15 replika."
    )
    pdf.multi_cell(182, 3.7, summary_text)
    pdf.ln(5)

    # --------------------------------------------------------------------------
    # 2. KPI METRIC CARDS (4 KOLOM)
    # --------------------------------------------------------------------------
    pdf.set_y(61)
    card_w = 45
    card_h = 20
    draw_metric_card(pdf, 10, 61, card_w, card_h, "Batas Aman (SLA)", "100 Users", "P95: 600 ms (< 800 ms SLA)", (16, 185, 129))
    draw_metric_card(pdf, 58, 61, card_w, card_h, "Failure Rate", "0.00%", "Zero Crash di semua tier", (16, 185, 129))
    draw_metric_card(pdf, 106, 61, card_w, card_h, "Throughput Puncak", "76.25 RPS", "2.435 requests diproses", (14, 165, 233))
    draw_metric_card(pdf, 154, 61, card_w, card_h, "Saturasi Server", "1.000 Users", "Queue latency terdeteksi", (245, 158, 11))

    pdf.set_y(85)

    # --------------------------------------------------------------------------
    # 3. TABEL PERBANDINGAN TIER BEBAN: 10 vs 100 vs 1000 USERS
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "1. Matriks Komparasi Kinerja 3 Skala Beban (10 vs 100 vs 1.000 Users)", ln=1)

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(224, 242, 254)  # Light Sky Blue
    pdf.set_draw_color(203, 213, 225)
    pdf.set_line_width(0.2)

    pdf.cell(35, 5.5, "Tingkatan Skala Beban", border=1, fill=True)
    pdf.cell(20, 5.5, "Total Req", border=1, fill=True, align="C")
    pdf.cell(22, 5.5, "Throughput", border=1, fill=True, align="C")
    pdf.cell(22, 5.5, "Rata-rata", border=1, fill=True, align="C")
    pdf.cell(20, 5.5, "Median P50", border=1, fill=True, align="C")
    pdf.cell(24, 5.5, "Percentile 95", border=1, fill=True, align="C")
    pdf.cell(22, 5.5, "Failure Rate", border=1, fill=True, align="C")
    pdf.cell(25, 5.5, "Status SLA", border=1, fill=True, align="C", ln=1)

    tier_data = [
        (
            "10 Users (Baseline)", "92 req", "4.82 RPS", "23.99 ms", "8.0 ms", "89.0 ms", "0.00%",
            "PASSED", (22, 101, 52)
        ),
        (
            "100 Users (High Load)", "1.035 req", "42.79 RPS", "112.47 ms", "21.0 ms", "600.0 ms", "0.00%",
            "PASSED", (22, 101, 52)
        ),
        (
            "1.000 Users (Stress Peak)", "2.435 req", "76.25 RPS", "2.988.0 ms", "990.0 ms", "19.000.0 ms", "0.00%",
            "EXCEEDED", (185, 28, 28)
        )
    ]

    pdf.set_font("Helvetica", "", 7.3)
    for t_name, t_req, t_tput, t_avg, t_p50, t_p95, t_fail, t_sla, s_color in tier_data:
        pdf.cell(35, 5, t_name, border=1)
        pdf.cell(20, 5, t_req, border=1, align="C")
        pdf.cell(22, 5, t_tput, border=1, align="C")
        pdf.cell(22, 5, t_avg, border=1, align="C")
        pdf.cell(20, 5, t_p50, border=1, align="C")
        pdf.cell(24, 5, t_p95, border=1, align="C")
        pdf.cell(22, 5, t_fail, border=1, align="C")

        pdf.set_font("Helvetica", "B", 7.3)
        pdf.set_text_color(*s_color)
        pdf.cell(25, 5, t_sla, border=1, align="C", ln=1)
        pdf.set_font("Helvetica", "", 7.3)
        pdf.set_text_color(15, 23, 42)

    pdf.ln(4)

    # --------------------------------------------------------------------------
    # 4. ANALISIS MENDALAM TIAP TINGKATAN BEBAN
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "2. Analisis Perilaku Sistem per Tingkatan Skala", ln=1)

    tier_analysis = [
        (
            "Tier 1: 10 Concurrent Users (Kondisi Ideal Normal Operasional)",
            "Pada beban 10 pengguna simultan, backend merespons instan dengan latensi rata-rata 23.99 ms dan P95 hanya 89 ms. "
            "Kapasitas CPU dan memory server staging terpakai minimal (< 10%). Seluruh transaksi pemesanan dan telemetri berjalan mulus."
        ),
        (
            "Tier 2: 100 Concurrent Users (Kapasitas Puncak Reguler / Rush Hour Awal)",
            "Throughput naik 8.9x lipat secara linear dari 4.82 ke 42.79 RPS. Latensi P95 berada pada 600 ms, tetap berada "
            "di bawah ambang batas SLA toleransi (800 ms). Tingkat kegagalan 0.00% membuktikan pooling koneksi database dan thread server Golang sangat tangguh."
        ),
        (
            "Tier 3: 1.000 Concurrent Users (Uji Ketahanan Ekstrem / Breaking Point)",
            "Dengan lonjakan 1.000 virtual users secara masif (100 user/detik), throughput mencapai batas maksimal instance staging (76.25 RPS). "
            "Server TIDAK CRASH (0 kegagalan / HTTP 500), namun antrean request menyebabkan latensi P95 naik ke 19 detik pada endpoint captcha/auth. "
            "Ini mengonfirmasi bahwa 1 single instance dev server memiliki kapasitas aman maksimal di kisaran 100-150 concurrent users."
        )
    ]

    for a_title, a_desc in tier_analysis:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(14, 116, 144)
        pdf.cell(0, 4.5, a_title, ln=1)
        pdf.set_font("Helvetica", "", 7.3)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(190, 3.6, a_desc)
        pdf.ln(1)

    pdf.ln(2)

    # --------------------------------------------------------------------------
    # 5. PERBANDINGAN RESPON ENDPOINT KUNCI: 10 vs 100 vs 1000 USERS
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "3. Respon Latensi Endpoint Kunci Lintas Skala (Median Latency P50)", ln=1)

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(65, 5, "Endpoint API Teruji", border=1, fill=True)
    pdf.cell(35, 5, "Fungsi Bisnis", border=1, fill=True, align="C")
    pdf.cell(30, 5, "10 Users (P50)", border=1, fill=True, align="C")
    pdf.cell(30, 5, "100 Users (P50)", border=1, fill=True, align="C")
    pdf.cell(30, 5, "1000 Users (P50)", border=1, fill=True, align="C", ln=1)

    ep_compare = [
        ("POST /order/api/user/estimateFare", "Fare Engine Jarak", "7.0 ms", "9.0 ms", "940.0 ms"),
        ("POST /order/api/user/createOrder", "Order Booking Ojek", "7.2 ms", "12.0 ms", "1.000.0 ms"),
        ("POST /driver/api/v2/online", "GPS Telemetry Heartbeat", "8.0 ms", "10.0 ms", "970.0 ms"),
        ("GET /account/api/ecgo/wallet/status", "Saldo Dompet Driver", "11.0 ms", "12.0 ms", "920.0 ms"),
        ("GET /v5/users/diskon/list", "100% Free Swap Kupon", "9.0 ms", "10.0 ms", "960.0 ms"),
        ("POST /account/base/driver/driverLoginByOtp", "Login PIN Driver", "14.0 ms", "38.0 ms", "980.0 ms"),
    ]

    pdf.set_font("Helvetica", "", 7.2)
    for ep, func, u10, u100, u1000 in ep_compare:
        pdf.cell(65, 4.4, ep, border=1)
        pdf.cell(35, 4.4, func, border=1, align="C")
        pdf.cell(30, 4.4, u10, border=1, align="C")
        pdf.cell(30, 4.4, u100, border=1, align="C")
        pdf.cell(30, 4.4, u1000, border=1, align="C", ln=1)

    # ==========================================================================
    # HALAMAN 2: REKOMENDASI ARSITEKTUR PRODUKSI & PENGESAHAN
    # ==========================================================================
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "4. Rekomendasi Skalabilitas Produksi (Berdasarkan Uji 1.000 Users)", ln=1)

    recommendations = [
        (
            "1. Horizontal Pod Autoscaler (HPA) Kubernetes Berbasis Target 100 RPS/Replika:",
            "Kapasitas stabil 1 pod berada di angka 45-75 RPS. Untuk melayani 1.000 concurrent users aktif (estimasi 500-750 RPS), "
            "dibutuhkan konfigurasi auto-scaling minimal 10 hingga 15 replika pod pada cluster Kubernetes production."
        ),
        (
            "2. Optimasi Database Connection Pool (PostgreSQL / MySQL Max Open Conns):",
            "Pada uji 1.000 users, waktu tunggu respon meningkat karena antrean koneksi database. Tingkatkan `max_open_conns` "
            "dan pasang PgBouncer / ProxySQL untuk mendistribusikan query read-heavy (saldo dompet, daftar kupon swap)."
        ),
        (
            "3. Cache Geohash untuk Estimasi Tarif (Redis Memory Grid):",
            "Permintaan estimasi tarif naik menjadi 225 request pada uji 1.000 user. Terapkan caching tarif 15-30 detik pada Redis "
            "berdasarkan zona pickup/dropoff geohash agar perhitungan rute tidak menghabiskan siklus CPU backend secara berulang."
        ),
        (
            "4. Asynchronous Queue untuk Pendaftaran & Captcha Verification (RabbitMQ / Kafka):",
            "Endpoint captcha/auth mengalami antrean terpanjang saat lonjakan 1.000 users. Pisahkan logic validasi captcha ke worker "
            "asinkron atau gunakan layanan verifikasi captcha terdistribusi (Cloudflare Turnstile) untuk mereduksi beban internal."
        )
    ]

    for r_title, r_body in recommendations:
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 4.2, r_title, ln=1)
        pdf.set_font("Helvetica", "", 7.2)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(190, 3.6, r_body)
        pdf.ln(1)

    pdf.ln(4)

    # --------------------------------------------------------------------------
    # 5. KESIMPULAN AKHIR KELAYAKAN SISTEM
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "5. Kesimpulan Kelayakan Sistem (System Readiness Verdict)", ln=1)

    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(10, pdf.get_y(), 190, 22, 'DF')
    pdf.set_xy(13, pdf.get_y() + 2)
    pdf.set_font("Helvetica", "", 7.3)
    pdf.set_text_color(30, 41, 59)
    verdict_text = (
        "KESIMPULAN QA: Ekosistem EvMoto & ECGO SuperApps DINYATAKAN LAYAK DAN SIAP (PRODUCTION READY) untuk kapasitas "
        "hingga 100 concurrent users aktif per instance tunggal dengan SLA latensi < 600 ms. Ketahanan arsitektur backend terbukti sangat "
        "unggul karena mampu bertahan dari beban ekstrem 1.000 concurrent users tanpa satupun error 500 (0.00% failure rate). "
        "Dengan menerapkan rekomendasi HPA Kubernetes (10-15 pod), sistem akan mampu menangani 1.000+ pengguna secara simultan dengan lancar."
    )
    pdf.multi_cell(184, 3.8, verdict_text)

    pdf.set_y(pdf.get_y() + 6)

    # --------------------------------------------------------------------------
    # 6. LEMBAR PENGESAHAN & SIGN-OFF LAPORAN
    # --------------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "6. Lembar Pengesahan & Tanda Tangan Laporan", ln=1)

    box_w = 90
    box_h = 32
    y_sign = pdf.get_y() + 2

    # Kotak Penanggung Jawab QA
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(10, y_sign, box_w, box_h, 'DF')
    pdf.set_xy(13, y_sign + 2)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(box_w - 6, 4, "Disusun & Diuji Oleh:", ln=1)
    pdf.set_xy(13, y_sign + 18)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.cell(box_w - 6, 4, "Bhagus Arif Prayogo", ln=1)
    pdf.set_xy(13, y_sign + 23)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(box_w - 6, 4, "Senior QA Engineer", ln=1)

    # Kotak Mengetahui / Atasan (Management Sign-off)
    pdf.rect(110, y_sign, box_w, box_h, 'DF')
    pdf.set_xy(113, y_sign + 2)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(box_w - 6, 4, "Disetujui / Diketahui Oleh:", ln=1)
    pdf.set_xy(113, y_sign + 18)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.cell(box_w - 6, 4, "[ CTO / VP of Engineering / Tech Lead ]", ln=1)
    pdf.set_xy(113, y_sign + 23)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(box_w - 6, 4, "Engineering & Technology Management", ln=1)

    # Simpan File PDF ke Proyek
    pdf.output(str(PROJECT_PDF_PATH))
    print(f"✅ PDF berhasil dibuat di proyek: {PROJECT_PDF_PATH}")

    # Salin ke folder Downloads
    try:
        shutil.copy2(str(PROJECT_PDF_PATH), str(DOWNLOAD_PDF_PATH))
        print(f"📥 PDF berhasil disalin ke folder Downloads: {DOWNLOAD_PDF_PATH}")
    except Exception as e:
        print(f"⚠️ Gagal menyalin ke folder Downloads: {e}")

    # Salin ke folder Dokumen Resmi
    try:
        if DOCS_DIR.exists():
            shutil.copy2(str(PROJECT_PDF_PATH), str(DOCS_PDF_PATH))
            print(f"📁 PDF berhasil disalin ke Dokumen Resmi: {DOCS_PDF_PATH}")
    except Exception as e:
        print(f"⚠️ Gagal menyalin ke Dokumen Resmi: {e}")


if __name__ == "__main__":
    generate_pdf()
