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
if os.getenv("PYTEST_K"):  # jalankan test tertentu saja (input k_filter di workflow)
    extra += ["-k", os.getenv("PYTEST_K")]
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
    nodes = [line.strip() for line in proc.stdout.splitlines() if "::" in line and not line.startswith(("<", "="))]
    k = os.getenv("PYTEST_K")
    if k:  # hanya unit yang berisi test terpilih (pencocokan sederhana pada nama node)
        nodes = [n for n in nodes if all(part.strip() in n for part in k.split(" and "))]
    return nodes


def device_of_tests(path):
    """Perangkat yang dibuka tiap test: 'driver' (fixture driver_app), 'user' (fixture driver), atau 'none'."""
    import ast
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))

    def args(fn):
        return {a.arg for a in fn.args.args}

    def autouse_args(body):
        found = set()
        for node in body:
            if isinstance(node, ast.FunctionDef) and any("autouse" in ast.unparse(d) for d in node.decorator_list):
                found |= args(node)
        return found

    def kind(names):
        return "driver" if "driver_app" in names else "user" if "driver" in names else "none"

    result, module_auto = {}, autouse_args(tree.body)
    for node in tree.body:
        scopes = [(node, set())] if isinstance(node, ast.FunctionDef) else \
                 [(fn, autouse_args(node.body)) for fn in node.body if isinstance(fn, ast.FunctionDef)] if isinstance(node, ast.ClassDef) else []
        for fn, class_auto in scopes:
            if fn.name.startswith("test"):
                result[fn.name] = kind(args(fn) | class_auto | module_auto)
    return result


account_sharding = os.getenv("ACCOUNT_SHARDING") == "1"

# Unit kerja: (nama_xml, label, argumen pytest, jumlah test, perangkat)
units = []
for f in files:
    nodes = collect(f) if (chunk_size > 0 or account_sharding) else []
    if account_sharding and nodes:
        # Pisahkan test per perangkat dulu (satu akun = satu perangkat), lalu potong per CHUNK_SIZE
        devices = device_of_tests(f)
        by_device = {}
        for node in nodes:
            name = node.split("::")[-1].split("[")[0]
            by_device.setdefault(devices.get(name, "none"), []).append(node)
        for dev, dev_nodes in sorted(by_device.items()):
            size = chunk_size or len(dev_nodes)
            for k in range(0, len(dev_nodes), size):
                part = dev_nodes[k:k + size]
                units.append((f"{f.stem}__{dev}{k // size + 1}", f"{f.name} {dev} {k // size + 1}", part, len(part), dev))
    elif chunk_size > 0 and len(nodes) > chunk_size:
        for k in range(0, len(nodes), chunk_size):
            part = nodes[k:k + chunk_size]
            units.append((f"{f.stem}__p{k // chunk_size + 1}", f"{f.name} bagian {k // chunk_size + 1}", part, len(part), "?"))
    else:
        count = len(nodes) or len(re.findall(r"^\s*(?:async\s+)?def test_", f.read_text(encoding="utf-8", errors="replace"), re.M))
        units.append((f.stem, f.name, [str(f.relative_to(project))], count, "?"))

# CI: bagi unit ke beberapa job; unit terbesar dulu ke job yang bebannya paling ringan (seimbang)
shard_total = int(os.getenv("SHARD_TOTAL", "1"))


def balance(items, slots):
    loads = [[0, []] for _ in range(slots)]
    for unit in sorted(items, key=lambda u: (-u[3], u[0])):
        target = min(loads, key=lambda load: load[0])
        target[0] += unit[3]
        target[1].append(unit)
    return [load[1] for load in loads]


if shard_total > 1 and os.getenv("ACCOUNT_SHARDING") == "1" and shard_total >= 3:
    # Satu akun hanya boleh login di satu perangkat: test aplikasi Driver (1 akun) di job 0,
    # test User yang butuh riwayat akun utama di job 1, sisanya ke job 2.. dengan akun QA Auto masing-masing.
    main_user = re.compile(os.getenv("USER_MAIN_FILES", r"^test_activity\.py$"))

    def group(unit):
        if unit[4] == "driver":
            return "driver"
        if unit[4] == "user" and main_user.search(unit[0].split("__")[0] + ".py"):
            return "user_main"
        return "pool"  # test User lain (akun QA Auto per job) dan test tanpa perangkat

    plan = [[u for u in units if group(u) == "driver"], [u for u in units if group(u) == "user_main"]]
    plan += balance([u for u in units if group(u) == "pool"], shard_total - 2)
    if os.getenv("DRY_RUN") == "all":
        for i, job in enumerate(plan):
            print(f"job {i:2}: {sum(u[3] for u in job):3} test | perangkat {sorted({u[4] for u in job})} | {len(job)} unit")
        print("total:", sum(u[3] for job in plan for u in job))
        sys.exit(0)
    units = plan[int(os.getenv("SHARD_INDEX", "0"))]
elif shard_total > 1:
    units = balance(units, shard_total)[int(os.getenv("SHARD_INDEX", "0"))]

# RUN_LAST: unit yang namanya cocok dijalankan paling akhir (mis. layar yang pernah membuat emulator CI mati),
# supaya bila emulator mati, unit lain sudah selesai lebih dulu.
run_last = re.compile(os.getenv("RUN_LAST") or "^$")
units.sort(key=lambda u: (bool(run_last.search(u[0])), -u[3]))
if os.getenv("DRY_RUN") == "1":  # hanya tampilkan rencana pembagian, tidak menjalankan test
    print(f"{sum(u[3] for u in units)} test dalam {len(units)} unit: " + ", ".join(u[0] for u in units))
    sys.exit(0)
groups = [units[i::buckets] for i in range(buckets)]
(out_dir / "EXPECTED").write_text(str(sum(u[3] for u in units)), encoding="utf-8")

RESUME_DIR = os.getenv("RESUME_DIR")


# Tanda hasil yang gagal karena lingkungan (emulator/Appium mati), bukan karena aplikasi atau test.
# Hasil seperti ini tidak dipakai ulang saat melanjutkan run, sehingga unitnya dijalankan lagi.
INFRA_MARKERS = ("Appium tidak aktif di", "device offline", "instrumentation process is not running",
                 "Could not find a connected Android device", "socket hang up")
infra_down = threading.Event()


def has_infra_error(xml_path):
    try:
        text = Path(xml_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(m in text for m in INFRA_MARKERS)


def appium_alive():
    import socket
    url = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723").split("//")[-1].split("/")[0]
    host, port = url.split(":")
    try:
        with socket.create_connection((host, int(port)), timeout=2):
            return True
    except OSError:
        return False


def find_previous(stem):
    """XML unit yang sama dari run sebelumnya (RESUME_DIR), di folder suite yang sama, tanpa error lingkungan."""
    if not RESUME_DIR:
        return None
    hits = [p for p in Path(RESUME_DIR).rglob(f"{stem}.xml") if p.parent.name == out_dir.name and not has_infra_error(p)]
    return max(hits, key=lambda p: p.stat().st_mtime) if hits else None


def run_bucket(index, group):
    log = out_dir / f"bucket_{index}.log"
    with log.open("a", encoding="utf-8") as fh:
        for stem, label, targets, _count, _device in group:
            xml = out_dir / f"{stem}.xml"
            if infra_down.is_set():
                fh.write(f"### {label}\n### DILEWATI: emulator/Appium mati, unit ini dijalankan saat run dilanjutkan\n")
                continue
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
            if has_infra_error(xml) and not appium_alive():
                # Emulator/Appium mati: unit ini dan sisanya tidak dicatat sebagai gagal palsu
                infra_down.set()
                xml.rename(xml.with_name(xml.name + ".infra_error"))  # bukan .xml: tidak ikut dihitung di laporan
                (out_dir / "INFRA_DOWN").write_text(f"emulator/Appium mati saat {label}", encoding="utf-8")
                fh.write("### EMULATOR/APPIUM MATI: unit ini dan sisanya dijalankan ulang saat run dilanjutkan\n")


threads = [threading.Thread(target=run_bucket, args=(i, g)) for i, g in enumerate(groups)]
for t in threads:
    t.start()
for t in threads:
    t.join()
(out_dir / "DONE").write_text("ok", encoding="utf-8")
print("selesai", len(units), "unit dari", len(files), "file")
