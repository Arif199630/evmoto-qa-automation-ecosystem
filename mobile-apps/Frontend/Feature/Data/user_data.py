"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - CENTRAL TEST DATA & USER PROVIDER
================================================================================
Pusat terpadu penyedia data kredensial multiple user (users.json) dan dataset
pengujian 4 Pilar QA (Registrasi, Login, dan Profil Pengguna).
================================================================================
"""
import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_JSON_PATH = os.path.join(CURRENT_DIR, "users.json")


# ==============================================================================
# 1. MOBILE USER DATA PROVIDER (MULTI-USER REPOSITORY LOADER)
# ==============================================================================

class MobileUserDataProvider:
    """Class penyedia data multiple user untuk automasi mobile."""

    _users = None

    @classmethod
    def load_users(cls):
        """Membaca data users dari file users.json dengan decoding utf-8-sig."""
        if cls._users is None:
            if os.path.exists(USERS_JSON_PATH):
                with open(USERS_JSON_PATH, "r", encoding="utf-8-sig") as f:
                    cls._users = json.load(f)
            else:
                cls._users = {}

            # Override default dev_user via environment variable (dev vs production)
            try:
                from config.config import ACTIVE_PHONE, ACTIVE_OTP, ENVIRONMENT
                active_phone = ACTIVE_PHONE
                active_otp = ACTIVE_OTP
                active_env = ENVIRONMENT
            except Exception:
                active_phone = os.getenv("ACTIVE_PHONE") or os.getenv("EVMOTO_DEV_PHONE")
                active_otp = os.getenv("ACTIVE_OTP") or os.getenv("EVMOTO_DEV_OTP")
                active_env = os.getenv("ENVIRONMENT", "dev").lower()

            if "dev_user" in cls._users:
                if active_phone:
                    cls._users["dev_user"]["phone"] = str(active_phone)
                if active_otp:
                    cls._users["dev_user"]["otp"] = str(active_otp)
                if active_env in ("prod", "production"):
                    cls._users["dev_user"]["role"] = "Prod Account (Active)"
                    cls._users["dev_user"]["name"] = "Prod User EvMoto"
                else:
                    cls._users["dev_user"]["role"] = "Dev Account (Active)"
                    cls._users["dev_user"]["name"] = "Dev User EvMoto"
        return cls._users

    @classmethod
    def get_user(cls, key_or_role: str) -> dict:
        """Mengambil data profil user berdasarkan key, nama role, atau nomor HP."""
        users = cls.load_users()
        if key_or_role in users:
            return users[key_or_role]
        for user_key, data in users.items():
            if data.get("role", "").lower() == key_or_role.lower():
                return data
            if data.get("phone", "") == str(key_or_role):
                return data
        raise KeyError(f"Mobile user dengan identitas '{key_or_role}' tidak ditemukan di users.json")

    @classmethod
    def get_credentials(cls, key_or_role: str = "dev_user") -> tuple:
        """Mengembalikan pasangan tuple (phone, otp) untuk user tertentu."""
        user = cls.get_user(key_or_role)
        return user["phone"], user["otp"]

    @classmethod
    def get_dev_user(cls) -> dict:
        return cls.get_user("dev_user")

    @classmethod
    def get_gopay_user(cls) -> dict:
        """Mengambil profil user fitur pembayaran Gopay."""
        return cls.get_user("gopay_user")

    @classmethod
    def get_registered_users(cls) -> list:
        """Mengembalikan seluruh daftar akun user yang berstatus terdaftar (registered)."""
        users = cls.load_users()
        return [data for data in users.values() if "registered" in data.get("role", "").lower() or "active" in data.get("role", "").lower()]

    @classmethod
    def get_unregistered_user(cls) -> dict:
        return cls.get_user("unregistered_user")

    @classmethod
    def get_invalid_prefix_user(cls) -> dict:
        return cls.get_user("invalid_prefix_user")

    @classmethod
    def get_short_phone_user(cls) -> dict:
        return cls.get_user("short_phone_user")

    @classmethod
    def get_sqli_user(cls) -> dict:
        return cls.get_user("sqli_payload_user")

    @classmethod
    def get_xss_user(cls) -> dict:
        return cls.get_user("xss_payload_user")

    @classmethod
    def list_all_roles(cls) -> list:
        return [data.get("role") for data in cls.load_users().values()]


# ==============================================================================
# RESOLUSI KREDENSIAL AKTIF DARI PROVIDER
# ==============================================================================
dev_phone, dev_otp = MobileUserDataProvider.get_credentials("dev_user")
gopay_phone, gopay_otp = MobileUserDataProvider.get_credentials("gopay_user")

REGISTERED_MOBILE_USERS = MobileUserDataProvider.get_registered_users()
REGISTERED_PHONE_NUMBERS = [u["phone"] for u in REGISTERED_MOBILE_USERS]


# ==============================================================================
# 2. DATASET PENGUJIAN HALAMAN REGISTRASI (REGISTER - 4 PILAR QA)
# ==============================================================================

# 1. Register - Positive True (PT)
REGISTER_DATA_POSITIVE_TRUE = {
    "TC_REG_PT_01": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi akun baru data valid tanpa kode referral",
        "full_name": "QA Tester EvMoto Dev",
        "otp": dev_otp,
        "referral_code": "",
        "expected_result": "SUCCESS_REGISTRATION"
    },
    "TC_REG_PT_02": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi akun baru dengan kode referral dev aktif (EVMOTO26)",
        "full_name": "QA Tester Referral EvMoto",
        "otp": dev_otp,
        "referral_code": "EVMOTO26",
        "expected_result": "SUCCESS_REGISTRATION_WITH_REFERRAL"
    },
    "TC_REG_PT_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi akun baru dengan nama berkarakter khusus sah Indonesia (apostrof & tanda hubung)",
        "full_name": "Ahmad Syafi'i Kusuma-Wardani",
        "otp": dev_otp,
        "referral_code": "",
        "expected_result": "SUCCESS_REGISTRATION_SPECIAL_NAME"
    },
    "TC_REG_PT_04": {
        "tag": "POSITIVE_TRUE",
        "description": "Navigasi kembali ke Login melalui tautan 'Sudah Punya Akun? Masuk'",
        "expected_result": "SUCCESS_NAVIGATE_TO_LOGIN"
    }
}

# 2. Register - Positive False (PF)
REGISTER_DATA_POSITIVE_FALSE = {
    "TC_REG_PF_01": {
        "tag": "POSITIVE_FALSE",
        "description": "Registrasi menggunakan nomor Dev yang sudah aktif di database (Duplikat)",
        "full_name": "QA Tester Duplicate",
        "phone": dev_phone,  # Nomor valid tetapi duplikat
        "expected_error": "Nomor handphone sudah terdaftar. Silakan masuk."
    },
    "TC_REG_PF_02": {
        "tag": "POSITIVE_FALSE",
        "description": "Registrasi dengan kode referral yang tidak valid / kadaluarsa",
        "full_name": "QA Tester Invalid Ref",
        "otp": dev_otp,
        "referral_code": "EXPIRED99",
        "expected_error": "Kode referral tidak valid atau sudah berakhir."
    },
    "TC_REG_PF_03": {
        "tag": "POSITIVE_FALSE",
        "description": "Submit 'Create Account' sebelum menekan 'Request OTP' (Alur bisnis tidak lengkap)",
        "full_name": "QA Tester Bypass OTP",
        "expected_behavior": "REJECT_SUBMIT_WITHOUT_OTP"
    },
    "TC_REG_PF_04": {
        "tag": "POSITIVE_FALSE",
        "description": "Request OTP berulang kali secara instan (Rate Limiting / Anti-Spam Cooldown)",
        "full_name": "QA Tester Spam OTP",
        "expected_behavior": "COOLDOWN_TIMER_ACTIVE"
    }
}

# 3. Register - Negative True (NT)
REGISTER_DATA_NEGATIVE_TRUE = {
    "TC_REG_NT_01": {
        "tag": "NEGATIVE_TRUE",
        "description": "Registrasi dengan kode OTP salah (misal: 9999, bukan 1234)",
        "phone": dev_phone,
        "otp_wrong": "9999",
        "expected_error": "Kode verifikasi salah. Silakan coba lagi."
    },
    "TC_REG_NT_02": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input nomor registrasi tidak diawali angka 8 (diawali 0)",
        "phone": "082100000000",
        "expected_error": "Nomor telepon harus diawali dengan 8"
    },
    "TC_REG_NT_03": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input nomor registrasi kurang dari 8 digit (terlalu pendek)",
        "phone": "82146",
        "expected_error": "Nomor telepon minimal 8 digit"
    },
    "TC_REG_NT_04": {
        "tag": "NEGATIVE_TRUE",
        "description": "Field nama lengkap dikosongkan saat pendaftaran",
        "full_name": "",
        "expected_error": "Silakan masukkan nama lengkap"
    },
    "TC_REG_NT_05": {
        "tag": "NEGATIVE_TRUE",
        "description": "Field nomor handphone dikosongkan saat menekan Request OTP atau submit",
        "phone": "",
        "expected_error": "Silakan masukkan nomor ponsel Anda"
    },
    "TC_REG_NT_06": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input kode OTP tidak lengkap (kurang dari 4 digit, misal hanya 2 digit)",
        "otp_incomplete": "12",
        "expected_error": "Kode OTP harus 4 digit"
    },
    "TC_REG_NT_07": {
        "tag": "NEGATIVE_TRUE",
        "description": "Field nama lengkap hanya berisi angka numerik tanpa huruf",
        "full_name_numeric": "1234567890",
        "expected_error": "Nama lengkap tidak boleh hanya berupa angka"
    },
    "TC_REG_NT_08": {
        "tag": "NEGATIVE_TRUE",
        "description": "Penolakan karakter simbol khusus pada kode referral",
        "referral_code_invalid": "EV@MOTO#99",
        "expected_error": "Kode referral hanya boleh berupa huruf dan angka"
    }
}

# 4. Register - Negative False (NF)
REGISTER_DATA_NEGATIVE_FALSE = {
    "TC_REG_NF_01": {
        "tag": "NEGATIVE_FALSE",
        "description": "Injeksi SQL Classic pada kolom pendaftaran (' OR '1'='1)",
        "payload": "' OR '1'='1",
        "expected_behavior": "INPUT_SANITIZED_OR_REJECTED"
    },
    "TC_REG_NF_02": {
        "tag": "NEGATIVE_FALSE",
        "description": "Injeksi Cross-Site Scripting (XSS) pada kolom Nama Lengkap",
        "payload": "<script>alert('EvMoto_XSS')</script>",
        "expected_behavior": "TEXT_ESCAPED_NO_EXECUTION"
    },
    "TC_REG_NF_03": {
        "tag": "NEGATIVE_FALSE",
        "description": "Boundary Value Ekstrem: Input nama melebihi 255 karakter",
        "payload": "A" * 300,
        "expected_behavior": "TRUNCATED_OR_CHAR_LIMIT_ERROR"
    },
    "TC_REG_NF_04": {
        "tag": "NEGATIVE_FALSE",
        "description": "Input field Nama Lengkap hanya berisi spasi kosong (whitespace only)",
        "whitespace_name": "     ",
        "expected_behavior": "TRIMMED_AND_REJECTED_AS_EMPTY"
    },
    "TC_REG_NF_05": {
        "tag": "NEGATIVE_FALSE",
        "description": "Input Nama Lengkap menggunakan karakter Emoji & simbol Unicode",
        "unicode_name": "Tester EvMoto 🛵⚡🇮🇩",
        "expected_behavior": "SAFE_UNICODE_HANDLING_NO_CRASH"
    },
    "TC_REG_NF_06": {
        "tag": "NEGATIVE_FALSE",
        "description": "Input karakter alfabet pada field nomor telepon (Filter Numeric)",
        "alphabet_phone": "821-EVMOTO-TEST",
        "expected_behavior": "ALPHA_CHARS_FILTERED_DIGITS_ONLY"
    }
}


# ==============================================================================
# 3. DATASET PENGUJIAN HALAMAN LOGIN (MASUK - 4 PILAR QA)
# ==============================================================================

# 1. Login - Positive True (PT)
LOGIN_DATA_POSITIVE_TRUE = {
    "TC_LOG_PT_01": {
        "tag": "POSITIVE_TRUE",
        "description": "Login langsung menggunakan nomor HP Dev 81299990001 dan OTP 1234",
        "phone": dev_phone,
        "otp": dev_otp,
        "expected_result": "SUCCESS_LOGIN_TO_HOME"
    },
    "TC_LOG_PT_02": {
        "tag": "POSITIVE_TRUE",
        "description": "Login akun terdaftar dengan format nomor telepon variasi panjang 10-12 digit",
        "phone": dev_phone,
        "otp": dev_otp,
        "expected_result": "SUCCESS_LOGIN_TO_HOME"
    },
    "TC_LOG_PT_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Login berhasil menggunakan alur Resend OTP setelah countdown selesai",
        "phone": dev_phone,
        "otp": dev_otp,
        "expected_result": "SUCCESS_LOGIN_VIA_RESEND_OTP"
    },
    "TC_LOG_PT_GOPAY": {
        "tag": "POSITIVE_TRUE",
        "description": "Login langsung user fitur pembayaran Gopay (81299990002)",
        "phone": gopay_phone,
        "otp": gopay_otp,
        "expected_result": "SUCCESS_LOGIN_GOPAY_USER"
    },
    "TC_LOG_PT_04": {
        "tag": "POSITIVE_TRUE",
        "description": "Navigasi alur login meninjau Terms and Conditions dan Privacy Policy",
        "expected_result": "SUCCESS_VIEW_LEGAL_PAGES"
    },
    "TC_LOG_PT_05": {
        "tag": "POSITIVE_TRUE",
        "description": "Login berhasil dengan skenario Location Phone dimatikan, verifikasi popup Location Permission, izinkan akses, dan lanjut login hingga masuk Beranda",
        "phone": dev_phone,
        "otp": dev_otp,
        "expected_result": "SUCCESS_LOGIN_WITH_LOCATION_PERMISSION_HANDLED"
    },
    "TC_LOG_PT_06": {
        "tag": "POSITIVE_TRUE",
        "description": "Login dengan nomor diawali format internasional +62 / 62 otomatis dinormalisasi",
        "phone_input": "+6281299990001",
        "expected_phone": dev_phone,
        "otp": dev_otp,
        "expected_result": "SUCCESS_LOGIN_TO_HOME"
    },
    "TC_LOG_PT_07": {
        "tag": "POSITIVE_TRUE",
        "description": "Perubahan nomor telepon dari layar OTP kembali ke layar login",
        "phone": dev_phone,
        "expected_result": "SUCCESS_NAVIGATE_BACK_TO_LOGIN"
    },
    "TC_LOG_PT_08": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi tipe keyboard numerik pada kolom nomor handphone",
        "expected_result": "INPUT_TYPE_PHONE_NUMERIC"
    }
}

# 2. Login - Positive False (PF)
LOGIN_DATA_POSITIVE_FALSE = {
    "TC_LOG_PF_01": {
        "tag": "POSITIVE_FALSE",
        "description": "Login dengan nomor telepon valid yang BELUM PERNAH TERDAFTAR",
        "phone": "81299990000",  # Format valid tapi belum ada akun
        "expected_error": "Nomor telepon belum terdaftar"
    },
    "TC_LOG_PF_02": {
        "tag": "POSITIVE_FALSE",
        "description": "Tombol 'Log In' tetap nonaktif (disabled) saat nomor kurang dari 8 digit",
        "short_phone": "82146",
        "expected_behavior": "BUTTON_LOG_IN_DISABLED"
    },
    "TC_LOG_PF_03": {
        "tag": "POSITIVE_FALSE",
        "description": "Percobaan klik 'Resend' sebelum countdown timer berakhir (Cooldown masih aktif)",
        "phone": dev_phone,
        "expected_behavior": "RESEND_DISABLED_DURING_COUNTDOWN"
    },
    "TC_LOG_PF_04": {
        "tag": "POSITIVE_FALSE",
        "description": "Percobaan input OTP salah berulang kali hingga batas maksimal (Rate Limit / Lockout)",
        "phone": dev_phone,
        "otp_wrong": "9999",
        "expected_behavior": "RATE_LIMIT_OR_MAX_RETRY_EXCEEDED"
    }
}

# 3. Login - Negative True (NT)
LOGIN_DATA_NEGATIVE_TRUE = {
    "TC_LOG_NT_01": {
        "tag": "NEGATIVE_TRUE",
        "description": "Login nomor Dev dengan kode OTP salah (9999, bukan 1234)",
        "phone": dev_phone,
        "otp_wrong": "9999",
        "expected_error": "Verification code is invalid"
    },
    "TC_LOG_NT_02": {
        "tag": "NEGATIVE_TRUE",
        "description": "Login nomor tidak diawali angka 8 (misal: 082100000000)",
        "phone": "082100000000",
        "expected_error": "Nomor telepon harus diawali dengan 8"
    },
    "TC_LOG_NT_03": {
        "tag": "NEGATIVE_TRUE",
        "description": "Field nomor handphone dikosongkan saat menekan tombol Masuk",
        "phone": "",
        "expected_error": "Silakan masukkan nomor ponsel Anda"
    },
    "TC_LOG_NT_04": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input nomor handphone kurang dari 8 digit (misal hanya 4 digit: 8214)",
        "short_phone": "8214",
        "expected_error": "Nomor telepon minimal 8 digit"
    },
    "TC_LOG_NT_05": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input kode OTP tidak lengkap (< 4 digit, misal hanya 2 digit: 12)",
        "phone": dev_phone,
        "otp_incomplete": "12",
        "expected_error": "Kode OTP harus 4 digit"
    },
    "TC_LOG_NT_06": {
        "tag": "NEGATIVE_TRUE",
        "description": "Menekan tombol Back dari layar OTP membatalkan verifikasi dan kembali ke Layar Login",
        "phone": dev_phone,
        "expected_behavior": "RETURN_TO_LOGIN_SCREEN_SAFELY"
    }
}

# 4. Login - Negative False (NF)
LOGIN_DATA_NEGATIVE_FALSE = {
    "TC_LOG_NF_01": {
        "tag": "NEGATIVE_FALSE",
        "description": "Injeksi SQL Classic pada kolom login (' OR '1'='1)",
        "payload": "' OR '1'='1",
        "expected_behavior": "INPUT_SANITIZED_NO_CRASH"
    },
    "TC_LOG_NF_02": {
        "tag": "NEGATIVE_FALSE",
        "description": "Injeksi Cross-Site Scripting (XSS) pada kolom login (<script>alert(1)</script>)",
        "payload": "<script>alert('XSS_LOGIN')</script>",
        "expected_behavior": "TEXT_ESCAPED_NO_EXECUTION"
    },
    "TC_LOG_NF_03": {
        "tag": "NEGATIVE_FALSE",
        "description": "Boundary Value Ekstrem: Input nomor HP melebihi batas panjang maksimum (25 digit)",
        "extreme_phone": "8211111111111111111111111",
        "expected_behavior": "TRUNCATED_OR_RESTRICTED_MAX_DIGITS"
    },
    "TC_LOG_NF_04": {
        "tag": "NEGATIVE_FALSE",
        "description": "Input karakter alfabet dan simbol pada kolom nomor handphone",
        "alphabet_phone": "821-EVMOTO-LOGIN#",
        "expected_behavior": "NON_DIGITS_FILTERED_OUT"
    },
    "TC_LOG_NF_05": {
        "tag": "NEGATIVE_FALSE",
        "description": "Input whitespace murni (spasi kosong) pada kolom nomor telepon",
        "whitespace_phone": "         ",
        "expected_behavior": "WHITESPACE_TRIMMED_BUTTON_DISABLED"
    },
    "TC_LOG_NF_06": {
        "tag": "NEGATIVE_FALSE",
        "description": "Rapid Repeated Clicking (Spamming tombol Log In) mencegah race condition",
        "phone": dev_phone,
        "expected_behavior": "PREVENT_DUPLICATE_REQUEST_NO_FREEZE"
    }
}


# ==============================================================================
# 4. DATASET PENGUJIAN HALAMAN PROFIL & AKUN PENGGUNA (4 PILAR QA)
# ==============================================================================

# 0. Dataset Happy Flow
PROFILE_HAPPY_FLOW_DATA = {
    "emergency_contact": {
        "name": "Budi Kontak Darurat",
        "phone": "81234567890"
    },
    "languages": ["id", "en"],
    "payment_methods": ["Cash", "Dompet EVMoto", "GoPay", "OVO"],
    "faq_steps": ["download", "open_home", "book_ride"]
}

# 1. Pilar 1: Positive Testing (Happy Path & Functional)
PROFILE_PILAR_1_POSITIVE = {
    "valid_emergency_contact": {
        "name": "Siti Rahma Keluarga",
        "phone": "81398765432"
    },
    "valid_emergency_contact_special_char": {
        "name": "Ahmad Syafi'i",
        "phone": "81299990001"
    },
    "payment_preferences": {
        "target_default": "Cash"
    },
    "language_switch": {
        "primary": "id",
        "secondary": "en"
    },
    "saved_address_home": {
        "label": "Rumah Utama",
        "note": "Pagar Hitam No 45 Dekat Pos Satpam"
    },
    "cs_ticket_valid": {
        "category": "Kendala Aplikasi",
        "description": "Pertanyaan seputar panduan isi saldo dan metode pembayaran Gopay"
    }
}

# 2. Pilar 2: Negative Testing (Form Validation)
PROFILE_PILAR_2_NEGATIVE = {
    "empty_name_contact": {
        "name": "",
        "phone": "81234567890",
        "expected_error": "MANDATORY_FIELD_NAME"
    },
    "empty_phone_contact": {
        "name": "Kontak Tanpa Nomor",
        "phone": "",
        "expected_error": "MANDATORY_FIELD_PHONE"
    },
    "invalid_phone_alphabetic": {
        "name": "Kontak Huruf",
        "phone": "812ABCDEFGH",
        "expected_error": "INVALID_PHONE_FORMAT"
    },
    "invalid_phone_symbols": {
        "name": "Kontak Simbol",
        "phone": "812!@#$%^&*",
        "expected_error": "INVALID_PHONE_FORMAT"
    },
    "empty_cs_description": {
        "description": "",
        "expected_error": "MANDATORY_CS_DESCRIPTION"
    }
}

# 3. Pilar 3: Boundary Value Analysis (BVA)
PROFILE_PILAR_3_BOUNDARY = {
    "name_min_boundary_2_char": {
        "name": "Ib",
        "phone": "81234567890",
        "is_valid": True
    },
    "name_below_min_1_char": {
        "name": "I",
        "phone": "81234567890",
        "is_valid": False
    },
    "name_max_boundary_50_char": {
        "name": "Muhammad Rizky Ramadhan Putra Kusuma Wardani Pratama",
        "phone": "81234567890",
        "is_valid": True
    },
    "phone_min_boundary_10_digit": {
        "name": "Budi Batas Min",
        "phone": "8123456789",  # 10 digit (dimulai 8)
        "is_valid": True
    },
    "phone_below_min_9_digit": {
        "name": "Budi Di Bawah Min",
        "phone": "812345678",   # 9 digit
        "is_valid": False
    },
    "phone_max_boundary_13_digit": {
        "name": "Budi Batas Max",
        "phone": "8123456789012",  # 13 digit
        "is_valid": True
    },
    "phone_above_max_14_digit": {
        "name": "Budi Melebihi Max",
        "phone": "81234567890123",  # 14 digit
        "is_valid": False
    },
    "emergency_contact_max_quota": {
        "max_allowed": 5,
        "description": "BVA batas maksimal 5 kontak darurat"
    }
}

# 4. Pilar 4: Security, Input Sanitization & UI Resilience
PROFILE_PILAR_4_SECURITY = {
    "sqli_contact_name": {
        "name": "' OR '1'='1' --",
        "phone": "81234567890",
        "description": "SQL Injection payload pada nama kontak darurat"
    },
    "xss_contact_name": {
        "name": "<script>alert('XSS_EVMOTO')</script>",
        "phone": "81234567890",
        "description": "Cross-Site Scripting payload pada form profil"
    },
    "whitespace_padding": {
        "name": "   Budi Spasi   ",
        "phone": "   81234567890   ",
        "description": "Auto-trim whitespace check"
    },
    "address_whitespace_padding": {
        "label": "   Rumah Utama   ",
        "note": "   Pagar Hijau   ",
        "description": "Auto-trim whitespace check pada alamat favorit"
    }
}


# ==============================================================================
# 5. DATASET PENGUJIAN HALAMAN BERANDA (HOME PAGE - 4 PILAR QA)
# ==============================================================================

# 1. Home - Happy Flow Complete E2E Dataset
HOME_HAPPY_FLOW_DATA = {
    "greeting_keyword": "where are you going",
    "search_destination": "Grand Indonesia, Jakarta Pusat",
    "quick_chips": ["coffee", "office", "home"],
    "services": ["EvRide", "EvSend", "EvRent"],
    "default_city": "Jakarta"
}

# 2. Home - Pilar 1: Positive True (PT)
HOME_PILAR_1_POSITIVE = {
    "valid_destination_mall": {
        "query": "Grand Indonesia Shopping Town",
        "expected_result": "SHOW_SEARCH_RESULTS"
    },
    "valid_destination_station": {
        "query": "Stasiun Sudirman Jakarta",
        "expected_result": "SHOW_SEARCH_RESULTS"
    },
    "quick_chip_coffee": "coffee",
    "quick_chip_office": "office",
    "quick_chip_home": "home",
    "top_up_shortcut": {
        "nominal": "50.000",
        "description": "Shortcut top up dompet dari beranda"
    },
    "evsend_package": {
        "sender_note": "Dokumen Kontrak",
        "recipient_name": "Budi Santoso",
        "recipient_phone": "81234567890"
    },
    "evrent_station": {
        "station_query": "Stasiun Penukaran Baterai Sudirman"
    },
    "recent_search_item": {
        "query": "Stasiun Gambir"
    }
}

# 3. Home - Pilar 2: Positive False (PF)
HOME_PILAR_2_NEGATIVE = {
    "dismiss_welcome": {
        "action": "continue",
        "description": "Penutupan popup sambutan awal"
    },
    "cancel_top_up": {
        "action": "close",
        "description": "Pembatalan modal pilihan top up dari beranda"
    },
    "cancel_exit_app": {
        "action": "cancel",
        "description": "Pembatalan konfirmasi keluar aplikasi via back key"
    },
    "out_of_coverage_location": {
        "query": "Puncak Jaya Wijaya, Papua Pegunungan",
        "expected_notice": "OUT_OF_OPERATIONAL_AREA"
    },
    "peak_hour_rush": {
        "description": "Informasi lonjakan tarif jam sibuk"
    }
}

# 4. Home - Pilar 3: Negative True / Boundary Value Analysis (NT)
HOME_PILAR_3_BOUNDARY = {
    "empty_search_query": {
        "query": "",
        "expected_behavior": "PREVENT_EMPTY_SEARCH_SUBMIT"
    },
    "non_existent_destination": {
        "query": "QwErTy987654321_LokasiFiktifTidakTerdaftarDiPeta",
        "expected_result": "EMPTY_SEARCH_RESULT_DISPLAYED"
    },
    "min_search_single_char": {
        "query": "J",
        "description": "BVA batas minimal 1 karakter pencarian"
    },
    "zero_wallet_state": {
        "balance": "Rp 0",
        "description": "Peringatan saldo nol saat memilih metode dompet"
    },
    "same_pickup_and_dropoff": {
        "location": "Grand Indonesia Shopping Town",
        "expected_error": "SAME_LOCATION_NOT_ALLOWED"
    }
}

# 5. Home - Pilar 4: Negative False / Security & Resilience (NF)
HOME_PILAR_4_SECURITY = {
    "sqli_destination_search": {
        "payload": "' OR '1'='1' --",
        "description": "SQL Injection payload pada bilah pencarian tujuan"
    },
    "xss_destination_search": {
        "payload": "<script>alert('XSS_EVMOTO_HOME')</script>",
        "description": "Cross-Site Scripting payload pada input destinasi"
    },
    "whitespace_search_query": {
        "payload": "   Stasiun Gambir   ",
        "description": "Auto-trimming whitespace pada input pencarian"
    },
    "rapid_tapping_shortcut": {
        "taps": 3,
        "description": "Proteksi anti-race condition multi-tap tombol layanan"
    },
    "background_app_duration": 3,
    "emoji_symbol_search": {
        "payload": "🛵⚡🧭📍🗺️💥",
        "description": "Pencarian karakter emoji kompleks"
    }
}

# ==============================================================================
# 6. DATASET PENGUJIAN HALAMAN AKTIVITAS (ACTIVITY & ORDER HISTORY)
# ==============================================================================

# 1. Activity - Happy Flow Data
ACTIVITY_HAPPY_FLOW_DATA = {
    "module": "Activity & Order History",
    "description": "Pengujian alur positif lengkap modul Aktivitas dari header hingga rincian pesanan",
    "primary_tabs": {
        "regular": "Tab Regular (History Order Normal Booking)",
        "booking": "Tab Booking (History Order Advance Booking)"
    },
    "sample_order_id": "ORD-EVM-20261020-0012",
    "sample_email": "tester.evmoto@example.com",
    "rating_stars": 5,
    "rating_comment": "Perjalanan sangat menyenangkan, motor EV hening dan nyaman!",
    "anti_race_pause_sec": 5.0
}

# 2. Activity - Pilar 1: Positive True (PT)
ACTIVITY_PILAR_1_POSITIVE = {
    "primary_tabs": ["Regular", "Booking"],
    "regular_normal_booking": {
        "service": "EvRide (Normal Booking)",
        "description": "Riwayat order perjalanan instan langsung saat itu juga",
        "sample_order_id": "ORD-REG-20261020-0088"
    },
    "advance_booking": {
        "service": "EvRide (Advance Booking)",
        "scheduled_datetime": "21 Okt 2026, 08:30 WIB",
        "pickup": "Apartemen Thamrin Residence",
        "destination": "Bandara Soekarno Hatta Terminal 3",
        "rescheduled_time": "21 Okt 2026, 09:30 WIB",
        "description": "Riwayat order reservasi perjalanan terjadwal di masa depan"
    },
    "status_tabs": {
        "ongoing": "Sedang Berlangsung / Dalam Proses",
        "completed": "Riwayat / Selesai",
        "cancelled": "Dibatalkan"
    },
    "service_filters": ["Semua", "EvRide", "EvSend", "EvRent"],
    "date_filter_7_days": {
        "range_label": "7 Hari Terakhir",
        "days": 7
    },
    "date_filter_30_days": {
        "range_label": "30 Hari Terakhir",
        "days": 30
    },
    "rating_submission": {
        "stars": 5,
        "tags": ["Driver Ramah", "Motor Bersih", "Tepat Waktu"],
        "comment": "Driver sangat ramah dan mematuhi rambu lalu lintas!"
    },
    "email_receipt": {
        "email": "laporan.perjalanan@evmoto.id",
        "expected_notice": "RECEIPT_SENT_SUCCESS"
    },
    "reorder_trip": {
        "service": "EvRide",
        "pickup": "Grand Indonesia West Mall",
        "destination": "Stasiun Gambir Pintu Timur"
    },
    "report_lost_item": {
        "category": "Barang Tertinggal",
        "description": "Tertinggal payung warna hitam di gantungan motor",
        "expected_ticket": "TICKET_CREATED"
    }
}

# 3. Activity - Pilar 2: Positive False (PF)
ACTIVITY_PILAR_2_NEGATIVE = {
    "dismiss_rating": {
        "action": "Nanti Saja",
        "description": "Menutup dialog rating tanpa submit ulasan"
    },
    "cancel_email_receipt": {
        "action": "Batal",
        "description": "Membatalkan modal pengiriman email e-receipt"
    },
    "cancel_order_issue_report": {
        "action": "Batal",
        "description": "Membatalkan pelaporan kendala pada pesanan"
    },
    "cancel_date_filter": {
        "action": "Batal",
        "description": "Menutup dialog pemilih tanggal tanpa menerapkan filter"
    },
    "abort_cancel_active_trip": {
        "action": "Lanjutkan Pesanan",
        "description": "Membatalkan dialog konfirmasi pembatalan pesanan aktif"
    },
    "cancel_advance_booking_reschedule": {
        "action": "Batal",
        "description": "Menutup modal ubah jadwal advance booking tanpa simpan waktu baru"
    }
}

# 4. Activity - Pilar 3: Negative True / Boundary Value Analysis (NT)
ACTIVITY_PILAR_3_BOUNDARY = {
    "empty_activity_history": {
        "expected_state": "EMPTY_STATE_NO_ACTIVITY",
        "label": "Belum Ada Aktivitas"
    },
    "empty_advance_booking_history": {
        "expected_state": "EMPTY_STATE_NO_ADVANCE_BOOKING",
        "label": "Belum Ada Advance Booking Terjadwal"
    },
    "empty_filter_match": {
        "filter": "EvRent",
        "expected_state": "NO_ORDERS_MATCH_FILTER"
    },
    "zero_star_rating": {
        "stars": 0,
        "expected_error": "MINIMUM_1_STAR_REQUIRED"
    },
    "empty_issue_description": {
        "description": "",
        "expected_error": "ISSUE_DESCRIPTION_REQUIRED"
    },
    "invalid_email_receipt": {
        "email": "email_tanpa_domain",
        "expected_error": "INVALID_EMAIL_FORMAT"
    },
    "offline_network_state": {
        "expected_snackbar": "Koneksi internet terputus"
    }
}

# 5. Activity - Pilar 4: Negative False / Security & Resilience (NF)
ACTIVITY_PILAR_4_SECURITY = {
    "sqli_rating_comment": {
        "payload": "' OR '1'='1' --",
        "description": "SQL Injection payload pada komentar ulasan driver"
    },
    "xss_issue_description": {
        "payload": "<script>alert('XSS_EVMOTO_ACTIVITY')</script>",
        "description": "Cross-Site Scripting payload pada deskripsi komplain"
    },
    "rapid_tapping_tab_switch": {
        "taps": 4,
        "description": "Multi-tap perpindahan cepat antara Tab Regular dan Tab Booking (anti race condition)"
    },
    "rapid_tapping_refresh": {
        "taps": 3,
        "description": "Proteksi anti-race condition multi-tap tombol refresh aktivitas"
    },
    "background_app_duration": 3,
    "hardware_back_nav": {
        "description": "Resiliensi tombol back dari layar rincian pesanan"
    },
    "infinite_scroll_stress": {
        "swipes": 4,
        "description": "Ketahanan render list terhadap gestur scroll vertikal cepat"
    }
}

__all__ = [
    "MobileUserDataProvider",
    "dev_phone",
    "dev_otp",
    "gopay_phone",
    "gopay_otp",
    "REGISTERED_MOBILE_USERS",
    "REGISTERED_PHONE_NUMBERS",
    "REGISTER_DATA_POSITIVE_TRUE",
    "REGISTER_DATA_POSITIVE_FALSE",
    "REGISTER_DATA_NEGATIVE_TRUE",
    "REGISTER_DATA_NEGATIVE_FALSE",
    "LOGIN_DATA_POSITIVE_TRUE",
    "LOGIN_DATA_POSITIVE_FALSE",
    "LOGIN_DATA_NEGATIVE_TRUE",
    "LOGIN_DATA_NEGATIVE_FALSE",
    "PROFILE_HAPPY_FLOW_DATA",
    "PROFILE_PILAR_1_POSITIVE",
    "PROFILE_PILAR_2_NEGATIVE",
    "PROFILE_PILAR_3_BOUNDARY",
    "PROFILE_PILAR_4_SECURITY",
    "HOME_HAPPY_FLOW_DATA",
    "HOME_PILAR_1_POSITIVE",
    "HOME_PILAR_2_NEGATIVE",
    "HOME_PILAR_3_BOUNDARY",
    "HOME_PILAR_4_SECURITY",
    "ACTIVITY_HAPPY_FLOW_DATA",
    "ACTIVITY_PILAR_1_POSITIVE",
    "ACTIVITY_PILAR_2_NEGATIVE",
    "ACTIVITY_PILAR_3_BOUNDARY",
    "ACTIVITY_PILAR_4_SECURITY"
]

