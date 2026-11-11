"""Run each test file in its own pytest process, spread over N parallel buckets.

A crash in one file cannot take the others down. Every file gets its own JUnit XML.
Usage: run_per_file.py <project_dir> <tests_dir> <out_dir> <buckets> [extra pytest args...]
"""
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

project, tests_dir, out_dir, buckets = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve(), int(sys.argv[4])
extra = sys.argv[5:]
out_dir.mkdir(parents=True, exist_ok=True)
import re

include = re.compile(os.getenv("FILE_INCLUDE", ".*"))
exclude = re.compile(os.getenv("FILE_EXCLUDE", "^$"))
user_include = re.compile(os.getenv("FILE_INCLUDE_USER") or ".*")
files = sorted(
    (f for f in (project / tests_dir).glob("test_*.py") if include.search(f.name) and user_include.search(f.name) and not exclude.search(f.name)),
    key=lambda p: -p.stat().st_size,
)
# CI: bagi file ke beberapa job paralel (SHARD_INDEX dari 0 sampai SHARD_TOTAL-1)
shard_total = int(os.getenv("SHARD_TOTAL", "1"))
if shard_total > 1:
    files = sorted(files, key=lambda p: p.name)[int(os.getenv("SHARD_INDEX", "0"))::shard_total]
groups = [files[i::buckets] for i in range(buckets)]

# Perkiraan jumlah test untuk halaman progres (fungsi test_ di file terpilih; parametrize dihitung 1).
expected = sum(len(re.findall(r"^\s*(?:async\s+)?def test_", f.read_text(encoding="utf-8", errors="replace"), re.M)) for f in files)
(out_dir / "EXPECTED").write_text(str(expected), encoding="utf-8")


RESUME_DIR = os.getenv("RESUME_DIR")


def find_previous(stem):
    """XML file test yang sama dari run sebelumnya (RESUME_DIR), di folder suite yang sama."""
    if not RESUME_DIR:
        return None
    hits = [p for p in Path(RESUME_DIR).rglob(f"{stem}.xml") if p.parent.name == out_dir.name]
    return max(hits, key=lambda p: p.stat().st_mtime) if hits else None


def run_bucket(index, group):
    log = out_dir / f"bucket_{index}.log"
    with log.open("a", encoding="utf-8") as fh:
        for f in group:
            xml = out_dir / f"{f.stem}.xml"
            if xml.exists():
                continue  # already finished in an earlier run
            previous = find_previous(f.stem)
            if previous:
                shutil.copy2(previous, xml)  # lanjutkan: file ini sudah selesai di run yang di-pause
                fh.write(f"### {f.name}\n### dilanjutkan dari hasil sebelumnya\n### exit 0 {f.name}\n")
                continue
            cmd = [sys.executable, "-m", "pytest", str(f.relative_to(project)), "-q", "-o", "addopts=",
                   "-p", "no:cacheprovider", "-rfE", f"--junitxml={xml}", *extra]
            fh.write(f"### {f.name}\n")
            fh.flush()
            proc = subprocess.run(cmd, cwd=project, stdout=fh, stderr=subprocess.STDOUT, env=os.environ.copy())
            fh.write(f"### exit {proc.returncode} {f.name}\n")
            fh.flush()


threads = [threading.Thread(target=run_bucket, args=(i, g)) for i, g in enumerate(groups)]
for t in threads:
    t.start()
for t in threads:
    t.join()
(out_dir / "DONE").write_text("ok", encoding="utf-8")
print("selesai", len(files), "file")
