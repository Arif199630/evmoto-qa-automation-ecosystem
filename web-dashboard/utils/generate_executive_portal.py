"""
=============================================================================
EXECUTIVE BUG TRACKER PORTAL GENERATOR (STANDALONE & PORTABLE)
=============================================================================
Menghasilkan berkas HTML mandiri (Single-File Standalone) dengan:
1. Bukti tangkapan layar (Evidence Screenshot) tertanam langsung dalam format Base64
2. Tanpa dependensi eksternal, dapat dibuka offline/online di semua browser (Chrome/Edge/Safari/HP)
3. Dilengkapi KPI Dashboard, Filter Dinamis, Galeri Gambar, dan Panduan Developer
4. Sangat mudah dibagikan ke atasan via Email, WhatsApp, atau Teams tanpa perlu setup
=============================================================================
"""

import os
import sys
import csv
import json
import base64
import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(ROOT_DIR, "reports")
CSV_PATH = os.path.join(REPORTS_DIR, "Bug_Tracker_EvMoto.csv")
PORTAL_PATH = os.path.join(REPORTS_DIR, "Executive_Bug_Tracker_Portal.html")


def image_to_base64(filepath):
    """Mengubah file gambar lokal menjadi Base64 Data URI agar tertanam mandiri."""
    if not filepath or not os.path.exists(filepath):
        return ""
    try:
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    except Exception:
        return ""


def generate_executive_portal():
    """Menyusun Executive Portal HTML mandiri."""
    records = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Konversi screenshot ke Base64
                abs_path = row.get("Path File Screenshot", "")
                if abs_path and os.path.exists(abs_path):
                    row["base64_screenshot"] = image_to_base64(abs_path)
                else:
                    # Coba cari di folder screenshots relatif
                    rel_name = os.path.basename(row.get("Evidence Screenshot Link", ""))
                    fallback_path = os.path.join(REPORTS_DIR, "screenshots", rel_name)
                    if os.path.exists(fallback_path):
                        row["base64_screenshot"] = image_to_base64(fallback_path)
                    else:
                        row["base64_screenshot"] = ""
                records.append(row)

    total_bugs = len(records)
    critical_count = sum(1 for r in records if r.get("Severity") == "Critical")
    major_count = sum(1 for r in records if r.get("Severity") == "Major")
    medium_count = sum(1 for r in records if r.get("Severity") == "Medium")
    open_count = sum(1 for r in records if r.get("Status") == "Open")

    records_json = json.dumps(records)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eVMOTO QA Automation - Executive Bug Tracker & Audit Report</title>
    <style>
        :root {{
            --primary: #1B365D;
            --accent: #2563EB;
            --bg-page: #F8FAFC;
            --surface: #FFFFFF;
            --border: #E2E8F0;
            --text-dark: #0F172A;
            --text-muted: #64748B;
            --danger: #DC2626;
            --warning: #EA580C;
            --success: #16A34A;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-page);
            color: var(--text-dark);
            line-height: 1.5;
            padding: 24px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header Banner */
        .executive-header {{
            background: linear-gradient(135deg, #1B365D 0%, #0F172A 100%);
            color: white;
            padding: 32px;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .header-left h1 {{
            font-size: 24px;
            font-weight: 700;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .header-left p {{
            font-size: 14px;
            color: #94A3B8;
            margin-top: 6px;
        }}
        .badge-live {{
            background: rgba(34, 197, 94, 0.2);
            color: #4ADE80;
            border: 1px solid rgba(34, 197, 94, 0.4);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }}
        .header-actions {{
            display: flex;
            gap: 12px;
        }}
        .btn-action {{
            background: rgba(255, 255, 255, 0.12);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 10px 18px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-action:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-1px);
        }}
        .btn-highlight {{
            background: #2563EB;
            border-color: #3B82F6;
        }}
        .btn-highlight:hover {{
            background: #1D4ED8;
        }}

        /* KPI Cards Grid */
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: var(--surface);
            padding: 20px;
            border-radius: 14px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            position: relative;
            overflow: hidden;
        }}
        .kpi-card::before {{
            content: '';
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 5px;
        }}
        .card-blue::before {{ background: #2563EB; }}
        .card-red::before {{ background: #DC2626; }}
        .card-orange::before {{ background: #EA580C; }}
        .card-yellow::before {{ background: #D97706; }}
        .card-green::before {{ background: #16A34A; }}

        .kpi-title {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }}
        .kpi-number {{
            font-size: 32px;
            font-weight: 800;
            margin-top: 6px;
            color: var(--text-dark);
        }}
        .kpi-sub {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        /* Navigation Tabs */
        .tab-bar {{
            display: flex;
            gap: 8px;
            border-bottom: 2px solid var(--border);
            margin-bottom: 20px;
        }}
        .tab-btn {{
            background: none;
            border: none;
            padding: 12px 20px;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s;
        }}
        .tab-btn.active {{
            color: var(--accent);
            border-bottom-color: var(--accent);
        }}
        .tab-btn:hover:not(.active) {{
            color: var(--text-dark);
        }}

        /* Content Sections */
        .tab-panel {{
            display: none;
        }}
        .tab-panel.active {{
            display: block;
        }}

        /* Search & Filter Bar */
        .filter-panel {{
            background: var(--surface);
            padding: 16px 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            display: flex;
            gap: 16px;
            align-items: center;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}
        .search-input {{
            flex: 1;
            min-width: 260px;
            padding: 10px 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            font-size: 14px;
            outline: none;
        }}
        .search-input:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }}
        .filter-select {{
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
            font-size: 13px;
            background: white;
            outline: none;
            cursor: pointer;
        }}

        /* Table Card */
        .table-card {{
            background: var(--surface);
            border-radius: 14px;
            border: 1px solid var(--border);
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }}
        .table-responsive {{
            overflow-x: auto;
            max-height: 700px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}
        thead th {{
            background: #0F172A;
            color: #F8FAFC;
            font-weight: 600;
            padding: 14px 16px;
            white-space: nowrap;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        tbody tr {{
            border-bottom: 1px solid #F1F5F9;
            transition: background 0.15s;
        }}
        tbody tr:hover {{
            background: #F8FAFC;
        }}
        tbody td {{
            padding: 14px 16px;
            vertical-align: middle;
        }}

        /* Badges */
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            text-align: center;
        }}
        .badge-critical {{ background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }}
        .badge-major {{ background: #FFEDD5; color: #9A3412; border: 1px solid #FED7AA; }}
        .badge-medium {{ background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }}
        .badge-minor {{ background: #E0F2FE; color: #075985; border: 1px solid #BAE6FD; }}
        .badge-open {{ background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }}

        .btn-view-evidence {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: #EFF6FF;
            color: #2563EB;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid #BFDBFE;
            transition: all 0.15s;
        }}
        .btn-view-evidence:hover {{
            background: #DBEAFE;
        }}

        /* Gallery Grid */
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 20px;
        }}
        .gallery-item {{
            background: white;
            border-radius: 12px;
            border: 1px solid var(--border);
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
        }}
        .gallery-thumb {{
            width: 100%;
            height: 220px;
            object-fit: cover;
            cursor: pointer;
            background: #0F172A;
            transition: transform 0.2s;
        }}
        .gallery-thumb:hover {{
            opacity: 0.95;
        }}
        .gallery-info {{
            padding: 16px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .gallery-tag {{
            font-size: 11px;
            font-weight: 700;
            color: var(--accent);
            text-transform: uppercase;
        }}
        .gallery-title {{
            font-size: 14px;
            font-weight: 600;
            margin: 6px 0;
            color: var(--text-dark);
        }}
        .gallery-meta {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        /* Modal Lightbox */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(4px);
            z-index: 99999;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}
        .modal-box {{
            background: white;
            border-radius: 16px;
            max-width: 1200px;
            width: 100%;
            max-height: 92vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
        }}
        .modal-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            border-bottom: 1px solid var(--border);
        }}
        .modal-scroll {{
            padding: 20px;
            overflow-y: auto;
            text-align: center;
            background: #0F172A;
        }}
        .modal-scroll img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}
        .close-btn {{
            background: none;
            border: none;
            font-size: 24px;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px;
        }}

        /* Info Alert Box */
        .share-banner {{
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .share-icon {{
            font-size: 28px;
        }}
        .share-text h4 {{
            font-size: 14px;
            color: #1E40AF;
            font-weight: 700;
        }}
        .share-text p {{
            font-size: 13px;
            color: #3B82F6;
            margin-top: 2px;
        }}

        @media print {{
            .tab-bar, .filter-panel, .header-actions, .share-banner {{ display: none !important; }}
            .tab-panel {{ display: block !important; }}
            body {{ padding: 0; background: white; }}
        }}
    </style>
</head>
<body>

    <div class="container">
        <!-- Banner Bagikan ke Atasan -->
        <div class="share-banner">
            <div class="share-icon">💡</div>
            <div class="share-text">
                <h4>PANDUAN BERBAGI KE ATASAN / STAKEHOLDER (TANPA RIBET):</h4>
                <p>Dokumen HTML ini bersifat <strong>100% mandiri (Single-File Portable)</strong> dengan seluruh bukti screenshot telah tertanam langsung (Base64). Anda dapat langsung melampirkan berkas <code>Executive_Bug_Tracker_Portal.html</code> ini melalui <strong>Email, WhatsApp, Slack, atau Google Drive</strong>. Atasan Anda dapat langsung mengklik dua kali untuk membukanya di browser apa pun tanpa perlu login atau instalasi apa pun!</p>
            </div>
        </div>

        <!-- Executive Header -->
        <div class="executive-header">
            <div class="header-left">
                <span class="badge-live">● QA AUTOMATION AUDIT - LIVE REPORT</span>
                <h1>🐞 eVMOTO Bug Tracker & Executive Portal</h1>
                <p>Framework: Page Object Model (POM) & 4 Pilar QA | Terakhir Diperbarui: {current_time} WIB</p>
            </div>
            <div class="header-actions">
                <a href="Bug_Tracker_EvMoto.xlsx" class="btn-action btn-highlight" download>
                    📊 Unduh Excel (.xlsx)
                </a>
                <a href="Bug_Tracker_EvMoto.csv" class="btn-action" download>
                    📥 Unduh CSV
                </a>
                <button class="btn-action" onclick="window.print()">
                    🖨️ Cetak / Simpan PDF
                </button>
            </div>
        </div>

        <!-- KPI Cards Grid -->
        <div class="kpi-row">
            <div class="kpi-card card-blue">
                <div class="kpi-title">Total Anomali / Bug</div>
                <div class="kpi-number">{total_bugs}</div>
                <div class="kpi-sub">Tercatat di seluruh modul</div>
            </div>
            <div class="kpi-card card-red">
                <div class="kpi-title">Critical (Blocker)</div>
                <div class="kpi-number" style="color: #DC2626;">{critical_count}</div>
                <div class="kpi-sub">Memerlukan atensi segera</div>
            </div>
            <div class="kpi-card card-orange">
                <div class="kpi-title">Major (High)</div>
                <div class="kpi-number" style="color: #EA580C;">{major_count}</div>
                <div class="kpi-sub">Fungsionalitas utama terdampak</div>
            </div>
            <div class="kpi-card card-yellow">
                <div class="kpi-title">Medium (Normal)</div>
                <div class="kpi-number" style="color: #D97706;">{medium_count}</div>
                <div class="kpi-sub">Validasi data & tampilan</div>
            </div>
            <div class="kpi-card card-green">
                <div class="kpi-title">Status Open</div>
                <div class="kpi-number" style="color: #16A34A;">{open_count}</div>
                <div class="kpi-sub">Siap ditugaskan ke developer</div>
            </div>
        </div>

        <!-- Tab Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-btn active" onclick="switchTab('tab-table')">📋 Tabel Tiket Bug (19 Kolom)</button>
            <button class="tab-btn" onclick="switchTab('tab-gallery')">📸 Galeri Bukti Tangkapan Layar (1080p)</button>
            <button class="tab-btn" onclick="switchTab('tab-summary')">📊 Analisis 4 Pilar QA</button>
        </div>

        <!-- TAB 1: TABEL TIKET BUG -->
        <div id="tab-table" class="tab-panel active">
            <div class="filter-panel">
                <input type="text" id="searchInput" class="search-input" placeholder="🔍 Cari berdasarkan Bug ID, Modul, Endpoint, atau Kata Kunci..." onkeyup="filterBugs()">
                <select id="platformSelect" class="filter-select" onchange="filterBugs()">
                    <option value="">Semua Platform</option>
                    <option value="Website">Website (Desktop)</option>
                    <option value="Mobile">Mobile Apps</option>
                </select>
                <select id="environmentSelect" class="filter-select" onchange="filterBugs()">
                    <option value="">Semua Environment</option>
                    <option value="Production">Production</option>
                    <option value="Dev">Dev / Staging</option>
                </select>
                <select id="severitySelect" class="filter-select" onchange="filterBugs()">
                    <option value="">Semua Severity</option>
                    <option value="Critical">Critical</option>
                    <option value="Major">Major</option>
                    <option value="Medium">Medium</option>
                    <option value="Minor">Minor</option>
                </select>
                <select id="pilarSelect" class="filter-select" onchange="filterBugs()">
                    <option value="">Semua 4 Pilar</option>
                    <option value="Pilar 1">Pilar 1: Positif True</option>
                    <option value="Pilar 2">Pilar 2: Positif False</option>
                    <option value="Pilar 3">Pilar 3: Negatif True</option>
                    <option value="Pilar 4">Pilar 4: Negatif False</option>
                </select>
            </div>

            <div class="table-card">
                <div class="table-responsive">
                    <table id="mainBugTable">
                        <thead>
                            <tr>
                                <th>Bug ID</th>
                                <th>Waktu</th>
                                <th>Modul / Fitur</th>
                                <th>Platform</th>
                                <th>Environment</th>
                                <th>Test Case & Fungsi</th>
                                <th>4 Pilar QA</th>
                                <th>Severity</th>
                                <th>Priority</th>
                                <th>Status</th>
                                <th>Ringkasan Masalah</th>
                                <th>Hasil Aktual / Pesan Kesalahan</th>
                                <th>Bukti Tangkapan Layar</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody">
                            <!-- Diisi via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 2: GALERI EVIDENCE SCREENSHOT -->
        <div id="tab-gallery" class="tab-panel">
            <div class="gallery-grid" id="galleryContainer">
                <!-- Diisi via JS -->
            </div>
        </div>

        <!-- TAB 3: ANALISIS 4 PILAR -->
        <div id="tab-summary" class="tab-panel">
            <div class="table-card" style="padding: 24px;">
                <h3 style="font-size: 18px; margin-bottom: 16px; color: var(--primary);">Distribusi Anomali Berdasarkan Filosofi 4 Pilar QA</h3>
                <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">
                    Metode 4 Pilar menjamin pengujian komprehensif dari segala sudut logika bisnis, proteksi keamanan, dan resiliensi sistem:
                </p>
                <table>
                    <thead>
                        <tr>
                            <th>Kategori Pilar</th>
                            <th>Filosofi Pengujian</th>
                            <th>Severity Umum</th>
                            <th>Status Penanganan</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Pilar 1: Positif True</strong></td>
                            <td>Memastikan respon sukses dan fungsionalitas utama bernilai BENAR saat data valid diberikan.</td>
                            <td><span class="badge badge-critical">Critical / Major</span></td>
                            <td>Prioritas P1 / P2</td>
                        </tr>
                        <tr>
                            <td><strong>Pilar 2: Positif False</strong></td>
                            <td>Memastikan antarmuka bersih dari error 500, whitelabel, dan aksi terkunci aman sebelum baris dipilih.</td>
                            <td><span class="badge badge-medium">Medium</span></td>
                            <td>Prioritas P3</td>
                        </tr>
                        <tr>
                            <td><strong>Pilar 3: Negatif True</strong></td>
                            <td>Memastikan proteksi aktif: penolakan akses tamu tanpa login dialihkan ke /login, validasi aktif.</td>
                            <td><span class="badge badge-major">Major</span></td>
                            <td>Prioritas P2</td>
                        </tr>
                        <tr>
                            <td><strong>Pilar 4: Negatif False</strong></td>
                            <td>Memastikan penyerang SQLi, manipulasi query, XSS script, rute fiktif DITOLAK TOTAL (False).</td>
                            <td><span class="badge badge-critical">Critical (Blocker)</span></td>
                            <td>Prioritas P1 (Security)</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Modal Pratinjau Bukti Screenshot -->
    <div class="modal-overlay" id="lightboxModal" onclick="closeLightbox(event)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div class="modal-top">
                <h3 id="lightboxTitle">📸 Bukti Tangkapan Layar (Evidence Screenshot)</h3>
                <button class="close-btn" onclick="closeLightbox(null)">&times;</button>
            </div>
            <div class="modal-scroll">
                <img id="lightboxImg" src="" alt="Screenshot Bukti Bug">
            </div>
        </div>
    </div>

    <script>
        const bugRecords = {records_json};

        function switchTab(tabId) {{
            document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.getElementById(tabId).classList.add("active");
            event.target.classList.add("active");
        }}

        function getSeverityBadge(sev) {{
            const map = {{
                "Critical": "badge-critical",
                "Major": "badge-major",
                "Medium": "badge-medium",
                "Minor": "badge-minor"
            }};
            return `<span class="badge ${{map[sev] || 'badge-minor'}}">${{sev || 'N/A'}}</span>`;
        }}

        function renderTableRows(data) {{
            const tbody = document.getElementById("tableBody");
            if (data.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; padding: 40px; color: #64748B;">Tidak ada anomali yang sesuai dengan filter.</td></tr>`;
                return;
            }}

            tbody.innerHTML = data.map(r => `
                <tr>
                    <td style="font-weight: 700; color: #1B365D;">${{r['Bug ID']}}</td>
                    <td style="white-space: nowrap; color: #64748B; font-size: 12px;">${{r.Timestamp}}</td>
                    <td style="font-weight: 600;">${{r['Modul / Fitur']}}</td>
                    <td><span class="badge" style="background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE;">${{r.Platform || 'Website (Desktop)'}}</span></td>
                    <td><span class="badge" style="background: ${{r.Environment === 'Production' ? '#ECFDF5; color: #047857; border: 1px solid #A7F3D0;' : '#FFFBEB; color: #B45309; border: 1px solid #FDE68A;'}}">${{r.Environment || 'Production'}}</span></td>
                    <td><code>${{r['Test Case & Fungsi']}}</code></td>
                    <td><span style="font-size: 12px;">${{r['4 Pilar QA']}}</span></td>
                    <td>${{getSeverityBadge(r.Severity)}}</td>
                    <td><span style="font-weight: 700; font-size: 12px;">${{r.Priority}}</span></td>
                    <td><span class="badge badge-open">${{r.Status}}</span></td>
                    <td style="max-width: 250px; font-size: 12px;">${{r['Ringkasan Bug (Summary)']}}</td>
                    <td style="max-width: 250px; font-size: 12px; color: #B91C1C;">${{r['Hasil Aktual / Error']}}</td>
                    <td style="text-align: center;">
                        ${{r.base64_screenshot 
                            ? `<button class="btn-view-evidence" onclick="openLightbox('${{r['Bug ID']}} - ${{r['Modul / Fitur']}}', '${{r.base64_screenshot}}')">📸 Lihat Bukti</button>`
                            : `<span style="color: #94A3B8; font-size: 11px;">Tidak ada</span>`
                        }}
                    </td>
                </tr>
            `).join("");
        }}

        function renderGallery(data) {{
            const container = document.getElementById("galleryContainer");
            const withScreenshots = data.filter(r => r.base64_screenshot);

            if (withScreenshots.length === 0) {{
                container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748B;">Belum ada screenshot yang tertanam.</div>`;
                return;
            }}

            container.innerHTML = withScreenshots.map(r => `
                <div class="gallery-item">
                    <img class="gallery-thumb" src="${{r.base64_screenshot}}" alt="${{r['Bug ID']}}" onclick="openLightbox('${{r['Bug ID']}} - ${{r['Modul / Fitur']}}', '${{r.base64_screenshot}}')">
                    <div class="gallery-info">
                        <div>
                            <span class="gallery-tag">${{r['Bug ID']}} • ${{r.Platform || 'Website'}} • ${{r.Environment || 'Production'}}</span>
                            <div class="gallery-title">${{r['Ringkasan Bug (Summary)']}}</div>
                        </div>
                        <div class="gallery-meta" style="margin-top: 10px;">
                            ${{getSeverityBadge(r.Severity)}} • Target URL: <code style="font-size: 11px;">${{r['Target URL']}}</code>
                        </div>
                    </div>
                </div>
            `).join("");
        }}

        function filterBugs() {{
            const q = document.getElementById("searchInput").value.toLowerCase();
            const plat = document.getElementById("platformSelect").value;
            const env = document.getElementById("environmentSelect").value;
            const sev = document.getElementById("severitySelect").value;
            const pil = document.getElementById("pilarSelect").value;

            const filtered = bugRecords.filter(r => {{
                const matchQ = Object.values(r).some(v => String(v).toLowerCase().includes(q));
                const matchPlat = !plat || (r.Platform && r.Platform.toLowerCase().includes(plat.toLowerCase()));
                const matchEnv = !env || (r.Environment && r.Environment.toLowerCase().includes(env.toLowerCase()));
                const matchSev = !sev || r.Severity === sev;
                const matchPil = !pil || (r['4 Pilar QA'] && r['4 Pilar QA'].includes(pil));
                return matchQ && matchPlat && matchEnv && matchSev && matchPil;
            }});

            renderTableRows(filtered);
            renderGallery(filtered);
        }}

        function openLightbox(title, imgSrc) {{
            document.getElementById("lightboxTitle").textContent = "📸 " + title;
            document.getElementById("lightboxImg").src = imgSrc;
            document.getElementById("lightboxModal").style.display = "flex";
        }}

        function closeLightbox(e) {{
            if (!e || e.target.id === "lightboxModal" || e.target.classList.contains("close-btn")) {{
                document.getElementById("lightboxModal").style.display = "none";
            }}
        }}

        // Inisialisasi awal
        renderTableRows(bugRecords);
        renderGallery(bugRecords);
    </script>
</body>
</html>
"""

    with open(PORTAL_PATH, mode="w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[ExecutivePortal] Sukses menghasilkan portal mandiri: {PORTAL_PATH}")
    print(f"[ExecutivePortal] Ukuran berkas: {os.path.getsize(PORTAL_PATH)} bytes dengan screenshot Base64.")
    return PORTAL_PATH


if __name__ == "__main__":
    generate_executive_portal()
