"""Tiny local progress page for the running pytest suites. Reads the run logs; changes nothing."""
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

RUNS = Path(__file__).resolve().parent / "runs"


def latest_run():
    runs = sorted(p for p in RUNS.glob("*") if p.is_dir()) if RUNS.exists() else []
    return runs[-1] if runs else RUNS


RUN_DIR = RUNS
SUITES_OLD = [
    ("Admin Dashboard", "admin_before.log", 650),
    ("Mobile User & Driver", "mobile_before/bucket_*.log", 593),
    ("Regression lintas aplikasi", "cross/bucket_*.log", 109),
    ("Admin (setelah dirapikan)", "admin_after/bucket_*.log", 590),
    ("Mobile (setelah dirapikan)", "mobile_after/bucket_*.log", 593),
    ("Lintas aplikasi (setelah dirapikan)", "cross_after/bucket_*.log", 109),
]
LINE = re.compile(r"^[.FEsxX]+(\s+\[\s*\d+%\])?\s*$")
SUMMARY = re.compile(r"(\d+ (?:passed|failed|error)[^\n]*?) in [\d.]+s")
COLLECTED = re.compile(r"(\d+) (?:tests? )?(?:collected|items)")


def status(name, log, total):
    paths = sorted(RUN_DIR.glob(log))
    if not paths:
        return {"name": name, "state": "belum mulai", "done": 0, "total": total}
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in paths)
    if "*" in log:
        started = text.count("### test_") - text.count("### exit")
        finished_all = (RUN_DIR / log.split("/")[0] / "DONE").exists()
        counts = {"pass": 0, "fail": 0, "error": 0, "skip": 0}
        for line in text.splitlines():
            line = line.strip()
            if LINE.match(line):
                chars = line.split("[")[0]
                counts["pass"] += chars.count(".")
                counts["fail"] += chars.count("F")
                counts["error"] += chars.count("E")
                counts["skip"] += chars.count("s") + chars.count("x")
        if finished_all:
            import xml.etree.ElementTree as ET
            counts = {"pass": 0, "fail": 0, "error": 0, "skip": 0}
            for xml in (RUN_DIR / log.split("/")[0]).glob("*.xml"):
                for tc in ET.parse(xml).getroot().iter("testcase"):
                    tags = {ch.tag for ch in tc}
                    key = "error" if "error" in tags else "fail" if "failure" in tags else "skip" if "skipped" in tags else "pass"
                    counts[key] += 1
        done = sum(counts.values())
        expected_file = RUN_DIR / log.split("/")[0] / "EXPECTED"
        if not total and expected_file.exists() and not finished_all:
            total = max(int(expected_file.read_text() or 0), done)
        state = "selesai" if finished_all else f"berjalan ({max(started, 0)} file aktif)"
        return {"name": name, "state": state, "done": done, "total": total or done, **counts, "summary": ""}
    counts = {"pass": 0, "fail": 0, "error": 0, "skip": 0}
    for line in text.splitlines():
        line = line.strip()
        if LINE.match(line):
            chars = line.split("[")[0]
            counts["pass"] += chars.count(".")
            counts["fail"] += chars.count("F")
            counts["error"] += chars.count("E")
            counts["skip"] += chars.count("s") + chars.count("x")
    m = COLLECTED.search(text)
    if m:
        total = int(m.group(1))
    done = sum(counts.values())
    final = SUMMARY.findall(text)
    state = "selesai" if final else "berjalan"
    return {"name": name, "state": state, "done": done, "total": total, **counts, "summary": final[-1] if final else ""}


PAGE = """<!doctype html><html lang="id"><head><meta charset="utf-8"><title>Progres Automation EvMoto</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Arial,sans-serif;margin:16px;background:#f6f7f9;color:#1f2933}
h1{font-size:18px;margin:0 0 4px}.sub{color:#52606d;font-size:13px;margin-bottom:16px}
.card{background:#fff;border:1px solid #d9e2ec;border-radius:8px;padding:12px 14px;margin-bottom:12px}
.row{display:flex;justify-content:space-between;font-size:14px;margin-bottom:8px;gap:8px;flex-wrap:wrap}
.bar{height:16px;background:#e4e7eb;border-radius:8px;overflow:hidden;display:flex}
.bar span{display:block;height:100%}.p{background:#2f9e44}.f{background:#e03131}.e{background:#f08c00}.s{background:#adb5bd}
.legend{font-size:12px;color:#52606d;margin-top:6px}.state{font-weight:bold}
</style></head><body>
<h1>Progres Automation Test EvMoto (staging, headless)</h1>
<div class="sub">Diperbarui otomatis tiap 3 detik · <span id="t"></span></div>
<div id="list"></div>
<script>
async function tick(){
  try{
    const r=await fetch('/status',{cache:'no-store'}); const d=await r.json();
    document.getElementById('t').textContent=new Date().toLocaleTimeString('id-ID');
    document.getElementById('list').innerHTML=d.map(s=>{
      const tot=s.total||Math.max(s.done,1), pct=Math.min(100,Math.round(100*s.done/tot));
      const w=k=>(100*(s[k]||0)/tot).toFixed(2)+'%';
      return `<div class="card"><div class="row"><span>${s.name}</span>
        <span class="state">${s.state} · ${s.done}/${s.total||'?'} (${s.total?pct:0}%)</span></div>
        <div class="bar"><span class="p" style="width:${w('pass')}"></span><span class="f" style="width:${w('fail')}"></span>
        <span class="e" style="width:${w('error')}"></span><span class="s" style="width:${w('skip')}"></span></div>
        <div class="legend">Lulus ${s.pass||0} · Gagal ${s.fail||0} · Error ${s.error||0} · Skip ${s.skip||0}${s.summary?' · '+s.summary:''}</div></div>`;
    }).join('');
  }catch(e){}
}
tick(); setInterval(tick,3000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/status"):
            global RUN_DIR
            RUN_DIR = latest_run()
            names = {"admin": "Admin Dashboard", "api": "REST API", "mobile": "Mobile User & Driver", "cross": "Lintas aplikasi"}
            try:
                suites = json.loads((RUN_DIR / "run_info.json").read_text(encoding="utf-8"))["suites"]
            except Exception:
                suites = []
            body = json.dumps([status(names[s], f"{s}/bucket_*.log", 0) for s in suites]).encode()
            ctype = "application/json"
        else:
            body = PAGE.encode()
            ctype = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


HTTPServer(("127.0.0.1", 8799), Handler).serve_forever()
