"""
=============================================================================
LARK BITABLE (LARK BASE) DIRECT CLOUD SYNCHRONIZER
=============================================================================
Menyediakan integrasi langsung pengiriman data anomali bug ke tabel Lark Base
(Bitable) melalui Lark Open API resmi (open.larksuite.com).
=============================================================================
"""

import os
import json
import urllib.request
import urllib.error

# Konfigurasi kredensial Lark Cloud API dari Environment Variable atau Config
LARK_APP_ID = os.getenv("LARK_APP_ID", "")
LARK_APP_SECRET = os.getenv("LARK_APP_SECRET", "")
LARK_ACCESS_TOKEN = os.getenv("LARK_ACCESS_TOKEN", "")
LARK_BITABLE_APP_TOKEN = os.getenv("LARK_BITABLE_APP_TOKEN", "")
LARK_BITABLE_TABLE_ID = os.getenv("LARK_BITABLE_TABLE_ID", "")


def get_tenant_access_token(app_id=None, app_secret=None):
    """Mendapatkan token otorisasi tenant dari Lark Open API."""
    aid = app_id or LARK_APP_ID
    asec = app_secret or LARK_APP_SECRET
    if not aid or not asec:
        return None

    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": aid, "app_secret": asec}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if res_data.get("code") == 0:
                return res_data.get("tenant_access_token")
            else:
                print(f"[LarkBitableSync] Gagal autentikasi tenant: {res_data.get('msg')}")
    except Exception as e:
        print(f"[LarkBitableSync] Kesalahan koneksi otorisasi Lark: {e}")

    return None


def push_record_to_lark_bitable(bug_record, app_token=None, table_id=None, token=None):
    """
    Menyisipkan baris record bug langsung ke tabel Lark Base (Bitable) di cloud.
    """
    b_app_token = app_token or LARK_BITABLE_APP_TOKEN
    b_table_id = table_id or LARK_BITABLE_TABLE_ID

    if not b_app_token or not b_table_id:
        return False

    auth_token = token or LARK_ACCESS_TOKEN
    if not auth_token:
        auth_token = get_tenant_access_token()

    if not auth_token:
        print("[LarkBitableSync] Autorisasi Lark API belum tersedia (Perlu Token/App ID).")
        return False

    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{b_app_token}/tables/{b_table_id}/records"
    payload = {
        "fields": {
            "Bug ID": bug_record.get("Bug ID", ""),
            "Timestamp": bug_record.get("Timestamp", ""),
            "Modul / Fitur": bug_record.get("Modul / Fitur", ""),
            "Platform": bug_record.get("Platform", "Website (Desktop)"),
            "Environment": bug_record.get("Environment", "Production"),
            "Test Case & Fungsi": bug_record.get("Test Case & Fungsi", ""),
            "4 Pilar QA": bug_record.get("4 Pilar QA", ""),
            "Ringkasan Bug (Summary)": bug_record.get("Ringkasan Bug (Summary)", ""),
            "Severity": bug_record.get("Severity", ""),
            "Priority": bug_record.get("Priority", ""),
            "Status": bug_record.get("Status", "Open"),
            "Reporter": bug_record.get("Reporter", "QA Automation (<PROD_USER>)"),
            "Assignee": bug_record.get("Assignee", ""),
            "Target URL": bug_record.get("Target URL", ""),
            "Langkah Reproduksi": bug_record.get("Langkah Reproduksi", ""),
            "Hasil Diharapkan (Expected)": bug_record.get("Hasil Diharapkan (Expected)", ""),
            "Hasil Aktual / Error": bug_record.get("Hasil Aktual / Error", ""),
            "Evidence Screenshot Link": bug_record.get("Evidence Screenshot Link", "")
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if res_data.get("code") == 0:
                print(f"[LarkBitableSync] Berhasil menyisipkan record {bug_record.get('Bug ID')} ke tabel Lark Base di cloud!")
                return True
            else:
                print(f"[LarkBitableSync] Gagal menyisipkan record ke Lark: {res_data.get('msg')}")
    except Exception as e:
        print(f"[LarkBitableSync] Gagal mengirim data ke Lark Bitable API: {e}")

    return False
