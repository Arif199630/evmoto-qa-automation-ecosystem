"""
Laporan PDF dari hasil run_all.py. Semua angka dibaca dari JUnit XML; tidak ada angka yang ditulis manual.

Pemakaian: python report.py <folder_hasil_run>
"""
import collections
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

LABELS = {
    "admin": "Admin Dashboard (Chrome headless ke staging)",
    "api": "REST API backend staging",
    "mobile": "Mobile User & Driver App",
    "cross": "Lintas aplikasi (Admin, Driver, User)",
}


def read_suite(folder):
    per_file = collections.OrderedDict()
    reasons = collections.Counter()
    mock = 0  # test dengan properti JUnit mock=true (memanggil mock lokal, bukan backend sungguhan)
    for xml in sorted(folder.glob("*.xml")):
        for tc in ET.parse(xml).getroot().iter("testcase"):
            if any(p.get("name") == "mock" and p.get("value") == "true" for p in tc.iter("property")):
                mock += 1
            mod = next((p for p in tc.get("classname", "").split(".") if p.startswith("test_")), xml.stem)
            counts = per_file.setdefault(mod, collections.Counter())
            state = "lulus"
            for child in tc:
                if child.tag in ("failure", "error", "skipped"):
                    state = {"failure": "gagal", "error": "error", "skipped": "skip"}[child.tag]
                    msg = (child.get("message") or child.text or "").strip().split("\n")[0]
                    reasons[(state, re.sub(r"Stacktrace.*|0x[0-9a-f]+", "", msg).strip()[:140])] += 1
            counts[state] += 1
    return per_file, reasons, mock


def main(run_dir):
    meta = json.loads((run_dir / "run_info.json").read_text(encoding="utf-8"))
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=16)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12, spaceBefore=8)
    body = ParagraphStyle("b", parent=ss["BodyText"], fontName="Helvetica", fontSize=9, leading=12)
    cell = ParagraphStyle("c", parent=body, fontSize=7.8, leading=9.6)
    head = ParagraphStyle("hc", parent=cell, textColor=colors.white, fontName="Helvetica-Bold")

    def table(rows, widths):
        t = Table([[Paragraph(str(c), head if i == 0 else cell) for c in r] for i, r in enumerate(rows)], colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                               ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C2CC")), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        return t

    story = [Paragraph("Laporan Regression EvMoto", h1),
             Paragraph(f"Environment {meta['environment']} · dijalankan {meta['started']} · selesai {datetime.now():%d %b %Y %H:%M} WIB", body),
             Paragraph(f"Mode mobile: <b>{meta['mobile_mode']}</b>. Sumber angka: JUnit XML di folder hasil run.", body),
             Spacer(1, 4), Paragraph("Ringkasan", h2)]
    summary = [["Suite", "Total", "Lulus", "Gagal", "Error", "Skip", "Lulus %"]]
    suites = {}
    mock_per_suite = {}
    for key in meta["suites"]:
        per_file, reasons, mock_per_suite[key] = read_suite(run_dir / key)
        suites[key] = (per_file, reasons)
        tot = collections.Counter()
        for c in per_file.values():
            tot.update(c)
        n = sum(tot.values())
        executed = n - tot["skip"]
        summary.append([LABELS[key], n, tot["lulus"], tot["gagal"], tot["error"], tot["skip"],
                        f"{100 * tot['lulus'] / executed:.1f}%" if executed else "-"])
    story.append(table(summary, [62 * mm, 18 * mm, 18 * mm, 18 * mm, 18 * mm, 18 * mm, 22 * mm]))
    story.append(Paragraph("Lulus % dihitung dari test yang dijalankan (tanpa skip). Skip selalu punya alasan tertulis: "
                           "karantina, URL staging belum tersedia, atau data uji belum ada.", cell))
    if meta["mobile_mode"].startswith("SIMULATOR"):
        story.append(Paragraph("<b>Perhatian:</b> mobile berjalan di simulator HeadlessMobileDriver. Hasil mobile memvalidasi kode test, "
                               "bukan perilaku aplikasi. Jalankan dengan emulator headless untuk bukti aplikasi.", body))
    if meta.get("mock_services"):
        rincian = ", ".join(f"{LABELS[k]}: {n}" for k, n in mock_per_suite.items() if n) or "tidak ada"
        story.append(Paragraph(
            f"<b>Perhatian - mock layanan aktif:</b> {sum(mock_per_suite.values())} test memanggil mock lokal ({rincian}). "
            "Test bertanda mock memvalidasi alur automation terhadap kontrak tiruan (stub), BUKAN backend sungguhan. "
            "Kontrak mock wajib dikonfirmasi tim backend; hasil lulus di sini bukan bukti fitur berjalan di staging.", body))
    for key, (per_file, reasons) in suites.items():
        story.append(Paragraph(LABELS[key], h2))
        rows = [["File test", "Lulus", "Gagal", "Error", "Skip"]]
        for mod, c in per_file.items():
            rows.append([mod, c["lulus"], c["gagal"], c["error"], c["skip"]])
        story.append(table(rows, [96 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm]))
        top = [[s, m, n] for (s, m), n in reasons.most_common(8)]
        if top:
            story.append(Spacer(1, 3))
            story.append(table([["Status", "Penyebab", "Jumlah"]] + top, [18 * mm, 148 * mm, 16 * mm]))
    out = run_dir / "Laporan_Regression_EvMoto.pdf"
    SimpleDocTemplate(str(out), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
                      title="Laporan Regression EvMoto").build(story)
    print("PDF:", out)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
