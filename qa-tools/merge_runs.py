"""Gabungkan hasil beberapa job CI (shard) menjadi satu folder run, lalu laporan PDF dibuat dari situ.

Pemakaian: python merge_runs.py <folder-artifact> <folder-hasil>
<folder-artifact> berisi banyak runs/<tanggal_jam>/<suite>/*.xml dari tiap job.
"""
import json
import shutil
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
suites, info = set(), {}
for xml in src.rglob("*.xml"):
    suite = xml.parent.name
    if suite not in ("admin", "api", "mobile", "cross"):
        continue
    (out / suite).mkdir(exist_ok=True)
    shutil.copy2(xml, out / suite / xml.name)
    suites.add(suite)
for ri in src.rglob("run_info.json"):
    data = json.loads(ri.read_text(encoding="utf-8"))
    info.setdefault("environment", data.get("environment"))
    info.setdefault("started", data.get("started"))
    info.setdefault("mobile_mode", data.get("mobile_mode"))
    info["mock_services"] = info.get("mock_services") or data.get("mock_services", False)
for suite in suites:
    (out / suite / "DONE").write_text("", encoding="utf-8")
info["suites"] = [s for s in ("admin", "api", "mobile", "cross") if s in suites]
(out / "run_info.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
print("digabung:", {s: len(list((out / s).glob("*.xml"))) for s in info["suites"]})
