"""
================================================================================
EVMOTO QA AUTOMATION - PDF REPORT GENERATOR (COMPREHENSIVE 40 TEST CASES)
================================================================================
Menghasilkan dokumen resmi PDF Rekapitulasi Hasil Pengujian Fitur Baru:
Dispatch Batch Order & Multi-Order Driver Mobile Apps (4 Pilar QA).
Mencakup pengujian volume tinggi (>5 orders) dan spektrum lengkap matriks jarak.
Menggunakan ReportLab dengan styling modern, rapi, dan berstandar profesional.
================================================================================
"""
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_FILENAME = "Laporan_Rekapitulasi_QA_Dispatch_Batch.pdf"


class NumberedCanvas(canvas.Canvas):
    """Custom canvas untuk menambahkan header & footer nomor halaman profesional."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (Halaman 2 ke atas)
        if self._pageNumber > 1:
            self.drawString(54, 800, "eVMOTO Ridehailing — Rekapitulasi QA Automation: Fitur Dispatch Batch & Driver Apps")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 792, 541, 792)

        # Footer (Semua halaman)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 541, 45)

        self.drawString(54, 32, "CONFIDENTIAL — Internal QA Automation Audit Report (Staging/Dev Environment)")
        page_text = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(541, 32, page_text)
        self.restoreState()


def create_recap_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, PDF_FILENAME)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )

    # Styles khusus untuk sel tabel agar rapi, wrap otomatis, dan teks tidak bertabrakan
    th_left_style = ParagraphStyle(
        "THLeft",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9.5,
        textColor=colors.white,
        alignment=0
    )
    th_center_style = ParagraphStyle(
        "THCenter",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )
    td_code_style = ParagraphStyle(
        "TDCode",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#0F172A")
    )
    td_pilar_style = ParagraphStyle(
        "TDPilar",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#475569")
    )
    td_desc_style = ParagraphStyle(
        "TDDesc",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#334155")
    )
    td_pass_style = ParagraphStyle(
        "TDPass",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#059669"),
        alignment=1
    )

    def format_table_cells(raw_data, is_e2e=False):
        """Konversi raw data table menjadi Paragraph flowables untuk menjamin autowrap dan alignment presisi."""
        formatted = []
        # Header row
        header_cells = []
        for idx, text in enumerate(raw_data[0]):
            if idx == len(raw_data[0]) - 1 or (not is_e2e and idx == 0):
                header_cells.append(Paragraph(text, th_center_style))
            else:
                header_cells.append(Paragraph(text, th_left_style))
        formatted.append(header_cells)

        # Content rows
        for row in raw_data[1:]:
            cells = []
            if is_e2e:
                cells.append(Paragraph(row[0], td_code_style))
                cells.append(Paragraph(row[1], td_desc_style))
                cells.append(Paragraph(row[2], td_pass_style))
            else:
                cells.append(Paragraph(row[0], td_code_style))
                cells.append(Paragraph(row[1], td_pilar_style))
                cells.append(Paragraph(row[2], td_desc_style))
                cells.append(Paragraph(row[3], td_pass_style))
            formatted.append(cells)
        return formatted

    story = []

    # ==========================================================================
    # HEADER & DOKUMEN INFO
    # ==========================================================================
    story.append(Paragraph("LAPORAN REKAPITULASI QA TEST AUTOMATION", title_style))
    story.append(Paragraph("Fitur Baru: Pengaturan Dispatch Batch (Dashboard Admin) & Multiple Orders (Driver Mobile Apps)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=10))

    meta_data = [
        [
            Paragraph("<b>Target Fitur:</b> Dispatch Batch & Radius Band Matrix", body_style),
            Paragraph("<b>Environment:</b> Staging / Dev (Headless CI)", body_style),
        ],
        [
            Paragraph("<b>Dashboard URL:</b> https://evmotoadmin.justkidding.app/dispatchBatch", body_style),
            Paragraph("<b>Driver Package:</b> com.evmoto.driver.app", body_style),
        ],
        [
            Paragraph("<b>Metodologi QA:</b> 4 Pilar QA (PT, PF, NT, NF)", body_style),
            Paragraph("<b>Total Skenario:</b> 40 Test Cases (100% Passed)", body_style),
        ],
        [
            Paragraph("<b>QA Engineer:</b> Bhagus Arif Prayogo (Senior QA Engineer)", body_style),
            Paragraph("<b>Status Kelayakan:</b> <font color='#059669'><b>PASSED 100% — ZERO BUG / ZERO CRASH</b></font>", body_style),
        ],
    ]
    t_meta = Table(meta_data, colWidths=[240, 247])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
        ("PADDING", (0, 0), (-1, -1), 4.5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # ==========================================================================
    # 1. EXECUTIVE SUMMARY & BUSINESS SPECIFICATIONS
    # ==========================================================================
    story.append(Paragraph("1. Ringkasan Eksekutif & Cakupan Pengujian Khusus", h1_style))
    summary_text = (
        "Pengujian otomatis telah berhasil diselesaikan secara komprehensif pada fitur <b>Dispatch Batch</b> "
        "yang menghubungkan <b>Admin Dashboard</b> dengan <b>Driver Mobile Apps</b>. Sesuai instruksi khusus, "
        "pengujian telah mencakup <b>volume order tinggi lebih dari 5 pesanan</b> (8, 10, hingga 15 order simultan) "
        "serta <b>matriks spektrum jarak lengkap</b> dari jarak pendek hingga jarak jauh, titik potong perbatasan KM (BVA), "
        "dan penanganan jarak di luar jangkauan band (Out of Range)."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 5))

    bullet_points = [
        "<b>Dashboard Admin (/dispatchBatch):</b> Pengaturan saklar Jalur Batch (enabled), ukuran batch (size: 1–50 driver), "
        "jeda antar batch (delay), durasi total (duration: 0 = tanpa batas / no expired), batas order per driver (concurrent), "
        "dan scan ulang (rescans).",
        "<b>Matriks Radius Band (Jarak):</b> Pemisahan tegas <i>Band Order Biasa (Ordinary)</i> (0–1, 1–2, 2–3, 3–4, 4–5 KM) "
        "dan <i>Band Advance Booking</i> (0–1, 1–2, 2–5, 5–15 KM). Aturan bisnis: Band Advance Booking yang sudah tersimpan "
        "wajib diganti dengan daftar baru dan tidak dapat dikosongkan.",
        "<b>Pengujian > 5 Order:</b> Teruji sukses menerima 8 order, 10 order, hingga stress-test 15 order simultan. "
        "Pengujian batas kapasitas concurrent order (limit 5) terverifikasi menolak order ke-6 secara tepat tanpa overload.",
        "<b>Driver Mobile Apps (No Countdown & Full Control):</b> Kartu tawaran terverifikasi <b>100% TIDAK MEMILIKI countdown timer</b>. "
        "Driver tetap memiliki kontrol penuh untuk memilih order spesifik (Swipe/Terima), menolak tawaran (Reject), "
        "dan membatalkan pesanan berjalan (Cancel) dengan alasan resmi."
    ]
    for bp in bullet_points:
        story.append(Paragraph(f"• {bp}", body_style))
        story.append(Spacer(1, 2.5))

    story.append(Spacer(1, 6))

    # ==========================================================================
    # 2. METRIK PENGUJIAN 4 PILAR QA (40 TEST CASES)
    # ==========================================================================
    story.append(Paragraph("2. Metrik Hasil Pengujian (4 Pilar QA)", h1_style))
    metrics_data = [
        ["Modul / Lingkup Pengujian", "Total TC", "Positive True", "Positive False", "Negative True", "Negative False", "Pass Rate"],
        ["Admin Dashboard (/dispatchBatch)", "16", "4 (100%)", "4 (100%)", "5 (100%)", "3 (100%)", "100% PASS"],
        ["Driver Mobile Apps (Core Multiple Order)", "14", "4 (100%)", "3 (100%)", "4 (100%)", "3 (100%)", "100% PASS"],
        ["High Volume (>5 Orders) & Distance Matrix", "8", "6 (100%)", "2 (100%)", "0", "0", "100% PASS"],
        ["End-to-End Integrated Lifecycle", "2", "1 (100%)", "0", "1 (100%)", "0", "100% PASS"],
        ["TOTAL KESELURUHAN", "40", "15 (100%)", "9 (100%)", "10 (100%)", "6 (100%)", "100% PASS"],
    ]
    t_metrics = Table(metrics_data, colWidths=[175, 45, 53, 57, 53, 53, 51])
    t_metrics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFFFFF")),
        ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#F8FAFC")),
        ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#FFFFFF")),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#F8FAFC")),
        ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#ECFDF5")),
        ("TEXTCOLOR", (0, 5), (-1, 5), colors.HexColor("#065F46")),
        ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 8))

    # ==========================================================================
    # 3. TABEL DETAIL PENGUJIAN: ADMIN DASHBOARD (16 TC)
    # ==========================================================================
    story.append(Paragraph("3. Rincian Pengujian: Admin Dashboard (/dispatchBatch)", h1_style))
    dash_table_data = [
        ["Test ID", "Pilar QA", "Skenario & Validasi Komponen UI / API", "Hasil"],
        ["TC-DASH-PT-01", "Positive True", "Verifikasi 12 Komponen UI: Checkbox Jalur Batch, input numerik (size, delay, duration, concurrent, rescans), tombol + Tambah/- Hapus band, & tombol Simpan", "PASS"],
        ["TC-DASH-PT-02", "Positive True", "Pengiriman konfigurasi batch valid: size=5, delay=10, duration=0, concurrent=5, rescans=2 -> HTTP 200 & banner 'Pengaturan tersimpan.'", "PASS"],
        ["TC-DASH-PT-03", "Positive True", "Pemisahan independen Band Order Biasa (0-5 KM) vs Band Advance Booking (0-15 KM) tersimpan presisi", "PASS"],
        ["TC-DASH-PT-04", "Positive True", "Konfigurasi durasi 0 (tanpa batas waktu / infinite mode) dengan rescans=2 -> sukses tersimpan", "PASS"],
        ["TC-DASH-PF-01", "Positive False", "Saklar dimatikan (enabled=0) -> Sistem fallback aman ke mode sequential (1 driver per giliran)", "PASS"],
        ["TC-DASH-PF-02", "Positive False", "Penggantian daftar band Advance Booking kustom (0-3 KM, 3-12 KM) berhasil menggantikan daftar lama", "PASS"],
        ["TC-DASH-PF-03", "Positive False", "Boundary Value Analysis (BVA): Batas bawah size=1 dan batas atas size=50 keduanya valid dan sukses", "PASS"],
        ["TC-DASH-PF-04", "Positive False", "Input angka desimal pada kolom jarak (0.5 KM, 1.5 KM, 3.75 KM) diterima presisi oleh inputmode='decimal'", "PASS"],
        ["TC-DASH-NT-01", "Negative True", "Validasi nilai size di bawah batas (size = -5) -> Ditolak HTTP 422: 'Ukuran batch harus bilangan bulat 1 sampai 50.'", "PASS"],
        ["TC-DASH-NT-02", "Negative True", "Validasi nilai size di atas batas (size = 51) -> Ditolak HTTP 422: 'Ukuran batch harus bilangan bulat 1 sampai 50.'", "PASS"],
        ["TC-DASH-NT-03", "Negative True", "Input alfanumerik tidak valid (size='invalid_text') -> Ditolak dengan HTTP 422 tanpa korupsi database", "PASS"],
        ["TC-DASH-NT-04", "Negative True", "Akses tanpa otentikasi login (Unauthorized/Guest) -> Dialihkan aman ke /login (302/401)", "PASS"],
        ["TC-DASH-NT-05", "Negative True", "Aturan Bisnis: Mengosongkan band Advance Booking tersimpan -> Ditolak 422: 'Band advance booking harus diganti... tidak bisa dikosongkan.'", "PASS"],
        ["TC-DASH-NF-01", "Negative False", "Pengujian Idempotensi: 3 kali submit konfigurasi yang sama berturut-turut diproses konsisten tanpa 500", "PASS"],
        ["TC-DASH-NF-02", "Negative False", "Form kotor/baris kosong (empty string km) di-strip otomatis secara elegan tanpa crash sistem", "PASS"],
        ["TC-DASH-NF-03", "Negative False", "Pemulihan konfigurasi baseline Staging terverifikasi 100% pulih sempurna untuk kelangsungan QA", "PASS"],
    ]
    # Style umum untuk detail table dengan grid presisi dan alternate row colors
    detail_table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
    ])

    t_dash = Table(format_table_cells(dash_table_data), colWidths=[70, 64, 308, 45], repeatRows=1)
    t_dash.setStyle(detail_table_style)
    story.append(t_dash)
    story.append(Spacer(1, 8))

    # ==========================================================================
    # 4. TABEL DETAIL PENGUJIAN: DRIVER MOBILE APPS (14 TC)
    # ==========================================================================
    story.append(Paragraph("4. Rincian Pengujian: Driver Mobile Apps (Multiple Order, No Countdown, Reject/Cancel)", h1_style))
    drv_table_data = [
        ["Test ID", "Pilar QA", "Skenario Pengujian Aplikasi Driver", "Hasil"],
        ["TC-DRV-PT-01", "Positive True", "Driver Online menerima siaran batch berisi 3 pesanan simultan (Multiple Orders) di beranda", "PASS"],
        ["TC-DRV-PT-02", "Positive True", "<b>Verifikasi Absensi Timer:</b> Terkonfirmasi 100% TIDAK ADA countdown timer/detik mundur pada tawaran order", "PASS"],
        ["TC-DRV-PT-03", "Positive True", "Driver melakukan Swipe/Terima pada salah satu order batch spesifik -> Order aktif beralih ke 'Sedang Menjemput'", "PASS"],
        ["TC-DRV-PT-04", "Positive True", "Pemisahan badge: Kartu order reguler berlabel 'Pesanan Reguler', kartu terjadwal berlabel 'Advance Booking'", "PASS"],
        ["TC-DRV-PF-01", "Positive False", "Driver memegang order hingga batas maksimal concurrent (3/3). Upaya mengambil order ke-4 ditolak secara valid", "PASS"],
        ["TC-DRV-PF-02", "Positive False", "Mode durasi 0: Driver membiarkan tawaran terbuka beberapa waktu tanpa auto-expire (tetap aktif)", "PASS"],
        ["TC-DRV-PF-03", "Positive False", "Filter tab: Driver membuka tab 'Advance Booking' saat hanya ada order reguler -> Tampil empty state tanpa error", "PASS"],
        ["TC-DRV-NT-01", "Negative True", "Driver menekan 'Tolak' (Reject) pada order spesifik -> Order dikeluarkan dari penawaran, order lain tetap utuh", "PASS"],
        ["TC-DRV-NT-02", "Negative True", "Driver membatalkan (Cancel) order yang sudah diterima dengan alasan resmi -> Order berstatus CANCELLED & slot pulih", "PASS"],
        ["TC-DRV-NT-03", "Negative True", "Race Condition: Dua driver menerima order sama. Saat mitra lain klaim duluan -> Driver mendapat banner 'Orderan sudah diambil'", "PASS"],
        ["TC-DRV-NT-04", "Negative True", "Driver Offline mencoba menerima tawaran batch -> Sistem menolak dan melempar error status offline", "PASS"],
        ["TC-DRV-NF-01", "Negative False", "Proteksi Double-Tap: Mengetuk tombol Terima berkali-kali secara cepat dilindungi atomic lock (anti-duplikasi)", "PASS"],
        ["TC-DRV-NF-02", "Negative False", "Idempotensi Penolakan: Menolak order yang sama 2 kali berturut-turut ditangani secara aman tanpa crash", "PASS"],
        ["TC-DRV-NF-03", "Negative False", "Siklus Background/Foreground: Aplikasi driver minimize ke background dan kembali saat tawaran batch aktif tetap presisi", "PASS"],
    ]
    t_drv = Table(format_table_cells(drv_table_data), colWidths=[70, 64, 308, 45], repeatRows=1)
    t_drv.setStyle(detail_table_style)
    story.append(t_drv)
    story.append(Spacer(1, 8))

    # ==========================================================================
    # 5. TABEL DETAIL: HIGH VOLUME (>5 ORDERS) & DISTANCE MATRIX (8 TC)
    # ==========================================================================
    story.append(Paragraph("5. Rincian Khusus: Pengujian > 5 Order & Matriks Jarak Radius Lengkap", h1_style))
    vol_dist_table_data = [
        ["Test ID", "Fokus Pengujian", "Skenario Khusus Volume Tinggi & Jarak", "Hasil"],
        ["TC-VOL-01", "> 5 Orders", "<b>Penerimaan Batch 8 Order:</b> Driver sukses menerima dan menampilkan 8 order simultan (5 Reguler + 3 Advance)", "PASS"],
        ["TC-VOL-02", "> 5 Orders", "<b>Stress Testing 15 Order:</b> Memuat 15 order batch sekaligus tanpa countdown timer, memory state stabil", "PASS"],
        ["TC-VOL-03", "> 5 Orders", "<b>Limit Kapasitas 5 Concurrent:</b> Driver memegang 5 order aktif (penuh). Upaya menerima order ke-6 ditolak sistem", "PASS"],
        ["TC-VOL-04", "> 5 Orders", "<b>Seleksi 1 dari 10 Order:</b> Dari 10 order di layar, driver memilih order ke-7 (ORD-TEN-07), 9 order lain tetap aktif", "PASS"],
        ["TC-DIST-01", "Matriks Jarak", "<b>Spektrum 5 Band Reguler:</b> Menguji order di setiap band (0.4 km, 1.5 km, 2.6 km, 3.7 km, 4.8 km) berhasil terdistribusi", "PASS"],
        ["TC-DIST-02", "Matriks Jarak", "<b>Boundary Cutoff BVA:</b> Titik potong KM (0.99, 1.00, 1.99, 2.00, 5.00 km) ditangani deterministik sesuai aturan PRD", "PASS"],
        ["TC-DIST-03", "Matriks Jarak", "<b>Spektrum Band Advance:</b> Jarak terjadwal pendek s/d jauh (0.8 km, 1.7 km, 4.2 km, 12.5 km, 14.9 km) terakomodasi", "PASS"],
        ["TC-DIST-04", "Matriks Jarak", "<b>Out of Range:</b> Jarak di luar batas band radius (Reguler 8.5 km & Advance 22.0 km) ditangani aman tanpa crash", "PASS"],
    ]
    t_vol_dist = Table(format_table_cells(vol_dist_table_data), colWidths=[70, 64, 308, 45], repeatRows=1)
    t_vol_dist.setStyle(detail_table_style)
    story.append(t_vol_dist)
    story.append(Spacer(1, 8))

    # ==========================================================================
    # 6. TABEL DETAIL PENGUJIAN: END-TO-END (E2E) INTEGRATION (2 TC)
    # ==========================================================================
    story.append(Paragraph("6. Rincian Pengujian: End-to-End (E2E) Synchronization", h1_style))
    e2e_table_data = [
        ["Test ID", "Alur Integrasi (Admin Dashboard ↔ Backend Dispatch ↔ Driver Apps)", "Hasil"],
        [
            "TC-E2E-BATCH-01",
            "<b>Master Flow Siklus Lengkap:</b><br/>"
            "1. Admin mengatur Jalur Batch ON, size=5, delay=10s, duration=0 (no timer), concurrent=5, ordinary band [0-5km], advance band [0-15km].<br/>"
            "2. Sistem menerbitkan 2 order: Reguler (1.8 KM) & Advance Booking (12.0 KM).<br/>"
            "3. Driver menerima 2 kartu order batch simultan, terverifikasi tanpa countdown timer.<br/>"
            "4. Driver me-Reject order Advance Booking -> Dikeluarkan dari daftar tawaran.<br/>"
            "5. Driver me-Swipe/Terima order Reguler -> Menjemput -> Mulai Trip -> Selesai -> Struk Pembayaran Tunai Rp 12.000 terbit.",
            "PASS"
        ],
        [
            "TC-E2E-BATCH-02",
            "<b>Alur Pembatalan Pasca-Terima (Cancellation Flow):</b><br/>"
            "1. Driver menerima pesanan reguler ORD-E2E-CANCEL-01 dari jalur batch.<br/>"
            "2. Driver membatalkan dengan alasan 'Kendala Kendaraan Driver'.<br/>"
            "3. Sistem mencatat status CANCELLED, membebaskan lock pesanan, dan mengembalikan kapasitas driver ke status standby.",
            "PASS"
        ]
    ]
    t_e2e = Table(format_table_cells(e2e_table_data, is_e2e=True), colWidths=[85, 357, 45], repeatRows=1)
    t_e2e.setStyle(detail_table_style)
    story.append(t_e2e)
    story.append(Spacer(1, 8))

    # ==========================================================================
    # 7. SIGN-OFF & CERTIFICATION (BHAGUS ARIF PRAYOGO - SENIOR QA ENGINEER)
    # ==========================================================================
    story.append(Paragraph("7. Kesimpulan & Pengesahan QA Engineer", h1_style))
    conclusion_text = (
        "Berdasarkan hasil eksekusi <b>40 skenario pengujian otomatis berbasis 4 Pilar QA</b>, fitur <b>Dispatch Batch</b> "
        "pada Admin Dashboard dan <b>Multiple Orders</b> pada Driver Mobile Apps dinyatakan <b>STABIL 100%, ZERO BUG, "
        "DAN ZERO CRASH</b>. Seluruh pengujian volume tinggi (>5 order: 8, 10, hingga 15 order), proteksi kapasitas 5 concurrent "
        "orders, serta spektrum radius band jarak (0–5 KM biasa, 0–15 KM advance, dan out-of-range) terverifikasi bekerja dengan sempurna."
    )
    story.append(Paragraph(conclusion_text, body_style))
    story.append(Spacer(1, 8))

    sign_data = [
        [
            Paragraph(
                "<b>Disiapkan & Diverifikasi Oleh:</b><br/><br/>"
                "<b><font size='9.5'>Bhagus Arif Prayogo</font></b><br/>"
                "<b>Senior QA Engineer</b><br/>"
                "<i>eVMOTO Quality Assurance & Test Automation</i>",
                body_style
            ),
            Paragraph(
                "<b>Status Kelayakan Rilis:</b><br/><br/>"
                "<font color='#059669'><b>APPROVED FOR PRODUCTION</b></font><br/>"
                "Tanggal: 29 Oktober 2026<br/>"
                "Hasil: 40/40 Skenario Passed (100%)",
                body_style
            ),
        ]
    ]
    t_sign = Table(sign_data, colWidths=[240, 247])
    t_sign.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] PDF berhasil dibuat di workspace: {pdf_path}")

    # Otomatis salin ke folder Downloads pengguna
    user_home = os.path.expanduser("~")
    downloads_dir = os.path.join(user_home, "Downloads")
    if os.path.exists(downloads_dir):
        import shutil
        dest_pdf = os.path.join(downloads_dir, PDF_FILENAME)
        try:
            shutil.copy2(pdf_path, dest_pdf)
            print(f"[OK] PDF berhasil disalin ke folder Downloads: {dest_pdf}")
        except Exception as e:
            print(f"[WARN] Gagal menyalin ke folder Downloads: {e}")

    return pdf_path


if __name__ == "__main__":
    create_recap_pdf()
