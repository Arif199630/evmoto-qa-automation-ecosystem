"""Halaman progres live untuk run GitHub Actions `evmoto-regression`.

Pemakaian:
  python ci_progress.py                          # ikuti run regression penuh (judul 'evmoto-regression all') terbaru
  python ci_progress.py --run 12345              # pantau satu run tertentu
  python ci_progress.py --judul "mobile" --port 8800
Buka http://localhost:8800. Data dari `gh` (butuh gh yang sudah login), diperbarui tiap 15 detik.

Progres tiap job dihitung dari WAKTU berjalan dibanding durasi job yang sama di run acuan (--referensi, default run penuh 17 Nov 2026),
karena langkah test panjang tidak punya hitungan test selama berjalan. Angka ini PERKIRAAN: dibatasi 99% sampai job benar-benar selesai.
Hasil lulus/gagal per test baru ada di laporan PDF setelah semua job selesai.
"""
import argparse
import json
import re
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="Arif199630/evmoto-qa-automation-ecosystem")
ap.add_argument("--port", type=int, default=8800)
ap.add_argument("--run", default="", help="Nomor run yang dipantau; kosong = run terbaru yang judulnya cocok dengan --judul")
ap.add_argument("--judul", default=r"evmoto-regression all", help="Regex judul run yang diikuti (default: regression penuh)")
ap.add_argument("--referensi", default="44049612532", help="Run acuan untuk durasi per job (default: run penuh terjadwal 17 Nov 2026)")
args = ap.parse_args()
STATE = {"updated": "-", "run": None, "jobs": [], "error": "", "menunggu": "", "ringkas": {}, "eta": ""}
REF = {}  # nama job -> durasi menit di run acuan


def gh(*a):
    return subprocess.run(["gh", *a, "-R", args.repo], capture_output=True, text=True, encoding="utf-8", timeout=90)


def parse(iso):
    if not iso or iso.startswith("0001"):
        return None
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def menit(a, b=None):
    if a is None:
        return 0.0
    b = b or datetime.now(timezone.utc)
    return max((b - a).total_seconds() / 60, 0.0)


def muat_acuan():
    try:
        jobs = json.loads(gh("run", "view", args.referensi, "--json", "jobs").stdout)["jobs"]
        for j in jobs:
            m = menit(parse(j.get("startedAt")), parse(j.get("completedAt"))) if parse(j.get("completedAt")) else 0
            if m > 0:
                REF[j["name"]] = round(m, 1)
    except Exception as e:  # noqa: BLE001 - tanpa acuan, progres tidak dihitung
        STATE["error"] = f"acuan tidak terbaca: {e}"


def pilih_run():
    campos = "databaseId,displayTitle,status,conclusion,createdAt,url"
    if args.run:
        return json.loads(gh("run", "view", args.run, "--json", campos).stdout)
    daftar = json.loads(gh("run", "list", "--workflow", "ci.yml", "--limit", "25", "--json", campos).stdout)
    cocok = [r for r in daftar if re.search(args.judul, r["displayTitle"] or "")]
    return cocok[0] if cocok else None


def poll():
    muat_acuan()
    while True:
        try:
            run = pilih_run()
            if run is None:
                STATE.update(run=None, jobs=[], menunggu=f"Menunggu run dengan judul '{args.judul}' dipicu...",
                             updated=datetime.now().strftime("%H.%M.%S"))
                time.sleep(15)
                continue
            data = json.loads(gh("run", "view", str(run["databaseId"]), "--json", "jobs").stdout)["jobs"]
            jobs = []
            bobot_total = bobot_selesai = 0.0
            sisa = 0.0
            lewat = False
            for job in data:
                mulai, selesai = parse(job.get("startedAt")), parse(job.get("completedAt"))
                nama = job["name"]
                ref = REF.get(nama)
                berjalan = job["status"] == "in_progress"
                dur = menit(mulai, selesai) if mulai else 0.0
                steps = job.get("steps", [])
                sekarang = next((s["name"] for s in steps if s["status"] == "in_progress"), "")
                if job["status"] == "completed":
                    persen = 100
                elif berjalan and ref:
                    persen = min(99, int(100 * dur / ref))
                elif berjalan:
                    persen = None
                else:
                    persen = 0
                if ref:
                    bobot_total += ref
                    bobot_selesai += ref if job["status"] == "completed" else min(dur, ref) if berjalan else 0
                    if berjalan:
                        if dur > ref:
                            lewat = True
                        sisa = max(sisa, ref - dur)
                    elif job["status"] == "queued" or job["status"] == "waiting" or job["status"] == "pending":
                        sisa = max(sisa, ref)
                jobs.append({"name": nama, "status": job["status"], "conclusion": job.get("conclusion") or "", "persen": persen,
                             "menit": int(dur), "ref": ref, "current": sekarang, "url": job.get("url", "")})
            ringkas = {"selesai": sum(1 for j in jobs if j["status"] == "completed" and j["conclusion"] in ("success", "skipped")),
                       "gagal": sum(1 for j in jobs if j["conclusion"] == "failure"),
                       "berjalan": sum(1 for j in jobs if j["status"] == "in_progress"),
                       "antre": sum(1 for j in jobs if j["status"] in ("queued", "waiting", "pending")),
                       "total": len(jobs),
                       "persen_total": int(100 * bobot_selesai / bobot_total) if bobot_total else None}
            if run["status"] == "completed":
                eta = "selesai"
            elif lewat and sisa <= 0:
                eta = "melewati durasi acuan; perkiraan sulit"
            else:
                wib = datetime.now(timezone.utc) + timedelta(minutes=sisa + 4, hours=7)  # +4 menit untuk job laporan
                eta = f"sekitar {wib.strftime('%H.%M')} WIB (±{int(sisa)} menit lagi, dari durasi acuan)"
            STATE.update(run=run, jobs=jobs, error="", menunggu="", ringkas=ringkas, eta=eta,
                         updated=datetime.now().strftime("%H.%M.%S"))
        except Exception as e:  # noqa: BLE001 - tampilkan masalah koneksi di halaman, jangan berhenti
            STATE["error"] = str(e)[:200]
        time.sleep(15)


PAGE = """<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Progres Regression EvMoto</title><style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b1f24;--mut:#5b6470;--bar:#e3e6ea;--ok:#1a7f37;--run:#0969da;--bad:#cf222e;--wait:#9a6700}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--card:#161b22;--ink:#e6edf3;--mut:#9aa4af;--bar:#30363d}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}main{max-width:780px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:0 0 4px}.mut{color:var(--mut);font-size:13px}.card{background:var(--card);border-radius:10px;padding:12px 14px;margin:10px 0;box-shadow:0 1px 2px #0002}
.row{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}.bar{height:12px;background:var(--bar);border-radius:6px;overflow:hidden;margin:8px 0 4px}
.fill{height:100%;transition:width .6s}.big{height:18px}.chips span{display:inline-block;margin:2px 10px 2px 0;font-size:13px}
a{color:var(--run)}</style></head><body><main>
<h1>Progres Regression EvMoto (GitHub Actions)</h1><div class="mut" id="meta">memuat...</div>
<div class="card"><div class="row"><b>Total run</b><span id="allpct">-</span></div><div class="bar big"><div class="fill" id="allfill" style="width:0;background:var(--run)"></div></div>
<div class="chips" id="chips"></div><div id="eta" class="mut"></div></div><div id="jobs"></div>
<p class="mut">Diperbarui tiap 15 detik. Persentase job = waktu berjalan dibanding durasi job yang sama di run acuan (perkiraan, maksimal 99% sampai selesai).
Jumlah test lulus/gagal baru ada di laporan PDF setelah semua job selesai.</p></main>
<script>
const warna=j=>j.status!=="completed"?(j.status==="in_progress"?"var(--run)":"var(--wait)"):j.conclusion==="success"?"var(--ok)":j.conclusion==="skipped"?"var(--mut)":"var(--bad)";
const esc=t=>String(t).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
async function tick(){try{const s=await (await fetch("/data")).json();const r=s.run;
if(!r){document.getElementById("meta").textContent=s.menunggu||"menunggu data...";return}
const k=s.ringkas||{};
document.getElementById("meta").innerHTML=`Run: <a href="${r.url}" target="_blank">${esc(r.displayTitle)}</a> · ${r.status} ${r.conclusion||""} · diperbarui ${s.updated}${s.error?" · <b>"+esc(s.error)+"</b>":""}`;
const tp=k.persen_total==null?0:k.persen_total;document.getElementById("allpct").textContent=k.persen_total==null?"-":tp+"%";document.getElementById("allfill").style.width=tp+"%";
document.getElementById("chips").innerHTML=`<span style="color:var(--ok)">● ${k.selesai} selesai</span><span style="color:var(--run)">● ${k.berjalan} berjalan</span><span style="color:var(--wait)">● ${k.antre} antre</span><span style="color:var(--bad)">● ${k.gagal} gagal</span><span class="mut">dari ${k.total} job</span>`;
document.getElementById("eta").textContent="Perkiraan selesai: "+(s.eta||"-");
const urut=[...s.jobs].sort((a,b)=>(a.status==="in_progress"?0:a.status==="completed"?2:1)-(b.status==="in_progress"?0:b.status==="completed"?2:1)||a.name.localeCompare(b.name,undefined,{numeric:true}));
document.getElementById("jobs").innerHTML=urut.map(j=>{const p=j.persen==null?0:j.persen;
const st=j.status==="completed"?(j.conclusion==="success"?"selesai":"selesai: "+j.conclusion):j.status==="in_progress"?`berjalan ${j.menit} mnt${j.ref?" / acuan "+Math.round(j.ref)+" mnt":""}`:"antre";
return `<div class="card"><div class="row"><b>${esc(j.name)}</b><span>${st}</span></div>
<div class="bar"><div class="fill" style="width:${p}%;background:${warna(j)}"></div></div>
<div class="mut">${j.persen==null?"tanpa acuan durasi":(j.status==="completed"?"100%":"≈ "+p+"%")}${j.current?" · langkah: "+esc(j.current.slice(0,60)):""} · <a href="${j.url}" target="_blank">log live</a></div></div>`}).join("");
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
