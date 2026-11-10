"""
=============================================================================
ENTERPRISE BUG TRACKER ENGINE FOR EVMOTO TEST AUTOMATION
=============================================================================
Mengotomasi pencatatan anomali/bug pengujian langsung ke dalam spreadsheet:
1. Microsoft Excel (.xlsx) dengan styling profesional, KPI Dashboard, & formula
2. CSV terstandardisasi (UTF-8 BOM) untuk impor 1-klik ke Lark Base / Google Sheets
3. Interactive HTML Dashboard (Tampilan Excel Online / Lark Base interaktif + modal screenshot)
4. Pengambilan evidence screenshot otomatis saat terjadi Failure / Error
=============================================================================
"""

import os
import sys
import csv
import json
import time
import datetime
import traceback
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(ROOT_DIR, "reports")
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "screenshots")
EXCEL_PATH = os.path.join(REPORTS_DIR, "Bug_Tracker_EvMoto.xlsx")
CSV_PATH = os.path.join(REPORTS_DIR, "Bug_Tracker_EvMoto.csv")
HTML_PATH = os.path.join(REPORTS_DIR, "Bug_Tracker_EvMoto.html")

# Pastikan stdout mendukung UTF-8 di Windows konsol
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Pastikan folder laporan dan tangkapan layar selalu tersedia
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


class BugTracker:
    """Mesin otomatis pencatat bug & penyusun rekapitulasi pengujian."""

    HEADERS = [
        "Bug ID",
        "Timestamp",
        "Modul / Fitur",
        "Platform",
        "Environment",
        "Test Case & Fungsi",
        "4 Pilar QA",
        "Ringkasan Bug (Summary)",
        "Severity",
        "Priority",
        "Status",
        "Reporter",
        "Assignee",
        "Target URL",
        "Langkah Reproduksi",
        "Hasil Diharapkan (Expected)",
        "Hasil Aktual / Error",
        "Evidence Screenshot Link",
        "Path File Screenshot",
        "Stack Trace Teknis",
    ]

    @classmethod
    def get_existing_records(cls):
        """Membaca daftar bug yang sudah tercatat sebelumnya dari CSV atau Excel."""
        records = []
        if os.path.exists(CSV_PATH):
            try:
                with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append(row)
            except Exception:
                pass
        return records

    @classmethod
    def get_next_bug_id(cls):
        """Menghasilkan Bug ID unik berurutan (misal: BUG-EVMOTO-001)."""
        existing = cls.get_existing_records()
        max_num = 0
        for r in existing:
            bug_id = r.get("Bug ID", "")
            if bug_id.startswith("BUG-EVMOTO-"):
                try:
                    num = int(bug_id.replace("BUG-EVMOTO-", ""))
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"BUG-EVMOTO-{max_num + 1:03d}"

    @classmethod
    def classify_metadata(cls, test_method_name, docstring, error_type, error_msg):
        """
        Menganalisis kategori 4 Pilar, Severity, Priority, dan modul berdasarkan metadata pengujian.
        """
        combined = f"{test_method_name} {docstring or ''}".lower()

        # Deteksi Pilar
        if "pilar 1" in combined or "positif_true" in combined or "positif (true)" in combined:
            pilar = "Pilar 1: Positif True"
        elif "pilar 2" in combined or "positif_false" in combined or "positif (false)" in combined:
            pilar = "Pilar 2: Positif False"
        elif "pilar 3" in combined or "negatif_true" in combined or "negatif (true)" in combined:
            pilar = "Pilar 3: Negatif True"
        elif "pilar 4" in combined or "negatif_false" in combined or "negatif (false)" in combined:
            pilar = "Pilar 4: Negatif False"
        else:
            pilar = "Pilar Umum: Fungsionalitas"

        # Deteksi Severity & Priority
        # Security/SQLi/XSS/Auth atau Crash fatal = Critical
        is_security = any(k in combined for k in ["sqli", "xss", "injeksi", "keamanan", "logout", "unauthorized"])
        is_critical_feature = any(k in combined for k in ["login", "transaksi", "order", "withdrawal", "price", "500"])

        if is_security or (is_critical_feature and "pilar 1" in combined):
            severity = "Critical"
            priority = "P1 - Blocker"
            assignee = "Backend & Security Team"
        elif "pilar 1" in combined or "pilar 3" in combined:
            severity = "Major"
            priority = "P2 - High"
            assignee = "Backend Team"
        elif "pilar 2" in combined:
            severity = "Medium"
            priority = "P3 - Medium"
            assignee = "Frontend Team"
        else:
            severity = "Minor"
            priority = "P4 - Low"
            assignee = "UI/UX & QA Team"

        return pilar, severity, priority, assignee

    @classmethod
    def extract_module_name(cls, test_instance):
        """Mendapatkan nama modul yang ramah dibaca dari class pengujian."""
        class_name = test_instance.__class__.__name__
        module_path = getattr(test_instance, "__module__", "")

        mapping = {
            "TestHalamanLogin": "Modul 01: Halaman Login",
            "TestLoginBugSimulation": "Modul 01: Halaman Login",
            "TestHalamanBeranda": "Modul 02: Home Page / Blackboard",
            "TestAccountCancellation": "Modul 03: Account Cancellation",
            "TestSystemManagement": "Modul 04: System Management",
            "TestEnterpriseManagement": "Modul 05: Enterprise Management",
            "TestUserManagement": "Modul 06: User Management",
            "TestAgreementManagement": "Modul 07: Basic Information & Agreement",
            "TestUrbanManagement": "Modul 08: Urban Management",
            "TestDriverManagement": "Modul 09: Driver Management",
            "TestVehicleManagement": "Modul 10: Vehicle Management",
            "TestBranchManagement": "Modul 11: Branch Management",
            "TestFranchiseeManagement": "Modul 12: Franchisee Management",
            "TestTravelOrderManagement": "Modul 13: Travel Order Management",
            "TestAppManagement": "Modul 14: App Management",
            "TestWithdrawalManagement": "Modul 15: Withdrawal Management",
            "TestCommentManagement": "Modul 16: Comment Management",
            "TestSystemSetup": "Modul 17: System Setup",
            "TestComplaintManagement": "Modul 18: Complaint Management",
            "TestProfileNavigation": "Modul 19: Profile & Top Navigation",
            "TestSensitiveWordManagement": "Modul 20: Sensitive Word Management",
            "TestFeedbackManagement": "Modul 21: Feedback Management",
            "TestVersionManagement": "Modul 22: Version Management",
            "TestActivityManagement": "Modul 23: Activity Management",
            "TestVehicleModelSetting": "Modul 24: Vehicle Model Setting",
            "TestPriceControl": "Modul 25: Price Control Management",
        }
        return mapping.get(class_name, f"Modul Pengujian ({class_name})")

    @classmethod
    def capture_screenshot(cls, driver, bug_id, test_name):
        """Mengambil tangkapan layar browser Selenium saat terjadi kesalahan."""
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_test_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in test_name)
        filename = f"{bug_id}_{sanitized_test_name}_{timestamp_str}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)

        if driver:
            try:
                # Simpan tangkapan layar langsung dari instans browser aktif
                driver.save_screenshot(filepath)
                return filepath, os.path.join("screenshots", filename)
            except Exception as e:
                print(f"[BugTracker] Gagal mengambil tangkapan layar: {e}")

        # Cadangan jika driver tidak dapat mengambil tangkapan layar
        return "", ""

    @classmethod
    def record_bug(cls, test_instance, error_info, failure_type="Failure"):
        """
        Fungsi inti untuk mencatat bug yang terjadi ke Excel, CSV, dan HTML secara otomatis.
        """
        try:
            test_method_name = getattr(test_instance, "_testMethodName", str(test_instance))
            test_func = getattr(test_instance, test_method_name, None)
            docstring = test_func.__doc__.strip() if test_func and test_func.__doc__ else ""

            # Dapatkan instans driver
            driver = getattr(test_instance, "driver", None)
            if not driver and hasattr(test_instance.__class__, "driver"):
                driver = getattr(test_instance.__class__, "driver")
            if not driver:
                try:
                    from config import Config
                    driver = getattr(Config, "active_driver", None)
                except Exception:
                    pass

            # Parse exception info
            exc_type, exc_val, exc_tb = error_info
            err_type_str = exc_type.__name__ if exc_type else failure_type
            raw_msg = str(exc_val) if exc_val else "Pengujian gagal tanpa pesan error rinci"
            if " : " in raw_msg:
                # Prioritaskan pesan spesifik dari assertion QA
                err_msg_str = raw_msg.split(" : ")[-1].strip()
            elif len(raw_msg) > 300:
                err_msg_str = raw_msg[:300].strip() + "..."
            else:
                err_msg_str = raw_msg
            tb_formatted = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))

            # Ambil URL & Environment saat error
            current_url = Config.get_base_url() if ("Config" in globals() or "Config" in locals()) else "https://dashboard.evmotoid.com"
            page_title = "EvMoto Admin"
            if driver:
                try:
                    current_url = driver.current_url
                    page_title = driver.title
                except Exception:
                    pass

            # Metadata klasifikasi
            bug_id = cls.get_next_bug_id()
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            module_name = cls.extract_module_name(test_instance)
            pilar, severity, priority, assignee = cls.classify_metadata(
                test_method_name, docstring, err_type_str, err_msg_str
            )

            # Evidence Screenshot
            abs_screenshot, rel_screenshot = cls.capture_screenshot(driver, bug_id, test_method_name)

            # Ringkasan & Langkah Reproduksi
            summary = docstring.split("\n")[0] if docstring else f"Kegagalan pada {test_method_name}"
            expected_result = "Elemen dan logika sistem beroperasi normal sesuai spesifikasi pengujian."
            if "login" in module_name.lower() or "login" in test_method_name.lower():
                expected_result = "Sistem berhasil mengautentikasi kredensial administrator, menerbitkan token sesi valid, dan mengarahkan pengguna ke dashboard /blackboard."
                steps = (
                    f"1. Buka browser dan navigasi ke URL Login: {current_url}\n"
                    f"2. Masukkan username administrator (dari .env, tidak ditulis di laporan)\n"
                    f"3. Masukkan kata sandi administrator (dari .env, tidak ditulis di laporan)\n"
                    f"4. Tekan tombol 'Log In' untuk mengirim permintaan autentikasi.\n"
                    f"5. Sistem memverifikasi token dan callback respon server.\n"
                    f"6. Amati perilaku sistem: terjadi anomali '{err_type_str}' pada form login."
                )
            elif "URL harus" in err_msg_str:
                expected_result = "Navigasi URL dan komponen halaman harus valid sesuai endpoint yang dituju."
                steps = (
                    f"1. Akses portal EvMoto Admin pada URL ({current_url}).\n"
                    f"2. Pastikan akun admin terotentikasi.\n"
                    f"3. Jalankan pengujian fungsi '{test_method_name}'.\n"
                    f"4. Amati respon navigasi URL dan komponen halaman."
                )
            else:
                steps = (
                    f"1. Akses portal EvMoto Admin pada URL ({current_url}).\n"
                    f"2. Pastikan akun admin terotentikasi.\n"
                    f"3. Jalankan pengujian fungsi '{test_method_name}'.\n"
                    f"4. Amati respon UI dan server: ditemukan anomali '{err_type_str}'."
                )

            # Konfigurasi Platform & Environment
            platform_val = "Website (Desktop)"
            env_val = "Production"
            try:
                from config import Config
                platform_val = getattr(Config, "PLATFORM", "Website (Desktop)")
                env_val = getattr(Config, "ENVIRONMENT", "Production")
            except Exception:
                pass

            # Buat record data lengkap
            record = {
                "Bug ID": bug_id,
                "Timestamp": now_str,
                "Modul / Fitur": module_name,
                "Platform": platform_val,
                "Environment": env_val,
                "Test Case & Fungsi": f"{test_method_name}()",
                "4 Pilar QA": pilar,
                "Ringkasan Bug (Summary)": summary,
                "Severity": severity,
                "Priority": priority,
                "Status": "Open",
                "Reporter": "QA Automation (<PROD_USER>)",
                "Assignee": assignee,
                "Target URL": current_url,
                "Langkah Reproduksi": steps,
                "Hasil Diharapkan (Expected)": expected_result,
                "Hasil Aktual / Error": f"{err_type_str}: {err_msg_str}",
                "Evidence Screenshot Link": rel_screenshot if rel_screenshot else "Screenshot tidak tersedia",
                "Path File Screenshot": abs_screenshot if abs_screenshot else "-",
                "Stack Trace Teknis": tb_formatted[:1000] if len(tb_formatted) > 1000 else tb_formatted,
            }

            # Simpan ke CSV
            cls._append_to_csv(record)

            # Simpan ke Excel dengan Styling Tingkat Enterprise
            cls._update_excel()

            # Render Ulang Interactive HTML Dashboard
            cls._render_html_dashboard()

            # Render Standalone Executive Portal (dengan Base64 screenshot mandiri untuk atasan)
            try:
                from utils.generate_executive_portal import generate_executive_portal
                generate_executive_portal()
            except Exception:
                pass

            # Sinkronisasi opsional ke Lark Webhook jika URL tersedia
            try:
                from utils.lark_sync import send_bug_to_lark_webhook
                send_bug_to_lark_webhook(record)
            except Exception:
                pass

            # Sinkronisasi opsional langsung ke Lark Base (Bitable) Cloud API jika token dikonfigurasi
            try:
                from utils.lark_bitable_sync import push_record_to_lark_bitable
                push_record_to_lark_bitable(record)
            except Exception:
                pass

            # Tampilkan informasi di konsol dengan format rapi
            print("\n" + "=" * 80)
            print("[BUG TRACKER ENGINE] ANOMALI TERDETEKSI & BERHASIL DICATAT SECARA OTOMATIS!")
            print(f"   -> Bug ID       : {bug_id}")
            print(f"   -> Modul        : {module_name}")
            print(f"   -> Test Method  : {test_method_name}")
            print(f"   -> Klasifikasi  : {pilar} | {severity} ({priority})")
            print(f"   -> Screenshot   : {rel_screenshot if rel_screenshot else 'None'}")
            print(f"   -> File Excel   : reports/Bug_Tracker_EvMoto.xlsx")
            print(f"   -> Impor Lark   : reports/Bug_Tracker_EvMoto.csv")
            print("=" * 80 + "\n")

            return record

        except Exception as e:
            print(f"[BugTracker] Peringatan: Terjadi kesalahan saat mencatat bug: {e}")
            traceback.print_exc()
            return None

    @classmethod
    def _append_to_csv(cls, record):
        """Menambahkan satu baris data ke file CSV (UTF-8 dengan BOM)."""
        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=cls.HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

    @classmethod
    def _update_excel(cls):
        """Menyusun ulang file Excel (.xlsx) dengan multi-sheet, format styling, dan formula KPI."""
        records = cls.get_existing_records()
        wb = Workbook()

        # ==========================================
        # TAB 1: DASHBOARD & KPI SUMMARY
        # ==========================================
        ws_dash = wb.active
        ws_dash.title = "Dashboard & KPI"
        ws_dash.views.sheetView[0].showGridLines = True

        # Palet Warna Korporat
        header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
        card_fill_blue = PatternFill(start_color="EBF4FF", end_color="EBF4FF", fill_type="solid")
        card_fill_red = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        card_fill_orange = PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid")
        card_fill_yellow = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        card_fill_green = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        card_fill_gray = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")

        font_title = Font(name="Segoe UI", size=16, bold=True, color="1B365D")
        font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="4B5563")
        font_kpi_num = Font(name="Segoe UI", size=20, bold=True, color="1F2937")
        font_kpi_label = Font(name="Segoe UI", size=9, bold=True, color="4B5563")
        font_section = Font(name="Segoe UI", size=12, bold=True, color="1B365D")
        font_table_hdr = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        font_table_cell = Font(name="Segoe UI", size=10, color="1F2937")

        thin_border = Border(
            left=Side(style="thin", color="D1D5DB"),
            right=Side(style="thin", color="D1D5DB"),
            top=Side(style="thin", color="D1D5DB"),
            bottom=Side(style="thin", color="D1D5DB"),
        )

        # Header Title
        ws_dash["B2"] = "EVMOTO TEST AUTOMATION - BUG TRACKER EXECUTIVE DASHBOARD"
        ws_dash["B2"].font = font_title
        ws_dash["B3"] = f"Terintegrasi Otomatis | Terakhir Diperbarui: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB"
        ws_dash["B3"].font = font_subtitle

        # Hitung Metrik
        total_bugs = len(records)
        critical_count = sum(1 for r in records if r.get("Severity") == "Critical")
        major_count = sum(1 for r in records if r.get("Severity") == "Major")
        medium_count = sum(1 for r in records if r.get("Severity") == "Medium")
        minor_count = sum(1 for r in records if r.get("Severity") == "Minor")
        open_count = sum(1 for r in records if r.get("Status") == "Open")

        # KPI Cards (Baris 5-6)
        cards = [
            ("B", "TOTAL BUGS", total_bugs, card_fill_blue, "1D4ED8"),
            ("D", "CRITICAL (BLOCKER)", critical_count, card_fill_red, "B91C1C"),
            ("F", "MAJOR (HIGH)", major_count, card_fill_orange, "C2410C"),
            ("H", "MEDIUM (NORMAL)", medium_count, card_fill_yellow, "B45309"),
            ("J", "MINOR (LOW)", minor_count, card_fill_gray, "4B5563"),
            ("L", "STATUS OPEN", open_count, card_fill_green, "15803D"),
        ]

        for col, label, val, fill, text_color in cards:
            c1 = f"{col}5"
            c2 = f"{col}6"
            ws_dash[c1] = label
            ws_dash[c1].font = font_kpi_label
            ws_dash[c1].alignment = Alignment(horizontal="center", vertical="center")
            ws_dash[c1].fill = fill
            ws_dash[c1].border = thin_border

            ws_dash[c2] = val
            ws_dash[c2].font = Font(name="Segoe UI", size=18, bold=True, color=text_color)
            ws_dash[c2].alignment = Alignment(horizontal="center", vertical="center")
            ws_dash[c2].fill = fill
            ws_dash[c2].border = thin_border

        # Distribusi Berdasarkan 4 Pilar QA (Baris 9)
        ws_dash["B9"] = "DISTRIBUSI BUG BERDASARKAN 4 PILAR TESTING"
        ws_dash["B9"].font = font_section

        pilar_headers = ["Pilar QA", "Deskripsi Filosofi", "Jumlah Bug", "Persentase (%)"]
        for idx, h in enumerate(pilar_headers, start=2):
            cell = ws_dash.cell(row=10, column=idx, value=h)
            cell.font = font_table_hdr
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        pilar_list = [
            ("Pilar 1: Positif True", "Memastikan aksi normal menghasilkan kondisi True valid"),
            ("Pilar 2: Positif False", "Memastikan kondisi normal bebas dari error 500 & anomali"),
            ("Pilar 3: Negatif True", "Memastikan proteksi keamanan & penolakan data aktif"),
            ("Pilar 4: Negatif False", "Memastikan injeksi SQLi, XSS, & manipulasi ditolak"),
        ]

        for row_idx, (p_name, p_desc) in enumerate(pilar_list, start=11):
            count = sum(1 for r in records if p_name in r.get("4 Pilar QA", ""))
            pct = f"{(count / total_bugs * 100):.1f}%" if total_bugs > 0 else "0.0%"

            ws_dash.cell(row=row_idx, column=2, value=p_name).font = font_table_cell
            ws_dash.cell(row=row_idx, column=3, value=p_desc).font = font_table_cell
            ws_dash.cell(row=row_idx, column=4, value=count).font = font_table_cell
            ws_dash.cell(row=row_idx, column=5, value=pct).font = font_table_cell

            for c in range(2, 6):
                ws_dash.cell(row=row_idx, column=c).border = thin_border
                if c in (4, 5):
                    ws_dash.cell(row=row_idx, column=c).alignment = Alignment(horizontal="center")

        # Lebar Kolom Dashboard
        col_widths_dash = {"A": 3, "B": 24, "C": 35, "D": 22, "E": 18, "F": 22, "G": 3, "H": 22, "I": 3, "J": 20, "K": 3, "L": 20}
        for col_letter, width in col_widths_dash.items():
            ws_dash.column_dimensions[col_letter].width = width

        # ==========================================
        # TAB 2: BUG TRACKER DETAIL LIST
        # ==========================================
        ws_bugs = wb.create_sheet(title="Bug Tracker")
        ws_bugs.views.sheetView[0].showGridLines = True
        ws_bugs.freeze_panes = "A2"

        # Tulis Header
        for col_idx, header_text in enumerate(cls.HEADERS, start=1):
            cell = ws_bugs.cell(row=1, column=col_idx, value=header_text)
            cell.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border

        ws_bugs.row_dimensions[1].height = 28

        # Styling Nilai & Badge
        fill_red = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        fill_orange = PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid")
        fill_yellow = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        fill_blue = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
        fill_green = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

        font_red = Font(name="Segoe UI", size=9, bold=True, color="991B1B")
        font_orange = Font(name="Segoe UI", size=9, bold=True, color="9A3412")
        font_yellow = Font(name="Segoe UI", size=9, bold=True, color="92400E")
        font_blue = Font(name="Segoe UI", size=9, bold=True, color="075985")
        font_green = Font(name="Segoe UI", size=9, bold=True, color="166534")

        # Tulis Baris Data
        for row_idx, r in enumerate(records, start=2):
            ws_bugs.row_dimensions[row_idx].height = 22
            for col_idx, col_name in enumerate(cls.HEADERS, start=1):
                val = r.get(col_name, "")
                cell = ws_bugs.cell(row=row_idx, column=col_idx, value=val)
                cell.font = Font(name="Segoe UI", size=9, color="1F2937")
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")

                # Format Khusus Berdasarkan Kolom
                if col_name in ("Bug ID", "Timestamp", "Priority", "Platform", "Environment"):
                    cell.alignment = Alignment(horizontal="center", vertical="center")

                elif col_name == "Severity":
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    if val == "Critical":
                        cell.fill = fill_red
                        cell.font = font_red
                    elif val == "Major":
                        cell.fill = fill_orange
                        cell.font = font_orange
                    elif val == "Medium":
                        cell.fill = fill_yellow
                        cell.font = font_yellow
                    elif val == "Minor":
                        cell.fill = fill_blue
                        cell.font = font_blue

                elif col_name == "Status":
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.fill = fill_green
                    cell.font = font_green

                elif col_name == "Evidence Screenshot Link":
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    if val and val != "Screenshot tidak tersedia":
                        cell.hyperlink = val
                        cell.value = "Buka Screenshot"
                        cell.font = Font(name="Segoe UI", size=9, color="2563EB", underline="single")

                elif col_name in ("Ringkasan Bug (Summary)", "Langkah Reproduksi", "Hasil Diharapkan (Expected)", "Hasil Aktual / Error", "Stack Trace Teknis"):
                    cell.alignment = Alignment(vertical="center", wrap_text=True)

        # Aktifkan AutoFilter pada tabel Bug Tracker
        if len(records) > 0:
            ws_bugs.auto_filter.ref = f"A1:{get_column_letter(len(cls.HEADERS))}{len(records) + 1}"

        # Pengaturan Lebar Kolom Otomatis
        fixed_widths = {
            "Bug ID": 16,
            "Timestamp": 19,
            "Modul / Fitur": 28,
            "Platform": 20,
            "Environment": 16,
            "Test Case & Fungsi": 32,
            "4 Pilar QA": 22,
            "Ringkasan Bug (Summary)": 38,
            "Severity": 13,
            "Priority": 15,
            "Status": 12,
            "Reporter": 22,
            "Assignee": 24,
            "Target URL": 32,
            "Langkah Reproduksi": 40,
            "Hasil Diharapkan (Expected)": 35,
            "Hasil Aktual / Error": 38,
            "Evidence Screenshot Link": 20,
            "Path File Screenshot": 35,
            "Stack Trace Teknis": 40,
        }
        for col_idx, col_name in enumerate(cls.HEADERS, start=1):
            letter = get_column_letter(col_idx)
            ws_bugs.column_dimensions[letter].width = fixed_widths.get(col_name, 20)

        # Simpan Workbook
        wb.save(EXCEL_PATH)

    @classmethod
    def _render_html_dashboard(cls):
        """
        Menyusun dashboard interaktif HTML (tampilan bergaya Excel Online & Lark Base).
        Menyediakan pencarian instan, filter status/severity, dan modal pratinjau screenshot.
        """
        records = cls.get_existing_records()
        records_json = json.dumps(records)

        html_template = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EvMoto Bug Tracker - Excel Online & Lark Base Interactive View</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #1B365D;
            --lark-blue: #3370FF;
            --bg-light: #F8FAFC;
            --border-color: #E2E8F0;
            --text-main: #0F172A;
            --text-muted: #64748B;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-light);
            color: var(--text-main);
            padding: 24px;
        }}
        .header-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
            padding: 20px 24px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 24px;
            border: 1px solid var(--border-color);
        }}
        .header-title h1 {{
            font-size: 20px;
            font-weight: 700;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header-title p {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }}
        .header-actions {{
            display: flex;
            gap: 12px;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 16px;
            font-size: 13px;
            font-weight: 600;
            border-radius: 8px;
            text-decoration: none;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }}
        .btn-primary {{
            background: var(--lark-blue);
            color: white;
        }}
        .btn-primary:hover {{ background: #2354c4; }}
        .btn-secondary {{
            background: #F1F5F9;
            color: #334155;
            border: 1px solid #CBD5E1;
        }}
        .btn-secondary:hover {{ background: #E2E8F0; }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: white;
            padding: 16px 20px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        .kpi-label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .kpi-val {{
            font-size: 26px;
            font-weight: 700;
            margin-top: 6px;
        }}
        .critical-val {{ color: #DC2626; }}
        .major-val {{ color: #EA580C; }}
        .medium-val {{ color: #D97706; }}
        .minor-val {{ color: #2563EB; }}
        .open-val {{ color: #16A34A; }}

        /* Table Filter Controls */
        .controls-bar {{
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
            background: white;
            padding: 14px 20px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            align-items: center;
        }}
        .search-box {{
            flex: 1;
            position: relative;
        }}
        .search-box input {{
            width: 100%;
            padding: 9px 14px;
            font-size: 13px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            outline: none;
        }}
        .search-box input:focus {{
            border-color: var(--lark-blue);
            box-shadow: 0 0 0 3px rgba(51, 112, 255, 0.15);
        }}
        .filter-select {{
            padding: 9px 14px;
            font-size: 13px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: white;
            outline: none;
            cursor: pointer;
        }}

        /* Table Container */
        .table-card {{
            background: white;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .table-responsive {{
            overflow-x: auto;
            max-height: 650px;
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
            padding: 12px 14px;
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
            padding: 12px 14px;
            vertical-align: middle;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
            text-align: center;
        }}
        .badge-critical {{ background: #FEE2E2; color: #991B1B; }}
        .badge-major {{ background: #FFEDD5; color: #9A3412; }}
        .badge-medium {{ background: #FEF3C7; color: #92400E; }}
        .badge-minor {{ background: #E0F2FE; color: #075985; }}
        .badge-open {{ background: #DCFCE7; color: #166534; }}

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
            text-decoration: none;
            cursor: pointer;
            border: 1px solid #BFDBFE;
        }}
        .btn-view-evidence:hover {{
            background: #DBEAFE;
        }}

        /* Modal Preview Screenshot */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.75);
            z-index: 9999;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}
        .modal-content {{
            background: white;
            border-radius: 14px;
            max-width: 1000px;
            width: 100%;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2);
        }}
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            border-bottom: 1px solid var(--border-color);
        }}
        .modal-body {{
            padding: 20px;
            overflow-y: auto;
            text-align: center;
            background: #000;
        }}
        .modal-body img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .close-modal {{
            cursor: pointer;
            font-size: 24px;
            color: var(--text-muted);
            background: none;
            border: none;
        }}
    </style>
</head>
<body>

    <div class="header-bar">
        <div class="header-title">
            <h1>🐞 EvMoto Automated Bug Tracker</h1>
            <p>Sistem Pelacak Bug Otomatis Terintegrasi (Excel Online, Lark Base & Screenshot Evidance)</p>
        </div>
        <div class="header-actions">
            <a href="Bug_Tracker_EvMoto.xlsx" class="btn btn-primary" download>
                📥 Unduh Excel (.xlsx)
            </a>
            <a href="Bug_Tracker_EvMoto.csv" class="btn btn-secondary" download>
                📊 Ekspor CSV (Lark Base)
            </a>
        </div>
    </div>

    <!-- KPI Summary Grid -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Anomali / Bug</div>
            <div class="kpi-val" id="kpi-total">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Critical (Blocker)</div>
            <div class="kpi-val critical-val" id="kpi-critical">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Major (High)</div>
            <div class="kpi-val major-val" id="kpi-major">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Medium (Normal)</div>
            <div class="kpi-val medium-val" id="kpi-medium">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Status Open</div>
            <div class="kpi-val open-val" id="kpi-open">0</div>
        </div>
    </div>

    <!-- Controls Bar -->
    <div class="controls-bar">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="🔍 Cari berdasarkan Bug ID, Modul, Nama Test, atau Pesan Error..." onkeyup="filterTable()">
        </div>
        <select id="severityFilter" class="filter-select" onchange="filterTable()">
            <option value="">Semua Severity</option>
            <option value="Critical">Critical</option>
            <option value="Major">Major</option>
            <option value="Medium">Medium</option>
            <option value="Minor">Minor</option>
        </select>
        <select id="pilarFilter" class="filter-select" onchange="filterTable()">
            <option value="">Semua 4 Pilar</option>
            <option value="Pilar 1">Pilar 1: Positif True</option>
            <option value="Pilar 2">Pilar 2: Positif False</option>
            <option value="Pilar 3">Pilar 3: Negatif True</option>
            <option value="Pilar 4">Pilar 4: Negatif False</option>
        </select>
    </div>

    <!-- Table Card -->
    <div class="table-card">
        <div class="table-responsive">
            <table id="bugTable">
                <thead>
                    <tr>
                        <th>Bug ID</th>
                        <th>Waktu</th>
                        <th>Modul</th>
                        <th>Platform</th>
                        <th>Environment</th>
                        <th>Test Case & Fungsi</th>
                        <th>4 Pilar QA</th>
                        <th>Severity</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Ringkasan Masalah</th>
                        <th>Hasil Aktual / Error</th>
                        <th>Evidence Screenshot</th>
                    </tr>
                </thead>
                <tbody id="bugTableBody">
                    <!-- Baris akan dirender oleh JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <!-- Modal Pratinjau Bukti Screenshot -->
    <div class="modal-overlay" id="screenshotModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">📸 Bukti Tangkapan Layar (Evidence Screenshot)</h3>
                <button class="close-modal" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <img id="modalImg" src="" alt="Screenshot Bukti Bug">
            </div>
        </div>
    </div>

    <script>
        const bugsData = {records_json};

        function renderKPIs(data) {{
            document.getElementById("kpi-total").textContent = data.length;
            document.getElementById("kpi-critical").textContent = data.filter(r => r.Severity === "Critical").length;
            document.getElementById("kpi-major").textContent = data.filter(r => r.Severity === "Major").length;
            document.getElementById("kpi-medium").textContent = data.filter(r => r.Severity === "Medium").length;
            document.getElementById("kpi-open").textContent = data.filter(r => r.Status === "Open").length;
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

        function renderTable(data) {{
            const tbody = document.getElementById("bugTableBody");
            if (data.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; padding: 40px; color: #64748B;">🎉 Tidak ada bug yang tercatat. Seluruh pengujian berjalan sempurna (100% Passed)!</td></tr>`;
                return;
            }}

            tbody.innerHTML = data.map(r => `
                <tr>
                    <td style="font-weight: 700; color: #1B365D;">${{r['Bug ID']}}</td>
                    <td style="white-space: nowrap; color: #64748B; font-size: 12px;">${{r.Timestamp}}</td>
                    <td style="font-weight: 500;">${{r['Modul / Fitur']}}</td>
                    <td><span class="badge" style="background:#EEF2FF; color:#4338CA; border:1px solid #C7D2FE;">${{r.Platform || 'Website (Desktop)'}}</span></td>
                    <td><span class="badge" style="background:${{r.Environment === 'Production' ? '#ECFDF5; color:#047857; border:1px solid #A7F3D0;' : '#FFFBEB; color:#B45309; border:1px solid #FDE68A;'}}">${{r.Environment || 'Production'}}</span></td>
                    <td><code>${{r['Test Case & Fungsi']}}</code></td>
                    <td><span style="font-size: 12px; font-weight: 500;">${{r['4 Pilar QA']}}</span></td>
                    <td>${{getSeverityBadge(r.Severity)}}</td>
                    <td><span style="font-size: 12px; font-weight: 600;">${{r.Priority}}</span></td>
                    <td><span class="badge badge-open">${{r.Status}}</span></td>
                    <td style="max-width: 250px; font-size: 12px;">${{r['Ringkasan Bug (Summary)']}}</td>
                    <td style="max-width: 250px; font-size: 12px; color: #B91C1C;">${{r['Hasil Aktual / Error']}}</td>
                    <td style="text-align: center;">
                        ${{r['Evidence Screenshot Link'] && r['Evidence Screenshot Link'] !== 'Screenshot tidak tersedia' 
                            ? `<button class="btn-view-evidence" onclick="openModal('${{r['Evidence Screenshot Link']}}', '${{r['Bug ID']}} - ${{r['Test Case & Fungsi']}}')">📸 Lihat Bukti</button>` 
                            : `<span style="color: #94A3B8; font-size: 11px;">Tidak ada</span>`
                        }}
                    </td>
                </tr>
            `).join("");
        }}

        function filterTable() {{
            const q = document.getElementById("searchInput").value.toLowerCase();
            const sev = document.getElementById("severityFilter").value;
            const pil = document.getElementById("pilarFilter").value;

            const filtered = bugsData.filter(r => {{
                const matchSearch = Object.values(r).some(v => String(v).toLowerCase().includes(q));
                const matchSev = !sev || r.Severity === sev;
                const matchPil = !pil || (r['4 Pilar QA'] && r['4 Pilar QA'].includes(pil));
                return matchSearch && matchSev && matchPil;
            }});

            renderTable(filtered);
        }}

        function openModal(imgSrc, title) {{
            document.getElementById("modalImg").src = imgSrc;
            document.getElementById("modalTitle").textContent = "📸 Evidence: " + title;
            document.getElementById("screenshotModal").style.display = "flex";
        }}

        function closeModal() {{
            document.getElementById("screenshotModal").style.display = "none";
        }}

        window.onclick = function(event) {{
            const modal = document.getElementById("screenshotModal");
            if (event.target === modal) {{
                modal.style.display = "none";
            }}
        }};

        // Inisialisasi awal
        renderKPIs(bugsData);
        renderTable(bugsData);
    </script>
</body>
</html>
"""
        with open(HTML_PATH, mode="w", encoding="utf-8") as f:
            f.write(html_template)
