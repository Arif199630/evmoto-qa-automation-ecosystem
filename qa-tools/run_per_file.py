"""Jalankan test per unit (satu file, atau potongan file besar) di proses pytest sendiri, dibagi ke N bucket paralel.

Crash di satu unit tidak menjatuhkan unit lain. Setiap unit menulis JUnit XML sendiri.
Pemakaian: run_per_file.py <project_dir> <tests_dir> <out_dir> <buckets> [argumen pytest tambahan...]

Env opsional:
  FILE_INCLUDE / FILE_EXCLUDE / FILE_INCLUDE_USER : filter nama file (regex)
  CHUNK_SIZE   : pecah file menjadi potongan berisi maks N test (0 = per file utuh). Semua test tetap dijalankan.
  SHARD_TOTAL / SHARD_INDEX : bagi unit ke beberapa job CI. Pembagian seimbang menurut jumlah test (bukan per nama file).
  RESUME_DIR   : folder hasil run sebelumnya; unit yang XML-nya sudah ada tidak diulang.
"""
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

project, tests_dir, out_dir, buckets = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve(), int(sys.argv[4])
extra = sys.argv[5:]
out_dir.mkdir(parents=True, exist_ok=True)

include = re.compile(os.getenv("FILE_INCLUDE", ".*"))
exclude = re.compile(os.getenv("FILE_EXCLUDE", "^$"))
user_include = re.compile(os.getenv("FILE_INCLUDE_USER") or ".*")
files = sorted(f for f in (project / tests_dir).glob("test_*.py")
               if include.search(f.name) and user_include.search(f.name) and not exclude.search(f.name))
chunk_size = int(os.getenv("CHUNK_SIZE", "0"))


def collect(path):
    """Node id semua test di satu file (tanpa menjalankannya)."""
    proc = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-o", "addopts=", "-p", "no:cacheprovider",
                           str(path.relative_to(project))], cwd=project, capture_output=True, text=True, env=os.environ.copy())
    return [line.strip() for line in proc.stdout.splitlines() if "::" in line and not line.startswith(("<", "="))]


# Unit kerja: (nama_xml, label, argumen pytest, jumlah test)
units = []
for f in files:
    nodes = collect(f) if chunk_size > 0 else []
    if chunk_size > 0 and len(nodes) > chunk_size:
        for k in range(0, len(nodes), chunk_size):
            part = nodes[k:k + chunk_size]
            units.append((f"{f.stem}__p{k // chunk_size + 1}", f"{f.name} bagian {k // chunk_size + 1}", part, len(part)))
    else:
        count = len(nodes) or len(re.findall(r"^\s*(?:async\s+)?def test_", f.read_text(encoding="utf-8", errors="replace"), re.M))
        units.append((f.stem, f.name, [str(f.relative_to(project))], count))

# CI: bagi unit ke beberapa job; unit terbesar dulu ke job yang bebannya paling ringan (seimbang)
shard_total = int(os.getenv("SHARD_TOTAL", "1"))
if shard_total > 1:
    loads = [[0, []] for _ in range(shard_total)]
    for unit in sorted(units, key=lambda u: (-u[3], u[0])):
        target = min(loads, key=lambda load: load[0])
        target[0] += unit[3]
        target[1].append(unit)
    units = loads[int(os.getenv("SHARD_INDEX", "0"))][1]

units.sort(key=lambda u: -u[3])
groups = [units[i::buckets] for i in range(buckets)]
(out_dir / "EXPECTED").write_text(str(sum(u[3] for u in units)), encoding="utf-8")

RESUME_DIR = os.getenv("RESUME_DIR")


def find_previous(stem):
    """XML unit yang sama dari run sebelumnya (RESUME_DIR), di folder suite yang sama."""
    if not RESUME_DIR:
        return None
    hits = [p for p in Path(RESUME_DIR).rglob(f"{stem}.xml") if p.parent.name == out_dir.name]
    return max(hits, key=lambda p: p.stat().st_mtime) if hits else None


def run_bucket(index, group):
    log = out_dir / f"bucket_{index}.log"
    with log.open("a", encoding="utf-8") as fh:
        for stem, label, targets, _count in group:
            xml = out_dir / f"{stem}.xml"
            if xml.exists():
                continue  # sudah selesai di run sebelumnya
            previous = find_previous(stem)
            if previous:
                shutil.copy2(previous, xml)  # lanjutkan: unit ini sudah selesai di run yang di-pause
                fh.write(f"### {label}\n### dilanjutkan dari hasil sebelumnya\n### exit 0 {label}\n")
                continue
            cmd = [sys.executable, "-m", "pytest", *targets, "-q", "-o", "addopts=",
                   "-p", "no:cacheprovider", "-rfE", f"--junitxml={xml}", *extra]
            fh.write(f"### {label}\n")
            fh.flush()
            proc = subprocess.run(cmd, cwd=project, stdout=fh, stderr=subprocess.STDOUT, env=os.environ.copy())
            fh.write(f"### exit {proc.returncode} {label}\n")
            fh.flush()


threads = [threading.Thread(target=run_bucket, args=(i, g)) for i, g in enumerate(groups)]
for t in threads:
    t.start()
for t in threads:
    t.join()
(out_dir / "DONE").write_text("ok", encoding="utf-8")
print("selesai", len(units), "unit dari", len(files), "file")
