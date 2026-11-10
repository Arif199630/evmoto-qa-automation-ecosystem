"""
Mock server lokal untuk layanan/endpoint yang BELUM ADA di staging EvMoto.

Hanya untuk dev/staging testing. Hasil test yang memakai mock ini memvalidasi alur automation
terhadap kontrak tiruan (stub), BUKAN perilaku backend sungguhan.

Cara pakai:
  python mock_server.py                 # port 8790, hanya 127.0.0.1
  python mock_server.py --port 8791

Rute dibaca dari fixtures/*.json (satu file per layanan). Tiap rute punya salah satu:
  "respons": {"status": 200, "body": {...}}   -> jawaban tetap, tanpa kode Python
  "handler": "<nama>"                          -> fungsi kecil di HANDLERS (untuk rute yang butuh state)

Rute bantu:
  GET  /__health  -> status server + daftar rute
  POST /__reset   -> kembalikan state ke data awal fixture (dipanggil conftest di awal tiap sesi pytest);
                     body {"ecgo_terhubung": false} untuk mencoba alur penautan akun dari awal
  GET  /__stats   -> jumlah request ke rute mock (dipakai conftest untuk menandai test mock=true)

Setiap respons membawa header X-Mock-Server: evmoto-qa-tools.
"""
import argparse
import json
import math
import threading
import uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
MOCK_HEADER = ("X-Mock-Server", "evmoto-qa-tools")
WIB = timezone(timedelta(hours=7))


# ------------------------------------------------------------------------------
# Fixture & state
# ------------------------------------------------------------------------------
def muat_fixtures():
    """Baca semua fixtures/*.json. Kembalikan (rute, data per layanan)."""
    rute, data = {}, {}
    for f in sorted(FIXTURES_DIR.glob("*.json")):
        isi = json.loads(f.read_text(encoding="utf-8"))
        data[isi["layanan"]] = isi.get("data", {})
        for r in isi["routes"]:
            rute[(r["method"].upper(), r["path"])] = {**r, "layanan": isi["layanan"]}
    return rute, data


ROUTES, DATA = muat_fixtures()
LOCK = threading.Lock()
STATE = {}


def reset_state(ecgo_terhubung=None):
    """State awal tiap sesi: semua diisi dari fixture, tidak ada yang tersisa dari run sebelumnya.

    ecgo_terhubung=False dipakai untuk mencoba alur penautan dari awal (start -> /connect/link -> status).
    """
    ecgo = DATA["ecgo_superapps"]["akun_uji"]
    order = DATA["evmoto_order"]
    STATE.clear()
    STATE.update({
        "hits": 0,
        "ecgo_token": set(),
        "ecgo_otp_diminta": set(),
        "ecgo_terhubung": bool(ecgo["sudah_terhubung_di_awal"] if ecgo_terhubung is None else ecgo_terhubung),
        "connect_token": set(),
        "tanggal_payout": set(),
        "nomor_sudah_klaim": set(),
        "kupon_berikutnya": 1001,
        "order_dievaluasi_subsidi": set(),
        "order": {o["orderId"]: {k: v for k, v in o.items() if not k.startswith("_")} for o in order["order_awal"]},
        "order_berikutnya": 1,
    })


reset_state()


# ------------------------------------------------------------------------------
# Helper respons
# ------------------------------------------------------------------------------
def evmoto(data, msg="SUCCESS", code=200, http=200):
    """Bentuk respons backend EvMoto (Golang): {code, msg, data}."""
    return http, {"code": code, "msg": msg, "data": data}


def evmoto_gagal(code, msg, http=200, **extra):
    return http, {"code": code, "msg": msg, **extra}


def ada_token_evmoto(req):
    """EvMoto mengirim token di header 'token' atau Authorization Bearer."""
    token = req["headers"].get("token") or req["headers"].get("authorization", "").replace("Bearer", "").strip()
    return bool(token)


def token_ecgo_valid(req):
    auth = req["headers"].get("authorization", "")
    return auth.startswith("Bearer ") and auth[7:] in STATE["ecgo_token"]


def iso_utc(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def bulat_setengah_ke_atas(nilai):
    """Sama dengan Go math.Round: 0,5 dibulatkan ke atas."""
    return int(math.floor(nilai + 0.5)) if nilai >= 0 else int(math.ceil(nilai - 0.5))


def ya(nilai):
    return str(nilai).strip().lower() in ("1", "true", "yes")


# ------------------------------------------------------------------------------
# ECGO SuperApps (Node.js)
# ------------------------------------------------------------------------------
def ecgo_generate_otp(req):
    d = DATA["ecgo_superapps"]["akun_uji"]
    phone = str(req["body"].get("phoneNumber", ""))
    if not phone:
        return 400, {"message": "phoneNumber wajib diisi"}
    STATE["ecgo_otp_diminta"].add(phone)
    kedaluwarsa = datetime.now(timezone.utc) + timedelta(minutes=d["otp_berlaku_menit"])
    return 200, {"message": "success", "otp": {
        "id": d["otp_id"], "code": int(d["otp"]), "userPhoneNumber": phone, "expiredAt": iso_utc(kedaluwarsa)}}


def ecgo_verify_otp(req):
    d = DATA["ecgo_superapps"]["akun_uji"]
    phone = str(req["body"].get("phoneNumber", ""))
    code = str(req["body"].get("code", ""))
    if phone not in STATE["ecgo_otp_diminta"] or code != str(d["otp"]):
        return 404, {"message": "Expired / Invalid code"}
    token = f"QA-MOCK-ECGO-{uuid.uuid4().hex}"
    STATE["ecgo_token"].add(token)
    return 200, {"message": "Login success", "token": token, "status": "verified"}


def ecgo_connect_status(req):
    if not token_ecgo_valid(req):
        return 401, {"success": False, "message": "Unauthorized"}
    terhubung = STATE["ecgo_terhubung"]
    return 200, {"success": True, "status": "completed" if terhubung else "not_connected", "linked": terhubung,
                 "couponGranted": terhubung, "hasVehicle": DATA["ecgo_superapps"]["akun_uji"]["punya_kendaraan"]}


def ecgo_connect_start(req):
    if not token_ecgo_valid(req):
        return 401, {"success": False, "message": "Unauthorized"}
    if STATE["ecgo_terhubung"]:
        return 409, {"success": False, "message": "Akun ECGO ini sudah terhubung dengan akun EvMoto."}
    token = f"QA-MOCK-CONNECT-{uuid.uuid4().hex[:16]}"
    STATE["connect_token"].add(token)
    return 200, {"success": True, "data": {"url": f"http://{req['host']}/connect?token={token}&found=1"}}


def ecgo_diskon_list(req):
    if not token_ecgo_valid(req):
        return 401, {"success": False, "message": "Unauthorized"}
    rows = []
    if STATE["ecgo_terhubung"]:
        sekarang = datetime.now(timezone.utc)
        for k in DATA["ecgo_superapps"]["kupon_setelah_terhubung"]:
            row = {key: v for key, v in k.items() if key != "berlaku_hari"}
            row["expiredAt"] = iso_utc(sekarang + timedelta(days=k["berlaku_hari"]))
            rows.append(row)
    return 200, {"message": "success", "data": {"count": len(rows), "rows": rows}}


def bridge_connect_link(req):
    token = str(req["body"].get("token", ""))
    if token not in STATE["connect_token"]:
        return 400, {"success": False, "message": "Token connect tidak valid atau sudah dipakai"}
    if not req["body"].get("found", True):
        return 404, {"success": False, "message": "Akun EvMoto tidak ditemukan"}
    STATE["connect_token"].discard(token)
    STATE["ecgo_terhubung"] = True
    return 200, {"success": True, "status": "completed", "linked": True}


# ------------------------------------------------------------------------------
# EvMoto fitur baru (Fitur 2, 3, 5)
# ------------------------------------------------------------------------------
def free_swap_daily(req):
    """Fitur 2: job payout harian kupon free swap. Satu tanggal hanya boleh diproses sekali (Redis lock)."""
    d = DATA["evmoto_new_features"]["free_swap"]
    tanggal = req["query"].get("date", datetime.now(WIB).strftime("%Y-%m-%d"))
    kunci = f"evmoto:freeswap:payout:{tanggal}"
    if tanggal in STATE["tanggal_payout"]:
        return evmoto_gagal(409, "DUPLICATE_JOB_LOCKED", http=409,
                            message=f"Lock {kunci} is already active or payout already completed.")
    STATE["tanggal_payout"].add(tanggal)

    kuota = int(req["query"].get("quota", d["kuota_default"]))
    drivers = d["driver_belum_terhubung"] if ya(req["query"].get("simulate_unlinked")) else d["driver_online"]
    hasil, dialokasikan = [], 0
    for drv in drivers:
        if drv["onlineMinutesWindow"] < d["target_menit"]:
            continue
        if not drv["linkedAt"]:
            status, kupon = "REJECTED_UNLINKED", None
        elif dialokasikan < kuota:
            dialokasikan += 1
            status, kupon = "ISSUED", f"QA-MOCK-CPN-{tanggal}-{drv['driverId']}"
        else:
            status, kupon = "QUOTA_EXCEEDED", None
        hasil.append({**drv, "couponStatus": status, "ecgoCouponId": kupon})
    return evmoto({"date": tanggal, "totalEvaluated": len(drivers), "allocatedCount": dialokasikan,
                   "quotaRemaining": kuota - dialokasikan, "redisLockKey": kunci, "eligibleDrivers": hasil})


def onboarding_voucher(req):
    """Fitur 3: paket kupon user baru. Dipakai PUT /account/base/user dan POST threeLogin."""
    d = DATA["evmoto_new_features"]["onboarding"]
    body = req["body"]
    user_id, company_id = body.get("userId", 0), body.get("companyId", d["company_evmoto"])
    phone = str(body.get("phone", ""))

    def jawab(msg, package_id, kupon):
        total = float(sum(k["amount"] for k in kupon))
        return evmoto({"userId": user_id, "companyId": company_id, "packageId": package_id, "vouchersIssued": len(kupon),
                       "totalDiscountValue": total, "budgetDeducted": total, "vouchers": kupon}, msg=msg)

    if ya(body.get("simulate_reregister_after_delete")) or (phone and phone in STATE["nomor_sudah_klaim"]):
        return jawab("ALREADY_CLAIMED_ONBOARDING_REWARD", d["package_id"], [])
    if company_id != d["company_evmoto"] or not d["paket_aktif"] or ya(body.get("simulate_inactive_package")):
        return jawab("SUCCESS", 0, [])

    sisa_budget = d["budget_saat_hampir_habis"] if ya(body.get("simulate_budget_exhausted")) else d["budget_normal"]
    kedaluwarsa = (datetime.now(WIB) + timedelta(days=d["kupon_berlaku_hari"])).strftime("%Y-%m-%d 23:59:59")
    kupon = []
    for nilai in d["nilai_kupon"]:
        if nilai > sisa_budget:
            break  # loop berhenti saat budget tidak cukup untuk kupon berikutnya
        sisa_budget -= nilai
        kupon.append({"couponId": STATE["kupon_berikutnya"], "amount": float(nilai), "expireTime": kedaluwarsa})
        STATE["kupon_berikutnya"] += 1
    if kupon and phone:
        STATE["nomor_sudah_klaim"].add(phone)
    msg = "SUCCESS" if len(kupon) == len(d["nilai_kupon"]) else "SUCCESS_PARTIAL_BUDGET_EXHAUSTED"
    return jawab(msg, d["package_id"], kupon)


def rush_hour_subsidy(req):
    """Fitur 5: subsidi jam sibuk, hanya mobil pribadi, satu orderId hanya dievaluasi sekali."""
    d = DATA["evmoto_new_features"]["rush_hour"]
    body = req["body"]
    order_id = str(body.get("orderId", ""))
    if order_id in STATE["order_dievaluasi_subsidi"]:
        return evmoto_gagal(409, "DUPLICATE_ORDER_SUBSIDY", http=409,
                            message=f"Order {order_id} has already been evaluated for rush hour subsidy.")
    STATE["order_dievaluasi_subsidi"].add(order_id)

    kendaraan = body.get("vehicleType")
    uang = float(body.get("orderMoney", 0))
    dibulatkan = bulat_setengah_ke_atas(uang)
    waktu = datetime.fromisoformat(str(body.get("orderTime")))
    if waktu.tzinfo:
        waktu = waktu.astimezone(WIB)
    jam = waktu.strftime("%H:%M")

    jendela = next((j["nama"] for j in d["jendela_wib"] if j["mulai"] <= jam <= j["selesai"]), "NONE")
    tier, subsidi, msg = 0, 0, "SUCCESS"
    if kendaraan != d["vehicle_type_mobil"]:
        jendela, msg = "NONE", "SUCCESS_NON_ELIGIBLE_VEHICLE"
    elif jendela == "NONE":
        msg = "SUCCESS_OUTSIDE_RUSH_HOUR"
    else:
        t = next(t for t in d["tier"] if t["sampai"] is None or dibulatkan <= t["sampai"])
        tier, subsidi = t["tier"], t["subsidi"]
    return evmoto({"orderId": order_id, "driverId": body.get("driverId"), "vehicleType": kendaraan,
                   "orderMoneyRaw": uang, "orderMoneyRounded": dibulatkan, "evaluatedTime": str(body.get("orderTime")),
                   "windowMatched": jendela, "tierApplied": tier, "subsidyAmount": subsidi,
                   "balanceChangeType": d["balance_change_type"], "incomeType": d["income_type"],
                   "isGuaranteedIncomeExempt": True}, msg=msg)


# ------------------------------------------------------------------------------
# EvMoto order penumpang
# ------------------------------------------------------------------------------
def hitung_tarif(body):
    d = DATA["evmoto_order"]["tarif"]
    lat1, lng1, lat2, lng2 = (math.radians(float(body.get(k, 0))) for k in ("originLat", "originLng", "destLat", "destLng"))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    jarak = round(6371 * 2 * math.asin(math.sqrt(a)), 2)
    return jarak, d["baseFare"] + bulat_setengah_ke_atas(d["pricePerKm"] * jarak)


def order_estimate_fare(req):
    if not ada_token_evmoto(req):
        return evmoto_gagal(600, "TOKEN_INVALID", data={})
    jarak, total = hitung_tarif(req["body"])
    d = DATA["evmoto_order"]["tarif"]
    return evmoto({"distanceKm": jarak, "baseFare": d["baseFare"], "pricePerKm": d["pricePerKm"],
                   "totalFare": total, "currency": "IDR"})


def order_create(req):
    if not ada_token_evmoto(req):
        return evmoto_gagal(600, "TOKEN_INVALID", data={})
    _, total = hitung_tarif(req["body"])
    order_id = f"QA-MOCK-ORD-{STATE['order_berikutnya']:04d}"
    STATE["order_berikutnya"] += 1
    STATE["order"][order_id] = {"orderId": order_id, "status": "SEARCHING_DRIVER", "totalFare": total}
    return evmoto(dict(STATE["order"][order_id]))


def order_cancel(req):
    if not ada_token_evmoto(req):
        return evmoto_gagal(600, "TOKEN_INVALID", data={})
    order = STATE["order"].get(str(req["body"].get("orderId", "")))
    if not order:
        return evmoto_gagal(500, "QA-MOCK: order tidak ditemukan", data={})
    if order["status"] == "CANCELLED":
        return evmoto_gagal(500, "QA-MOCK: order sudah dibatalkan", data={})
    order["status"] = "CANCELLED"
    return evmoto({"orderId": order["orderId"], "status": "CANCELLED"})


HANDLERS = {f.__name__: f for f in (
    ecgo_generate_otp, ecgo_verify_otp, ecgo_connect_status, ecgo_connect_start, ecgo_diskon_list,
    bridge_connect_link, free_swap_daily, onboarding_voucher, rush_hour_subsidy,
    order_estimate_fare, order_create, order_cancel,
)}


# ------------------------------------------------------------------------------
# HTTP server
# ------------------------------------------------------------------------------
class MockHandler(BaseHTTPRequestHandler):
    server_version = "EvMotoQAMock/1.0"

    def kirim(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header(*MOCK_HEADER)
        self.end_headers()
        self.wfile.write(data)

    def proses(self):
        url = urlparse(self.path)
        panjang = int(self.headers.get("Content-Length") or 0)
        mentah = self.rfile.read(panjang) if panjang else b""
        try:
            body = json.loads(mentah) if mentah else {}
        except ValueError:
            return self.kirim(400, {"message": "QA-MOCK: body bukan JSON"})
        req = {"body": body if isinstance(body, dict) else {},
               "query": {k: v[-1] for k, v in parse_qs(url.query).items()},
               "headers": {k.lower(): v for k, v in self.headers.items()},
               "host": self.headers.get("Host", "127.0.0.1")}

        with LOCK:
            if url.path == "/__health":
                return self.kirim(200, {"status": "ok", "mock": True,
                                        "routes": [f"{m} {p}" for m, p in sorted(ROUTES)]})
            if url.path == "/__reset" and self.command == "POST":
                reset_state(req["body"].get("ecgo_terhubung"))
                return self.kirim(200, {"status": "reset"})
            if url.path == "/__stats":
                return self.kirim(200, {"hits": STATE["hits"]})

            rute = ROUTES.get((self.command, url.path))
            if not rute:
                return self.kirim(404, {"code": 404, "msg": f"QA-MOCK: rute {self.command} {url.path} tidak ada di fixture"})
            STATE["hits"] += 1
            if "respons" in rute:
                return self.kirim(rute["respons"].get("status", 200), rute["respons"]["body"])
            status, isi = HANDLERS[rute["handler"]](req)
            return self.kirim(status, isi)

    do_GET = do_POST = do_PUT = do_DELETE = proses

    def log_message(self, fmt, *args):
        print(f"[mock {datetime.now():%H:%M:%S}] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}", flush=True)


def main():
    ap = argparse.ArgumentParser(description="Mock server lokal EvMoto QA (hanya 127.0.0.1).")
    ap.add_argument("--port", type=int, default=8790)
    args = ap.parse_args()
    for r in ROUTES.values():
        if "handler" in r and r["handler"] not in HANDLERS:
            raise SystemExit(f"Fixture {r['layanan']}: handler '{r['handler']}' tidak ada di mock_server.py")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), MockHandler)
    print(f"Mock server QA aktif di http://127.0.0.1:{args.port} ({len(ROUTES)} rute). Ctrl+C untuk berhenti.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
