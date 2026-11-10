"""Halaman progres live untuk run GitHub Actions `evmoto-regression`.

Pemakaian: python ci_progress.py [--repo OWNER/REPO] [--port 8800]
Buka http://localhost:8800. Data diambil dari `gh run view` tiap 15 detik (butuh gh yang sudah login).
Jumlah test per job baru terlihat setelah job selesai; selama berjalan yang tampil adalah langkah (step) job.
"""
import argparse
import json
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="Arif199630/evmoto-qa-automation-ecosystem")
ap.add_argument("--port", type=int, default=8800)
args = ap.parse_args()
STATE = {"updated": "-", "run": None, "jobs": [], "error": ""}


def gh(*a):
    return subprocess.run(["gh", *a, "-R", args.repo], capture_output=True, text=True, encoding="utf-8", timeout=60)


def minutes_since(iso):
    if not iso or iso.startswith("0001"):
        return 0
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return int((datetime.now(timezone.utc) - t).total_seconds() // 60)


def poll():
    while True:
        try:
            r = gh("run", "list", "--workflow", "evmoto-regression", "--limit", "1",
                   "--json", "databaseId,displayTitle,status,conclusion,createdAt,url")
            run = json.loads(r.stdout)[0]
            j = gh("run", "view", str(run["databaseId"]), "--json", "jobs")
            jobs = []
            for job in json.loads(j.stdout)["jobs"]:
                steps = job.get("steps", [])
                done = sum(1 for s in steps if s["status"] == "completed")
                current = next((s["name"] for s in steps if s["status"] == "in_progress"), "")
                jobs.append({"name": job["name"], "status": job["status"], "conclusion": job.get("conclusion") or "",
                             "done": done, "total": len(steps) or 1, "current": current,
                             "minutes": minutes_since(job.get("startedAt", "")), "url": job.get("url", "")})
            STATE.update(run=run, jobs=jobs, error="", updated=datetime.now().strftime("%H.%M.%S"))
        except Exception as e:  # tampilkan masalah koneksi di halaman, jangan berhenti
            STATE["error"] = str(e)
        time.sleep(15)


PAGE = """<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Progres CI EvMoto</title><style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b1f24;--mut:#5b6470;--bar:#e3e6ea;--ok:#1a7f37;--run:#0969da;--bad:#cf222e}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--card:#161b22;--ink:#e6edf3;--mut:#9aa4af;--bar:#30363d}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}main{max-width:760px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:0 0 4px}.mut{color:var(--mut);font-size:13px}.card{background:var(--card);border-radius:10px;padding:12px 14px;margin:10px 0;box-shadow:0 1px 2px #0002}
.row{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}.bar{height:12px;background:var(--bar);border-radius:6px;overflow:hidden;margin:8px 0 4px}
.fill{height:100%}a{color:var(--run)}</style></head><body><main>
<h1>Progres CI EvMoto (GitHub Actions)</h1><div class="mut" id="meta">memuat...</div><div id="jobs"></div>
<p class="mut">Diperbarui tiap 15 detik. Jumlah test lulus/gagal muncul di laporan PDF setelah semua job selesai.</p></main>
<script>
const color=j=>j.conclusion==="success"?"var(--ok)":j.conclusion==="failure"?"var(--bad)":"var(--run)";
async function tick(){try{const s=await (await fetch("/data")).json();
const r=s.run||{};const all=s.jobs.length||1,fin=s.jobs.filter(j=>j.status==="completed").length;
document.getElementById("meta").innerHTML=`Run: <a href="${r.url||"#"}" target="_blank">${r.displayTitle||"-"}</a> · ${r.status||"-"} ${r.conclusion||""} · ${fin}/${all} job selesai · diperbarui ${s.updated}${s.error?" · <b>"+s.error+"</b>":""}`;
document.getElementById("jobs").innerHTML=s.jobs.map(j=>{const pct=j.status==="completed"?100:Math.round(100*j.done/j.total);
return `<div class="card"><div class="row"><b>${j.name}</b><span>${j.status==="completed"?(j.conclusion==="success"?"selesai":"selesai: "+j.conclusion):"berjalan "+j.minutes+" menit"}</span></div>
<div class="bar"><div class="fill" style="width:${pct}%;background:${color(j)}"></div></div>
<div class="mut">${pct}% langkah${j.current?" · sekarang: "+j.current:""} · <a href="${j.url}" target="_blank">log live</a></div></div>`}).join("");
}catch(e){document.getElementById("meta").textContent="Server progres tidak menjawab: "+e}}
tick();setInterval(tick,5000);</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(STATE).encode() if self.path == "/data" else PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json" if self.path == "/data" else "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


threading.Thread(target=poll, daemon=True).start()
print(f"Progres CI: http://localhost:{args.port}")
ThreadingHTTPServer(("127.0.0.1", args.port), H).serve_forever()
