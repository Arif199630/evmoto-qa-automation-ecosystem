"""
Quality gate untuk project automation EvMoto. Jalankan sebelum test.

Memeriksa hal yang membuat hasil test tidak valid:
  1. method_hilang      : test memanggil method Page Object / helper yang tidak ada
  2. assert_palsu       : assert True, assert x or True, assertTrue(True) -> tidak pernah gagal
  3. domain_production  : domain production ditulis langsung di file test
  4. file_duplikat      : dua file test dengan isi sama persis
  5. conftest_ganda     : lebih dari satu conftest.py di folder test

Pelanggaran lama dicatat di quality_baseline_<project>.json dan tidak menggagalkan gate.
Pelanggaran BARU menggagalkan gate (exit 1), supaya kode test hanya bisa makin baik.

Pemakaian:
  python quality_gate.py admin            # cek project admin
  python quality_gate.py mobile           # cek project mobile
  python quality_gate.py mobile --update-baseline   # setelah membereskan pelanggaran lama
"""
import ast
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = HERE.parent

PROJECTS = {
    "admin": {
        "root": SCRATCH / "web-dashboard" if (SCRATCH / "web-dashboard").exists() else SCRATCH / "Automation_Project_EvMoto",
        "pages": ["Frontend/Feature/Pages"],
        "tests": ["Frontend/Feature/Step_Definition"],
        "helpers": [],
    },
    "mobile": {
        "root": SCRATCH / "mobile-apps" if (SCRATCH / "mobile-apps").exists() else SCRATCH / "evmoto-user-mobile-automation",
        "pages": ["Frontend/Feature/Pages", "core"],
        "tests": ["Frontend/Feature/Step_Definition", "api-testing/suites"],
        "helpers": ["Frontend/Feature/Helper", "api-testing/client"],
    },
}
PRODUCTION_HOSTS = ("dashboard.evmotoid.com", "new-api.evmotoid.com", "//api.evmotoid.com")
OBJECT_SUFFIXES = ("_page", "_pg", "page", "_calculator", "calculator", "_helper", "helper", "_simulator")
FAKE_ASSERT = re.compile(r"^\s*(assert\s+True\s*(#.*)?$|assert\s+.+\s+or\s+True\b|self\.assertTrue\(\s*True\s*[,)])", re.M)


def defined_names(dirs, root):
    names = set()
    for d in dirs:
        for f in (root / d).rglob("*.py"):
            if "_archive" in f.parts:
                continue
            for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            names.add(item.name)
                        elif isinstance(item, ast.Assign):
                            names.update(t.id for t in item.targets if isinstance(t, ast.Name))
    return names


def receiver_name(node):
    obj = node.func.value
    if isinstance(obj, ast.Attribute):
        return obj.attr
    if isinstance(obj, ast.Name):
        return obj.id
    return ""


def undefined_names(text, filename):
    """Nama tak terdefinisi menurut pyflakes (kosong bila pyflakes belum terpasang)."""
    try:
        from pyflakes.api import check
        from pyflakes.reporter import Reporter
    except ImportError:
        return []
    import io
    out = io.StringIO()
    check(text, filename, Reporter(out, io.StringIO()))
    return sorted({m.group(1) for m in re.finditer(r"undefined name '([^']+)'", out.getvalue())})


def scan(project):
    cfg = PROJECTS[project]
    root = cfg["root"]
    known = defined_names(cfg["pages"] + cfg["helpers"], root)
    found = defaultdict(list)
    test_files = [f for d in cfg["tests"] for f in (root / d).rglob("test_*.py") if "_archive" not in f.parts]
    hashes = defaultdict(list)
    for f in test_files:
        rel = f.relative_to(root).as_posix()
        text = f.read_text(encoding="utf-8")
        hashes[hashlib.sha1(text.encode()).hexdigest()].append(rel)
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                name = receiver_name(node).lower()
                if name.endswith(OBJECT_SUFFIXES) and node.func.attr not in known and not node.func.attr.startswith("assert"):
                    found["method_hilang"].append(f"{rel}::{receiver_name(node)}.{node.func.attr}")
        # Kunci = nama fungsi test + urutan di dalamnya, bukan nomor baris,
        # supaya menambah/menghapus baris lain tidak terbaca sebagai pelanggaran baru.
        funcs = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(ast.parse(text))
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        per_func = defaultdict(int)
        for m in FAKE_ASSERT.finditer(text):
            line = text[: m.start()].count("\n") + 1
            inside = [f for f in funcs if f[0] <= line <= f[1]]
            func = min(inside, key=lambda f: f[1] - f[0])[2] if inside else "<module>"
            per_func[func] += 1
            found["assert_palsu"].append(f"{rel}::{func}#{per_func[func]}")
        # Nama yang dipakai tetapi tidak pernah didefinisikan/di-import (NameError saat test jalan)
        for name in undefined_names(text, rel):
            found["nama_tidak_terdefinisi"].append(f"{rel}::{name}")
        for host in PRODUCTION_HOSTS:
            if host in text:
                found["domain_production"].append(f"{rel}:{host}")
    for files in hashes.values():
        if len(files) > 1:
            found["file_duplikat"].append(" = ".join(sorted(files)))
    conftests = [c.relative_to(root).as_posix() for c in root.rglob("conftest.py") if "_archive" not in c.parts]
    if project == "mobile":
        conftests = [c for c in conftests if not c.startswith("api-testing/")]
    if len(conftests) > 1:
        found["conftest_ganda"].append(", ".join(sorted(conftests)))
    return {k: sorted(set(v)) for k, v in found.items()}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in PROJECTS:
        print(__doc__)
        return 2
    project = sys.argv[1]
    baseline_path = HERE / f"quality_baseline_{project}.json"
    current = scan(project)
    if "--update-baseline" in sys.argv or not baseline_path.exists():
        baseline_path.write_text(json.dumps(current, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"Baseline {project} disimpan: " + ", ".join(f"{k}={len(v)}" for k, v in current.items()))
        return 0
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    new = {k: [x for x in v if x not in set(baseline.get(k, []))] for k, v in current.items()}
    new = {k: v for k, v in new.items() if v}
    fixed = sum(len(set(baseline.get(k, [])) - set(current.get(k, []))) for k in baseline)
    print(f"Quality gate {project}: " + ", ".join(f"{k}={len(v)}" for k, v in current.items()) + f" | sudah dibereskan sejak baseline: {fixed}")
    if new:
        print("GAGAL: pelanggaran BARU (perbaiki sebelum menjalankan test):")
        for k, items in new.items():
            for x in items:
                print(f"  [{k}] {x}")
        return 1
    print("LULUS: tidak ada pelanggaran baru.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
