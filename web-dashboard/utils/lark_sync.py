"""
=============================================================================
LARK SUITE / FEISHU WEBHOOK SYNCHRONIZER
=============================================================================
Menyediakan integrasi langsung pengiriman notifikasi Bug Card ke Larksuite:
- Lark Base (Bitable) & Lark Group Chat Webhook
- Menampilkan kartu interaktif dengan status severity, langkah reproduksi,
  dan tombol tautan bukti screenshot.
=============================================================================
"""

import os
import json
import urllib.request
import urllib.error

# Ambil webhook URL dari environment variable jika diset
LARK_WEBHOOK_URL = os.getenv("LARK_WEBHOOK_URL", "")


def send_bug_to_lark_webhook(bug_record, webhook_url=None):
    """
    Mengirimkan kartu interaktif Bug Report ke Lark Group Chat melalui Incoming Webhook.
    """
    url = webhook_url or LARK_WEBHOOK_URL
    if not url:
        # Webhook URL belum dikonfigurasi, lewati pengiriman ke cloud
        return False

    severity_color = {
        "Critical": "red",
        "Major": "orange",
        "Medium": "yellow",
        "Minor": "blue"
    }.get(bug_record.get("Severity"), "grey")

    card_payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🐞 [BUG TRACKER] {bug_record.get('Bug ID')}: {bug_record.get('Ringkasan Bug (Summary)')[:60]}"
                },
                "template": severity_color
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**Modul:**\n{bug_record.get('Modul / Fitur')}"}
                        },
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**Platform:**\n{bug_record.get('Platform', 'Website (Desktop)')}"}
                        },
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**Environment:**\n{bug_record.get('Environment', 'Production')}"}
                        },
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**4 Pilar QA:**\n{bug_record.get('4 Pilar QA')}"}
                        },
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**Severity:**\n{bug_record.get('Severity')}"}
                        },
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**Priority:**\n{bug_record.get('Priority')}"}
                        },
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**Test Case:**\n`{bug_record.get('Test Case & Fungsi')}`"}
                        },
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**Status:**\n{bug_record.get('Status')}"}
                        }
                    ]
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**Hasil Aktual / Error:**\n```\n{bug_record.get('Hasil Aktual / Error')[:250]}\n```"
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"Reporter: {bug_record.get('Reporter')} | URL: {bug_record.get('Target URL')} | {bug_record.get('Timestamp')}"
                        }
                    ]
                }
            ]
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(card_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_code = response.getcode()
            if res_code == 200:
                print(f"[LarkSync] Kartu Bug {bug_record.get('Bug ID')} berhasil dikirim ke Lark!")
                return True
    except Exception as e:
        print(f"[LarkSync] Gagal mengirim kartu bug ke Lark webhook: {e}")

    return False
