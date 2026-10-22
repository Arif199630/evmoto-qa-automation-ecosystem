"""
=============================================================================
EVMOTO USER MOBILE AUTOMATION - LARK SUITE / FEISHU NOTIFIER
=============================================================================
Menyediakan integrasi langsung pengiriman Kartu Interaktif Bug Report dan
Ringkasan Eksekusi Pengujian Otomatis ke Grup Chat Tim Developer di Lark.
=============================================================================
"""

import os
import json
import urllib.request
import urllib.error
import time

# Default Lark Webhook URL dari Environment Variable
LARK_WEBHOOK_URL = os.getenv("LARK_WEBHOOK_URL", "")


def send_lark_interactive_card(card_payload: dict, webhook_url: str = None) -> bool:
    """
    Mengirimkan kartu interaktif ke Lark Incoming Webhook.
    """
    url = webhook_url or LARK_WEBHOOK_URL or os.getenv("LARK_WEBHOOK_URL", "")
    if not url:
        print("[LarkNotifier] PERINGATAN: LARK_WEBHOOK_URL belum diset. Pengiriman dilewati.")
        return False

    req_data = {
        "msg_type": "interactive",
        "card": card_payload
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(req_data).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            resp_body = response.read().decode("utf-8")
            resp_json = json.loads(resp_body) if resp_body else {}
            
            if status_code == 200 and resp_json.get("code", 0) == 0:
                print(f"[LarkNotifier] BERHASIL! Notifikasi terkirim ke Lark. (Status: 200 OK)")
                return True
            else:
                print(f"[LarkNotifier] Respons Lark non-zero: {resp_body}")
                return False
    except urllib.error.HTTPError as e:
        print(f"[LarkNotifier] HTTP Error {e.code}: {e.read().decode('utf-8', errors='replace')}")
        return False
    except Exception as e:
        print(f"[LarkNotifier] Gagal mengirim pesan ke Lark: {e}")
        return False


def build_register_stuck_bug_card() -> dict:
    """
    Menyusun Kartu Interaktif Lengkap untuk Bug Registrasi Stuck di Halaman Register.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S WIB")
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "🚨 [CRITICAL BUG REPORT] Registrasi Akun Baru Stuck Saat Klik 'Buat Akun'"
            },
            "template": "red"
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": "**Modul / Fitur:**\nAuth - Registrasi User Baru"}
                    },
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": "**Platform:**\nAndroid Mobile (Flutter)"}
                    },
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": "**Target Environment:**\nGolang Server (`api-dev.evmoto.internal`)"}
                    },
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": "**Target APK:**\n`evmoto-user-1.2.32-env-prod_debug_golang` (v2103)"}
                    },
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": "**Severity / Priority:**\n🔴 **Critical** / ⚡ **P0 (Immediate Blocker)**"}
                    },
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": "**Pelapor:**\nTim Sales Lapangan & QA Automation"}
                    }
                ]
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        "### 🔍 Ringkasan Masalah (Root Cause):\n"
                        "Calon user menginput semua data dengan benar (Nomor HP, Nama, OTP 4-digit). Saat tombol **'Create Account' / 'Buat Akun'** ditekan, aplikasi **membeku (stuck)** di layar formulir tanpa feedback.\n\n"
                        "**Hasil Analisis Jaringan & Backend Golang:**\n"
                        "- **Request Mobile:** `POST https://api-dev.evmoto.internal/account/base/user`\n"
                        "- **Respons Server:** `HTTP 405 Method Not Allowed`\n"
                        "- **Header Server:** `Allow: PUT` *(Router Golang hanya menerima PUT, method POST belum terdaftar)*\n"
                        "- **Aplikasi Mobile:** Mengalami *Silent Failure* — indikator loading ditutup tapi tidak memunculkan snackbar error."
                    )
                }
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        "### 📋 Langkah Reproduksi (Steps to Reproduce):\n"
                        "1. Buka aplikasi **eVMoto User** pada environment Golang.\n"
                        "2. Di halaman Login, klik **'Register as a New User'**.\n"
                        "3. Input No HP baru (`821xxxxxxx`) & Nama Lengkap.\n"
                        "4. Klik **'Request OTP'**, lalu masukkan kode OTP `1234`.\n"
                        "5. Klik tombol biru **'Create Account' / 'Buat Akun'**.\n"
                        "6. **Hasil Aktual:** Loading tertutup seketika, layar tetap diam di form registrasi. Notifikasi Chucker memunculkan `405 Method Not Allowed`."
                    )
                }
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        "### 🛠️ Rekomendasi Solusi Tim Engineer:\n"
                        "1. **Backend Golang:** Daftarkan route handler `POST /account/base/user` di router Gin/Fiber untuk memproses pendaftaran user baru.\n"
                        "2. **Mobile Flutter:** Tambahkan penanganan `catchError` di `RegisterController` agar memunculkan `SnackbarHelper.showError()` saat API merespons error `>= 400`."
                    )
                }
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"Automated QA Bug Alert | Waktu Laporan: {timestamp} | In-App Chucker Enabled"
                    }
                ]
            }
        ]
    }


def send_register_stuck_bug_report(webhook_url: str = None) -> bool:
    """
    Helper satu klik untuk mengirim laporan bug registrasi stuck ke Lark.
    """
    card = build_register_stuck_bug_card()
    return send_lark_interactive_card(card, webhook_url=webhook_url)


def send_test_failure_to_lark(test_name: str, docstring: str = "", error_message: str = "", screenshot_path: str = None, webhook_url: str = None) -> bool:
    """
    Mengirimkan laporan kegagalan skenario pengujian otomatis ke Lark secara real-time.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S WIB")
    clean_error = (error_message or "AssertionError / Element Not Found").strip()[:350]
    clean_doc = (docstring or "Automated Mobile Test Execution").strip().split("\n")[0][:120]

    card_payload = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"❌ [TEST FAILED] {test_name}"
            },
            "template": "red"
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": f"**Test Case:**\n`{test_name}`"}
                    },
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": "**Platform / Engine:**\nAndroid (Appium UiAutomator2)"}
                    },
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": "**Deskripsi Skenario:**\n" + clean_doc}
                    },
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": f"**Status:**\n🔴 **FAILED**"}
                    }
                ]
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**Pesan Kesalahan / Traceback:**\n```text\n{clean_error}\n```"
                }
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"Waktu: {timestamp} | Bukti Screenshot: {os.path.basename(screenshot_path) if screenshot_path else 'Tersedia di reports/screenshots'}"
                    }
                ]
            }
        ]
    }

    return send_lark_interactive_card(card_payload, webhook_url=webhook_url)


def send_server_alert_to_lark(status_code: int, status_message: str, webhook_url: str = None) -> bool:
    """
    Mengirimkan peringatan bahwa server backend dev/staging mati (HTTP 500) atau restart (HTTP 502).
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S WIB")
    template = "red" if status_code == 500 else "orange"

    card_payload = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"⚠️ [SERVER ALERT HTTP {status_code}] Backend api-dev.evmoto.internal"
            },
            "template": template
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        f"**Kondisi Server:** {status_message}\n\n"
                        "Automasi pengujian eVMoto mendeteksi server backend sedang mengalami kendala. "
                        "Eksekusi pengujian di-skip otomatis untuk mencegah false-alarm gagal uji."
                    )
                }
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"Server Health Check Hook | {timestamp}"
                    }
                ]
            }
        ]
    }

    return send_lark_interactive_card(card_payload, webhook_url=webhook_url)
